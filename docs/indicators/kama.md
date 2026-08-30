---
title: Kaufman's Adaptive Moving Average (KAMA)
---

[← All indicators](../index.md)

`zeonta.kama()` — Adapts its own smoothing to how efficiently price is trending.

## What it measures

Every fixed-length moving average is a compromise: short enough to catch real moves, long enough to ignore noise, and wrong for whichever regime it wasn't tuned for. KAMA sidesteps the trade-off by measuring, bar by bar, how efficiently price is trending (the Efficiency Ratio) and using that to slide its own speed between a fast and a slow EMA automatically.

## Formula

```text
Efficiency Ratio ER = |Close - Close (n periods ago)| / Sum(|Close - Prior Close|, n); Smoothing Constant SC = [ER x (fastest SC - slowest SC) + slowest SC]^2, where fastest SC = 2/(fast+1) and slowest SC = 2/(slow+1); KAMA = Prior KAMA + SC x (Close - Prior KAMA)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `10` |
| `fast` | `2` |
| `slow` | `30` |

## Returns

| Column |
| --- |
| `KAMA_10_2_30` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.kama(df['close'], length=10, fast=2, slow=30).tail(3)
```

```text
date
2024-10-25    91.133245
2024-10-26    90.873663
2024-10-27    90.563219
Name: KAMA_10_2_30, dtype: float64
```

**Accessor form:** `df.zta.kama(...)`

## How to read it

Read it exactly like any other moving average — trend direction, support/resistance, crossovers — but trust it more through a regime change: it tightens onto price by itself when a clean trend starts and flattens out by itself when the market goes choppy, without you re-tuning a length.

## Pitfalls

KAMA is still reactive, not predictive — it adapts to a regime change after price has already started moving differently, the same lag every moving average has, just with a self-adjusting length. The Efficiency Ratio itself is noisy on short windows, so very small `length` values can make KAMA's speed jump around almost as much as price does.

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/kaufmans-adaptive-moving-average-kama](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/kaufmans-adaptive-moving-average-kama)
