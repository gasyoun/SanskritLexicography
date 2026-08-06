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
        candidates = nm.get("nominal_candidates")
        promoted = nm.get("already_promoted_count")
        runnable = nm.get("runnable_count")
        remaining = runnable
        if remaining is None and isinstance(promoted, int) and isinstance(candidates, int):
            remaining = max(0, candidates - promoted)
        out.update(
            {
                "candidates": candidates,
                "promoted": promoted,
                "runnable": runnable,
                "pwg_hits": nm.get("pwg_hits"),
                # B7 burn-down fields, mirroring the verb lane's universe/promoted/runnable shape.
                "remaining": remaining,
                "pct": round(100 * promoted / candidates, 2) if candidates else None,
            }
        )
    # The medium-50 band-4 relaunch arc (H317 -> H389 -> H437): promoted count
    # is live-measured (H317 worklist keys intersected against the store) when
    # that file is present; falls back to the last documented count otherwise.
    m50 = _load_json_from(RT / "src" / "pilot" / "H317_medium50_worklist.08.07.26.json")
    m50_promoted, m50_total, m50_measured = 2, 50, False
    if m50:
        keys = m50.get("keys") or []
        m50_total = m50.get("n_selected") or len(keys)
        store_keys = _store_key1_set()
        if store_keys is not None:
            m50_promoted = sum(1 for k in keys if k in store_keys)
            m50_measured = True
    out["medium50_promoted"] = m50_promoted
    out["medium50_total"] = m50_total
    out["medium50_measured"] = m50_measured
    # Structured pause reason (code + link), not prose-only — B7 acceptance.
    out["medium50_pause_reason"] = {
        "code": "killgate_cascade",
        "label": "paused — kill-gate/self-heal budget cascade on dense band-4 nominal singletons",
        "docs": ["H437", "H442", "H462"],
        "doc_urls": [
            "https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H437-Sonnet_RussianTranslation_pwg-ru-medium50-resume-post-h428_09.07.26.md",
            "https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H442-Opus_RussianTranslation_pwg-ru-killgate-recalibration-nominal-medium_09.07.26.md",
            "https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H462-Fable_RussianTranslation_launch-telemetry-ledger-code-vs-docs-audit_10.07.26.md",
        ],
    }
    # legacy field, kept for any existing consumer of the old prose-only status
    out["medium50_status"] = out["medium50_pause_reason"]["label"]
    return out


def _load_json_from(path: Path):
    try:
        with path.open(encoding="utf-8-sig") as fh:
            return json.load(fh)
    except Exception as e:  # noqa: BLE001 — a missing local artifact must not crash the build
        print(f"  ! could not read {path}: {e}")
        return None


def _store_key1_set():
    p = RT / "src" / "pwg_ru_translated.jsonl"
    if not p.exists():
        return None
    keys = set()
    with p.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception:  # noqa: BLE001
                continue
            k = d.get("key1")
            if k:
                keys.add(k)
    return keys


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
        # sheet_id only (no path, no notes) — aggregate privacy contract from H2235
        sheets.append({"sheet_id": data.get("sheet_id"), "open": sheet_open, "total": len(items)})
    return {
        "measured": True,
        "sheet_count": len(files),
        "g5_total": total,
        "g5_decided": decided,
        "g5_open": open_,
        "sheets": sheets,
    }


def review_transitions():
    """Daily approved / needs_review *transitions* from store review timestamps (B5, H2260).

    H2235 primary path: derive daily approved transitions from review timestamps
    when present; else fall back to append-only stock series on rebuild (that
    stock path lives in main()'s timeseries row and was shipped by Sonnet #1092).

    Field of record: ``human_review.reviewed_at`` (ISO datetime). Present on
    every currently human-touched row (approved + needs_review); absent on the
    bulk ``ai_translated`` population. Coverage is therefore honest but small —
    a true full-store transition series will grow only as more rows acquire
    reviewed_at. Never invent timestamps from provenance.generated_at (that is
    generation day, not human-signoff day).
    """
    p = RT / "src" / "pwg_ru_translated.jsonl"
    if not p.exists():
        return {"measured": False, "method": "human_review.reviewed_at"}
    by_day = {}  # date -> {approved, needs_review, other}
    with_ts = 0
    approved_total = needs_total = 0
    approved_with_ts = needs_with_ts = 0
    with p.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception:  # noqa: BLE001
                continue
            rs = d.get("review_status") or "unknown"
            if rs == "approved":
                approved_total += 1
            elif rs == "needs_review":
                needs_total += 1
            hr = d.get("human_review") or {}
            ra = hr.get("reviewed_at") if isinstance(hr, dict) else None
            if not ra:
                continue
            with_ts += 1
            day = str(ra)[:10]
            bucket = by_day.setdefault(day, {"approved": 0, "needs_review": 0, "other": 0})
            if rs == "approved":
                bucket["approved"] += 1
                approved_with_ts += 1
            elif rs == "needs_review":
                bucket["needs_review"] += 1
                needs_with_ts += 1
            else:
                bucket["other"] += 1
    if not by_day:
        return {
            "measured": False,
            "method": "human_review.reviewed_at",
            "rows_with_reviewed_at": 0,
            "approved_with_reviewed_at": 0,
            "approved_total": approved_total,
            "note": "no human_review.reviewed_at on any store row; use append-only stock series",
        }
    daily = [
        {"date": day, **by_day[day]}
        for day in sorted(by_day)
    ]
    return {
        "measured": True,
        "method": "human_review.reviewed_at",
        "rows_with_reviewed_at": with_ts,
        "approved_with_reviewed_at": approved_with_ts,
        "approved_total": approved_total,
        "needs_review_with_reviewed_at": needs_with_ts,
        "needs_review_total": needs_total,
        "coverage_approved": (
            f"{approved_with_ts}/{approved_total}" if approved_total else "0/0"
        ),
        "daily": daily,
        "note": (
            "per-day transition counts from human_review.reviewed_at; "
            "append-only stock series (progress_timeseries approved/needs_review) "
            "remains the rebuild-date depth signal"
        ),
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


def kitchen_slice():
    """H2241 K-slice: daily kitchen operator/yield/health points for the trend
    charts, read from the sibling kitchen_data.json build (same directory,
    always co-located since both are committed progress_dashboard/ outputs).

    Mapping lives in kitchen_slices.progress_kitchen_slice (H2268 dual-run pin).
    """
    # Local import: kitchen_slices is co-located; keep build_progress_data
    # import surface small for scripts that only need progress lanes.
    import kitchen_slices as ks  # noqa: PLC0415

    p = OUT / "kitchen_data.json"
    if not p.exists():
        return {"measured": False}
    try:
        with p.open(encoding="utf-8-sig") as fh:
            kd = json.load(fh)
    except Exception as e:  # noqa: BLE001 — a malformed kitchen build must not crash this one
        print(f"  ! could not read kitchen_data.json: {e}")
        return {"measured": False}
    return ks.progress_kitchen_slice(kd)


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
    rt_x = review_transitions()
    kit = kitchen_slice()

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
        # H2260 best-of-both: transition series from reviewed_at (H2235 primary path)
        "review_throughput": rt_x,
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
        # H2241 K-slice: daily kitchen operator/yield/health points.
        "kitchen_yield_clean_pct": kit.get("yield_clean_pct") if kit.get("measured") else None,
        "kitchen_health_last_verdict": kit.get("health_last_verdict") if kit.get("measured") else None,
        "kitchen_health_last_go": kit.get("health_last_go") if kit.get("measured") else None,
        "kitchen_idle_hours": kit.get("idle_hours") if kit.get("measured") else None,
        # H2268 net-new: live current idle (campaign total is a stock).
        "kitchen_current_idle_hours": kit.get("current_idle_hours") if kit.get("measured") else None,
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
    if rt_x.get("measured"):
        days = rt_x.get("daily") or []
        print(
            f"  transitions: {rt_x.get('rows_with_reviewed_at')} rows with reviewed_at "
            f"across {len(days)} day(s); approved coverage {rt_x.get('coverage_approved')}"
        )
    if kit.get("measured"):
        print(
            f"  K-slice:     yield_clean={kit.get('yield_clean_pct')}%  "
            f"health_last={kit.get('health_last_verdict')}  "
            f"idle_hours={kit.get('idle_hours')}  "
            f"current_idle={kit.get('current_idle_hours')}"
        )


if __name__ == "__main__":
    main()
