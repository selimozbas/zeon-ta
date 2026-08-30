---
title: Stochastic RSI (StochRSI)
---

[← All indicators](../index.md)

`zeonta.stoch_rsi()` — The Stochastic formula applied to RSI instead of price — momentum of momentum.

## What it measures

Takes `stoch`'s exact range-position formula and applies it to `rsi` instead of price — an oscillator of an oscillator. RSI alone measures momentum; StochRSI measures how extreme *that* momentum reading is relative to its own recent history, which makes it swing between its bounds far more often and far more sharply than RSI itself ever does.

## Formula

```text
StochRSI = (RSI - LowestLow(RSI, n)) / (HighestHigh(RSI, n) - LowestLow(RSI, n))
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `rsi_length` | `14` |
| `stoch_length` | `14` |
| `smooth_k` | `3` |
| `smooth_d` | `3` |

## Returns

| Column |
| --- |
| `STOCHRSIk_14_14_3_3` |
| `STOCHRSId_14_14_3_3` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.stoch_rsi(df['close']).tail(3)
```

```text
            STOCHRSIk_14_14_3_3  STOCHRSId_14_14_3_3
date                                                
2024-10-25            42.204660            34.814315
2024-10-26            25.801741            34.817172
2024-10-27            10.968497            26.324966
```

**Accessor form:** `df.zta.stoch_rsi(...)`

## How to read it

Above 80 conventionally "overbought", below 20 "oversold" — but because StochRSI is so much more volatile than RSI, it spends far more time near those extremes, so treat crossings of the 50 line or %K crossing %D as more useful signals than the extremes alone.

## Pitfalls

When RSI itself goes flat — most obviously when it is pinned at 100 or 0 through a strong trend — StochRSI's own high-low range collapses to zero and the indicator falls back to the midpoint (50) rather than staying at an extreme, which can look like a reversal signal that isn't one. It is also a doubly-derived indicator (RSI of price, then Stochastic of RSI), so treat single readings with real caution.

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/stochrsi](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/stochrsi)
