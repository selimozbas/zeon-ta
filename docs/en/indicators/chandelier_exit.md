# Chandelier Exit

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/chandelier_exit.md)

`zeonta.chandelier_exit()` — ATR-based trailing stop set from the recent n-bar high/low.

## What it measures

A volatility-anchored trailing stop, the same core idea `supertrend` and `parabolic_sar` use, but built differently: instead of ratcheting forward bar by bar, it is recomputed fresh from the last `n` bars' extreme and ATR every single time. That makes it simpler to reason about — no internal state to track — but it also means, unlike those two, the line itself can move against an open position from one bar to the next.

## Formula

```text
Long = HighestHigh(n) - ATR(n) x multiplier; Short = LowestLow(n) + ATR(n) x multiplier
```

## Parameters

**Required inputs:** `high`, `low`, `close`

| Parameter | Default |
| --- | --- |
| `length` | `22` |
| `multiplier` | `3.0` |

## Returns

| Column |
| --- |
| `CELONG_22_3.0` |
| `CESHORT_22_3.0` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.chandelier_exit(df['high'], df['low'], df['close']).tail(3)
```

```text
            CELONG_22_3.0  CESHORT_22_3.0
date                                     
2024-10-25      89.639229       92.259671
2024-10-26      89.634478       92.264422
2024-10-27      89.572493       91.472007
```

**Accessor form:** `df.zta.chandelier_exit(...)`

## How to read it

Hold a long position above `CELONG`; a close below it is the exit signal. Hold a short position below `CESHORT`; a close above it is the exit signal. Which line is relevant depends entirely on the position actually held — the indicator itself has no opinion about which side you are on.

## Pitfalls

Because each bar recomputes the stop from scratch rather than ratcheting it, a fresh (lower) high combined with a wider ATR reading can pull the long stop *down* even while the trend is fully intact — a real retreat, not a bug. Some charting platforms add an optional one-way ratchet on top of the plain formula; this implementation follows the published formula exactly, with no ratchet.

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/chandelier-exit](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/chandelier-exit)
