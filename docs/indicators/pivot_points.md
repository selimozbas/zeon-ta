---
title: Pivot Points
---

[← All indicators](../index.md)

`zeonta.pivot_points()` — Classic or Fibonacci pivot levels derived from the previous bar.

## What it measures

A grid of levels for today, computed from yesterday's range before the market even opens. Floor traders used them precisely because they need no chart and no recalculation during the session.

## Formula

```text
Classic: Pivot = (High + Low + Close) / 3; R1 = 2xPivot - Low; S1 = 2xPivot - High; R2 = Pivot + (High - Low); S2 = Pivot - (High - Low); R3 = Pivot + 2x(High - Low); S3 = Pivot - 2x(High - Low). Fibonacci: R1/S1 = Pivot +/- 0.382x(High - Low); R2/S2 = Pivot +/- 0.618x(High - Low); R3/S3 = Pivot +/- 1.0x(High - Low)
```

## Parameters

**Required inputs:** `high`, `low`, `close`

| Parameter | Default |
| --- | --- |
| `kind` | `'classic'` |

## Returns

| Column |
| --- |
| `PP_classic` |
| `R1_classic` |
| `R2_classic` |
| `R3_classic` |
| `S1_classic` |
| `S2_classic` |
| `S3_classic` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.pivot_points(df['high'], df['low'], df['close'], kind='classic').tail(2)
```

```text
            PP_classic  R1_classic  R2_classic  R3_classic  S1_classic  S2_classic  S3_classic
date                                                                                          
2024-10-26   90.229367   90.693933   91.291667   92.353967   89.631633   89.167067   88.104767
2024-10-27   89.485600   89.875200   90.631400   91.777200   88.729400   88.339800   87.194000
```

**Accessor form:** `df.zta.pivot_points(...)`

## How to read it

The central pivot is the day's reference: trading above it is a bullish session, below it bearish. R1/S1 are the levels reached on an ordinary day; R3/S3 only come into play on a big one. Feed daily bars for daily pivots, weekly bars for weekly ones.

## Pitfalls

Pivots are arithmetic, not analysis — they carry no information beyond the previous bar's range and work mainly as a shared reference grid. They are far less meaningful on instruments without a real session boundary. Classic R3/S3 has no single universally cited formula (StockCharts' own Classic page does not define R3/S3 at all); this library follows TradingView's own documented formula, confirmed empirically against a live reading.

## Reference

Formula source: [https://www.tradingview.com/support/solutions/43000521824-pivot-points-standard/](https://www.tradingview.com/support/solutions/43000521824-pivot-points-standard/)
