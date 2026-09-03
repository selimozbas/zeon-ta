---
title: Kalman Filter
---

[← All indicators](../index.md)

`zeonta.kalman_filter()` — Recursive minimum-variance price estimate that updates its own confidence bar by bar.

## What it measures

The Kalman filter (Kalman, 1960) is the textbook recursive estimator for a hidden quantity observed through noise — used everywhere from spacecraft guidance to GPS. Applied to log(Close), it treats the 'true' price level as a random walk observed noisily bar by bar, and updates a minimum-mean-square-error estimate of it one bar at a time. There's no fixed window and no hand-picked smoothing constant like an EMA's `length` — the filter's own running confidence in its estimate (`P`) decides how much weight each new bar gets.

## Formula

```text
On log(Close): predict P = P_prev + process_variance; correct K = P / (P + measurement_variance), x = x_prev + K x (log(Close) - x_prev), P = (1 - K) x P; seeded x = log(Close[0]), P = 1.0; output = exp(x)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `process_variance` | `1e-06` |
| `measurement_variance` | `0.0001` |

## Returns

| Column |
| --- |
| `KALMAN_1e-06_0.0001` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.kalman_filter(df['close']).tail(3)
```

```text
date
2024-10-25    90.717933
2024-10-26    90.564608
2024-10-27    90.364428
Name: KALMAN_1e-06_0.0001, dtype: float64
```

**Accessor form:** `df.zta.kalman_filter(...)`

## How to read it

Read it like any other adaptive moving average — trend direction, dynamic support/resistance. `process_variance`/`measurement_variance` set the smoothness/responsiveness trade-off the way `length` does for an EMA: smaller `process_variance` relative to `measurement_variance` trusts the running estimate more and produces a smoother, slower line.

## Pitfalls

There is no single 'correct' process_variance/measurement_variance pairing — unlike the filter's own update equations (a single, universally cited formulation), the noise variances are a tuning choice specific to the instrument and timeframe, the same way an EMA's `length` is. Filtering happens in log-price space specifically so the defaults stay roughly scale-free across instruments at very different price levels; passing raw non-log values elsewhere and comparing variances across two differently-scaled instruments directly would be a mismatch.

## Reference

Formula source: [https://www.cs.unc.edu/~welch/media/pdf/kalman_intro.pdf](https://www.cs.unc.edu/~welch/media/pdf/kalman_intro.pdf)
