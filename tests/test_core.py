"""Internal building blocks — the shared contracts everything else assumes."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zeonta._core import (
    as_array,
    common_index,
    ema_values,
    first_full_window,
    rolling_linreg,
    rolling_max,
    rolling_mean,
    rolling_mean_abs_dev,
    rolling_std,
    validate_length,
    validate_multiplier,
    wilder_values,
    wrap_series,
)


class TestAsArray:
    def test_accepts_series_ndarray_and_list(self) -> None:
        expected = np.array([1.0, 2.0, 3.0])
        for value in (pd.Series(expected), expected, [1, 2, 3], (1, 2, 3)):
            np.testing.assert_allclose(as_array(value, "x"), expected)

    def test_result_is_always_float64(self) -> None:
        assert as_array(np.array([1, 2, 3], dtype="int32"), "x").dtype == np.float64

    def test_does_not_alias_the_caller_series(self) -> None:
        """Mutating our copy must not reach back into the user's data."""
        original = pd.Series([1.0, 2.0, 3.0])
        array = as_array(original, "x")
        array[0] = 99.0
        assert original.iloc[0] == 1.0

    def test_rejects_empty_input(self) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            as_array([], "close")

    def test_rejects_two_dimensional_input(self) -> None:
        with pytest.raises(ValueError, match="one-dimensional"):
            as_array(np.zeros((3, 2)), "close")  # type: ignore[arg-type]

    def test_rejects_non_numeric_input(self) -> None:
        with pytest.raises((TypeError, ValueError)):
            as_array(["a", "b"], "close")  # type: ignore[list-item]


class TestValidation:
    def test_length_must_be_a_plain_integer(self) -> None:
        with pytest.raises(ValueError, match="must be an integer"):
            validate_length(True)  # type: ignore[arg-type]

    def test_length_respects_the_minimum(self) -> None:
        with pytest.raises(ValueError, match="must be >= 2"):
            validate_length(1, minimum=2)

    def test_multiplier_rejects_non_finite_values(self) -> None:
        with pytest.raises(ValueError, match="must be finite"):
            validate_multiplier(float("inf"))

    def test_multiplier_rejects_zero(self) -> None:
        with pytest.raises(ValueError, match="must be > 0"):
            validate_multiplier(0.0)

    def test_common_index_finds_the_first_pandas_argument(self) -> None:
        series = pd.Series([1.0], index=["a"])
        assert common_index([1.0], series) is series.index
        assert common_index([1.0], np.array([1.0])) is None

    def test_wrap_series_rejects_a_mismatched_index(self) -> None:
        with pytest.raises(ValueError, match="does not match"):
            wrap_series(np.zeros(3), pd.RangeIndex(5), "X")


class TestRolling:
    def test_mean_matches_pandas(self) -> None:
        values = np.arange(10.0)
        np.testing.assert_allclose(
            rolling_mean(values, 3), pd.Series(values).rolling(3).mean(), equal_nan=True
        )

    def test_warmup_is_exactly_length_minus_one(self) -> None:
        assert np.isnan(rolling_mean(np.arange(10.0), 4)[:3]).all()
        assert np.isfinite(rolling_mean(np.arange(10.0), 4)[3:]).all()

    def test_shorter_input_than_window_is_all_nan(self) -> None:
        assert np.isnan(rolling_max(np.arange(3.0), 5)).all()

    def test_a_nan_poisons_only_the_windows_containing_it(self) -> None:
        values = np.array([1.0, 2.0, np.nan, 4.0, 5.0, 6.0])
        result = rolling_mean(values, 2)
        assert np.isnan(result[2]) and np.isnan(result[3])
        assert np.isfinite(result[4])

    def test_std_defaults_to_the_population_estimate(self) -> None:
        values = np.array([1.0, 2.0, 3.0, 4.0])
        np.testing.assert_allclose(rolling_std(values, 4)[-1], np.std(values))
        np.testing.assert_allclose(rolling_std(values, 4, ddof=1)[-1], np.std(values, ddof=1))

    def test_mean_abs_dev_matches_the_definition(self) -> None:
        values = np.array([1.0, 2.0, 6.0])
        expected = np.abs(values - values.mean()).mean()
        np.testing.assert_allclose(rolling_mean_abs_dev(values, 3)[-1], expected)

    def test_linreg_recovers_a_known_line(self) -> None:
        values = 3.0 + 2.0 * np.arange(20.0)
        slope, intercept, endpoint = rolling_linreg(values, 5)
        np.testing.assert_allclose(slope[-1], 2.0)
        np.testing.assert_allclose(endpoint[-1], values[-1])
        np.testing.assert_allclose(intercept[-1], values[-5])

    def test_linreg_needs_at_least_two_points(self) -> None:
        with pytest.raises(ValueError, match="must be >= 2"):
            rolling_linreg(np.arange(10.0), 1)


class TestSmoothing:
    def test_first_full_window_skips_leading_nans(self) -> None:
        values = np.array([np.nan, np.nan, 1.0, 2.0, 3.0])
        assert first_full_window(values, 3) == 4

    def test_first_full_window_returns_minus_one_when_impossible(self) -> None:
        assert first_full_window(np.array([np.nan, 1.0]), 3) == -1

    def test_ema_alpha_is_two_over_length_plus_one(self) -> None:
        values = np.array([1.0, 2.0, 3.0, 4.0])
        result = ema_values(values, 3)
        # seed = mean(1,2,3) = 2 ; next = 0.5*4 + 0.5*2 = 3
        np.testing.assert_allclose(result[2:], [2.0, 3.0])

    def test_wilder_alpha_is_one_over_length(self) -> None:
        values = np.array([1.0, 2.0, 3.0, 6.0])
        result = wilder_values(values, 3)
        # seed = 2 ; next = (2*2 + 6)/3 = 10/3
        np.testing.assert_allclose(result[3], 10 / 3)

    def test_length_one_returns_the_input(self) -> None:
        values = np.array([1.0, 5.0, 2.0])
        np.testing.assert_allclose(ema_values(values, 1), values)
        np.testing.assert_allclose(wilder_values(values, 1), values)

    def test_both_smoothers_converge_to_a_constant(self) -> None:
        values = np.full(200, 4.0)
        np.testing.assert_allclose(ema_values(values, 20)[-1], 4.0)
        np.testing.assert_allclose(wilder_values(values, 20)[-1], 4.0)

    def test_wilder_is_slower_than_ema_at_the_same_length(self) -> None:
        values = np.concatenate([np.zeros(50), np.ones(20)])
        assert wilder_values(values, 10)[-1] < ema_values(values, 10)[-1]
