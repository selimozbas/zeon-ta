---
title: Chaikin Oscillator
---

[← All indicators](../index.md)

`zeonta.chaikin_oscillator()` — MACD's fast-EMA-minus-slow-EMA shape applied to the A/D Line instead of price.

## What it measures

The same fast-EMA-minus-slow-EMA shape `macd` applies to price, applied here to `adl` instead. ADL itself only tells you the cumulative *level* of buying versus selling pressure; taking the difference of two EMAs of it turns that into a rate-of-change reading — whether accumulation/distribution is currently speeding up or slowing down, the same relationship `awesome_oscillator` has to raw price.

## Formula

```text
ChaikinOsc = EMA(ADL, fast) - EMA(ADL, slow)
```

## Parameters

**Required inputs:** `high`, `low`, `close`, `volume`

| Parameter | Default |
| --- | --- |
| `fast` | `3` |
| `slow` | `10` |

## Returns

| Column |
| --- |
| `ADOSC_3_10` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.chaikin_oscillator(df['high'], df['low'], df['close'], df['volume']).tail(3)
```

```text
date
2024-10-25   -433147.921630
2024-10-26   -548733.439778
2024-10-27   -586042.606100
Name: ADOSC_3_10, dtype: float64
```

**Accessor form:** `df.zta.chaikin_oscillator(...)`

## How to read it

Read it like any zero-centred momentum oscillator: crossing above zero signals ADL is accelerating upward (buying pressure building faster than its own recent average), crossing below signals the opposite. A divergence between the Chaikin Oscillator and price — price making a new high while the oscillator fails to — is read the same bearish-divergence way `macd` divergence is.

## Pitfalls

Inherits every caveat `adl` has: a very narrow high-low range makes the underlying Money Flow Multiplier noisy, and the whole thing is built on a running total with no natural reset point. Because it is the difference of two EMAs, it also inherits `macd`'s own lag — both EMAs react to the same underlying series, so the oscillator reflects a *change* in ADL's trend a few bars after it actually happens, not at the moment it happens.

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/chaikin-oscillator](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/chaikin-oscillator)
