---
title: Detrended Fluctuation Analysis (DFA)
---

[← All indicators](../index.md)

`zeonta.dfa()` — Detrended Fluctuation Analysis: a scaling exponent for persistence, robust to trends.

## What it measures

Peng et al. (1994) developed DFA to detect long-range correlations in DNA sequences without being fooled by the sequence's own local trends — the same non-stationarity problem a price series has. It estimates the same underlying quantity hurst_exponent's classical (1951) R/S analysis does, from the same rolling window of log returns, but by explicitly removing a local linear trend from every box before measuring fluctuation, rather than assuming the window is already trend-free.

## Formula

```text
profile = cumsum(log_returns_window - mean(log_returns_window)); for each box size n: split profile into non-overlapping n-length boxes, detrend each with a local linear fit, pool squared residuals into F(n) = sqrt(mean(residual^2)); DFA = slope of log(F(n)) regressed against log(n)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `window` | `100` |

## Returns

| Column |
| --- |
| `DFA_100` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.dfa(df['close']).tail(3)
```

```text
date
2024-10-25    0.492814
2024-10-26    0.481514
2024-10-27    0.584808
Name: DFA_100, dtype: float64
```

**Accessor form:** `df.zta.dfa(...)`

## How to read it

Same scale as hurst_exponent: ``alpha ~= 0.5`` random walk, ``alpha > 0.5`` persistent/trending, ``alpha < 0.5`` anti-persistent/mean-reverting. Because DFA explicitly detrends each box, it stays reliable through a genuine trend or regime shift inside the window where R/S analysis can be pulled off by that trend alone — the two indicators are worth comparing on the same series precisely when they might disagree.

## Pitfalls

This is DFA1 (linear local detrending) — higher-order variants (DFA2, DFA3, quadratic/cubic local fits) exist and can differ on the same data, so treat this as one specific, standard order of the method, the same caveat hurst_exponent's own docstring gives for R/S versus other Hurst estimators. Like hurst_exponent, this is a per-bar rolling regression over several box sizes, not a single vectorised pass — measure it on your own data before a large history (see `BENCHMARKS.md`).

## Reference

Formula source: [https://doi.org/10.1103/PhysRevE.49.1685](https://doi.org/10.1103/PhysRevE.49.1685)
