"""Trend systems.

SuperTrend and ADX carry recursive state, so these tests lean on invariants that
must hold on *every* bar rather than on a handful of spot values — a ratchet that
leaks backwards one bar in a thousand would slip past a spot check.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import zeonta


def _supertrend(frame: pd.DataFrame, **kwargs: object) -> pd.DataFrame:
    return zeonta.supertrend(frame["high"], frame["low"], frame["close"], **kwargs)


def test_supertrend_line_sits_below_price_in_an_uptrend(ohlcv: pd.DataFrame) -> None:
    out = _supertrend(ohlcv)
    line = out["SUPERT_10_3.0"]
    direction = out["SUPERTd_10_3.0"]
    up = direction == 1.0
    assert (line[up] <= ohlcv["close"][up]).all()


def test_supertrend_line_sits_above_price_in_a_downtrend(ohlcv: pd.DataFrame) -> None:
    out = _supertrend(ohlcv)
    line = out["SUPERT_10_3.0"]
    direction = out["SUPERTd_10_3.0"]
    down = direction == -1.0
    assert (line[down] >= ohlcv["close"][down]).all()


def test_supertrend_lower_band_only_ratchets_upward_within_an_uptrend(
    ohlcv: pd.DataFrame,
) -> None:
    """The one-way ratchet: while direction stays up, the line must never fall."""
    out = _supertrend(ohlcv)
    line = out["SUPERT_10_3.0"].to_numpy()
    direction = out["SUPERTd_10_3.0"].to_numpy()
    for i in range(1, len(line)):
        if direction[i] == 1.0 and direction[i - 1] == 1.0:
            assert line[i] >= line[i - 1] - 1e-12, f"lower band fell at bar {i}"
        if direction[i] == -1.0 and direction[i - 1] == -1.0:
            assert line[i] <= line[i - 1] + 1e-12, f"upper band rose at bar {i}"


def test_supertrend_direction_is_only_ever_plus_or_minus_one(ohlcv: pd.DataFrame) -> None:
    direction = _supertrend(ohlcv)["SUPERTd_10_3.0"].dropna()
    assert set(direction.unique()) <= {1.0, -1.0}


def test_supertrend_long_and_short_columns_partition_the_line(ohlcv: pd.DataFrame) -> None:
    out = _supertrend(ohlcv)
    long_line = out["SUPERTl_10_3.0"]
    short_line = out["SUPERTs_10_3.0"]
    assert not (long_line.notna() & short_line.notna()).any()
    combined = long_line.fillna(short_line)
    np.testing.assert_allclose(combined, out["SUPERT_10_3.0"], equal_nan=True)


def test_supertrend_higher_multiplier_flips_less_often(ohlcv: pd.DataFrame) -> None:
    def flips(multiplier: float) -> int:
        direction = _supertrend(ohlcv, multiplier=multiplier)["SUPERTd_10_" + str(multiplier)]
        return int((direction.diff() != 0).sum())

    assert flips(4.0) < flips(1.5)


def test_supertrend_never_flips_in_a_steady_uptrend() -> None:
    close = np.linspace(10, 200, 250)
    out = zeonta.supertrend(close + 1, close - 1, close)
    direction = out["SUPERTd_10_3.0"].dropna()
    assert (direction == 1.0).all()


def test_adx_is_high_in_a_clean_trend() -> None:
    prices = np.arange(1.0, 80.0)
    out = zeonta.adx(prices, prices - 1, prices)
    assert out["ADX_14"].iloc[-1] > 90
    assert out["DMP_14"].iloc[-1] > out["DMN_14"].iloc[-1]


def test_adx_reads_a_downtrend_as_strongly_as_an_uptrend() -> None:
    """ADX measures strength only; direction lives in the DI pair."""
    up = np.arange(1.0, 80.0)
    down = up[::-1].copy()
    up_adx = zeonta.adx(up, up - 1, up)["ADX_14"].iloc[-1]
    down_adx = zeonta.adx(down + 1, down, down)["ADX_14"].iloc[-1]
    assert up_adx == pytest.approx(down_adx, rel=0.05)
    assert zeonta.adx(down + 1, down, down)["DMN_14"].iloc[-1] > 0


def test_adx_is_low_in_a_choppy_range() -> None:
    close = np.tile([10.0, 10.5], 60)
    out = zeonta.adx(close + 0.2, close - 0.2, close)
    assert out["ADX_14"].iloc[-1] < 40


def test_adx_stays_within_bounds(ohlcv: pd.DataFrame) -> None:
    out = zeonta.adx(ohlcv["high"], ohlcv["low"], ohlcv["close"]).dropna()
    assert out.to_numpy().min() >= 0.0
    assert out.to_numpy().max() <= 100.0


def test_adx_needs_roughly_twice_the_length_to_warm_up(ohlcv: pd.DataFrame) -> None:
    out = zeonta.adx(ohlcv["high"], ohlcv["low"], ohlcv["close"], length=14)
    first = out["ADX_14"].first_valid_index()
    assert out.index.get_loc(first) >= 27


def test_ichimoku_lines_are_midpoints_of_their_windows(ohlcv: pd.DataFrame) -> None:
    visible, _ = zeonta.ichimoku(ohlcv["high"], ohlcv["low"], ohlcv["close"])
    expected = (ohlcv["high"].rolling(9).max() + ohlcv["low"].rolling(9).min()) / 2
    np.testing.assert_allclose(visible["ITS_9"], expected, equal_nan=True)


def test_ichimoku_cloud_is_shifted_forward(ohlcv: pd.DataFrame) -> None:
    visible, forward = zeonta.ichimoku(ohlcv["high"], ohlcv["low"], ohlcv["close"])
    tenkan = visible["ITS_9"]
    kijun = visible["IKS_26"]
    unshifted = (tenkan + kijun) / 2
    np.testing.assert_allclose(visible["ISA_9_26"].iloc[26:], unshifted.iloc[:-26], equal_nan=True)
    assert len(forward) == 26


def test_ichimoku_forward_cloud_continues_past_the_last_bar(ohlcv: pd.DataFrame) -> None:
    """The projected cloud must be returned, not silently dropped."""
    _, forward = zeonta.ichimoku(ohlcv["high"], ohlcv["low"], ohlcv["close"])
    assert list(forward.columns) == ["ISA_9_26", "ISB_52"]
    assert len(forward) == 26
    assert forward.notna().all().all()


def test_ichimoku_forward_cloud_continues_real_dates_on_a_datetime_index(
    ohlcv: pd.DataFrame,
) -> None:
    """A regularly spaced DatetimeIndex should project as real future dates,
    not an arbitrary integer offset, so it concatenates onto a date chart."""
    _, forward = zeonta.ichimoku(ohlcv["high"], ohlcv["low"], ohlcv["close"])
    assert isinstance(forward.index, pd.DatetimeIndex)
    assert forward.index[0] == ohlcv.index[-1] + pd.Timedelta(days=1)
    assert (forward.index.to_series().diff().dropna() == pd.Timedelta(days=1)).all()


def test_ichimoku_forward_cloud_falls_back_to_integers_without_a_datetime_index() -> None:
    """No index (or a non-DatetimeIndex) must not crash; it degrades to a
    plain integer continuation of the input's length."""
    prices = [float(i) for i in range(1, 120)]
    _, forward = zeonta.ichimoku(prices, [p - 1 for p in prices], prices)
    assert isinstance(forward.index, pd.RangeIndex)
    assert forward.index[0] == len(prices)
    assert len(forward) == 26


def test_ichimoku_chikou_is_shifted_backward(ohlcv: pd.DataFrame) -> None:
    visible, _ = zeonta.ichimoku(ohlcv["high"], ohlcv["low"], ohlcv["close"])
    np.testing.assert_allclose(
        visible["ICS_26"].iloc[:-26], ohlcv["close"].iloc[26:], equal_nan=True
    )
    assert visible["ICS_26"].iloc[-26:].isna().all()


def test_donchian_brackets_price(ohlcv: pd.DataFrame) -> None:
    out = zeonta.donchian(ohlcv["high"], ohlcv["low"], length=20).dropna()
    highs = ohlcv["high"].loc[out.index]
    lows = ohlcv["low"].loc[out.index]
    assert (out["DCU_20"] >= highs).all()
    assert (out["DCL_20"] <= lows).all()


def test_donchian_middle_is_the_channel_midpoint() -> None:
    out = zeonta.donchian([3, 4, 5], [1, 2, 3], length=2)
    np.testing.assert_allclose(out.iloc[-1].to_numpy(), [2.0, 3.5, 5.0])


def _psar(frame: pd.DataFrame, **kwargs: object) -> pd.DataFrame:
    return zeonta.parabolic_sar(frame["high"], frame["low"], **kwargs)


def test_psar_never_flips_when_price_only_ever_rises() -> None:
    high = np.linspace(10, 200, 250) + 1
    low = np.linspace(10, 200, 250) - 1
    out = zeonta.parabolic_sar(high, low)
    direction = out["PSARd_0.02_0.02_0.2"].dropna()
    assert (direction == 1.0).all()


def test_psar_stays_below_the_low_on_continuation_bars_in_an_uptrend(
    ohlcv: pd.DataFrame,
) -> None:
    """The reversal bar itself is exempt: SAR there is set to the old extreme
    point, which is not guaranteed to respect the reversal bar's own low —
    a documented quirk of the classic algorithm, not a bug."""
    out = _psar(ohlcv)
    line = out["PSAR_0.02_0.02_0.2"].to_numpy()
    direction = out["PSARd_0.02_0.02_0.2"].to_numpy()
    low = ohlcv["low"].to_numpy()
    for i in range(2, len(direction)):
        if direction[i] == 1.0 and direction[i - 1] == 1.0:
            assert line[i] <= low[i] + 1e-9, f"bar {i}"


def test_psar_stays_above_the_high_on_continuation_bars_in_a_downtrend(
    ohlcv: pd.DataFrame,
) -> None:
    out = _psar(ohlcv)
    line = out["PSAR_0.02_0.02_0.2"].to_numpy()
    direction = out["PSARd_0.02_0.02_0.2"].to_numpy()
    high = ohlcv["high"].to_numpy()
    for i in range(2, len(direction)):
        if direction[i] == -1.0 and direction[i - 1] == -1.0:
            assert line[i] >= high[i] - 1e-9, f"bar {i}"


def test_psar_direction_is_only_ever_plus_or_minus_one(ohlcv: pd.DataFrame) -> None:
    direction = _psar(ohlcv)["PSARd_0.02_0.02_0.2"].dropna()
    assert set(direction.unique()) <= {1.0, -1.0}


def test_psar_long_and_short_columns_partition_the_line(ohlcv: pd.DataFrame) -> None:
    out = _psar(ohlcv)
    long_line = out["PSARl_0.02_0.02_0.2"]
    short_line = out["PSARs_0.02_0.02_0.2"]
    assert not (long_line.notna() & short_line.notna()).any()
    combined = long_line.fillna(short_line)
    np.testing.assert_allclose(combined, out["PSAR_0.02_0.02_0.2"], equal_nan=True)


def test_psar_first_bar_has_no_prior_bar_to_seed_from(ohlcv: pd.DataFrame) -> None:
    out = _psar(ohlcv)
    assert out.iloc[0].isna().all()


def test_psar_higher_start_af_flips_less_often(ohlcv: pd.DataFrame) -> None:
    """A larger starting acceleration factor pulls SAR toward price faster,
    so it should cross (and therefore flip) more readily — check the two
    extremes rather than assuming monotonicity in between."""

    def flips(start: float) -> int:
        direction = _psar(ohlcv, start=start, increment=start)[f"PSARd_{start}_{start}_0.2"]
        return int((direction.diff() != 0).sum())

    assert flips(0.2) > flips(0.01)


def test_psar_rejects_non_positive_start() -> None:
    with pytest.raises(ValueError, match="'start' must be > 0"):
        zeonta.parabolic_sar([2.0] * 10, [1.0] * 10, start=0.0)


def test_psar_rejects_start_greater_than_max_af() -> None:
    with pytest.raises(ValueError, match="'start' must be <= 'max_af'"):
        zeonta.parabolic_sar([2.0] * 10, [1.0] * 10, start=0.3, max_af=0.2)


def test_psar_accepts_start_equal_to_max_af() -> None:
    """The boundary itself is valid: AF simply never grows past its start."""
    out = zeonta.parabolic_sar([2.0] * 20, [1.0] * 20, start=0.2, max_af=0.2)
    assert out.notna().any().any()


def test_psar_gap_bar_is_nan_and_state_freezes_across_it() -> None:
    high = [2.0] * 20
    low = [1.0] * 20
    high[10] = float("nan")
    out = zeonta.parabolic_sar(high, low)
    line = out["PSAR_0.02_0.02_0.2"]
    direction = out["PSARd_0.02_0.02_0.2"]
    assert np.isnan(line.iloc[10])
    assert np.isnan(direction.iloc[10])
    # Every bar after the gap must still be computable — the algorithm picks
    # back up rather than propagating NaN forever.
    assert line.iloc[11:].notna().all()
    assert direction.iloc[11:].notna().all()


def test_psar_gap_bar_does_not_silently_produce_a_finite_value() -> None:
    """Python's builtin min/max ignore NaN in comparisons, so a naive clamp
    against a gap bar's low/high could silently keep a wrong finite number
    instead of surfacing the missing data — this pins that it does not."""
    high = np.array([2.0] * 30)
    low = np.array([1.0] * 30)
    low[15] = np.nan
    out = zeonta.parabolic_sar(high, low)
    assert np.isnan(out["PSAR_0.02_0.02_0.2"].iloc[15])


def test_aroon_matches_the_hand_computed_example() -> None:
    out = zeonta.aroon([1, 2, 5, 2, 1], [0, 1, 4, 1, 0], length=4)
    np.testing.assert_allclose(out.iloc[-1].to_numpy(), [50.0, 100.0, -50.0])


def test_aroon_warmup_is_exactly_the_length() -> None:
    # The window scanned is length+1 bars (today plus `length` back), so the
    # first `length` bars (not length-1) cannot form a full window.
    out = zeonta.aroon(list(range(20)), list(range(-1, 19)), length=5)
    assert int(out["AROONU_5"].isna().sum()) == 5


def test_aroon_up_is_100_when_today_is_the_highest_high() -> None:
    out = zeonta.aroon(list(range(1, 30)), [x - 1 for x in range(1, 30)], length=10)
    np.testing.assert_allclose(out["AROONU_10"].iloc[-1], 100.0)


def test_aroon_down_is_100_when_today_is_the_lowest_low() -> None:
    high = list(range(30, 1, -1))
    low = [x - 1 for x in high]
    out = zeonta.aroon(high, low, length=10)
    np.testing.assert_allclose(out["AROOND_10"].iloc[-1], 100.0)


def test_aroon_oscillator_is_up_minus_down() -> None:
    out = zeonta.aroon([3, 1, 4, 1, 5, 9, 2, 6], [1, 0, 2, 0, 3, 7, 1, 4], length=4)
    np.testing.assert_allclose(
        out["AROONOSC_4"].to_numpy(),
        (out["AROONU_4"] - out["AROOND_4"]).to_numpy(),
        equal_nan=True,
    )


def test_aroon_stays_within_bounds(ohlcv: pd.DataFrame) -> None:
    out = zeonta.aroon(ohlcv["high"], ohlcv["low"]).dropna()
    assert out["AROONU_25"].between(0.0, 100.0).all()
    assert out["AROOND_25"].between(0.0, 100.0).all()
    assert out["AROONOSC_25"].between(-100.0, 100.0).all()


def test_aroon_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.aroon([1.0, 2.0, 3.0], [0.0, 1.0, 2.0], length=0)


def test_aroon_is_nan_while_a_gap_bar_sits_inside_the_window() -> None:
    """argmax/argmin have no real concept of NaN: a NaN in the window
    compares False against every other value, so it is silently treated as
    the running extreme instead of being excluded — producing a
    finite-looking but meaningless "days since" figure. Every window that
    has not fully aged the gap out must be NaN instead."""
    high = [1.0, 2.0, 5.0, np.nan, 1.0, 3.0, 2.0]
    low = [0.0, 1.0, 4.0, np.nan, 0.0, 2.0, 1.0]
    out = zeonta.aroon(high, low, length=4)
    # window = length + 1 = 5 bars; the gap at index 3 is inside every
    # window through index 7, all of which are out of range for this
    # 7-bar input, so the whole tail after warm-up must stay NaN.
    assert out.iloc[4:].isna().all().all()


def test_aroon_recovers_once_the_gap_bar_ages_out_of_the_window() -> None:
    high = [1.0, 2.0, 5.0, np.nan, 1.0, 3.0, 2.0, 4.0, 3.0]
    low = [0.0, 1.0, 4.0, np.nan, 0.0, 2.0, 1.0, 3.0, 2.0]
    out = zeonta.aroon(high, low, length=4)
    # window at index 8 covers indices 4..8, clear of the index-3 gap.
    assert out.iloc[8].notna().all()


def test_chandelier_exit_long_is_highest_high_minus_multiplier_times_atr(
    ohlcv: pd.DataFrame,
) -> None:
    out = zeonta.chandelier_exit(ohlcv["high"], ohlcv["low"], ohlcv["close"], length=22)
    highest = ohlcv["high"].rolling(22).max()
    atr = zeonta.atr(ohlcv["high"], ohlcv["low"], ohlcv["close"], length=22)
    expected = highest - 3.0 * atr
    np.testing.assert_allclose(out["CELONG_22_3.0"].to_numpy(), expected.to_numpy(), equal_nan=True)


def test_chandelier_exit_short_is_lowest_low_plus_multiplier_times_atr(
    ohlcv: pd.DataFrame,
) -> None:
    out = zeonta.chandelier_exit(ohlcv["high"], ohlcv["low"], ohlcv["close"], length=22)
    lowest = ohlcv["low"].rolling(22).min()
    atr = zeonta.atr(ohlcv["high"], ohlcv["low"], ohlcv["close"], length=22)
    expected = lowest + 3.0 * atr
    np.testing.assert_allclose(
        out["CESHORT_22_3.0"].to_numpy(), expected.to_numpy(), equal_nan=True
    )


def test_chandelier_exit_long_sits_at_or_below_the_recent_high(ohlcv: pd.DataFrame) -> None:
    out = zeonta.chandelier_exit(ohlcv["high"], ohlcv["low"], ohlcv["close"]).dropna()
    highest = ohlcv["high"].rolling(22).max().loc[out.index]
    assert (out["CELONG_22_3.0"] <= highest).all()


def test_chandelier_exit_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.chandelier_exit([2.0] * 30, [1.0] * 30, [1.5] * 30, length=0)


def test_vortex_matches_the_hand_computed_example() -> None:
    high = [12.0, 13.0, 11.0, 14.0]
    low = [10.0, 11.0, 9.0, 12.0]
    close = [11.0, 12.0, 10.0, 13.0]
    out = zeonta.vortex(high, low, close, length=3)
    np.testing.assert_allclose(out.iloc[-1].to_numpy(), [8.0 / 9.0, 2.0 / 3.0])


def test_vortex_plus_leads_in_a_clean_uptrend() -> None:
    prices = np.arange(1.0, 60.0)
    out = zeonta.vortex(prices + 1, prices - 1, prices, length=14).dropna()
    assert (out["VTXP_14"] > out["VTXM_14"]).all()


def test_vortex_minus_leads_in_a_clean_downtrend() -> None:
    prices = np.arange(60.0, 1.0, -1.0)
    out = zeonta.vortex(prices + 1, prices - 1, prices, length=14).dropna()
    assert (out["VTXM_14"] > out["VTXP_14"]).all()


def test_vortex_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.vortex([2.0] * 20, [1.0] * 20, [1.5] * 20, length=0)
