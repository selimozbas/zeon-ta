# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
  The TA 101 lesson describes it this way too, but the initial implementation
  used the wrong deviation, which inflated the channel exactly when price was
  tracking the trend most cleanly.
- `squeeze`: the momentum midline now uses the published TTM Squeeze nested
  average, `avg(avg(highest_high, lowest_low), sma)` (range midpoint and SMA
  weighted equally at 1/2 each), instead of an equal three-way mean of the
  three inputs. The TA 101 lesson's wording, `Avg(HighestHigh, LowestLow,
  SMA)`, reads as the latter; the source site is a third-party reference, not
  authoritative, so this follows the canonical TTM Squeeze definition instead.
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

First release. Covers the complete
[TA 101](https://ta.cognicode.org) curriculum — all 24 lessons across six
modules — as 25 registered indicator functions.

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
  `kc_multiplier` makes squeezes *more* frequent. The TA 101 quiz for that
  lesson asserts the opposite; the formula wins.

[Unreleased]: https://github.com/selimozbas/zeon-ta/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/selimozbas/zeon-ta/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/selimozbas/zeon-ta/releases/tag/v0.1.0
