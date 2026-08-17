# Triple Exponential Moving Average (TEMA)

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/tema.md)

`zeonta.tema()` — EMA with even less lag than DEMA, by combining three nested EMAs.

## What it measures

The same lag-cancelling idea as `dema`, carried one smoothing pass further. Where a straight price move already cancels almost perfectly under DEMA, TEMA's extra term keeps that cancellation working on *curved* moves — accelerations and decelerations — where DEMA itself starts to fall behind again.

## Formula

```text
TEMA = (3 x EMA1) - (3 x EMA2) + EMA3, where EMA1 = EMA(Close, n), EMA2 = EMA(EMA1, n) and EMA3 = EMA(EMA2, n)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `20` |

## Returns

| Column |
| --- |
| `TEMA_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.tema(df['close'], length=20).tail(3)
```

```text
date
2024-10-25    90.151836
2024-10-26    89.833830
2024-10-27    89.413759
Name: TEMA_20, dtype: float64
```

**Accessor form:** `df.zta.tema(...)`

## How to read it

Read it like `dema` or `ema`, but trust it most exactly where DEMA starts to slip: a trend that is itself speeding up or slowing down, not just moving in a straight line.

## Pitfalls

Three layers of lag-cancelling means three layers of overshoot risk — TEMA reacts to noise even more eagerly than `dema` does, and needs roughly three times a plain EMA's warm-up (`EMA3` needs a full window of already-warmed-up `EMA2` values).

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/triple-exponential-moving-average-tema](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/triple-exponential-moving-average-tema)
