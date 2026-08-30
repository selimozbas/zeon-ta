---
title: True Strength Index (TSI)
---

[← All indicators](../index.md)

`zeonta.tsi()` — Double-smoothed momentum, bounded and steadier than a single-pass oscillator.

## What it measures

William Blau's double smoothing operates on the raw price change itself, before any ratio is taken — the opposite order from `rsi`, which first turns gains/losses into separate averages and only then divides. TSI's double-EMA-first approach is meant to track the underlying trend closely while still filtering short-term noise.

## Formula

```text
PC = Close - Close[1 bar ago]; DoubleSmoothedPC = EMA(EMA(PC, long), short); DoubleSmoothedAbsPC = EMA(EMA(|PC|, long), short); TSI = 100 x DoubleSmoothedPC / DoubleSmoothedAbsPC; Signal = EMA(TSI, signal)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `long` | `25` |
| `short` | `13` |
| `signal` | `7` |

## Returns

| Column |
| --- |
| `TSI_25_13_7` |
| `TSIs_25_13_7` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.tsi(df['close']).tail(3)
```

```text
            TSI_25_13_7  TSIs_25_13_7
date                                 
2024-10-25   -12.260304    -11.761409
2024-10-26   -14.523263    -12.451873
2024-10-27   -17.545947    -13.725391
```

**Accessor form:** `df.zta.tsi(...)`

## How to read it

Overbought/oversold readings, centerline crossovers, signal-line crossovers and divergences all apply, the same vocabulary as `rsi` and `macd` combined — TSI is somewhat unusual in that its peaks and troughs often line up closely with price's own peaks and troughs, unlike oscillators that flatten out during a strong sustained move.

## Pitfalls

Neither StockCharts nor Fidelity's guide commits to one canonical default signal-line period — this implementation uses 7 alongside the (25, 13) core smoothing pair, the value repeated most often across independent sources, but TSI(25,13,13) and TSI(40,20,10) are both also in common use.

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/true-strength-index](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/true-strength-index)
