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


def _coverage_bucket(rows: list[dict]) -> dict:
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
        "windows": n,
        "wall_clock_present": wc,
        "wall_clock_coverage_pct": round(100 * wc / n, 1) if n else None,
        "token_metrics_present": tok,
        "token_coverage_pct": round(100 * tok / n, 1) if n else None,
        "gen_model_present": gm,
        "gen_model_coverage_pct": round(100 * gm / n, 1) if n else None,
        "gen_models": dict(models.most_common(12)),
    }


def instrumentation_coverage(rows: list[dict]) -> dict:
    """K6 / A7 / K9 (H2230) — how complete wall-clock + token + gen_model fields are.

    Split post_cut (the row's production_metrics carries a ``wall_clock_source``
    key, i.e. it passed through the auto-derive path added in H1553/H2212) from
    historical (no ``wall_clock_source`` key at all — written before that path
    existed, so a null there was never recoverable). A single blended
    coverage_pct silently conflated "legitimately unknown, pre-instrumentation"
    with "should have it, something's actually missing" — this split makes the
    post_cut number the honest instrumentation-health signal.
    """
    if not rows:
        return {"measured": False}
    post_cut_rows = []
    historical_rows = []
    for r in rows:
        pm = r.get("production_metrics") or {}
        if "wall_clock_source" in pm:
            post_cut_rows.append(r)
        else:
            historical_rows.append(r)
    overall = _coverage_bucket(rows)
    post_cut = _coverage_bucket(post_cut_rows)
    historical = _coverage_bucket(historical_rows)
    return {
        "measured": True,
        "windows": overall["windows"],
        "wall_clock_present": overall["wall_clock_present"],
        "wall_clock_coverage_pct": overall["wall_clock_coverage_pct"],
        "token_metrics_present": overall["token_metrics_present"],
        "token_coverage_pct": overall["token_coverage_pct"],
        "gen_model_present": overall["gen_model_present"],
        "gen_model_coverage_pct": overall["gen_model_coverage_pct"],
        "gen_models": overall["gen_models"],
        "post_cut": post_cut,
        "historical": historical,
        "note": (
            "post_cut = rows stamped by the H1553/H2212 auto-derive path (has a "
            "wall_clock_source key) — this is the honest instrumentation-health "
            "number; historical = rows written before that path existed, where a "
            "null was never recoverable and is expected, not a gap"
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


# ---------------------------------------------------------------------------
# H2218 residual — B1 subscription $ · B9 idle reasons · B10 article parity
# ---------------------------------------------------------------------------

IDLE_REASON_TAXONOMY = (
    "human",
    "weekly_cap",
    "health_nogo",
    "machine_off",
    "waiting_requeue",
    "unknown",
)

SUBSCRIPTION_SOURCES = (
    "usage_export_paste",
    "manual",
    "weekly_receipt_summary",
)


def load_subscription(path: Path) -> dict:
    """B1 — optional Claude Max / subscription spend paste (never invent $).

    Expected JSON (gitignored under pilot/output/economy_subscription.json):
      {
        "period_start": "YYYY-MM-DD",
        "period_end": "YYYY-MM-DD",
        "currency": "USD",
        "amount": 100.0,
        "source": "usage_export_paste" | "manual" | "weekly_receipt_summary",
        "notes": "optional free text (no account emails)"
      }
    """
    if not path.exists():
        return {
            "measured": False,
            "badge": "subscription not pasted",
            "note": (
                "Paste a weekly Max receipt or usage-export summary into "
                "RussianTranslation/src/pilot/output/economy_subscription.json "
                "(schema in progress_dashboard/examples/economy_subscription.example.json). "
                "Until then the kitchen only shows list-price sample bands (K8)."
            ),
        }
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return {
            "measured": False,
            "error": str(e)[:200],
            "badge": "subscription file unreadable",
        }
    if not isinstance(raw, dict):
        return {"measured": False, "badge": "subscription file not an object"}

    amount = raw.get("amount")
    try:
        amount_f = float(amount) if amount is not None else None
    except (TypeError, ValueError):
        amount_f = None
    source = raw.get("source") or "manual"
    if source not in SUBSCRIPTION_SOURCES:
        source = "manual"
    currency = (raw.get("currency") or "USD").strip() or "USD"
    period_start = raw.get("period_start")
    period_end = raw.get("period_end")
    notes = raw.get("notes")
    if isinstance(notes, str) and len(notes) > 280:
        notes = notes[:277] + "…"
    # Never surface emails if a human pasted one by mistake.
    if isinstance(notes, str):
        notes = re.sub(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            "<email>",
            notes,
        )

    measured = amount_f is not None and amount_f >= 0
    return {
        "measured": measured,
        "amount": amount_f if measured else None,
        "currency": currency if measured else None,
        "period_start": period_start,
        "period_end": period_end,
        "source": source if measured else None,
        "notes": notes if measured else None,
        "badge": (
            f"subscription window {currency} {amount_f:g} (pasted)"
            if measured
            else "subscription amount missing"
        ),
        "note": (
            "Human-pasted subscription/usage total — not list-price token math"
            if measured
            else "File present but amount missing or invalid"
        ),
    }


def _load_idle_reason_log(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
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


def append_idle_reason(
    path: Path,
    *,
    reason: str,
    gap_from: str | None = None,
    gap_to: str | None = None,
    evidence: str | None = None,
    note: str | None = None,
    tagged_by: str = "operator",
) -> dict:
    """Append one idle-reason tag (operator or measured auto-rule). B9 writer path."""
    if reason not in IDLE_REASON_TAXONOMY:
        raise ValueError(
            f"idle reason must be one of {IDLE_REASON_TAXONOMY}, got {reason!r}"
        )
    row = {
        "ts": datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
        "reason": reason,
        "gap_from": gap_from,
        "gap_to": gap_to,
        "evidence": evidence,
        "note": note,
        "tagged_by": tagged_by,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def _nogo_intervals(health: dict) -> list[tuple[datetime, datetime, dict]]:
    """Turn probe NO-GO points into short evidence intervals (±30 min)."""
    out = []
    for p in health.get("recent") or []:
        if p.get("verdict") != "NO-GO":
            continue
        dt = _parse_ts(p.get("ts"))
        if not dt:
            continue
        out.append(
            (
                dt - timedelta(minutes=30),
                dt + timedelta(minutes=30),
                p,
            )
        )
    return out


def _reason_from_log(logs: list[dict], gap_from: str | None, gap_to: str | None) -> dict | None:
    """Exact or overlapping log hit for a gap."""
    gf = _parse_ts(gap_from)
    gt = _parse_ts(gap_to)
    best = None
    for row in logs:
        reason = row.get("reason")
        if reason not in IDLE_REASON_TAXONOMY:
            continue
        lf = _parse_ts(row.get("gap_from"))
        lt = _parse_ts(row.get("gap_to"))
        # exact key match preferred
        if gap_from and row.get("gap_from") == gap_from and (
            not gap_to or row.get("gap_to") == gap_to
        ):
            return {
                "reason": reason,
                "source": "idle_reason_log",
                "evidence": row.get("evidence") or row.get("note"),
                "tagged_by": row.get("tagged_by"),
            }
        if gf and gt and lf and lt:
            # overlap
            if lf <= gt and lt >= gf:
                best = {
                    "reason": reason,
                    "source": "idle_reason_log",
                    "evidence": row.get("evidence") or row.get("note"),
                    "tagged_by": row.get("tagged_by"),
                }
    return best


def annotate_idle_reasons(
    gaps: list[dict],
    *,
    log_path: Path,
    ledger_rows: list[dict],
    health: dict,
) -> dict:
    """B9 — attach reason class to each idle gap (unknown unless measured/tagged).

    Auto-rules only with named evidence:
      - health_nogo: gap overlaps a probe NO-GO interval
      - weekly_cap: a ledger row with weekly_cap_fired=true ends within 2h before gap start
      - waiting_requeue: last ledger row before gap has state needs_requeue
    Historical silence alone → unknown (never guessed).
    """
    logs = _load_idle_reason_log(log_path)
    nogo = _nogo_intervals(health if isinstance(health, dict) else {})

    # ledger timeline for cap / requeue rules
    timeline = []
    for r in ledger_rows:
        dt = _parse_ts(r.get("recorded_at"))
        if not dt:
            continue
        timeline.append((dt, r))
    timeline.sort(key=lambda x: x[0])

    counts: Counter = Counter()
    annotated = []
    for g in gaps:
        entry = dict(g)
        hit = _reason_from_log(logs, g.get("from"), g.get("to"))
        if hit:
            entry["reason"] = hit["reason"]
            entry["reason_source"] = hit["source"]
            entry["reason_evidence"] = hit.get("evidence")
        else:
            reason = "unknown"
            source = "default"
            evidence = None
            gf = _parse_ts(g.get("from"))
            gt = _parse_ts(g.get("to"))
            if gf and gt:
                for lo, hi, probe in nogo:
                    if lo <= gt and hi >= gf:
                        reason = "health_nogo"
                        source = "health_probe_overlap"
                        evidence = (
                            f"probe NO-GO {probe.get('elapsed_ms')}ms "
                            f"@{probe.get('ts')} account={probe.get('account')}"
                        )
                        break
            if reason == "unknown" and gf and timeline:
                # last ledger row at or before gap start
                prev = None
                for dt, r in timeline:
                    if dt <= gf:
                        prev = (dt, r)
                    else:
                        break
                if prev:
                    pdt, prow = prev
                    pm = prow.get("production_metrics") or {}
                    if pm.get("weekly_cap_fired") is True and (
                        gf - pdt
                    ).total_seconds() <= 2 * 3600:
                        reason = "weekly_cap"
                        source = "ledger_weekly_cap_fired"
                        evidence = f"ledger {prow.get('root')} @ {prow.get('recorded_at')}"
                    elif (prow.get("state") == "needs_requeue") and (
                        gf - pdt
                    ).total_seconds() <= 3600:
                        reason = "waiting_requeue"
                        source = "ledger_needs_requeue"
                        evidence = f"ledger {prow.get('root')} @ {prow.get('recorded_at')}"
            entry["reason"] = reason
            entry["reason_source"] = source
            if evidence:
                entry["reason_evidence"] = evidence
        counts[entry["reason"]] += 1
        annotated.append(entry)

    known = sum(v for k, v in counts.items() if k != "unknown")
    return {
        "measured": bool(annotated) or bool(logs),
        "taxonomy": list(IDLE_REASON_TAXONOMY),
        "gap_count": len(annotated),
        "reason_counts": dict(counts),
        "known_reason_count": known,
        "unknown_reason_count": counts.get("unknown", 0),
        "log_entries": len(logs),
        "log_path": str(log_path.name) if log_path else None,
        "annotated_gaps": annotated,
        "note": (
            "Reasons from operator log or measured auto-rules only; "
            "historical silence stays unknown"
        ),
    }


def store_root_set(store: Path) -> set[str]:
    """Unique PWG roots in the RU store (provenance.root preferred)."""
    roots: set[str] = set()
    if not store.exists():
        return roots
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
            root = (
                prov.get("root")
                or row.get("root")
                or prov.get("window_root")
            )
            if not root:
                sc = row.get("subcard") or ""
                if sc:
                    root = sc.split("~~", 1)[0].lstrip("_")
            if root:
                roots.add(str(root))
    return roots


def article_site_root_set(article_site: Path) -> set[str] | None:
    """Roots published under article_site/, or None if the tree is absent."""
    if not article_site.exists():
        return None
    roots: set[str] = set()
    md = article_site / "md"
    if md.is_dir():
        for p in md.glob("*.md"):
            # skip subcards dir handled separately; only top-level md/<root>.md
            if p.is_file():
                roots.add(p.stem)
    articles_js = article_site / "articles.js"
    if articles_js.exists():
        try:
            text = articles_js.read_text(encoding="utf-8")
        except OSError:
            text = ""
        for m in re.finditer(r'"(?:root|id)"\s*:\s*"([^"]+)"', text):
            roots.add(m.group(1))
        # Prefer keys of ARTICLES object: "sTA": {
        for m in re.finditer(
            r'["\']([A-Za-z_~0-9]+)["\']\s*:\s*\{',
            text,
        ):
            key = m.group(1)
            if key in ("schema", "meta", "version", "generated"):
                continue
            if len(key) <= 40:
                roots.add(key)
    # empty tree still "measured" as zero articles
    return roots


def article_site_parity(store: Path, article_site: Path, missing_cap: int = 20) -> dict:
    """B10 — store root inventory vs published article_site (names only, no DE/RU)."""
    store_roots = store_root_set(store)
    if not store.exists():
        return {
            "measured": False,
            "note": "store missing — cannot compute parity",
        }
    art = article_site_root_set(article_site)
    if art is None:
        return {
            "measured": False,
            "store_roots": len(store_roots),
            "article_roots": None,
            "in_store_not_article": None,
            "in_article_not_store": None,
            "parity_pct": None,
            "missing_from_article_sample": [],
            "note": (
                "article_site/ not built on this machine — run "
                "python RussianTranslation/src/pilot/build_article_site.py "
                "then rebuild kitchen"
            ),
        }
    in_store_not = sorted(store_roots - art)
    in_art_not = sorted(art - store_roots)
    n_store = len(store_roots)
    n_art = len(art)
    # parity: share of store roots that have an article page
    covered = n_store - len(in_store_not)
    parity = round(100 * covered / n_store, 1) if n_store else None
    return {
        "measured": True,
        "store_roots": n_store,
        "article_roots": n_art,
        "in_store_not_article": len(in_store_not),
        "in_article_not_store": len(in_art_not),
        "parity_pct": parity,
        "missing_from_article_sample": in_store_not[:missing_cap],
        "extra_in_article_sample": in_art_not[:missing_cap],
        "note": "Root names only — no DE/RU body on the public kitchen",
    }


# OPT-8 / H2229 — lease collision / store-hit banner (observability only).
COLLISION_EVENT_TYPES = frozenset({
    "lease_collision",
    "store_hit",
    "occupied_keys_unreadable",
    "key_overlap",
})

OPERATOR_ONE_LINER_COLLISION = (
    "If the kitchen collision banner is red (or collision_guard.blocked=true): "
    "DO NOT start a second paid window on those keys/root — a live job or recent "
    "store-hit / lease collision already holds them. Wait for the live job to "
    "finish or requeue that lease; only then import another window."
)

_COLLISION_SUMMARY_RE = re.compile(
    r"key overlap|occupied-keys|SECOND paid window|keys already active|"
    r"DO NOT START A SECOND PAID WINDOW|store.?hit",
    re.I,
)


def _is_collision_event(e: dict) -> bool:
    if not isinstance(e, dict):
        return False
    et = e.get("type") or ""
    if et in COLLISION_EVENT_TYPES:
        return True
    if e.get("state") == "blocked_second_window":
        return True
    summary = e.get("summary") or ""
    return bool(_COLLISION_SUMMARY_RE.search(summary))


def _live_orchestrator_jobs(db_path: Path | None, cap: int = 12) -> list[dict]:
    """Optional advisory: pending/in_progress jobs from max_orchestrator.sqlite."""
    if not db_path or not db_path.exists():
        return []
    try:
        import sqlite3
    except ImportError:
        return []
    out = []
    try:
        con = sqlite3.connect(str(db_path))
        con.row_factory = sqlite3.Row
        rows = con.execute(
            "SELECT external_id, state, started_at, profile_slot FROM jobs "
            "WHERE state IN ('pending','in_progress') ORDER BY id DESC LIMIT ?",
            (cap,),
        ).fetchall()
        for r in rows:
            out.append(
                {
                    "external_id": r["external_id"],
                    "state": r["state"],
                    "started_at": r["started_at"],
                    "profile_slot": r["profile_slot"],
                }
            )
        con.close()
    except Exception:  # noqa: BLE001
        return []
    return out


def collision_guard(
    events_path: Path,
    *,
    orchestrator_db: Path | None = None,
    recent_limit: int = 12,
) -> dict:
    """OPT-8 / H2229 — surface store-hit / lease collision for the public kitchen.

    Reads dashboard_events.jsonl for collision types (emitted when existing
    occupied-keys / nominal-active guards abort). Optional orchestrator sqlite
    lists live jobs as advisory context. Never changes paid spend — display only.
    """
    collisions: list[dict] = []
    if events_path.exists():
        with events_path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not _is_collision_event(e):
                    continue
                data = e.get("data") if isinstance(e.get("data"), dict) else {}
                collisions.append(
                    {
                        "ts": e.get("ts"),
                        "type": e.get("type"),
                        "root": e.get("root"),
                        "level": e.get("level"),
                        "summary": (e.get("summary") or "")[:200],
                        "kind": data.get("kind"),
                        "overlap_count": data.get("overlap_count"),
                        "overlap_sample": data.get("overlap_sample"),
                    }
                )

    live = _live_orchestrator_jobs(orchestrator_db)
    recent = collisions[-recent_limit:]
    blocked = bool(collisions)
    last = recent[-1] if recent else None
    kinds = Counter(
        (c.get("kind") or c.get("type") or "unknown") for c in collisions
    )
    return {
        "measured": bool(collisions) or events_path.exists() or bool(live),
        "blocked": blocked,
        "banner": (
            "DO NOT START A SECOND PAID WINDOW"
            if blocked
            else None
        ),
        "operator_one_liner": OPERATOR_ONE_LINER_COLLISION,
        "collision_count": len(collisions),
        "kind_counts": dict(kinds),
        "last": last,
        "recent": recent,
        "live_jobs": live,
        "live_job_count": len(live),
        "note": (
            "Observability for existing store-hit preflight / occupied-keys / "
            "nominal lease collision aborts (OPT-8). Red banner means a recorded "
            "collision event — not a new concurrency protocol."
        ),
    }

