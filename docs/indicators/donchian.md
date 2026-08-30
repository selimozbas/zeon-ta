---
title: Donchian Channels
---

[← All indicators](../index.md)

`zeonta.donchian()` — Highest high and lowest low over n bars — the classic breakout channel.

## What it measures

The simplest channel there is: the highest high and lowest low of the last n bars. Its simplicity is the point — the original Turtle Trading system was built almost entirely on breakouts of this channel.

## Formula

```text
Upper Channel = Highest High(n); Lower Channel = Lowest Low(n); Middle Line = (Upper Channel + Lower Channel) / 2
```

## Parameters

**Required inputs:** `high`, `low`

| Parameter | Default |
| --- | --- |
| `length` | `20` |

## Returns

| Column |
| --- |
| `DCL_20` |
| `DCM_20` |
| `DCU_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.donchian(df['high'], df['low'], length=20).tail(3)
```

```text
             DCL_20    DCM_20   DCU_20
date                                  
2024-10-25  88.9268  90.94945  92.9721
2024-10-26  88.9268  90.94945  92.9721
2024-10-27  88.0724  90.52225  92.9721
```

**Accessor form:** `df.zta.donchian(...)`

## How to read it

A close at the upper channel means this bar made the highest high of the last n bars — that statement *is* the breakout signal. The middle line is a common exit for a position entered on a breakout.

## Pitfalls

The channel includes the current bar, so price can never close outside it — "price broke above the channel" really means "price reached the channel". Compare against the previous bar's channel if you want a breakout that excludes the breaking bar.
