# Force Index

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/force_index.md)

`zeonta.force_index()` — Volume-weighted price change: Elder's Force Index.

## What it measures

Alexander Elder's combination of price direction, price magnitude and volume into one line — a bar that moves further on more volume produces a proportionally larger reading than the same move on light volume, something a pure price indicator like `momentum` cannot see. It is the same author's indicator as `elder_ray`, viewing buying/selling pressure through volume instead of through price relative to an EMA.

## Formula

```text
FI(1) = (Close - PriorClose) x Volume; FI(n) = EMA(FI(1), n)
```

## Parameters

**Required inputs:** `close`, `volume`

| Parameter | Default |
| --- | --- |
| `length` | `13` |

## Returns

| Column |
| --- |
| `FI_13` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.force_index(df['close'], df['volume']).tail(3)
```

```text
date
2024-10-25    -79964.843100
2024-10-26   -120209.208486
2024-10-27   -126957.856416
Name: FI_13, dtype: float64
```

**Accessor form:** `df.zta.force_index(...)`

## How to read it

A rising Force Index confirms an uptrend (price advancing on strong volume); a falling one during an uptrend, or a bearish divergence against price, warns that the advance is losing conviction. Elder himself used both a short unsmoothed version (``length=1``, or 2) for entry timing and the smoothed 13-period version for the underlying trend.

## Pitfalls

Like `obv` and `adl`, only its sign and slope are meaningful — the absolute level scales directly with the security's own typical share volume, so it cannot be compared across different symbols.

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/force-index](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/force-index)
