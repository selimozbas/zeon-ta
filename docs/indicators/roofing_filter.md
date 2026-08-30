---
title: Roofing Filter
---

[← All indicators](../index.md)

`zeonta.roofing_filter()` — 2-pole highpass then a SuperSmoother low-pass, isolating a chosen band of cycles.

## What it measures

Removes both ends of the spectrum from price: a 2-pole high-pass removes cycles longer than `hp_length` (slow drift an oscillator shouldn't react to), and [super_smoother](super_smoother.md) then removes cycles shorter than `lp_length` (the aliasing noise a plain moving average lets through). What's left is only the band of cycles between the two.

## Formula

```text
2-pole highpass(Close, hp_length) then SuperSmoother(., lp_length): keeps only cycles between lp_length and hp_length bars
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `hp_length` | `48` |
| `lp_length` | `10` |

## Returns

| Column |
| --- |
| `ROOF_48_10` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.roofing_filter(df['close']).tail(3)
```

```text
date
2024-10-25   -0.159426
2024-10-26   -0.137719
2024-10-27   -0.354899
Name: ROOF_48_10, dtype: float64
```

**Accessor form:** `df.zta.roofing_filter(...)`

## How to read it

Ehlers designed this specifically to precede other oscillators — feeding this into [stoch](stoch.md) or [rsi](rsi.md) instead of raw price makes them react to genuine cycles rather than trend or noise.

## Pitfalls

Not an oscillator on its own — it has no fixed range and no natural zero line. It's a pre-processing filter meant to sit in front of one.

## Reference

Formula source: [https://www.mesasoftware.com/papers/SwissArmyKnifeIndicator.pdf](https://www.mesasoftware.com/papers/SwissArmyKnifeIndicator.pdf)
