---
title: ADX / DMI
---

[← All indicators](../index.md)

`zeonta.adx()` — Wilder's directional movement system: trend strength (ADX) and direction (DI).

## What it measures

Wilder's answer to a question most indicators dodge: is there a trend here at all? ADX measures trend strength without caring about direction, while the +DI/-DI pair supplies the direction separately.

## Formula

```text
+DM = up-move if up-move > down-move and up-move > 0, else 0; -DM = down-move if down-move > up-move and down-move > 0, else 0; +DI = 100 x WilderSmooth(+DM, period) / ATR(period); -DI = 100 x WilderSmooth(-DM, period) / ATR(period); DX = 100 x |+DI - -DI| / (+DI + -DI); ADX = WilderSmooth(DX, period)
```

## Parameters

**Required inputs:** `high`, `low`, `close`

| Parameter | Default |
| --- | --- |
| `length` | `14` |

## Returns

| Column |
| --- |
| `ADX_14` |
| `DMP_14` |
| `DMN_14` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.adx(df['high'], df['low'], df['close'], length=14).tail(3)
```

```text
               ADX_14     DMP_14     DMN_14
date                                       
2024-10-25  15.703691  16.436469  22.152539
2024-10-26  16.249237  15.310359  24.633880
2024-10-27  17.531395  13.906973  28.363100
```

**Accessor form:** `df.zta.adx(...)`

## How to read it

Readings below 20 mean no usable trend, above 25 a trend worth following, and above 40 a strong one. Which DI line is on top tells you the direction: `DMP` above `DMN` is an uptrend. ADX is the classic filter for indicators that misbehave in ranges.

## Pitfalls

A rising ADX in a downtrend is still a rising ADX — it never says "bullish". Because it smooths an already-smoothed series it needs roughly `2 x length` bars before it produces anything, and it turns late by construction.
