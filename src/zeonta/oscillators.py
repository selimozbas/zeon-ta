"""Momentum oscillators: RSI, Stochastic, MACD and CCI.

Formulas follow the TA 101 *Oscillators* module.
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

__all__ = ["cci", "macd", "rsi", "stoch"]


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

    References
    ----------
    https://ta.cognicode.org/learn/rsi
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

    References
    ----------
    https://ta.cognicode.org/learn/stochastic
    """
    length = validate_length(length)
    smooth_k = validate_length(smooth_k, "smooth_k")
    smooth_d = validate_length(smooth_d, "smooth_d")

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

    References
    ----------
    https://ta.cognicode.org/learn/macd
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

    References
    ----------
    https://ta.cognicode.org/learn/cci
    """
    length = validate_length(length)
    if constant <= 0:
        raise ValueError(f"'constant' must be > 0, got {constant}")

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
