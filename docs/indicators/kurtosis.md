---
title: Kurtosis
---

[← All indicators](../index.md)

`zeonta.kurtosis()` — Adjusted Fisher-Pearson excess kurtosis: how fat-tailed the recent distribution is.

## What it measures

[skewness](skewness.md)'s sibling shape measure: not which side has the longer tail, but how fat *both* tails are compared to a normal distribution — how much of the window's spread comes from a few extreme bars rather than being spread evenly.

## Formula

```text
Adjusted Fisher-Pearson excess coefficient: G2 = ((n-1)/((n-2)(n-3))) * ((n+1)g2 + 6), g2 = m4/m2^2 - 3, the same bias-adjusted formula pandas' own rolling .kurt() uses
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `20` |

## Returns

| Column |
| --- |
| `KURT_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.kurtosis(df['close']).tail(3)
```

```text
date
2024-10-25   -0.164868
2024-10-26   -0.344097
2024-10-27   -0.100764
Name: KURT_20, dtype: float64
```

**Accessor form:** `df.zta.kurtosis(...)`

## How to read it

`0` reads like a normal distribution's tails. Positive (fat tails) means a few extreme bars dominate the window's spread — the pattern a market that is mostly quiet with occasional sharp shocks produces. Negative (thin tails) means moves have been unusually uniform in size.

## Pitfalls

Needs more points than `skewness` to be stable (a 4th-moment estimate is noisier still on a short window) and, like it, is `NaN` on a perfectly flat window.

## Reference

Formula source: [https://en.wikipedia.org/wiki/Kurtosis](https://en.wikipedia.org/wiki/Kurtosis)
