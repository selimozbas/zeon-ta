# Sample Entropy (SampEn)

[← All indicators](../index.md) · [Türkçe](../../tr/indicators/sample_entropy.md)

`zeonta.sample_entropy()` — Sample Entropy: how unpredictable a series is, from 0 (regular) upward (irregular).

## What it measures

Richman and Moorman (2000) built Sample Entropy to fix a specific flaw in the earlier Approximate Entropy (Pincus, 1991): ApEn counts a template as matching itself, which biases it — more so on shorter series — toward reading more regular than the data actually is. SampEn excludes self-matches entirely. It asks a different question from hurst_exponent/dfa: not whether a series trends or reverts, but how much it repeats its own short-term patterns at all, independent of which direction those patterns point.

## Formula

```text
Build every length-m and length-(m+1) template from the log-return window; B = count of length-m template pairs within tolerance r*std(window) (self-matches excluded); A = same count at length m+1; SampEn = -ln(A/B)
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
| `SAMPEN_100_2_0.2` |

## Usage

Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as `df`. The output shown is the real output.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.sample_entropy(df['close']).tail(3)
```

```text
date
2024-10-25    2.433613
2024-10-26    2.451005
2024-10-27    2.433613
Name: SAMPEN_100_2_0.2, dtype: float64
```

**Accessor form:** `df.zta.sample_entropy(...)`

## How to read it

Low values (near 0) mean the window keeps repeating short patterns — regular, more predictable behaviour. High values mean little to no repeating structure — irregular, closer to noise. Unlike hurst_exponent/dfa, a high reading here does not say *which way* price is likely to move, only that its recent behaviour has been harder to characterise by a short repeating pattern.

## Pitfalls

By far the slowest indicator in this library — every bar compares every pair of templates in its own window (O(window^2)), not the single vectorised pass most indicators here use, and slower again than hurst_exponent/dfa's own per-bar loops (see `BENCHMARKS.md`). `m` and `r` are real choices, not defaults to ignore: Richman & Moorman's own examples use `m=2`, `r` between `0.1` and `0.25` of the window's standard deviation, and a different pairing changes the result — this is one specific, standard parameterisation, not the only one used in the literature.

## Reference

Formula source: [https://physionet.org/content/sampen/1.0.0/](https://physionet.org/content/sampen/1.0.0/)
