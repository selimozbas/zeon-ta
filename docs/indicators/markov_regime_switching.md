---
title: Markov Regime-Switching Probability
---

[← All indicators](../index.md)

`zeonta.markov_regime_switching()` — Filtered probability the current bar is in a Hamilton 2-state high-volatility regime.

## What it measures

Hamilton's 1989 Markov-switching model treats a series as alternating between a small number of hidden 'regimes', each with its own statistical behaviour, and estimates both the regimes' parameters and which one is currently active at the same time. This implementation uses 2 states on log returns, distinguished purely by variance, so the output reads as a real-time estimate of 'is the market in its high- or low-volatility regime right now'. It is the only indicator in this library that fits an iterative statistical model (Expectation-Maximization) rather than evaluating a formula directly — every bar re-fits the model from scratch on its own trailing window, using nothing past that bar, so the output stays aligned and look-ahead free the same way every other indicator here is.

## Formula

```text
On each rolling window of log returns: fit y_t = mu_{S_t} + eps_t, eps_t ~ N(0, sigma_{S_t}^2), S_t in {0,1} a first-order Markov chain, by EM (Hamilton filter forward + Kim smoother backward per E-step; closed-form mu/sigma^2/transition updates per M-step); report the filtered probability P(S_t=high-variance | Y_1..t) for the window's last bar
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `window` | `100` |
| `max_iterations` | `50` |
| `tolerance` | `1e-06` |

## Returns

| Column |
| --- |
| `MRSW_100_50_1e-06` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.markov_regime_switching(df['close']).tail(3)
```

```text
date
2024-10-25    0.379057
2024-10-26    0.593392
2024-10-27    0.277477
Name: MRSW_100_50_1e-06, dtype: float64
```

**Accessor form:** `df.zta.markov_regime_switching(...)`

## How to read it

Values near 1 mean the model is confident the current bar sits in the higher-variance of its two fitted regimes; values near 0 mean the lower-variance one. Traders use this as a regime filter the way `hurst_exponent` is used for trend/mean-reversion character: lean on breakout/momentum tooling when this is high (volatility expansion), lean on mean-reversion/range tooling when it is low. A rising value crossing through the middle of its range can flag the *start* of a volatility regime change before a fixed-window realized-volatility measure would clearly show it.

## Pitfalls

EM is not guaranteed to converge to the globally best fit — it can settle into different local optima depending on where it starts, which is why this implementation always seeds every window the same deterministic way (splitting the window's own returns at their median, self-transition probabilities seeded at 0.9) rather than randomly; that makes the output reproducible run to run, but does not make any one window's fit the unique correct answer — on a window with no real regime structure (constant volatility throughout), the 2-state fit can still find an arbitrary, unstable split of ordinary noise into two 'regimes'. `max_iterations` is a runtime safety valve, not a convergence guarantee: a window that has not converged when the cap is hit still reports its last iterate's estimate rather than `NaN`. And by far the most expensive indicator in this library — see its own docstring for the actual complexity — every bar re-runs up to `max_iterations` full forward/backward passes over its own window; `BENCHMARKS.md` does not cover it.

## Reference

Formula source: [https://www.jstor.org/stable/1912559](https://www.jstor.org/stable/1912559)
