#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_reglue_sheet_v2.py — the H180 re-glue spot-check vote, rebuilt (H2827).

Why v2
------
The v1 sheet (`build_h180_review_sheets.py::build_reglue`) rendered each pilot
card as one undifferentiated ``<pre>`` blob of the generated ``reglue/<key1>.md``
and asked a single question — "is this re-glue well-formed?". Three defects,
all raised on the published sheet
[h180_reglue.html](https://gasyoun.github.io/vote/sheets/h180_reglue.html):

1. **Citations were dead text.** Cologne's own PWG ls→href map
   (csl-lslink) was never joined, so ``<ls>MBH. 12,8081.</ls>`` rendered as
   prose. It is now a link; see [`ls_links.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_links.py).
2. **The glue typology was invisible.** ``[NWS·nws_at_sense]`` was a bare
   string; nothing told the reviewer that *nws_at_sense* is an **addition**
   while *restate* — 96 % of all supplements — is an **abridgement** that adds
   no meaning. The three axes already exist in
   [`ADDENDA_TYPOLOGY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/ADDENDA_TYPOLOGY.md);
   v2 renders them as chips and votes on them.
3. **Gloss chains read as broken Russian.** NWS separates sense clusters with a
   full stop, faithfully carried over from the German
   (``gehen, kommen, wandern. weggehen.`` → ``идти, приходить, странствовать.
   уходить.``). v2 splits the chain into numbered clusters for reading and keeps
   the source string verbatim in a raw panel — a display transform, never a
   store edit.

What a reviewer now decides per card: (a) approve/reject the **typology +
placement**, (b) rate 1–5 the **overall well-formedness**. Both signals export
in the standard ``/decisions-apply`` contract.

v3 (H2844) — two things MG asked for on the published v2
--------------------------------------------------------
**P1. The newline is not editorial.** Every store newline reached the print
view as a hard ``<br>``, so ``<ls>MBH. 12,8081.</ls>`` sat on its own line,
torn off the verse it sources. Measured: 24,103 of the store's 41,306 RU
citations (58.4 %) begin a line this way — the majority case. The wrap is
csl-orig's physical line-break of the printed PWG column and marks no
structure, so it is now collapsed **at render time** by
[`line_collapse.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/line_collapse.py);
the store is never touched and the raw panel proves it with a SHA-256 taken
before and after rendering (:func:`digest_guard`).

**P2. «How will the final card actually look?»** — one data source, two
renderings, one sheet-wide control:

===========  ===================  ==============================================
mode          reading              line policy
===========  ===================  ==============================================
expanded      etext / screen       each sense and supplement on its own line
compact       printed dictionary   senses run on; supplements inline behind
                                   their sense marker
===========  ===================  ==============================================

Both renderings are built from the same ``reglue/<key1>.json`` in the same
pass and shipped in the same document; the toggle is CSS-only (``:has()``), so
there is no way for one mode to drift from the other or for a reviewer to vote
on a card the sheet cannot show.

Inputs (local, untracked — point PWG_RU_DATA_ROOT at the tree that has them):
    <data>/src/pwg_ru_translated.jsonl
    <data>/pwg_ru/reglue/<key1>.json
Output (gitignored, published to the vote hub by hand):
    <data>/review/h180_reglue_v3_sheet.html
    <data>/review/h180_reglue_v3_sample.jsonl

Run: python src/build_reglue_sheet_v2.py
     python src/build_reglue_sheet_v2.py --selftest
"""
import sys, os, io, json, html, re, collections

from csl_pyutil import render_review_sheet, mark_cyrillic, anatomy
from review_binding import stamp, write_lock
from review_sheet_standard import standard_config, slp1_iast, pwg_entry_href, DA_RATING
from sheet_screening import screening_block
from ls_links import LsLinks, HIT, NO_LOCUS, MINTABLE
# H1646/H1808 legibility standard: reuse the g5 card renderer rather than
# re-escaping CDSL markup into a wall of text. print_panel is the canonical
# article-site render (<ls> -> Cologne link + bibliography tooltip, {#…#} ->
# italic IAST, Russian highlighted); EXTRA_CSS/legend_html come with it.
from g5_card_render import print_panel, EXTRA_CSS as G5_CSS, legend_html as g5_legend
# H2844 P1: which store newlines are the printed column's line-wrap (collapse)
# and which are structure (keep). Pure functions over the store string.
from line_collapse import COMPACT, EXPANDED, collapse, store_digest

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("PWG_RU_DATA_ROOT", os.path.dirname(HERE))
REGLUE_DIR = os.path.join(DATA, "pwg_ru", "reglue")
REVIEW = os.path.join(DATA, "review")
GENERATED = "2026-08-16"

ORDER = [("gA", 5), ("Cid", 5), ("Sam", 5), ("jIv", 5), ("rakz", 5), ("vraj", 5), ("yat", 5),
         ("DA", 4), ("Ap", 4), ("Bid", 4), ("Buj", 4), ("banD", 4), ("Sru", 4),
         ("viS", 3), ("siD", 3)]

# --------------------------------------------------------------------- typology
# The three axes of ADDENDA_TYPOLOGY.md §1, collapsed to what a reviewer must
# see on the card: does this supplement ADD meaning, merely RESTATE it more
# briefly, or CANCEL/CORRECT what PWG said?
#   subtype -> (op, direction, class, one-line gloss)
TYPOLOGY = {
    "nws_at_sense":     ("add",      "additive",  "adds",     "NWS adds meaning at this PWG sense"),
    "sch_star":         ("add",      "additive",  "adds",     "Schmidt adds a new sense (printed *)"),
    "derived_sense":    ("add",      "additive",  "adds",     "preverb / causative / desiderative sub-sense"),
    "foreign_fragment": ("add",      "additive",  "adds",     "supplement partly in EN / FR / LA, shown with its RU"),
    "a2a":              ("relocate", "additive",  "adds",     "Nachträge-to-Nachträge — a supplement to a supplement"),
    "restate":          ("restate",  "abridging", "restates", "PW says the same thing more briefly — NOT a new meaning"),
    "pw_correct":       ("correct",  "abridging", "cancels",  "PW changes a value (gender, form, reading) — overrides PWG"),
    "pw_cancels":       ("delete",   "abridging", "cancels",  "PW withdraws PWG material"),
}
CLASS_LABEL = {"adds": "＋ added meaning", "restates": "≈ restatement",
               "cancels": "✕ cancels / corrects"}

# --------------------------------------------------------------------- gloss chains
# NWS/SCH separate sense clusters with a full stop. Splitting on it is safe only
# away from these abbreviations, which legitimately end in a period mid-sentence.
ABBREV = ("т. е", "т. н", "и т. д", "и т. п", "напр", "ср", "см", "перен", "букв",
          "нар", "прил", "сущ", "гл", "мн", "ед", "вин", "род", "дат", "твор",
          "v. a", "s. v", "cf", "vgl", "resp", "Akk", "Dat", "Gen", "Instr", "Lok",
          "Abl", "Nom", "Voc", "Adj", "Adv", "Comp", "sc")
SPLIT_RE = re.compile(r"(?<=[а-яёA-Za-z\)\]])\.\s+(?=[а-яё\(\[«])")
#: never split straight after a Russian pronoun-clitic abbreviation
#: (``кому-л.``, ``что-л.``, ``каком-л.``) — the period is part of the token.
CLITIC_TAIL = re.compile(r"-л$", re.U)


SANSKRIT_SPAN = re.compile(r"\{[#%].*?[#%]\}", re.S)


def gloss_clusters(text):
    """Split a period-separated gloss chain into clusters. Display-only.

    NWS/SCH carry the German source's full stop between sense clusters, which
    reads as broken Russian (``странствовать. уходить.``). Splitting it is a
    *rendering* choice — the store string is never touched, and the raw card
    stays one panel away.

    Conservative by construction: a ``{#…#}`` / ``{%…%}`` Sanskrit span is masked
    first so its internal periods can never be split points; the split then fires
    only where a period is followed by a space and a *lowercase* Cyrillic letter
    or an opening bracket, and never directly after a known abbreviation.
    Citation-bearing bodies are left alone entirely — a link must not be torn out
    of the clause that sources it. Returns ``[]`` when the text is not a chain
    (fewer than two clusters), so the caller falls back to plain rendering.
    """
    if "<ls" in (text or ""):
        return []
    masked = SANSKRIT_SPAN.sub(lambda m: "\x00" * len(m.group(0)), text or "")
    out, last = [], 0
    for m in SPLIT_RE.finditer(masked):
        head = masked[last:m.start()]
        stem = head.rstrip()
        if any(stem.endswith(a) for a in ABBREV) or CLITIC_TAIL.search(stem):
            continue
        # never split inside an unclosed bracket — «(Lok или нар. места)» is one
        # parenthetical, not two clusters
        if (stem.count("(") != stem.count(")")
                or stem.count("[") != stem.count("]")):
            continue
        if len(head.strip()) >= 3:
            out.append(text[last:m.start()].strip())
            last = m.end()
    tail = text[last:].strip().rstrip(".").strip() if text else ""
    if tail:
        out.append(tail)
    return out if len(out) >= 2 else []


# --------------------------------------------------------------------- rendering
def esc(s):
    return html.escape("" if s is None else str(s))


#: additive to the g5 EXTRA_CSS — the typology chips and the citation-gap marks.
EXTRA_CSS = G5_CSS + """  .tchip { display:inline-block; padding:1px 7px; border-radius:9px;
    font-size:11px; font-weight:600; margin-right:4px; white-space:nowrap; }
  .t-adds { background:#173a22; color:#8fe3a8; border:1px solid #2f6b42; }
  .t-restates { background:#3a3117; color:#e6c07b; border:1px solid #6b5a2f; }
  .t-cancels { background:#3a1a1a; color:#e69a9a; border:1px solid #6b2f2f; }
  .t-meta { background:#23282f; color:#9aa0aa; border:1px solid #3a4048; }
  .sense { margin:0 0 14px 0; padding:8px 10px; border-left:3px solid #3a4048; }
  .sense > .hd { font-weight:700; color:#9aa0aa; margin-bottom:4px; }
  .supp { margin:7px 0 0 16px; padding:5px 9px; border-left:2px solid #3a4048; }
  .supp .body { margin-top:3px; }
  .clusters { margin:3px 0 0 18px; padding:0; }
  .clusters li { margin:2px 0; }
  .cov { font-size:12px; color:#9aa0aa; margin-bottom:10px; line-height:1.7; }
  .cov b { color:#d8dce2; }
  .printview span.ls sup { color:#e06c75; font-weight:700; }
""" + """
  /* ---- H2844 P2: one data source, two renderings, a CSS-only sheet toggle.
     Both renderings ship in the document; `:has()` picks which is displayed, so
     no script can leave the sheet showing a mode it did not render. */
  .render-compact { display:none; }
  body:has(#modecompact:checked) .render-expanded { display:none; }
  body:has(#modecompact:checked) .render-compact { display:block; }
  .modeswitch { display:inline-flex; align-items:center; gap:6px; margin-left:10px;
    padding:2px 10px; border:1px solid #3a4048; border-radius:12px; }
  .modeswitch input { accent-color:#7fb2ff; }
  .modeswitch label { cursor:pointer; color:#d8dce2; }
  /* compact = the printed dictionary column: senses run on, supplements sit
     inline behind the sense marker they belong to. */
  .cflow { line-height:1.75; }
  .cflow .cmark { color:#9aa0aa; font-weight:700; margin:0 4px 0 8px; }
  .cflow .csupp .tchip { font-size:10px; padding:0 5px; }
  .cflow .printview { display:inline; }
  .cflow h4 { display:inline; font-size:inherit; color:#9aa0aa; margin:0 6px 0 0; }
  .cflow .clusters { display:inline; list-style:none; margin:0; padding:0; }
  .cflow .clusters li { display:inline; }
  .cflow .clusters li::after { content:" · "; color:#5c6773; }
  .cflow .clusters li:last-child::after { content:""; }
"""

#: build_article_site renders an UNRESOLVED citation as `<span class=ls …>`
#: (attribute values deliberately unquoted). Mark it with WHY it is unresolved.
_UNRESOLVED_LS = re.compile(r"(<span class=ls[^>]*>)(.*?)(</span>)", re.S)
_TAGS = re.compile(r"<[^>]+>")


def _mark_gaps(html_body):
    """Append ⚑ (mintable) / ∅ (no locus) to each unresolved citation, and count."""
    stats = collections.Counter()

    def sub(m):
        visible = _TAGS.sub("", m.group(2))
        status = MINTABLE if re.search(r"\d", visible) else NO_LOCUS
        stats[status] += 1
        mark = "⚑" if status == MINTABLE else "∅"
        return "%s%s<sup>%s</sup>%s" % (m.group(1), m.group(2), mark, m.group(3))

    out = _UNRESOLVED_LS.sub(sub, html_body)
    stats[HIT] = out.count("<a class=ls ")
    return out, stats


def render_body(raw, mode=EXPANDED, nl=None):
    """One store body as the PRINT view, with unresolved citations marked.

    Goes through ``g5_card_render.print_panel`` — the same renderer the public
    article site uses — so ``<ls>`` arrives as a Cologne link with its full
    bibliographic tooltip, ``{#…#}`` as italic IAST, and Russian highlighted.
    A period-separated gloss chain is split into numbered clusters for reading
    (display only; the raw store string is one panel away).

    H2844 P1: the store's inherited column line-wraps are collapsed FIRST, so
    the citation reaches ``print_panel`` inside the clause that sources it
    instead of behind a ``<br>``. ``nl`` is an optional Counter that tallies
    how many wraps were collapsed and how many structural breaks kept.
    """
    text, n_col, n_kept = collapse(raw or "", mode)
    if nl is not None:
        nl["collapsed"] += n_col
        nl["kept"] += n_kept
    clusters = gloss_clusters(text)
    if clusters:
        inner = "".join("<li>%s</li>" % print_panel(c) for c in clusters)
        body = '<ol class="clusters">%s</ol>' % inner
    else:
        body = print_panel(text)
    return _mark_gaps(body)


#: `placement_reason` as a reviewer-facing chip (H2879 S6). Shown only when the
#: supplement is NOT placed, so a `restate` chip can never be read on its own as
#: a claim about some PWG sense (acceptance criterion A1).
PLACEMENT_REASON_LABEL = {
    "no_target_marker": "no target given",
    "out_of_range": "sense number above PWG's range",
    "not_found": "sense not found",
}


def _supp_head(sup):
    """The typology chips — identical in both renderings, so a reviewer voting
    in compact mode votes on the same classification they see in expanded."""
    subtype = sup.get("subtype", "?")
    op, direction, klass, gloss = TYPOLOGY.get(
        subtype, (sup.get("op", "?"), "?", "restates", "unclassified subtype"))
    lang = ' <span class="tchip t-meta">‹%s›</span>' % esc(sup["lang"]) if sup.get("lang") else ""
    cancels = (' <span class="tchip t-cancels">cancels PWG</span>'
               if sup.get("cancels") else "")
    why = PLACEMENT_REASON_LABEL.get(sup.get("placement_reason"))
    unplaced = (' <span class="tchip t-meta" title="the typology label says what '
                'kind of supplement this is; it does not assert a target sense">'
                'not placed: %s</span>' % esc(why)) if why else ""
    head = ('<span class="tchip t-%s" title="%s">%s</span>'
            '<span class="tchip t-meta">%s</span>'
            '<span class="tchip t-meta">%s · %s</span>%s%s%s'
            % (klass, esc(gloss), esc(CLASS_LABEL[klass]), esc(subtype),
               esc(sup.get("badge", "?")), esc(op), lang, cancels, unplaced))
    return head, klass


def render_supplement(sup, mode=EXPANDED, nl=None):
    head, klass = _supp_head(sup)
    body, stats = render_body(sup.get("ru", ""), mode, nl)
    if mode == COMPACT:
        return ('<span class="csupp"> %s %s</span>' % (head, body)), stats, klass
    return ('<div class="supp">%s<div class="body">%s</div></div>'
            % (head, body)), stats, klass


def render_card(key1, obj, mode=EXPANDED, nl=None):
    """Return (html, per-card stats) for one pilot headword in ONE rendering.

    Both renderings come from this function and the same ``obj`` — the compact
    column view is not a second data path, only a second line policy (H2844 P2).
    """
    ls_stats = collections.Counter()
    klass_stats = collections.Counter()
    chunks = []
    n_placed = n_new = 0
    compact = mode == COMPACT
    for hom in obj["homonyms"]:
        chunks.append("<h4>homonym %s</h4>" % esc(hom["h"]))
        for s in hom["senses"]:
            pwg_body, st = render_body(s.get("pwg_ru", ""), mode, nl)
            ls_stats += st
            if compact:
                block = ['<span class="csense"><span class="cmark">%s)</span>%s'
                         % (esc(s["sense"]), pwg_body)]
            else:
                block = ['<div class="sense"><div class="hd">PWG sense %s</div>%s'
                         % (esc(s["sense"]), pwg_body)]
            for sup in s["supplements"]:
                h, st2, kl = render_supplement(sup, mode, nl)
                ls_stats += st2
                klass_stats[kl] += 1
                n_placed += 1
                block.append(h)
            block.append("</span>" if compact else "</div>")
            chunks.append("".join(block))
        if hom["new_senses"]:
            chunks.append('<span class="csense"><span class="cmark">＋</span>'
                          if compact else
                          '<div class="sense"><div class="hd">'
                          '＋ new senses (no PWG sense to attach to)</div>')
            for sup in hom["new_senses"]:
                h, st2, kl = render_supplement(sup, mode, nl)
                ls_stats += st2
                klass_stats[kl] += 1
                n_new += 1
                chunks.append(h)
            chunks.append("</span>" if compact else "</div>")
    body = ('<div class="cflow">%s</div>' % "".join(chunks)) if compact \
        else "".join(chunks)
    cov = ('<div class="cov">citations: <b>%d</b> linked to Cologne · '
           '<b>%d</b> ⚑ mintable gap (locus, no target) · <b>%d</b> ∅ bare '
           'abbreviation (nothing to link)<br>supplements: <b>%d</b> placed at a PWG '
           'sense · <b>%d</b> new &nbsp;|&nbsp; <b>%d</b> add meaning · <b>%d</b> '
           'restate · <b>%d</b> cancel/correct</div>'
           % (ls_stats[HIT], ls_stats[MINTABLE], ls_stats[NO_LOCUS], n_placed, n_new,
              klass_stats["adds"], klass_stats["restates"], klass_stats["cancels"]))
    return cov + body, ls_stats, klass_stats, n_placed, n_new


# --------------------------------------------------------------------- build
def card_bodies(obj):
    """Every store string this card renders, in a fixed order — the input to the
    byte-identity hash (H2844: «verify with a hash, not by eye»)."""
    out = []
    for hom in obj["homonyms"]:
        for s in hom["senses"]:
            out.append(s.get("pwg_ru", ""))
            out.extend(sup.get("ru", "") for sup in s["supplements"])
        out.extend(sup.get("ru", "") for sup in hom["new_senses"])
    return out


def digest_guard(bodies_before, bodies_after, raw_before, raw_after):
    """Refuse to publish if rendering changed one byte of the store text.

    ``collapse`` is a pure function, so this can only ever fire on a future
    regression — which is exactly what the acceptance asks it to catch. Returns
    the (identical) digests so the sheet can print them.
    """
    a = store_digest(*bodies_before)
    b = store_digest(*bodies_after)
    ra = store_digest(*raw_before)
    rb = store_digest(*raw_after)
    if a != b:
        raise SystemExit("STORE MUTATED: sense bodies %s -> %s" % (a[:16], b[:16]))
    if ra != rb:
        raise SystemExit("RAW PANEL MUTATED: %s -> %s" % (ra[:16], rb[:16]))
    return a, ra


def build():
    items = []
    totals = collections.Counter()
    nl = collections.Counter()
    bodies_before, bodies_after, raw_before, raw_after = [], [], [], []
    for key1, nlayers in ORDER:
        p = os.path.join(REGLUE_DIR, key1 + ".json")
        if not os.path.exists(p):
            print("  [skip] %s: no reglue json (run build_reglue.py first)" % key1)
            continue
        obj = json.load(io.open(p, encoding="utf-8"))
        raw_md = os.path.join(REGLUE_DIR, key1 + ".md")
        raw = io.open(raw_md, encoding="utf-8").read() if os.path.exists(raw_md) else ""
        bodies_before.extend(card_bodies(obj))
        raw_before.append(raw)

        expanded, ls_stats, klass_stats, n_placed, n_new = render_card(
            key1, obj, EXPANDED, nl)
        compact, _, _, _, _ = render_card(key1, obj, COMPACT, None)
        totals += ls_stats
        totals += klass_stats

        bodies_after.extend(card_bodies(obj))
        raw_after.append(raw)

        badges = ["%d-layer" % nlayers]
        if ls_stats[MINTABLE]:
            badges.append("%d mintable citation gaps" % ls_stats[MINTABLE])
        if klass_stats["cancels"]:
            badges.append("%d cancel/correct" % klass_stats["cancels"])
        items.append({
            "id": "reglue2::%s" % key1,
            "filt": "%dL" % nlayers,
            "title": slp1_iast(key1),
            "title_href": pwg_entry_href(key1),
            "badges": badges,
            "question": (
                'Is the <b>glue typology and placement</b> right on this card? '
                '<span class="muted">(green ＋ = the supplement really adds meaning · '
                'amber ≈ = PW only restates PWG more briefly · red ✕ = it cancels or '
                'corrects PWG. Approve = the chips and the sense each supplement sits '
                'at are correct; Reject = say which supplement is mis-typed or '
                'mis-placed. Rate 1–5 below for overall well-formedness.)</span>'),
            "note_placeholder": "if reject: which supplement, what the right subtype / sense is",
            "panels": [
                ("1 · re-glued card — print view, typology chips, linked citations "
                 "(«компактно» вверху страницы переключает на печатную колонку)",
                 '<div class="render-expanded">%s</div>'
                 '<div class="render-compact">%s</div>' % (expanded, compact)),
                ("2 · the same card as raw store markup — colours = parts of the "
                 "entry; quote from here in a note",
                 anatomy.highlight(raw)),
            ],
        })
    digests = digest_guard(bodies_before, bodies_after, raw_before, raw_after)
    return items, totals, nl, digests


#: The sheet-wide mode control (H2844 P2). It rides in the header subtitle,
#: which the template interpolates as raw HTML; the CSS above does the switching
#: through `:has()`, so the sheet needs no script of its own for it.
MODE_SWITCH = (
    '<span class="modeswitch">'
    '<input type="checkbox" id="modecompact">'
    '<label for="modecompact">компактно (печатная колонка)</label>'
    '</span>')


def main():
    os.makedirs(REVIEW, exist_ok=True)
    items, totals, nl, digests = build()
    if not items:
        print("no cards built — is PWG_RU_DATA_ROOT pointing at a tree with "
              "pwg_ru/reglue/*.json?")
        return 1
    body_hash, raw_hash = digests

    sheet_id = "h180-reglue-spotcheck-v3-2026-08-16"
    config = standard_config(
        save_as="RussianTranslation\\pwg_ru\\eval\\h180_reglue_v3.decisions.json")
    config.update({
        "sheet_id": sheet_id,
        "title": "H180 · content-aware re-glue spot-check (v3)",
        "subtitle": ("15 pilot cards with the glue typology surfaced, Cologne "
                     "ls-links joined, NWS gloss chains split for reading, and "
                     "the printed column's line-wraps collapsed" + MODE_SWITCH),
        "footer": ("Approve = typology chips and placement are right · Reject = "
                   "something is mis-typed or mis-placed (say what in the note) · "
                   "Defer = unsure. The 1–5 rating is overall well-formedness. "
                   "⚑ marks a citation with a real locus that no resolver pattern "
                   "covers — the mintable gap; ∅ marks a bare abbreviation, which "
                   "has nothing to link to.<br>"
                   "<b>Компактно / развёрнуто</b> — один и тот же материал в двух "
                   "видах: развёрнутый (etext, каждое значение с новой строки) и "
                   "компактный (печатная колонка, значения идут подряд, дополнения "
                   "стоят сразу за своим значением). Перенос строки из csl-orig — "
                   "это перенос печатной колонки, а не структура: %d таких переносов "
                   "склеены на этих карточках, %d структурных границ сохранены. "
                   "Текст store не менялся — SHA-256 значений %s, сырой панели %s."
                   "<br>" % (nl["collapsed"], nl["kept"],
                             body_hash[:16], raw_hash[:16]) + g5_legend()),
        "approve_label": "Typology right",
        "reject_label": "Mis-typed / mis-placed",
        "filters": [("5L", "5-layer"), ("4L", "4-layer"), ("3L", "3-layer")],
        "generated": GENERATED,
        "rating": DA_RATING,
        "extra_css": EXTRA_CSS,
    })
    sc = screening_block(
        deterministic=totals[HIT] + totals[NO_LOCUS], lookup=totals[MINTABLE],
        agent=0, human=len(items),
        evidence_path="RussianTranslation/pwg_ru/SCREENING_H1650.md",
        rules=["ls_resolver", "citation_tm", "h180-reglue-v3", "line_collapse"])
    doc = render_review_sheet(items, config, extras=True, screening=sc)
    doc, chash = stamp(doc)
    if 'id="modecompact"' not in doc or "render-compact" not in doc:
        raise SystemExit("the compact/expanded control did not survive rendering")

    sample = os.path.join(REVIEW, "h180_reglue_v3_sample.jsonl")
    with io.open(sample, "w", encoding="utf-8") as fh:
        for it in items:
            fh.write(json.dumps({k: it[k] for k in ("id", "filt", "title")},
                                ensure_ascii=False) + "\n")
    out = os.path.join(REVIEW, "h180_reglue_v3_sheet.html")
    with io.open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(doc)
    write_lock(sheet_id, chash, [it["id"] for it in items], GENERATED, source_html=out)

    print("  %d cards -> %s" % (len(items), out))
    print("  citations: %d linked · %d mintable gaps · %d bare abbreviations"
          % (totals[HIT], totals[MINTABLE], totals[NO_LOCUS]))
    print("  supplements: %d add meaning · %d restate · %d cancel/correct"
          % (totals["adds"], totals["restates"], totals["cancels"]))
    print("  line-wraps: %d collapsed · %d structural breaks kept"
          % (nl["collapsed"], nl["kept"]))
    print("  store unchanged: sense bodies sha256 %s · raw panel sha256 %s"
          % (body_hash, raw_hash))
    return 0


def selftest():
    """Fixture selftest for the display-only gloss-chain split (CI gate)."""
    ok = True

    def check(cond, msg):
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + msg)
        ok = ok and bool(cond)

    # the H2827 motivating case — gā, NWS, five clusters visible in the first line
    ga = ("{#gā (=pw gā 1)#} идти, приходить, странствовать. уходить. приходить "
          "к кому-л. (Akk) (с личными подлежащими). приходить к какому-л. месту "
          "(Akk) или направляться туда (место, укрытие). идти дорогой (Akk, Instr).")
    cl = gloss_clusters(ga)
    check(len(cl) >= 4, "gā chain splits into %d clusters" % len(cl))
    check(cl and cl[0].endswith("странствовать"),
          "first cluster keeps its internal commas: %r" % (cl[0] if cl else None))
    check(any(c.startswith("уходить") for c in cl), "'уходить' is its own cluster")
    check(not any(c.startswith("(Akk)") for c in cl),
          "no split after the clitic 'кому-л.'")

    # a period inside an unclosed parenthetical is not a cluster boundary
    cl2 = gloss_clusters("идти куда-л. (Lok или нар. места). происходить")
    check(cl2 == ["идти куда-л. (Lok или нар. места)", "происходить"],
          "no split inside «(Lok или нар. места)»: %r" % (cl2,))

    # a Sanskrit span's internal periods are never split points
    check(gloss_clusters("{#a. b. c#} одно. другое") == ["{#a. b. c#} одно", "другое"],
          "periods inside {#…#} are masked")

    # a citation-bearing body is left whole — a link must keep its clause
    check(gloss_clusters("идти <ls>MBH. 1,1</ls>. уходить.") == [],
          "citation-bearing body is not split")

    # not a chain -> no list, caller renders plainly
    check(gloss_clusters("просто одна глосса") == [], "single gloss -> no clusters")

    # every subtype the relationship sidecar can emit must be classified
    from_spec = {"restate", "nws_at_sense", "a2a", "sch_star", "foreign_fragment",
                 "derived_sense", "pw_correct", "pw_cancels"}
    check(from_spec <= set(TYPOLOGY), "every ADDENDA_TYPOLOGY subtype is classified")

    # ---------------------------------------------------------------- H2844 P1
    # The newline-collapse fixtures. Three things must hold at once: an
    # inherited wrap goes, a structural break stays, and no citation is left
    # torn out of the clause that sources it.
    ga_ls = ("{#yadA ca pfTivIM sarvAM yajamAno 'nuparyagAH#}\n"
             "<ls>MBH. 12,8081.</ls>")
    joined, n_col, n_kept = collapse(ga_ls)
    check("#} <ls>MBH. 12,8081.</ls>" in joined and (n_col, n_kept) == (1, 0),
          "fixture inherited-wrap: MBH. 12,8081. rejoins its verse")

    div_case = "{%достигать%}: {#ko vA#}\n<div n=\"1\"> 1) {%обретать%}"
    kept, n_col2, n_kept2 = collapse(div_case)
    check("\n<div" in kept and (n_col2, n_kept2) == (0, 1),
          "fixture structural-newline: a <div> sense division survives expanded mode")
    check("\n" not in collapse(div_case, COMPACT)[0],
          "fixture compact: the same division runs on in the printed column")

    # the rendered proof, not just the string: the print view must carry the
    # citation and the clause in ONE line, i.e. with no <br> between them.
    rendered, _ = render_body(ga_ls)
    between = rendered.split("nuparyagAH")[-1].split("MBH")[0]
    check("<br>" not in between,
          "fixture citation-clause-intact: no <br> between the verse and its citation")
    check("<a class=ls" in rendered or "<span class=ls" in rendered,
          "the collapsed citation still renders as a citation, not prose")
    check("<br>" in render_body(div_case)[0],
          "the structural break still renders as a line break in expanded mode")
    check("<br>" not in render_body(div_case, COMPACT)[0],
          "and as no line break at all in compact mode")

    # a page-column marker line is typesetting on both sides of the marker
    page = "{#aBIpsatI#}\n<ls>MBH. 1,6469.</ls>\n[Page1-0651]\n{#aBIpsantI#}"
    check(collapse(page)[1] == 3 and "\n" not in collapse(page)[0],
          "fixture page-marker: a [PageN-NNNN] line collapses on both sides")

    # both renderings come from one data source and one function
    obj = {"homonyms": [{"h": "0", "new_senses": [],
                         "senses": [{"sense": "1", "pwg_ru": ga_ls,
                                     "supplements": [{"subtype": "restate",
                                                      "badge": "PW", "op": "restate",
                                                      "ru": "то же короче"}]}]}]}
    before = store_digest(*card_bodies(obj))
    exp_html = render_card("t", obj, EXPANDED)[0]
    cmp_html = render_card("t", obj, COMPACT)[0]
    check(store_digest(*card_bodies(obj)) == before,
          "rendering both modes leaves the store object byte-identical")
    check('class="sense"' in exp_html and 'class="cflow"' in cmp_html,
          "expanded renders sense blocks, compact renders one running column")
    check("MBH" in exp_html and "MBH" in cmp_html,
          "the same citation is present in both renderings")
    # mark_cyrillic wraps each Cyrillic RUN in <mark>, so match one word, not the
    # phrase — a phrase would fail for a reason that has nothing to do with modes
    check("короче" in exp_html and "короче" in cmp_html,
          "the supplement is present in both renderings")
    check('class="csupp"' in cmp_html,
          "in compact the supplement sits inline behind its sense marker")

    print("build_reglue_sheet_v2 selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(main())
