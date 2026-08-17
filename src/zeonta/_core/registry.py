"""Indicator registry.

Every public indicator is registered through the :func:`indicator` decorator. The
decorator reads the function's own signature to derive which OHLCV series it
consumes and which keyword parameters it exposes, so the registry can never drift
away from the implementation.

The registry powers three things:

* the ``DataFrame.zta`` accessor, whose methods are generated from it;
* :func:`zeonta.list_indicators`, the discovery entry point;
* the documentation tests, which assert that every ``.md`` file documents the
  parameters the code actually accepts.

Most indicators implement a well-known, widely published technical-analysis
formula; those pass ``lesson=`` as a purely internal category tag (it carries
no public URL). A smaller set of indicators additionally cite the specific
external source their formula was verified against via ``reference=`` (a full
URL) — used only when a formula has genuine ambiguity across sources worth
pinning down. At most one of the two is set.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any, TypeVar

__all__ = [
    "OHLCV_FIELDS",
    "IndicatorSpec",
    "get_spec",
    "indicator",
    "iter_specs",
]

#: Series names an indicator may declare as positional inputs.
OHLCV_FIELDS: tuple[str, ...] = ("open", "high", "low", "close", "volume")

F = TypeVar("F", bound=Callable[..., Any])


@dataclass(frozen=True)
class IndicatorSpec:
    """Everything the library knows about one indicator.

    ``lesson`` is an internal category slug with no public meaning; at most
    one of ``lesson``/``reference`` is set, and both may be ``None``.
    """

    name: str
    category: str
    summary: str
    lesson: str | None
    reference: str | None
    inputs: tuple[str, ...]
    params: Mapping[str, Any]
    outputs: tuple[str, ...]
    returns_frame: bool
    func: Callable[..., Any] = field(repr=False)

    def __post_init__(self) -> None:
        if self.lesson is not None and self.reference is not None:
            raise ValueError(f"{self.name!r}: 'lesson' and 'reference' are mutually exclusive")

    @property
    def url(self) -> str | None:
        """External source URL, if this indicator cites one."""
        return self.reference


_REGISTRY: dict[str, IndicatorSpec] = {}


def _split_signature(func: Callable[..., Any]) -> tuple[tuple[str, ...], dict[str, Any]]:
    """Derive (inputs, params) from a function signature.

    Leading parameters whose names are OHLCV fields are treated as data inputs;
    everything after them is a tunable parameter and must have a default.
    """
    signature = inspect.signature(func)
    inputs: list[str] = []
    params: dict[str, Any] = {}

    for name, parameter in signature.parameters.items():
        if parameter.kind in (parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD):
            continue
        if not params and name in OHLCV_FIELDS and parameter.default is parameter.empty:
            inputs.append(name)
            continue
        if parameter.default is parameter.empty:
            raise TypeError(
                f"{func.__name__}: parameter {name!r} must either be an OHLCV input "
                f"({', '.join(OHLCV_FIELDS)}) or have a default value"
            )
        params[name] = parameter.default

    if not inputs:
        raise TypeError(f"{func.__name__}: at least one OHLCV input is required")
    return tuple(inputs), params


def indicator(
    *,
    category: str,
    summary: str,
    outputs: tuple[str, ...],
    lesson: str | None = None,
    reference: str | None = None,
    returns_frame: bool | None = None,
    name: str | None = None,
) -> Callable[[F], F]:
    """Register an indicator function.

    Parameters
    ----------
    category:
        Curriculum module the indicator belongs to.
    summary:
        One-line description, surfaced by :func:`zeonta.list_indicators`.
    outputs:
        Base names of the produced columns, before parameters are interpolated.
    lesson:
        Internal category slug; carries no public URL. Mutually exclusive
        with ``reference``.
    reference:
        Full URL to the external source this indicator's formula was
        verified against, for the minority of indicators that cite one.
        Mutually exclusive with ``lesson``.
    returns_frame:
        Whether the indicator returns a ``DataFrame``. Defaults to ``True`` when
        more than one output is declared; pass it explicitly for indicators whose
        column count depends on their parameters (such as the EMA ribbon).
    name:
        Registry key. Defaults to the function's own name.
    """

    def decorator(func: F) -> F:
        inputs, params = _split_signature(func)
        key = name or func.__name__
        if key in _REGISTRY:
            raise ValueError(f"indicator {key!r} is already registered")
        _REGISTRY[key] = IndicatorSpec(
            name=key,
            category=category,
            summary=summary,
            lesson=lesson,
            reference=reference,
            inputs=inputs,
            params=params,
            outputs=tuple(outputs),
            returns_frame=len(outputs) > 1 if returns_frame is None else returns_frame,
            func=func,
        )
        return func

    return decorator


def get_spec(name: str) -> IndicatorSpec:
    """Look up one indicator's spec by name."""
    try:
        return _REGISTRY[name]
    except KeyError:
        raise KeyError(
            f"unknown indicator {name!r}; available: {', '.join(sorted(_REGISTRY))}"
        ) from None


def iter_specs() -> tuple[IndicatorSpec, ...]:
    """All registered indicator specs, sorted by category then name."""
    order = {
        "foundations": 0,
        "moving_averages": 1,
        "oscillators": 2,
        "volume": 3,
        "volatility": 4,
        "trend": 5,
        "advanced": 6,
    }
    return tuple(
        sorted(_REGISTRY.values(), key=lambda spec: (order.get(spec.category, 99), spec.name))
    )
