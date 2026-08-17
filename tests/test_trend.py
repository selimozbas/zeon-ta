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
