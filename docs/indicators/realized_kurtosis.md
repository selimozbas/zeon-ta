---
title: Realized Kurtosis
---

[← All indicators](../index.md)

`zeonta.realized_kurtosis()` — Realized kurtosis of returns, normalized by realized volatility (Amaya et al., 2015).

## What it measures

realized_skewness's companion statistic from the same paper: the window's 4th-power log returns rescaled by its own squared realized volatility rather than kurtosis's bias-adjustment factor applied to price levels.

## Formula

```text
RVar = sum(r_i^2); RKurt = n * sum(r_i^4) / RVar^2, over a window of n log returns
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `20` |

## Returns

| Column |
| --- |
| `RKURT_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.realized_kurtosis(df['close']).tail(3)
```

```text
date
2024-10-25    2.940156
2024-10-26    2.588749
2024-10-27    2.410279
Name: RKURT_20, dtype: float64
```

**Accessor form:** `df.zta.realized_kurtosis(...)`

## How to read it

Always >= 0; larger means fatter tails relative to the window's own realized volatility. Unlike kurtosis, this is not excess kurtosis — there is no -3 term, so a normal-like return process reads near 3, not near 0. The paper finds a positive relationship between a stock's realized kurtosis and its subsequent week's return.

## Pitfalls

Same length/warm-up/NaN conventions as realized_skewness — see that indicator's own notes.

## Reference

Formula source: [https://doi.org/10.1016/j.jfineco.2015.02.009](https://doi.org/10.1016/j.jfineco.2015.02.009)
