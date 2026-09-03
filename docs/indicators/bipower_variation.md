---
title: Realized Bipower Variation
---

[← All indicators](../index.md)

`zeonta.bipower_variation()` — Realized bipower variation: a jump-robust alternative to realized variance.

## What it measures

Realized variance (the sum of squared log returns over a window) is a consistent estimator of total quadratic variation — both the continuous, diffusive part of price movement and any jumps. Barndorff-Nielsen & Shephard (2004, 2006) show that summing products of adjacent absolute returns instead, scaled by pi/2, estimates only the continuous part: a single large jump return inflates realized variance through its own squared value, but only enters bipower variation through two bounded cross-products with its ordinary-sized neighbours.

## Formula

```text
BV = (pi/2) x sum(|r[i-1]| x |r[i]|, i = 2..n) over a window of log returns
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `window` | `20` |

## Returns

| Column |
| --- |
| `BV_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.bipower_variation(df['close']).tail(3)
```

```text
date
2024-10-25    0.000687
2024-10-26    0.000757
2024-10-27    0.000865
Name: BV_20, dtype: float64
```

**Accessor form:** `df.zta.bipower_variation(...)`

## How to read it

BV reads on the same scale as a realized-variance-style estimate (log-return variance units, not annualized or square-rooted into a volatility). Comparing it to a same-window realized variance is this pair's own basis for detecting jumps: a realized variance well above bipower variation suggests a jump occurred, though the paper's full statistical test for that (its Z-statistic) needs a separate quarticity estimator this function does not compute.

## Pitfalls

This is the plain realized-BPV estimator from the paper's own equation, with no finite-sample bias correction (no n/(n-1) adjustment) — the paper itself states this estimator's consistency without one. window counts log returns, not close bars, so one extra close bar is needed beyond window to produce a value.

## Reference

Formula source: [https://doi.org/10.1093/jjfinec/nbi022](https://doi.org/10.1093/jjfinec/nbi022)
