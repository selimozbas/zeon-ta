---
title: Fractal Adaptive Moving Average
---

[← All indicators](../index.md)

`zeonta.frama()` — EMA whose smoothing constant adapts to price's own fractal dimension.

## What it measures

An EMA whose smoothing constant adapts to price's own fractal dimension — the same self-adjusting idea [kama](kama.md) and [vidya](vidya.md) use, built from how rough the high-low range looks at two different window scales instead of Kaufman's Efficiency Ratio or Chande's CMO.

## Formula

```text
D = (ln(N1+N2)-ln(N3))/ln(2); alpha = clip(exp(-4.6*(D-1)), 0.01, 1.0); FRAMA = alpha*Price + (1-alpha)*FRAMA[-1]
```

## Parameters

**Required inputs:** `high`, `low`

| Parameter | Default |
| --- | --- |
| `length` | `16` |

## Returns

| Column |
| --- |
| `FRAMA_16` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.frama(df['high'], df['low']).tail(3)
```

```text
date
2024-10-25    91.016652
2024-10-26    90.914430
2024-10-27    90.463903
Name: FRAMA_16, dtype: float64
```

**Accessor form:** `df.zta.frama(...)`

## How to read it

Read like any moving average. At a fractal dimension of 1 (a straight trend) it moves as fast as price itself; at a fractal dimension of 2 (pure noise) it moves as slowly as a 200-bar SMA — rapidly following real moves while staying flat through congestion.

## Pitfalls

Outputs the midpoint price directly for the first `length` bars rather than `NaN` — there is no fixed-window warm-up the way `ema` has, since the adaptive recursion only starts once a full window exists to measure the fractal dimension from.

## Reference

Formula source: [https://www.mesasoftware.com/papers/FRAMA.pdf](https://www.mesasoftware.com/papers/FRAMA.pdf)
