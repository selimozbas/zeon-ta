---
title: CUSUM Filter
---

[← All indicators](../index.md)

`zeonta.cusum_filter()` — Symmetric CUSUM filter: flags bars where cumulative log-return drift crosses a level.

## What it measures

Lopez de Prado's Symmetric CUSUM Filter tracks two running sums of log returns, one for upward drift and one for downward, each reset to zero the moment it crosses a fixed threshold. In the book it is used to sample bars for a downstream ML pipeline — only the bars where an event fires are kept. This library's aligned-per-bar contract has no place for dropping bars, so this function reports the discrete event flag itself at every bar instead, the same flag-column shape divergence already uses for events that only fire on some bars.

## Formula

```text
S+[t] = max(0, S+[t-1] + r[t]); S-[t] = min(0, S-[t-1] + r[t]); event = -1 and S- reset to 0 if S-[t] < -threshold; event = +1 and S+ reset to 0 if S+[t] > threshold; else event = 0
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `threshold` | `0.05` |

## Returns

| Column |
| --- |
| `CUSUM_0.05` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.cusum_filter(df['close']).tail(3)
```

```text
date
2024-10-25    0.0
2024-10-26    0.0
2024-10-27   -1.0
Name: CUSUM_0.05, dtype: float64
```

**Accessor form:** `df.zta.cusum_filter(...)`

## How to read it

A +1 means enough cumulative upward drift has built up since the last reset to cross threshold; -1 the same for downward drift; 0 means neither running sum has crossed yet. Because the running sums only reset on a crossing, the series will not fire repeatedly while hovering near the threshold — it takes a fresh, full run of drift to trigger the next event.

## Pitfalls

This is a genuinely stateful, whole-series recursion, not a fixed rolling window — like drawdown's running peak, prepending more history changes every later flag, since the running sums start accumulating from a different point. threshold is a fixed level in log-return units, not a multiple of a rolling volatility estimate; picking one that suits the instrument's typical volatility is left to the caller.

## Reference

Formula source: [https://doi.org/10.1002/9781119482086](https://doi.org/10.1002/9781119482086)
