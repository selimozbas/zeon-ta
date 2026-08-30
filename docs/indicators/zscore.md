---
title: Z-Score
---

[← All indicators](../index.md)

`zeonta.zscore()` — How many standard deviations price sits from its own rolling mean.

## What it measures

The same mean and spread [bbands](bbands.md) plots as two lines around price, collapsed into a single number: how many standard deviations price currently sits from its own rolling mean.

## Formula

```text
ZSCORE = (Close - SMA(Close, n)) / STDDEV(Close, n)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `20` |

## Returns

| Column |
| --- |
| `ZSCORE_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.zscore(df['close']).tail(3)
```

```text
date
2024-10-25   -0.842618
2024-10-26   -1.885195
2024-10-27   -2.193980
Name: ZSCORE_20, dtype: float64
```

**Accessor form:** `df.zta.zscore(...)`

## How to read it

`|ZSCORE| > 2` is a common, if arbitrary, threshold for 'unusually far from the mean' — the same idea as touching a Bollinger Band, expressed as a number instead of a price level you have to compare visually against the close.

## Pitfalls

Assumes the window's distribution is roughly normal enough for 'standard deviations from the mean' to be a meaningful yardstick — a window dominated by one huge outlier bar distorts both the mean and the spread it is being measured against.

## Reference

Formula source: [https://en.wikipedia.org/wiki/Standard_score](https://en.wikipedia.org/wiki/Standard_score)
