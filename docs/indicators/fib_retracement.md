---
title: Fibonacci Retracement
---

[← All indicators](../index.md)

`zeonta.fib_retracement()` — Fibonacci retracement levels drawn from the most recent swing.

## What it measures

After a strong move, price rarely goes straight on — it gives some back. Fibonacci retracement marks the fractions of that move where the pullback most often stops. This implementation picks the swing automatically from a rolling window.

## Formula

```text
Ratios = 0.236, 0.382, 0.5, 0.618, 0.786 (derived from the Fibonacci sequence, 0.5 included by convention); after an uptrend, level = High - (High - Low) x ratio; after a downtrend, level = Low + (High - Low) x ratio; extensions use the same ratios beyond 100% (127.2%, 161.8%, 261.8%) to project targets
```

## Parameters

**Required inputs:** `high`, `low`

| Parameter | Default |
| --- | --- |
| `lookback` | `100` |
| `ratios` | `(0.236, 0.382, 0.5, 0.618, 0.786)` |
| `extensions` | `False` |

## Returns

| Column |
| --- |
| `FIB_0` |
| `FIB_1` |
| `FIB_0.236` |
| `FIB_0.382` |
| `FIB_0.5` |
| `FIB_0.618` |
| `FIB_0.786` |
| `FIBDIR` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.fib_retracement(df['high'], df['low'], lookback=60)[['FIB_0', 'FIB_0.382', 'FIB_0.618', 'FIB_1', 'FIBDIR']].tail(3)
```

```text
              FIB_0  FIB_0.382  FIB_0.618    FIB_1  FIBDIR
date                                                      
2024-10-25  88.9268  90.835769  92.015131  93.9241    -1.0
2024-10-26  88.9268  90.835769  92.015131  93.9241    -1.0
2024-10-27  88.0724  90.307749  91.688751  93.9241    -1.0
```

**Accessor form:** `df.zta.fib_retracement(...)`

## How to read it

The 0.382-0.618 zone is where most tradeable pullbacks end; 0.786 is the last level before the move is usually considered failed. `FIBDIR` tells you which way the swing ran, so you know whether levels are measured down from the high or up from the low.

## Pitfalls

Fibonacci levels work because enough traders draw the same lines, not because of anything physical. Two people picking different swings get different levels and both can be "right". Since the swing here is recomputed each bar, the levels repaint as new extremes print.
