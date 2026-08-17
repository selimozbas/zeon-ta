# Divergences

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/divergence.md)

`zeonta.divergence()` — Regular and hidden divergences between price swings and an oscillator.

## What it measures

When price makes a new extreme but the oscillator does not, the move is being made with less force than the one before it. That disagreement — divergence — is one of the few genuinely forward-looking things in technical analysis.

## Formula

```text
Regular Bearish = price Higher High + oscillator Lower High; Regular Bullish = price Lower Low + oscillator Higher Low; Hidden Bearish = price Lower High + oscillator Higher High; Hidden Bullish = price Higher Low + oscillator Lower Low
```

## Parameters

**Required inputs:** `high`, `low`, `close`

| Parameter | Default |
| --- | --- |
| `oscillator` | `None` |
| `osc_length` | `14` |
| `left` | `5` |
| `right` | `5` |

## Returns

| Column |
| --- |
| `DIVREGBULL_5_5` |
| `DIVREGBEAR_5_5` |
| `DIVHIDBULL_5_5` |
| `DIVHIDBEAR_5_5` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.divergence(df['high'], df['low'], df['close'], left=5, right=5).sum()
```

```text
DIVREGBULL_5_5    2.0
DIVREGBEAR_5_5    3.0
DIVHIDBULL_5_5    0.0
DIVHIDBEAR_5_5    4.0
dtype: float64
```

**Accessor form:** `df.zta.divergence(...)`

## How to read it

Regular divergence argues the trend is tiring and a reversal is closer. Hidden divergence argues the opposite: a pullback inside a trend is ending and the trend is about to resume. The default oscillator is RSI(14); pass any series via `oscillator`.

## Pitfalls

A divergence is a warning, not a signal — in a strong trend an oscillator can diverge three or four times while price keeps going, and each one looks convincing in hindsight. Wait for price confirmation. Note too that flags land on the pivot bar, which is only knowable `right` bars later: shift the output before backtesting.
