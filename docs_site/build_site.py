"""Build the pwg_ru research-conventions site from docs_site/wiki/.

ZettelkastenWiki Wave-3 pilot #2 (consolidation angle): the scattered
editorial-convention and metrics docs under
RussianTranslation/research/ are published as one navigable knowledge site
(nav + search + SEO + cross-links) with **zero per-file frontmatter edits** —
using the v0.2.0 defaults layer:

- title_from_h1  → each doc's `# H1` becomes its page title
- source_filter  → repo-relative `[label](FILE.md)` links are rewritten to
  `[[FILE|label]]` so the package's stem resolver connects them into working
  on-site links (they were GitHub-relative and would 404 on a static site).

The docs are copied verbatim into docs_site/wiki/research/ (rebuild with
`sync` below when the originals change). Build:

    python docs_site/build_site.py [out_dir]
    python docs_site/build_site.py --sync     # re-copy the 10 source docs
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

from zettelkastenwiki import GroupSpec, SiteConfig, publish

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SOURCE = REPO / "RussianTranslation" / "research"
DOCS = [
    "HANDOFF_apparatus_conventions.md",
    "HANDOFF_microstructure_conventions.md",
    "HANDOFF_sense_ordering.md",
    "JUDGE_AB.md",
    "JUDGE_POLICY.md",
    "ROOT_ENTRY_ARCHITECTURE.md",
    "cross_dict_metrics.md",
    "merge_BU.md",
    "sense_order_metrics.md",
    "README.md",
]

# Stems that exist as pages in this site — only rewrite links that resolve here.
_STEMS = {Path(d).stem for d in DOCS}
_MD_LINK = re.compile(r"\[([^\]]+)\]\(([./A-Za-z0-9_-]+?)\.md(?:#[^)]*)?\)")


def _rewrite_md_links(body: str) -> str:
    def repl(m: "re.Match[str]") -> str:
        label, target = m.group(1), m.group(2)
        stem = target.rsplit("/", 1)[-1]
        if stem in _STEMS:
            return f"[[{stem}|{label}]]"
        return label  # off-site repo doc → keep the text, drop the dead link
    return _MD_LINK.sub(repl, body)


CONFIG = SiteConfig(
    base_url="https://gasyoun.github.io/SanskritLexicography/research",
    site_name="pwg_ru — research conventions",
    org_name="SanskritLexicography",
    org_url="https://github.com/gasyoun/SanskritLexicography",
    author="Mārcis Gasūns",
    language="en",
    wiki_root=HERE / "wiki",
    groups=(
        GroupSpec(name="research", nav_label="Research", home_style="cards", jsonld_type="article"),
    ),
    title_from_h1=True,
    source_filter=_rewrite_md_links,
    seo_title_suffix=" — pwg_ru research",
    default_cta_primary=("Repository", "https://github.com/gasyoun/SanskritLexicography"),
    home_title="pwg_ru research conventions & metrics",
    home_description=(
        "Editorial-convention and metrics studies behind the pwg_ru Russian "
        "translation layer: apparatus, microstructure, sense ordering, judge policy."
    ),
    footer_extra_html='<a href="https://github.com/gasyoun/SanskritLexicography">GitHub</a>',
)


def sync() -> None:
    dest = HERE / "wiki" / "research"
    dest.mkdir(parents=True, exist_ok=True)
    for name in DOCS:
        src = SOURCE / name
        if src.exists():
            shutil.copyfile(src, dest / name)
    print(f"Synced {len(DOCS)} docs verbatim into {dest}")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if "--sync" in sys.argv:
        sync()
        sys.exit(0)
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "_site"
    publish(CONFIG, out)
    print(f"Research site built at {out}")
