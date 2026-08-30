# McGinley Dynamic

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/mcgd.md)

`zeonta.mcgd()` — A moving average that speeds up in fast markets and slows down in quiet ones.

## What it measures

John McGinley built this specifically to fix a complaint about ordinary moving averages: a fixed-period EMA/SMA lags badly in a fast market and whipsaws in a slow one, because its speed never changes. The `(Close/MD)^4` term makes McGinley Dynamic self-adjusting instead — it speeds up automatically whenever price pulls away from it, and slows back down once price and the average are close again.

## Formula

```text
MD[0] = Close[0]; MD[i] = MD[i-1] + (Close[i] - MD[i-1]) / (N * (Close[i]/MD[i-1])^4), N = length
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `10` |

## Returns

| Column |
| --- |
| `MCGD_10` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.mcgd(df['close']).tail(3)
```

```text
date
2024-10-25    90.661309
2024-10-26    90.496121
2024-10-27    90.275758
Name: MCGD_10, dtype: float64
```

**Accessor form:** `df.zta.mcgd(...)`

## How to read it

Read the same way as any moving average (price crossing it, its own slope) — McGinley's own pitch is that it needs less re-tuning across changing market conditions than a fixed-period EMA/SMA would, not that it reads differently.

## Pitfalls

The `(Close/MD)^4` term is exactly `0` when `Close` is `0`, which would divide by zero in the update step — held at the prior value for that one bar instead, since the formula has no real answer at that singular point.

## Reference

Formula source: [https://www.tradingview.com/support/solutions/43000589175-mcginley-dynamic/](https://www.tradingview.com/support/solutions/43000589175-mcginley-dynamic/)
