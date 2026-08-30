---
title: Momentum
---

[← All indicators](../index.md)

`zeonta.momentum()` — Raw price change over n bars.

## What it measures

The plainest possible momentum reading: how much has price moved, in its own units, over the last n bars? No smoothing, no normalisation — just today's close minus the close from n bars back.

## Formula

```text
Momentum = Close - Close (n periods ago)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `10` |

## Returns

| Column |
| --- |
| `MOM_10` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.momentum(df['close'], length=10).tail(3)
```

```text
date
2024-10-25   -2.2001
2024-10-26   -2.7384
2024-10-27   -2.7623
Name: MOM_10, dtype: float64
```

**Accessor form:** `df.zta.momentum(...)`

## How to read it

Above zero means price is higher than it was n bars ago (rising momentum); below zero means it is lower. The line's own slope — is momentum itself accelerating or fading — is usually more informative than the zero crossing alone.

## Pitfalls

Being expressed in raw price units means a Momentum reading of 2 means nothing without knowing the instrument's price level — never compare it across symbols. Use [roc](roc.md) instead when you need a percentage that is comparable across symbols or over a long history where the price level itself has changed a lot.

## Reference

Formula source: [https://en.wikipedia.org/wiki/Momentum_(technical_analysis)](https://en.wikipedia.org/wiki/Momentum_(technical_analysis))
