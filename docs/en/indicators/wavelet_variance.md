# Multi-Scale Wavelet Variance (MODWT)

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/wavelet_variance.md)

`zeonta.wavelet_variance()` — Multi-scale volatility (MODWT): how much movement lives at each timescale.

## What it measures

atr() and a rolling standard deviation both answer 'how much did price move' with a single blended number. Percival & Walden's 'Wavelet Methods for Time Series Analysis' (2000) — the standard reference for this technique — splits that number apart by timescale using the Maximal Overlap DWT: because it is energy-conserving (unlike a plain DWT), the resulting per-scale variances are a genuine decomposition of total variance, not independent or overlapping readings. `wavelet_denoise` in this library uses an ordinary DWT to reconstruct a filtered price; this instead keeps the raw per-scale energy to describe the shape of the volatility itself.

## Formula

```text
For each rolling window: MODWT-decompose (norm=True, trim_approx=True) into `level` detail bands; WVAR_j = mean(detail_band_j ** 2) for each level j, 1 (finest) through `level` (coarsest)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `window` | `64` |
| `wavelet` | `'db4'` |
| `level` | `5` |

## Returns

| Column |
| --- |
| `WVAR_1` |
| `WVAR_2` |
| `WVAR_3` |
| `WVAR_4` |
| `WVAR_5` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.wavelet_variance(df['close']).tail(3)
```

```text
              WVAR_1    WVAR_2    WVAR_3    WVAR_4    WVAR_5
date                                                        
2024-10-25  0.057980  0.051089  0.129020  0.131990  0.287943
2024-10-26  0.057469  0.066789  0.128876  0.181626  0.311155
2024-10-27  0.061135  0.104635  0.155178  0.230250  0.334630
```

**Accessor form:** `df.zta.wavelet_variance(...)`

## How to read it

Each `WVAR_j` column covers a doubling band of bars (`WVAR_1` ~ 2-4 bars, `WVAR_2` ~ 4-8, and so on up to `WVAR_{level}`). A bar where the finest bands dominate is mostly high-frequency noise (thin books, HFT churn); one where the coarsest bands dominate reflects a genuine slower move — a distinction a single ATR reading cannot make since it always blends every timescale into one number. Traders use this as a regime read: which kind of volatility is currently driving the tape.

## Pitfalls

This uses the *biased* wavelet-variance estimator (average over every coefficient in the window) rather than Percival & Walden's *unbiased* one (which excludes boundary-affected coefficients) — simpler and always defined for any window/level pair, at the cost of a small bias the academic literature documents. `window` must be an exact multiple of `2**level`, a hard MODWT requirement, not a tunable default. And like `wavelet_denoise`, every bar re-runs its own decomposition rather than one pass over the whole series — measure it on your own data before a large history (see `BENCHMARKS.md`).

## Reference

Formula source: [https://staff.washington.edu/dbp/wmtsa.html](https://staff.washington.edu/dbp/wmtsa.html)
