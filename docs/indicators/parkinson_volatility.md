---
title: Parkinson Volatility
---

[← All indicators](../index.md)

`zeonta.parkinson_volatility()` — Extreme-value volatility from the high-low range alone, ~5x more efficient than C2C.

## What it measures

An extreme-value volatility estimator built from the high-low range alone, on the theory that the whole path a bar took — not just where it closed — carries information about its variance. The same idea [true_range](true_range.md)/[atr](atr.md) apply to range, applied here to variance instead.

## Formula

```text
PARKV = 100 * sqrt(mean(ln(High/Low)^2, length) / (4 * ln(2)))
```

## Parameters

**Required inputs:** `high`, `low`

| Parameter | Default |
| --- | --- |
| `length` | `20` |

## Returns

| Column |
| --- |
| `PARKV_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.parkinson_volatility(df['high'], df['low']).tail(3)
```

```text
date
2024-10-25    0.948051
2024-10-26    0.939496
2024-10-27    0.966346
Name: PARKV_20, dtype: float64
```

**Accessor form:** `df.zta.parkinson_volatility(...)`

## How to read it

Read like any volatility measure: a rising value means the market's own bars are spanning more ground, falling means they're tightening up. Reported in percent, not annualized — multiply by `sqrt(periods_per_year)` if you want the conventional annualized figure.

## Pitfalls

Assumes zero drift and no opening jumps; a strongly trending or gapping series inflates this estimator. [rogers_satchell_volatility](rogers_satchell_volatility.md) and [yang_zhang_volatility](yang_zhang_volatility.md) correct for exactly that.

## Reference

Formula source: [https://www.ivolatility.com/education/parkinsons-historical-volatility/](https://www.ivolatility.com/education/parkinsons-historical-volatility/)
