---
title: Cumulative Return
---

[← All indicators](../index.md)

`zeonta.cumulative_return()` — Cumulative percentage return since the start of the series.

## What it measures

The odd one out among this library's indicators: every other one only ever looks back a fixed *length* of bars, so its value at bar N is stable no matter how much history you later add before it. This instead anchors to bar 0 of whatever series you pass in — the running percentage gain or loss since the very start of *that* series.

## Formula

```text
CUMRET = (Close[t] / Close[0] - 1) * 100
```

## Parameters

**Required inputs:** `close`

_None._

## Returns

| Column |
| --- |
| `CUMRET` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.cumulative_return(df['close']).tail(3)
```

```text
date
2024-10-25    -9.195891
2024-10-26   -10.180769
2024-10-27   -10.822573
Name: CUMRET, dtype: float64
```

**Accessor form:** `df.zta.cumulative_return(...)`

## How to read it

A straightforward running total return line, the same shape an equity-curve chart plots — reads highest where price has run up the most since bar 0, lowest where it has run down the most.

## Pitfalls

Re-running this on a longer history changes *every* earlier value, since the anchor point (bar 0) moves with it — by design, since the question being asked is always 'return since the start of this series', but a real surprise if you expected the same stability every other indicator here gives you.

## Reference

Formula source: [https://en.wikipedia.org/wiki/Rate_of_return](https://en.wikipedia.org/wiki/Rate_of_return)
