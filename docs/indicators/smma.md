---
title: Smoothed Moving Average (SMMA)
---

[← All indicators](../index.md)

`zeonta.smma()` — Wilder's exponential smoothing, exposed as its own moving average.

## What it measures

The exact recursion J. Welles Wilder used throughout *New Concepts in Technical Trading Systems* (1978) for `rsi`, `atr` and `adx`, exposed here as its own line instead of staying buried inside those three. Algebraically identical to `ema` with `alpha = 1/n` instead of `2/(n+1)` — the same shape of formula, just a gentler smoothing constant, which is why Wilder's tools all feel a step calmer than a plain EMA-based equivalent at the same length.

## Formula

```text
SMMA[t] = SMMA[t-1] + (Close[t] - SMMA[t-1]) / n, seeded by the plain SMA of the first n bars
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `9` |

## Returns

| Column |
| --- |
| `SMMA_9` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.smma(df['close'], length=9).tail(3)
```

```text
date
2024-10-25    90.639953
2024-10-26    90.470959
2024-10-27    90.249985
Name: SMMA_9, dtype: float64
```

**Accessor form:** `df.zta.smma(...)`

## How to read it

Read it like any other moving average — trend direction, dynamic support/resistance — but expect it to lag noticeably more than an EMA of the same stated length, since `alpha=1/n` is always smaller than EMA's `2/(n+1)` for any n > 1. It also never fully forgets old prices the way `wma`'s hard window edge does; every bar since warm-up still carries a shrinking sliver of weight.

## Pitfalls

Neither StockCharts nor Wikipedia document SMMA as its own named indicator — it appears only embedded inside RSI/ATR/ADX on those sites. The default length here (9) follows TradingView's own dedicated Smoothed Moving Average page rather than Wilder's own convention of 14 used for RSI/ATR/ADX, since no single source states a canonical default for SMMA as a standalone indicator; the recursion itself was independently confirmed against MetaTrader's MQL5 documentation.

## Reference

Formula source: [https://www.tradingview.com/support/solutions/43000591343-smoothed-moving-average/](https://www.tradingview.com/support/solutions/43000591343-smoothed-moving-average/)
