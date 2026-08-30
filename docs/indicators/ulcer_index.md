---
title: Ulcer Index
---

[← All indicators](../index.md)

`zeonta.ulcer_index()` — Drawdown-based risk measure — the expected percentage decline, not price swing size.

## What it measures

Unlike `atr` or `bbands`, which measure movement in *either* direction, the Ulcer Index (Peter Martin, 1987) only measures how far price has fallen from its own recent high — squaring the drawdown before averaging means a single deep decline dominates the reading far more than several small ones of the same total size, mirroring how a real drawdown actually feels to hold through.

## Formula

```text
PercentDrawdown = (Close - HighestClose(n)) / HighestClose(n) x 100; UI = sqrt(mean(PercentDrawdown^2, n))
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `14` |

## Returns

| Column |
| --- |
| `UI_14` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.ulcer_index(df['close']).tail(3)
```

```text
date
2024-10-25    1.909861
2024-10-26    2.083540
2024-10-27    2.327038
Name: UI_14, dtype: float64
```

**Accessor form:** `df.zta.ulcer_index(...)`

## How to read it

Higher readings mean deeper, more sustained drawdowns — a security a risk-averse holder would find harder to sit through, even if its raw price swings (as measured by `atr`) are not especially large. Comparing the Ulcer Index across candidate investments is a way to rank them by how much drawdown pain they have historically caused, independent of their average return.

## Pitfalls

Originally designed with mutual funds in mind and focused purely on downside risk — it says nothing about upside potential, so it should complement a return measure, not replace one.

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ulcer-index](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ulcer-index)
