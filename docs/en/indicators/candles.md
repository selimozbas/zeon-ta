# Candlestick Anatomy and Patterns

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/candles.md)

`zeonta.candles()` — Candle body/wick geometry plus doji, engulfing and hammer detection.

## What it measures

A candle compresses four numbers into one shape: where trading opened and closed (the body) and how far it strayed in between (the wicks). This function returns that geometry as plain columns, plus flags for the three patterns that show up most: the doji, the engulfing pair and the hammer/shooting-star.

## Formula

```text
Body = |Close - Open|; bullish candle when Close > Open, bearish when Close < Open; Upper wick = High - max(Open, Close); Lower wick = min(Open, Close) - Low.
```

## Parameters

**Required inputs:** `open`, `high`, `low`, `close`

| Parameter | Default |
| --- | --- |
| `doji_threshold` | `0.1` |
| `hammer_ratio` | `2.0` |

## Returns

| Column |
| --- |
| `CDLBODY` |
| `CDLUPPER` |
| `CDLLOWER` |
| `CDLRANGE` |
| `CDLDIR` |
| `CDLDOJI` |
| `CDLENG` |
| `CDLHAM` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.candles(df['open'], df['high'], df['low'], df['close'])[['CDLBODY', 'CDLDIR', 'CDLDOJI', 'CDLENG']].tail(3)
```

```text
            CDLBODY  CDLDIR  CDLDOJI  CDLENG
date                                        
2024-10-25   0.3995    -1.0      0.0     0.0
2024-10-26   1.0998    -1.0      0.0     0.0
2024-10-27   0.7475    -1.0      0.0     0.0
```

**Accessor form:** `df.zta.candles(...)`

## How to read it

A long body means one side dominated the whole session; a long wick means a level was tested and rejected. `CDLDIR` gives direction, `CDLDOJI` marks indecision, `CDLENG` flags a reversal pair (+1 bullish, -1 bearish) and `CDLHAM` flags a rejection candle (+1 hammer, -1 shooting star).

## Pitfalls

A pattern is a description of one or two bars, not a signal. A hammer in the middle of a range means nothing; the same hammer at a level that has already been tested twice is what traders act on. Always read patterns together with location.

## Reference

Formula source: [https://ta.cognicode.org/learn/candlesticks](https://ta.cognicode.org/learn/candlesticks)
