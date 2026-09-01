# Roadmap

Most Python TA libraries end up abandoned: the original `pandas-ta` is
archived, `ta` hasn't shipped since 2021, and `TA-Lib`'s C dependency makes
it hard to install in the first place. zeon-ta's answer to that isn't a
fixed release calendar — small teams that promise one tend to either burn
out or quietly drop it — it's that indicators keep shipping as soon as
they're formula-verified and tested, rather than being batched for an
arbitrary announcement date. This file is where that ongoing work is tracked
publicly, so "still maintained" is something you can check, not just claim.

It gets revisited as priorities shift; treat headings as direction, not a
committed date. See [CHANGELOG.md](CHANGELOG.md) for what has actually
shipped.

## Near-term focus

**More indicator sources, scanned with the same rigor as always** (see
[CONTRIBUTING.md#formula-verification-is-not-optional](CONTRIBUTING.md#formula-verification-is-not-optional)) —
candidates so far have come from pandas-ta-classic's own list and directly
from academic papers; the next passes look at TA-Lib's non-candlestick
battery for anything not already covered, and well-documented indicators
from MQL5/cTrader's own community libraries. Anything without a single,
unambiguous, cross-checkable formula gets declined and recorded in
CHANGELOG.md, the same way `STC`, `JMA`, `MAMA` and `Decycler` already are —
that bar doesn't move just because a new batch is underway.

**Performance and infrastructure:**
- An optional acceleration path (Numba or Cython, likely a `zeon-ta[speed]`
  extra) for the handful of genuinely sequential indicators that can't be
  vectorized and currently run a plain Python loop — `supertrend`, `adx`
  and `parabolic_sar` are the slowest of these today (`BENCHMARKS.md` has
  the actual numbers); the newer Ehlers cycle filters follow the same
  per-bar-loop shape but haven't been benchmarked yet.
- Accepting `polars` Series/DataFrames alongside pandas — an open design
  question (the input contract and the accessor are both built around
  pandas today), not yet a commitment either way.
- Periodically re-evaluating the dependency floor (`numpy>=2.5`,
  `pandas>=3.0`, `python>=3.12`) — this project deliberately tracks recent
  versions rather than pinning old ones, but "recent" is worth
  re-checking against actual adoption data every so often rather than
  assumed.

**Ecosystem integration examples** — showing zeon-ta plugged into the
backtest engines people already use (`backtesting.py`, `vectorbt`) rather
than asking anyone to choose between them and this library. Likely lands as
new files under `examples/`, following the same "must actually run, tested
by `tests/test_examples.py`" rule the existing ones do.

## Also on the list, not yet scheduled

- **1.0** — follows once the API surface and the integration story above
  feel settled, not on a fixed date. The versioning policy in
  [CONTRIBUTING.md#versioning](CONTRIBUTING.md#versioning) already applies
  today regardless of the version number.
- Multi-timeframe helpers (resampling OHLCV to a higher timeframe before
  indicator calculation, correctly and without look-ahead).

## Deliberately out of scope

- **TA-Lib's ~60-strong candlestick pattern battery.** Pattern-matching
  heuristics with no single formal definition across implementations;
  already declined once, stays declined.
- **Order-flow / microstructure indicators** (VPIN, Kyle's lambda, and
  similar). They need tick or order-book data; this library's contract is
  OHLCV bars, and that isn't changing to accommodate a handful of
  indicators.
- **Indicators with no single agreed-on formula across sources** —
  the standing rule, not a one-time decision. `STC`, `JMA`, `MAMA`,
  `TD Sequential` and `Decycler` are declined for this reason today; the
  same test applies to every future candidate.
