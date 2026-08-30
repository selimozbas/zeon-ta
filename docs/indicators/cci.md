---
title: Commodity Channel Index (CCI)
---

[← All indicators](../index.md)

`zeonta.cci()` — How far typical price has strayed from its own average, in mean deviations.

## What it measures

CCI measures how far typical price has strayed from its own average, expressed in units of that period's normal deviation. Despite the name it has nothing to do with commodities specifically — it works on anything.

## Formula

```text
TP = (High + Low + Close) / 3; CCI = (TP - SMA(TP, 20)) / (0.015 x MeanDeviation(TP, 20))
```

## Parameters

**Required inputs:** `high`, `low`, `close`

| Parameter | Default |
| --- | --- |
| `length` | `20` |
| `constant` | `0.015` |

## Returns

| Column |
| --- |
| `CCI_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.cci(df['high'], df['low'], df['close']).tail(3)
```

```text
date
2024-10-25    -60.651903
2024-10-26   -131.135840
2024-10-27   -176.160519
Name: CCI_20, dtype: float64
```

**Accessor form:** `df.zta.cci(...)`

## How to read it

The 0.015 constant is chosen so that roughly 70-80% of readings fall between -100 and +100. Moves outside that band mark unusual displacement: either an exhausted extreme or, in the trend-following reading, a breakout worth joining.

## Pitfalls

CCI is unbounded, so "+100 is overbought" is a convention, not a ceiling — strong trends routinely print +300. The two standard interpretations (fade the extreme vs. follow the breakout) are opposites, so decide which one you are using before you trade it.
