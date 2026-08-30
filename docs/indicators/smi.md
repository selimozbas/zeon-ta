---
title: Stochastic Momentum Index (SMI)
---

[← All indicators](../index.md)

`zeonta.smi()` — Double-smoothed stochastic that measures distance from the range's midpoint.

## What it measures

William Blau's refinement of [stoch](stoch.md): instead of measuring where the close sits *within* the high-low range (0 to 100), it measures the close's distance from the range's *midpoint*, then double-smooths both that distance and the range itself with two EMA passes before dividing.

## Formula

```text
Mid = (HH+LL)/2; SMI = 200 * EMA(EMA(Close-Mid,fast),slow) / EMA(EMA(HH-LL,fast),slow)
```

## Parameters

**Required inputs:** `high`, `low`, `close`

| Parameter | Default |
| --- | --- |
| `length` | `10` |
| `fast` | `3` |
| `slow` | `3` |
| `signal_length` | `3` |

## Returns

| Column |
| --- |
| `SMI_10_3_3` |
| `SMIs_10_3_3` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.smi(df['high'], df['low'], df['close']).tail(3)
```

```text
            SMI_10_3_3  SMIs_10_3_3
date                               
2024-10-25  -37.061631   -38.831674
2024-10-26  -49.537086   -44.184380
2024-10-27  -60.390672   -52.287526
```

**Accessor form:** `df.zta.smi(...)`

## How to read it

Same overbought/oversold intuition as an ordinary stochastic (readings above +40 / below -40 are commonly cited), but because both the numerator and denominator are double-smoothed, SMI reaches its -100/+100 bounds far less abruptly than %K does.

## Pitfalls

Three separate smoothing periods (`length` for the range, `fast` and `slow` for the two EMA passes) stack together, so the effective lag is longer than any one of them alone suggests.

## Reference

Formula source: [https://www.tradingview.com/support/solutions/43000589925-stochastic-momentum-index/](https://www.tradingview.com/support/solutions/43000589925-stochastic-momentum-index/)
