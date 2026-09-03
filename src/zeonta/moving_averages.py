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
    require_aligned_index,
    require_non_negative,
    require_same_length,
    rolling_max,
    rolling_mean,
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
from .oscillators import cmo

__all__ = [
    "alma",
    "dema",
    "efficiency_ratio",
    "ema",
    "ema_ribbon",
    "emd_imf1",
    "frama",
    "gmma",
    "hma",
    "instantaneous_trendline",
    "kalman_filter",
    "kama",
    "ma_cross",
    "mcgd",
    "sma",
    "smma",
    "super_smoother",
    "t3",
    "tema",
    "trima",
    "vidya",
    "vwma",
    "wavelet_denoise",
    "wma",
    "zlema",
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

    order = [f"MAfast_{fast}", f"MAslow_{slow}", f"cross_{fast}_{slow}"]
    return wrap_frame(
        {
            f"MAfast_{fast}": fast_line,
            f"MAslow_{slow}": slow_line,
            f"cross_{fast}_{slow}": cross,
        },
        common_index(close),
        order=order,
        roles={"fast": order[0], "slow": order[1], "cross": order[2]},
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


def _efficiency_ratio_values(values: np.ndarray, length: int) -> np.ndarray:
    """Kaufman's Efficiency Ratio, the shared core of :func:`kama` and :func:`efficiency_ratio`.

    ``ER = |Close - Close[n ago]| / Sum(|Close[i] - Close[i-1]|, n)`` — net
    movement over total movement, ``1`` for a bar that trended in a
    straight line, ``0`` for a perfectly flat window (which has no
    movement at all, efficient or not, rather than an undefined ``0/0``).
    """
    size = values.shape[0]
    abs_change = np.abs(np.diff(values, prepend=np.nan))
    volatility = np.full(size, np.nan, dtype="float64")
    volatility[1:] = rolling_sum(abs_change[1:], length)

    net_change = np.full(size, np.nan, dtype="float64")
    if size > length:
        net_change[length:] = np.abs(values[length:] - values[:-length])

    with np.errstate(divide="ignore", invalid="ignore"):
        efficiency = net_change / volatility
    return np.where(volatility == 0.0, 0.0, efficiency)


@indicator(
    category="moving_averages",
    summary="How efficiently price is trending: net movement over total movement.",
    reference=(
        "https://chartschool.stockcharts.com/table-of-contents/"
        "technical-indicators-and-overlays/technical-overlays/kaufmans-adaptive-moving-average-kama"
    ),
    outputs=("ER",),
)
def efficiency_ratio(close: ArrayLike, length: int = 10) -> pd.Series:
    """Kaufman's Efficiency Ratio.

    ``ER = |Close - Close[n ago]| / Sum(|Close[i] - Close[i-1]|, n)`` — the
    same ratio :func:`kama` blends into its own adaptive smoothing
    constant, exposed here on its own. ``1`` means the window trended in
    a straight line (every bar's movement contributed to the net move);
    near ``0`` means the window churned in place (a lot of bar-to-bar
    movement that mostly cancelled itself out).

    Parameters
    ----------
    close:
        Closing prices.
    length:
        Look-back window. Must be >= 1.

    Returns
    -------
    pandas.Series
        Named ``ER_{length}``, ranging 0 to 1. ``0`` on a perfectly flat
        window rather than an undefined ``0/0``.

    Examples
    --------
    >>> import zeonta
    >>> float(zeonta.efficiency_ratio(list(range(1, 10)), length=5).iloc[-1])
    1.0

    References
    ----------
    https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/kaufmans-adaptive-moving-average-kama
    """
    length = validate_length(length)
    values = as_array(close, "close")
    result = _efficiency_ratio_values(values, length)
    return wrap_series(result, common_index(close), f"ER_{length}")


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
    efficiency = _efficiency_ratio_values(values, length)

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
    summary="Recursive minimum-variance price estimate that updates its own confidence bar by bar.",
    reference="https://www.cs.unc.edu/~welch/media/pdf/kalman_intro.pdf",
    outputs=("KALMAN",),
)
def kalman_filter(
    close: ArrayLike,
    process_variance: Number = 1e-6,
    measurement_variance: Number = 1e-4,
) -> pd.Series:
    """Kalman Filter (Kalman, 1960; recursion per Welch & Bishop's tutorial).

    Treats ``log(Close)`` as a hidden, slowly drifting "true" level observed
    through noise, and tracks a minimum-mean-square-error estimate of it one
    bar at a time — no fixed window, no hand-picked smoothing constant.
    Every bar is a predict/correct pair::

        # predict
        P[i] = P[i-1] + process_variance
        # correct
        K[i] = P[i] / (P[i] + measurement_variance)
        x[i] = x[i-1] + K[i] * (log(Close[i]) - x[i-1])
        P[i] = (1 - K[i]) * P[i]

    seeded at the first finite bar with ``x = log(Close)``, ``P = 1.0``. The
    output is ``exp(x)``, back in price units. Filtering in log space keeps
    ``process_variance``/``measurement_variance`` on the same, roughly
    scale-free footing (daily log-return variance) whether the instrument
    trades at 10 or 100,000 — the same reason :func:`sample_entropy` works
    from log returns rather than raw price.

    The gain ``K`` starts high — an uncertain filter trusts its first few
    observations almost completely — and falls as ``P`` shrinks with each
    correction. Unlike :func:`ema`'s fixed smoothing constant, it is the
    filter's own running confidence in its estimate, not a hand-picked
    length, that decides how much each new bar moves it.

    Parameters
    ----------
    close:
        Closing prices.
    process_variance:
        How much the hidden "true" log-price is assumed to drift between
        bars. Smaller values trust the running estimate more and produce a
        smoother, slower line; must be > 0. There is no single correct
        value — tune it the way you would :func:`ema`'s ``length``, as a
        smoothness/responsiveness trade-off, not a formula input with one
        right answer.
    measurement_variance:
        How noisy a single bar's ``log(Close)`` is assumed to be around the
        true level. The default, ``1e-4``, is on the order of a ~1% daily
        move's variance; must be > 0.

    Returns
    -------
    pandas.Series
        Named ``KALMAN_{process_variance}_{measurement_variance}``. ``NaN``
        only where ``close`` itself has no finite value yet to seed from.

    Notes
    -----
    A ``NaN`` inside ``close`` holds the estimate across the gap rather than
    poisoning every bar after it — the same convention :func:`ema` and
    :func:`kama` use — and resumes updating from that held estimate as soon
    as a finite bar returns.

    Examples
    --------
    >>> import zeonta
    >>> round(float(zeonta.kalman_filter([100, 101, 99, 102, 105]).iloc[-1]), 2)
    101.77

    References
    ----------
    https://www.cs.unc.edu/~welch/media/pdf/kalman_intro.pdf
    """
    process_variance = validate_multiplier(process_variance, "process_variance")
    measurement_variance = validate_multiplier(measurement_variance, "measurement_variance")

    values = as_array(close, "close")
    size = values.shape[0]
    result = np.full(size, np.nan, dtype="float64")
    if size:
        with np.errstate(divide="ignore", invalid="ignore"):
            log_price = np.log(values)
        finite = np.isfinite(log_price)
        seed = int(np.argmax(finite)) if finite.any() else -1
        if seed >= 0:
            estimate = log_price[seed]
            variance = 1.0
            result[seed] = estimate
            for i in range(seed + 1, size):
                if not finite[i]:
                    # Hold the estimate across the gap rather than letting a
                    # single NaN propagate forever, matching kama()/ema_values().
                    result[i] = estimate
                    continue
                variance += process_variance
                gain = variance / (variance + measurement_variance)
                estimate = estimate + gain * (log_price[i] - estimate)
                variance = (1.0 - gain) * variance
                result[i] = estimate
        result = np.exp(result)

    return wrap_series(
        result, common_index(close), f"KALMAN_{process_variance}_{measurement_variance}"
    )


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
    result = super_smoother_values(values, length)
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


def _fit_natural_cubic_spline(
    x_knots: np.ndarray, y_knots: np.ndarray, x_query: np.ndarray
) -> np.ndarray:
    """Compute the natural cubic spline through ``(x_knots, y_knots)`` at ``x_query``.

    Hand-implemented (solves the standard tridiagonal second-derivative
    system directly with ``np.linalg.solve``) rather than adding a
    dependency for it — checked against ``scipy.interpolate.CubicSpline``
    while this was written (max difference ~1e-15) but scipy is not a
    runtime dependency of this library. ``x_knots`` must be sorted with no
    duplicates; ``len(x_knots) >= 2``.
    """
    n = x_knots.shape[0]
    if n == 2:
        slope = (y_knots[1] - y_knots[0]) / (x_knots[1] - x_knots[0])
        return np.asarray(y_knots[0] + slope * (x_query - x_knots[0]), dtype="float64")

    h = np.diff(x_knots)
    coefficients = np.zeros((n, n), dtype="float64")
    rhs = np.zeros(n, dtype="float64")
    coefficients[0, 0] = 1.0
    coefficients[n - 1, n - 1] = 1.0
    for i in range(1, n - 1):
        coefficients[i, i - 1] = h[i - 1]
        coefficients[i, i] = 2.0 * (h[i - 1] + h[i])
        coefficients[i, i + 1] = h[i]
        rhs[i] = 6.0 * (
            (y_knots[i + 1] - y_knots[i]) / h[i] - (y_knots[i] - y_knots[i - 1]) / h[i - 1]
        )
    second_derivative = np.linalg.solve(coefficients, rhs)

    segment = np.clip(np.searchsorted(x_knots, x_query, side="right") - 1, 0, n - 2)
    left_x, right_x = x_knots[segment], x_knots[segment + 1]
    span = right_x - left_x
    a = (right_x - x_query) / span
    b = (x_query - left_x) / span
    result = (
        a * y_knots[segment]
        + b * y_knots[segment + 1]
        + ((a**3 - a) * second_derivative[segment] + (b**3 - b) * second_derivative[segment + 1])
        * (span**2)
        / 6.0
    )
    return np.asarray(result, dtype="float64")


def _local_extrema(h: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Indices of *h*'s interior local maxima and local minima."""
    delta = np.diff(h)
    maxima = np.flatnonzero((delta[:-1] > 0.0) & (delta[1:] < 0.0)) + 1
    minima = np.flatnonzero((delta[:-1] < 0.0) & (delta[1:] > 0.0)) + 1
    return maxima, minima


def _envelope_mean(t: np.ndarray, h: np.ndarray) -> np.ndarray | None:
    """Mean of the upper/lower envelopes spline-fit through *h*'s extrema.

    ``None`` when *h* has fewer than two maxima or two minima — too few to
    define an envelope at all, the signal for the sifting loop to stop.

    Deliberately does *not* anchor either spline with *h*'s own first/last
    sample (a tempting way to avoid extrapolating past the real extrema,
    tried first here and rejected): pinning both the upper and lower
    envelope to the same literal endpoint value forces their mean to
    equal ``h`` exactly at that point, so every sift would zero out the
    boundary bars deterministically — caught by checking that the last
    bar of a sifted, clearly-oscillating test signal was not suspiciously
    always exactly ``0.0``. Left unanchored, the natural cubic spline
    still extrapolates past the outermost real extremum using that
    segment's own cubic, which is what Huang et al.'s paper calls for in
    substance (a smooth envelope beyond the last extremum) without the
    boundary artifact the anchored version introduced.
    """
    maxima, minima = _local_extrema(h)
    if maxima.shape[0] < 2 or minima.shape[0] < 2:
        return None
    upper = _fit_natural_cubic_spline(t[maxima], h[maxima], t)
    lower = _fit_natural_cubic_spline(t[minima], h[minima], t)
    return np.asarray((upper + lower) / 2.0, dtype="float64")


def _sift_first_imf(x: np.ndarray, max_iterations: int, sd_threshold: float) -> np.ndarray | None:
    """Extract the first Intrinsic Mode Function from *x* by sifting.

    Huang et al. (1998)'s own iterative procedure: repeatedly subtract the
    local mean of the upper/lower envelopes until the Cauchy-type
    convergence measure ``SD`` (the normalised squared change between
    successive sifts) drops below *sd_threshold*, or *max_iterations* is
    reached (a practical safety cap Huang's own convergence criterion does
    not itself require, since it is not guaranteed to converge on every
    input). ``None`` if *x* never had two-and-two extrema to sift even
    once — too little oscillatory structure to extract anything from.
    """
    t = np.arange(x.shape[0], dtype="float64")
    h = x
    sifted_at_least_once = False
    for _ in range(max_iterations):
        mean_envelope = _envelope_mean(t, h)
        if mean_envelope is None:
            break
        h_next = h - mean_envelope
        previous_energy = np.sum(h * h)
        sd = np.sum((h - h_next) ** 2) / previous_energy if previous_energy > 0.0 else 0.0
        h = h_next
        sifted_at_least_once = True
        if sd < sd_threshold:
            break
    return h if sifted_at_least_once else None


@indicator(
    category="moving_averages",
    summary="Empirical Mode Decomposition's first IMF: the dominant local oscillation.",
    reference="https://doi.org/10.1098/rspa.1998.0193",
    outputs=("EMDIMF1",),
)
def emd_imf1(
    close: ArrayLike,
    window: int = 100,
    max_iterations: int = 50,
    sd_threshold: Number = 0.25,
) -> pd.Series:
    """Empirical Mode Decomposition — first Intrinsic Mode Function (Huang et al., 1998).

    A rival to this library's wavelet tools for splitting price by
    timescale, built on a different idea: rather than a fixed basis
    (Fourier's sines, a wavelet's fixed mother function), EMD derives its
    basis functions — Intrinsic Mode Functions (IMFs) — directly from the
    data's own local extrema, by repeated ("sifting") subtraction of a
    spline-fit envelope mean. It was designed specifically for signals
    that are non-stationary and nonlinear, which describes a price series
    better than a fixed sinusoidal or wavelet basis assumes.

    This returns only the *first* IMF: the fastest local oscillation, with
    the slower trend/cycle components (later IMFs, and the final residual
    trend a full decomposition would also produce) removed. A full
    decomposition's IMF count varies with the data, which does not fit
    this library's fixed-column contract — see the Notes below for how to
    approximate the removed trend yourself.

    Parameters
    ----------
    close:
        Closing prices.
    window:
        Bars per rolling extraction. Must be >= 16 — a natural cubic
        spline envelope needs several extrema to be meaningful, not just
        the bare minimum two.
    max_iterations:
        Safety cap on sifting iterations per window. Not part of Huang et
        al.'s own convergence criterion (which has no guaranteed bound) —
        an engineering limit so a window that never converges cannot loop
        indefinitely. Must be >= 1.
    sd_threshold:
        Sifting stops once the Cauchy-type convergence measure ``SD``
        drops below this. Huang et al. recommend ``0.2`` to ``0.3``;
        ``0.25`` (the default) is their own paper's most-used value. Must
        be > 0.

    Returns
    -------
    pandas.Series
        Named ``EMDIMF1_{window}``. ``NaN`` for the first ``window - 1``
        bars, and wherever a window never had two-and-two extrema to sift
        even once (e.g. a monotonic or very short-period window).

    Notes
    -----
    Causal and rolling, like this library's wavelet-based tools, and for
    the same reason: sifting the *whole* series in one pass — the
    textbook approach — lets a bar's value depend on bars that arrive
    later. Every bar here is sifted from only its own trailing *window*,
    so a value once written never changes.

    ``close - zeonta.emd_imf1(close, window)`` approximates the trend/cycle
    residual a full decomposition would isolate, though it is not exactly
    that residual — this only ever extracts one IMF, not the full
    recursive decomposition down to a monotonic trend.

    By far the most expensive indicator in this library to compute: every
    bar re-runs an iterative spline-fitting loop over its own window, not
    a single vectorised pass or even the single fixed-shape loop
    :func:`~zeonta.sample_entropy` uses (see `BENCHMARKS.md`).

    Examples
    --------
    >>> import numpy as np
    >>> import zeonta
    >>> t = np.arange(150, dtype="float64")
    >>> fast = 0.5 * np.sin(2 * np.pi * t / 8)
    >>> slow_trend = 0.02 * t + 3 * np.sin(2 * np.pi * t / 150)
    >>> result = zeonta.emd_imf1(fast + slow_trend, window=100)
    >>> bool(result.dropna().std() < slow_trend.std())
    True

    References
    ----------
    https://doi.org/10.1098/rspa.1998.0193
    """
    window = validate_length(window, "window", minimum=16)
    if not isinstance(max_iterations, (int, np.integer)) or max_iterations < 1:
        raise ValueError(f"'max_iterations' must be an integer >= 1, got {max_iterations!r}")
    sd_threshold = validate_multiplier(sd_threshold, "sd_threshold")

    values = as_array(close, "close")
    size = values.shape[0]
    result = np.full(size, np.nan, dtype="float64")
    for i in range(window - 1, size):
        segment = values[i - window + 1 : i + 1]
        if not np.all(np.isfinite(segment)):
            continue
        imf1 = _sift_first_imf(segment, max_iterations, sd_threshold)
        if imf1 is not None:
            result[i] = imf1[-1]

    return wrap_series(result, common_index(close), f"EMDIMF1_{window}")


@indicator(
    category="moving_averages",
    summary="Simple moving average, but each bar weighted by its own volume.",
    reference="https://www.tradingview.com/support/solutions/43000592293-volume-weighted-moving-average-vwma/",
    outputs=("VWMA",),
)
def vwma(close: ArrayLike, volume: ArrayLike, length: int = 20) -> pd.Series:
    """Volume-Weighted Moving Average.

    ``VWMA = Sum(Close * Volume, n) / Sum(Volume, n)``. A plain
    :func:`sma` treats every bar equally regardless of how much traded on
    it; VWMA instead lets a heavy-volume bar pull the average toward its
    own close more than a quiet bar does.

    Parameters
    ----------
    close, volume:
        Series of equal length.
    length:
        Look-back window for both sums.

    Returns
    -------
    pandas.Series
        Named ``VWMA_{length}``. ``NaN`` wherever the window's total
        volume is exactly ``0``, rather than an undefined division.

    Examples
    --------
    >>> import zeonta
    >>> float(zeonta.vwma([10.0, 11.0, 12.0], [100.0, 200.0, 300.0], length=3).iloc[-1])
    11.333333333333334

    References
    ----------
    https://www.tradingview.com/support/solutions/43000592293-volume-weighted-moving-average-vwma/
    """
    length = validate_length(length)
    require_aligned_index(close=close, volume=volume)
    close_values = as_array(close, "close")
    volume_values = as_array(volume, "volume")
    require_same_length(close=close_values, volume=volume_values)
    require_non_negative(volume=volume_values)

    sum_volume = rolling_sum(volume_values, length)
    sum_price_volume = rolling_sum(close_values * volume_values, length)
    with np.errstate(divide="ignore", invalid="ignore"):
        result = np.where(sum_volume > 0.0, sum_price_volume / sum_volume, np.nan)

    return wrap_series(result, common_index(close, volume), f"VWMA_{length}")


@indicator(
    category="moving_averages",
    summary="An EMA fed de-lagged data, to track price with less delay than a plain EMA.",
    reference="https://user42.tuxfamily.org/chart/manual/Zero_002dLag-Exponential-Moving-Average.html",
    outputs=("ZLEMA",),
)
def zlema(close: ArrayLike, length: int = 20) -> pd.Series:
    """Zero-Lag Exponential Moving Average (Ehlers & Way, 2001).

    A plain EMA run not on price itself but on price with its own lag
    subtracted out first::

        lag = floor((n - 1) / 2)
        data[t] = Close[t] + (Close[t] - Close[t - lag])
        ZLEMA = EMA(data, n)

    A straight line's EMA always lags it by exactly ``lag`` bars; adding
    ``Close[t] - Close[t-lag]`` back in is designed to cancel that lag out
    (exactly, on a straight line — real price is not one, so some lag
    still remains in practice).

    Parameters
    ----------
    close:
        Closing prices.
    length:
        EMA period. Must be >= 1.

    Returns
    -------
    pandas.Series
        Named ``ZLEMA_{length}``. Bars before ``lag`` use ``Close`` itself
        (no prior bar far enough back yet to de-lag against).

    Examples
    --------
    >>> import zeonta
    >>> zeonta.zlema([10.0, 11.0, 9.0, 12.0, 13.0], length=3).tolist()
    [nan, nan, 9.666666666666666, 12.333333333333332, 13.166666666666666]

    References
    ----------
    https://user42.tuxfamily.org/chart/manual/Zero_002dLag-Exponential-Moving-Average.html
    """
    length = validate_length(length)
    values = as_array(close, "close")
    lag = (length - 1) // 2

    data = values.copy()
    if lag > 0 and values.shape[0] > lag:
        data[lag:] = values[lag:] + (values[lag:] - values[:-lag])

    result = ema_values(data, length)
    return wrap_series(result, common_index(close), f"ZLEMA_{length}")


@indicator(
    category="moving_averages",
    summary="Gaussian-weighted moving average tuned by an offset (lag vs. smoothness) and sigma.",
    reference="https://www.tradingview.com/support/solutions/43000594683-arnaud-legoux-moving-average/",
    outputs=("ALMA",),
)
def alma(
    close: ArrayLike, length: int = 9, offset: Number = 0.85, sigma: Number = 6.0
) -> pd.Series:
    """Arnaud Legoux Moving Average (Legoux & Ossanna, 2009).

    Weights each bar in the window by a Gaussian curve rather than
    uniformly (:func:`sma`) or linearly (:func:`wma`)::

        m = floor(offset * (n - 1));  s = n / sigma
        w[j] = exp(-(j - m)^2 / (2 * s^2))     for j = 0 .. n-1
        ALMA = sum(w[j] * Close[t-n+1+j]) / sum(w[j])

    ``offset`` slides the Gaussian's peak within the window — toward the
    most recent bar (``offset`` near ``1``) for less lag, or toward the
    middle (``offset`` near ``0``) for more smoothing. ``sigma`` widens or
    narrows the curve itself.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        Window size. Must be >= 2.
    offset:
        Where the Gaussian peak sits within the window, in ``[0, 1]``.
        ``0.85`` (the default) is Legoux's own most commonly cited value.
    sigma:
        Gaussian width control. ``6`` (the default) is Legoux's own
        cited value. Must be > 0.

    Returns
    -------
    pandas.Series
        Named ``ALMA_{length}_{offset}_{sigma}``.

    Examples
    --------
    >>> import zeonta
    >>> float(zeonta.alma([10.0, 11.0, 9.0, 12.0, 13.0], length=5).iloc[-1])
    11.491571199166234

    References
    ----------
    https://www.tradingview.com/support/solutions/43000594683-arnaud-legoux-moving-average/
    """
    length = validate_length(length, minimum=2)
    offset = validate_multiplier(offset, "offset", minimum=-1.0)
    if offset > 1.0:
        raise ValueError(f"'offset' must be <= 1, got {offset}")
    sigma = validate_multiplier(sigma, "sigma")

    values = as_array(close, "close")
    size = values.shape[0]

    m = np.floor(offset * (length - 1))
    s = length / sigma
    j = np.arange(length, dtype="float64")
    weights = np.exp(-((j - m) ** 2) / (2.0 * s * s))
    weight_sum = weights.sum()

    result = np.full(size, np.nan, dtype="float64")
    for i in range(length - 1, size):
        window = values[i - length + 1 : i + 1]
        if not np.all(np.isfinite(window)):
            continue
        result[i] = np.dot(window, weights) / weight_sum

    return wrap_series(result, common_index(close), f"ALMA_{length}_{offset}_{sigma}")


@indicator(
    category="moving_averages",
    summary="A moving average that speeds up in fast markets and slows down in quiet ones.",
    reference="https://www.tradingview.com/support/solutions/43000589175-mcginley-dynamic/",
    outputs=("MCGD",),
)
def mcgd(close: ArrayLike, length: int = 10) -> pd.Series:
    """McGinley Dynamic (John R. McGinley, 1997).

    ``MD[0] = Close[0]``; for every following bar,
    ``MD[i] = MD[i-1] + (Close[i] - MD[i-1]) / (N * (Close[i] / MD[i-1])^4)``,
    with ``N = length``. The ``(Close/MD)^4`` term is the whole idea: it
    grows quickly whenever price pulls away from the average, which
    speeds the average up to catch up in a fast market, and shrinks back
    toward ``1`` when price and the average are close, which slows the
    average back down in a quiet one — self-adjusting in a way a fixed-
    period :func:`ema` is not.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        The ``N`` constant. McGinley's own convention treats it the same
        way an EMA/SMA period is chosen. Must be >= 1.

    Returns
    -------
    pandas.Series
        Named ``MCGD_{length}``. Never ``NaN`` past the first bar — a
        recursive running value, not a windowed statistic.

    Examples
    --------
    >>> import zeonta
    >>> zeonta.mcgd([10.0, 11.0, 9.0, 12.0], length=10).tolist()
    [10.0, 10.068301345536508, 9.900981074320383, 9.998256757959089]

    References
    ----------
    https://www.tradingview.com/support/solutions/43000589175-mcginley-dynamic/
    """
    length = validate_length(length)
    values = as_array(close, "close")
    size = values.shape[0]
    result = np.full(size, np.nan, dtype="float64")
    result[0] = values[0]
    for i in range(1, size):
        previous = result[i - 1]
        current = values[i]
        # The (Close/MD)^4 term is 0 whenever current is exactly 0, which
        # would divide by zero below — the formula has no real answer at
        # that singular point, so this bar is held flat instead, the same
        # convention used when there is no finite previous value to build on.
        if not np.isfinite(previous + current) or previous == 0.0 or current == 0.0:
            result[i] = previous
            continue
        result[i] = previous + (current - previous) / (length * (current / previous) ** 4)

    return wrap_series(result, common_index(close), f"MCGD_{length}")


@indicator(
    category="moving_averages",
    summary="An SMA of an SMA, weighting the middle of the window most heavily.",
    reference="https://tulipindicators.org/trima",
    outputs=("TRIMA",),
)
def trima(close: ArrayLike, length: int = 20) -> pd.Series:
    """Triangular Moving Average.

    An :func:`sma` of an :func:`sma`, with the two window sizes chosen so
    the combined effect is a triangular (rather than rectangular) set of
    weights across the full ``length`` bars — the middle of the window
    counts for the most, tapering off toward both edges::

        even length: TRIMA = SMA(SMA(Close, n/2), n/2 + 1)
        odd length:  TRIMA = SMA(SMA(Close, (n+1)/2), (n+1)/2)

    Parameters
    ----------
    close:
        Closing prices.
    length:
        Overall window. Must be >= 1.

    Returns
    -------
    pandas.Series
        Named ``TRIMA_{length}``.

    Examples
    --------
    >>> import zeonta
    >>> zeonta.trima(list(range(1, 8)), length=5).tolist()
    [nan, nan, nan, nan, 3.0, 4.0, 5.0]

    References
    ----------
    https://tulipindicators.org/trima
    """
    length = validate_length(length)
    values = as_array(close, "close")
    if length % 2 == 0:
        first_length, second_length = length // 2, length // 2 + 1
    else:
        first_length = second_length = (length + 1) // 2

    first_pass = rolling_mean(values, first_length)
    result = rolling_mean(first_pass, second_length)
    return wrap_series(result, common_index(close), f"TRIMA_{length}")


@indicator(
    category="moving_averages",
    summary="An EMA whose smoothing speed adapts bar by bar to CMO's momentum reading.",
    reference="https://www.tradingpedia.com/forex-trading-indicators/chandes-variable-index-dynamic-average/",
    outputs=("VIDYA",),
)
def vidya(close: ArrayLike, length: int = 14, cmo_length: int = 9) -> pd.Series:
    """Variable Index Dynamic Average (Tushar Chande, 1992; revised 1995).

    ``VIDYA[i] = Close[i] * F * |CMO[i]| + VIDYA[i-1] * (1 - F * |CMO[i]|)``,
    where ``F = 2 / (length + 1)`` is an ordinary EMA smoothing constant.
    ``CMO`` here is Chande's own volatility index in his original ``[-1, 1]``
    scale (his own 1995 revision, replacing an earlier standard-deviation-
    based one) — :func:`cmo` in this library reports the same quantity on
    the ``[-100, 100]`` percentage scale most charting platforms use, so it
    is divided by ``100`` before use here. ``|CMO/100|`` ranges 0 to 1, so
    this behaves like an EMA whose smoothing constant is scaled down toward
    ``0`` (freezing the average) whenever momentum is weak and choppy, and
    scaled up toward the full ``F`` whenever momentum is strongly one-sided.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        Period for the base EMA smoothing constant ``F``. Must be >= 1.
    cmo_length:
        Look-back for the :func:`cmo` volatility index. Must be >= 1.

    Returns
    -------
    pandas.Series
        Named ``VIDYA_{length}_{cmo_length}``. ``NaN`` until ``cmo_length``
        bars of :func:`cmo` are available, then seeded with ``Close``.

    Examples
    --------
    >>> import zeonta
    >>> round(float(zeonta.vidya(list(range(1, 20)), length=5, cmo_length=4).iloc[-1]), 4)
    17.0069

    References
    ----------
    https://www.tradingpedia.com/forex-trading-indicators/chandes-variable-index-dynamic-average/
    """
    length = validate_length(length)
    cmo_length = validate_length(cmo_length, "cmo_length")
    values = as_array(close, "close")
    size = values.shape[0]

    alpha = np.abs(cmo(values, length=cmo_length).to_numpy() / 100.0) * (2.0 / (length + 1.0))

    result = np.full(size, np.nan, dtype="float64")
    previous = np.nan
    for i in range(size):
        value = values[i]
        factor = alpha[i]
        valid = np.isfinite(value) and np.isfinite(factor)
        if not np.isfinite(previous):
            if valid:
                previous = value
                result[i] = previous
            continue
        if valid:
            previous = value * factor + previous * (1.0 - factor)
        # else: hold `previous` across the gap, matching kama()'s convention.
        result[i] = previous

    return wrap_series(result, common_index(close), f"VIDYA_{length}_{cmo_length}")


@indicator(
    category="moving_averages",
    summary="EMA whose smoothing constant adapts to price's own fractal dimension.",
    outputs=("FRAMA",),
    reference="https://www.mesasoftware.com/papers/FRAMA.pdf",
)
def frama(high: ArrayLike, low: ArrayLike, length: int = 16) -> pd.Series:
    """Fractal Adaptive Moving Average (John Ehlers, 2005).

    Splits the window in half, measures each half's own high-low range
    per bar (a proxy for how much "box-counting" the price path needs at
    that scale — Ehlers' own fractal-dimension argument), and combines
    them into a fractal dimension between market noise (``D=2``) and a
    straight line (``D=1``)::

        N1 = (Highest(High, n/2) - Lowest(Low, n/2)) / (n/2)          [most recent half]
        N2 = (same, for the OLDER half of the window) / (n/2)
        N3 = (Highest(High, n) - Lowest(Low, n)) / n
        D = (ln(N1 + N2) - ln(N3)) / ln(2)
        alpha = clip(exp(-4.6 * (D - 1)), 0.01, 1.0)
        FRAMA = alpha * (High+Low)/2 + (1 - alpha) * FRAMA[-1]

    At ``D=1`` (a straight trend line) alpha is ``1`` — as fast as an
    average can be, equal to price itself. At ``D=2`` (pure noise) alpha
    is ``0.01`` — as slow as a 200-bar SMA. This is the same "let the
    market's own statistics set the smoothing speed" idea :func:`kama`
    and :func:`vidya` use, built from range roughness instead of
    Kaufman's Efficiency Ratio or Chande's CMO.

    Parameters
    ----------
    high, low:
        Price series of equal length.
    length:
        Total window split into two equal halves. Must be even and >= 2;
        Ehlers' own default is ``16``.

    Returns
    -------
    pandas.Series
        Named ``FRAMA_{length}``.

    Notes
    -----
    Ehlers' own construction outputs the midpoint price directly for the
    first ``length`` bars (there is no fixed-window warm-up the way
    :func:`ema` has) rather than ``NaN`` — the adaptive recursion only
    starts once a full window is available to measure the fractal
    dimension from. A degenerate sub-window (``N1``, ``N2`` or ``N3``
    exactly ``0``, a perfectly flat half) holds the previous fractal
    dimension rather than producing an undefined ``log(0)``, matching
    Ehlers' own EasyLanguage code.

    Examples
    --------
    >>> import zeonta
    >>> high = list(range(2, 42))
    >>> low = list(range(0, 40))
    >>> round(float(zeonta.frama(high, low, length=8).iloc[-1]), 6)
    38.987829

    References
    ----------
    https://www.mesasoftware.com/papers/FRAMA.pdf
    """
    length = validate_length(length, minimum=2)
    if length % 2 != 0:
        raise ValueError(f"'length' must be an even number, got {length}")
    require_aligned_index(high=high, low=low)
    high_values = as_array(high, "high")
    low_values = as_array(low, "low")
    size = require_same_length(high=high_values, low=low_values)

    half = length // 2
    price = (high_values + low_values) / 2.0

    n3 = (rolling_max(high_values, length) - rolling_min(low_values, length)) / length
    recent_high = rolling_max(high_values, half)
    recent_low = rolling_min(low_values, half)
    n1 = (recent_high - recent_low) / half
    if half < size:
        older_high = np.concatenate((np.full(half, np.nan), recent_high[:-half]))
        older_low = np.concatenate((np.full(half, np.nan), recent_low[:-half]))
    else:
        older_high = np.full(size, np.nan)
        older_low = np.full(size, np.nan)
    n2 = (older_high - older_low) / half

    with np.errstate(divide="ignore", invalid="ignore"):
        raw_dimen = (np.log(n1 + n2) - np.log(n3)) / np.log(2.0)
    valid_dimen = (n1 > 0.0) & (n2 > 0.0) & (n3 > 0.0)
    dimen = pd.Series(np.where(valid_dimen, raw_dimen, np.nan)).ffill().to_numpy()

    with np.errstate(over="ignore"):
        alpha = np.exp(-4.6 * (dimen - 1.0))
    alpha = np.clip(alpha, 0.01, 1.0)

    result = np.full(size, np.nan, dtype="float64")
    previous = np.nan
    for i in range(size):
        if i < length:
            previous = price[i]
            result[i] = previous
            continue
        factor = alpha[i]
        value = price[i]
        if np.isfinite(value) and np.isfinite(factor) and np.isfinite(previous):
            previous = factor * value + (1.0 - factor) * previous
        # else: hold `previous` across a gap rather than propagating NaN.
        result[i] = previous

    return wrap_series(result, common_index(high, low), f"FRAMA_{length}")


#: Guppy's own short-term (speculator) and long-term (investor) EMA groups.
GMMA_FAST_LENGTHS: tuple[int, ...] = (3, 5, 8, 10, 12, 15)
GMMA_SLOW_LENGTHS: tuple[int, ...] = (30, 35, 40, 45, 50, 60)


@indicator(
    category="moving_averages",
    summary="Two six-EMA ribbons (short-term traders, long-term investors) plotted together.",
    outputs=tuple(
        [f"GMMAf_{n}" for n in GMMA_FAST_LENGTHS] + [f"GMMAs_{n}" for n in GMMA_SLOW_LENGTHS]
    ),
    returns_frame=True,
    reference=(
        "https://chartschool.stockcharts.com/table-of-contents/trading-strategies-and-models/"
        "trading-strategies/moving-average-trading-strategies/"
        "guppy-multiple-moving-average-an-ma-ribbon-designed-to-tip-the-markets-hand"
    ),
)
def gmma(close: ArrayLike) -> pd.DataFrame:
    """Guppy Multiple Moving Average (Daryl Guppy).

    Two fixed six-line EMA ribbons (see :func:`ema_ribbon`) plotted together
    rather than one: a "fast" group (``3, 5, 8, 10, 12, 15``) standing in for
    short-term trader activity, and a "slow" group
    (``30, 35, 40, 45, 50, 60``) standing in for longer-term investor
    activity. Neither group's period is tunable — the whole point of
    GMMA is this specific pair of period sets, not a generic ribbon.

    Parameters
    ----------
    close:
        Closing prices.

    Returns
    -------
    pandas.DataFrame
        Columns ``GMMAf_3`` .. ``GMMAf_15`` (the fast group) followed by
        ``GMMAs_30`` .. ``GMMAs_60`` (the slow group).

    Notes
    -----
    Compression *within* a group (the six lines converging) signals
    agreement among that group's own timescales; wide separation
    *between* the two groups signals a well-established trend. The
    fast group crossing the slow group is the classic GMMA entry
    signal, but reading the ribbons' own compression/expansion is the
    indicator's real purpose.

    Examples
    --------
    >>> import zeonta
    >>> list(zeonta.gmma(list(range(70))).columns)  # doctest: +NORMALIZE_WHITESPACE
    ['GMMAf_3', 'GMMAf_5', 'GMMAf_8', 'GMMAf_10', 'GMMAf_12', 'GMMAf_15',
     'GMMAs_30', 'GMMAs_35', 'GMMAs_40', 'GMMAs_45', 'GMMAs_50', 'GMMAs_60']

    References
    ----------
    https://chartschool.stockcharts.com/table-of-contents/trading-strategies-and-models/trading-strategies/moving-average-trading-strategies/guppy-multiple-moving-average-an-ma-ribbon-designed-to-tip-the-markets-hand
    """
    values = as_array(close, "close")
    order = [f"GMMAf_{n}" for n in GMMA_FAST_LENGTHS] + [f"GMMAs_{n}" for n in GMMA_SLOW_LENGTHS]
    columns = {
        name: ema_values(values, length)
        for name, length in zip(order, (*GMMA_FAST_LENGTHS, *GMMA_SLOW_LENGTHS), strict=True)
    }
    return wrap_frame(columns, common_index(close), order=order)
