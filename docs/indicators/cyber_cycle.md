---
title: Cyber Cycle
---

[← All indicators](../index.md)

`zeonta.cyber_cycle()` — Ehlers' band-limited cycle extraction with a fixed smoothing constant.

## What it measures

A 4-bar weighted smooth of the median price fed into a 2-pole highpass tuned by a fixed smoothing constant rather than a length in bars. Ehlers' own "Adaptive" variant instead measures the market's own dominant cycle period (via a Hilbert Transform discriminator) and feeds that into the constant bar by bar — that measurement stage is the same dominant-cycle apparatus behind MAMA, an indicator this library has already declined, so only the fixed-constant form is implemented here.

## Formula

```text
Smooth = (P+2P[-1]+2P[-2]+P[-3])/6; Cycle = (1-a/2)^2*(Smooth-2Smooth[-1]+Smooth[-2]) + 2(1-a)Cycle[-1] - (1-a)^2Cycle[-2]
```

## Parameters

**Required inputs:** `high`, `low`

| Parameter | Default |
| --- | --- |
| `alpha` | `0.07` |

## Returns

| Column |
| --- |
| `CYBERCYCLE` |
| `CYBERCYCLEt` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.cyber_cycle(df['high'], df['low']).tail(3)
```

```text
            CYBERCYCLE  CYBERCYCLEt
date                               
2024-10-25   -0.118686    -0.538025
2024-10-26   -0.007175    -0.118686
2024-10-27   -0.334161    -0.007175
```

**Accessor form:** `df.zta.cyber_cycle(...)`

## How to read it

Oscillates around zero at the market's own dominant cycle rate; the crossover between `CYBERCYCLE` and its own one-bar-delayed trigger line is the standard read, the same pattern [fisher_transform](fisher_transform.md) uses.

## Pitfalls

A fixed smoothing constant means the filter is tuned for one cycle length — it will lag or overreact if the market's actual dominant cycle drifts far from what `alpha=0.07` implicitly assumes.

## Reference

Formula source: [https://help.ctrader.com/indicators/built-in/oscillators/cyber-cycle/](https://help.ctrader.com/indicators/built-in/oscillators/cyber-cycle/)
