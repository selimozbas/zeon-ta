"""Render the English and Turkish indicator documentation.

Run with ``python tools/gen_docs.py``; pass ``--check`` to verify the committed
files are up to date without writing anything, which is what CI and
``tests/test_docs.py`` do.

Only prose comes from :mod:`docs_content`. Parameter tables and output column
names are read from the indicator registry, and every example is a real callable
that is invoked against the test fixture — the snippet shown in the docs is
recovered from that same callable's source, so the code you read and the output
you read cannot disagree, and neither can drift away from the library.
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

LABELS = {
    "en": {
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
        "other_lang": "Türkçe",
        "back": "All indicators",
        "none": "None.",
        "note": (
            "Examples run against the 300-bar OHLCV fixture in `tests/data/ohlcv.csv`, loaded as "
            "`df`. The output shown is the real output."
        ),
    },
    "tr": {
        "measures": "Ne ölçer",
        "formula": "Formül",
        "params": "Parametreler",
        "returns": "Döndürdükleri",
        "usage": "Kullanım",
        "reading": "Nasıl okunur",
        "pitfalls": "Dikkat edilmesi gerekenler",
        "reference": "Kaynak",
        "param": "Parametre",
        "default": "Varsayılan",
        "column": "Kolon",
        "inputs": "Gerekli girdiler",
        "accessor": "Accessor biçimi",
        "source": "Formül kaynağı",
        "other_lang": "English",
        "back": "Tüm indikatörler",
        "none": "Yok.",
        "note": (
            "Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV "
            "fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır."
        ),
    },
}

CATEGORY_TITLES = {
    "foundations": ("Foundations", "Temeller"),
    "moving_averages": ("Moving Averages", "Hareketli Ortalamalar"),
    "oscillators": ("Oscillators", "Osilatörler"),
    "volume": ("Volume", "Hacim"),
    "volatility": ("Volatility", "Oynaklık"),
    "trend": ("Trend Systems", "Trend Sistemleri"),
    "advanced": ("Advanced Tools", "İleri Seviye Araçlar"),
    "statistics": ("Statistics", "İstatistik"),
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


def parameter_table(spec: IndicatorSpec, lang: str) -> list[str]:
    labels = LABELS[lang]
    if not spec.params:
        return [f"_{labels['none']}_", ""]
    lines = [f"| {labels['param']} | {labels['default']} |", "| --- | --- |"]
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


def render(spec: IndicatorSpec, lang: str, examples: list[tuple[str, str]]) -> str:
    doc = CONTENT[spec.name]
    labels = LABELS[lang]
    other = "tr" if lang == "en" else "en"

    lines = [
        f"# {doc[f'title_{lang}']}",
        "",
        f"[← {labels['back']}](../index.md) · "
        f"[{labels['other_lang']}](../../{other}/indicators/{spec.name}.md)",
        "",
        f"`zeonta.{spec.name}()` — {spec.summary}",
        "",
        f"## {labels['measures']}",
        "",
        doc[f"about_{lang}"],
        "",
        f"## {labels['formula']}",
        "",
        "```text",
        doc[f"formula_{lang}"],
        "```",
        "",
        f"## {labels['params']}",
        "",
        f"**{labels['inputs']}:** " + ", ".join(f"`{field}`" for field in spec.inputs),
        "",
    ]
    lines += parameter_table(spec, lang)
    lines += [f"## {labels['returns']}", "", f"| {labels['column']} |", "| --- |"]
    lines += [f"| `{name}` |" for name in output_columns(spec)]
    lines += [
        "",
        f"## {labels['usage']}",
        "",
        labels["note"],
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
        f"**{labels['accessor']}:** `df.zta.{spec.name}(...)`",
        "",
        f"## {labels['reading']}",
        "",
        doc[f"reading_{lang}"],
        "",
        f"## {labels['pitfalls']}",
        "",
        doc[f"pitfalls_{lang}"],
    ]
    if spec.url is not None:
        lines += [
            "",
            f"## {labels['reference']}",
            "",
            f"{labels['source']}: [{spec.url}]({spec.url})",
        ]
    return "\n".join(lines).rstrip() + "\n"


def render_index(lang: str) -> str:
    labels = LABELS[lang]
    other = "tr" if lang == "en" else "en"
    heading = "Indicator Reference" if lang == "en" else "İndikatör Referansı"
    intro = (
        "Every indicator in `zeon-ta`, grouped by module. A few indicators additionally "
        "link to the external source their formula was verified against — see "
        "[methodology.md](methodology.md) for how that verification is done."
        if lang == "en"
        else "`zeon-ta` içindeki tüm indikatörler, modüllere göre gruplanmıştır. Birkaç "
        "indikatör, formülünün doğrulandığı dış kaynağa ek olarak bağlantı verir — bu "
        "doğrulamanın nasıl yapıldığı için bkz. [methodology.md](methodology.md)."
    )
    header = "| Indicator | Summary |" if lang == "en" else "| İndikatör | Özet |"
    lines = [f"# {heading}", "", f"[{labels['other_lang']}](../{other}/index.md)", "", intro, ""]
    for category, (title_en, title_tr) in CATEGORY_TITLES.items():
        specs = [spec for spec in iter_specs() if spec.category == category]
        if not specs:
            continue
        lines += [f"## {title_en if lang == 'en' else title_tr}", "", header, "| --- | --- |"]
        for spec in specs:
            title = CONTENT[spec.name][f"title_{lang}"]
            lines.append(f"| [`{spec.name}`](indicators/{spec.name}.md) | {title} |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


README_INTRO = {
    "en": """# zeon-ta

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

## Indicators

{tables}

### Cross-asset utilities (outside the registry)

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
[docs/en/methodology.md](docs/en/methodology.md) for how a formula gets
verified before it's implemented. This project follows a
[Code of Conduct](CODE_OF_CONDUCT.md); see [SECURITY.md](SECURITY.md) to
report a vulnerability privately.

## License

GPL-3.0-or-later — see [LICENSE](LICENSE).
""",
    "tr": """# zeon-ta

[![CI](https://github.com/selimozbas/zeon-ta/actions/workflows/ci.yml/badge.svg)](https://github.com/selimozbas/zeon-ta/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](pyproject.toml)
[![Lisans](https://img.shields.io/github/license/selimozbas/zeon-ta)](LICENSE)

**English: [README.md](README.md)**

Python için teknik analiz — RSI'dan causal bir cross-wavelet lead-lag
dönüşümüne kadar. Standart indikatör setinin yanında zeon-ta, daha yeni ve
akademik kaynaklı araçlar da içerir — Ehlers'in döngü-analizi filtreleri,
Hurst üsteli, dalgacık tabanlı gürültü giderme ve çok ölçekli oynaklık,
varlıklar-arası bir lead-lag dönüşümü — her biri bir halk anlatısı
formülüne değil, geldiği belirli makaleye dayanır.

Formüller, mevcut olduğunda standart ve yaygın olarak yayımlanmış teknik
analiz tanımlarını izler. Bir formülün kaynağı kendi akademik makalesi
olduğunda, ya da bir aday indikatörün kaynaklar arasında tek bir mutabık
formülü olmadığı ortaya çıktığında, docstring hangisinin ve nedenini
söyler.

## Neden bir TA kütüphanesi daha

- **Klasik ve modern, ikisi de formülü doğrulanmış.** İster RSI olsun
  ister bir MODWT dalgacık-varyans ayrıştırması, her indikatör formülünün
  neye karşı doğrulandığını belirtir; kaynaklar arasında tek bir mutabık
  formülü olmayan bir aday indikatör tahmin edilmek yerine doğrudan
  reddedilir (her iki durumda da [CHANGELOG.md](CHANGELOG.md)'de
  belgelenir).
- **Derleme adımı yok.** Her bağımlılık önceden derlenmiş wheel olarak gelir,
  bu yüzden `pip install` her yerde sorunsuz çalışır — ARM Mac'ler ve ince
  konteynerler dâhil.
- **Tek sözleşme, tüm indikatörler.** `Series`, dizi ya da liste verin; index'iniz
  korunmuş ve girdinizle aynı uzunlukta pandas nesnesi alın. Isınma barları
  kırpılmaz, `NaN` kalır; böylece geriye dönük testin altından hiçbir şey sessizce
  kaymaz.
- **İki çağırma biçimi.** Fonksiyonel API ve tam olarak aynı koda yönlenen `.zta`
  DataFrame accessor'ı — eşitlikleri gelenekle değil, testlerle doğrulanır.
- **Dürüst dokümantasyon.** Her indikatörün sayfası, hangi çıktının geleceğe bakma
  bilgisi içerdiği ve buna karşı ne yapılacağı dâhil, tuzaklarını açıkça yazar.
- **Varsayılan değil, ölçülmüş performans.** Her indikatör 1M bar'a kadar
  ölçülür; gerçek sayılar ve yöntem [BENCHMARKS.md](BENCHMARKS.md) içinde —
  çoğu bu ölçekte bile düşük milisaniyelerde tamamlanır.

## Kurulum

Henüz PyPI'de değil — doğrudan GitHub'dan kurun:

```bash
pip install git+https://github.com/selimozbas/zeon-ta.git
```

Ya da klonlayıp yerel olarak kurun:

```bash
git clone https://github.com/selimozbas/zeon-ta.git
cd zeon-ta
pip install .
```

Python 3.12+ gerektirir.

## Hızlı başlangıç

```python
import pandas as pd
import zeonta

df = pd.read_csv('ohlcv.csv', parse_dates=['date']).set_index('date')

# Fonksiyonel
rsi = zeonta.rsi(df['close'], length=14)
bands = zeonta.bbands(df['close'], length=20, std=2)

# Accessor — birebir aynı sonuç
rsi = df.zta.rsi(length=14)
trend = df.zta.supertrend(length=10, multiplier=3)

# Mevcut her şeyi listele
print(zeonta.list_indicators())
```

Daha fazlası için, gömülü bir örnek veri setine karşı doğrudan çalıştırılabilen
[examples/](examples/) dizinine bakın.

## Çıktı sözleşmesi

| Girdi | Çıktı |
| --- | --- |
| `pd.Series` | Aynı index'e sahip `Series` / `DataFrame` |
| `np.ndarray` veya `list` | `RangeIndex`'li `Series` / `DataFrame` |

Tek çizgili indikatörler isimlendirilmiş bir `Series`, çok çizgili olanlar ise
kolon adlarında kullanılan ayarları taşıyan bir `DataFrame` döndürür (`RSI_14`,
`MACD_12_26_9`, `SUPERT_10_3.0`). `ichimoku` ayrıca bulutun son barın ötesine
düşen kısmını atmak yerine ek olarak döndürür.

## İndikatörler

{tables}

### Varlıklar-arası araçlar (registry dışında)

`zeonta.cross_asset.wavelet_lead_lag(close_a, close_b, period=20)`, *iki
bağımsız* fiyat serisini karşılaştırır — seçilen bir zaman ölçeğinde
hangisinin diğerine öncülük ettiğini ve ne kadar — causal bir Morlet
Cross-Wavelet Dönüşümü ile (Torrence & Compo, 1998). `list_indicators()`'da
veya `.zta` accessor'ında yer almaz: kayıtlı her indikatör tek bir varlığın
kendi OHLCV kolonlarını varsayar, ikinci bağımsız bir seri bu sözleşmeye
uymaz. Doğrudan import edip çağırın; tam yöntem ve belgelenmiş bir gecikme
tahmini uyarısı için kendi docstring'ine bakın.

## Geliştirme

```bash
pip install -e ".[dev]"
pytest                      # test paketi
ruff check . && mypy src/   # lint ve tip kontrolü
python tools/gen_docs.py    # dokümanları yeniden üret
```

Dokümantasyon üretilir: metinler `tools/docs_content.py` içinde yaşar; parametre
tabloları, kolon adları ve örnek çıktılar ise doğrudan koddan ve her örneğin
fiilen çalıştırılmasından alınır. Commit'lenmiş dosyalar saparsa bir test
başarısız olur.

Tam iş akışı için bkz. [CONTRIBUTING.md](CONTRIBUTING.md); bir formülün
uygulanmadan önce nasıl doğrulandığı için bkz.
[docs/tr/methodology.md](docs/tr/methodology.md). Bu proje bir
[Davranış Kuralları](CODE_OF_CONDUCT.md) belgesine sahiptir; bir güvenlik
açığını gizli olarak bildirmek için bkz. [SECURITY.md](SECURITY.md).

## Lisans

GPL-3.0-or-later — bkz. [LICENSE](LICENSE).
""",
}


def render_readme(lang: str) -> str:
    header = (
        "| Indicator | What it does | Docs |"
        if lang == "en"
        else ("| İndikatör | Ne yapar | Doküman |")
    )
    docs_label = "docs" if lang == "en" else "doküman"
    blocks: list[str] = []
    for category, (title_en, title_tr) in CATEGORY_TITLES.items():
        specs = [spec for spec in iter_specs() if spec.category == category]
        if not specs:
            continue
        heading = title_en if lang == "en" else title_tr
        blocks += [f"### {heading}", "", header, "| --- | --- | --- |"]
        for spec in specs:
            title = CONTENT[spec.name][f"title_{lang}"]
            link = f"docs/{lang}/indicators/{spec.name}.md"
            blocks.append(f"| `{spec.name}` | {title} | [{docs_label}]({link}) |")
        blocks.append("")
    return README_INTRO[lang].replace("{tables}", "\n".join(blocks).rstrip())


def build() -> dict[Path, str]:
    """Every documentation file mapped to the content it should hold."""
    files: dict[Path, str] = {}
    files[ROOT / "README.md"] = render_readme("en")
    files[ROOT / "README.tr.md"] = render_readme("tr")
    evaluated = {spec.name: evaluate(CONTENT[spec.name]["example"]) for spec in iter_specs()}
    for spec in iter_specs():
        for lang in ("en", "tr"):
            files[DOCS / lang / "indicators" / f"{spec.name}.md"] = render(
                spec, lang, evaluated[spec.name]
            )
    for lang in ("en", "tr"):
        files[DOCS / lang / "index.md"] = render_index(lang)
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
