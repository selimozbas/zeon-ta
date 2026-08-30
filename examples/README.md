# Examples

Every script here runs against the same 300-bar OHLCV fixture the test suite
uses (`tests/data/ohlcv.csv`), needs no extra dependencies beyond zeon-ta's
own, and is itself run by the test suite (`tests/test_examples.py`) so it
can't silently go stale.

- [`basic_usage.py`](basic_usage.py) — the functional API, the `.zta`
  accessor, a multi-line (`DataFrame`) indicator, and `zeonta.list_indicators()`
  for discovery.
- [`accessor_pipeline.py`](accessor_pipeline.py) — chaining several `.zta`
  calls into one feature table, the shape a feature-engineering step for a
  model or a screener typically takes.
- [`signal_walkthrough.py`](signal_walkthrough.py) — combining a trend read
  (SuperTrend's own direction flip) with a momentum confirmation (RSI) into
  one boolean signal column. Illustrates *how* to wire two indicators
  together, not a trading strategy — no position sizing, no risk management,
  not backtested for profitability.
- [`next_gen_indicators.py`](next_gen_indicators.py) — the indicators most
  TA libraries don't carry: OHLC volatility estimators (Parkinson,
  Garman-Klass, Yang-Zhang) against plain ATR, and Ehlers' cycle-analysis
  filters (Roofing Filter, Even Better Sinewave, Cyber Cycle, Voss
  Predictive Filter, Reflex/Trendflex).
- [`cross_asset.py`](cross_asset.py) — `zeonta.cross_asset`'s two-asset
  functions (`correlation`, `beta`, the causal `wavelet_lead_lag` transform),
  which take two independent price series and so live outside the indicator
  registry and the `.zta` accessor. Builds a synthetic second series from the
  fixture to have two inputs to compare — swap in two real series for actual
  use.

```bash
python examples/basic_usage.py
python examples/accessor_pipeline.py
python examples/signal_walkthrough.py
python examples/next_gen_indicators.py
python examples/cross_asset.py
```
