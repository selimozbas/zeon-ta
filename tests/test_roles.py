"""``frame.attrs["roles"]`` — stable, parameter-free column lookup.

Every multi-output indicator's ``pd.DataFrame`` bakes its call parameters into
its column names (``MACDh_12_26_9``), which is deliberate — it avoids column
collisions when the same indicator is combined twice with different
parameters. ``roles`` is the parameter-free escape hatch: a fixed map from a
semantic name (``"histogram"``) to whatever the actual column happens to be
called for that call, retrievable through :func:`zeonta.role`.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import zeonta
from helpers import call_spec
from zeonta._core import iter_specs, wrap_frame

# A representative sample of indicators this feature was added to, each with
# one role picked from the ones assigned to it in the source.
ROLE_SAMPLES = [
    ("macd", "signal"),
    ("bbands", "middle"),
    ("supertrend", "direction"),
    ("adx", "plus_di"),
    ("donchian", "upper"),
    ("kdj", "j"),
    ("ichimoku", "lagging"),
    ("ppo", "histogram"),
    ("aroon", "oscillator"),
    ("vwap", "line"),
]


@pytest.mark.parametrize("name, role_name", ROLE_SAMPLES)
def test_role_map_matches_frame_columns(name: str, role_name: str, ohlcv: pd.DataFrame) -> None:
    spec = zeonta.get_spec(name)
    result = call_spec(spec, ohlcv)
    frame = result[0] if isinstance(result, tuple) else result

    assert isinstance(frame, pd.DataFrame)
    roles = frame.attrs["roles"]
    assert set(roles.values()) <= set(frame.columns)

    column = roles[role_name]
    pd.testing.assert_series_equal(zeonta.role(frame, role_name), frame[column], check_names=True)


def test_role_raises_key_error_for_unknown_role(ohlcv: pd.DataFrame) -> None:
    frame = zeonta.macd(ohlcv["close"])
    with pytest.raises(KeyError):
        zeonta.role(frame, "not_a_real_role")


def test_role_raises_key_error_on_a_plain_series(ohlcv: pd.DataFrame) -> None:
    """A single-output Series (e.g. RSI) carries no role map at all."""
    series = zeonta.rsi(ohlcv["close"])
    assert isinstance(series, pd.Series)
    assert series.attrs.get("roles") is None
    with pytest.raises(KeyError):
        zeonta.role(series, "anything")


def test_wrap_frame_rejects_a_role_pointing_at_an_unknown_column() -> None:
    """A role mapping to a column that isn't actually one of the frame's own
    columns is a programming error in the indicator that called ``wrap_frame``,
    not user input — it must fail loudly rather than silently keying to
    nothing."""
    with pytest.raises(ValueError, match="not one of"):
        wrap_frame(
            {"A": np.array([1.0, 2.0])},
            None,
            order=["A"],
            roles={"line": "NOT_A_COLUMN"},
        )


def test_every_role_map_is_internally_consistent(ohlcv: pd.DataFrame) -> None:
    """For every registered indicator that returns a DataFrame and carries a
    role map, every role must point at one of that frame's actual columns."""
    checked_at_least_one = False
    for spec in iter_specs():
        if not spec.returns_frame:
            continue
        result = call_spec(spec, ohlcv)
        frame = result[0] if isinstance(result, tuple) else result
        roles = frame.attrs.get("roles")
        if not roles:
            # Deliberately skipped: variable column count (ema_ribbon, gmma,
            # wavelet_variance) or a ratio-list-sized output (fib_retracement).
            continue
        checked_at_least_one = True
        assert set(roles.values()) <= set(frame.columns), spec.name
        for role_name in roles:
            pd.testing.assert_series_equal(
                zeonta.role(frame, role_name), frame[roles[role_name]], check_names=True
            )
    assert checked_at_least_one
