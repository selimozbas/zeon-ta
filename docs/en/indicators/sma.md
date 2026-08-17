# Simple Moving Average (SMA)

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/sma.md)

`zeonta.sma()` — Equally weighted average of the last n closes.

## What it measures

The simplest way to see a trend through the noise: average the last n closes and plot that instead of price. Every bar in the window counts the same, which makes the SMA smooth and predictable — and also means a single old bar dropping out of the window can move it.

## Formula

```text
SMA(n) = (1/n) x sum(Close[i]) for the last n bars — an equally weighted average of the n most recent closes.
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `20` |

## Returns

| Column |
| --- |
| `SMA_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.sma(df['close'], length=20).tail(3)
```

```text
date
2024-10-25    90.703090
2024-10-26    90.624895
2024-10-27    90.504580
Name: SMA_20, dtype: float64
```

```python
df.zta.sma(50).tail(3)
```

```text
date
2024-10-25    91.545918
2024-10-26    91.470696
2024-10-27    91.385108
Name: SMA_50, dtype: float64
```

**Accessor form:** `df.zta.sma(...)`

## How to read it

Price above a rising SMA is the textbook uptrend; price below a falling one is the downtrend. The 50 and 200 are watched far more than any other lengths, simply because so many people watch them.

## Pitfalls

An SMA lags by roughly half its length, so it confirms a turn well after it happened; it is a description of the past, not a forecast. In a sideways market price crosses it constantly, producing signals that are all noise.

## Reference

Formula source: [https://ta.cognicode.org/learn/sma](https://ta.cognicode.org/learn/sma)
