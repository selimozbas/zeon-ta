# Security Policy

## Supported versions

zeon-ta is pre-1.0 and has not yet been published to PyPI. Until a `1.0`
release, only the latest commit on `main` is supported — there are no
maintained release branches to backport a fix to.

## Reporting a vulnerability

Please **do not** open a public GitHub issue for a suspected security
vulnerability. Instead, report it privately through GitHub's
[private vulnerability reporting](https://github.com/selimozbas/zeon-ta/security/advisories/new)
for this repository.

Include, as far as you can:

- A description of the issue and its potential impact.
- Steps to reproduce, or a minimal example.
- The affected commit or version.

You should get an initial response within a few days. This is a
single-maintainer project run outside of working hours, so please be
patient — every report is read and taken seriously.

## Scope

zeon-ta is a pure NumPy + Pandas numerical library: it computes indicators
from arrays you already hold in memory and has no network, filesystem, or
subprocess access of its own. Realistic security concerns are things like:

- A crafted input (`NaN`/`Inf` patterns, extreme lengths, adversarial
  parameter values) causing a crash, hang, or resource-exhaustion rather
  than a clean `ValueError`.
- A supply-chain issue in the packaging or release pipeline
  (`pyproject.toml`, `.github/workflows/`).

Reports along either of these lines are especially welcome.
