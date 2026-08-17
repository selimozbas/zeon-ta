# zeon-ta

[![PyPI](https://img.shields.io/pypi/v/zeon-ta)](https://pypi.org/project/zeon-ta/)
[![Python](https://img.shields.io/pypi/pyversions/zeon-ta)](https://pypi.org/project/zeon-ta/)
[![License](https://img.shields.io/pypi/l/zeon-ta)](LICENSE)

**Türkçe: [README.tr.md](README.tr.md)**

Technical analysis indicators for Python that are actually maintained — no C
extension to compile, no abandoned API. NumPy and pandas are the only
dependencies.

Most formulas are implemented from the [TA 101](https://ta.cognicode.org)
curriculum; a few common indicators outside that curriculum (OBV, CMF, MFI,
ROC, Momentum, KAMA, Parabolic SAR) are included too. Every function's
docstring links back to its specific source, TA 101 or otherwise.

## Why another TA library

- **No build step.** Pure NumPy/pandas, so `pip install` just works — everywhere,
  including on ARM Macs and in slim containers where TA-Lib is a fight.
- **One contract, every indicator.** Pass a `Series`, an array or a list; get
  pandas back with your index intact and the same length as your input. Warm-up
  bars are `NaN`, never trimmed, so nothing silently shifts under a backtest.
- **Two ways to call it.** A functional API and a `.zta` DataFrame accessor that
  routes to the exact same code — verified equal by tests, not by convention.
- **Documented honestly.** Every indicator's page states its pitfalls, including
  where an output contains look-ahead information and what to do about it.

## Install

```bash
pip install zeon-ta
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
| `ema` | Exponential Moving Average (EMA) | [docs](docs/en/indicators/ema.md) |
| `ema_ribbon` | EMA Ribbon | [docs](docs/en/indicators/ema_ribbon.md) |
| `kama` | Kaufman's Adaptive Moving Average (KAMA) | [docs](docs/en/indicators/kama.md) |
| `ma_cross` | Moving Average Crossovers | [docs](docs/en/indicators/ma_cross.md) |
| `sma` | Simple Moving Average (SMA) | [docs](docs/en/indicators/sma.md) |

### Oscillators

| Indicator | What it does | Docs |
| --- | --- | --- |
| `cci` | Commodity Channel Index (CCI) | [docs](docs/en/indicators/cci.md) |
| `macd` | MACD (Moving Average Convergence Divergence) | [docs](docs/en/indicators/macd.md) |
| `momentum` | Momentum | [docs](docs/en/indicators/momentum.md) |
| `roc` | Rate of Change (ROC) | [docs](docs/en/indicators/roc.md) |
| `rsi` | Relative Strength Index (RSI) | [docs](docs/en/indicators/rsi.md) |
| `stoch` | Stochastic Oscillator | [docs](docs/en/indicators/stoch.md) |

### Volume

| Indicator | What it does | Docs |
| --- | --- | --- |
| `cmf` | Chaikin Money Flow (CMF) | [docs](docs/en/indicators/cmf.md) |
| `mfi` | Money Flow Index (MFI) | [docs](docs/en/indicators/mfi.md) |
| `obv` | On-Balance Volume (OBV) | [docs](docs/en/indicators/obv.md) |

### Volatility

| Indicator | What it does | Docs |
| --- | --- | --- |
| `atr` | Average True Range (ATR) | [docs](docs/en/indicators/atr.md) |
| `bbands` | Bollinger Bands | [docs](docs/en/indicators/bbands.md) |
| `keltner` | Keltner Channels | [docs](docs/en/indicators/keltner.md) |
| `squeeze` | The Squeeze (TTM Squeeze) | [docs](docs/en/indicators/squeeze.md) |
| `true_range` | True Range | [docs](docs/en/indicators/true_range.md) |

### Trend Systems

| Indicator | What it does | Docs |
| --- | --- | --- |
| `adx` | ADX / DMI | [docs](docs/en/indicators/adx.md) |
| `donchian` | Donchian Channels | [docs](docs/en/indicators/donchian.md) |
| `ichimoku` | Ichimoku | [docs](docs/en/indicators/ichimoku.md) |
| `parabolic_sar` | Parabolic SAR | [docs](docs/en/indicators/parabolic_sar.md) |
| `supertrend` | SuperTrend | [docs](docs/en/indicators/supertrend.md) |

### Advanced Tools

| Indicator | What it does | Docs |
| --- | --- | --- |
| `divergence` | Divergences | [docs](docs/en/indicators/divergence.md) |
| `fib_retracement` | Fibonacci Retracement | [docs](docs/en/indicators/fib_retracement.md) |
| `pivot_points` | Pivot Points | [docs](docs/en/indicators/pivot_points.md) |
| `vwap` | VWAP (Volume-Weighted Average Price) | [docs](docs/en/indicators/vwap.md) |

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

## License

GPL-3.0-or-later — see [LICENSE](LICENSE).
