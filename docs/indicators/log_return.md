---
title: Logarithmic Return
---

[← All indicators](../index.md)

`zeonta.log_return()` — Logarithmic return over a fixed bar lag.

## What it measures

[roc](roc.md)'s statistical cousin: the same bar-lag comparison, expressed as a log ratio instead of a percentage. Log returns are additive across time (summing single-bar log returns over a window equals the log return over the whole window), which simple percentage change is not — the reason most statistical work on a return series (including this library's own `hurst_exponent`, `dfa` and `sample_entropy`) uses this form rather than `roc`.

## Formula

```text
LOGRET = ln(Close[t] / Close[t-n])
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `1` |

## Returns

| Column |
| --- |
| `LOGRET_1` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.log_return(df['close']).tail(3)
```

```text
date
2024-10-25   -0.004526
2024-10-26   -0.010905
2024-10-27   -0.007171
Name: LOGRET_1, dtype: float64
```

**Accessor form:** `df.zta.log_return(...)`

## How to read it

For everyday-sized moves, a log return and a simple percentage return are nearly identical (`ln(1.01) ~= 0.00995`); they diverge more visibly on a large single-bar move.

## Pitfalls

Requires strictly positive prices — `ln` of a zero or negative value is undefined, which surfaces here as `NaN` rather than an exception.

## Reference

Formula source: [https://en.wikipedia.org/wiki/Rate_of_return](https://en.wikipedia.org/wiki/Rate_of_return)
