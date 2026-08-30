---
title: Coppock Curve
---

[← All indicators](../index.md)

`zeonta.coppock_curve()` — A WMA of two summed rate-of-change measures, built to spot major long-term bottoms.

## What it measures

Edwin Coppock built the two `roc` periods (14 and 11) around how long, in his research, it took investor sentiment to recover from a loss — unconventional inputs for a technical indicator, but the result is a slow, heavily-smoothed long-term momentum line. Summing two `roc` readings before smoothing gives it a broader view of momentum than either period alone.

## Formula

```text
Coppock = WMA(ROC(Close, long) + ROC(Close, short), wma_length)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `long` | `14` |
| `short` | `11` |
| `wma_length` | `10` |

## Returns

| Column |
| --- |
| `COPC_14_11_10` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.coppock_curve(df['close']).tail(3)
```

```text
date
2024-10-25   -1.019351
2024-10-26   -1.941507
2024-10-27   -2.904687
Name: COPC_14_11_10, dtype: float64
```

**Accessor form:** `df.zta.coppock_curve(...)`

## How to read it

Originally designed for monthly charts to call major market bottoms: a buy signal is the Coppock Curve turning up from below zero. It was never meant for everyday trading signals or for calling tops — Coppock built it specifically as a long-term, buy-side-only tool.

## Pitfalls

Applying Coppock's own (14, 11, 10) settings to daily charts (rather than the monthly charts it was designed for) produces a much noisier, faster-turning line that no longer behaves like the major-bottom-calling tool it was built to be.

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/coppock-curve](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/coppock-curve)
