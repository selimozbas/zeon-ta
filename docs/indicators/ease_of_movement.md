---
title: Ease of Movement (EMV)
---

[← All indicators](../index.md)

`zeonta.ease_of_movement()` — How much price moves per unit of volume — Arms' Ease of Movement.

## What it measures

Richard Arms' box-ratio idea directly compares a bar's price movement against how much volume that movement needed — the same underlying question `chaikin_oscillator` and `mfi` ask, from a different angle. A large price move on light volume scores much higher than the same move on heavy volume.

## Formula

```text
DistanceMoved = (High+Low)/2 - (PriorHigh+PriorLow)/2; BoxRatio = (Volume/100,000,000) / (High-Low); EMV(1) = DistanceMoved / BoxRatio; EOM = SMA(EMV(1), n)
```

## Parameters

**Required inputs:** `high`, `low`, `volume`

| Parameter | Default |
| --- | --- |
| `length` | `14` |

## Returns

| Column |
| --- |
| `EOM_14` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.ease_of_movement(df['high'], df['low'], df['volume']).tail(3)
```

```text
date
2024-10-25    24.475105
2024-10-26     6.079390
2024-10-27   -27.581227
Name: EOM_14, dtype: float64
```

**Accessor form:** `df.zta.ease_of_movement(...)`

## How to read it

Sustained positive readings mean price is advancing easily — little volume is needed per unit of price movement, a healthy uptrend. Readings near or below zero mean price is struggling against volume to move at all, whether flat or actively declining.

## Pitfalls

A zero-range bar or a zero-volume bar makes the box ratio degenerate (a zero or infinite denominator); this implementation treats either case as contributing ``0`` to the raw EMV rather than raising or producing ``inf``/``NaN``, the same convention `cmf`'s Money Flow Multiplier uses for its own zero-range case.

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ease-of-movement-emv](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ease-of-movement-emv)
