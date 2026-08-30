---
title: Voss Predictive Filter
---

[← All indicators](../index.md)

`zeonta.voss_predictive_filter()` — A band-limiting filter feeding Voss' negative-group-delay predictor.

## What it measures

Band-limits price with a 2-pole bandpass filter, then runs it through a filter with *negative group delay* (Henning Voss' "Universal Negative Group Delay Filter for the Prediction of Band-Limited Signals", adapted by Ehlers) to produce a second line that leads the bandpass output rather than lagging it.

## Formula

```text
Filt = BandPass(Close, period, bandwidth); Voss = ((3+order)/2)*Filt - sum((k+1)/order * Voss[-(order-k)], k=0..order-1)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `period` | `20` |
| `predict` | `3` |
| `bandwidth` | `0.25` |

## Returns

| Column |
| --- |
| `VOSSFILT` |
| `VOSS` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.voss_predictive_filter(df['close']).tail(3)
```

```text
            VOSSFILT      VOSS
date                          
2024-10-25 -0.411779 -0.115044
2024-10-26 -0.405698 -0.274864
2024-10-27 -0.422881 -0.489957
```

**Accessor form:** `df.zta.voss_predictive_filter(...)`

## How to read it

Plot `VOSS` against `VOSSFILT` — `VOSS` measurably precedes `VOSSFILT`'s own turns, so a crossover between the two at a peak or valley is Ehlers' own suggested signal.

## Pitfalls

This cannot see the future — the input must already be band-limited (which the bandpass stage guarantees only within its own passband), and a market that isn't currently cycling near `period` gives a `VOSS` line with nothing meaningful to lead.

## Reference

Formula source: [https://www.mesasoftware.com/papers/A%20PEEK%20INTO%20THE%20FUTURE.pdf](https://www.mesasoftware.com/papers/A%20PEEK%20INTO%20THE%20FUTURE.pdf)
