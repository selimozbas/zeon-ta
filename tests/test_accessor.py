"""The ``.zta`` accessor must be a pure routing layer with no maths of its own."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import zeonta
from helpers import as_frames, call_spec
from zeonta._core import IndicatorSpec


def test_accessor_matches_the_functional_call(spec: IndicatorSpec, ohlcv: pd.DataFrame) -> None:
    """Every indicator must give identical numbers through both entry points."""
    direct = as_frames(call_spec(spec, ohlcv))
    through_accessor = as_frames(getattr(ohlcv.zta, spec.name)())
    assert direct.keys() == through_accessor.keys(), spec.name
    for name, series in direct.items():
        pd.testing.assert_series_equal(series, through_accessor[name])


def test_accessor_forwards_positional_arguments(ohlcv: pd.DataFrame) -> None:
    pd.testing.assert_series_equal(ohlcv.zta.sma(5), zeonta.sma(ohlcv["close"], 5))


def test_accessor_forwards_keyword_arguments(ohlcv: pd.DataFrame) -> None:
    pd.testing.assert_series_equal(ohlcv.zta.rsi(length=7), zeonta.rsi(ohlcv["close"], length=7))


def test_accessor_matches_columns_case_insensitively(ohlcv: pd.DataFrame) -> None:
    upper = ohlcv.rename(columns=str.upper)
    np.testing.assert_allclose(upper.zta.sma(10), ohlcv.zta.sma(10), equal_nan=True)


def test_accessor_reports_a_missing_column_usefully() -> None:
    frame = pd.DataFrame({"close": [1.0, 2.0, 3.0]})
    with pytest.raises(KeyError, match="needs a 'high' column"):
        frame.zta.atr()


def test_accessor_rejects_unknown_indicators(ohlcv: pd.DataFrame) -> None:
    with pytest.raises(AttributeError, match="unknown indicator"):
        ohlcv.zta.triple_witching_hour()


def test_accessor_is_discoverable(ohlcv: pd.DataFrame) -> None:
    listed = dir(ohlcv.zta)
    assert "supertrend" in listed
    assert "ichimoku" in listed


def test_accessor_carries_the_function_docstring(ohlcv: pd.DataFrame) -> None:
    assert ohlcv.zta.rsi.__doc__ == zeonta.rsi.__doc__
