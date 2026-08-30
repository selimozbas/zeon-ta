# Chaikin Volatility (CVI)

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/chaikin_volatility.md)

`zeonta.chaikin_volatility()` — Rate of change of a smoothed high-low range: is the range widening or narrowing.

## What it measures

Marc Chaikin's rate-of-change take on volatility: rather than reporting the typical range as a level the way [atr](atr.md) does, this smooths the range with an EMA and then reports the *percentage change* of that smoothed range over the same window — is the range widening or narrowing, not how large it currently is.

## Formula

```text
CVI = ROC(EMA(High - Low, n), n)
```

## Parameters

**Required inputs:** `high`, `low`

| Parameter | Default |
| --- | --- |
| `length` | `10` |

## Returns

| Column |
| --- |
| `CVI_10` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.chaikin_volatility(df['high'], df['low']).tail(3)
```

```text
date
2024-10-25     4.441483
2024-10-26    -6.330787
2024-10-27   -12.577711
Name: CVI_10, dtype: float64
```

**Accessor form:** `df.zta.chaikin_volatility(...)`

## How to read it

Positive means the range has widened over the window (volatility picking up); negative means it has narrowed (volatility settling down) — often used to spot the quiet-before-the-storm setup a low, falling CVI can precede.

## Pitfalls

A rate of change of an already-smoothed quantity — expect more lag than `atr` itself, since this adds a second transformation on top of the EMA smoothing.

## Reference

Formula source: [https://www.luxalgo.com/library/concept/chaikin-volatility/](https://www.luxalgo.com/library/concept/chaikin-volatility/)
