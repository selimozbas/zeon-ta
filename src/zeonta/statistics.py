"""Statistics: rolling standard deviation, variance, z-score, skewness, kurtosis, MAD, returns."""

from __future__ import annotations

import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

from ._core import (
    ArrayLike,
    Number,
    as_array,
    common_index,
    indicator,
    rolling_mean,
    rolling_std,
    validate_length,
    validate_multiplier,
    wrap_series,
)

__all__ = [
    "cumulative_return",
    "drawdown",
    "ffd",
    "kurtosis",
    "log_return",
    "mad",
    "skewness",
    "stddev",
    "variance",
    "zscore",
]


@indicator(
    category="statistics",
    summary="Rolling standard deviation of price.",
    reference="https://en.wikipedia.org/wiki/Standard_deviation",
    outputs=("STDDEV",),
)
def stddev(close: ArrayLike, length: int = 20, ddof: int = 0) -> pd.Series:
    """Rolling Standard Deviation.

    ``STDDEV = std(Close, n)``. ``ddof=0`` (population, the default) matches
    what :func:`bbands` uses; pass ``ddof=1`` for the sample estimate.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        Look-back window.
    ddof:
        Delta degrees of freedom. Must be ``< length``.

    Returns
    -------
    pandas.Series
        Named ``STDDEV_{length}``.

    Examples
    --------
    >>> import zeonta
    >>> float(zeonta.stddev([1.0, 2.0, 3.0, 4.0], length=4).iloc[-1])
    1.118033988749895
    """
    length = validate_length(length)
    values = as_array(close, "close")
    result = rolling_std(values, length, ddof=ddof)
    return wrap_series(result, common_index(close), f"STDDEV_{length}")


@indicator(
    category="statistics",
    summary="Rolling variance of price.",
    reference="https://en.wikipedia.org/wiki/Variance",
    outputs=("VAR",),
)
def variance(close: ArrayLike, length: int = 20, ddof: int = 0) -> pd.Series:
    """Rolling Variance.

    ``VAR = variance(Close, n)`` — the square of :func:`stddev`, computed
    directly rather than by squaring it.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        Look-back window.
    ddof:
        Delta degrees of freedom. Must be ``< length``.

    Returns
    -------
    pandas.Series
        Named ``VAR_{length}``.

    Examples
    --------
    >>> import zeonta
    >>> round(float(zeonta.variance([1.0, 2.0, 3.0, 4.0], length=4).iloc[-1]), 6)
    1.25
    """
    length = validate_length(length)
    values = as_array(close, "close")
    std = rolling_std(values, length, ddof=ddof)
    return wrap_series(std * std, common_index(close), f"VAR_{length}")


@indicator(
    category="statistics",
    summary="How many standard deviations price sits from its own rolling mean.",
    reference="https://en.wikipedia.org/wiki/Standard_score",
    outputs=("ZSCORE",),
)
def zscore(close: ArrayLike, length: int = 20) -> pd.Series:
    """Rolling Z-Score.

    ``ZSCORE = (Close - SMA(Close, n)) / STDDEV(Close, n)`` (population
    standard deviation). A statistical cousin of :func:`bbands`: the same
    mean and spread, expressed as a single number of standard deviations
    rather than a pair of bands to plot price against.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        Look-back window for both the mean and the standard deviation.

    Returns
    -------
    pandas.Series
        Named ``ZSCORE_{length}``. ``NaN`` wherever the window's standard
        deviation is exactly ``0`` (a perfectly flat window).

    Examples
    --------
    >>> import zeonta
    >>> float(zeonta.zscore([1.0, 2.0, 3.0, 4.0, 10.0], length=4).iloc[-1])
    1.6867605906952476
    """
    length = validate_length(length)
    values = as_array(close, "close")
    mean = rolling_mean(values, length)
    std = rolling_std(values, length, ddof=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        result = np.where(std > 0.0, (values - mean) / std, np.nan)
    return wrap_series(result, common_index(close), f"ZSCORE_{length}")


def _rolling_moment_windows(values: np.ndarray, length: int) -> tuple[np.ndarray, np.ndarray]:
    """``(windows, means)`` for every rolling window of *length*, NaN-padded to length."""
    size = values.shape[0]
    if size < length:
        return np.empty((0, length)), np.empty(0)
    windows = sliding_window_view(values, length)
    return windows, windows.mean(axis=1)


@indicator(
    category="statistics",
    summary="Adjusted Fisher-Pearson skewness: which tail of the recent distribution is longer.",
    reference="https://en.wikipedia.org/wiki/Skewness",
    outputs=("SKEW",),
)
def skewness(close: ArrayLike, length: int = 20) -> pd.Series:
    """Rolling Skewness (adjusted Fisher-Pearson coefficient).

    ``G1 = (sqrt(n*(n-1)) / (n-2)) * (m3 / m2^1.5)``, where ``m2``/``m3``
    are the window's 2nd/3rd central moments — the same bias-adjusted
    formula :meth:`pandas.Series.rolling.skew` uses (checked against it
    directly while this was written). Positive means a longer right tail
    (occasional sharp rallies within an otherwise typical window),
    negative a longer left tail (occasional sharp drops).

    Parameters
    ----------
    close:
        Closing prices.
    length:
        Look-back window. Must be >= 3.

    Returns
    -------
    pandas.Series
        Named ``SKEW_{length}``. ``NaN`` wherever the window is perfectly
        flat (zero variance, so the ratio is undefined).

    Examples
    --------
    >>> import zeonta
    >>> float(zeonta.skewness([1.0, 2.0, 3.0, 4.0, 20.0], length=5).iloc[-1])
    2.125050587633151
    """
    length = validate_length(length, minimum=3)
    values = as_array(close, "close")
    windows, mean = _rolling_moment_windows(values, length)
    result = np.full(values.shape[0], np.nan, dtype="float64")
    if windows.shape[0] > 0:
        deviation = windows - mean[:, None]
        m2 = np.mean(deviation**2, axis=1)
        m3 = np.mean(deviation**3, axis=1)
        with np.errstate(divide="ignore", invalid="ignore"):
            g1 = np.where(m2 > 0.0, m3 / m2**1.5, np.nan)
        adjustment = np.sqrt(length * (length - 1)) / (length - 2)
        result[length - 1 :] = adjustment * g1
    return wrap_series(result, common_index(close), f"SKEW_{length}")


@indicator(
    category="statistics",
    summary="Adjusted Fisher-Pearson excess kurtosis: how fat-tailed the recent distribution is.",
    reference="https://en.wikipedia.org/wiki/Kurtosis",
    outputs=("KURT",),
)
def kurtosis(close: ArrayLike, length: int = 20) -> pd.Series:
    """Rolling Kurtosis (adjusted Fisher-Pearson excess coefficient).

    ``G2 = ((n-1) / ((n-2)*(n-3))) * ((n+1)*g2 + 6)``, where
    ``g2 = m4/m2^2 - 3`` and ``m2``/``m4`` are the window's 2nd/4th central
    moments — the same bias-adjusted formula
    :meth:`pandas.Series.rolling.kurt` uses (checked against it directly
    while this was written). ``0`` is normal-distribution-like tails;
    positive means fatter tails / more outliers than normal (a window
    with a few large moves and otherwise little else); negative means
    thinner tails than normal.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        Look-back window. Must be >= 4.

    Returns
    -------
    pandas.Series
        Named ``KURT_{length}``. ``NaN`` wherever the window is perfectly
        flat (zero variance, so the ratio is undefined).

    Examples
    --------
    >>> import zeonta
    >>> float(zeonta.kurtosis([1.0, 2.0, 3.0, 4.0, 5.0, 30.0], length=6).iloc[-1])
    5.663774197249584
    """
    length = validate_length(length, minimum=4)
    values = as_array(close, "close")
    windows, mean = _rolling_moment_windows(values, length)
    result = np.full(values.shape[0], np.nan, dtype="float64")
    if windows.shape[0] > 0:
        deviation = windows - mean[:, None]
        m2 = np.mean(deviation**2, axis=1)
        m4 = np.mean(deviation**4, axis=1)
        with np.errstate(divide="ignore", invalid="ignore"):
            g2 = np.where(m2 > 0.0, m4 / m2**2 - 3.0, np.nan)
        adjustment = (length - 1) / ((length - 2) * (length - 3))
        result[length - 1 :] = adjustment * ((length + 1) * g2 + 6.0)
    return wrap_series(result, common_index(close), f"KURT_{length}")


@indicator(
    category="statistics",
    summary="Rolling median absolute deviation: a spread measure robust to outliers.",
    reference="https://en.wikipedia.org/wiki/Median_absolute_deviation",
    outputs=("MAD",),
)
def mad(close: ArrayLike, length: int = 20) -> pd.Series:
    """Rolling Median Absolute Deviation.

    ``MAD = median(|Close - median(Close, n)|, n)``. Unlike
    :func:`stddev` (which squares every deviation, so one large outlier
    dominates the reading) or the mean absolute deviation :func:`cci`
    uses internally, taking the *median* of the absolute deviations makes
    this robust to a single wild bar within the window.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        Look-back window. Must be >= 2.

    Returns
    -------
    pandas.Series
        Named ``MAD_{length}``.

    Examples
    --------
    >>> import zeonta
    >>> float(zeonta.mad([1.0, 2.0, 3.0, 4.0, 100.0], length=5).iloc[-1])
    1.0
    """
    length = validate_length(length, minimum=2)
    values = as_array(close, "close")
    size = values.shape[0]
    result = np.full(size, np.nan, dtype="float64")
    if size >= length:
        windows = sliding_window_view(values, length)
        median = np.median(windows, axis=1, keepdims=True)
        result[length - 1 :] = np.median(np.abs(windows - median), axis=1)
    return wrap_series(result, common_index(close), f"MAD_{length}")


@indicator(
    category="statistics",
    summary="Logarithmic return over a fixed bar lag.",
    reference="https://en.wikipedia.org/wiki/Rate_of_return",
    outputs=("LOGRET",),
)
def log_return(close: ArrayLike, length: int = 1) -> pd.Series:
    """Logarithmic Return.

    ``LOGRET = ln(Close[t] / Close[t-n])``. Unlike :func:`roc`'s simple
    percentage change, log returns are additive across time (the sum of
    single-bar log returns over a window equals the log return over the
    whole window), which is why they are the usual choice for statistical
    work on a return series rather than for charting.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        Bars to look back. Must be >= 1.

    Returns
    -------
    pandas.Series
        Named ``LOGRET_{length}``.

    Examples
    --------
    >>> import zeonta
    >>> import numpy as np
    >>> float(zeonta.log_return([100.0, 110.0]).iloc[-1]) == float(np.log(1.1))
    True
    """
    length = validate_length(length)
    values = as_array(close, "close")
    size = values.shape[0]
    result = np.full(size, np.nan, dtype="float64")
    if size > length:
        with np.errstate(divide="ignore", invalid="ignore"):
            result[length:] = np.log(values[length:] / values[:-length])
    return wrap_series(result, common_index(close), f"LOGRET_{length}")


def _ffd_weights(d: float, threshold: float) -> np.ndarray:
    """Binomial-series weights for fixed-width fractional differentiation.

    ``w_0 = 1``, ``w_k = -w_{k-1} * (d - k + 1) / k`` (the coefficients of
    ``(1-B)^d`` expanded as a binomial series in the backshift operator
    ``B``), generated until the newest weight's magnitude drops below
    *threshold* — the fixed truncation window this indicator is named for.
    """
    weights = [1.0]
    k = 1
    while True:
        next_weight = -weights[-1] * (d - k + 1) / k
        if abs(next_weight) < threshold:
            break
        weights.append(next_weight)
        k += 1
    return np.array(weights, dtype="float64")


@indicator(
    category="statistics",
    summary="Fractionally differenced price with a fixed-width weight window (Lopez de Prado).",
    reference="https://doi.org/10.1002/9781119482086",
    outputs=("FFD",),
)
def ffd(close: ArrayLike, d: Number = 0.5, threshold: Number = 1e-3) -> pd.Series:
    """Fixed-width window Fractional Differentiation (Lopez de Prado, 2018).

    Plain differencing (:func:`log_return`'s ``length=1`` case, or a plain
    ``Close.diff()``) removes *all* memory of a series' own level to force
    stationarity — order ``d=1``. This generalizes differencing to any
    fractional order ``0 < d < 1`` via the binomial series expansion of
    ``(1-B)^d`` (``B`` the backshift/lag operator)::

        w_0 = 1
        w_k = -w_{k-1} * (d - k + 1) / k,  k = 1, 2, ...

    generating weights until ``|w_k| < threshold`` — the *fixed-width*
    truncation this indicator is named for, chapter 5 of *Advances in
    Financial Machine Learning*'s alternative to expanding-window fractional
    differentiation, which instead reweights its *entire* history at every
    bar and is not causal in the same simple convolution sense. With the
    weights truncated to a fixed count ``l*`` (one shy of the first index
    whose weight falls below *threshold*), the output at each bar is::

        FFD[t] = sum(w_k * Close[t-k], k = 0 .. l*)

    the same fixed set of weights applied at every bar. A ``d`` close to
    ``0`` barely differences the series at all (it stays close to
    ``Close`` itself, non-stationary); ``d`` close to ``1`` approaches
    plain first differencing (stationary, but memory-free). The idea is
    to find the *smallest* ``d`` that achieves stationarity, keeping as
    much of the original series' memory as the transform allows — this
    function computes the transform for a chosen ``d``, not that search.

    Parameters
    ----------
    close:
        Closing prices.
    d:
        Fractional differencing order. Must satisfy ``0 < d < 1``; this
        function does not estimate an optimal ``d`` for you (typically
        found externally via an ADF stationarity test on a grid of ``d``
        values, per the book's own worked example).
    threshold:
        Weight-loss threshold controlling how many weights are kept: a
        smaller value keeps a longer (and slower) weight window with less
        approximation error relative to the full, untruncated expansion.
        Must satisfy ``0 < threshold < 1``. The book's own default (also
        used by this method's independent open-source replications, e.g.
        ``mlfinlab``'s ``frac_diff_ffd``) is ``1e-5``, but that keeps
        several *hundred* weights even at ``d=0.5`` — a window this
        library's other rolling indicators never ask for. ``1e-3`` (this
        function's own default, not the book's) keeps the same weight
        *formula* and truncation *rule* while needing a far shorter, more
        usable window; pass ``1e-5`` yourself to match the book's own
        examples exactly.

    Returns
    -------
    pandas.Series
        Named ``FFD_{d}_{threshold}``. ``NaN`` for the first ``l*`` bars,
        where ``l*`` (one less than the weight count) is the width of the
        fixed window every later bar's estimate is convolved over.

    Notes
    -----
    Every output bar is a fixed linear combination of a *fixed* number of
    trailing closes, so a single non-finite bar only poisons the bars whose
    own window still contains it — the same self-recovering behaviour every
    other rolling-window indicator in this library has, with no special
    casing needed.

    Examples
    --------
    >>> import zeonta
    >>> closes = [100.0, 101.0, 99.0, 102.0, 98.0, 103.0, 97.0, 104.0]
    >>> round(float(zeonta.ffd(closes, d=0.5, threshold=0.2).iloc[-1]), 6)
    55.5

    References
    ----------
    https://doi.org/10.1002/9781119482086
    """
    d = validate_multiplier(d, "d", minimum=0.0)
    if d >= 1.0:
        raise ValueError(f"'d' must satisfy 0 < d < 1, got {d}")
    threshold = validate_multiplier(threshold, "threshold", minimum=0.0)
    if threshold >= 1.0:
        raise ValueError(f"'threshold' must satisfy 0 < threshold < 1, got {threshold}")

    values = as_array(close, "close")
    size = values.shape[0]
    weights = _ffd_weights(float(d), float(threshold))
    width = weights.shape[0] - 1  # l*: bars looked back beyond the current one

    result = np.full(size, np.nan, dtype="float64")
    if size > width:
        windows = sliding_window_view(values, width + 1)
        result[width:] = windows @ weights[::-1]
    return wrap_series(result, common_index(close), f"FFD_{d}_{threshold}")


@indicator(
    category="statistics",
    summary="Cumulative percentage return since the start of the series.",
    reference="https://en.wikipedia.org/wiki/Rate_of_return",
    outputs=("CUMRET",),
)
def cumulative_return(close: ArrayLike) -> pd.Series:
    """Cumulative Return.

    ``CUMRET = (Close[t] / Close[0] - 1) * 100`` — the running percentage
    gain or loss since the very first bar of the input, unlike every
    other indicator in this library, which only ever looks back a fixed
    *length* of bars. Re-running this on a longer history changes every
    earlier value, since the anchor point (bar 0) changes with it —
    intentional, since the whole point is "return since the start of
    *this* series," but worth knowing before comparing two calls made
    with different amounts of history.

    Parameters
    ----------
    close:
        Closing prices.

    Returns
    -------
    pandas.Series
        Named ``CUMRET``. Always ``0`` on the first bar.

    Examples
    --------
    >>> import zeonta
    >>> [round(v, 6) for v in zeonta.cumulative_return([100.0, 110.0, 90.0])]
    [0.0, 10.0, -10.0]
    """
    values = as_array(close, "close")
    with np.errstate(divide="ignore", invalid="ignore"):
        result = (values / values[0] - 1.0) * 100.0
    return wrap_series(result, common_index(close), "CUMRET")


@indicator(
    category="statistics",
    summary="Percentage decline from the running peak, since the start of the series.",
    reference="https://en.wikipedia.org/wiki/Drawdown_(economics)",
    outputs=("DD",),
)
def drawdown(close: ArrayLike) -> pd.Series:
    """Drawdown.

    ``DD = (Close - CumMax(Close)) / CumMax(Close) * 100``, where
    ``CumMax`` is the running (expanding) all-time-high of ``Close`` up
    to and including the current bar. Always ``<= 0``; ``0`` exactly at
    every new high.

    Parameters
    ----------
    close:
        Closing prices.

    Returns
    -------
    pandas.Series
        Named ``DD``. Like :func:`cumulative_return`, this looks back to
        the start of whatever series you pass in rather than a fixed
        *length* — prepending more history can only ever move the running
        peak higher (or leave it unchanged), so it can change every later
        value the same way :func:`cumulative_return` does.

    Examples
    --------
    >>> import zeonta
    >>> [round(v, 6) for v in zeonta.drawdown([10.0, 12.0, 11.0, 15.0, 9.0])]
    [0.0, 0.0, -8.333333, 0.0, -40.0]

    References
    ----------
    https://en.wikipedia.org/wiki/Drawdown_(economics)
    """
    values = as_array(close, "close")
    # A plain np.maximum.accumulate would let one missing bar poison every
    # later running-peak value with NaN forever; pandas' own cummax skips
    # a NaN instead, holding the last real peak — the same
    # gap-does-not-poison-the-rest convention this library's running
    # totals (obv, adl) already follow, applied to a running maximum.
    running_peak = pd.Series(values).cummax().to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        result = np.where(running_peak != 0.0, (values - running_peak) / running_peak * 100.0, 0.0)
    result = np.where(np.isfinite(running_peak), result, np.nan)
    return wrap_series(result, common_index(close), "DD")
