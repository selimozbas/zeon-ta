# Heikin-Ashi Candles

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/heikin_ashi.md)

`zeonta.heikin_ashi()` — Recursively smoothed candles that filter noise from the price bars themselves.

## What it measures

'Average bar' — builds a second, smoothed OHLC series from the real one, where each bar's open folds in the *previous* bar's own smoothed open and close. The same kind of recursive, self-referencing smoothing [ema](ema.md) applies to a single price line, applied here to a whole candle.

## Formula

```text
HAclose=(O+H+L+C)/4; HAopen[0]=(O+C)/2 then (HAopen[-1]+HAclose[-1])/2; HAhigh=max(H,HAopen,HAclose); HAlow=min(L,HAopen,HAclose)
```

## Parameters

**Required inputs:** `open`, `high`, `low`, `close`

_None._

## Returns

| Column |
| --- |
| `HAopen` |
| `HAhigh` |
| `HAlow` |
| `HAclose` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.heikin_ashi(df['open'], df['high'], df['low'], df['close']).tail(3)
```

```text
               HAopen     HAhigh    HAlow   HAclose
date                                               
2024-10-25  90.360474  90.827100  89.7648  90.29595
2024-10-26  90.328212  90.328212  89.0960  89.66890
2024-10-27  89.998556  89.998556  88.0724  88.85595
```

**Accessor form:** `df.zta.heikin_ashi(...)`

## How to read it

A run of same-direction candles with little or no opposite-colored wick is the classic read for a trend that has not shown genuine reversal pressure yet — noise a plain candle chart would still show bar to bar is filtered out here.

## Pitfalls

The recursive open means a single missing bar changes every later Heikin-Ashi value from that point on — there is no fixed window for the effect to age out of, unlike most indicators in this library.

## Reference

Formula source: [https://www.babypips.com/learn/forex/how-to-calculate-heikin-ashi](https://www.babypips.com/learn/forex/how-to-calculate-heikin-ashi)
