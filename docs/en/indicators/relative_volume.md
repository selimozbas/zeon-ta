# Volume Basics

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/relative_volume.md)

`zeonta.relative_volume()` — Volume moving average and relative volume (today versus normal).

## What it measures

Raw volume is close to meaningless on its own — a million shares is enormous for one ticker and a rounding error for another. Dividing by the recent average turns it into a number that means the same thing everywhere: how busy is this bar compared to normal?

## Formula

```text
Volume MA(n) = (1/n) x sum(Volume[i]) for the last n bars (a simple moving average applied to volume instead of price). Relative volume = current bar's Volume / Volume MA(n).
```

## Parameters

**Required inputs:** `volume`

| Parameter | Default |
| --- | --- |
| `length` | `20` |

## Returns

| Column |
| --- |
| `VOLMA_20` |
| `RVOL_20` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.relative_volume(df['volume'], length=20).tail(3)
```

```text
             VOLMA_20   RVOL_20
date                           
2024-10-25  514563.25  1.445869
2024-10-26  500691.60  0.739206
2024-10-27  480908.10  0.546788
```

**Accessor form:** `df.zta.relative_volume(...)`

## How to read it

`RVOL` of 1.0 is a perfectly ordinary bar; 2.0 is twice the recent norm. A breakout on high relative volume has participation behind it, while the same breakout on 0.5 is being made by very few people and tends not to hold.

## Pitfalls

Relative volume is distorted around scheduled events — index rebalances, options expiry and earnings all produce huge readings that say nothing about conviction. It also runs high at the open and close of every session, so compare like with like.

## Reference

Formula source: [https://ta.cognicode.org/learn/volume-basics](https://ta.cognicode.org/learn/volume-basics)
