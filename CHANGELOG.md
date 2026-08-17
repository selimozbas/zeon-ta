# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

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

[Unreleased]: https://github.com/selimozbas/zeon-ta/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/selimozbas/zeon-ta/releases/tag/v0.1.0
