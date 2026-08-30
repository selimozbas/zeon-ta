---
title: Vertical Horizontal Filter (VHF)
---

[← All indicators](../index.md)

`zeonta.vertical_horizontal_filter()` — How much of a window's net move survived versus how much back-and-forth it took.

## What it measures

Adam White's version of the same comparison [choppiness_index](choppiness_index.md) makes, built the opposite way round and read the opposite direction: the numerator ('vertical' movement) is the net distance the window's closing range covered; the denominator ('horizontal' movement) is the total bar-by-bar distance it took to get there.

## Formula

```text
VHF = (HighestClose(n) - LowestClose(n)) / Sum(|Close[i] - Close[i-1]|, n)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `28` |

## Returns

| Column |
| --- |
| `VHF_28` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.vertical_horizontal_filter(df['close']).tail(3)
```

```text
date
2024-10-25    0.214621
2024-10-26    0.237501
2024-10-27    0.272314
Name: VHF_28, dtype: float64
```

**Accessor form:** `df.zta.vertical_horizontal_filter(...)`

## How to read it

Higher means more trend (the opposite direction from CHOP, despite the similar construction) — little wasted motion getting from the window's start to its end. Lower means more whipsaw: a lot of bar-by-bar distance covered for little net progress.

## Pitfalls

`NaN` wherever the window's bar-to-bar movement summed to exactly `0` (a perfectly flat window), rather than an undefined division.

## Reference

Formula source: [https://www.rdocumentation.org/packages/TTR/versions/0.24.4/topics/VHF](https://www.rdocumentation.org/packages/TTR/versions/0.24.4/topics/VHF)
