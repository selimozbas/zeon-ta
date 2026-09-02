"""Advanced tools: VWAP, Fibonacci, pivot points, divergences, Hurst exponent, OU half-life."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

from ._core import (
    ArrayLike,
    Number,
    as_array,
    common_index,
    indicator,
    require_aligned_index,
    require_non_negative,
    require_same_length,
    rolling_sum,
    validate_length,
    validate_multiplier,
    wrap_frame,
    wrap_series,
)
from .foundations import _pivot_flags
from .oscillators import rsi

__all__ = [
    "approximate_entropy",
    "cpr",
    "dfa",
    "divergence",
    "fib_retracement",
    "hurst_exponent",
    "ou_half_life",
    "permutation_entropy",
    "pivot_points",
    "sample_entropy",
    "vwap",
]

#: Retracement ratios. 0.5 is not a Fibonacci number but is included by convention.
FIB_RATIOS: tuple[float, ...] = (0.236, 0.382, 0.5, 0.618, 0.786)

#: Extension ratios used to project targets beyond the swing.
FIB_EXTENSIONS: tuple[float, ...] = (1.272, 1.618, 2.618)


@indicator(
    category="advanced",
    summary="Volume-weighted average price with standard-deviation bands.",
    lesson="vwap",
    outputs=("VWAP", "VWAPU", "VWAPL"),
)
def vwap(
    high: ArrayLike,
    low: ArrayLike,
    close: ArrayLike,
    volume: ArrayLike,
    anchor: str = "session",
    length: int = 20,
    std: Number = 1.0,
) -> pd.DataFrame:
    """Volume-Weighted Average Price.

    ``TypicalPrice = (High + Low + Close) / 3``;
    ``VWAP = sum(TypicalPrice * Volume) / sum(Volume)``.

    With ``anchor="session"`` the sums reset at each session open, which is the
    only form institutions actually benchmark against — a VWAP that never resets
    is a different statistic. With ``anchor="rolling"`` the sums run over a fixed
    ``length`` window instead, which is what you want on continuously traded
    markets such as crypto.

    Bands sit at ``VWAP +/- std`` volume-weighted standard deviations of typical price.

    Parameters
    ----------
    high, low, close, volume:
        Series of equal length.
    anchor:
        ``"session"`` (reset each calendar day; requires a ``DatetimeIndex``) or
        ``"rolling"``.
    length:
        Window length, used only when ``anchor="rolling"``.
    std:
        Band width in volume-weighted standard deviations.

    Returns
    -------
    pandas.DataFrame
        Columns ``VWAP_{anchor}``, ``VWAPU_{anchor}``, ``VWAPL_{anchor}``.

    Raises
    ------
    ValueError
        If ``anchor="session"`` but the inputs carry no ``DatetimeIndex`` to
        derive session boundaries from. Pass a ``pd.Series`` with a
        ``DatetimeIndex``, or switch to ``anchor="rolling"``. Also raised if
        ``volume`` contains negative values, which have no meaning for a
        volume-weighted average and would otherwise surface only as a silent
        ``NaN`` once a window's net volume happened to cross zero.

    Examples
    --------
    >>> import pandas as pd, zeonta
    >>> idx = pd.date_range('2024-01-01', periods=4, freq='h')
    >>> bars = {k: pd.Series(v, index=idx) for k, v in
    ...         {'h': [2, 3, 4, 5], 'l': [1, 2, 3, 4], 'c': [1.5, 2.5, 3.5, 4.5],
    ...          'v': [10, 10, 10, 10]}.items()}
    >>> round(float(zeonta.vwap(bars['h'], bars['l'], bars['c'], bars['v']).iloc[-1, 0]), 4)
    3.0
    """
    if anchor not in ("session", "rolling"):
        raise ValueError(f"'anchor' must be 'session' or 'rolling', got {anchor!r}")
    length = validate_length(length)
    factor = validate_multiplier(std, "std")

    require_aligned_index(high=high, low=low, close=close, volume=volume)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    close_values = as_array(close, "close")
    volume_values = as_array(volume, "volume")
    require_same_length(high=high_values, low=low_values, close=close_values, volume=volume_values)
    require_non_negative(volume=volume_values)

    index = common_index(high, low, close, volume)
    typical = (high_values + low_values + close_values) / 3.0
    weighted = typical * volume_values
    weighted_square = typical * typical * volume_values

    if anchor == "session":
        if not isinstance(index, pd.DatetimeIndex):
            raise ValueError(
                "anchor='session' needs a DatetimeIndex to find session boundaries; "
                "pass pandas Series with a DatetimeIndex or use anchor='rolling'"
            )
        groups = pd.Series(index.normalize(), index=index)
        sum_volume = pd.Series(volume_values, index=index).groupby(groups).cumsum().to_numpy()
        sum_weighted = pd.Series(weighted, index=index).groupby(groups).cumsum().to_numpy()
        sum_square = pd.Series(weighted_square, index=index).groupby(groups).cumsum().to_numpy()
    else:
        sum_volume = rolling_sum(volume_values, length)
        sum_weighted = rolling_sum(weighted, length)
        sum_square = rolling_sum(weighted_square, length)

    with np.errstate(divide="ignore", invalid="ignore"):
        average = np.where(sum_volume > 0.0, sum_weighted / sum_volume, np.nan)
        variance = np.where(sum_volume > 0.0, sum_square / sum_volume - average * average, np.nan)
    deviation = np.sqrt(np.clip(variance, 0.0, None))

    suffix = anchor if anchor == "session" else f"rolling_{length}"
    order = [f"VWAP_{suffix}", f"VWAPU_{suffix}", f"VWAPL_{suffix}"]
    columns = (average, average + factor * deviation, average - factor * deviation)
    return wrap_frame(
        dict(zip(order, columns, strict=True)),
        index,
        order=order,
        roles={"line": order[0], "upper": order[1], "lower": order[2]},
    )


@indicator(
    category="advanced",
    summary="Fibonacci retracement levels drawn from the most recent swing.",
    lesson="fibonacci",
    outputs=("FIB",),
    returns_frame=True,
)
def fib_retracement(
    high: ArrayLike,
    low: ArrayLike,
    lookback: int = 100,
    ratios: Sequence[float] = FIB_RATIOS,
    extensions: bool = False,
) -> pd.DataFrame:
    """Fibonacci retracement levels over a rolling swing.

    The swing is the highest high and lowest low of the last ``lookback`` bars.
    Whichever of the two printed **later** defines the direction: if the high came
    last the market was rising, so levels are measured down from the high
    (``High - (High - Low) * ratio``); otherwise they are measured up from the low
    (``Low + (High - Low) * ratio``).

    Parameters
    ----------
    high, low:
        Price series of equal length.
    lookback:
        Bars in the swing window.
    ratios:
        Retracement ratios. Defaults to ``0.236, 0.382, 0.5, 0.618, 0.786``
        (``0.5`` is not a Fibonacci ratio but is drawn by convention).
    extensions:
        Also emit the ``1.272``, ``1.618`` and ``2.618`` projection levels.

    Returns
    -------
    pandas.DataFrame
        ``FIB_0`` (swing start), ``FIB_1`` (swing end), one ``FIB_{ratio}`` column
        per requested ratio, and ``FIBDIR`` (``1.0`` after an up-swing, ``-1.0``
        after a down-swing).

    Notes
    -----
    Fibonacci levels are self-fulfilling rather than physical: they matter because
    enough traders draw the same lines from the same swing. Two people picking
    different swings get different levels and both can be "right".

    Examples
    --------
    >>> import zeonta
    >>> out = zeonta.fib_retracement([1, 2, 3, 4, 5], [0, 1, 2, 3, 4], lookback=5)
    >>> float(out['FIBDIR'].iloc[-1])
    1.0
    """
    lookback = validate_length(lookback, "lookback", minimum=2)
    all_ratios = list(ratios) + (list(FIB_EXTENSIONS) if extensions else [])
    if not all_ratios:
        raise ValueError("'ratios' must not be empty")

    require_aligned_index(high=high, low=low)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    size = require_same_length(high=high_values, low=low_values)

    swing_high = np.full(size, np.nan, dtype="float64")
    swing_low = np.full(size, np.nan, dtype="float64")
    direction = np.full(size, np.nan, dtype="float64")

    if size >= lookback:
        high_windows = sliding_window_view(high_values, lookback)
        low_windows = sliding_window_view(low_values, lookback)
        swing_high[lookback - 1 :] = high_windows.max(axis=1)
        swing_low[lookback - 1 :] = low_windows.min(axis=1)
        # The extreme that printed later tells us which way the swing ran.
        high_position = high_windows.argmax(axis=1)
        low_position = low_windows.argmin(axis=1)
        direction[lookback - 1 :] = np.where(high_position >= low_position, 1.0, -1.0)

    span = swing_high - swing_low
    columns = {
        "FIB_0": np.where(direction > 0, swing_high, swing_low),
        "FIB_1": np.where(direction > 0, swing_low, swing_high),
    }
    for ratio in all_ratios:
        columns[f"FIB_{ratio}"] = np.where(
            direction > 0, swing_high - span * ratio, swing_low + span * ratio
        )
    columns["FIBDIR"] = direction

    return wrap_frame(columns, common_index(high, low), order=list(columns))


@indicator(
    category="advanced",
    summary="Classic or Fibonacci pivot levels derived from the previous bar.",
    reference="https://www.tradingview.com/support/solutions/43000521824-pivot-points-standard/",
    outputs=("PP", "R1", "R2", "R3", "S1", "S2", "S3"),
)
def pivot_points(
    high: ArrayLike,
    low: ArrayLike,
    close: ArrayLike,
    kind: str = "classic",
) -> pd.DataFrame:
    """Pivot points from the previous period's range.

    Classic::

        P  = (High + Low + Close) / 3
        R1 = 2*P - Low          S1 = 2*P - High
        R2 = P + (High - Low)   S2 = P - (High - Low)
        R3 = P + 2*(High - Low) S3 = P - 2*(High - Low)

    Fibonacci::

        R1/S1 = P +/- 0.382*(High - Low)
        R2/S2 = P +/- 0.618*(High - Low)
        R3/S3 = P +/- 1.000*(High - Low)

    Parameters
    ----------
    high, low, close:
        Price series of equal length.
    kind:
        ``"classic"`` or ``"fibonacci"``.

    Returns
    -------
    pandas.DataFrame
        Columns ``PP_{kind}``, ``R1_{kind}`` .. ``R3_{kind}``, ``S1_{kind}`` .. ``S3_{kind}``.

    Notes
    -----
    Levels are computed from the **previous** bar and apply to the current one, so
    the output is causal and safe to trade on. Feed daily bars for daily pivots,
    weekly bars for weekly pivots.

    Classic R3/S3 has no single universally cited formula — StockCharts'
    own Classic Pivot Points page does not define R3/S3 at all, and other
    write-ups describe a different one (``High + 2*(P - Low)``, actually the
    Camarilla system's R3, not Classic's) that this library previously used
    by mistake. ``P +/- 2*(High - Low)`` here is TradingView's own documented
    formula, confirmed both against their support page and empirically
    against a live TradingView reading; see ``tests/test_tradingview_parity.py``.

    Examples
    --------
    >>> import zeonta
    >>> out = zeonta.pivot_points([10, 11], [8, 9], [9, 10])
    >>> round(float(out['PP_classic'].iloc[1]), 4)
    9.0

    References
    ----------
    https://www.tradingview.com/support/solutions/43000521824-pivot-points-standard/
    """
    if kind not in ("classic", "fibonacci"):
        raise ValueError(f"'kind' must be 'classic' or 'fibonacci', got {kind!r}")

    require_aligned_index(high=high, low=low, close=close)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    close_values = as_array(close, "close")
    require_same_length(high=high_values, low=low_values, close=close_values)

    previous_high = np.concatenate(([np.nan], high_values[:-1]))
    previous_low = np.concatenate(([np.nan], low_values[:-1]))
    previous_close = np.concatenate(([np.nan], close_values[:-1]))

    pivot = (previous_high + previous_low + previous_close) / 3.0
    span = previous_high - previous_low

    if kind == "classic":
        r1, s1 = 2.0 * pivot - previous_low, 2.0 * pivot - previous_high
        r2, s2 = pivot + span, pivot - span
        r3, s3 = pivot + 2.0 * span, pivot - 2.0 * span
    else:
        r1, s1 = pivot + 0.382 * span, pivot - 0.382 * span
        r2, s2 = pivot + 0.618 * span, pivot - 0.618 * span
        r3, s3 = pivot + 1.0 * span, pivot - 1.0 * span

    order = [f"{name}_{kind}" for name in ("PP", "R1", "R2", "R3", "S1", "S2", "S3")]
    return wrap_frame(
        dict(zip(order, (pivot, r1, r2, r3, s1, s2, s3), strict=True)),
        common_index(high, low, close),
        order=order,
        roles={
            "pivot": order[0],
            "resistance_1": order[1],
            "resistance_2": order[2],
            "resistance_3": order[3],
            "support_1": order[4],
            "support_2": order[5],
            "support_3": order[6],
        },
    )


@indicator(
    category="advanced",
    summary="Classic pivot with a width band (Top/Bottom Central) around it, from the prior bar.",
    outputs=("CPR_PIVOT", "CPR_BC", "CPR_TC"),
    reference="https://www.luxalgo.com/library/concept/central-pivot-range/",
)
def cpr(high: ArrayLike, low: ArrayLike, close: ArrayLike) -> pd.DataFrame:
    """Central Pivot Range.

    The same classic pivot :func:`pivot_points` computes, plus a width
    band built from the same previous bar's range::

        Pivot = (High + Low + Close) / 3
        BC (Bottom Central) = (High + Low) / 2
        TC (Top Central) = 2*Pivot - BC

    The CPR's width is always exactly two-thirds of the distance between
    the previous close and the previous range's midpoint — a narrow CPR
    means the prior bar closed near the middle of its own range
    (indecision), a wide one that it closed near an extreme (a
    directional bar).

    Parameters
    ----------
    high, low, close:
        Price series of equal length.

    Returns
    -------
    pandas.DataFrame
        Columns ``CPR_PIVOT``, ``CPR_BC`` (bottom), ``CPR_TC`` (top).

    Notes
    -----
    Like :func:`pivot_points`, levels are computed from the **previous**
    bar and apply to the current one, so the output is causal. Feed daily
    bars for daily CPR levels, weekly bars for weekly ones.

    Examples
    --------
    >>> import zeonta
    >>> out = zeonta.cpr([10.0, 14.0], [8.0, 9.0], [9.6, 13.0])
    >>> out.iloc[1].round(4).tolist()
    [9.2, 9.0, 9.4]

    References
    ----------
    https://www.luxalgo.com/library/concept/central-pivot-range/
    """
    require_aligned_index(high=high, low=low, close=close)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    close_values = as_array(close, "close")
    require_same_length(high=high_values, low=low_values, close=close_values)

    previous_high = np.concatenate(([np.nan], high_values[:-1]))
    previous_low = np.concatenate(([np.nan], low_values[:-1]))
    previous_close = np.concatenate(([np.nan], close_values[:-1]))

    pivot = (previous_high + previous_low + previous_close) / 3.0
    bottom_central = (previous_high + previous_low) / 2.0
    top_central = 2.0 * pivot - bottom_central

    order = ["CPR_PIVOT", "CPR_BC", "CPR_TC"]
    return wrap_frame(
        dict(zip(order, (pivot, bottom_central, top_central), strict=True)),
        common_index(high, low, close),
        order=order,
        roles={"pivot": order[0], "bottom": order[1], "top": order[2]},
    )


@indicator(
    category="advanced",
    summary="Regular and hidden divergences between price swings and an oscillator.",
    lesson="divergences",
    outputs=("DIVREGBULL", "DIVREGBEAR", "DIVHIDBULL", "DIVHIDBEAR"),
)
def divergence(
    high: ArrayLike,
    low: ArrayLike,
    close: ArrayLike,
    oscillator: ArrayLike | None = None,
    osc_length: int = 14,
    left: int = 5,
    right: int = 5,
) -> pd.DataFrame:
    """Regular and hidden divergences between price and an oscillator.

    Comparing the last two confirmed price swings with the oscillator at the same
    bars:

    ===================  ==========================  ==========================
    Type                 Price                       Oscillator
    ===================  ==========================  ==========================
    Regular bearish      Higher high                 Lower high
    Regular bullish      Lower low                   Higher low
    Hidden bearish       Lower high                  Higher high
    Hidden bullish       Higher low                  Lower low
    ===================  ==========================  ==========================

    Regular divergence argues the trend is tiring; hidden divergence argues a
    pullback inside a trend is ending.

    Parameters
    ----------
    high, low, close:
        Price series of equal length.
    oscillator:
        Any oscillator aligned to the same bars. Defaults to ``RSI(osc_length)``
        computed from ``close``.
    osc_length:
        Length of the default RSI. Ignored when ``oscillator`` is supplied.
    left, right:
        Bars required on each side of a swing pivot.

    Returns
    -------
    pandas.DataFrame
        Four ``1.0``/``0.0`` flag columns — ``DIVREGBULL_...``, ``DIVREGBEAR_...``,
        ``DIVHIDBULL_...``, ``DIVHIDBEAR_...`` — set on the bar of the **later**
        pivot of each divergent pair.

    Warning
    -------
    Flags land on the pivot bar, which only becomes knowable ``right`` bars later.
    Shift the output forward by ``right`` before using it in a backtest.

    A divergence is a warning, not a signal: in a strong trend an oscillator can
    diverge repeatedly while price keeps going. Wait for price confirmation.

    Examples
    --------
    >>> import zeonta
    >>> prices = [float(i) for i in range(60)]
    >>> out = zeonta.divergence(prices, prices, prices, left=2, right=2)
    >>> set(out.iloc[-1].dropna().unique()) <= {0.0, 1.0}
    True
    """
    left = validate_length(left, "left")
    right = validate_length(right, "right")
    osc_length = validate_length(osc_length, "osc_length")

    require_aligned_index(high=high, low=low, close=close)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    close_values = as_array(close, "close")
    size = require_same_length(high=high_values, low=low_values, close=close_values)

    if oscillator is None:
        osc_values = rsi(close_values, length=osc_length).to_numpy()
    else:
        require_aligned_index(close=close, oscillator=oscillator)
        osc_values = as_array(oscillator, "oscillator")
        require_same_length(close=close_values, oscillator=osc_values)

    high_flags = _pivot_flags(high_values, left, right, high=True)
    low_flags = _pivot_flags(low_values, left, right, high=False)

    regular_bull = np.zeros(size, dtype="float64")
    regular_bear = np.zeros(size, dtype="float64")
    hidden_bull = np.zeros(size, dtype="float64")
    hidden_bear = np.zeros(size, dtype="float64")

    def scan(flags: np.ndarray, prices: np.ndarray, at_highs: bool) -> None:
        previous = -1
        for i in np.flatnonzero(flags):
            if previous >= 0 and np.isfinite(osc_values[i]) and np.isfinite(osc_values[previous]):
                price_up = prices[i] > prices[previous]
                osc_up = osc_values[i] > osc_values[previous]
                if at_highs:
                    if price_up and not osc_up:
                        regular_bear[i] = 1.0
                    elif not price_up and osc_up:
                        hidden_bear[i] = 1.0
                elif not price_up and osc_up:
                    regular_bull[i] = 1.0
                elif price_up and not osc_up:
                    hidden_bull[i] = 1.0
            previous = int(i)

    scan(high_flags, high_values, at_highs=True)
    scan(low_flags, low_values, at_highs=False)

    suffix = f"{left}_{right}"
    order = [
        f"DIVREGBULL_{suffix}",
        f"DIVREGBEAR_{suffix}",
        f"DIVHIDBULL_{suffix}",
        f"DIVHIDBEAR_{suffix}",
    ]
    return wrap_frame(
        dict(zip(order, (regular_bull, regular_bear, hidden_bull, hidden_bear), strict=True)),
        common_index(high, low, close),
        order=order,
        roles={
            "regular_bullish": order[0],
            "regular_bearish": order[1],
            "hidden_bullish": order[2],
            "hidden_bearish": order[3],
        },
    )


def _rescaled_range(segment: np.ndarray, lag: int) -> float | None:
    """Mean R/S ratio over ``segment`` split into non-overlapping chunks of *lag*.

    ``None`` when no chunk has a non-zero standard deviation (the ratio is
    undefined there, e.g. every chunk is a flat run).
    """
    chunk_count = segment.shape[0] // lag
    ratios = []
    for c in range(chunk_count):
        chunk = segment[c * lag : (c + 1) * lag]
        deviations = np.cumsum(chunk - chunk.mean())
        spread = chunk.std()
        if spread > 0.0:
            ratios.append((deviations.max() - deviations.min()) / spread)
    return float(np.mean(ratios)) if ratios else None


@indicator(
    category="advanced",
    summary="How persistent recent price moves are: trending, mean-reverting, or a random walk.",
    reference="https://en.wikipedia.org/wiki/Hurst_exponent",
    outputs=("HURST",),
)
def hurst_exponent(close: ArrayLike, window: int = 100) -> pd.Series:
    """Hurst Exponent via Rescaled Range (R/S) analysis.

    For each rolling window of log returns, R/S is computed at several
    sub-period lengths (powers of two from 8 up to half the window): split
    the window into non-overlapping chunks of that length, take the
    range of each chunk's cumulative mean-adjusted deviation divided by
    its standard deviation, and average across chunks. The Hurst exponent
    is the slope of ``log(R/S)`` regressed against ``log(lag)`` — the rate
    the rescaled range grows as the sample gets longer.

    Parameters
    ----------
    close:
        Closing prices.
    window:
        Rolling look-back, in bars. Must be >= 32 (enough for at least two
        lag values — 8 and 16 — to regress against).

    Returns
    -------
    pandas.Series
        Named ``HURST_{window}``. Conventionally read as: ``H ≈ 0.5`` a
        random walk with no memory; ``H > 0.5`` trending/persistent (a move
        tends to be followed by more of the same); ``H < 0.5``
        mean-reverting/anti-persistent (a move tends to be followed by a
        reversal). ``NaN`` wherever every chunk of every lag happens to be
        perfectly flat (no lag produces a usable R/S ratio).

    Notes
    -----
    R/S analysis is the classical (1951) estimator and the one most widely
    cross-referenced; other methods (DFA, the generalized Hurst exponent)
    exist and do not always agree with R/S on the same data — this is an
    estimate from one specific, standard method, not a settled physical
    constant of the series. The choice of lag values (powers of two from 8)
    is this implementation's own, reasoned choice; no source surveyed
    states one canonical lag set.

    Unlike every other indicator in this library, this one is not O(n):
    every bar re-runs a small regression over several lag values, each
    re-scanning its own window. On 10,000 bars this takes on the order of a
    second rather than the low milliseconds typical elsewhere (see
    ``BENCHMARKS.md``) — expected, not a bug, given what the computation
    actually does.

    Examples
    --------
    >>> import zeonta
    >>> import numpy as np
    >>> rng = np.random.default_rng(0)
    >>> walk = 100.0 + np.cumsum(rng.normal(size=200))
    >>> result = zeonta.hurst_exponent(walk, window=64)
    >>> bool(0.0 <= result.dropna().iloc[-1] <= 1.5)
    True

    References
    ----------
    https://en.wikipedia.org/wiki/Hurst_exponent
    """
    window = validate_length(window, minimum=32)
    values = as_array(close, "close")
    size = values.shape[0]

    with np.errstate(divide="ignore", invalid="ignore"):
        log_returns = np.diff(np.log(values), prepend=np.nan)

    lags = []
    lag = 8
    while lag <= window // 2:
        lags.append(lag)
        lag *= 2

    result = np.full(size, np.nan, dtype="float64")
    for i in range(window, size + 1):
        segment = log_returns[i - window : i]
        if not np.all(np.isfinite(segment)):
            continue
        log_lags = []
        log_rs = []
        for n in lags:
            rs = _rescaled_range(segment, n)
            if rs is not None:
                log_lags.append(np.log(n))
                log_rs.append(np.log(rs))
        if len(log_lags) >= 2:
            slope, _ = np.polyfit(log_lags, log_rs, 1)
            result[i - 1] = slope

    return wrap_series(result, common_index(close), f"HURST_{window}")


@indicator(
    category="advanced",
    summary="Ornstein-Uhlenbeck half-life: bars until a mean-reverting series closes half its gap.",
    reference="https://en.wikipedia.org/wiki/Ornstein%E2%80%93Uhlenbeck_process",
    outputs=("OUHL",),
)
def ou_half_life(close: ArrayLike, window: int = 100) -> pd.Series:
    """Ornstein-Uhlenbeck Half-Life of Mean Reversion.

    Fits the discretised Ornstein-Uhlenbeck process to a rolling *window*
    of price by ordinary least squares: regress each bar's change,
    ``Close[t] - Close[t-1]``, against the *prior* close, ``Close[t-1]``::

        Close[t] - Close[t-1] = lambda * Close[t-1] + c + error

    ``lambda`` (the fitted slope) is the discrete-time mean-reversion
    speed: negative means the series pulls back toward its own recent
    level, positive or zero means it does not (a trend or a random walk).
    Half-life converts that speed into bars::

        OUHL = -ln(2) / lambda            (lambda < 0)
        OUHL = NaN                        (lambda >= 0, no mean reversion)

    This is the number of bars for the gap between price and its
    implied long-run level to close by half, under the fitted process —
    the standard way this method gets used to pick a *lookback length*
    for a mean-reversion strategy, rather than as a signal on its own.

    Parameters
    ----------
    close:
        Closing prices.
    window:
        Bars per rolling regression. Must be >= 3 (an OLS fit through 2
        points is exact and uninformative).

    Returns
    -------
    pandas.Series
        Named ``OUHL_{window}``. The first ``window`` bars are ``NaN`` —
        the regression needs ``window`` consecutive bar-to-bar changes,
        one more price bar than that. Also ``NaN`` wherever the fitted
        ``lambda`` is >= 0.

    Examples
    --------
    >>> import numpy as np
    >>> import zeonta
    >>> rng = np.random.default_rng(0)
    >>> noise = rng.normal(scale=1.0, size=150)
    >>> mean_reverting = 100.0 + np.convolve(noise, [0.6**k for k in range(20)])[:150]
    >>> result = zeonta.ou_half_life(mean_reverting, window=100)
    >>> bool(result.iloc[-1] > 0)
    True

    References
    ----------
    https://en.wikipedia.org/wiki/Ornstein%E2%80%93Uhlenbeck_process
    """
    window = validate_length(window, "window", minimum=3)
    values = as_array(close, "close")
    size = values.shape[0]

    result = np.full(size, np.nan, dtype="float64")
    if size < window + 1:
        return wrap_series(result, common_index(close), f"OUHL_{window}")

    y_lag = values[:-1]
    dy = values[1:] - values[:-1]

    x_windows = sliding_window_view(y_lag, window)
    y_windows = sliding_window_view(dy, window)
    sum_x = x_windows.sum(axis=1)
    sum_y = y_windows.sum(axis=1)
    sum_xy = (x_windows * y_windows).sum(axis=1)
    sum_xx = (x_windows * x_windows).sum(axis=1)

    denominator = window * sum_xx - sum_x * sum_x
    with np.errstate(divide="ignore", invalid="ignore"):
        lam = np.where(denominator != 0.0, (window * sum_xy - sum_x * sum_y) / denominator, np.nan)
        half_life = np.where(lam < 0.0, -np.log(2.0) / lam, np.nan)

    result[window:] = half_life
    return wrap_series(result, common_index(close), f"OUHL_{window}")


def _dfa_fluctuation(profile: np.ndarray, box_size: int) -> float:
    """Pooled RMS residual of *profile* detrended box-by-box at *box_size*.

    Vectorised, batch-OLS equivalent of fitting a separate least-squares
    line to every non-overlapping box of length ``box_size`` and pooling
    every box's squared residuals into one RMS — checked against a
    straightforward per-box ``np.polyfit`` loop while this was written.
    """
    n_boxes = profile.shape[0] // box_size
    used = profile[: n_boxes * box_size].reshape(n_boxes, box_size)
    x = np.arange(box_size, dtype="float64")
    sum_x = x.sum()
    sum_xx = (x * x).sum()
    sum_y = used.sum(axis=1)
    sum_xy = used @ x
    denominator = box_size * sum_xx - sum_x * sum_x
    slope = (box_size * sum_xy - sum_x * sum_y) / denominator
    intercept = (sum_y - slope * sum_x) / box_size
    trend = intercept[:, None] + slope[:, None] * x[None, :]
    residual = used - trend
    return float(np.sqrt(np.mean(residual * residual)))


@indicator(
    category="advanced",
    summary="Detrended Fluctuation Analysis: a scaling exponent for persistence, robust to trends.",
    reference="https://doi.org/10.1103/PhysRevE.49.1685",
    outputs=("DFA",),
)
def dfa(close: ArrayLike, window: int = 100) -> pd.Series:
    """Detrended Fluctuation Analysis (Peng et al., 1994).

    Estimates the same kind of scaling exponent :func:`hurst_exponent`
    does, from the same input — a rolling window of *log returns*, not
    raw price — by a different, later method designed specifically to
    stay reliable on *non-stationary* data, where :func:`hurst_exponent`'s
    classical R/S analysis can be biased. DFA integrates the return
    window into its own profile as its first step::

        profile[k] = cumsum(log_returns_window - mean(log_returns_window))[k]

    For each of several box sizes ``n``: split ``profile`` into
    non-overlapping boxes of length ``n``, fit and remove a local linear
    trend from each box (the "detrended" step — the reason DFA tolerates
    non-stationarity that R/S does not), and pool every box's squared
    residual into one RMS fluctuation, ``F(n)``. The DFA exponent is the
    slope of ``log(F(n))`` regressed against ``log(n)``.

    Parameters
    ----------
    close:
        Closing prices.
    window:
        Rolling look-back, in log returns. Must be >= 32, so at least two
        box sizes (4 and 8 bars) fit within ``window // 4``.

    Returns
    -------
    pandas.Series
        Named ``DFA_{window}``.

    Notes
    -----
    Reads the same way as :func:`hurst_exponent`: ``alpha ~= 0.5`` is an
    uncorrelated random walk, ``alpha > 0.5`` persistent/trending,
    ``alpha < 0.5`` anti-persistent/mean-reverting — but this is a
    *different, later* estimator (1994 vs. R/S's 1951) applied to the same
    kind of input, not a second opinion computed the same way. Like
    `hurst_exponent`, this is a per-bar rolling regression over several
    box sizes rather than a single vectorised pass — measure it on your
    own data before a large history (see `BENCHMARKS.md`).

    Examples
    --------
    >>> import numpy as np
    >>> import zeonta
    >>> rng = np.random.default_rng(0)
    >>> walk = 100.0 * np.cumprod(1.0 + rng.normal(scale=0.01, size=150))
    >>> result = zeonta.dfa(walk, window=100)
    >>> bool(0.0 < result.iloc[-1] < 1.5)
    True

    References
    ----------
    https://doi.org/10.1103/PhysRevE.49.1685
    """
    window = validate_length(window, "window", minimum=32)
    values = as_array(close, "close")
    size = values.shape[0]
    with np.errstate(divide="ignore", invalid="ignore"):
        log_returns = np.diff(np.log(values), prepend=np.nan)

    box_sizes: list[int] = []
    box = 4
    while box <= window // 4:
        box_sizes.append(box)
        box *= 2

    result = np.full(size, np.nan, dtype="float64")
    for i in range(window, size + 1):
        segment = log_returns[i - window : i]
        if not np.all(np.isfinite(segment)):
            continue
        profile = np.cumsum(segment - segment.mean())
        log_boxes = []
        log_f = []
        for box_size in box_sizes:
            fluctuation = _dfa_fluctuation(profile, box_size)
            if fluctuation > 0.0:
                log_boxes.append(np.log(box_size))
                log_f.append(np.log(fluctuation))
        if len(log_boxes) >= 2:
            slope, _ = np.polyfit(log_boxes, log_f, 1)
            result[i - 1] = slope

    return wrap_series(result, common_index(close), f"DFA_{window}")


def _sample_entropy_value(segment: np.ndarray, m: int, tolerance: float) -> float:
    """Sample Entropy of one *segment*, Richman & Moorman (2000).

    ``tolerance`` is an absolute distance already (the caller scales it
    from *segment*'s own standard deviation) — this only implements the
    template-matching count.
    """
    template_count = segment.shape[0] - m
    if template_count < 2:
        return np.nan

    index_m = np.arange(template_count)[:, None] + np.arange(m)[None, :]
    vectors_m = segment[index_m]
    index_m1 = np.arange(template_count)[:, None] + np.arange(m + 1)[None, :]
    vectors_m1 = segment[index_m1]

    # Chebyshev (L-infinity) distance between every pair of templates.
    distance_m = np.abs(vectors_m[:, None, :] - vectors_m[None, :, :]).max(axis=2)
    distance_m1 = np.abs(vectors_m1[:, None, :] - vectors_m1[None, :, :]).max(axis=2)
    np.fill_diagonal(distance_m, np.inf)  # no self-matches, unlike Approximate Entropy
    np.fill_diagonal(distance_m1, np.inf)

    b_count = np.count_nonzero(distance_m <= tolerance)
    a_count = np.count_nonzero(distance_m1 <= tolerance)
    if b_count == 0 or a_count == 0:
        return np.nan
    return float(-np.log(a_count / b_count))


@indicator(
    category="advanced",
    summary="Sample Entropy: how unpredictable a series is, from 0 (regular) upward (irregular).",
    reference="https://physionet.org/content/sampen/1.0.0/",
    outputs=("SAMPEN",),
)
def sample_entropy(close: ArrayLike, window: int = 100, m: int = 2, r: Number = 0.2) -> pd.Series:
    """Sample Entropy (Richman & Moorman, 2000).

    Measures how *unpredictable* a rolling window of log returns is,
    independent of its scale of persistence — a different question from
    :func:`hurst_exponent`/:func:`dfa`, which ask whether a series trends
    or reverts, not how noisy it is at either extreme.

    Builds every length-``m`` and length-``m+1`` "template" vector from
    the window and counts, at each length, how many *different* templates
    are within tolerance ``r`` of each other (Chebyshev/L-infinity
    distance, self-matches excluded — the fix Sample Entropy makes over
    the older, self-match-biased Approximate Entropy)::

        SampEn = -ln(A / B)

    where ``B`` counts length-``m`` matches and ``A`` counts length-
    ``(m+1)`` matches, both over the same template positions. A window
    that keeps repeating short patterns matches often at both lengths
    (``A/B`` close to 1, ``SampEn`` near 0); a window with no repeating
    structure barely matches at all (``SampEn`` large).

    Parameters
    ----------
    close:
        Closing prices.
    window:
        Bars per rolling estimate, in log returns. Must be >= 20.
    m:
        Template length. Richman & Moorman's own examples use ``2``
        (the default); must be >= 1.
    r:
        Matching tolerance as a fraction of the window's own standard
        deviation (the standard scale-free convention) — the *actual*
        Chebyshev distance threshold is ``r * std(window)``. Richman &
        Moorman recommend ``0.1`` to ``0.25``; ``0.2`` (the default) is
        their own most-used value. Must be > 0.

    Returns
    -------
    pandas.Series
        Named ``SAMPEN_{window}_{m}_{r}``. ``NaN`` wherever a window has
        too few matches at either template length to form a ratio
        (a very short or very tightly-toleranced window).

    Notes
    -----
    Every bar compares every pair of templates in its own *window* —
    ``O(window^2)`` per bar, not the single vectorised pass most other
    indicators here use, and slower again than :func:`hurst_exponent` or
    :func:`dfa`'s own per-bar loops (see `BENCHMARKS.md`).

    Examples
    --------
    >>> import numpy as np
    >>> import zeonta
    >>> rng = np.random.default_rng(0)
    >>> noisy = 100.0 * np.cumprod(1.0 + rng.normal(scale=0.01, size=150))
    >>> result = zeonta.sample_entropy(noisy, window=100)
    >>> bool(result.iloc[-1] > 0.0)
    True

    References
    ----------
    https://physionet.org/content/sampen/1.0.0/
    """
    window = validate_length(window, "window", minimum=20)
    if not isinstance(m, (int, np.integer)) or isinstance(m, bool) or m < 1:
        raise ValueError(f"'m' must be an integer >= 1, got {m!r}")
    r = validate_multiplier(r, "r")

    values = as_array(close, "close")
    size = values.shape[0]
    with np.errstate(divide="ignore", invalid="ignore"):
        log_returns = np.diff(np.log(values), prepend=np.nan)

    result = np.full(size, np.nan, dtype="float64")
    for i in range(window, size + 1):
        segment = log_returns[i - window : i]
        if not np.all(np.isfinite(segment)):
            continue
        tolerance = r * segment.std()
        if tolerance == 0.0:
            continue
        result[i - 1] = _sample_entropy_value(segment, m, tolerance)

    return wrap_series(result, common_index(close), f"SAMPEN_{window}_{m}_{r}")


def _approximate_entropy_value(segment: np.ndarray, m: int, tolerance: float) -> float:
    """Approximate Entropy of one *segment*, Pincus (1991).

    Unlike :func:`_sample_entropy_value`, self-matches are *not* excluded
    (a template always matches itself at distance 0) — the very bias
    Sample Entropy was later designed to remove.
    """

    def phi(length: int) -> float:
        count = segment.shape[0] - length + 1
        index = np.arange(count)[:, None] + np.arange(length)[None, :]
        vectors = segment[index]
        distance = np.abs(vectors[:, None, :] - vectors[None, :, :]).max(axis=2)
        matches = np.count_nonzero(distance <= tolerance, axis=1)
        return float(np.mean(np.log(matches / count)))

    return phi(m) - phi(m + 1)


@indicator(
    category="advanced",
    summary="How unpredictable a window is — sample_entropy's older, self-match-biased ancestor.",
    outputs=("APEN",),
    reference="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC54970/",
)
def approximate_entropy(
    close: ArrayLike, window: int = 100, m: int = 2, r: Number = 0.2
) -> pd.Series:
    """Approximate Entropy (Pincus, 1991).

    :func:`sample_entropy`'s predecessor, and the whole reason Sample
    Entropy exists: it counts template matches the same way, but counts a
    template as matching *itself* (distance 0, always within tolerance),
    which biases every count upward and makes the statistic depend more
    on the window length than Sample Entropy does::

        ApEn = phi(m) - phi(m+1)

    where ``phi(k) = mean(ln(C_i^k))`` over every length-``k`` template
    ``i``, and ``C_i^k`` is the fraction of *all* length-``k`` templates
    (including ``i`` itself) within tolerance ``r`` of template ``i``.

    Parameters
    ----------
    close:
        Closing prices.
    window:
        Bars per rolling estimate, in log returns. Must be >= 20.
    m:
        Template length. Pincus's own examples use ``2`` (the default);
        must be >= 1.
    r:
        Matching tolerance as a fraction of the window's own standard
        deviation — the *actual* Chebyshev distance threshold is
        ``r * std(window)``. ``0.2`` (the default) is the conventional
        choice, shared with :func:`sample_entropy`. Must be > 0.

    Returns
    -------
    pandas.Series
        Named ``APEN_{window}_{m}_{r}``. Never negative in this
        self-match-inclusive form (unlike :func:`sample_entropy`, which
        can be undefined when a window's tightest tolerance still finds
        no matches at all).

    Notes
    -----
    Kept here for the reader who specifically wants Pincus's original
    statistic — for new work, :func:`sample_entropy` corrects the two
    biases (self-matches, and sensitivity to window length) this
    estimator has by construction. Same ``O(window^2)`` per-bar cost as
    :func:`sample_entropy`; see `BENCHMARKS.md`.

    Examples
    --------
    >>> import numpy as np
    >>> import zeonta
    >>> rng = np.random.default_rng(0)
    >>> noisy = 100.0 * np.cumprod(1.0 + rng.normal(scale=0.01, size=150))
    >>> result = zeonta.approximate_entropy(noisy, window=100)
    >>> bool(result.iloc[-1] > 0.0)
    True

    References
    ----------
    https://www.ncbi.nlm.nih.gov/pmc/articles/PMC54970/
    """
    window = validate_length(window, "window", minimum=20)
    if not isinstance(m, (int, np.integer)) or isinstance(m, bool) or m < 1:
        raise ValueError(f"'m' must be an integer >= 1, got {m!r}")
    r = validate_multiplier(r, "r")

    values = as_array(close, "close")
    size = values.shape[0]
    with np.errstate(divide="ignore", invalid="ignore"):
        log_returns = np.diff(np.log(values), prepend=np.nan)

    result = np.full(size, np.nan, dtype="float64")
    for i in range(window, size + 1):
        segment = log_returns[i - window : i]
        if not np.all(np.isfinite(segment)):
            continue
        tolerance = r * segment.std()
        if tolerance == 0.0:
            continue
        result[i - 1] = _approximate_entropy_value(segment, m, tolerance)

    return wrap_series(result, common_index(close), f"APEN_{window}_{m}_{r}")


def _ordinal_pattern_counts(segment: np.ndarray, order: int, delay: int) -> np.ndarray:
    """Count which ordinal pattern each overlapping length-``order`` window matches.

    Windows are spaced ``delay`` bars apart; ties are broken by index, the
    conventional Bandt-Pompe rule.
    """
    span = (order - 1) * delay + 1
    count = segment.shape[0] - span + 1
    index = np.arange(count)[:, None] + np.arange(0, span, delay)[None, :]
    windows = segment[index]
    # argsort of argsort gives each element's rank within its own window,
    # which is exactly the ordinal pattern Bandt & Pompe define.
    patterns = np.argsort(np.argsort(windows, axis=1, kind="stable"), axis=1, kind="stable")
    _, counts = np.unique(patterns, axis=0, return_counts=True)
    return counts


@indicator(
    category="advanced",
    summary="Shannon entropy of a window's own ordinal (up/down) patterns, ignoring move size.",
    outputs=("PERMEN",),
    reference="https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.88.174102",
)
def permutation_entropy(
    close: ArrayLike, window: int = 100, order: int = 3, delay: int = 1
) -> pd.Series:
    """Permutation Entropy (Bandt & Pompe, 2002).

    Reduces every overlapping length-``order`` slice of a rolling window
    to the *ordering* of its values (which of the ``order!`` possible
    orderings it matches — "up then down then up", say — never their
    actual size), then takes the Shannon entropy of how often each
    ordering occurred::

        PERMEN = -sum(p_i * ln(p_i))

    over every ordering ``i`` that appeared, ``p_i`` its observed
    frequency. A window that keeps repeating the same up/down shape has
    low permutation entropy; one with no preferred shape at all
    approaches ``ln(order!)``, the maximum for that ``order``.

    Parameters
    ----------
    close:
        Closing prices.
    window:
        Bars per rolling estimate. Must be >= 20.
    order:
        Length of each ordinal pattern (the embedding dimension). Bandt &
        Pompe's own examples use ``3`` to ``7``; must be >= 2, and
        ``window`` must be able to hold at least a few non-overlapping
        patterns of this length.
    delay:
        Spacing, in bars, between the points that make up one pattern.
        ``1`` (the default) compares consecutive bars; a larger delay
        looks for the same up/down shape at a slower pace. Must be >= 1.

    Returns
    -------
    pandas.Series
        Named ``PERMEN_{window}_{order}_{delay}``, in nats (natural-log
        units) — divide by ``ln(order!)`` for the normalized 0-1 form
        some other software reports instead.

    Notes
    -----
    Ties within a window (two equal prices) are broken by position, the
    conventional Bandt-Pompe rule — a run of identical prices is treated
    as already sorted, not as an error.

    Examples
    --------
    >>> import numpy as np
    >>> import zeonta
    >>> rng = np.random.default_rng(0)
    >>> noisy = 100.0 * np.cumprod(1.0 + rng.normal(scale=0.01, size=150))
    >>> result = zeonta.permutation_entropy(noisy, window=100, order=3)
    >>> bool(result.iloc[-1] > 0.0)
    True

    References
    ----------
    https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.88.174102
    """
    window = validate_length(window, "window", minimum=20)
    if not isinstance(order, (int, np.integer)) or isinstance(order, bool) or order < 2:
        raise ValueError(f"'order' must be an integer >= 2, got {order!r}")
    delay = validate_length(delay, "delay")
    span = (order - 1) * delay + 1
    if window < span + 1:
        raise ValueError(
            f"'window' must be large enough to hold at least two length-{order} "
            f"patterns spaced {delay} apart (>= {span + 1}), got {window}"
        )

    values = as_array(close, "close")
    size = values.shape[0]

    result = np.full(size, np.nan, dtype="float64")
    for i in range(window, size + 1):
        segment = values[i - window : i]
        if not np.all(np.isfinite(segment)):
            continue
        counts = _ordinal_pattern_counts(segment, order, delay)
        probabilities = counts / counts.sum()
        result[i - 1] = float(-np.sum(probabilities * np.log(probabilities)))

    return wrap_series(result, common_index(close), f"PERMEN_{window}_{order}_{delay}")
