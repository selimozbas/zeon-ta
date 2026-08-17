# SuperTrend

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/supertrend.md)

`zeonta.supertrend()` — ATR-based trailing line that flips between support and resistance.

## What it measures

A single line that sits under price in an uptrend and above it in a downtrend. Unlike a moving average it does not smooth price into a lagging curve — it builds a volatility-adjusted band and lets the trend ride one side of it until price forces a flip.

## Formula

```text
Basic Upper Band = hl2 + multiplier x ATR(period); Basic Lower Band = hl2 - multiplier x ATR(period); Final Upper Band trails downward only, Final Lower Band trails upward only; SuperTrend = Final Lower Band while price closes above it (uptrend), Final Upper Band while price closes below it (downtrend); a flip occurs when close crosses to the opposite band
```

## Parameters

**Required inputs:** `high`, `low`, `close`

| Parameter | Default |
| --- | --- |
| `length` | `10` |
| `multiplier` | `3.0` |

## Returns

| Column |
| --- |
| `SUPERT_10_3.0` |
| `SUPERTd_10_3.0` |
| `SUPERTl_10_3.0` |
| `SUPERTs_10_3.0` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.supertrend(df['high'], df['low'], df['close'], length=10, multiplier=3)[['SUPERT_10_3.0', 'SUPERTd_10_3.0']].tail(3)
```

```text
            SUPERT_10_3.0  SUPERTd_10_3.0
date                                     
2024-10-25      92.539619            -1.0
2024-10-26      92.539619            -1.0
2024-10-27      92.539619            -1.0
```

**Accessor form:** `df.zta.supertrend(...)`

## How to read it

`SUPERTd` is the regime: `1.0` long-biased, `-1.0` short-biased. The one-way ratchet means the line only ever moves in the trend's favour, which makes it a natural trailing stop. `SUPERTl` and `SUPERTs` are the line masked to each regime, ready to plot in two colours.

## Pitfalls

SuperTrend has no opinion about trend strength — it flips identically on a powerful move and a feeble one. In a range it flips repeatedly, and trading it mechanically as a stop-and-reverse system produces a string of small losses. Pair it with a strength filter such as [adx](adx.md).

## Reference

Formula source: [https://ta.cognicode.org/learn/supertrend](https://ta.cognicode.org/learn/supertrend)
