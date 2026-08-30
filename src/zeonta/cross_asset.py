"""Cross-asset tools: functions that compare two independent price series.

These are **not** part of the indicator registry. Every registered
indicator (:func:`zeonta.list_indicators`, the ``.zta`` accessor, and the
registry-wide contract test suite) assumes it consumes one asset's own
OHLCV columns — a genuine second, independent price series (a different
symbol, on its own timeline) does not fit that contract. Call the
functions here directly instead of through ``.zta``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ._core import (
    ArrayLike,
    Number,
    as_array,
    common_index,
    require_aligned_index,
    require_same_length,
    rolling_mean,
    rolling_std,
    validate_length,
    validate_multiplier,
    wrap_frame,
    wrap_series,
)

__all__ = ["beta", "correlation", "wavelet_lead_lag"]


def _morlet_kernel(scale: float, omega0: float, cutoff: int) -> np.ndarray:
    """Causal half (m = 0, 1, ..., cutoff) of the normalised Morlet wavelet.

    ``m`` counts bars into the past from "now" (``m=0`` is the current bar).
    Derived directly from Torrence & Compo (1998) eq. (1), (6) and (8) with
    ``δt=1``: ``ψ0(η) = π^-1/4 exp(iω0η) exp(-η²/2)``, normalised by
    ``(1/√s)``, evaluated at ``η = -m/s`` and conjugated (a real-valued CWT
    convolution weights ``x[n']`` by ``conj(ψ[(n'-n)/s])``).
    """
    m = np.arange(0, cutoff + 1, dtype="float64")
    kernel = (
        (1.0 / np.sqrt(scale))
        * (np.pi**-0.25)
        * np.exp(1j * omega0 * m / scale)
        * np.exp(-(m**2) / (2.0 * scale**2))
    )
    return np.asarray(kernel, dtype="complex128")


def _scale_from_period(period: float, omega0: float) -> float:
    """Morlet scale <-> Fourier period, Torrence & Compo (1998) Table 1."""
    return float(period * (omega0 + np.sqrt(2.0 + omega0**2)) / (4.0 * np.pi))


def correlation(close_a: ArrayLike, close_b: ArrayLike, length: int = 20) -> pd.Series:
    """Rolling Pearson Correlation between two price series.

    ``r = Cov(A, B) / (STDDEV(A) * STDDEV(B))`` over a rolling *length*-bar
    window, ranging -1 (moving in perfect opposition) to +1 (moving in
    perfect lockstep). Computed directly on price levels, not returns —
    for two series that are each trending, this mostly measures whether
    they are trending the *same direction*, which is usually what "is
    this pair correlated" means in practice; see :func:`beta` for the
    return-based version used to size a hedge.

    Not part of the indicator registry — see this module's own
    docstring for why a second, independent price series does not fit
    that contract. Call it directly rather than through ``.zta``.

    Parameters
    ----------
    close_a, close_b:
        Two closing-price series, one per asset, on the same timeline
        (an aligned index if both are ``pd.Series``; ``ValueError``
        otherwise).
    length:
        Rolling window. Must be >= 2.

    Returns
    -------
    pandas.DataFrame
        Named ``CORR_{length}``. ``NaN`` wherever either window has zero
        variance (a perfectly flat window can't correlate with anything).

    Examples
    --------
    >>> from zeonta.cross_asset import correlation
    >>> a = [10.0, 11.0, 9.0, 12.0, 13.0, 11.5]
    >>> b = [20.0, 21.5, 19.0, 23.0, 24.0, 22.0]
    >>> round(float(correlation(a, b, length=4).iloc[-1]), 6)
    0.997427

    References
    ----------
    https://en.wikipedia.org/wiki/Pearson_correlation_coefficient
    """
    length = validate_length(length, "length", minimum=2)
    require_aligned_index(close_a=close_a, close_b=close_b)
    a = as_array(close_a, "close_a")
    b = as_array(close_b, "close_b")
    require_same_length(close_a=a, close_b=b)

    mean_a = rolling_mean(a, length)
    mean_b = rolling_mean(b, length)
    std_a = rolling_std(a, length)
    std_b = rolling_std(b, length)
    mean_ab = rolling_mean(a * b, length)
    covariance = mean_ab - mean_a * mean_b

    with np.errstate(divide="ignore", invalid="ignore"):
        result = covariance / (std_a * std_b)
    result = np.where((std_a > 0.0) & (std_b > 0.0), result, np.nan)

    index = common_index(close_a, close_b)
    return wrap_series(result, index, f"CORR_{length}")


def beta(close_a: ArrayLike, close_b: ArrayLike, length: int = 20) -> pd.Series:
    """Rolling Beta of one asset's returns against another's.

    ``beta = Cov(R_a, R_b) / Var(R_b)`` over a rolling *length*-bar
    window of simple returns, where ``R_b`` is the benchmark
    (``close_b``) and ``R_a`` (``close_a``) is the asset being measured
    against it — the standard regression-slope definition finance uses
    to size a hedge: how much ``a`` tends to move for a given move in
    ``b``. Unlike :func:`correlation`, this is computed on returns, not
    raw price levels, and is not symmetric in its two arguments.

    Not part of the indicator registry — see this module's own
    docstring for why a second, independent price series does not fit
    that contract. Call it directly rather than through ``.zta``.

    Parameters
    ----------
    close_a:
        Closing prices of the asset being measured.
    close_b:
        Closing prices of the benchmark being measured against.
    length:
        Rolling window, in bar-to-bar returns. Must be >= 2.

    Returns
    -------
    pandas.Series
        Named ``BETA_{length}``. ``NaN`` for the first ``length`` bars
        (one bar is lost to differencing before the window can fill),
        and wherever the benchmark's own variance is exactly ``0``.

    Examples
    --------
    >>> from zeonta.cross_asset import beta
    >>> a = [10.0, 11.0, 9.0, 12.0, 13.0, 11.5]
    >>> b = [20.0, 21.5, 19.0, 23.0, 24.0, 22.0]
    >>> round(float(beta(a, b, length=3).iloc[-1]), 6)
    1.525413

    References
    ----------
    https://en.wikipedia.org/wiki/Beta_(finance)
    """
    length = validate_length(length, "length", minimum=2)
    require_aligned_index(close_a=close_a, close_b=close_b)
    a = as_array(close_a, "close_a")
    b = as_array(close_b, "close_b")
    size = require_same_length(close_a=a, close_b=b)

    with np.errstate(divide="ignore", invalid="ignore"):
        return_a = a[1:] / a[:-1] - 1.0
        return_b = b[1:] / b[:-1] - 1.0

    mean_a = rolling_mean(return_a, length)
    mean_b = rolling_mean(return_b, length)
    mean_ab = rolling_mean(return_a * return_b, length)
    var_b = rolling_std(return_b, length) ** 2
    covariance = mean_ab - mean_a * mean_b

    with np.errstate(divide="ignore", invalid="ignore"):
        raw = np.where(var_b > 0.0, covariance / var_b, np.nan)

    result = np.full(size, np.nan, dtype="float64")
    result[1:] = raw

    index = common_index(close_a, close_b)
    return wrap_series(result, index, f"BETA_{length}")


def wavelet_lead_lag(
    close_a: ArrayLike,
    close_b: ArrayLike,
    period: int = 20,
    omega0: Number = 6.0,
    e_foldings: Number = 3.0,
) -> pd.DataFrame:
    """Wavelet Lead-Lag (Cross-Wavelet Transform, Morlet).

    Given two price series, decomposes both with a Morlet Continuous
    Wavelet Transform at the single Fourier *period* requested, then forms
    the cross-wavelet spectrum ``W_XY = W_X * conj(W_Y)`` (Torrence & Compo
    1998, eq. in "Cross-wavelet spectrum"). Returns that spectrum split
    into magnitude and phase:

    - ``XWT_POWER = |W_XY|`` — how much co-movement exists at *period*,
      right now (near zero when the two series are unrelated or when
      either is flat at this scale).
    - ``XWT_PHASE = atan2(Im(W_XY), Re(W_XY))`` — the *lead-lag angle*, in
      radians. Sign convention (verified numerically, not just asserted
      from the paper's prose — see the module's own test suite): positive
      means *close_a* leads *close_b*; negative means *close_b* leads
      *close_a*; near zero means the two move together in phase at this
      timescale. Dividing by ``2*pi/period`` converts the angle to an
      approximate lead/lag in bars, though see the causality note below
      for why that conversion is not exact.

    **Causal, like this library's other wavelet-based tools.** The
    standard Torrence & Compo CWT convolves each point against the *full*
    (two-sided) Morlet kernel, which — like a whole-series DWT — lets a
    bar's value depend on bars that arrive later. This implementation
    instead uses only the *causal half* of the kernel (``m >= 0``: the
    current bar and bars before it), so a value once written never
    changes. This is a deliberate departure from the textbook transform,
    not an oversight, and it has a real cost: a numerical check (see the
    module's tests) against synthetic sine pairs of known lag shows the
    causal, one-sided kernel consistently *over-reports* the lag magnitude
    by roughly 5-10% versus the true value, while never getting the
    *sign* wrong. Treat ``XWT_PHASE``'s sign as reliable and its
    bar-count conversion as approximate.

    Parameters
    ----------
    close_a, close_b:
        Two closing-price series, one per asset, on the same timeline (an
        aligned index if both are ``pd.Series``; ``ValueError`` otherwise —
        see :func:`~zeonta._core.require_aligned_index`). Unlike a
        registered indicator's inputs, these are two independent assets,
        not two columns of the same one.
    period:
        The Fourier period (in bars) to analyse — the timescale of
        co-movement this call answers "which one is leading" for. Must be
        >= 2.
    omega0:
        Morlet's nondimensional frequency. Torrence & Compo use ``6``
        (the default) "to satisfy the admissibility condition"; values
        much below ~5 make the wavelet's own zero-mean assumption
        increasingly inaccurate. Must be > 0.
    e_foldings:
        How many e-folding times (``sqrt(2)*scale``, Table 1) of the
        Morlet's Gaussian envelope to keep before truncating the causal
        kernel — the warm-up and per-bar cost are both roughly
        ``e_foldings * sqrt(2) * scale`` bars, itself roughly
        ``period`` (e.g. ~83 bars for the period=20 default). The default,
        ``3``, leaves the Gaussian envelope at ``exp(-9) ≈ 1.2e-4`` of its
        peak at the truncation point; a numerical check found ``2`` already
        gives the same phase to 3 decimal places, so ``3`` is a safety
        margin, not a value tuned for accuracy. Must be > 0.

    Returns
    -------
    pandas.DataFrame
        Columns ``XWT_POWER`` and ``XWT_PHASE``. The first bars — as many
        as the kernel's truncated length needs — are ``NaN``.

    Examples
    --------
    >>> import numpy as np
    >>> from zeonta.cross_asset import wavelet_lead_lag
    >>> t = np.arange(200)
    >>> a = np.cos(2 * np.pi * t / 20)
    >>> b = np.cos(2 * np.pi * (t - 3) / 20)  # b repeats a, 3 bars later: a leads
    >>> result = wavelet_lead_lag(a, b, period=20)
    >>> bool(result["XWT_PHASE"].iloc[-1] > 0)
    True

    References
    ----------
    https://psl.noaa.gov/people/gilbert.p.compo/Torrence_compo1998.pdf
    """
    period = validate_length(period, "period", minimum=2)
    omega0 = validate_multiplier(omega0, "omega0")
    e_foldings = validate_multiplier(e_foldings, "e_foldings")
    require_aligned_index(close_a=close_a, close_b=close_b)
    a = as_array(close_a, "close_a")
    b = as_array(close_b, "close_b")
    size = require_same_length(close_a=a, close_b=b)

    scale = _scale_from_period(float(period), omega0)
    cutoff = int(np.ceil(e_foldings * np.sqrt(2.0) * scale))
    cutoff = min(cutoff, size - 1)
    kernel = _morlet_kernel(scale, omega0, cutoff)

    power = np.full(size, np.nan, dtype="float64")
    phase = np.full(size, np.nan, dtype="float64")
    for i in range(cutoff, size):
        window_a = a[i - cutoff : i + 1][::-1]
        window_b = b[i - cutoff : i + 1][::-1]
        if not (np.all(np.isfinite(window_a)) and np.all(np.isfinite(window_b))):
            continue
        w_a = np.sum(window_a * kernel)
        w_b = np.sum(window_b * kernel)
        w_xy = w_a * np.conj(w_b)
        power[i] = float(np.abs(w_xy))
        phase[i] = float(np.arctan2(w_xy.imag, w_xy.real))

    index = common_index(close_a, close_b)
    return wrap_frame(
        {"XWT_POWER": power, "XWT_PHASE": phase}, index, order=["XWT_POWER", "XWT_PHASE"]
    )
