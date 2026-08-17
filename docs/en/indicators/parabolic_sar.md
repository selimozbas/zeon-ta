# Parabolic SAR

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/parabolic_sar.md)

`zeonta.parabolic_sar()` — Trailing stop-and-reverse dots that accelerate the longer a trend runs.

## What it measures

A series of dots that sit under price in an uptrend and above it in a downtrend, one step closer to price every bar. "Parabolic" describes the shape of that approach: the acceleration factor grows every time a new high (or low) prints, so the dots curve in toward price faster and faster the longer a trend runs.

## Formula

```text
Rising: Current SAR = Prior SAR + Prior AF x (Prior EP - Prior SAR); Falling: Current SAR = Prior SAR - Prior AF x (Prior SAR - Prior EP); AF starts at 0.02, increases by 0.02 with each new extreme point, capped at 0.20; SAR cannot move above the prior two periods' lows in an uptrend, nor below the prior two periods' highs in a downtrend
```

## Parameters

**Required inputs:** `high`, `low`

| Parameter | Default |
| --- | --- |
| `start` | `0.02` |
| `increment` | `0.02` |
| `max_af` | `0.2` |

## Returns

| Column |
| --- |
| `PSAR_0.02_0.02_0.2` |
| `PSARd_0.02_0.02_0.2` |
| `PSARl_0.02_0.02_0.2` |
| `PSARs_0.02_0.02_0.2` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.parabolic_sar(df['high'], df['low']).tail(3)
```

```text
            PSAR_0.02_0.02_0.2  PSARd_0.02_0.02_0.2  PSARl_0.02_0.02_0.2  PSARs_0.02_0.02_0.2
date                                                                                         
2024-10-25           92.226216                 -1.0                  NaN            92.226216
2024-10-26           92.028251                 -1.0                  NaN            92.028251
2024-10-27           91.842164                 -1.0                  NaN            91.842164
```

**Accessor form:** `df.zta.parabolic_sar(...)`

## How to read it

Most traders use it exactly as its name suggests: a stop that trails price and flips sides ("stop and reverse") the moment price crosses it. `PSARd` gives the regime directly (`1.0` long-biased, `-1.0` short-biased); `PSARl`/`PSARs` are the dots pre-split for two-colour plotting, matching [supertrend](supertrend.md)'s convention.

## Pitfalls

The accelerating AF is a double-edged sword: it rides a strong trend tightly, but it also means SAR gives back less and less room the longer a trend runs, so a normal pullback late in a trend can trigger a reversal that a wider stop would have survived. Like [supertrend](supertrend.md), it whipsaws repeatedly in a range and carries no opinion about trend strength — pair it with a filter such as [adx](adx.md).

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/parabolic-sar](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/parabolic-sar)
