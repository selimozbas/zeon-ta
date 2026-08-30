"""The three promises the whole library makes, checked against every indicator.

If one of these breaks, user code silently misaligns rather than erroring — which
is why they get their own generic test rather than being spot-checked per module.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
import pytest

import zeonta
from helpers import as_frames, call_spec
from zeonta._core import IndicatorSpec, iter_specs

#: Early enough in the 300-bar fixture that even the slowest default window
#: in the registry (``ma_cross``'s 200-bar SMA) has room to fully clear the
#: gap and still leave finite bars in the tail to check.
GAP_INDEX = 30


def test_registry_covers_every_standard_indicator() -> None:
    """The core set of well-known indicators must all be implemented — no more,
    no fewer. ``lesson`` is purely an internal category slug (no public URL).

    A smaller set of indicators (OBV, CMF, MFI, ROC, Momentum, KAMA, Parabolic
    SAR) carry ``reference`` instead of ``lesson`` and are excluded from this
    set on purpose; see ``test_indicators_with_a_reference``.
    """
    lessons = {spec.lesson for spec in iter_specs() if spec.lesson is not None}
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
        "divergences",
    }


def test_indicators_with_a_reference() -> None:
    """The minority of indicators that cite an external source, and only those."""
    expected = {
        "obv",
        "cmf",
        "mfi",
        "roc",
        "momentum",
        "kama",
        "parabolic_sar",
        "wma",
        "adl",
        "aroon",
        "williams_r",
        "stoch_rsi",
        "awesome_oscillator",
        "hma",
        "dema",
        "tema",
        "chaikin_oscillator",
        "chandelier_exit",
        "vortex",
        "ultimate_oscillator",
        "elder_ray",
        "pivot_points",
        "smma",
        "trix",
        "ppo",
        "tsi",
        "dpo",
        "coppock_curve",
        "force_index",
        "ease_of_movement",
        "ulcer_index",
        "linreg",
        "t3",
        "fisher_transform",
        "super_smoother",
        "instantaneous_trendline",
        "hurst_exponent",
        "wavelet_denoise",
        "wavelet_variance",
        "ou_half_life",
        "dfa",
        "sample_entropy",
        "emd_imf1",
        "stddev",
        "variance",
        "zscore",
        "skewness",
        "kurtosis",
        "mad",
        "log_return",
        "cumulative_return",
        "bop",
        "pvt",
        "nvi",
        "pvi",
        "vwma",
        "zlema",
        "alma",
        "mcgd",
        "natr",
        "mass_index",
        "choppiness_index",
        "vertical_horizontal_filter",
        "cmo",
        "drawdown",
        "trima",
        "vidya",
        "efficiency_ratio",
        "center_of_gravity",
        "laguerre_rsi",
        "kst",
        "rvgi",
        "smi",
        "chaikin_volatility",
        "relative_volatility_index",
        "klinger_volume_oscillator",
        "williams_ad",
        "heikin_ashi",
        "adxr",
        "qstick",
        "accbands",
        "bias",
        "psl",
        "cpr",
        "vwmacd",
        "kdj",
        "qqe",
    }
    with_reference = {spec.name for spec in iter_specs() if spec.reference is not None}
    assert with_reference == expected
    for spec in iter_specs():
        if spec.name in expected:
            assert spec.lesson is None
            assert spec.reference is not None
            assert spec.reference.startswith("https://")
            assert spec.url == spec.reference
        else:
            assert spec.url is None


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


def test_misaligned_series_indices_are_rejected(spec: IndicatorSpec, ohlcv: pd.DataFrame) -> None:
    """Same-length Series from different date ranges must not be combined positionally.

    Two Series can have identical length while covering entirely different
    periods; without an explicit check they would silently line up bar N with
    bar N regardless of what date each one actually is.
    """
    if len(spec.inputs) < 2:
        pytest.skip("single-input indicator has nothing to misalign")
    series = [ohlcv[field] for field in spec.inputs]
    shifted_index = pd.RangeIndex(1000, 1000 + len(ohlcv))
    series[-1] = series[-1].set_axis(shifted_index)
    with pytest.raises(ValueError, match="different indices"):
        spec.func(*series)


def _inject_gap(frame: pd.DataFrame, spec: IndicatorSpec, index: int) -> pd.DataFrame:
    """*frame* with every one of *spec*'s required input columns set to ``NaN``
    at *index* — a single fully missing OHLCV bar, the realistic worst case
    a bad data feed produces."""
    gapped = frame.copy()
    for field in spec.inputs:
        gapped.iloc[index, gapped.columns.get_loc(field)] = np.nan
    return gapped


def test_a_missing_bar_raises_no_warnings(spec: IndicatorSpec, ohlcv: pd.DataFrame) -> None:
    """A single missing OHLCV bar is ordinary, real-world bad data, not a
    reason to pollute a caller's logs with a ``RuntimeWarning`` — the same
    class of bug ``true_range()`` had (an all-``NaN`` slice warning from
    ``np.nanmax`` on a fully missing bar) before it was fixed."""
    if spec.name == "vwap":
        pytest.skip("session VWAP needs a DatetimeIndex; not exercised with a plain gap here")
    gapped = _inject_gap(ohlcv, spec, GAP_INDEX)
    with warnings.catch_warnings():
        warnings.simplefilter("error", category=RuntimeWarning)
        call_spec(spec, gapped)


def test_a_missing_bar_does_not_poison_every_later_bar(
    spec: IndicatorSpec, ohlcv: pd.DataFrame
) -> None:
    """A single missing bar must have a *bounded* effect: once enough clean
    bars have accumulated after it, every output column must recover and
    produce a finite value again somewhere in the remaining 199 bars — not
    stay ``NaN`` forever. This is the exact shape of two bugs already found
    this way: ``adl()``'s running total went permanently ``NaN`` because
    ``np.cumsum`` propagated one gap's ``NaN`` through every later bar, and
    ``aroon()`` did the mirror-image wrong thing (a finite-looking but
    meaningless value instead of ``NaN``) because ``argmax``/``argmin`` treat
    a ``NaN`` in the window as if it were the extreme rather than excluding
    it. Both are fixed; this test is what would have caught them.
    """
    if spec.name == "vwap":
        pytest.skip("session VWAP needs a DatetimeIndex; not exercised with a plain gap here")
    gapped = _inject_gap(ohlcv, spec, GAP_INDEX)
    result = call_spec(spec, gapped)
    for name, series in as_frames(result).items():
        tail = series.iloc[GAP_INDEX + 1 :]
        assert tail.notna().any(), f"{spec.name}.{name}: NaN forever after the gap"


def test_constant_input_does_not_raise_or_warn(spec: IndicatorSpec, ohlcv: pd.DataFrame) -> None:
    """A perfectly flat market (every OHLCV value identical) is a degenerate
    but legal input. Formulas shaped like a ratio or a deviation must handle
    the resulting zero range/zero variance via an explicit branch, not an
    uncaught exception or a division-by-zero warning."""
    if spec.name == "vwap":
        pytest.skip("session VWAP needs a DatetimeIndex; not exercised with flat input here")
    flat = pd.DataFrame(
        {column: (1000.0 if column == "volume" else 100.0) for column in ohlcv.columns},
        index=ohlcv.index,
    )
    with warnings.catch_warnings():
        warnings.simplefilter("error", category=RuntimeWarning)
        call_spec(spec, flat)


def test_zero_volume_does_not_raise(spec: IndicatorSpec, ohlcv: pd.DataFrame) -> None:
    if "volume" not in spec.inputs:
        pytest.skip("no volume input")
    if spec.name == "vwap":
        pytest.skip("session VWAP needs a DatetimeIndex; not exercised with zero volume here")
    zeroed = ohlcv.copy()
    zeroed["volume"] = 0.0
    call_spec(spec, zeroed)


def test_negative_volume_is_rejected(spec: IndicatorSpec, ohlcv: pd.DataFrame) -> None:
    if "volume" not in spec.inputs:
        pytest.skip("no volume input")
    negative = ohlcv.copy()
    negative.iloc[10, negative.columns.get_loc("volume")] = -1.0
    with pytest.raises(ValueError, match="'volume' must not contain negative values"):
        call_spec(spec, negative)


def test_list_indicators_matches_registry() -> None:
    table = zeonta.list_indicators()
    assert list(table["name"]) == [spec.name for spec in iter_specs()]
    assert not table["summary"].str.strip().eq("").any()
    for spec in iter_specs():
        row = table.loc[table["name"] == spec.name, "source"].iloc[0]
        if spec.url is None:
            assert pd.isna(row), spec.name
        else:
            assert row == spec.url and row.startswith("https://"), spec.name


def test_public_api_is_exported() -> None:
    for spec in iter_specs():
        assert spec.name in zeonta.__all__, spec.name
        assert getattr(zeonta, spec.name) is spec.func
