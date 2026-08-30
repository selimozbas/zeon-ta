# Standard Deviation

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/stddev.md)

`zeonta.stddev()` — Rolling standard deviation of price.

## What it measures

The building block [bbands](bbands.md) plots as a band around price, exposed here on its own. Population standard deviation (`ddof=0`, matching charting-platform convention) unless you pass `ddof=1` for the sample estimate.

## Formula

```text
STDDEV = std(Close, n)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `20` |
| `ddof` | `0` |

## Returns

| Column |
| --- |
| `STDDEV_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.stddev(df['close']).tail(3)
```

```text
date
2024-10-25    0.720243
2024-10-26    0.798801
2024-10-27    0.921786
Name: STDDEV_20, dtype: float64
```

**Accessor form:** `df.zta.stddev(...)`

## How to read it

A rising STDDEV means price has gotten choppier over the window; a falling one means it has calmed down — the same read [squeeze](squeeze.md) automates for a specific band-width comparison.

## Pitfalls

A raw price measure, not a percentage — a $5 standard deviation means something completely different for a $20 stock than for a $2,000 one. Compare across symbols using a percentage-based measure instead, or normalise it yourself.

## Reference

Formula source: [https://en.wikipedia.org/wiki/Standard_deviation](https://en.wikipedia.org/wiki/Standard_deviation)
