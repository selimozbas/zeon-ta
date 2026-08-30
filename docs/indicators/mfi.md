---
title: Money Flow Index (MFI)
---

[← All indicators](../index.md)

`zeonta.mfi()` — "Volume-weighted RSI" — momentum measured through money flow instead of price.

## What it measures

Take [rsi](rsi.md)'s exact machinery — gains and losses summed over a window, squeezed onto a 0-100 scale — and replace "price change" with "typical price times volume". The result answers a question RSI cannot: was this move backed by real participation, or did it happen on thin volume?

## Formula

```text
Typical Price = (High + Low + Close) / 3; Raw Money Flow = Typical Price x Volume; Money Flow Ratio = Sum(Positive Money Flow, n) / Sum(Negative Money Flow, n); MFI = 100 - 100 / (1 + Money Flow Ratio)
```

## Parameters

**Required inputs:** `high`, `low`, `close`, `volume`

| Parameter | Default |
| --- | --- |
| `length` | `14` |

## Returns

| Column |
| --- |
| `MFI_14` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.mfi(df['high'], df['low'], df['close'], df['volume'], length=14).tail(3)
```

```text
date
2024-10-25    31.570060
2024-10-26    24.899728
2024-10-27    25.350635
Name: MFI_14, dtype: float64
```

**Accessor form:** `df.zta.mfi(...)`

## How to read it

Read the 0-100 scale exactly like RSI — above 80 conventionally "overbought", below 20 "oversold" — but treat an MFI reading that disagrees with RSI as the more informative signal: it means the volume behind the move doesn't match its price action.

## Pitfalls

Unlike RSI's Wilder-smoothed averages, MFI sums positive and negative flow with a plain (unsmoothed) rolling window, so it can be noisier bar to bar than RSI at the same length. It also inherits RSI's core caution: "overbought" is a description of momentum, not an instruction to sell — a strong trend can hold MFI above 80 for weeks.

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/money-flow-index-mfi](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/money-flow-index-mfi)
