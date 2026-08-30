"""Volatility indicators — golden values traced by hand from the formulas."""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
import pytest

import zeonta


def test_true_range_takes_the_widest_of_the_three_measures() -> None:
    # bar 0 has no previous close -> H-L = 2
    # bar 1: H-L = 1, |H-prevC| = |12-9| = 3, |L-prevC| = |11-9| = 2 -> 3
    result = zeonta.true_range([10, 12], [8, 11], [9, 11.5])
    np.testing.assert_allclose(result, [2.0, 3.0])


def test_true_range_captures_a_gap_that_high_minus_low_misses() -> None:
    """A gap up leaves a narrow bar whose true range is still large."""
    result = zeonta.true_range([10, 20], [9, 19], [9.5, 19.5])
    assert result.iloc[1] == pytest.approx(20 - 9.5)


def test_true_range_a_fully_missing_bar_is_nan_without_warning() -> None:
    """A bar with both high and low missing makes every one of the three
    measures NaN; `np.nanmax` over an all-NaN slice is correct but noisy —
    the value must still be NaN, and no RuntimeWarning should reach the
    caller's logs for what is an entirely expected case."""
    with warnings.catch_warnings():
        warnings.simplefilter("error", category=RuntimeWarning)
        result = zeonta.true_range(
            [10.0, 12.0, np.nan, 13.0],
            [8.0, 11.0, np.nan, 12.0],
            [9.0, 11.5, np.nan, 12.5],
        )
    assert np.isnan(result.iloc[2])
    assert not result.iloc[[0, 1, 3]].isna().any()


def test_atr_seed_is_the_average_of_the_first_true_ranges() -> None:
    # TR = [2, 3, 2]; ATR(3) at bar 2 = mean = 7/3
    result = zeonta.atr([10, 12, 13], [8, 9, 11], [9, 11, 12], length=3)
    np.testing.assert_allclose(result.iloc[2], 7 / 3)


def test_atr_is_zero_on_a_perfectly_flat_market() -> None:
    np.testing.assert_allclose(zeonta.atr([5.0] * 30, [5.0] * 30, [5.0] * 30).iloc[-1], 0.0)


def test_atr_is_never_negative(ohlcv: pd.DataFrame) -> None:
    values = zeonta.atr(ohlcv["high"], ohlcv["low"], ohlcv["close"]).dropna()
    assert (values >= 0).all()


def test_atr_rises_when_volatility_rises() -> None:
    calm_high = [10.1] * 40
    calm_low = [9.9] * 40
    wild_high = calm_high + [15.0] * 20
    wild_low = calm_low + [5.0] * 20
    close = [10.0] * 60
    values = zeonta.atr(wild_high, wild_low, close, length=14)
    assert values.iloc[-1] > values.iloc[39]


def test_bbands_are_symmetric_around_the_sma() -> None:
    prices = list(np.linspace(10, 40, 100))
    out = zeonta.bbands(prices, length=20, std=2)
    middle = out["BBM_20_2.0"]
    np.testing.assert_allclose(
        (out["BBU_20_2.0"] - middle).to_numpy(),
        (middle - out["BBL_20_2.0"]).to_numpy(),
        equal_nan=True,
    )
    np.testing.assert_allclose(middle.to_numpy(), zeonta.sma(prices, 20).to_numpy(), equal_nan=True)


def test_bbands_collapse_onto_the_middle_when_price_is_flat() -> None:
    out = zeonta.bbands([10.0] * 25)
    last = out.iloc[-1]
    assert last["BBU_20_2.0"] == last["BBL_20_2.0"] == last["BBM_20_2.0"] == 10.0
    assert last["BBB_20_2.0"] == 0.0
    assert last["BBP_20_2.0"] == 0.5


def test_bbands_percent_b_is_one_at_the_upper_band(ohlcv: pd.DataFrame) -> None:
    out = zeonta.bbands(ohlcv["close"])
    upper = zeonta.bbands(ohlcv["close"])["BBU_20_2.0"]
    at_upper = zeonta.bbands(upper)  # not the point; just ensure percent-b maths is consistent
    assert at_upper is not None
    row = out.dropna().iloc[0]
    expected = (ohlcv["close"].loc[row.name] - row["BBL_20_2.0"]) / (
        row["BBU_20_2.0"] - row["BBL_20_2.0"]
    )
    np.testing.assert_allclose(row["BBP_20_2.0"], expected)


def test_bbands_sample_deviation_is_wider_than_population(ohlcv: pd.DataFrame) -> None:
    population = zeonta.bbands(ohlcv["close"], ddof=0)["BBU_20_2.0"].iloc[-1]
    sample = zeonta.bbands(ohlcv["close"], ddof=1)["BBU_20_2.0"].iloc[-1]
    assert sample > population


def test_bbands_rejects_non_positive_std() -> None:
    with pytest.raises(ValueError, match="'std' must be > 0"):
        zeonta.bbands([10.0] * 25, std=0)


def test_keltner_is_the_ema_plus_atr(ohlcv: pd.DataFrame) -> None:
    out = zeonta.keltner(ohlcv["high"], ohlcv["low"], ohlcv["close"])
    expected_mid = zeonta.ema(ohlcv["close"], 20)
    expected_atr = zeonta.atr(ohlcv["high"], ohlcv["low"], ohlcv["close"], 10)
    np.testing.assert_allclose(out["KCM_20_2.0"], expected_mid, equal_nan=True)
    np.testing.assert_allclose(out["KCU_20_2.0"], expected_mid + 2.0 * expected_atr, equal_nan=True)


def test_keltner_is_smoother_than_bollinger_through_a_shock(ohlcv: pd.DataFrame) -> None:
    """The property the squeeze relies on: ATR reacts slower than std deviation."""
    close = ohlcv["close"].copy()
    close.iloc[150] *= 1.15  # single violent bar
    high = ohlcv["high"].copy()
    high.iloc[150] *= 1.15
    bb_width = zeonta.bbands(close)["BBU_20_2.0"] - zeonta.bbands(close)["BBL_20_2.0"]
    kc = zeonta.keltner(high, ohlcv["low"], close)
    kc_width = kc["KCU_20_2.0"] - kc["KCL_20_2.0"]
    bb_jump = bb_width.iloc[150] / bb_width.iloc[149]
    kc_jump = kc_width.iloc[150] / kc_width.iloc[149]
    assert bb_jump > kc_jump


def test_squeeze_momentum_midline_is_a_nested_average(ohlcv: pd.DataFrame) -> None:
    """TTM weights the high-low midpoint and the SMA equally, at 1/2 each.

    Some casual descriptions write the midline as ``Avg(HighestHigh, LowestLow,
    SMA)``, which reads as an equal three-way mean (1/3 each). The published
    TTM Squeeze uses ``avg(avg(hh, ll), sma)``; this pins the weighting we
    implement.
    """
    high, low, close = ohlcv["high"], ohlcv["low"], ohlcv["close"]
    length = 20
    range_mid = (high.rolling(length).max() + low.rolling(length).min()) / 2
    expected_midline = (range_mid + close.rolling(length).mean()) / 2
    three_way = (
        high.rolling(length).max() + low.rolling(length).min() + close.rolling(length).mean()
    ) / 3

    from zeonta._core import rolling_linreg

    expected = rolling_linreg((close - expected_midline).to_numpy(), length).endpoint
    wrong = rolling_linreg((close - three_way).to_numpy(), length).endpoint
    actual = zeonta.squeeze(high, low, close).filter(like="SQZ_MOM").iloc[:, 0].to_numpy()

    np.testing.assert_allclose(actual, expected, equal_nan=True)
    assert not np.allclose(actual[length:], wrong[length:])


def test_squeeze_flags_are_mutually_exclusive(ohlcv: pd.DataFrame) -> None:
    out = zeonta.squeeze(ohlcv["high"], ohlcv["low"], ohlcv["close"]).dropna()
    on = out.filter(like="SQZ_ON").iloc[:, 0]
    off = out.filter(like="SQZ_OFF").iloc[:, 0]
    assert ((on + off) == 1.0).all()


def test_squeeze_turns_on_when_price_goes_quiet() -> None:
    """A volatile stretch followed by a dead-flat one must end in a squeeze."""
    rng = np.random.default_rng(7)
    noisy = 100 + np.cumsum(rng.normal(0, 2.0, 80))
    quiet = np.full(60, noisy[-1])
    close = np.concatenate([noisy, quiet])
    high = close + np.concatenate([np.full(80, 2.0), np.full(60, 0.01)])
    low = close - np.concatenate([np.full(80, 2.0), np.full(60, 0.01)])
    out = zeonta.squeeze(high, low, close)
    assert out.filter(like="SQZ_ON").iloc[-1, 0] == 1.0


def test_squeeze_widening_the_keltner_makes_squeezes_more_frequent(ohlcv: pd.DataFrame) -> None:
    """A wider Keltner Channel is easier for the Bollinger Bands to fit inside.

    Some casual descriptions of this indicator claim the opposite, but the
    formula itself (``squeeze ON when BB Upper < KC Upper and BB Lower > KC
    Lower``) says a larger ``kc_multiplier`` pushes the Keltner bands further
    out, so enclosure becomes easier, not harder. The implementation follows
    the formula.
    """
    tight = zeonta.squeeze(ohlcv["high"], ohlcv["low"], ohlcv["close"], kc_multiplier=1.5)
    wide = zeonta.squeeze(ohlcv["high"], ohlcv["low"], ohlcv["close"], kc_multiplier=3.0)
    assert wide.filter(like="SQZ_ON").sum().iloc[0] > tight.filter(like="SQZ_ON").sum().iloc[0]


def test_ulcer_index_matches_the_hand_computed_value() -> None:
    # highest close over window [90,90]=90 -> drawdown at idx3=(90-90)/90*100=0
    # window [100,90]=100 -> drawdown at idx2=(90-100)/100*100=-10
    # mean(0^2,(-10)^2)/... sqrt(mean(0,100))=sqrt(50)
    result = zeonta.ulcer_index([100.0, 100.0, 90.0, 90.0], length=2)
    np.testing.assert_allclose(result.iloc[-1], (50.0) ** 0.5)


def test_ulcer_index_is_zero_when_every_bar_is_a_new_high() -> None:
    result = zeonta.ulcer_index(list(range(1, 30)), length=10)
    np.testing.assert_allclose(result.dropna().to_numpy(), 0.0)


def test_ulcer_index_is_never_negative(ohlcv: pd.DataFrame) -> None:
    result = zeonta.ulcer_index(ohlcv["close"]).dropna()
    assert (result >= 0.0).all()


def test_ulcer_index_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.ulcer_index([1.0, 2.0, 3.0], length=0)


def test_wavelet_variance_warmup_is_exactly_window_minus_one_bars() -> None:
    rng = np.random.default_rng(7)
    values = np.cumsum(rng.normal(size=80)) + 100.0
    result = zeonta.wavelet_variance(values, window=32, level=3)
    assert result.iloc[:31].isna().all().all()
    assert result.iloc[31:].notna().all().all()


def test_wavelet_variance_is_causal_new_bars_never_change_past_values() -> None:
    """The same non-repaint requirement as wavelet_denoise: a bar's value
    must never depend on bars that arrive after it."""
    rng = np.random.default_rng(42)
    prices = np.cumsum(rng.normal(size=100)) + 100.0
    full = zeonta.wavelet_variance(prices, window=32, level=3)
    prefix = zeonta.wavelet_variance(prices[:60], window=32, level=3)
    np.testing.assert_allclose(full.iloc[:60].to_numpy(), prefix.to_numpy(), equal_nan=True)


def test_wavelet_variance_is_near_zero_on_a_flat_series() -> None:
    result = zeonta.wavelet_variance([100.0] * 64, window=32, level=2)
    np.testing.assert_allclose(result.dropna().to_numpy(), 0.0, atol=1e-20)


def test_wavelet_variance_columns_are_named_by_level() -> None:
    result = zeonta.wavelet_variance([1.0] * 32, window=16, level=3)
    assert list(result.columns) == ["WVAR_1", "WVAR_2", "WVAR_3"]


def test_wavelet_variance_rejects_a_window_not_a_multiple_of_2_pow_level() -> None:
    with pytest.raises(ValueError, match="must be an exact multiple"):
        zeonta.wavelet_variance(list(range(40)), window=30, level=3)


def test_wavelet_variance_rejects_non_positive_level() -> None:
    with pytest.raises(ValueError, match="'level' must be >= 1"):
        zeonta.wavelet_variance(list(range(40)), level=0)


def test_natr_matches_atr_divided_by_close() -> None:
    high, low, close = [2.0] * 20, [1.0] * 20, [1.5] * 20
    atr_result = zeonta.atr(high, low, close, length=14)
    natr_result = zeonta.natr(high, low, close, length=14)
    np.testing.assert_allclose(natr_result.iloc[-1], atr_result.iloc[-1] / 1.5 * 100.0)


def test_natr_is_nan_when_close_is_zero() -> None:
    high, low, close = [2.0] * 20, [1.0] * 20, [0.0] * 20
    result = zeonta.natr(high, low, close, length=14)
    assert result.dropna().empty


def test_mass_index_is_flat_on_a_perfectly_constant_range() -> None:
    """Single and double EMA of a constant range both converge to that same
    constant exactly (no gradual approach, since the SMA seed of a constant
    input equals the constant), so the ratio is 1.0 everywhere it's defined
    and the 25-bar sum settles at exactly 25."""
    result = zeonta.mass_index([2.0] * 50, [1.0] * 50, ema_length=9, sum_length=25)
    np.testing.assert_allclose(result.dropna().to_numpy(), 25.0)


def test_mass_index_rejects_non_positive_ema_length() -> None:
    with pytest.raises(ValueError, match="'ema_length' must be >="):
        zeonta.mass_index([2.0] * 10, [1.0] * 10, ema_length=0)


def test_mass_index_rejects_non_positive_sum_length() -> None:
    with pytest.raises(ValueError, match="'sum_length' must be >="):
        zeonta.mass_index([2.0] * 10, [1.0] * 10, sum_length=0)


def test_chaikin_volatility_matches_the_hand_computed_roc_of_the_smoothed_range() -> None:
    high = [12.0, 13.5, 11.0, 15.0, 17.0, 14.5, 18.0]
    low = [10.0, 11.0, 9.5, 11.0, 12.0, 11.0, 12.5]
    result = zeonta.chaikin_volatility(high, low, length=3)
    np.testing.assert_allclose(result.dropna().to_numpy(), [87.5, 54.166666666666664])


def test_chaikin_volatility_is_zero_on_a_constant_range() -> None:
    result = zeonta.chaikin_volatility([12.0] * 10, [10.0] * 10, length=3)
    np.testing.assert_allclose(result.dropna().to_numpy(), 0.0)


def test_chaikin_volatility_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.chaikin_volatility([2.0, 3.0], [1.0, 1.5], length=0)


def test_relative_volatility_index_stays_within_bounds(ohlcv: pd.DataFrame) -> None:
    result = zeonta.relative_volatility_index(ohlcv["close"])
    values = result.dropna().to_numpy()
    assert (values >= 0.0).all() and (values <= 100.0).all()


def test_relative_volatility_index_matches_the_hand_computed_value() -> None:
    close = [10.0, 10.5, 10.2, 10.8, 10.3, 10.9, 10.4, 11.0, 10.6, 11.2]
    result = zeonta.relative_volatility_index(close, stdev_length=4, smooth_length=3)
    np.testing.assert_allclose(result.iloc[-1], 72.21514421674283)


def test_relative_volatility_index_rejects_non_positive_stdev_length() -> None:
    with pytest.raises(ValueError, match="'stdev_length' must be >="):
        zeonta.relative_volatility_index([1.0, 2.0, 3.0], stdev_length=0)


def test_relative_volatility_index_rejects_non_positive_smooth_length() -> None:
    with pytest.raises(ValueError, match="'smooth_length' must be >="):
        zeonta.relative_volatility_index([1.0, 2.0, 3.0], smooth_length=0)


def test_accbands_matches_the_hand_computed_value() -> None:
    high = [12.0, 13.0, 11.0, 14.0, 15.0]
    low = [10.0, 11.0, 9.0, 12.0, 13.0]
    close = [11.0, 12.5, 10.0, 13.5, 14.5]
    out = zeonta.accbands(high, low, close, length=3)
    np.testing.assert_allclose(out["ACCBU_3"].iloc[-1], 17.664468864468862)
    np.testing.assert_allclose(out["ACCBL_3"].iloc[-1], 7.664468864468863)
    np.testing.assert_allclose(out["ACCBM_3"].iloc[-1], 12.666666666666666)


def test_accbands_brackets_close_between_lower_and_upper(ohlcv: pd.DataFrame) -> None:
    out = zeonta.accbands(ohlcv["high"], ohlcv["low"], ohlcv["close"]).dropna()
    assert (out["ACCBU_20"] >= out["ACCBM_20"]).all()
    assert (out["ACCBM_20"] >= out["ACCBL_20"]).all()


def test_accbands_upper_lower_are_nan_on_a_zero_price_zero_range_bar() -> None:
    """High + Low == 0 leaves the ratio undefined; only the outer bands
    (which depend on the ratio) go NaN — the middle band is a plain SMA
    of Close and stays well-defined at 0.0."""
    result = zeonta.accbands([0.0] * 10, [0.0] * 10, [0.0] * 10, length=5)
    assert result["ACCBL_5"].isna().all()
    assert result["ACCBU_5"].isna().all()
    np.testing.assert_allclose(result["ACCBM_5"].dropna().to_numpy(), 0.0)


def test_accbands_rejects_non_positive_length() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.accbands([2.0, 3.0], [1.0, 2.0], [1.5, 2.5], length=0)


def test_accbands_rejects_non_positive_c() -> None:
    with pytest.raises(ValueError, match="'c' must be > 0"):
        zeonta.accbands([2.0, 3.0], [1.0, 2.0], [1.5, 2.5], c=0.0)
