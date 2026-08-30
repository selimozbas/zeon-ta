---
title: TRIX (Triple Exponential Average)
---

[← All indicators](../index.md)

`zeonta.trix()` — 1-bar percent change of a triple-smoothed EMA — momentum with heavy noise filtering.

## What it measures

Three EMA passes before ever measuring a change is a deliberately heavier filter than `roc`'s single comparison against an older price, or `macd`'s single-pass EMA difference — the tradeoff for that extra noise reduction is proportionally more lag before TRIX actually turns.

## Formula

```text
EMA1 = EMA(Close, n); EMA2 = EMA(EMA1, n); EMA3 = EMA(EMA2, n); TRIX = (EMA3[t] - EMA3[t-1]) / EMA3[t-1] x 100
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `15` |
| `signal` | `9` |

## Returns

| Column |
| --- |
| `TRIX_15_9` |
| `TRIXs_15_9` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.trix(df['close']).tail(3)
```

```text
            TRIX_15_9  TRIXs_15_9
date                             
2024-10-25  -0.053222   -0.049919
2024-10-26  -0.056651   -0.051266
2024-10-27  -0.062506   -0.053514
```

**Accessor form:** `df.zta.trix(...)`

## How to read it

Read the zero line and the signal line the same way as `macd`: crossing above zero is bullish, crossing below is bearish, and a cross of TRIX above/below its own signal line (a 9-day EMA of TRIX) gives an earlier, noisier version of the same call.

## Pitfalls

The triple smoothing that makes TRIX quiet also makes it slow — on a fast-moving or short-lived trend it can still be turning while the move is already over. It is usually applied to longer time frames (weekly charts, or long daily lengths) for exactly this reason.

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/trix](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/trix)
