"""Advanced tools: VWAP, Fibonacci retracement, pivot points and divergences."""

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
)
from .foundations import _pivot_flags
from .oscillators import rsi

__all__ = ["divergence", "fib_retracement", "pivot_points", "vwap"]

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
    return wrap_frame(dict(zip(order, columns, strict=True)), index, order=order)


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
    )
