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


def test_trend_channel_bands_collapse_on_a_perfectly_linear_series() -> None:
    """Bands measure scatter about the trend line, so a straight line has none.

    Using the deviation about the window *mean* instead would give a wide
    channel here, which is backwards: the more perfectly price follows the
    trend, the tighter the channel should be.
    """
    out = zeonta.trend_channel([float(i) for i in range(60)], length=20)
    last = out.iloc[-1]
    np.testing.assert_allclose(last["LRCU_20"], last["LRCM_20"], atol=1e-9)
    np.testing.assert_allclose(last["LRCL_20"], last["LRCM_20"], atol=1e-9)


def test_trend_channel_widens_with_scatter_around_the_trend() -> None:
    rng = np.random.default_rng(3)
    trend = np.linspace(0, 100, 200)
    quiet = zeonta.trend_channel(trend + rng.normal(0, 0.1, 200), length=30)
    noisy = zeonta.trend_channel(trend + rng.normal(0, 5.0, 200), length=30)
    quiet_width = quiet["LRCU_30"].iloc[-1] - quiet["LRCL_30"].iloc[-1]
    noisy_width = noisy["LRCU_30"].iloc[-1] - noisy["LRCL_30"].iloc[-1]
    assert noisy_width > 10 * quiet_width


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


def test_relative_volume_rejects_negative_volume() -> None:
    with pytest.raises(ValueError, match="'volume' must not contain negative values"):
        zeonta.relative_volume([100.0, -1.0, 100.0], length=2)


def test_heikin_ashi_matches_the_hand_computed_recursion() -> None:
    open_ = [10.0, 11.0, 10.5, 12.0]
    high = [12.0, 13.0, 11.5, 14.0]
    low = [9.0, 10.0, 9.5, 11.0]
    close = [11.0, 10.5, 11.2, 13.5]
    out = zeonta.heikin_ashi(open_, high, low, close)
    np.testing.assert_allclose(out["HAclose"].to_numpy(), [10.5, 11.125, 10.675, 12.625])
    np.testing.assert_allclose(out["HAopen"].iloc[0], 10.5)


def test_heikin_ashi_high_and_low_bracket_open_and_close() -> None:
    open_ = [10.0, 11.0, 10.5, 12.0]
    high = [12.0, 13.0, 11.5, 14.0]
    low = [9.0, 10.0, 9.5, 11.0]
    close = [11.0, 10.5, 11.2, 13.5]
    out = zeonta.heikin_ashi(open_, high, low, close)
    assert (out["HAhigh"] >= out[["HAopen", "HAclose"]].max(axis=1)).all()
    assert (out["HAlow"] <= out[["HAopen", "HAclose"]].min(axis=1)).all()


def test_heikin_ashi_is_never_nan_for_finite_input() -> None:
    out = zeonta.heikin_ashi([10.0] * 10, [11.0] * 10, [9.0] * 10, [10.0] * 10)
    assert out.notna().all().all()


def test_heikin_ashi_holds_the_prior_open_through_a_gap() -> None:
    """A fully missing bar has no *own* open to compute (its HAclose is
    NaN), so the bar right after it freezes at the gap bar's HAopen
    instead of advancing the recursion — the gap-freeze convention this
    library applies elsewhere, adapted to a value with no fixed window."""
    open_ = [10.0, 11.0, np.nan, 12.0]
    high = [12.0, 13.0, np.nan, 14.0]
    low = [9.0, 10.0, np.nan, 11.0]
    close = [11.0, 10.5, np.nan, 13.5]
    out = zeonta.heikin_ashi(open_, high, low, close)
    assert out["HAclose"].iloc[2:].isna().to_numpy().tolist() == [True, False]
    assert out["HAopen"].iloc[3] == out["HAopen"].iloc[2]


def test_williams_fractals_matches_the_hand_computed_pivots() -> None:
    high = [10.0, 11.0, 15.0, 11.0, 10.0]
    low = [8.0, 7.0, 6.0, 7.0, 8.0]
    out = zeonta.williams_fractals(high, low)
    np.testing.assert_allclose(out["FRACTALB"].iloc[2], 15.0)
    np.testing.assert_allclose(out["FRACTALU"].iloc[2], 6.0)
    assert out["FRACTALB"].drop(index=2).isna().all()
    assert out["FRACTALU"].drop(index=2).isna().all()


def test_williams_fractals_matches_support_resistance_at_left_right_two() -> None:
    """Williams Fractals is exactly support_resistance's own pivot test at
    left=right=2, just reported without the forward shift/hold."""
    rng = np.random.default_rng(0)
    high = 100.0 + np.cumsum(rng.normal(size=60))
    low = high - rng.uniform(0.5, 2.0, size=60)
    fractals = zeonta.williams_fractals(high, low)
    pivots = zeonta.support_resistance(high, low, left=2, right=2)
    np.testing.assert_allclose(
        fractals["FRACTALB"].to_numpy(), pivots["PIVOTHIGH_2_2"].to_numpy(), equal_nan=True
    )
    np.testing.assert_allclose(
        fractals["FRACTALU"].to_numpy(), pivots["PIVOTLOW_2_2"].to_numpy(), equal_nan=True
    )


def test_williams_fractals_is_nan_when_no_pivot_qualifies() -> None:
    result = zeonta.williams_fractals([10.0] * 10, [9.0] * 10)
    assert result.isna().all().all()


def test_williams_fractals_needs_at_least_five_bars() -> None:
    result = zeonta.williams_fractals([10.0, 11.0, 12.0], [8.0, 9.0, 10.0])
    assert result.isna().all().all()
