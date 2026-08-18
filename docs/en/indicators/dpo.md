# Detrended Price Oscillator (DPO)

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/dpo.md)

`zeonta.dpo()` — Price from n/2+1 bars ago minus the current n-bar SMA, built to expose cycles.

## What it measures

Every other oscillator in this library compares the *current* price against a moving average or a prior value; DPO instead compares an *older* price against the *current* SMA. That inversion is deliberate — it removes the trend component so the leftover oscillation lines up with the market's actual cycle peaks and troughs, at the cost of the line no longer reacting to the most recent bars at all.

## Formula

```text
DPO = Close[n/2 + 1 bars ago] - SMA(Close, n)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `20` |

## Returns

| Column |
| --- |
| `DPO_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.dpo(df['close']).tail(3)
```

```text
date
2024-10-25    0.245810
2024-10-26    1.671405
2024-10-27    1.352820
Name: DPO_20, dtype: float64
```

**Accessor form:** `df.zta.dpo(...)`

## How to read it

Count the bars between successive DPO peaks (or troughs) to estimate the dominant cycle length in the data, then use that estimate to set lengths for other tools. This is a cycle-identification tool, not a momentum or trend signal — it should not be read the way `macd` or `rsi` are.

## Pitfalls

Because it is deliberately shifted left (using an older price), the most recent DPO value does not reflect the most recent bars — it lags by design and cannot be used for a real-time signal the way it might naively appear on a chart.

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/detrended-price-oscillator-dpo](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/detrended-price-oscillator-dpo)
