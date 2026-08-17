"""Moving averages — golden values traced by hand from the formulas."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import zeonta


def test_sma_matches_hand_computed_windows() -> None:
    result = zeonta.sma([1, 2, 3, 4, 5], length=3)
    assert result.name == "SMA_3"
    assert np.isnan(result.iloc[0]) and np.isnan(result.iloc[1])
    np.testing.assert_allclose(result.iloc[2:], [2.0, 3.0, 4.0])


def test_sma_of_one_is_the_input() -> None:
    values = [3.0, 1.0, 4.0, 1.0, 5.0]
    np.testing.assert_allclose(zeonta.sma(values, length=1).to_numpy(), values)


def test_sma_warmup_is_exactly_length_minus_one() -> None:
    result = zeonta.sma(list(range(20)), length=7)
    assert int(result.isna().sum()) == 6


def test_ema_seed_is_the_sma_then_recursion() -> None:
    # k = 2/(3+1) = 0.5. Seed at bar 2 = mean(1,2,3) = 2.
    # bar 3 = 0.5*4 + 0.5*2 = 3.0 ; bar 4 = 0.5*5 + 0.5*3 = 4.0
    result = zeonta.ema([1, 2, 3, 4, 5], length=3)
    np.testing.assert_allclose(result.iloc[2:], [2.0, 3.0, 4.0])


def test_ema_reacts_faster_than_sma_after_a_jump() -> None:
    prices = [10.0] * 20 + [20.0] * 5
    fast = zeonta.ema(prices, length=10).iloc[-1]
    slow = zeonta.sma(prices, length=10).iloc[-1]
    assert fast > slow


def test_ema_converges_to_a_constant_series() -> None:
    np.testing.assert_allclose(zeonta.ema([7.0] * 60, length=10).iloc[-1], 7.0)


def test_ma_cross_marks_golden_and_death_crosses() -> None:
    prices = [10.0] * 10 + list(np.linspace(10, 30, 20)) + list(np.linspace(30, 5, 25))
    out = zeonta.ma_cross(prices, fast=3, slow=8)
    signals = out["cross_3_8"].dropna()
    assert set(signals.unique()) <= {-1.0, 0.0, 1.0}
    assert (signals == 1.0).sum() == 1
    assert (signals == -1.0).sum() == 1
    # The golden cross must come before the death cross on a rise-then-fall series.
    assert signals[signals == 1.0].index[0] < signals[signals == -1.0].index[0]


def test_ma_cross_rejects_fast_not_smaller_than_slow() -> None:
    with pytest.raises(ValueError, match="'fast' must be smaller than 'slow'"):
        zeonta.ma_cross([1.0] * 10, fast=10, slow=10)


def test_ma_cross_ema_mode_uses_emas() -> None:
    prices = list(np.linspace(1, 50, 60))
    out = zeonta.ma_cross(prices, fast=5, slow=10, mode="ema")
    np.testing.assert_allclose(out["MAfast_5"], zeonta.ema(prices, 5), equal_nan=True)


def test_ma_cross_rejects_unknown_mode() -> None:
    with pytest.raises(ValueError, match="'mode' must be"):
        zeonta.ma_cross([1.0] * 10, fast=2, slow=3, mode="wma")


def test_ema_ribbon_columns_match_requested_lengths() -> None:
    out = zeonta.ema_ribbon(list(range(80)), lengths=(5, 10, 20))
    assert list(out.columns) == ["EMA_5", "EMA_10", "EMA_20"]
    np.testing.assert_allclose(out["EMA_10"], zeonta.ema(list(range(80)), 10), equal_nan=True)


def test_ema_ribbon_fans_out_in_a_trend() -> None:
    out = zeonta.ema_ribbon(list(np.linspace(1, 100, 200)), lengths=(5, 10, 20, 40))
    last = out.iloc[-1]
    # In a steady uptrend, shorter EMAs sit above longer ones.
    assert list(last) == sorted(last, reverse=True)


def test_ema_ribbon_requires_increasing_lengths() -> None:
    with pytest.raises(ValueError, match="strictly increasing"):
        zeonta.ema_ribbon(list(range(50)), lengths=(20, 10))


def test_ema_ribbon_requires_at_least_two_lengths() -> None:
    with pytest.raises(ValueError, match="at least two"):
        zeonta.ema_ribbon(list(range(50)), lengths=(20,))


@pytest.mark.parametrize("length", [0, -3])
def test_non_positive_length_is_rejected(length: int) -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.sma([1.0, 2.0, 3.0], length=length)


def test_non_integer_length_is_rejected() -> None:
    with pytest.raises(ValueError, match="must be an integer"):
        zeonta.sma([1.0, 2.0, 3.0], length=2.5)  # type: ignore[arg-type]


def test_index_is_carried_through(ohlcv: pd.DataFrame) -> None:
    result = zeonta.sma(ohlcv["close"], length=10)
    pd.testing.assert_index_equal(result.index, ohlcv.index)
