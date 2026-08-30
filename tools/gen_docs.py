"""Render the indicator documentation published at the project's GitHub Pages site.

Run with ``python tools/gen_docs.py``; pass ``--check`` to verify the committed
files are up to date without writing anything, which is what CI and
``tests/test_docs.py`` do.

Only prose comes from :mod:`docs_content`. Parameter tables and output column
names are read from the indicator registry, and every example is a real callable
that is invoked against the test fixture — the snippet shown in the docs is
recovered from that same callable's source, so the code you read and the output
you read cannot disagree, and neither can drift away from the library.

README.md is generated too, but deliberately stays a short pitch for the
project (what it is, why, install, quick start) with a link out to the full
docs site — the per-indicator reference used to be embedded directly in the
README as one giant table per category, which made it slow to read and slow
to regenerate; that detail now lives only in ``docs/``.
"""

from __future__ import annotations

import argparse
import ast
import inspect
import sys
import textwrap
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

import pandas as pd  # noqa: E402
from docs_content import CONTENT  # noqa: E402

from zeonta._core import IndicatorSpec, iter_specs  # noqa: E402

DOCS = ROOT / "docs"
FIXTURE = ROOT / "tests" / "data" / "ohlcv.csv"

#: GitHub Pages URL this project's docs/ folder is published at (Settings ->
#: Pages -> Deploy from a branch -> main / docs).
PAGES_URL = "https://selimozbas.github.io/zeon-ta/"

LABELS = {
    "measures": "What it measures",
    "formula": "Formula",
    "params": "Parameters",
    "returns": "Returns",
    "usage": "Usage",
    "reading": "How to read it",
    "pitfalls": "Pitfalls",
    "reference": "Reference",
    "param": "Parameter",
    "default": "Default",
    "column": "Column",
    "inputs": "Required inputs",
    "accessor": "Accessor form",
    "source": "Formula source",
    "back": "All indicators",
    "none": "None.",
    "note": (
        "Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as "
        "`df`. The output shown is the real output."
    ),
}

CATEGORY_TITLES = {
    "foundations": "Foundations",
    "moving_averages": "Moving Averages",
    "oscillators": "Oscillators",
    "volume": "Volume",
    "volatility": "Volatility",
    "trend": "Trend Systems",
    "advanced": "Advanced Tools",
    "statistics": "Statistics",
}


def load_fixture() -> pd.DataFrame:
    frame = pd.read_csv(FIXTURE, parse_dates=["date"]).set_index("date")
    return frame.astype("float64")


def lambda_source(function: Callable[..., Any]) -> str:
    """Recover the expression a single-line ``lambda df: ...`` computes."""
    source = textwrap.dedent(inspect.getsource(function)).strip().rstrip(",")
    node = ast.parse(source, mode="eval").body
    if not isinstance(node, ast.Lambda):
        raise TypeError(f"documentation examples must be lambdas, got {source!r}")
    return ast.unparse(node.body)


def evaluate(examples: list[Callable[[pd.DataFrame], Any]]) -> list[tuple[str, str]]:
    """Run each example against the fixture, pairing its source with its output."""
    frame = load_fixture()
    rendered = []
    with pd.option_context("display.width", 100, "display.max_columns", 12):
        for example in examples:
            rendered.append((lambda_source(example), str(example(frame))))
    return rendered


def format_default(value: object) -> str:
    return f"`{value!r}`" if isinstance(value, str) else f"`{value}`"


def parameter_table(spec: IndicatorSpec) -> list[str]:
    if not spec.params:
        return [f"_{LABELS['none']}_", ""]
    lines = [f"| {LABELS['param']} | {LABELS['default']} |", "| --- | --- |"]
    lines += [f"| `{name}` | {format_default(value)} |" for name, value in spec.params.items()]
    lines.append("")
    return lines


def output_columns(spec: IndicatorSpec) -> list[str]:
    """The real column names a default call produces on the fixture."""
    frame = load_fixture()
    result = spec.func(*[frame[field] for field in spec.inputs])
    if isinstance(result, tuple):
        result = result[0]
    if isinstance(result, pd.Series):
        return [str(result.name)]
    return [str(name) for name in result.columns]


def render(spec: IndicatorSpec, examples: list[tuple[str, str]]) -> str:
    doc = CONTENT[spec.name]

    lines = [
        "---",
        f"title: {doc['title']}",
        "---",
        "",
        f"[← {LABELS['back']}](../index.md)",
        "",
        f"`zeonta.{spec.name}()` — {spec.summary}",
        "",
        f"## {LABELS['measures']}",
        "",
        doc["about"],
        "",
        f"## {LABELS['formula']}",
        "",
        "```text",
        doc["formula"],
        "```",
        "",
        f"## {LABELS['params']}",
        "",
        f"**{LABELS['inputs']}:** " + ", ".join(f"`{field}`" for field in spec.inputs),
        "",
    ]
    lines += parameter_table(spec)
    lines += [f"## {LABELS['returns']}", "", f"| {LABELS['column']} |", "| --- |"]
    lines += [f"| `{name}` |" for name in output_columns(spec)]
    lines += [
        "",
        f"## {LABELS['usage']}",
        "",
        LABELS["note"],
        "",
        "```python",
        "import pandas as pd",
        "import zeonta",
        "",
        "df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')",
        "```",
        "",
    ]
    for expression, output in examples:
        lines += ["```python", expression, "```", "", "```text", output, "```", ""]
    lines += [
        f"**{LABELS['accessor']}:** `df.zta.{spec.name}(...)`",
        "",
        f"## {LABELS['reading']}",
        "",
        doc["reading"],
        "",
        f"## {LABELS['pitfalls']}",
        "",
        doc["pitfalls"],
    ]
    if spec.url is not None:
        lines += [
            "",
            f"## {LABELS['reference']}",
            "",
            f"{LABELS['source']}: [{spec.url}]({spec.url})",
        ]
    return "\n".join(lines).rstrip() + "\n"


def render_index() -> str:
    intro = (
        "Every indicator in `zeon-ta`, grouped by module. A few indicators additionally "
        "link to the external source their formula was verified against — see "
        "[methodology.md](methodology.md) for how that verification is done."
    )
    lines = [
        "---",
        "title: Indicator Reference",
        "---",
        "",
        "# Indicator Reference",
        "",
        intro,
        "",
    ]
    for category, title in CATEGORY_TITLES.items():
        specs = [spec for spec in iter_specs() if spec.category == category]
        if not specs:
            continue
        lines += [f"## {title}", "", "| Indicator | Summary |", "| --- | --- |"]
        for spec in specs:
            title_text = CONTENT[spec.name]["title"]
            lines.append(f"| [`{spec.name}`](indicators/{spec.name}.md) | {title_text} |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


README = """# zeon-ta

[![CI](https://github.com/selimozbas/zeon-ta/actions/workflows/ci.yml/badge.svg)](https://github.com/selimozbas/zeon-ta/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](pyproject.toml)
[![License](https://img.shields.io/github/license/selimozbas/zeon-ta)](LICENSE)

Technical analysis for Python — the widely used classics (RSI, MACD,
Bollinger Bands, Ichimoku, and the rest of the standard toolkit) alongside
modern, academically-sourced tools most TA libraries skip: Ehlers'
cycle-analysis filters, the Hurst exponent, wavelet-based denoising and
multi-scale volatility, OHLC volatility estimators standard in
quantitative finance (Parkinson, Garman-Klass, Rogers-Satchell,
Yang-Zhang), and a causal cross-wavelet lead-lag transform.

Formulas follow standard, widely published technical-analysis definitions
where one exists. Where a formula's own academic paper is the source
instead, or where a candidate indicator turned out to have no single
agreed-on formula across implementations, the docstring says which and
why.

## Why another TA library

- **Broad on purpose.** {count} indicators across {categories} categories
  (moving averages, oscillators, volatility, trend, volume, statistics)
  — not just the popular dozen.
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

The full indicator reference — {count} indicators across {categories} categories,
each with its formula, parameters, worked examples and (where one exists) the
external source it was verified against — is published at:

**{pages_url}**

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

MIT — see [LICENSE](LICENSE).
"""


def render_readme() -> str:
    return README.format(
        count=len(list(iter_specs())),
        categories=len({spec.category for spec in iter_specs()}),
        pages_url=PAGES_URL,
    )


def build() -> dict[Path, str]:
    """Every documentation file mapped to the content it should hold."""
    files: dict[Path, str] = {}
    files[ROOT / "README.md"] = render_readme()
    evaluated = {spec.name: evaluate(CONTENT[spec.name]["example"]) for spec in iter_specs()}
    for spec in iter_specs():
        files[DOCS / "indicators" / f"{spec.name}.md"] = render(spec, evaluated[spec.name])
    files[DOCS / "index.md"] = render_index()
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate indicator documentation.")
    parser.add_argument("--check", action="store_true", help="fail if files are out of date")
    args = parser.parse_args()

    missing = sorted({spec.name for spec in iter_specs()} - set(CONTENT))
    if missing:
        print(f"docs_content.py is missing entries for: {', '.join(missing)}", file=sys.stderr)
        return 1

    files = build()
    stale: list[Path] = []
    for path, content in files.items():
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            stale.append(path)
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")

    if args.check and stale:
        print("out-of-date documentation files:", file=sys.stderr)
        for path in stale:
            print(f"  {path.relative_to(ROOT)}", file=sys.stderr)
        print("run: python tools/gen_docs.py", file=sys.stderr)
        return 1

    print(f"{'checked' if args.check else 'wrote'} {len(files)} files ({len(stale)} changed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
