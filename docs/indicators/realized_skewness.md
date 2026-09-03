---
title: Realized Skewness
---

[← All indicators](../index.md)

`zeonta.realized_skewness()` — Realized skewness of returns, normalized by realized volatility (Amaya et al., 2015).

## What it measures

skewness computes the adjusted Fisher-Pearson moment ratio directly on rolling price levels. Amaya, Christoffersen, Jacobs & Vasquez (2015) instead build a skewness measure from the window's own log returns, normalized by its own realized volatility rather than by a bias-adjustment factor — the same construction the high-frequency realized-variance literature (bipower_variation and realized_semivariance's own family) already uses, extended to the third moment.

## Formula

```text
RVar = sum(r_i^2); RSkew = sqrt(n) * sum(r_i^3) / RVar^1.5, over a window of n log returns
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `20` |

## Returns

| Column |
| --- |
| `RSKEW_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.realized_skewness(df['close']).tail(3)
```

```text
date
2024-10-25    0.600908
2024-10-26    0.308760
2024-10-27    0.236446
Name: RSKEW_20, dtype: float64
```

**Accessor form:** `df.zta.realized_skewness(...)`

## How to read it

Negative means the window's return distribution has a fatter left (down-move) tail than right; positive the opposite — the same sign convention as skewness, on a differently normalized quantity. The paper finds a strong, robust negative relationship between a stock's realized skewness and its subsequent week's return in the cross-section.

## Pitfalls

length counts log returns, one more close bar than that is needed. The paper's own setting builds this from 5-minute intraday returns aggregated into a weekly statistic; this function applies the identical formula at whatever bar frequency close is sampled at, generalizing the estimator rather than the paper's specific data frequency. NaN wherever the window's realized variance is exactly 0.

## Reference

Formula source: [https://doi.org/10.1016/j.jfineco.2015.02.009](https://doi.org/10.1016/j.jfineco.2015.02.009)
