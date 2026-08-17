# MACD (Moving Average Convergence Divergence)

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/macd.md)

`zeonta.macd()` — Difference between two EMAs, with a signal line and histogram.

## What it measures

MACD turns the distance between a fast and a slow EMA into its own series. That distance grows when a trend accelerates and shrinks when it tires, which makes MACD a momentum reading built entirely out of trend tools.

## Formula

```text
MACD Line = EMA(12) - EMA(26); Signal Line = EMA(9) of MACD Line; Histogram = MACD Line - Signal Line
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `fast` | `12` |
| `slow` | `26` |
| `signal` | `9` |

## Returns

| Column |
| --- |
| `MACD_12_26_9` |
| `MACDs_12_26_9` |
| `MACDh_12_26_9` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.macd(df['close']).tail(3)
```

```text
            MACD_12_26_9  MACDs_12_26_9  MACDh_12_26_9
date                                                  
2024-10-25     -0.381243      -0.343159      -0.038084
2024-10-26     -0.462624      -0.367052      -0.095572
2024-10-27     -0.571910      -0.408024      -0.163887
```

**Accessor form:** `df.zta.macd(...)`

## How to read it

The histogram is the part most people actually trade: it crosses zero exactly when the MACD line crosses its signal, and its height shows how fast the gap is changing. MACD above zero means the fast EMA is above the slow one — an uptrend by that definition.

## Pitfalls

MACD is unbounded and its values scale with price, so a reading of 3 means something entirely different on a $20 stock and a $2,000 one — never compare raw MACD across symbols. And as a doubly smoothed trend tool it whipsaws badly in a range.

## Reference

Formula source: [https://ta.cognicode.org/learn/macd](https://ta.cognicode.org/learn/macd)
