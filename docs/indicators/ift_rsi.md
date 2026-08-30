---
title: Inverse Fisher Transform of RSI
---

[← All indicators](../index.md)

`zeonta.ift_rsi()` — RSI compressed toward -1/+1 through Ehlers' Inverse Fisher Transform.

## What it measures

Rescales [rsi](rsi.md) toward zero, smooths it, and squashes the result through Ehlers' Inverse Fisher Transform — a curve that passes the middle of its input through almost unchanged but compresses everything else hard toward -1 or +1, trading RSI's gentle 0-100 curve for a near-binary reading.

## Formula

```text
v1 = 0.1*(RSI-50); v2 = WMA(v1, smooth); IFTRSI = (exp(2*v2)-1)/(exp(2*v2)+1)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `14` |
| `smooth` | `9` |

## Returns

| Column |
| --- |
| `IFTRSI_14_9` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.ift_rsi(df['close']).tail(3)
```

```text
date
2024-10-25   -0.616901
2024-10-26   -0.687237
2024-10-27   -0.764766
Name: IFTRSI_14_9, dtype: float64
```

**Accessor form:** `df.zta.ift_rsi(...)`

## How to read it

Readings pin close to -1 or +1 far more often than RSI pins near 0 or 100 — that compression is the entire point, giving very clear (if less nuanced) turning-point signals.

## Pitfalls

The compression means small, genuine changes in the underlying RSI can vanish once squashed toward an extreme — this trades resolution for clarity, not a free improvement on RSI.

## Reference

Formula source: [https://www.mesasoftware.com/papers/TheInverseFisherTransform.pdf](https://www.mesasoftware.com/papers/TheInverseFisherTransform.pdf)
