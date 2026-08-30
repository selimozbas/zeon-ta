---
title: Positive Volume Index (PVI)
---

[← All indicators](../index.md)

`zeonta.pvi()` — Cumulative index that only moves on a bar where volume rose versus the prior bar.

## What it measures

The mirror-image complement of [nvi](nvi.md): only updates on a bar where volume *rose* versus the bar before it, holding flat through every quiet-volume bar. Built on the same Dysart/Fosback idea, from the opposite side — heavy volume days reflect crowd-driven activity rather than informed money.

## Formula

```text
Starts at 1000. When Volume[i] > Volume[i-1]: PVI[i] = PVI[i-1] * (1 + (Close[i]-Close[i-1])/Close[i-1]); otherwise unchanged
```

## Parameters

**Required inputs:** `close`, `volume`

_None._

## Returns

| Column |
| --- |
| `PVI` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.pvi(df['close'], df['volume']).tail(3)
```

```text
date
2024-10-25    830.069322
2024-10-26    830.069322
2024-10-27    830.069322
Name: PVI, dtype: float64
```

**Accessor form:** `df.zta.pvi(...)`

## How to read it

Read the opposite way from NVI in the classic Fosback framework: PVI is treated as the noisier, crowd-driven half of the pair, so less weight is typically put on it alone than on NVI's own long-run signal.

## Pitfalls

Same starting-value caveat as `nvi`: `1000` is StockCharts'/Fidelity's convention, not a universal constant — compare a PVI series only against itself.

## Reference

Formula source: [https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/positive-volume-index](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/positive-volume-index)
