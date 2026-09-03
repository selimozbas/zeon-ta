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
from ._core import resolve_role as role
from .advanced import (
    FIB_EXTENSIONS,
    FIB_RATIOS,
    approximate_entropy,
    cpr,
    dfa,
    divergence,
    fib_retracement,
    higuchi_fractal_dimension,
    hurst_exponent,
    markov_regime_switching,
    multifractal_dfa,
    ou_half_life,
    permutation_entropy,
    pivot_points,
    sample_entropy,
    shannon_entropy,
    vwap,
)
from .foundations import (
    candles,
    heikin_ashi,
    relative_volume,
    sr_levels,
    support_resistance,
    trend_channel,
    williams_fractals,
)
from .moving_averages import (
    GMMA_FAST_LENGTHS,
    GMMA_SLOW_LENGTHS,
    alma,
    dema,
    efficiency_ratio,
    ema,
    ema_ribbon,
    emd_imf1,
    frama,
    gmma,
    hma,
    instantaneous_trendline,
    kalman_filter,
    kama,
    ma_cross,
    mcgd,
    sma,
    smma,
    super_smoother,
    t3,
    tema,
    trima,
    vidya,
    vwma,
    wavelet_denoise,
    wma,
    zlema,
)
from .oscillators import (
    awesome_oscillator,
    bias,
    cci,
    center_of_gravity,
    cmo,
    connors_rsi,
    coppock_curve,
    cyber_cycle,
    dpo,
    elder_ray,
    even_better_sinewave,
    fisher_transform,
    ift_rsi,
    kdj,
    kst,
    laguerre_rsi,
    macd,
    momentum,
    ppo,
    psl,
    qqe,
    reflex_trendflex,
    roc,
    roofing_filter,
    rsi,
    rvgi,
    smi,
    stoch,
    stoch_rsi,
    trix,
    tsi,
    ultimate_oscillator,
    voss_predictive_filter,
    williams_r,
)
from .statistics import (
    cumulative_return,
    drawdown,
    ffd,
    kurtosis,
    log_return,
    mad,
    skewness,
    stddev,
    variance,
    zscore,
)
from .trend import (
    adx,
    adxr,
    aroon,
    chandelier_exit,
    choppiness_index,
    donchian,
    ichimoku,
    linreg,
    parabolic_sar,
    qstick,
    supertrend,
    vertical_horizontal_filter,
    vortex,
)
from .volatility import (
    abdi_ranaldo_spread,
    accbands,
    atr,
    bbands,
    bipower_variation,
    chaikin_volatility,
    corwin_schultz_spread,
    garman_klass_volatility,
    keltner,
    mass_index,
    natr,
    parkinson_volatility,
    realized_semivariance,
    relative_volatility_index,
    rogers_satchell_volatility,
    roll_spread,
    squeeze,
    true_range,
    ulcer_index,
    wavelet_variance,
    yang_zhang_volatility,
)
from .volume import (
    adl,
    amihud_illiquidity,
    bop,
    chaikin_oscillator,
    cmf,
    ease_of_movement,
    force_index,
    klinger_volume_oscillator,
    mfi,
    nvi,
    obv,
    pvi,
    pvt,
    vwmacd,
    williams_ad,
)

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
    "GMMA_FAST_LENGTHS",
    "GMMA_SLOW_LENGTHS",
    "IndicatorSpec",
    "__version__",
    "abdi_ranaldo_spread",
    "accbands",
    "adl",
    "adx",
    "adxr",
    "alma",
    "amihud_illiquidity",
    "approximate_entropy",
    "aroon",
    "atr",
    "awesome_oscillator",
    "bbands",
    "bias",
    "bipower_variation",
    "bop",
    "candles",
    "cci",
    "center_of_gravity",
    "chaikin_oscillator",
    "chaikin_volatility",
    "chandelier_exit",
    "choppiness_index",
    "cmf",
    "cmo",
    "connors_rsi",
    "coppock_curve",
    "corwin_schultz_spread",
    "cpr",
    "cumulative_return",
    "cyber_cycle",
    "dema",
    "dfa",
    "divergence",
    "donchian",
    "dpo",
    "drawdown",
    "ease_of_movement",
    "efficiency_ratio",
    "elder_ray",
    "ema",
    "ema_ribbon",
    "emd_imf1",
    "even_better_sinewave",
    "ffd",
    "fib_retracement",
    "fisher_transform",
    "force_index",
    "frama",
    "garman_klass_volatility",
    "get_spec",
    "gmma",
    "heikin_ashi",
    "higuchi_fractal_dimension",
    "hma",
    "hurst_exponent",
    "ichimoku",
    "ift_rsi",
    "instantaneous_trendline",
    "kalman_filter",
    "kama",
    "kdj",
    "keltner",
    "klinger_volume_oscillator",
    "kst",
    "kurtosis",
    "laguerre_rsi",
    "linreg",
    "list_indicators",
    "log_return",
    "ma_cross",
    "macd",
    "mad",
    "markov_regime_switching",
    "mass_index",
    "mcgd",
    "mfi",
    "momentum",
    "multifractal_dfa",
    "natr",
    "nvi",
    "obv",
    "ou_half_life",
    "parabolic_sar",
    "parkinson_volatility",
    "permutation_entropy",
    "pivot_points",
    "ppo",
    "psl",
    "pvi",
    "pvt",
    "qqe",
    "qstick",
    "realized_semivariance",
    "reflex_trendflex",
    "relative_volatility_index",
    "relative_volume",
    "roc",
    "rogers_satchell_volatility",
    "role",
    "roll_spread",
    "roofing_filter",
    "rsi",
    "rvgi",
    "sample_entropy",
    "shannon_entropy",
    "skewness",
    "sma",
    "smi",
    "smma",
    "squeeze",
    "sr_levels",
    "stddev",
    "stoch",
    "stoch_rsi",
    "super_smoother",
    "supertrend",
    "support_resistance",
    "t3",
    "tema",
    "trend_channel",
    "trima",
    "trix",
    "true_range",
    "tsi",
    "ulcer_index",
    "ultimate_oscillator",
    "variance",
    "vertical_horizontal_filter",
    "vidya",
    "vortex",
    "voss_predictive_filter",
    "vwap",
    "vwma",
    "vwmacd",
    "wavelet_denoise",
    "wavelet_variance",
    "williams_ad",
    "williams_fractals",
    "williams_r",
    "wma",
    "yang_zhang_volatility",
    "zlema",
    "zscore",
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
    >>> sorted(table['category'].unique())  # doctest: +NORMALIZE_WHITESPACE
    ['advanced', 'foundations', 'moving_averages', 'oscillators',
     'statistics', 'trend', 'volatility', 'volume']
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
