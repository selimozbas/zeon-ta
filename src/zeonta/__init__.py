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

Formulas follow standard, widely published technical-analysis definitions. A
handful of indicators additionally cite the specific external source their
formula was verified against in a ``References`` section of their own
docstring.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _installed_version

import pandas as pd

from . import accessor as _accessor  # noqa: F401  (registers the .zta accessor)
from ._core import IndicatorSpec, get_spec, iter_specs
from .advanced import (
    FIB_EXTENSIONS,
    FIB_RATIOS,
    dfa,
    divergence,
    fib_retracement,
    hurst_exponent,
    ou_half_life,
    pivot_points,
    sample_entropy,
    vwap,
)
from .foundations import candles, relative_volume, sr_levels, support_resistance, trend_channel
from .moving_averages import (
    dema,
    ema,
    ema_ribbon,
    emd_imf1,
    hma,
    instantaneous_trendline,
    kama,
    ma_cross,
    sma,
    smma,
    super_smoother,
    t3,
    tema,
    wavelet_denoise,
    wma,
)
from .oscillators import (
    awesome_oscillator,
    cci,
    coppock_curve,
    dpo,
    elder_ray,
    fisher_transform,
    macd,
    momentum,
    ppo,
    roc,
    rsi,
    stoch,
    stoch_rsi,
    trix,
    tsi,
    ultimate_oscillator,
    williams_r,
)
from .trend import (
    adx,
    aroon,
    chandelier_exit,
    donchian,
    ichimoku,
    linreg,
    parabolic_sar,
    supertrend,
    vortex,
)
from .volatility import atr, bbands, keltner, squeeze, true_range, ulcer_index, wavelet_variance
from .volume import adl, chaikin_oscillator, cmf, ease_of_movement, force_index, mfi, obv

try:
    # Single source of truth: read back the version hatchling wrote into the
    # installed package's metadata, rather than duplicating pyproject.toml's
    # `version` as a second literal that can silently drift out of sync.
    __version__ = _installed_version("zeon-ta")
except PackageNotFoundError:  # pragma: no cover - only when run from source, unbuilt
    __version__ = "0.0.0+unknown"

__all__ = [
    "FIB_EXTENSIONS",
    "FIB_RATIOS",
    "IndicatorSpec",
    "__version__",
    "adl",
    "adx",
    "aroon",
    "atr",
    "awesome_oscillator",
    "bbands",
    "candles",
    "cci",
    "chaikin_oscillator",
    "chandelier_exit",
    "cmf",
    "coppock_curve",
    "dema",
    "dfa",
    "divergence",
    "donchian",
    "dpo",
    "ease_of_movement",
    "elder_ray",
    "ema",
    "ema_ribbon",
    "emd_imf1",
    "fib_retracement",
    "fisher_transform",
    "force_index",
    "get_spec",
    "hma",
    "hurst_exponent",
    "ichimoku",
    "instantaneous_trendline",
    "kama",
    "keltner",
    "linreg",
    "list_indicators",
    "ma_cross",
    "macd",
    "mfi",
    "momentum",
    "obv",
    "ou_half_life",
    "parabolic_sar",
    "pivot_points",
    "ppo",
    "relative_volume",
    "roc",
    "rsi",
    "sample_entropy",
    "sma",
    "smma",
    "squeeze",
    "sr_levels",
    "stoch",
    "stoch_rsi",
    "super_smoother",
    "supertrend",
    "support_resistance",
    "t3",
    "tema",
    "trend_channel",
    "trix",
    "true_range",
    "tsi",
    "ulcer_index",
    "ultimate_oscillator",
    "vortex",
    "vwap",
    "wavelet_denoise",
    "wavelet_variance",
    "williams_r",
    "wma",
]


def list_indicators() -> pd.DataFrame:
    """Return every registered indicator as a browsable ``DataFrame``.

    Columns: ``name``, ``category``, ``summary``, ``inputs`` (required OHLCV
    series), ``params`` (tunable parameters with their defaults), ``outputs``
    (base column names) and ``source`` (the external reference URL, for the
    indicators that cite one; ``None`` otherwise).

    Examples
    --------
    >>> import zeonta
    >>> table = zeonta.list_indicators()
    >>> len(table) >= 30
    True
    >>> sorted(table['category'].unique())
    ['advanced', 'foundations', 'moving_averages', 'oscillators', 'trend', 'volatility', 'volume']
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
                "source": spec.url,
            }
            for spec in iter_specs()
        ]
    )
