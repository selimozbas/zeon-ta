---
title: Median Absolute Deviation (MAD)
---

[← All indicators](../index.md)

`zeonta.mad()` — Rolling median absolute deviation: a spread measure robust to outliers.

## What it measures

A spread measure like [stddev](stddev.md), but built from medians instead of means and squares at every step — the same robust-to-outliers idea behind using a median instead of a mean in the first place, applied twice over.

## Formula

```text
MAD = median(|Close - median(Close, n)|, n)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `20` |

## Returns

| Column |
| --- |
| `MAD_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.mad(df['close']).tail(3)
```

```text
date
2024-10-25    0.45280
2024-10-26    0.52970
2024-10-27    0.62205
Name: MAD_20, dtype: float64
```

**Accessor form:** `df.zta.mad(...)`

## How to read it

Reads the same direction as `stddev` — rising means the window has gotten choppier — but a single wild bar barely moves MAD, while it can dominate `stddev` outright.

## Pitfalls

Not the same thing as the mean absolute deviation [cci](cci.md) uses internally, despite the similar name — that one averages the deviations, this one takes their median, and the two disagree whenever the window has any outliers at all.

## Reference

Formula source: [https://en.wikipedia.org/wiki/Median_absolute_deviation](https://en.wikipedia.org/wiki/Median_absolute_deviation)
