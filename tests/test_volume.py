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


def test_obv_rejects_negative_volume() -> None:
    with pytest.raises(ValueError, match="'volume' must not contain negative values"):
        zeonta.obv([10.0, 11.0, 12.0], [100.0, -1.0, 100.0])


def test_obv_an_interior_gap_does_not_poison_the_running_total() -> None:
    """A single unknown bar must contribute nothing and then get out of the
    way, not turn every later bar into NaN via cumsum."""
    close = [10.0, 11.0, np.nan, 13.0, 14.0]
    volume = [100.0, 50.0, 80.0, 60.0, 70.0]
    result = zeonta.obv(close, volume)
    assert not result.isna().any()
    # bar 2 is the gap: contributes 0, so OBV holds at bar 1's value.
    np.testing.assert_allclose(result.iloc[2], result.iloc[1])
    # bar 3 compares today's real close (13) against the last *known* real
    # close (11, since bar 2 was unknown) rather than the missing one.
    np.testing.assert_allclose(result.iloc[3], result.iloc[1] + volume[3])


def test_obv_a_gap_in_volume_alone_also_holds_flat() -> None:
    close = [10.0, 11.0, 12.0, 13.0]
    volume = [100.0, 50.0, np.nan, 60.0]
    result = zeonta.obv(close, volume)
    assert not result.isna().any()
    np.testing.assert_allclose(result.iloc[2], result.iloc[1])


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


@pytest.mark.parametrize("func_name", ["cmf", "mfi"])
def test_rejects_negative_volume(func_name: str) -> None:
    func = getattr(zeonta, func_name)
    with pytest.raises(ValueError, match="'volume' must not contain negative values"):
        func([2.0] * 10, [1.0] * 10, [1.5] * 10, [-100.0] * 10)


def test_adl_matches_the_hand_computed_running_total() -> None:
    # Both bars close at the high -> multiplier = 1 on each -> MFV = volume.
    result = zeonta.adl([11, 12], [9, 10], [11, 12], [100, 100])
    np.testing.assert_allclose(result.to_numpy(), [100.0, 200.0])


def test_adl_subtracts_when_the_close_is_at_the_low() -> None:
    result = zeonta.adl([11, 12], [9, 10], [9, 10], [100, 50])
    np.testing.assert_allclose(result.to_numpy(), [-100.0, -150.0])


def test_adl_has_no_warmup_period() -> None:
    result = zeonta.adl([11, 12, 13], [9, 10, 11], [10, 11, 12], [1, 2, 3])
    assert not result.isna().any()


def test_adl_treats_a_zero_range_bar_as_carrying_no_flow() -> None:
    result = zeonta.adl([10.0, 10.0], [10.0, 10.0], [10.0, 10.0], [100.0, 100.0])
    np.testing.assert_allclose(result.to_numpy(), [0.0, 0.0])


def test_adl_rejects_negative_volume() -> None:
    with pytest.raises(ValueError, match="'volume' must not contain negative values"):
        zeonta.adl([11.0, 12.0], [9.0, 10.0], [11.0, 12.0], [100.0, -1.0])


def test_adl_an_interior_gap_does_not_poison_the_running_total() -> None:
    """A single unknown bar must contribute nothing and then get out of the
    way, not turn every later bar into NaN via cumsum — the same convention
    obv() uses."""
    high = [11.0, 12.0, np.nan, 13.0, 14.0]
    low = [9.0, 10.0, 8.0, 11.0, 12.0]
    close = [10.0, 11.0, 9.0, 12.5, 13.5]
    volume = [100.0, 50.0, 80.0, 60.0, 70.0]
    result = zeonta.adl(high, low, close, volume)
    assert not result.isna().any()
    # bar 2 is the gap: contributes 0, so ADL holds at bar 1's value.
    np.testing.assert_allclose(result.iloc[2], result.iloc[1])


def test_adl_a_gap_in_volume_alone_also_holds_flat() -> None:
    high = [11.0, 12.0, 13.0, 14.0]
    low = [9.0, 10.0, 11.0, 12.0]
    close = [10.0, 11.0, 12.0, 13.0]
    volume = [100.0, 50.0, np.nan, 60.0]
    result = zeonta.adl(high, low, close, volume)
    assert not result.isna().any()
    np.testing.assert_allclose(result.iloc[2], result.iloc[1])


def test_adl_and_cmf_share_the_same_money_flow_multiplier(ohlcv: pd.DataFrame) -> None:
    """CMF is ADL's per-bar increment summed over a window and normalised by
    volume; the two must agree bar for bar on the underlying multiplier."""
    adl = zeonta.adl(ohlcv["high"], ohlcv["low"], ohlcv["close"], ohlcv["volume"])
    increment = adl.diff()
    increment.iloc[0] = adl.iloc[0]
    manual_cmf = increment.rolling(20).sum() / ohlcv["volume"].rolling(20).sum()
    cmf = zeonta.cmf(ohlcv["high"], ohlcv["low"], ohlcv["close"], ohlcv["volume"], length=20)
    np.testing.assert_allclose(cmf.to_numpy(), manual_cmf.to_numpy(), equal_nan=True, atol=1e-9)


def test_chaikin_oscillator_is_the_fast_minus_slow_ema_of_adl(ohlcv: pd.DataFrame) -> None:
    adl = zeonta.adl(ohlcv["high"], ohlcv["low"], ohlcv["close"], ohlcv["volume"])
    expected = zeonta.ema(adl, 3) - zeonta.ema(adl, 10)
    result = zeonta.chaikin_oscillator(ohlcv["high"], ohlcv["low"], ohlcv["close"], ohlcv["volume"])
    np.testing.assert_allclose(result.to_numpy(), expected.to_numpy(), equal_nan=True)


def test_chaikin_oscillator_is_zero_on_a_flat_adl() -> None:
    # Every bar closes at the midpoint -> multiplier 0 -> ADL never moves.
    result = zeonta.chaikin_oscillator(
        [10.0] * 20, [8.0] * 20, [9.0] * 20, [100.0] * 20, fast=3, slow=10
    )
    np.testing.assert_allclose(result.dropna().to_numpy(), 0.0)


def test_chaikin_oscillator_rejects_fast_not_smaller_than_slow() -> None:
    with pytest.raises(ValueError, match="'fast' must be smaller than 'slow'"):
        zeonta.chaikin_oscillator(
            [11.0] * 15, [9.0] * 15, [10.0] * 15, [100.0] * 15, fast=10, slow=3
        )


def test_chaikin_oscillator_rejects_negative_volume() -> None:
    with pytest.raises(ValueError, match="'volume' must not contain negative values"):
        zeonta.chaikin_oscillator([11.0, 12.0], [9.0, 10.0], [11.0, 12.0], [100.0, -1.0])


def test_chaikin_oscillator_an_interior_gap_does_not_poison_the_underlying_adl() -> None:
    """The underlying ADL running total must not go permanently NaN after a
    single bad bar — same convention as adl() and obv()."""
    high = [11.0, 12.0, np.nan, 13.0, 14.0, 15.0]
    low = [9.0, 10.0, 8.0, 11.0, 12.0, 13.0]
    close = [10.0, 11.0, 9.0, 12.5, 13.5, 14.5]
    volume = [100.0, 50.0, 80.0, 60.0, 70.0, 90.0]
    result = zeonta.chaikin_oscillator(high, low, close, volume, fast=2, slow=3)
    assert not result.iloc[3:].isna().any()
