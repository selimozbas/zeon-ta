---
title: Weighted Moving Average (WMA)
---

[← All indicators](../index.md)

`zeonta.wma()` — Moving average giving linearly increasing weight to more recent closes.

## What it measures

Sits directly between `sma` and `ema` in how it treats the window: every bar still gets a fixed, predictable weight (unlike EMA's decay that technically never reaches zero), but that weight now favours recent bars in a straight line instead of treating the whole window equally like SMA does.

## Formula

```text
WMA = (P1 x n + P2 x (n-1) + ... + Pn x 1) / (n + (n-1) + ... + 1), where P1 is the most recent close and Pn is the oldest close in the window
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `20` |

## Returns

| Column |
| --- |
| `WMA_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.wma(df['close'], length=20).tail(3)
```

```text
date
2024-10-25    90.600817
2024-10-26    90.449951
2024-10-27    90.245885
Name: WMA_20, dtype: float64
```

**Accessor form:** `df.zta.wma(...)`

## How to read it

Read it exactly like `sma` — trend direction, support, crossovers — but expect it to turn sooner after a reversal since the most recent bars carry more weight. It is also the building block several other moving averages (like the Hull Moving Average) chain together to cut lag further.

## Pitfalls

The linear taper is a much gentler lag reduction than EMA's exponential one — at the same length, WMA sits closer to SMA than to EMA in how much it lags. It also inherits every fixed-length moving average's core limitation: no length is right for both a trending and a choppy market, unlike the adaptive :func:`~zeonta.kama`.

## Reference

Formula source: [https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/wma](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/wma)
