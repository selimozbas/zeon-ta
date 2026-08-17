"""Internal building blocks. Not part of the public API — contents may change."""

from .registry import OHLCV_FIELDS, IndicatorSpec, get_spec, indicator, iter_specs, lesson_url
from .rolling import (
    rolling_linreg,
    rolling_max,
    rolling_mean,
    rolling_mean_abs_dev,
    rolling_min,
    rolling_std,
    rolling_sum,
)
from .smoothing import ema_values, first_full_window, wilder_values
from .types import ArrayLike, Number
from .validation import (
    as_array,
    common_index,
    require_same_length,
    validate_length,
    validate_multiplier,
    wrap_frame,
    wrap_series,
)

__all__ = [
    "OHLCV_FIELDS",
    "ArrayLike",
    "IndicatorSpec",
    "Number",
    "as_array",
    "common_index",
    "ema_values",
    "first_full_window",
    "get_spec",
    "indicator",
    "iter_specs",
    "lesson_url",
    "require_same_length",
    "rolling_linreg",
    "rolling_max",
    "rolling_mean",
    "rolling_mean_abs_dev",
    "rolling_min",
    "rolling_std",
    "rolling_sum",
    "validate_length",
    "validate_multiplier",
    "wilder_values",
    "wrap_frame",
    "wrap_series",
]
