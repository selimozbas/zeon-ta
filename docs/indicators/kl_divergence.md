---
title: Kullback-Leibler Divergence
---

[← All indicators](../index.md)

`zeonta.kl_divergence()` — Kullback-Leibler divergence between a short and a long window's return distributions.

## What it measures

Reuses shannon_entropy's own equal-width-bucket binning convention, applied to two nested windows ending on the same bar: a short, recent one and a long, older one that contains it. Because the short window is always the long window's own most recent trailing subset, its values are automatically bounded by the long window's own range, so both distributions can share one set of bin edges with no separate alignment convention to invent.

## Formula

```text
edges = bins equal-width buckets spanning the long window's own min..max; P_i = short window's fraction in bucket i; Q_i = long window's fraction in bucket i; KL = sum(P_i * ln(P_i / Q_i), over buckets with P_i > 0)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `short` | `20` |
| `long` | `100` |
| `bins` | `10` |

## Returns

| Column |
| --- |
| `KLDIV_20_100_10` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.kl_divergence(df['close']).tail(3)
```

```text
date
2024-10-25    0.187260
2024-10-26    0.229345
2024-10-27    0.264909
Name: KLDIV_20_100_10, dtype: float64
```

**Accessor form:** `df.zta.kl_divergence(...)`

## How to read it

KL is 0 when the recent return distribution looks just like the longer history it sits inside, and grows as the recent window's shape — not just its level — diverges from it: a recent stretch of unusually one-sided, narrow, or fat-tailed returns compared to the longer lookback reads as a large KL value.

## Pitfalls

`long` must exceed `short`. Because the short window is a literal trailing subset of the long window's own return array, every bucket the short distribution puts mass in is guaranteed to have some long-window mass too, so KL is always finite and well-defined here (unlike a KL divergence between two unrelated samples).

## Reference

Formula source: [https://doi.org/10.1214/aoms/1177729694](https://doi.org/10.1214/aoms/1177729694)
