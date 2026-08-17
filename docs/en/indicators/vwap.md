# VWAP (Volume-Weighted Average Price)

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/vwap.md)

`zeonta.vwap()` — Volume-weighted average price with standard-deviation bands.

## What it measures

The average price actually paid today, weighted by how much traded at each level. It is not a chart study so much as a benchmark: institutions are measured against VWAP, which is why price gravitates to it.

## Formula

```text
Typical Price = (High + Low + Close) / 3; VWAP = sum(Typical Price x Volume) / sum(Volume), reset at each session open; Upper/Lower Band = VWAP +/- k x stdev(Typical Price, weighted by volume)
```

## Parameters

**Required inputs:** `high`, `low`, `close`, `volume`

| Parameter | Default |
| --- | --- |
| `anchor` | `'session'` |
| `length` | `20` |
| `std` | `1.0` |

## Returns

| Column |
| --- |
| `VWAP_session` |
| `VWAPU_session` |
| `VWAPL_session` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.vwap(df['high'], df['low'], df['close'], df['volume'], anchor='rolling', length=20).tail(3)
```

```text
            VWAP_rolling_20  VWAPU_rolling_20  VWAPL_rolling_20
date                                                           
2024-10-25        90.640999         91.326784         89.955215
2024-10-26        90.599117         91.327749         89.870484
2024-10-27        90.528552         91.327042         89.730063
```

**Accessor form:** `df.zta.vwap(...)`

## How to read it

Price above VWAP means buyers are paying up relative to the session's average. The bands mark statistically stretched levels within the session. Use `anchor="session"` on instruments with a real open, and `anchor="rolling"` on 24/7 markets like crypto.

## Pitfalls

A VWAP that never resets is a different statistic entirely and loses the benchmark meaning — the reset is the point. Session anchoring needs a `DatetimeIndex` to find session boundaries; without one this function raises rather than silently computing the wrong thing.

## Reference

Formula source: [https://ta.cognicode.org/learn/vwap](https://ta.cognicode.org/learn/vwap)
