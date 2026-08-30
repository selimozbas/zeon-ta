---
title: Bollinger Bands
---

[← All indicators](../index.md)

`zeonta.bbands()` — SMA envelope scaled by standard deviation; width tracks volatility.

## What it measures

A moving average with an envelope whose width is set by recent volatility. When the market gets quiet the bands squeeze in; when it gets violent they flare out. That self-adjusting width is the whole point.

## Formula

```text
Middle Band = SMA(Close, 20); Upper Band = Middle + 2 x StdDev(Close, 20); Lower Band = Middle - 2 x StdDev(Close, 20)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `20` |
| `std` | `2.0` |
| `ddof` | `0` |

## Returns

| Column |
| --- |
| `BBL_20_2.0` |
| `BBM_20_2.0` |
| `BBU_20_2.0` |
| `BBB_20_2.0` |
| `BBP_20_2.0` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.bbands(df['close'], length=20, std=2).tail(3)
```

```text
            BBL_20_2.0  BBM_20_2.0  BBU_20_2.0  BBB_20_2.0  BBP_20_2.0
date                                                                  
2024-10-25   89.262603   90.703090   92.143577    0.031763    0.289346
2024-10-26   89.027293   90.624895   92.222497    0.035257    0.028701
2024-10-27   88.661008   90.504580   92.348152    0.040740   -0.048495
```

**Accessor form:** `df.zta.bbands(...)`

## How to read it

`BBB` (bandwidth) is the number to watch for compression — a multi-month low in bandwidth precedes most large moves. `BBP` (percent-B) locates price inside the bands: `0` sits on the lower band, `1` on the upper, and values outside `0..1` mean price has closed beyond them.

## Pitfalls

Touching the upper band is not a sell signal. In a strong trend price "walks the band", riding it for dozens of bars — Bollinger himself said the bands are a relative measure of high and low, not a trading system. Note also that the standard deviation here is the population one (`ddof=0`), matching charting platforms.
