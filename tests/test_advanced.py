"""Advanced tools: VWAP, Fibonacci, pivot points and divergences."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import zeonta


def test_vwap_equals_the_volume_weighted_mean_of_typical_price() -> None:
    index = pd.date_range("2024-01-01", periods=4, freq="h")
    high = pd.Series([2.0, 3.0, 4.0, 5.0], index=index)
    low = pd.Series([1.0, 2.0, 3.0, 4.0], index=index)
    close = pd.Series([1.5, 2.5, 3.5, 4.5], index=index)
    volume = pd.Series([10.0] * 4, index=index)
    out = zeonta.vwap(high, low, close, volume)
    # Typical prices are 1.5, 2.5, 3.5, 4.5 with equal volume -> plain mean.
    np.testing.assert_allclose(out.iloc[-1, 0], 3.0)


def test_vwap_resets_at_each_session() -> None:
    index = pd.DatetimeIndex(
        ["2024-01-01 09:00", "2024-01-01 10:00", "2024-01-02 09:00", "2024-01-02 10:00"]
    )
    price = pd.Series([10.0, 20.0, 100.0, 200.0], index=index)
    volume = pd.Series([1.0] * 4, index=index)
    out = zeonta.vwap(price, price, price, volume, anchor="session")
    # Second session starts over rather than dragging the first session's average along.
    np.testing.assert_allclose(out.iloc[2, 0], 100.0)
    np.testing.assert_allclose(out.iloc[3, 0], 150.0)


def test_vwap_weights_high_volume_bars_more() -> None:
    index = pd.date_range("2024-01-01", periods=2, freq="h")
    price = pd.Series([10.0, 20.0], index=index)
    volume = pd.Series([1.0, 9.0], index=index)
    out = zeonta.vwap(price, price, price, volume)
    np.testing.assert_allclose(out.iloc[-1, 0], (10 * 1 + 20 * 9) / 10)


def test_vwap_session_anchor_requires_a_datetime_index(ohlcv: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="DatetimeIndex"):
        zeonta.vwap(
            ohlcv["high"].to_numpy(),
            ohlcv["low"].to_numpy(),
            ohlcv["close"].to_numpy(),
            ohlcv["volume"].to_numpy(),
            anchor="session",
        )


def test_vwap_rolling_anchor_works_without_an_index(ohlcv: pd.DataFrame) -> None:
    out = zeonta.vwap(
        ohlcv["high"].to_numpy(),
        ohlcv["low"].to_numpy(),
        ohlcv["close"].to_numpy(),
        ohlcv["volume"].to_numpy(),
        anchor="rolling",
        length=20,
    )
    assert out["VWAP_rolling_20"].notna().sum() == len(ohlcv) - 19


def test_vwap_bands_bracket_the_average(ohlcv: pd.DataFrame) -> None:
    out = zeonta.vwap(
        ohlcv["high"], ohlcv["low"], ohlcv["close"], ohlcv["volume"], anchor="rolling"
    ).dropna()
    assert (out["VWAPU_rolling_20"] >= out["VWAP_rolling_20"]).all()
    assert (out["VWAPL_rolling_20"] <= out["VWAP_rolling_20"]).all()


def test_vwap_rejects_unknown_anchor(ohlcv: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="'anchor' must be"):
        zeonta.vwap(ohlcv["high"], ohlcv["low"], ohlcv["close"], ohlcv["volume"], anchor="weekly")


def test_vwap_rejects_negative_volume(ohlcv: pd.DataFrame) -> None:
    """Negative volume is nonsensical and would otherwise surface only as a
    silent NaN once a window's net volume happened to cross zero."""
    volume = ohlcv["volume"].copy()
    volume.iloc[10] = -1.0
    with pytest.raises(ValueError, match="'volume' must not contain negative values"):
        zeonta.vwap(ohlcv["high"], ohlcv["low"], ohlcv["close"], volume)


def test_fib_levels_sit_between_the_swing_extremes() -> None:
    out = zeonta.fib_retracement([1, 2, 3, 4, 5], [0, 1, 2, 3, 4], lookback=5)
    last = out.iloc[-1]
    assert last["FIBDIR"] == 1.0
    # Up-swing: high 5, low 0, span 5 -> 0.618 level = 5 - 5*0.618
    np.testing.assert_allclose(last["FIB_0.618"], 5 - 5 * 0.618)
    np.testing.assert_allclose(last["FIB_0"], 5.0)
    np.testing.assert_allclose(last["FIB_1"], 0.0)


def test_fib_direction_flips_on_a_down_swing() -> None:
    highs = [5, 4, 3, 2, 1]
    lows = [4, 3, 2, 1, 0]
    out = zeonta.fib_retracement(highs, lows, lookback=5)
    assert out["FIBDIR"].iloc[-1] == -1.0
    np.testing.assert_allclose(out["FIB_0.5"].iloc[-1], 0 + 5 * 0.5)


def test_fib_extensions_are_opt_in() -> None:
    base = zeonta.fib_retracement([1, 2, 3], [0, 1, 2], lookback=3)
    extended = zeonta.fib_retracement([1, 2, 3], [0, 1, 2], lookback=3, extensions=True)
    assert "FIB_1.618" not in base.columns
    assert "FIB_1.618" in extended.columns


def test_fib_rejects_empty_ratios() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        zeonta.fib_retracement([1, 2, 3], [0, 1, 2], lookback=3, ratios=[])


def test_classic_pivot_points_match_the_formula() -> None:
    out = zeonta.pivot_points([10, 11], [8, 9], [9, 10])
    # Previous bar H=10 L=8 C=9 -> P = 9, R1 = 2*9-8 = 10, S1 = 2*9-10 = 8
    row = out.iloc[1]
    np.testing.assert_allclose(row["PP_classic"], 9.0)
    np.testing.assert_allclose(row["R1_classic"], 10.0)
    np.testing.assert_allclose(row["S1_classic"], 8.0)
    np.testing.assert_allclose(row["R2_classic"], 11.0)
    np.testing.assert_allclose(row["S2_classic"], 7.0)


def test_fibonacci_pivot_points_use_fib_ratios() -> None:
    out = zeonta.pivot_points([10, 11], [8, 9], [9, 10], kind="fibonacci")
    row = out.iloc[1]
    np.testing.assert_allclose(row["R1_fibonacci"], 9 + 0.382 * 2)
    np.testing.assert_allclose(row["S3_fibonacci"], 9 - 1.0 * 2)


def test_pivot_points_are_causal() -> None:
    """Levels derive from the previous bar, so bar 0 has none."""
    out = zeonta.pivot_points([10, 11], [8, 9], [9, 10])
    assert out.iloc[0].isna().all()


def test_pivot_points_reject_unknown_kind() -> None:
    with pytest.raises(ValueError, match="'kind' must be"):
        zeonta.pivot_points([10, 11], [8, 9], [9, 10], kind="camarilla")


def test_regular_bearish_divergence_is_detected() -> None:
    """Price makes a higher high while the oscillator makes a lower high."""
    highs = np.array([1, 2, 5, 2, 1, 2, 6, 2, 1], dtype=float)
    lows = highs - 1
    osc = np.array([10, 20, 80, 20, 10, 20, 70, 20, 10], dtype=float)
    out = zeonta.divergence(highs, lows, highs, oscillator=osc, left=2, right=2)
    assert out["DIVREGBEAR_2_2"].iloc[6] == 1.0


def test_regular_bullish_divergence_is_detected() -> None:
    lows = np.array([9, 8, 5, 8, 9, 8, 4, 8, 9], dtype=float)
    highs = lows + 1
    osc = np.array([50, 40, 20, 40, 50, 40, 30, 40, 50], dtype=float)
    out = zeonta.divergence(highs, lows, lows, oscillator=osc, left=2, right=2)
    assert out["DIVREGBULL_2_2"].iloc[6] == 1.0


def test_hidden_bearish_divergence_is_detected() -> None:
    """Price makes a lower high while the oscillator makes a higher high."""
    highs = np.array([1, 2, 6, 2, 1, 2, 5, 2, 1], dtype=float)
    osc = np.array([10, 20, 70, 20, 10, 20, 80, 20, 10], dtype=float)
    out = zeonta.divergence(highs, highs - 1, highs, oscillator=osc, left=2, right=2)
    assert out["DIVHIDBEAR_2_2"].iloc[6] == 1.0


def test_divergence_defaults_to_rsi(ohlcv: pd.DataFrame) -> None:
    out = zeonta.divergence(ohlcv["high"], ohlcv["low"], ohlcv["close"])
    assert out.to_numpy().sum() > 0
    assert set(np.unique(out.to_numpy())) <= {0.0, 1.0}


def test_divergence_rejects_a_mismatched_oscillator(ohlcv: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="same length"):
        zeonta.divergence(ohlcv["high"], ohlcv["low"], ohlcv["close"], oscillator=np.arange(10.0))


def test_no_divergence_flags_in_a_clean_trend() -> None:
    """Price and oscillator moving together must not produce regular divergences."""
    prices = np.linspace(1, 100, 200)
    out = zeonta.divergence(prices, prices, prices, oscillator=prices, left=3, right=3)
    assert out["DIVREGBEAR_3_3"].sum() == 0
    assert out["DIVREGBULL_3_3"].sum() == 0
