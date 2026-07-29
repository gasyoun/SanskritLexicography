#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""g5_card_render — how ONE G5 card's three panels are rendered (H1808).

MG, voting `g5_batch1v3_sheet.html` 28-07-2026, filed five defects. Three are
rendering defects this module owns; the other two (type scale, and the anatomy
colouring being unreachable outside csl-atlas) were fixed in the shared emitter,
csl-pyutil v0.6.0.

1. **«ṚV(Sā) I 165, 11 is not clickable? … All such entries are long ago
   clickable even at Cologne»** — and they already were, on OUR public article
   site: `pilot/build_article_site._render()` turns `<ls>` into a Cologne
   scan/edition link (via the `ls_resolver` port of Cologne's own
   `ls_service.dart`) with a `pwg_sources` bibliography tooltip. The sheet
   escaped everything into `<pre>` instead, so 69 of 150 cards printed
   `&lt;ls&gt;…` as literal text. The print panel now goes through that same
   renderer — the sheet shows what the site shows.

2. **«не понятно, чем Русский перевод … отличается от Разметка store»** —
   measured: on 50 of 150 cards the two panels were textually IDENTICAL, differing
   only by the Cyrillic highlight, because the print panel's only transformation
   was `<ab>` → Russian and those cards carry no `<ab>`. They are now
   categorically different surfaces: panel 1 is the rendered print view, panel 2
   is the raw store markup *colour-coded by part class* (`csl_pyutil.anatomy`).
   Headings say what each is FOR, and a card whose two panels still carry the
   same text says so in one muted line rather than leaving the reader to diff.

3. **«почему аббревиатуры без tooltips? например [Gen, unsp] не очевидно что
   это»** — `<ab>` tokens did get tooltips; the NWS layer's bracketed
   `[diasystem, domain]` tags never did, because they are not markup at all, just
   text. Both slots are now glossed here in Russian from a MEASURED vocabulary —
   `nws_tag_census.py` over the whole scraped NWS corpus (34,101 lemma cards
   carrying 48,214 tagged senses), not over our translation slice and not from
   `nws_split.DIASET`, which is a token-peeling helper rather than an attested
   vocabulary. Using it as one produced two wrong tooltips; see `DIASYSTEM_RU`.

   That census also surfaced a data defect worth its own look: 12 rows carry
   `без уточн.` and 2 carry `Мед.` — the tag itself translated into Russian in a
   handful of rows while 153/28 stayed Latin. Machine-readable tags should not be
   half-translated; logged in the handoff, not repaired here.

The one thing NOT fixed here: NWS-layer citations that carry no `<ls>` markup at
all (`ṚV(Sā) I 165, 11` is one). Their sigla use a different convention from
PWG's own (`ṚV(Sā) I 165, 11` vs `ṚV. 1,165,11`), so `ls_resolver` returns None.
Across this batch there are exactly 3 such spans on 3 of 150 cards, so they are
MARKED as citations with a source tooltip and left unlinked rather than guessed
at — honest gap over a fabricated link. Normalising the NWS citation convention
store-side is H1809.
"""
import io
import os
import re
import sys

from csl_pyutil import anatomy, mark_cyrillic

HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (HERE, os.path.join(HERE, "pilot")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pwg_sources                                    # noqa: E402  <ls> siglum -> full title
from build_article_site import _render as site_render  # noqa: E402  the canonical renderer

# --------------------------------------------------------------------- NWS bracket tags
#: Slot 1 of an NWS `[X, Y]` tag — the diasystem (tradition the sense belongs to).
#:
#: MEASURED, not guessed (H1847, `nws_tag_census.py` over the scraped NWS corpus).
#: The first version of this map was copied from `nws_split.DIASET` — a helper for
#: PEELING a leading token, not an attested vocabulary — and carried six values
#: (`Class`, `Epic`, `Gramm`, `Lex`, `Skt`, `Pkt`) that never occur, while
#: glossing `Śā` as "шайва". The census refutes that gloss: `Śā` is the ONLY
#: diasystem whose senses carry subject domains (Soc, Ling, Med, Al, Math, Art,
#: Bio, Astr), which is śāstra — technical/scientific literature — not Śaiva;
#: tantric material has its own tag, `Tan`. Nine values, in frequency order.
#: Glosses are Russian because the only surface rendering them is a Russian sheet.
DIASYSTEM_RU = {
    "Śā": "шастра — научно-техническая литература",
    "Ved": "ведийское",
    "Gen": "общеупотребительное (вне конкретной традиции)",
    "Buddh": "буддийское",
    "Epigr": "эпиграфика (надписи)",
    "Tan": "тантрическое",
    "Reg": "региональное / местное употребление",
    "Kāv": "кавья (поэзия)",
    "Jin": "джайнское",
    "Ep": "эпическое",
}

#: Slot 2 — the subject domain. `unsp` (153 of 202 occurrences store-wide) is the
#: default "not specified", which is exactly what MG could not guess from `[Gen, unsp]`.
DOMAIN_RU = {
    "unsp": "домен не указан (unspecified)",
    "без уточн.": "домен не указан (unspecified)",
    "Soc": "общественные отношения",
    "Ling": "лингвистика / грамматика",
    "Phil": "философия",
    "Med": "медицина",
    "Мед.": "медицина",
    "Rit": "ритуал",
    "Al": "алхимия",
    "Poe": "поэтика",
    "Art": "искусство / ремесло",
    "Math": "математика",
    "Bio": "биология (растения, животные)",
    "Mat": "материалы / вещества",
    "Astr": "астрономия / астрология",
    # 119 senses, all under Gen. Almost certainly "эпическое" as a DOMAIN,
    # but the corpus also has Ep as a DIASYSTEM, so the reading is not
    # settled — say so rather than guess twice in one map (H1847).
    "Epi": "Epi — значение не установлено (119 значений, все при Gen)",
}

#: What the domain slot MEANS, for the legend — the striking fact the census
#: turned up (H1847): the domain is essentially a **śāstra** classification.
#: `Ved`, `Epigr`, `Tan`, `Reg`, `Jin` are 100% `unsp`; `Śā` is the near-inverse,
#: only ~1% `unsp`. So «домен не указан» on a Vedic sense is not a gap in the
#: data — that dimension simply does not apply to that tradition.
DOMAIN_NOTE_RU = (
    "Домен — предметная область (шастра). Он заполнен почти только у Śā "
    "(шастровая литература); у Ved / Epigr / Tan / Reg / Jin он всегда «unsp», "
    "то есть измерение к этой традиции просто не применяется, а не «данных нет»."
)

#: `[ifc (Bhvr)]`-style positional tags: where in a compound the word stands.
POSITION_RU = {
    "ifc": "in fine compositi — в конце сложного слова",
    "iic": "in initio compositi — в начале сложного слова",
    "ibc": "in bahuvrīhi compositi — в составе бахуврихи",
    "Bhvr": "бахуврихи (притяжательное сложное слово)",
    "Tatp": "татпуруша",
    "Dvandva": "двандва",
    "Karmadh": "кармадхарая",
}

_BRACKET_TAG = re.compile(
    r"\[(?P<a>[A-ZĀŚa-z][\wĀāŚśṢṣṚṛñ.]{0,10})\s*,\s*(?P<b>[^\]\[]{1,24})\]")
_BRACKET_POS = re.compile(r"\[(?P<inner>[a-zA-Z]{2,4}(?:\s*\([A-Za-z]+\))?)\]")
_BRACKET_NWS = re.compile(r"\[NWS:\s*(?P<src>[^\]]+)\]")
_TAG_SPLIT = re.compile(r"(<[^>]+>)")


def _norm(tok):
    return (tok or "").strip().rstrip(".")


def _abbr(visible, title):
    return '<abbr class="nwstag" title="%s">%s</abbr>' % (
        title.replace('"', "&quot;"), visible)


def _gloss_bracket(m):
    """`[Ved, unsp]` -> the same text with a Russian hover gloss for both slots."""
    a, b = m.group("a"), m.group("b").strip()
    ga = DIASYSTEM_RU.get(_norm(a))
    # a `(s.v. X)` suffix on slot 2 points at the entry the NWS note hangs off
    sv = ""
    core = b
    msv = re.match(r"(?P<head>[^(]+)\((?P<sv>s\.v\.[^)]*)\)\s*$", b)
    if msv:
        core, sv = msv.group("head").strip(), msv.group("sv").strip()
    gb = DOMAIN_RU.get(core) or DOMAIN_RU.get(_norm(core))
    if not ga and not gb:
        return m.group(0)
    bits = ["%s — %s" % (a, ga or "диасистемная помета"),
            "%s — %s" % (core, gb or "домен")]
    if sv:
        bits.append("%s — статья, к которой относится помета" % sv)
    return _abbr(m.group(0), "; ".join(bits))


def _gloss_position(m):
    inner = m.group("inner")
    parts = re.match(r"(?P<k>[a-zA-Z]+)(?:\s*\((?P<sub>[A-Za-z]+)\))?$", inner.strip())
    if not parts:
        return m.group(0)
    k, sub = parts.group("k"), parts.group("sub")
    if k not in POSITION_RU:
        return m.group(0)
    title = POSITION_RU[k]
    if sub and sub in POSITION_RU:
        title += "; %s — %s" % (sub, POSITION_RU[sub])
    return _abbr(m.group(0), title)


def _gloss_nws(m):
    return _abbr(m.group(0),
                 "NWS — слой «Nachträge»: источник добавления и страница (%s). "
                 "Это провенанс пометы, а не цитата из текста." % m.group("src").strip())


# --------------------------------------------------------------------- bare citations
#: A citation-shaped span: siglum + locus, e.g. `ṚV(Sā) I 165, 11`. Only spans
#: whose siglum resolves in PWG's own 2,681-entry bibliography are marked, so
#: ordinary prose is never dressed up as a citation.
_BARE_CIT = re.compile(
    r"(?P<sig>[A-ZĀĪŪṚṜṆṬḌŚṢḤṂÑṄ][^\s\[\]{}<>]{0,14}?)"
    r"(?P<rec>\s*\([^)]{1,8}\))?"
    r"\s+(?P<loc>(?:[IVXLC]+|\d+)[\d,\s;.]*\d)")


def _bare_citation_html(m):
    sig = _norm(m.group("sig"))
    src = None
    for cand in (pwg_sources.source_key(sig + "."), sig):
        if not cand:
            continue
        try:
            src = pwg_sources.resolve(cand)
        except Exception:
            src = None
        if src:
            break
    if not src:
        return m.group(0)
    # first sentence only — pwgbib entries run to a full bibliographic paragraph,
    # and a tooltip that long is unreadable at hover size
    short = re.split(r"(?<=[.!?])\s", src.strip(), maxsplit=1)[0].rstrip(".")
    title = ("%s — %s. Ссылки нет: в этом слое цитата не размечена тегом ls, "
             "а её сиглы не в конвенции PWG (H1809)." % (sig, short))
    return '<span class="barecit" title="%s">%s</span>' % (
        title.replace('"', "&quot;"), m.group(0))


#: Elements whose CONTENT is already a resolved citation / abbreviation / gloss.
#: Their inner text is still a text node, so a naive tag-skipping walk would
#: happily re-mark a linked `<a class=ls>ṚV. 1,165,11</a>` as an *unlinked* bare
#: citation — 65 of 150 cards did exactly that on the first run.
_PROTECTED = re.compile(
    r"<a\b[^>]*>.*?</a>|<abbr\b[^>]*>.*?</abbr>|<span class=ls[^>]*>.*?</span>",
    re.S)


def _on_text_nodes(html_text, fn):
    """Apply `fn` to the text between tags only, never inside a tag."""
    parts = _TAG_SPLIT.split(html_text)
    for i, part in enumerate(parts):
        if not part.startswith("<"):
            parts[i] = fn(part)
    return "".join(parts)


def annotate(html_text, *, bare_citations=True):
    """Gloss the NWS bracket tags (and optionally mark unlinked citations) in
    already-rendered HTML — on text nodes only, and never inside an element that
    already carries a citation/abbreviation meaning."""
    def fn(chunk):
        chunk = _BRACKET_NWS.sub(_gloss_nws, chunk)
        chunk = _BRACKET_TAG.sub(_gloss_bracket, chunk)
        chunk = _BRACKET_POS.sub(_gloss_position, chunk)
        if bare_citations:
            chunk = _BARE_CIT.sub(_bare_citation_html, chunk)
        return chunk

    out, last = [], 0
    for m in _PROTECTED.finditer(html_text):
        out.append(_on_text_nodes(html_text[last:m.start()], fn))
        out.append(m.group(0))            # already meaningful — leave alone
        last = m.end()
    out.append(_on_text_nodes(html_text[last:], fn))
    return "".join(out)


# --------------------------------------------------------------------- the three panels
PANEL_PRINT = "1 · Печатный вид — это и оценивается"
PANEL_STORE = "2 · Та же строка в разметке store — цвета = части статьи, отсюда копировать в заметку"
PANEL_DE = "3 · Немецкий источник (de), та же разметка"

#: Which anatomy classes a PWG card can actually show — the legend lists only these.
PWG_LEGEND_PARTS = ["sanskrit", "gloss", "citation", "grammar", "abbreviation",
                    "homonym", "structure"]


def print_panel(ru_text):
    """Panel 1 — the RU sense as PRINT will show it, through the same renderer the
    public article site uses: `<ls>` becomes a Cologne link with a bibliography
    tooltip, `<ab>` its Russian equivalent with the German/English expansion in
    the tooltip, `{#…#}` italic IAST. Russian words are highlighted (V7)."""
    rendered = site_render(ru_text or "", "html", "ru")
    return '<div class="printview">%s</div>' % annotate(mark_cyrillic(rendered))


def store_panel(ru_text):
    """Panel 2 — the same line as RAW STORE MARKUP, colour-coded by part class so
    it cannot be mistaken for panel 1. This is the text to quote in a note."""
    return anatomy.highlight(ru_text or "", plain_hook=_anatomy_plain)


def de_panel(de_text):
    """Panel 3 — the German source, same colouring, so the reviewer compares like
    with like."""
    return anatomy.highlight(de_text or "(store row not found)", plain_hook=_anatomy_plain)


def _anatomy_plain(chunk):
    """anatomy's plain_hook: the NWS bracket tags and unmarked citations live in
    the UNTAGGED runs, which the colouring would otherwise pass through as prose."""
    import html as _html
    escaped = _html.escape(chunk)
    out = annotate(escaped)
    if out == escaped:
        return None                     # nothing to add — let anatomy style it
    return '<span style="color:#d8dce2">%s</span>' % out


def same_text(ru_text):
    """True when panel 1 and panel 2 would read the same, i.e. the store markup
    carries nothing this card's print view transforms. 50 of the 150 cards in
    batch1v3 were in this state, which is what made the two panels look redundant."""
    stripped = re.sub(r"<[^>]+>", "", site_render(ru_text or "", "html", "ru"))
    raw = re.sub(r"\s+", " ", (ru_text or "").replace("¦", "")).strip()
    return re.sub(r"\s+", " ", stripped).strip() == raw


EXTRA_CSS = """  .printview { line-height:1.6; }
  .printview a.ls { color:#7fb2ff; text-decoration:underline dotted; text-underline-offset:3px; }
  .printview span.ls { color:#9aa0aa; border-bottom:1px dotted #5c6773; }
  .printview span.ab { color:#c9a227; border-bottom:1px dotted #5c6773; cursor:help; }
  .printview i.sa { color:#e6c07b; font-style:italic; }
  abbr.nwstag { border-bottom:1px dashed #7f8c9b; text-decoration:none; cursor:help; }
  span.barecit { border-bottom:1px dotted #e06c75; color:#e06c75; cursor:help; }
  .panelnote { color:#9aa0aa; font-style:italic; margin-top:6px; }
"""


def legend_html():
    """One legend for the whole sheet (footer), not one per card."""
    return anatomy.legend_html(
        parts=PWG_LEGEND_PARTS,
        extra_chips=[("#7fb2ff", "цитата со ссылкой на Cologne"),
                     ("#e06c75", "цитата без ссылки — сиглы не в конвенции PWG"),
                     ("#7f8c9b", "помета NWS с пояснением при наведении")])


def _selftest():
    sys.stdout.reconfigure(encoding="utf-8")
    ok = True

    def check(cond, label):
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + label)
        ok = ok and bool(cond)

    # pwg_ab's abbreviation table and pwg_sources' bibliography both live in the
    # sibling csl-pywork checkout, which CI does not have. Their absence is a
    # supported degradation (no tooltip), not a failure — so gate exactly the
    # checks that need them and keep the rest of the lane meaningful.
    import pwg_ab
    have_ab = bool(pwg_ab.table())
    try:
        have_bib = bool(pwg_sources.bib())
    except Exception:
        have_bib = False

    def check_if(available, cond, label, why):
        if available:
            return check(cond, label)
        print("  skip " + label + "  (" + why + ")")

    ls = "<ab>Vgl.</ab> {#anApta#}. — <ab>caus.</ab> {#Apayati#}\n<ls>P. 6,4,57.</ls>"
    p = print_panel(ls)
    check("<a class=ls" in p, "<ls> renders as a Cologne link, not escaped markup")
    check("ashtadhyayi" in p or "href=" in p, "the link carries a resolved href")
    # the Cyrillic highlight wraps the word but not its period, so match the run
    check_if(have_ab, ">ср<" in p and "Vergleiche" in p,
             "<ab>Vgl.</ab> shows its Russian equivalent, German in the tooltip",
             "pwgab table absent — csl-pywork not checked out")
    check_if(have_ab, "\xa0" in p,
             "unquoted title attributes stay nbsp-shielded (site convention)",
             "pwgab table absent")
    check("&lt;ls&gt;" not in p, "no escaped tag text leaks into the print view")

    nws = ("{#Adika#} [Ved, unsp] [ifc (Bhvr)] ṚV(Sā) I 165, 11 "
           "[NWS: Windisch 1883 : 106]")
    p = print_panel(nws)
    check("ведийское" in p, "[Ved, unsp] slot 1 is glossed")
    check("unspecified" in p, "[Ved, unsp] slot 2 (unsp) is glossed — MG's example")
    check("in fine compositi" in p, "[ifc (Bhvr)] is glossed")
    check("NWS —" in p, "[NWS: …] provenance is glossed")
    check_if(have_bib, 'class="barecit"' in p,
             "an unlinked citation is marked, not silently prose",
             "pwgbib bibliography absent — csl-pywork not checked out")

    linked = print_panel("<ls>P. 6,4,57.</ls> и <ls>MBH. 3, 12</ls>")
    check('class="barecit"' not in linked,
          "a citation that already resolved to a link is NOT re-marked as bare")
    check(linked.count("<a class=ls") == 2, "both resolved citations stay links")
    print("  (pwgab table %s · pwgbib bibliography %s)"
          % ("present" if have_ab else "ABSENT", "present" if have_bib else "ABSENT"))

    a = store_panel(ls)
    check('class="anatomy"' in a, "panel 2 is the colour-coded anatomy block")
    check(anatomy.PARTS["citation"][0] in a, "citations are tinted in panel 2")
    check("&lt;ls&gt;" in a, "panel 2 keeps the markup visible for quoting")

    check(same_text("тест без разметки") is True, "same_text: plain row reads alike")
    check(same_text(ls) is False, "same_text: a marked-up row does not")

    check("цитата со ссылкой" in legend_html(), "legend names the citation states")
    print("SELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(_selftest())
