---
title: Skewness
---

[← All indicators](../index.md)

`zeonta.skewness()` — Adjusted Fisher-Pearson skewness: which tail of the recent distribution is longer.

## What it measures

A shape measure for the window's recent return distribution rather than a level or trend measure like most of this library: which side has the longer tail.

## Formula

```text
Adjusted Fisher-Pearson coefficient: G1 = (sqrt(n(n-1))/(n-2)) * (m3/m2^1.5), the same bias-adjusted formula pandas' own rolling .skew() uses
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `20` |

## Returns

| Column |
| --- |
| `SKEW_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.skewness(df['close']).tail(3)
```

```text
date
2024-10-25    0.232469
2024-10-26    0.067171
2024-10-27   -0.211194
Name: SKEW_20, dtype: float64
```

**Accessor form:** `df.zta.skewness(...)`

## How to read it

Positive skew means the window had a longer right tail — a few outsized up-moves against an otherwise typical range, common in a slow grind higher punctuated by sharp rallies. Negative skew is the mirror image: a slow grind punctuated by sharp drops, the shape many equity indices show over the long run.

## Pitfalls

Needs a real spread to mean anything — `NaN` on a perfectly flat window, and noisy on a short one (a handful of points barely constrains a third-moment estimate).

## Reference

Formula source: [https://en.wikipedia.org/wiki/Skewness](https://en.wikipedia.org/wiki/Skewness)
