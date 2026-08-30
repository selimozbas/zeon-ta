# Chande Momentum Oscillator (CMO)

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/cmo.md)

`zeonta.cmo()` — Sum of gains vs. losses over a plain window, unlike RSI's Wilder smoothing.

## What it measures

Built from the same up-move/down-move split as [rsi](rsi.md), but combined differently (a normalised difference rather than a ratio) and, unlike RSI, never smoothed — a gain or loss drops out of the window completely once it ages past `length` bars rather than fading gradually the way Wilder smoothing does.

## Formula

```text
CMO = 100 * (SumUp(n) - SumDown(n)) / (SumUp(n) + SumDown(n))
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `14` |

## Returns

| Column |
| --- |
| `CMO_14` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.cmo(df['close']).tail(3)
```

```text
date
2024-10-25   -15.862131
2024-10-26   -25.918211
2024-10-27   -32.165313
Name: CMO_14, dtype: float64
```

**Accessor form:** `df.zta.cmo(...)`

## How to read it

Reads on the same -100/+100 scale and the same overbought/oversold intuition as other bounded oscillators, but because it is never smoothed it reacts more abruptly than RSI to an old extreme move finally aging out of the window.

## Pitfalls

`0` on a perfectly flat window (both sums are `0`), not an undefined `0/0`.

## Reference

Formula source: [https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/cmo](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/cmo)
