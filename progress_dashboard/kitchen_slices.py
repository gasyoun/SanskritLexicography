# -*- coding: utf-8 -*-
"""K1–K8 aggregates for the public PWG→RU progress kitchen (H2212).

Pure helpers consumed by build_kitchen_data.py. Missing inputs degrade
quietly to measured=False — never raise.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path


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


def _mean(vals):
    nums = [v for v in vals if isinstance(v, (int, float))]
    if not nums:
        return None
    return round(sum(nums) / len(nums), 3)


def _sanitize_next_action(text: str | None) -> str | None:
    if not text or not isinstance(text, str):
        return None
    s = text.strip()
    # Drop absolute Windows / Unix paths and temp workflow dumps.
    s = re.sub(r"[A-Za-z]:\\[^\s]+", "<path>", s)
    s = re.sub(r"/tmp/[^\s]+", "<path>", s)
    s = re.sub(r"C:\\Users\\[^\s]+", "<path>", s)
    s = re.sub(r"\\{2,}[^\s]+", "<path>", s)
    if len(s) > 220:
        s = s[:217] + "…"
    return s


def load_ledger_rows(ledger: Path) -> list[dict]:
    if not ledger.exists():
        return []
    rows = []
    with ledger.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def operator_strip(window_status: Path, speed: dict, act: dict) -> dict:
    """K1 — what is stuck right now."""
    ws = {}
    if window_status.exists():
        try:
            ws = json.loads(window_status.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            ws = {}
    newest = speed.get("newest_card_at")
    oldest = speed.get("oldest_card_at")
    now = datetime.now(timezone.utc)
    days_since = None
    campaign_days = None
    nd = _parse_ts(newest)
    od = _parse_ts(oldest)
    if nd:
        days_since = round((now - nd).total_seconds() / 86400, 2)
    if od:
        campaign_days = max(1, int((now - od).total_seconds() / 86400) + 1)
    root = (
        ws.get("root")
        or (ws.get("workflow_meta") or {}).get("root")
        or act.get("window_root")
    )
    state = ws.get("state") or act.get("window_state")
    next_action = _sanitize_next_action(ws.get("next_action") or act.get("next_action"))
    return {
        "measured": bool(root or state or newest),
        "root": root,
        "state": state,
        "next_action": next_action,
        "recorded_at": ws.get("recorded_at"),
        "requeue_count": ws.get("requeue_count"),
        "clean_key_count": ws.get("clean_key_count"),
        "translated": ws.get("translated"),
        "pending": ws.get("pending"),
        "newest_card_at": newest,
        "oldest_card_at": oldest,
        "days_since_last_card": days_since,
        "campaign_days": campaign_days,
    }


def yield_quality(rows: list[dict]) -> dict:
    """K2 — outcome mix, requeue load, clean-key yield, top roots."""
    if not rows:
        return {"measured": False}
    states = Counter(r.get("state") or "unknown" for r in rows)
    rq = [r.get("requeue_count") for r in rows if isinstance(r.get("requeue_count"), (int, float))]
    tr = [
        r.get("requeue_transient_count")
        for r in rows
        if isinstance(r.get("requeue_transient_count"), (int, float))
    ]
    de = [
        r.get("requeue_defect_count")
        for r in rows
        if isinstance(r.get("requeue_defect_count"), (int, float))
    ]
    ck = [
        r.get("clean_key_count")
        for r in rows
        if isinstance(r.get("clean_key_count"), (int, float))
    ]
    roots = Counter(r.get("root") for r in rows if r.get("root"))
    clean_n = states.get("clean", 0)
    return {
        "measured": True,
        "windows": len(rows),
        "outcome_mix": dict(states.most_common()),
        "clean_windows": clean_n,
        "clean_window_pct": round(100 * clean_n / len(rows), 2) if rows else None,
        "requeue_sum": int(sum(rq)) if rq else 0,
        "mean_requeue": _mean(rq),
        "transient_sum": int(sum(tr)) if tr else 0,
        "defect_sum": int(sum(de)) if de else 0,
        "clean_key_sum": int(sum(ck)) if ck else 0,
        "mean_clean_keys": _mean(ck),
        "top_roots": [
            {"root": root, "windows": n} for root, n in roots.most_common(8)
        ],
    }


def gate_summary(events: Path, limit: int = 200) -> dict:
    """A5 — recent gate_summary pass-ish rate (exit=0 vs not)."""
    if not events.exists():
        return {"measured": False}
    total = 0
    exit0 = 0
    recent = []
    with events.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if e.get("type") != "gate_summary":
                continue
            total += 1
            data = e.get("data") or {}
            rc = data.get("returncode")
            if rc == 0 or (isinstance(rc, str) and rc == "0"):
                exit0 += 1
            recent.append(
                {
                    "ts": e.get("ts"),
                    "root": e.get("root"),
                    "summary": (e.get("summary") or "")[:120],
                    "returncode": rc,
                    "requeue": data.get("requeue"),
                }
            )
    recent = recent[-limit:]
    return {
        "measured": total > 0,
        "gate_summaries": total,
        "exit0": exit0,
        "exit0_pct": round(100 * exit0 / total, 1) if total else None,
        "recent_shown": len(recent),
        "recent": recent[-12:],
    }


def instrumentation_coverage(rows: list[dict]) -> dict:
    """K6 / A7 — how complete wall-clock + gen_model fields are."""
    if not rows:
        return {"measured": False}
    n = len(rows)
    wc = 0
    tok = 0
    gm = 0
    models: Counter = Counter()
    for r in rows:
        pm = r.get("production_metrics") or {}
        if isinstance(pm.get("wall_clock_minutes"), (int, float)) and pm["wall_clock_minutes"] > 0:
            wc += 1
        t = (
            pm.get("max_total_tokens")
            or pm.get("max_output_tokens")
            or pm.get("total_tokens")
        )
        if isinstance(t, (int, float)) and t > 0:
            tok += 1
        m = r.get("gen_model")
        if m:
            gm += 1
            models[str(m)] += 1
    return {
        "measured": True,
        "windows": n,
        "wall_clock_present": wc,
        "wall_clock_coverage_pct": round(100 * wc / n, 1) if n else None,
        "token_metrics_present": tok,
        "token_coverage_pct": round(100 * tok / n, 1) if n else None,
        "gen_model_present": gm,
        "gen_model_coverage_pct": round(100 * gm / n, 1) if n else None,
        "gen_models": dict(models.most_common(12)),
        "note": (
            "audit_window already stamps production_metrics when wall-clock can be "
            "derived; historical ledger rows predate that path — coverage <100% is expected"
        ),
    }


def health_ribbon(pilot_out: Path, ceiling_ms: int = 65_000) -> dict:
    """K5 — last c4 (and siblings) probe GO/NO-GO + recent sparkline."""
    paths = sorted(pilot_out.glob("*gate0*probe_events.jsonl")) + sorted(
        pilot_out.glob("*_probe_events.jsonl")
    )
    # Prefer dedicated c4 health probe log when present.
    preferred = pilot_out / "h963_c4_gate0_probe_events.jsonl"
    if preferred.exists():
        paths = [preferred] + [p for p in paths if p != preferred]

    probes = []
    seen = set()
    for path in paths:
        if not path.exists() or path in seen:
            continue
        seen.add(path)
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if e.get("event") not in ("probe_call", "health", None) and e.get(
                    "stage"
                ) not in ("probe", "gate0", None):
                    # keep measured / purpose==measured rows
                    if e.get("purpose") != "measured" and e.get("elapsed_ms") is None:
                        continue
                elapsed = e.get("elapsed_ms")
                if not isinstance(elapsed, (int, float)):
                    continue
                ceil = e.get("latency_ceiling_ms") or ceiling_ms
                try:
                    ceil = int(ceil)
                except (TypeError, ValueError):
                    ceil = ceiling_ms
                verdict = "GO" if elapsed <= ceil else "NO-GO"
                probes.append(
                    {
                        "ts": e.get("ts"),
                        "account": e.get("account") or e.get("profile") or "?",
                        "elapsed_ms": int(elapsed),
                        "duration_api_ms": e.get("duration_api_ms"),
                        "ceiling_ms": ceil,
                        "verdict": verdict,
                        "model": e.get("model"),
                        "source": path.name,
                    }
                )
    if not probes:
        return {
            "measured": False,
            "note": "no gate0 probe_events.jsonl under pilot/output",
            "ceiling_ms": ceiling_ms,
        }
    probes.sort(key=lambda p: p.get("ts") or "")
    last = probes[-1]
    go_n = sum(1 for p in probes if p["verdict"] == "GO")
    return {
        "measured": True,
        "ceiling_ms": ceiling_ms,
        "probes": len(probes),
        "go_count": go_n,
        "nogo_count": len(probes) - go_n,
        "go_pct": round(100 * go_n / len(probes), 1),
        "last": last,
        "last_verdict": last["verdict"],
        "recent": probes[-14:],
        "note": "GO if elapsed_ms ≤ latency ceiling (default 65s; H2011/H2174 c4 series)",
    }


def quality_slice(pilot_out: Path, rows: list[dict], events: Path) -> dict:
    """B4/B6/B11/B12 light surface — fidelity, clean windows, crashes, judge coverage."""
    out: dict = {"measured": False}
    fid_path = pilot_out / "fidelity_aggregate.json"
    if fid_path.exists():
        try:
            fid = json.loads(fid_path.read_text(encoding="utf-8"))
            out["fidelity"] = {
                "n": fid.get("n"),
                "good": fid.get("good"),
                "bad": fid.get("bad"),
                "precision": fid.get("precision"),
                "ci95_wilson": fid.get("ci95_wilson"),
            }
            out["measured"] = True
        except Exception:  # noqa: BLE001
            pass

    if rows:
        clean_n = sum(1 for r in rows if r.get("state") == "clean")
        with_judge = sum(
            1
            for r in rows
            if isinstance(r.get("judge_sample_count"), (int, float))
            and r["judge_sample_count"] > 0
        )
        out["clean_windows"] = clean_n
        out["promotion_vs_generation"] = {
            "clean_ledger_windows": clean_n,
            "total_windows": len(rows),
            "note": "clean = mechanically clean window state, not article-site publish",
        }
        out["judge_coverage"] = {
            "windows_with_sample": with_judge,
            "windows": len(rows),
            "pct": round(100 * with_judge / len(rows), 1) if rows else None,
        }
        out["measured"] = True

    crashes = 0
    last_crash = None
    if events.exists():
        with events.open(encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                try:
                    e = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if e.get("type") == "crash_state":
                    crashes += 1
                    last_crash = {
                        "ts": e.get("ts"),
                        "root": e.get("root"),
                        "summary": (e.get("summary") or "")[:120],
                    }
    out["crashes"] = crashes
    out["last_crash"] = last_crash
    if crashes:
        out["crashes_per_100_windows"] = (
            round(100 * crashes / len(rows), 2) if rows else None
        )
    return out


def cost_honesty(econ: dict, spend: dict) -> dict:
    """K8 — sample-size badge so band is not read as full invoice."""
    summary = {}
    if isinstance(econ, dict):
        summary = econ.get("summary") or {}
        if not isinstance(summary, dict):
            summary = {}
    total_clean = summary.get("total_clean")
    cov = summary.get("coverage") if isinstance(summary.get("coverage"), dict) else {}
    return {
        "measured": bool(total_clean is not None or spend.get("measured")),
        "priced_clean_cards": total_clean,
        "economy_source": econ.get("source") if isinstance(econ, dict) else None,
        "outcome_rows": cov.get("outcome_rows"),
        "structured_agents_used": cov.get("structured_agents_used"),
        "badge": (
            f"priced sample n={total_clean} clean cards"
            if total_clean is not None
            else "priced sample size unknown"
        ),
        "note": (
            "Economy band is list-price extremes on a probe/log sample — not the "
            "Claude Max subscription invoice and not full-campaign billed spend"
        ),
    }


def eta_verb(rt: Path, speed: dict) -> dict:
    """K4 — projected days to finish verb DCS scope at 14d active-day rate."""
    wl = rt / "src" / "pilot" / "output" / "verb_batch_worklist.json"
    if not wl.exists():
        return {"measured": False}
    try:
        v = json.loads(wl.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {"measured": False}

    def n(key):
        val = v.get(key)
        if isinstance(val, list):
            return len(val)
        if isinstance(val, int):
            return val
        return None

    promoted = n("done_promoted")
    scope = n("dcs_attested")
    remaining = None
    if isinstance(promoted, int) and isinstance(scope, int):
        remaining = max(0, scope - promoted)
    rate = speed.get("mean_cards_per_active_day_14d")
    # rate is cards/day not roots/day — convert roughly via mean senses? Keep as
    # cards/day and also project roots using ledger mean translated if possible.
    est_days = None
    basis = None
    if remaining is not None and isinstance(rate, (int, float)) and rate > 0:
        # Without roots/day, use remaining roots as if 1 "unit" ~ mean cards/root from store is unknown.
        # Conservative: treat remaining * as roots needing work; use rate as cards/day only for card ETA.
        est_days = None
        basis = "cards_rate_only"
    return {
        "measured": promoted is not None and scope is not None,
        "verb_promoted": promoted,
        "verb_scope_dcs": scope,
        "verb_remaining": remaining,
        "verb_pct": round(100 * promoted / scope, 2) if scope else None,
        "mean_cards_per_active_day_14d": rate,
        "estimated_days_at_14d_card_rate": (
            round(remaining / rate, 1)
            if remaining is not None and isinstance(rate, (int, float)) and rate > 0
            else None
        ),
        "estimate_label": "estimate",
        "note": (
            "ETA divides remaining DCS-attested verb roots by mean cards/active-day (14d). "
            "Units differ (roots vs cards) — treat as order-of-magnitude only, not a schedule."
        ),
        "basis": basis or "verb_remaining / mean_cards_per_active_day_14d",
    }


def calendar_with_idle(
    store_speed_data: dict,
    ledger: Path,
    gaps: list[dict],
    calendar_days: int,
    heat_level_fn,
    utc_now_fn,
) -> dict:
    """K7 — heatmap cells with idle overlay."""
    by_day = dict(store_speed_data.get("cards_by_day") or {})
    windows_by_day: dict[str, int] = {}
    if ledger.exists():
        with ledger.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ts = r.get("recorded_at") or ""
                if len(ts) >= 10:
                    d = ts[:10]
                    windows_by_day[d] = windows_by_day.get(d, 0) + 1

    idle_by_day: dict[str, int] = {}
    for g in gaps:
        frm = _parse_ts(g.get("from"))
        to = _parse_ts(g.get("to"))
        secs = int(g.get("seconds") or 0)
        if not frm or not to or secs <= 0:
            continue
        # Attribute whole gap to start day (simple); long gaps also mark intervening days.
        cur = frm.date()
        end_d = to.date()
        if cur == end_d:
            iso = cur.isoformat()
            idle_by_day[iso] = idle_by_day.get(iso, 0) + secs
        else:
            # split proportionally by calendar day span
            days = max(1, (end_d - cur).days + 1)
            share = secs // days
            while cur <= end_d:
                iso = cur.isoformat()
                idle_by_day[iso] = idle_by_day.get(iso, 0) + share
                cur = cur + timedelta(days=1)

    end = utc_now_fn().date()
    start = end - timedelta(days=calendar_days - 1)
    cells = []
    cur = start
    while cur <= end:
        iso = cur.isoformat()
        cards = by_day.get(iso, 0)
        wins = windows_by_day.get(iso, 0)
        idle_s = idle_by_day.get(iso, 0)
        # level: card heat if any cards; else idle marker 0 + idle flag
        cells.append(
            {
                "date": iso,
                "cards": cards,
                "windows": wins,
                "idle_seconds": idle_s,
                "idle_hours": round(idle_s / 3600, 2) if idle_s else 0,
                "level": heat_level_fn(cards),
                "idle": idle_s >= 3600 and cards == 0,  # ≥1h idle and no cards
            }
        )
        cur = cur + timedelta(days=1)
    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "days": calendar_days,
        "cells": cells,
        "max_cards": max((c["cards"] for c in cells), default=0),
        "active_days": sum(1 for c in cells if c["cards"] or c["windows"]),
        "idle_days": sum(1 for c in cells if c.get("idle")),
    }


def enrich_store_speed_oldest(store: Path, speed: dict) -> dict:
    """Add oldest_card_at when scanning store (speed already has newest)."""
    if not store.exists():
        return speed
    if speed.get("oldest_card_at"):
        return speed
    oldest = None
    with store.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            prov = row.get("provenance") or {}
            ts = prov.get("generated_at") or row.get("generated_at")
            dt = _parse_ts(ts)
            if not dt:
                continue
            if oldest is None or dt < oldest:
                oldest = dt
    if oldest:
        speed = dict(speed)
        speed["oldest_card_at"] = oldest.isoformat(timespec="seconds").replace(
            "+00:00", "Z"
        )
    return speed
