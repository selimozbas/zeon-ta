"""Vectorised rolling-window helpers.

Every helper returns an array the same length as its input, with the first
``length - 1`` bars set to ``NaN``. Windows are built with
``numpy.lib.stride_tricks.sliding_window_view``, so a ``NaN`` anywhere in a
window naturally propagates to that bar's result — exactly the warm-up
behaviour the public API promises.
"""

from __future__ import annotations

from typing import NamedTuple

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

__all__ = [
    "LinregResult",
    "rolling_linreg",
    "rolling_max",
    "rolling_mean",
    "rolling_mean_abs_dev",
    "rolling_min",
    "rolling_std",
    "rolling_sum",
]


def _windows(values: np.ndarray, length: int) -> np.ndarray:
    """Return the (n - length + 1, length) sliding-window view of *values*."""
    return sliding_window_view(values, length)


def _blank(values: np.ndarray) -> np.ndarray:
    return np.full(values.shape[0], np.nan, dtype="float64")


def _apply(values: np.ndarray, length: int, reducer: str) -> np.ndarray:
    out = _blank(values)
    if values.shape[0] < length:
        return out
    windows = _windows(values, length)
    out[length - 1 :] = getattr(windows, reducer)(axis=1)
    return out


def rolling_mean(values: np.ndarray, length: int) -> np.ndarray:
    """Simple moving average."""
    return _apply(values, length, "mean")


def rolling_sum(values: np.ndarray, length: int) -> np.ndarray:
    """Rolling sum."""
    return _apply(values, length, "sum")


def rolling_max(values: np.ndarray, length: int) -> np.ndarray:
    """Rolling maximum (highest high)."""
    return _apply(values, length, "max")


def rolling_min(values: np.ndarray, length: int) -> np.ndarray:
    """Rolling minimum (lowest low)."""
    return _apply(values, length, "min")


def rolling_std(values: np.ndarray, length: int, ddof: int = 0) -> np.ndarray:
    """Rolling standard deviation.

    ``ddof=0`` (population) is the default because that is what charting
    platforms use for Bollinger Bands; pass ``ddof=1`` for the sample estimate.
    """
    out = _blank(values)
    if values.shape[0] < length:
        return out
    if length - ddof <= 0:
        raise ValueError(f"'length' must be greater than ddof={ddof}, got {length}")
    out[length - 1 :] = _windows(values, length).std(axis=1, ddof=ddof)
    return out


def rolling_mean_abs_dev(values: np.ndarray, length: int) -> np.ndarray:
    """Rolling mean absolute deviation about the window mean (used by CCI)."""
    out = _blank(values)
    if values.shape[0] < length:
        return out
    windows = _windows(values, length)
    means = windows.mean(axis=1, keepdims=True)
    out[length - 1 :] = np.abs(windows - means).mean(axis=1)
    return out


class LinregResult(NamedTuple):
    """Rolling regression outputs, one array per statistic."""

    slope: np.ndarray
    intercept: np.ndarray
    endpoint: np.ndarray
    residual_std: np.ndarray


def rolling_linreg(values: np.ndarray, length: int) -> LinregResult:
    """Rolling ordinary-least-squares fit over ``x = 0 .. length - 1``.

    ``endpoint`` is the fitted value at the most recent bar of each window, i.e.
    ``intercept + slope * (length - 1)`` — what linear-regression channels and
    the TTM Squeeze momentum histogram plot.

    ``residual_std`` is the population standard deviation of the window's points
    **about the fitted line**, not about their mean. That distinction matters:
    a regression channel is meant to measure scatter around the trend, and in a
    steep trend the deviation about the mean is dominated by the trend itself.
    """
    slope = _blank(values)
    intercept = _blank(values)
    endpoint = _blank(values)
    residual_std = _blank(values)
    if values.shape[0] < length:
        return LinregResult(slope, intercept, endpoint, residual_std)
    if length < 2:
        raise ValueError(f"'length' must be >= 2 for a linear regression, got {length}")

    x = np.arange(length, dtype="float64")
    sum_x = x.sum()
    sum_xx = (x * x).sum()
    denominator = length * sum_xx - sum_x * sum_x

    windows = _windows(values, length)
    sum_y = windows.sum(axis=1)
    sum_xy = windows @ x

    window_slope = (length * sum_xy - sum_x * sum_y) / denominator
    window_intercept = (sum_y - window_slope * sum_x) / length
    fitted = window_intercept[:, None] + window_slope[:, None] * x[None, :]
    residuals = windows - fitted

    slope[length - 1 :] = window_slope
    intercept[length - 1 :] = window_intercept
    endpoint[length - 1 :] = window_intercept + window_slope * (length - 1)
    residual_std[length - 1 :] = np.sqrt((residuals * residuals).mean(axis=1))
    return LinregResult(slope, intercept, endpoint, residual_std)
