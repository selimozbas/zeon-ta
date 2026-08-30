---
title: Approximate Entropy
---

[← All indicators](../index.md)

`zeonta.approximate_entropy()` — How unpredictable a window is — sample_entropy's older, self-match-biased ancestor.

## What it measures

[sample_entropy](sample_entropy.md)'s predecessor, and the whole reason Sample Entropy exists: it counts template matches the same way but counts a template as matching *itself*, which biases every count upward and makes the statistic depend more on window length than Sample Entropy does.

## Formula

```text
ApEn = phi(m) - phi(m+1), phi(k) = mean(ln(C_i^k)) including self-matches
```

## Parameters

**Required inputs:** `close`

| Parameter | Default |
| --- | --- |
| `window` | `100` |
| `m` | `2` |
| `r` | `0.2` |

## Returns

| Column |
| --- |
| `APEN_100_2_0.2` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.approximate_entropy(df['close'], window=100).tail(3)
```

```text
date
2024-10-25    0.536491
2024-10-26    0.536491
2024-10-27    0.522488
Name: APEN_100_2_0.2, dtype: float64
```

**Accessor form:** `df.zta.approximate_entropy(...)`

## How to read it

Read like `sample_entropy` — low means the window keeps repeating short patterns, high means little structure at all. Kept here for the reader who specifically wants Pincus's original statistic; for new work, `sample_entropy` corrects this estimator's two known biases.

## Pitfalls

Same `O(window^2)` per-bar cost as `sample_entropy` — see `BENCHMARKS.md`. Never negative in this self-match-inclusive form, unlike `sample_entropy`, which can be undefined when a window's tightest tolerance finds no matches at all.

## Reference

Formula source: [https://www.ncbi.nlm.nih.gov/pmc/articles/PMC54970/](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC54970/)
