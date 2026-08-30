---
title: Permutation Entropy
---

[← All indicators](../index.md)

`zeonta.permutation_entropy()` — Shannon entropy of a window's own ordinal (up/down) patterns, ignoring move size.

## What it measures

Reduces every overlapping slice of a rolling window to the *ordering* of its values — which of the possible orderings it matches, never their actual size — then takes the Shannon entropy of how often each ordering occurred. A different way of asking `sample_entropy`'s question, from shape rather than distance.

## Formula

```text
PERMEN = -sum(p_i * ln(p_i)) over each observed ordinal pattern i
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `window` | `100` |
| `order` | `3` |
| `delay` | `1` |

## Returns

| Column |
| --- |
| `PERMEN_100_3_1` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.permutation_entropy(df['close'], window=100, order=3).tail(3)
```

```text
date
2024-10-25    1.737093
2024-10-26    1.730196
2024-10-27    1.722218
Name: PERMEN_100_3_1, dtype: float64
```

**Accessor form:** `df.zta.permutation_entropy(...)`

## How to read it

A window that keeps repeating the same up/down shape has low permutation entropy; one with no preferred shape approaches `ln(order!)`, the maximum for that `order`.

## Pitfalls

Reported in nats (natural-log units), not the normalized 0-1 form some other software reports — divide by `ln(order!)` to get that. Ties within a window are broken by position, the conventional Bandt-Pompe rule, not treated as an error.

## Reference

Formula source: [https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.88.174102](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.88.174102)
