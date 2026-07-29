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

**batch1v3 (26-07-2026, P1 ruling).** MG ruled the voting-queue triage
`@DECIDE` (screening audit §7): cards carrying a machine-findable store flag
are AUTO-REJECTED from sheets — ``review_residue_gate.machine_flags`` (D1
Cyrillic-in-``{#…#}`` · D3 gloss-wrapper drift · D4 slot-count mismatch) is now
a second hard pre-filter, so batch1v2 (which could still show D-class rows —
they are not German-visible) was superseded before any vote.

Instrument per ruling D6: plain approve/reject/defer (approve = print-ready,
maps to run_batch's ``approved``; reject = not print-ready; defer =
``needs_review``). No DA rating — G5 is a bulk edition decision, not a quality
scale. Exports flow: download/auto-save decisions.json → ``validate_decisions``
→ ``apply_decisions --gate G5`` (merges into ``src/_review_queue.csv`` and runs
``run_batch.py validate_review``).

**batch1v3 re-issue (29-07-2026, H1808).** MG filed five defects while voting
it. Card rendering moved out to ``g5_card_render`` (see its docstring for which
defect each panel answers); the type scale and the anatomy colouring were fixed
a level down, in csl-pyutil v0.6.0. Because the fixes are PRESENTATION only,
``--pin-ids <lock>`` re-renders exactly the locked ids, in order, after proving
every card's content digest is unchanged — same ``sheet_id`` + same ids means a
vote already in the browser's localStorage still binds. The lock now carries
``item_digests`` so the next such re-issue can prove that from the lock alone.

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
import hashlib
import html
import io
import json
import os
import re
import sys

from csl_pyutil import render_review_sheet
from review_binding import stamp, write_lock
from review_residue_gate import machine_flags, visible_german
from review_sheet_standard import pwg_entry_href, slp1_iast, standard_config
import g5_card_render as cardrender

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(HERE)
REVIEW = os.path.join(RT, "review")

SHEET_ID = "g5-live-queue-batch1v3-2026-07-26"
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


def card_digest(ru, de):
    """What a card SHOWS, independent of how it is rendered. A presentation-only
    re-issue must leave this untouched for every pinned id — that is the whole
    proof that re-cutting the lock cannot invalidate a vote already cast."""
    h = hashlib.sha256()
    h.update((ru or "").encode("utf-8"))
    h.update(b"\x00")
    h.update((de or "").encode("utf-8"))
    return h.hexdigest()[:16]


def legacy_digests_from_sheet(path):
    """Digests recovered from a PRE-H1808 sheet (`<pre>` store + de panels), for
    locks minted before `item_digests` existed. Returns {} when the file is absent
    or is not in that format — the caller then refuses rather than assuming."""
    if not path or not os.path.exists(path):
        return {}
    doc = io.open(path, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r'<section class="card" data-id="([^"]+)"(.*?)</section>', doc, re.S):
        body = m.group(2)
        ru = re.search(r"<h4>Разметка store[^<]*</h4><pre>(.*?)</pre>", body, re.S)
        de = re.search(r"<h4>Немецкий источник \(de\)</h4><pre>(.*?)</pre>", body, re.S)
        if not ru or not de:
            return {}
        out[m.group(1)] = card_digest(html.unescape(ru.group(1)),
                                      html.unescape(de.group(1)))
    return out


def card_panels(ru, de):
    """The three panels, per H1808 — see g5_card_render for what each one is and
    which of MG's five defects it answers."""
    panels = [(cardrender.PANEL_PRINT, cardrender.print_panel(ru)),
              (cardrender.PANEL_STORE, cardrender.store_panel(ru))]
    if cardrender.same_text(ru):
        # MG: "не понятно, чем ... отличается" — on these cards it genuinely does
        # not, so say so instead of leaving two identical-looking blocks.
        panels[1] = (panels[1][0],
                     panels[1][1] + '<div class="panelnote">Текст тот же, что в '
                     'панели 1 — эта строка не несёт разметки, кроме показанной '
                     'цветом; панель нужна только для точной цитаты в заметке.</div>')
    panels.append((cardrender.PANEL_DE, cardrender.de_panel(de)))
    return panels


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
    ap.add_argument("--out", default=os.path.join(REVIEW, "g5_batch1v3_sheet.html"))
    ap.add_argument("--locks-dir", default=None)
    ap.add_argument("--pin-ids", metavar="LOCK",
                    help="re-render EXACTLY the review_ids in an existing lock "
                         "file, in its order, bypassing selection and the "
                         "pre-filters. This is how a sheet is re-issued for a "
                         "PRESENTATION fix without disturbing a vote in "
                         "progress: same sheet_id + same ids means the browser's "
                         "localStorage votes still bind (H1808). Refuses if any "
                         "pinned card's RU text has drifted since the lock.")
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

    pinned_lock = None
    if args.pin_ids:
        pinned_lock = json.load(io.open(args.pin_ids, encoding="utf-8"))
        by_id = {(r.get("review_id") or ""): r for r in queue}
        chosen = []
        for rid in pinned_lock["ids"]:
            row = by_id.get(rid)
            if row is None:                     # positional id aged out of the queue
                row = {"review_id": rid, "key1": "", "ru": ""}
            chosen.append(row)
        print("pinned re-issue: %d ids from %s"
              % (len(chosen), os.path.basename(args.pin_ids)))
        n_decided = n_german = n_mflag = 0
        return finish(args, chosen, store_rec, queue, n_decided, n_german, n_mflag,
                      pinned_lock)

    decided = load_decided_ids(args.review_csv)
    n_decided = n_german = n_mflag = 0
    candidates = []
    for r in queue:
        if (r.get("review_id") or "") in decided:
            n_decided += 1
            continue
        rec = store_rec(r)
        ru = rec.get("ru") or r.get("ru") or ""
        if not args.no_residue_gate:
            if visible_german(ru):
                n_german += 1
                continue
            # P1 ruling 26-07-2026: machine-flagged cards are auto-rejected from
            # sheets — triage/repair (H1651) happens before a human vote.
            if machine_flags(ru, rec.get("de") or ""):
                n_mflag += 1
                continue
        candidates.append(r)
    print("queue %d | already decided %d | German excluded %d | machine-flag "
          "excluded %d | eligible %d"
          % (len(queue), n_decided, n_german, n_mflag, len(candidates)))

    chosen = pick(candidates, args.n)
    return finish(args, chosen, store_rec, queue, n_decided, n_german, n_mflag, None)


def finish(args, chosen, store_rec, queue, n_decided, n_german, n_mflag, pinned_lock):
    items, digests = [], {}
    for r in chosen:
        rec = store_rec(r)
        root = (rec.get("provenance") or {}).get("root") or r.get("key1") or ""
        stratum = rec.get("stratum") or "na"
        ru = rec.get("ru") or r.get("ru") or ""
        de = rec.get("de") or "(store row not found)"
        digests[r["review_id"]] = card_digest(ru, de)
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
            "panels": card_panels(ru, de),
        })

    force_lock = False
    if pinned_lock is not None:
        # A pinned re-issue re-cuts the lock, which write_lock rightly refuses by
        # default (H1703). Force it ONLY after proving every card still shows the
        # same content, so votes already cast cannot be invalidated by the re-cut.
        was = pinned_lock.get("item_digests") or legacy_digests_from_sheet(args.out)
        if not was:
            raise SystemExit(
                "--pin-ids: the lock carries no item_digests and %s could not be "
                "read in the pre-H1808 panel format, so drift cannot be proven.\n"
                "  Re-issuing blind could change what a half-finished vote is "
                "voting on. Re-run without --pin-ids to cut a fresh sheet."
                % os.path.basename(args.out or ""))
        drift = sorted(i for i, d in digests.items() if was.get(i) != d)
        if drift:
            raise SystemExit(
                "--pin-ids: %d of %d pinned cards changed content since the lock "
                "(%s%s).\n  A presentation re-issue must not move the text under "
                "a vote. Cut a fresh batch instead."
                % (len(drift), len(digests), ", ".join(drift[:3]),
                   " …" if len(drift) > 3 else ""))
        print("  drift check: %d/%d pinned cards byte-identical to the locked "
              "generation" % (len(digests), len(digests)))
        force_lock = True

    strata = sorted({it["filt"] for it in items})
    if pinned_lock is not None:
        subtitle = ("%d карточек — переиздание партии 1v3 БЕЗ смены состава "
                    "(те же %d review_id, что в локе; голоса в браузере "
                    "сохраняются). Изменено только оформление: печатный вид с "
                    "кликабельными цитатами, разметка store с цветовой анатомией, "
                    "подсказки к пометам NWS, шрифт +150%%" % (len(items), len(items)))
    else:
        subtitle = ("%d карточек живой очереди (%d ai_translated; уже решено %d, "
                    "снято немецким фильтром %d, снято машинными флагами D1/D3/D4 "
                    "%d — авто-reject по решению P1 26-07) — немецкий и машинные "
                    "дефекты отсеяны ДО показа человеку, RU-панель показывает "
                    "печатный вид" % (len(items), len(queue), n_decided,
                                      n_german, n_mflag))
    config = {
        "sheet_id": SHEET_ID,
        "title": "G5 · печатная годность — живая очередь, партия 1v3",
        "subtitle": subtitle,
        "footer": ("Approve = print-ready (run_batch пометит approved) · Reject = "
                   "не годен · Defer = needs_review. Экспорт валидируется против "
                   "review/locks/%s.lock.json перед любым применением.<br>"
                   "Цвета в панелях 2–3 (разметка store и немецкий источник): %s"
                   % (SHEET_ID, cardrender.legend_html())),
        "approve_label": "Print-ready", "reject_label": "Reject",
        "filters": [(s, s) for s in strata],
        "generated": GENERATED,
        "extra_css": cardrender.EXTRA_CSS,
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
    lock_path = write_lock(SHEET_ID, chash, [it["id"] for it in items], GENERATED,
                           locks_dir=args.locks_dir, gate="G5", source_html=args.out,
                           force=force_lock)
    # additive: lets the NEXT presentation re-issue prove drift from the lock
    # alone, instead of having to parse the previous sheet's HTML.
    lock = json.load(io.open(lock_path, encoding="utf-8"))
    lock["item_digests"] = digests
    with io.open(lock_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(lock, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("G5 sheet: %d cards -> %s\n  %s\n  lock -> %s"
          % (len(items), args.out, chash, lock_path))


if __name__ == "__main__":
    main()
