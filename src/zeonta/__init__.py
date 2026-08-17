"""zeon-ta — modern technical analysis indicators for Python.

Every indicator follows the same three rules:

* **Flexible input** — pass a ``pandas.Series``, a NumPy array or a plain list.
* **Pandas output** — a ``Series`` for single-line indicators, a ``DataFrame`` for
  multi-line ones. The input's index is preserved when there is one.
* **Aligned output** — the result always has the same length as the input;
  warm-up bars are ``NaN`` rather than trimmed, so nothing silently shifts.

Two equivalent ways to call anything::

    import zeonta

    zeonta.rsi(df['close'], length=14)   # functional
    df.zta.rsi(length=14)                # accessor, same code underneath

Formulas are taken from the TA 101 curriculum at https://ta.cognicode.org —
each function's docstring links to the lesson it implements.
"""

from __future__ import annotations

import pandas as pd

from . import accessor as _accessor  # noqa: F401  (registers the .zta accessor)
from ._core import IndicatorSpec, get_spec, iter_specs
from .advanced import (
    FIB_EXTENSIONS,
    FIB_RATIOS,
    divergence,
    fib_retracement,
    pivot_points,
    vwap,
)
from .foundations import candles, relative_volume, sr_levels, support_resistance, trend_channel
from .moving_averages import ema, ema_ribbon, ma_cross, sma
from .oscillators import cci, macd, rsi, stoch
from .trend import adx, donchian, ichimoku, supertrend
from .volatility import atr, bbands, keltner, squeeze, true_range

__version__ = "0.1.0"

__all__ = [
    "FIB_EXTENSIONS",
    "FIB_RATIOS",
    "IndicatorSpec",
    "__version__",
    "adx",
    "atr",
    "bbands",
    "candles",
    "cci",
    "divergence",
    "donchian",
    "ema",
    "ema_ribbon",
    "fib_retracement",
    "get_spec",
    "ichimoku",
    "keltner",
    "list_indicators",
    "ma_cross",
    "macd",
    "pivot_points",
    "relative_volume",
    "rsi",
    "sma",
    "squeeze",
    "sr_levels",
    "stoch",
    "supertrend",
    "support_resistance",
    "trend_channel",
    "true_range",
    "vwap",
]


def list_indicators() -> pd.DataFrame:
    """Return every registered indicator as a browsable ``DataFrame``.

    Columns: ``name``, ``category``, ``summary``, ``inputs`` (required OHLCV
    series), ``params`` (tunable parameters with their defaults), ``outputs``
    (base column names) and ``lesson`` (link to the source formula).

    Examples
    --------
    >>> import zeonta
    >>> table = zeonta.list_indicators()
    >>> len(table) >= 24
    True
    >>> sorted(table['category'].unique())
    ['advanced', 'foundations', 'moving_averages', 'oscillators', 'trend', 'volatility']
    """
    return pd.DataFrame(
        [
            {
                "name": spec.name,
                "category": spec.category,
                "summary": spec.summary,
                "inputs": ", ".join(spec.inputs),
                "params": ", ".join(f"{key}={value!r}" for key, value in spec.params.items()),
                "outputs": ", ".join(spec.outputs),
                "lesson": spec.url,
            }
            for spec in iter_specs()
        ]
    )
