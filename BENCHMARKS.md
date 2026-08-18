# Performance

zeon-ta is built on NumPy, pandas and PyWavelets — no build step, every
dependency ships prebuilt wheels. This page answers the question that
raises: is it actually fast enough? Numbers below are real, reproducible
measurements, not estimates.

## Methodology

`benchmarks/run.py` times every registered indicator, called with its
default parameters, against a deterministic synthetic OHLCV series (a seeded
random walk with realistic high/low/open ordering — no zero-range bars). Each
indicator is timed once per size with `time.perf_counter`; sizes tested are
10,000, 100,000 and 1,000,000 bars.

```bash
python benchmarks/run.py                  # all three sizes
python benchmarks/run.py --sizes 100000   # a single size, for a quicker pass
```

Measured on: Apple M5, Python 3.12.14, NumPy 2.5.2, pandas 3.0.5, macOS.
Your numbers will differ by hardware, but the relative shape — which
indicators are cheap, which are expensive, and why — will not.

## Headline numbers

At **1,000,000 bars** (roughly 2,700 years of daily data, or ~2 years of
minute bars — far beyond what almost any real backtest needs):

- **32 of 47 indicators complete in under half a second; 44 of 47 in under
  a second.**
- **The slowest, `ema_ribbon`, takes 1.86 seconds** — expected, since it is
  six full EMA passes by design, not a bottleneck to fix.
- Every other indicator using a Wilder-style or stateful recursion (`adx`,
  `parabolic_sar`, `supertrend`, `kama`) stays under 1.3 seconds despite
  being unable to vectorize away their bar-by-bar state.
- At 10,000 bars — a realistic size for years of daily data — **every
  single indicator completes in under 20 milliseconds**, most in well under
  1ms.

Nothing in the registry shows worse-than-linear scaling: every indicator's
time roughly tracks its input size 10x-to-10x, with no quadratic blowups.

## What was found and fixed

The benchmark's first run surfaced two real bottlenecks, both from a
per-bar Python loop where a vectorized alternative existed:

- **`support_resistance`**: 2.48s -> 0.06s at 1M bars (**~40x**). Its pivot
  detection (`_pivot_flags`) moved from a `for` loop with per-bar array
  slicing to a single `sliding_window_view` pass; its confirmed-pivot
  carry-forward moved from a second per-bar loop to a shift + `ffill`,
  the same pattern `obv()` already used for its own gap handling.
- **`divergence`** (which reuses `_pivot_flags` for its own swing
  detection): 3.30s -> 0.77s (**~4.3x**) from the same fix. Its remaining
  time is a genuinely sequential pass over *confirmed pivots only*
  (comparing each new swing against the last one to detect a divergence),
  not over every bar — a much smaller, harder-to-vectorize loop with
  diminishing returns for the complexity it would add.

Both changes are bit-identical to the previous output (existing golden-value
and doctest coverage caught this immediately) and added no new dependency.

## Why no numba (yet)

The remaining slowest indicators (`adx`, `parabolic_sar`, `supertrend`,
`kama`, `ema_ribbon`) are either inherently stateful/recursive by their own
published definition (see each one's docstring) or, in `ema_ribbon`'s case,
doing exactly as much work as its six EMA lines require. A JIT compiler
(numba) could speed up the stateful ones further, at the cost of a new
dependency, a JIT warm-up on first call, and a track record of lagging
behind new Python releases — a real tension with this project's own
latest-versions-first policy. Given every indicator already finishes in
under 2 seconds on a dataset far larger than any realistic backtest, that
trade isn't worth making right now. Revisit if a real workload shows
otherwise.
