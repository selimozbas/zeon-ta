# Acceleration Bands

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/accbands.md)

`zeonta.accbands()` — SMA envelope of High/Low scaled by their own range, widening with volatility.

## What it measures

Price Headley's volatility envelope: unlike [bbands](bbands.md) (which scales a fixed multiplier by *rolling* standard deviation), the widening here comes from each individual bar's *own* high-low range — a single big bar pushes the bands apart immediately, with no lag from a deviation window.

## Formula

```text
Ratio = c*(High-Low)/(High+Low); Upper=SMA(High*(1+Ratio),n); Lower=SMA(Low*(1-Ratio),n); Middle=SMA(Close,n)
```

## Parameters

**Required inputs:** `high`, `low`, `close`

| Parameter | Default |
| --- | --- |
| `length` | `20` |
| `c` | `4.0` |

## Returns

| Column |
| --- |
| `ACCBL_20` |
| `ACCBM_20` |
| `ACCBU_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.accbands(df['high'], df['low'], df['close']).tail(3)
```

```text
             ACCBL_20   ACCBM_20   ACCBU_20
date                                       
2024-10-25  87.553747  90.703090  93.958972
2024-10-26  87.543579  90.624895  93.875104
2024-10-27  87.307017  90.504580  93.911617
```

**Accessor form:** `df.zta.accbands(...)`

## How to read it

Read like any envelope: a close outside the bands on a weekly or monthly chart is Headley's own preferred breakout signal; on shorter frames the bands double as dynamic support/resistance.

## Pitfalls

A zero-range-and-zero-price bar (High + Low == 0) leaves the ratio undefined; the bands fall back to `NaN` for that bar rather than dividing by zero.

## Reference

Formula source: [https://help.tc2000.com/m/69445/l/755840-acceleration-bands](https://help.tc2000.com/m/69445/l/755840-acceleration-bands)
