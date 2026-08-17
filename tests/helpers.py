"""Small utilities shared by the test modules."""

from __future__ import annotations

from typing import Any

import pandas as pd

from zeonta._core import IndicatorSpec


def call_spec(spec: IndicatorSpec, frame: pd.DataFrame, **kwargs: Any) -> Any:
    """Invoke an indicator with the columns it declared it needs."""
    series = [frame[field] for field in spec.inputs]
    return spec.func(*series, **kwargs)


def as_frames(result: Any) -> dict[str, pd.Series]:
    """Flatten any indicator result into ``{column name: Series}``."""
    if isinstance(result, tuple):
        result = result[0]
    if isinstance(result, pd.Series):
        return {str(result.name): result}
    return {str(name): result[name] for name in result.columns}
