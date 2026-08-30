"""Volatility tools: True Range, ATR, Bollinger Bands, Keltner Channels, Squeeze, Ulcer Index."""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
import pywt

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
    rolling_sum,
    validate_length,
    validate_multiplier,
    wilder_values,
    wrap_frame,
    wrap_series,
)

__all__ = [
    "accbands",
    "atr",
    "bbands",
    "chaikin_volatility",
    "keltner",
    "mass_index",
    "natr",
    "relative_volatility_index",
    "squeeze",
    "true_range",
    "ulcer_index",
    "wavelet_variance",
]


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


@indicator(
    category="volatility",
    summary="Drawdown-based risk measure — the expected percentage decline, not price swing size.",
    reference=(
        "https://chartschool.stockcharts.com/table-of-contents/"
        "technical-indicators-and-overlays/technical-indicators/ulcer-index"
    ),
    outputs=("UI",),
)
def ulcer_index(close: ArrayLike, length: int = 14) -> pd.Series:
    """Ulcer Index.

    ``PercentDrawdown = (Close - HighestClose(n)) / HighestClose(n) * 100``;
    ``UI = sqrt(mean(PercentDrawdown^2, n))``. Unlike :func:`atr` or
    :func:`bbands`, which measure movement in *either* direction, the Ulcer
    Index (Peter Martin, 1987) only measures how far price has fallen from
    its own recent high — squaring the drawdown before averaging means a
    single deep decline dominates the reading far more than several small
    ones of the same total size, mirroring how a real drawdown actually
    feels to hold through.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        Look-back window for both the running high and the average.

    Returns
    -------
    pandas.Series
        Named ``UI_{length}``. Always ``>= 0``; ``0`` only when price has
        made a new high on every bar in the window.

    Examples
    --------
    >>> import zeonta
    >>> float(zeonta.ulcer_index([100.0, 100.0, 90.0, 90.0], length=2).iloc[-1])
    7.0710678118654755

    References
    ----------
    https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ulcer-index
    """
    length = validate_length(length)
    values = as_array(close, "close")

    highest_close = rolling_max(values, length)
    with np.errstate(divide="ignore", invalid="ignore"):
        percent_drawdown = (values - highest_close) / highest_close * 100.0
    percent_drawdown = np.where(highest_close == 0.0, 0.0, percent_drawdown)

    result = np.sqrt(rolling_mean(percent_drawdown**2, length))

    return wrap_series(result, common_index(close), f"UI_{length}")


@indicator(
    category="volatility",
    summary="Multi-scale volatility (MODWT): how much movement lives at each timescale.",
    reference="https://staff.washington.edu/dbp/wmtsa.html",
    outputs=("WVAR",),
    returns_frame=True,
)
def wavelet_variance(
    close: ArrayLike, window: int = 64, wavelet: str = "db4", level: int = 5
) -> pd.DataFrame:
    """Multi-Scale Wavelet Variance (Percival & Walden, MODWT).

    :func:`atr` and rolling standard deviation answer "how much did price
    move", lumping every timescale into one number. This splits that
    movement by scale instead: each rolling *window* of price is
    decomposed with a Maximal Overlap DWT into *level* detail bands —
    ``WVAR_1`` covers 2-4 bar swings, ``WVAR_2`` covers 4-8 bars, doubling
    up to ``WVAR_{level}`` covering ``2^level`` to ``2^(level+1)`` bars —
    and each column is that band's mean squared coefficient (the *biased*
    wavelet-variance estimator; Percival & Walden also give an *unbiased*
    one that excludes boundary-affected coefficients, which this simpler,
    always-defined form does not attempt). Because an MODWT (unlike a
    plain DWT) is energy-conserving, the columns are a genuine
    decomposition: summed together (plus what the coarsest band's
    approximation leaves out) they reconstruct the window's total
    variance, rather than being independent, possibly-overlapping
    readings.

    Splitting volatility apart like this is a *regime* read: a bar where
    ``WVAR_1`` dominates is mostly high-frequency noise (thin order books,
    HFT churn), while one where ``WVAR_4``/``WVAR_5`` dominate reflects a
    genuine slower move — the kind :func:`atr` cannot distinguish, since it
    only ever reports a single blended number.

    Parameters
    ----------
    close:
        Closing prices.
    window:
        Bars per rolling decomposition. Must be an exact multiple of
        ``2**level`` (a hard MODWT requirement — see ``pywt.swt``); the
        defaults (64, level 5) satisfy this with ``2**5 = 32``.
    wavelet:
        Any discrete wavelet name PyWavelets recognises. ``"db4"`` matches
        this library's other wavelet-based indicator, :func:`wavelet_denoise`;
        published wavelet-variance software (e.g. MATLAB's ``modwtvar``)
        more often defaults to ``"sym4"`` — both are valid choices, the
        difference is which filter shape is assumed for the finest scale.
    level:
        Number of scales to compute. Must be >= 1 and satisfy the
        *window* constraint above.

    Returns
    -------
    pandas.DataFrame
        Columns ``WVAR_1`` (finest) through ``WVAR_{level}`` (coarsest).
        The first ``window - 1`` rows are ``NaN``.

    Notes
    -----
    Like :func:`wavelet_denoise`, this recomputes its decomposition from
    scratch on every rolling *window* rather than once over the whole
    series, so that a bar's value never depends on bars that come after
    it — see that function's own docstring for why a single whole-series
    pass is unsuitable for anything meant to generate a live signal.

    Examples
    --------
    >>> import numpy as np
    >>> import zeonta
    >>> rng = np.random.default_rng(0)
    >>> noisy = np.cumsum(rng.normal(size=32)) + 100.0
    >>> result = zeonta.wavelet_variance(noisy, window=16, level=2)
    >>> list(result.columns)
    ['WVAR_1', 'WVAR_2']
    >>> result.iloc[:15].isna().all().all()
    np.True_
    >>> [round(v, 6) for v in result.iloc[-1]]
    [0.076275, 0.061968]

    References
    ----------
    https://staff.washington.edu/dbp/wmtsa.html
    """
    window = validate_length(window, "window", minimum=2)
    if level < 1:
        raise ValueError(f"'level' must be >= 1, got {level}")
    span = 2**level
    if window % span != 0:
        raise ValueError(
            f"'window' ({window}) must be an exact multiple of 2**level ({span}) "
            "for a MODWT decomposition"
        )

    values = as_array(close, "close")
    size = values.shape[0]
    columns = {f"WVAR_{lvl}": np.full(size, np.nan, dtype="float64") for lvl in range(1, level + 1)}

    for i in range(window - 1, size):
        segment = values[i - window + 1 : i + 1]
        if not np.all(np.isfinite(segment)):
            continue
        # pywt's Cython core needs a writable buffer; a slice of the
        # caller's array may not be (e.g. a read-only view from
        # DataFrame.to_numpy()).
        coeffs = pywt.swt(
            np.array(segment, dtype="float64"), wavelet, level=level, trim_approx=True, norm=True
        )
        # trim_approx=True orders coeffs as [cA_level, cD_level, ..., cD_1];
        # reversing the detail bands puts them in level order, 1..level.
        for lvl, detail in enumerate(reversed(coeffs[1:]), start=1):
            columns[f"WVAR_{lvl}"][i] = float(np.mean(detail**2))

    return wrap_frame(columns, common_index(close), order=list(columns))


@indicator(
    category="volatility",
    summary="ATR expressed as a percentage of price, so different symbols become comparable.",
    reference="https://www.tradingview.com/support/solutions/43000501823-average-true-range-natr/",
    outputs=("NATR",),
)
def natr(high: ArrayLike, low: ArrayLike, close: ArrayLike, length: int = 14) -> pd.Series:
    """Normalized Average True Range.

    ``NATR = ATR(n) / Close * 100``. :func:`atr` reports a raw price
    amount, which means a $2 ATR is huge for a $10 stock and tiny for a
    $2,000 one — NATR expresses the same measurement as a percentage of
    price instead, so different symbols (or the same symbol at very
    different price levels over time) become directly comparable.

    Parameters
    ----------
    high, low, close:
        Price series of equal length.
    length:
        Wilder smoothing period, passed straight through to :func:`atr`.

    Returns
    -------
    pandas.Series
        Named ``NATR_{length}``; the first ``length - 1`` bars are ``NaN``.

    Examples
    --------
    >>> import zeonta
    >>> float(zeonta.natr([2] * 20, [1] * 20, [1.5] * 20, length=14).iloc[-1])
    66.66666666666666

    References
    ----------
    https://www.tradingview.com/support/solutions/43000501823-average-true-range-natr/
    """
    length = validate_length(length)
    close_values = as_array(close, "close")
    atr_values = atr(high, low, close, length=length).to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        result = np.where(close_values != 0.0, atr_values / close_values * 100.0, np.nan)

    return wrap_series(result, common_index(high, low, close), f"NATR_{length}")


@indicator(
    category="volatility",
    summary="Range-expansion measure built to flag reversals, from EMA-of-EMA ratio of the range.",
    reference=(
        "https://chartschool.stockcharts.com/table-of-contents/"
        "technical-indicators-and-overlays/technical-indicators/mass-index"
    ),
    outputs=("MASS",),
)
def mass_index(
    high: ArrayLike, low: ArrayLike, ema_length: int = 9, sum_length: int = 25
) -> pd.Series:
    """Mass Index (Donald Dorsey).

    ``SingleEMA = EMA(High - Low, ema_length)``;
    ``DoubleEMA = EMA(SingleEMA, ema_length)``;
    ``Ratio = SingleEMA / DoubleEMA``;
    ``MASS = Sum(Ratio, sum_length)``.

    Built entirely from the bar-to-bar *range*, not price direction — the
    EMA-of-an-EMA ratio picks up on the range widening (a single EMA
    reacts faster than a double one, so the ratio grows) regardless of
    whether that widening comes from an up move or a down move. Dorsey's
    own claim was that this range expansion tends to appear before a
    trend reversal, without saying which direction the reversal goes.

    Parameters
    ----------
    high, low:
        Price series of equal length.
    ema_length:
        Period for both EMA passes. Must be >= 1.
    sum_length:
        Window for the final sum. Must be >= 1.

    Returns
    -------
    pandas.Series
        Named ``MASS_{ema_length}_{sum_length}``.

    Notes
    -----
    Dorsey's own commonly cited "reversal bulge" threshold is 27,
    dropping back below 26.5 — a level read, not a zero-line or bounded
    oscillator the way most indicators in this library are.

    Examples
    --------
    >>> import zeonta
    >>> float(zeonta.mass_index([2.0] * 50, [1.0] * 50, ema_length=9, sum_length=25).iloc[-1])
    25.0

    References
    ----------
    https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/mass-index
    """
    ema_length = validate_length(ema_length, "ema_length")
    sum_length = validate_length(sum_length, "sum_length")
    require_aligned_index(high=high, low=low)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    require_same_length(high=high_values, low=low_values)

    single_ema = ema_values(high_values - low_values, ema_length)
    double_ema = ema_values(single_ema, ema_length)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(double_ema != 0.0, single_ema / double_ema, 0.0)
    result = rolling_sum(ratio, sum_length)

    return wrap_series(result, common_index(high, low), f"MASS_{ema_length}_{sum_length}")


@indicator(
    category="volatility",
    summary="Rate of change of a smoothed high-low range: is the range widening or narrowing.",
    reference="https://www.luxalgo.com/library/concept/chaikin-volatility/",
    outputs=("CVI",),
)
def chaikin_volatility(high: ArrayLike, low: ArrayLike, length: int = 10) -> pd.Series:
    """Chaikin Volatility (Marc Chaikin).

    ``CVI = ROC(EMA(High - Low, n), n)`` — an EMA of the bar-to-bar range,
    then the percentage change of *that* EMA over the same window. Unlike
    :func:`atr` (a level: how large is the typical range right now),
    this is a rate of change: is the range wider than it was ``n`` bars
    ago, or narrower.

    Parameters
    ----------
    high, low:
        Price series of equal length.
    length:
        Period for both the EMA and the rate-of-change look-back.

    Returns
    -------
    pandas.Series
        Named ``CVI_{length}``. Positive means the range has widened
        over the window, negative means it has narrowed.

    Examples
    --------
    >>> import zeonta
    >>> high = [12.0, 13.5, 11.0, 15.0, 17.0, 14.5, 18.0]
    >>> low = [10.0, 11.0, 9.5, 11.0, 12.0, 11.0, 12.5]
    >>> zeonta.chaikin_volatility(high, low, length=3).dropna().tolist()
    [87.5, 54.166666666666664]

    References
    ----------
    https://www.luxalgo.com/library/concept/chaikin-volatility/
    """
    length = validate_length(length)
    require_aligned_index(high=high, low=low)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    size = require_same_length(high=high_values, low=low_values)

    smoothed_range = ema_values(high_values - low_values, length)
    result = np.full(size, np.nan, dtype="float64")
    if size > length:
        with np.errstate(divide="ignore", invalid="ignore"):
            result[length:] = (
                (smoothed_range[length:] - smoothed_range[:-length])
                / smoothed_range[:-length]
                * 100.0
            )

    return wrap_series(result, common_index(high, low), f"CVI_{length}")


@indicator(
    category="volatility",
    summary="RSI's up/down split applied to standard deviation instead of price change.",
    reference="https://user42.tuxfamily.org/chart/manual/Relative-Volatility-Index.html",
    outputs=("RVI",),
)
def relative_volatility_index(
    close: ArrayLike, stdev_length: int = 10, smooth_length: int = 14
) -> pd.Series:
    """Relative Volatility Index (Donald Dorsey).

    The same up/down-split-then-smooth structure :func:`rsi` uses,
    substituting a rolling standard deviation for the plain price change
    Wilder used::

        SD = STDDEV(Close, stdev_length)
        U = SD where Close > Close[-1], else 0
        D = SD where Close < Close[-1], else 0
        RVI = 100 * EMA(U, smooth_length) / (EMA(U, smooth_length) + EMA(D, smooth_length))

    Where :func:`rsi` asks "how much of recent price movement was
    gains versus losses", RVI asks "how much of recent *volatility*
    showed up on up bars versus down bars" — a volatility measure with
    direction, unlike :func:`atr`.

    Parameters
    ----------
    close:
        Closing prices.
    stdev_length:
        Window for the rolling standard deviation.
    smooth_length:
        EMA period applied to the up/down volatility split.

    Returns
    -------
    pandas.Series
        Named ``RVI_{stdev_length}_{smooth_length}``, ranging 0 to 100.

    Examples
    --------
    >>> import zeonta
    >>> close = [10.0, 11.0, 10.5, 12.0, 13.0, 12.5, 14.0, 13.5, 15.0, 14.5]
    >>> result = zeonta.relative_volatility_index(close, stdev_length=3, smooth_length=4)
    >>> round(float(result.iloc[-1]), 6)
    41.27568

    References
    ----------
    https://user42.tuxfamily.org/chart/manual/Relative-Volatility-Index.html
    """
    stdev_length = validate_length(stdev_length, "stdev_length")
    smooth_length = validate_length(smooth_length, "smooth_length")
    values = as_array(close, "close")

    deviation = rolling_std(values, stdev_length)
    change = np.diff(values, prepend=np.nan)
    up = np.where(change > 0.0, deviation, 0.0)
    down = np.where(change < 0.0, deviation, 0.0)
    up = np.where(np.isfinite(change) & np.isfinite(deviation), up, np.nan)
    down = np.where(np.isfinite(change) & np.isfinite(deviation), down, np.nan)

    smoothed_up = ema_values(up, smooth_length)
    smoothed_down = ema_values(down, smooth_length)
    total = smoothed_up + smoothed_down
    with np.errstate(divide="ignore", invalid="ignore"):
        result = np.where(total > 0.0, 100.0 * smoothed_up / total, 0.0)
    result = np.where(np.isfinite(total), result, np.nan)

    return wrap_series(result, common_index(close), f"RVI_{stdev_length}_{smooth_length}")


@indicator(
    category="volatility",
    summary="SMA envelope of High/Low scaled by their own range, widening with volatility.",
    outputs=("ACCBL", "ACCBM", "ACCBU"),
    reference="https://help.tc2000.com/m/69445/l/755840-acceleration-bands",
)
def accbands(
    high: ArrayLike,
    low: ArrayLike,
    close: ArrayLike,
    length: int = 20,
    c: Number = 4.0,
) -> pd.DataFrame:
    """Acceleration Bands (Price Headley).

    Widens High and Low outward by a fraction of the bar's own high-low
    range before averaging::

        Ratio = c * (High - Low) / (High + Low)
        Upper = SMA(High * (1 + Ratio), length)
        Lower = SMA(Low * (1 - Ratio), length)
        Middle = SMA(Close, length)

    Unlike :func:`bbands` (which scales a fixed multiplier by *rolling*
    standard deviation), the widening here comes from each individual
    bar's *own* high-low range — a big single bar pushes the bands apart
    immediately, with no lag from a rolling deviation window.

    Parameters
    ----------
    high, low, close:
        Price series of equal length.
    length:
        SMA period applied to all three bands.
    c:
        Range-scaling constant. Headley's own default is ``4``.

    Returns
    -------
    pandas.DataFrame
        Columns ``ACCBL_{length}`` (lower), ``ACCBM_{length}`` (middle),
        ``ACCBU_{length}`` (upper).

    Examples
    --------
    >>> import zeonta
    >>> high = [12.0, 13.0, 11.0, 14.0, 15.0]
    >>> low = [10.0, 11.0, 9.0, 12.0, 13.0]
    >>> close = [11.0, 12.5, 10.0, 13.5, 14.5]
    >>> out = zeonta.accbands(high, low, close, length=3)
    >>> round(float(out['ACCBU_3'].iloc[-1]), 6)
    17.664469

    References
    ----------
    https://help.tc2000.com/m/69445/l/755840-acceleration-bands
    """
    length = validate_length(length)
    factor = validate_multiplier(c, "c")

    require_aligned_index(high=high, low=low, close=close)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    close_values = as_array(close, "close")
    require_same_length(high=high_values, low=low_values, close=close_values)

    denom = high_values + low_values
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(denom != 0.0, factor * (high_values - low_values) / denom, np.nan)

    upper = rolling_mean(high_values * (1.0 + ratio), length)
    lower = rolling_mean(low_values * (1.0 - ratio), length)
    middle = rolling_mean(close_values, length)

    order = [f"ACCBL_{length}", f"ACCBM_{length}", f"ACCBU_{length}"]
    return wrap_frame(
        dict(zip(order, (lower, middle, upper), strict=True)),
        common_index(high, low, close),
        order=order,
    )
