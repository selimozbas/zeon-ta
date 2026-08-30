# Volume-Weighted Moving Average (VWMA)

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/vwma.md)

`zeonta.vwma()` — Simple moving average, but each bar weighted by its own volume.

## What it measures

[sma](sma.md) treats every bar in the window equally regardless of how much traded on it; VWMA instead lets a heavy-volume bar pull the average toward its own close more than a quiet bar does — the same volume-weighting idea [vwap](vwap.md) uses, but over a fixed rolling window instead of resetting each session.

## Formula

```text
VWMA = Sum(Close * Volume, n) / Sum(Volume, n)
```

## Parameters

**Required inputs:** `close`, `volume`

| Parameter | Default |
| --- | --- |
| `length` | `20` |

## Returns

| Column |
| --- |
| `VWMA_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.vwma(df['close'], df['volume']).tail(3)
```

```text
date
2024-10-25    90.613110
2024-10-26    90.553374
2024-10-27    90.473801
Name: VWMA_20, dtype: float64
```

**Accessor form:** `df.zta.vwma(...)`

## How to read it

Read the same way as any moving average — price crossing above/below it, or its own slope — with the difference that a break on unusually heavy volume shows up more prominently here than in a plain SMA of the same length.

## Pitfalls

`NaN` whenever the window's total volume is exactly `0` (no trading at all in that window) rather than an undefined division.

## Reference

Formula source: [https://www.tradingview.com/support/solutions/43000592293-volume-weighted-moving-average-vwma/](https://www.tradingview.com/support/solutions/43000592293-volume-weighted-moving-average-vwma/)
