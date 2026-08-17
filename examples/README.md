# Examples

- [`basic_usage.py`](basic_usage.py) — the functional API, the `.zta`
  accessor, a multi-line (`DataFrame`) indicator, and `zeonta.list_indicators()`
  for discovery. Runs against the same 300-bar OHLCV fixture the test suite
  uses; no extra dependencies beyond zeon-ta's own (NumPy and pandas), no
  plotting, no trading strategy or signal logic — purely how to call things.

```bash
python examples/basic_usage.py
```
