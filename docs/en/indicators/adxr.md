# ADX Rating (ADXR)

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/adxr.md)

`zeonta.adxr()` — ADX averaged with its own value from length-1 bars ago, smoothing its tops/bottoms.

## What it measures

A smoothed extension of [adx](adx.md): today's ADX averaged with its own value from ``length - 1`` bars ago. The same idea `trima`'s double-SMA pass applies to price, applied here to ADX instead — trading a bit more lag for fewer false tops and bottoms in the trend-strength reading.

## Formula

```text
ADXR = (ADX + ADX[length - 1 bars ago]) / 2
```

## Parameters

**Required inputs:** `high`, `low`, `close`

| Parameter | Default |
| --- | --- |
| `length` | `14` |

## Returns

| Column |
| --- |
| `ADXR_14` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.adxr(df['high'], df['low'], df['close']).tail(3)
```

```text
date
2024-10-25    16.628347
2024-10-26    16.505838
2024-10-27    17.121435
Name: ADXR_14, dtype: float64
```

**Accessor form:** `df.zta.adxr(...)`

## How to read it

Read exactly like `adx` — a rising ADXR means the trend (whichever direction) is strengthening. Smoother than `adx` itself, so a change in ADXR's own direction is a steadier signal that trend strength has peaked or bottomed.

## Pitfalls

Needs roughly ``3 * length`` bars before it produces a value — `adx`'s own ``2 * length``-bar warm-up, plus another ``length - 1`` bars for the lagged copy it averages against.

## Reference

Formula source: [https://www.fmlabs.com/reference/ADXR.htm](https://www.fmlabs.com/reference/ADXR.htm)
