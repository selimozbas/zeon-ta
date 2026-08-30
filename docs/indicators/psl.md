---
title: Psychological Line (PSL)
---

[← All indicators](../index.md)

`zeonta.psl()` — Percentage of up-closes over a rolling window — raw market sentiment.

## What it measures

A pure vote-counting sentiment gauge: the share of bars in a rolling window where price closed above the prior close, as a percentage. Unlike every ratio-based oscillator in this library ([rsi](rsi.md), [cmo](cmo.md), ...), PSL only asks *how often* price rose, never *by how much*.

## Formula

```text
PSL = (up-closing bars in the last n) / n * 100
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `12` |

## Returns

| Column |
| --- |
| `PSL_12` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.psl(df['close']).tail(3)
```

```text
date
2024-10-25    33.333333
2024-10-26    33.333333
2024-10-27    25.000000
Name: PSL_12, dtype: float64
```

**Accessor form:** `df.zta.psl(...)`

## How to read it

Above 50 means more than half the window's bars closed up; below 50 the mirror. Readings above roughly 75 or below 25 are commonly read as overbought/oversold sentiment extremes.

## Pitfalls

A flat close (unchanged from the prior bar) counts as *not* up, the same convention as most up/down-day counters.

## Reference

Formula source: [https://help.tradestation.com/10_00/eng/tradestationhelp/elanalysis/indicator/psychological_line_indicator_.htm](https://help.tradestation.com/10_00/eng/tradestationhelp/elanalysis/indicator/psychological_line_indicator_.htm)
