# Balance of Power (BOP)

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/bop.md)

`zeonta.bop()` — Where the close landed between open and the bar's range, unweighted by volume.

## What it measures

Igor Livshin's 2001 measure of who won the bar outright: buyers pushed the close up from the open (positive), or sellers pushed it down (negative), scaled by how wide the bar's own range was. Similar in shape to [cmf](cmf.md)'s Money Flow Multiplier, but measured from the open rather than volume-weighted, and left as a raw per-bar ratio rather than summed over a window.

## Formula

```text
BOP = (Close - Open) / (High - Low)
```

## Parameters

**Required inputs:** `open`, `high`, `low`, `close`

_None._

## Returns

| Column |
| --- |
| `BOP` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.bop(df['open'], df['high'], df['low'], df['close']).tail(3)
```

```text
date
2024-10-25   -0.376071
2024-10-26   -0.959853
2024-10-27   -0.476996
Name: BOP, dtype: float64
```

**Accessor form:** `df.zta.bop(...)`

## How to read it

Raw values are choppy bar to bar; many traders pipe this into `sma()` themselves for a smoother line, which is how StockCharts' own page presents it — this function returns the unsmoothed ratio to match TA-Lib's own zero-parameter convention.

## Pitfalls

Zero-range bars (`High == Low`) would divide by zero; treated as `0` rather than raising or producing a warning.

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/balance-of-power-bop](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/balance-of-power-bop)
