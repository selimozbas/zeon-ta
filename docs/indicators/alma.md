---
title: Arnaud Legoux Moving Average (ALMA)
---

[← All indicators](../index.md)

`zeonta.alma()` — Gaussian-weighted moving average tuned by an offset (lag vs. smoothness) and sigma.

## What it measures

Where [wma](wma.md) weights the window linearly and [ema](ema.md) weights it exponentially, ALMA weights it with a Gaussian bell curve whose peak position (`offset`) and width (`sigma`) are both separately tunable — two independent knobs for the same lag-versus-smoothness tradeoff every moving average makes.

## Formula

```text
m = floor(offset*(n-1)); s = n/sigma; w[j] = exp(-(j-m)^2/(2*s^2)) for j=0..n-1; ALMA = sum(w[j] * Close[t-n+1+j]) / sum(w[j])
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `9` |
| `offset` | `0.85` |
| `sigma` | `6.0` |

## Returns

| Column |
| --- |
| `ALMA_9_0.85_6.0` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.alma(df['close']).tail(3)
```

```text
date
2024-10-25    90.160843
2024-10-26    90.147718
2024-10-27    89.829007
Name: ALMA_9_0.85_6.0, dtype: float64
```

**Accessor form:** `df.zta.alma(...)`

## How to read it

Read the same way as any moving average. `offset` near `1` behaves more like a responsive EMA; `offset` near `0` behaves more like a smooth, centered average — `0.85` is a starting point tuned toward responsiveness, not a midpoint.

## Pitfalls

Two extra parameters beyond `length` (`offset`, `sigma`) that meaningfully change the result — treat the defaults as Legoux's own starting point, not universal constants, the same caveat this library gives Ehlers' own tunable filters.

## Reference

Formula source: [https://www.tradingview.com/support/solutions/43000594683-arnaud-legoux-moving-average/](https://www.tradingview.com/support/solutions/43000594683-arnaud-legoux-moving-average/)
