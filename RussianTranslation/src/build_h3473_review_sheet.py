#!/usr/bin/env python
"""H3473 wave-4 review sheet — human gate over wave-1-carried fill corrections.

Census chain: 3451 pool re-entry rows -> 188 distinct carried pairs
(wave4_receipt/carried_fill_census.json) -> agent-adjudicated -> 9 wrong/minor
candidates on this sheet. Approve applies the PROPOSED correction to the
tracked TM via apply_decisions.py after export; reject keeps the pair;
defer parks it. Never applied unvoted (H3473 contract).

    PYTHONPATH=<csl-pyutil clone> python src/build_h3473_review_sheet.py [--out FILE]
"""
from __future__ import annotations

import argparse
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from csl_pyutil import render_review_sheet  # noqa: E402
from review_sheet_standard import pwg_entry_href, slp1_iast, standard_config  # noqa: E402

REVIEW = os.path.normpath(os.path.join(HERE, "..", "review"))

#: (id, key1, reach, severity, source_span, carried_target, proposal, rationale)
ITEMS = [
    ("h3473-w-habend", "dvika", 10, "wrong (R15 #7 / R3434 convicted)",
     "habend", "от", "имеющий",
     "German participle 'habend' (having) rendered as bare preposition; "
     "relation inverted. Convicted by both independent gates."),
    ("h3473-w-opfer", "udBid", 4, "wrong (R3434 convicted)",
     "ein <ab>best.</ab> Opfer", "совершать", "определённая жертва",
     "'ein bestimmtes Opfer' (a certain sacrifice, noun phrase) destroyed "
     "into a verb. Convicted by R3434 serious rows."),
    ("h3473-w-mund", None, 4, "wrong",
     "Mund", "рте", "рот",
     "Nominative 'Mund' rendered in prepositional case; case drift."),
    ("h3473-w-alt", None, 4, "wrong (R15 #6 family)",
     "alt", "возраста", "старый",
     "'alt' (old) rendered as 'возраста' (of age); wrong lexical meaning. "
     "Defer if the entry context genuinely needs the age construction."),
    ("h3473-s-hat", None, 2, "suspect (alignment artifact?)",
     "hat", "воодушевил",
     "(unfill — no safe static correction)",
     "'hat' (has) cannot mean 'воодушевил'; likely a span-alignment bleed. "
     "Approve = remove this carried fill from the TM row."),
    ("h3473-s-von-etwas", None, 2, "suspect (alignment artifact?)",
     "von Etwas", "утверждать о чём-л.",
     "(unfill — no safe static correction)",
     "'von Etwas' (of something) cannot mean 'утверждать'; same artifact "
     "class as h3473-s-hat. Approve = remove this carried fill."),
    ("h3473-m-pflanze", None, 128, "minor (german residue)",
     "eine <ab>best.</ab> Pflanze", "одно <ab>best.</ab> растение",
     "одно определённое растение",
     "German abbreviation 'best.' (= bestimmtes) left untranslated inside "
     "the RU target; highest-reach residue in the census (x128 rows)."),
    ("h3473-m-truppen", None, 2, "minor (german residue)",
     "einer <ab>best.</ab> Truppenaufstellung", "построения <ab>best.</ab> войск",
     "построения определённых войск",
     "Same untranslated-'best.' residue class as h3473-m-pflanze."),
    ("h3473-m-wild", None, 2, "minor (case drift)",
     "wild, der Ordnung widerstrebend", "дикому, противящемуся порядку",
     "дикий, противящийся порядку",
     "Gloss rendered in dative; PWG uses these as nominal adjectives."),
]


def build_items():
    out = []
    for iid, key1, reach, sev, src, tgt, prop, why in ITEMS:
        badges = ["x%d" % reach, sev]
        head = "%s — %s ⇒ %s" % (
            html.escape(slp1_iast(key1)) if key1 else "(entry)",
            html.escape(src), html.escape(tgt))
        q = "<b>%s</b><br><span style='opacity:.8'>%s</span>" % (head, html.escape(why))
        href = pwg_entry_href(key1) if key1 else None
        link = ("<p><a href='%s'>PWG entry %s</a></p>" % (href, html.escape(key1))) \
            if href else ""
        panels = [
            ("Carried fill (wave-1, in publication TM)", q),
            ("Proposed correction", "<b>%s</b>%s" % (
                html.escape(prop),
                " <i>(approve removes the fill; row re-unfills)</i>"
                if prop.startswith("(") else "")),
            ("Evidence", "<p>census: wave4_receipt/carried_fill_census.json · "
                         "reach x%d promoted/quarantine rows · parent receipt: "
                         "wave3_receipt/WAVE3_GATE_VERDICT.md</p>%s" % (reach, link)),
        ]
        out.append({"id": iid, "filt": sev.split(" ")[0], "title": head,
                    "badges": badges, "question": q, "panels": panels})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(
        REVIEW, "h3473_wave4_sensefill_sheet.html"))
    a = ap.parse_args()
    config = {
        "sheet_id": "h3473-wave4-sensefill",
        "title": "H3473 wave 4 — wave-1-carried fill corrections",
        "subtitle": "9 wrong/minor candidates from the 188-pair carried-fill "
                    "census (3451 re-entry rows). Approve = apply proposal to "
                    "the tracked TM after export.",
        "footer": "H3473 · OxAlpha · never applied unvoted",
        "approve_label": "Accept correction",
        "reject_label": "Keep as-is",
        "filters": [("wrong", "wrong"), ("suspect", "suspect"),
                    ("minor", "minor")],
        "generated": "25-08-2026",
    }
    config.update(standard_config(save_as=os.path.join(
        "RussianTranslation", "pwg_ru", "eval",
        "h3473_wave4_sensefill.decisions.json")))
    screening = {
        "deterministic": 3451,
        "lookup": 188,
        "agent": 188,
        "human": len(ITEMS),
        "evidence_path": "RussianTranslation/release/pwg_tm_canonical/wave4_receipt/carried_fill_census.json",
        "rules": [
            "pool origins exact_source_reuse+sense_merge only",
            "identity and placeholder-style spans excluded",
            "agent labels every distinct pair; only wrong/minor/suspect reach this sheet",
        ],
    }
    doc = render_review_sheet(build_items(), config, screening=screening)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(doc)
    print("sheet: %s (%d items)" % (a.out, len(ITEMS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
