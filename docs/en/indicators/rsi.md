# Relative Strength Index (RSI)

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/rsi.md)

`zeonta.rsi()` — Wilder's momentum oscillator bounded between 0 and 100.

## What it measures

RSI asks a narrow question: over the last n bars, how much of the total movement was upward? The answer is squeezed onto a 0-100 scale, which makes momentum comparable across symbols and timeframes.

## Formula

```text
RSI = 100 - 100 / (1 + RS), RS = AvgGain(14, Wilder-smoothed) / AvgLoss(14, Wilder-smoothed)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `14` |

## Returns

| Column |
| --- |
| `RSI_14` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.rsi(df['close'], length=14).tail(3)
```

```text
date
2024-10-25    43.273375
2024-10-26    37.184787
2024-10-27    33.843069
Name: RSI_14, dtype: float64
```

**Accessor form:** `df.zta.rsi(...)`

## How to read it

Above 70 is conventionally "overbought" and below 30 "oversold", but the more durable reading is the 50 line: RSI holding above 50 through pullbacks is a trend in good health. Divergence between RSI and price is the other classic use — see [divergence](divergence.md).

## Pitfalls

"Overbought" does not mean "about to fall". In a strong trend RSI can sit above 70 for weeks, and shorting every such reading is one of the most reliable ways to lose money with this indicator. Treat 70/30 as a description of momentum, not an instruction.
