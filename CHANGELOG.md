# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
