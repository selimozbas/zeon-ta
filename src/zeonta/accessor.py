"""The ``DataFrame.zta`` accessor.

This is a thin routing layer, deliberately holding no maths of its own: it looks
an indicator up in the registry, pulls the OHLCV columns that indicator declared,
and forwards everything else untouched. ``df.zta.rsi(14)`` and
``zeonta.rsi(df['close'], 14)`` therefore cannot drift apart.

Column matching is case-insensitive, so ``Close``, ``close`` and ``CLOSE`` all work.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pandas as pd

from ._core import get_spec, iter_specs

__all__ = ["ZeonTAAccessor"]


@pd.api.extensions.register_dataframe_accessor("zta")
class ZeonTAAccessor:
    """Call any registered indicator directly on an OHLCV ``DataFrame``.

    Examples
    --------
    >>> import pandas as pd, zeonta  # noqa: F401
    >>> df = pd.DataFrame({'close': [float(i) for i in range(30)]})
    >>> df.zta.sma(5).name
    'SMA_5'
    """

    def __init__(self, frame: pd.DataFrame) -> None:
        self._frame = frame
        self._columns = {str(name).lower(): name for name in frame.columns}

    def _series(self, field: str, indicator_name: str) -> pd.Series:
        try:
            column = self._columns[field]
        except KeyError:
            available = ", ".join(str(name) for name in self._frame.columns)
            raise KeyError(
                f"{indicator_name!r} needs a {field!r} column; frame has: {available}"
            ) from None
        return self._frame[column]

    def __getattr__(self, name: str) -> Callable[..., Any]:
        if name.startswith("_"):
            raise AttributeError(name)
        try:
            spec = get_spec(name)
        except KeyError as exc:
            raise AttributeError(str(exc)) from None

        def call(*args: Any, **kwargs: Any) -> Any:
            series = [self._series(field, spec.name) for field in spec.inputs]
            return spec.func(*series, *args, **kwargs)

        call.__name__ = spec.name
        call.__doc__ = spec.func.__doc__
        return call

    def __dir__(self) -> list[str]:
        return sorted({*super().__dir__(), *(spec.name for spec in iter_specs())})
