"""Statistics — golden values traced by hand, and cross-checks against pandas'
own rolling .skew()/.kurt() for the two indicators built to match them exactly.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import zeonta


def test_stddev_matches_the_hand_computed_population_std() -> None:
    result = zeonta.stddev([1.0, 2.0, 3.0, 4.0], length=4)
    np.testing.assert_allclose(result.iloc[-1], np.std([1.0, 2.0, 3.0, 4.0], ddof=0))


def test_stddev_supports_sample_ddof() -> None:
    result = zeonta.stddev([1.0, 2.0, 3.0, 4.0], length=4, ddof=1)
    np.testing.assert_allclose(result.iloc[-1], np.std([1.0, 2.0, 3.0, 4.0], ddof=1))


def test_variance_is_stddev_squared() -> None:
    values = [1.0, 5.0, 2.0, 8.0, 3.0, 9.0]
    std = zeonta.stddev(values, length=4)
    var = zeonta.variance(values, length=4)
    np.testing.assert_allclose(var.dropna().to_numpy(), (std.dropna() ** 2).to_numpy())


def test_zscore_is_zero_when_price_equals_the_rolling_mean() -> None:
    values = [10.0, 12.0, 8.0, 10.0]
    result = zeonta.zscore(values, length=4)
    np.testing.assert_allclose(result.iloc[-1], 0.0, atol=1e-12)


def test_zscore_is_nan_on_a_flat_window() -> None:
    result = zeonta.zscore([5.0] * 20, length=10)
    assert result.dropna().empty


def test_skewness_matches_pandas_own_rolling_skew() -> None:
    rng = np.random.default_rng(0)
    values = pd.Series(rng.normal(size=60))
    ours = zeonta.skewness(values, length=15)
    theirs = values.rolling(15).skew()
    np.testing.assert_allclose(ours.dropna().to_numpy(), theirs.dropna().to_numpy())


def test_kurtosis_matches_pandas_own_rolling_kurt() -> None:
    rng = np.random.default_rng(1)
    values = pd.Series(rng.normal(size=60))
    ours = zeonta.kurtosis(values, length=15)
    theirs = values.rolling(15).kurt()
    np.testing.assert_allclose(ours.dropna().to_numpy(), theirs.dropna().to_numpy())


def test_mad_is_robust_to_a_single_outlier_unlike_stddev() -> None:
    calm = [10.0, 10.1, 9.9, 10.0, 10.05]
    with_outlier = [10.0, 10.1, 9.9, 10.0, 500.0]
    mad_calm = zeonta.mad(calm, length=5).iloc[-1]
    mad_outlier = zeonta.mad(with_outlier, length=5).iloc[-1]
    std_calm = zeonta.stddev(calm, length=5).iloc[-1]
    std_outlier = zeonta.stddev(with_outlier, length=5).iloc[-1]
    assert mad_outlier / mad_calm < std_outlier / std_calm


def test_ffd_matches_a_hand_traced_binomial_weight_recursion() -> None:
    """d=0.5, threshold=0.2 truncates to just two weights: w0=1, w1=-0.5
    (w2 = -w1*(0.5-1)/2 = -0.125, whose magnitude is below the threshold and
    so is not kept). FFD[t] is then just Close[t] - 0.5*Close[t-1]."""
    closes = [100.0, 101.0, 99.0, 102.0]
    result = zeonta.ffd(closes, d=0.5, threshold=0.2)
    expected = [np.nan, 101.0 - 0.5 * 100.0, 99.0 - 0.5 * 101.0, 102.0 - 0.5 * 99.0]
    np.testing.assert_allclose(result.to_numpy(), expected)


def test_ffd_preserves_more_correlation_than_plain_differencing() -> None:
    """The whole point of fractional (vs. integer) differencing: on a
    long-memory (random-walk) series, FFD's output should still track the
    original level far more closely than a plain first difference does."""
    rng = np.random.default_rng(2)
    raw = 100.0 + np.cumsum(rng.normal(size=2000))

    ffd_values = zeonta.ffd(raw, d=0.4, threshold=1e-4).to_numpy()
    diff_values = np.diff(raw, prepend=np.nan)

    valid = ~np.isnan(ffd_values)
    corr_ffd = np.corrcoef(raw[valid], ffd_values[valid])[0, 1]
    corr_diff = np.corrcoef(raw[valid], diff_values[valid])[0, 1]
    assert corr_ffd > corr_diff


def test_ffd_short_input_is_all_nan_not_an_error() -> None:
    result = zeonta.ffd([1.0, 2.0, 3.0])  # default threshold needs far more than 3 bars
    assert len(result) == 3
    assert result.isna().all()


@pytest.mark.parametrize("bad_d", [0.0, 1.0, -0.5, 1.5])
def test_ffd_rejects_d_outside_open_unit_interval(bad_d: float) -> None:
    with pytest.raises(ValueError, match="'d'"):
        zeonta.ffd([1.0, 2.0, 3.0], d=bad_d)


@pytest.mark.parametrize("bad_threshold", [0.0, 1.0, -0.1, 1.1])
def test_ffd_rejects_threshold_outside_open_unit_interval(bad_threshold: float) -> None:
    with pytest.raises(ValueError, match="'threshold'"):
        zeonta.ffd([1.0, 2.0, 3.0], threshold=bad_threshold)


def test_log_return_matches_the_hand_computed_value() -> None:
    result = zeonta.log_return([100.0, 110.0, 121.0], length=1)
    np.testing.assert_allclose(result.dropna().to_numpy(), [np.log(1.1), np.log(1.1)])


def test_log_return_is_additive_across_bars() -> None:
    """The whole reason to prefer this over roc(): summing single-bar log
    returns over a window equals the log return over the whole window."""
    values = [100.0, 105.0, 98.0, 112.0]
    single_bar = zeonta.log_return(values, length=1).dropna()
    whole_window = zeonta.log_return(values, length=3).dropna()
    np.testing.assert_allclose(single_bar.sum(), whole_window.iloc[-1])


def test_cumulative_return_is_zero_on_the_first_bar() -> None:
    result = zeonta.cumulative_return([100.0, 110.0, 90.0])
    assert result.iloc[0] == 0.0


def test_cumulative_return_matches_the_hand_computed_percentage() -> None:
    result = zeonta.cumulative_return([100.0, 110.0, 90.0])
    np.testing.assert_allclose(result.to_numpy(), [0.0, 10.0, -10.0])


def test_cumulative_return_changes_every_earlier_value_with_more_history() -> None:
    """Documented, deliberate behaviour: unlike every length-windowed
    indicator here, prepending history moves the anchor (bar 0) and so
    changes every previously computed value."""
    short = zeonta.cumulative_return([100.0, 110.0, 90.0])
    longer = zeonta.cumulative_return([50.0, 100.0, 110.0, 90.0])
    assert not np.allclose(short.to_numpy(), longer.iloc[1:].to_numpy())


def test_skewness_rejects_a_window_below_three() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.skewness([1.0, 2.0, 3.0], length=2)


def test_kurtosis_rejects_a_window_below_four() -> None:
    with pytest.raises(ValueError, match="must be >="):
        zeonta.kurtosis([1.0, 2.0, 3.0, 4.0], length=3)


def test_drawdown_is_zero_at_every_new_high() -> None:
    result = zeonta.drawdown([10.0, 12.0, 15.0, 20.0])
    np.testing.assert_allclose(result.to_numpy(), [0.0, 0.0, 0.0, 0.0])


def test_drawdown_matches_the_hand_computed_percentage_from_the_running_peak() -> None:
    result = zeonta.drawdown([10.0, 12.0, 11.0, 15.0, 9.0])
    np.testing.assert_allclose(result.to_numpy(), [0.0, 0.0, -8.333333333333334, 0.0, -40.0])


def test_drawdown_survives_a_gap_by_holding_the_last_real_peak() -> None:
    """Regression guard for the ``np.maximum.accumulate`` bug class already
    fixed in ``adl()``: one missing bar must not poison every later running
    peak with ``NaN`` forever."""
    values = [10.0, 12.0, np.nan, 8.0, 15.0]
    result = zeonta.drawdown(values)
    assert np.isnan(result.iloc[2])
    np.testing.assert_allclose(result.iloc[3], (8.0 - 12.0) / 12.0 * 100.0)
    np.testing.assert_allclose(result.iloc[4], 0.0)
