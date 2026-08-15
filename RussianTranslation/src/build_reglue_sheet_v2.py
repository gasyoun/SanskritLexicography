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

Inputs (local, untracked — point PWG_RU_DATA_ROOT at the tree that has them):
    <data>/src/pwg_ru_translated.jsonl
    <data>/pwg_ru/reglue/<key1>.json
Output (gitignored, published to the vote hub by hand):
    <data>/review/h180_reglue_v2_sheet.html
    <data>/review/h180_reglue_v2_sample.jsonl

Run: python src/build_reglue_sheet_v2.py
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

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("PWG_RU_DATA_ROOT", os.path.dirname(HERE))
REGLUE_DIR = os.path.join(DATA, "pwg_ru", "reglue")
REVIEW = os.path.join(DATA, "review")
GENERATED = "2026-08-15"

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


def render_body(raw):
    """One store body as the PRINT view, with unresolved citations marked.

    Goes through ``g5_card_render.print_panel`` — the same renderer the public
    article site uses — so ``<ls>`` arrives as a Cologne link with its full
    bibliographic tooltip, ``{#…#}`` as italic IAST, and Russian highlighted.
    A period-separated gloss chain is split into numbered clusters for reading
    (display only; the raw store string is one panel away).
    """
    clusters = gloss_clusters(raw or "")
    if clusters:
        inner = "".join("<li>%s</li>" % print_panel(c) for c in clusters)
        body = '<ol class="clusters">%s</ol>' % inner
    else:
        body = print_panel(raw or "")
    return _mark_gaps(body)


def render_supplement(sup):
    subtype = sup.get("subtype", "?")
    op, direction, klass, gloss = TYPOLOGY.get(
        subtype, (sup.get("op", "?"), "?", "restates", "unclassified subtype"))
    body, stats = render_body(sup.get("ru", ""))
    lang = ' <span class="tchip t-meta">‹%s›</span>' % esc(sup["lang"]) if sup.get("lang") else ""
    cancels = (' <span class="tchip t-cancels">cancels PWG</span>'
               if sup.get("cancels") else "")
    head = ('<span class="tchip t-%s" title="%s">%s</span>'
            '<span class="tchip t-meta">%s</span>'
            '<span class="tchip t-meta">%s · %s</span>%s%s'
            % (klass, esc(gloss), esc(CLASS_LABEL[klass]), esc(subtype),
               esc(sup.get("badge", "?")), esc(op), lang, cancels))
    return ('<div class="supp">%s<div class="body">%s</div></div>'
            % (head, body)), stats, klass


def render_card(key1, obj):
    """Return (html, per-card stats) for one pilot headword."""
    ls_stats = collections.Counter()
    klass_stats = collections.Counter()
    chunks = []
    n_placed = n_new = 0
    for hom in obj["homonyms"]:
        chunks.append("<h4>homonym %s</h4>" % esc(hom["h"]))
        for s in hom["senses"]:
            pwg_body, st = render_body(s.get("pwg_ru", ""))
            ls_stats += st
            block = ['<div class="sense"><div class="hd">PWG sense %s</div>%s'
                     % (esc(s["sense"]), pwg_body)]
            for sup in s["supplements"]:
                h, st2, kl = render_supplement(sup)
                ls_stats += st2
                klass_stats[kl] += 1
                n_placed += 1
                block.append(h)
            block.append("</div>")
            chunks.append("".join(block))
        if hom["new_senses"]:
            chunks.append('<div class="sense"><div class="hd">'
                          '＋ new senses (no PWG sense to attach to)</div>')
            for sup in hom["new_senses"]:
                h, st2, kl = render_supplement(sup)
                ls_stats += st2
                klass_stats[kl] += 1
                n_new += 1
                chunks.append(h)
            chunks.append("</div>")
    cov = ('<div class="cov">citations: <b>%d</b> linked to Cologne · '
           '<b>%d</b> ⚑ mintable gap (locus, no target) · <b>%d</b> ∅ bare '
           'abbreviation (nothing to link)<br>supplements: <b>%d</b> placed at a PWG '
           'sense · <b>%d</b> new &nbsp;|&nbsp; <b>%d</b> add meaning · <b>%d</b> '
           'restate · <b>%d</b> cancel/correct</div>'
           % (ls_stats[HIT], ls_stats[MINTABLE], ls_stats[NO_LOCUS], n_placed, n_new,
              klass_stats["adds"], klass_stats["restates"], klass_stats["cancels"]))
    return cov + "".join(chunks), ls_stats, klass_stats, n_placed, n_new


# --------------------------------------------------------------------- build
def build():
    items = []
    totals = collections.Counter()
    for key1, nlayers in ORDER:
        p = os.path.join(REGLUE_DIR, key1 + ".json")
        if not os.path.exists(p):
            print("  [skip] %s: no reglue json (run build_reglue.py first)" % key1)
            continue
        obj = json.load(io.open(p, encoding="utf-8"))
        card, ls_stats, klass_stats, n_placed, n_new = render_card(key1, obj)
        totals += ls_stats
        totals += klass_stats
        raw_md = os.path.join(REGLUE_DIR, key1 + ".md")
        raw = io.open(raw_md, encoding="utf-8").read() if os.path.exists(raw_md) else ""
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
                ("1 · re-glued card — print view, typology chips, linked citations",
                 card),
                ("2 · the same card as raw store markup — colours = parts of the "
                 "entry; quote from here in a note",
                 anatomy.highlight(raw)),
            ],
        })
    return items, totals


def main():
    os.makedirs(REVIEW, exist_ok=True)
    items, totals = build()
    if not items:
        print("no cards built — is PWG_RU_DATA_ROOT pointing at a tree with "
              "pwg_ru/reglue/*.json?")
        return 1

    sheet_id = "h180-reglue-spotcheck-v2-2026-08-15"
    config = standard_config(
        save_as="RussianTranslation\\pwg_ru\\eval\\h180_reglue_v2.decisions.json")
    config.update({
        "sheet_id": sheet_id,
        "title": "H180 · content-aware re-glue spot-check (v2)",
        "subtitle": ("15 pilot cards with the glue typology surfaced, Cologne "
                     "ls-links joined, and NWS gloss chains split for reading"),
        "footer": ("Approve = typology chips and placement are right · Reject = "
                   "something is mis-typed or mis-placed (say what in the note) · "
                   "Defer = unsure. The 1–5 rating is overall well-formedness. "
                   "⚑ marks a citation with a real locus that no resolver pattern "
                   "covers — the mintable gap; ∅ marks a bare abbreviation, which "
                   "has nothing to link to.<br>" + g5_legend()),
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
        rules=["ls_resolver", "citation_tm", "h180-reglue-v2"])
    doc = render_review_sheet(items, config, extras=True, screening=sc)
    doc, chash = stamp(doc)

    sample = os.path.join(REVIEW, "h180_reglue_v2_sample.jsonl")
    with io.open(sample, "w", encoding="utf-8") as fh:
        for it in items:
            fh.write(json.dumps({k: it[k] for k in ("id", "filt", "title")},
                                ensure_ascii=False) + "\n")
    out = os.path.join(REVIEW, "h180_reglue_v2_sheet.html")
    with io.open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(doc)
    write_lock(sheet_id, chash, [it["id"] for it in items], GENERATED, source_html=out)

    print("  %d cards -> %s" % (len(items), out))
    print("  citations: %d linked · %d mintable gaps · %d bare abbreviations"
          % (totals[HIT], totals[MINTABLE], totals[NO_LOCUS]))
    print("  supplements: %d add meaning · %d restate · %d cancel/correct"
          % (totals["adds"], totals["restates"], totals["cancels"]))
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

    print("build_reglue_sheet_v2 selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(main())
