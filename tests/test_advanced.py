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


def test_classic_pivot_points_r3_s3_match_tradingviews_own_formula() -> None:
    """R3/S3 = P +/- 2*(High-Low), TradingView's own documented formula
    (their Pivot Points Standard support page) and empirically confirmed
    against a live reading. StockCharts' own Classic page does not define
    R3/S3 at all, and this library previously used a different formula
    (High + 2*(P-Low), actually Camarilla's R3, not Classic's) by mistake."""
    out = zeonta.pivot_points([10, 11], [8, 9], [9, 10])
    row = out.iloc[1]
    np.testing.assert_allclose(row["R3_classic"], 13.0)
    np.testing.assert_allclose(row["S3_classic"], 5.0)


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


def test_hurst_exponent_matches_an_independent_reimplementation() -> None:
    """Recompute the same R/S regression a different way (no shared helper
    function) to catch a bug either implementation alone would miss."""
    rng = np.random.default_rng(3)
    prices = 100.0 * np.cumprod(1 + rng.normal(scale=0.01, size=200))
    result = zeonta.hurst_exponent(prices, window=64)

    log_returns = np.diff(np.log(prices))
    window = 64
    segment = log_returns[-window:]
    lags = [8, 16, 32]
    log_lag, log_rs = [], []
    for lag in lags:
        chunks = window // lag
        ratios = []
        for c in range(chunks):
            piece = segment[c * lag : (c + 1) * lag]
            cum_dev = np.cumsum(piece - piece.mean())
            ratios.append((cum_dev.max() - cum_dev.min()) / piece.std())
        log_lag.append(np.log(lag))
        log_rs.append(np.log(np.mean(ratios)))
    expected_slope = np.polyfit(log_lag, log_rs, 1)[0]

    np.testing.assert_allclose(result.iloc[-1], expected_slope)


def test_hurst_exponent_is_higher_for_persistent_than_anti_persistent_returns() -> None:
    """Same noise, opposite-sign AR(1) return autocorrelation: a positively
    autocorrelated (trend-persistent) series must score higher than a
    negatively autocorrelated (mean-reverting) one."""
    rng = np.random.default_rng(4)
    n = 400
    noise = rng.normal(scale=0.01, size=n)

    persistent_returns = np.zeros(n)
    antipersistent_returns = np.zeros(n)
    for i in range(1, n):
        persistent_returns[i] = 0.4 * persistent_returns[i - 1] + noise[i]
        antipersistent_returns[i] = -0.4 * antipersistent_returns[i - 1] + noise[i]

    persistent_price = 100.0 * np.cumprod(1 + persistent_returns)
    antipersistent_price = 100.0 * np.cumprod(1 + antipersistent_returns)

    h_persistent = zeonta.hurst_exponent(persistent_price, window=100).dropna().iloc[-1]
    h_antipersistent = zeonta.hurst_exponent(antipersistent_price, window=100).dropna().iloc[-1]
    assert h_persistent > h_antipersistent


def test_hurst_exponent_is_nan_on_a_perfectly_flat_series() -> None:
    """Every chunk has zero standard deviation, so no lag produces a usable
    R/S ratio - this must be NaN, not a crash or a divide-by-zero warning
    (already covered by the registry-wide constant-input contract test)."""
    result = zeonta.hurst_exponent([50.0] * 200, window=64)
    assert result.isna().all()


def test_hurst_exponent_short_input_is_all_nan_not_an_error() -> None:
    result = zeonta.hurst_exponent([1.0, 2.0, 3.0], window=100)
    assert len(result) == 3
    assert result.isna().all()


def test_hurst_exponent_rejects_a_window_too_small_for_two_lags() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.hurst_exponent(list(range(1, 50)), window=16)


def test_ou_half_life_matches_an_independent_polyfit_regression() -> None:
    prices = [100.0, 102.0, 99.0, 101.0, 98.0, 103.0]
    result = zeonta.ou_half_life(prices, window=5)

    values = np.array(prices)
    slope, _ = np.polyfit(values[:-1], values[1:] - values[:-1], 1)
    expected = -np.log(2.0) / slope
    assert slope < 0.0, "test fixture must be mean-reverting for this assertion to be meaningful"
    np.testing.assert_allclose(result.iloc[-1], expected)
    assert result.iloc[:-1].isna().all()


def test_ou_half_life_is_nan_for_a_pure_trend_lambda_non_negative() -> None:
    """A deterministic linear trend has a constant bar-to-bar change that
    does not covary with the prior level at all - the fitted lambda is
    exactly 0, which by convention (no mean reversion detected) is NaN,
    not a spurious near-infinite half-life."""
    result = zeonta.ou_half_life(list(range(1, 60)), window=20)
    assert result.isna().all()


def test_ou_half_life_is_nan_on_a_perfectly_flat_series() -> None:
    result = zeonta.ou_half_life([50.0] * 20, window=10)
    assert result.isna().all()


def test_ou_half_life_short_input_is_all_nan_not_an_error() -> None:
    result = zeonta.ou_half_life([1.0, 2.0, 3.0], window=100)
    assert len(result) == 3
    assert result.isna().all()


def test_ou_half_life_warmup_is_exactly_window_bars() -> None:
    result = zeonta.ou_half_life(list(range(1, 60)), window=20)
    assert result.iloc[:20].isna().all()


def test_ou_half_life_rejects_window_below_three() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.ou_half_life(list(range(1, 20)), window=2)


def test_dfa_is_higher_for_persistent_than_anti_persistent_returns() -> None:
    """Same construction as the equivalent hurst_exponent test: same noise,
    opposite-sign AR(1) return autocorrelation must rank the same way for
    DFA's exponent as it does for R/S's, since both estimate the same
    persistence concept."""
    rng = np.random.default_rng(4)
    n = 400
    noise = rng.normal(scale=0.01, size=n)

    persistent_returns = np.zeros(n)
    antipersistent_returns = np.zeros(n)
    for i in range(1, n):
        persistent_returns[i] = 0.4 * persistent_returns[i - 1] + noise[i]
        antipersistent_returns[i] = -0.4 * antipersistent_returns[i - 1] + noise[i]

    persistent_price = 100.0 * np.cumprod(1 + persistent_returns)
    antipersistent_price = 100.0 * np.cumprod(1 + antipersistent_returns)

    d_persistent = zeonta.dfa(persistent_price, window=100).dropna().iloc[-1]
    d_antipersistent = zeonta.dfa(antipersistent_price, window=100).dropna().iloc[-1]
    assert d_persistent > d_antipersistent


def test_dfa_is_nan_on_a_perfectly_flat_series() -> None:
    """Zero log returns everywhere means every box's fluctuation is exactly
    zero, so no box size yields a usable log(F(n)) - must be NaN, not a
    crash or a divide-by-zero warning (covered generically by the
    registry-wide constant-input contract test, pinned down here too)."""
    result = zeonta.dfa([100.0] * 80, window=32)
    assert result.isna().all()


def test_dfa_short_input_is_all_nan_not_an_error() -> None:
    result = zeonta.dfa([1.0, 2.0, 3.0], window=100)
    assert len(result) == 3
    assert result.isna().all()


def test_dfa_warmup_is_exactly_window_bars() -> None:
    rng = np.random.default_rng(1)
    prices = 100.0 + np.cumsum(rng.normal(size=80))
    result = zeonta.dfa(prices, window=32)
    assert result.iloc[:32].isna().all()
    assert result.iloc[32:].notna().all()


def test_dfa_rejects_a_window_too_small_for_two_box_sizes() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.dfa(list(range(1, 50)), window=16)
