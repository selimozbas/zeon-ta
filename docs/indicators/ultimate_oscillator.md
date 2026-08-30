---
title: Ultimate Oscillator
---

[← All indicators](../index.md)

`zeonta.ultimate_oscillator()` — Larry Williams' three-timeframe blend of buying pressure over true range.

## What it measures

Developed by Larry Williams specifically to fix single-period oscillators' tendency to give false divergence signals: by blending three different look-backs (weighted 4:2:1 toward the fastest) into one line, a bearish-looking divergence on the short window alone gets outvoted when the two longer windows disagree. Buying Pressure (BP) and True Range (TR) are both measured against the *prior* close rather than the current bar's own open, so a gap is counted as part of that bar's range instead of being invisible to it.

## Formula

```text
BP = Close - Min(Low, PriorClose); TR = Max(High, PriorClose) - Min(Low, PriorClose); Average_n = Sum(BP, n) / Sum(TR, n); UO = 100 x (4xAverage_fast + 2xAverage_medium + Average_slow) / 7
```

## Parameters

**Required inputs:** `high`, `low`, `close`

| Parameter | Default |
| --- | --- |
| `fast` | `7` |
| `medium` | `14` |
| `slow` | `28` |

## Returns

| Column |
| --- |
| `UO_7_14_28` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.ultimate_oscillator(df['high'], df['low'], df['close']).tail(3)
```

```text
date
2024-10-25    43.163796
2024-10-26    42.451754
2024-10-27    41.226164
Name: UO_7_14_28, dtype: float64
```

**Accessor form:** `df.zta.ultimate_oscillator(...)`

## How to read it

Readings above 70 are considered overbought, below 30 oversold — the classic buy signal Williams himself described is a bullish divergence (price makes a lower low, UO does not) that then breaks back above 50, all three conditions together rather than any one alone.

## Pitfalls

The three windows must satisfy `fast < medium < slow`; passing them out of order raises `ValueError` rather than silently computing something meaningless. Like RSI and Stochastic, being at an overbought or oversold reading is not by itself a signal to act — Williams' own rule requires the divergence-plus-50-break combination, not the raw level alone.

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ultimate-oscillator](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ultimate-oscillator)
