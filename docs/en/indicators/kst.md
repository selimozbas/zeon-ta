# Pring's Know Sure Thing (KST)

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/kst.md)

`zeonta.kst()` — Four weighted-and-smoothed ROC cycles combined into one long-cycle momentum line.

## What it measures

Martin Pring combines four separately smoothed [roc](roc.md) cycles into one line, weighting the longer cycles more heavily on the theory that they capture significant momentum shifts better than short-term noise does.

## Formula

```text
KST = 1*SMA(ROC(roc1),sma1) + 2*SMA(ROC(roc2),sma2) + 3*SMA(ROC(roc3),sma3) + 4*SMA(ROC(roc4),sma4)
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `roc1` | `10` |
| `roc2` | `15` |
| `roc3` | `20` |
| `roc4` | `30` |
| `sma1` | `10` |
| `sma2` | `10` |
| `sma3` | `10` |
| `sma4` | `15` |
| `signal` | `9` |

## Returns

| Column |
| --- |
| `KST_10_15_20_30` |
| `KSTs_10_15_20_30` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.kst(df['close']).tail(3)
```

```text
            KST_10_15_20_30  KSTs_10_15_20_30
date                                         
2024-10-25       -10.961943        -10.673602
2024-10-26       -12.683430        -10.766873
2024-10-27       -14.701257        -11.235720
```

**Accessor form:** `df.zta.kst(...)`

## How to read it

Read like [macd](macd.md): the crossover between KST and its own signal line, or KST crossing its own zero line, are the two standard reads.

## Pitfalls

Nine parameters in total (four ROC lengths, four matching SMA lengths, one signal length) — Pring's own daily-chart defaults are widely used as-is rather than tuned per symbol.

## Reference

Formula source: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/prings-know-sure-thing-kst](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/prings-know-sure-thing-kst)
