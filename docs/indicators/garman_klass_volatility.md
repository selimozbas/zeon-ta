---
title: Garman-Klass Volatility
---

[← All indicators](../index.md)

`zeonta.garman_klass_volatility()` — OHLC volatility adding the open-close jump to Parkinson's range term.

## What it measures

Extends [parkinson_volatility](parkinson_volatility.md) with the open-close jump, using all four OHLC prices rather than the range alone for a more statistically efficient estimate at the same window length.

## Formula

```text
GKV = 100 * sqrt(mean(0.5*ln(High/Low)^2 - (2*ln(2)-1)*ln(Close/Open)^2, length))
```

## Parameters

**Required inputs:** `open`, `high`, `low`, `close`

| Parameter | Default |
| --- | --- |
| `length` | `20` |

## Returns

| Column |
| --- |
| `GKV_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.garman_klass_volatility(df['open'], df['high'], df['low'], df['close']).tail(3)
```

```text
date
2024-10-25    1.042482
2024-10-26    1.017819
2024-10-27    1.045577
Name: GKV_20, dtype: float64
```

**Accessor form:** `df.zta.garman_klass_volatility(...)`

## How to read it

Read the same way as `parkinson_volatility` — reported in percent, not annualized.

## Pitfalls

Still assumes zero drift and no opening jump, the same limitation `parkinson_volatility` has; [yang_zhang_volatility](yang_zhang_volatility.md) is the estimator in this family that corrects for both.

## Reference

Formula source: [https://www.cmegroup.com/trading/fx/files/a_estimation_of_security_price.pdf](https://www.cmegroup.com/trading/fx/files/a_estimation_of_security_price.pdf)
