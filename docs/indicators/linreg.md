---
title: Linear Regression Slope & Forecast
---

[← All indicators](../index.md)

`zeonta.linreg()` — Linear regression fit over the window: its slope and its endpoint (forecast) value.

## What it measures

StockCharts documents these as two separate indicators — Slope (default 20) and Linear Regression Forecast (default 14) — but both come from the exact same regression fit this library already computes inside `trend_channel` and `squeeze`, so they are exposed here as two columns from one call, sharing one length parameter, following the convention most platforms with a combined `LINEARREG` indicator family use.

## Formula

```text
Fits an ordinary-least-squares line y = mx + b to the last n closes; Slope = m; Forecast = the fitted line's value at the most recent bar
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `14` |

## Returns

| Column |
| --- |
| `LRSlope_14` |
| `LRForecast_14` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.linreg(df['close']).tail(3)
```

```text
            LRSlope_14  LRForecast_14
date                                 
2024-10-25   -0.128042      89.925937
2024-10-26   -0.164103      89.551111
2024-10-27   -0.208671      89.073237
```

**Accessor form:** `df.zta.linreg(...)`

## How to read it

``LRSlope`` reads like any trend-strength measure: its sign gives direction, its magnitude gives steepness, directly comparable to `~zeonta.aroon`'s trend read from a completely different angle. ``LRForecast`` tracks price closely, like a smoothed moving average, but overshoots less on a sharp reversal since it fits a straight line rather than weighting recent bars more heavily.

## Pitfalls

"Forecast" describes what the line represents (StockCharts' own name for it), not a claim about the future: ``LRForecast`` is the fitted value at the *current*, already-known bar, not a projection beyond it — using it as an actual price prediction is a misreading of the name.

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/linear-regression-forecast](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/linear-regression-forecast)
