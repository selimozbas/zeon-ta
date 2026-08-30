---
title: Support and Resistance
---

[← All indicators](../index.md)

`zeonta.support_resistance()` — Confirmed swing pivots and the most recent support/resistance they mark.

## What it measures

Support and resistance are not lines someone draws by eye — they are prices the market has already turned at. This function finds those turning points mechanically as swing pivots, then carries the most recent confirmed one forward as a usable level.

## Formula

```text
Pivot High(leftBars, rightBars) at bar i: High[i] > High[i-leftBars..i-1] and High[i] > High[i+1..i+rightBars] (local maximum). Pivot Low is the mirror. A price where multiple pivots cluster becomes a support/resistance level.
```

## Parameters

**Required inputs:** `high`, `low`

| Parameter | Default |
| --- | --- |
| `left` | `10` |
| `right` | `10` |

## Returns

| Column |
| --- |
| `PIVOTHIGH_10_10` |
| `PIVOTLOW_10_10` |
| `RES_10_10` |
| `SUP_10_10` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.support_resistance(df['high'], df['low'], left=5, right=5)[['RES_5_5', 'SUP_5_5']].tail(3)
```

```text
            RES_5_5  SUP_5_5
date                        
2024-10-25  92.9721  89.7116
2024-10-26  92.9721  89.7116
2024-10-27  92.9721  89.7116
```

```python
zeonta.sr_levels(df['high'], df['low'], left=5, right=5, max_levels=3)
```

```text
       level  touches     kind
0  93.029363       16     both
1  95.336044        9     both
2  90.813267        3  support
```

**Accessor form:** `df.zta.support_resistance(...)`

## How to read it

`PIVOTHIGH` / `PIVOTLOW` mark where a swing actually formed. `RES` / `SUP` hold the most recent confirmed level and are the columns to trade against. Use `sr_levels()` when you want the clustered levels ranked by how many times each was touched.

## Pitfalls

A pivot cannot be known until `right` more bars have printed, so the `PIVOTHIGH` / `PIVOTLOW` columns contain look-ahead information — they place the pivot on the bar it occurred, not the bar you learned about it. Backtest against `RES` / `SUP`, which are already delayed by `right` bars.
