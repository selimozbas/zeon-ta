# Price Volume Trend (PVT)

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/pvt.md)

`zeonta.pvt()` — Running total of volume-scaled percentage price change.

## What it measures

[obv](obv.md)'s more graded cousin: OBV adds a bar's *entire* volume based only on which direction the close moved; PVT scales the volume it adds by *how much* the close moved as a percentage, so a 3% up day contributes three times as much as a 1% up day rather than the same full volume either way.

## Formula

```text
PVT[0] = 0; PVT[i] = PVT[i-1] + Volume[i] * (Close[i] - Close[i-1]) / Close[i-1]
```

## Parameters

**Required inputs:** `close`, `volume`

_None._

## Returns

| Column |
| --- |
| `PVT` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.pvt(df['close'], df['volume']).tail(3)
```

```text
date
2024-10-25   -59713.678888
2024-10-26   -63728.003586
2024-10-27   -65606.949086
Name: PVT, dtype: float64
```

**Accessor form:** `df.zta.pvt(...)`

## How to read it

Read the same way as OBV — a rising line alongside rising price confirms the trend with real participation behind it; a PVT that fails to make a new high alongside price is a classic bearish divergence warning.

## Pitfalls

A running total with an arbitrary starting level, like `obv`/`adl` — only its slope and its divergence from price carry meaning, never its absolute value.

## Reference

Formula source: [https://www.tradingview.com/support/solutions/43000502345-price-volume-trend-pvt/](https://www.tradingview.com/support/solutions/43000502345-price-volume-trend-pvt/)
