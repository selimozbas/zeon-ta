---
title: The Squeeze (TTM Squeeze)
---

[← All indicators](../index.md)

`zeonta.squeeze()` — Detects Bollinger Bands compressed inside Keltner Channels, plus a momentum read.

## What it measures

Two volatility measures that react at different speeds, compared against each other. When the faster one (Bollinger) contracts inside the slower one (Keltner), volatility has compressed unusually far — and compressed volatility tends to expand.

## Formula

```text
Squeeze ON when BB Upper < KC Upper AND BB Lower > KC Lower (Bollinger Bands compressed fully inside Keltner Channels); Momentum = LinReg(Close - Avg(HighestHigh(n), LowestLow(n), SMA(Close,n)), n)
```

## Parameters

**Required inputs:** `high`, `low`, `close`

| Parameter | Default |
| --- | --- |
| `bb_length` | `20` |
| `bb_std` | `2.0` |
| `kc_length` | `20` |
| `kc_multiplier` | `1.5` |

## Returns

| Column |
| --- |
| `SQZ_ON_20_2.0_20_1.5` |
| `SQZ_OFF_20_2.0_20_1.5` |
| `SQZ_MOM_20_2.0_20_1.5` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.squeeze(df['high'], df['low'], df['close']).tail(3)
```

```text
            SQZ_ON_20_2.0_20_1.5  SQZ_OFF_20_2.0_20_1.5  SQZ_MOM_20_2.0_20_1.5
date                                                                          
2024-10-25                   1.0                    0.0              -0.410355
2024-10-26                   1.0                    0.0              -0.675908
2024-10-27                   0.0                    1.0              -0.975041
```

**Accessor form:** `df.zta.squeeze(...)`

## How to read it

`SQZ_ON` marks the compression; the bar traders actually act on is the release, when `SQZ_OFF` first turns on. The momentum histogram supplies the direction: rising bars above zero at the release point up, falling bars below zero point down.

## Pitfalls

The squeeze says a move is likely, never which way — trading it without the momentum read is a coin flip. Note also that widening `kc_multiplier` pushes the Keltner bands further out and therefore makes squeezes **more** frequent, not less — some casual descriptions of this indicator claim the opposite, but that claim doesn't follow from the formula itself, which this library follows. The momentum midline uses the published TTM *nested* average — `avg(avg(hh, ll), sma)`, weighting the range midpoint and the SMA at one half each — rather than an equal three-way mean, which some casual descriptions suggest instead; values here will differ from an implementation that follows that reading literally.
