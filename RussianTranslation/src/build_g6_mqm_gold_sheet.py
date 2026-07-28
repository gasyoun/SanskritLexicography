#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_g6_mqm_gold_sheet.py — the G6 starter gold sheet (H1404, ruling D10).

~20 cards from the committed gold scaffold (``gold/gold_set.jsonl``, 320 rows),
stratified over the 8 (period × kind) cells, under the MQM-style instrument
ruled for G6 (D6): the reviewer confirms or corrects the LLM label against the
fixed 6-label error typology

  correct · lemma-variant · proper-name · partial · wrong-sense · hallucinated

Vote contract (matches ``apply_decisions.py`` G6):
  approve = the shown LLM label is right;
  reject  = it is wrong — pick the CORRECT label from the required select
            control (H1802); the note stays free-text rationale only;
  defer   = needs adjudication (row lands with needs_adjudication=true).

**H1802.** The first real vote on this sheet (H1796) measured 5/6 rejects
writing prose instead of the label as the note's first word — an
unenforceable convention that made all 20 votes (including 14 clean
approves) fail ``apply_decisions.py``'s all-or-nothing apply. Replaced with
``config["reject_labels"]``, a required single-select control; the note
textarea remains for the rationale. A NEW sheet_id/generation is used below
since the 2026-07-25 generation already carries applied votes (H1796) and a
voted sheet is never regenerated in place.

Export flow: decisions.json → ``validate_decisions`` → ``apply_decisions
--gate G6`` (builds the 11-column CSV and runs ``gold_ingest.py`` with an
explicit out path — the 320-row hard gate stays with the full set).

Deterministic: sorted ids, evenly strided per stratum. No RNG.

The gold scaffold is public (tracked), but the sheet HTML stays gitignored
(``review/g6_*_sheet.html``) like every other sheet — the committed artifact is
the metadata lock.

Run (from RussianTranslation/):
  python src/build_g6_mqm_gold_sheet.py [--n 20] [--gold-set PATH]
"""
import argparse
import collections
import html
import io
import json
import os
import sys

from csl_pyutil import mark_cyrillic, render_review_sheet
from review_binding import stamp, write_lock
from review_sheet_standard import standard_config

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(HERE)
REVIEW = os.path.join(RT, "review")

LEGACY_SHEET_ID = "g6-mqm-gold-starter-2026-07-25"
LEGACY_GENERATED = "2026-07-25"

#: H1802 re-cut with the reject_labels picker. The pre-picker generation keeps
#: its own id + lock (LEGACY_SHEET_ID above) — its votes are already applied
#: (H1796) and must stay validatable.
SHEET_ID = "g6-mqm-gold-starter-reject-picker-2026-07-28"
GENERATED = "2026-07-28"

LABELS = ("correct", "lemma-variant", "proper-name", "partial", "wrong-sense",
          "hallucinated")
LABEL_RU = {
    "correct": "перевод верен",
    "lemma-variant": "вариант той же леммы (не ошибка смысла)",
    "proper-name": "имя собственное, переведённое как нарицательное (или наоборот)",
    "partial": "переведена только часть значения",
    "wrong-sense": "не то значение",
    "hallucinated": "перевода в источнике нет / выдумано",
}


def esc(s):
    return html.escape("" if s is None else str(s))


def pick(rows, n):
    """Evenly strided per (period, kind) stratum, ids sorted numerically;
    round-robin across cells so the cut at n stays balanced (cells differ by
    at most one card)."""
    strata = collections.defaultdict(list)
    for r in rows:
        strata[(r["period"], r["kind"])].append(r)
    cells = sorted(strata)
    per = -(-n // len(cells))  # ceil
    picks = {}
    for cell in cells:
        pool = sorted(strata[cell], key=lambda r: int(r["id"]))
        step = max(1, len(pool) // per)
        picks[cell] = pool[::step][:per]
    out = []
    for rnd in range(per):
        for cell in cells:
            if rnd < len(picks[cell]) and len(out) < n:
                out.append(picks[cell][rnd])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--gold-set", default=os.path.join(RT, "gold", "gold_set.jsonl"))
    ap.add_argument("--out", default=os.path.join(REVIEW, "g6_mqm_starter_sheet.html"))
    ap.add_argument("--locks-dir", default=None)
    args = ap.parse_args()

    rows = [json.loads(l) for l in io.open(args.gold_set, encoding="utf-8") if l.strip()]
    chosen = pick(rows, args.n)

    legend = "".join("<div><span class=\"chip\">%s</span> %s</div>"
                     % (esc(l), esc(LABEL_RU[l])) for l in LABELS)
    items = []
    for r in chosen:
        items.append({
            "id": str(r["id"]),
            "filt": r["period"],
            "question": ("Верен ли ярлык LLM <b>«%s»</b> для этого перевода? "
                         '<span class="muted">(reject → выберите правильный ярлык '
                         "из списка ниже)</span>" % esc(r["label"])),
            "title": r.get("sa") or r.get("slp1") or str(r["id"]),
            "badges": [r["period"], r["kind"], r.get("work") or ""],
            "note_placeholder": "необязательный комментарий к решению",
            "panels": [("Санскрит (sa)", "<pre>%s</pre>" % esc(r.get("sa"))),
                       ("Русский (ru)", "<pre>%s</pre>" % mark_cyrillic(esc(r.get("ru")))),
                       ("Ярлык LLM · типология MQM",
                        "<pre><b>%s</b></pre>%s" % (esc(r["label"]), legend))],
        })

    periods = []
    for r in chosen:
        if r["period"] not in periods:
            periods.append(r["period"])
    config = {
        "sheet_id": SHEET_ID,
        "title": "G6 · золотой стандарт — стартовый лист MQM",
        "subtitle": ("%d карточек из gold/gold_set.jsonl (320), стратификация "
                     "period × kind; типология из 6 ярлыков" % len(items)),
        "footer": ("Approve = ярлык LLM верен · Reject = неверен (выберите правильный "
                   "ярлык из списка) · Defer = на адjudication. Экспорт "
                   "валидируется против review/locks/%s.lock.json." % SHEET_ID),
        "approve_label": "Label верен", "reject_label": "Label неверен",
        "filters": [(p, p) for p in sorted(periods)],
        "generated": GENERATED,
        "strict_review": {"reviewer": "", "require_all_votes": True,
                          "require_reject_note": True},
        "reject_labels": [(l, LABEL_RU[l]) for l in LABELS if l != "correct"],
    }
    config.update(standard_config(
        save_as="RussianTranslation\\review\\%s_decisions.json" % SHEET_ID))

    doc = render_review_sheet(items, config, extras=True)
    doc, chash = stamp(doc)
    os.makedirs(REVIEW, exist_ok=True)
    with io.open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(doc)
    lock = write_lock(SHEET_ID, chash, [it["id"] for it in items], GENERATED,
                      locks_dir=args.locks_dir, gate="G6", source_html=args.out)
    print("G6 sheet: %d cards -> %s\n  %s\n  lock -> %s"
          % (len(items), args.out, chash, lock))


if __name__ == "__main__":
    main()
