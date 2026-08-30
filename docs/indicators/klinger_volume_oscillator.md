---
title: Klinger Volume Oscillator (KVO)
---

[← All indicators](../index.md)

`zeonta.klinger_volume_oscillator()` — Difference of two EMAs of a trend-and-range-scaled volume force.

## What it measures

Stephen Klinger's more graded cousin of [obv](obv.md): rather than adding or subtracting a bar's entire volume by direction alone, the 'volume force' is scaled by how the bar's own range compares to the accumulated range since the trend last flipped — a half-hearted push contributes less than a bar where the range dominates the whole move.

## Formula

```text
VF = 100 * Volume * Trend * |2*(dm/cm) - 1|, dm = High-Low, cm accumulates dm since the trend last flipped; KVO = EMA(VF,fast) - EMA(VF,slow)
```

## Parameters

**Required inputs:** `high`, `low`, `close`, `volume`

| Parameter | Default |
| --- | --- |
| `fast` | `34` |
| `slow` | `55` |
| `signal_length` | `13` |

## Returns

| Column |
| --- |
| `KVO_34_55` |
| `KVOs_34_55` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.klinger_volume_oscillator(df['high'], df['low'], df['close'], df['volume']).tail(3)
```

```text
               KVO_34_55    KVOs_34_55
date                                  
2024-10-25 -1.865480e+06 -1.177855e+06
2024-10-26 -1.784800e+06 -1.264561e+06
2024-10-27 -1.735052e+06 -1.331774e+06
```

**Accessor form:** `df.zta.klinger_volume_oscillator(...)`

## How to read it

Read like [macd](macd.md): the crossover between KVO and its own signal line, or KVO crossing zero, confirming a price move with real volume conviction behind it.

## Pitfalls

The trend/cm bookkeeping means a single missing bar has more reach than a plain EMA gap would — a NaN bar breaks the trend comparison for the bar right after it too, recovering fully only once two consecutive clean bars are available.

## Reference

Formula source: [https://tulipindicators.org/kvo](https://tulipindicators.org/kvo)
