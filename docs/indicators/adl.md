---
title: Accumulation/Distribution Line (ADL)
---

[← All indicators](../index.md)

`zeonta.adl()` — Running total of volume weighted by where the close sits in its own range.

## What it measures

Where `obv` only asks whether the close was up or down and assigns the *entire* bar's volume to one side or the other, ADL asks *where inside the bar's full range* the close landed and weights volume by that graded position instead — a bar that closed near, but not exactly at, the high contributes most (not all) of its volume positively. It is also the running-total version of `cmf`, which instead sums the same per-bar flow over a fixed window and divides by volume to get a bounded ratio.

## Formula

```text
MFM = ((Close - Low) - (High - Close)) / (High - Low); MFV = MFM x Volume; ADL = Previous ADL + MFV
```

## Parameters

**Required inputs:** `high`, `low`, `close`, `volume`

_None._

## Returns

| Column |
| --- |
| `ADL` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.adl(df['high'], df['low'], df['close'], df['volume']).tail(3)
```

```text
date
2024-10-25    1.563072e+06
2024-10-26    1.207817e+06
2024-10-27    1.082389e+06
Name: ADL, dtype: float64
```

**Accessor form:** `df.zta.adl(...)`

## How to read it

Read it exactly like `obv`: the absolute level is arbitrary (it depends on where the series happens to start), only its *slope* and its agreement or disagreement with price matter. ADL rising while price is flat or falling is read as accumulation building beneath the surface — the same bullish-divergence idea `obv` is used for, just with a more graded input.

## Pitfalls

A very narrow high-low range makes the Money Flow Multiplier's denominator tiny, so ordinary volume on a quiet bar can swing ADL sharply even though little actually happened — this implementation defines the exact zero-range case as contributing nothing rather than blowing up, but near-zero ranges are still noisy. Like `obv`, it is a running total with no natural reset point, so comparing absolute levels across two different time windows tells you nothing.

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/accumulation-distribution-line](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/accumulation-distribution-line)
