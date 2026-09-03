---
title: Higuchi Fractal Dimension
---

[← All indicators](../index.md)

`zeonta.higuchi_fractal_dimension()` — Fractal dimension of price itself, from curve-length scaling (Higuchi, 1988).

## What it measures

Higuchi (1988) estimates a time series' fractal dimension directly from its own curve, without going through returns first the way hurst_exponent and dfa do: it measures how much shorter the window's own path gets when only every k-th point is kept, for several step sizes k, and reads the fractal dimension off how fast that shrinkage compounds. It is also a different construction from frama()'s internal box-counting dimension, which compares high-low range at two window halves rather than resampling the price path itself.

## Formula

```text
For k = 1..k_max, resample the window every k-th point starting at each offset m = 1..k: L_m(k) = (N-1) / (floor((N-m)/k) x k^2) x sum |x(m+i x k) - x(m+(i-1) x k)|; L(k) = mean over m of L_m(k); HFD = slope of log(L(k)) regressed against log(1/k)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `window` | `100` |
| `k_max` | `10` |

## Returns

| Column |
| --- |
| `HFD_100_10` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.higuchi_fractal_dimension(df['close']).tail(3)
```

```text
date
2024-10-25    1.588714
2024-10-26    1.587688
2024-10-27    1.595381
Name: HFD_100_10, dtype: float64
```

**Accessor form:** `df.zta.higuchi_fractal_dimension(...)`

## How to read it

Reads the same way as any box-counting fractal dimension: values near 1 describe a path close to a straight line (a strong, persistent trend); values near 2 describe a path that fills space as roughly as pure noise (choppy, directionless). Unlike hurst_exponent/dfa, there is no 0.5 'random walk' reference point built into the reading — 1 and 2 are the two ends of the scale here, not a midpoint split.

## Pitfalls

k_max is a free parameter the original paper does not pin to one value; 10 is the convention most secondary literature on this method has settled on, not something Higuchi's own paper mandates. A short or unusually smooth window can produce fewer than two usable (k, L(k)) pairs to regress against, in which case the result is NaN rather than an unreliable single-point slope.

## Reference

Formula source: [https://doi.org/10.1016/0167-2789(88)90081-4](https://doi.org/10.1016/0167-2789(88)90081-4)
