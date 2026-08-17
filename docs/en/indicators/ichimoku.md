# Ichimoku

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/ichimoku.md)

`zeonta.ichimoku()` — Five-line Japanese system giving trend, momentum and support in one view.

## What it measures

A complete system rather than a single indicator: five lines that between them give trend, momentum, and support and resistance in one glance. The cloud between the two Senkou spans is projected 26 bars into the future, which is what makes Ichimoku look unlike anything else on a chart.

## Formula

```text
Tenkan-sen = (Highest High(9) + Lowest Low(9)) / 2; Kijun-sen = (Highest High(26) + Lowest Low(26)) / 2; Senkou Span A = (Tenkan-sen + Kijun-sen) / 2, plotted 26 periods ahead; Senkou Span B = (Highest High(52) + Lowest Low(52)) / 2, plotted 26 periods ahead; Chikou Span = Close, plotted 26 periods behind
```

## Parameters

**Required inputs:** `high`, `low`, `close`

| Parameter | Default |
| --- | --- |
| `tenkan` | `9` |
| `kijun` | `26` |
| `senkou` | `52` |
| `displacement` | `26` |

## Returns

| Column |
| --- |
| `ITS_9` |
| `IKS_26` |
| `ISA_9_26` |
| `ISB_52` |
| `ICS_26` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.ichimoku(df['high'], df['low'], df['close'])[0].tail(2)
```

```text
               ITS_9    IKS_26   ISA_9_26    ISB_52  ICS_26
date                                                       
2024-10-26  90.52465  90.94945  91.997300  92.92670     NaN
2024-10-27  89.85265  90.52225  91.869125  92.79215     NaN
```

```python
zeonta.ichimoku(df['high'], df['low'], df['close'])[1].head(2)
```

```text
             ISA_9_26    ISB_52
2024-10-28  91.869125  92.79215
2024-10-29  91.869125  92.79215
```

**Accessor form:** `df.zta.ichimoku(...)`

## How to read it

Price above the cloud is bullish, below it bearish, inside it undecided. A thick cloud is strong support or resistance; a thin one is easily cut through. This function returns two frames — the on-chart lines, and the part of the cloud that lands beyond the last bar.

## Pitfalls

The forward cloud is not a forecast: it is today's midpoints drawn 26 bars to the right, and it will not change when it gets there. Also, the default 9/26/52 settings come from a six-day Japanese trading week; they carry no special meaning on a five-day or 24/7 market.

## Reference

Formula source: [https://ta.cognicode.org/learn/ichimoku](https://ta.cognicode.org/learn/ichimoku)
