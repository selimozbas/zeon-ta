---
title: Exponential Moving Average (EMA)
---

[← All indicators](../index.md)

`zeonta.ema()` — Exponentially weighted average that reacts faster to recent closes.

## What it measures

The EMA fixes the SMA's biggest quirk: instead of every bar in a window counting equally and then abruptly dropping out, weight decays smoothly into the past. Recent bars matter most and old ones fade rather than fall off a cliff.

## Formula

```text
EMA(n) today = Close x k + EMA(n) yesterday x (1 - k), where k = 2 / (n + 1). Seed value: EMA(n) on the first available bar = SMA(n) of the first n closes.
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `20` |

## Returns

| Column |
| --- |
| `EMA_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.ema(df['close'], length=20).tail(3)
```

```text
date
2024-10-25    90.721181
2024-10-26    90.568592
2024-10-27    90.369888
Name: EMA_20, dtype: float64
```

**Accessor form:** `df.zta.ema(...)`

## How to read it

Read it exactly like an SMA, but expect it to turn sooner. The gap between a fast and a slow EMA is the basis of MACD, and stacked EMAs of increasing length form the ribbon.

## Pitfalls

Faster response also means more false turns — the EMA reacts to a one-bar spike that an SMA would smooth away. Note also that different platforms seed the recursion differently; this library seeds with the SMA of the first n closes, so the first handful of values may not match a chart that seeds from the first close alone.
