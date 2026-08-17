"""Documentation must stay in lockstep with the code and across both languages."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

from zeonta._core import IndicatorSpec, iter_specs

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
LANGS = ("en", "tr")


def doc_path(name: str, lang: str) -> Path:
    return DOCS / lang / "indicators" / f"{name}.md"


@pytest.mark.parametrize("lang", LANGS)
def test_every_indicator_is_documented(spec: IndicatorSpec, lang: str) -> None:
    assert doc_path(spec.name, lang).exists(), f"missing {lang} doc for {spec.name}"


def test_the_two_languages_cover_the_same_files() -> None:
    """A half-translated docs tree is worse than an obviously missing one."""
    english = {path.name for path in (DOCS / "en" / "indicators").glob("*.md")}
    turkish = {path.name for path in (DOCS / "tr" / "indicators").glob("*.md")}
    assert english == turkish


def test_no_orphan_documentation() -> None:
    documented = {path.stem for path in (DOCS / "en" / "indicators").glob("*.md")}
    assert documented == {spec.name for spec in iter_specs()}


@pytest.mark.parametrize("lang", LANGS)
def test_parameter_table_matches_the_signature(spec: IndicatorSpec, lang: str) -> None:
    """The documented parameters and defaults must be the real ones."""
    text = doc_path(spec.name, lang).read_text(encoding="utf-8")
    rows = dict(re.findall(r"^\| `([a-z_]+)` \| `(.+?)` \|$", text, re.MULTILINE))
    for name, default in spec.params.items():
        assert name in rows, f"{spec.name} ({lang}): {name} is not documented"
        expected = repr(default) if isinstance(default, str) else str(default)
        assert rows[name] == expected, f"{spec.name} ({lang}): {name} default drifted"


@pytest.mark.parametrize("lang", LANGS)
def test_required_inputs_are_documented(spec: IndicatorSpec, lang: str) -> None:
    text = doc_path(spec.name, lang).read_text(encoding="utf-8")
    expected = ", ".join(f"`{field}`" for field in spec.inputs)
    assert f"**{'Required inputs' if lang == 'en' else 'Gerekli girdiler'}:** {expected}" in text


@pytest.mark.parametrize("lang", LANGS)
def test_every_doc_with_a_reference_links_to_it(spec: IndicatorSpec, lang: str) -> None:
    """Indicators that cite an external source must link to it; the rest must
    not carry a stray link (nothing to attribute)."""
    text = doc_path(spec.name, lang).read_text(encoding="utf-8")
    if spec.url is None:
        assert "## Reference" not in text and "## Kaynak" not in text
    else:
        assert spec.url in text


@pytest.mark.parametrize("lang", LANGS)
def test_indexes_list_every_indicator(lang: str) -> None:
    text = (DOCS / lang / "index.md").read_text(encoding="utf-8")
    for spec in iter_specs():
        assert f"indicators/{spec.name}.md" in text, f"{spec.name} missing from {lang} index"


@pytest.mark.parametrize("lang", LANGS)
def test_internal_links_resolve(lang: str) -> None:
    """Broken relative links are invisible until a reader hits a 404 on GitHub."""
    for path in (DOCS / lang).rglob("*.md"):
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


def test_readmes_link_every_indicator() -> None:
    for readme, lang in (("README.md", "en"), ("README.tr.md", "tr")):
        text = (ROOT / readme).read_text(encoding="utf-8")
        for spec in iter_specs():
            assert f"docs/{lang}/indicators/{spec.name}.md" in text, f"{spec.name} in {readme}"
