---
title: Yang-Zhang Volatility
---

[← All indicators](../index.md)

`zeonta.yang_zhang_volatility()` — Drift-independent volatility blending overnight, open-close and Rogers-Satchell.

## What it measures

Combines an overnight-gap variance term, an intraday open-to-close variance term, and [rogers_satchell_volatility](rogers_satchell_volatility.md)'s own drift-independent range term into the most statistically efficient of the four OHLC volatility estimators in this module, while staying unbiased under both drift and opening jumps.

## Formula

```text
YZV = 100 * sqrt(Var(overnight) + k*Var(open_close) + (1-k)*mean(RogersSatchell_per_bar)), k = 0.34/(1.34+(n+1)/(n-1))
```

## Parameters

**Required inputs:** `open`, `high`, `low`, `close`

| Parameter | Default |
| --- | --- |
| `length` | `20` |

## Returns

| Column |
| --- |
| `YZV_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.yang_zhang_volatility(df['open'], df['high'], df['low'], df['close']).tail(3)
```

```text
date
2024-10-25    0.986835
2024-10-26    0.965372
2024-10-27    0.989890
Name: YZV_20, dtype: float64
```

**Accessor form:** `df.zta.yang_zhang_volatility(...)`

## How to read it

Read the same way as the other estimators in this family — percent, not annualized.

## Pitfalls

Needs `length >= 2` (the variance terms need at least two points), and the combining weight `k` is recomputed from `length` itself — it is not a universal constant.

## Reference

Formula source: [https://iwpfinance.com/concepts/technical-analysis/yang-zhang-volatility](https://iwpfinance.com/concepts/technical-analysis/yang-zhang-volatility)
