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
    super_smoother_values,
    validate_length,
    validate_multiplier,
    wilder_values,
    wrap_frame,
    wrap_series,
)

__all__ = [
    "awesome_oscillator",
    "bias",
    "cci",
    "center_of_gravity",
    "cmo",
    "connors_rsi",
    "coppock_curve",
    "cyber_cycle",
    "dpo",
    "elder_ray",
    "even_better_sinewave",
    "fisher_transform",
    "ift_rsi",
    "kdj",
    "kst",
    "laguerre_rsi",
    "macd",
    "momentum",
    "ppo",
    "psl",
    "qqe",
    "reflex_trendflex",
    "roc",
    "roofing_filter",
    "rsi",
    "rvgi",
    "smi",
    "stoch",
    "stoch_rsi",
    "trix",
    "tsi",
    "ultimate_oscillator",
    "voss_predictive_filter",
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
    order = [f"STOCHk_{suffix}", f"STOCHd_{suffix}"]
    return wrap_frame(
        {f"STOCHk_{suffix}": percent_k, f"STOCHd_{suffix}": percent_d},
        common_index(high, low, close),
        order=order,
        roles={"k": order[0], "d": order[1]},
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
        roles={"k": order[0], "d": order[1]},
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
        roles={"line": order[0], "signal": order[1], "histogram": order[2]},
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
        roles={"bull_power": order[0], "bear_power": order[1]},
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
        roles={"line": order[0], "signal": order[1]},
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
        roles={"line": order[0], "signal": order[1], "histogram": order[2]},
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
        roles={"line": order[0], "signal": order[1]},
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
        roles={"line": order[0], "trigger": order[1]},
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
        dict(zip(order, (result, trigger), strict=True)),
        common_index(high, low),
        order=order,
        roles={"line": order[0], "trigger": order[1]},
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
        dict(zip(order, (result, signal_line), strict=True)),
        common_index(close),
        order=order,
        roles={"line": order[0], "signal": order[1]},
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
        roles={"line": order[0], "signal": order[1]},
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
        roles={"line": order[0], "signal": order[1]},
    )


@indicator(
    category="oscillators",
    summary="Percentage deviation of Close from its own SMA.",
    outputs=("BIAS",),
    reference="https://research.titanfx.com/technical-analysis/ma/bias",
)
def bias(close: ArrayLike, length: int = 26) -> pd.Series:
    """Bias.

    A staple of Chinese/Taiwanese technical analysis, putting a number on
    how far price has stretched away from its own moving average::

        BIAS = (Close - SMA(Close, length)) / SMA(Close, length) * 100

    Positive means price sits above its own average by that many percent;
    negative the mirror. A large reading in either direction is commonly
    read as "stretched too far, a pullback or rebound is more likely" —
    unlike :func:`efficiency_ratio` or :func:`choppiness_index`, which
    describe how a *window* moved, this describes a single distance.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        SMA period. Commonly cited defaults are ``6``, ``12`` or ``24``;
        this library uses ``26`` to match the value most commonly shipped
        as the indicator's own default.

    Returns
    -------
    pandas.Series
        Named ``BIAS_{length}``. ``NaN`` wherever the window's SMA is
        exactly ``0``, rather than an undefined division.

    Examples
    --------
    >>> import zeonta
    >>> close = [10.0, 11.0, 9.0, 12.0]
    >>> round(float(zeonta.bias(close, length=4).iloc[-1]), 6)
    14.285714

    References
    ----------
    https://research.titanfx.com/technical-analysis/ma/bias
    """
    length = validate_length(length)
    values = as_array(close, "close")
    average = rolling_mean(values, length)
    with np.errstate(divide="ignore", invalid="ignore"):
        result = np.where(average != 0.0, (values - average) / average * 100.0, np.nan)
    return wrap_series(result, common_index(close), f"BIAS_{length}")


@indicator(
    category="oscillators",
    summary="Percentage of up-closes over a rolling window — raw market sentiment.",
    outputs=("PSL",),
    reference=(
        "https://help.tradestation.com/10_00/eng/tradestationhelp/elanalysis/"
        "indicator/psychological_line_indicator_.htm"
    ),
)
def psl(close: ArrayLike, length: int = 12) -> pd.Series:
    """Psychological Line.

    The share of up-closing bars over a rolling window, as a percentage::

        PSL = (number of bars where Close > Close[-1] in the last n) / n * 100

    A pure vote-counting sentiment gauge — it only asks *how often* price
    rose, never *by how much*, unlike every ratio-based oscillator in this
    module (:func:`rsi`, :func:`cmo`, ...) which weighs the size of each
    move.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        Rolling window, in bars. Commonly cited defaults are ``12`` or
        ``24``.

    Returns
    -------
    pandas.Series
        Named ``PSL_{length}``, ranging 0-100.

    Examples
    --------
    >>> import zeonta
    >>> close = [10.0, 11.0, 10.5, 12.0, 13.0]
    >>> zeonta.psl(close, length=4).round(4).tolist()
    [nan, nan, nan, nan, 75.0]

    References
    ----------
    https://help.tradestation.com/10_00/eng/tradestationhelp/elanalysis/indicator/psychological_line_indicator_.htm
    """
    length = validate_length(length)
    values = as_array(close, "close")
    change = np.diff(values, prepend=np.nan)
    up_bar = np.where(np.isfinite(change), (change > 0.0).astype("float64"), np.nan)
    result = rolling_mean(up_bar, length) * 100.0
    return wrap_series(result, common_index(close), f"PSL_{length}")


@indicator(
    category="oscillators",
    summary="Stochastic %K/%D reworked with Wilder smoothing, plus a fast, overshooting J line.",
    outputs=("K", "D", "J"),
    reference="https://www.tradingview.com/scripts/kdj/",
)
def kdj(
    high: ArrayLike,
    low: ArrayLike,
    close: ArrayLike,
    length: int = 9,
    signal: int = 3,
) -> pd.DataFrame:
    """KDJ — a stochastic variant popular in Chinese-market technical analysis.

    Starts from the same Raw Stochastic Value :func:`stoch` calls ``%K``
    before smoothing, then smooths it twice with Wilder's recursion
    (``alpha = 1/signal``, the same recursion :func:`smma` exposes) rather
    than a plain SMA::

        RSV = 100 * (Close - LowestLow(length)) / (HighestHigh(length) - LowestLow(length))
        K = Wilder(RSV, signal)
        D = Wilder(K, signal)
        J = 3*K - 2*D

    ``J`` extrapolates past the ``K``/``D`` move rather than averaging it,
    so it swings outside the usual 0-100 range — the point of it is to
    signal overbought/oversold conditions *before* ``K`` and ``D`` reach
    their own extremes.

    Parameters
    ----------
    high, low, close:
        Price series of equal length.
    length:
        Look-back for the Raw Stochastic Value.
    signal:
        Wilder smoothing period applied twice (RSV to K, then K to D).

    Returns
    -------
    pandas.DataFrame
        Columns ``K_{length}_{signal}``, ``D_{length}_{signal}``,
        ``J_{length}_{signal}``.

    Examples
    --------
    >>> import zeonta
    >>> high = [12.0, 13.0, 11.0, 14.0, 15.0, 13.5, 16.0]
    >>> low = [10.0, 11.0, 9.0, 12.0, 13.0, 11.5, 14.0]
    >>> close = [11.0, 12.5, 10.0, 13.5, 14.5, 12.5, 15.5]
    >>> out = zeonta.kdj(high, low, close, length=3, signal=2)
    >>> round(float(out.iloc[-1, 0]), 6)
    70.233135

    References
    ----------
    https://www.tradingview.com/scripts/kdj/
    """
    length = validate_length(length)
    signal = validate_length(signal, "signal")
    require_aligned_index(high=high, low=low, close=close)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    close_values = as_array(close, "close")
    require_same_length(high=high_values, low=low_values, close=close_values)

    highest = rolling_max(high_values, length)
    lowest = rolling_min(low_values, length)
    span = highest - lowest
    with np.errstate(divide="ignore", invalid="ignore"):
        fast_k = np.where(span != 0.0, 100.0 * (close_values - lowest) / span, np.nan)

    k_line = wilder_values(fast_k, signal)
    d_line = wilder_values(k_line, signal)
    j_line = 3.0 * k_line - 2.0 * d_line

    suffix = f"{length}_{signal}"
    order = [f"K_{suffix}", f"D_{suffix}", f"J_{suffix}"]
    return wrap_frame(
        dict(zip(order, (k_line, d_line, j_line), strict=True)),
        common_index(high, low, close),
        order=order,
        roles={"k": order[0], "d": order[1], "j": order[2]},
    )


@indicator(
    category="oscillators",
    summary="A smoothed RSI with an ATR-style trailing band, flipping like a Supertrend on RSI.",
    outputs=("QQE", "QQEl"),
    reference=(
        "https://www.prorealcode.com/prorealtime-indicators/"
        "qqe-indicator-quantitative-qualitative-estimation/"
    ),
)
def qqe(
    close: ArrayLike,
    length: int = 14,
    smooth: int = 5,
    factor: Number = 4.236,
) -> pd.DataFrame:
    """Quantitative Qualitative Estimation.

    Smooths :func:`rsi` with an EMA, measures that smoothed line's own
    bar-to-bar volatility (Wilder-smoothed twice, at ``2*length - 1``
    bars — the same "double the RSI period minus one" period Wilder-style
    indicators use elsewhere), and uses it to build a trailing band around
    the smoothed RSI — the same one-way-ratchet, flip-on-cross construction
    :func:`supertrend` uses on price, applied to RSI instead::

        RsiMa = EMA(RSI(length), smooth)
        AtrRsi = |RsiMa - RsiMa[-1]|
        DeltaFastAtrRsi = EMA(EMA(AtrRsi, 2*length-1), 2*length-1) * factor
        newlong = RsiMa - DeltaFastAtrRsi ; newshort = RsiMa + DeltaFastAtrRsi

    ``longband`` only ratchets up while ``RsiMa`` stays above it,
    ``shortband`` only ratchets down while ``RsiMa`` stays below it, and
    the trend flips to long when ``RsiMa`` crosses above the previous
    ``shortband``, or to short when it crosses below the previous
    ``longband``. The trailing line (``QQEl``) then follows whichever band
    matches the current trend.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        RSI period.
    smooth:
        EMA period smoothing the RSI before everything else is built from it.
    factor:
        Multiplier scaling the double-smoothed volatility into a band
        width. The commonly cited default is ``4.236``.

    Returns
    -------
    pandas.DataFrame
        Columns ``QQE_{length}_{smooth}_{factor}`` (the smoothed RSI) and
        ``QQEl_{length}_{smooth}_{factor}`` (the trailing trend band, on
        the same 0-100 scale).

    Notes
    -----
    QQE has no single academic paper behind it — it originates as a
    MetaTrader community indicator — but its band and trend-flip
    construction is precise and cross-confirmed identically across
    multiple independent implementations (this library verified it
    against both a documented ProRealTime port and pandas-ta-classic's
    own source), unlike indicators this library has declined (STC,
    MavilimW) where the recursion itself could not be pinned down.

    Examples
    --------
    >>> import zeonta
    >>> close = list(range(1, 31)) + list(range(29, 14, -1)) + list(range(16, 41))
    >>> out = zeonta.qqe(close, length=5, smooth=2, factor=2.0)
    >>> bool(out.iloc[-1, 0] > out.iloc[-1, 1])
    True

    References
    ----------
    https://www.prorealcode.com/prorealtime-indicators/qqe-indicator-quantitative-qualitative-estimation/
    """
    length = validate_length(length)
    smooth = validate_length(smooth, "smooth")
    factor = validate_multiplier(factor, "factor")
    values = as_array(close, "close")
    size = values.shape[0]

    rsi_values = rsi(values, length=length).to_numpy()
    rsi_ma = ema_values(rsi_values, smooth)
    atr_rsi = np.abs(np.diff(rsi_ma, prepend=np.nan))
    wilders_period = 2 * length - 1
    ma_atr_rsi = ema_values(atr_rsi, wilders_period)
    delta = ema_values(ma_atr_rsi, wilders_period) * factor

    new_long = rsi_ma - delta
    new_short = rsi_ma + delta

    long_band = np.full(size, np.nan, dtype="float64")
    short_band = np.full(size, np.nan, dtype="float64")
    trend = np.full(size, np.nan, dtype="float64")
    line = np.full(size, np.nan, dtype="float64")

    # rsi_ma and delta are both built entirely from ema_values()/wilder_values(),
    # which hold their previous output forward through any gap rather than ever
    # re-emitting NaN once seeded — so once this loop's own start bar is found,
    # every later bar is guaranteed finite too; no gap-freeze branch is needed
    # inside the loop itself, unlike this library's raw-price sequential
    # indicators (supertrend, laguerre_rsi, heikin_ashi, ...).
    finite = np.isfinite(delta) & np.isfinite(rsi_ma)
    start = int(np.argmax(finite)) if finite.any() else -1

    if start >= 0:
        long_band[start] = new_long[start]
        short_band[start] = new_short[start]
        trend[start] = 1.0
        line[start] = long_band[start]

        for i in range(start + 1, size):
            previous_rsi_ma = rsi_ma[i - 1]
            previous_long = long_band[i - 1]
            previous_short = short_band[i - 1]

            if previous_rsi_ma > previous_long and rsi_ma[i] > previous_long:
                long_band[i] = max(previous_long, new_long[i])
            else:
                long_band[i] = new_long[i]

            if previous_rsi_ma < previous_short and rsi_ma[i] < previous_short:
                short_band[i] = min(previous_short, new_short[i])
            else:
                short_band[i] = new_short[i]

            crossed_above_short = previous_rsi_ma <= previous_short and rsi_ma[i] > previous_short
            crossed_below_long = previous_rsi_ma >= previous_long and rsi_ma[i] < previous_long
            if crossed_above_short:
                trend[i] = 1.0
            elif crossed_below_long:
                trend[i] = -1.0
            else:
                trend[i] = trend[i - 1]

            line[i] = long_band[i] if trend[i] == 1.0 else short_band[i]

    suffix = f"{length}_{smooth}_{factor}"
    order = [f"QQE_{suffix}", f"QQEl_{suffix}"]
    return wrap_frame(
        dict(zip(order, (rsi_ma, line), strict=True)),
        common_index(close),
        order=order,
        roles={"rsi": order[0], "trend_line": order[1]},
    )


def _streak_values(change: np.ndarray) -> np.ndarray:
    """Signed run length of consecutive up- or down-closes.

    Positive while closes keep rising, negative while they keep falling,
    reset to ``0`` on an unchanged close or a missing bar.
    """
    size = change.shape[0]
    streak = np.zeros(size, dtype="float64")
    for i in range(1, size):
        move = change[i]
        if not np.isfinite(move) or move == 0.0:
            streak[i] = 0.0
        elif move > 0.0:
            streak[i] = streak[i - 1] + 1.0 if streak[i - 1] > 0.0 else 1.0
        else:
            streak[i] = streak[i - 1] - 1.0 if streak[i - 1] < 0.0 else -1.0
    return streak


def _rolling_percent_rank(values: np.ndarray, length: int) -> np.ndarray:
    """``100 * (count of the last length values <= the newest one) / length``."""
    size = values.shape[0]
    result = np.full(size, np.nan, dtype="float64")
    for i in range(length - 1, size):
        window = values[i - length + 1 : i + 1]
        if not np.all(np.isfinite(window)):
            continue
        result[i] = 100.0 * np.count_nonzero(window <= window[-1]) / length
    return result


@indicator(
    category="oscillators",
    summary="Composite RSI averaging price RSI, streak RSI and a 1-bar-return percent rank.",
    outputs=("CRSI",),
    reference="https://www.tradingview.com/support/solutions/43000502017-connors-rsi-crsi/",
)
def connors_rsi(
    close: ArrayLike,
    rsi_length: int = 3,
    streak_length: int = 2,
    rank_length: int = 100,
) -> pd.Series:
    """Connors RSI (Larry Connors).

    Averages three independent readings of the same close series, each
    built for a different kind of short-term mean-reversion signal::

        CRSI = (RSI(Close, rsi_length) + RSI(Streak, streak_length)
                + PercentRank(ROC(1), rank_length)) / 3

    ``Streak`` is the signed run length of consecutive up- or
    down-closes (positive while price keeps rising, negative while it
    keeps falling, reset to ``0`` on an unchanged close), and
    ``RSI(Streak, ...)`` applies the ordinary :func:`rsi` recursion to
    that streak series instead of to price — asking "is the current
    up/down run itself unusually long?" rather than "is price itself
    overbought?". ``PercentRank(ROC(1), rank_length)`` — the fraction of
    the last ``rank_length`` one-bar returns that this bar's own return
    equals or exceeds — adds a third, magnitude-aware read that neither
    RSI term captures on its own.

    Parameters
    ----------
    close:
        Closing prices.
    rsi_length:
        RSI period applied to price. Connors' own default is ``3``.
    streak_length:
        RSI period applied to the streak. Connors' own default is ``2``.
    rank_length:
        Look-back for the percent-rank term. Connors' own default is ``100``.

    Returns
    -------
    pandas.Series
        Named ``CRSI_{rsi_length}_{streak_length}_{rank_length}``, ranging
        0-100 like each of its three components.

    Examples
    --------
    >>> import zeonta
    >>> close = [10.0, 10.5, 11.0, 10.8, 11.2, 11.5, 11.3, 11.6, 11.9, 11.7]
    >>> result = zeonta.connors_rsi(close, rsi_length=3, streak_length=2, rank_length=5)
    >>> round(float(result.iloc[-1]), 6)
    43.606594

    References
    ----------
    https://www.tradingview.com/support/solutions/43000502017-connors-rsi-crsi/
    """
    rsi_length = validate_length(rsi_length, "rsi_length")
    streak_length = validate_length(streak_length, "streak_length")
    rank_length = validate_length(rank_length, "rank_length", minimum=2)

    values = as_array(close, "close")
    change = np.diff(values, prepend=np.nan)
    streak = _streak_values(change)

    rsi_close = rsi(values, length=rsi_length).to_numpy()
    rsi_streak = rsi(streak, length=streak_length).to_numpy()
    one_bar_roc = roc(values, length=1).to_numpy()
    percent_rank = _rolling_percent_rank(one_bar_roc, rank_length)

    result = (rsi_close + rsi_streak + percent_rank) / 3.0
    suffix = f"{rsi_length}_{streak_length}_{rank_length}"
    return wrap_series(result, common_index(close), f"CRSI_{suffix}")


@indicator(
    category="oscillators",
    summary="RSI compressed toward -1/+1 through Ehlers' Inverse Fisher Transform.",
    outputs=("IFTRSI",),
    reference="https://www.mesasoftware.com/papers/TheInverseFisherTransform.pdf",
)
def ift_rsi(close: ArrayLike, length: int = 14, smooth: int = 9) -> pd.Series:
    """Inverse Fisher Transform of RSI (John Ehlers).

    Rescales :func:`rsi` to roughly ``[-5, 5]``, smooths it, and squashes
    the result through the inverse hyperbolic-tangent-shaped Inverse
    Fisher Transform::

        v1 = 0.1 * (RSI(length) - 50)
        v2 = WMA(v1, smooth)
        IFTRSI = (exp(2*v2) - 1) / (exp(2*v2) + 1)

    The transform's own shape does most of the work: near the middle it
    passes ``v2`` through almost unchanged, but it compresses everything
    else hard toward ``-1`` or ``+1`` — RSI's own gentle 0-100 curve
    becomes a near-binary reading, trading nuance for very clear
    turning-point signals.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        RSI period.
    smooth:
        WMA period smoothing the rescaled RSI before the transform.
        Ehlers' own default is ``9``.

    Returns
    -------
    pandas.Series
        Named ``IFTRSI_{length}_{smooth}``, ranging -1 to 1.

    Examples
    --------
    >>> import zeonta
    >>> round(float(zeonta.ift_rsi(list(range(1, 40)), length=14, smooth=9).iloc[-1]), 6)
    0.999909

    References
    ----------
    https://www.mesasoftware.com/papers/TheInverseFisherTransform.pdf
    """
    length = validate_length(length)
    smooth = validate_length(smooth, "smooth")

    rsi_values = rsi(close, length=length).to_numpy()
    v1 = 0.1 * (rsi_values - 50.0)
    v2 = rolling_wma(v1, smooth)
    with np.errstate(over="ignore"):
        exponent = np.exp(2.0 * v2)
    result = (exponent - 1.0) / (exponent + 1.0)

    return wrap_series(result, common_index(close), f"IFTRSI_{length}_{smooth}")


def _two_pole_highpass_values(values: np.ndarray, period: int) -> np.ndarray:
    """Ehlers' 2-pole high-pass filter (the "2PHP" recipe from his own Swiss Army Knife paper).

    Zeroed for the first *period* bars rather than left undefined — his
    own EasyLanguage bootstrap convention.
    """
    size = values.shape[0]
    angle = 2.0 * np.pi / period
    alpha1 = (np.cos(angle) + np.sin(angle) - 1.0) / np.cos(angle)
    c0 = (1.0 - alpha1 / 2.0) ** 2
    a1 = 2.0 * (1.0 - alpha1)
    a2 = -((1.0 - alpha1) ** 2)

    result = np.zeros(size, dtype="float64")
    for i in range(period, size):
        window = values[i - 2 : i + 1]
        previous = result[i - 2 : i]
        if not np.all(np.isfinite(window)) or not np.all(np.isfinite(previous)):
            result[i] = result[i - 1]  # freeze through a gap rather than propagate NaN
            continue
        result[i] = c0 * (values[i] - 2.0 * values[i - 1] + values[i - 2]) + (
            a1 * result[i - 1] + a2 * result[i - 2]
        )
    return result


@indicator(
    category="oscillators",
    summary="2-pole highpass then a SuperSmoother low-pass, isolating a chosen band of cycles.",
    outputs=("ROOF",),
    reference="https://www.mesasoftware.com/papers/SwissArmyKnifeIndicator.pdf",
)
def roofing_filter(close: ArrayLike, hp_length: int = 48, lp_length: int = 10) -> pd.Series:
    """Roofing Filter (John Ehlers).

    Removes both ends of the spectrum from price: a 2-pole high-pass
    filter removes cycles longer than ``hp_length`` (the slow drift an
    oscillator doesn't want to react to), and :func:`super_smoother` then
    removes cycles shorter than ``lp_length`` (the aliasing noise an
    ordinary moving average lets through). What is left is only the band
    of cycles between the two — the same "roof and floor" both ends of a
    building keep out, hence the name. Ehlers designed this specifically
    to precede oscillators like :func:`stoch` or :func:`rsi`, replacing
    raw price as their input so they react to genuine cycles rather than
    trend or noise.

    Parameters
    ----------
    close:
        Closing prices.
    hp_length:
        High-pass cutoff, in bars — cycles longer than this are removed.
        Ehlers' own default is ``48``.
    lp_length:
        Low-pass cutoff, in bars — cycles shorter than this are removed.
        Ehlers' own default is ``10``.

    Returns
    -------
    pandas.Series
        Named ``ROOF_{hp_length}_{lp_length}``.

    Examples
    --------
    >>> import zeonta
    >>> import numpy as np
    >>> t = np.arange(100.0)
    >>> close = 100.0 + 5.0 * np.sin(2.0 * np.pi * t / 20.0)
    >>> result = zeonta.roofing_filter(close, hp_length=48, lp_length=10)
    >>> bool(result.iloc[60:].abs().max() < 10.0)
    True

    References
    ----------
    https://www.mesasoftware.com/papers/SwissArmyKnifeIndicator.pdf
    """
    hp_length = validate_length(hp_length, "hp_length", minimum=2)
    lp_length = validate_length(lp_length, "lp_length", minimum=2)
    values = as_array(close, "close")

    high_passed = _two_pole_highpass_values(values, hp_length)
    result = super_smoother_values(high_passed, lp_length)

    return wrap_series(result, common_index(close), f"ROOF_{hp_length}_{lp_length}")


@indicator(
    category="oscillators",
    summary="A highpass-then-smoothed cycle, self-normalized to trace out an actual sine wave.",
    outputs=("EBSW",),
    reference="https://www.tradingview.com/script/thzgGKyQ-Ehlers-Even-Better-Sinewave-EBSW/",
)
def even_better_sinewave(close: ArrayLike, hp_length: int = 40, lp_length: int = 10) -> pd.Series:
    """Even Better Sinewave (John Ehlers).

    A 1-pole high-pass removes the trend, :func:`super_smoother` then
    removes short-term noise, and the result is divided by its own
    recent RMS amplitude::

        alpha1 = (1 - sin(2*pi/hp_length)) / cos(2*pi/hp_length)
        HP = 0.5*(1+alpha1)*(Price - Price[-1]) + alpha1*HP[-1]
        Filt = SuperSmoother(HP, lp_length)
        Wave = mean(Filt, Filt[-1], Filt[-2])
        Pwr = mean(Filt^2, Filt[-1]^2, Filt[-2]^2)
        EBSW = Wave / sqrt(Pwr)

    Where a plain oscillator's amplitude drifts with volatility, dividing
    by the local RMS amplitude (``Pwr``) keeps this one's swings a
    genuine sine wave regardless of how big the underlying cycle
    currently is — the whole point of the "even better" in the name,
    versus Ehlers' earlier, unnormalized Sinewave Indicator.

    Parameters
    ----------
    close:
        Closing prices.
    hp_length:
        High-pass cutoff removing the trend. Ehlers' own default is ``40``.
    lp_length:
        SuperSmoother cutoff removing short-term noise. Ehlers' own
        default is ``10``.

    Returns
    -------
    pandas.Series
        Named ``EBSW_{hp_length}_{lp_length}``, ranging roughly -1 to 1.
        Exactly ``0`` wherever the filtered signal has been flat for
        three bars running, rather than an undefined ``0/0``.

    Examples
    --------
    >>> import zeonta
    >>> import numpy as np
    >>> t = np.arange(150.0)
    >>> close = 100.0 + 5.0 * np.sin(2.0 * np.pi * t / 20.0)
    >>> result = zeonta.even_better_sinewave(close, hp_length=40, lp_length=10)
    >>> bool(result.iloc[80:].abs().max() <= 1.01)
    True

    References
    ----------
    https://www.tradingview.com/script/thzgGKyQ-Ehlers-Even-Better-Sinewave-EBSW/
    """
    hp_length = validate_length(hp_length, "hp_length", minimum=2)
    lp_length = validate_length(lp_length, "lp_length", minimum=2)
    values = as_array(close, "close")
    size = values.shape[0]

    angle = 2.0 * np.pi / hp_length
    alpha1 = (1.0 - np.sin(angle)) / np.cos(angle)
    high_passed = np.zeros(size, dtype="float64")
    for i in range(1, size):
        pair = values[i - 1 : i + 1]
        if not np.all(np.isfinite(pair)) or not np.isfinite(high_passed[i - 1]):
            high_passed[i] = high_passed[i - 1]
            continue
        high_passed[i] = (
            0.5 * (1.0 + alpha1) * (values[i] - values[i - 1]) + alpha1 * high_passed[i - 1]
        )

    filt = super_smoother_values(high_passed, lp_length)
    filt_1 = np.concatenate(([np.nan], filt[:-1]))
    filt_2 = np.concatenate(([np.nan, np.nan], filt[:-2]))

    wave = (filt + filt_1 + filt_2) / 3.0
    power = (filt**2 + filt_1**2 + filt_2**2) / 3.0
    with np.errstate(divide="ignore", invalid="ignore"):
        result = np.where(power != 0.0, wave / np.sqrt(power), 0.0)
    result = np.where(np.isfinite(power), result, np.nan)

    return wrap_series(result, common_index(close), f"EBSW_{hp_length}_{lp_length}")


@indicator(
    category="oscillators",
    summary="Ehlers' band-limited cycle extraction with a fixed smoothing constant.",
    outputs=("CYBERCYCLE", "CYBERCYCLEt"),
    reference="https://help.ctrader.com/indicators/built-in/oscillators/cyber-cycle/",
)
def cyber_cycle(high: ArrayLike, low: ArrayLike, alpha: Number = 0.07) -> pd.DataFrame:
    """Cyber Cycle (John Ehlers).

    A 4-bar weighted smooth of the median price, then a 2-pole highpass
    tuned by a fixed ``alpha`` rather than a length in bars::

        Smooth = (Price + 2*Price[-1] + 2*Price[-2] + Price[-3]) / 6
        Cycle = (1-alpha/2)^2 * (Smooth - 2*Smooth[-1] + Smooth[-2])
                + 2*(1-alpha)*Cycle[-1] - (1-alpha)^2*Cycle[-2]

    with a simpler bootstrap formula for the first 7 bars. This is the
    fixed-``alpha`` Cyber Cycle from Ehlers' "Cybernetic Analysis for
    Stocks and Futures" — his own "Adaptive" variant instead measures the
    market's own dominant cycle period (via a Hilbert Transform
    discriminator) and feeds that into ``alpha`` bar by bar. That
    measurement stage is a substantially larger, separately-nontrivial
    piece of machinery on its own — the same dominant-cycle apparatus
    behind MAMA, an indicator this library has already declined for
    exactly that reason — so only the fixed-``alpha`` form is implemented
    here.

    Parameters
    ----------
    high, low:
        Price series of equal length.
    alpha:
        Smoothing constant. Ehlers' own default is ``0.07``. Must be > 0.

    Returns
    -------
    pandas.DataFrame
        ``CYBERCYCLE`` and its own one-bar-delayed trigger line
        ``CYBERCYCLEt`` — the same pattern :func:`fisher_transform` and
        :func:`center_of_gravity` use.

    Examples
    --------
    >>> import zeonta
    >>> import numpy as np
    >>> t = np.arange(60.0)
    >>> high = 100.5 + 5.0 * np.sin(2.0 * np.pi * t / 15.0)
    >>> low = 99.5 + 5.0 * np.sin(2.0 * np.pi * t / 15.0)
    >>> result = zeonta.cyber_cycle(high, low)
    >>> bool(result['CYBERCYCLE'].iloc[-20:].abs().max() < 6.0)
    True

    References
    ----------
    https://help.ctrader.com/indicators/built-in/oscillators/cyber-cycle/
    """
    alpha = validate_multiplier(alpha, "alpha")
    require_aligned_index(high=high, low=low)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    size = require_same_length(high=high_values, low=low_values)
    price = (high_values + low_values) / 2.0

    smooth = np.full(size, np.nan, dtype="float64")
    cycle = np.zeros(size, dtype="float64")
    for i in range(size):
        if i >= 3:
            window = price[i - 3 : i + 1]
            if np.all(np.isfinite(window)):
                smooth[i] = (window[3] + 2.0 * window[2] + 2.0 * window[1] + window[0]) / 6.0
        elif np.isfinite(price[i]):
            smooth[i] = price[i]

        if i < 7:
            if i >= 2 and np.all(np.isfinite(price[i - 2 : i + 1])):
                cycle[i] = (price[i] - 2.0 * price[i - 1] + price[i - 2]) / 4.0
            continue

        window_s = smooth[i - 2 : i + 1]
        previous_c = cycle[i - 2 : i]
        if not np.all(np.isfinite(window_s)) or not np.all(np.isfinite(previous_c)):
            cycle[i] = cycle[i - 1]
            continue
        cycle[i] = (1.0 - 0.5 * alpha) ** 2 * (window_s[2] - 2.0 * window_s[1] + window_s[0]) + (
            2.0 * (1.0 - alpha) * cycle[i - 1] - (1.0 - alpha) ** 2 * cycle[i - 2]
        )

    trigger = np.concatenate(([np.nan], cycle[:-1]))
    order = ["CYBERCYCLE", "CYBERCYCLEt"]
    return wrap_frame(
        dict(zip(order, (cycle, trigger), strict=True)),
        common_index(high, low),
        order=order,
        roles={"line": order[0], "trigger": order[1]},
    )


@indicator(
    category="oscillators",
    summary="A band-limiting filter feeding Voss' negative-group-delay predictor.",
    outputs=("VOSSFILT", "VOSS"),
    reference="https://www.mesasoftware.com/papers/A%20PEEK%20INTO%20THE%20FUTURE.pdf",
)
def voss_predictive_filter(
    close: ArrayLike, period: int = 20, predict: int = 3, bandwidth: Number = 0.25
) -> pd.DataFrame:
    """Voss Predictive Filter (Henning U. Voss, adapted by John Ehlers).

    Band-limits price with a 2-pole bandpass filter, then runs it through
    a filter with *negative group delay* — Voss' "Universal Negative
    Group Delay Filter for the Prediction of Band-Limited Signals" — to
    produce a second line that leads the bandpass output rather than
    lagging it::

        order = 3 * predict
        Filt = BandPass(Close, period, bandwidth)      [2-pole, Ehlers' own]
        Voss = ((3+order)/2)*Filt - sum((k+1)/order * Voss[-(order-k)], k=0..order-1)

    This cannot see the future — the qualification is that ``Filt`` must
    already be band-limited, which is exactly what the bandpass stage
    guarantees — but within that band, ``Voss`` measurably precedes
    ``Filt``'s own turns, which is as close to a genuine lead as a causal
    filter gets.

    Parameters
    ----------
    close:
        Closing prices.
    period:
        Center period of the band-limiting bandpass filter. Ehlers' own
        default is ``20``.
    predict:
        Bars of desired prediction; sets the predictor's own filter order
        (``3 * predict``). Ehlers recommends not exceeding ``3`` — more
        prediction trades for a noisier output. Must be >= 1.
    bandwidth:
        Bandpass filter width as a fraction of ``period``. Ehlers' own
        default is ``0.25``. Must be > 0.

    Returns
    -------
    pandas.DataFrame
        ``VOSSFILT`` (the band-limited input) and ``VOSS`` (the
        predictive line) — plotted together, a ``VOSS``/``VOSSFILT``
        crossover at a peak or valley is Ehlers' own suggested signal.

    Examples
    --------
    >>> import zeonta
    >>> import numpy as np
    >>> t = np.arange(80.0)
    >>> close = 100.0 + 5.0 * np.sin(2.0 * np.pi * t / 20.0)
    >>> result = zeonta.voss_predictive_filter(close, period=20, predict=3)
    >>> bool(result['VOSSFILT'].iloc[30:].abs().max() < 10.0)
    True

    References
    ----------
    https://www.mesasoftware.com/papers/A%20PEEK%20INTO%20THE%20FUTURE.pdf
    """
    period = validate_length(period, "period", minimum=2)
    predict = validate_length(predict, "predict")
    bandwidth = validate_multiplier(bandwidth, "bandwidth")
    values = as_array(close, "close")
    size = values.shape[0]

    order = 3 * predict
    f1 = np.cos(2.0 * np.pi / period)
    g1 = np.cos(bandwidth * 2.0 * np.pi / period)
    s1 = 1.0 / g1 - np.sqrt(1.0 / (g1 * g1) - 1.0)

    filt = np.zeros(size, dtype="float64")
    warmup = 5  # Ehlers' own literal "CurrentBar <= 5" bootstrap bar count
    for i in range(size):
        if i < warmup or i < 2:
            continue
        pair = (values[i], values[i - 2])
        if (
            not np.all(np.isfinite(pair))
            or not np.isfinite(filt[i - 1])
            or not np.isfinite(filt[i - 2])
        ):
            filt[i] = filt[i - 1]
            continue
        filt[i] = (
            0.5 * (1.0 - s1) * (values[i] - values[i - 2])
            + f1 * (1.0 + s1) * filt[i - 1]
            - s1 * filt[i - 2]
        )

    voss = np.zeros(size, dtype="float64")
    weights = np.array([(count + 1.0) / order for count in range(order)])
    for i in range(size):
        if i < warmup:
            continue
        lag_indices = [i - (order - count) for count in range(order)]
        lags = np.array([voss[idx] if idx >= 0 else 0.0 for idx in lag_indices])
        sum_c = float(np.dot(weights, lags))
        voss[i] = ((3.0 + order) / 2.0) * filt[i] - sum_c

    order_cols = ["VOSSFILT", "VOSS"]
    return wrap_frame(
        dict(zip(order_cols, (filt, voss), strict=True)),
        common_index(close),
        order=order_cols,
        roles={"filter": order_cols[0], "predictor": order_cols[1]},
    )


@indicator(
    category="oscillators",
    summary="Ehlers' zero-lag pair: deviation from a fitted line (cycle) vs. current value.",
    outputs=("REFLEX", "TRENDFLEX"),
    reference="https://www.prorealcode.com/prorealtime-indicators/reflex-and-trendflex-indicators-john-f-ehlers/",
)
def reflex_trendflex(close: ArrayLike, length: int = 20) -> pd.DataFrame:
    """Reflex and Trendflex (John Ehlers).

    Both start from the same :func:`super_smoother` pass at half
    ``length``, then average that filtered line's own deviation from a
    reference over the full window — Reflex measures deviation from a
    straight line drawn across the window (stripping trend, isolating
    cycle swings), Trendflex measures deviation from the filtered line's
    *current* value (keeping trend in)::

        Filt = SuperSmoother(Close, length/2)
        Slope = (Filt[-length] - Filt) / length
        ReflexSum  = mean(Filt + k*Slope - Filt[-k], k=1..length)
        TrendflexSum = mean(Filt - Filt[-k], k=1..length)
        MS = 0.04*Sum^2 + 0.96*MS[-1]           [separately, for each line]
        Output = Sum / sqrt(MS)

    Both self-normalize against their own recent mean square, the same
    "divide by local RMS" idea :func:`even_better_sinewave` uses, so
    their scale stays comparable across different volatility regimes.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        Window length in bars. Ehlers' own default is ``20``; the
        SuperSmoother pre-filter runs at half of this.

    Returns
    -------
    pandas.DataFrame
        ``REFLEX_{length}`` and ``TRENDFLEX_{length}``.

    Examples
    --------
    >>> import zeonta
    >>> import numpy as np
    >>> t = np.arange(100.0)
    >>> close = 100.0 + 5.0 * np.sin(2.0 * np.pi * t / 20.0)
    >>> result = zeonta.reflex_trendflex(close, length=20)
    >>> bool(result['REFLEX_20'].iloc[50:].abs().max() <= 2.0)
    True

    References
    ----------
    https://www.prorealcode.com/prorealtime-indicators/reflex-and-trendflex-indicators-john-f-ehlers/
    """
    length = validate_length(length, minimum=4)
    values = as_array(close, "close")
    size = values.shape[0]

    filt = super_smoother_values(values, length / 2.0)

    reflex_sum = np.full(size, np.nan, dtype="float64")
    trendflex_sum = np.full(size, np.nan, dtype="float64")
    for i in range(length, size):
        window = filt[i - length : i + 1]
        if not np.all(np.isfinite(window)):
            continue
        current = window[-1]
        slope = (window[0] - current) / length
        counts = np.arange(1, length + 1)
        lagged = window[-1 - counts]  # Filt[i - count], count = 1..length
        reflex_sum[i] = float(np.mean((current + counts * slope) - lagged))
        trendflex_sum[i] = float(np.mean(current - lagged))

    def normalize(sums: np.ndarray) -> np.ndarray:
        ms = np.full(size, np.nan, dtype="float64")
        result = np.full(size, np.nan, dtype="float64")
        previous_ms = 0.0
        for i in range(size):
            value = sums[i]
            if not np.isfinite(value):
                continue
            previous_ms = 0.04 * value * value + 0.96 * previous_ms
            ms[i] = previous_ms
            result[i] = value / np.sqrt(ms[i]) if ms[i] != 0.0 else 0.0
        return result

    reflex = normalize(reflex_sum)
    trendflex = normalize(trendflex_sum)

    order = [f"REFLEX_{length}", f"TRENDFLEX_{length}"]
    return wrap_frame(
        dict(zip(order, (reflex, trendflex), strict=True)),
        common_index(close),
        order=order,
        roles={"reflex": order[0], "trendflex": order[1]},
    )
