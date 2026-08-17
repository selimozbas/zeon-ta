"""Moving averages: SMA, EMA, WMA, DEMA, TEMA, HMA, crossovers, the EMA
ribbon, and KAMA.

KAMA, HMA, DEMA and TEMA additionally cite the external source their formula
was verified against; see each one's own ``References`` section.
"""

from __future__ import annotations

import itertools
from collections.abc import Sequence

import numpy as np
import pandas as pd

from ._core import (
    ArrayLike,
    as_array,
    common_index,
    ema_values,
    indicator,
    rolling_mean,
    rolling_sum,
    rolling_wma,
    validate_length,
    wrap_frame,
    wrap_series,
)

__all__ = ["dema", "ema", "ema_ribbon", "hma", "kama", "ma_cross", "sma", "tema", "wma"]


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
