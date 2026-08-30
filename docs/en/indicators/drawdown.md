# Drawdown

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/drawdown.md)

`zeonta.drawdown()` — Percentage decline from the running peak, since the start of the series.

## What it measures

The running percentage decline from the series' own all-time high so far — the same idea [cumulative_return](cumulative_return.md) applies to total gain, applied here to loss from the peak instead.

## Formula

```text
DD = (Close - CumMax(Close)) / CumMax(Close) * 100
```

## Parameters

**Required inputs:** `close`

_None._

## Returns

| Column |
| --- |
| `DD` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.drawdown(df['close']).tail(3)
```

```text
date
2024-10-25   -13.421818
2024-10-26   -14.360861
2024-10-27   -14.972795
Name: DD, dtype: float64
```

**Accessor form:** `df.zta.drawdown(...)`

## How to read it

Always `<= 0`; `0` exactly at every new high. The most negative value reached over a history is its maximum drawdown — the standard way to describe how bad the worst stretch was, independent of when it happened.

## Pitfalls

Like `cumulative_return`, this looks back to the start of whatever series you pass in rather than a fixed length — prepending more history can only move the running peak higher, which can change every later value.

## Reference

Formula source: [https://en.wikipedia.org/wiki/Drawdown_(economics)](https://en.wikipedia.org/wiki/Drawdown_(economics))
