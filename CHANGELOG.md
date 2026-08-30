# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- **New dependency: PyWavelets (`pywavelets>=1.9`).** Needed for
  `wavelet_denoise` below — no wavelet transform exists in NumPy or pandas
  themselves (NumPy's FFT gives frequency information but discards *when*
  a frequency occurs; a DWT keeps both). This is the project's first
  dependency beyond NumPy + pandas; every other indicator is unaffected.
  Registered indicators: 61 -> 62.

### Added

- **New `statistics` category** — eight generic statistical indicators,
  filling gaps found by cross-checking against other libraries' coverage
  (TA-Lib/pandas-ta-style categories): `stddev`, `variance`, `zscore`,
  `skewness`, `kurtosis`, `mad` (median, not mean, absolute deviation —
  distinct from the mean absolute deviation `cci` already uses
  internally), `log_return`, and `cumulative_return`. Unlike the recent
  academic batch, these are textbook, single-formula statistics with no
  verification ambiguity; `skewness` and `kurtosis` specifically use the
  adjusted Fisher-Pearson formulas, checked to match
  `pandas.Series.rolling().skew()`/`.kurt()` exactly (pandas already being
  a dependency, this is a strong, convenient second source). Also
  reviewed but intentionally not added: `APO` (Absolute Price Oscillator,
  which is `macd`'s own main line under a different name) and `THERM`
  (Market Thermometer, not in TA-Lib's own indicator set and not found
  with a single clearly authoritative source). Registered indicators:
  67 -> 75.

- **Moving averages** — `emd_imf1` (Huang et al., 1998): the fifth and
  last of the academic indicator batch, and the biggest single
  implementation in it. Empirical Mode Decomposition derives its own
  basis functions from a signal's local extrema rather than assuming a
  fixed one (Fourier's sines, a wavelet's mother function) — this returns
  only the first Intrinsic Mode Function (the fastest local oscillation)
  of what a full recursive decomposition would produce, since the full
  IMF count varies with the data and does not fit a fixed-column output.

  Needed a natural cubic spline to fit the envelope through local
  extrema, which does not exist in NumPy; hand-implemented it (the
  standard tridiagonal second-derivative system, solved directly) rather
  than adding scipy as a second major dependency after PyWavelets —
  checked against `scipy.interpolate.CubicSpline` while writing it
  (installed only in the dev environment for that one check, never a
  runtime dependency; max difference ~1e-15) before relying on it.

  Found and fixed a real bug before finalizing: an earlier version
  anchored both the upper and lower envelope splines to the window's own
  first/last sample, which forces their mean to equal the data exactly at
  that point — so every sift zeroed out the boundary bars deterministically,
  caught by noticing a suspiciously exact `0.0` at the read-out point
  rather than trusting the formula. Removing that anchor and letting the
  spline extrapolate past the outermost real extremum fixed it (correlation
  with a synthetic fast-oscillation component went from unusable to 0.999).

  Causal and rolling for the same non-repaint reason as this library's
  wavelet tools, verified the same way (a data-prefix run agrees exactly
  with the equivalent slice of a full run). By far the most expensive
  indicator in the library — every bar re-runs an iterative spline-fitting
  sift over its own window — documented as such.

  Registered indicators: 66 -> 67.

- **Advanced** — `sample_entropy` (Richman & Moorman, 2000): the third of
  the five-indicator academic batch. Measures how much a rolling window
  of log returns repeats its own short-term patterns (`SampEn = -ln(A/B)`,
  counting length-`m` vs. length-`(m+1)` template matches within a
  tolerance scaled to the window's own standard deviation, self-matches
  excluded) — a different question from `hurst_exponent`/`dfa` (trend vs.
  reversion) and from `wavelet_variance` (which timescale the volatility
  is at): how *unpredictable* the series is, independent of direction.
  Verified directionally against a periodic-vs-white-noise pair (near-zero
  entropy for an exactly repeating pattern, clearly higher for
  unstructured noise) rather than trusting the formula alone. By far the
  slowest indicator in the library — every bar compares every pair of
  templates in its own window (`O(window^2)`), documented as such.
  Registered indicators: 65 -> 66.

- **Advanced** — `ou_half_life` and `dfa`, the first two of a batch of
  newer, academically-sourced indicators (`hepsi` — "all of them" — was
  requested from five proposed candidates; Sample/Approximate Entropy and
  EMD follow separately).

  - `ou_half_life`: fits the discretised Ornstein-Uhlenbeck process to a
    rolling window by OLS (`Close[t]-Close[t-1]` regressed against
    `Close[t-1]`) and converts the fitted mean-reversion speed into a
    half-life in bars (`-ln(2)/lambda`) — the standard way this method is
    used, per two independent sources, to pick a *lookback length* for a
    mean-reversion strategy rather than as a signal read on its own. `NaN`
    when the fitted `lambda` is `>= 0` (no mean reversion detected), by
    documented convention, rather than a misleading negative half-life.
  - `dfa`: Detrended Fluctuation Analysis (Peng et al., 1994), a second,
    later estimator for the same persistence question `hurst_exponent`'s
    classical R/S analysis asks — applied to the *same* rolling window of
    log returns as `hurst_exponent` for direct comparability (an
    intermediate version applied it to raw price and produced clearly
    wrong values, ~1.5, for an ordinary random walk; caught by sanity
    checking against the known theoretical value before finalizing) —
    but explicitly detrends each box locally first, which is why DFA
    tolerates non-stationarity inside the window that R/S cannot.
    Verified vectorised per-box detrending against a straightforward
    per-box `np.polyfit` loop before relying on it.

  Registered indicators: 63 -> 65.

- **`zeonta.cross_asset.wavelet_lead_lag`** — a Morlet Cross-Wavelet
  Transform between *two independent* price series, answering which one
  is leading the other (and by roughly how much) at a chosen Fourier
  period. Formula verified directly from Torrence & Compo's 1998 "A
  Practical Guide to Wavelet Analysis" (read from the source PDF, the
  standard reference for this technique): `W_XY(s) = W_X(s) * conj(W_Y(s))`,
  power `= |W_XY|`, phase `= atan2(Im(W_XY), Re(W_XY))`. The lead/lag
  *sign* convention was confirmed numerically against synthetic sine
  pairs of known lag (not just asserted from the paper's prose) — see the
  function's own test suite.

  **Deliberately not part of the indicator registry.** Every registered
  indicator assumes one asset's own OHLCV columns (`_split_signature` in
  `registry.py` mechanically requires it); a second, independent price
  series doesn't fit that contract, and stretching the registry to allow
  it would touch the `.zta` accessor, the generic contract-test suite,
  and the doc generator all at once for the sake of one function. It's
  called directly (`zeonta.cross_asset.wavelet_lead_lag(...)`) instead,
  with its own hand-written tests and its own README section — this is a
  deliberate two-tier decision, not an oversight.

  **Causal, like this library's other wavelet-based tools**, for the same
  reason: the standard whole-series CWT convolves each point against a
  wavelet kernel extending into the future. This implementation uses only
  the *causal half* of the Morlet kernel instead, which has a real,
  documented cost — a numerical check against synthetic lag pairs found
  the causal kernel consistently *over-reports* the lag magnitude by
  roughly 5-10%, though it never gets the direction (sign) wrong.
  Verified with the same kind of prefix-vs-full-series test used for
  `wavelet_denoise`/`wavelet_variance`.

  Also declined, for the record: **Wavelet MACD**, proposed alongside
  this — no single canonical formula exists (one paper denoises MACD's
  DIF line with a specific Coiflet-5 wavelet; another uses genetic
  algorithms to tune ordinary MACD's parameters instead; both are called
  "Wavelet MACD" but do unrelated things), the same class of problem
  `MavilimW` and `IFT-CCI` were declined for earlier. **Wavelet Coherence**
  (a normalized 0-1 version of this same cross-wavelet idea) was also
  considered and declined for now: Torrence & Compo's own paper states
  raw coherence is trivially 1 at every point unless smoothed in time and
  scale, and that smoothing methodology comes from a *later*, separate
  paper (Torrence & Webster 1999 / Grinsted et al. 2004) not yet verified
  against a primary source.

- **Volatility** — `wavelet_variance`: multi-scale volatility via the
  Maximal Overlap DWT (MODWT) — splits the single blended number `atr()`
  or a rolling standard deviation gives into `level` per-scale bands
  (`WVAR_1` covering 2-4 bar swings up through `WVAR_{level}`, doubling
  each level), so a bar dominated by high-frequency noise can be told
  apart from one driven by a genuine slower move. Verified against
  Percival & Walden's *Wavelet Methods for Time Series Analysis* (2000),
  the standard reference for this technique, and against `pywt.swt`'s own
  documented energy-conservation property (confirmed numerically: total
  coefficient energy equals input energy to float precision) — without
  `norm=True` the transform does *not* have the variance-partitioning
  property this indicator relies on, easy to miss since `pywt.swt` works
  and returns plausible-looking numbers either way. Uses the *biased*
  wavelet-variance estimator (mean over every coefficient in the window)
  rather than Percival & Walden's *unbiased* one (which excludes
  boundary-affected coefficients), documented as a deliberate
  simplicity/always-defined tradeoff in its own docstring. Same causal,
  rolling, non-repaint design as `wavelet_denoise` below, for the same
  reason — verified by the same kind of prefix-vs-full-series test.
  Registered indicators: 62 -> 63.

- **Moving averages** — `wavelet_denoise`: causal, rolling Discrete Wavelet
  Transform denoising (`db4`, level 2 by default), soft-thresholded with
  the Donoho & Johnstone (1994) universal threshold
  (`sigma = MAD(finest detail band) / 0.6745`,
  `threshold = sigma * sqrt(2 * log(window))`) — the standard rule
  published work on wavelet-denoised technical indicators applies to
  price/return series before building indicators on top of them.
  Deliberately **not** the naive whole-series-in-one-pass approach that
  academic backtests typically use: that repaints every past bar's value
  as new data arrives, which is unusable for a live signal even though it
  looks fine in-sample. Every bar here is decomposed from its own
  trailing `window` only, so a value once written never changes — the
  same non-repaint guarantee as every other indicator in this library,
  at the cost of one decomposition per bar instead of one pass over the
  whole series. Returns a denoised price series meant to be piped into an
  existing indicator (`zeonta.rsi(zeonta.wavelet_denoise(df["close"]))`)
  rather than a `Wavelet_RSI`/`Wavelet_MACD` pair, since that's the same
  computation without duplicating `rsi()`/`macd()`.

- **Moving averages** — `t3` (Tillson's T3): three cascaded "Generalized
  DEMA" passes (`(1+v)*EMA - v*EMA(EMA)`, blending toward `dema` as `v`
  grows), built to cut `dema`/`tema`'s overshoot on a sharp reversal.
  Neither StockCharts nor Wikipedia document it — Tillson published it in
  *TASC*, January 1998; the volume factor default (0.7) is Tillson's own
  and agreed on everywhere, the length default (5) follows an
  independently maintained reference implementation since no source states
  one length as canonical. Registered indicators: 56 -> 57.

Two names considered and declined for this project, for the record: a
second **Parabolic SAR** (already implemented — see `0.1.0`) and
**Inverse Fisher Transform on CCI**, which — like `MavilimW` before it —
has no single authoritative formula: community adaptations disagree on the
CCI scaling constant (`0.1*CCI` vs `0.1*CCI/4`), and the disagreement
traces to the same source `MavilimW` did. Ehlers' own paper documents the
Inverse Fisher Transform applied to RSI, not CCI; that RSI version remains
a candidate if requested specifically.

**Ehlers cycle-analysis indicators**, requested by name after the Tillson T3
batch: `fisher_transform` (normalizes price into a bounded range, then
applies the inverse hyperbolic tangent transform to sharpen turning points
into visible spikes — verified against Ehlers' original TASC article,
"Using The Fisher Transform", *Stocks & Commodities* V. 20:11);
`super_smoother` (a 2-pole IIR filter designed to track price with less lag
*and* less noise than an EMA of comparable smoothness — its docstring
documents a real degrees/radians bug found in a well-known third-party
library's default implementation of the same filter, used here as
independent confirmation the radians-consistent formula is correct);
`instantaneous_trendline` (a 2nd-order recursive filter that estimates the
dominant cycle's trend component with minimal lag, seeded by a simple
weighted average for its first 7 bars per Ehlers' own convention).

Also `hurst_exponent`: classical Rescaled Range (R/S) analysis over a
rolling window, estimating whether a series' returns are trending
(H > 0.5), mean-reverting (H < 0.5), or a random walk (H ≈ 0.5). Documented
as one of several disagreeing Hurst-estimation methods (vs. DFA,
generalized Hurst exponent) rather than a single settled value, and as the
one indicator in the library that is not O(n) — its rolling multi-lag
regression measures ~1.18s per 10k bars against low milliseconds for
everything else (see [BENCHMARKS.md](BENCHMARKS.md)).

A **Wavelet-De-noised Indicators** family (PyWavelets-based `Wavelet_RSI`/
`Wavelet_MACD`) was proposed alongside these but deliberately not built: it
would add the project's first dependency beyond NumPy + Pandas, which needs
its own explicit decision rather than riding in with an unrelated indicator
batch. A **Random Forest trend-prediction indicator** was also proposed and
skipped for now, by choice, as out of scope for a formula-driven TA
library.

Registered indicators: 57 -> 61.

Nine indicators, each citing the external source its formula was verified
against, each verified against a second independent source as well (see each
one's own docstring for the specific second source and any default-parameter
ambiguity found along the way):

- **Oscillators** — `trix` (Triple Exponential Average, with signal line);
  `ppo` (Percentage Price Oscillator — `macd`'s construction expressed as a
  percentage, comparable across symbols); `tsi` (True Strength Index,
  William Blau's double-smoothed momentum); `dpo` (Detrended Price
  Oscillator, a cycle-identification tool built differently from every other
  oscillator here — it compares an *older* price to the *current* SMA);
  `coppock_curve` (a WMA of two summed ROC readings, built for calling major
  long-term bottoms on monthly charts).
- **Volume** — `force_index` (Alexander Elder; price change x volume,
  EMA-smoothed — the same author as `elder_ray`, viewed through volume
  instead of an EMA); `ease_of_movement` (Richard Arms' box-ratio: how much
  volume a bar's price movement needed).
- **Volatility** — `ulcer_index` (Peter Martin's drawdown-only risk measure —
  squares the drawdown before averaging, so one deep decline dominates the
  reading far more than several small ones of the same total size).
- **Trend** — `linreg` (Slope and Forecast/endpoint from the same
  ordinary-least-squares fit `trend_channel`/`squeeze` already use).

Registered indicators: 47 -> 56.

Also: doctests across the whole library are now actually executed.
`pytest --doctest-modules` was never wired into `testpaths`, so every
docstring `Examples` block — the ones this project's own methodology
insists must be computed, never guessed — had silently never been checked
by CI. All 50 pre-existing doctests turned out to still be correct; this
closes the gap going forward.

- `benchmarks/run.py` and [BENCHMARKS.md](BENCHMARKS.md): every registered
  indicator timed against synthetic OHLCV data at 10k/100k/1M bars, with
  real, reproducible numbers and methodology rather than assumed
  performance. At 1M bars, 32/47 indicators finish in under half a second
  and the slowest (`ema_ribbon`, six full EMA passes by design) in under 2s;
  at a realistic 10k bars every indicator finishes in under 20ms.
- Ruff's `D` (pydocstyle) rule set is now enforced (`numpy` docstring
  convention), so a public function/class/module missing a docstring, or one
  with a formatting slip (no blank line before an elaboration, closing
  quotes not on their own line, etc.), now fails `ruff check .` — this is
  the project's PEP 257 conformance made automatic rather than manually
  maintained. `D401` (imperative-mood summaries) is deliberately disabled:
  every indicator's docstring opens with the indicator's own name ("Simple
  Moving Average.", "True Range...") to match how it's referred to
  everywhere else (README, docs, tests), and imperative mood would fight
  that established convention rather than improve it. `D105`/`D107` are
  disabled for self-explanatory magic methods and `__init__`s already
  documented by their class's own docstring, both allowed under PEP 257's
  own wording. `tests/*` and the internal `tools/gen_docs.py` and
  `tools/docs_content.py` build scripts are exempt (not part of the public
  API); `_core` needed no exemption — its own public names already carried
  docstrings.
- **Moving averages** — `smma` (Smoothed Moving Average, a.k.a. Wilder's
  Moving Average / RMA): the exact recursion already used inside `rsi`,
  `atr` and `adx`, exposed as its own standalone line. Neither StockCharts
  nor Wikipedia document it as a named indicator on its own; the default
  length (9) follows TradingView's dedicated Smoothed Moving Average page
  rather than Wilder's own 14 (used for RSI/ATR/ADX), since no single
  source states a canonical standalone default. The recursion was
  independently confirmed against MetaTrader's MQL5 documentation.
- Five new registry-wide contract tests in `tests/test_contracts.py`, applied
  automatically to every indicator: a single missing OHLCV bar must raise no
  warnings and must not stay `NaN` forever once enough clean bars follow it
  (the exact shape of the `adl()` and `aroon()` bugs just fixed); a flat
  market (every OHLCV value identical) must not raise or warn; volume-taking
  indicators must accept zero volume and reject negative volume. Any future
  indicator gets this coverage for free just by being registered.
- `tests/test_tradingview_parity.py`: a committed 300-bar SPY daily dataset
  (`tests/data/tv_spy_daily.csv`, fetched from Yahoo Finance's public chart
  API right after that day's regular-session close) checked against values
  read directly off TradingView's own "Technicals" page for the same symbol
  and moment — 17 core indicators (SMA, EMA, RSI, MACD, CCI, ADX, Awesome
  Oscillator, Momentum, Stochastic RSI, Williams %R, Bull Bear Power,
  Ultimate Oscillator, Stochastic, Ichimoku's base line, and both Classic
  and Fibonacci pivot points) matched TradingView to the penny, catching two
  real bugs in the process — `hma` and `pivot_points` (see Fixed, below).

### Changed

- `support_resistance` and `divergence` no longer detect swing pivots with a
  per-bar Python loop. The shared `_pivot_flags` helper moved to a single
  `sliding_window_view` pass, and `support_resistance`'s confirmed-pivot
  carry-forward moved from its own loop to a shift + `ffill` (the same
  pattern `obv()` already used). Found and measured via the new
  `benchmarks/run.py`: `support_resistance` went from 2.48s to 0.06s at 1M
  bars (~40x), `divergence` from 3.30s to 0.77s (~4.3x). Output is
  bit-identical to before; no new dependency.

### Fixed

- `hma` used the wrong rounding rule for its two intermediate WMA lengths.
  Alan Hull's own formula (confirmed on alanhull.com and a second
  independent write-up) truncates `n/2` and `sqrt(n)` toward zero; this
  library was rounding both to the nearest whole number instead, which
  agrees with Hull's formula only when those values happen to land on a
  whole number. For `length=9` this made a real, non-trivial difference —
  775.70 (rounded) vs. Hull's true 776.37, confirmed both against his
  formula and empirically against a live TradingView reading of the same
  data. Fixed to truncate, matching Hull's own definition; on a pure linear
  ramp the corrected HMA now converges to the exact ramp value, the same
  clean cancellation `dema`/`tema` already have — a good sign the fix is
  right, not just TradingView-compatible by coincidence.
- `pivot_points`'s Classic `R3`/`S3` used `High + 2*(Pivot - Low)` /
  `Low - 2*(High - Pivot)`, which is actually the Camarilla system's `R3`,
  not Classic's — StockCharts' own Classic Pivot Points page does not
  define `R3`/`S3` at all, so this had no independent check until now.
  Confirmed against TradingView's own documented formula
  (`Pivot +/- 2*(High - Low)`) and empirically against a live reading (all
  seven Classic levels, and all seven Fibonacci levels, now match exactly).
  Switched from `lesson="pivot-points"` to a cited `reference` for this
  reason. `P`, `R1`, `R2`, `S1`, `S2` and the Fibonacci system were already
  correct and unaffected.

## [0.2.0] - 2026-08-17

### Added

Seven indicators, each additionally citing the external source its formula
was verified against (`IndicatorSpec.reference`, a new field alongside
`lesson`; the two are mutually exclusive):

- **New `volume` category** — `obv` (On-Balance Volume), `cmf` (Chaikin Money
  Flow), `mfi` (Money Flow Index). These combine volume with price direction
  or position, distinct from `relative_volume` (volume size alone) and `vwap`
  (volume-weighted price).
- **Oscillators** — `momentum` (raw n-bar price difference) and `roc` (the
  same comparison expressed as a percentage).
- **Moving averages** — `kama` (Kaufman's Adaptive Moving Average), which
  blends a fast and slow EMA constant by an Efficiency Ratio measured each bar,
  so it tracks tightly through a clean trend and flattens on its own in a
  choppy one.
- **Trend systems** — `parabolic_sar`, a trailing stop-and-reverse system
  whose acceleration factor grows with every new extreme point, following the
  same one-pass recursive-state pattern as `supertrend` and `adx`.
- **Moving averages** — `wma` (Weighted Moving Average), giving linearly
  increasing weight to more recent closes; sits between `sma` (equal weight)
  and `ema` (exponential decay) in how fast it turns. Backed by a new
  `rolling_wma` core primitive, reusable by any future moving average built
  as a WMA chain.
- **Moving averages** — `dema` and `tema` (Double/Triple Exponential Moving
  Average, Patrick Mulloy), which cancel most of a plain EMA's lag by
  offsetting it with its own EMA (and, for TEMA, EMA-of-EMA); `hma` (Hull
  Moving Average), a WMA-of-WMAs that extrapolates ahead of a fast WMA then
  re-smooths, cutting lag further still at the cost of occasional overshoot
  on sharp reversals.
- **Oscillators** — `williams_r` (mathematically `stoch`'s unsmoothed `%K`
  minus 100, on a 0 to -100 scale); `stoch_rsi` (the `stoch` formula applied
  to `rsi` instead of price, scaled to 0-100 and %K/%D-smoothed to match
  `stoch`'s convention rather than the source's bare 0-1 form);
  `awesome_oscillator` (Bill Williams; `macd`'s fast-SMA-minus-slow-SMA shape
  applied to the bar's own midpoint instead of the close).
- **Trend systems** — `aroon`, returning `AROONU`/`AROOND`/`AROONOSC` in one
  call. Where `donchian` marks *where* the n-bar high/low sit, Aroon marks
  *how long ago* they happened.
- **New in `volume`** — `adl` (Accumulation/Distribution Line), the
  running-total sibling of `cmf` — same Money Flow Multiplier (now factored
  into a shared `_money_flow_multiplier` helper), but accumulated instead of
  summed over a window and divided by volume.
- **New in `volume`** — `chaikin_oscillator`, `macd`'s fast-EMA-minus-slow-EMA
  shape applied to `adl` instead of price.
- **Trend systems** — `chandelier_exit`, an ATR-anchored trailing stop
  recomputed fresh from the last n bars' extreme every bar rather than
  ratcheted, unlike `supertrend`/`parabolic_sar`; `vortex`, a +VI/-VI
  directional pair built from plain rolling sums instead of Wilder smoothing,
  the same crossover relationship `adx`'s DI pair has.
- **Oscillators** — `ultimate_oscillator` (Larry Williams; blends three
  look-backs weighted 4:2:1 to resist the false divergences a single-period
  oscillator gives); `elder_ray` (Bull Power / Bear Power — high and low
  measured against an EMA, reading the tug-of-war inside each bar rather than
  just where it closed).

Registered indicators: 25 -> 46. `list_indicators()`'s `lesson` column is
renamed `source`, now holding the external reference URL for the indicators
that cite one and `None` for the rest.

### Changed

- `IndicatorSpec` and the `@indicator` decorator: `lesson` is now optional and
  `reference` (a full external URL) was added; the two are mutually exclusive,
  enforced by `IndicatorSpec.__post_init__`. `lesson` is a purely internal
  category slug with no derived URL — `IndicatorSpec.url` now returns the
  `reference` value directly (`None` when not set), rather than deriving a
  link from `lesson`. Docstrings and generated docs only show a "Reference"
  section for the indicators that actually cite one.

### Fixed

- `parabolic_sar` now rejects `start > max_af`. Accepting it meant the
  acceleration factor started above its own ceiling and immediately dropped
  *down* to `max_af` on the first new extreme point — the opposite of the
  documented "grows then holds" behaviour.
- Negative volume is now rejected by `relative_volume`, `obv`, `cmf` and
  `mfi`, matching the check `vwap` already had. Volume cannot be negative;
  previously a bad feed produced a numerically valid but meaningless result
  (e.g. negative volume nudging OBV the wrong way) instead of failing loudly.
- `adl` (and `chaikin_oscillator`, which builds on the same running total) no
  longer goes permanently `NaN` after a single unknown `high`/`low`/`close`/
  `volume` bar. `np.cumsum` was propagating that one gap's `NaN` through
  every bar after it, contradicting both `adl`'s own "Never NaN" docstring
  promise and the gap-handling convention `obv` already followed. A gap bar's
  contribution is now `0`, same as `obv`.
- `aroon` no longer produces a finite-looking but meaningless result when a
  `NaN` sits inside its look-back window. `argmax`/`argmin` have no real
  concept of `NaN` (comparisons against it are always `False`), so a window
  containing a gap was silently treated as if the gap were the extreme value
  instead of being excluded. Every window that has not fully aged the gap out
  is now `NaN`, as it should be.
- `true_range` no longer emits a `RuntimeWarning: All-NaN slice encountered`
  for a bar whose `high` and `low` are both missing. The resulting value was
  already correctly `NaN`; only the warning (which polluted callers' logs)
  is suppressed, and only for this specific, expected case.
- **NaN-gap handling made consistent across the three recursive/cumulative
  indicators added in this release:**
  - `obv`: a single unknown close or volume no longer poisons every bar after
    it via `cumsum`. A gap bar now contributes nothing (held flat), and the
    bar where data resumes compares against the last *known* close rather
    than the missing one.
  - `kama`: a `NaN` inside `close` widens the local warm-up but the series
    now recovers afterward — KAMA holds its last value across the gap and
    resumes updating once the Efficiency Ratio window clears it, matching
    the convention `ema`/Wilder-smoothed indicators already use.
  - `parabolic_sar`: a bar with a missing `high`/`low` now produces a clean
    `NaN` for that bar and leaves AF, the extreme point and trend direction
    untouched, so the next valid bar continues correctly. Previously,
    Python's built-in `min()`/`max()` silently ignore `NaN` in comparisons,
    which could produce a wrong-but-finite SAR instead of surfacing the gap.

## [0.1.1] - 2026-08-17

### Fixed

- **Silent index misalignment across multi-input indicators.** Every indicator
  taking more than one series (`high`/`low`/`close`/`volume`/`oscillator`) now
  calls `require_aligned_index`, which raises `ValueError` when two or more
  `pd.Series`/`pd.DataFrame` arguments have equal length but different
  indices. Previously such inputs were combined purely by position — same
  length, wrong pairing — with no signal that the result was meaningless.
  Plain arrays and lists carry no index and are unaffected.
- `trend_channel`: the channel bands now measure scatter about the fitted
  regression line (residual standard deviation), not about the window mean.
  The standard definition describes it this way too, but the initial
  implementation used the wrong deviation, which inflated the channel exactly
  when price was tracking the trend most cleanly.
- `squeeze`: the momentum midline now uses the published TTM Squeeze nested
  average, `avg(avg(highest_high, lowest_low), sma)` (range midpoint and SMA
  weighted equally at 1/2 each), instead of an equal three-way mean of the
  three inputs, which some casual descriptions suggest instead; this follows
  the canonical TTM Squeeze definition.
- `vwap` now rejects negative `volume` with a clear `ValueError` instead of
  producing a silent `NaN` once a window's net volume happened to cross zero.
- `ichimoku`'s forward-projected cloud now continues as real future dates when
  the input carries a `DatetimeIndex` with a regular frequency, instead of an
  arbitrary integer offset — it concatenates directly onto a date-indexed
  chart. Falls back to an integer `RangeIndex` when no such frequency exists.
- `zeonta.__version__` is now read from installed package metadata instead of
  being a second hardcoded literal that could drift out of sync with the
  `version` in `pyproject.toml` (as it briefly did during this release).

## [0.1.0] - 2026-08-17

First release. A core set of 24 standard technical-analysis indicators
across six modules, as 25 registered indicator functions.

### Added

- **Foundations** — `candles`, `support_resistance` (plus the `sr_levels`
  clustering helper), `trend_channel`, `relative_volume`.
- **Moving averages** — `sma`, `ema`, `ma_cross`, `ema_ribbon`.
- **Oscillators** — `rsi`, `stoch`, `macd`, `cci`.
- **Volatility** — `true_range`, `atr`, `bbands`, `keltner`, `squeeze`.
- **Trend systems** — `supertrend`, `adx`, `ichimoku`, `donchian`.
- **Advanced tools** — `vwap`, `fib_retracement`, `pivot_points`, `divergence`.
- `DataFrame.zta` accessor routing to the same functions, with case-insensitive
  OHLCV column matching.
- `zeonta.list_indicators()` for discovery, backed by an indicator registry that
  derives inputs and parameters from each function's own signature.
- English and Turkish documentation for every indicator, generated from the
  registry with example output produced by actually running the examples.
- `py.typed` marker; the package ships its type information.

### Notes

- `ichimoku` returns two frames: the on-chart lines, and the part of the cloud
  that projects beyond the last bar. The projection is returned rather than
  silently discarded.
- `vwap` with `anchor="session"` requires a `DatetimeIndex` and raises a clear
  error without one, rather than computing a different statistic quietly.
- The TTM Squeeze follows the published formula, under which a larger
  `kc_multiplier` makes squeezes *more* frequent, not less, despite some
  casual descriptions asserting the opposite.

[Unreleased]: https://github.com/selimozbas/zeon-ta/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/selimozbas/zeon-ta/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/selimozbas/zeon-ta/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/selimozbas/zeon-ta/releases/tag/v0.1.0
