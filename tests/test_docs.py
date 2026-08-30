"""Documentation must stay in lockstep with the code."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from zeonta._core import IndicatorSpec, iter_specs

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"


def doc_path(name: str) -> Path:
    return DOCS / "indicators" / f"{name}.md"


def test_every_indicator_is_documented(spec: IndicatorSpec) -> None:
    assert doc_path(spec.name).exists(), f"missing doc for {spec.name}"


def test_no_orphan_documentation() -> None:
    documented = {path.stem for path in (DOCS / "indicators").glob("*.md")}
    assert documented == {spec.name for spec in iter_specs()}


def test_parameter_table_matches_the_signature(spec: IndicatorSpec) -> None:
    """The documented parameters and defaults must be the real ones."""
    text = doc_path(spec.name).read_text(encoding="utf-8")
    rows = dict(re.findall(r"^\| `([a-z_][a-z0-9_]*)` \| `(.+?)` \|$", text, re.MULTILINE))
    for name, default in spec.params.items():
        assert name in rows, f"{spec.name}: {name} is not documented"
        expected = repr(default) if isinstance(default, str) else str(default)
        assert rows[name] == expected, f"{spec.name}: {name} default drifted"


def test_required_inputs_are_documented(spec: IndicatorSpec) -> None:
    text = doc_path(spec.name).read_text(encoding="utf-8")
    expected = ", ".join(f"`{field}`" for field in spec.inputs)
    assert f"**Required inputs:** {expected}" in text


def test_every_doc_with_a_reference_links_to_it(spec: IndicatorSpec) -> None:
    """Indicators that cite an external source must link to it; the rest must
    not carry a stray link (nothing to attribute)."""
    text = doc_path(spec.name).read_text(encoding="utf-8")
    if spec.url is None:
        assert "## Reference" not in text
    else:
        assert spec.url in text


def test_index_lists_every_indicator() -> None:
    text = (DOCS / "index.md").read_text(encoding="utf-8")
    for spec in iter_specs():
        assert f"indicators/{spec.name}.md" in text, f"{spec.name} missing from the index"


def test_internal_links_resolve() -> None:
    """Broken relative links are invisible until a reader hits a 404 on GitHub Pages."""
    for path in DOCS.rglob("*.md"):
        for target in re.findall(r"\]\((?!https?:)([^)#]+)\)", path.read_text(encoding="utf-8")):
            assert (path.parent / target).resolve().exists(), f"{path.name} -> {target}"


def test_generated_docs_are_up_to_date() -> None:
    """Fails when someone changes the code or prose without regenerating the docs."""
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "gen_docs.py"), "--check"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_readme_links_to_the_docs_site() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "docs/index.md" in text
    assert "github.io" in text
