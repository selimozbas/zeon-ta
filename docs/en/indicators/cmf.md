# Chaikin Money Flow (CMF)

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/cmf.md)

`zeonta.cmf()` — Volume-weighted measure of where price closed within its own range.

## What it measures

[obv](obv.md)'s more careful cousin: instead of asking only whether the close was up or down, CMF asks *where inside the bar's full range* the close landed, and weights that position by volume. A close pinned to the high of the range scores close to +1; a close pinned to the low scores close to -1.

## Formula

```text
Money Flow Multiplier = ((Close - Low) - (High - Close)) / (High - Low); Money Flow Volume = Money Flow Multiplier x Volume; CMF = Sum(Money Flow Volume, n) / Sum(Volume, n)
```

## Parameters

**Required inputs:** `high`, `low`, `close`, `volume`

| Parameter | Default |
| --- | --- |
| `length` | `20` |

## Returns

| Column |
| --- |
| `CMF_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.cmf(df['high'], df['low'], df['close'], df['volume'], length=20).tail(3)
```

```text
date
2024-10-25   -0.155522
2024-10-26   -0.202660
2024-10-27   -0.226028
Name: CMF_20, dtype: float64
```

**Accessor form:** `df.zta.cmf(...)`

## How to read it

Sustained readings above zero over the window mean volume has concentrated on bars that closed strong — buying pressure. Traders often use the zero line itself as a trend filter ("only take longs while CMF is positive") rather than trading specific levels.

## Pitfalls

A bar with a very narrow high-low range makes the Money Flow Multiplier's denominator tiny, so ordinary volume on a quiet bar can swing CMF sharply even though nothing much happened — this implementation defines that degenerate case as `0` rather than letting it blow up, but a run of narrow-range bars can still make CMF noisier than the price action underneath it would suggest.

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/chaikin-money-flow-cmf](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/chaikin-money-flow-cmf)
