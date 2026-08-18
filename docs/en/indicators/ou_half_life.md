# Ornstein-Uhlenbeck Half-Life of Mean Reversion

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/ou_half_life.md)

`zeonta.ou_half_life()` — Ornstein-Uhlenbeck half-life: bars until a mean-reverting series closes half its gap.

## What it measures

The Ornstein-Uhlenbeck process is the standard continuous-time model for a mean-reverting series in quantitative finance; fitting it to price and converting the fitted mean-reversion speed into a half-life — how many bars until the gap between price and its own implied long-run level closes by half — is a widely used way to pick a *lookback length* for a mean-reversion strategy, rather than a signal read on its own. Unlike hurst_exponent, which asks whether a series is persistent or anti-persistent in general, this asks a narrower, more actionable question of a series already assumed to mean-revert: how fast.

## Formula

```text
Regress Close[t]-Close[t-1] against Close[t-1] over a rolling window (OLS); lambda = fitted slope; OUHL = -ln(2)/lambda if lambda < 0, else NaN
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `window` | `100` |

## Returns

| Column |
| --- |
| `OUHL_100` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.ou_half_life(df['close']).tail(3)
```

```text
date
2024-10-25    11.424672
2024-10-26    16.224036
2024-10-27    25.045121
Name: OUHL_100, dtype: float64
```

**Accessor form:** `df.zta.ou_half_life(...)`

## How to read it

A short half-life (a handful of bars) means reversion happens fast — a mean-reversion entry can expect to be closed out soon. A long half-life means reversion is slow, if it is even reliably happening at all; `NaN` means the fitted `lambda` was >= 0 over that window — no mean reversion was detected there, so the whole premise of a mean-reversion trade does not currently hold. Traders commonly use the half-life value itself as the lookback/holding-period parameter for another indicator or strategy, rather than trading on it directly.

## Pitfalls

The fit assumes the series' mean-reversion behaviour is roughly stable over the whole rolling window — a regime change partway through the window (the series stops or starts mean-reverting) biases the estimate toward whichever behaviour dominates the window, not a clean split. And like `hurst_exponent`, this is one specific, standard estimation method (OLS on the discretised process), not the only one in the literature.

## Reference

Formula source: [https://en.wikipedia.org/wiki/Ornstein%E2%80%93Uhlenbeck_process](https://en.wikipedia.org/wiki/Ornstein%E2%80%93Uhlenbeck_process)
