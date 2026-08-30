---
title: Aroon and the Aroon Oscillator
---

[← All indicators](../index.md)

`zeonta.aroon()` — How recently price made a new high vs. a new low, as a 0-100 pair.

## What it measures

Where `donchian` marks *where* the n-bar high and low currently sit in price terms, Aroon marks *how long ago* they happened. A fresh high scores Aroon-Up at 100 no matter how far away it is in price; a high from `n` bars back scores 0 even if price is still sitting right next to it — the whole indicator is about recency, not level.

## Formula

```text
Aroon-Up = ((n - DaysSinceHighestHigh) / n) x 100; Aroon-Down = ((n - DaysSinceLowestLow) / n) x 100; Aroon Oscillator = Aroon-Up - Aroon-Down
```

## Parameters

**Required inputs:** `high`, `low`

| Parameter | Default |
| --- | --- |
| `length` | `25` |

## Returns

| Column |
| --- |
| `AROONU_25` |
| `AROOND_25` |
| `AROONOSC_25` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.aroon(df['high'], df['low']).tail(3)
```

```text
            AROONU_25  AROOND_25  AROONOSC_25
date                                         
2024-10-25       64.0       92.0        -28.0
2024-10-26       60.0       88.0        -28.0
2024-10-27       56.0      100.0        -44.0
```

**Accessor form:** `df.zta.aroon(...)`

## How to read it

Aroon-Up above 70 with Aroon-Down below 30 signals a strong uptrend (highs keep getting made, lows are stale); the mirror image signals a downtrend. The Aroon Oscillator condenses both into one line around zero: sustained positive readings mark an uptrend bias, sustained negative ones a downtrend bias.

## Pitfalls

Aroon-Up and Aroon-Down can both be high or both be low at once (a choppy market can make fresh highs and fresh lows in the same window), which the oscillator alone hides by netting them against each other — check the two raw lines, not just the oscillator, before concluding there is no trend. Ties for the extreme value within the window are broken toward the most recent occurrence, per the source's own convention.

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/aroon](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/aroon)
