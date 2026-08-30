# Relative Vigor Index (RVGI)

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/rvgi.md)

`zeonta.rvgi()` — Symmetrically weighted ratio of body strength to range: a smoother BOP.

## What it measures

The same idea [bop](bop.md) measures raw — closing strength relative to the bar's own range — smoothed two ways at once: a 4-bar symmetric weighting on both the body and the range before an SMA of each, plus the same weighting again for its own signal line.

## Formula

```text
Body/Range each symmetrically weighted over 4 bars (1-2-2-1), then RVGI = SMA(Body, n) / SMA(Range, n)
```

## Parameters

**Required inputs:** `open`, `high`, `low`, `close`

| Parameter | Default |
| --- | --- |
| `length` | `10` |

## Returns

| Column |
| --- |
| `RVGI_10` |
| `RVGIs_10` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.rvgi(df['open'], df['high'], df['low'], df['close']).tail(3)
```

```text
             RVGI_10  RVGIs_10
date                          
2024-10-25 -0.069802 -0.082001
2024-10-26 -0.113195 -0.082534
2024-10-27 -0.181959 -0.103652
```

**Accessor form:** `df.zta.rvgi(...)`

## How to read it

The crossover between RVGI and its own signal line is the standard read — a smoother, less choppy version of watching raw BOP cross its own zero line.

## Pitfalls

Zero-range or zero-body bars are not specially guarded beyond the SMA smoothing itself — a long stretch of identical open/close or high/low bars can still produce an undefined `0/0` ratio, surfacing as `NaN`.

## Reference

Formula source: [https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/relative-vigor-index](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/relative-vigor-index)
