---
title: Multiscale Entropy
---

[← All indicators](../index.md)

`zeonta.multiscale_entropy()` — Sample Entropy recomputed at several coarse-graining scales (Costa et al., 2002).

## What it measures

sample_entropy measures unpredictability at one, single time scale. Costa, Goldberger & Peng (2002) repeat that same measurement after coarse-graining the window at several scale factors — replacing every non-overlapping run of tau consecutive log returns with their own mean — and reuse sample_entropy's own template-matching machinery directly on each coarse-grained series rather than reimplementing it. Scale 1 (no coarse-graining) is exactly sample_entropy on the same window.

## Formula

```text
y_j^(tau) = mean of log returns [(j-1)*tau+1 .. j*tau], j = 1..floor(window/tau); MSE(tau) = sample_entropy's own SampEn computed on y^(tau), for tau = 1..scales
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `window` | `100` |
| `scales` | `5` |
| `m` | `2` |
| `r` | `0.2` |

## Returns

| Column |
| --- |
| `MSE_100_2_0.2_1` |
| `MSE_100_2_0.2_2` |
| `MSE_100_2_0.2_3` |
| `MSE_100_2_0.2_4` |
| `MSE_100_2_0.2_5` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.multiscale_entropy(df['close'], scales=3).tail(3)
```

```text
            MSE_100_2_0.2_1  MSE_100_2_0.2_2  MSE_100_2_0.2_3
date                                                         
2024-10-25         2.433613         2.484907         1.145132
2024-10-26         2.451005         2.014903         1.609438
2024-10-27         2.433613         2.484907         1.060872
```

**Accessor form:** `df.zta.multiscale_entropy(...)`

## How to read it

A series with structure spread across multiple timescales keeps a roughly flat or rising entropy profile across scales; a series that is only complex at the finest scale (e.g. close to pure noise) has its entropy collapse quickly as tau grows, since averaging noise into blocks removes most of what made it unpredictable bar to bar. Comparing the whole profile, not just one scale, is the point of the method.

## Pitfalls

The tolerance r*std is fixed at scale 1's own standard deviation and reused, unchanged, at every coarser scale — the convention Costa et al.'s own papers and the PhysioNet MSE toolkit use, not a per-scale recomputation some later papers use instead. Same O(window^2) per-bar, per-scale cost as sample_entropy, now repeated once per scale.

## Reference

Formula source: [https://doi.org/10.1103/PhysRevLett.89.068102](https://doi.org/10.1103/PhysRevLett.89.068102)
