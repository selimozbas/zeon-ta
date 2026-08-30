# Normalized Average True Range (NATR)

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/natr.md)

`zeonta.natr()` — ATR expressed as a percentage of price, so different symbols become comparable.

## What it measures

[atr](atr.md) reports a raw price amount — a $2 ATR is huge for a $10 stock and tiny for a $2,000 one. NATR expresses the same measurement as a percentage of price instead, so different symbols (or the same symbol at very different price levels over time) become directly comparable.

## Formula

```text
NATR = ATR(n) / Close * 100
```

## Parameters

**Required inputs:** `high`, `low`, `close`

| Parameter | Default |
| --- | --- |
| `length` | `14` |

## Returns

| Column |
| --- |
| `NATR_14` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.natr(df['high'], df['low'], df['close']).tail(3)
```

```text
date
2024-10-25    1.330037
2024-10-26    1.340412
2024-10-27    1.380133
Name: NATR_14, dtype: float64
```

**Accessor form:** `df.zta.natr(...)`

## How to read it

Read the same way as ATR — rising means volatility is increasing — but compare its *level* across symbols or across a long price history the way you never would with raw ATR.

## Pitfalls

`NaN` when `Close` is exactly `0`, rather than an undefined division.

## Reference

Formula source: [https://www.tradingview.com/support/solutions/43000501823-average-true-range-natr/](https://www.tradingview.com/support/solutions/43000501823-average-true-range-natr/)
