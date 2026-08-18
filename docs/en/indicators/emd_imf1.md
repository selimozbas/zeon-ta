# Empirical Mode Decomposition — First IMF

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/emd_imf1.md)

`zeonta.emd_imf1()` — Empirical Mode Decomposition's first IMF: the dominant local oscillation.

## What it measures

Huang et al. (1998) built EMD as an alternative to Fourier and wavelet analysis for signals that are non-stationary and nonlinear — a price series among them. Rather than projecting onto a fixed basis (sines, or a wavelet's fixed mother function), EMD derives its own basis functions directly from the data's local extrema. This library exposes only the first of what a full decomposition would produce: the fastest local oscillation, with slower components (later IMFs, and the residual trend a full decomposition ends with) left out, since a full decomposition's IMF count varies with the data and does not fit a fixed-column output.

## Formula

```text
Sift close within a rolling window: fit natural cubic splines through its local maxima and minima to form upper/lower envelopes, subtract their mean, repeat on the result until the Cauchy-type convergence measure SD < sd_threshold or max_iterations is reached; the result is the first Intrinsic Mode Function
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `window` | `100` |
| `max_iterations` | `50` |
| `sd_threshold` | `0.25` |

## Returns

| Column |
| --- |
| `EMDIMF1_100` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.emd_imf1(df['close']).tail(3)
```

```text
date
2024-10-25    0.765580
2024-10-26   -0.421528
2024-10-27   -1.444587
Name: EMDIMF1_100, dtype: float64
```

**Accessor form:** `df.zta.emd_imf1(...)`

## How to read it

`close - zeonta.emd_imf1(close, window)` approximates the trend/cycle residual a full decomposition would isolate, though it is not exactly that residual — only one IMF has been removed, not the full recursive decomposition down to a monotonic trend. Used directly, IMF1 behaves like a cycle/noise extraction, similar in spirit to what `wavelet_denoise` removes but from the opposite direction: this keeps the fast component rather than filtering it out.

## Pitfalls

By far the most expensive indicator in this library to compute: every bar re-runs an iterative spline-fitting loop over its own window, not a single vectorised pass (see `BENCHMARKS.md`). Boundary handling is a known, real weak point of EMD in general — this implementation deliberately does not anchor the envelope splines to the window's own first/last sample (an earlier version did, and it turned out to force every sifted value at the boundary to exactly 0.0, caught by noticing a suspiciously exact zero rather than trusting the formula); letting the natural cubic spline extrapolate past the outermost real extremum instead avoids that specific artifact, but boundary bars are still the least reliable part of any EMD window for that reason.

## Reference

Formula source: [https://doi.org/10.1098/rspa.1998.0193](https://doi.org/10.1098/rspa.1998.0193)
