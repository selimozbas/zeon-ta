# Trend Basics and Trend Channels

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/trend_channel.md)

`zeonta.trend_channel()` — Linear-regression trend line with standard-deviation channel bands.

## What it measures

"Is this an uptrend?" is usually answered by eye. A least-squares fit answers it with a number: the slope. The channel bands around that fit show how tightly price has been hugging the trend.

## Formula

```text
Linear regression over length n bars (x = 0..n-1, y = close): slope b = (nSxy - SxSy) / (nSx^2 - (Sx)^2); intercept a = (Sy - bSx) / n; regression line = a + b*x. Channel bands = regression line +/- (multiplier x standard deviation of closes from the regression line).
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `100` |
| `multiplier` | `2.0` |

## Returns

| Column |
| --- |
| `LRCM_100` |
| `LRCU_100` |
| `LRCL_100` |
| `LRCSLOPE_100` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.trend_channel(df['close'], length=50).tail(3)
```

```text
              LRCM_50    LRCU_50    LRCL_50  LRCSLOPE_50
date                                                    
2024-10-25  90.207156  92.134307  88.280006    -0.054643
2024-10-26  90.072080  92.077091  88.067070    -0.057086
2024-10-27  89.891669  92.029878  87.753459    -0.060957
```

**Accessor form:** `df.zta.trend_channel(...)`

## How to read it

`LRCSLOPE` is the per-bar drift: positive is an uptrend, negative a downtrend, and its magnitude is the trend's steepness. Price near `LRCU` is extended relative to the trend; near `LRCL` it is lagging behind it.

## Pitfalls

The fit is recomputed every bar, so the channel repaints as new data arrives — the line you see today over past bars is not the line that existed back then. Also, a regression will happily fit a straight line through pure noise; check the slope against something like ADX before trusting it.

## Reference

Formula source: [https://ta.cognicode.org/learn/trend-basics](https://ta.cognicode.org/learn/trend-basics)
