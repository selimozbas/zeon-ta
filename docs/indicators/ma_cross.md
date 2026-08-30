---
title: Moving Average Crossovers
---

[← All indicators](../index.md)

`zeonta.ma_cross()` — Fast/slow moving-average crossover signals (golden and death cross).

## What it measures

Two averages of different lengths, and a signal whenever they swap places. The 50/200 pair has famous names — the golden cross and the death cross — and gets reported in the financial press, which is part of why it moves markets at all.

## Formula

```text
Bullish crossover (golden cross when fast=50, slow=200): fastMA[i-1] <= slowMA[i-1] and fastMA[i] > slowMA[i]. Bearish crossunder (death cross): fastMA[i-1] >= slowMA[i-1] and fastMA[i] < slowMA[i].
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `fast` | `50` |
| `slow` | `200` |
| `mode` | `'sma'` |

## Returns

| Column |
| --- |
| `MAfast_50` |
| `MAslow_200` |
| `cross_50_200` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.ma_cross(df['close'], fast=20, slow=50).query('cross_20_50 != 0').tail(3)
```

```text
            MAfast_20  MAslow_50  cross_20_50
date                                         
2024-06-29  96.420760  96.434442         -1.0
2024-07-11  97.134010  97.088798          1.0
2024-07-20  96.591125  96.678434         -1.0
```

**Accessor form:** `df.zta.ma_cross(...)`

## How to read it

The `cross` column is `1.0` on the bar the fast average crosses above the slow one, `-1.0` when it crosses below, and `0.0` otherwise. Many traders use the crossover as a regime filter — only take longs while the fast average is on top — rather than as an entry trigger.

## Pitfalls

Because both inputs lag, the crossover lags twice over: by the time a golden cross prints, a large part of the move is usually behind you. In a range the pair crosses back and forth repeatedly, and trading each one mechanically bleeds money.
