#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Best-effort historical wall-clock / gen_model backfill for window_ledger.jsonl (H2218 R4).

Recoverable sources only — never invent minutes or models:

  1. Rows that already have wall_clock_minutes > 0 keep their value; if
     wall_clock_source is missing, stamp ``pre_existing`` + backfilled metadata.
  2. Workflow JSON still on disk with meta.generated_at → derive minutes from
     mtime − generated_at (same rule as window_reports.derive_wall_clock_minutes),
     only when 0.5 ≤ minutes ≤ 480 and the ledger workflow path (or basename
     match) points at that file.
  3. gen_model only when workflow meta.gen_model (or top-level gen_model) is set.

Unrecoverable rows stay null. Dry-run by default; ``--apply`` rewrites the
gitignored ledger in place (backup .bak written first).

Usage (from repo root or worktree; data via PWG_DATA_ROOT):

  python progress_dashboard/backfill_ledger_metrics.py
  python progress_dashboard/backfill_ledger_metrics.py --apply
  PWG_DATA_ROOT=... python progress_dashboard/backfill_ledger_metrics.py --apply
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

OUT = Path(__file__).resolve().parent
REPO = OUT.parent
DATA_REPO = Path(os.environ.get("PWG_DATA_ROOT", REPO)).resolve()
RT = DATA_REPO / "RussianTranslation"
PILOT_OUT = RT / "src" / "pilot" / "output"
LEDGER = PILOT_OUT / "window_ledger.jsonl"

MIN_MINUTES = 0.5
MAX_MINUTES = 480.0


def _parse_ts(raw):
    if not raw or not isinstance(raw, str):
        return None
    s = raw.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _load_rows(path: Path) -> list[dict]:
    rows = []
    if not path.exists():
        return rows
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def _wf_index() -> dict[str, Path]:
    """Map basename and absolute path → workflow json under RussianTranslation."""
    idx: dict[str, Path] = {}
    candidates = list(RT.glob("wf_output*.json"))
    if (PILOT_OUT).exists():
        candidates += list(PILOT_OUT.glob("wf_output*.json"))
        candidates += list(PILOT_OUT.glob("**/wf_output*.json"))
    for p in candidates:
        if not p.is_file():
            continue
        idx[str(p.resolve())] = p
        idx[p.name] = p
        # Windows path variants as stored in ledger
        idx[str(p)] = p
    return idx


def _read_wf_meta(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    if not isinstance(data, dict):
        return {}
    meta = data.get("meta") or data.get("workflow_meta") or {}
    if not isinstance(meta, dict):
        meta = {}
    # top-level fallbacks some harnesses use
    if not meta.get("generated_at") and data.get("generated_at"):
        meta = dict(meta)
        meta["generated_at"] = data.get("generated_at")
    if not meta.get("gen_model") and data.get("gen_model"):
        meta = dict(meta)
        meta["gen_model"] = data.get("gen_model")
    return meta


def _derive_minutes(wf_path: Path, meta: dict) -> tuple[float | None, str]:
    generated = _parse_ts(meta.get("generated_at"))
    if generated is None:
        return None, "unavailable"
    try:
        mtime = wf_path.stat().st_mtime
    except OSError:
        return None, "unavailable"
    end = datetime.fromtimestamp(mtime, tz=timezone.utc)
    delta_sec = (end - generated).total_seconds()
    if delta_sec <= 0:
        return None, "unavailable"
    minutes = round(delta_sec / 60.0, 3)
    if minutes < MIN_MINUTES or minutes > MAX_MINUTES:
        return None, "out_of_range"
    return minutes, "derived_mtime"


def coverage(rows: list[dict]) -> dict:
    n = len(rows)
    wc = 0
    gm = 0
    for r in rows:
        pm = r.get("production_metrics") or {}
        if isinstance(pm.get("wall_clock_minutes"), (int, float)) and pm[
            "wall_clock_minutes"
        ] > 0:
            wc += 1
        if r.get("gen_model"):
            gm += 1
    return {
        "windows": n,
        "wall_clock_present": wc,
        "wall_clock_coverage_pct": round(100 * wc / n, 1) if n else None,
        "gen_model_present": gm,
        "gen_model_coverage_pct": round(100 * gm / n, 1) if n else None,
    }


def backfill(rows: list[dict], wf_idx: dict[str, Path]) -> tuple[list[dict], dict]:
    stats = {
        "wall_clock_stamped_source": 0,
        "wall_clock_derived": 0,
        "gen_model_from_wf": 0,
        "unchanged": 0,
    }
    out = []
    for r in rows:
        row = dict(r)
        pm = dict(row.get("production_metrics") or {})
        changed = False

        mins = pm.get("wall_clock_minutes")
        has_wc = isinstance(mins, (int, float)) and mins > 0
        if has_wc and not pm.get("wall_clock_source"):
            pm["wall_clock_source"] = "pre_existing"
            pm["backfilled"] = True
            pm["backfill_source"] = "pre_existing_wall_clock"
            stats["wall_clock_stamped_source"] += 1
            changed = True
        elif not has_wc:
            wf_raw = row.get("workflow")
            wf_path = None
            if isinstance(wf_raw, str) and wf_raw:
                wf_path = wf_idx.get(wf_raw) or wf_idx.get(Path(wf_raw).name)
                if wf_path is None:
                    try:
                        cand = Path(wf_raw)
                        if cand.is_file():
                            wf_path = cand
                    except OSError:
                        pass
            if wf_path is not None:
                meta = _read_wf_meta(wf_path)
                minutes, src = _derive_minutes(wf_path, meta)
                if minutes is not None:
                    pm["wall_clock_minutes"] = minutes
                    pm["wall_clock_source"] = src
                    pm["backfilled"] = True
                    pm["backfill_source"] = f"workflow:{wf_path.name}"
                    stats["wall_clock_derived"] += 1
                    changed = True
                # gen_model from same meta
                if not row.get("gen_model") and meta.get("gen_model"):
                    row["gen_model"] = meta["gen_model"]
                    pm["gen_model_backfilled"] = True
                    pm["backfill_source"] = (
                        (pm.get("backfill_source") or "")
                        + "+gen_model"
                    ).strip("+")
                    stats["gen_model_from_wf"] += 1
                    changed = True
            if not changed:
                stats["unchanged"] += 1
        else:
            # already complete wall-clock
            if not row.get("gen_model"):
                wf_raw = row.get("workflow")
                if isinstance(wf_raw, str) and wf_raw:
                    wf_path = wf_idx.get(wf_raw) or wf_idx.get(Path(wf_raw).name)
                    if wf_path is not None:
                        meta = _read_wf_meta(wf_path)
                        if meta.get("gen_model"):
                            row["gen_model"] = meta["gen_model"]
                            pm["gen_model_backfilled"] = True
                            pm["backfilled"] = True
                            pm["backfill_source"] = f"workflow:{wf_path.name}"
                            stats["gen_model_from_wf"] += 1
                            changed = True
            if not changed:
                stats["unchanged"] += 1

        if pm:
            row["production_metrics"] = pm
        out.append(row)
    return out, stats


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--apply",
        action="store_true",
        help="Rewrite window_ledger.jsonl (default is dry-run report only)",
    )
    ap.add_argument(
        "--ledger",
        type=Path,
        default=LEDGER,
        help="Path to window_ledger.jsonl",
    )
    args = ap.parse_args()

    ledger: Path = args.ledger
    if not ledger.exists():
        print(f"ledger missing: {ledger}")
        print("coverage before: n/a")
        return 0

    rows = _load_rows(ledger)
    before = coverage(rows)
    print("coverage before:")
    print(
        f"  wall_clock {before['wall_clock_present']}/{before['windows']} "
        f"({before['wall_clock_coverage_pct']}%)"
    )
    print(
        f"  gen_model  {before['gen_model_present']}/{before['windows']} "
        f"({before['gen_model_coverage_pct']}%)"
    )

    wf_idx = _wf_index()
    print(f"workflow files indexed: {len({p for p in wf_idx.values()})}")

    new_rows, stats = backfill(rows, wf_idx)
    after = coverage(new_rows)
    print("coverage after (would-write):")
    print(
        f"  wall_clock {after['wall_clock_present']}/{after['windows']} "
        f"({after['wall_clock_coverage_pct']}%)"
    )
    print(
        f"  gen_model  {after['gen_model_present']}/{after['windows']} "
        f"({after['gen_model_coverage_pct']}%)"
    )
    print("stats:", json.dumps(stats, ensure_ascii=False))

    if not args.apply:
        print("dry-run only — pass --apply to rewrite ledger (gitignored local file)")
        return 0

    bak = ledger.with_suffix(ledger.suffix + ".bak")
    shutil.copy2(ledger, bak)
    tmp = ledger.with_suffix(ledger.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        for r in new_rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp.replace(ledger)
    print(f"wrote {ledger} (backup {bak})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
