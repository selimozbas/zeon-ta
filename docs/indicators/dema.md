---
title: Double Exponential Moving Average (DEMA)
---

[← All indicators](../index.md)

`zeonta.dema()` — EMA with roughly half the lag, by offsetting a single EMA with its own EMA.

## What it measures

A single EMA always lags, because it is, by construction, still catching up to price. DEMA estimates that lag by smoothing the EMA a second time — the gap between EMA1 and EMA2 tells you roughly how far behind EMA1 has fallen — then adds that gap back once to cancel most of it out.

## Formula

```text
DEMA = (2 x EMA1) - EMA2, where EMA1 = EMA(Close, n) and EMA2 = EMA(EMA1, n)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `20` |

## Returns

| Column |
| --- |
| `DEMA_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.dema(df['close'], length=20).tail(3)
```

```text
date
2024-10-25    90.218397
2024-10-26    89.975636
2024-10-27    89.653624
Name: DEMA_20, dtype: float64
```

**Accessor form:** `df.zta.dema(...)`

## How to read it

Read it exactly like `ema` — trend direction, support, crossovers — but expect turns sooner: on a straight-line move DEMA carries essentially zero lag, a property `ema` alone never has.

## Pitfalls

Cancelling lag also cancels some of the smoothing that made moving averages useful in the first place — DEMA overshoots and whips around real reversals more than `ema` does, especially at short lengths. It also needs roughly twice the warm-up of a plain EMA (`EMA2` needs a full window of already-warmed-up `EMA1` values).

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/double-exponential-moving-average-dema](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/double-exponential-moving-average-dema)
