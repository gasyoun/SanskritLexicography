#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_bli_gold_b1_500_sheet.py -- H2551 vehicle for MG pass-1 annotation.

Emits the 500-card Russian review sheet over the frozen H2401 frame
(gold_frame_b1_stratified_500.tsv), per
docs/BLI_GOLD_SET_ANNOTATION_PROTOCOL_2026.md section 5. This handoff's whole
job is emitting the sheet -- it does not annotate, score, or adjudicate.

Inverted screening case (protocol section 5 / review-sheet Phase 0-bis): the
human label IS the deliverable, so all 500 cards are class (d) -- no
deterministic/lookup/agent resolver applies.

Each card carries the SLP1 headword + IAST + full Kochergina gloss + stratum
badges (band / POS / polysemy). The pass-1 label is entered in the free-text
note field as the set of acceptable Russian translation equivalents,
comma-separated; SKIP + a reason (cross-reference only / proper name /
grammatical apparatus) is the reject path (protocol section 5).

No title_href: Kochergina entries have no stable public per-headword URL in
this repo's tooling (no koch_entry_href helper exists, unlike
review_sheet_standard.pwg_entry_href for PWG roots) -- the full gloss is
already inline on the card, so this does not block answerability (V4 n/a,
stated per /review-sheet Phase 2).

Regen (canonical invocation, from the repo root):

  python RussianTranslation/src/eval/build_bli_gold_b1_500_sheet.py

Output: ``RussianTranslation/review/<sheet_id>_review.html`` (gitignored).
"""
import io
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from csl_pyutil import esc, mark_cyrillic, render_review_sheet  # noqa: E402

from review_binding import stamp, write_lock  # noqa: E402
from review_sheet_standard import standard_config  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
RT_ROOT = os.path.dirname(os.path.dirname(HERE))
REVIEW = os.path.join(RT_ROOT, "review")
FRAME_TSV = os.path.join(HERE, "gold_frame_b1_stratified_500.tsv")

SHEET_ID = "sanskritlexicography-bli_gold_b1_500_review"
GENERATED = "12-08-2026"

BAND_LABEL = {"5": "band 5 (частотнейшие)", "4": "band 4", "3": "band 3",
              "2": "band 2", "1": "band 1 (редкие)"}
POS_LABEL = {"NOUN": "NOUN", "VERB": "VERB", "ADJ": "ADJ", "ADV": "ADV",
             "OTHER": "OTHER"}

_S2I = {
    "A": "ā", "I": "ī", "U": "ū", "f": "ṛ", "F": "ṝ",
    "x": "ḷ", "X": "ḹ", "E": "ai", "O": "au", "M": "ṃ",
    "H": "ḥ", "K": "kh", "G": "gh", "N": "ṅ", "C": "ch", "J": "jh",
    "Y": "ñ", "w": "ṭ", "W": "ṭh", "q": "ḍ", "Q": "ḍh",
    "R": "ṇ", "T": "th", "D": "dh", "P": "ph", "B": "bh", "S": "ś",
    "z": "ṣ",
}


def slp1_iast(s):
    return "".join(_S2I.get(c, c) for c in (s or ""))


def parse_frame(path):
    rows = []
    with io.open(path, encoding="utf-8") as f:
        header = None
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            cols = line.split("\t")
            if header is None:
                header = cols
                continue
            rows.append(dict(zip(header, cols)))
    return rows


def build_items(rows):
    out = []
    for r in rows:
        slp1 = r["slp1"]
        band = r["band"]
        pos = r["pos"]
        polysemy = r["polysemy"]
        n_senses = r["n_senses"]
        gloss = r["koch_gloss"]

        badges = [
            BAND_LABEL.get(band, "band %s" % band),
            POS_LABEL.get(pos, pos),
            "полисемия %s (%s знач.)" % (polysemy, n_senses),
        ]
        panels = [
            ("Kochergina gloss", mark_cyrillic(esc(gloss))),
        ]
        out.append({
            "id": slp1,
            "filt": "band" + band,
            "title": "%s / %s" % (slp1, slp1_iast(slp1)),
            "badges": badges,
            "question": "",
            "panels": panels,
            "note_placeholder": (
                "Допустимые русские эквиваленты "
                "через запятую "
                "(SKIP + причина, если строка не "
                "аннотируема)"
            ),
        })
    return out


def main():
    rows = parse_frame(FRAME_TSV)
    assert len(rows) == 500, "frame row count changed: %d (expected 500)" % len(rows)

    filters = [("band" + b, BAND_LABEL[b]) for b in ("5", "4", "3", "2", "1")]

    config = {
        "sheet_id": SHEET_ID,
        "title": "BLI gold B1: Sa→Ru pass-1 (MG) — 500 карточек",
        "generated": GENERATED,
        "subtitle": (
            "H2551 · вторая из трёх B1-линий "
            "· рамка заморожена H2401 "
            "(gold_frame_b1_stratified_500.tsv, seed 20260810)"
        ),
        "footer": (
            "Метка (поле записи) = "
            "ввести допустимые русские "
            "эквиваленты через запятую "
            "и нажать Approve в конце. Reject = SKIP "
            "(строка неаннотируема — "
            "только ссылка, имя "
            "собственное, грамматический "
            "аппарат) — укажите причину "
            "в поле записи. Defer = не уверен, "
            "вернуться позже. Метка карты "
            "питает P@1/P@5/MRR-знаменатель (H2402); "
            "SKIP исключает строку из знаменателя."
        ),
        "approve_label": "Сохранить метку",
        "reject_label": "SKIP",
        "reject_labels": [
            ("xref", "только перекрёстная ссылка"),
            ("proper_name", "собственное имя"),
            ("grammar", "грамматический аппарат"),
        ],
        "filters": filters,
    }
    config.update(standard_config(
        save_as=r"RussianTranslation\review\%s_decisions.json" % SHEET_ID))

    screening = {
        "deterministic": 0,
        "lookup": 0,
        "agent": 0,
        "human": len(rows),
        "evidence_path": "docs/BLI_GOLD_SET_ANNOTATION_PROTOCOL_2026.md#5-annotation-protocol",
        "rules": ["none -- human label is the deliverable (protocol section 5)"],
    }

    items = build_items(rows)
    html_out = render_review_sheet(items, config, extras=True, screening=screening)

    html_out, chash = stamp(html_out)

    os.makedirs(REVIEW, exist_ok=True)
    out = os.path.join(REVIEW, SHEET_ID + ".html")
    io.open(out, "w", encoding="utf-8").write(html_out)
    write_lock(SHEET_ID, chash, [it["id"] for it in items], GENERATED,
               source_html=out)
    print("sheet:", out, "(%d items)" % len(items))


def selftest():
    rows = parse_frame(FRAME_TSV)
    assert len(rows) == 500
    ids = set(r["slp1"] for r in rows)
    assert len(ids) == 500, "duplicate slp1 ids in frame"
    items = build_items(rows[:3])
    for it in items:
        assert it["id"]
        assert it["panels"][0][1]
    print("selftest: OK (%d frame rows)" % len(rows))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        selftest()
    else:
        main()
