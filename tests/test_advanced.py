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


def test_cpr_pivot_matches_the_classic_pivot_formula() -> None:
    """CPR's own pivot must agree exactly with pivot_points' classic pivot."""
    high, low, close = [10.0, 14.0], [8.0, 9.0], [9.6, 13.0]
    cpr_out = zeonta.cpr(high, low, close)
    pivot_out = zeonta.pivot_points(high, low, close, kind="classic")
    np.testing.assert_allclose(cpr_out["CPR_PIVOT"].to_numpy(), pivot_out["PP_classic"].to_numpy())


def test_cpr_matches_the_hand_computed_bc_and_tc() -> None:
    out = zeonta.cpr([10.0, 14.0], [8.0, 9.0], [9.6, 13.0])
    row = out.iloc[1]
    np.testing.assert_allclose(row["CPR_PIVOT"], 9.2)
    np.testing.assert_allclose(row["CPR_BC"], 9.0)
    np.testing.assert_allclose(row["CPR_TC"], 9.4)


def test_cpr_bc_and_tc_are_equidistant_from_the_pivot() -> None:
    out = zeonta.cpr([10.0, 14.0, 11.0], [8.0, 9.0, 7.0], [9.6, 13.0, 8.0]).dropna()
    distance_to_bc = out["CPR_PIVOT"] - out["CPR_BC"]
    distance_to_tc = out["CPR_TC"] - out["CPR_PIVOT"]
    np.testing.assert_allclose(distance_to_bc.to_numpy(), distance_to_tc.to_numpy())


def test_cpr_is_causal() -> None:
    out = zeonta.cpr([10.0, 11.0], [8.0, 9.0], [9.0, 10.0])
    assert out.iloc[0].isna().all()


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


def test_higuchi_fractal_dimension_matches_an_independent_reimplementation() -> None:
    """Recompute L_m(k)/L(k)/the regression a different way (no shared
    helper function) to catch a bug either implementation alone would miss."""

    def reference_hfd(values: list[float], k_max: int) -> float:
        n = len(values)
        log_inv_k, log_length = [], []
        for k in range(1, k_max + 1):
            lengths = []
            for m in range(1, k + 1):
                positions = list(range(m - 1, n, k))
                if len(positions) < 2:
                    continue
                n_max = len(positions) - 1
                total = sum(
                    abs(values[positions[i + 1]] - values[positions[i]]) for i in range(n_max)
                )
                lengths.append(total * (n - 1) / (n_max * k * k))
            if lengths:
                log_inv_k.append(np.log(1.0 / k))
                log_length.append(np.log(float(np.mean(lengths))))
        return float(np.polyfit(log_inv_k, log_length, 1)[0])

    rng = np.random.default_rng(7)
    prices = (100.0 + np.cumsum(rng.normal(size=60))).tolist()
    result = zeonta.higuchi_fractal_dimension(prices, window=60, k_max=6)

    expected = reference_hfd(prices, 6)
    np.testing.assert_allclose(result.iloc[-1], expected)


def test_higuchi_fractal_dimension_is_lower_for_a_straight_line_than_noise() -> None:
    """A straight line's curve length barely shrinks as the sampling step
    widens (HFD near 1); pure noise's shrinks as fast as possible (HFD near
    the theoretical ceiling of 2)."""
    line = np.arange(1.0, 201.0)
    rng = np.random.default_rng(1)
    noise = rng.normal(size=200)

    h_line = zeonta.higuchi_fractal_dimension(line, window=100, k_max=10).dropna().iloc[-1]
    h_noise = zeonta.higuchi_fractal_dimension(noise, window=100, k_max=10).dropna().iloc[-1]

    assert h_line < h_noise
    assert 1.0 <= h_line <= 1.1
    assert 1.8 <= h_noise <= 2.2


def test_higuchi_fractal_dimension_short_input_is_all_nan_not_an_error() -> None:
    result = zeonta.higuchi_fractal_dimension([1.0, 2.0, 3.0], window=100, k_max=10)
    assert len(result) == 3
    assert result.isna().all()


def test_higuchi_fractal_dimension_rejects_k_max_below_two() -> None:
    with pytest.raises(ValueError, match="k_max"):
        zeonta.higuchi_fractal_dimension(list(range(1, 50)), window=20, k_max=1)


def test_higuchi_fractal_dimension_rejects_a_window_too_small_for_k_max() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.higuchi_fractal_dimension(list(range(1, 50)), window=10, k_max=10)


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


def test_sample_entropy_is_higher_for_noisy_than_periodic_returns() -> None:
    """A perfectly periodic return series repeats its own short patterns
    exactly, so it should score near-zero entropy; unstructured noise at a
    comparable scale should score noticeably higher."""
    rng = np.random.default_rng(2)
    n = 300
    t = np.arange(n)
    periodic_returns = 0.01 * np.sin(2 * np.pi * t / 10)
    noisy_returns = rng.normal(scale=0.01, size=n)
    periodic_price = 100.0 * np.cumprod(1 + periodic_returns)
    noisy_price = 100.0 * np.cumprod(1 + noisy_returns)

    periodic_entropy = zeonta.sample_entropy(periodic_price, window=100).dropna().iloc[-1]
    noisy_entropy = zeonta.sample_entropy(noisy_price, window=100).dropna().iloc[-1]
    assert noisy_entropy > periodic_entropy
    np.testing.assert_allclose(periodic_entropy, 0.0, atol=1e-9)


def test_sample_entropy_is_nan_on_a_perfectly_flat_series() -> None:
    """Zero log returns everywhere means a zero-width tolerance - no
    meaningful match count is possible, so this must be NaN, not a crash
    or a divide-by-zero warning (covered generically by the registry-wide
    constant-input contract test, pinned down here too)."""
    result = zeonta.sample_entropy([100.0] * 50, window=20)
    assert result.isna().all()


def test_sample_entropy_short_input_is_all_nan_not_an_error() -> None:
    result = zeonta.sample_entropy([1.0, 2.0, 3.0], window=100)
    assert len(result) == 3
    assert result.isna().all()


def test_sample_entropy_rejects_window_below_twenty() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.sample_entropy(list(range(1, 50)), window=10)


def test_sample_entropy_rejects_m_below_one() -> None:
    with pytest.raises(ValueError, match="'m' must be an integer >= 1"):
        zeonta.sample_entropy(list(range(1, 50)), m=0)


def test_sample_entropy_rejects_non_positive_r() -> None:
    with pytest.raises(ValueError, match="'r' must be > 0"):
        zeonta.sample_entropy(list(range(1, 50)), r=0.0)


def test_sample_entropy_is_nan_when_tolerance_is_too_tight_for_any_match() -> None:
    rng = np.random.default_rng(0)
    prices = 100.0 * np.cumprod(1 + rng.normal(scale=0.02, size=60))
    result = zeonta.sample_entropy(prices, window=20, r=0.0001)
    assert result.isna().all()


def test_sample_entropy_is_nan_when_m_leaves_too_few_templates() -> None:
    """window - m must leave at least two templates to compare; m close to
    window (window=20, m=19 -> a single template) must be NaN, not a crash."""
    rng = np.random.default_rng(0)
    prices = 100.0 * np.cumprod(1 + rng.normal(scale=0.02, size=60))
    result = zeonta.sample_entropy(prices, window=20, m=19)
    assert result.isna().all()


def test_approximate_entropy_is_higher_for_noisy_than_periodic_returns() -> None:
    """The same shape test as sample_entropy: a periodic series repeats its
    own short patterns almost exactly, unstructured noise should not."""
    rng = np.random.default_rng(2)
    n = 300
    t = np.arange(n)
    periodic_returns = 0.01 * np.sin(2 * np.pi * t / 10)
    noisy_returns = rng.normal(scale=0.01, size=n)
    periodic_price = 100.0 * np.cumprod(1 + periodic_returns)
    noisy_price = 100.0 * np.cumprod(1 + noisy_returns)

    periodic_entropy = zeonta.approximate_entropy(periodic_price, window=100).dropna().iloc[-1]
    noisy_entropy = zeonta.approximate_entropy(noisy_price, window=100).dropna().iloc[-1]
    assert noisy_entropy > periodic_entropy


def test_approximate_entropy_is_never_negative() -> None:
    """Unlike sample_entropy, self-matches are always counted, so C_i^k is
    always >= 1/count and phi(m) can never fall below phi(m+1)'s own floor
    by more than measurement noise allows — this is the property Sample
    Entropy was built specifically to remove."""
    rng = np.random.default_rng(0)
    prices = 100.0 * np.cumprod(1 + rng.normal(scale=0.01, size=150))
    result = zeonta.approximate_entropy(prices, window=100).dropna()
    assert (result >= 0.0).all()


def test_approximate_entropy_short_input_is_all_nan_not_an_error() -> None:
    result = zeonta.approximate_entropy([1.0, 2.0, 3.0], window=100)
    assert len(result) == 3
    assert result.isna().all()


def test_approximate_entropy_rejects_window_below_twenty() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.approximate_entropy(list(range(1, 50)), window=10)


def test_approximate_entropy_rejects_m_below_one() -> None:
    with pytest.raises(ValueError, match="'m' must be an integer >= 1"):
        zeonta.approximate_entropy(list(range(1, 50)), m=0)


def test_approximate_entropy_rejects_non_positive_r() -> None:
    with pytest.raises(ValueError, match="'r' must be > 0"):
        zeonta.approximate_entropy(list(range(1, 50)), r=0.0)


def test_permutation_entropy_is_zero_for_a_monotonic_series() -> None:
    """A strictly increasing series produces exactly one ordinal pattern
    ("everything ascending") in every window, so its probability is 1 and
    the entropy is exactly 0."""
    result = zeonta.permutation_entropy(list(range(1, 130)), window=100, order=3)
    np.testing.assert_allclose(result.dropna().to_numpy(), 0.0, atol=1e-12)


def test_permutation_entropy_is_higher_for_noise_than_a_clean_ramp() -> None:
    rng = np.random.default_rng(3)
    ramp = list(range(1, 130))
    noisy = (100.0 + rng.normal(scale=1.0, size=130)).tolist()
    ramp_entropy = zeonta.permutation_entropy(ramp, window=100, order=3).dropna().iloc[-1]
    noisy_entropy = zeonta.permutation_entropy(noisy, window=100, order=3).dropna().iloc[-1]
    assert noisy_entropy > ramp_entropy


def test_permutation_entropy_short_input_is_all_nan_not_an_error() -> None:
    result = zeonta.permutation_entropy([1.0, 2.0, 3.0], window=100)
    assert len(result) == 3
    assert result.isna().all()


def test_permutation_entropy_rejects_window_below_twenty() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.permutation_entropy(list(range(1, 50)), window=10)


def test_permutation_entropy_rejects_order_below_two() -> None:
    with pytest.raises(ValueError, match="'order' must be an integer >= 2"):
        zeonta.permutation_entropy(list(range(1, 50)), order=1)


def test_permutation_entropy_rejects_non_positive_delay() -> None:
    with pytest.raises(ValueError, match="'delay' must be >="):
        zeonta.permutation_entropy(list(range(1, 50)), delay=0)


def test_shannon_entropy_matches_a_hand_traced_two_bucket_window() -> None:
    """20 log returns split 15-5 across two equal-width buckets should give
    the textbook two-outcome Shannon entropy for p = 0.75/0.25, normalized by
    log(2) for a 2-bucket window."""
    # 15 returns clustered near -0.01, 5 clustered near +0.03: bucket edges
    # split the [-0.01, 0.03] range into a "low" and a "high" half.
    log_returns = [-0.01] * 15 + [0.03] * 5
    prices = [100.0]
    for r in log_returns:
        prices.append(prices[-1] * np.exp(r))
    result = zeonta.shannon_entropy(prices, window=20, bins=2)

    p_low, p_high = 0.75, 0.25
    expected = -(p_low * np.log(p_low) + p_high * np.log(p_high)) / np.log(2)
    np.testing.assert_allclose(result.iloc[-1], expected)


def test_shannon_entropy_is_zero_on_a_perfectly_flat_series() -> None:
    """Zero log returns everywhere means a zero-width bucket range - defined
    as exactly 0.0 (no spread at all), not NaN or a divide-by-zero warning."""
    result = zeonta.shannon_entropy([100.0] * 50, window=20)
    np.testing.assert_allclose(result.dropna().to_numpy(), 0.0)


def test_shannon_entropy_is_higher_for_noise_than_a_single_repeated_move() -> None:
    """A window whose returns take on almost the same one value every bar
    (all mass in one or two neighboring buckets) has low entropy; Gaussian
    noise spread across many move sizes should score noticeably higher."""
    rng = np.random.default_rng(1)
    repeated = 100.0 * np.cumprod(1.0 + np.full(60, 0.005))
    noisy = 100.0 * np.cumprod(1.0 + rng.normal(scale=0.01, size=60))

    repeated_entropy = zeonta.shannon_entropy(repeated, window=50).dropna().iloc[-1]
    noisy_entropy = zeonta.shannon_entropy(noisy, window=50).dropna().iloc[-1]
    assert noisy_entropy > repeated_entropy


def test_shannon_entropy_stays_within_zero_to_one() -> None:
    rng = np.random.default_rng(4)
    prices = 100.0 * np.cumprod(1.0 + rng.normal(scale=0.02, size=200))
    result = zeonta.shannon_entropy(prices, window=50).dropna()
    assert ((result >= 0.0) & (result <= 1.0)).all()


def test_shannon_entropy_short_input_is_all_nan_not_an_error() -> None:
    result = zeonta.shannon_entropy([1.0, 2.0, 3.0], window=100)
    assert len(result) == 3
    assert result.isna().all()


def test_shannon_entropy_rejects_window_below_twenty() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.shannon_entropy(list(range(1, 50)), window=10)


def test_shannon_entropy_rejects_bins_below_two() -> None:
    with pytest.raises(ValueError, match="'bins' must be an integer >= 2"):
        zeonta.shannon_entropy(list(range(1, 50)), bins=1)


def test_permutation_entropy_rejects_a_window_too_small_for_two_patterns() -> None:
    with pytest.raises(ValueError, match="'window' must be large enough"):
        zeonta.permutation_entropy(list(range(1, 50)), window=20, order=25, delay=1)


def test_markov_regime_switching_separates_a_planted_low_and_high_volatility_regime() -> None:
    """150 bars of quiet returns followed by 150 bars of turbulent returns is
    an unambiguous 2-regime series. With window=60, index 110 sits well
    inside the low-volatility stretch (its whole window, bars 50-109, is
    quiet, with a 40-bar margin from the regime change at 150) and index
    270 sits well inside the high-volatility stretch (its whole window,
    bars 210-269, is turbulent, 120 bars past the change) - both far enough
    from the boundary that neither window straddles it."""
    rng = np.random.default_rng(0)
    quiet_returns = rng.normal(scale=0.002, size=150)
    turbulent_returns = rng.normal(scale=0.03, size=150)
    prices = 100.0 * np.cumprod(1 + np.concatenate([quiet_returns, turbulent_returns]))

    result = zeonta.markov_regime_switching(prices, window=60)

    assert result.iloc[110] < 0.3
    assert result.iloc[270] > 0.7


def test_markov_regime_switching_short_input_is_all_nan_not_an_error() -> None:
    result = zeonta.markov_regime_switching([1.0, 2.0, 3.0], window=100)
    assert len(result) == 3
    assert result.isna().all()


def test_markov_regime_switching_rejects_window_below_twenty() -> None:
    with pytest.raises(ValueError, match="'window' must be >="):
        zeonta.markov_regime_switching(list(range(1, 50)), window=10)


def test_markov_regime_switching_rejects_max_iterations_below_one() -> None:
    with pytest.raises(ValueError, match="'max_iterations' must be >="):
        zeonta.markov_regime_switching(list(range(1, 50)), max_iterations=0)


def test_markov_regime_switching_rejects_non_positive_tolerance() -> None:
    with pytest.raises(ValueError, match="'tolerance' must be > 0"):
        zeonta.markov_regime_switching(list(range(1, 50)), tolerance=0.0)


def test_markov_regime_switching_is_deterministic() -> None:
    """EM is otherwise sensitive to starting values; this is the property
    that makes the fixed, deterministic initialisation scheme correct."""
    rng = np.random.default_rng(3)
    prices = 100.0 * np.cumprod(1 + rng.normal(scale=0.01, size=200))
    first = zeonta.markov_regime_switching(prices, window=50)
    second = zeonta.markov_regime_switching(prices, window=50)
    pd.testing.assert_series_equal(first, second)


def test_markov_regime_switching_stays_within_zero_to_one() -> None:
    rng = np.random.default_rng(9)
    quiet_returns = rng.normal(scale=0.002, size=150)
    turbulent_returns = rng.normal(scale=0.03, size=150)
    prices = 100.0 * np.cumprod(1 + np.concatenate([quiet_returns, turbulent_returns]))
    result = zeonta.markov_regime_switching(prices, window=50).dropna()
    assert ((result >= 0.0) & (result <= 1.0)).all()
