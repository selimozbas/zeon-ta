"""Volatility tools: True Range, ATR, Bollinger Bands, Keltner Channels, TTM Squeeze."""

from __future__ import annotations

import warnings

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
    rolling_linreg,
    rolling_max,
    rolling_mean,
    rolling_min,
    rolling_std,
    validate_length,
    validate_multiplier,
    wilder_values,
    wrap_frame,
    wrap_series,
)

__all__ = ["atr", "bbands", "keltner", "squeeze", "true_range"]


def _true_range_values(high: np.ndarray, low: np.ndarray, close: np.ndarray) -> np.ndarray:
    """``max(H-L, |H-prevC|, |L-prevC|)``; bar 0 falls back to ``H-L``."""
    previous_close = np.concatenate(([np.nan], close[:-1]))
    high_low = high - low
    high_close = np.abs(high - previous_close)
    low_close = np.abs(low - previous_close)
    # A bar whose high and low are both missing has all three measures NaN,
    # which makes nanmax warn "All-NaN slice encountered" even though NaN is
    # exactly the right answer there (not just bar 0, which is why this is
    # suppressed rather than special-cased for one index).
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="All-NaN slice encountered")
        result = np.nanmax(np.vstack([high_low, high_close, low_close]), axis=0)
    result[0] = high_low[0]
    return result


@indicator(
    category="volatility",
    summary="Per-bar range including gaps: max(H-L, |H-prevC|, |L-prevC|).",
    lesson="atr",
    outputs=("TRUERANGE",),
)
def true_range(high: ArrayLike, low: ArrayLike, close: ArrayLike) -> pd.Series:
    """True Range — the building block of ATR.

    ``TR = max(High - Low, |High - PrevClose|, |Low - PrevClose|)``. The first bar
    has no previous close, so it falls back to ``High - Low``.

    Parameters
    ----------
    high, low, close:
        Price series of equal length.

    Returns
    -------
    pandas.Series
        Named ``TRUERANGE``. Never ``NaN`` for finite inputs.

    Notes
    -----
    This assumes ordinary OHLC data (``low <= high`` on every bar). No such
    check is performed: real feeds occasionally carry a bad tick, and rejecting
    the whole call for one bad bar would be more disruptive than useful. A
    violated bar simply produces a locally distorted (though not necessarily
    negative) reading rather than raising — clean the input first if your data
    source is not trustworthy. Every other volatility and trend indicator built
    on true range (:func:`atr`, :func:`keltner`, :func:`squeeze`,
    :func:`~zeonta.supertrend`, :func:`~zeonta.adx`) inherits this assumption.

    Examples
    --------
    >>> import zeonta
    >>> zeonta.true_range([10, 12], [8, 11], [9, 11.5]).tolist()
    [2.0, 3.0]
    """
    require_aligned_index(high=high, low=low, close=close)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    close_values = as_array(close, "close")
    require_same_length(high=high_values, low=low_values, close=close_values)
    values = _true_range_values(high_values, low_values, close_values)
    return wrap_series(values, common_index(high, low, close), "TRUERANGE")


@indicator(
    category="volatility",
    summary="Wilder-smoothed average of True Range — how much a symbol typically moves.",
    lesson="atr",
    outputs=("ATR",),
)
def atr(high: ArrayLike, low: ArrayLike, close: ArrayLike, length: int = 14) -> pd.Series:
    """Average True Range.

    ``first ATR = SMA(TR, n)``, then ``ATR = (PrevATR * (n - 1) + TR) / n`` —
    Wilder's smoothing. ATR measures volatility only; it says nothing about direction.

    Parameters
    ----------
    high, low, close:
        Price series of equal length.
    length:
        Wilder smoothing period.

    Returns
    -------
    pandas.Series
        Named ``ATR_{length}``; the first ``length - 1`` bars are ``NaN``.

    Examples
    --------
    >>> import zeonta
    >>> float(zeonta.atr([2] * 20, [1] * 20, [1.5] * 20, length=14).iloc[-1])
    1.0
    """
    length = validate_length(length)
    require_aligned_index(high=high, low=low, close=close)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    close_values = as_array(close, "close")
    require_same_length(high=high_values, low=low_values, close=close_values)

    ranges = _true_range_values(high_values, low_values, close_values)
    return wrap_series(
        wilder_values(ranges, length), common_index(high, low, close), f"ATR_{length}"
    )


@indicator(
    category="volatility",
    summary="SMA envelope scaled by standard deviation; width tracks volatility.",
    lesson="bollinger-bands",
    outputs=("BBL", "BBM", "BBU", "BBB", "BBP"),
)
def bbands(
    close: ArrayLike,
    length: int = 20,
    std: Number = 2.0,
    ddof: int = 0,
) -> pd.DataFrame:
    """Bollinger Bands.

    ``Middle = SMA(Close, n)``; ``Upper = Middle + k * StdDev(Close, n)``;
    ``Lower = Middle - k * StdDev(Close, n)``.

    Two derived series are included because they are what most strategies
    actually test against: ``BBB`` (bandwidth, ``(Upper - Lower) / Middle``) and
    ``BBP`` (percent-B, where price sits inside the bands — ``0`` at the lower
    band, ``1`` at the upper).

    Parameters
    ----------
    close:
        Closing prices.
    length:
        Look-back for both the average and the deviation.
    std:
        Standard-deviation multiplier.
    ddof:
        Delta degrees of freedom for the deviation. ``0`` (population) matches
        charting platforms; ``1`` gives the sample estimate.

    Returns
    -------
    pandas.DataFrame
        Columns ``BBL_{length}_{std}``, ``BBM_...``, ``BBU_...``, ``BBB_...``, ``BBP_...``.

    Examples
    --------
    >>> import zeonta
    >>> out = zeonta.bbands([10] * 25)
    >>> float(out.iloc[-1]["BBB_20_2.0"])
    0.0
    """
    length = validate_length(length, minimum=2)
    multiplier = validate_multiplier(std, "std")

    values = as_array(close, "close")
    middle = rolling_mean(values, length)
    deviation = rolling_std(values, length, ddof=ddof)
    upper = middle + multiplier * deviation
    lower = middle - multiplier * deviation

    span = upper - lower
    with np.errstate(divide="ignore", invalid="ignore"):
        bandwidth = np.where(middle != 0.0, span / middle, np.nan)
        percent = np.where(span != 0.0, (values - lower) / span, np.nan)
    bandwidth = np.where(np.isfinite(middle) & (span == 0.0), 0.0, bandwidth)
    percent = np.where(np.isfinite(middle) & (span == 0.0), 0.5, percent)

    suffix = f"{length}_{multiplier}"
    order = [f"BBL_{suffix}", f"BBM_{suffix}", f"BBU_{suffix}", f"BBB_{suffix}", f"BBP_{suffix}"]
    return wrap_frame(
        dict(zip(order, (lower, middle, upper, bandwidth, percent), strict=True)),
        common_index(close),
        order=order,
    )


@indicator(
    category="volatility",
    summary="EMA envelope scaled by ATR — smoother and less reactive than Bollinger.",
    lesson="keltner-channels",
    outputs=("KCL", "KCM", "KCU"),
)
def keltner(
    high: ArrayLike,
    low: ArrayLike,
    close: ArrayLike,
    length: int = 20,
    atr_length: int = 10,
    multiplier: Number = 2.0,
) -> pd.DataFrame:
    """Keltner Channels.

    ``Middle = EMA(Close, n)``; ``Upper = Middle + k * ATR(atr_length)``;
    ``Lower = Middle - k * ATR(atr_length)``.

    Because ATR reacts more slowly than standard deviation, Keltner Channels
    stay smoother than Bollinger Bands through a volatility spike — which is
    exactly the property the TTM Squeeze exploits.

    Parameters
    ----------
    high, low, close:
        Price series of equal length.
    length:
        EMA length of the centre line.
    atr_length:
        ATR period used for the band width.
    multiplier:
        ATR multiplier.

    Returns
    -------
    pandas.DataFrame
        Columns ``KCL_{length}_{multiplier}``, ``KCM_...``, ``KCU_...``.

    Examples
    --------
    >>> import zeonta
    >>> list(zeonta.keltner([2] * 30, [1] * 30, [1.5] * 30).columns)
    ['KCL_20_2.0', 'KCM_20_2.0', 'KCU_20_2.0']
    """
    length = validate_length(length)
    atr_length = validate_length(atr_length, "atr_length")
    factor = validate_multiplier(multiplier)

    require_aligned_index(high=high, low=low, close=close)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    close_values = as_array(close, "close")
    require_same_length(high=high_values, low=low_values, close=close_values)

    middle = ema_values(close_values, length)
    ranges = wilder_values(_true_range_values(high_values, low_values, close_values), atr_length)
    upper = middle + factor * ranges
    lower = middle - factor * ranges

    suffix = f"{length}_{factor}"
    order = [f"KCL_{suffix}", f"KCM_{suffix}", f"KCU_{suffix}"]
    return wrap_frame(
        dict(zip(order, (lower, middle, upper), strict=True)),
        common_index(high, low, close),
        order=order,
    )


@indicator(
    category="volatility",
    summary="Detects Bollinger Bands compressed inside Keltner Channels, plus a momentum read.",
    lesson="squeeze",
    outputs=("SQZ_ON", "SQZ_OFF", "SQZ_MOM"),
)
def squeeze(
    high: ArrayLike,
    low: ArrayLike,
    close: ArrayLike,
    bb_length: int = 20,
    bb_std: Number = 2.0,
    kc_length: int = 20,
    kc_multiplier: Number = 1.5,
) -> pd.DataFrame:
    """TTM Squeeze.

    The squeeze is **on** when the Bollinger Bands sit entirely inside the
    Keltner Channels (``BB Upper < KC Upper`` *and* ``BB Lower > KC Lower``) —
    volatility has compressed. It turns **off** on the release, which is the bar
    traders actually act on.

    Momentum is the linear-regression endpoint of price minus a midline:
    ``LinReg(Close - Avg(Avg(HighestHigh(n), LowestLow(n)), SMA(Close, n)), n)``.
    Note the *nested* average — the high-low midpoint and the SMA each carry half
    the weight. Its sign tells you which way the compressed energy is pointing.

    Parameters
    ----------
    high, low, close:
        Price series of equal length.
    bb_length, bb_std:
        Bollinger Band settings.
    kc_length, kc_multiplier:
        Keltner Channel settings. A larger multiplier widens the Keltner
        Channel, making squeezes rarer.

    Returns
    -------
    pandas.DataFrame
        Columns ``SQZ_ON``, ``SQZ_OFF`` (``1.0``/``0.0`` flags) and ``SQZ_MOM``
        (the momentum histogram), suffixed with the settings.

    Examples
    --------
    >>> import zeonta
    >>> sorted(c.split('_')[1] for c in zeonta.squeeze([2] * 40, [1] * 40, [1.5] * 40).columns)
    ['MOM', 'OFF', 'ON']
    """
    bb_length = validate_length(bb_length, "bb_length", minimum=2)
    kc_length = validate_length(kc_length, "kc_length", minimum=2)
    bb_factor = validate_multiplier(bb_std, "bb_std")
    kc_factor = validate_multiplier(kc_multiplier, "kc_multiplier")

    require_aligned_index(high=high, low=low, close=close)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    close_values = as_array(close, "close")
    require_same_length(high=high_values, low=low_values, close=close_values)

    basis = rolling_mean(close_values, bb_length)
    deviation = rolling_std(close_values, bb_length, ddof=0)
    bb_upper = basis + bb_factor * deviation
    bb_lower = basis - bb_factor * deviation

    kc_basis = ema_values(close_values, kc_length)
    ranges = wilder_values(_true_range_values(high_values, low_values, close_values), kc_length)
    kc_upper = kc_basis + kc_factor * ranges
    kc_lower = kc_basis - kc_factor * ranges

    comparable = np.isfinite(bb_upper) & np.isfinite(kc_upper)
    on = np.full(close_values.shape[0], np.nan, dtype="float64")
    off = np.full(close_values.shape[0], np.nan, dtype="float64")
    inside = comparable & (bb_upper < kc_upper) & (bb_lower > kc_lower)
    on[comparable] = 0.0
    off[comparable] = 0.0
    on[inside] = 1.0
    off[comparable & ~inside] = 1.0

    # avg(avg(highest high, lowest low), sma) — a nested average, so the range
    # midpoint and the SMA each carry half the weight. Some casual descriptions
    # write this as "Avg(HighestHigh, LowestLow, SMA)", which reads as an equal
    # three-way mean; that is not the published TTM Squeeze definition.
    range_mid = (rolling_max(high_values, kc_length) + rolling_min(low_values, kc_length)) / 2.0
    midline = (range_mid + rolling_mean(close_values, kc_length)) / 2.0
    momentum = rolling_linreg(close_values - midline, kc_length).endpoint

    suffix = f"{bb_length}_{bb_factor}_{kc_length}_{kc_factor}"
    order = [f"SQZ_ON_{suffix}", f"SQZ_OFF_{suffix}", f"SQZ_MOM_{suffix}"]
    return wrap_frame(
        dict(zip(order, (on, off, momentum), strict=True)),
        common_index(high, low, close),
        order=order,
    )
