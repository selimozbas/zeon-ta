---
title: Realized Semivariance
---

[← All indicators](../index.md)

`zeonta.realized_semivariance()` — Realized variance split into its positive- and negative-return halves.

## What it measures

Barndorff-Nielsen, Kinnebrock & Shephard (2010) split realized variance — the sum of squared log returns over a window — into the part driven by up-moves and the part driven by down-moves. Ordinary realized variance cannot tell a volatile rally apart from a volatile selloff; the paper shows the downside half on its own carries real predictive power for future volatility that the symmetric total dilutes.

## Formula

```text
RS+ = sum(r^2 : r > 0) over the window; RS- = sum(r^2 : r <= 0) over the window; RS+ + RS- = realized variance
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `20` |

## Returns

| Column |
| --- |
| `RSPOS_20` |
| `RSNEG_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.realized_semivariance(df['close']).tail(3)
```

```text
            RSPOS_20  RSNEG_20
date                          
2024-10-25  0.000509  0.000358
2024-10-26  0.000504  0.000477
2024-10-27  0.000499  0.000528
```

**Accessor form:** `df.zta.realized_semivariance(...)`

## How to read it

RSPOS and RSNEG always sum to the same window's realized variance (sum of squared log returns) exactly — a useful sanity check on the two columns together. A window with RSNEG well above RSPOS reflects a period whose volatility was concentrated in down-moves, and vice versa.

## Pitfalls

length counts log returns, not close bars, so one extra close bar is needed beyond length to produce a value — the same convention bipower_variation uses. A bar with a non-positive close (making its log return NaN) poisons only the windows still containing it, the same self-recovering behaviour every rolling-window indicator in this library has.

## Reference

Formula source: [https://doi.org/10.1093/acprof:oso/9780199549498.003.0007](https://doi.org/10.1093/acprof:oso/9780199549498.003.0007)
