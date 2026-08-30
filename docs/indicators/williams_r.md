---
title: Williams %R
---

[← All indicators](../index.md)

`zeonta.williams_r()` — Where the close sits inside the recent high-low range, on a 0 to -100 scale.

## What it measures

The same range-position idea as `stoch`, developed independently by Larry Williams and published first: where the close sits inside the recent high-low range. Williams just inverted and shifted the scale — literally `%R = %K - 100` for the unsmoothed `%K` — so it reads 0 to -100 instead of 0 to 100.

## Formula

```text
%R = (HighestHigh(n) - Close) / (HighestHigh(n) - LowestLow(n)) x -100
```

## Parameters

**Required inputs:** `high`, `low`, `close`

| Parameter | Default |
| --- | --- |
| `length` | `14` |

## Returns

| Column |
| --- |
| `WILLR_14` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.williams_r(df['high'], df['low'], df['close'], length=14).tail(3)
```

```text
date
2024-10-25   -71.092379
2024-10-26   -95.248807
2024-10-27   -91.636223
Name: WILLR_14, dtype: float64
```

**Accessor form:** `df.zta.williams_r(...)`

## How to read it

Readings from -20 to 0 are conventionally "overbought", -80 to -100 "oversold" — the exact mirror of `stoch`'s 80/20. A cross above -50 signals price trading in the upper half of its recent range, below -50 the lower half.

## Pitfalls

Being mathematically identical to unsmoothed `stoch` minus 100, it inherits exactly the same weakness: it saturates in a trend, pinning near 0 or -100 for as long as the trend runs, generating premature reversal signals the whole way. Pair it with a trend filter before acting on the extremes.

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/williams-r](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/williams-r)
