"""Registration rules and the error paths users actually hit.

The ``indicator`` decorator derives an indicator's inputs and parameters from its
signature, which is what keeps the registry, the accessor and the documentation
honest. These tests pin down the cases where it must refuse to register.
"""

from __future__ import annotations

from collections.abc import Iterator

import numpy as np
import pandas as pd
import pytest

import zeonta
from zeonta._core import ema_values, get_spec, indicator, wilder_values
from zeonta._core import registry as registry_module
from zeonta._core.rolling import rolling_std
from zeonta._core.validation import validate_multiplier


@pytest.fixture(autouse=True)
def isolated_registry() -> Iterator[None]:
    """Undo any registration a test performs.

    Without this, a test indicator would leak into ``iter_specs()`` and make
    unrelated tests (and the documentation check) pass or fail depending on the
    order pytest happened to run them in.
    """
    snapshot = dict(registry_module._REGISTRY)
    try:
        yield
    finally:
        registry_module._REGISTRY.clear()
        registry_module._REGISTRY.update(snapshot)


class TestRegistration:
    def test_lesson_and_reference_are_mutually_exclusive(self) -> None:
        """The ``indicator`` decorator always passes a valid combination; this
        pins the ``IndicatorSpec`` invariant it relies on directly."""
        from zeonta._core.registry import IndicatorSpec

        def dummy(close: pd.Series) -> pd.Series:  # pragma: no cover - never called
            return close

        with pytest.raises(ValueError, match="mutually exclusive"):
            IndicatorSpec(
                name="dummy",
                category="x",
                summary="s",
                lesson="rsi",
                reference="https://example.com",
                inputs=("close",),
                params={},
                outputs=("O",),
                returns_frame=False,
                func=dummy,
            )

    def test_neither_lesson_nor_reference_is_allowed(self) -> None:
        """An indicator citing no source at all (internal category only) is valid."""
        from zeonta._core.registry import IndicatorSpec

        def dummy(close: pd.Series) -> pd.Series:  # pragma: no cover - never called
            return close

        spec = IndicatorSpec(
            name="dummy",
            category="x",
            summary="s",
            lesson=None,
            reference=None,
            inputs=("close",),
            params={},
            outputs=("O",),
            returns_frame=False,
            func=dummy,
        )
        assert spec.url is None

    def test_a_parameter_without_a_default_is_rejected(self) -> None:
        with pytest.raises(TypeError, match="must either be an OHLCV input"):

            @indicator(category="x", summary="s", lesson="l", outputs=("O",))
            def missing_default(close: pd.Series, length: int) -> pd.Series:  # pragma: no cover
                return close

    def test_an_indicator_with_no_ohlcv_input_is_rejected(self) -> None:
        with pytest.raises(TypeError, match="at least one OHLCV input"):

            @indicator(category="x", summary="s", lesson="l", outputs=("O",))
            def no_inputs(length: int = 5) -> pd.Series:  # pragma: no cover
                return pd.Series([1.0])

    def test_a_duplicate_name_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="already registered"):

            @indicator(category="x", summary="s", lesson="l", outputs=("O",), name="rsi")
            def duplicate(close: pd.Series) -> pd.Series:  # pragma: no cover
                return close

    def test_var_args_are_ignored_when_deriving_the_signature(self) -> None:
        @indicator(category="x", summary="s", lesson="l", outputs=("O",), name="_probe")
        def probe(close: pd.Series, length: int = 3, *args: object, **kwargs: object) -> pd.Series:
            return zeonta.sma(close, length)

        spec = get_spec("_probe")
        assert spec.inputs == ("close",)
        assert spec.params == {"length": 3}

    def test_unknown_indicator_lookup_lists_the_alternatives(self) -> None:
        with pytest.raises(KeyError, match="available:"):
            get_spec("triple_witching_hour")


class TestAccessorInternals:
    def test_private_attributes_are_not_treated_as_indicators(self) -> None:
        """pandas probes for private attributes; those must raise plainly, not look up."""
        frame = pd.DataFrame({"close": [1.0, 2.0, 3.0]})
        with pytest.raises(AttributeError):
            getattr(frame.zta, "_repr_html_")  # noqa: B009 - the lookup itself is the test


class TestEdgeCases:
    def test_smoothers_carry_across_an_interior_gap(self) -> None:
        """A NaN mid-series must not poison every value after it."""
        values = np.array([1.0, 2.0, 3.0, np.nan, 5.0, 6.0])
        for smoother in (ema_values, wilder_values):
            result = smoother(values, 3)
            assert np.isfinite(result[-1]), smoother.__name__
            # The gap bar holds the previous value rather than a fresh computation.
            assert result[3] == result[2]

    def test_rolling_std_rejects_a_ddof_that_exceeds_the_window(self) -> None:
        with pytest.raises(ValueError, match="greater than ddof"):
            rolling_std(np.arange(10.0), 1, ddof=1)

    def test_multiplier_rejects_a_non_numeric_value(self) -> None:
        with pytest.raises(ValueError, match="must be a number"):
            validate_multiplier("2.0")  # type: ignore[arg-type]

    def test_hidden_bullish_divergence_is_detected(self) -> None:
        """Price makes a higher low while the oscillator makes a lower low."""
        lows = np.array([9, 8, 4, 8, 9, 8, 5, 8, 9], dtype=float)
        osc = np.array([50, 40, 30, 40, 50, 40, 20, 40, 50], dtype=float)
        out = zeonta.divergence(lows + 1, lows, lows, oscillator=osc, left=2, right=2)
        assert out["DIVHIDBULL_2_2"].iloc[6] == 1.0

    def test_pivots_ignore_bars_with_missing_prices(self) -> None:
        highs = np.array([1.0, 2.0, np.nan, 2.0, 1.0, 2.0, 5.0, 2.0, 1.0])
        out = zeonta.support_resistance(highs, highs - 1, left=2, right=2)
        assert np.isnan(out["PIVOTHIGH_2_2"].iloc[2])
        assert out["PIVOTHIGH_2_2"].iloc[6] == 5.0

    def test_supertrend_on_data_too_short_for_atr_is_all_nan(self) -> None:
        out = zeonta.supertrend([2.0], [1.0], [1.5], length=10)
        assert out.isna().all().all()
