#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_g5_review_sheet.py — the G5 starter review sheet (H1404, ruling D10).

First sheet of the G5 publication-review lane under the binding standard: a
deterministic ~150-card slice of the LIVE review queue
(``src/_review_queue.jsonl``, 11,163 ``ai_translated`` rows as of 25-07-2026),
NOT the 2026-06 legacy 217-row triage queue — that generation's ``ord:N`` ids
no longer resolve against the current store, so its judge annotations are
audit history, not a work queue (see the deep manual §"queue generations").

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
from review_sheet_standard import pwg_entry_href, slp1_iast, standard_config

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(HERE)
REVIEW = os.path.join(RT, "review")

SHEET_ID = "g5-live-queue-batch1-2026-07-25"
GENERATED = "2026-07-25"


def esc(s):
    return html.escape("" if s is None else str(s))


def load_jsonl(path):
    return [json.loads(l) for l in io.open(path, encoding="utf-8") if l.strip()]


def pick(queue_rows, n):
    """Round-robin across sorted roots; within a root, review_id order."""
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
    ap.add_argument("--out", default=os.path.join(REVIEW, "g5_batch1_sheet.html"))
    ap.add_argument("--locks-dir", default=None)
    args = ap.parse_args()

    queue = load_jsonl(args.queue)
    store = {}
    for rec in load_jsonl(args.store):
        store[(rec.get("subcard"), str(rec.get("sense_tag")))] = rec

    chosen = pick(queue, args.n)
    items = []
    for r in chosen:
        # review_id row:NNNNNN:subcard:<subcard>#<sense_tag> — join the store
        # for the German source panel and the real root.
        rec = {}
        rid = r["review_id"]
        if ":subcard:" in rid and "#" in rid:
            sub, tag = rid.split(":subcard:", 1)[1].rsplit("#", 1)
            rec = store.get((sub, tag), {})
        root = (rec.get("provenance") or {}).get("root") or r.get("key1") or ""
        stratum = rec.get("stratum") or "na"
        items.append({
            "id": rid,
            "filt": stratum,
            "title": rec.get("iast") or slp1_iast(r.get("key1") or ""),
            "title_href": pwg_entry_href(root),
            "badges": [rec.get("source_type") or "?", stratum],
            "question": ("Годен ли этот русский перевод в печать как есть? "
                         '<span class="muted">(Print-ready = да, как напечатано ниже · '
                         "Reject = нет (почему — в заметку) · Defer = отложить "
                         "в needs_review)</span>"),
            "note_placeholder": "reject → что именно не так; частичная правка — тоже сюда",
            "panels": [("Русский перевод (ru)",
                        "<pre>%s</pre>" % mark_cyrillic(esc(r.get("ru") or ""))),
                       ("Немецкий источник (de)",
                        "<pre>%s</pre>" % esc(rec.get("de") or "(store row not found)"))],
        })

    strata = sorted({it["filt"] for it in items})
    config = {
        "sheet_id": SHEET_ID,
        "title": "G5 · печатная годность — живая очередь, партия 1",
        "subtitle": ("первые %d карточек живой очереди (11,163 ai_translated) под "
                     "стандартом привязки H1404 — round-robin по корням" % len(items)),
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
