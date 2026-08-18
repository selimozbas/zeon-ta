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
    validate_length,
    validate_multiplier,
    wrap_frame,
)

__all__ = ["wavelet_lead_lag"]


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
