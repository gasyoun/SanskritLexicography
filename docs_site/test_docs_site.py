"""The pwg_ru research-conventions site (ZettelkastenWiki pilot #2) must
publish the frontmatter-less convention docs into a harness-passing site
with real H1 titles and resolved cross-links. Skipped without the package."""

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

zk = pytest.importorskip("zettelkastenwiki")

from build_site import CONFIG, DOCS  # noqa: E402

from zettelkastenwiki import load_catalog, publish, testing  # noqa: E402


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    out = tmp_path_factory.mktemp("research_site")
    publish(CONFIG, out)
    return out


def test_invariant_harness(site):
    testing.run_all(site, CONFIG)


def test_all_docs_published(site):
    assert len(load_catalog(CONFIG)) == len(DOCS)


def test_titles_from_h1_not_filenames(site):
    # The defaults layer: every page has a real title from its # H1, none the
    # ugly filename stem.
    notes = load_catalog(CONFIG)
    stems = [n.slug for n in notes if n.title == Path(n.rel_path).stem]
    assert not stems, f"pages fell back to filename titles: {stems}"


def test_md_links_rewritten_to_working_cross_links(site):
    # `[label](JUDGE_POLICY.md)` in the source must become an on-site link.
    page = (site / "research" / "judge-ab" / "index.html").read_text(encoding="utf-8")
    assert "/SanskritLexicography/research/research/" in page, "no resolved cross-links"
    assert ".md\"" not in page, "a raw .md link leaked into the output"
