#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_g5_review_sheet.py — the G5 live-queue review sheet (H1404, ruling D10).

G5 publication-review lane under the binding standard: a deterministic
~150-card slice of the LIVE review queue (``src/_review_queue.jsonl``, 11,163
``ai_translated`` rows), NOT the 2026-06 legacy 217-row triage queue — that
generation's ``ord:N`` ids no longer resolve against the current store, so its
judge annotations are audit history, not a work queue (see the deep manual
§"queue generations").

**batch1v2 (2026-07-26).** Batch 1 (``g5-live-queue-batch1-2026-07-25``) was
aborted by the reviewer at 5/150 votes: cards reached the human with
reader-visible German («Я не должен искать немецкие слова в русском переводе.
Ты должен. Перед тем как мне показывать»). Two changes, both permanent:

* every candidate passes ``review_residue_gate`` (H1302 prose scan + H1303
  ``<ab>`` classification + ``<ls>``-tail check) BEFORE a human sees it;
* the RU panel shows the *print rendering* (``pwg_ab_ru.RU_MAP`` applied to
  ``<ab>`` tokens, original kept as a hover tooltip) — batch 1 showed raw store
  markup, so deliberately render-translated abbreviations (``<ab>s. u.</ab>`` →
  «см.») looked like leaked German. The raw store markup stays available in a
  second panel for note-quoting.

Cards already decided in ``src/_review_queue.csv`` are excluded — a rejected
card never re-surfaces unless its underlying data changed (/decisions-apply
contract).

Instrument per ruling D6: plain approve/reject/defer (approve = print-ready,
maps to run_batch's ``approved``; reject = not print-ready; defer =
``needs_review``). No DA rating — G5 is a bulk edition decision, not a quality
scale. Exports flow: download/auto-save decisions.json → ``validate_decisions``
→ ``apply_decisions --gate G5`` (merges into ``src/_review_queue.csv`` and runs
``run_batch.py validate_review``).

Selection is round-robin across sorted roots (key1) so a small batch still
touches many entries; within a root, rows in review_id order. Fully
deterministic — no RNG.

PUBLISH SAFETY: the sheet embeds unpublished RU translations from the
gitignored store → the HTML is gitignored (``review/g5_*_sheet.html``); only
the metadata lock (``review/locks/<sheet_id>.lock.json``) is committed.

Run (from RussianTranslation/, in a clone that has the gitignored queue+store):
  python src/build_g5_review_sheet.py [--n 150] [--queue PATH] [--store PATH]
      [--review-csv PATH] [--no-residue-gate]
"""
import argparse
import collections
import csv
import html
import io
import json
import os
import re
import sys

from csl_pyutil import mark_cyrillic, render_review_sheet
from review_binding import stamp, write_lock
from review_residue_gate import visible_german
from review_sheet_standard import pwg_entry_href, slp1_iast, standard_config
from pwg_ab_ru import RU_MAP
import pwg_ab

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(HERE)
REVIEW = os.path.join(RT, "review")

SHEET_ID = "g5-live-queue-batch1v2-2026-07-26"
GENERATED = "2026-07-26"

_AB = re.compile(r"<ab\b[^>]*>(.*?)</ab>", re.S)


def esc(s):
    return html.escape("" if s is None else str(s))


def load_jsonl(path):
    return [json.loads(l) for l in io.open(path, encoding="utf-8") if l.strip()]


def load_decided_ids(review_csv):
    """review_ids already carrying a non-blank decision — never re-presented."""
    if not review_csv or not os.path.exists(review_csv):
        return set()
    with io.open(review_csv, encoding="utf-8-sig", newline="") as fh:
        return {(row.get("review_id") or "").strip()
                for row in csv.DictReader(fh)
                if (row.get("decision") or "").strip()}


def render_ru_print(ru_text):
    """The RU text as PRINT shows it: RU_MAP-mapped <ab> tokens display their
    Russian form (original German/Latin kept as a hover tooltip); everything
    else — {#…#} Sanskrit, <ls> citations, unmapped Latin sigla — verbatim."""
    out, last = [], 0
    for m in _AB.finditer(ru_text):
        out.append(mark_cyrillic(esc(ru_text[last:m.start()])))
        tok = re.sub(r"\s+", " ", m.group(1)).strip()
        vis = RU_MAP.get(tok)
        if vis is None:
            out.append(mark_cyrillic(esc(m.group(0))))     # Latin siglum, verbatim
        else:
            r = pwg_ab.resolve(tok)
            title = tok + (" — %s" % r["de"] if r and r.get("de") else "")
            out.append('<abbr title="%s">%s</abbr>' % (esc(title), mark_cyrillic(esc(vis))))
        last = m.end()
    out.append(mark_cyrillic(esc(ru_text[last:])))
    return "".join(out)


def pick(queue_rows, n):
    """Round-robin across sorted roots; within a root, rows in review_id order."""
    by_root = collections.defaultdict(list)
    for r in queue_rows:
        by_root[r.get("key1") or "?"].append(r)
    for rows in by_root.values():
        rows.sort(key=lambda r: r["review_id"])
    roots = sorted(by_root)
    out, i = [], 0
    while len(out) < n and any(by_root[k] for k in roots):
        root = roots[i % len(roots)]
        if by_root[root]:
            out.append(by_root[root].pop(0))
        i += 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--queue", default=os.path.join(HERE, "_review_queue.jsonl"))
    ap.add_argument("--store",
                    default=os.environ.get("PWG_RU_STORE",
                                           os.path.join(HERE, "pwg_ru_translated.jsonl")))
    ap.add_argument("--review-csv", default=os.path.join(HERE, "_review_queue.csv"))
    ap.add_argument("--no-residue-gate", action="store_true",
                    help="present ungated cards (forensics only — the gate is "
                         "the batch1 abort's standing mandate)")
    ap.add_argument("--out", default=os.path.join(REVIEW, "g5_batch1v2_sheet.html"))
    ap.add_argument("--locks-dir", default=None)
    args = ap.parse_args()

    queue = load_jsonl(args.queue)
    store = {}
    for rec in load_jsonl(args.store):
        store[(rec.get("subcard"), str(rec.get("sense_tag")))] = rec

    def store_rec(r):
        rid = r.get("review_id") or ""
        if ":subcard:" in rid and "#" in rid:
            sub, tag = rid.split(":subcard:", 1)[1].rsplit("#", 1)
            return store.get((sub, tag), {})
        return {}

    decided = load_decided_ids(args.review_csv)
    n_decided = n_flagged = 0
    candidates = []
    for r in queue:
        if (r.get("review_id") or "") in decided:
            n_decided += 1
            continue
        ru = store_rec(r).get("ru") or r.get("ru") or ""
        if not args.no_residue_gate and visible_german(ru):
            n_flagged += 1
            continue
        candidates.append(r)
    print("queue %d | already decided %d | residue-gate excluded %d | eligible %d"
          % (len(queue), n_decided, n_flagged, len(candidates)))

    chosen = pick(candidates, args.n)
    items = []
    for r in chosen:
        rec = store_rec(r)
        root = (rec.get("provenance") or {}).get("root") or r.get("key1") or ""
        stratum = rec.get("stratum") or "na"
        ru = rec.get("ru") or r.get("ru") or ""
        items.append({
            "id": r["review_id"],
            "filt": stratum,
            "title": rec.get("iast") or slp1_iast(r.get("key1") or ""),
            "title_href": pwg_entry_href(root),
            "badges": [rec.get("source_type") or "?", stratum],
            "question": ("Годен ли этот русский перевод в печать как есть? "
                         '<span class="muted">(Print-ready = да, как напечатано ниже · '
                         "Reject = нет (почему — в заметку) · Defer = отложить "
                         "в needs_review)</span>"),
            "note_placeholder": "reject → что именно не так; частичная правка — тоже сюда",
            "panels": [("Русский перевод — как в печати (ab → рус., оригинал в подсказке)",
                        "<pre>%s</pre>" % render_ru_print(ru)),
                       ("Разметка store (для цитирования в заметках)",
                        "<pre>%s</pre>" % esc(ru)),
                       ("Немецкий источник (de)",
                        "<pre>%s</pre>" % esc(rec.get("de") or "(store row not found)"))],
        })

    strata = sorted({it["filt"] for it in items})
    config = {
        "sheet_id": SHEET_ID,
        "title": "G5 · печатная годность — живая очередь, партия 1v2",
        "subtitle": ("%d карточек живой очереди (%d ai_translated; уже решено %d, "
                     "снято немецким фильтром %d) — переделка партии 1 по вердикту "
                     "25-07-2026: немецкий отсеян ДО показа человеку, RU-панель "
                     "показывает печатный вид" % (len(items), len(queue), n_decided,
                                                  n_flagged)),
        "footer": ("Approve = print-ready (run_batch пометит approved) · Reject = "
                   "не годен · Defer = needs_review. Экспорт валидируется против "
                   "review/locks/%s.lock.json перед любым применением." % SHEET_ID),
        "approve_label": "Print-ready", "reject_label": "Reject",
        "filters": [(s, s) for s in strata],
        "generated": GENERATED,
        "strict_review": {"reviewer": "", "require_all_votes": False,
                          "require_reject_note": True},
    }
    config.update(standard_config(
        save_as="RussianTranslation\\review\\%s_decisions.json" % SHEET_ID))

    doc = render_review_sheet(items, config, extras=True)
    doc, chash = stamp(doc)
    os.makedirs(REVIEW, exist_ok=True)
    with io.open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(doc)
    lock = write_lock(SHEET_ID, chash, [it["id"] for it in items], GENERATED,
                      locks_dir=args.locks_dir, gate="G5", source_html=args.out)
    print("G5 sheet: %d cards -> %s\n  %s\n  lock -> %s"
          % (len(items), args.out, chash, lock))


if __name__ == "__main__":
    main()
