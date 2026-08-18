# Wavelet-Denoised Price (Discrete Wavelet Transform)

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/wavelet_denoise.md)

`zeonta.wavelet_denoise()` — Causal rolling wavelet (DWT) denoising: cuts noise without an EMA's lag.

## What it measures

Wavelet transforms split a series into frequency bands the way a Fourier transform does, but — unlike Fourier — keep time localisation: they show *when* a frequency occurs, not just that it does. Academic work on wavelet-denoised technical indicators (e.g. de-noising return series before building new indicators on top of them) exploits exactly this to separate genuine price structure from noise without the lag an SMA/EMA adds. Classic wavelet denoising decomposes an entire series in a single pass, which is fine for an offline study but means every bar's value can depend on bars that come after it. This implementation instead re-runs the decomposition from scratch on every rolling `window`, using nothing past the current bar — see its own docstring for why that distinction matters for anything meant to generate live signals.

## Formula

```text
For each rolling window: DWT-decompose into an approximation band and `level` detail bands; sigma = MAD(finest detail band) / 0.6745; soft-threshold every detail band at sigma*sqrt(2*log(window)); reconstruct and keep only the window's last sample
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `window` | `64` |
| `wavelet` | `'db4'` |
| `level` | `2` |

## Returns

| Column |
| --- |
| `WDENOISE_64_db4` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.wavelet_denoise(df['close']).tail(3)
```

```text
date
2024-10-25    90.191874
2024-10-26    89.518209
2024-10-27    88.777733
Name: WDENOISE_64_db4, dtype: float64
```

**Accessor form:** `df.zta.wavelet_denoise(...)`

## How to read it

This is a building block, not a finished signal: it returns a denoised price series meant to be fed into an existing indicator in place of raw `close` — e.g. `zeonta.rsi(zeonta.wavelet_denoise(df['close']))` or the same for `macd` — to get a lower-lag version of it. Used on its own as a trendline, it turns roughly the way a Super Smoother or Instantaneous Trendline does, but rejects noise by frequency-band thresholding rather than by a fixed recursive filter.

## Pitfalls

The rolling window means each bar re-decomposes from scratch rather than one vectorised pass — measure it on your own data before using it on a large history (see `BENCHMARKS.md`). The wavelet family and decomposition level are real choices, not defaults to ignore: `db4` at level 2 is what published work on wavelet-denoised indicators most often uses, but a different pairing changes the result. And because a longer lookback resolves lower frequencies at the cost of reacting more slowly, `window` is trading the same lag-versus-noise tradeoff every smoother in this library makes — just via a different mechanism.

## Reference

Formula source: [https://doi.org/10.1093/biomet/81.3.425](https://doi.org/10.1093/biomet/81.3.425)
