---
title: Relative Volatility Index (RVI)
---

[← All indicators](../index.md)

`zeonta.relative_volatility_index()` — RSI's up/down split applied to standard deviation instead of price change.

## What it measures

Donald Dorsey's [rsi](rsi.md)-shaped take on volatility: the same up/down-split-then-smooth structure Wilder used for price change, applied to a rolling standard deviation instead — a volatility measure with *direction*, unlike [atr](atr.md).

## Formula

```text
SD = STDDEV(Close, stdev_length); U/D = SD split by up/down close; RVI = 100 * EMA(U) / (EMA(U) + EMA(D))
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `stdev_length` | `10` |
| `smooth_length` | `14` |

## Returns

| Column |
| --- |
| `RVI_10_14` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.relative_volatility_index(df['close']).tail(3)
```

```text
date
2024-10-25    37.835098
2024-10-26    32.714115
2024-10-27    27.861198
Name: RVI_10_14, dtype: float64
```

**Accessor form:** `df.zta.relative_volatility_index(...)`

## How to read it

Above 50 means recent volatility has shown up more on up bars than down bars; below 50 is the reverse. Often paired with a trend indicator: rising RVI alongside a confirmed uptrend supports the move, while rising RVI against the trend warns of a possible reversal.

## Pitfalls

Two stacked periods (`stdev_length`, `smooth_length`) rather than the single period `rsi` needs — both change the result meaningfully.

## Reference

Formula source: [https://user42.tuxfamily.org/chart/manual/Relative-Volatility-Index.html](https://user42.tuxfamily.org/chart/manual/Relative-Volatility-Index.html)
