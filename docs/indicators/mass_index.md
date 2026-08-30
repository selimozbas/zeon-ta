---
title: Mass Index
---

[← All indicators](../index.md)

`zeonta.mass_index()` — Range-expansion measure built to flag reversals, from EMA-of-EMA ratio of the range.

## What it measures

Donald Dorsey built this entirely from the bar-to-bar *range*, not price direction: an EMA reacts faster than an EMA-of-that-EMA, so their ratio grows whenever the range is widening, whether that widening comes from an up move or a down move. Dorsey's own claim was that this range expansion tends to appear before a trend reversal, without saying which direction the reversal goes.

## Formula

```text
SingleEMA = EMA(High-Low, ema_length); DoubleEMA = EMA(SingleEMA, ema_length); Ratio = SingleEMA/DoubleEMA; MASS = Sum(Ratio, sum_length)
```

## Parameters

**Required inputs:** `high`, `low`

| Parameter | Default |
| --- | --- |
| `ema_length` | `9` |
| `sum_length` | `25` |

## Returns

| Column |
| --- |
| `MASS_9_25` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.mass_index(df['high'], df['low']).tail(3)
```

```text
date
2024-10-25    27.912747
2024-10-26    27.761708
2024-10-27    27.669469
Name: MASS_9_25, dtype: float64
```

**Accessor form:** `df.zta.mass_index(...)`

## How to read it

Dorsey's own 'reversal bulge' threshold is a reading of 27 followed by a drop back below 26.5 — a specific level pattern to watch for, not a zero-line crossing or a bounded oscillator the way most indicators in this library work.

## Pitfalls

Reads in the mid-20s during ordinary conditions by construction (it is a 25-bar sum of a ratio that hovers near 1), so it needs its own specific threshold rather than a 0/50/100-style intuition.

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/mass-index](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/mass-index)
