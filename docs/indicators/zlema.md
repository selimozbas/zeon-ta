---
title: Zero-Lag Exponential Moving Average (ZLEMA)
---

[← All indicators](../index.md)

`zeonta.zlema()` — An EMA fed de-lagged data, to track price with less delay than a plain EMA.

## What it measures

Ehlers & Way's answer to [ema](ema.md)'s built-in lag: rather than changing the smoothing formula itself, they modify what goes *into* it — feeding the EMA a de-lagged version of price (today's close plus how far it has moved from `lag` bars ago) rather than the raw close.

## Formula

```text
lag = floor((n-1)/2); data[t] = Close[t] + (Close[t] - Close[t-lag]); ZLEMA = EMA(data, n)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `20` |

## Returns

| Column |
| --- |
| `ZLEMA_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.zlema(df['close']).tail(3)
```

```text
date
2024-10-25    90.105026
2024-10-26    89.808691
2024-10-27    89.394787
Name: ZLEMA_20, dtype: float64
```

**Accessor form:** `df.zta.zlema(...)`

## How to read it

Read the same way as any EMA-family line — a faster-reacting alternative to `ema` of the same length, at the cost of overshooting more on a sharp reversal (removing lag makes the line more willing to move, in either direction).

## Pitfalls

The lag-cancellation is exact only on a straight line; real price is not one, so some lag remains and the 'zero' in the name is aspirational rather than literal.

## Reference

Formula source: [https://user42.tuxfamily.org/chart/manual/Zero_002dLag-Exponential-Moving-Average.html](https://user42.tuxfamily.org/chart/manual/Zero_002dLag-Exponential-Moving-Average.html)
