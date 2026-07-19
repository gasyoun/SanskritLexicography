#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_h180_review_sheets.py — the four (three buildable) H180 human HTML voting
sheets, following the org /review-sheet convention (interactive HTML, never
markdown checkboxes — [[feedback_interactive_review_not_checkboxes]]).

Rendering is the shared csl_pyutil.render_review_sheet emitter (v0.3.0 — this
script was its donor, so the item dicts already match its schema), extras on,
plus the 19-07-2026 V1–V8 standard wiring from review_sheet_standard (visible
id chips, IAST headword links into the kosha colocation viewer, taller note
box, save-as banner, RU-run highlighting). The export matches the {sheet_id,
generated, decided, items:[{id, decision, note}]} contract that
/decisions-apply consumes; the download names itself <sheet_id>_decisions.json
(the emitter's fix for the donor's bare 'decisions.json'). localStorage keys
('review-sheet:' + sheet_id) and the sheet_ids are unchanged, so any votes
already cast in a browser survive regeneration.

Three sheets are built (the fourth — Arm-A-vs-B coherence — needs the deferred
Arm-B model run, so it is intentionally skipped until synth output exists):

  1. typology  — κ-label sample: the 7 five-layer roots' non-pwg sub-card senses
                 + a deterministic 30-item random tail; confirm/correct the
                 LLM-proposed relationship subtype (reject → write the right
                 subtype in the note, for κ vs the LLM proposal).
  2. learner   — threshold calibration: a stratified sample across the retention
                 bands; is this headword learner-core (does a Russian student
                 need it)?
  3. reglue    — 15-card spot-check: is each rendered re-glue well-formed
                 (supplements at sensible senses, cancellations visible)?

PUBLISH SAFETY: the typology + reglue sheets embed translated `ru` bodies from
the gitignored/unpublished store, and this repo is PUBLIC — so the generated
HTML + the samples that carry translations are gitignored (see .gitignore). Only
this generator is committed; sheets are opened locally from file:// and voted in
the browser, then decisions.json feeds /decisions-apply.

Inputs (all local): src/pwg_ru_translated.jsonl, src/pwg_ru_relationships.jsonl,
pwg_ru/learner_scores.tsv, pwg_ru/reglue/*.md
Outputs (local, gitignored): review/h180_{typology,learner,reglue}_sheet.html
                              review/h180_{typology,learner,reglue}_sample.jsonl

Run: python src/build_h180_review_sheets.py
"""
import sys, os, io, json, html, re, collections

from csl_pyutil import render_review_sheet, mark_cyrillic
from review_sheet_standard import standard_config, slp1_iast, pwg_entry_href

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STORE = os.path.join(HERE, "pwg_ru_translated.jsonl")
REL = os.path.join(HERE, "pwg_ru_relationships.jsonl")
LEARNER = os.path.join(ROOT, "pwg_ru", "learner_scores.tsv")
REGLUE_DIR = os.path.join(ROOT, "pwg_ru", "reglue")
REVIEW = os.path.join(ROOT, "review")
GENERATED = "2026-07-06"

FIVE_LAYER = ["yat", "vraj", "rakz", "jIv", "gA", "Sam", "Cid"]


def esc(s):
    return html.escape("" if s is None else str(s))


def write_sheet(slug, cfg, items):
    os.makedirs(REVIEW, exist_ok=True)
    # sample jsonl (audit trail of exactly what was shown)
    sample_path = os.path.join(REVIEW, f"h180_{slug}_sample.jsonl")
    with io.open(sample_path, "w", encoding="utf-8") as fh:
        for it in items:
            fh.write(json.dumps({k: it[k] for k in ("id", "filt", "title") if k in it},
                                ensure_ascii=False) + "\n")
    # 19-07-2026 standard fragment (V3 show_ids, V6 note height, V8 save-as
    # banner); the sheet's own keys win on collision. Rendering is the shared
    # emitter — same localStorage key scheme as the hand-rolled donor template,
    # so prior in-browser votes survive.
    config = standard_config(
        save_as="RussianTranslation\\pwg_ru\\eval\\h180_%s.decisions.json" % slug)
    config.update(cfg)
    config["generated"] = GENERATED
    doc = render_review_sheet(items, config, extras=True)
    out = os.path.join(REVIEW, f"h180_{slug}_sheet.html")
    with io.open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(doc)
    print(f"  {slug:9s} {len(items):3d} items -> {out}")
    return out


# ----------------------------------------------------------------------------- data
def load_store():
    by_sub = {}
    for line in io.open(STORE, encoding="utf-8"):
        line = line.strip()
        if line:
            d = json.loads(line)
            by_sub[(d["subcard"], str(d.get("sense_tag")))] = d
    return by_sub


def build_typology(by_sub):
    rows = [json.loads(l) for l in io.open(REL, encoding="utf-8") if l.strip()]
    # CORE: the 7 five-layer roots yield ~640 supplements — far too many for a κ
    # pass. Stratify by (layer, subtype) and cap ~8 per stratum so every subtype is
    # represented (κ needs coverage of each class), aiming for ~a few dozen.
    core_pool = collections.defaultdict(list)
    for r in rows:
        if r["key1"] in FIVE_LAYER:
            core_pool[(r["layer"], r["relationship"]["subtype"])].append(r)
    core = []
    for key in sorted(core_pool):
        pool = sorted(core_pool[key], key=lambda r: (r["subcard"], r["sense_tag"]))
        step = max(1, len(pool) // 8)
        core.extend(pool[::step][:8])
    # TAIL: deterministic 30-item sample, evenly-strided over the sorted remainder.
    tail = sorted((r for r in rows if r["key1"] not in FIVE_LAYER),
                  key=lambda r: (r["subcard"], r["sense_tag"]))
    step = max(1, len(tail) // 30)
    tail_sample = tail[::step][:30]
    sample = core + tail_sample
    items = []
    for r in sample:
        rel = r["relationship"]; ip = rel["insertion_point"]
        rec = by_sub.get((r["subcard"], r["sense_tag"]), {})
        ru = esc(rec.get("ru", "(body not found)"))
        de = esc(rec.get("de", ""))
        # V4: the store row's provenance.root is the real SLP1 root; the
        # subcard prefix before '~~' is only the safe_root fallback.
        root = (rec.get("provenance") or {}).get("root") or r["subcard"].split("~~", 1)[0]
        proposal = (
            f'<pre>subtype   : <b>{esc(rel["subtype"])}</b>\n'
            f'op/dir    : {esc(rel["op"])} / {esc(rel["direction"])}\n'
            f'target    : {esc(ip["target_sense"])} (anchor {esc(ip["anchor"])})\n'
            f'evidence  : {esc(rel.get("evidence",""))}</pre>')
        items.append({
            "id": f'{r["subcard"]}::{r["sense_tag"]}',
            "filt": r["layer"],
            "title": f'{slp1_iast(r["key1"])} · {r["layer"]} · sense {r["sense_tag"]}',
            "title_href": pwg_entry_href(root),
            "badges": [rel["subtype"], "5-layer" if r["key1"] in FIVE_LAYER else "tail"],
            "question": (f'Is the proposed subtype <b>«{esc(rel["subtype"])}»</b> correct '
                         f'for this sub-card? <span class="muted">(reject → write the correct '
                         f'subtype in the note, for κ)</span>'),
            "note_placeholder": "if reject: correct subtype + why (e.g. 'nws_at_sense, attaches to sense 2')",
            "panels": [("LLM proposal (confidence: llm)", proposal),
                       ("Sub-card — Russian (ru)", f'<pre>{mark_cyrillic(ru)}</pre>'),
                       ("Sub-card — source (de)", f'<pre>{de}</pre>')],
        })
    return items


def build_learner():
    rows = []
    with io.open(LEARNER, encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 6:
                rows.append({"key1": p[0], "learner": float(p[1]), "learner_norm": float(p[2]),
                             "support": float(p[3]), "scholarly": float(p[4]), "dicts": p[5]})
    RU = ("KCH", "KOW", "KNA", "SMI", "FRI")

    def n_ru(r):
        return sum(c in r["dicts"] for c in RU)

    bands = {
        "solid": [r for r in rows if n_ru(r) >= 2],
        "koch1": [r for r in rows if "KCH" in r["dicts"] and n_ru(r) == 1],
        "medonly": [r for r in rows if r["learner"] == 0 and r["support"] > 0],
        "control": [r for r in rows if r["learner"] == 0 and r["support"] == 0 and r["scholarly"] > 0],
    }
    band_label = {"solid": "≥2 Russian dicts", "koch1": "Kochergina-only",
                  "medonly": "medium-only (learner=0)", "control": "scholarly-only control"}
    items = []
    for band, pool in bands.items():
        pool.sort(key=lambda r: r["key1"])
        step = max(1, len(pool) // 15)
        for r in pool[::step][:15]:
            scores = (f'<pre>learner_score : <b>{r["learner"]:.2f}</b>  (norm {r["learner_norm"]:.2f})\n'
                      f'support_score : {r["support"]:.2f}   (CAE/CCS/MD)\n'
                      f'scholarly     : {r["scholarly"]:.2f}   (PW/MW/AP — non-gating)</pre>')
            items.append({
                "id": f'learner::{r["key1"]}',
                "filt": band,
                "title": slp1_iast(r["key1"]),
                "title_href": pwg_entry_href(r["key1"]),
                "badges": [band_label[band]],
                "question": ('Does a Russian student need this headword? '
                             '<span class="muted">(approve = learner-core; reject = scholarly-only / skip)</span>'),
                "note_placeholder": "optional: why keep/drop for a learner edition",
                "panels": [("retention scores", scores),
                           ("dictionaries that kept it", f'<pre>{esc(r["dicts"])}</pre>')],
            })
    return items


def build_reglue():
    order = [("gA", 5), ("Cid", 5), ("Sam", 5), ("jIv", 5), ("rakz", 5), ("vraj", 5), ("yat", 5),
             ("DA", 4), ("Ap", 4), ("Bid", 4), ("Buj", 4), ("banD", 4), ("Sru", 4),
             ("viS", 3), ("siD", 3)]
    items = []
    for key1, nlayers in order:
        p = os.path.join(REGLUE_DIR, key1 + ".md")
        if not os.path.exists(p):
            continue
        body = io.open(p, encoding="utf-8").read()
        items.append({
            "id": f"reglue::{key1}",
            "filt": f"{nlayers}L",
            "title": slp1_iast(key1),
            "title_href": pwg_entry_href(key1),
            "badges": [f"{nlayers}-layer"],
            "question": ('Is this re-glue well-formed? <span class="muted">(supplements land at '
                         'sensible senses · cancellations visible · foreign fragments shown with RU · '
                         'nothing broken)</span>'),
            "note_placeholder": "if reject: what is misplaced / broken",
            "panels": [("rendered re-glue card", f'<pre>{mark_cyrillic(esc(body))}</pre>')],
        })
    return items


def main():
    by_sub = load_store()
    print("building H180 review sheets ...")

    write_sheet("typology", {
        "sheet_id": "h180-typology-kappa-2026-07-06",
        "title": "H180 · addenda-typology κ-label",
        "subtitle": "confirm/correct the LLM-proposed relationship subtype (7 five-layer roots + 30-item tail)",
        "footer": ("Approve = the LLM subtype is right · Reject = wrong (write the correct subtype "
                   "in the note — this is the second signal for κ) · Defer = can't tell."),
        "approve_label": "Correct", "reject_label": "Wrong",
        "filters": [("pw", "pw"), ("sch", "sch"), ("pwkvn", "pwkvn"), ("nws", "nws")],
    }, build_typology(by_sub))

    write_sheet("learner", {
        "sheet_id": "h180-learner-threshold-2026-07-06",
        "title": "H180 · learner-core threshold calibration",
        "subtitle": "is each PWG headword learner-core? — stratified across retention bands",
        "footer": ("Approve = a Russian student needs this headword (learner-core) · Reject = "
                   "scholarly-only / skip · Defer = unsure. Calibrates the learner_score cut."),
        "approve_label": "Learner-core", "reject_label": "Skip",
        "filters": [("solid", "≥2 RU"), ("koch1", "Koch-only"), ("medonly", "medium-only"), ("control", "control")],
    }, build_learner())

    write_sheet("reglue", {
        "sheet_id": "h180-reglue-spotcheck-2026-07-06",
        "title": "H180 · content-aware re-glue spot-check",
        "subtitle": "eyeball each of the 15 pilot re-glue cards (success criterion d)",
        "footer": ("Approve = well-formed re-glue · Reject = something misplaced/broken (say what "
                   "in the note) · Defer = unsure."),
        "approve_label": "Well-formed", "reject_label": "Broken",
        "filters": [("5L", "5-layer"), ("4L", "4-layer"), ("3L", "3-layer")],
    }, build_reglue())

    print("\nNOTE: the 4th sheet (Arm-A-vs-B coherence) is skipped — it needs the deferred "
          "Arm-B model run (synth_de_first.py generation) before there is a B output to compare.")
    print(f"open locally, e.g.:  start {os.path.join(REVIEW, 'h180_reglue_sheet.html')}")


if __name__ == "__main__":
    main()
