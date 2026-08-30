# zeon-ta

[![CI](https://github.com/selimozbas/zeon-ta/actions/workflows/ci.yml/badge.svg)](https://github.com/selimozbas/zeon-ta/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](pyproject.toml)
[![License](https://img.shields.io/github/license/selimozbas/zeon-ta)](LICENSE)

Technical analysis for Python, from RSI to a causal cross-wavelet lead-lag
transform. Alongside the standard indicator set, zeon-ta implements newer,
academically-sourced tools — Ehlers' cycle-analysis filters, the Hurst
exponent, wavelet-based denoising and multi-scale volatility, a
cross-asset lead-lag transform — each one traced to the specific paper it
comes from, not to a folklore formula.

Formulas follow standard, widely published technical-analysis definitions
where one exists. Where a formula's own academic paper is the source
instead, or where a candidate indicator turned out to have no single
agreed-on formula across implementations, the docstring says which and
why.

## Why another TA library

- **Classic and modern, both formula-verified.** Every indicator — whether
  it is RSI or a MODWT wavelet-variance decomposition — cites what its
  formula was checked against, and a proposed indicator with no single
  agreed-on formula across sources is declined outright rather than
  guessed at (documented in [CHANGELOG.md](CHANGELOG.md) either way).
- **No build step.** Every dependency ships prebuilt wheels, so `pip install`
  just works — everywhere, including on ARM Macs and in slim containers.
- **One contract, every indicator.** Pass a `Series`, an array or a list; get
  pandas back with your index intact and the same length as your input. Warm-up
  bars are `NaN`, never trimmed, so nothing silently shifts under a backtest.
- **Two ways to call it.** A functional API and a `.zta` DataFrame accessor that
  routes to the exact same code — verified equal by tests, not by convention.
- **Documented honestly.** Every indicator's page states its pitfalls, including
  where an output contains look-ahead information and what to do about it.
- **Measured, not assumed, performance.** Every indicator is benchmarked at up
  to 1M bars, with real numbers and methodology in [BENCHMARKS.md](BENCHMARKS.md)
  — most complete in low milliseconds even at that size.

## Install

Not on PyPI yet — install straight from GitHub:

```bash
pip install git+https://github.com/selimozbas/zeon-ta.git
```

Or clone and install locally:

```bash
git clone https://github.com/selimozbas/zeon-ta.git
cd zeon-ta
pip install .
```

Requires Python 3.12+.

## Quick start

```python
import pandas as pd
import zeonta

df = pd.read_csv('ohlcv.csv', parse_dates=['date']).set_index('date')

# Functional
rsi = zeonta.rsi(df['close'], length=14)
bands = zeonta.bbands(df['close'], length=20, std=2)

# Accessor — identical results
rsi = df.zta.rsi(length=14)
trend = df.zta.supertrend(length=10, multiplier=3)

# Discover everything that is available
print(zeonta.list_indicators())
```

More in [examples/](examples/), runnable directly against a committed sample dataset.

## Output contract

| Input | Output |
| --- | --- |
| `pd.Series` | `Series` / `DataFrame` with the same index |
| `np.ndarray` or `list` | `Series` / `DataFrame` with a `RangeIndex` |

Single-line indicators return a named `Series`; multi-line ones return a
`DataFrame` whose column names carry the settings used (`RSI_14`,
`MACD_12_26_9`, `SUPERT_10_3.0`). `ichimoku` additionally returns the part of
the cloud that projects past the last bar, rather than discarding it.

## Documentation

The full indicator reference — 127 indicators across 8 categories,
each with its formula, parameters, worked examples and (where one exists) the
external source it was verified against — is published at:

**https://selimozbas.github.io/zeon-ta/**

It's generated straight from the code and from actually running every
example (see `tools/gen_docs.py`), so it never drifts out of sync with what's
installed. Browse it locally under [docs/](docs/index.md) instead if you'd
rather not leave the repo.

`zeonta.cross_asset.wavelet_lead_lag(close_a, close_b, period=20)` compares
*two independent* price series — which one is leading the other, and by how
much, at a chosen timescale — via a causal Morlet Cross-Wavelet Transform
(Torrence & Compo, 1998). It isn't in `list_indicators()` or the `.zta`
accessor: every registered indicator assumes one asset's own OHLCV columns,
and a second, independent series doesn't fit that contract. Import and call
it directly; see its own docstring for the full method and a documented
lag-estimate caveat.

## Development

```bash
pip install -e ".[dev]"
pytest                      # test suite
ruff check . && mypy src/   # lint and types
python tools/gen_docs.py    # regenerate the docs
```

Documentation is generated: prose lives in `tools/docs_content.py`, while
parameter tables, column names and example output are taken from the code
itself and from actually running each example. A test fails if the committed
files drift.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow, and
[docs/methodology.md](docs/methodology.md) for how a formula gets
verified before it's implemented. This project follows a
[Code of Conduct](CODE_OF_CONDUCT.md); see [SECURITY.md](SECURITY.md) to
report a vulnerability privately.

## License

GPL-3.0-or-later — see [LICENSE](LICENSE).
