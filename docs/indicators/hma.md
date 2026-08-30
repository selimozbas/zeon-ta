---
title: Hull Moving Average (HMA)
---

[← All indicators](../index.md)

`zeonta.hma()` — Fast-turning WMA-of-WMAs designed to cut lag without adding noise.

## What it measures

`wma` alone reduces lag only modestly next to `sma`. Hull's insight: take a fast half-length WMA, double it, and subtract the full-length WMA — this extrapolates *ahead* of the fast WMA rather than just averaging alongside it. That extrapolation is jumpy on its own, so one more short WMA smooths it back into a genuinely quick yet still-smooth line.

## Formula

```text
Raw = (2 x WMA(Close, Integer(n/2))) - WMA(Close, n); HMA = WMA(Raw, Integer(sqrt(n))) — both intermediate lengths truncated toward zero, per Alan Hull's own formula, not rounded to the nearest whole number
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `20` |

## Returns

| Column |
| --- |
| `HMA_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.hma(df['close'], length=20).tail(3)
```

```text
date
2024-10-25    90.055085
2024-10-26    89.841562
2024-10-27    89.517649
Name: HMA_20, dtype: float64
```

**Accessor form:** `df.zta.hma(...)`

## How to read it

Read it like any other moving average, but expect it to hug price far more closely than `sma`, `ema` or plain `wma` at the same length — and to occasionally overshoot a sharp turn before settling, a direct consequence of the extrapolation step.

## Pitfalls

The same extrapolation that cuts lag also means HMA can overshoot past the actual turning point on a sharp reversal, briefly pointing the wrong way before correcting — unlike `sma`/`wma`, which merely lag, never overshoot. It is also the most compute-heavy moving average in this library (three WMA passes per bar). Some secondary write-ups describe the two intermediate lengths as rounded rather than truncated; this implementation follows Alan Hull's own formula (truncation), confirmed both against his own site and empirically against a live TradingView reading.

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/hull-moving-average-hma](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/hull-moving-average-hma)
