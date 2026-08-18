"""Moving averages: SMA, EMA, SMMA, WMA, DEMA, TEMA, HMA, crossovers, the EMA ribbon, and KAMA.

KAMA, HMA, DEMA and TEMA additionally cite the external source their formula
was verified against; see each one's own ``References`` section.
"""

from __future__ import annotations

import itertools
from collections.abc import Sequence

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
    rolling_mean,
    rolling_sum,
    rolling_wma,
    validate_length,
    validate_multiplier,
    wilder_values,
    wrap_frame,
    wrap_series,
)

__all__ = [
    "dema",
    "ema",
    "ema_ribbon",
    "hma",
    "instantaneous_trendline",
    "kama",
    "ma_cross",
    "sma",
    "smma",
    "super_smoother",
    "t3",
    "tema",
    "wavelet_denoise",
    "wma",
]


@indicator(
    category="moving_averages",
    summary="Equally weighted average of the last n closes.",
    lesson="sma",
    outputs=("SMA",),
)
def sma(close: ArrayLike, length: int = 20) -> pd.Series:
    """Simple Moving Average.

    ``SMA(n) = (1/n) * sum(Close[i])`` over the last ``n`` bars — an equally
    weighted average of the ``n`` most recent closes.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        Look-back window in bars. Must be >= 1.

    Returns
    -------
    pandas.Series
        Named ``SMA_{length}``. The first ``length - 1`` bars are ``NaN``.

    Examples
    --------
    >>> import zeonta
    >>> zeonta.sma([1, 2, 3, 4, 5], length=3).tolist()
    [nan, nan, 2.0, 3.0, 4.0]
    """
    length = validate_length(length)
    values = as_array(close, "close")
    return wrap_series(rolling_mean(values, length), common_index(close), f"SMA_{length}")


@indicator(
    category="moving_averages",
    summary="Moving average giving linearly increasing weight to more recent closes.",
    reference="https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/wma",
    outputs=("WMA",),
)
def wma(close: ArrayLike, length: int = 20) -> pd.Series:
    """Weighted Moving Average.

    ``WMA(n) = sum(i * Close[t-n+i], i=1..n) / sum(i, i=1..n)`` — the most
    recent close in the window gets weight ``n``, the oldest gets weight
    ``1``, decreasing by one in between. Compared to :func:`sma`, where every
    bar in the window counts equally, WMA leans toward whatever just happened
    — closer to :func:`ema` in spirit, but with weights that taper off in a
    straight line instead of an exponential curve, and that reach exactly
    zero at the edge of the window rather than fading forever.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        Look-back window in bars. Must be >= 1.

    Returns
    -------
    pandas.Series
        Named ``WMA_{length}``. The first ``length - 1`` bars are ``NaN``.

    Examples
    --------
    >>> import zeonta
    >>> zeonta.wma([1, 2, 3, 4, 5], length=3).tolist()
    [nan, nan, 2.3333333333333335, 3.3333333333333335, 4.333333333333333]

    References
    ----------
    https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/wma
    """
    length = validate_length(length)
    values = as_array(close, "close")
    return wrap_series(rolling_wma(values, length), common_index(close), f"WMA_{length}")


@indicator(
    category="moving_averages",
    summary="Wilder's exponential smoothing, exposed as its own moving average.",
    reference="https://www.tradingview.com/support/solutions/43000591343-smoothed-moving-average/",
    outputs=("SMMA",),
)
def smma(close: ArrayLike, length: int = 9) -> pd.Series:
    """Smoothed Moving Average (SMMA), also called Wilder's Moving Average or RMA.

    ``SMMA[t] = SMMA[t-1] + (Close[t] - SMMA[t-1]) / n``, seeded by the plain
    SMA of the first ``n`` bars — the exact recursion J. Welles Wilder used
    throughout *New Concepts in Technical Trading Systems* (1978) for
    :func:`~zeonta.rsi`, :func:`~zeonta.atr` and :func:`~zeonta.adx`, exposed
    here as a standalone line rather than buried inside those. Algebraically
    identical to :func:`ema` with ``alpha = 1/n`` instead of ``2/(n+1)``, so
    it reacts more slowly than an EMA of the same length and never fully
    forgets old prices — every bar since warm-up still carries a sliver of
    weight, unlike :func:`wma`'s hard cutoff at the edge of its window.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        Smoothing period. Must be >= 1.

    Returns
    -------
    pandas.Series
        Named ``SMMA_{length}``. The first ``length - 1`` bars are ``NaN``.

    Notes
    -----
    Neither StockCharts nor Wikipedia document SMMA as its own named
    indicator (it appears only embedded inside RSI/ATR/ADX); the default
    length here follows TradingView's own dedicated Smoothed Moving Average
    page, which states 9. The recursion itself was independently confirmed
    against MetaTrader's MQL5 documentation, which states the identical seed
    and step.

    Examples
    --------
    >>> import zeonta
    >>> zeonta.smma([1, 2, 3, 4, 5], length=3).tolist()
    [nan, nan, 2.0, 2.666666666666667, 3.4444444444444446]

    References
    ----------
    https://www.tradingview.com/support/solutions/43000591343-smoothed-moving-average/
    """
    length = validate_length(length)
    values = as_array(close, "close")
    return wrap_series(wilder_values(values, length), common_index(close), f"SMMA_{length}")


@indicator(
    category="moving_averages",
    summary="Exponentially weighted average that reacts faster to recent closes.",
    lesson="ema",
    outputs=("EMA",),
)
def ema(close: ArrayLike, length: int = 20) -> pd.Series:
    """Exponential Moving Average.

    ``EMA(n) today = Close * k + EMA(n) yesterday * (1 - k)`` with ``k = 2 / (n + 1)``.
    The recursion is seeded with the SMA of the first ``n`` closes, so the first
    non-``NaN`` value lands on bar ``n - 1``.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        Look-back window in bars. Must be >= 1 (``length=1`` returns the input).

    Returns
    -------
    pandas.Series
        Named ``EMA_{length}``.

    Examples
    --------
    >>> import zeonta
    >>> float(zeonta.ema([1, 2, 3, 4, 5], length=3).iloc[-1])
    4.0
    """
    length = validate_length(length)
    values = as_array(close, "close")
    return wrap_series(ema_values(values, length), common_index(close), f"EMA_{length}")


@indicator(
    category="moving_averages",
    summary="EMA with roughly half the lag, by offsetting a single EMA with its own EMA.",
    reference=(
        "https://chartschool.stockcharts.com/table-of-contents/"
        "technical-indicators-and-overlays/technical-overlays/double-exponential-moving-average-dema"
    ),
    outputs=("DEMA",),
)
def dema(close: ArrayLike, length: int = 20) -> pd.Series:
    """Double Exponential Moving Average.

    ``DEMA = 2 * EMA1 - EMA2``, where ``EMA1 = EMA(Close, n)`` and
    ``EMA2 = EMA(EMA1, n)``. A single EMA lags price because it is, in effect,
    always catching up; DEMA estimates how far behind EMA1 has fallen by
    smoothing it a second time, then adds that gap back once to cancel most
    of the lag out.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        EMA period, applied twice.

    Returns
    -------
    pandas.Series
        Named ``DEMA_{length}``. The first ``2 * (length - 1)`` bars are
        ``NaN`` — EMA2 needs a full window of already-warmed-up EMA1 values.

    Examples
    --------
    >>> import zeonta
    >>> float(zeonta.dema([1, 2, 3, 4, 5, 6, 7], length=3).iloc[-1])
    7.0

    References
    ----------
    https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/double-exponential-moving-average-dema
    """
    length = validate_length(length)
    values = as_array(close, "close")
    ema1 = ema_values(values, length)
    ema2 = ema_values(ema1, length)
    return wrap_series(2.0 * ema1 - ema2, common_index(close), f"DEMA_{length}")


@indicator(
    category="moving_averages",
    summary="EMA with even less lag than DEMA, by combining three nested EMAs.",
    reference=(
        "https://chartschool.stockcharts.com/table-of-contents/"
        "technical-indicators-and-overlays/technical-overlays/triple-exponential-moving-average-tema"
    ),
    outputs=("TEMA",),
)
def tema(close: ArrayLike, length: int = 20) -> pd.Series:
    """Triple Exponential Moving Average.

    ``TEMA = 3*EMA1 - 3*EMA2 + EMA3``, where ``EMA1 = EMA(Close, n)``,
    ``EMA2 = EMA(EMA1, n)`` and ``EMA3 = EMA(EMA2, n)`` — the same
    lag-cancelling idea as :func:`dema`, carried one smoothing pass further.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        EMA period, applied three times.

    Returns
    -------
    pandas.Series
        Named ``TEMA_{length}``. The first ``3 * (length - 1)`` bars are
        ``NaN`` — EMA3 needs a full window of already-warmed-up EMA2 values.

    Examples
    --------
    >>> import zeonta
    >>> float(zeonta.tema([1, 2, 3, 4, 5, 6, 7, 8, 9], length=3).iloc[-1])
    9.0

    References
    ----------
    https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/triple-exponential-moving-average-tema
    """
    length = validate_length(length)
    values = as_array(close, "close")
    ema1 = ema_values(values, length)
    ema2 = ema_values(ema1, length)
    ema3 = ema_values(ema2, length)
    return wrap_series(3.0 * ema1 - 3.0 * ema2 + ema3, common_index(close), f"TEMA_{length}")


@indicator(
    category="moving_averages",
    summary="Fast/slow moving-average crossover signals (golden and death cross).",
    lesson="ma-crossovers",
    outputs=("MAfast", "MAslow", "cross"),
)
def ma_cross(
    close: ArrayLike,
    fast: int = 50,
    slow: int = 200,
    mode: str = "sma",
) -> pd.DataFrame:
    """Moving-average crossover signals.

    Bullish crossover (a *golden cross* at the 50/200 default):
    ``fast[i-1] <= slow[i-1] and fast[i] > slow[i]``.
    Bearish crossunder (*death cross*): ``fast[i-1] >= slow[i-1] and fast[i] < slow[i]``.

    Parameters
    ----------
    close:
        Closing prices.
    fast:
        Length of the fast average. Must be smaller than ``slow``.
    slow:
        Length of the slow average.
    mode:
        ``"sma"`` or ``"ema"`` — which average to cross.

    Returns
    -------
    pandas.DataFrame
        Columns ``MAfast_{fast}``, ``MAslow_{slow}`` and ``cross_{fast}_{slow}``,
        where ``cross`` is ``1.0`` on a bullish crossover, ``-1.0`` on a bearish
        crossunder and ``0.0`` otherwise (``NaN`` while either average is warming up).

    Examples
    --------
    >>> import zeonta
    >>> out = zeonta.ma_cross(list(range(1, 30)), fast=3, slow=5)
    >>> sorted(out.columns)
    ['MAfast_3', 'MAslow_5', 'cross_3_5']
    """
    fast = validate_length(fast, "fast")
    slow = validate_length(slow, "slow")
    if fast >= slow:
        raise ValueError(f"'fast' must be smaller than 'slow', got fast={fast}, slow={slow}")
    if mode not in ("sma", "ema"):
        raise ValueError(f"'mode' must be 'sma' or 'ema', got {mode!r}")

    values = as_array(close, "close")
    smoother = rolling_mean if mode == "sma" else ema_values
    fast_line = smoother(values, fast)
    slow_line = smoother(values, slow)

    difference = fast_line - slow_line
    previous = np.concatenate(([np.nan], difference[:-1]))

    cross = np.full(values.shape[0], np.nan, dtype="float64")
    comparable = np.isfinite(difference) & np.isfinite(previous)
    cross[comparable] = 0.0
    cross[comparable & (previous <= 0) & (difference > 0)] = 1.0
    cross[comparable & (previous >= 0) & (difference < 0)] = -1.0

    return wrap_frame(
        {
            f"MAfast_{fast}": fast_line,
            f"MAslow_{slow}": slow_line,
            f"cross_{fast}_{slow}": cross,
        },
        common_index(close),
        order=[f"MAfast_{fast}", f"MAslow_{slow}", f"cross_{fast}_{slow}"],
    )


@indicator(
    category="moving_averages",
    summary="A fan of EMAs of increasing length; spacing shows trend strength.",
    lesson="ema-ribbon",
    outputs=("EMA",),
    returns_frame=True,
)
def ema_ribbon(
    close: ArrayLike,
    lengths: Sequence[int] = (20, 30, 40, 50, 60, 70),
) -> pd.DataFrame:
    """EMA Ribbon — several EMAs of increasing length plotted together.

    The default is the evenly spaced ``20, 30, 40, 50, 60, 70`` set; the
    Fibonacci-flavoured ``8, 13, 21, 34, 55, 89`` is an equally common choice.
    Each line is a plain :func:`ema`.

    Parameters
    ----------
    close:
        Closing prices.
    lengths:
        Strictly increasing EMA lengths.

    Returns
    -------
    pandas.DataFrame
        One ``EMA_{length}`` column per requested length, in the given order.

    Examples
    --------
    >>> import zeonta
    >>> list(zeonta.ema_ribbon(list(range(50)), lengths=(5, 10)).columns)
    ['EMA_5', 'EMA_10']
    """
    if len(lengths) < 2:
        raise ValueError(f"'lengths' must contain at least two lengths, got {list(lengths)}")
    checked = [validate_length(length, "lengths") for length in lengths]
    if any(later <= earlier for earlier, later in itertools.pairwise(checked)):
        raise ValueError(f"'lengths' must be strictly increasing, got {checked}")

    values = as_array(close, "close")
    columns = {f"EMA_{length}": ema_values(values, length) for length in checked}
    return wrap_frame(columns, common_index(close), order=list(columns))


@indicator(
    category="moving_averages",
    summary="Adapts its own smoothing to how efficiently price is trending.",
    reference=(
        "https://chartschool.stockcharts.com/table-of-contents/"
        "technical-indicators-and-overlays/technical-overlays/kaufmans-adaptive-moving-average-kama"
    ),
    outputs=("KAMA",),
)
def kama(close: ArrayLike, length: int = 10, fast: int = 2, slow: int = 30) -> pd.Series:
    """Kaufman's Adaptive Moving Average.

    The Efficiency Ratio compares net movement to total movement over the
    window: ``ER = |Close - Close[n ago]| / Sum(|Close[i] - Close[i-1]|, n)``,
    ``1`` for a bar that trended in a straight line, near ``0`` for one that
    churned in place. That ratio blends two EMA smoothing constants into one
    that adapts bar by bar:
    ``SC = (ER * (2/(fast+1) - 2/(slow+1)) + 2/(slow+1))^2``;
    ``KAMA[i] = KAMA[i-1] + SC * (Close[i] - KAMA[i-1])``.

    Unlike :func:`sma` or :func:`ema`, KAMA has no single fixed speed: it
    tracks price closely while the trend is clean and flattens out on its own
    when price is choppy, without you having to pick a different length for
    each regime.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        Efficiency Ratio look-back.
    fast, slow:
        Periods for the fastest and slowest EMA smoothing constants blended
        by the Efficiency Ratio. ``fast`` must be smaller than ``slow``.

    Returns
    -------
    pandas.Series
        Named ``KAMA_{length}_{fast}_{slow}``. Seeded with ``Close`` at the
        first bar where the Efficiency Ratio becomes computable (bar
        ``length``), so the first ``length`` bars are ``NaN``.

    Notes
    -----
    With ``length=1`` the Efficiency Ratio is always exactly ``1`` (a
    single-bar move is, trivially, "perfectly efficient"), which collapses
    the smoothing constant to the fixed value ``(2 / (fast + 1)) ** 2`` and
    turns KAMA into an ordinary constant-alpha recursion — a useful sanity
    check on the formula.

    A ``NaN`` inside ``close`` widens the warm-up locally (any window
    touching it has an undefined Efficiency Ratio) but does not stop the
    series recovering afterward: KAMA holds its last computed value across
    the gap and resumes updating as soon as the window clears it, the same
    convention :func:`ema` and Wilder-smoothed indicators use.

    Examples
    --------
    >>> import zeonta
    >>> round(float(zeonta.kama(list(range(1, 30)), length=5).iloc[-1]), 4)
    27.75

    References
    ----------
    https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/kaufmans-adaptive-moving-average-kama
    """
    length = validate_length(length)
    fast = validate_length(fast, "fast")
    slow = validate_length(slow, "slow")
    if fast >= slow:
        raise ValueError(f"'fast' must be smaller than 'slow', got fast={fast}, slow={slow}")

    values = as_array(close, "close")
    size = values.shape[0]

    abs_change = np.abs(np.diff(values, prepend=np.nan))
    volatility = np.full(size, np.nan, dtype="float64")
    volatility[1:] = rolling_sum(abs_change[1:], length)

    net_change = np.full(size, np.nan, dtype="float64")
    if size > length:
        net_change[length:] = np.abs(values[length:] - values[:-length])

    with np.errstate(divide="ignore", invalid="ignore"):
        efficiency = net_change / volatility
    # A perfectly flat window has no movement at all, efficient or not.
    efficiency = np.where(volatility == 0.0, 0.0, efficiency)

    fast_sc = 2.0 / (fast + 1.0)
    slow_sc = 2.0 / (slow + 1.0)
    smoothing = (efficiency * (fast_sc - slow_sc) + slow_sc) ** 2

    result = np.full(size, np.nan, dtype="float64")
    previous = np.nan
    for i in range(length, size):
        value = values[i]
        smoothing_constant = smoothing[i]
        valid = np.isfinite(value) and np.isfinite(smoothing_constant)
        if not np.isfinite(previous):
            # Not seeded yet: only a fully valid bar can start the recursion.
            if valid:
                previous = value
                result[i] = previous
            continue
        if valid:
            previous = previous + smoothing_constant * (value - previous)
        # else: hold `previous` across the gap rather than letting a single
        # NaN propagate forever, matching ema_values/wilder_values elsewhere.
        result[i] = previous

    return wrap_series(result, common_index(close), f"KAMA_{length}_{fast}_{slow}")


@indicator(
    category="moving_averages",
    summary="Fast-turning WMA-of-WMAs designed to cut lag without adding noise.",
    reference=(
        "https://chartschool.stockcharts.com/table-of-contents/"
        "technical-indicators-and-overlays/technical-overlays/hull-moving-average-hma"
    ),
    outputs=("HMA",),
)
def hma(close: ArrayLike, length: int = 20) -> pd.Series:
    """Hull Moving Average.

    ``Raw = 2 * WMA(Close, Integer(n/2)) - WMA(Close, n)``, then
    ``HMA = WMA(Raw, Integer(sqrt(n)))``. The half-length WMA reacts fast; the
    full-length WMA gives the "usual" reading; doubling the fast one and
    subtracting the slow one extrapolates *ahead* of the fast WMA. Smoothing
    that extrapolation with one more (short) WMA turns a jumpy overshoot into
    a genuinely quick, still-smooth line — Hull's answer to the fact that
    :func:`wma` alone reduces lag only modestly.

    Both intermediate lengths are *truncated* toward zero (``Integer()`` in
    Alan Hull's own formula), not rounded to the nearest whole number — for
    an odd ``length`` this differs from what some secondary write-ups
    describe. Confirmed against alanhull.com's own formula, a second
    independent write-up, and empirically against TradingView's own
    Hull Moving Average reading for a live symbol; see
    ``tests/test_tradingview_parity.py``.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        Overall look-back. Must be >= 1 (``length=1`` returns the input).

    Returns
    -------
    pandas.Series
        Named ``HMA_{length}``.

    Examples
    --------
    >>> import zeonta
    >>> round(float(zeonta.hma(list(range(1, 31)), length=9).iloc[-1]), 4)
    30.0

    References
    ----------
    https://alanhull.com/the-hull-moving-average/
    """
    length = validate_length(length)
    values = as_array(close, "close")

    # length=1 is a degenerate edge case Hull's own formula never
    # contemplates (his examples all use large n); floor(1/2)=0 would break
    # the WMA below, so it is clamped to 1, preserving "HMA(1) == input".
    half_length = max(1, int(length / 2.0))
    sqrt_length = int(length**0.5)

    raw = 2.0 * rolling_wma(values, half_length) - rolling_wma(values, length)
    return wrap_series(rolling_wma(raw, sqrt_length), common_index(close), f"HMA_{length}")


@indicator(
    category="moving_averages",
    summary="Tillson's T3: cascaded generalized DEMA, smoother than DEMA/TEMA with less overshoot.",
    reference="https://c.mql5.com/forextsd/forum/173/tillson_t3_better_mas_and_oscillators.pdf",
    outputs=("T3",),
)
def t3(close: ArrayLike, length: int = 5, volume_factor: Number = 0.7) -> pd.Series:
    """T3 Moving Average (Tillson).

    ``GD(x, v) = (1 + v) * EMA(x, n) - v * EMA(EMA(x, n), n)`` — a
    "Generalized DEMA" that blends a plain EMA and a full DEMA by the
    ``volume_factor`` ``v`` (``v`` near ``0`` behaves like a plain EMA,
    ``v=1`` gives :func:`dema` exactly). ``T3 = GD(GD(GD(Close)))`` — three
    of these passes cascaded, six EMAs in total. Tim Tillson designed it
    specifically to cut :func:`dema`/:func:`tema`'s tendency to overshoot on
    a sharp reversal while staying nearly as responsive.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        Period for each of the six underlying EMA passes.
    volume_factor:
        Blends toward a plain EMA (near ``0``) or a full DEMA (``1``) at
        every stage. Tillson's own recommendation, used almost universally,
        is ``0.7``.

    Returns
    -------
    pandas.Series
        Named ``T3_{length}_{volume_factor}``.

    Notes
    -----
    Neither StockCharts nor Wikipedia document T3 — Tillson published it in
    *Technical Analysis of Stocks & Commodities*, January 1998, not through
    either of those channels. The default length here (5) follows an
    independently maintained reference implementation (Stock Indicators for
    .NET/Python); no source surveyed states one length as canonical the way
    Tillson's own 0.7 volume factor is agreed on everywhere.

    Examples
    --------
    >>> import zeonta
    >>> float(zeonta.t3(list(range(1, 40)), length=3, volume_factor=0.7).iloc[-1])
    38.1

    References
    ----------
    https://c.mql5.com/forextsd/forum/173/tillson_t3_better_mas_and_oscillators.pdf
    """
    length = validate_length(length)
    volume_factor = validate_multiplier(volume_factor, "volume_factor")
    values = as_array(close, "close")

    def gd(series: np.ndarray) -> np.ndarray:
        e1 = ema_values(series, length)
        e2 = ema_values(e1, length)
        return (1.0 + volume_factor) * e1 - volume_factor * e2

    result = gd(gd(gd(values)))

    return wrap_series(result, common_index(close), f"T3_{length}_{volume_factor}")


@indicator(
    category="moving_averages",
    summary="Ehlers' 2-pole low-pass filter: less lag than an EMA of the same critical period.",
    reference="https://www.mesasoftware.com/papers/EhlersSuperSmoother.pdf",
    outputs=("SSF",),
)
def super_smoother(close: ArrayLike, length: int = 20) -> pd.Series:
    """Super Smoother Filter (Ehlers).

    A 2-pole digital low-pass filter designed to remove aliasing noise
    (the jitter an ordinary moving average lets through) with far less lag
    than an EMA of the same critical period::

        a1 = exp(-1.414 * pi / n);  b1 = 2 * a1 * cos(1.414 * pi / n)
        c2 = b1;  c3 = -a1^2;  c1 = 1 - c2 - c3
        SSF[t] = c1 * (Close[t] + Close[t-1]) / 2 + c2 * SSF[t-1] + c3 * SSF[t-2]

    The first two bars are seeded directly from price (Ehlers' own
    bootstrap), since the recursion has no prior filtered values yet.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        The filter's critical period — the wavelength that separates what
        gets kept from what gets filtered out. Must be >= 1.

    Returns
    -------
    pandas.Series
        Named ``SSF_{length}``.

    Notes
    -----
    ``cos()``'s argument must be in radians here; at least one popular
    reference implementation keeps Ehlers' original EasyLanguage constant
    (``180``, meant for a degrees-based ``Cos()``) unconverted when porting
    to a radians-based language, which silently produces a different
    filter. This implementation follows the radians-consistent form
    (``cos(1.414 * pi / n)``), confirmed against an independent Python
    reference implementation.

    Examples
    --------
    >>> import zeonta
    >>> zeonta.super_smoother([10.0, 11.0, 12.0, 11.5, 12.5], length=3).tolist()
    [10.0, 11.0, 11.557155807187828, 11.780916493912489, 12.01394985765405]

    References
    ----------
    https://www.mesasoftware.com/papers/EhlersSuperSmoother.pdf
    """
    length = validate_length(length)
    values = as_array(close, "close")
    size = values.shape[0]

    a1 = np.exp(-1.414 * np.pi / length)
    b1 = 2.0 * a1 * np.cos(1.414 * np.pi / length)
    c2 = b1
    c3 = -a1 * a1
    c1 = 1.0 - c2 - c3

    result = np.full(size, np.nan, dtype="float64")
    prev_price = np.nan
    f1 = np.nan
    f2 = np.nan

    for i in range(size):
        price = values[i]
        if not np.isfinite(price):
            # Hold the last filtered value through a gap rather than
            # poisoning the recursion, the same convention ema_values() uses.
            result[i] = f1
            continue
        if not (np.isfinite(f1) and np.isfinite(f2) and np.isfinite(prev_price)):
            filtered = price
        else:
            filtered = c1 * (price + prev_price) / 2.0 + c2 * f1 + c3 * f2
        result[i] = filtered
        f2 = f1
        f1 = filtered
        prev_price = price

    return wrap_series(result, common_index(close), f"SSF_{length}")


@indicator(
    category="moving_averages",
    summary="Ehlers' Instantaneous Trendline: a filter tuned to track the trend, not the cycle.",
    reference=(
        "https://www.tradingview.com/support/solutions/43000589152-instantaneous-trendline/"
    ),
    outputs=("ITREND",),
)
def instantaneous_trendline(close: ArrayLike, alpha: Number = 0.07) -> pd.Series:
    """Instantaneous Trendline (Ehlers).

    ::

        IT[t] = (a - a^2/4) * Close[t] + 0.5*a^2 * Close[t-1]
                - (a - 0.75*a^2) * Close[t-2]
                + 2*(1-a) * IT[t-1] - (1-a)^2 * IT[t-2]

    where ``a`` is ``alpha``. Ehlers designed this specifically to
    track the *trend* component of price while rejecting the *cyclic*
    component — unlike an EMA of comparable responsiveness, which passes
    both through together. The first three bars, with no filtered history
    yet, are seeded as ``(Close[t] + 2*Close[t-1] + Close[t-2]) / 4``.

    Parameters
    ----------
    close:
        Closing prices.
    alpha:
        Smoothing factor; must be in ``(0, 1)``. Ehlers' own default is
        ``0.07``, roughly comparable to a 28-bar EMA (``alpha = 2/(n+1)``
        at ``n≈27.6``), though this indicator is parameterised by ``alpha``
        directly rather than by a bar count.

    Returns
    -------
    pandas.Series
        Named ``ITREND_{alpha}``.

    Examples
    --------
    >>> import zeonta
    >>> zeonta.instantaneous_trendline([10.0, 11.0, 12.0, 11.5, 12.5], alpha=0.5).tolist()
    [nan, nan, 11.0, 11.625, 11.875]

    References
    ----------
    https://www.tradingview.com/support/solutions/43000589152-instantaneous-trendline/
    """
    alpha = validate_multiplier(alpha, "alpha", minimum=0.0)
    if alpha >= 1.0:
        raise ValueError(f"'alpha' must be < 1, got {alpha}")
    values = as_array(close, "close")
    size = values.shape[0]

    result = np.full(size, np.nan, dtype="float64")
    for i in range(2, size):
        window = values[i - 2 : i + 1]
        if not np.all(np.isfinite(window)):
            continue
        seeded = (values[i] + 2.0 * values[i - 1] + values[i - 2]) / 4.0
        # Ehlers' own bootstrap covers bars 0-6 (indices < 7); a gap that
        # disrupts the recursive state later on falls back to the same
        # seed rather than reading NaN into the filter.
        if i < 7 or not (np.isfinite(result[i - 1]) and np.isfinite(result[i - 2])):
            result[i] = seeded
        else:
            result[i] = (
                (alpha - alpha * alpha / 4.0) * values[i]
                + 0.5 * alpha * alpha * values[i - 1]
                - (alpha - 0.75 * alpha * alpha) * values[i - 2]
                + 2.0 * (1.0 - alpha) * result[i - 1]
                - (1.0 - alpha) * (1.0 - alpha) * result[i - 2]
            )

    return wrap_series(result, common_index(close), f"ITREND_{alpha}")


def _wavelet_denoise_endpoint(segment: np.ndarray, wavelet: str, level: int) -> float:
    """Denoise *segment* with a level-*level* DWT and return only its last sample.

    Soft-thresholds every detail band with the Donoho-Johnstone universal
    threshold (noise sigma from the finest band's MAD) and leaves the
    approximation band untouched, then reconstructs and keeps the endpoint —
    the one sample that reflects *segment* and nothing after it.
    """
    # pywt's Cython core needs a writable buffer; a slice of the caller's
    # array may not be (e.g. a read-only view from DataFrame.to_numpy()).
    coeffs = pywt.wavedec(np.array(segment, dtype="float64"), wavelet, level=level)
    sigma = float(np.median(np.abs(coeffs[-1])) / 0.6745)
    threshold = 0.0 if sigma == 0.0 else sigma * np.sqrt(2.0 * np.log(segment.shape[0]))
    denoised = [coeffs[0], *(pywt.threshold(band, threshold, mode="soft") for band in coeffs[1:])]
    reconstructed: np.ndarray = pywt.waverec(denoised, wavelet)
    return float(reconstructed[-1])


@indicator(
    category="moving_averages",
    summary="Causal rolling wavelet (DWT) denoising: cuts noise without an EMA's lag.",
    reference="https://doi.org/10.1093/biomet/81.3.425",
    outputs=("WDENOISE",),
)
def wavelet_denoise(
    close: ArrayLike, window: int = 64, wavelet: str = "db4", level: int = 2
) -> pd.Series:
    """Wavelet-Denoised Price (Discrete Wavelet Transform, causal/rolling).

    Splits each rolling *window* of price into an approximation band (the
    trend) and *level* detail bands (finer and finer noise), zeroes out
    whatever in the detail bands is small enough to be noise rather than
    signal, and reconstructs — recovering the trend with far less lag than
    an EMA of comparable smoothness, since it only removes the parts of the
    signal identified as noise rather than damping everything equally.

    "Small enough to be noise" uses the Donoho-Johnstone universal
    threshold: the finest detail band's median absolute deviation estimates
    the noise level (``sigma = MAD(cD1) / 0.6745``, the usual
    Gaussian-consistent scaling), and any detail coefficient below
    ``sigma * sqrt(2 * log(window))`` is soft-thresholded — shrunk toward
    zero by the threshold rather than hard-clipped to it, which avoids
    reintroducing sharp jumps at the cutoff. This is the same rule
    academic work on wavelet-denoised technical indicators applies to
    price/return series before rebuilding indicators on top of it.

    **This implementation only ever looks backward.** Naive wavelet
    denoising decomposes an entire series in one pass, which means every
    bar's smoothed value depends on bars that come after it — each new bar
    silently *repaints* every past value, which is unusable for a live
    signal even though it looks fine in an in-sample backtest. Here, bar
    ``i``'s value comes only from ``close[i - window + 1 : i + 1]``: once
    written, it never changes as new bars arrive. The tradeoff is that each
    bar re-runs its own decomposition from scratch, rather than one pass
    over the whole series.

    Parameters
    ----------
    close:
        Closing prices.
    window:
        Bars per rolling decomposition. Must be large enough for *wavelet*
        to reach *level* levels — see ``pywt.dwt_max_level``; the defaults
        (64, ``"db4"``, level 2) need at least 28. Larger windows resolve
        lower frequencies but react more slowly to a genuine regime change.
    wavelet:
        Any discrete wavelet name PyWavelets recognises (``pywt.wavelist(kind="discrete")``).
        ``"db4"`` (Daubechies, 4 vanishing moments) is what published
        wavelet-denoised-indicator work most often uses.
    level:
        Number of detail bands to threshold. Must be >= 1 and small enough
        for *window* bars to support (see *window* above).

    Returns
    -------
    pandas.Series
        Named ``WDENOISE_{window}_{wavelet}``. The first ``window - 1``
        bars are ``NaN`` — there isn't a full window to decompose yet.

    Notes
    -----
    A denoised price series is a building block, not a finished
    indicator: pipe it into an existing indicator in place of raw
    ``close`` (e.g. ``zeonta.rsi(zeonta.wavelet_denoise(df["close"]))`` or
    the same for ``macd``) to get a wavelet-denoised version of it.

    Examples
    --------
    >>> import numpy as np
    >>> import zeonta
    >>> rng = np.random.default_rng(0)
    >>> noisy = np.cumsum(rng.normal(size=64)) + 100.0
    >>> result = zeonta.wavelet_denoise(noisy, window=32, level=2)
    >>> result.iloc[:31].isna().all()
    np.True_
    >>> round(result.iloc[-1], 6)
    np.float64(103.975548)

    References
    ----------
    https://doi.org/10.1093/biomet/81.3.425
    """
    window = validate_length(window, "window", minimum=2)
    if level < 1:
        raise ValueError(f"'level' must be >= 1, got {level}")
    max_level = pywt.dwt_max_level(window, pywt.Wavelet(wavelet).dec_len)
    if level > max_level:
        raise ValueError(
            f"'window' ({window}) is too short for {level} level(s) of '{wavelet}' — "
            f"the most this window supports is level={max_level}"
        )

    values = as_array(close, "close")
    size = values.shape[0]
    result = np.full(size, np.nan, dtype="float64")
    for i in range(window - 1, size):
        segment = values[i - window + 1 : i + 1]
        if not np.all(np.isfinite(segment)):
            continue
        result[i] = _wavelet_denoise_endpoint(segment, wavelet, level)

    return wrap_series(result, common_index(close), f"WDENOISE_{window}_{wavelet}")
