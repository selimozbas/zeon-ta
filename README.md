# zeon-ta

[![CI](https://github.com/selimozbas/zeon-ta/actions/workflows/ci.yml/badge.svg)](https://github.com/selimozbas/zeon-ta/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](pyproject.toml)
[![License](https://img.shields.io/github/license/selimozbas/zeon-ta)](LICENSE)

Technical analysis for Python, from RSI to a causal cross-wavelet lead-lag
transform. Alongside the standard indicator set, zeon-ta implements newer,
academically-sourced tools — Ehlers' cycle-analysis filters, the Hurst
exponent, wavelet-based denoising and multi-scale volatility, a
cross-asset lead-lag transform — each one traced to the specific paper it
comes from, not to a folklore formula.

Formulas follow standard, widely published technical-analysis definitions
where one exists. Where a formula's own academic paper is the source
instead, or where a candidate indicator turned out to have no single
agreed-on formula across implementations, the docstring says which and
why.

## Why another TA library

- **Classic and modern, both formula-verified.** Every indicator — whether
  it is RSI or a MODWT wavelet-variance decomposition — cites what its
  formula was checked against, and a proposed indicator with no single
  agreed-on formula across sources is declined outright rather than
  guessed at (documented in [CHANGELOG.md](CHANGELOG.md) either way).
- **No build step.** Every dependency ships prebuilt wheels, so `pip install`
  just works — everywhere, including on ARM Macs and in slim containers.
- **One contract, every indicator.** Pass a `Series`, an array or a list; get
  pandas back with your index intact and the same length as your input. Warm-up
  bars are `NaN`, never trimmed, so nothing silently shifts under a backtest.
- **Two ways to call it.** A functional API and a `.zta` DataFrame accessor that
  routes to the exact same code — verified equal by tests, not by convention.
- **Documented honestly.** Every indicator's page states its pitfalls, including
  where an output contains look-ahead information and what to do about it.
- **Measured, not assumed, performance.** Every indicator is benchmarked at up
  to 1M bars, with real numbers and methodology in [BENCHMARKS.md](BENCHMARKS.md)
  — most complete in low milliseconds even at that size.

## Install

Not on PyPI yet — install straight from GitHub:

```bash
pip install git+https://github.com/selimozbas/zeon-ta.git
```

Or clone and install locally:

```bash
git clone https://github.com/selimozbas/zeon-ta.git
cd zeon-ta
pip install .
```

Requires Python 3.12+.

## Quick start

```python
import pandas as pd
import zeonta

df = pd.read_csv('ohlcv.csv', parse_dates=['date']).set_index('date')

# Functional
rsi = zeonta.rsi(df['close'], length=14)
bands = zeonta.bbands(df['close'], length=20, std=2)

# Accessor — identical results
rsi = df.zta.rsi(length=14)
trend = df.zta.supertrend(length=10, multiplier=3)

# Discover everything that is available
print(zeonta.list_indicators())
```

More in [examples/](examples/), runnable directly against a committed sample dataset.

## Output contract

| Input | Output |
| --- | --- |
| `pd.Series` | `Series` / `DataFrame` with the same index |
| `np.ndarray` or `list` | `Series` / `DataFrame` with a `RangeIndex` |

Single-line indicators return a named `Series`; multi-line ones return a
`DataFrame` whose column names carry the settings used (`RSI_14`,
`MACD_12_26_9`, `SUPERT_10_3.0`). `ichimoku` additionally returns the part of
the cloud that projects past the last bar, rather than discarding it.

## Indicators

### Foundations

| Indicator | What it does | Docs |
| --- | --- | --- |
| `candles` | Candlestick Anatomy and Patterns | [docs](docs/en/indicators/candles.md) |
| `relative_volume` | Volume Basics | [docs](docs/en/indicators/relative_volume.md) |
| `support_resistance` | Support and Resistance | [docs](docs/en/indicators/support_resistance.md) |
| `trend_channel` | Trend Basics and Trend Channels | [docs](docs/en/indicators/trend_channel.md) |

### Moving Averages

| Indicator | What it does | Docs |
| --- | --- | --- |
| `alma` | Arnaud Legoux Moving Average (ALMA) | [docs](docs/en/indicators/alma.md) |
| `dema` | Double Exponential Moving Average (DEMA) | [docs](docs/en/indicators/dema.md) |
| `ema` | Exponential Moving Average (EMA) | [docs](docs/en/indicators/ema.md) |
| `ema_ribbon` | EMA Ribbon | [docs](docs/en/indicators/ema_ribbon.md) |
| `emd_imf1` | Empirical Mode Decomposition — First IMF | [docs](docs/en/indicators/emd_imf1.md) |
| `hma` | Hull Moving Average (HMA) | [docs](docs/en/indicators/hma.md) |
| `instantaneous_trendline` | Instantaneous Trendline (Ehlers) | [docs](docs/en/indicators/instantaneous_trendline.md) |
| `kama` | Kaufman's Adaptive Moving Average (KAMA) | [docs](docs/en/indicators/kama.md) |
| `ma_cross` | Moving Average Crossovers | [docs](docs/en/indicators/ma_cross.md) |
| `mcgd` | McGinley Dynamic | [docs](docs/en/indicators/mcgd.md) |
| `sma` | Simple Moving Average (SMA) | [docs](docs/en/indicators/sma.md) |
| `smma` | Smoothed Moving Average (SMMA) | [docs](docs/en/indicators/smma.md) |
| `super_smoother` | Super Smoother Filter (Ehlers) | [docs](docs/en/indicators/super_smoother.md) |
| `t3` | T3 Moving Average (Tillson) | [docs](docs/en/indicators/t3.md) |
| `tema` | Triple Exponential Moving Average (TEMA) | [docs](docs/en/indicators/tema.md) |
| `vwma` | Volume-Weighted Moving Average (VWMA) | [docs](docs/en/indicators/vwma.md) |
| `wavelet_denoise` | Wavelet-Denoised Price (Discrete Wavelet Transform) | [docs](docs/en/indicators/wavelet_denoise.md) |
| `wma` | Weighted Moving Average (WMA) | [docs](docs/en/indicators/wma.md) |
| `zlema` | Zero-Lag Exponential Moving Average (ZLEMA) | [docs](docs/en/indicators/zlema.md) |

### Oscillators

| Indicator | What it does | Docs |
| --- | --- | --- |
| `awesome_oscillator` | Awesome Oscillator (AO) | [docs](docs/en/indicators/awesome_oscillator.md) |
| `cci` | Commodity Channel Index (CCI) | [docs](docs/en/indicators/cci.md) |
| `coppock_curve` | Coppock Curve | [docs](docs/en/indicators/coppock_curve.md) |
| `dpo` | Detrended Price Oscillator (DPO) | [docs](docs/en/indicators/dpo.md) |
| `elder_ray` | Elder Ray (Bull Power / Bear Power) | [docs](docs/en/indicators/elder_ray.md) |
| `fisher_transform` | Fisher Transform (Ehlers) | [docs](docs/en/indicators/fisher_transform.md) |
| `macd` | MACD (Moving Average Convergence Divergence) | [docs](docs/en/indicators/macd.md) |
| `momentum` | Momentum | [docs](docs/en/indicators/momentum.md) |
| `ppo` | Percentage Price Oscillator (PPO) | [docs](docs/en/indicators/ppo.md) |
| `roc` | Rate of Change (ROC) | [docs](docs/en/indicators/roc.md) |
| `rsi` | Relative Strength Index (RSI) | [docs](docs/en/indicators/rsi.md) |
| `stoch` | Stochastic Oscillator | [docs](docs/en/indicators/stoch.md) |
| `stoch_rsi` | Stochastic RSI (StochRSI) | [docs](docs/en/indicators/stoch_rsi.md) |
| `trix` | TRIX (Triple Exponential Average) | [docs](docs/en/indicators/trix.md) |
| `tsi` | True Strength Index (TSI) | [docs](docs/en/indicators/tsi.md) |
| `ultimate_oscillator` | Ultimate Oscillator | [docs](docs/en/indicators/ultimate_oscillator.md) |
| `williams_r` | Williams %R | [docs](docs/en/indicators/williams_r.md) |

### Volume

| Indicator | What it does | Docs |
| --- | --- | --- |
| `adl` | Accumulation/Distribution Line (ADL) | [docs](docs/en/indicators/adl.md) |
| `bop` | Balance of Power (BOP) | [docs](docs/en/indicators/bop.md) |
| `chaikin_oscillator` | Chaikin Oscillator | [docs](docs/en/indicators/chaikin_oscillator.md) |
| `cmf` | Chaikin Money Flow (CMF) | [docs](docs/en/indicators/cmf.md) |
| `ease_of_movement` | Ease of Movement (EMV) | [docs](docs/en/indicators/ease_of_movement.md) |
| `force_index` | Force Index | [docs](docs/en/indicators/force_index.md) |
| `mfi` | Money Flow Index (MFI) | [docs](docs/en/indicators/mfi.md) |
| `nvi` | Negative Volume Index (NVI) | [docs](docs/en/indicators/nvi.md) |
| `obv` | On-Balance Volume (OBV) | [docs](docs/en/indicators/obv.md) |
| `pvi` | Positive Volume Index (PVI) | [docs](docs/en/indicators/pvi.md) |
| `pvt` | Price Volume Trend (PVT) | [docs](docs/en/indicators/pvt.md) |

### Volatility

| Indicator | What it does | Docs |
| --- | --- | --- |
| `atr` | Average True Range (ATR) | [docs](docs/en/indicators/atr.md) |
| `bbands` | Bollinger Bands | [docs](docs/en/indicators/bbands.md) |
| `keltner` | Keltner Channels | [docs](docs/en/indicators/keltner.md) |
| `mass_index` | Mass Index | [docs](docs/en/indicators/mass_index.md) |
| `natr` | Normalized Average True Range (NATR) | [docs](docs/en/indicators/natr.md) |
| `squeeze` | The Squeeze (TTM Squeeze) | [docs](docs/en/indicators/squeeze.md) |
| `true_range` | True Range | [docs](docs/en/indicators/true_range.md) |
| `ulcer_index` | Ulcer Index | [docs](docs/en/indicators/ulcer_index.md) |
| `wavelet_variance` | Multi-Scale Wavelet Variance (MODWT) | [docs](docs/en/indicators/wavelet_variance.md) |

### Trend Systems

| Indicator | What it does | Docs |
| --- | --- | --- |
| `adx` | ADX / DMI | [docs](docs/en/indicators/adx.md) |
| `aroon` | Aroon and the Aroon Oscillator | [docs](docs/en/indicators/aroon.md) |
| `chandelier_exit` | Chandelier Exit | [docs](docs/en/indicators/chandelier_exit.md) |
| `choppiness_index` | Choppiness Index (CHOP) | [docs](docs/en/indicators/choppiness_index.md) |
| `donchian` | Donchian Channels | [docs](docs/en/indicators/donchian.md) |
| `ichimoku` | Ichimoku | [docs](docs/en/indicators/ichimoku.md) |
| `linreg` | Linear Regression Slope & Forecast | [docs](docs/en/indicators/linreg.md) |
| `parabolic_sar` | Parabolic SAR | [docs](docs/en/indicators/parabolic_sar.md) |
| `supertrend` | SuperTrend | [docs](docs/en/indicators/supertrend.md) |
| `vertical_horizontal_filter` | Vertical Horizontal Filter (VHF) | [docs](docs/en/indicators/vertical_horizontal_filter.md) |
| `vortex` | Vortex Indicator | [docs](docs/en/indicators/vortex.md) |

### Advanced Tools

| Indicator | What it does | Docs |
| --- | --- | --- |
| `dfa` | Detrended Fluctuation Analysis (DFA) | [docs](docs/en/indicators/dfa.md) |
| `divergence` | Divergences | [docs](docs/en/indicators/divergence.md) |
| `fib_retracement` | Fibonacci Retracement | [docs](docs/en/indicators/fib_retracement.md) |
| `hurst_exponent` | Hurst Exponent (Rescaled Range Analysis) | [docs](docs/en/indicators/hurst_exponent.md) |
| `ou_half_life` | Ornstein-Uhlenbeck Half-Life of Mean Reversion | [docs](docs/en/indicators/ou_half_life.md) |
| `pivot_points` | Pivot Points | [docs](docs/en/indicators/pivot_points.md) |
| `sample_entropy` | Sample Entropy (SampEn) | [docs](docs/en/indicators/sample_entropy.md) |
| `vwap` | VWAP (Volume-Weighted Average Price) | [docs](docs/en/indicators/vwap.md) |

### Statistics

| Indicator | What it does | Docs |
| --- | --- | --- |
| `cumulative_return` | Cumulative Return | [docs](docs/en/indicators/cumulative_return.md) |
| `kurtosis` | Kurtosis | [docs](docs/en/indicators/kurtosis.md) |
| `log_return` | Logarithmic Return | [docs](docs/en/indicators/log_return.md) |
| `mad` | Median Absolute Deviation (MAD) | [docs](docs/en/indicators/mad.md) |
| `skewness` | Skewness | [docs](docs/en/indicators/skewness.md) |
| `stddev` | Standard Deviation | [docs](docs/en/indicators/stddev.md) |
| `variance` | Variance | [docs](docs/en/indicators/variance.md) |
| `zscore` | Z-Score | [docs](docs/en/indicators/zscore.md) |

### Cross-asset utilities (outside the registry)

`zeonta.cross_asset.wavelet_lead_lag(close_a, close_b, period=20)` compares
*two independent* price series — which one is leading the other, and by how
much, at a chosen timescale — via a causal Morlet Cross-Wavelet Transform
(Torrence & Compo, 1998). It isn't in `list_indicators()` or the `.zta`
accessor: every registered indicator assumes one asset's own OHLCV columns,
and a second, independent series doesn't fit that contract. Import and call
it directly; see its own docstring for the full method and a documented
lag-estimate caveat.

## Development

```bash
pip install -e ".[dev]"
pytest                      # test suite
ruff check . && mypy src/   # lint and types
python tools/gen_docs.py    # regenerate the docs
```

Documentation is generated: prose lives in `tools/docs_content.py`, while
parameter tables, column names and example output are taken from the code
itself and from actually running each example. A test fails if the committed
files drift.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow, and
[docs/en/methodology.md](docs/en/methodology.md) for how a formula gets
verified before it's implemented. This project follows a
[Code of Conduct](CODE_OF_CONDUCT.md); see [SECURITY.md](SECURITY.md) to
report a vulnerability privately.

## License

GPL-3.0-or-later — see [LICENSE](LICENSE).
