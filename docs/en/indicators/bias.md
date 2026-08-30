# Bias

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/bias.md)

`zeonta.bias()` — Percentage deviation of Close from its own SMA.

## What it measures

A staple of Chinese/Taiwanese technical analysis: puts a number on how far price has stretched away from its own moving average. Where [efficiency_ratio](efficiency_ratio.md) or [choppiness_index](choppiness_index.md) describe how a *window* moved, Bias describes a single distance — price's current gap from its own average, nothing more.

## Formula

```text
BIAS = (Close - SMA(Close, length)) / SMA(Close, length) * 100
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `26` |

## Returns

| Column |
| --- |
| `BIAS_26` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.bias(df['close']).tail(3)
```

```text
date
2024-10-25   -0.861441
2024-10-26   -1.828151
2024-10-27   -2.366023
Name: BIAS_26, dtype: float64
```

**Accessor form:** `df.zta.bias(...)`

## How to read it

A large positive or negative reading is commonly read as "stretched too far" — a pullback toward the average (if positive) or a rebound away from it (if negative) becomes more likely the further Bias strays from zero.

## Pitfalls

`NaN` wherever the window's SMA is exactly `0`, rather than an undefined division.

## Reference

Formula source: [https://research.titanfx.com/technical-analysis/ma/bias](https://research.titanfx.com/technical-analysis/ma/bias)
