---
title: Reflex and Trendflex
---

[← All indicators](../index.md)

`zeonta.reflex_trendflex()` — Ehlers' zero-lag pair: deviation from a fitted line (cycle) vs. current value.

## What it measures

Both start from the same [super_smoother](super_smoother.md) pass at half `length`, then average that filtered line's own deviation from a reference over the full window — Reflex measures deviation from a straight line drawn across the window (stripping trend, isolating cycle swings), Trendflex measures deviation from the filtered line's *current* value (keeping trend in).

## Formula

```text
Filt = SuperSmoother(Close, length/2); Reflex = mean(Filt+k*Slope-Filt[-k]) / sqrt(MS); Trendflex = mean(Filt-Filt[-k]) / sqrt(MS)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `20` |

## Returns

| Column |
| --- |
| `REFLEX_20` |
| `TRENDFLEX_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.reflex_trendflex(df['close']).tail(3)
```

```text
            REFLEX_20  TRENDFLEX_20
date                               
2024-10-25  -0.119571     -0.845713
2024-10-26  -0.412141     -0.866909
2024-10-27  -0.910793     -1.203085
```

**Accessor form:** `df.zta.reflex_trendflex(...)`

## How to read it

Both self-normalize against their own recent mean square, the same "divide by local RMS" idea [even_better_sinewave](even_better_sinewave.md) uses, so their scale stays comparable across different volatility regimes — read zero-line crossings and extremes the same way you would any zero-lag oscillator.

## Pitfalls

Reflex and Trendflex answer different questions from the same input — Reflex isolates the cycle, Trendflex keeps the trend — so reading one where you meant the other gives a misleading signal even though both are always well-defined together.

## Reference

Formula source: [https://www.prorealcode.com/prorealtime-indicators/reflex-and-trendflex-indicators-john-f-ehlers/](https://www.prorealcode.com/prorealtime-indicators/reflex-and-trendflex-indicators-john-f-ehlers/)
