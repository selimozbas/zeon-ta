---
title: Conditional Drawdown at Risk (CDaR)
---

[← All indicators](../index.md)

`zeonta.cdar()` — Conditional Drawdown at Risk: average of the worst drawdowns in a rolling window.

## What it measures

The CVaR/Expected-Shortfall construction applied to a drawdown series instead of a return series, reusing drawdown rather than recomputing the running peak. Chekhlov, Uryasev & Zabarankin (2005) originally define this as a Rockafellar-Uryasev-style optimization, but their own Theorem 1 proves the optimum coincides exactly with the worst-fraction average implemented here — a closed-form equivalent, not an independent approximation.

## Formula

```text
k = ceil((1-alpha)*length); CDaR = mean of the k largest drawdown magnitudes (-drawdown) in the rolling window
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `100` |
| `alpha` | `0.95` |

## Returns

| Column |
| --- |
| `CDAR_100_0.95` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.cdar(df['close']).tail(3)
```

```text
date
2024-10-25    13.660438
2024-10-26    13.841578
2024-10-27    14.100074
Name: CDAR_100_0.95, dtype: float64
```

**Accessor form:** `df.zta.cdar(...)`

## How to read it

Reported as a positive percentage, like ulcer_index, not signed like drawdown itself — 8.0 reads as 'the expected worst-case drawdown magnitude over this window is about 8%'. alpha=0.95 (the default) means 'the average of the worst 5% of drawdowns in the window'.

## Pitfalls

CDaR contains the maximal drawdown (alpha -> 1, k -> 1) and the average drawdown (alpha -> 0, k -> length) as its two limiting cases — a useful sanity check when picking alpha. NaN for warm-up bars and any window containing a non-finite drawdown.

## Reference

Formula source: [https://doi.org/10.21314/JCF.2005.121](https://doi.org/10.21314/JCF.2005.121)
