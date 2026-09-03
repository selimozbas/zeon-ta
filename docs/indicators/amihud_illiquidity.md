---
title: Amihud Illiquidity Ratio
---

[← All indicators](../index.md)

`zeonta.amihud_illiquidity()` — Average price impact per dollar traded: a coarse, cross-market illiquidity proxy.

## What it measures

Amihud (2002) proposes the simplest possible price-impact proxy available from daily bars alone: how far price moves, per dollar of volume that traded. A bar that swings a lot on thin dollar volume is illiquid — a small order was enough to move the price; a bar that barely moves on heavy dollar volume is liquid. Averaged over a window, this gives a rough, easily computed stand-in for the microstructure-level measures (quoted spreads, order-book depth) that need data most markets and most history don't have.

## Formula

```text
ILLIQ = mean(|R_t| / DollarVolume_t, length), R_t = (Close_t - Close_{t-1}) / Close_{t-1}, DollarVolume_t = Close_t x Volume_t
```

## Parameters

**Required inputs:** `close`, `volume`

| Parameter | Default |
| --- | --- |
| `length` | `21` |

## Returns

| Column |
| --- |
| `AMIHUD_21` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.amihud_illiquidity(df['close'], df['volume']).tail(3)
```

```text
date
2024-10-25    1.368973e-10
2024-10-26    1.443496e-10
2024-10-27    1.572156e-10
Name: AMIHUD_21, dtype: float64
```

**Accessor form:** `df.zta.amihud_illiquidity(...)`

## How to read it

Higher values mean less liquidity (more price impact per dollar traded); lower values mean more. Amihud's own paper uses ILLIQ cross-sectionally, ranking many stocks against each other and against their own history — the raw number is not comparable across instruments quoted in different currencies or at very different price and volume levels without further normalization.

## Pitfalls

A bar with zero dollar volume produces an undefined ratio (treated as NaN, not infinite), which only makes the windows still containing it NaN rather than corrupting the series from that point on. length=21 (roughly one trading month) is this library's own choice of averaging window, not something the 2002 paper prescribes — the paper's own cross-sectional study averages over a full year.

## Reference

Formula source: [https://doi.org/10.1016/S1386-4181(01)00024-6](https://doi.org/10.1016/S1386-4181(01)00024-6)
