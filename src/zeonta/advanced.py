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
    "cusum_filter",
    "dfa",
    "divergence",
    "fib_retracement",
    "higuchi_fractal_dimension",
    "hurst_exponent",
    "kl_divergence",
    "markov_regime_switching",
    "multifractal_dfa",
    "multiscale_entropy",
    "ou_half_life",
    "permutation_entropy",
    "pivot_points",
    "sample_entropy",
    "shannon_entropy",
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


def _higuchi_fd_value(segment: np.ndarray, k_max: int) -> float:
    """Higuchi Fractal Dimension of one *segment* (Higuchi, 1988).

    For each ``k`` from 1 to *k_max*, builds ``k`` sub-series (one per
    offset ``m``) by sampling ``segment`` every ``k``-th point starting at
    ``m``, measures each sub-series' own mean curve length ``L_m(k)``, and
    averages them into ``L(k)``. The returned value is the slope of
    ``log(L(k))`` regressed against ``log(1/k)`` — the rate curve length
    shrinks as the sampling step widens.
    """
    n = segment.shape[0]
    log_inv_k = []
    log_length = []
    for k in range(1, k_max + 1):
        lengths = []
        for m in range(1, k + 1):
            # n_max = floor((n-m)/k) is always >= 1 here: the caller only ever
            # passes a segment of length n = window >= 2*k_max (enforced by
            # this function's own validation), so n-m >= n-k_max >= k_max >= k.
            n_max = (n - m) // k
            index = (m - 1) + np.arange(n_max + 1) * k
            curve_length = np.abs(np.diff(segment[index])).sum() * (n - 1) / (n_max * k * k)
            lengths.append(curve_length)
        if lengths:
            average_length = float(np.mean(lengths))
            if average_length > 0.0:
                log_inv_k.append(np.log(1.0 / k))
                log_length.append(np.log(average_length))
    if len(log_inv_k) < 2:
        return np.nan
    slope, _ = np.polyfit(log_inv_k, log_length, 1)
    return float(slope)


@indicator(
    category="advanced",
    summary="Fractal dimension of price itself, from curve-length scaling (Higuchi, 1988).",
    reference="https://doi.org/10.1016/0167-2789(88)90081-4",
    outputs=("HFD",),
)
def higuchi_fractal_dimension(close: ArrayLike, window: int = 100, k_max: int = 10) -> pd.Series:
    """Higuchi Fractal Dimension (Higuchi, 1988).

    Measures the fractal dimension of the rolling window's own price path —
    a different question from :func:`hurst_exponent`/:func:`dfa` (which
    estimate a scaling exponent from *returns*) and from :func:`frama`'s
    internal box-counting dimension (which compares high-low *range* at two
    scales over a fixed short window). Higuchi's method instead works
    directly on price, by literally re-sampling the window at ``k`` step
    sizes for ``k = 1 .. k_max``, measuring how much each re-sampled curve's
    total length shrinks as the step widens::

        L_m(k) = (N-1)/(floor((N-m)/k)*k^2) *
                 sum_{i=1..floor((N-m)/k)} |x(m+i*k) - x(m+(i-1)*k)|
        L(k)   = mean over m=1..k of L_m(k)
        HFD    = slope of log(L(k)) regressed against log(1/k), k=1..k_max

    where ``N`` is *window* and ``x`` is the window's own price series
    (0-indexed here; ``m`` ranges 1..k as in Higuchi's own paper). A curve
    that fills a straight line has ``HFD`` near ``1``; one that fills the
    plane as roughly as pure noise approaches ``2`` — the same reading
    convention as any box-counting fractal dimension, :func:`frama`'s
    included.

    Parameters
    ----------
    close:
        Closing prices.
    window:
        Rolling look-back, in bars. Must be >= ``2 * k_max`` so the largest
        step size still has room for at least one full sub-series.
    k_max:
        Largest step size sampled. Higuchi's own paper leaves this a free
        choice; ``10`` is the value most commonly used in the literature
        that has followed it (electroencephalography and other biomedical
        signal-processing applications, where this estimator is most
        widely used). Must be an integer >= 2 (at least two step sizes are
        needed to regress a slope at all).

    Returns
    -------
    pandas.Series
        Named ``HFD_{window}_{k_max}``, nominally in ``[1, 2]`` (a noisy
        short window can push the fitted slope slightly outside that
        range). ``NaN`` for warm-up bars and for any window producing
        fewer than two usable ``(k, L(k))`` pairs to regress against
        (e.g. every re-sampling degenerates to a single repeated value).

    Notes
    -----
    Like :func:`hurst_exponent` and :func:`dfa`, this is a per-bar loop
    over several step sizes rather than a single vectorised pass — this
    library's usual O(1)-per-bar shape does not apply here (see
    ``BENCHMARKS.md`` for the comparable indicators it does cover).

    Examples
    --------
    >>> import zeonta
    >>> import numpy as np
    >>> rng = np.random.default_rng(0)
    >>> walk = 100.0 + np.cumsum(rng.normal(size=200))
    >>> result = zeonta.higuchi_fractal_dimension(walk, window=100, k_max=10)
    >>> bool(1.0 <= result.dropna().iloc[-1] <= 2.0)
    True

    References
    ----------
    https://doi.org/10.1016/0167-2789(88)90081-4
    """
    if isinstance(k_max, bool) or not isinstance(k_max, (int, np.integer)) or k_max < 2:
        raise ValueError(f"'k_max' must be an integer >= 2, got {k_max!r}")
    k_max = int(k_max)
    window = validate_length(window, minimum=2 * k_max)
    values = as_array(close, "close")
    size = values.shape[0]

    result = np.full(size, np.nan, dtype="float64")
    for i in range(window, size + 1):
        segment = values[i - window : i]
        if not np.all(np.isfinite(segment)):
            continue
        result[i - 1] = _higuchi_fd_value(segment, k_max)

    return wrap_series(result, common_index(close), f"HFD_{window}_{k_max}")


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


#: Floor applied to every fitted/estimated variance (Hamilton filter density
#: evaluation and the EM M-step) so a state that momentarily explains only a
#: handful of points can't collapse its variance to exactly zero and blow up
#: the density evaluated at that point.
_MRSW_VARIANCE_FLOOR = 1e-12

#: Floor applied to every transition probability and to the denominator used
#: to normalise the Hamilton filter's predictive mixture, keeping every
#: recursion well-defined (no divide-by-zero) even on a degenerate/flat
#: segment. Transition probabilities are kept within
#: ``[_MRSW_PROB_FLOOR, 1 - _MRSW_PROB_FLOOR]``.
_MRSW_PROB_FLOOR = 1e-6


def _markov_stationary_distribution(p00: float, p11: float) -> np.ndarray:
    """Stationary distribution ``[P(S=0), P(S=1)]`` of the 2-state chain.

    Falls back to ``[0.5, 0.5]`` when the chain is (numerically) degenerate,
    e.g. ``p00 = p11 = 1`` (no mixing at all, so no well-defined stationary
    distribution exists). Every ``p00``/``p11`` this module actually passes
    in is either the fixed ``0.9`` seed or already kept within
    ``[_MRSW_PROB_FLOOR, 1 - _MRSW_PROB_FLOOR]`` by :func:`_markov_m_step`,
    so this branch is a defensive guard, not a reachable path today.
    """
    denominator = (1.0 - p00) + (1.0 - p11)
    if denominator < _MRSW_PROB_FLOOR:  # pragma: no cover - defensive; see docstring
        return np.array([0.5, 0.5])
    pi0 = (1.0 - p11) / denominator
    return np.array([pi0, 1.0 - pi0])


def _markov_hamilton_filter(
    y: np.ndarray, mu: np.ndarray, sigma2: np.ndarray, p00: float, p11: float
) -> tuple[np.ndarray, np.ndarray, float]:
    """Hamilton (1989) forward filter for one segment of log returns.

    Returns ``filtered[t, j] = P(S_t=j | Y_1..Y_t)``,
    ``predicted[t, j] = P(S_t=j | Y_1..Y_{t-1})`` (the one-step-ahead
    prediction the Kim smoother needs), and the segment's log-likelihood
    under ``mu``/``sigma2``/``p00``/``p11``.
    """
    size = y.shape[0]
    transition = np.array([[p00, 1.0 - p00], [1.0 - p11, p11]])
    sigma2_floored = np.maximum(sigma2, _MRSW_VARIANCE_FLOOR)
    probability = _markov_stationary_distribution(p00, p11)

    filtered = np.empty((size, 2))
    predicted = np.empty((size, 2))
    log_likelihood = 0.0
    for t in range(size):
        predicted_t = probability @ transition
        density = np.exp(-0.5 * (y[t] - mu) ** 2 / sigma2_floored) / np.sqrt(
            2.0 * np.pi * sigma2_floored
        )
        joint = predicted_t * density
        total = max(float(joint.sum()), _MRSW_VARIANCE_FLOOR)
        probability = joint / total
        log_likelihood += np.log(total)
        filtered[t] = probability
        predicted[t] = predicted_t

    return filtered, predicted, float(log_likelihood)


def _markov_kim_smoother(
    filtered: np.ndarray, predicted: np.ndarray, p00: float, p11: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Kim (1994) backward smoother, given one Hamilton filter pass.

    Returns ``smoothed[t, j] = P(S_t=j | Y_1..Y_T)`` (``gamma_t(j)``), the
    segment-summed transition counts ``sum_t xi_t(i, j)`` for
    ``t = 2..T`` (0-indexed transitions ``0..T-2``), and
    ``sum_t smoothed[t, i]`` over that same range (the M-step's transition
    denominator, ``sum_t gamma_{t-1}(i)``).
    """
    transition = np.array([[p00, 1.0 - p00], [1.0 - p11, p11]])
    size = filtered.shape[0]
    smoothed = np.empty_like(filtered)
    smoothed[-1] = filtered[-1]
    xi_sum = np.zeros((2, 2))
    gamma_prior_sum = np.zeros(2)
    for t in range(size - 2, -1, -1):
        ratio = smoothed[t + 1] / np.maximum(predicted[t + 1], _MRSW_VARIANCE_FLOOR)
        xi_t = filtered[t][:, None] * transition * ratio[None, :]
        xi_sum += xi_t
        smoothed[t] = xi_t.sum(axis=1)
        gamma_prior_sum += smoothed[t]

    return smoothed, xi_sum, gamma_prior_sum


def _markov_m_step(
    y: np.ndarray, smoothed: np.ndarray, xi_sum: np.ndarray, gamma_prior_sum: np.ndarray
) -> tuple[np.ndarray, np.ndarray, float, float]:
    """Closed-form EM M-step update from one E-step's gamma/xi."""
    totals = np.maximum(smoothed.sum(axis=0), _MRSW_VARIANCE_FLOOR)
    mu = (smoothed * y[:, None]).sum(axis=0) / totals
    sigma2 = (smoothed * (y[:, None] - mu[None, :]) ** 2).sum(axis=0) / totals
    sigma2 = np.maximum(sigma2, _MRSW_VARIANCE_FLOOR)

    gamma_prior = np.maximum(gamma_prior_sum, _MRSW_VARIANCE_FLOOR)
    p00 = float(np.clip(xi_sum[0, 0] / gamma_prior[0], _MRSW_PROB_FLOOR, 1.0 - _MRSW_PROB_FLOOR))
    p11 = float(np.clip(xi_sum[1, 1] / gamma_prior[1], _MRSW_PROB_FLOOR, 1.0 - _MRSW_PROB_FLOOR))
    return mu, sigma2, p00, p11


def _markov_regime_probability(y: np.ndarray, max_iterations: int, tolerance: float) -> float:
    """Fit the 2-state Hamilton model to one *segment* via EM.

    Returns the filtered probability of its higher-variance regime at the
    segment's last bar. Initialisation is fixed and deterministic (see
    :func:`markov_regime_switching`'s docstring): split *y* at its own
    median into a low/high half to seed each state's mean/variance, and
    seed both self-transition probabilities at ``0.9``. EM then alternates
    the Hamilton filter/Kim smoother E-step with the closed-form M-step
    until the segment's log-likelihood improves by less than *tolerance*,
    or *max_iterations* is reached — whichever comes first; the last
    iterate's parameters are used either way.
    """
    median = np.median(y)
    low_half = y[y <= median]
    high_half = y[y > median]
    if low_half.size == 0 or high_half.size == 0:
        # Perfectly flat segment: nothing to split on either side of the
        # median. Seed both states identically; the variance floor below
        # keeps every recursion well-defined regardless.
        low_half = y
        high_half = y

    mu = np.array([low_half.mean(), high_half.mean()])
    sigma2 = np.maximum(np.array([low_half.var(), high_half.var()]), _MRSW_VARIANCE_FLOOR)
    p00 = 0.9
    p11 = 0.9

    previous_log_likelihood: float | None = None
    for _ in range(max_iterations):
        filtered, predicted, log_likelihood = _markov_hamilton_filter(y, mu, sigma2, p00, p11)
        if (
            previous_log_likelihood is not None
            and (log_likelihood - previous_log_likelihood) < tolerance
        ):
            break
        previous_log_likelihood = log_likelihood
        smoothed, xi_sum, gamma_prior_sum = _markov_kim_smoother(filtered, predicted, p00, p11)
        mu, sigma2, p00, p11 = _markov_m_step(y, smoothed, xi_sum, gamma_prior_sum)

    filtered, _, _ = _markov_hamilton_filter(y, mu, sigma2, p00, p11)
    high_variance_state = 1 if sigma2[1] >= sigma2[0] else 0
    return float(filtered[-1, high_variance_state])


@indicator(
    category="advanced",
    summary="Filtered probability the current bar is in a Hamilton 2-state high-volatility regime.",
    outputs=("MRSW",),
    reference="https://www.jstor.org/stable/1912559",
)
def markov_regime_switching(
    close: ArrayLike,
    window: int = 100,
    max_iterations: int = 50,
    tolerance: Number = 1e-6,
) -> pd.Series:
    """Hamilton (1989) 2-state Markov-switching model of log returns.

    Fits ``y_t = mu_{S_t} + eps_t``, ``eps_t ~ N(0, sigma_{S_t}^2)`` on each
    rolling *window* of log returns, where ``S_t in {0, 1}`` is a
    first-order Markov chain with self-transition probabilities ``p00`` and
    ``p11``. Reports the *filtered* probability, ``P(S_t = high | Y_1..t)``,
    that the window's last bar belongs to whichever of the two converged
    states has the larger variance — the "high-volatility" regime.

    Parameters are estimated per window by Expectation-Maximization: the
    E-step runs the Hamilton filter forward and the Kim (1994) smoother
    backward over the window to get each bar's regime probabilities
    (``gamma``) and each bar-pair's transition probabilities (``xi``); the
    M-step re-estimates ``mu``, ``sigma^2`` and the transition matrix from
    those in closed form::

        mu_j      = sum_t(gamma_t(j) * y_t) / sum_t(gamma_t(j))
        sigma_j^2 = sum_t(gamma_t(j) * (y_t - mu_j)^2) / sum_t(gamma_t(j))
        p_ij      = sum_t(xi_t(i, j)) / sum_t(gamma_{t-1}(i))

    repeated until the window's log-likelihood improves by less than
    *tolerance* or *max_iterations* is hit.

    This is the only indicator in this library that fits an iterative
    statistical model rather than evaluating a formula directly — but it
    still passes this project's "single verifiable formula" bar: Hamilton's
    own paper, and every standard reference since (his own 1994 textbook
    *Time Series Analysis* ch. 22; Kim & Nelson (1999) *State-Space Models
    with Regime Switching*), describe exactly this Hamilton-filter/Kim-
    smoother/EM combination. There is no formula ambiguity here, only the
    normal, expected fact that EM is iterative rather than closed-form.

    Parameters
    ----------
    close:
        Closing prices.
    window:
        Bars per rolling re-estimation, in log returns. Must be >= 20 (as
        with :func:`sample_entropy`) — a 2-state model with 6 free
        parameters (two means, two variances, two transition
        probabilities) needs a reasonable minimum sample to estimate at
        all, and this library's other rolling-window statistical
        estimators use the same floor.
    max_iterations:
        EM iteration cap per window, bounding worst-case runtime. EM's own
        convergence is not guaranteed within any fixed number of
        iterations; a window that has not converged by *max_iterations*
        still reports its *last* iterate's estimate, not ``NaN`` — this
        parameter is a safety valve on runtime, not a correctness
        guarantee. Must be an integer >= 1.
    tolerance:
        Log-likelihood improvement, in nats, below which EM stops early.
        Must be > 0.

    Returns
    -------
    pandas.Series
        Named ``MRSW_{window}_{max_iterations}_{tolerance}``, in
        ``[0, 1]``. ``NaN`` for warm-up bars (fewer than *window* log
        returns available yet) and for any window containing a
        non-finite log return. A value near ``1`` means the model is
        confident the current bar sits in the higher-variance of its two
        fitted regimes; near ``0`` means the lower-variance regime —
        which internal EM label ("state 0" vs "state 1") that corresponds
        to is resolved and discarded on every window, since EM's own
        labelling is arbitrary (the well-known "label-switching" problem).

    Notes
    -----
    Deterministic, fixed initialisation, chosen specifically so the same
    input always produces the same output (EM is otherwise sensitive to
    starting values and can converge to different local optima from
    different seeds): each window's own log returns are split at their own
    median into a "low" and "high" half; ``mu``/``sigma^2`` for state 0 and
    state 1 are seeded from the low and high half's own mean/variance;
    both self-transition probabilities are seeded at ``0.9``, the standard
    "regimes are persistent" prior used throughout this literature (a
    regime is assumed to typically last many bars, not flip every bar) —
    not an arbitrary guess. A window whose low/high halves happen to share
    the same variance (a degenerate, flat window) is not special-cased
    beyond the variance floor below; the recursion stays well-defined.

    Every bar re-fits the model from scratch on only the trailing *window*
    bars ending at that bar — the only choice consistent with this
    library's no-look-ahead, aligned-output contract, but also the most
    expensive computation in this library: roughly ``O(window *
    max_iterations)`` per bar, i.e. ``O(size * window * max_iterations)``
    overall, since each of the ``size`` bars re-runs up to
    *max_iterations* full forward/backward passes over its own *window*.
    ``BENCHMARKS.md`` does not cover this indicator (only
    ``supertrend``/``adx``/``parabolic_sar``).

    A variance floor (``1e-12``) and a transition-probability floor
    (keeping every ``p_ij`` within ``[1e-6, 1 - 1e-6]``) are applied inside
    both the Hamilton filter's density evaluation and the M-step's
    parameter updates, so a degenerate or very short window cannot divide
    by zero or produce an undefined log-likelihood.

    Examples
    --------
    >>> import numpy as np
    >>> import zeonta
    >>> rng = np.random.default_rng(0)
    >>> calm = rng.normal(scale=0.002, size=80)
    >>> turbulent = rng.normal(scale=0.03, size=80)
    >>> prices = 100.0 * np.cumprod(1 + np.concatenate([calm, turbulent]))
    >>> result = zeonta.markov_regime_switching(prices, window=60)
    >>> bool(result.iloc[-1] > result.iloc[79])
    True

    References
    ----------
    Hamilton, J.D. (1989). "A New Approach to the Economic Analysis of
    Nonstationary Time Series and the Business Cycle". Econometrica 57(2).
    https://www.jstor.org/stable/1912559
    """
    window = validate_length(window, "window", minimum=20)
    max_iterations = validate_length(max_iterations, "max_iterations", minimum=1)
    tolerance = validate_multiplier(tolerance, "tolerance")

    values = as_array(close, "close")
    size = values.shape[0]
    with np.errstate(divide="ignore", invalid="ignore"):
        log_returns = np.diff(np.log(values), prepend=np.nan)

    result = np.full(size, np.nan, dtype="float64")
    for i in range(window, size + 1):
        segment = log_returns[i - window : i]
        if not np.all(np.isfinite(segment)):
            continue
        result[i - 1] = _markov_regime_probability(segment, max_iterations, tolerance)

    return wrap_series(result, common_index(close), f"MRSW_{window}_{max_iterations}_{tolerance}")


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


def _dfa_box_fluctuations(profile: np.ndarray, box_size: int) -> np.ndarray:
    """Per-box mean squared residual (``F^2(box_size, nu)``) of *profile*.

    Vectorised, batch-OLS equivalent of fitting a separate least-squares
    line to every non-overlapping box of length ``box_size`` and returning
    each box's own mean squared residual — checked against a
    straightforward per-box ``np.polyfit`` loop while this was written.
    Shared by :func:`dfa` (which pools these into one RMS, its ``F(n)``)
    and :func:`multifractal_dfa` (which combines them with a ``q``-th-power
    average instead, its ``F_q(n)``).
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
    return np.mean(residual * residual, axis=1)  # one F^2 per box


def _dfa_fluctuation(profile: np.ndarray, box_size: int) -> float:
    """Pooled RMS residual of *profile* detrended box-by-box at *box_size*.

    Equivalent to pooling every box's own residuals into one RMS, since
    every box here has the same size — see :func:`_dfa_box_fluctuations`.
    """
    return float(np.sqrt(np.mean(_dfa_box_fluctuations(profile, box_size))))


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


def _mfdfa_fq(f2_per_box: np.ndarray, q: float) -> float:
    """``F_q(n)`` (Kantelhardt et al., 2002).

    The ``q``-th-order fluctuation function, pooling one box size's own
    per-box ``F^2(n, nu)`` values.

    ``q = 0`` is the paper's own special case (the ``q``-th power average
    degenerates at ``q=0``, replaced by a log-average instead, per l'Hopital
    applied to the general formula); ``q = 2`` reduces exactly to
    :func:`_dfa_fluctuation`'s plain-DFA fluctuation.
    """
    if q == 0.0:
        return float(np.exp(0.5 * np.mean(np.log(f2_per_box))))
    return float(np.mean(f2_per_box ** (q / 2.0)) ** (1.0 / q))


def _mfdfa_h(profile: np.ndarray, box_sizes: list[int], q: float) -> float:
    """Generalized Hurst exponent ``h(q)``.

    The slope of ``log(F_q(n))`` against ``log(n)`` over *box_sizes*.
    """
    log_boxes = []
    log_fq = []
    for box_size in box_sizes:
        f2_per_box = _dfa_box_fluctuations(profile, box_size)
        if np.all(f2_per_box > 0.0):
            fq = _mfdfa_fq(f2_per_box, q)
            if fq > 0.0:
                log_boxes.append(np.log(box_size))
                log_fq.append(np.log(fq))
    if len(log_boxes) < 2:
        return np.nan
    slope, _ = np.polyfit(log_boxes, log_fq, 1)
    return float(slope)


def _validate_q(value: Number, name: str) -> float:
    """Validate a Multifractal DFA moment order: any finite, non-zero real number."""
    if isinstance(value, bool) or not isinstance(value, (int, float, np.integer, np.floating)):
        raise ValueError(f"{name!r} must be a number, got {type(value).__name__}")
    if not np.isfinite(value):
        raise ValueError(f"{name!r} must be finite, got {value}")
    return float(value)


@indicator(
    category="advanced",
    summary="Width of the generalized-Hurst spectrum across fluctuation sizes (multifractality).",
    reference="https://doi.org/10.1016/S0378-4371(02)01383-3",
    outputs=("MFDFA",),
)
def multifractal_dfa(
    close: ArrayLike, window: int = 100, q_min: Number = -5.0, q_max: Number = 5.0
) -> pd.Series:
    """Multifractal Detrended Fluctuation Analysis (Kantelhardt et al., 2002).

    :func:`dfa` fits one scaling exponent to a return series, implicitly
    treating small and large fluctuations as scaling the same way — the
    *monofractal* assumption. MF-DFA checks that assumption by generalizing
    DFA's fluctuation function with a ``q``-th-power average over boxes
    instead of a plain RMS::

        F_q(n) = { (1/N_n) * sum_nu [F^2(n, nu)]^(q/2) } ^ (1/q),   q != 0
        F_0(n) = exp{ (1/(2*N_n)) * sum_nu ln[F^2(n, nu)] }

    using the same per-box detrended fluctuations ``F^2(n, nu)`` as
    :func:`dfa` (this function reuses that machinery directly). Negative
    ``q`` weights *small* fluctuations more heavily, positive ``q`` weights
    *large* ones; the generalized Hurst exponent ``h(q)`` is then the slope
    of ``log(F_q(n))`` against ``log(n)``, exactly as in :func:`dfa` (whose
    single exponent is this method's ``h(2)``). A series whose small and
    large fluctuations scale identically (*monofractal*, e.g. plain
    fractional Brownian motion) has ``h(q)`` essentially constant across
    ``q``; a genuinely *multifractal* series has small and large
    fluctuations scaling differently, so ``h(q)`` varies with ``q``. This
    function reports that variation as a single number, the width of the
    generalized-Hurst spectrum between two chosen extremes::

        MFDFA = h(q_min) - h(q_max)

    Parameters
    ----------
    close:
        Closing prices.
    window:
        Rolling look-back, in log returns. Must be >= 32, the same
        requirement as :func:`dfa` and for the same reason (room for at
        least two box sizes).
    q_min, q_max:
        The two ``q`` values ``h(q)`` is compared at. Must satisfy
        ``q_min < q_max``; the paper's own examples (and the tutorial
        literature that has followed it, e.g. Ihlen, 2012,
        "Introduction to Multifractal Detrended Fluctuation Analysis in
        Matlab") most commonly scan ``q`` symmetrically over ``-5`` to
        ``5``, which is this function's default.

    Returns
    -------
    pandas.Series
        Named ``MFDFA_{window}_{q_min}_{q_max}``. Near ``0`` for a
        monofractal series; larger (and, for the default ``q_min < 0 <
        q_max`` ordering, positive) for a more strongly multifractal one.
        ``NaN`` for warm-up bars and wherever either ``h(q_min)`` or
        ``h(q_max)`` cannot be estimated (fewer than two usable box sizes,
        the same condition :func:`dfa` itself uses).

    Notes
    -----
    This implementation divides each rolling window into non-overlapping
    boxes from the start only, the same convention :func:`dfa` already uses
    in this library — the wider MF-DFA literature also pools boxes counted
    from the *end* of the profile to use every point, a refinement this
    function does not add, kept consistent with :func:`dfa`'s own existing
    behaviour rather than introducing a second convention between the two.
    Like :func:`dfa`/:func:`hurst_exponent`/:func:`higuchi_fractal_dimension`,
    this is a per-bar loop over several box sizes (now doubled, for
    ``q_min`` and ``q_max`` each) rather than a single vectorised pass.

    Examples
    --------
    >>> import numpy as np
    >>> import zeonta
    >>> rng = np.random.default_rng(0)
    >>> walk = 100.0 * np.cumprod(1.0 + rng.normal(scale=0.01, size=150))
    >>> result = zeonta.multifractal_dfa(walk, window=100)
    >>> bool(np.isfinite(result.iloc[-1]))
    True

    References
    ----------
    https://doi.org/10.1016/S0378-4371(02)01383-3
    """
    window = validate_length(window, "window", minimum=32)
    q_min = _validate_q(q_min, "q_min")
    q_max = _validate_q(q_max, "q_max")
    if q_min >= q_max:
        raise ValueError(f"'q_min' must be < 'q_max', got q_min={q_min}, q_max={q_max}")

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
        h_min = _mfdfa_h(profile, box_sizes, q_min)
        h_max = _mfdfa_h(profile, box_sizes, q_max)
        if np.isfinite(h_min) and np.isfinite(h_max):
            result[i - 1] = h_min - h_max

    return wrap_series(result, common_index(close), f"MFDFA_{window}_{q_min}_{q_max}")


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


@indicator(
    category="advanced",
    summary="How spread out a window's log returns are — noise vs. clustered structure.",
    outputs=("SHENT",),
    reference="https://ieeexplore.ieee.org/document/6773024",
)
def shannon_entropy(close: ArrayLike, window: int = 50, bins: int = 10) -> pd.Series:
    """Shannon Entropy (Shannon, 1948) of a rolling window's log returns.

    Bins each window's log returns into ``bins`` equal-width buckets
    spanning that window's own min-to-max range, and takes the entropy of
    the resulting frequency distribution::

        H = -sum(p_i * log(p_i))   over every bucket i with p_i > 0

    ``p_i`` the fraction of the window's returns landing in bucket ``i``.
    Divided by ``log(bins)`` (the maximum possible entropy for that many
    buckets, reached when every bucket holds an equal share) so the
    result is a bin-count-independent ``0``-``1`` reading: returns packed
    into one or two buckets (a quiet, directional stretch) score low;
    returns spread evenly across every bucket (no dominant move size)
    score close to ``1``.

    Unlike :func:`sample_entropy`/:func:`approximate_entropy`, which ask
    whether a window's *shape* repeats over time, this asks nothing about
    order or repetition at all — only how uniformly the move sizes
    themselves are distributed within the window.

    Parameters
    ----------
    close:
        Closing prices.
    window:
        Bars per rolling estimate, in log returns. Must be >= 20.
    bins:
        Equal-width buckets the window's own return range is divided
        into. Must be >= 2. Like :func:`sample_entropy`'s ``m``/``r``,
        this is a tunable resolution, not a value with one provably
        correct setting — more buckets resolve finer structure at the
        cost of needing more bars per bucket to estimate each ``p_i``
        reliably.

    Returns
    -------
    pandas.Series
        Named ``SHENT_{window}_{bins}``, normalized to ``0``-``1``.
        ``NaN`` wherever a window has too few log returns to fill (the
        warm-up) or contains a non-finite one. A window whose returns are
        all identical (every bucket but one empty) is defined as exactly
        ``0.0`` rather than left undefined.

    Examples
    --------
    >>> import numpy as np
    >>> import zeonta
    >>> rng = np.random.default_rng(0)
    >>> noisy = 100.0 * np.cumprod(1.0 + rng.normal(scale=0.01, size=150))
    >>> result = zeonta.shannon_entropy(noisy, window=50)
    >>> bool(0.0 <= result.iloc[-1] <= 1.0)
    True

    References
    ----------
    Shannon, C.E. (1948). "A Mathematical Theory of Communication".
    https://ieeexplore.ieee.org/document/6773024
    """
    window = validate_length(window, "window", minimum=20)
    if not isinstance(bins, (int, np.integer)) or isinstance(bins, bool) or bins < 2:
        raise ValueError(f"'bins' must be an integer >= 2, got {bins!r}")

    values = as_array(close, "close")
    size = values.shape[0]
    with np.errstate(divide="ignore", invalid="ignore"):
        log_returns = np.diff(np.log(values), prepend=np.nan)

    result = np.full(size, np.nan, dtype="float64")
    log_bins = np.log(bins)
    for i in range(window, size + 1):
        segment = log_returns[i - window : i]
        if not np.all(np.isfinite(segment)):
            continue
        low, high = segment.min(), segment.max()
        if high == low:
            result[i - 1] = 0.0
            continue
        counts, _ = np.histogram(segment, bins=bins, range=(low, high))
        probabilities = counts[counts > 0] / window
        entropy = -np.sum(probabilities * np.log(probabilities))
        result[i - 1] = entropy / log_bins

    return wrap_series(result, common_index(close), f"SHENT_{window}_{bins}")


@indicator(
    category="advanced",
    summary="Symmetric CUSUM filter: flags bars where cumulative log-return drift crosses a level.",
    outputs=("CUSUM",),
    reference="https://doi.org/10.1002/9781119482086",
)
def cusum_filter(close: ArrayLike, threshold: Number = 0.05) -> pd.Series:
    """Symmetric CUSUM Filter (Lopez de Prado, 2018, *Advances in Financial Machine Learning*).

    Section 2.5.2.1. Maintains two running sums of log returns, one tracking upward drift and
    one downward, each reset to zero the moment it fires::

        S+[0] = S-[0] = 0
        S+[t] = max(0, S+[t-1] + r[t])
        S-[t] = min(0, S-[t-1] + r[t])

        if S-[t] < -threshold: event = -1, S-[t] reset to 0
        elif S+[t] > threshold: event = +1, S+[t] reset to 0
        else: event = 0

    where ``r[t] = ln(Close[t] / Close[t-1])``. Originally used in the book
    to *sample* bars for a downstream ML pipeline (only bars where an event
    fires are kept) rather than to produce a value at every bar. This
    library's aligned-per-bar output contract has no place for dropping
    bars, so this function instead reports the discrete event flag itself at
    every bar — ``0.0`` on every bar with no crossing, matching the same
    binary/discrete-flag shape :func:`divergence` already uses in this
    module for an event that only fires on some bars.

    Parameters
    ----------
    close:
        Closing prices.
    threshold:
        The fixed drift threshold ``h``, in the same units as the log
        returns being summed (e.g. ``0.05`` means "5% of cumulative log
        drift since the last reset"). The book parameterizes this directly
        as a fixed level rather than a multiple of a rolling volatility
        estimate; this function does the same, to avoid inventing a second,
        uncited convention on top of the book's own one. Must be > 0.

    Returns
    -------
    pandas.Series
        Named ``CUSUM_{threshold}``, one of ``1.0`` (upward drift crossed
        ``threshold``), ``-1.0`` (downward drift crossed ``-threshold``) or
        ``0.0`` (no crossing this bar). ``NaN`` on the first bar (no log
        return yet) and on any bar whose own log return is non-finite —
        the running sums are left unchanged there rather than poisoned,
        the same self-recovering behaviour :func:`bipower_variation` and
        similar running estimators in this library already have.

    Notes
    -----
    This is a genuinely stateful, whole-series recursion — like
    :func:`~zeonta.drawdown`'s running peak, not a fixed rolling window — so
    prepending more history to the same series can change every later flag
    (the running sums start from a different point). The recursion and its
    exact reset rule are also implemented, independently of this library,
    in the open-source ``mlfinlab``/``mlfinpy`` replications of the book's
    own ``getTEvents`` function, cross-checked against this implementation
    while it was written.

    Examples
    --------
    >>> import zeonta
    >>> close = [100.0, 101.0, 102.0, 103.0, 90.0]
    >>> zeonta.cusum_filter(close, threshold=0.01).tolist()
    [nan, 0.0, 1.0, 0.0, -1.0]

    References
    ----------
    Lopez de Prado, M. (2018). *Advances in Financial Machine Learning*,
    section 2.5.2.1. https://doi.org/10.1002/9781119482086
    """
    threshold = validate_multiplier(threshold, "threshold")
    values = as_array(close, "close")
    size = values.shape[0]
    with np.errstate(divide="ignore", invalid="ignore"):
        log_returns = np.diff(np.log(values), prepend=np.nan)

    result = np.full(size, np.nan, dtype="float64")
    s_pos = 0.0
    s_neg = 0.0
    for i in range(1, size):
        change = log_returns[i]
        if not np.isfinite(change):
            continue
        s_pos = max(0.0, s_pos + change)
        s_neg = min(0.0, s_neg + change)
        if s_neg < -threshold:
            s_neg = 0.0
            result[i] = -1.0
        elif s_pos > threshold:
            s_pos = 0.0
            result[i] = 1.0
        else:
            result[i] = 0.0

    return wrap_series(result, common_index(close), f"CUSUM_{threshold}")


@indicator(
    category="advanced",
    summary="Sample Entropy recomputed at several coarse-graining scales (Costa et al., 2002).",
    outputs=("MSE",),
    returns_frame=True,
    reference="https://doi.org/10.1103/PhysRevLett.89.068102",
)
def multiscale_entropy(
    close: ArrayLike, window: int = 100, scales: int = 5, m: int = 2, r: Number = 0.2
) -> pd.DataFrame:
    """Multiscale Entropy (Costa, Goldberger & Peng, 2002).

    :func:`sample_entropy` measures unpredictability at the series' own,
    single time scale. Multiscale Entropy repeats that same measurement
    after *coarse-graining* the window at several scale factors ``tau``,
    replacing every non-overlapping run of ``tau`` consecutive log returns
    with their own mean::

        y_j^(tau) = (1/tau) * sum(log_return[(j-1)*tau + 1 .. j*tau]),
                    j = 1 .. floor(window / tau)

    then computes :func:`sample_entropy`'s own ``SampEn`` statistic on each
    ``y^(tau)`` series (reusing that function's template-matching machinery
    directly rather than reimplementing it). ``tau=1`` is the coarse-graining
    identity, so scale 1 is exactly :func:`sample_entropy` on the same
    window. A series with structure spread across multiple timescales (many
    real physiological and financial series) keeps a roughly flat or rising
    entropy profile across scales; a series that is only complex at the
    finest scale (e.g. pure white noise) has its entropy collapse quickly as
    ``tau`` grows, since averaging pure noise into blocks removes most of
    what made it "unpredictable" bar to bar.

    Parameters
    ----------
    close:
        Closing prices.
    window:
        Bars per rolling estimate, in log returns, at scale 1 (the finest).
        Must be >= 20, the same floor :func:`sample_entropy` itself uses;
        coarser scales see a proportionally shorter, coarse-grained series
        from the same window.
    scales:
        Number of scale factors evaluated, ``tau = 1, 2, .., scales``. Must
        be an integer >= 1.
    m, r:
        Passed through to :func:`sample_entropy`'s own template length and
        tolerance at every scale. Per Costa et al.'s own papers and the
        PhysioNet ``pyMSE``/``mse`` reference toolkit built from them, the
        tolerance is **not** recomputed from each coarse-grained series' own
        (shrinking) standard deviation — it stays fixed at ``r`` times the
        *original*, scale-1 window's standard deviation across every scale,
        which is what this function does. Recomputing ``r * std`` per scale
        is a documented alternative some later papers use instead, but
        Costa et al.'s own construction, and the toolkit built directly from
        it, use the fixed-original-SD convention implemented here.

    Returns
    -------
    pandas.DataFrame
        Columns ``MSE_{window}_{m}_{r}_{tau}`` for ``tau = 1 .. scales``.
        ``NaN`` for warm-up bars, for any window containing a non-finite log
        return, and for any scale whose coarse-grained series is too short
        to form at least two ``SampEn`` template matches (the same
        condition :func:`sample_entropy` itself uses).

    Notes
    -----
    Same ``O(window^2)`` per-bar, per-scale cost as :func:`sample_entropy`,
    now repeated ``scales`` times per bar.

    Examples
    --------
    >>> import numpy as np
    >>> import zeonta
    >>> rng = np.random.default_rng(0)
    >>> noisy = 100.0 * np.cumprod(1.0 + rng.normal(scale=0.01, size=150))
    >>> result = zeonta.multiscale_entropy(noisy, window=100, scales=3)
    >>> list(result.columns)
    ['MSE_100_2_0.2_1', 'MSE_100_2_0.2_2', 'MSE_100_2_0.2_3']
    >>> bool(np.isfinite(result.iloc[-1]).all())
    True

    References
    ----------
    Costa, M., Goldberger, A.L., Peng, C.-K. (2002). "Multiscale Entropy
    Analysis of Complex Physiologic Time Series". Physical Review Letters
    89, 068102. https://doi.org/10.1103/PhysRevLett.89.068102
    """
    window = validate_length(window, "window", minimum=20)
    if not isinstance(scales, (int, np.integer)) or isinstance(scales, bool) or scales < 1:
        raise ValueError(f"'scales' must be an integer >= 1, got {scales!r}")
    if not isinstance(m, (int, np.integer)) or isinstance(m, bool) or m < 1:
        raise ValueError(f"'m' must be an integer >= 1, got {m!r}")
    r = validate_multiplier(r, "r")

    values = as_array(close, "close")
    size = values.shape[0]
    with np.errstate(divide="ignore", invalid="ignore"):
        log_returns = np.diff(np.log(values), prepend=np.nan)

    columns = {
        f"MSE_{window}_{m}_{r}_{tau}": np.full(size, np.nan, dtype="float64")
        for tau in range(1, scales + 1)
    }
    order = list(columns)

    for i in range(window, size + 1):
        segment = log_returns[i - window : i]
        if not np.all(np.isfinite(segment)):
            continue
        tolerance = r * segment.std()
        if tolerance == 0.0:
            continue
        for tau in range(1, scales + 1):
            n_blocks = window // tau
            coarse = segment[: n_blocks * tau].reshape(n_blocks, tau).mean(axis=1)
            columns[f"MSE_{window}_{m}_{r}_{tau}"][i - 1] = _sample_entropy_value(
                coarse, m, tolerance
            )

    return wrap_frame(columns, common_index(close), order=order)


@indicator(
    category="advanced",
    summary="Kullback-Leibler divergence between a short and a long window's return distributions.",
    outputs=("KLDIV",),
    reference="https://doi.org/10.1214/aoms/1177729694",
)
def kl_divergence(close: ArrayLike, short: int = 20, long: int = 100, bins: int = 10) -> pd.Series:
    """Kullback-Leibler Divergence between a rolling short and long window.

    Kullback & Leibler (1951). Reuses :func:`shannon_entropy`'s own binning convention (equal-width
    buckets, histogram counts turned into a frequency distribution) rather
    than inventing a new one, applied to *two* nested windows ending on the
    same bar: a short, recent one (``P``) and a long, older one that
    contains it (``Q``)::

        edges = bins equal-width buckets spanning Q's own min..max
        P_i   = fraction of the short window's returns in bucket i
        Q_i   = fraction of the long window's returns in bucket i
        KL    = sum(P_i * ln(P_i / Q_i), over every bucket i with P_i > 0)

    Because the short window is always the long window's own most recent
    trailing subset (``short <= long``, both ending at the current bar), its
    values are automatically bounded by the long window's own range — the
    same *Q*-spanning bin edges used for both distributions, with no
    separate alignment convention to invent. ``KL`` is ``0`` when the recent
    return distribution looks just like the longer history it sits inside,
    and grows as the recent window's shape (not just its level) diverges
    from it — e.g. a recent stretch of unusually one-sided, narrow, or
    fat-tailed returns compared to the longer lookback.

    Parameters
    ----------
    close:
        Closing prices.
    short:
        Bars in the recent window, in log returns. Must be >= 20 (the same
        floor :func:`shannon_entropy` uses).
    long:
        Bars in the older, containing window. Must be > ``short``.
    bins:
        Equal-width buckets the long window's own return range is divided
        into for both distributions. Must be >= 2; a tunable resolution,
        the same convention :func:`shannon_entropy` already documents.

    Returns
    -------
    pandas.Series
        Named ``KLDIV_{short}_{long}_{bins}``. Always ``>= 0`` (Gibbs'
        inequality) and always well-defined: because the short window's
        values are a literal subset of the long window's own array (not
        merely bounded by the same range), any bucket ``P`` puts mass in
        necessarily has ``Q`` mass in it too — the same values are counted
        in both histograms. ``NaN`` for warm-up bars and for any window
        containing a non-finite log return.

    Examples
    --------
    >>> import numpy as np
    >>> import zeonta
    >>> rng = np.random.default_rng(0)
    >>> calm = rng.normal(scale=0.005, size=100)
    >>> turbulent = rng.normal(scale=0.05, size=20)
    >>> prices = 100.0 * np.cumprod(1.0 + np.concatenate([calm, turbulent]))
    >>> result = zeonta.kl_divergence(prices, short=20, long=100)
    >>> bool(result.iloc[-1] > 0.0)
    True

    References
    ----------
    Kullback, S., Leibler, R.A. (1951). "On Information and Sufficiency".
    Annals of Mathematical Statistics 22(1). https://doi.org/10.1214/aoms/1177729694
    """
    short = validate_length(short, "short", minimum=20)
    long = validate_length(long, "long", minimum=short + 1)
    if not isinstance(bins, (int, np.integer)) or isinstance(bins, bool) or bins < 2:
        raise ValueError(f"'bins' must be an integer >= 2, got {bins!r}")

    values = as_array(close, "close")
    size = values.shape[0]
    with np.errstate(divide="ignore", invalid="ignore"):
        log_returns = np.diff(np.log(values), prepend=np.nan)

    result = np.full(size, np.nan, dtype="float64")
    for i in range(long, size + 1):
        long_segment = log_returns[i - long : i]
        if not np.all(np.isfinite(long_segment)):
            continue
        short_segment = long_segment[-short:]
        low, high = long_segment.min(), long_segment.max()
        if high == low:
            result[i - 1] = 0.0
            continue
        long_counts, edges = np.histogram(long_segment, bins=bins, range=(low, high))
        short_counts, _ = np.histogram(short_segment, bins=edges)
        p = short_counts / short
        q = long_counts / long
        mask = p > 0.0
        # q[mask] > 0 always holds: every value short_segment contributes to
        # bucket i is a literal element of long_segment too (short is its
        # trailing subset, not merely bounded by its range), so that same
        # value also counts toward q_i.
        result[i - 1] = float(np.sum(p[mask] * np.log(p[mask] / q[mask])))

    return wrap_series(result, common_index(close), f"KLDIV_{short}_{long}_{bins}")
