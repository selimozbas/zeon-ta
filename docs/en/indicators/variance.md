# Variance

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/variance.md)

`zeonta.variance()` — Rolling variance of price.

## What it measures

[stddev](stddev.md) before the square root — computed directly here rather than by squaring it, but numerically the same relationship. Statistical work (variance is additive for independent series; standard deviation is not) reaches for this form; charting reaches for `stddev`, since it shares price's own units.

## Formula

```text
VAR = variance(Close, n) = STDDEV(Close, n) ^ 2
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
| `VAR_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.variance(df['close']).tail(3)
```

```text
date
2024-10-25    0.518750
2024-10-26    0.638083
2024-10-27    0.849690
Name: VAR_20, dtype: float64
```

**Accessor form:** `df.zta.variance(...)`

## How to read it

Same direction as `stddev`, just on a squared (and therefore larger) scale.

## Pitfalls

Squared units — a variance of 4 for a price series in dollars is technically 'dollars squared', not directly comparable to price itself the way `stddev` is.

## Reference

Formula source: [https://en.wikipedia.org/wiki/Variance](https://en.wikipedia.org/wiki/Variance)
