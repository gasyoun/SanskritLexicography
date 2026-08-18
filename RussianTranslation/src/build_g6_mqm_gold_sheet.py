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

**Evidence panels (H1801, MG's ruling of 28-07-2026).** The first real vote on
this sheet (H1796) showed the reviewer only the form, the Russian and the LLM's
label; one label was reversed at adjudication once the withheld evidence
surfaced (id 122, ``na`` -> «словно», ``08_rigveda``), and four further cards
carried the same complaint. Every card now carries, BEFORE the vote: a
period-routed dictionary sense list (Vedic ⇒ GRA first, else MW/PWG), a Whitney
root line, attested contexts from the card's own work, and the ranked A2/A4
Sa→Ru glossary figures — or an explicit ``evidence not found`` line naming what
was searched. Built by ``gold_evidence_panel.py``; ``--no-evidence`` reproduces
the pre-H1801 layout for diffing.

**V9 + the full 320-card cut (H215, 14-08-2026).** The generator now emits the
two things the shared emitter requires of every sheet in the org: a screening
block (``sheet_screening``) stating what was machine-screened before a human
sees a card, and an evidence manifest (``review_evidence_preflight``) declaring
per card what was joined and what was deliberately withheld — the adjudicated
A/B/C grade above all, which is keyed on these same ids but is derived from the
very LLM label under review. ``csl_pyutil.render_review_sheet`` runs the V9
preflight over the rendered HTML and raises before returning it, so a sheet that
leaks SLP1 into Russian prose cannot be built (see ``declared_slp1_tokens`` for
the four machine regions where SLP1 is shown on purpose). Two display changes
followed: dictionary headwords render in IAST with the SLP1 key demoted to a
machine span, and ``corpus_contexts`` streams the work file twice instead of
materializing it — the single-pass version was a MemoryError on the 150 MB
``dic_mw.jsonl``, which is why the 20-card starter built and the 320-card cut
did not (the small cut never drew a card from a large work).

The starter generation (``SHEET_ID``/``GENERATED`` below) is FROZEN: it carries
applied votes, its lock binds the pre-V9 hash, and ``write_lock`` will refuse to
overwrite it. A new cut passes its own ``--sheet-id`` and ``--generated``.

The gold scaffold is public (tracked), but the sheet HTML stays gitignored
(``review/*_sheet.html``) like every other sheet — the committed artifact is
the metadata lock.

Run (from RussianTranslation/):
  python src/build_g6_mqm_gold_sheet.py [--n 20] [--gold-set PATH]
  python src/build_g6_mqm_gold_sheet.py --no-evidence   # pre-H1801 layout
  # the full 320-card cut (H215):
  python src/build_g6_mqm_gold_sheet.py --n 320 \\
      --sheet-id h215-gold-full-320-2026-08-14 --generated 2026-08-14 \\
      --out review/h215_gold_full_320_sheet.html \\
      --coverage-json review/h215_gold_full_320_evidence_coverage.json
"""
import argparse
import collections
import html
import io
import json
import os
import re
import sys

from csl_pyutil import RU_UI_STRINGS, mark_cyrillic, render_review_sheet
from packset_output import emit_sheet
from review_binding import stamp, write_lock
from review_sheet_standard import standard_config
from review_evidence_preflight import EvidenceManifest
from sheet_screening import screening_block

import gold_evidence_panel as evidence

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(HERE)
REVIEW = os.path.join(RT, "review")

LEGACY_SHEET_ID = "g6-mqm-gold-starter-2026-07-25"
LEGACY_GENERATED = "2026-07-25"

#: The two H1796 follow-ups landed within a day of each other and re-cut the
#: SAME sheet: H1802 added the required reject-label picker, H1801 the evidence
#: panels. They are one instrument, not two, so they share one generation.
#: ``g6-mqm-gold-starter-reject-picker-2026-07-28`` (H1802, picker only) was
#: never voted and is superseded by this id; its lock stays as a record.
#: The 2026-07-25 generation keeps its own id + lock (LEGACY_SHEET_ID) — its
#: votes are already applied (H1796) and must stay validatable.
SHEET_ID = "g6-mqm-gold-starter-evidence-picker-2026-07-29"
GENERATED = "2026-07-29"
SUPERSEDED_SHEET_IDS = ("g6-mqm-gold-starter-reject-picker-2026-07-28",)

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


_WORD = re.compile(r"[A-Za-z]+")


def declared_slp1_tokens(chosen, panels_by_id):
    """SLP1 this sheet shows deliberately, enumerated from the panel data itself.

    V9's rule is "humans read IAST; SLP1 belongs in ids and machine columns
    only". This instrument has four such machine regions, and every one of them
    is evidence a reviewer needs *as the machine stored it*:

    * the card's own key/id — the join key the vote is recorded against;
    * the matched-form window inside a context hit — that IS the proof the form
      was attested, so re-rendering it in IAST would destroy the evidence;
    * the dictionary panel's lookup trace and headword key — the headword itself
      is rendered in IAST (``_key_iast``) with the SLP1 kept beside it in a
      demoted machine span, and the ``searched`` lines are literal lookup keys
      (``dcs_lemma2root[antarDA]``, ``MW k1=avAkSAKa``);
    * the dictionary entry body, the quoted corpus passage, and the work codes
      in the glossary's per-work counts — verbatim printed source and its
      citation sigla (MBh, BhP, BhG, AitBr, MaitrUp …), which are source
      abbreviations, not transliteration, and travel with the quoted text.

    Declaring these from the data, rather than silencing the check globally,
    keeps the gate live over everything else — the Russian instructions, the
    card's ``sa``/``ru``, the labels — where a stray SLP1 token still fails the
    build.
    """
    out = set()
    for r in chosen:
        for field in (r.get("slp1"), r.get("id")):
            out.update(_WORD.findall(str(field or "")))
    for p in (panels_by_id or {}).values():
        for name in ("dictionary", "root", "contexts", "glossary"):
            panel = p.get(name) or {}
            for line in panel.get("searched") or []:
                out.update(_WORD.findall(str(line or "")))
        for e in (p.get("dictionary") or {}).get("entries", []) or []:
            out.update(_WORD.findall(str(e.get("key") or "")))
            out.update(_WORD.findall(str(e.get("text") or "")))
        for r in (p.get("root") or {}).get("roots", []) or []:
            for field in (r.get("root_slp1"), r.get("lemma")):
                out.update(_WORD.findall(str(field or "")))
        for d in (p.get("root") or {}).get("lemmas", []) or []:
            out.update(_WORD.findall(str(d.get("lemma") or "")))
        for hit in (p.get("contexts") or {}).get("hits", []) or []:
            for field in (hit.get("sa_slp1_window"), hit.get("work"),
                          hit.get("passage"), hit.get("sa")):
                out.update(_WORD.findall(str(field or "")))
        for g in (p.get("glossary") or {}).get("glosses", []) or []:
            for work, _n in g.get("top_works") or []:
                out.update(_WORD.findall(str(work or "")))
    return out


def build_manifest(sheet_id, items, panels_by_id, gold_set_path):
    """What this sheet joined per card, and what it deliberately did not (H1889).

    The V9 preflight exists to stop a sheet asking a human what the repo already
    answers — the exact complaint MG raised about voting rows the machine had
    already ruled. Every field here is one the evidence panels actually rendered.
    """
    man = EvidenceManifest(sheet_id, [it["id"] for it in items])
    rel = lambda p: os.path.relpath(p, RT).replace("\\", "/")  # noqa: E731

    man.declare_joined(rel(gold_set_path), ["id", "slp1", "sa", "ru", "kind",
                                            "period", "work", "label"])
    for key, fields in (("gra", ["senses"]), ("mw", ["senses"]), ("pwg", ["senses"]),
                        ("whitney", ["root"]), ("corpus", ["passage", "sa", "ru"]),
                        ("surface_glossary", ["ru_rank"])):
        path = evidence.DEFAULT_PATHS.get(key)
        if path:
            man.declare_joined(str(path).replace("\\", "/"), fields)

    for card_id, p in (panels_by_id or {}).items():
        man.add_card(card_id,
                     [n for n in ("dictionary", "root", "contexts", "glossary")
                      if p[n]["found"]],
                     omitted=[n for n in ("dictionary", "root", "contexts", "glossary")
                              if not p[n]["found"]])

    man.declare_omitted_path(
        "gold/grade_gold.jsonl",
        "the agent-adjudicated A/B/C publication grade is keyed on these same 320 ids, "
        "but it answers a DIFFERENT question (publication grade) than this instrument "
        "(6-label semantic typology), and it is derived from the very LLM label under "
        "review here — showing it would anchor the reviewer on the thing being judged")
    man.declare_omitted(
        "corpus_lexicon.jsonl (1.09M pairs)",
        "the alignment lexicon these gold rows were sampled FROM; re-showing the "
        "source row would restate the card, not add independent evidence")
    return man


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--gold-set", default=os.path.join(RT, "gold", "gold_set.jsonl"))
    ap.add_argument("--out", default=os.path.join(REVIEW, "g6_mqm_starter_sheet.html"))
    ap.add_argument("--locks-dir", default=None)
    ap.add_argument("--no-evidence", action="store_true",
                    help="pre-H1801 layout (no evidence panels) — for diffing only")
    ap.add_argument("--sheet-id", default=None)
    ap.add_argument("--github-inbox", action="store_true",
                    help="add the «Сохранить в GitHub» control and the hydrate read "
                         "(H2991). Changes the rendered bytes, so it re-cuts the "
                         "sheet -- never turn it on mid-vote")
    ap.add_argument("--client-id", default="Ov23lifQmcuDYuTw0ZWv",
                    help="public OAuth App client id (ships in the HTML by design)")
    ap.add_argument("--device-url",
                    default="https://kosha.193.232.229.92.sslip.io/gh-device",
                    help="CORS relay for the device-code exchange (FINDINGS §477)")
    ap.add_argument("--pack-size", type=int, default=0,
                    help="split into pack pages of at most N cards, sharing one "
                         "sheet_id (H3098). 0 = one file, the historical default")
    ap.add_argument("--hub-name", default=None,
                    help="published directory stem for the pack pages "
                         "(default: the --out filename stem)")
    ap.add_argument("--generated", default=None,
                    help="generation date for the config + lock; a NEW cut of this "
                         "instrument (e.g. the full 320) must pass its own date, "
                         "since a voted generation is never regenerated in place")
    ap.add_argument("--coverage-json", default=None,
                    help="write the per-card evidence coverage as JSON")
    args = ap.parse_args()
    sheet_id = args.sheet_id or (LEGACY_SHEET_ID if args.no_evidence else SHEET_ID)
    generated = args.generated or GENERATED

    rows = [json.loads(l) for l in io.open(args.gold_set, encoding="utf-8") if l.strip()]
    chosen = pick(rows, args.n)

    panels_by_id = {} if args.no_evidence else evidence.build_panels(chosen)

    legend = "".join("<div><span class=\"chip\">%s</span> %s</div>"
                     % (esc(l), esc(LABEL_RU[l])) for l in LABELS)
    items = []
    for r in chosen:
        # MG: «Это все надо давать ДО, а не ПОСЛЕ» — the evidence sits between
        # the rendering and the label, so it is read before the label is judged.
        panels = [("Санскрит (sa)", "<pre>%s</pre>" % esc(r.get("sa"))),
                  ("Русский (ru)", "<pre>%s</pre>" % mark_cyrillic(esc(r.get("ru"))))]
        if not args.no_evidence:
            panels.extend(evidence.render_panels(panels_by_id[str(r["id"])]))
        panels.append(("Ярлык LLM · типология MQM",
                       "<pre><b>%s</b></pre>%s" % (esc(r["label"]), legend)))
        items.append({
            "id": str(r["id"]),
            "filt": r["period"],
            "question": ("Верен ли ярлык LLM <b>«%s»</b> для этого перевода? "
                         '<span class="muted">(reject → выберите правильный ярлык '
                         "из списка ниже)</span>" % esc(r["label"])),
            "title": r.get("sa") or r.get("slp1") or str(r["id"]),
            "badges": [r["period"], r["kind"], r.get("work") or ""],
            # H1802: the label is a required select control, so the note is
            # free-text rationale only — never the carrier of the answer.
            "note_placeholder": "необязательный комментарий к решению",
            "panels": panels,
        })

    periods = []
    for r in chosen:
        if r["period"] not in periods:
            periods.append(r["period"])
    config = {
        "sheet_id": sheet_id,
        "title": "G6 · золотой стандарт — стартовый лист MQM",
        "subtitle": ("%d карточек из gold/gold_set.jsonl (320), стратификация "
                     "period × kind; типология из 6 ярлыков%s"
                     % (len(items), "" if args.no_evidence else
                        "; каждая карточка несёт словарь, корень и контексты ДО голоса")),
        "footer": ("Approve = ярлык LLM верен · Reject = неверен (выберите правильный "
                   "ярлык из списка) · Defer = на адjudication. Экспорт "
                   "валидируется против review/locks/%s.lock.json." % sheet_id),
        "approve_label": "Label верен", "reject_label": "Label неверен",
        "filters": [(p, p) for p in sorted(periods)],
        "generated": generated,
        "strict_review": {"reviewer": "", "require_all_votes": True,
                          "require_reject_note": True},
        "reject_labels": [(l, LABEL_RU[l]) for l in LABELS if l != "correct"],
    }
    # V9 SLP1 leak check: this instrument shows SLP1 on purpose in exactly two
    # machine columns — the card's own key and the matched-form window inside a
    # context hit, which IS the evidence that the form was attested. Those are
    # declared here rather than silenced globally, so any SLP1 that leaks into
    # actual prose still fails the build. Citation sigla (MBh, BhP, AitBr …) are
    # source abbreviations, not transliteration, and travel with the quoted text.
    config["preflight"] = {"allow_slp1_tokens": tuple(sorted(
        declared_slp1_tokens(chosen, panels_by_id)))}
    config.update(standard_config(
        save_as="RussianTranslation\\review\\%s_decisions.json" % sheet_id))
    # H2991/H3105 — «Сохранить в GitHub»: each pack writes
    # decisions/<sheet_id>/pack-NN.json to the public inbox and hydrates from it
    # on load, so 32 packs stop meaning 32 files to shepherd by hand and
    # merge_vote_packs.py can do the accumulating. client_id is public by design
    # (it ships in the HTML); device_url is the CORS relay, without which GitHub's
    # device endpoints cannot be read from a static page at all (FINDINGS §477).
    # Leave `branch` unset: the contents API then writes to the inbox repo's own
    # default branch, which is `master` -- guessing `main` was the v0.17.0 bug.
    # This instrument is Russian end to end -- title, subtitle, footer, both vote
    # labels, every reject label. The emitter's own chrome was still English, and
    # V17 has just made the most-read element on the page (the progress bar and
    # the whole-sheet ETA) part of that chrome. One line fixes all of it.
    config["ui_strings"] = RU_UI_STRINGS
    if args.github_inbox:
        config["github_inbox"] = {
            "repo": "gasyoun/vote-inbox",
            "client_id": args.client_id,
            "device_url": args.device_url,
        }

    # H1649/H1650: every sheet must state what was screened before a human sees it.
    # Honest accounting for this instrument: every card carries an LLM label from the
    # gold scaffold (agent), evidence panels are dictionary/root/context lookups, and
    # every card still goes to a human — nothing is auto-resolved away here.
    cov = evidence.coverage(panels_by_id) if panels_by_id else {}
    looked_up = max(cov.get("dictionary", 0), cov.get("root", 0),
                    cov.get("contexts", 0), cov.get("glossary", 0))
    sc = screening_block(
        deterministic=0, lookup=looked_up, agent=len(items), human=len(items),
        evidence_path="RussianTranslation/gold/HUMAN_GOLD_PROTOCOL.md",
        rules=["mqm-6-label-typology", "h1801-evidence-before-label",
               "h1802-reject-label-picker"],
    )
    os.makedirs(REVIEW, exist_ok=True)
    # H3098: --pack-size splits a long sheet into pack pages sharing one sheet_id
    # (and therefore one localStorage record). 0 keeps the historical single file.
    paths, lock, n_packs = emit_sheet(
        items, config, args.out,
        screening=sc,
        manifest=build_manifest(sheet_id, items, panels_by_id, args.gold_set),
        generated=generated, locks_dir=args.locks_dir, gate="G6",
        pack_size=args.pack_size, hub_name=args.hub_name)
    if n_packs:
        print("G6 sheet: %d cards -> %d packs of <=%d"
              % (len(items), n_packs, args.pack_size))
        for p in paths:
            print("    %s" % p)
        print("  lock -> %s" % lock)
    else:
        print("G6 sheet: %d cards -> %s\n  lock -> %s" % (len(items), args.out, lock))
    if panels_by_id:
        cov = evidence.coverage(panels_by_id)
        print("  evidence: dictionary %d/%d · root %d/%d · contexts %d/%d · glossary %d/%d"
              % (cov["dictionary"], cov["cards"], cov["root"], cov["cards"],
                 cov["contexts"], cov["cards"], cov["glossary"], cov["cards"]))
        if args.coverage_json:
            with io.open(args.coverage_json, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(panels_by_id, fh, ensure_ascii=False, indent=1, sort_keys=True)
            print("  coverage -> %s" % args.coverage_json)


if __name__ == "__main__":
    main()
