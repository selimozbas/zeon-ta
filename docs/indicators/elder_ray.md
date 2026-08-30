---
title: Elder Ray (Bull Power / Bear Power)
---

[← All indicators](../index.md)

`zeonta.elder_ray()` — Bull Power / Bear Power — the day's high and low measured against an EMA.

## What it measures

Developed by Alexander Elder as a way to look inside each individual bar relative to the prevailing trend rather than only at where it closed. Bull Power reads how far buyers managed to push price above the EMA within the bar; Bear Power reads how far sellers pushed it below. Two numbers per bar instead of one closing-price comparison captures the tug-of-war that happened *during* the bar, which the close alone erases.

## Formula

```text
EMA = EMA(Close, length); Bull Power = High - EMA; Bear Power = Low - EMA
```

## Parameters

**Required inputs:** `high`, `low`, `close`

| Parameter | Default |
| --- | --- |
| `length` | `13` |

## Returns

| Column |
| --- |
| `BULLP_13` |
| `BEARP_13` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.elder_ray(df['high'], df['low'], df['close']).tail(3)
```

```text
            BULLP_13  BEARP_13
date                          
2024-10-25  0.303033 -0.759267
2024-10-26 -0.081543 -1.227343
2024-10-27 -0.420822 -1.987922
```

**Accessor form:** `df.zta.elder_ray(...)`

## How to read it

In a healthy uptrend, Bull Power stays positive while Bear Power stays negative but shrinks toward zero bar by bar — sellers are losing their grip even during pullbacks. Bear Power turning positive, or Bull Power turning negative, while the EMA itself is still rising is the classic Elder Ray warning that the trend has lost control of the bar and a reversal may be near.

## Pitfalls

On a steady, non-accelerating trend, the EMA's own fixed lag can exceed the bar's high-low spread, which flips Bear Power positive (in an uptrend) or Bull Power negative (in a downtrend) even though nothing about the trend has actually changed — a real property of how far a lagging EMA sits behind price, not a signal of weakness. Elder's own rule reads the two lines *together* with the EMA's slope, never Bull or Bear Power in isolation.

## Reference

Formula source: [https://www.tradingview.com/support/solutions/43000717955-bull-bear-power/](https://www.tradingview.com/support/solutions/43000717955-bull-bear-power/)
