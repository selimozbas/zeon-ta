# KDJ

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/kdj.md)

`zeonta.kdj()` — Stochastic %K/%D reworked with Wilder smoothing, plus a fast, overshooting J line.

## What it measures

A stochastic variant popular in Chinese-market technical analysis. Starts from the same Raw Stochastic Value [stoch](stoch.md) calls `%K` before smoothing, then smooths it twice with Wilder's recursion (the same one [smma](smma.md) exposes) rather than a plain SMA. `J` extrapolates past the `K`/`D` move rather than averaging it, so it swings outside the usual 0-100 range — the point of it is to flag overbought/oversold conditions *before* `K` and `D` reach their own extremes.

## Formula

```text
RSV = 100*(Close-LL)/(HH-LL); K = Wilder(RSV, signal); D = Wilder(K, signal); J = 3*K - 2*D
```

## Parameters

**Required inputs:** `high`, `low`, `close`

| Parameter | Default |
| --- | --- |
| `length` | `9` |
| `signal` | `3` |

## Returns

| Column |
| --- |
| `K_9_3` |
| `D_9_3` |
| `J_9_3` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.kdj(df['high'], df['low'], df['close']).tail(3)
```

```text
                K_9_3      D_9_3      J_9_3
date                                       
2024-10-25  32.635164  33.577094  30.751304
2024-10-26  23.761553  30.305247  10.674166
2024-10-27  19.677575  26.762690   5.507346
```

**Accessor form:** `df.zta.kdj(...)`

## How to read it

Read like `stoch`: crossovers between `K` and `D` signal momentum shifts, with `J` leading both — a `J` reading well above 100 or below 0 is the earliest warning of an extreme.

## Pitfalls

`J` is unbounded by design — do not clamp it to 0-100 the way `K`/`D` naturally are.

## Reference

Formula source: [https://www.tradingview.com/scripts/kdj/](https://www.tradingview.com/scripts/kdj/)
