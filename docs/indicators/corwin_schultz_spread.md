---
title: Corwin-Schultz Spread Estimator
---

[← All indicators](../index.md)

`zeonta.corwin_schultz_spread()` — Bid-ask spread estimated from two days' high-low ranges alone.

## What it measures

Corwin & Schultz (2012) estimate a bid-ask spread from nothing but two consecutive bars' highs and lows — no trade or quote data at all. The insight: a bar's high is usually a buyer-initiated trade at the ask and its low a seller-initiated trade at the bid, so a bar's own high-low range carries both the day's price volatility and a fixed bid-ask-bounce contribution. Volatility grows with the length of the interval measured; the bounce does not, so writing down the expected squared range for one bar and for a two-bar window and solving that pair of equations together isolates the spread on its own.

## Formula

```text
beta = ln(H[t-1]/L[t-1])^2 + ln(H[t]/L[t])^2; gamma = ln(max(H[t-1],H[t]) / min(L[t-1],L[t]))^2; alpha = (sqrt(2 x beta) - sqrt(beta))/(3-2 x sqrt(2)) - sqrt(gamma/(3-2 x sqrt(2))); S = max(2 x (exp(alpha)-1) / (1+exp(alpha)), 0)
```

## Parameters

**Required inputs:** `high`, `low`

_None._

## Returns

| Column |
| --- |
| `CS` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.corwin_schultz_spread(df['high'], df['low']).tail(3)
```

```text
date
2024-10-25    0.0
2024-10-26    0.0
2024-10-27    0.0
Name: CS, dtype: float64
```

**Accessor form:** `df.zta.corwin_schultz_spread(...)`

## How to read it

Read CS as a fraction of price — 0.01 is a 1% quoted spread. It is a liquidity-cost estimate, not a volatility measure in the usual sense: a wider CS means trading this instrument costs more of the price just to cross the spread, independent of how much the price itself is moving.

## Pitfalls

The closed-form estimate can come out negative on a bar pair whose combined 2-day range happens to be tighter than either single day's own range — the paper's own remedy, floored to zero here, is what this function applies rather than leaving a meaningless negative number or turning it into NaN. This implements the paper's core two-day estimator only, not its optional overnight-jump adjustment for cases where the previous close printed outside the current day's own high-low range.

## Reference

Formula source: [https://doi.org/10.1111/j.1540-6261.2012.01729.x](https://doi.org/10.1111/j.1540-6261.2012.01729.x)
