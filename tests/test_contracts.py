"""The three promises the whole library makes, checked against every indicator.

If one of these breaks, user code silently misaligns rather than erroring — which
is why they get their own generic test rather than being spot-checked per module.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import zeonta
from helpers import as_frames, call_spec
from zeonta._core import IndicatorSpec, iter_specs


def test_registry_covers_every_curriculum_lesson() -> None:
    lessons = {spec.lesson for spec in iter_specs()}
    assert lessons == {
        "candlesticks",
        "support-resistance",
        "trend-basics",
        "volume-basics",
        "sma",
        "ema",
        "ma-crossovers",
        "ema-ribbon",
        "rsi",
        "stochastic",
        "macd",
        "cci",
        "bollinger-bands",
        "atr",
        "keltner-channels",
        "squeeze",
        "supertrend",
        "adx-dmi",
        "ichimoku",
        "donchian-channels",
        "vwap",
        "fibonacci",
        "pivot-points",
        "divergences",
    }


def test_length_is_preserved(spec: IndicatorSpec, ohlcv: pd.DataFrame) -> None:
    """An indicator never trims its warm-up; results stay bar-aligned with input."""
    for series in as_frames(call_spec(spec, ohlcv)).values():
        assert len(series) == len(ohlcv), spec.name


def test_index_is_preserved(spec: IndicatorSpec, ohlcv: pd.DataFrame) -> None:
    for series in as_frames(call_spec(spec, ohlcv)).values():
        pd.testing.assert_index_equal(series.index, ohlcv.index)


def test_output_is_pandas_and_float(spec: IndicatorSpec, ohlcv: pd.DataFrame) -> None:
    result = call_spec(spec, ohlcv)
    primary = result[0] if isinstance(result, tuple) else result
    expected = pd.DataFrame if spec.returns_frame else pd.Series
    assert isinstance(primary, expected), spec.name
    for series in as_frames(result).values():
        assert series.dtype == np.float64, f"{spec.name}: {series.name}"


def test_input_types_are_equivalent(spec: IndicatorSpec, ohlcv: pd.DataFrame) -> None:
    """Series, ndarray and list inputs must produce identical numbers."""
    if spec.name == "vwap":
        pytest.skip("session VWAP needs a DatetimeIndex; covered in test_advanced")

    from_series = as_frames(call_spec(spec, ohlcv))
    arrays = ohlcv.copy()
    from_arrays = as_frames(spec.func(*[arrays[field].to_numpy() for field in spec.inputs]))
    from_lists = as_frames(spec.func(*[list(arrays[field]) for field in spec.inputs]))

    for name, series in from_series.items():
        for other in (from_arrays[name], from_lists[name]):
            np.testing.assert_allclose(
                series.to_numpy(), other.to_numpy(), rtol=0, atol=0, err_msg=f"{spec.name}.{name}"
            )


def test_short_input_does_not_raise(spec: IndicatorSpec, ohlcv: pd.DataFrame) -> None:
    """Fewer bars than the look-back yields all-NaN, not an exception."""
    tiny = ohlcv.iloc[:3]
    if spec.name == "vwap":
        pytest.skip("covered separately: rolling VWAP over 3 bars is exercised in test_advanced")
    for series in as_frames(call_spec(spec, tiny)).values():
        assert len(series) == 3, spec.name


def test_empty_input_is_rejected(spec: IndicatorSpec, ohlcv: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        call_spec(spec, ohlcv.iloc[:0])


def test_mismatched_lengths_are_rejected(spec: IndicatorSpec, ohlcv: pd.DataFrame) -> None:
    if len(spec.inputs) < 2:
        pytest.skip("single-input indicator cannot mismatch")
    series = [ohlcv[field].to_numpy() for field in spec.inputs]
    series[-1] = series[-1][:-1]
    with pytest.raises(ValueError, match="same length"):
        spec.func(*series)


def test_list_indicators_matches_registry() -> None:
    table = zeonta.list_indicators()
    assert list(table["name"]) == [spec.name for spec in iter_specs()]
    assert not table["summary"].str.strip().eq("").any()
    assert table["lesson"].str.startswith("https://ta.cognicode.org/learn/").all()


def test_public_api_is_exported() -> None:
    for spec in iter_specs():
        assert spec.name in zeonta.__all__, spec.name
        assert getattr(zeonta, spec.name) is spec.func
