---
title: Percentage Price Oscillator (PPO)
---

[← All indicators](../index.md)

`zeonta.ppo()` — MACD expressed as a percentage, comparable across symbols and price levels.

## What it measures

Exactly `macd`'s construction, divided by the slow EMA to turn an absolute price difference into a percentage. A PPO reading of 5 means the fast EMA sits 5% above the slow one regardless of whether the security trades at $5 or $500 — a comparison `macd`'s own raw output cannot make across symbols.

## Formula

```text
PPO = (EMA(Close, fast) - EMA(Close, slow)) / EMA(Close, slow) x 100; Signal = EMA(PPO, signal); Histogram = PPO - Signal
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `fast` | `12` |
| `slow` | `26` |
| `signal` | `9` |

## Returns

| Column |
| --- |
| `PPO_12_26_9` |
| `PPOs_12_26_9` |
| `PPOh_12_26_9` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.ppo(df['close']).tail(3)
```

```text
            PPO_12_26_9  PPOs_12_26_9  PPOh_12_26_9
date                                               
2024-10-25    -0.419527     -0.376846     -0.042681
2024-10-26    -0.509810     -0.403439     -0.106371
2024-10-27    -0.631409     -0.449033     -0.182376
```

**Accessor form:** `df.zta.ppo(...)`

## How to read it

Read it exactly like `macd`: signal-line crossovers, centerline crossovers and divergences all carry the same meaning, just on a percentage scale that stays comparable when screening across many different symbols.

## Pitfalls

Because it divides by the slow EMA, a security whose price (and therefore whose EMA) crosses through zero makes PPO briefly undefined or wildly scaled — this only matters for spread/synthetic series that can go negative, not for ordinary prices.

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/percentage-price-oscillator-ppo](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/percentage-price-oscillator-ppo)
