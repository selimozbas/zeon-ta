# Contributing to zeon-ta

Thanks for considering a contribution. This document covers how the codebase
is structured, how a new indicator gets added end to end, and what the test
suite expects before a change is done.

By participating in this project you agree to abide by its
[Code of Conduct](CODE_OF_CONDUCT.md). Found a security issue rather than a
bug? See [SECURITY.md](SECURITY.md) instead of opening a public issue.

## Setup

```bash
git clone https://github.com/selimozbas/zeon-ta.git
cd zeon-ta
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## How an indicator is built

Every indicator is a plain function decorated with `@indicator(...)`. The
decorator inspects the function's own signature to derive its `inputs`
(leading OHLCV-named parameters) and `params` (everything after, which must
have defaults), and registers an `IndicatorSpec` that drives discovery
(`zeonta.list_indicators()`), the `.zta` accessor, the contract tests, and
documentation generation — all from one source of truth.

```python
@indicator(
    category="oscillators",
    summary="One-line description, shown by list_indicators().",
    reference="https://chartschool.stockcharts.com/.../your-indicator",
    outputs=("XYZ",),
)
def your_indicator(close: ArrayLike, length: int = 14) -> pd.Series:
    """One-paragraph description, then the formula, then how it differs
    from or relates to similar indicators already in the library.

    Parameters
    ----------
    close:
        Closing prices.
    length:
        Look-back window.

    Returns
    -------
    pandas.Series
        Named ``XYZ_{length}``.

    Examples
    --------
    >>> import zeonta
    >>> float(zeonta.your_indicator([...]).iloc[-1])
    <the actual computed value, never guessed — see below>

    References
    ----------
    https://chartschool.stockcharts.com/.../your-indicator
    """
    length = validate_length(length)
    values = as_array(close, "close")
    ...
    return wrap_series(result, common_index(close), f"XYZ_{length}")
```

Every indicator in the library follows the same three contracts, enforced by
`tests/test_contracts.py` against *every* registered function automatically:

- **Flexible input.** Accept `pd.Series`, `np.ndarray`, or a plain list.
  Normalise with `as_array()`.
- **Aligned output.** The result has the same length and (when the input was
  a `Series`) the same index as the input — never trimmed. Bars that cannot
  be computed yet are `NaN`. Use `wrap_series()` / `wrap_frame()` to build
  the return value.
- **Guarded against silent misalignment.** Any function taking more than one
  series (`high`/`low`/`close`/`volume`/...) calls `require_aligned_index()`
  first, so two same-length `Series` from different date ranges raise instead
  of being combined positionally.

Use `validate_length()` / `validate_multiplier()` for parameter checks, and
`require_non_negative()` for anything that represents volume. Look at a
recent addition (`src/zeonta/trend.py`'s `vortex` or `chandelier_exit` are
good examples) for the exact shape to copy.

`lesson` vs. `reference` on the decorator: `lesson` is a purely internal
category slug used for indicators from the original curriculum this project
started from and carries no public URL. `reference` is a full external URL
and is the one new indicators should use — see the next section. The two are
mutually exclusive; most new indicators set `reference` and leave `lesson`
unset.

## Formula verification is not optional

**Never implement a formula from a single source.** This project has, more
than once, found that an initially-trusted source's own stated formula was
wrong (see `CHANGELOG.md`'s `0.1.1` entry for two examples caught this way).
Before writing any code:

1. Find the formula in an independent, authoritative source — StockCharts
   ChartSchool is preferred; fall back to Fidelity's Technical Indicator
   Guide, Wikipedia, or the vendor's own official documentation (e.g.
   MetaTrader5, TradingView) when ChartSchool has no page for it.
2. Cross-check against a second source if the first is at all ambiguous
   about a default parameter, a rounding rule, or an edge case (division by
   zero, the very first bar, a flat market).
3. Put the confirmed source URL in `reference=` on the decorator and in the
   `References` section of the docstring.

See `docs/en/methodology.md` for the full writeup of this process and past
examples of formulas that turned out to be wrong.

**Never guess a doctest or example value.** Compute it by actually running
the function, then paste the real result into the docstring. A guessed value
that happens to look plausible is worse than no example at all — it silently
teaches the wrong number. This project's history has repeated examples of an
initially-guessed value turning out to be off (see `dema`/`tema`/`hma`/
`williams_r`/`stoch_rsi` in `CHANGELOG.md`), which is exactly why this rule
exists.

## Testing conventions

- **Golden values, traced by hand.** For at least one test per indicator,
  work the formula out on paper (or in a scratch script) against a small,
  fixed input, and assert the function produces that exact number. Comment
  the arithmetic inline so a future reader can verify it without re-deriving
  it — see `tests/test_oscillators.py::test_rsi_matches_a_hand_traced_wilder_recursion`
  for the pattern.
- **Property tests alongside golden values,** not instead of them: bounds
  (e.g. an oscillator stays within its documented range), monotonicity in a
  clean trend, a rejected invalid parameter, a flat/zero-range edge case.
- **Contract tests are automatic.** Because every indicator is registered,
  `tests/test_contracts.py` already covers length preservation, index
  preservation, `Series`/`ndarray`/list input equivalence, misaligned-index
  rejection, and mismatched-length rejection for your new function with no
  extra code from you — just make sure the function is registered and
  exported.
- **Doctests run for real.** Every `Examples` block in a docstring is
  executed by the test suite (`doctest.testmod`); an example that raises or
  prints the wrong value fails CI.
- **100% statement coverage is maintained.** Run
  `pytest --cov=zeonta --cov-report=term-missing` and cover any line the
  report flags as missed.

## Documentation workflow

Prose lives in exactly one place: `tools/docs_content.py`, one dict entry per
indicator with English and Turkish `title`, `formula`, `about`, `reading`,
and `pitfalls` fields, plus an `example` list of `lambda df: ...` callables
run against `tests/data/ohlcv.csv`. Everything else — parameter tables,
output column names, the rendered example output, the README indicator
tables, the per-language indicator indexes — is derived mechanically from
the registry and from actually executing the examples.

After adding or changing an indicator:

```bash
python tools/gen_docs.py          # regenerates docs/, README.md, README.tr.md
python tools/gen_docs.py --check  # verifies nothing is stale, no writes (what CI runs)
```

`tests/test_docs.py::test_generated_docs_are_up_to_date` runs the `--check`
form automatically, so a docs update committed alongside a code change is
required, not optional.

## Before opening a pull request

```bash
pytest -q
ruff check .
ruff format --check .
mypy src/
pytest --cov=zeonta --cov-report=term-missing
python tools/gen_docs.py --check
```

All five must pass. If you added an indicator, also update
`CHANGELOG.md` under the current unreleased entry.

## License

By contributing, you agree your contribution is licensed under the same
terms as the project: GPL-3.0-or-later (see [LICENSE](LICENSE)).
