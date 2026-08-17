# Vortex Indicator

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/vortex.md)

`zeonta.vortex()` — Compares how far price moved from the prior bar's opposite extreme, both directions.

## What it measures

Each line measures how far the current bar's range stretched away from the *opposite* extreme of the prior bar, summed over a window and normalised by the same window's true range. +VI leads -VI in an uptrend and the two cross around trend changes — the same directional-pair relationship `adx`'s +DI/-DI lines have, though Vortex uses plain rolling sums throughout rather than Wilder smoothing, so it reacts faster and forgets old bars completely once they age out of the window.

## Formula

```text
+VM = |High - PriorLow|; -VM = |Low - PriorHigh|; +VI = Sum(+VM, n) / Sum(TR, n); -VI = Sum(-VM, n) / Sum(TR, n)
```

## Parameters

**Required inputs:** `high`, `low`, `close`

| Parameter | Default |
| --- | --- |
| `length` | `14` |

## Returns

| Column |
| --- |
| `VTXP_14` |
| `VTXM_14` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.vortex(df['high'], df['low'], df['close']).tail(3)
```

```text
             VTXP_14   VTXM_14
date                          
2024-10-25  1.002726  1.050817
2024-10-26  0.913460  1.066400
2024-10-27  0.872397  1.093248
```

**Accessor form:** `df.zta.vortex(...)`

## How to read it

A crossover of +VI above -VI is read as a bullish signal, the reverse as bearish — the further apart the two lines sit, the stronger the implied trend. Because the lines use plain sums, they respond quickly to a fresh burst of directional movement, which also means more crossovers (and more false signals) in a genuinely choppy market than a Wilder-smoothed pair like ADX's DI lines would give.

## Pitfalls

Vortex has no fixed upper bound the way RSI or Stochastic do — both lines typically sit somewhere around 0.5 to 1.5, but a sharp enough move can push either one higher still, so treat the absolute level with caution and lean on the crossover and the gap between the two lines instead.

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/vortex-indicator](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/vortex-indicator)
