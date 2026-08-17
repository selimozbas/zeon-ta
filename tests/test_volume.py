"""Volume-based indicators: On-Balance Volume, Chaikin Money Flow, Money Flow Index."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import zeonta


def test_obv_matches_the_hand_computed_running_total() -> None:
    result = zeonta.obv([10, 11, 10, 10], [100, 50, 80, 20])
    np.testing.assert_allclose(result.to_numpy(), [0.0, 50.0, -30.0, -30.0])


def test_obv_starts_at_zero_regardless_of_the_first_bars_volume() -> None:
    result = zeonta.obv([10, 11, 12], [999, 50, 50])
    np.testing.assert_allclose(result.iloc[0], 0.0)


def test_obv_never_changes_on_a_flat_close() -> None:
    result = zeonta.obv([10, 10, 10], [100, 100, 100])
    np.testing.assert_allclose(result.to_numpy(), [0.0, 0.0, 0.0])


def test_obv_has_no_warmup_period() -> None:
    result = zeonta.obv([10, 11, 12, 13], [1, 2, 3, 4])
    assert not result.isna().any()


def test_obv_rises_through_a_clean_uptrend() -> None:
    result = zeonta.obv(list(range(1, 30)), [10.0] * 29)
    assert result.is_monotonic_increasing


def test_cmf_matches_the_hand_computed_ratio() -> None:
    # Both bars close at the high -> multiplier = 1 on each -> CMF = 1.
    result = zeonta.cmf([11, 12], [9, 10], [11, 12], [100, 100], length=2)
    np.testing.assert_allclose(result.iloc[-1], 1.0)


def test_cmf_is_negative_one_when_every_close_is_at_the_low() -> None:
    result = zeonta.cmf([11, 12], [9, 10], [9, 10], [100, 100], length=2)
    np.testing.assert_allclose(result.iloc[-1], -1.0)


def test_cmf_treats_a_zero_range_bar_as_carrying_no_pressure() -> None:
    result = zeonta.cmf([10.0] * 25, [10.0] * 25, [10.0] * 25, [100.0] * 25, length=20)
    np.testing.assert_allclose(result.dropna().to_numpy(), 0.0)


def test_cmf_stays_within_its_theoretical_bounds(ohlcv: pd.DataFrame) -> None:
    result = zeonta.cmf(ohlcv["high"], ohlcv["low"], ohlcv["close"], ohlcv["volume"]).dropna()
    assert result.between(-1.0, 1.0).all()


def test_mfi_is_100_when_every_bar_gains() -> None:
    prices = [float(i) for i in range(2, 20)]
    result = zeonta.mfi(prices, [p - 1 for p in prices], prices, [100.0] * 18, length=14)
    np.testing.assert_allclose(result.iloc[-1], 100.0)


def test_mfi_is_0_when_every_bar_loses() -> None:
    prices = [float(i) for i in range(20, 2, -1)]
    result = zeonta.mfi(prices, [p - 1 for p in prices], prices, [100.0] * 18, length=14)
    np.testing.assert_allclose(result.iloc[-1], 0.0)


def test_mfi_is_50_on_a_perfectly_flat_market() -> None:
    result = zeonta.mfi([10.0] * 20, [9.0] * 20, [9.5] * 20, [100.0] * 20, length=14)
    np.testing.assert_allclose(result.iloc[-1], 50.0)


def test_mfi_stays_within_bounds(ohlcv: pd.DataFrame) -> None:
    result = zeonta.mfi(ohlcv["high"], ohlcv["low"], ohlcv["close"], ohlcv["volume"]).dropna()
    assert result.between(0.0, 100.0).all()


def test_mfi_uses_plain_sums_not_wilder_smoothing() -> None:
    """MFI's window is a flat rolling sum, so a value ages out after exactly
    `length` bars — unlike RSI's Wilder smoothing, which never fully forgets."""
    # A single early spike in positive flow should vanish from MFI once it
    # falls outside the window, but persist (attenuated) in RSI-style smoothing.
    prices = [10.0] * 30
    prices[1] = 20.0  # one big up-move at bar 1, flat everywhere else
    highs = prices
    lows = [p - 1 for p in prices]
    volume = [100.0] * 30
    result = zeonta.mfi(highs, lows, prices, volume, length=5)
    # Once bar 1's positive flow ages out of the 5-bar window, positive and
    # negative sums are both back to zero -> the flat-market convention (50).
    np.testing.assert_allclose(result.iloc[10], 50.0)


@pytest.mark.parametrize("func_name", ["cmf", "mfi"])
def test_length_must_be_positive(func_name: str) -> None:
    func = getattr(zeonta, func_name)
    with pytest.raises(ValueError, match="must be >="):
        func([2.0] * 10, [1.0] * 10, [1.5] * 10, [100.0] * 10, length=0)
