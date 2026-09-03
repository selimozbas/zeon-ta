---
title: Fixed-Width Window Fractional Differentiation
---

[← All indicators](../index.md)

`zeonta.ffd()` — Fractionally differenced price with a fixed-width weight window (Lopez de Prado).

## What it measures

Plain differencing (a 1-bar log_return or Close.diff()) makes a price series stationary but throws away all memory of its own level along with it. Lopez de Prado (2018) generalizes differencing to a fractional order d between 0 and 1 via the binomial series expansion of (1-B)^d, then truncates that expansion's weights to a fixed count once they fall below a threshold — the 'fixed-width window' this method is named for, as opposed to the same book's expanding-window variant, which reweights a series' entire history at every bar instead of a fixed trailing window.

## Formula

```text
w_0 = 1, w_k = -w_{k-1} x (d-k+1)/k generated until |w_k| < threshold (l* weights kept); FFD[t] = sum(w_k x Close[t-k], k = 0..l*)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `d` | `0.5` |
| `threshold` | `0.001` |

## Returns

| Column |
| --- |
| `FFD_0.5_0.001` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.ffd(df['close']).tail(3)
```

```text
date
2024-10-25    7.325091
2024-10-26    6.540558
2024-10-27    6.438725
Name: FFD_0.5_0.001, dtype: float64
```

**Accessor form:** `df.zta.ffd(...)`

## How to read it

d close to 0 barely differences the series (it stays close to raw Close, and non-stationary); d close to 1 approaches plain first differencing (stationary, but memory-free). The book's own point is to search for the smallest d that a stationarity test (e.g. ADF) accepts, keeping as much memory as the transform allows — this function computes the transform for a d you choose, not that search.

## Pitfalls

threshold controls a real memory/window-length trade-off, not just a numerical nicety: the book's own default (1e-5) keeps several hundred weights even at d=0.5, which needs a correspondingly long history before the first output bar. This function defaults to a shorter, more usable 1e-3 instead — the weight recursion and truncation rule are unchanged from the book, only the default cutoff is this library's own choice, the same way many rolling-window defaults elsewhere here are a reasonable pick rather than something the source itself mandates.

## Reference

Formula source: [https://doi.org/10.1002/9781119482086](https://doi.org/10.1002/9781119482086)
