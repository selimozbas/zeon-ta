# EMA Ribbon

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/ema_ribbon.md)

`zeonta.ema_ribbon()` — A fan of EMAs of increasing length; spacing shows trend strength.

## What it measures

One EMA tells you the trend; six of them tell you how much agreement there is. When the whole fan points the same way and spreads apart, every timeframe in the ribbon agrees. When it knots together, none of them do.

## Formula

```text
EMA Ribbon = 6 EMAs of increasing length plotted together, e.g. EMA(20), EMA(30), EMA(40), EMA(50), EMA(60), EMA(70) (or Fibonacci-like: 8, 13, 21, 34, 55, 89). Each EMA(n) = Close x k + previous EMA(n) x (1 - k), k = 2/(n+1).
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `lengths` | `(20, 30, 40, 50, 60, 70)` |

## Returns

| Column |
| --- |
| `EMA_20` |
| `EMA_30` |
| `EMA_40` |
| `EMA_50` |
| `EMA_60` |
| `EMA_70` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.ema_ribbon(df['close'], lengths=(8, 13, 21, 34, 55, 89)).tail(2)
```

```text
                EMA_8     EMA_13     EMA_21     EMA_34     EMA_55     EMA_89
date                                                                        
2024-10-26  90.083492  90.323343  90.599422  90.956204  91.463247  92.183236
2024-10-27  89.727649  90.060322  90.406948  90.814833  91.356781  92.100991
```

**Accessor form:** `df.zta.ema_ribbon(...)`

## How to read it

Widely spaced and correctly ordered (shortest on top in an uptrend) means a strong, well-established trend. Compressed and interleaved means the trend has stalled — often just before a decisive move in either direction.

## Pitfalls

The ribbon is six lagging indicators, not six independent opinions — they all come from the same closes, so their "agreement" is much weaker evidence than it looks. It is a visualisation aid more than a signal generator.

## Reference

Formula source: [https://ta.cognicode.org/learn/ema-ribbon](https://ta.cognicode.org/learn/ema-ribbon)
