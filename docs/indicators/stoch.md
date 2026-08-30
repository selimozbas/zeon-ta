---
title: Stochastic Oscillator
---

[← All indicators](../index.md)

`zeonta.stoch()` — Where the close sits inside the recent high-low range.

## What it measures

Where did this bar close inside its recent range — at the top, the bottom, or the middle? That is the entire idea. Closing near the highs of the last n bars scores near 100; closing near the lows scores near 0.

## Formula

```text
%K = 100 x (Close - LowestLow(n)) / (HighestHigh(n) - LowestLow(n)); %K(smoothed) = SMA(%K, smoothK); %D = SMA(%K smoothed, smoothD)
```

## Parameters

**Required inputs:** `high`, `low`, `close`

| Parameter | Default |
| --- | --- |
| `length` | `14` |
| `smooth_k` | `3` |
| `smooth_d` | `3` |

## Returns

| Column |
| --- |
| `STOCHk_14_3_3` |
| `STOCHd_14_3_3` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.stoch(df['high'], df['low'], df['close']).tail(3)
```

```text
            STOCHk_14_3_3  STOCHd_14_3_3
date                                    
2024-10-25      37.289365      31.251025
2024-10-26      24.223173      31.328924
2024-10-27      14.007530      25.173356
```

**Accessor form:** `df.zta.stoch(...)`

## How to read it

Above 80 means closes are clustering at the top of the range, below 20 at the bottom. The `%D` line is the smoothed signal; `%K` crossing above `%D` from a low reading is the classic long trigger.

## Pitfalls

The stochastic is built for ranges, and in a trend it saturates: it pins near 100 for the whole of a strong advance, generating a stream of premature sell signals. Filter it with a trend measure such as ADX before acting on extremes.
