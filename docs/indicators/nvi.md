---
title: Negative Volume Index (NVI)
---

[← All indicators](../index.md)

`zeonta.nvi()` — Cumulative index that only moves on a bar where volume fell versus the prior bar.

## What it measures

Paul Dysart's idea from the 1930s-40s, popularised by Norman Fosback: price moves on *quiet* (falling) volume days are more likely to reflect informed money moving without drawing a crowd, while moves on heavy volume days reflect crowd-driven activity. NVI only updates on the quiet days, holding flat through every heavy-volume bar — the mirror-image complement of [pvi](pvi.md).

## Formula

```text
Starts at 1000. When Volume[i] < Volume[i-1]: NVI[i] = NVI[i-1] * (1 + (Close[i]-Close[i-1])/Close[i-1]); otherwise unchanged
```

## Parameters

**Required inputs:** `close`, `volume`

_None._

## Returns

| Column |
| --- |
| `NVI` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.nvi(df['close'], df['volume']).tail(3)
```

```text
date
2024-10-25    1093.934042
2024-10-26    1082.069032
2024-10-27    1074.337105
Name: NVI, dtype: float64
```

**Accessor form:** `df.zta.nvi(...)`

## How to read it

StockCharts' own long-run study found the market was more often in a bull market when NVI sat above its own 255-day moving average than below it — used as a long-term, low-frequency regime read rather than a short-term signal.

## Pitfalls

The starting value of `1000` is a convention (StockCharts'), not a law of the formula — some other implementations start at `100` or `1`. Only ever compare an NVI series against itself (its own moving average, or its own history), never its absolute level against a different symbol's.

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/negative-volume-index-nvi](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/negative-volume-index-nvi)
