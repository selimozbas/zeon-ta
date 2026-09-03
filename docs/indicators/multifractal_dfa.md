---
title: Multifractal Detrended Fluctuation Analysis
---

[← All indicators](../index.md)

`zeonta.multifractal_dfa()` — Width of the generalized-Hurst spectrum across fluctuation sizes (multifractality).

## What it measures

dfa fits one scaling exponent to a return series, implicitly treating small and large fluctuations as scaling the same way. Kantelhardt et al. (2002) generalize DFA's fluctuation function with a q-th-power average over boxes instead of a plain RMS, reusing the exact same per-box detrended fluctuations dfa computes: negative q weights small fluctuations more heavily, positive q weights large ones. A monofractal series (small and large fluctuations scale identically, e.g. plain fractional Brownian motion) has h(q) essentially constant across q; a genuinely multifractal series has h(q) vary with q, and this function reports that variation as a single number, the width of the generalized-Hurst spectrum between two chosen q extremes.

## Formula

```text
F_q(n) = {mean over boxes of [F^2(n,box)]^(q/2)}^(1/q) for q != 0, or exp(mean(ln[F^2(n,box)])/2) for q = 0; h(q) = slope of log(F_q(n)) vs log(n); MFDFA = h(q_min) - h(q_max)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `window` | `100` |
| `q_min` | `-5.0` |
| `q_max` | `5.0` |

## Returns

| Column |
| --- |
| `MFDFA_100_-5.0_5.0` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.multifractal_dfa(df['close']).tail(3)
```

```text
date
2024-10-25    1.318860
2024-10-26    0.871528
2024-10-27    1.168866
Name: MFDFA_100_-5.0_5.0, dtype: float64
```

**Accessor form:** `df.zta.multifractal_dfa(...)`

## How to read it

Near 0 describes a monofractal series (dfa's own single exponent already tells the whole story); larger describes a more strongly multifractal one, where small and large price swings genuinely follow different scaling laws. h(2) — the special case at q=2 this function does not expose on its own — reduces exactly to dfa's own exponent, so dfa and this function are checking related but different things.

## Pitfalls

q_min and q_max default to -5 and 5, the range most commonly scanned in the tutorial literature that has followed the original 2002 paper (e.g. Ihlen, 2012) — not something the paper itself mandates as the one correct choice. Like dfa, this divides each window into non-overlapping boxes counted from the start only, not also from the end as some MF-DFA implementations do, kept consistent with dfa's own existing convention in this library.

## Reference

Formula source: [https://doi.org/10.1016/S0378-4371(02)01383-3](https://doi.org/10.1016/S0378-4371(02)01383-3)
