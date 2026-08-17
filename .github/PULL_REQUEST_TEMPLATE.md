## Summary

What does this change, and why?

## Checklist

- [ ] Formula (if a new/changed indicator) was verified against an
      independent authoritative source — see
      [CONTRIBUTING.md](../CONTRIBUTING.md#formula-verification-is-not-optional).
      Source link:
- [ ] Every docstring `Examples` value was computed by actually running the
      code, not guessed.
- [ ] Tests added: at least one hand-traced golden value, plus relevant edge
      cases (flat/zero-range input, invalid parameters, bounds).
- [ ] `pytest -q` passes
- [ ] `ruff check .` and `ruff format --check .` pass
- [ ] `mypy src/` passes
- [ ] `pytest --cov=zeonta --cov-report=term-missing` shows no missed lines
- [ ] `python tools/gen_docs.py --check` passes (or `python tools/gen_docs.py`
      was run and the regenerated files are included in this PR)
- [ ] `CHANGELOG.md` updated, if user-facing

## Related issue

Closes #
