# Choppiness Index (CHOP)

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/choppiness_index.md)

`zeonta.choppiness_index()` — How much a window's price range came from many small moves versus one big one.

## What it measures

E.W. Dreiss compares two ways of measuring the same window's movement: sum up every single bar's own range (a lot, if price zigzags back and forth all window long), versus the range of the window measured start to end (small, if all that zigzagging cancelled itself out). A high ratio between the two means most of the motion was wasted; a ratio close to 1 means the window's bars each contributed net progress in the same direction.

## Formula

```text
CHOP = 100 * log10(Sum(TrueRange, n) / (HighestHigh(n) - LowestLow(n))) / log10(n)
```

## Parameters

**Required inputs:** `high`, `low`, `close`

| Parameter | Default |
| --- | --- |
| `length` | `14` |

## Returns

| Column |
| --- |
| `CHOP_14` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.choppiness_index(df['high'], df['low'], df['close']).tail(3)
```

```text
date
2024-10-25    59.636167
2024-10-26    60.407122
2024-10-27    54.470928
Name: CHOP_14, dtype: float64
```

**Accessor form:** `df.zta.choppiness_index(...)`

## How to read it

Dreiss' own commonly cited reading: above `61.8` suggests consolidation, below `38.2` suggests a clean trend (Fibonacci numbers chosen for familiarity, not derived from the formula). Bounded to `[0, 100]` by construction, but says nothing about *which* direction a trend runs, the same caveat `atr` carries.

## Pitfalls

`NaN` on a perfectly flat window (both the numerator and denominator collapse to `0`) rather than an undefined division or a misleading number.

## Reference

Formula source: [https://www.tradingview.com/support/solutions/43000501980-choppiness-index-chop/](https://www.tradingview.com/support/solutions/43000501980-choppiness-index-chop/)
