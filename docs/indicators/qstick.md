---
title: Qstick
---

[← All indicators](../index.md)

`zeonta.qstick()` — SMA of each bar's own Close-minus-Open body, a simple candle-bias gauge.

## What it measures

Tushar Chande's simplest indicator: a moving average of each bar's own body (Close minus Open). Distinct from [bop](bop.md), which normalises the same close-minus-open difference by the bar's own high-low range instead of smoothing it directly.

## Formula

```text
QS = SMA(Close - Open, length)
```

## Parameters

**Required inputs:** `open`, `close`

| Parameter | Default |
| --- | --- |
| `length` | `10` |

## Returns

| Column |
| --- |
| `QS_10` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.qstick(df['open'], df['close']).tail(3)
```

```text
date
2024-10-25   -0.24931
2024-10-26   -0.32247
2024-10-27   -0.32389
Name: QS_10, dtype: float64
```

**Accessor form:** `df.zta.qstick(...)`

## How to read it

Positive means closes have consistently landed above opens over the window (bullish body bias); negative the mirror. A cross of Qstick's own zero line is the standard read.

## Pitfalls

No special edge cases — a plain SMA of a simple bar-body difference.

## Reference

Formula source: [https://corporatefinanceinstitute.com/resources/knowledge/trading-investing/qstick-indicator/](https://corporatefinanceinstitute.com/resources/knowledge/trading-investing/qstick-indicator/)
