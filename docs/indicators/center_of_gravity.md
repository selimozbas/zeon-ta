---
title: Center of Gravity Oscillator (CG)
---

[← All indicators](../index.md)

`zeonta.center_of_gravity()` — Ehlers' zero-lag oscillator: the balance point of price over the window.

## What it measures

John Ehlers' balance-point oscillator: treats the window's prices as weights along a beam and finds where it would balance, then inverts the sign since that balance point moves in exact opposition to price swings. The result is a smoothed oscillator with essentially zero lag, unlike a conventional smoothed indicator that trades lag for smoothness.

## Formula

```text
Price = (High+Low)/2; CG = -sum((1+k)*Price[t-k], k=0..n-1) / sum(Price[t-k], k=0..n-1)
```

## Parameters

**Required inputs:** `high`, `low`

| Parameter | Default |
| --- | --- |
| `length` | `10` |

## Returns

| Column |
| --- |
| `CG_10` |
| `CGs_10` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.center_of_gravity(df['high'], df['low']).tail(3)
```

```text
               CG_10    CGs_10
date                          
2024-10-25 -5.518245 -5.520843
2024-10-26 -5.514617 -5.518245
2024-10-27 -5.515026 -5.514617
```

**Accessor form:** `df.zta.center_of_gravity(...)`

## How to read it

Ehlers' own suggested signal is the crossover between CG and its own one-bar-delayed trigger line — the same pattern [fisher_transform](fisher_transform.md) uses. Ideally, `length` should be about half the market's dominant cycle length.

## Pitfalls

The scale is not comparable across different `length` values or to price itself — Ehlers' own paper notes only the *shape* of the curve matters.

## Reference

Formula source: [https://www.mesasoftware.com/papers/TheCGOscillator.pdf](https://www.mesasoftware.com/papers/TheCGOscillator.pdf)
