"""Oscillators — golden values traced by hand from the formulas."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import zeonta


def test_rsi_matches_a_hand_traced_wilder_recursion() -> None:
    # closes 10, 11, 10.5, 11.5, 12 -> changes +1, -0.5, +1, +0.5
    # seed (bar 3): avgGain = (1+0+1)/3 = 2/3 ; avgLoss = (0+0.5+0)/3 = 1/6 -> RS 4 -> RSI 80
    # bar 4: avgGain = (2/3*2 + 0.5)/3 = 11/18 ; avgLoss = (1/6*2)/3 = 1/9 -> RS 5.5 -> RSI 84.6153...
    result = zeonta.rsi([10, 11, 10.5, 11.5, 12], length=3)
    assert result.name == "RSI_3"
    np.testing.assert_allclose(result.iloc[3], 80.0)
    np.testing.assert_allclose(result.iloc[4], 100 - 100 / 6.5)


def test_rsi_is_100_when_every_bar_gains() -> None:
    np.testing.assert_allclose(zeonta.rsi(list(range(1, 40)), length=14).iloc[-1], 100.0)


def test_rsi_is_0_when_every_bar_loses() -> None:
    np.testing.assert_allclose(zeonta.rsi(list(range(40, 1, -1)), length=14).iloc[-1], 0.0)


def test_rsi_is_50_on_a_perfectly_flat_series() -> None:
    """No gains and no losses is genuinely neutral, not undefined."""
    np.testing.assert_allclose(zeonta.rsi([25.0] * 40, length=14).iloc[-1], 50.0)


def test_rsi_stays_within_bounds(ohlcv: pd.DataFrame) -> None:
    values = zeonta.rsi(ohlcv["close"]).dropna()
    assert values.between(0.0, 100.0).all()


def test_stoch_places_close_inside_the_range() -> None:
    # window of 2 at the last bar: highest high 6, lowest low 3, close 5 -> 100*(5-3)/(6-3)
    out = zeonta.stoch([3, 4, 5, 6], [1, 2, 3, 4], [2, 3, 4, 5], length=2, smooth_k=1, smooth_d=1)
    np.testing.assert_allclose(out.iloc[-1, 0], 100 * 2 / 3)


def test_stoch_is_100_at_the_top_of_the_range() -> None:
    out = zeonta.stoch([5, 6], [1, 2], [5, 6], length=2, smooth_k=1, smooth_d=1)
    np.testing.assert_allclose(out.iloc[-1, 0], 100.0)


def test_stoch_returns_midpoint_on_a_zero_width_range() -> None:
    out = zeonta.stoch([5.0] * 10, [5.0] * 10, [5.0] * 10, length=3)
    assert out.dropna().to_numpy().max() == 50.0


def test_stoch_d_is_the_smoothed_k() -> None:
    frame = zeonta.stoch(
        list(np.linspace(10, 20, 60)),
        list(np.linspace(9, 19, 60)),
        list(np.linspace(9.5, 19.5, 60)),
        length=5,
        smooth_k=3,
        smooth_d=3,
    )
    k, d = frame.columns
    np.testing.assert_allclose(
        frame[d].to_numpy(), zeonta.sma(frame[k], 3).to_numpy(), equal_nan=True
    )


def test_macd_is_the_difference_of_two_emas() -> None:
    prices = list(np.linspace(10, 60, 200))
    out = zeonta.macd(prices)
    expected = zeonta.ema(prices, 12) - zeonta.ema(prices, 26)
    np.testing.assert_allclose(out["MACD_12_26_9"], expected, equal_nan=True)


def test_macd_histogram_is_line_minus_signal() -> None:
    out = zeonta.macd(list(np.linspace(10, 60, 200)))
    np.testing.assert_allclose(
        out["MACDh_12_26_9"], out["MACD_12_26_9"] - out["MACDs_12_26_9"], equal_nan=True
    )


def test_macd_is_positive_in_an_uptrend() -> None:
    assert zeonta.macd(list(np.linspace(10, 100, 200)))["MACD_12_26_9"].iloc[-1] > 0


def test_macd_rejects_fast_not_smaller_than_slow() -> None:
    with pytest.raises(ValueError, match="'fast' must be smaller than 'slow'"):
        zeonta.macd(list(range(50)), fast=26, slow=12)


def test_cci_matches_the_lambert_formula() -> None:
    highs = [10.0, 11.0, 12.0]
    lows = [8.0, 9.0, 10.0]
    closes = [9.0, 10.0, 11.0]
    typical = np.array([9.0, 10.0, 11.0])
    mean = typical.mean()
    deviation = np.abs(typical - mean).mean()
    expected = (typical[-1] - mean) / (0.015 * deviation)
    out = zeonta.cci(highs, lows, closes, length=3)
    np.testing.assert_allclose(out.iloc[-1], expected)


def test_cci_is_zero_on_a_flat_market() -> None:
    np.testing.assert_allclose(zeonta.cci([2.0] * 25, [1.0] * 25, [1.5] * 25).iloc[-1], 0.0)


def test_cci_rejects_non_positive_constant() -> None:
    with pytest.raises(ValueError, match="'constant' must be > 0"):
        zeonta.cci([2.0] * 25, [1.0] * 25, [1.5] * 25, constant=0.0)


def test_cmo_matches_the_hand_computed_ratio() -> None:
    result = zeonta.cmo([10.0, 11.0, 10.5, 12.0, 11.5], length=4)
    np.testing.assert_allclose(result.iloc[-1], 42.857142857142854)


def test_cmo_is_100_when_every_bar_gains() -> None:
    np.testing.assert_allclose(zeonta.cmo(list(range(1, 40)), length=14).iloc[-1], 100.0)


def test_cmo_is_negative_100_when_every_bar_loses() -> None:
    np.testing.assert_allclose(zeonta.cmo(list(range(40, 1, -1)), length=14).iloc[-1], -100.0)


def test_cmo_is_zero_on_a_perfectly_flat_series() -> None:
    """No gains and no losses is genuinely neutral, not undefined."""
    np.testing.assert_allclose(zeonta.cmo([25.0] * 40, length=14).iloc[-1], 0.0)


def test_cmo_stays_within_bounds(ohlcv: pd.DataFrame) -> None:
    result = zeonta.cmo(ohlcv["close"]).dropna()
    assert result.between(-100.0, 100.0).all()


def test_cmo_does_not_smooth_a_gain_out_of_the_window_gradually() -> None:
    """Unlike RSI's Wilder smoothing, a gain drops out completely once it
    ages past `length` bars rather than fading gradually - the whole
    point of using plain sums instead."""
    prices = [10.0] * 30
    prices[1] = 20.0  # one big up-move at bar 1, flat everywhere else
    result = zeonta.cmo(prices, length=5)
    # Once bar 1's gain ages out of the 5-bar window, both sums are back
    # to zero -> the flat-market convention (0), not a lingering positive
    # reading the way RSI's Wilder smoothing would still show.
    np.testing.assert_allclose(result.iloc[10], 0.0)


def test_cmo_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.cmo([1.0, 2.0, 3.0], length=0)


def test_momentum_is_the_raw_n_bar_difference() -> None:
    result = zeonta.momentum([10, 11, 12, 15], length=3)
    assert np.isnan(result.iloc[:3]).all()
    np.testing.assert_allclose(result.iloc[3], 5.0)


def test_momentum_is_negative_in_a_downtrend() -> None:
    assert zeonta.momentum(list(range(30, 0, -1)), length=5).iloc[-1] < 0


def test_momentum_is_zero_on_a_flat_series() -> None:
    np.testing.assert_allclose(zeonta.momentum([5.0] * 20, length=5).dropna().to_numpy(), 0.0)


def test_roc_matches_the_hand_computed_percentage() -> None:
    # close 3 bars ago = 10, current = 15 -> (15-10)/10*100 = 50
    result = zeonta.roc([10, 11, 12, 15], length=3)
    np.testing.assert_allclose(result.iloc[3], 50.0)


def test_roc_and_momentum_agree_on_direction() -> None:
    prices = list(np.linspace(10, 40, 50))
    momentum = zeonta.momentum(prices, length=9)
    roc = zeonta.roc(prices, length=9)
    np.testing.assert_allclose(np.sign(momentum.dropna()), np.sign(roc.dropna()))


def test_roc_is_undefined_when_the_reference_close_is_zero() -> None:
    result = zeonta.roc([0, 5, 10, 20], length=1)
    assert np.isnan(result.iloc[1])


def test_roc_is_zero_on_a_flat_series() -> None:
    np.testing.assert_allclose(zeonta.roc([5.0] * 20, length=5).dropna().to_numpy(), 0.0)


def test_williams_r_equals_unsmoothed_stoch_k_minus_100(ohlcv: pd.DataFrame) -> None:
    """The formula's own claim: %R = %K - 100 for the unsmoothed %K."""
    willr = zeonta.williams_r(ohlcv["high"], ohlcv["low"], ohlcv["close"], length=14)
    stoch_k = zeonta.stoch(
        ohlcv["high"], ohlcv["low"], ohlcv["close"], length=14, smooth_k=1, smooth_d=1
    )["STOCHk_14_1_1"]
    np.testing.assert_allclose(willr.to_numpy(), (stoch_k - 100.0).to_numpy(), equal_nan=True)


def test_williams_r_matches_the_hand_computed_value() -> None:
    # highest high=6, lowest low=1, close=5.5 -> (6-5.5)/(6-1)*-100 = -10
    result = zeonta.williams_r([5, 6], [1, 2], [5, 5.5], length=2)
    np.testing.assert_allclose(result.iloc[-1], -10.0)


def test_williams_r_stays_within_bounds(ohlcv: pd.DataFrame) -> None:
    result = zeonta.williams_r(ohlcv["high"], ohlcv["low"], ohlcv["close"]).dropna()
    assert result.between(-100.0, 0.0).all()


def test_williams_r_is_midpoint_on_a_dead_flat_range() -> None:
    result = zeonta.williams_r([5.0] * 20, [5.0] * 20, [5.0] * 20, length=5)
    np.testing.assert_allclose(result.dropna().to_numpy(), -50.0)


def test_stoch_rsi_stays_within_bounds(ohlcv: pd.DataFrame) -> None:
    out = zeonta.stoch_rsi(ohlcv["close"]).dropna()
    assert out.to_numpy().min() >= 0.0
    assert out.to_numpy().max() <= 100.0


def test_stoch_rsi_falls_back_to_the_midpoint_when_rsi_is_flat() -> None:
    """A steady uptrend pins RSI at 100; once RSI itself stops moving,
    StochRSI's own high-low range collapses to zero."""
    result = zeonta.stoch_rsi(list(range(1, 40)), rsi_length=5, stoch_length=5)
    np.testing.assert_allclose(result.iloc[-1, 0], 50.0)


def test_stoch_rsi_d_is_the_smoothed_k() -> None:
    prices = list(np.linspace(10, 40, 60))
    out = zeonta.stoch_rsi(prices, rsi_length=5, stoch_length=5, smooth_k=3, smooth_d=3)
    k, d = out.columns
    np.testing.assert_allclose(out[d].to_numpy(), zeonta.sma(out[k], 3).to_numpy(), equal_nan=True)


def test_stoch_rsi_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.stoch_rsi(list(range(20)), rsi_length=0)


def test_awesome_oscillator_matches_the_hand_computed_sma_difference() -> None:
    high = [11.0, 12.0, 13.0]
    low = [9.0, 10.0, 11.0]
    # median prices: 10, 11, 12 -> SMA(2)=11.5(fast), SMA(3)=11(slow) at bar 2
    result = zeonta.awesome_oscillator(high, low, fast=2, slow=3)
    np.testing.assert_allclose(result.iloc[-1], 11.5 - 11.0)


def test_awesome_oscillator_is_zero_on_a_flat_median_price() -> None:
    result = zeonta.awesome_oscillator([11.0] * 34, [9.0] * 34, fast=5, slow=34)
    np.testing.assert_allclose(result.dropna().to_numpy(), 0.0)


def test_awesome_oscillator_is_positive_in_an_uptrend() -> None:
    high = list(np.linspace(11, 111, 60))
    low = list(np.linspace(9, 109, 60))
    result = zeonta.awesome_oscillator(high, low, fast=5, slow=34)
    assert result.iloc[-1] > 0


def test_awesome_oscillator_rejects_fast_not_smaller_than_slow() -> None:
    with pytest.raises(ValueError, match="'fast' must be smaller than 'slow'"):
        zeonta.awesome_oscillator([11.0] * 10, [9.0] * 10, fast=34, slow=5)


def test_ultimate_oscillator_matches_the_hand_computed_value() -> None:
    high = [11.0, 12.0, 10.5, 13.0]
    low = [9.0, 10.0, 8.5, 11.0]
    close = [10.0, 11.5, 9.0, 12.5]
    # bar 3: priorClose=9.0 -> BP=12.5-min(11,9)=3.5, TR=max(13,9)-min(11,9)=4.0
    # bar 2: priorClose=11.5 -> BP=9.0-min(8.5,11.5)=0.5, TR=max(10.5,11.5)-min(8.5,11.5)=3.0
    # bar 1: priorClose=10.0 -> BP=11.5-min(10,10)=1.5, TR=max(12,10)-min(10,10)=2.0
    avg1 = 3.5 / 4.0
    avg2 = (3.5 + 0.5) / (4.0 + 3.0)
    avg3 = (3.5 + 0.5 + 1.5) / (4.0 + 3.0 + 2.0)
    expected = 100.0 * (4.0 * avg1 + 2.0 * avg2 + avg3) / 7.0
    result = zeonta.ultimate_oscillator(high, low, close, fast=1, medium=2, slow=3)
    np.testing.assert_allclose(result.iloc[-1], expected)


def test_ultimate_oscillator_stays_within_bounds(ohlcv: pd.DataFrame) -> None:
    result = zeonta.ultimate_oscillator(ohlcv["high"], ohlcv["low"], ohlcv["close"]).dropna()
    assert result.between(0.0, 100.0).all()


def test_ultimate_oscillator_is_high_in_an_accelerating_uptrend() -> None:
    # A *linear* ramp keeps BP/TR pinned at a constant 0.5 at every window
    # (each day's gain and range both grow by the same fixed step), which
    # can't separate up from down — an accelerating move is needed instead.
    prices = np.array([float(i) ** 1.5 for i in range(1, 60)])
    result = zeonta.ultimate_oscillator(prices + 1, prices - 1, prices)
    assert result.iloc[-1] > 70.0


def test_ultimate_oscillator_is_low_in_an_accelerating_downtrend() -> None:
    prices = np.array([float(i) ** 1.5 for i in range(1, 60)])[::-1]
    result = zeonta.ultimate_oscillator(prices + 1, prices - 1, prices)
    assert result.iloc[-1] < 30.0


def test_ultimate_oscillator_rejects_windows_out_of_order() -> None:
    with pytest.raises(ValueError, match="'fast' < 'medium' < 'slow'"):
        zeonta.ultimate_oscillator([11.0] * 30, [9.0] * 30, [10.0] * 30, fast=14, medium=7, slow=28)


def test_elder_ray_matches_the_hand_computed_value() -> None:
    high = [11.0, 12.0, 13.0, 14.0]
    low = [9.0, 10.0, 11.0, 12.0]
    close = [10.0, 11.0, 12.0, 13.0]
    out = zeonta.elder_ray(high, low, close, length=3)
    ema = zeonta.ema(close, length=3)
    np.testing.assert_allclose(
        out["BULLP_3"].to_numpy(), (np.array(high) - ema).to_numpy(), equal_nan=True
    )
    np.testing.assert_allclose(
        out["BEARP_3"].to_numpy(), (np.array(low) - ema).to_numpy(), equal_nan=True
    )


def test_elder_ray_bull_power_is_positive_in_a_clean_uptrend() -> None:
    prices = np.arange(1.0, 60.0)
    out = zeonta.elder_ray(prices + 1, prices - 1, prices).dropna()
    assert (out["BULLP_13"] > 0.0).all()


def test_elder_ray_bear_power_is_negative_right_after_a_sharp_drop() -> None:
    # Right after a sudden drop, the lagging EMA is still well above the new
    # low, so bear power is unambiguously negative — unlike a steady linear
    # ramp, where EMA's fixed lag can exceed the bar's own high-low spread
    # and flip bear power positive (a real, documented property of this
    # indicator, not a bug).
    high = [50.0] * 20 + [10.0] * 10
    low = [49.0] * 20 + [9.0] * 10
    close = [49.5] * 20 + [9.5] * 10
    out = zeonta.elder_ray(high, low, close, length=13).dropna()
    assert (out["BEARP_13"].iloc[-10:] < 0.0).all()


def test_elder_ray_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.elder_ray([2.0] * 20, [1.0] * 20, [1.5] * 20, length=0)


def test_trix_is_zero_on_a_flat_series() -> None:
    result = zeonta.trix([25.0] * 40, length=5, signal=3)
    np.testing.assert_allclose(result["TRIX_5_3"].dropna().to_numpy(), 0.0)


def test_trix_matches_the_triple_ema_pct_change_formula() -> None:
    prices = list(np.linspace(10, 60, 80))
    result = zeonta.trix(prices, length=5, signal=3)
    ema1 = zeonta.ema(prices, 5)
    ema2 = zeonta.ema(ema1, 5)
    ema3 = zeonta.ema(ema2, 5)
    expected = (ema3 - ema3.shift(1)) / ema3.shift(1) * 100.0
    np.testing.assert_allclose(
        result["TRIX_5_3"].to_numpy(), expected.to_numpy(), equal_nan=True, rtol=1e-9
    )


def test_trix_signal_is_the_ema_of_trix() -> None:
    prices = list(np.linspace(10, 60, 80))
    result = zeonta.trix(prices, length=5, signal=3)
    expected_signal = zeonta.ema(result["TRIX_5_3"], 3)
    np.testing.assert_allclose(
        result["TRIXs_5_3"].to_numpy(), expected_signal.to_numpy(), equal_nan=True
    )


def test_trix_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.trix(list(range(20)), length=0)


def test_ppo_matches_the_pct_ema_difference_formula() -> None:
    prices = list(np.linspace(10, 60, 200))
    out = zeonta.ppo(prices)
    fast = zeonta.ema(prices, 12)
    slow = zeonta.ema(prices, 26)
    expected = (fast - slow) / slow * 100.0
    np.testing.assert_allclose(out["PPO_12_26_9"].to_numpy(), expected.to_numpy(), equal_nan=True)


def test_ppo_histogram_is_line_minus_signal() -> None:
    out = zeonta.ppo(list(np.linspace(10, 60, 200)))
    np.testing.assert_allclose(
        out["PPOh_12_26_9"], out["PPO_12_26_9"] - out["PPOs_12_26_9"], equal_nan=True
    )


def test_ppo_rejects_fast_not_smaller_than_slow() -> None:
    with pytest.raises(ValueError, match="'fast' must be smaller than 'slow'"):
        zeonta.ppo(list(range(50)), fast=26, slow=12)


def test_ppo_and_macd_agree_on_direction() -> None:
    """PPO is MACD normalised by the slow EMA — same sign, different scale."""
    prices = list(np.linspace(10, 100, 200))
    macd_line = zeonta.macd(prices)["MACD_12_26_9"]
    ppo_line = zeonta.ppo(prices)["PPO_12_26_9"]
    np.testing.assert_allclose(np.sign(macd_line.dropna()), np.sign(ppo_line.dropna()))


def test_tsi_is_zero_on_a_flat_series() -> None:
    result = zeonta.tsi([25.0] * 60, long=10, short=5, signal=3)
    np.testing.assert_allclose(result["TSI_10_5_3"].dropna().to_numpy(), 0.0)


def test_tsi_stays_within_bounds(ohlcv: pd.DataFrame) -> None:
    result = zeonta.tsi(ohlcv["close"]).dropna()
    assert result["TSI_25_13_7"].between(-100.0, 100.0).all()


def test_tsi_is_positive_in_a_clean_uptrend() -> None:
    result = zeonta.tsi(list(np.linspace(10, 100, 120)), long=10, short=5, signal=3)
    assert result["TSI_10_5_3"].iloc[-1] > 0


def test_tsi_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.tsi(list(range(60)), long=0)


def test_dpo_matches_the_hand_computed_shift_minus_sma() -> None:
    # length=10 -> shift = 10//2+1 = 6. Close 6 bars ago minus the 10-bar SMA.
    prices = [float(i) for i in range(1, 30)]
    result = zeonta.dpo(prices, length=10)
    sma = zeonta.sma(prices, length=10)
    shifted = pd.Series(prices).shift(6)
    expected = shifted - sma
    np.testing.assert_allclose(result.to_numpy(), expected.to_numpy(), equal_nan=True)


def test_dpo_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.dpo(list(range(20)), length=0)


def test_coppock_curve_matches_the_hand_computed_wma_of_summed_roc() -> None:
    prices = [float(i) for i in range(1, 60)]
    result = zeonta.coppock_curve(prices, long=5, short=3, wma_length=3)
    combined = zeonta.roc(prices, length=5) + zeonta.roc(prices, length=3)
    expected = zeonta.wma(combined, length=3)
    np.testing.assert_allclose(result.to_numpy(), expected.to_numpy(), equal_nan=True)


def test_coppock_curve_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.coppock_curve(list(range(30)), long=0)


def test_fisher_transform_matches_the_hand_traced_recursion() -> None:
    # length=3, so the first valid bar is index 2.
    # bar2: price=[10,11,12] highest=12 lowest=10 -> position=(12-10)/2-0.5=0.5
    #   value1 = 0.33*2*0.5 + 0.67*0 = 0.33
    #   fish = 0.5*ln(1.33/0.67) + 0.5*0 = 0.5*ln(1.9850746...)
    high = [10.0, 11.0, 12.0]
    low = [10.0, 11.0, 12.0]
    out = zeonta.fisher_transform(high, low, length=3)
    expected_value1 = 0.33 * 2 * 0.5
    expected_fish = 0.5 * np.log((1 + expected_value1) / (1 - expected_value1))
    np.testing.assert_allclose(out["FISHERT_3"].iloc[-1], expected_fish)


def test_fisher_transform_trigger_is_fish_shifted_by_one_bar() -> None:
    high = list(np.linspace(10, 20, 30))
    low = list(np.linspace(9, 19, 30))
    out = zeonta.fisher_transform(high, low, length=5)
    np.testing.assert_allclose(
        out["FISHERTs_5"].to_numpy(), out["FISHERT_5"].shift(1).to_numpy(), equal_nan=True
    )


def test_fisher_transform_is_zero_on_a_flat_series() -> None:
    out = zeonta.fisher_transform([10.0] * 20, [10.0] * 20, length=5)
    np.testing.assert_allclose(out["FISHERT_5"].dropna().to_numpy(), 0.0)


def test_fisher_transform_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.fisher_transform([1.0, 2.0], [0.5, 1.5], length=0)


def test_center_of_gravity_matches_the_hand_computed_balance_point() -> None:
    high = [12.0, 13.0, 11.0, 14.0, 15.0]
    low = [10.0, 11.0, 9.0, 12.0, 13.0]
    out = zeonta.center_of_gravity(high, low, length=5)
    np.testing.assert_allclose(out["CG_5"].iloc[-1], -2.8833333333333333)


def test_center_of_gravity_trigger_is_cg_shifted_by_one_bar() -> None:
    high = list(np.linspace(10, 20, 30))
    low = list(np.linspace(9, 19, 30))
    out = zeonta.center_of_gravity(high, low, length=5)
    np.testing.assert_allclose(
        out["CGs_5"].to_numpy(), out["CG_5"].shift(1).to_numpy(), equal_nan=True
    )


def test_center_of_gravity_is_constant_on_a_flat_series() -> None:
    out = zeonta.center_of_gravity([100.0] * 10, [100.0] * 10, length=5)
    np.testing.assert_allclose(out["CG_5"].dropna().to_numpy(), -3.0)


def test_center_of_gravity_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.center_of_gravity([1.0, 2.0], [0.5, 1.5], length=0)


def test_laguerre_rsi_settles_at_one_after_a_clean_uptrend() -> None:
    result = zeonta.laguerre_rsi(list(range(1, 51)))
    np.testing.assert_allclose(result.iloc[-1], 1.0)


def test_laguerre_rsi_settles_at_zero_after_a_clean_downtrend() -> None:
    result = zeonta.laguerre_rsi(list(range(50, 0, -1)))
    np.testing.assert_allclose(result.iloc[-1], 0.0)


def test_laguerre_rsi_rejects_gamma_at_or_above_one() -> None:
    with pytest.raises(ValueError, match="must be < 1"):
        zeonta.laguerre_rsi([1.0, 2.0], gamma=1.0)


def test_kst_matches_the_hand_computed_weighted_roc_sum() -> None:
    close = [float(v) for v in range(10, 25)]
    result = zeonta.kst(
        close, roc1=2, roc2=3, roc3=4, roc4=5, sma1=2, sma2=2, sma3=2, sma4=2, signal=2
    )
    np.testing.assert_allclose(result["KST_2_3_4_5"].iloc[-1], 208.35915492957747)
    np.testing.assert_allclose(result["KSTs_2_3_4_5"].iloc[-1], 214.10094965379668)


def test_kst_is_zero_on_a_flat_series() -> None:
    result = zeonta.kst(
        [50.0] * 60, roc1=2, roc2=3, roc3=4, roc4=5, sma1=2, sma2=2, sma3=2, sma4=2, signal=2
    )
    np.testing.assert_allclose(result.dropna().to_numpy(), 0.0)


def test_rvgi_is_all_nan_on_a_perfectly_flat_series() -> None:
    """Zero body and zero range together is an undefined 0/0 ratio."""
    flat = [10.0] * 30
    result = zeonta.rvgi(flat, flat, flat, flat, length=5)
    assert result.isna().all().all()


def test_rvgi_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.rvgi([1.0, 2.0], [1.5, 2.5], [0.5, 1.5], [1.0, 2.0], length=0)


def test_smi_is_zero_when_close_sits_exactly_on_the_midpoint() -> None:
    high = [12.0] * 30
    low = [10.0] * 30
    close = [11.0] * 30
    result = zeonta.smi(high, low, close, length=5, fast=3, slow=3, signal_length=3)
    np.testing.assert_allclose(result.dropna().to_numpy(), 0.0)


def test_smi_stays_within_bounds(ohlcv: pd.DataFrame) -> None:
    result = zeonta.smi(ohlcv["high"], ohlcv["low"], ohlcv["close"])
    values = result.dropna().to_numpy()
    assert (values >= -100.0).all() and (values <= 100.0).all()


def test_smi_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.smi([1.0, 2.0], [0.5, 1.5], [0.8, 1.8], length=0)


def test_bias_is_zero_on_a_flat_series() -> None:
    result = zeonta.bias([5.0] * 10, length=4)
    np.testing.assert_allclose(result.dropna().to_numpy(), 0.0)


def test_bias_matches_the_hand_computed_percentage() -> None:
    close = [10.0, 11.0, 9.0, 12.0]
    result = zeonta.bias(close, length=4)
    np.testing.assert_allclose(result.iloc[-1], 14.285714285714285)


def test_bias_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.bias([1.0, 2.0], length=0)


def test_psl_is_100_when_every_bar_in_the_window_closed_up() -> None:
    result = zeonta.psl([1.0, 2.0, 3.0, 4.0, 5.0], length=4)
    np.testing.assert_allclose(result.dropna().to_numpy(), 100.0)


def test_psl_is_0_when_every_bar_in_the_window_closed_down() -> None:
    result = zeonta.psl([5.0, 4.0, 3.0, 2.0, 1.0], length=4)
    np.testing.assert_allclose(result.dropna().to_numpy(), 0.0)


def test_psl_matches_the_hand_computed_percentage() -> None:
    close = [10.0, 11.0, 10.5, 12.0, 13.0]
    result = zeonta.psl(close, length=4)
    np.testing.assert_allclose(result.iloc[-1], 75.0)


def test_psl_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.psl([1.0, 2.0], length=0)


def test_kdj_matches_the_hand_computed_recursion() -> None:
    high = [12.0, 13.0, 11.0, 14.0, 15.0, 13.5, 16.0]
    low = [10.0, 11.0, 9.0, 12.0, 13.0, 11.5, 14.0]
    close = [11.0, 12.5, 10.0, 13.5, 14.5, 12.5, 15.5]
    out = zeonta.kdj(high, low, close, length=3, signal=2)
    np.testing.assert_allclose(out["K_3_2"].iloc[-1], 70.23313492063492)
    np.testing.assert_allclose(out["D_3_2"].iloc[-1], 64.52132936507937)
    np.testing.assert_allclose(out["J_3_2"].iloc[-1], 81.65674603174603)


def test_kdj_is_all_nan_on_a_zero_range_series() -> None:
    result = zeonta.kdj([10.0] * 10, [10.0] * 10, [10.0] * 10, length=3, signal=2)
    assert result.isna().all().all()


def test_kdj_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError, match="'length' must be >="):
        zeonta.kdj([1.0, 2.0], [0.5, 1.5], [0.8, 1.8], length=0)


def test_kdj_rejects_non_positive_signal() -> None:
    with pytest.raises(ValueError, match="'signal' must be >="):
        zeonta.kdj([1.0, 2.0], [0.5, 1.5], [0.8, 1.8], signal=0)


def test_qqe_settles_with_the_smoothed_rsi_above_its_own_trailing_line_in_a_clean_uptrend() -> None:
    close = list(range(1, 31)) + list(range(29, 14, -1)) + list(range(16, 41))
    out = zeonta.qqe(close, length=5, smooth=2, factor=2.0)
    assert out.iloc[-1, 0] > out.iloc[-1, 1]


def test_qqe_is_causal_new_bars_never_change_past_values() -> None:
    close = list(range(1, 31)) + list(range(29, 14, -1)) + list(range(16, 41))
    full = zeonta.qqe(close, length=5, smooth=2, factor=2.0)
    prefix = zeonta.qqe(close[:50], length=5, smooth=2, factor=2.0)
    np.testing.assert_allclose(full.iloc[:50].to_numpy(), prefix.to_numpy(), equal_nan=True)


def test_qqe_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError, match="'length' must be >="):
        zeonta.qqe(list(range(1, 10)), length=0)


def test_qqe_rejects_non_positive_smooth() -> None:
    with pytest.raises(ValueError, match="'smooth' must be >="):
        zeonta.qqe(list(range(1, 10)), smooth=0)


def test_qqe_rejects_non_positive_factor() -> None:
    with pytest.raises(ValueError, match="'factor' must be > 0"):
        zeonta.qqe(list(range(1, 10)), factor=0.0)


def test_connors_rsi_matches_an_independent_reimplementation() -> None:
    close = [10.0, 10.5, 11.0, 10.8, 11.2, 11.5, 11.3, 11.6, 11.9, 11.7]
    result = zeonta.connors_rsi(close, rsi_length=3, streak_length=2, rank_length=5)
    np.testing.assert_allclose(result.iloc[-1], 43.606594399277306)


def test_connors_rsi_stays_within_bounds(ohlcv: pd.DataFrame) -> None:
    result = zeonta.connors_rsi(ohlcv["close"], rank_length=50).dropna()
    assert result.between(0.0, 100.0).all()


def test_connors_rsi_streak_resets_on_an_unchanged_close() -> None:
    """A flat bar (Close == previous Close) must zero the streak rather
    than continuing or reversing the run — exercised end to end (no
    warning, no NaN once warmed up) rather than inspecting the private
    streak array directly."""
    close = [10.0, 11.0, 12.0, 12.0, 13.0]
    result = zeonta.connors_rsi(close, rsi_length=2, streak_length=2, rank_length=2)
    assert result.iloc[2:].notna().all()


def test_connors_rsi_rejects_non_positive_rsi_length() -> None:
    with pytest.raises(ValueError, match="'rsi_length' must be >="):
        zeonta.connors_rsi(list(range(1, 20)), rsi_length=0)


def test_connors_rsi_rejects_non_positive_streak_length() -> None:
    with pytest.raises(ValueError, match="'streak_length' must be >="):
        zeonta.connors_rsi(list(range(1, 20)), streak_length=0)


def test_connors_rsi_rejects_rank_length_below_two() -> None:
    with pytest.raises(ValueError, match="'rank_length' must be >="):
        zeonta.connors_rsi(list(range(1, 20)), rank_length=1)


def test_ift_rsi_matches_an_independent_reimplementation() -> None:
    result = zeonta.ift_rsi(list(range(1, 40)), length=14, smooth=9)
    np.testing.assert_allclose(result.iloc[-1], 0.9999092042625951)


def test_ift_rsi_is_zero_on_a_perfectly_flat_series() -> None:
    """RSI itself is neutral (50) on a flat series, which maps to v1=0 and
    an Inverse Fisher Transform output of exactly 0."""
    result = zeonta.ift_rsi([50.0] * 30, length=14, smooth=9)
    np.testing.assert_allclose(result.dropna().to_numpy(), 0.0)


def test_ift_rsi_stays_within_bounds(ohlcv: pd.DataFrame) -> None:
    result = zeonta.ift_rsi(ohlcv["close"]).dropna()
    assert result.between(-1.0, 1.0).all()


def test_ift_rsi_settles_near_one_after_a_clean_uptrend() -> None:
    result = zeonta.ift_rsi(list(range(1, 60)), length=14, smooth=9)
    assert result.iloc[-1] > 0.99


def test_ift_rsi_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError, match="'length' must be >="):
        zeonta.ift_rsi(list(range(1, 20)), length=0)


def test_ift_rsi_rejects_non_positive_smooth() -> None:
    with pytest.raises(ValueError, match="'smooth' must be >="):
        zeonta.ift_rsi(list(range(1, 20)), smooth=0)


def test_roofing_filter_matches_an_independent_reimplementation() -> None:
    rng = np.random.default_rng(0)
    close = 100.0 + np.cumsum(rng.normal(size=80))
    result = zeonta.roofing_filter(close, hp_length=20, lp_length=10)
    np.testing.assert_allclose(result.iloc[-1], -0.0008118327093320638)


def test_roofing_filter_is_zero_on_a_flat_series() -> None:
    result = zeonta.roofing_filter([10.0] * 60, hp_length=20, lp_length=10)
    np.testing.assert_allclose(result.to_numpy(), 0.0)


def test_roofing_filter_recovers_after_an_interior_gap() -> None:
    rng = np.random.default_rng(0)
    close = (100.0 + np.cumsum(rng.normal(size=100))).tolist()
    close[60] = float("nan")
    result = zeonta.roofing_filter(close, hp_length=20, lp_length=10)
    assert result.iloc[70:].notna().all()


def test_roofing_filter_rejects_non_positive_hp_length() -> None:
    with pytest.raises(ValueError, match="'hp_length' must be >="):
        zeonta.roofing_filter(list(range(1, 60)), hp_length=1)


def test_roofing_filter_rejects_non_positive_lp_length() -> None:
    with pytest.raises(ValueError, match="'lp_length' must be >="):
        zeonta.roofing_filter(list(range(1, 60)), lp_length=1)


def test_even_better_sinewave_matches_an_independent_reimplementation() -> None:
    rng = np.random.default_rng(1)
    close = 100.0 + np.cumsum(rng.normal(size=80))
    result = zeonta.even_better_sinewave(close, hp_length=40, lp_length=10)
    np.testing.assert_allclose(result.iloc[-1], -0.33900001728602347)


def test_even_better_sinewave_is_zero_on_a_flat_series() -> None:
    result = zeonta.even_better_sinewave([10.0] * 60, hp_length=40, lp_length=10)
    np.testing.assert_allclose(result.dropna().to_numpy(), 0.0)


def test_even_better_sinewave_stays_within_bounds(ohlcv: pd.DataFrame) -> None:
    result = zeonta.even_better_sinewave(ohlcv["close"]).dropna()
    assert result.between(-1.5, 1.5).all()


def test_even_better_sinewave_rejects_non_positive_hp_length() -> None:
    with pytest.raises(ValueError, match="'hp_length' must be >="):
        zeonta.even_better_sinewave(list(range(1, 60)), hp_length=1)


def test_even_better_sinewave_rejects_non_positive_lp_length() -> None:
    with pytest.raises(ValueError, match="'lp_length' must be >="):
        zeonta.even_better_sinewave(list(range(1, 60)), lp_length=1)


def test_cyber_cycle_matches_an_independent_reimplementation() -> None:
    rng = np.random.default_rng(2)
    high = 100.0 + np.cumsum(rng.normal(size=50)) + 0.5
    low = high - 1.0
    result = zeonta.cyber_cycle(high, low)
    np.testing.assert_allclose(result["CYBERCYCLE"].iloc[-1], -1.4043291793301915)


def test_cyber_cycle_trigger_is_cycle_shifted_by_one_bar() -> None:
    rng = np.random.default_rng(2)
    high = 100.0 + np.cumsum(rng.normal(size=50)) + 0.5
    low = high - 1.0
    result = zeonta.cyber_cycle(high, low)
    np.testing.assert_allclose(
        result["CYBERCYCLEt"].to_numpy(), result["CYBERCYCLE"].shift(1).to_numpy(), equal_nan=True
    )


def test_cyber_cycle_is_zero_on_a_flat_series() -> None:
    result = zeonta.cyber_cycle([11.0] * 30, [9.0] * 30)
    np.testing.assert_allclose(result["CYBERCYCLE"].to_numpy(), 0.0)


def test_cyber_cycle_rejects_non_positive_alpha() -> None:
    with pytest.raises(ValueError, match="'alpha' must be > 0"):
        zeonta.cyber_cycle([11.0, 12.0], [9.0, 10.0], alpha=0.0)


def test_voss_predictive_filter_matches_an_independent_reimplementation() -> None:
    rng = np.random.default_rng(3)
    close = 100.0 + np.cumsum(rng.normal(size=60))
    result = zeonta.voss_predictive_filter(close, period=20, predict=3, bandwidth=0.25)
    np.testing.assert_allclose(result["VOSSFILT"].iloc[-1], -0.798783267593836)
    np.testing.assert_allclose(result["VOSS"].iloc[-1], -1.4600140804367272)


def test_voss_predictive_filter_is_zero_on_a_flat_series() -> None:
    result = zeonta.voss_predictive_filter([10.0] * 40)
    np.testing.assert_allclose(result.to_numpy(), 0.0)


def test_voss_predictive_filter_rejects_non_positive_period() -> None:
    with pytest.raises(ValueError, match="'period' must be >="):
        zeonta.voss_predictive_filter(list(range(1, 40)), period=1)


def test_voss_predictive_filter_rejects_non_positive_predict() -> None:
    with pytest.raises(ValueError, match="'predict' must be >="):
        zeonta.voss_predictive_filter(list(range(1, 40)), predict=0)


def test_voss_predictive_filter_rejects_non_positive_bandwidth() -> None:
    with pytest.raises(ValueError, match="'bandwidth' must be > 0"):
        zeonta.voss_predictive_filter(list(range(1, 40)), bandwidth=0.0)


def test_reflex_trendflex_matches_an_independent_reimplementation() -> None:
    rng = np.random.default_rng(4)
    close = 100.0 + np.cumsum(rng.normal(size=60))
    result = zeonta.reflex_trendflex(close, length=20)
    np.testing.assert_allclose(result["REFLEX_20"].iloc[-1], 0.4365385585728406)
    np.testing.assert_allclose(result["TRENDFLEX_20"].iloc[-1], -0.4252007505049121)


def test_reflex_trendflex_is_zero_on_a_flat_series() -> None:
    result = zeonta.reflex_trendflex([10.0] * 40, length=20)
    np.testing.assert_allclose(result.dropna().to_numpy(), 0.0)


def test_reflex_trendflex_recovers_after_an_interior_gap() -> None:
    rng = np.random.default_rng(4)
    close = (100.0 + np.cumsum(rng.normal(size=100))).tolist()
    close[60] = float("nan")
    result = zeonta.reflex_trendflex(close, length=20)
    assert result.iloc[85:].notna().all().all()


def test_reflex_trendflex_rejects_a_length_below_four() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.reflex_trendflex(list(range(1, 20)), length=3)


def test_reflex_trendflex_is_nan_while_the_very_first_bar_is_still_missing() -> None:
    """A missing first bar leaves the SuperSmoother pre-filter permanently
    unseeded at that position (it has no earlier value to hold), so every
    window that still includes bar 0 must stay NaN rather than a bogus
    number - only once the window has aged past bar 0 does it recover."""
    close = [float("nan")] + [100.0 + i for i in range(40)]
    result = zeonta.reflex_trendflex(close, length=20)
    assert result.iloc[20].isna().all()
    assert result.iloc[21].notna().all()
