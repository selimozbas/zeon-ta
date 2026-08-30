---
title: Guppy Multiple Moving Average
---

[← All indicators](../index.md)

`zeonta.gmma()` — Two six-EMA ribbons (short-term traders, long-term investors) plotted together.

## What it measures

Two fixed six-line [ema_ribbon](ema_ribbon.md)s plotted together rather than one: a fast group standing in for short-term trader activity, and a slow group standing in for longer-term investor activity. Neither group's periods are tunable — the whole point of GMMA is this specific pair of period sets, not a generic ribbon.

## Formula

```text
Two 6-line EMA groups: fast = EMA(3,5,8,10,12,15), slow = EMA(30,35,40,45,50,60)
```

## Parameters

**Required inputs:** `close`

_None._

## Returns

| Column |
| --- |
| `GMMAf_3` |
| `GMMAf_5` |
| `GMMAf_8` |
| `GMMAf_10` |
| `GMMAf_12` |
| `GMMAf_15` |
| `GMMAs_30` |
| `GMMAs_35` |
| `GMMAs_40` |
| `GMMAs_45` |
| `GMMAs_50` |
| `GMMAs_60` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.gmma(df['close']).tail(3)
```

```text
              GMMAf_3    GMMAf_5    GMMAf_8   GMMAf_10   GMMAf_12   GMMAf_15   GMMAs_30  \
date                                                                                      
2024-10-25  90.230603  90.260040  90.359061  90.428278  90.493176  90.583335  90.972082   
2024-10-26  89.674801  89.879693  90.083492  90.190227  90.281764  90.400293  90.852528   
2024-10-27  89.078501  89.413862  89.727649  89.879677  90.004908  90.160531  90.699604   

             GMMAs_35   GMMAs_40   GMMAs_45   GMMAs_50   GMMAs_60  
date                                                               
2024-10-25  91.091171  91.208183  91.323688  91.437720  91.660472  
2024-10-26  90.981606  91.106272  91.227832  91.346790  91.577145  
2024-10-27  90.842750  90.978268  91.108456  91.234453  91.475671  
```

**Accessor form:** `df.zta.gmma(...)`

## How to read it

Compression *within* a group signals agreement among that group's own timescales; wide separation *between* the two groups signals a well-established trend. The fast group crossing the slow group is the classic entry signal, but reading the ribbons' own compression/expansion is the indicator's real purpose.

## Pitfalls

Twelve EMA lines at once is a lot to plot — most charting tools shade each group as a ribbon rather than drawing all twelve individually.

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/trading-strategies-and-models/trading-strategies/moving-average-trading-strategies/guppy-multiple-moving-average-an-ma-ribbon-designed-to-tip-the-markets-hand](https://chartschool.stockcharts.com/table-of-contents/trading-strategies-and-models/trading-strategies/moving-average-trading-strategies/guppy-multiple-moving-average-an-ma-ribbon-designed-to-tip-the-markets-hand)
