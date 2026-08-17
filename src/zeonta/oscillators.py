"""Momentum oscillators: RSI, Stochastic, MACD, CCI, Momentum, ROC, Williams
%R, Stochastic RSI, and the Awesome Oscillator.

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
    validate_length,
    wilder_values,
    wrap_frame,
    wrap_series,
)

__all__ = [
    "awesome_oscillator",
    "cci",
    "macd",
    "momentum",
    "roc",
    "rsi",
    "stoch",
    "stoch_rsi",
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
