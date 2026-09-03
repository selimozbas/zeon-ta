---
title: Roll Spread Estimator
---

[← All indicators](../index.md)

`zeonta.roll_spread()` — Roll's (1984) implicit bid-ask spread from the serial covariance of returns.

## What it measures

Roll (1984) shows that in an efficient market, the bid-ask bounce alone — trades alternating between the bid and the ask with no new information moving the 'true' price at all — induces negative first-order serial covariance in successive returns. The size of that induced negative covariance identifies the spread directly, with no trade-direction data needed at all, only a return series.

## Formula

```text
Scov[t] = Cov(r, r_lag1) over the trailing window; Spread[t] = 2 x sqrt(-Scov[t]) if Scov[t] < 0, else undefined
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `21` |

## Returns

| Column |
| --- |
| `ROLL_21` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.roll_spread(df['close']).tail(3)
```

```text
date
2024-10-25   NaN
2024-10-26   NaN
2024-10-27   NaN
Name: ROLL_21, dtype: float64
```

**Accessor form:** `df.zta.roll_spread(...)`

## How to read it

Read ROLL as a fraction of price. Unlike corwin_schultz_spread and abdi_ranaldo_spread, which use the high-low range and stay defined on almost every bar, Roll's estimator needs the return series' own serial covariance to be negative — something that is common at tick/trade frequency but frequently fails at daily frequency, especially for heavily traded instruments.

## Pitfalls

Whenever a window's serial covariance is non-negative, the estimator is genuinely undefined (NaN here) — not zero, and not a valid spread computed from a negative number under the square root. This is a well-documented limitation of the estimator itself (see Harris, 1990), not a bug: expect long stretches of NaN on daily bars for liquid instruments, where corwin_schultz_spread/abdi_ranaldo_spread stay defined far more often.

## Reference

Formula source: [https://doi.org/10.1111/j.1540-6261.1984.tb03897.x](https://doi.org/10.1111/j.1540-6261.1984.tb03897.x)
