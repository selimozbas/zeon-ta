---
title: Kaufman's Efficiency Ratio (ER)
---

[← All indicators](../index.md)

`zeonta.efficiency_ratio()` — How efficiently price is trending: net movement over total movement.

## What it measures

The adaptive core [kama](kama.md) blends into its own smoothing constant, exposed here on its own: net movement over total movement, a direct measure of how much of a window's bar-to-bar churn actually went somewhere.

## Formula

```text
ER = |Close - Close[n ago]| / Sum(|Close[i] - Close[i-1]|, n)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `10` |

## Returns

| Column |
| --- |
| `ER_10` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.efficiency_ratio(df['close']).tail(3)
```

```text
date
2024-10-25    0.434691
2024-10-26    0.489035
2024-10-27    0.491207
Name: ER_10, dtype: float64
```

**Accessor form:** `df.zta.efficiency_ratio(...)`

## How to read it

`1` means the window trended in a straight line; near `0` means it churned in place. Often used as a regime filter feeding into another indicator's parameters, the way `kama` uses it internally, rather than traded on directly.

## Pitfalls

`0` on a perfectly flat window rather than an undefined `0/0`.

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/kaufmans-adaptive-moving-average-kama](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/kaufmans-adaptive-moving-average-kama)
