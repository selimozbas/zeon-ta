---
title: How Formulas Are Verified
---

# How formulas are verified

Every indicator in `zeon-ta` is implemented from a formula that has been
checked against an independent, authoritative source — never from a single
source trusted at face value, and never from memory. This page explains why,
and what the process actually looks like.

## Why this is a hard rule

Early in this project, two indicators were implemented from a single
source's stated formula and both turned out to be wrong once cross-checked
against a second source:

- **`trend_channel`**'s bands were measuring how far price scattered around
  the *window's mean*, when the standard definition (and the source's own
  prose, read carefully) actually calls for scatter around the *fitted
  regression line* — a different, smaller number that inflates the channel
  incorrectly.
- **`squeeze`**'s momentum midline used a flat three-way average of its
  three inputs, when the canonical TTM Squeeze formula uses a specific
  nested average that weights two of them together first.

Neither mistake was a typo — both came from trusting one source's wording
without checking it against how the indicator is actually computed
elsewhere. That is the whole reason the verification rule below exists, and
why it applies to every indicator added since, not just the ones that broke.

## The process

1. **Find the formula in a primary, authoritative source.**
   [StockCharts ChartSchool](https://chartschool.stockcharts.com/) is
   preferred — it is maintained, cites the original developer where one
   exists, and is precise about defaults and edge cases. When ChartSchool
   has no page for an indicator, the fallback order is: Fidelity's Technical
   Indicator Guide, Wikipedia, or the originating platform's own official
   documentation (MetaTrader5, TradingView) for indicators native to a
   specific platform.
2. **Cross-check against a second source whenever the first is ambiguous**
   about a default parameter, a rounding rule, how the very first bar is
   handled, or a division-by-zero edge case. Two sources agreeing on the
   core formula but differing on a default is common and worth noting in the
   docstring; two sources actively disagreeing on the formula itself is a
   sign to keep looking rather than pick one arbitrarily.
3. **Record the source.** The confirmed URL goes on the function's
   `@indicator(reference=...)` and in its docstring's `References` section,
   so anyone reading the code — not just this page — can check the
   implementation against the same source.
4. **Compute every example, never guess it.** A docstring's `Examples`
   block is executed by the test suite, but the *value written into the
   docstring* is authored by a person first. Several examples in this
   library's history were initially guessed and turned out to be wrong once
   actually computed — `hma`'s doctest was guessed as `30.0` on a straight
   ramp and was actually `29.3333`, `williams_r`'s was guessed as `0.0` and
   was actually `-0.0` (a genuine float sign edge case), `stoch_rsi`'s was
   guessed as `100.0` and was actually `50.0` (a flat-market convention
   triggered by RSI itself pinning at its own ceiling). None of these were
   caught by reasoning about the formula harder; all were caught by running
   the code before trusting the number.
5. **Write tests that would have caught the two mistakes above.** At least
   one golden value traced by hand against the confirmed formula, not
   against the implementation's own output — a test that reproduces a bug
   instead of catching it is worse than no test.

## What this does not cover

A handful of indicators (marked with `lesson` instead of `reference` in the
registry) predate this project's move to citing external sources per
function; they follow the same standard, widely published definitions, just
without an individually cited URL in their docstring. Every indicator added
since — see `CHANGELOG.md`'s `0.2.0` entry onward — carries an explicit
`reference`.

See [CONTRIBUTING.md](../CONTRIBUTING.md#formula-verification-is-not-optional)
for how this applies when adding a new indicator.
