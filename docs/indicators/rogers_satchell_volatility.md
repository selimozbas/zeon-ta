---
title: Rogers-Satchell Volatility
---

[← All indicators](../index.md)

`zeonta.rogers_satchell_volatility()` — Drift-independent OHLC volatility that stays unbiased in a trending market.

## What it measures

An OHLC volatility estimator that, unlike [parkinson_volatility](parkinson_volatility.md) and [garman_klass_volatility](garman_klass_volatility.md), does not assume zero drift — it stays unbiased whether the market trended hard or went nowhere over the window.

## Formula

```text
RSV = 100 * sqrt(mean(ln(High/Close)*ln(High/Open) + ln(Low/Close)*ln(Low/Open), length))
```

## Parameters

**Required inputs:** `open`, `high`, `low`, `close`

| Parameter | Default |
| --- | --- |
| `length` | `20` |

## Returns

| Column |
| --- |
| `RSV_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.rogers_satchell_volatility(df['open'], df['high'], df['low'], df['close']).tail(3)
```

```text
date
2024-10-25    1.019766
2024-10-26    0.990325
2024-10-27    1.016857
Name: RSV_20, dtype: float64
```

**Accessor form:** `df.zta.rogers_satchell_volatility(...)`

## How to read it

Read the same way as the other estimators in this family — percent, not annualized.

## Pitfalls

Drift-independent but still assumes no opening jump; [yang_zhang_volatility](yang_zhang_volatility.md) adds that correction on top of this estimator's own range term.

## Reference

Formula source: [https://www.luxalgo.com/library/concept/rogers-satchell-estimator/](https://www.luxalgo.com/library/concept/rogers-satchell-estimator/)
