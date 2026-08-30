# Quantitative Qualitative Estimation (QQE)

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/qqe.md)

`zeonta.qqe()` — A smoothed RSI with an ATR-style trailing band, flipping like a Supertrend on RSI.

## What it measures

Smooths [rsi](rsi.md) with an EMA, measures that smoothed line's own bar-to-bar volatility (Wilder-smoothed twice), and uses it to build a trailing band around the smoothed RSI — the same one-way-ratchet, flip-on-cross construction [supertrend](supertrend.md) uses on price, applied to RSI instead. QQE has no single academic paper behind it — it originates as a MetaTrader community indicator — but its construction is precise and cross-confirmed identically across multiple independent implementations, unlike indicators this library has declined for lacking exactly that.

## Formula

```text
RsiMa = EMA(RSI, smooth); DeltaFastAtrRsi = EMA(EMA(|ΔRsiMa|, 2n-1), 2n-1)*factor; trailing band flips like a Supertrend built on RsiMa
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `length` | `14` |
| `smooth` | `5` |
| `factor` | `4.236` |

## Returns

| Column |
| --- |
| `QQE_14_5_4.236` |
| `QQEl_14_5_4.236` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.qqe(df['close']).tail(3)
```

```text
            QQE_14_5_4.236  QQEl_14_5_4.236
date                                       
2024-10-25       43.655912        46.597895
2024-10-26       41.498870        46.597895
2024-10-27       38.946936        45.623334
```

**Accessor form:** `df.zta.qqe(...)`

## How to read it

The trailing line's own value is bullish support while price/RSI stays above it, and resistance while below — read the crossover between the smoothed RSI and the trailing line the way you would `supertrend`'s flips, or watch the smoothed RSI cross its own 50 midline.

## Pitfalls

Needs a long warm-up — the double-smoothed volatility term alone needs roughly `2*(2*length-1)` bars on top of RSI's own warm-up before it produces a value.

## Reference

Formula source: [https://www.prorealcode.com/prorealtime-indicators/qqe-indicator-quantitative-qualitative-estimation/](https://www.prorealcode.com/prorealtime-indicators/qqe-indicator-quantitative-qualitative-estimation/)
