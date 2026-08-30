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
    Number,
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
    validate_multiplier,
    wilder_values,
    wrap_frame,
    wrap_series,
)

__all__ = [
    "awesome_oscillator",
    "cci",
    "center_of_gravity",
    "cmo",
    "coppock_curve",
    "dpo",
    "elder_ray",
    "fisher_transform",
    "kst",
    "laguerre_rsi",
    "macd",
    "momentum",
    "ppo",
    "roc",
    "rsi",
    "rvgi",
    "smi",
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
    summary="Sum of gains vs. losses over a plain window, unlike RSI's Wilder smoothing.",
    reference=(
        "https://www.fidelity.com/learning-center/trading-investing/"
        "technical-analysis/technical-indicator-guide/cmo"
    ),
    outputs=("CMO",),
)
def cmo(close: ArrayLike, length: int = 14) -> pd.Series:
    """Chande Momentum Oscillator (Tushar Chande, 1994).

    ``CMO = 100 * (SumUp(n) - SumDown(n)) / (SumUp(n) + SumDown(n))``,
    where ``SumUp``/``SumDown`` are plain rolling sums of each bar's gain
    or loss. Built from the same up-move/down-move split as :func:`rsi`,
    but combined differently (a normalised difference rather than a
    ratio) and — unlike RSI — never smoothed, so a gain or loss drops out
    of the window completely once it ages past ``length`` bars rather
    than fading gradually.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        Look-back window. Chande's own book and various platforms cite
        ``9``, ``14`` and ``20`` as common choices; ``14`` (the default)
        matches this library's other Wilder-family oscillators.

    Returns
    -------
    pandas.Series
        Named ``CMO_{length}``, ranging -100 to +100. ``0`` wherever both
        sums are zero (a perfectly flat window), rather than an undefined
        ``0/0``.

    Examples
    --------
    >>> import zeonta
    >>> float(zeonta.cmo([10.0, 11.0, 10.5, 12.0, 11.5], length=4).iloc[-1])
    42.857142857142854

    References
    ----------
    https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/cmo
    """
    length = validate_length(length)
    values = as_array(close, "close")

    change = np.diff(values, prepend=np.nan)
    gains = np.where(np.isfinite(change), np.maximum(change, 0.0), np.nan)
    losses = np.where(np.isfinite(change), np.maximum(-change, 0.0), np.nan)

    sum_up = np.full(values.shape[0], np.nan, dtype="float64")
    sum_down = np.full(values.shape[0], np.nan, dtype="float64")
    sum_up[1:] = rolling_sum(gains[1:], length)
    sum_down[1:] = rolling_sum(losses[1:], length)

    total = sum_up + sum_down
    with np.errstate(divide="ignore", invalid="ignore"):
        result = np.where(total > 0.0, 100.0 * (sum_up - sum_down) / total, 0.0)
    result = np.where(np.isfinite(total), result, np.nan)

    return wrap_series(result, common_index(close), f"CMO_{length}")


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


@indicator(
    category="oscillators",
    summary="Ehlers' Fisher Transform: normalized price reshaped to sharpen its turning points.",
    reference="https://www.mesasoftware.com/papers/UsingTheFisherTransform.pdf",
    outputs=("FISHERT", "FISHERTs"),
)
def fisher_transform(high: ArrayLike, low: ArrayLike, length: int = 10) -> pd.DataFrame:
    """Fisher Transform (Ehlers).

    ``Price = (High + Low) / 2``; the price's position within its own
    ``n``-bar range is normalised to roughly -1..1 and lightly smoothed
    (``Value1[t] = 0.33 * 2 * (Position - 0.5) + 0.67 * Value1[t-1]``,
    clamped to ±0.999 so the next step never divides by zero); then
    ``Fish[t] = 0.5 * ln((1 + Value1[t]) / (1 - Value1[t])) + 0.5 * Fish[t-1]``.
    Ordinary price data has a roughly uniform-to-bimodal distribution, not a
    Gaussian one — the Fisher Transform reshapes it toward Gaussian, which
    makes large deviations genuinely rare events instead of routine noise,
    giving sharper, more clearly defined turning points than an oscillator
    built directly from price.

    Parameters
    ----------
    high, low:
        Price series of equal length.
    length:
        Look-back window for the high-low range the price is normalised
        against.

    Returns
    -------
    pandas.DataFrame
        ``FISHERT_{length}`` and ``FISHERTs_{length}`` — the transform
        itself, and that same line delayed by one bar (Ehlers' own
        "trigger" line, meant to be read as a crossover pair the same way
        :func:`macd`'s signal line is).

    Examples
    --------
    >>> import zeonta
    >>> high = [11.0, 12.0, 13.0, 12.5, 12.0, 11.5, 11.0, 12.0, 13.0, 14.0]
    >>> low = [9.0, 10.0, 11.0, 10.5, 10.0, 9.5, 9.0, 10.0, 11.0, 12.0]
    >>> float(zeonta.fisher_transform(high, low, length=5).iloc[-1, 0])
    0.379269728917503

    References
    ----------
    https://www.mesasoftware.com/papers/UsingTheFisherTransform.pdf
    """
    length = validate_length(length)
    require_aligned_index(high=high, low=low)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    size = require_same_length(high=high_values, low=low_values)

    price = (high_values + low_values) / 2.0
    highest = rolling_max(price, length)
    lowest = rolling_min(price, length)

    fish = np.full(size, np.nan, dtype="float64")
    start = length - 1
    if size > start:
        value1_prev = 0.0
        fish_prev = 0.0
        for i in range(start, size):
            span = highest[i] - lowest[i]
            if not (np.isfinite(price[i]) and np.isfinite(span)):
                # A gap leaves the recursive state frozen rather than
                # producing a value from missing data, the same convention
                # kama() and parabolic_sar() use for their own state.
                continue
            position = 0.0 if span == 0.0 else (price[i] - lowest[i]) / span - 0.5
            value1 = 0.33 * 2.0 * position + 0.67 * value1_prev
            value1 = min(max(value1, -0.999), 0.999)
            fish_value = 0.5 * np.log((1.0 + value1) / (1.0 - value1)) + 0.5 * fish_prev
            fish[i] = fish_value
            value1_prev = value1
            fish_prev = fish_value

    trigger = _shift(fish, 1)

    order = [f"FISHERT_{length}", f"FISHERTs_{length}"]
    return wrap_frame(
        dict(zip(order, (fish, trigger), strict=True)),
        common_index(high, low),
        order=order,
    )


@indicator(
    category="oscillators",
    summary="Ehlers' zero-lag oscillator: the balance point of price over the window.",
    reference="https://www.mesasoftware.com/papers/TheCGOscillator.pdf",
    outputs=("CG", "CGs"),
)
def center_of_gravity(high: ArrayLike, low: ArrayLike, length: int = 10) -> pd.DataFrame:
    """Center of Gravity Oscillator (John Ehlers, 2002).

    Treats the ``length`` prices in the window as weights placed along a
    beam, evenly spaced, and finds the balance point::

        Price = (High + Low) / 2
        CG[t] = -sum((1 + k) * Price[t-k], k=0..length-1) / sum(Price[t-k], k=0..length-1)

    (``k=0`` is the current bar.) A Simple Moving Average weights every
    bar equally, so its balance point sits exactly in the window's
    middle; Ehlers' insight was that inverting the sign of this natural
    balance point turns it into an oscillator that moves in phase with
    price and has essentially zero lag, unlike a conventional smoothed
    oscillator.

    Parameters
    ----------
    high, low:
        Price series of equal length.
    length:
        Window size. Ehlers' own suggested default is ``10``; he notes it
        should ideally be about half the dominant market cycle length.
        Must be >= 1.

    Returns
    -------
    pandas.DataFrame
        ``CG_{length}`` and its own one-bar-delayed trigger line
        ``CGs_{length}`` — Ehlers' own suggested crossover signal, the
        same trigger-line pattern :func:`fisher_transform` uses.

    Examples
    --------
    >>> import zeonta
    >>> high = [12.0, 13.0, 11.0, 14.0, 15.0]
    >>> low = [10.0, 11.0, 9.0, 12.0, 13.0]
    >>> float(zeonta.center_of_gravity(high, low, length=5).iloc[-1, 0])
    -2.8833333333333333

    References
    ----------
    https://www.mesasoftware.com/papers/TheCGOscillator.pdf
    """
    length = validate_length(length)
    require_aligned_index(high=high, low=low)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    size = require_same_length(high=high_values, low=low_values)

    price = (high_values + low_values) / 2.0
    weights = np.arange(1, length + 1, dtype="float64")

    result = np.full(size, np.nan, dtype="float64")
    for i in range(length - 1, size):
        window = price[i - length + 1 : i + 1][::-1]
        if not np.all(np.isfinite(window)):
            continue
        denom = window.sum()
        if denom != 0.0:
            result[i] = -np.dot(weights, window) / denom

    trigger = _shift(result, 1)
    order = [f"CG_{length}", f"CGs_{length}"]
    return wrap_frame(
        dict(zip(order, (result, trigger), strict=True)), common_index(high, low), order=order
    )


@indicator(
    category="oscillators",
    summary="RSI computed over a 4-stage Laguerre filter instead of Wilder smoothing.",
    reference="https://www.mesasoftware.com/papers/TimeWarp.pdf",
    outputs=("LRSI",),
)
def laguerre_rsi(close: ArrayLike, gamma: Number = 0.5) -> pd.Series:
    """Laguerre RSI (John Ehlers, 2004).

    Replaces Wilder's smoothing with a 4-stage Laguerre filter — a
    cascade of all-pass elements that "time warps" the delay between
    taps instead of using fixed unit delays, letting a useful RSI-like
    reading emerge from only 4 filter stages rather than a full look-back
    window::

        L0 = (1-gamma)*Close + gamma*L0[1]
        L1 = -gamma*L0 + L0[1] + gamma*L1[1]
        L2 = -gamma*L1 + L1[1] + gamma*L2[1]
        L3 = -gamma*L2 + L2[1] + gamma*L3[1]
        CU = sum(max(stage[i] - stage[i+1], 0) for i in 0..2)
        CD = sum(max(stage[i+1] - stage[i], 0) for i in 0..2)
        LRSI = CU / (CU + CD)

    Parameters
    ----------
    close:
        Closing prices.
    gamma:
        Damping factor for the Laguerre filter, in ``(0, 1)``. Ehlers'
        own example uses ``0.5``, and notes it can be adjusted up to
        around ``0.8`` for extra smoothing.

    Returns
    -------
    pandas.Series
        Named ``LRSI_{gamma}``, ranging 0 to 1.

    Notes
    -----
    Because the filter starts from a zero initial state, the first few
    bars are a warm-up transient of the recursion settling down, not a
    meaningful reading — Ehlers' own paper does not specify a fixed
    warm-up length, since the filter (unlike a windowed indicator) never
    stops being influenced, in ever-diminishing amounts, by its start.
    Confirmed empirically on a synthetic trend well past this transient:
    the reading settles at exactly ``1.0`` at the end of a clean uptrend
    and ``0.0`` at the end of a clean downtrend.

    Examples
    --------
    >>> import zeonta
    >>> close = [10.0, 11.0, 10.5, 12.0, 13.0, 12.5]
    >>> float(zeonta.laguerre_rsi(close, gamma=0.5).iloc[-1])
    1.0

    References
    ----------
    https://www.mesasoftware.com/papers/TimeWarp.pdf
    """
    gamma = validate_multiplier(gamma, "gamma")
    if gamma >= 1.0:
        raise ValueError(f"'gamma' must be < 1, got {gamma}")
    values = as_array(close, "close")
    size = values.shape[0]

    result = np.full(size, np.nan, dtype="float64")
    l0 = l1 = l2 = l3 = 0.0
    rsi_value = 0.0
    for i in range(size):
        price = values[i]
        if not np.isfinite(price):
            # Freeze the filter's state through a gap rather than feeding
            # it missing data, the same convention fisher_transform uses.
            result[i] = rsi_value
            continue
        l0_prev, l1_prev, l2_prev, l3_prev = l0, l1, l2, l3
        l0 = (1.0 - gamma) * price + gamma * l0_prev
        l1 = -gamma * l0 + l0_prev + gamma * l1_prev
        l2 = -gamma * l1 + l1_prev + gamma * l2_prev
        l3 = -gamma * l2 + l2_prev + gamma * l3_prev

        cu = cd = 0.0
        if l0 >= l1:
            cu += l0 - l1
        else:
            cd += l1 - l0
        if l1 >= l2:
            cu += l1 - l2
        else:
            cd += l2 - l1
        if l2 >= l3:
            cu += l2 - l3
        else:
            cd += l3 - l2

        if cu + cd != 0.0:
            rsi_value = cu / (cu + cd)
        result[i] = rsi_value

    return wrap_series(result, common_index(close), f"LRSI_{gamma}")


@indicator(
    category="oscillators",
    summary="Four weighted-and-smoothed ROC cycles combined into one long-cycle momentum line.",
    reference="https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/prings-know-sure-thing-kst",
    outputs=("KST", "KSTs"),
)
def kst(
    close: ArrayLike,
    roc1: int = 10,
    roc2: int = 15,
    roc3: int = 20,
    roc4: int = 30,
    sma1: int = 10,
    sma2: int = 10,
    sma3: int = 10,
    sma4: int = 15,
    signal: int = 9,
) -> pd.DataFrame:
    """Pring's Know Sure Thing (Martin Pring, 1992).

    Four Rate-of-Change cycles, each smoothed by its own SMA, weighted by
    increasing multiples and summed::

        KST = 1*SMA(ROC(roc1),sma1) + 2*SMA(ROC(roc2),sma2)
            + 3*SMA(ROC(roc3),sma3) + 4*SMA(ROC(roc4),sma4)

    with a ``signal``-period SMA of ``KST`` as its own trigger line.
    Longer-period components are weighted more heavily, on the theory
    that they capture more significant momentum cycles than short-term
    noise.

    Parameters
    ----------
    close:
        Closing prices.
    roc1, roc2, roc3, roc4:
        The four Rate-of-Change look-backs. Pring's own daily-chart
        defaults are ``10, 15, 20, 30``.
    sma1, sma2, sma3, sma4:
        Smoothing period applied to each ROC in turn, paired
        positionally. Pring's own defaults are ``10, 10, 10, 15``.
    signal:
        SMA period for the trigger line. Pring's own default is ``9``.

    Returns
    -------
    pandas.DataFrame
        Columns ``KST_{roc1}_{roc2}_{roc3}_{roc4}`` and
        ``KSTs_{roc1}_{roc2}_{roc3}_{roc4}`` (the signal line).

    Examples
    --------
    >>> import zeonta
    >>> close = [10.0, 11.0, 9.0, 12.0, 8.0, 13.0, 10.5, 11.5, 14.0, 9.5, 12.5, 13.5]
    >>> out = zeonta.kst(close, roc1=2, roc2=3, roc3=4, roc4=5,
    ...                  sma1=2, sma2=2, sma3=2, sma4=2, signal=2)
    >>> round(float(out.iloc[-1, 0]), 4)
    124.9286
    >>> round(float(out.iloc[-1, 1]), 4)
    64.0211

    References
    ----------
    https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/prings-know-sure-thing-kst
    """
    for name, value in (
        ("roc1", roc1),
        ("roc2", roc2),
        ("roc3", roc3),
        ("roc4", roc4),
        ("sma1", sma1),
        ("sma2", sma2),
        ("sma3", sma3),
        ("sma4", sma4),
        ("signal", signal),
    ):
        validate_length(value, name)

    values = as_array(close, "close")
    size = values.shape[0]

    def _smoothed_roc(period: int, smoothing: int) -> np.ndarray:
        change = np.full(size, np.nan, dtype="float64")
        if size > period:
            with np.errstate(divide="ignore", invalid="ignore"):
                change[period:] = (values[period:] - values[:-period]) / values[:-period] * 100.0
        return rolling_mean(change, smoothing)

    components = [
        _smoothed_roc(roc1, sma1),
        _smoothed_roc(roc2, sma2),
        _smoothed_roc(roc3, sma3),
        _smoothed_roc(roc4, sma4),
    ]
    result = np.zeros(size, dtype="float64")
    for weight, component in enumerate(components, start=1):
        result = result + weight * component
    signal_line = rolling_mean(result, signal)

    suffix = f"{roc1}_{roc2}_{roc3}_{roc4}"
    order = [f"KST_{suffix}", f"KSTs_{suffix}"]
    return wrap_frame(
        dict(zip(order, (result, signal_line), strict=True)), common_index(close), order=order
    )


@indicator(
    category="oscillators",
    summary="Symmetrically weighted ratio of body strength to range: a smoother BOP.",
    reference="https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/relative-vigor-index",
    outputs=("RVGI", "RVGIs"),
)
def rvgi(
    open: ArrayLike, high: ArrayLike, low: ArrayLike, close: ArrayLike, length: int = 10
) -> pd.DataFrame:
    """Relative Vigor Index.

    The idea behind :func:`bop` (closing strength relative to the bar's
    own range), smoothed two ways at once. Both the body and the range
    are first symmetrically weighted over 4 bars (``1-2-2-1``, most
    weight in the middle) before an ``n``-bar SMA is taken of each::

        Body[t] = (Body[t] + 2*Body[t-1] + 2*Body[t-2] + Body[t-3]) / 6,  Body = Close - Open
        Range[t] = (Range[t] + 2*Range[t-1] + 2*Range[t-2] + Range[t-3]) / 6,  Range = High - Low
        RVGI = SMA(Body, n) / SMA(Range, n)

    with the same ``1-2-2-1`` weighting applied to ``RVGI`` itself as its
    signal line.

    Parameters
    ----------
    open, high, low, close:
        Series of equal length.
    length:
        SMA window applied to the pre-weighted body and range. Must be
        >= 1.

    Returns
    -------
    pandas.DataFrame
        Columns ``RVGI_{length}`` and ``RVGIs_{length}`` (the signal
        line).

    Examples
    --------
    >>> import zeonta
    >>> open_ = [10.0, 10.5, 9.5, 11.0, 10.0, 12.0, 11.5, 10.5, 11.8, 12.2]
    >>> high = [11.0, 11.5, 10.5, 12.0, 11.5, 13.0, 12.5, 11.5, 12.5, 13.0]
    >>> low = [9.5, 9.8, 8.8, 10.2, 9.5, 11.0, 10.5, 9.8, 11.0, 11.8]
    >>> close = [10.8, 10.0, 10.8, 11.5, 11.2, 12.5, 11.0, 11.2, 12.3, 12.0]
    >>> out = zeonta.rvgi(open_, high, low, close, length=3)
    >>> round(float(out.iloc[-1, 0]), 6)
    0.15528
    >>> round(float(out.iloc[-1, 1]), 6)
    0.254987

    References
    ----------
    https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/relative-vigor-index
    """
    length = validate_length(length)
    require_aligned_index(open=open, high=high, low=low, close=close)
    open_values = as_array(open, "open")
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    close_values = as_array(close, "close")
    require_same_length(open=open_values, high=high_values, low=low_values, close=close_values)

    def _weighted4(x: np.ndarray) -> np.ndarray:
        out = np.full(x.shape[0], np.nan, dtype="float64")
        if x.shape[0] > 3:
            weighted = x[3:] + 2.0 * x[2:-1] + 2.0 * x[1:-2] + x[:-3]
            out[3:] = weighted / 6.0
        return out

    body = _weighted4(close_values - open_values)
    span = _weighted4(high_values - low_values)
    with np.errstate(divide="ignore", invalid="ignore"):
        result = rolling_mean(body, length) / rolling_mean(span, length)
    signal_line = _weighted4(result)

    order = [f"RVGI_{length}", f"RVGIs_{length}"]
    return wrap_frame(
        dict(zip(order, (result, signal_line), strict=True)),
        common_index(open, high, low, close),
        order=order,
    )


@indicator(
    category="oscillators",
    summary="Double-smoothed stochastic that measures distance from the range's midpoint.",
    reference="https://www.tradingview.com/support/solutions/43000589925-stochastic-momentum-index/",
    outputs=("SMI", "SMIs"),
)
def smi(
    high: ArrayLike,
    low: ArrayLike,
    close: ArrayLike,
    length: int = 10,
    fast: int = 3,
    slow: int = 3,
    signal_length: int = 3,
) -> pd.DataFrame:
    """Stochastic Momentum Index (William Blau, 1993).

    A refinement of :func:`stoch`: rather than measuring where the close
    sits *within* the high-low range, it measures the close's distance
    from the range's *midpoint*, and double-smooths both that distance
    and the range itself with two EMA passes before dividing::

        Mid = (HighestHigh(length) + LowestLow(length)) / 2
        Distance = Close - Mid;  Range = HighestHigh(length) - LowestLow(length)
        SMI = 200 * EMA(EMA(Distance, fast), slow) / EMA(EMA(Range, fast), slow)

    with an EMA of ``SMI`` itself as the signal line. Unlike the fast/slow
    %K of an ordinary stochastic, both EMA passes here smooth the same
    two quantities, so ``SMI`` reaches its stated -100/+100 bounds far
    less abruptly.

    Parameters
    ----------
    high, low, close:
        Price series of equal length.
    length:
        Look-back for the highest-high/lowest-low range.
    fast, slow:
        The two successive EMA smoothing periods.
    signal_length:
        EMA period for the signal line.

    Returns
    -------
    pandas.DataFrame
        Columns ``SMI_{length}_{fast}_{slow}`` and
        ``SMIs_{length}_{fast}_{slow}`` (the signal line).

    Examples
    --------
    >>> import zeonta
    >>> high = [12.0, 13.0, 11.0, 14.0, 15.0, 13.5, 16.0, 14.5, 15.5, 17.0]
    >>> low = [10.0, 11.0, 9.0, 12.0, 13.0, 11.5, 14.0, 12.5, 13.5, 15.0]
    >>> close = [11.0, 12.5, 10.0, 13.5, 14.5, 12.5, 15.5, 13.5, 15.0, 16.5]
    >>> out = zeonta.smi(high, low, close, length=3, fast=2, slow=2, signal_length=2)
    >>> round(float(out.iloc[-1, 0]), 6)
    51.886998
    >>> round(float(out.iloc[-1, 1]), 6)
    43.66447

    References
    ----------
    https://www.tradingview.com/support/solutions/43000589925-stochastic-momentum-index/
    """
    length = validate_length(length)
    fast = validate_length(fast, "fast")
    slow = validate_length(slow, "slow")
    signal_length = validate_length(signal_length, "signal_length")
    require_aligned_index(high=high, low=low, close=close)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    close_values = as_array(close, "close")
    require_same_length(high=high_values, low=low_values, close=close_values)

    highest = rolling_max(high_values, length)
    lowest = rolling_min(low_values, length)
    midpoint = (highest + lowest) / 2.0
    distance = close_values - midpoint
    span = highest - lowest

    smoothed_distance = ema_values(ema_values(distance, fast), slow)
    smoothed_span = ema_values(ema_values(span, fast), slow)
    with np.errstate(divide="ignore", invalid="ignore"):
        result = 200.0 * smoothed_distance / smoothed_span
    signal_line = ema_values(result, signal_length)

    suffix = f"{length}_{fast}_{slow}"
    order = [f"SMI_{suffix}", f"SMIs_{suffix}"]
    return wrap_frame(
        dict(zip(order, (result, signal_line), strict=True)),
        common_index(high, low, close),
        order=order,
    )
