# Benchmarks

- [`run.py`](run.py) — times every registered indicator, at default
  parameters, against synthetic OHLCV data at 10k/100k/1M bars. No extra
  dependencies beyond zeon-ta's own (NumPy and pandas).

```bash
python benchmarks/run.py                  # all three sizes
python benchmarks/run.py --sizes 100000   # a single size, for a quicker pass
python benchmarks/run.py --csv out.csv    # also write raw results
```

See [BENCHMARKS.md](../BENCHMARKS.md) for methodology and results.
