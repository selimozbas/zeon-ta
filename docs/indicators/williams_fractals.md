---
title: Williams Fractals
---

[← All indicators](../index.md)

`zeonta.williams_fractals()` — Bill Williams' 5-bar pivot: a high or low with two lower/higher bars on each side.

## What it measures

Bill Williams' 5-bar pivot test — the same strict local-extremum check [support_resistance](support_resistance.md) builds on, at that indicator's own `left=right=2`.

## Formula

```text
Bearish: High[i] > 2 highs each side; Bullish: Low[i] < 2 lows each side
```

## Parameters

**Required inputs:** `high`, `low`

_None._

## Returns

| Column |
| --- |
| `FRACTALB` |
| `FRACTALU` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.williams_fractals(df['high'], df['low']).tail(5)
```

```text
            FRACTALB  FRACTALU
date                          
2024-10-23   91.4888   88.9268
2024-10-24       NaN       NaN
2024-10-25       NaN       NaN
2024-10-26       NaN       NaN
2024-10-27       NaN       NaN
```

**Accessor form:** `df.zta.williams_fractals(...)`

## How to read it

A confirmed fractal marks a potential reversal point; Williams' own methodology pairs it with the Alligator and Awesome Oscillator rather than trading fractals alone.

## Pitfalls

A fractal is only knowable 2 bars after it happened (the two right-side bars must exist first) — unlike `support_resistance`'s `RES`/`SUP` columns, this does not shift the flag forward, so a fractal shown at bar i was not actually confirmed until bar i+2. Look ahead of the marked bar, not at it, if trading the confirmation.

## Reference

Formula source: [https://www.metatrader5.com/en/terminal/help/indicators/bw_indicators/fractals](https://www.metatrader5.com/en/terminal/help/indicators/bw_indicators/fractals)
