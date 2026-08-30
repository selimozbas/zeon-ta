---
title: Awesome Oscillator (AO)
---

[← All indicators](../index.md)

`zeonta.awesome_oscillator()` — Momentum from the gap between a fast and slow SMA of the bar's own midpoint.

## What it measures

Bill Williams' momentum reading, built from the same "fast SMA minus slow SMA" shape as `macd`, but with two differences: it uses the bar's own midpoint rather than the close, and contrasts two plain SMAs instead of two EMAs, so it carries no memory beyond each window's own edge.

## Formula

```text
MedianPrice = (High + Low) / 2; AO = SMA(MedianPrice, 5) - SMA(MedianPrice, 34)
```

## Parameters

**Required inputs:** `high`, `low`

| Parameter | Default |
| --- | --- |
| `fast` | `5` |
| `slow` | `34` |

## Returns

| Column |
| --- |
| `AO_5_34` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.awesome_oscillator(df['high'], df['low']).tail(3)
```

```text
date
2024-10-25   -1.058354
2024-10-26   -0.963254
2024-10-27   -0.985917
Name: AO_5_34, dtype: float64
```

**Accessor form:** `df.zta.awesome_oscillator(...)`

## How to read it

Read the histogram like `macd`'s: positive and rising is strengthening upward momentum, a colour/sign change at the zero line marks a shift in which side (5-bar or 34-bar) is currently dominant. A widely cited pattern ("saucer") looks for two or three consecutive bars getting shorter then one getting taller, all on the same side of zero.

## Pitfalls

Using the bar's midpoint instead of the close means AO can shift even on a bar that closed flat, purely from an intrabar wick — it is reading range, not just direction. Being unbounded and denominated in price units, it also can't be compared across symbols or price levels the way a 0-100 oscillator can.

## Reference

Formula source: [https://www.metatrader5.com/en/terminal/help/indicators/bw_indicators/awesome](https://www.metatrader5.com/en/terminal/help/indicators/bw_indicators/awesome)
