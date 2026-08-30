---
title: Keltner Channels
---

[← All indicators](../index.md)

`zeonta.keltner()` — EMA envelope scaled by ATR — smoother and less reactive than Bollinger.

## What it measures

The same idea as Bollinger Bands with one substitution: ATR instead of standard deviation. Since ATR reacts more slowly than standard deviation, Keltner Channels stay smoother through a shock — which is precisely what makes the pair useful together.

## Formula

```text
Middle Line = EMA(Close, 20); Upper Band = Middle + 2 x ATR(10); Lower Band = Middle - 2 x ATR(10)
```

## Parameters

**Required inputs:** `high`, `low`, `close`

| Parameter | Default |
| --- | --- |
| `length` | `20` |
| `atr_length` | `10` |
| `multiplier` | `2.0` |

## Returns

| Column |
| --- |
| `KCL_20_2.0` |
| `KCM_20_2.0` |
| `KCU_20_2.0` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.keltner(df['high'], df['low'], df['close']).tail(3)
```

```text
            KCL_20_2.0  KCM_20_2.0  KCU_20_2.0
date                                          
2024-10-25   88.199025   90.721181   93.243337
2024-10-26   88.069492   90.568592   93.067693
2024-10-27   87.807278   90.369888   92.932498
```

**Accessor form:** `df.zta.keltner(...)`

## How to read it

A close outside the channel is a genuine breakout candidate, since the channel widens far less eagerly than a Bollinger band does. Comparing the two channels is the basis of [squeeze](squeeze.md).

## Pitfalls

Implementations differ more than you would expect: some use SMA rather than EMA for the centre line, and older versions use a simple high-low range instead of ATR. Check the definition before comparing this output against a chart.
