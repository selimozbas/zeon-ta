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

- **1.0** — a deliberate, separate decision to declare the API stable,
  not something the version number arrives at by climbing high enough.
  Until then, each item above ships as its own `0.x.0` minor release as
  it's ready (`0.3.0` → `0.4.0` → `0.5.0` → ...), with `0.x.y` patches
  for fixes in between — the same minor-vs-patch discipline
  [CONTRIBUTING.md#versioning](CONTRIBUTING.md#versioning) describes
  already applies now, not only after 1.0.
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
- **KNN / Lorentzian Distance Classifier** and similar machine-learning
  "indicators" popularized on retail charting platforms. These are one
  specific author's implementation choices (feature set, distance metric,
  training window), not a published formula multiple independent sources
  agree on — the same class of problem as `STC`/`JMA`/`MAMA` above. They
  also don't fit this library's stateless, formula-in/values-out contract:
  a trained classifier over a rolling history is a different shape of tool.
- **Fuzzy-logic oscillators.** Membership functions and rule sets are
  designed per paper/implementation with no standard choice — the "0-100
  buy/sell fuzziness" score two implementations produce for the same input
  can differ entirely, which fails the same formula-verification bar as
  everything else on this list.
- **"Fractal Dimension Index" (FDI).** The name is genuinely ambiguous
  across independent sources, not just inconsistently described: Carlos
  Sevcik's original FDI (corrected by Alex Matulich) is a normalized
  waveform arc-length construction, while John Ehlers & Ric Way's own
  "Fractal Dimension" (TASC, June 2010) is a box-counting dimension — the
  same family of calculation `frama()` already computes internally as its
  `dimen`, but not the same formula as Sevcik/Matulich's. No source treats
  one of these as "the" canonical FDI over the other; declined for the
  same reason `STC`/`JMA`/`MAMA` are.
- **Singular Spectrum Analysis (SSA).** Embedding a rolling window into a
  trajectory matrix and reconstructing a trend from the leading singular
  components needs two real design choices — the embedding (window) length
  and how many leading components to keep — that the SSA literature treats
  as genuinely open, with no single convention independent
  implementations/tutorials converge on. The same test that declines
  `STC`/`JMA`/`MAMA` applies here.
- **MODWT (Maximal Overlap Discrete Wavelet Transform).** This project's
  existing `pywt` dependency exposes `pywt.swt`, which is often described
  as equivalent to MODWT — but `pywt`'s own documentation calls its
  implementation only "closely related" to the published construction,
  citing a stated difference, and additionally requires the input length
  be a multiple of `2**level`, which does not fit this library's
  arbitrary-length rolling-window contract. Declined rather than shipped
  on an equivalence that couldn't be confirmed cleanly.
- **One-sided (causal) Hodrick-Prescott filter.** A state-space/Kalman
  reformulation that reduces to a causal HP filter is a real idea in the
  econometrics literature, but no single, independently cross-checked
  parameterization of that state-space model could be confirmed against a
  primary source in this research pass — declined rather than guessed.
- **Beveridge-Nelson decomposition.** Requires fitting an ARIMA(p,d,q)
  model to the series first, and no single order convention is agreed on
  for an arbitrary price series; doing the model-selection step properly
  would need `statsmodels`, a new runtime dependency this project does not
  add without a separate, deliberate decision (see
  [CONTRIBUTING.md](CONTRIBUTING.md) on not adding dependencies for one
  indicator).
- **Lempel-Ziv Complexity (LZC).** Applying the (unambiguous) LZ76
  algorithm to a continuous price series first requires binarizing it —
  above/below the window's own mean, or its median — and then, for a
  normalized 0-1 reading, a further normalization-factor convention;
  independent sources do not agree on either choice.
- **Recurrence Quantification Analysis (RQA).** Phase-space embedding
  (dimension and delay) and the recurrence threshold used to build the
  recurrence matrix are all real, non-uniquely-specified design choices —
  more free parameters with more literature disagreement than any other
  candidate considered alongside it, with no single defensible default
  parameterization multiple independent sources converge on.
- **Kyle's lambda, an OHLCV-only "proxy" variant.** Investigated
  specifically as a possible carve-out from the order-flow/microstructure
  entry above: every simplified construction found (regressing price
  change against signed volume using a return-sign stand-in for the true
  trade sign) relies on inventing a sign convention — contemporaneous
  return sign, lagged return sign, or a tick-test-style approximation —
  that independent sources do not agree on, the same class of problem that
  declined VPIN's Bulk Volume Classification bucketing above. The
  tick/order-book-data requirement for the *true* Kyle's lambda, in the
  entry above, stands as originally written.
- **Bai-Perron multiple structural break test** (Bai & Perron, 1998,
  Econometrica). Its usual application dates an unknown number of
  breakpoints *ex post* over a whole, fixed series via dynamic programming
  over sum-of-squared-residuals, then picks the break count with a
  BIC-type criterion or sequential testing — a procedure built around
  seeing the whole series at once. Reworking it into a per-bar, no-
  look-ahead rolling estimate with a single, independently-agreed
  break-count selection rule usable at every bar could not be confirmed
  against a primary or secondary source; every rolling adaptation found
  invents its own truncation of the method rather than following one the
  literature already agrees on.
- **Zivot-Andrews structural-break unit root test** (Zivot & Andrews,
  1992, Journal of Business & Economic Statistics). Its own break-date
  search is a real, endogenous procedure with one commonly-implemented
  default (Model C, breaking both intercept and trend — the default in
  both `statsmodels.tsa.stattools.zivot_andrews` and `arch.unitroot.ZivotAndrews`),
  but the ADF-type regression at each candidate breakpoint additionally
  needs a lagged-difference order, and *that* choice (a fixed lag, AIC/BIC
  selection, or Ng-Perron's general-to-specific search) is a second,
  independently-contested convention layered on top of the model-A/B/C
  choice — the same class of "a second free parameter with no single
  agreed selection rule" problem that declined MODWT's block-length and
  SSA's component count. Combined with the cost of searching every
  candidate break point inside every rolling window (an ADF-type
  regression per candidate, repeated at every bar — asymptotically
  heavier than `markov_regime_switching`, this library's current slowest
  indicator), this is declined rather than shipped on an invented lag
  convention.
- **Hasbrouck's Bayesian Gibbs estimate of Roll's model** (Hasbrouck,
  2009, Journal of Finance). Requires Markov Chain Monte Carlo (Gibbs)
  sampling — a fundamentally different computational shape from every
  other indicator in this library, and a genuinely stochastic one:
  correctness would depend on a chain length, a burn-in period, and a
  fixed RNG seed, none of which have one agreed convention for a generic
  per-bar use case. `markov_regime_switching`'s own EM fit was only
  accepted because its M-step is closed-form and deterministic; Gibbs
  sampling has no such determinism without inventing an arbitrary
  seed/chain-length/burn-in convention this project declines to invent.
- **Fong-Holden-Trzcinka (FHT) spread estimator** (Fong, Holden &
  Trzcinka, 2017, *Review of Financial Studies* 30(12), 4437-4480 —
  corrected from a research note's mistaken "Journal of Finance"; the
  actual title is "A Simple Estimation of Bid-Ask Spreads from Daily
  Close, High, and Low Prices"). The measure is a closed-form function of
  the proportion of zero-return days and the standard deviation of daily
  returns via the standard normal quantile, but the paper additionally
  requires the LOT-style effective spread this simplifies from to
  identify which of two candidate closed-form roots is the economically
  meaningful one, plus a stated minimum sample length (a full month of
  daily data in the paper's own calibration) before the zero-return-day
  proportion is reliable at all. This library's per-bar, arbitrary-window
  contract has no single, independently cross-checked way to adapt that
  root-selection and minimum-sample-length machinery to an
  arbitrary rolling window; declined rather than guessed.
- **Florackis-Gregoriou-Kostakis (FGK) illiquidity ratio** (Florackis,
  Gregoriou & Kostakis, 2011, *Journal of Banking & Finance* 35(12),
  3335-3350 — corrected from a research note's "2014"; the actual title
  is "Trading Frequency and Asset Pricing on the London Stock Exchange:
  Evidence from a New Price Impact Ratio", introducing what the paper
  calls the "Return-to-Turnover" ratio). An Amihud-style illiquidity
  ratio using turnover rather than dollar volume, but independent
  secondary sources describing it disagree on whether the turnover term
  enters as a plain ratio or through the specific log-cycle weighting a
  research note attributed to this paper — no source found reproduces
  the paper's own exact formula closely enough to resolve that, only its
  name and its general "turnover instead of dollar volume" idea. Declined
  rather than reconstruct an unverified formula.
- **Fuzzy Entropy (FuzzEn)** (Chen et al., 2007, IEEE Transactions on
  Biomedical Engineering). Shares `sample_entropy`'s template-matching
  structure, replacing the hard Chebyshev-distance cutoff with a soft
  fuzzy membership function — but the exact exponential family used for
  that membership function is genuinely inconsistent across the
  literature that has followed the original paper: Chen et al.'s own
  construction, later "local" baseline-corrected variants, and other
  authors' own reformulations use different exponents and different
  template baseline-removal conventions, with no independent source
  treating one as the settled default the way Richman & Moorman's
  Sample Entropy formula itself is settled. The same class of "which of
  several published exponential families is canonical" ambiguity that
  declined fuzzy-logic oscillators.
- **Horizontal Visibility Graph (HVG) tail exponent** (Lacasa et al.,
  2008, PNAS/EPL). The visibility criterion itself (two bars connected
  iff every bar strictly between them is below both) is unambiguous, and
  an uncorrelated series' own degree distribution has an exact closed
  form the original paper derives (`P(k) = (1/3)(2/3)^(k-2)`). But the
  practical *summary statistic* this library would need to output — the
  exponential decay rate lambda fit from a correlated series' own degree
  distribution — has no single agreed estimation procedure across the
  literature that followed: a plain log-linear least-squares fit over
  every observed degree, a fit restricted to the distribution's tail
  only (with no agreed cutoff for where "the tail" begins), and a
  maximum-likelihood exponential fit all appear in different papers with
  materially different results on the same series. Declined rather than
  pick one estimation convention with no independent source treating it
  as the standard.
- **Variational Mode Decomposition (VMD)** (Dragomiretskiy & Zosso,
  2014, IEEE Transactions on Signal Processing). Requires an iterative
  ADMM optimization with several hyperparameters (`alpha`, `K`,
  convergence tolerance) that the literature genuinely varies on by
  application; `pywt`, this project's only wavelet dependency, does not
  implement VMD at all (the reference Python implementation, `vmdpy`, is
  a separate, unadopted third-party package this project will not add as
  a dependency for one indicator). A much heavier numerical-optimization
  undertaking than this library's existing iterative estimator
  (`markov_regime_switching`'s EM, which at least has closed-form
  M-steps) with no single dominant, independently cross-checked
  parameterization; declined.
- **Autocorrelation Periodogram** (Ehlers). This project has already
  declined `Decycler` for exactly this reason, and the same problem
  recurs here: Ehlers' own 2013 book presentation (*Cycle Analytics for
  Traders*) and his own 2016 TASC magazine article ("Measuring Market
  Cycles") disagree on two material implementation details — the
  roofing/high-pass pre-filter used before the autocorrelation itself
  (a simple first-order high-pass in one presentation vs. a canonical
  2-pole high-pass feeding a Super Smoother bandpass in the other), and
  how the dominant cycle length is extracted from the resulting spectrum
  (peak-finding vs. a center-of-gravity-weighted average over bins at or
  above half the peak power). Two internally inconsistent presentations
  by the method's own author, the same standing problem that already
  declined `STC`/`JMA`/`Decycler`.
- **Synchrosqueezed Wavelet Transform (SWT)** (Daubechies, Lu & Wu,
  2011, Applied and Computational Harmonic Analysis). `pywt` has no
  synchrosqueezing support at all — a feature request for it
  (`PyWavelets/pywt#258`) has stood open, unimplemented, since 2016 — so
  unlike `pywt.swt`'s "closely related" but confirmed-inequivalent
  relationship to MODWT (already declined above), there is no existing
  primitive in this project's wavelet dependency to build on at all.
  Implementing the reassignment method from scratch would be substantial
  novel numerical work with real risk of subtle bugs in a published
  algorithm this library has no supporting machinery for; declined
  rather than attempted from a blank page.
- **Meilijson volatility estimator** (Meilijson, 2009 working paper,
  published 2011 in *REVSTAT — Statistical Journal* 9(2), as "The
  Garman-Klass Volatility Estimator Revisited" — corrected from a
  research note's "1992"). The paper is *not* the drift-corrected
  extension of Garman-Klass a research note described: it stays within
  Garman & Klass's own zero-drift Brownian-motion assumption and instead
  improves the estimator's statistical *efficiency* (7.7322 vs. 7.4) by
  compressing the OHLC data to a different statistic (conditioning the
  path on the sign of its own total drift over the bar). This is a
  single-paper result with materially lower independent citation and
  replication than Parkinson/Garman-Klass/Rogers-Satchell/Yang-Zhang (all
  already in `volatility.py`), and reconstructing its exact statistic
  from the paper's own path-conditioning argument, without a second
  independent source to cross-check the reconstruction against, would
  cross into guessing a formula rather than verifying one. Declined
  rather than duplicate `garman_klass_volatility` under a different name
  on an unverified reconstruction.
