"""Momentum oscillators.

RSI, Stochastic, MACD, CCI, Momentum, ROC, Williams %R, Stochastic RSI, and
the Awesome Oscillator.

Momentum, ROC, Williams %R, Stochastic RSI and the Awesome Oscillator
additionally cite the external source their formula was verified against;
see each function's own ``References`` section.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ._core import (
    ArrayLike,
    as_array,
    common_index,
    ema_values,
    indicator,
    require_aligned_index,
    require_same_length,
    rolling_max,
    rolling_mean,
    rolling_mean_abs_dev,
    rolling_min,
    rolling_sum,
    rolling_wma,
    validate_length,
    wilder_values,
    wrap_frame,
    wrap_series,
)

__all__ = [
    "awesome_oscillator",
    "cci",
    "coppock_curve",
    "dpo",
    "elder_ray",
    "macd",
    "momentum",
    "ppo",
    "roc",
    "rsi",
    "stoch",
    "stoch_rsi",
    "trix",
    "tsi",
    "ultimate_oscillator",
    "williams_r",
]


def _shift(values: np.ndarray, length: int) -> np.ndarray:
    """*values* shifted forward by *length* bars, padded with ``NaN``."""
    shifted = np.full(values.shape[0], np.nan, dtype="float64")
    if values.shape[0] > length:
        shifted[length:] = values[:-length]
    return shifted


@indicator(
    category="oscillators",
    summary="Wilder's momentum oscillator bounded between 0 and 100.",
    lesson="rsi",
    outputs=("RSI",),
)
def rsi(close: ArrayLike, length: int = 14) -> pd.Series:
    """Relative Strength Index.

    ``RSI = 100 - 100 / (1 + RS)`` where
    ``RS = AvgGain(n, Wilder-smoothed) / AvgLoss(n, Wilder-smoothed)``.

    When average loss is zero the ratio is undefined; the result is pinned to
    ``100`` (pure gains) — the standard convention.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        Wilder smoothing period.

    Returns
    -------
    pandas.Series
        Named ``RSI_{length}``, ranging 0-100.

    Examples
    --------
    >>> import zeonta
    >>> float(zeonta.rsi(list(range(1, 40)), length=14).iloc[-1])
    100.0
    """
    length = validate_length(length)
    values = as_array(close, "close")

    change = np.diff(values, prepend=np.nan)
    gains = np.where(np.isfinite(change), np.maximum(change, 0.0), np.nan)
    losses = np.where(np.isfinite(change), np.maximum(-change, 0.0), np.nan)

    # Bar 0 has no change, so smoothing starts from bar 1.
    average_gain = np.full(values.shape[0], np.nan, dtype="float64")
    average_loss = np.full(values.shape[0], np.nan, dtype="float64")
    average_gain[1:] = wilder_values(gains[1:], length)
    average_loss[1:] = wilder_values(losses[1:], length)

    with np.errstate(divide="ignore", invalid="ignore"):
        strength = average_gain / average_loss
        result = 100.0 - 100.0 / (1.0 + strength)

    # avg_loss == 0 -> RS is infinite -> RSI is 100; both zero -> flat market -> 50.
    flat = (average_loss == 0.0) & (average_gain == 0.0)
    result = np.where((average_loss == 0.0) & np.isfinite(average_gain), 100.0, result)
    result = np.where(flat, 50.0, result)
    result = np.where(np.isfinite(average_gain) & np.isfinite(average_loss), result, np.nan)

    return wrap_series(result, common_index(close), f"RSI_{length}")


@indicator(
    category="oscillators",
    summary="Where the close sits inside the recent high-low range.",
    lesson="stochastic",
    outputs=("STOCHk", "STOCHd"),
)
def stoch(
    high: ArrayLike,
    low: ArrayLike,
    close: ArrayLike,
    length: int = 14,
    smooth_k: int = 3,
    smooth_d: int = 3,
) -> pd.DataFrame:
    """Stochastic Oscillator.

    ``%K = 100 * (Close - LowestLow(n)) / (HighestHigh(n) - LowestLow(n))``,
    then ``%K = SMA(%K, smooth_k)`` and ``%D = SMA(%K, smooth_d)``.

    Parameters
    ----------
    high, low, close:
        Price series of equal length.
    length:
        Look-back for the high-low range.
    smooth_k:
        Smoothing applied to raw ``%K``. Use ``1`` for the "fast" stochastic.
    smooth_d:
        Smoothing applied to ``%K`` to obtain the ``%D`` signal line.

    Returns
    -------
    pandas.DataFrame
        Columns ``STOCHk_{length}_{smooth_k}_{smooth_d}`` and
        ``STOCHd_{length}_{smooth_k}_{smooth_d}``, ranging 0-100.

    Examples
    --------
    >>> import zeonta
    >>> out = zeonta.stoch(
    ...     [3, 4, 5, 6], [1, 2, 3, 4], [2, 3, 4, 5], length=2, smooth_k=1, smooth_d=1
    ... )
    >>> round(float(out.iloc[-1, 0]), 2)
    66.67
    """
    length = validate_length(length)
    smooth_k = validate_length(smooth_k, "smooth_k")
    smooth_d = validate_length(smooth_d, "smooth_d")

    require_aligned_index(high=high, low=low, close=close)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    close_values = as_array(close, "close")
    require_same_length(high=high_values, low=low_values, close=close_values)

    highest = rolling_max(high_values, length)
    lowest = rolling_min(low_values, length)
    span = highest - lowest

    with np.errstate(divide="ignore", invalid="ignore"):
        raw_k = 100.0 * (close_values - lowest) / span
    # A dead-flat range gives no information; convention puts %K mid-scale.
    raw_k = np.where(span == 0.0, 50.0, raw_k)

    percent_k = rolling_mean(raw_k, smooth_k) if smooth_k > 1 else raw_k
    percent_d = rolling_mean(percent_k, smooth_d) if smooth_d > 1 else percent_k

    suffix = f"{length}_{smooth_k}_{smooth_d}"
    return wrap_frame(
        {f"STOCHk_{suffix}": percent_k, f"STOCHd_{suffix}": percent_d},
        common_index(high, low, close),
        order=[f"STOCHk_{suffix}", f"STOCHd_{suffix}"],
    )


@indicator(
    category="oscillators",
    summary="Where the close sits inside the recent high-low range, on a 0 to -100 scale.",
    reference=(
        "https://chartschool.stockcharts.com/table-of-contents/"
        "technical-indicators-and-overlays/technical-indicators/williams-r"
    ),
    outputs=("WILLR",),
)
def williams_r(high: ArrayLike, low: ArrayLike, close: ArrayLike, length: int = 14) -> pd.Series:
    """Williams %R.

    ``%R = (HighestHigh(n) - Close) / (HighestHigh(n) - LowestLow(n)) * -100``
    — the same range-position idea as the unsmoothed ``%K`` in :func:`stoch`,
    just inverted and shifted onto a 0 to -100 scale instead of 0 to 100
    (``%R = %K - 100`` exactly, bar for bar).

    Parameters
    ----------
    high, low, close:
        Price series of equal length.
    length:
        Look-back for the high-low range.

    Returns
    -------
    pandas.Series
        Named ``WILLR_{length}``, ranging 0 to -100. A dead-flat range (no
        information either way) is pinned to -50, the midpoint.

    Examples
    --------
    >>> import zeonta
    >>> float(zeonta.williams_r([5, 6], [1, 2], [5, 5.5], length=2).iloc[-1])
    -10.0

    References
    ----------
    https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/williams-r
    """
    length = validate_length(length)
    require_aligned_index(high=high, low=low, close=close)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    close_values = as_array(close, "close")
    require_same_length(high=high_values, low=low_values, close=close_values)

    highest = rolling_max(high_values, length)
    lowest = rolling_min(low_values, length)
    span = highest - lowest

    with np.errstate(divide="ignore", invalid="ignore"):
        result = (highest - close_values) / span * -100.0
    # A dead-flat range gives no information; convention puts %R mid-scale.
    result = np.where(span == 0.0, -50.0, result)

    return wrap_series(result, common_index(high, low, close), f"WILLR_{length}")


@indicator(
    category="oscillators",
    summary="The Stochastic formula applied to RSI instead of price — momentum of momentum.",
    reference=(
        "https://chartschool.stockcharts.com/table-of-contents/"
        "technical-indicators-and-overlays/technical-indicators/stochrsi"
    ),
    outputs=("STOCHRSIk", "STOCHRSId"),
)
def stoch_rsi(
    close: ArrayLike,
    rsi_length: int = 14,
    stoch_length: int = 14,
    smooth_k: int = 3,
    smooth_d: int = 3,
) -> pd.DataFrame:
    """Stochastic RSI.

    ``StochRSI = (RSI - LowestLow(RSI, n)) / (HighestHigh(RSI, n) -
    LowestLow(RSI, n))`` — the same range-position formula :func:`stoch`
    applies to price, applied to :func:`rsi` instead. RSI alone measures
    momentum; StochRSI measures how extreme *that* momentum reading is
    relative to its own recent history, which makes it swing far more
    aggressively than RSI itself.

    Unlike the source formula (which is unsmoothed and ranges 0-1), this
    scales to 0-100 and applies the same ``%K``/``%D`` smoothing
    :func:`stoch` uses, matching how most charting platforms display it and
    keeping the output on the same scale as this library's other oscillators.

    Parameters
    ----------
    close:
        Closing prices.
    rsi_length:
        Look-back for the underlying RSI.
    stoch_length:
        Look-back for the high-low range applied to RSI values.
    smooth_k:
        Smoothing applied to raw ``%K``. Use ``1`` for the unsmoothed line.
    smooth_d:
        Smoothing applied to ``%K`` to obtain the ``%D`` signal line.

    Returns
    -------
    pandas.DataFrame
        Columns ``STOCHRSIk_{rsi_length}_{stoch_length}_{smooth_k}_{smooth_d}``
        and ``STOCHRSId_...``, ranging 0-100.

    Examples
    --------
    A steady uptrend pins RSI itself at 100 once gains dominate — but with RSI
    now *flat* at 100, StochRSI's own high-low range collapses to zero and it
    falls back to the midpoint convention, same as :func:`stoch` does on a
    flat price range:

    >>> import zeonta
    >>> out = zeonta.stoch_rsi(list(range(1, 40)), rsi_length=5, stoch_length=5)
    >>> float(out.iloc[-1, 0])
    50.0

    References
    ----------
    https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/stochrsi
    """
    rsi_length = validate_length(rsi_length, "rsi_length")
    stoch_length = validate_length(stoch_length, "stoch_length")
    smooth_k = validate_length(smooth_k, "smooth_k")
    smooth_d = validate_length(smooth_d, "smooth_d")

    values = as_array(close, "close")
    rsi_values = rsi(values, length=rsi_length).to_numpy()

    lowest = rolling_min(rsi_values, stoch_length)
    highest = rolling_max(rsi_values, stoch_length)
    span = highest - lowest

    with np.errstate(divide="ignore", invalid="ignore"):
        raw_k = 100.0 * (rsi_values - lowest) / span
    raw_k = np.where(span == 0.0, 50.0, raw_k)

    percent_k = rolling_mean(raw_k, smooth_k) if smooth_k > 1 else raw_k
    percent_d = rolling_mean(percent_k, smooth_d) if smooth_d > 1 else percent_k

    suffix = f"{rsi_length}_{stoch_length}_{smooth_k}_{smooth_d}"
    order = [f"STOCHRSIk_{suffix}", f"STOCHRSId_{suffix}"]
    return wrap_frame(
        dict(zip(order, (percent_k, percent_d), strict=True)),
        common_index(close),
        order=order,
    )


@indicator(
    category="oscillators",
    summary="Momentum from the gap between a fast and slow SMA of the bar's own midpoint.",
    reference="https://www.metatrader5.com/en/terminal/help/indicators/bw_indicators/awesome",
    outputs=("AO",),
)
def awesome_oscillator(high: ArrayLike, low: ArrayLike, fast: int = 5, slow: int = 34) -> pd.Series:
    """Awesome Oscillator.

    ``MedianPrice = (High + Low) / 2``;
    ``AO = SMA(MedianPrice, fast) - SMA(MedianPrice, slow)``. Bill Williams'
    momentum reading: it uses the bar's own midpoint rather than the close,
    and — unlike :func:`macd`, which contrasts two EMAs — contrasts two plain
    SMAs, so it has no memory beyond each window's edge.

    Parameters
    ----------
    high, low:
        Price series of equal length.
    fast, slow:
        SMA lengths; ``fast`` must be smaller than ``slow``.

    Returns
    -------
    pandas.Series
        Named ``AO_{fast}_{slow}``, in price units, centred on zero.

    Examples
    --------
    >>> import zeonta
    >>> float(zeonta.awesome_oscillator([11] * 34, [9] * 34, fast=3, slow=5).iloc[-1])
    0.0

    References
    ----------
    https://www.metatrader5.com/en/terminal/help/indicators/bw_indicators/awesome
    """
    fast = validate_length(fast, "fast")
    slow = validate_length(slow, "slow")
    if fast >= slow:
        raise ValueError(f"'fast' must be smaller than 'slow', got fast={fast}, slow={slow}")

    require_aligned_index(high=high, low=low)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    require_same_length(high=high_values, low=low_values)

    median_price = (high_values + low_values) / 2.0
    result = rolling_mean(median_price, fast) - rolling_mean(median_price, slow)

    return wrap_series(result, common_index(high, low), f"AO_{fast}_{slow}")


@indicator(
    category="oscillators",
    summary="Difference between two EMAs, with a signal line and histogram.",
    lesson="macd",
    outputs=("MACD", "MACDs", "MACDh"),
)
def macd(
    close: ArrayLike,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> pd.DataFrame:
    """Moving Average Convergence Divergence.

    ``MACD = EMA(fast) - EMA(slow)``; ``Signal = EMA(MACD, signal)``;
    ``Histogram = MACD - Signal``.

    Parameters
    ----------
    close:
        Closing prices.
    fast, slow:
        EMA lengths; ``fast`` must be smaller than ``slow``.
    signal:
        EMA length of the signal line.

    Returns
    -------
    pandas.DataFrame
        Columns ``MACD_{f}_{s}_{sig}``, ``MACDs_{f}_{s}_{sig}``, ``MACDh_{f}_{s}_{sig}``.

    Examples
    --------
    >>> import zeonta
    >>> list(zeonta.macd(list(range(100))).columns)
    ['MACD_12_26_9', 'MACDs_12_26_9', 'MACDh_12_26_9']
    """
    fast = validate_length(fast, "fast")
    slow = validate_length(slow, "slow")
    signal = validate_length(signal, "signal")
    if fast >= slow:
        raise ValueError(f"'fast' must be smaller than 'slow', got fast={fast}, slow={slow}")

    values = as_array(close, "close")
    macd_line = ema_values(values, fast) - ema_values(values, slow)
    signal_line = ema_values(macd_line, signal)
    histogram = macd_line - signal_line

    suffix = f"{fast}_{slow}_{signal}"
    order = [f"MACD_{suffix}", f"MACDs_{suffix}", f"MACDh_{suffix}"]
    return wrap_frame(
        dict(zip(order, (macd_line, signal_line, histogram), strict=True)),
        common_index(close),
        order=order,
    )


@indicator(
    category="oscillators",
    summary="How far typical price has strayed from its own average, in mean deviations.",
    lesson="cci",
    outputs=("CCI",),
)
def cci(
    high: ArrayLike,
    low: ArrayLike,
    close: ArrayLike,
    length: int = 20,
    constant: float = 0.015,
) -> pd.Series:
    """Commodity Channel Index.

    ``TP = (High + Low + Close) / 3``;
    ``CCI = (TP - SMA(TP, n)) / (constant * MeanDeviation(TP, n))``.

    The ``0.015`` constant is Lambert's original scaling choice, which places
    roughly 70-80% of readings inside +/-100.

    Parameters
    ----------
    high, low, close:
        Price series of equal length.
    length:
        Look-back window.
    constant:
        Lambert scaling constant.

    Returns
    -------
    pandas.Series
        Named ``CCI_{length}``. Bars where mean deviation is zero (a perfectly
        flat window) return ``0.0``.

    Examples
    --------
    >>> import zeonta
    >>> float(zeonta.cci([2] * 25, [1] * 25, [1.5] * 25).iloc[-1])
    0.0
    """
    length = validate_length(length)
    if constant <= 0:
        raise ValueError(f"'constant' must be > 0, got {constant}")

    require_aligned_index(high=high, low=low, close=close)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    close_values = as_array(close, "close")
    require_same_length(high=high_values, low=low_values, close=close_values)

    typical = (high_values + low_values + close_values) / 3.0
    average = rolling_mean(typical, length)
    deviation = rolling_mean_abs_dev(typical, length)

    with np.errstate(divide="ignore", invalid="ignore"):
        result = (typical - average) / (constant * deviation)
    result = np.where(deviation == 0.0, 0.0, result)
    result = np.where(np.isfinite(average), result, np.nan)

    return wrap_series(result, common_index(high, low, close), f"CCI_{length}")


@indicator(
    category="oscillators",
    summary="Raw price change over n bars.",
    reference="https://en.wikipedia.org/wiki/Momentum_(technical_analysis)",
    outputs=("MOM",),
)
def momentum(close: ArrayLike, length: int = 10) -> pd.Series:
    """Momentum.

    ``MOM = Close - Close[n bars ago]`` — the plain, unnormalised price
    change; :func:`roc` expresses the same comparison as a percentage instead.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        How many bars back to compare against.

    Returns
    -------
    pandas.Series
        Named ``MOM_{length}``, in the same units as ``close``. The first
        ``length`` bars are ``NaN``.

    Examples
    --------
    >>> import zeonta
    >>> float(zeonta.momentum([10, 11, 12, 15], length=3).iloc[-1])
    5.0

    References
    ----------
    https://en.wikipedia.org/wiki/Momentum_(technical_analysis)
    """
    length = validate_length(length)
    values = as_array(close, "close")
    previous = _shift(values, length)

    return wrap_series(values - previous, common_index(close), f"MOM_{length}")


@indicator(
    category="oscillators",
    summary="Percentage price change over n bars — the normalised sibling of momentum.",
    reference=(
        "https://chartschool.stockcharts.com/table-of-contents/"
        "technical-indicators-and-overlays/technical-indicators/rate-of-change-roc"
    ),
    outputs=("ROC",),
)
def roc(close: ArrayLike, length: int = 12) -> pd.Series:
    """Rate of Change.

    ``ROC = (Close - Close[n bars ago]) / Close[n bars ago] * 100``.
    Expressing the change as a percentage (rather than :func:`momentum`'s raw
    price difference) makes it comparable across symbols and price levels.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        How many bars back to compare against.

    Returns
    -------
    pandas.Series
        Named ``ROC_{length}``. The first ``length`` bars are ``NaN``; a bar
        whose reference close was exactly ``0`` is also ``NaN``, since the
        percentage change is undefined there.

    Examples
    --------
    >>> import zeonta
    >>> float(zeonta.roc([10, 11, 12, 15], length=3).iloc[-1])
    50.0

    References
    ----------
    https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/rate-of-change-roc
    """
    length = validate_length(length)
    values = as_array(close, "close")
    previous = _shift(values, length)

    with np.errstate(divide="ignore", invalid="ignore"):
        result = (values - previous) / previous * 100.0
    result = np.where(previous == 0.0, np.nan, result)

    return wrap_series(result, common_index(close), f"ROC_{length}")


@indicator(
    category="oscillators",
    summary="Larry Williams' three-timeframe blend of buying pressure over true range.",
    reference=(
        "https://chartschool.stockcharts.com/table-of-contents/"
        "technical-indicators-and-overlays/technical-indicators/ultimate-oscillator"
    ),
    outputs=("UO",),
)
def ultimate_oscillator(
    high: ArrayLike,
    low: ArrayLike,
    close: ArrayLike,
    fast: int = 7,
    medium: int = 14,
    slow: int = 28,
) -> pd.Series:
    """Ultimate Oscillator.

    ``BP = Close - Min(Low, PriorClose)`` (Buying Pressure);
    ``TR = Max(High, PriorClose) - Min(Low, PriorClose)`` (True Range, the
    same maximum-of-three-measures range :func:`true_range` computes, just
    expressed via the prior close directly); ``Average_n = Sum(BP, n) /
    Sum(TR, n)`` computed over each of the three windows;
    ``UO = 100 * (4*Average_fast + 2*Average_medium + Average_slow) / 7``.
    Blending three timeframes with descending weight aims to capture both
    short-term momentum and the longer trend in one bounded line, tempering
    the whipsaws a single-period oscillator gives in a choppy market.

    Parameters
    ----------
    high, low, close:
        Price series of equal length.
    fast, medium, slow:
        The three look-back windows, weighted 4:2:1 respectively in the
        final blend; must satisfy ``fast < medium < slow``.

    Returns
    -------
    pandas.Series
        Named ``UO_{fast}_{medium}_{slow}``, ranging 0-100.

    Examples
    --------
    >>> import zeonta
    >>> high = [11.0, 12.0, 10.5, 13.0]
    >>> low = [9.0, 10.0, 8.5, 11.0]
    >>> close = [10.0, 11.5, 9.0, 12.5]
    >>> float(zeonta.ultimate_oscillator(high, low, close, fast=1, medium=2, slow=3).iloc[-1])
    75.05668934240362

    References
    ----------
    https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ultimate-oscillator
    """
    fast = validate_length(fast, "fast")
    medium = validate_length(medium, "medium")
    slow = validate_length(slow, "slow")
    if not fast < medium < slow:
        raise ValueError(
            f"'fast' < 'medium' < 'slow' is required, got fast={fast}, medium={medium}, slow={slow}"
        )

    require_aligned_index(high=high, low=low, close=close)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    close_values = as_array(close, "close")
    size = require_same_length(high=high_values, low=low_values, close=close_values)

    prior_close = np.concatenate(([np.nan], close_values[:-1]))
    buying_pressure = close_values - np.minimum(low_values, prior_close)
    true_range = np.maximum(high_values, prior_close) - np.minimum(low_values, prior_close)

    def average(length: int) -> np.ndarray:
        # No prior close at bar 0, so both sums start from bar 1, matching
        # the same alignment convention used by mfi() and vortex().
        sum_bp = np.full(size, np.nan, dtype="float64")
        sum_tr = np.full(size, np.nan, dtype="float64")
        sum_bp[1:] = rolling_sum(buying_pressure[1:], length)
        sum_tr[1:] = rolling_sum(true_range[1:], length)
        with np.errstate(divide="ignore", invalid="ignore"):
            result = sum_bp / sum_tr
        return np.where(np.isfinite(sum_tr) & (sum_tr == 0.0), 0.0, result)

    avg_fast = average(fast)
    avg_medium = average(medium)
    avg_slow = average(slow)
    result = 100.0 * (4.0 * avg_fast + 2.0 * avg_medium + avg_slow) / 7.0

    return wrap_series(result, common_index(high, low, close), f"UO_{fast}_{medium}_{slow}")


@indicator(
    category="oscillators",
    summary="Bull Power / Bear Power — the day's high and low measured against an EMA.",
    reference="https://www.tradingview.com/support/solutions/43000717955-bull-bear-power/",
    outputs=("BULLP", "BEARP"),
)
def elder_ray(high: ArrayLike, low: ArrayLike, close: ArrayLike, length: int = 13) -> pd.DataFrame:
    """Elder Ray (Bull Power / Bear Power).

    ``EMA = EMA(Close, length)``; ``Bull Power = High - EMA``;
    ``Bear Power = Low - EMA``. Bull Power reads how far buyers pushed price
    above the prevailing trend within the bar; Bear Power reads how far
    sellers pushed it below. Developed by Alexander Elder as a way to see
    the tug-of-war inside each bar relative to the trend, rather than just
    where the bar closed.

    Parameters
    ----------
    high, low, close:
        Price series of equal length.
    length:
        EMA period the two power lines are measured against.

    Returns
    -------
    pandas.DataFrame
        ``BULLP_{length}`` and ``BEARP_{length}``. In a clean uptrend
        Bull Power stays positive and Bear Power negative but shrinking;
        Bear Power turning positive, or Bull Power turning negative, is the
        classic warning that the trend has lost control of the bar.

    Examples
    --------
    >>> import zeonta
    >>> high = [11.0, 12.0, 13.0, 14.0]
    >>> low = [9.0, 10.0, 11.0, 12.0]
    >>> close = [10.0, 11.0, 12.0, 13.0]
    >>> out = zeonta.elder_ray(high, low, close, length=3)
    >>> [round(value, 4) for value in out.iloc[-1].tolist()]
    [2.0, 0.0]

    References
    ----------
    https://www.tradingview.com/support/solutions/43000717955-bull-bear-power/
    """
    length = validate_length(length)
    require_aligned_index(high=high, low=low, close=close)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    close_values = as_array(close, "close")
    require_same_length(high=high_values, low=low_values, close=close_values)

    baseline = ema_values(close_values, length)
    bull_power = high_values - baseline
    bear_power = low_values - baseline

    order = [f"BULLP_{length}", f"BEARP_{length}"]
    return wrap_frame(
        dict(zip(order, (bull_power, bear_power), strict=True)),
        common_index(high, low, close),
        order=order,
    )


@indicator(
    category="oscillators",
    summary="1-bar percent change of a triple-smoothed EMA — momentum with heavy noise filtering.",
    reference=(
        "https://chartschool.stockcharts.com/table-of-contents/"
        "technical-indicators-and-overlays/technical-indicators/trix"
    ),
    outputs=("TRIX", "TRIXs"),
)
def trix(close: ArrayLike, length: int = 15, signal: int = 9) -> pd.DataFrame:
    """TRIX (Triple Exponential Average).

    ``EMA1 = EMA(Close, n)``; ``EMA2 = EMA(EMA1, n)``; ``EMA3 = EMA(EMA2, n)``;
    ``TRIX = (EMA3[t] - EMA3[t-1]) / EMA3[t-1] * 100``. Three passes of
    smoothing before ever measuring a change is why TRIX filters out far
    more noise than a single-EMA oscillator like :func:`roc` — the tradeoff
    is proportionally more lag before it turns.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        Period for each of the three EMA passes.
    signal:
        EMA period for the signal line.

    Returns
    -------
    pandas.DataFrame
        ``TRIX_{length}_{signal}`` and ``TRIXs_{length}_{signal}`` (its
        signal line, an EMA of TRIX itself — the same construction
        :func:`macd`'s signal line uses).

    Examples
    --------
    >>> import zeonta
    >>> out = zeonta.trix(list(range(1, 60)), length=5, signal=3)
    >>> bool(out['TRIX_5_3'].iloc[-1] > 0)
    True

    References
    ----------
    https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/trix
    """
    length = validate_length(length)
    signal = validate_length(signal, "signal")
    values = as_array(close, "close")

    ema1 = ema_values(values, length)
    ema2 = ema_values(ema1, length)
    ema3 = ema_values(ema2, length)

    previous = _shift(ema3, 1)
    with np.errstate(divide="ignore", invalid="ignore"):
        trix_line = (ema3 - previous) / previous * 100.0
    trix_line = np.where(previous == 0.0, np.nan, trix_line)

    signal_line = ema_values(trix_line, signal)

    order = [f"TRIX_{length}_{signal}", f"TRIXs_{length}_{signal}"]
    return wrap_frame(
        dict(zip(order, (trix_line, signal_line), strict=True)),
        common_index(close),
        order=order,
    )


@indicator(
    category="oscillators",
    summary="MACD expressed as a percentage, comparable across symbols and price levels.",
    reference=(
        "https://chartschool.stockcharts.com/table-of-contents/"
        "technical-indicators-and-overlays/technical-indicators/percentage-price-oscillator-ppo"
    ),
    outputs=("PPO", "PPOs", "PPOh"),
)
def ppo(close: ArrayLike, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """Percentage Price Oscillator.

    ``PPO = (EMA(Close, fast) - EMA(Close, slow)) / EMA(Close, slow) * 100``;
    ``Signal = EMA(PPO, signal)``; ``Histogram = PPO - Signal``. Exactly
    :func:`macd`'s construction, normalised by the slow EMA so a PPO reading
    means the same thing on a $5 stock and a $500 one — :func:`macd`'s own
    absolute-price-difference output does not.

    Parameters
    ----------
    close:
        Closing prices.
    fast, slow:
        EMA lengths; ``fast`` must be smaller than ``slow``.
    signal:
        EMA length of the signal line.

    Returns
    -------
    pandas.DataFrame
        Columns ``PPO_{f}_{s}_{sig}``, ``PPOs_{f}_{s}_{sig}``, ``PPOh_{f}_{s}_{sig}``.

    Examples
    --------
    >>> import zeonta
    >>> list(zeonta.ppo(list(range(100))).columns)
    ['PPO_12_26_9', 'PPOs_12_26_9', 'PPOh_12_26_9']

    References
    ----------
    https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/percentage-price-oscillator-ppo
    """
    fast = validate_length(fast, "fast")
    slow = validate_length(slow, "slow")
    signal = validate_length(signal, "signal")
    if fast >= slow:
        raise ValueError(f"'fast' must be smaller than 'slow', got fast={fast}, slow={slow}")

    values = as_array(close, "close")
    fast_ema = ema_values(values, fast)
    slow_ema = ema_values(values, slow)
    with np.errstate(divide="ignore", invalid="ignore"):
        ppo_line = (fast_ema - slow_ema) / slow_ema * 100.0
    ppo_line = np.where(slow_ema == 0.0, np.nan, ppo_line)
    signal_line = ema_values(ppo_line, signal)
    histogram = ppo_line - signal_line

    suffix = f"{fast}_{slow}_{signal}"
    order = [f"PPO_{suffix}", f"PPOs_{suffix}", f"PPOh_{suffix}"]
    return wrap_frame(
        dict(zip(order, (ppo_line, signal_line, histogram), strict=True)),
        common_index(close),
        order=order,
    )


@indicator(
    category="oscillators",
    summary="Double-smoothed momentum, bounded and steadier than a single-pass oscillator.",
    reference=(
        "https://chartschool.stockcharts.com/table-of-contents/"
        "technical-indicators-and-overlays/technical-indicators/true-strength-index"
    ),
    outputs=("TSI", "TSIs"),
)
def tsi(close: ArrayLike, long: int = 25, short: int = 13, signal: int = 7) -> pd.DataFrame:
    """True Strength Index.

    ``PC = Close - Close[1 bar ago]``;
    ``DoubleSmoothedPC = EMA(EMA(PC, long), short)``;
    ``DoubleSmoothedAbsPC = EMA(EMA(|PC|, long), short)``;
    ``TSI = 100 * DoubleSmoothedPC / DoubleSmoothedAbsPC``;
    ``Signal = EMA(TSI, signal)``. William Blau's double smoothing of the
    raw price change (rather than smoothing an already-derived ratio, the
    way :func:`rsi` does) is meant to track the underlying trend closely
    while still filtering out short-term noise.

    Parameters
    ----------
    close:
        Closing prices.
    long, short:
        The two EMA lengths applied in sequence to the raw price change.
    signal:
        EMA length of the signal line.

    Returns
    -------
    pandas.DataFrame
        ``TSI_{long}_{short}_{signal}`` (roughly -100 to 100) and
        ``TSIs_{long}_{short}_{signal}``, its signal line.

    Notes
    -----
    Neither StockCharts nor Fidelity's guide commits to one canonical
    default signal-line period — TSI(25, 13, 7), TSI(25, 13, 13) and
    TSI(40, 20, 10) are all cited across independent sources. ``signal=7``
    is used here, the value repeated most often alongside the (25, 13) core
    smoothing pair.

    Examples
    --------
    >>> import zeonta
    >>> list(zeonta.tsi(list(range(60))).columns)
    ['TSI_25_13_7', 'TSIs_25_13_7']

    References
    ----------
    https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/true-strength-index
    """
    long = validate_length(long, "long")
    short = validate_length(short, "short")
    signal = validate_length(signal, "signal")
    values = as_array(close, "close")

    price_change = np.diff(values, prepend=np.nan)
    double_pc = ema_values(ema_values(price_change, long), short)
    double_abs_pc = ema_values(ema_values(np.abs(price_change), long), short)

    with np.errstate(divide="ignore", invalid="ignore"):
        tsi_line = 100.0 * double_pc / double_abs_pc
    # A perfectly flat run of recent price changes makes the denominator
    # zero; TSI is centred on zero, so "no measurable change" is 0, not NaN.
    tsi_line = np.where(double_abs_pc == 0.0, 0.0, tsi_line)
    tsi_line = np.where(np.isfinite(double_abs_pc), tsi_line, np.nan)

    signal_line = ema_values(tsi_line, signal)

    suffix = f"{long}_{short}_{signal}"
    order = [f"TSI_{suffix}", f"TSIs_{suffix}"]
    return wrap_frame(
        dict(zip(order, (tsi_line, signal_line), strict=True)),
        common_index(close),
        order=order,
    )


@indicator(
    category="oscillators",
    summary="Price from n/2+1 bars ago minus the current n-bar SMA, built to expose cycles.",
    reference=(
        "https://chartschool.stockcharts.com/table-of-contents/"
        "technical-indicators-and-overlays/technical-indicators/detrended-price-oscillator-dpo"
    ),
    outputs=("DPO",),
)
def dpo(close: ArrayLike, length: int = 20) -> pd.Series:
    """Detrended Price Oscillator.

    ``DPO = Close[n/2 + 1 bars ago] - SMA(Close, n)``. Subtracting an
    *older* price from the *current* moving average — rather than the
    current price, the way every other oscillator in this library works —
    is deliberate: it removes the trend component so the leftover
    oscillation lines up with the market's actual cycle peaks and troughs,
    at the cost of the line no longer reacting to the most recent bars at
    all.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        SMA window; also sets how far back the compared price is taken
        (``length // 2 + 1`` bars).

    Returns
    -------
    pandas.Series
        Named ``DPO_{length}``.

    Notes
    -----
    A cycle-identification tool, not a momentum or trend signal — it should
    not be read the way :func:`macd` or :func:`rsi` are.

    Examples
    --------
    >>> import zeonta
    >>> float(zeonta.dpo([float(i) for i in range(1, 30)], length=10).iloc[-1])
    -1.5

    References
    ----------
    https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/detrended-price-oscillator-dpo
    """
    length = validate_length(length)
    values = as_array(close, "close")

    shift = length // 2 + 1
    sma = rolling_mean(values, length)
    shifted_close = _shift(values, shift)
    result = shifted_close - sma

    return wrap_series(result, common_index(close), f"DPO_{length}")


@indicator(
    category="oscillators",
    summary="A WMA of two summed rate-of-change measures, built to spot major long-term bottoms.",
    reference=(
        "https://chartschool.stockcharts.com/table-of-contents/"
        "technical-indicators-and-overlays/technical-indicators/coppock-curve"
    ),
    outputs=("COPC",),
)
def coppock_curve(
    close: ArrayLike, long: int = 14, short: int = 11, wma_length: int = 10
) -> pd.Series:
    """Coppock Curve.

    ``Coppock = WMA(ROC(Close, long) + ROC(Close, short), wma_length)``.
    Edwin Coppock built the two ROC periods around how long, in his
    research, it took investor sentiment to recover from a loss —
    unconventional inputs, but the result is a slow, heavily-smoothed
    long-term momentum line, originally meant for monthly charts and major
    market bottoms rather than everyday trading.

    Parameters
    ----------
    close:
        Closing prices.
    long, short:
        The two Rate-of-Change lengths that get summed.
    wma_length:
        Length of the final weighted-moving-average smoothing.

    Returns
    -------
    pandas.Series
        Named ``COPC_{long}_{short}_{wma_length}``.

    Examples
    --------
    >>> import zeonta
    >>> prices = [float(i) for i in range(1, 60)]
    >>> float(zeonta.coppock_curve(prices, long=5, short=3, wma_length=3).iloc[-1])
    14.79952699292322

    References
    ----------
    https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/coppock-curve
    """
    long = validate_length(long, "long")
    short = validate_length(short, "short")
    wma_length = validate_length(wma_length, "wma_length")
    values = as_array(close, "close")

    combined = roc(values, length=long).to_numpy() + roc(values, length=short).to_numpy()
    result = rolling_wma(combined, wma_length)

    suffix = f"{long}_{short}_{wma_length}"
    return wrap_series(result, common_index(close), f"COPC_{suffix}")
