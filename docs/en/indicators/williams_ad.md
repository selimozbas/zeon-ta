# Williams Accumulation/Distribution (WAD)

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/williams_ad.md)

`zeonta.williams_ad()` — Running total gated by whether today extended a rising or falling close.

## What it measures

Larry Williams' predecessor to [adl](adl.md): where ADL weighs a bar by where the close sits inside *that bar's own* range, WAD anchors each bar against the *prior* close instead — a bar that gapped up only gets credit for the move above yesterday's close, not its own full range. No volume term, despite living in this category alongside ADL/OBV.

## Formula

```text
TRH = max(Close[-1], High); TRL = min(Close[-1], Low); WAD += (Close-TRL) if Close rose, (Close-TRH) if Close fell, else unchanged
```

## Parameters

**Required inputs:** `high`, `low`, `close`

_None._

## Returns

| Column |
| --- |
| `WAD` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.williams_ad(df['high'], df['low'], df['close']).tail(3)
```

```text
date
2024-10-25   -17.4391
2024-10-26   -18.5619
2024-10-27   -19.7192
Name: WAD, dtype: float64
```

**Accessor form:** `df.zta.williams_ad(...)`

## How to read it

Read the same way as `adl`/`obv` — a rising line alongside rising price confirms the trend; a failure to make a new high alongside price is a divergence warning.

## Pitfalls

A running total with an arbitrary starting level, like `adl`/`obv`/`pvt` — only its slope and its divergence from price carry meaning.

## Reference

Formula source: [https://tulipindicators.org/wad](https://tulipindicators.org/wad)
