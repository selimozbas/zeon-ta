# Variable Index Dynamic Average (VIDYA)

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/vidya.md)

`zeonta.vidya()` — An EMA whose smoothing speed adapts bar by bar to CMO's momentum reading.

## What it measures

An [ema](ema.md) whose smoothing constant is scaled by [cmo](cmo.md)'s momentum reading instead of staying fixed — freezing toward `0` (no update at all) when momentum is weak and choppy, and opening up toward the full EMA constant when momentum is strongly one-sided. A different self-adjusting idea from [kama](kama.md)'s Efficiency Ratio, but the same underlying motivation: don't use one fixed speed for every market condition.

## Formula

```text
VIDYA = Close * F * |CMO/100| + VIDYA[-1] * (1 - F * |CMO/100|), F = 2/(length+1)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `14` |
| `cmo_length` | `9` |

## Returns

| Column |
| --- |
| `VIDYA_14_9` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.vidya(df['close']).tail(3)
```

```text
date
2024-10-25    91.395668
2024-10-26    91.266282
2024-10-27    91.057410
Name: VIDYA_14_9, dtype: float64
```

**Accessor form:** `df.zta.vidya(...)`

## How to read it

Read the same way as any moving average — price crossing it, or its own slope.

## Pitfalls

Two stacked parameters (`length` for the base EMA speed, `cmo_length` for the momentum reading driving it) that both meaningfully change the result — not a single-knob indicator the way `ema` is.

## Reference

Formula source: [https://www.tradingpedia.com/forex-trading-indicators/chandes-variable-index-dynamic-average/](https://www.tradingpedia.com/forex-trading-indicators/chandes-variable-index-dynamic-average/)
