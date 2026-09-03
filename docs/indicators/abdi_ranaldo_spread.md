---
title: Abdi-Ranaldo Spread Estimator
---

[← All indicators](../index.md)

`zeonta.abdi_ranaldo_spread()` — Bid-ask spread from close vs. the high-low midrange (Abdi & Ranaldo, 2017).

## What it measures

Abdi & Ranaldo (2017) combine corwin_schultz_spread's insight (a bar's high-low midrange is a better estimate of the efficient price than its close, because the bid-ask half-spreads on either side of the range cancel) with roll_spread's autocovariance construction, but applied to midrange-to-close-to-midrange instead of close-to-close. The result is a two-day, close/high/low-only spread estimator that behaves better than either building block alone on daily data.

## Formula

```text
eta[t] = (ln(High[t]) + ln(Low[t])) / 2; S[t] = sqrt(max((ln(Close[t-1]) - eta[t-1]) x (ln(Close[t-1]) - eta[t]), 0))
```

## Parameters

**Required inputs:** `high`, `low`, `close`

_None._

## Returns

| Column |
| --- |
| `AR` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.abdi_ranaldo_spread(df['high'], df['low'], df['close']).tail(3)
```

```text
date
2024-10-25    0.0
2024-10-26    0.0
2024-10-27    0.0
Name: AR, dtype: float64
```

**Accessor form:** `df.zta.abdi_ranaldo_spread(...)`

## How to read it

Read AR as a fraction of price — 0.01 is a 1% quoted spread, the same convention as corwin_schultz_spread. It is a liquidity-cost estimate, not a volatility measure: a wider AR means more of the price is spent just crossing the spread on a round trip.

## Pitfalls

The raw product inside the square root can come out negative, the same known limitation corwin_schultz_spread and roll_spread both have; the paper's own remedy, applied here, is to floor each single two-day estimate at zero rather than leave it negative or turn the whole bar into NaN. Only the first bar (no earlier bar to pair against) is genuinely undefined, and is NaN.

## Reference

Formula source: [https://doi.org/10.1093/rfs/hhx084](https://doi.org/10.1093/rfs/hhx084)
