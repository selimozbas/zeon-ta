# Average True Range (ATR)

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/atr.md)

`zeonta.atr()` — Wilder-smoothed average of True Range — how much a symbol typically moves.

## What it measures

How far does this symbol typically move in one bar? ATR answers that in the instrument's own units. Because true range includes the gap from the previous close, it does not understate volatility on a market that jumps overnight.

## Formula

```text
TR = max(High - Low, |High - PrevClose|, |Low - PrevClose|); ATR = Wilder-smoothed average of TR over 14 periods (first ATR = SMA(TR,14), then ATR = (PrevATR x 13 + TR) / 14)
```

## Parameters

**Required inputs:** `high`, `low`, `close`

| Parameter | Default |
| --- | --- |
| `length` | `14` |

## Returns

| Column |
| --- |
| `ATR_14` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.atr(df['high'], df['low'], df['close'], length=14).tail(3)
```

```text
date
2024-10-25    1.198313
2024-10-26    1.194562
2024-10-27    1.221172
Name: ATR_14, dtype: float64
```

**Accessor form:** `df.zta.atr(...)`

## How to read it

ATR is the standard way to size a position and place a stop: a stop at 2 x ATR is the same amount of "room" whether you are trading a quiet bond ETF or a volatile small-cap. Rising ATR means conditions are getting wider, not that price is going up.

## Pitfalls

ATR is directionless — a crash and a melt-up produce the same reading. It is also an absolute figure, so an ATR of 5 is meaningless without knowing the price; divide by close if you need to compare across symbols.

## Reference

Formula source: [https://ta.cognicode.org/learn/atr](https://ta.cognicode.org/learn/atr)
