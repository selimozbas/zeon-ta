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


def test_wma_matches_the_hand_computed_weighted_average() -> None:
    # window [1,2,3]: weights 1,2,3 -> (1*1+2*2+3*3)/6 = 14/6
    result = zeonta.wma([1, 2, 3, 4, 5], length=3)
    assert result.name == "WMA_3"
    assert np.isnan(result.iloc[0]) and np.isnan(result.iloc[1])
    np.testing.assert_allclose(result.iloc[2:], [14 / 6, 20 / 6, 26 / 6])


def test_wma_of_one_is_the_input() -> None:
    values = [3.0, 1.0, 4.0, 1.0, 5.0]
    np.testing.assert_allclose(zeonta.wma(values, length=1).to_numpy(), values)


def test_wma_warmup_is_exactly_length_minus_one() -> None:
    result = zeonta.wma(list(range(20)), length=7)
    assert int(result.isna().sum()) == 6


def test_wma_is_exact_on_a_flat_series() -> None:
    np.testing.assert_allclose(zeonta.wma([7.0] * 20, length=5).dropna().to_numpy(), 7.0)


def test_wma_weighs_recent_bars_more_than_sma_does() -> None:
    """A late jump should move WMA further than SMA at the same length."""
    prices = [10.0] * 9 + [20.0]
    wma_value = zeonta.wma(prices, length=10).iloc[-1]
    sma_value = zeonta.sma(prices, length=10).iloc[-1]
    assert wma_value > sma_value


def test_smma_seed_is_the_sma_then_wilder_recursion() -> None:
    # Seed at bar 2 = mean(1,2,3) = 2.0. alpha = 1/3.
    # bar 3: 2.0 + (4-2.0)/3 = 2.6666...; bar 4: 2.6666... + (5-2.6666...)/3 = 3.4444...
    result = zeonta.smma([1, 2, 3, 4, 5], length=3)
    assert result.name == "SMMA_3"
    assert np.isnan(result.iloc[0]) and np.isnan(result.iloc[1])
    np.testing.assert_allclose(result.iloc[2:], [2.0, 8 / 3, 31 / 9])


def test_smma_of_one_is_the_input() -> None:
    values = [3.0, 1.0, 4.0, 1.0, 5.0]
    np.testing.assert_allclose(zeonta.smma(values, length=1).to_numpy(), values)


def test_smma_warmup_is_exactly_length_minus_one() -> None:
    result = zeonta.smma(list(range(20)), length=7)
    assert int(result.isna().sum()) == 6


def test_smma_is_exact_on_a_flat_series() -> None:
    np.testing.assert_allclose(zeonta.smma([7.0] * 20, length=5).dropna().to_numpy(), 7.0)


def test_smma_matches_wilder_values_directly() -> None:
    """SMMA is Wilder's smoothing exposed as its own indicator — it must
    agree exactly with the recursion already used inside rsi()/atr()/adx()."""
    from zeonta._core.smoothing import wilder_values

    values = np.array([10.0, 11.0, 10.5, 12.0, 11.5, 13.0, 12.5, 14.0])
    np.testing.assert_allclose(
        zeonta.smma(values, length=4).to_numpy(), wilder_values(values, 4), equal_nan=True
    )


def test_smma_reacts_slower_than_ema_of_the_same_length() -> None:
    """alpha=1/n (SMMA) is smaller than alpha=2/(n+1) (EMA) for any n > 1,
    so a late jump moves SMMA less than it moves EMA at the same length."""
    prices = [10.0] * 19 + [20.0]
    smma_value = zeonta.smma(prices, length=10).iloc[-1]
    ema_value = zeonta.ema(prices, length=10).iloc[-1]
    assert smma_value < ema_value


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


def test_kama_seeds_with_close_at_the_first_computable_bar() -> None:
    values = [10.0, 12.0, 11.0, 15.0, 14.0, 20.0]
    result = zeonta.kama(values, length=3, fast=2, slow=30)
    assert np.isnan(result.iloc[:3]).all()
    np.testing.assert_allclose(result.iloc[3], values[3])


def test_kama_length_one_collapses_to_a_constant_alpha_recursion() -> None:
    """With a 1-bar window the Efficiency Ratio is always exactly 1, which
    pins the smoothing constant to (2/(fast+1))**2 for every bar — a
    hand-computable case that exercises the adaptive formula end to end."""
    values = [10.0, 12.0, 11.0, 15.0, 14.0, 20.0, 18.0, 25.0]
    result = zeonta.kama(values, length=1, fast=2, slow=30)
    alpha = (2.0 / 3.0) ** 2  # fast=2 -> fast_sc = 2/3, squared per the formula

    expected = [np.nan, values[1]]
    for value in values[2:]:
        expected.append(expected[-1] + alpha * (value - expected[-1]))

    np.testing.assert_allclose(result.to_numpy(), expected)


def test_kama_tracks_a_clean_trend_faster_than_a_choppy_one() -> None:
    """A high Efficiency Ratio should make KAMA move faster toward price."""
    trending = list(np.linspace(0, 50, 40))
    choppy = list(np.tile([25.0, 24.0], 20))

    trend_speed = abs(zeonta.kama(trending, length=10).diff().iloc[-1])
    chop_speed = abs(zeonta.kama(choppy, length=10).diff().iloc[-1])
    assert trend_speed > chop_speed


def test_kama_settles_into_a_fixed_steady_state_lag_on_a_straight_ramp() -> None:
    """ER = 1 the whole way pins SC at fast_sc**2 = (2/3)**2 = 4/9 every bar.

    A constant-alpha recursion tracking a straight ramp of slope m settles
    into a fixed lag of ``(1 - alpha) / alpha * m`` behind price — it never
    fully catches up, no matter how many bars follow. With alpha=4/9 and a
    unit slope that lag is exactly 1.25, which is what distinguishes this
    from a naive "eventually equals close" expectation.
    """
    values = list(np.arange(1.0, 200.0))
    result = zeonta.kama(values, length=10, fast=2, slow=30)
    alpha = (2.0 / 3.0) ** 2
    expected_lag = (1 - alpha) / alpha
    np.testing.assert_allclose(values[-1] - result.iloc[-1], expected_lag, atol=1e-6)


def test_kama_rejects_fast_not_smaller_than_slow() -> None:
    with pytest.raises(ValueError, match="'fast' must be smaller than 'slow'"):
        zeonta.kama(list(range(20)), length=5, fast=30, slow=30)


def test_kama_on_a_flat_series_has_zero_efficiency_and_matches_the_flat_price() -> None:
    result = zeonta.kama([7.0] * 20, length=5)
    np.testing.assert_allclose(result.dropna().to_numpy(), 7.0)


def test_kama_recovers_after_an_interior_gap() -> None:
    """A single bad tick must not poison the rest of the series: KAMA should
    hold its last value through the gap and resume updating once the
    Efficiency Ratio window clears it again."""
    values = [float(v) for v in range(1, 40)]
    values[15] = float("nan")
    result = zeonta.kama(values, length=5)

    # The gap widens the local warm-up (every window touching bar 15 is
    # NaN), but nothing after the window clears should stay NaN.
    assert not result.iloc[21:].isna().any()
    # The held value during the gap must be finite, not NaN or garbage.
    assert np.isfinite(result.iloc[16])


def test_kama_holds_its_value_exactly_through_a_gap_bar() -> None:
    values = [10.0, 12.0, 11.0, 15.0, 14.0, float("nan"), 20.0, 18.0, 25.0]
    result = zeonta.kama(values, length=1, fast=2, slow=30)
    # Bar 5 is the gap itself: nothing is knowable there, so it holds bar 4's
    # value rather than becoming NaN or silently updating on garbage input.
    np.testing.assert_allclose(result.iloc[5], result.iloc[4])


def test_dema_matches_the_hand_computed_double_ema() -> None:
    values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
    result = zeonta.dema(values, length=3)
    ema1 = zeonta.ema(values, length=3)
    ema2 = zeonta.ema(ema1, length=3)
    np.testing.assert_allclose(result.to_numpy(), (2.0 * ema1 - ema2).to_numpy(), equal_nan=True)


def test_dema_warmup_is_double_emas_own() -> None:
    # EMA1 warms up after `length - 1` bars; EMA2 needs a full window of
    # already-warmed-up EMA1 values, so DEMA needs 2*(length-1) bars.
    result = zeonta.dema(list(range(20)), length=4)
    assert int(result.isna().sum()) == 2 * 3


def test_dema_is_exact_on_a_flat_series() -> None:
    np.testing.assert_allclose(zeonta.dema([7.0] * 20, length=5).dropna().to_numpy(), 7.0)


def test_dema_has_less_steady_state_lag_than_ema() -> None:
    ramp = list(np.linspace(0, 100, 200))
    target = ramp[-1]
    ema_lag = target - zeonta.ema(ramp, length=10).iloc[-1]
    dema_lag = target - zeonta.dema(ramp, length=10).iloc[-1]
    assert abs(dema_lag) < abs(ema_lag)


def test_tema_matches_the_hand_computed_triple_ema() -> None:
    values = [float(v) for v in range(1, 15)]
    result = zeonta.tema(values, length=3)
    ema1 = zeonta.ema(values, length=3)
    ema2 = zeonta.ema(ema1, length=3)
    ema3 = zeonta.ema(ema2, length=3)
    expected = 3.0 * ema1 - 3.0 * ema2 + ema3
    np.testing.assert_allclose(result.to_numpy(), expected.to_numpy(), equal_nan=True)


def test_tema_warmup_is_triple_emas_own() -> None:
    result = zeonta.tema(list(range(30)), length=4)
    assert int(result.isna().sum()) == 3 * 3


def test_tema_is_exact_on_a_flat_series() -> None:
    np.testing.assert_allclose(zeonta.tema([7.0] * 30, length=5).dropna().to_numpy(), 7.0)


def test_tema_has_less_lag_than_dema_on_a_curve() -> None:
    """A pure straight ramp cancels lag exactly for both DEMA and TEMA (see
    the flat/ramp tests above), which can't distinguish them — a curved
    series can."""
    curve = list(np.linspace(0, 10, 100) ** 2)
    target = curve[-1]
    dema_lag = target - zeonta.dema(curve, length=10).iloc[-1]
    tema_lag = target - zeonta.tema(curve, length=10).iloc[-1]
    assert abs(tema_lag) < abs(dema_lag)


def test_hma_matches_alan_hulls_own_truncation_rule() -> None:
    """Alan Hull's own formula (alanhull.com) and an independent write-up
    both specify ``Integer()`` (truncate toward zero), not round-to-nearest,
    for both intermediate lengths: n=11 -> half-length truncates to 5
    (11/2=5.5), sqrt-length truncates to 3 (sqrt(11)=3.317)."""
    values = list(np.linspace(1, 50, 40))
    result = zeonta.hma(values, length=11)

    values_array = np.array(values)
    raw = (
        2.0 * zeonta.wma(values_array, length=5).to_numpy()
        - zeonta.wma(values_array, length=11).to_numpy()
    )
    expected = zeonta.wma(raw, length=3)

    np.testing.assert_allclose(result.to_numpy(), expected.to_numpy(), equal_nan=True)


def test_hma_converges_exactly_on_a_pure_ramp() -> None:
    """Like DEMA/TEMA, a WMA-cascade indicator cancels lag exactly on a
    perfectly linear series — this only holds with the correct (truncating)
    rounding rule; the previous round-to-nearest implementation missed the
    ramp's true value by a visible margin."""
    ramp = list(range(1, 31))
    np.testing.assert_allclose(zeonta.hma(ramp, length=9).iloc[-1], 30.0)


def test_hma_of_one_is_the_input() -> None:
    values = [3.0, 1.0, 4.0, 1.0, 5.0]
    np.testing.assert_allclose(zeonta.hma(values, length=1).to_numpy(), values)


def test_hma_is_exact_on_a_flat_series() -> None:
    np.testing.assert_allclose(zeonta.hma([7.0] * 30, length=9).dropna().to_numpy(), 7.0)


def test_hma_has_less_steady_state_lag_than_wma() -> None:
    ramp = list(np.linspace(0, 100, 200))
    target = ramp[-1]
    wma_lag = target - zeonta.wma(ramp, length=10).iloc[-1]
    hma_lag = target - zeonta.hma(ramp, length=10).iloc[-1]
    assert abs(hma_lag) < abs(wma_lag)


def test_hma_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.hma([1.0, 2.0, 3.0], length=0)
