---
title: Super Smoother Filter (Ehlers)
---

[← All indicators](../index.md)

`zeonta.super_smoother()` — Ehlers' 2-pole low-pass filter: less lag than an EMA of the same critical period.

## What it measures

A 2-pole digital low-pass filter, drawn from Ehlers' background in aerospace analog filter design rather than the classic finance literature: it removes the high-frequency jitter an ordinary moving average lets straight through, with meaningfully less lag than an EMA of the same critical period. Where `t3` cuts lag by cascading DEMA-style corrections, this cuts it by an entirely different route — genuine digital signal processing filter design.

## Formula

```text
a1 = exp(-1.414 x pi / n); b1 = 2 x a1 x cos(1.414 x pi / n); c2 = b1; c3 = -a1^2; c1 = 1 - c2 - c3; SSF = c1 x (Close + Close[t-1]) / 2 + c2 x SSF[t-1] + c3 x SSF[t-2]
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `20` |

## Returns

| Column |
| --- |
| `SSF_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.super_smoother(df['close']).tail(3)
```

```text
date
2024-10-25    90.403862
2024-10-26    90.276889
2024-10-27    90.078809
Name: SSF_20, dtype: float64
```

**Accessor form:** `df.zta.super_smoother(...)`

## How to read it

Read it exactly like any other moving average — trend direction, dynamic support and resistance, a baseline for a crossover system — but expect it to hug price noticeably more tightly, with less of the whipsaw jitter a plain `sma`/`ema` of the same length would show on choppy data.

## Pitfalls

``cos()``'s argument must be in radians; at least one popular open-source reference implementation keeps Ehlers' original EasyLanguage constant (``180``, meant for a degrees-based ``Cos()``) unconverted when porting to a radians-based language, which silently produces a different (wrong) filter — confirmed by inspecting that implementation's own source directly. This implementation uses the radians-consistent form throughout.

## Reference

Formula source: [https://www.mesasoftware.com/papers/EhlersSuperSmoother.pdf](https://www.mesasoftware.com/papers/EhlersSuperSmoother.pdf)
