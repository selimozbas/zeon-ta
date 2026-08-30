---
title: Instantaneous Trendline (Ehlers)
---

[← All indicators](../index.md)

`zeonta.instantaneous_trendline()` — Ehlers' Instantaneous Trendline: a filter tuned to track the trend, not the cycle.

## What it measures

Ehlers designed this second-order filter specifically to track the *trend* component of price while rejecting the *cyclic* component — an ordinary moving average passes both through together, which is why it lags: part of that lag is spent smoothing out a cycle that was never trend in the first place. `super_smoother` is a general-purpose low-pass filter; this one is purpose-built to isolate trend specifically.

## Formula

```text
IT = (a - a^2/4) x Close + 0.5 x a^2 x Close[t-1] - (a - 0.75 x a^2) x Close[t-2] + 2 x (1-a) x IT[t-1] - (1-a)^2 x IT[t-2]
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `alpha` | `0.07` |

## Returns

| Column |
| --- |
| `ITREND_0.07` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.instantaneous_trendline(df['close']).tail(3)
```

```text
date
2024-10-25    90.275484
2024-10-26    90.138468
2024-10-27    89.906359
Name: ITREND_0.07, dtype: float64
```

**Accessor form:** `df.zta.instantaneous_trendline(...)`

## How to read it

Read it as a smoothed trend line, similar in spirit to `super_smoother` or an EMA, but expect the reading to be genuinely flatter through a cyclical, range-bound stretch since that is precisely the component this filter is designed to reject.

## Pitfalls

Parameterised by ``alpha`` directly (Ehlers' own default is ``0.07``) rather than by a bar-count length the way most of this library's other filters are — a length-based wrapper is a natural extension some platforms add, but the primary source itself uses ``alpha``, so that is what this implementation exposes.

## Reference

Formula source: [https://www.tradingview.com/support/solutions/43000589152-instantaneous-trendline/](https://www.tradingview.com/support/solutions/43000589152-instantaneous-trendline/)
