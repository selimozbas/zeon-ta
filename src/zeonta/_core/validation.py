"""Input normalisation and parameter validation shared by every indicator.

The whole library rests on three contracts enforced here:

1. **Input tolerance** — ``pd.Series``, ``np.ndarray`` and plain sequences are all
   accepted and normalised to a 1-D ``float64`` array internally.
2. **Pandas output** — results are always ``pd.Series`` / ``pd.DataFrame``. When the
   caller passed a ``pd.Series`` its index is preserved, otherwise a ``RangeIndex``
   is used. Call ``.to_numpy()`` if you want raw arrays back.
3. **Length preservation** — an indicator never trims its output. Bars that cannot
   be computed yet are ``NaN``, so results always align with the input bar-for-bar.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np
import pandas as pd

from .types import ArrayLike, Number

__all__ = [
    "as_array",
    "common_index",
    "require_aligned_index",
    "require_same_length",
    "resolve_role",
    "validate_length",
    "validate_multiplier",
    "wrap_frame",
    "wrap_series",
]


def as_array(values: ArrayLike, name: str) -> np.ndarray:
    """Normalise *values* to a contiguous 1-D ``float64`` array.

    Parameters
    ----------
    values:
        The user-supplied series. ``pd.Series``, ``np.ndarray``, list or tuple.
    name:
        Argument name, used to build actionable error messages.

    Raises
    ------
    ValueError
        If the input is empty or not one-dimensional.
    TypeError
        If the input cannot be interpreted as numeric data.
    """
    if isinstance(values, pd.Series):
        array = values.to_numpy(dtype="float64", copy=True)
    else:
        try:
            array = np.asarray(values, dtype="float64")
        except (TypeError, ValueError) as exc:  # pragma: no cover - message passthrough
            raise TypeError(f"{name!r} must contain numeric values ({exc})") from exc

    if array.ndim != 1:
        raise ValueError(f"{name!r} must be one-dimensional, got {array.ndim} dimensions")
    if array.size == 0:
        raise ValueError(f"{name!r} must not be empty")
    return np.ascontiguousarray(array, dtype="float64")


def common_index(*values: Any) -> pd.Index | None:
    """Return the index of the first ``pd.Series``/``pd.DataFrame`` argument, if any."""
    for value in values:
        if isinstance(value, (pd.Series, pd.DataFrame)):
            return value.index
    return None


def require_aligned_index(**values: Any) -> None:
    """Reject multiple ``pd.Series``/``pd.DataFrame`` inputs whose indices disagree.

    Two same-length Series pulled from different date ranges (or otherwise
    unaligned) would otherwise be combined purely by position — same length,
    wrong pairing — with nothing to signal that the result is meaningless.
    Plain arrays and lists carry no index, so they are exempt; only pandas
    objects are compared, and only when more than one is present.
    """
    indices = {
        name: value.index
        for name, value in values.items()
        if isinstance(value, (pd.Series, pd.DataFrame))
    }
    if len(indices) < 2:
        return
    names = list(indices)
    reference_name, reference = names[0], indices[names[0]]
    for name in names[1:]:
        if not indices[name].equals(reference):
            raise ValueError(
                f"{name!r} and {reference_name!r} have different indices; "
                "inputs must share the same index (e.g. select columns from one "
                "DataFrame, or call .reindex()/.align() first)"
            )


def require_non_negative(**arrays: np.ndarray) -> None:
    """Reject arrays containing a negative value.

    Volume cannot be negative; used by every indicator that consumes it
    (:func:`~zeonta.relative_volume`, :func:`~zeonta.vwap`, :func:`~zeonta.obv`,
    :func:`~zeonta.cmf`, :func:`~zeonta.mfi`) so a bad feed fails loudly at the
    boundary instead of quietly producing a number with no real meaning.
    ``NaN`` values are ignored here — that is a separate, valid "missing data"
    state handled elsewhere, not a negativity violation.
    """
    for name, array in arrays.items():
        if np.any(array < 0.0):
            raise ValueError(f"{name!r} must not contain negative values")


def require_same_length(**arrays: np.ndarray) -> int:
    """Assert all given arrays share one length and return it."""
    lengths = {name: array.size for name, array in arrays.items()}
    if len(set(lengths.values())) > 1:
        detail = ", ".join(f"{name}={size}" for name, size in lengths.items())
        raise ValueError(f"all inputs must have the same length, got {detail}")
    return next(iter(lengths.values()))


def validate_length(length: int, name: str = "length", minimum: int = 1) -> int:
    """Validate a look-back window parameter."""
    if isinstance(length, bool) or not isinstance(length, (int, np.integer)):
        raise ValueError(f"{name!r} must be an integer, got {type(length).__name__}")
    if length < minimum:
        raise ValueError(f"{name!r} must be >= {minimum}, got {length}")
    return int(length)


def validate_multiplier(value: Number, name: str = "multiplier", minimum: float = 0.0) -> float:
    """Validate a real-valued multiplier such as an ATR or std-deviation factor."""
    if isinstance(value, bool) or not isinstance(value, (int, float, np.integer, np.floating)):
        raise ValueError(f"{name!r} must be a number, got {type(value).__name__}")
    if not np.isfinite(value):
        raise ValueError(f"{name!r} must be finite, got {value}")
    if value <= minimum:
        raise ValueError(f"{name!r} must be > {minimum}, got {value}")
    return float(value)


def _resolve_index(values: np.ndarray, index: pd.Index | None) -> pd.Index:
    if index is None:
        return pd.RangeIndex(values.shape[0])
    if len(index) != values.shape[0]:
        raise ValueError(
            f"index length {len(index)} does not match result length {values.shape[0]}"
        )
    return index


def wrap_series(values: np.ndarray, index: pd.Index | None, name: str) -> pd.Series:
    """Wrap a computed array as a named ``pd.Series``."""
    return pd.Series(values, index=_resolve_index(values, index), name=name, dtype="float64")


def wrap_frame(
    columns: Mapping[str, np.ndarray],
    index: pd.Index | None,
    order: Sequence[str] | None = None,
    roles: Mapping[str, str] | None = None,
) -> pd.DataFrame:
    """Wrap several computed arrays as a ``pd.DataFrame`` with stable column order.

    ``roles`` (optional) maps a stable, parameter-free role name (e.g.
    ``"signal"``, ``"histogram"``) to the actual (parameterized) column name
    in this frame, e.g. ``{"line": "MACD_12_26_9", "signal": "MACDs_12_26_9",
    "histogram": "MACDh_12_26_9"}``. It is stored on the returned frame as
    ``frame.attrs["roles"]`` so callers can look a column up by a name that
    stays constant across parameter changes, via ``zeonta.role(frame, "signal")``,
    without the parameterized column names ever changing.
    """
    names = list(order) if order is not None else list(columns)
    first = columns[names[0]]
    resolved = _resolve_index(first, index)
    frame = pd.DataFrame({name: columns[name] for name in names}, index=resolved)
    if roles is not None:
        for role, column in roles.items():
            if column not in names:
                raise ValueError(
                    f"role {role!r} maps to column {column!r}, which is not one of "
                    f"this frame's columns {names!r}"
                )
        frame.attrs["roles"] = dict(roles)
    return frame


def resolve_role(frame: pd.DataFrame, role: str) -> pd.Series:
    """Return the column of *frame* matching a stable, parameter-free role name.

    Works on any ``pd.DataFrame`` returned by one of zeonta's own multi-output
    indicators (``macd()``, ``bbands()``, ``supertrend()``, ...): those frames
    carry a ``frame.attrs["roles"]`` map from role name (e.g. ``"histogram"``)
    to the actual parameterized column name (e.g. ``"MACDh_12_26_9"``). This
    lets code retrieve a column by its constant role instead of hardcoding a
    name that changes with the indicator's parameters.

    Raises
    ------
    KeyError
        If *frame* carries no role map (it wasn't returned by one of this
        library's indicators, or is a single-output ``pd.Series`` instead —
        roles only exist on multi-output DataFrames), or if *role* isn't one
        of the roles *frame* defines.
    """
    roles = frame.attrs.get("roles")
    if not roles:
        raise KeyError(
            "this DataFrame carries no role map — role() only works on DataFrames "
            "returned by zeonta's own multi-output indicators"
        )
    if role not in roles:
        raise KeyError(f"unknown role {role!r}; available roles: {sorted(roles)}")
    column: pd.Series = frame[roles[role]]
    return column
