---
title: Hurst Exponent (Rescaled Range Analysis)
---

[← All indicators](../index.md)

`zeonta.hurst_exponent()` — How persistent recent price moves are: trending, mean-reverting, or a random walk.

## What it measures

Harold Hurst developed this while studying multi-year Nile River flood records in the 1950s, long before it was applied to markets; Rescaled Range (R/S) analysis is the classical estimator for it. Applied to a return series it measures *persistence* — whether a move tends to be followed by more of the same (trending) or by a reversal (mean-reverting) — a fundamentally different question from what any of this library's other indicators ask, which all measure price/momentum directly rather than the statistical character of the series generating it.

## Formula

```text
For each lag n: split the window's log returns into chunks of size n; R/S(n) = mean over chunks of range(cumulative mean-adjusted deviation) / std-dev(chunk); H = slope of log(R/S) regressed against log(n)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `window` | `100` |

## Returns

| Column |
| --- |
| `HURST_100` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.hurst_exponent(df['close']).tail(3)
```

```text
date
2024-10-25    0.641674
2024-10-26    0.603123
2024-10-27    0.584958
Name: HURST_100, dtype: float64
```

**Accessor form:** `df.zta.hurst_exponent(...)`

## How to read it

``H ≈ 0.5``: a random walk with no memory — past moves say nothing about future ones. ``H > 0.5``: trending/persistent — a move tends to be followed by more of the same. ``H < 0.5``: mean-reverting/anti-persistent — a move tends to be followed by a reversal. Many traders use this as a *regime filter*: lean on trend-following tools when ``H`` is comfortably above 0.5, lean on oscillators/mean-reversion tools when it sits below.

## Pitfalls

R/S analysis is the classical (1951) estimator, not the only one — other methods (DFA, the generalized Hurst exponent) exist and do not always agree with R/S on the same data, so treat this as an estimate from one specific, standard method rather than a settled physical constant of the series. It is also, by a wide margin, the slowest indicator in this library (see its own docstring and `BENCHMARKS.md`) — a rolling regression over multiple lag values on every bar, not the single vectorised pass every other indicator here uses.

## Reference

Formula source: [https://en.wikipedia.org/wiki/Hurst_exponent](https://en.wikipedia.org/wiki/Hurst_exponent)
