"""wavelet_lead_lag — not part of the registry, so it gets its own test file
rather than the generic registry-wide contract suite in test_contracts.py.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
import pytest

from zeonta.cross_asset import wavelet_lead_lag


def _sine_pair(period: int, lag: int, n: int = 300) -> tuple[np.ndarray, np.ndarray]:
    """*a* leads *b* by *lag* bars: b repeats what a did *lag* bars earlier."""
    t = np.arange(n, dtype="float64")
    omega = 2.0 * np.pi / period
    a = np.cos(omega * t)
    b = np.cos(omega * (t - lag))
    return a, b


def test_positive_phase_means_the_first_series_leads() -> None:
    a, b = _sine_pair(period=20, lag=3)
    result = wavelet_lead_lag(a, b, period=20)
    assert result["XWT_PHASE"].iloc[-1] > 0


def test_negative_phase_means_the_second_series_leads() -> None:
    a, b = _sine_pair(period=20, lag=3)
    # swap: now b leads a
    result = wavelet_lead_lag(b, a, period=20)
    assert result["XWT_PHASE"].iloc[-1] < 0


def test_phase_sign_flips_with_the_argument_order_and_is_antisymmetric() -> None:
    a, b = _sine_pair(period=20, lag=3)
    forward = wavelet_lead_lag(a, b, period=20)["XWT_PHASE"].iloc[-1]
    backward = wavelet_lead_lag(b, a, period=20)["XWT_PHASE"].iloc[-1]
    np.testing.assert_allclose(forward, -backward)


def test_identical_series_have_approximately_zero_phase() -> None:
    a, _ = _sine_pair(period=20, lag=0)
    result = wavelet_lead_lag(a, a, period=20)
    np.testing.assert_allclose(result["XWT_PHASE"].iloc[-1], 0.0, atol=1e-9)


def test_the_bar_count_conversion_is_approximate_but_same_direction() -> None:
    """The causal, one-sided kernel is documented to over-report lag magnitude
    by roughly 5-10% rather than get the direction wrong — this pins down
    that the error stays in that ballpark rather than silently growing."""
    a, b = _sine_pair(period=20, lag=3)
    result = wavelet_lead_lag(a, b, period=20)
    phase = result["XWT_PHASE"].iloc[-1]
    omega = 2.0 * np.pi / 20
    estimated_lag = phase / omega
    assert 3.0 < estimated_lag < 3.6


def test_warmup_bars_are_nan() -> None:
    a, b = _sine_pair(period=20, lag=0, n=200)
    result = wavelet_lead_lag(a, b, period=20)
    assert result["XWT_POWER"].iloc[0:5].isna().all()
    assert result["XWT_POWER"].iloc[-1:].notna().all()


def test_is_causal_new_bars_never_change_past_values() -> None:
    a, b = _sine_pair(period=20, lag=3, n=200)
    full = wavelet_lead_lag(a, b, period=20)
    prefix = wavelet_lead_lag(a[:120], b[:120], period=20)
    np.testing.assert_allclose(full.iloc[:120].to_numpy(), prefix.to_numpy(), equal_nan=True)


def test_a_missing_bar_is_nan_but_later_bars_recover() -> None:
    # period=10's default kernel is ~42 bars wide — the gap needs that many
    # clean bars after it before the window clears.
    a, b = _sine_pair(period=10, lag=0, n=250)
    a = a.copy()
    a[60] = np.nan
    with warnings.catch_warnings():
        warnings.simplefilter("error", category=RuntimeWarning)
        result = wavelet_lead_lag(a, b, period=10)
    assert np.isnan(result["XWT_POWER"].iloc[60])
    assert result["XWT_POWER"].iloc[200:].notna().all()


def test_rejects_misaligned_series_indices() -> None:
    a, b = _sine_pair(period=20, lag=0, n=50)
    series_a = pd.Series(a)
    series_b = pd.Series(b, index=pd.RangeIndex(1000, 1050))
    with pytest.raises(ValueError, match="different indices"):
        wavelet_lead_lag(series_a, series_b, period=20)


def test_rejects_mismatched_lengths() -> None:
    a, b = _sine_pair(period=20, lag=0, n=50)
    with pytest.raises(ValueError, match="same length"):
        wavelet_lead_lag(a, b[:-1], period=20)


def test_rejects_period_below_two() -> None:
    a, b = _sine_pair(period=20, lag=0, n=50)
    with pytest.raises(ValueError, match="must be >="):
        wavelet_lead_lag(a, b, period=1)


def test_rejects_non_positive_omega0() -> None:
    a, b = _sine_pair(period=20, lag=0, n=50)
    with pytest.raises(ValueError, match="'omega0' must be > 0"):
        wavelet_lead_lag(a, b, omega0=0.0)


def test_rejects_non_positive_e_foldings() -> None:
    a, b = _sine_pair(period=20, lag=0, n=50)
    with pytest.raises(ValueError, match="'e_foldings' must be > 0"):
        wavelet_lead_lag(a, b, e_foldings=0.0)
