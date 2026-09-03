---
title: Shannon Entropy
---

[← All indicators](../index.md)

`zeonta.shannon_entropy()` — How spread out a window's log returns are — noise vs. clustered structure.

## What it measures

Shannon's 1948 entropy measures how uniformly a distribution's probability mass is spread across its possible outcomes. Applied to a rolling window of log returns, 'outcomes' are equal-width return-size buckets: a window whose returns pile into one or two buckets (a quiet, directional stretch) has low entropy, one whose returns spread evenly across every bucket (no dominant move size) approaches the maximum, `log(bins)` — this indicator reports that ratio, so the result stays 0-1 regardless of `bins`. Unlike sample_entropy/approximate_entropy/permutation_entropy, it asks nothing about order or repetition — only how the move *sizes* are distributed.

## Formula

```text
Bin a window's log returns into `bins` equal-width buckets spanning that window's own min-to-max range; H = -sum(p_i x log(p_i)) over buckets with p_i > 0, p_i = count_i / window; normalized result = H / log(bins)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `window` | `50` |
| `bins` | `10` |

## Returns

| Column |
| --- |
| `SHENT_50_10` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.shannon_entropy(df['close']).tail(3)
```

```text
date
2024-10-25    0.873898
2024-10-26    0.881630
2024-10-27    0.884834
Name: SHENT_50_10, dtype: float64
```

**Accessor form:** `df.zta.shannon_entropy(...)`

## How to read it

Low values mean recent returns have clustered around one typical size — often a quiet, low-volatility or persistently one-directional stretch. High values (near 1) mean return sizes have been spread out with no dominant scale — often choppier or more heterogeneous conditions. A sudden entropy drop or spike is sometimes read as a precursor to a volatility regime change, though this indicator only measures the current window's own spread, not what comes next.

## Pitfalls

`bins` is a real, tunable choice — like sample_entropy's `m`/`r` — not a value with one provably correct setting: more buckets resolve finer structure but need more bars per bucket to estimate each `p_i` reliably, so a small `window` with a large `bins` count produces a noisy estimate. A window whose returns are all identical (zero range) is defined as exactly `0.0` rather than left undefined.

## Reference

Formula source: [https://ieeexplore.ieee.org/document/6773024](https://ieeexplore.ieee.org/document/6773024)
