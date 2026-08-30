---
title: Volume-Weighted MACD
---

[← All indicators](../index.md)

`zeonta.vwmacd()` — MACD built from Volume-Weighted Moving Averages instead of EMAs.

## What it measures

The same fast-minus-slow-then-signal shape as [macd](macd.md), but built from [vwma](vwma.md) instead of a plain EMA. Weighting the fast and slow lines by volume makes crossovers more representative of moves that traded heavily, rather than treating a thin, quiet bar the same as a heavily-traded one the way plain MACD does. The signal line stays a plain EMA — the MACD line itself already carries the volume weighting.

## Formula

```text
VWMACD = VWMA(fast) - VWMA(slow); Signal = EMA(VWMACD, signal); Histogram = VWMACD - Signal
```

## Parameters

**Required inputs:** `close`, `volume`

| Parameter | Default |
| --- | --- |
| `fast` | `12` |
| `slow` | `26` |
| `signal` | `9` |

## Returns

| Column |
| --- |
| `VWMACD_12_26_9` |
| `VWMACDs_12_26_9` |
| `VWMACDh_12_26_9` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.vwmacd(df['close'], df['volume']).tail(3)
```

```text
            VWMACD_12_26_9  VWMACDs_12_26_9  VWMACDh_12_26_9
date                                                        
2024-10-25       -0.220966        -0.248308         0.027342
2024-10-26       -0.261812        -0.251009        -0.010803
2024-10-27       -0.426664        -0.286140        -0.140524
```

**Accessor form:** `df.zta.vwmacd(...)`

## How to read it

Read exactly like `macd` — the crossover between the line and its own signal, or the line crossing zero.

## Pitfalls

Inherits `vwma`'s own zero-total-volume edge case: `NaN` wherever a window's total volume is exactly `0`.

## Reference

Formula source: [https://vectoralpha.dev/projects/ta/indicators/vwmacd/](https://vectoralpha.dev/projects/ta/indicators/vwmacd/)
