# Laguerre RSI

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/laguerre_rsi.md)

`zeonta.laguerre_rsi()` — RSI computed over a 4-stage Laguerre filter instead of Wilder smoothing.

## What it measures

John Ehlers' fast-acting alternative to [rsi](rsi.md): rather than a full look-back window smoothed by Wilder's recursion, this runs price through a 4-stage all-pass filter cascade (a 'time warp' that delays low-frequency components more than high-frequency ones) and reads momentum from the relationships between the four stages.

## Formula

```text
4-stage Laguerre filter (L0..L3) replaces Wilder smoothing; CU/CD from stage-to-stage differences; LRSI = CU/(CU+CD)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `gamma` | `0.5` |

## Returns

| Column |
| --- |
| `LRSI_0.5` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.laguerre_rsi(df['close']).tail(3)
```

```text
date
2024-10-25    0.000000
2024-10-26    0.182379
2024-10-27    0.002458
Name: LRSI_0.5, dtype: float64
```

**Accessor form:** `df.zta.laguerre_rsi(...)`

## How to read it

Same 0-1 scale and overbought/oversold intuition as RSI (Ehlers' own example uses 20%/80% levels), but known for reacting much faster and often pinning near the extremes rather than drifting through the middle.

## Pitfalls

The filter starts from a zero initial state, so the first several bars are a warm-up transient rather than a meaningful reading — there is no fixed warm-up length the way a windowed indicator has, since the filter's own memory never fully clears, just fades.

## Reference

Formula source: [https://www.mesasoftware.com/papers/TimeWarp.pdf](https://www.mesasoftware.com/papers/TimeWarp.pdf)
