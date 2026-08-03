#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the PWG->RU/EN *progress* dashboard data.

Companion to the public article browser (article_site/, served at the repo
root of https://gasyoun.github.io/SanskritLexicography/). Where the article
site shows the *finished* translations, this shows *how far along the work is*
— the honest denominators for the verb lane, the nominal lane, store depth,
frequency coverage, and the corpus/TM asset.

WHY THIS RUNS LOCALLY, NOT IN CI: the numbers are derived from local-only /
gitignored artifacts (`RussianTranslation/src/pwg_ru_translated.jsonl`, the
`verb_batch_worklist.json` / `nominal_batch_worklist.json` snapshots, the
frequency manifest). GitHub Actions never checks those out, so — exactly like
`build_article_site.py` — this is run on the residential machine and only the
tiny aggregate `progress_data.json` (+ the append-only `progress_timeseries.json`)
is committed. The `findings-dashboard.yml` workflow then merely *copies* the
committed HTML+JSON onto the gh-pages `/progress/` subdir; it does not rebuild.

Emits, next to this script:
  - progress_data.json        one snapshot of every lane/metric, with a per-metric
                              `measured` flag so the trust block can say whether a
                              number was counted live or is a documented fallback.
  - progress_timeseries.json  append-only; one row per build date, for trend lines.

Run: python progress_dashboard/build_progress_data.py
     (from the repo root; paths below are resolved relative to it.)

When the data lives in a different checkout than this script (e.g. building on an
isolated worktree that lacks the gitignored artifacts), point it at the checkout
that has them:  PWG_DATA_ROOT=/path/to/main/checkout python .../build_progress_data.py
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

OUT = Path(__file__).resolve().parent
REPO = OUT.parent
# The data root defaults to this checkout, but can be overridden when the
# gitignored artifacts live elsewhere (isolated worktree build).
DATA_REPO = Path(os.environ.get("PWG_DATA_ROOT", REPO)).resolve()
RT = DATA_REPO / "RussianTranslation"

# --- documented fallback constants (numbers that live in prose, not a machine file) ---
# Total PWG headwords, from RussianTranslation/.ai_state.md ("43,968 / 106,082
# DCS-attested PWG headwords (41%)").
TOTAL_HEADWORDS_FALLBACK = 106082
# corpus_lexicon recall, measured in H309 (overall 95.4%). No machine file exposes
# it, so it is carried as a documented constant until a metrics file does.
CORPUS_RECALL_PCT = 95.4


def _load_json(rel):
    p = RT / rel
    try:
        with p.open(encoding="utf-8-sig") as fh:
            return json.load(fh)
    except Exception as e:  # noqa: BLE001 — a missing local artifact must not crash the build
        print(f"  ! could not read {rel}: {e}")
        return None


def verb_lane():
    v = _load_json("src/pilot/output/verb_batch_worklist.json")
    if not v:
        return {"measured": False}

    def n(key):
        val = v.get(key)
        return len(val) if isinstance(val, list) else (val if isinstance(val, int) else None)

    return {
        "measured": True,
        "universe": n("universe_verbs01"),
        "dcs_attested": n("dcs_attested"),
        "promoted": n("done_promoted"),
        "runnable": n("runnable_remaining"),
        "blocked": n("blocked_missing_rootmap"),
    }


def nominal_lane():
    nm = _load_json("src/pilot/output/nominal_batch_worklist.json")
    out = {"measured": bool(nm)}
    if nm:
        out.update(
            {
                "candidates": nm.get("nominal_candidates"),
                "promoted": nm.get("already_promoted_count"),
                "runnable": nm.get("runnable_count"),
                "pwg_hits": nm.get("pwg_hits"),
            }
        )
    # The medium-50 band-4 relaunch arc (H317 -> H389 -> H437): 2/50 promoted,
    # lane paused on kill-gate miscalibration (H442). Documented, not in this file.
    out["medium50_promoted"] = 2
    out["medium50_total"] = 50
    out["medium50_status"] = "paused (kill-gate recalibration, H442/H462)"
    return out


def store_depth():
    p = RT / "src" / "pwg_ru_translated.jsonl"
    if not p.exists():
        return {"measured": False}
    senses = 0
    roots = set()
    review = {}
    with p.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception:  # noqa: BLE001
                continue
            senses += 1
            k = d.get("key1") or d.get("h") or d.get("root")
            if k:
                roots.add(k)
            rs = d.get("review_status", "unknown")
            review[rs] = review.get(rs, 0) + 1
    # K3 review honesty: human_reviewed = approved (signed-off), not a phantom key.
    approved = int(review.get("approved", 0) or 0)
    ai = int(review.get("ai_translated", 0) or 0)
    needs = int(review.get("needs_review", 0) or 0)
    # legacy key some writers used
    if review.get("human_reviewed"):
        approved = max(approved, int(review.get("human_reviewed") or 0))
    other = senses - approved - ai - needs
    return {
        "measured": True,
        "senses": senses,
        "roots": len(roots),
        "review": review,
        "human_reviewed": approved,
        "review_breakdown": {
            "approved": approved,
            "ai_translated": ai,
            "needs_review": needs,
            "other": max(0, other),
        },
    }


def review_queue():
    """G5 live-review-sheet open depth (B5, H2235).

    G5 sheet decision files (`review/g5-live-queue-*_decisions.json`) are
    gitignored — they carry reviewer notes on individual PWG cards, which is
    private editorial content. Only the aggregate open/decided/total counts
    are surfaced here, never a sheet path or item content.
    """
    review_dir = RT / "review"
    if not review_dir.is_dir():
        return {"measured": False}
    files = sorted(review_dir.glob("g5-live-queue-*_decisions.json"))
    if not files:
        return {"measured": False}
    total = decided = open_ = 0
    sheets = []
    for f in files:
        data = None
        try:
            with f.open(encoding="utf-8-sig") as fh:
                data = json.load(fh)
        except Exception:  # noqa: BLE001 — a malformed sheet must not crash the build
            continue
        items = data.get("items") or []
        sheet_decided = sum(1 for it in items if it.get("decision"))
        sheet_open = len(items) - sheet_decided
        total += len(items)
        decided += sheet_decided
        open_ += sheet_open
        sheets.append({"sheet_id": data.get("sheet_id"), "open": sheet_open, "total": len(items)})
    return {
        "measured": True,
        "sheet_count": len(files),
        "g5_total": total,
        "g5_decided": decided,
        "g5_open": open_,
        "sheets": sheets,
    }


def coverage():
    f = _load_json("src/pilot/output/scale_manifest.freq.json")
    attested = len(f) if isinstance(f, list) else None
    total = TOTAL_HEADWORDS_FALLBACK
    pct = round(attested / total * 100, 1) if attested else None
    return {
        "measured": attested is not None,
        "dcs_attested_headwords": attested,
        "total_headwords": total,
        "total_measured": False,  # denominator is a documented constant
        "pct": pct,
    }


def corpus():
    p = RT / "src" / "corpus_lexicon.jsonl"
    pairs = None
    if p.exists():
        # 1M+ lines; count cheaply without JSON-parsing each row.
        with p.open(encoding="utf-8") as fh:
            pairs = sum(1 for _ in fh)
    return {
        "measured": pairs is not None,
        "pairs": pairs if pairs is not None else 1093391,
        "pairs_measured": pairs is not None,
        "recall_pct": CORPUS_RECALL_PCT,
        "recall_measured": False,
    }


def main():
    now = datetime.now(timezone.utc)
    today = now.date().isoformat()
    generated_at = now.isoformat(timespec="seconds").replace("+00:00", "Z")
    verb = verb_lane()
    nom = nominal_lane()
    st = store_depth()
    cov = coverage()
    cor = corpus()
    rq = review_queue()

    data = {
        "generated_at": generated_at,
        "snapshot_date": today,
        "repo_url": "https://github.com/gasyoun/SanskritLexicography/blob/master",
        "site_url": "https://gasyoun.github.io/SanskritLexicography/",
        "kitchen_url": "https://gasyoun.github.io/SanskritLexicography/progress/",
        "refresh_hint_seconds": 60,
        "lanes": {"verb": verb, "nominal": nom},
        "store": st,
        "coverage": cov,
        "corpus": cor,
        "review_queue": rq,
    }

    (OUT / "progress_data.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"progress_data.json written ({generated_at}).")

    # append-only timeseries: one row per build date (last write per date wins)
    ts_path = OUT / "progress_timeseries.json"
    ts = {"snapshots": []}
    if ts_path.exists():
        try:
            ts = json.loads(ts_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            ts = {"snapshots": []}
    rb = st.get("review_breakdown") or {}
    row = {
        "date": today,
        "generated_at": generated_at,
        "verb_promoted": verb.get("promoted"),
        "verb_dcs_attested": verb.get("dcs_attested"),
        "senses": st.get("senses"),
        "roots": st.get("roots"),
        "coverage_pct": cov.get("pct"),
        "approved": rb.get("approved"),
        "ai_translated": rb.get("ai_translated"),
        "needs_review": rb.get("needs_review"),
        "g5_open": rq.get("g5_open") if rq.get("measured") else None,
        "g5_total": rq.get("g5_total") if rq.get("measured") else None,
    }
    ts["snapshots"] = [s for s in ts.get("snapshots", []) if s.get("date") != today] + [row]
    ts["snapshots"].sort(key=lambda s: s["date"])
    ts_path.write_text(json.dumps(ts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"progress_timeseries.json: {len(ts['snapshots'])} snapshot(s).")

    # console summary
    print(
        f"  verb lane:   {verb.get('promoted')}/{verb.get('dcs_attested')} promoted "
        f"({verb.get('runnable')} runnable, {verb.get('blocked')} blocked)"
    )
    print(f"  store:       {st.get('senses')} senses across {st.get('roots')} roots")
    print(f"  coverage:    {cov.get('pct')}% DCS-attested ({cov.get('dcs_attested_headwords')}/{cov.get('total_headwords')})")
    print(f"  corpus/TM:   {cor.get('pairs')} pairs, {cor.get('recall_pct')}% recall")
    if rq.get("measured"):
        print(f"  G5 queue:    {rq.get('g5_open')} open / {rq.get('g5_total')} across {rq.get('sheet_count')} sheet(s)")


if __name__ == "__main__":
    main()
