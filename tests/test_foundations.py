"""Foundations: candle anatomy, pivots, regression channels and volume."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import zeonta


def test_candle_geometry_adds_up(ohlcv: pd.DataFrame) -> None:
    out = zeonta.candles(ohlcv["open"], ohlcv["high"], ohlcv["low"], ohlcv["close"])
    reconstructed = out["CDLBODY"] + out["CDLUPPER"] + out["CDLLOWER"]
    np.testing.assert_allclose(reconstructed, out["CDLRANGE"], atol=1e-9)


def test_candle_wicks_are_never_negative(ohlcv: pd.DataFrame) -> None:
    out = zeonta.candles(ohlcv["open"], ohlcv["high"], ohlcv["low"], ohlcv["close"])
    assert (out["CDLUPPER"] >= -1e-12).all()
    assert (out["CDLLOWER"] >= -1e-12).all()


def test_doji_is_flagged_when_the_body_is_tiny() -> None:
    out = zeonta.candles([10, 10], [11, 11], [9, 9], [10.05, 10.9])
    assert out["CDLDOJI"].tolist() == [1.0, 0.0]


def test_bullish_engulfing_is_detected() -> None:
    # bar 0 bearish 10 -> 9; bar 1 bullish 8.9 -> 10.2 swallowing it whole
    out = zeonta.candles([10, 8.9], [10.2, 10.3], [8.8, 8.8], [9, 10.2])
    assert out["CDLENG"].iloc[1] == 1.0


def test_bearish_engulfing_is_detected() -> None:
    out = zeonta.candles([9, 10.3], [10.4, 10.5], [8.8, 8.7], [10, 8.9])
    assert out["CDLENG"].iloc[1] == -1.0


def test_engulfing_is_undefined_on_the_first_bar() -> None:
    out = zeonta.candles([10, 9], [11, 11], [9, 8], [10.5, 10.5])
    assert np.isnan(out["CDLENG"].iloc[0])


def test_hammer_and_shooting_star_have_opposite_signs() -> None:
    hammer = zeonta.candles([10.0], [10.2], [8.0], [10.1])
    star = zeonta.candles([10.0], [12.0], [9.9], [10.1])
    assert hammer["CDLHAM"].iloc[0] == 1.0
    assert star["CDLHAM"].iloc[0] == -1.0


def test_pivot_high_needs_bars_on_both_sides() -> None:
    highs = [1, 2, 5, 2, 1, 2, 1]
    out = zeonta.support_resistance(highs, [h - 1 for h in highs], left=2, right=2)
    pivots = out["PIVOTHIGH_2_2"]
    assert pivots.iloc[2] == 5.0
    assert pivots.drop(index=pivots.index[2]).isna().all()


def test_resistance_is_delayed_until_the_pivot_is_confirmable() -> None:
    """The causal column must not know about a pivot before its right bars print."""
    highs = [1, 2, 5, 2, 1, 2, 1]
    out = zeonta.support_resistance(highs, [h - 1 for h in highs], left=2, right=2)
    resistance = out["RES_2_2"]
    assert resistance.iloc[:4].isna().all()
    assert resistance.iloc[4] == 5.0


def test_pivots_require_a_strict_extreme() -> None:
    """A plateau is not a pivot — otherwise flat data produces phantom levels."""
    highs = [1, 5, 5, 5, 1]
    out = zeonta.support_resistance(highs, [h - 1 for h in highs], left=1, right=1)
    assert out["PIVOTHIGH_1_1"].isna().all()


def test_sr_levels_merges_nearby_pivots_and_ranks_by_touches() -> None:
    highs = [1, 2, 5, 2, 1, 2, 5.01, 2, 1]
    levels = zeonta.sr_levels(highs, [h - 1 for h in highs], left=2, right=2, tolerance=0.01)
    assert levels.iloc[0]["touches"] == 2
    assert levels.iloc[0]["level"] == pytest.approx(5.005)


def test_sr_levels_respects_max_levels(ohlcv: pd.DataFrame) -> None:
    levels = zeonta.sr_levels(ohlcv["high"], ohlcv["low"], left=3, right=3, max_levels=4)
    assert len(levels) <= 4
    assert list(levels.columns) == ["level", "touches", "kind"]


def test_trend_channel_recovers_a_known_slope() -> None:
    out = zeonta.trend_channel([float(i) for i in range(50)], length=10)
    np.testing.assert_allclose(out["LRCSLOPE_10"].iloc[-1], 1.0)
    np.testing.assert_allclose(out["LRCM_10"].iloc[-1], 49.0)


def test_trend_channel_slope_is_negative_in_a_downtrend() -> None:
    out = zeonta.trend_channel(list(np.linspace(100, 10, 60)), length=20)
    assert out["LRCSLOPE_20"].iloc[-1] < 0


def test_trend_channel_bands_bracket_the_line(ohlcv: pd.DataFrame) -> None:
    out = zeonta.trend_channel(ohlcv["close"], length=50).dropna()
    assert (out["LRCU_50"] >= out["LRCM_50"]).all()
    assert (out["LRCL_50"] <= out["LRCM_50"]).all()


def test_trend_channel_needs_at_least_two_bars() -> None:
    with pytest.raises(ValueError, match="must be >= 2"):
        zeonta.trend_channel(list(range(20)), length=1)


def test_relative_volume_is_one_on_a_constant_series() -> None:
    out = zeonta.relative_volume([1000.0] * 40, length=20)
    np.testing.assert_allclose(out["RVOL_20"].iloc[-1], 1.0)


def test_relative_volume_matches_the_hand_computed_ratio() -> None:
    # average over the last 20 bars = (19*100 + 200)/20 = 105 ; 200/105 = 1.9047...
    out = zeonta.relative_volume([100.0] * 19 + [200.0], length=20)
    np.testing.assert_allclose(out["RVOL_20"].iloc[-1], 200 / 105)


def test_relative_volume_is_undefined_when_nothing_traded() -> None:
    out = zeonta.relative_volume([0.0] * 25, length=20)
    assert out["RVOL_20"].isna().all()
