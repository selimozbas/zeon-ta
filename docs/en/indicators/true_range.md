# True Range

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/true_range.md)

`zeonta.true_range()` — Per-bar range including gaps: max(H-L, |H-prevC|, |L-prevC|).

## What it measures

The raw, unsmoothed bar range that ATR averages. Exposed on its own because building custom volatility logic almost always starts here rather than with a smoothed ATR.

## Formula

```text
TR = max(High - Low, |High - PrevClose|, |Low - PrevClose|)
```

## Parameters

**Required inputs:** `high`, `low`, `close`

_None._

## Returns

| Column |
| --- |
| `TRUERANGE` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.true_range(df['high'], df['low'], df['close']).tail(3)
```

```text
date
2024-10-25    1.0623
2024-10-26    1.1458
2024-10-27    1.5671
Name: TRUERANGE, dtype: float64
```

**Accessor form:** `df.zta.true_range(...)`

## How to read it

Each value is that single bar's full extent including any gap from the previous close. Spikes mark the individual bars where something happened.

## Pitfalls

The first bar has no previous close, so it falls back to `High - Low` rather than being `NaN`. That single value is slightly understated by construction.

## Reference

Formula source: [https://ta.cognicode.org/learn/atr](https://ta.cognicode.org/learn/atr)
