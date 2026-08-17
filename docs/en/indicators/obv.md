# On-Balance Volume (OBV)

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/obv.md)

`zeonta.obv()` — Cumulative volume, added on up closes and subtracted on down closes.

## What it measures

The oldest and simplest way to combine volume with direction: add the bar's volume when price closed up, subtract it when price closed down, and run a cumulative total. The idea behind it — volume leads price — is what [divergence](divergence.md) between OBV and price is built to catch.

## Formula

```text
If Close > Prior Close: OBV = Prior OBV + Volume; if Close < Prior Close: OBV = Prior OBV - Volume; if Close = Prior Close: OBV = Prior OBV (unchanged)
```

## Parameters

**Required inputs:** `close`, `volume`

_None._

## Returns

| Column |
| --- |
| `OBV` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.obv(df['close'], df['volume']).tail(3)
```

```text
date
2024-10-25    4756931.0
2024-10-26    4386817.0
2024-10-27    4123862.0
Name: OBV, dtype: float64
```

**Accessor form:** `df.zta.obv(...)`

## How to read it

The absolute level means nothing (it depends entirely on where the running total happened to start); what matters is its slope and whether that slope agrees with price's. OBV rising while price is flat or falling is read as accumulation building under the surface — the classic bullish divergence.

## Pitfalls

OBV treats every bar's entire volume as either fully bullish or fully bearish based on the close alone, ignoring how the bar actually traded intrabar — a bar that opened low, spiked high, and drifted back down to close marginally up still counts as 100% buying volume. [cmf](cmf.md) uses the bar's full range instead and is less crude on this point.

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/on-balance-volume-obv](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/on-balance-volume-obv)
