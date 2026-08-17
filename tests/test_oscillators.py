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
