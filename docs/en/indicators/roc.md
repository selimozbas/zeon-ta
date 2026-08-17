# Rate of Change (ROC)

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/roc.md)

`zeonta.roc()` — Percentage price change over n bars — the normalised sibling of momentum.

## What it measures

The normalised sibling of [momentum](momentum.md): the same n-bars-back comparison, expressed as a percentage instead of a raw price difference. That one change makes it comparable across symbols and across price levels of the same symbol over time.

## Formula

```text
ROC = [(Close - Close n periods ago) / (Close n periods ago)] x 100
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `12` |

## Returns

| Column |
| --- |
| `ROC_12` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.roc(df['close'], length=12).tail(3)
```

```text
date
2024-10-25   -1.119992
2024-10-26   -2.012009
2024-10-27   -4.132452
Name: ROC_12, dtype: float64
```

**Accessor form:** `df.zta.roc(...)`

## How to read it

ROC oscillates around zero the same way Momentum does, but a reading of "+5" always means the same thing — a 5% rise over the window — whether the symbol trades at $10 or $10,000. Sharp spikes away from zero mark unusually fast moves relative to the instrument's own recent pace.

## Pitfalls

ROC divides by the price n bars ago, so it is undefined (returned as `NaN`) on any bar whose reference close happened to be exactly zero — a real possibility on instruments quoted as a spread or a rate rather than a price. It also inherits Momentum's whipsaw behaviour in a range: a fast oscillation with no persistent trend behind it.

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/rate-of-change-roc](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/rate-of-change-roc)
