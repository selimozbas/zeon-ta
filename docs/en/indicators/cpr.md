# Central Pivot Range (CPR)

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/cpr.md)

`zeonta.cpr()` — Classic pivot with a width band (Top/Bottom Central) around it, from the prior bar.

## What it measures

The same classic pivot [pivot_points](pivot_points.md) computes, plus a width band (Bottom Central, Top Central) built from the same previous bar's range. The band's width is always exactly two-thirds of the distance between the previous close and the previous range's midpoint.

## Formula

```text
Pivot=(H+L+C)/3; BC=(H+L)/2; TC=2*Pivot-BC
```

## Parameters

**Required inputs:** `high`, `low`, `close`

_None._

## Returns

| Column |
| --- |
| `CPR_PIVOT` |
| `CPR_BC` |
| `CPR_TC` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.cpr(df['high'], df['low'], df['close']).tail(3)
```

```text
            CPR_PIVOT    CPR_BC     CPR_TC
date                                      
2024-10-25  90.649533  90.72185  90.577217
2024-10-26  90.229367  90.29595  90.162783
2024-10-27  89.485600  89.66890  89.302300
```

**Accessor form:** `df.zta.cpr(...)`

## How to read it

A narrow CPR means the prior bar closed near the middle of its own range (indecision, often preceding a bigger move); a wide CPR means it closed near an extreme (a directional bar, often preceding continuation).

## Pitfalls

Like `pivot_points`, levels are computed from the **previous** bar and apply to the current one — feed daily bars for daily CPR levels, weekly bars for weekly ones.

## Reference

Formula source: [https://www.luxalgo.com/library/concept/central-pivot-range/](https://www.luxalgo.com/library/concept/central-pivot-range/)
