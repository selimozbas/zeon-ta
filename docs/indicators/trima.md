---
title: Triangular Moving Average (TRIMA)
---

[← All indicators](../index.md)

`zeonta.trima()` — An SMA of an SMA, weighting the middle of the window most heavily.

## What it measures

An [sma](sma.md) of an [sma](sma.md), with the two window sizes chosen so the combined effect weights the middle of the window most heavily rather than every bar equally — a triangular weighting shape instead of `sma`'s rectangular one.

## Formula

```text
Even length: TRIMA = SMA(SMA(Close, n/2), n/2+1); Odd length: TRIMA = SMA(SMA(Close, (n+1)/2), (n+1)/2)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `20` |

## Returns

| Column |
| --- |
| `TRIMA_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.trima(df['close']).tail(3)
```

```text
date
2024-10-25    90.931086
2024-10-26    90.872321
2024-10-27    90.777766
Name: TRIMA_20, dtype: float64
```

**Accessor form:** `df.zta.trima(...)`

## How to read it

Read the same way as any moving average. Smoother than an `sma` of the same length (the middle-weighting suppresses noise at both edges of the window), at the cost of a longer effective lag.

## Pitfalls

No special edge cases — a plain double SMA pass.

## Reference

Formula source: [https://tulipindicators.org/trima](https://tulipindicators.org/trima)
