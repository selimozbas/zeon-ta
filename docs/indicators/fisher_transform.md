---
title: Fisher Transform (Ehlers)
---

[← All indicators](../index.md)

`zeonta.fisher_transform()` — Ehlers' Fisher Transform: normalized price reshaped to sharpen its turning points.

## What it measures

Ordinary price data has a roughly uniform-to-bimodal distribution, not the Gaussian (bell-curve) one most statistical tools quietly assume. Ehlers' insight was to reshape a normalised price into something close to Gaussian — under that reshaping, large deviations become genuinely rare events instead of routine noise, which is exactly what makes the transform's turning points sharper and more decisive than an oscillator built directly from price.

## Formula

```text
Position = (Price - LowestPrice(n)) / (HighestPrice(n) - LowestPrice(n)) - 0.5; Value1 = 0.33 x 2 x Position + 0.67 x Value1[t-1], clamped to +/-0.999; Fish = 0.5 x ln((1 + Value1) / (1 - Value1)) + 0.5 x Fish[t-1]
```

## Parameters

**Required inputs:** `high`, `low`

| Parameter | Default |
| --- | --- |
| `length` | `10` |

## Returns

| Column |
| --- |
| `FISHERT_10` |
| `FISHERTs_10` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.fisher_transform(df['high'], df['low']).tail(3)
```

```text
            FISHERT_10  FISHERTs_10
date                               
2024-10-25   -0.813408    -0.884008
2024-10-26   -0.951520    -0.813408
2024-10-27   -1.273442    -0.951520
```

**Accessor form:** `df.zta.fisher_transform(...)`

## How to read it

Read ``FISHERT``/``FISHERTs`` as a crossover pair the same way `macd`'s line and signal are read: the sharpness Ehlers built into this transform means the crossovers tend to occur right at genuine turning points rather than lagging behind them the way a rounded indicator like `macd` does.

## Pitfalls

The sharp, decisive turns are a direct consequence of amplifying values near the edge of the recent range — on a genuinely choppy, range-bound market this can mean more frequent, less meaningful crossovers rather than fewer, cleaner ones.

## Reference

Formula source: [https://www.mesasoftware.com/papers/UsingTheFisherTransform.pdf](https://www.mesasoftware.com/papers/UsingTheFisherTransform.pdf)
