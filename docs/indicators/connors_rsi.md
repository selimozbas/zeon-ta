---
title: Connors RSI
---

[← All indicators](../index.md)

`zeonta.connors_rsi()` — Composite RSI averaging price RSI, streak RSI and a 1-bar-return percent rank.

## What it measures

Averages three independent short-term readings of the same close series: an ordinary [rsi](rsi.md) on price, an `rsi` on the signed streak of consecutive up/down closes (is the current run itself unusually long?), and a percent-rank of the latest 1-bar return against its own recent history (a magnitude-aware read neither RSI term captures).

## Formula

```text
CRSI = (RSI(Close) + RSI(Streak) + PercentRank(ROC(1))) / 3
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `rsi_length` | `3` |
| `streak_length` | `2` |
| `rank_length` | `100` |

## Returns

| Column |
| --- |
| `CRSI_3_2_100` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.connors_rsi(df['close']).tail(3)
```

```text
date
2024-10-25    29.258298
2024-10-26    12.382256
2024-10-27    10.799912
Name: CRSI_3_2_100, dtype: float64
```

**Accessor form:** `df.zta.connors_rsi(...)`

## How to read it

Ranges 0-100 like each of its three components; short-term mean-reversion traders commonly treat readings under 10-20 or over 80-90 as extremes.

## Pitfalls

Three separate lookbacks (`rsi_length`, `streak_length`, `rank_length`) stack together — changing any one changes the blend, not just one leg of it.

## Reference

Formula source: [https://www.tradingview.com/support/solutions/43000502017-connors-rsi-crsi/](https://www.tradingview.com/support/solutions/43000502017-connors-rsi-crsi/)
