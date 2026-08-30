---
title: Even Better Sinewave
---

[← All indicators](../index.md)

`zeonta.even_better_sinewave()` — A highpass-then-smoothed cycle, self-normalized to trace out an actual sine wave.

## What it measures

A highpass-then-smoothed cycle extraction, like [roofing_filter](roofing_filter.md), but divided by its own recent RMS amplitude so the result traces out an actual sine wave regardless of how big the underlying cycle currently is — the "even better" in the name is this self-normalization, versus Ehlers' earlier, unnormalized Sinewave Indicator.

## Formula

```text
HP = highpass(Close, hp_length); Filt = SuperSmoother(HP, lp_length); EBSW = mean(Filt,Filt[-1],Filt[-2]) / sqrt(mean(Filt^2,Filt[-1]^2,Filt[-2]^2))
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `hp_length` | `40` |
| `lp_length` | `10` |

## Returns

| Column |
| --- |
| `EBSW_40_10` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.even_better_sinewave(df['close']).tail(3)
```

```text
date
2024-10-25   -0.968824
2024-10-26   -0.984350
2024-10-27   -0.982904
Name: EBSW_40_10, dtype: float64
```

**Accessor form:** `df.zta.even_better_sinewave(...)`

## How to read it

Ranges roughly -1 to 1 like a genuine sine wave; zero-line crossings and peaks/troughs mark the cycle's own turning points far more cleanly than an un-normalized oscillator would in a low-volatility stretch.

## Pitfalls

Exactly `0` (not `NaN`) wherever the filtered signal has been flat for three bars running — a degenerate but legal `0/0` case, not a division error.

## Reference

Formula source: [https://www.tradingview.com/script/thzgGKyQ-Ehlers-Even-Better-Sinewave-EBSW/](https://www.tradingview.com/script/thzgGKyQ-Ehlers-Even-Better-Sinewave-EBSW/)
