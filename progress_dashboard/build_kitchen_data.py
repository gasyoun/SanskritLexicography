#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the PWG→RU *kitchen* snapshot (process, not results).

Companion to build_progress_data.py (lane denominators) and the local
RussianTranslation dashboard_server.py (sub-second ops on localhost:8765).

This emits a small public-safe aggregate for gh-pages /progress/ so the web
page can show the *process* behind the article site:

  - speed      cards/day, recent wall-clock minutes/window
  - cost       tokens/window from the window ledger (+ economy band when present)
  - idle       gaps between stage_boundary audit_end → next audit_start
  - calendar   day-bucketed card + window activity (heatmap) + idle overlay (K7)
  - changelog  recent version bullets from RussianTranslation/CHANGELOG.md
  - K1–K8      operator strip, yield/requeue, ETA, health, instrumentation,
               cost honesty (see kitchen_slices.py / ROADMAP_PROGRESS_KITCHEN_IMPROVEMENTS_2026)
  - residual   B1 subscription $, B9 idle reasons, B10 article-site parity (H2218)
  - OPT-8      collision_guard — store-hit / lease collision kitchen banner (H2229)

All inputs are local-only / gitignored pipeline artifacts under
RussianTranslation/. Missing files degrade that slice; the build never raises.

Run (repo root or via live_refresh.py):
  python progress_dashboard/build_kitchen_data.py
  PWG_DATA_ROOT=/path/to/main/checkout python ...  # isolated worktree

Writes: progress_dashboard/kitchen_data.json
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# Same-dir import for K1–K8 aggregators (H2212).
_sys_dir = str(Path(__file__).resolve().parent)
if _sys_dir not in sys.path:
    sys.path.insert(0, _sys_dir)
import kitchen_slices as ks  # noqa: E402

OUT = Path(__file__).resolve().parent
REPO = OUT.parent
DATA_REPO = Path(os.environ.get("PWG_DATA_ROOT", REPO)).resolve()
RT = DATA_REPO / "RussianTranslation"
PILOT_OUT = RT / "src" / "pilot" / "output"
STORE = RT / "src" / "pwg_ru_translated.jsonl"
LEDGER = PILOT_OUT / "window_ledger.jsonl"
EVENTS = PILOT_OUT / "dashboard_events.jsonl"
WINDOW_STATUS = PILOT_OUT / "window_status.json"
CHANGELOG = RT / "CHANGELOG.md"
ECONOMY = PILOT_OUT / "economy_ledger.json"
SUBSCRIPTION = PILOT_OUT / "economy_subscription.json"
IDLE_REASON_LOG = PILOT_OUT / "idle_reason_log.jsonl"
ARTICLE_SITE = RT / "article_site"
# Scheduler sqlite (cwd-relative when operators run from pilot/); also under pilot/output.
ORCHESTRATOR_DB_CANDIDATES = (
    PILOT_OUT / "max_orchestrator.sqlite",
    RT / "src" / "pilot" / "max_orchestrator.sqlite",
    DATA_REPO / "max_orchestrator.sqlite",
)

# "Translation is on" if any of these artifacts moved within this window.
ACTIVE_WITHIN_SECONDS = 15 * 60
# Gaps shorter than this between audit stages are not counted as idle (pipeline churn).
MIN_IDLE_SECONDS = 120
# Calendar depth shown on the public page.
CALENDAR_DAYS = 120
# Changelog entries kept for the web feed.
CHANGELOG_VERSIONS = 12
CHANGELOG_BULLETS_PER = 4
# Recent windows + idle gaps lists are 1:1 length on the public page.
RECENT_LIST_LEN = 12
# Default Sonnet-class list prices (USD / million tokens) — same as economy_ledger.
DEFAULT_PRICE_USD_PER_M = {
    "input": 3.0,
    "output": 15.0,
    "cache_write": 3.75,
    "cache_read": 0.3,
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    return utc_now().isoformat(timespec="seconds").replace("+00:00", "Z")


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


def _day(ts: str | None) -> str | None:
    if not ts or len(ts) < 10:
        return None
    return ts[:10]


def _iter_jsonl(path: Path):
    if not path.exists():
        return
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def _file_info(path: Path) -> dict:
    if not path.exists():
        return {"exists": False, "mtime": None, "age_seconds": None, "size": None}
    st = path.stat()
    mtime = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc)
    return {
        "exists": True,
        "mtime": mtime.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "age_seconds": int((utc_now() - mtime).total_seconds()),
        "size": st.st_size,
    }


def _mean(vals):
    nums = [v for v in vals if isinstance(v, (int, float))]
    if not nums:
        return None
    return round(sum(nums) / len(nums), 3)


def activity_status() -> dict:
    """Whether the campaign looks live right now (store / status / ledger mtime)."""
    infos = {
        "store": _file_info(STORE),
        "window_status": _file_info(WINDOW_STATUS),
        "window_ledger": _file_info(LEDGER),
        "events": _file_info(EVENTS),
    }
    ages = [
        i["age_seconds"]
        for i in infos.values()
        if i.get("exists") and isinstance(i.get("age_seconds"), int)
    ]
    youngest = min(ages) if ages else None
    active = youngest is not None and youngest <= ACTIVE_WITHIN_SECONDS
    ws = None
    if WINDOW_STATUS.exists():
        try:
            ws = json.loads(WINDOW_STATUS.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            ws = None
    return {
        "translation_on": active,
        "active_within_seconds": ACTIVE_WITHIN_SECONDS,
        "youngest_artifact_age_seconds": youngest,
        "window_state": (ws or {}).get("state"),
        "window_root": (ws or {}).get("root") or ((ws or {}).get("workflow_meta") or {}).get("root"),
        "next_action": (ws or {}).get("next_action"),
        "artifacts": infos,
    }


def store_speed() -> dict:
    """Cards written per recent day / hour from store provenance timestamps."""
    by_day: dict[str, int] = {}
    by_hour: dict[str, int] = {}
    total = 0
    newest = None
    oldest = None
    if not STORE.exists():
        return {"measured": False, "total_cards": 0, "cards_by_day": {}, "last_24h": 0, "last_hour": 0}
    now = utc_now()
    cutoff_24h = now - timedelta(hours=24)
    cutoff_1h = now - timedelta(hours=1)
    last_24h = 0
    last_hour = 0
    for row in _iter_jsonl(STORE):
        prov = row.get("provenance") or {}
        ts = prov.get("generated_at") or row.get("generated_at")
        dt = _parse_ts(ts)
        if not dt:
            continue
        total += 1
        day = dt.date().isoformat()
        hour = dt.strftime("%Y-%m-%dT%H")
        by_day[day] = by_day.get(day, 0) + 1
        by_hour[hour] = by_hour.get(hour, 0) + 1
        if newest is None or dt > newest:
            newest = dt
        if oldest is None or dt < oldest:
            oldest = dt
        if dt >= cutoff_24h:
            last_24h += 1
        if dt >= cutoff_1h:
            last_hour += 1
    # mean cards/day over the last 14 calendar days that have any activity
    recent_days = sorted(by_day)[-14:]
    mean_day = _mean([by_day[d] for d in recent_days]) if recent_days else None
    return {
        "measured": total > 0,
        "total_cards": total,
        "last_24h": last_24h,
        "last_hour": last_hour,
        "mean_cards_per_active_day_14d": mean_day,
        "newest_card_at": newest.isoformat(timespec="seconds").replace("+00:00", "Z") if newest else None,
        "oldest_card_at": oldest.isoformat(timespec="seconds").replace("+00:00", "Z") if oldest else None,
        "cards_by_day": by_day,
    }


def ledger_cost_speed() -> dict:
    """Recent window wall-clock + token figures from window_ledger.jsonl."""
    rows = list(_iter_jsonl(LEDGER)) if LEDGER.exists() else []
    if not rows:
        return {"measured": False, "windows": 0}
    minutes = []
    tokens = []
    recent = []
    wall_clock_n = 0
    for r in rows[-80:]:
        pm = r.get("production_metrics") or {}
        mins = pm.get("wall_clock_minutes")
        tok = (
            pm.get("max_total_tokens")
            or pm.get("max_output_tokens")
            or pm.get("output_tokens")
            or pm.get("total_tokens")
        )
        if isinstance(mins, (int, float)) and mins > 0:
            minutes.append(float(mins))
            wall_clock_n += 1
        if isinstance(tok, (int, float)) and tok > 0:
            tokens.append(float(tok))
        recent.append(
            {
                "recorded_at": r.get("recorded_at"),
                "root": r.get("root"),
                "state": r.get("state"),
                "workflow_keys": r.get("workflow_keys"),
                "translated": r.get("translated"),
                "requeue_count": r.get("requeue_count"),
                "clean_key_count": r.get("clean_key_count"),
                "wall_clock_minutes": mins,
                "tokens": tok,
                "gen_model": r.get("gen_model"),
            }
        )
    shown = recent[-RECENT_LIST_LEN:]
    return {
        "measured": True,
        "windows": len(rows),
        "recent_windows_shown": len(shown),
        "list_len": RECENT_LIST_LEN,
        "mean_wall_clock_minutes": _mean(minutes),
        "wall_clock_sample_n": wall_clock_n,
        "mean_tokens_per_window": _mean(tokens),
        "last_window": recent[-1] if recent else None,
        "recent": shown,
        "all_rows": rows,
    }


def _token_spend_band(tokens: float | int | None, price: dict) -> dict | None:
    """Absolute $ band for a token pile (not per-clean)."""
    if not isinstance(tokens, (int, float)) or tokens <= 0:
        return None
    cr = float(price.get("cache_read") or DEFAULT_PRICE_USD_PER_M["cache_read"])
    inp = float(price.get("input") or DEFAULT_PRICE_USD_PER_M["input"])
    out = float(price.get("output") or DEFAULT_PRICE_USD_PER_M["output"])
    return {
        "floor_usd": round(tokens * cr / 1e6, 4),
        "ceil_usd": round(tokens * inp / 1e6, 4),
        "true_upper_usd": round(tokens * out / 1e6, 4),
        "tokens": int(tokens),
        "basis": "floor=cache_read rate, ceil=fresh-input rate; EXCLUDES output premium",
    }


def _spend_totals_from_economy(summary: dict, runs: list | None = None) -> dict:
    """Split total $ into clean-dictionary path vs prep/redo (wasted + requeues).

    When per-run rows are available:
      clean_path  = tokens on non-requeue rows with clean > 0
      prep_redo   = tokens on requeue rows + clean=0 wasted rows
    Fallback (summary aggregates only):
      clean_path  = total_tokens - wasted_tokens
      prep_redo   = wasted_tokens  (requeue split unavailable)
    """
    price = summary.get("price_basis_usd_per_million") or DEFAULT_PRICE_USD_PER_M
    total_tokens = summary.get("total_tokens")
    wasted_tokens = summary.get("wasted_tokens") or 0
    total_clean = summary.get("total_clean")

    clean_tokens = None
    prep_tokens = None
    split_source = "summary_fallback"

    if runs:
        c_tok = 0
        p_tok = 0
        saw = False
        for r in runs:
            tok = r.get("tokens")
            if not isinstance(tok, (int, float)) or tok <= 0:
                continue
            saw = True
            clean = r.get("clean")
            is_rq = bool(r.get("is_requeue"))
            if clean == 0:
                p_tok += tok
            elif is_rq:
                p_tok += tok
            elif isinstance(clean, (int, float)) and clean > 0:
                c_tok += tok
            else:
                # unknown clean — pool into prep so we never understate overhead
                p_tok += tok
        if saw:
            clean_tokens = c_tok
            prep_tokens = p_tok
            total_tokens = c_tok + p_tok
            split_source = "runs_requeue_and_wasted"

    if clean_tokens is None:
        if isinstance(total_tokens, (int, float)):
            wt = wasted_tokens if isinstance(wasted_tokens, (int, float)) else 0
            clean_tokens = max(0, int(total_tokens) - int(wt))
            prep_tokens = int(wt)
        else:
            clean_tokens = None
            prep_tokens = None

    out = {
        "measured": clean_tokens is not None or prep_tokens is not None,
        "split_source": split_source,
        "total_clean_cards": total_clean,
        "price_basis_usd_per_million": price,
        "clean_dictionary": _token_spend_band(clean_tokens, price),
        "prep_or_redo": _token_spend_band(prep_tokens, price),
        "all_priced": _token_spend_band(total_tokens, price)
        if isinstance(total_tokens, (int, float))
        else None,
        "notes": {
            "clean_dictionary": (
                "tokens on first-pass (non-_rq) runs that produced clean cards — "
                "the production spend toward a clean dictionary"
            ),
            "prep_or_redo": (
                "tokens on clean=0 wasted runs plus requeue (_rq) windows — "
                "preparation, failed drains, and work that had to be redone"
            ),
            "band": (
                "same economy band rates as $/clean card (cache-read floor … fresh-input ceil); "
                "true_upper prices every token at the output rate"
            ),
        },
    }
    if split_source == "summary_fallback":
        out["notes"]["caveat"] = (
            "per-run requeue split unavailable; prep_or_redo = wasted clean=0 tokens only; "
            "requeue tokens remain inside clean_dictionary"
        )
    return out


def economy_band() -> dict:
    """Optional durable economy ledger (agents/$ per clean card) if present."""
    if not ECONOMY.exists():
        # try computing on the fly from the frozen probe log (cheap enough)
        probe = RT / "src" / "pilot" / "generation_api_probe_log.jsonl"
        if not probe.exists():
            return {"measured": False}
        try:
            pilot = str(RT / "src" / "pilot")
            if pilot not in sys.path:
                sys.path.insert(0, pilot)
            import economy_ledger as el  # noqa: WPS433

            rows = el.read_rows(str(probe))
            data = el.build_ledger(rows, source_log=str(probe))
            # Public kitchen only gets aggregates — never the per-run dump.
            summary = {}
            if isinstance(data.get("aggregate"), dict):
                summary.update(data["aggregate"])
            if isinstance(data.get("coverage"), dict):
                summary["coverage"] = data["coverage"]
            summary["price_basis_usd_per_million"] = data.get("price_basis_usd_per_million")
            # Convenience aliases for the HTML cards.
            if "agents_per_clean_incl_requeues" in summary:
                summary.setdefault(
                    "agents_per_clean", summary["agents_per_clean_incl_requeues"]
                )
            band = {}
            for key in (
                "cost_per_clean_floor_usd",
                "cost_per_clean_ceil_usd",
                "cost_band_usd_per_clean",
                "usd_per_clean_floor",
                "usd_per_clean_ceil",
            ):
                if key in summary:
                    band[key] = summary[key]
            if band:
                summary["cost_band_usd_per_clean"] = band
            spend = _spend_totals_from_economy(summary, runs=data.get("runs"))
            return {
                "measured": True,
                "source": "generation_api_probe_log.jsonl",
                "schema": data.get("schema"),
                "summary": summary,
                "spend": spend,
            }
        except Exception as e:  # noqa: BLE001
            return {"measured": False, "error": str(e)[:200]}
    try:
        data = json.loads(ECONOMY.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return {"measured": False, "error": str(e)[:200]}
    summary = data.get("summary") or data.get("aggregate") or data
    if not isinstance(summary, dict):
        summary = {}
    # Prefer embedded price basis when present at top level.
    if "price_basis_usd_per_million" not in summary and data.get(
        "price_basis_usd_per_million"
    ):
        summary = dict(summary)
        summary["price_basis_usd_per_million"] = data["price_basis_usd_per_million"]
    runs = data.get("runs") if isinstance(data.get("runs"), list) else None
    return {
        "measured": True,
        "source": "economy_ledger.json",
        "schema": data.get("schema"),
        "summary": summary,
        "spend": _spend_totals_from_economy(summary, runs=runs),
    }


def _idle_by_month(gaps: list[dict], current_idle: int | None) -> list[dict]:
    """Sum idle seconds per calendar month (UTC) from campaign start → now.

    Each completed gap is attributed to the month of its ``from`` timestamp.
    Open current idle (if any) is added to the current month so the latest
    month reflects time since the last artifact moved.
    """
    month_secs: dict[str, int] = {}
    for g in gaps:
        frm = g.get("from") or ""
        if len(frm) < 7:
            continue
        ym = frm[:7]
        month_secs[ym] = month_secs.get(ym, 0) + int(g.get("seconds") or 0)

    if current_idle is not None and current_idle > 0:
        ym = utc_now().strftime("%Y-%m")
        month_secs[ym] = month_secs.get(ym, 0) + int(current_idle)

    if not month_secs:
        return []

    # Fill every month from first recorded idle through current month.
    first = min(month_secs)
    y, m = int(first[:4]), int(first[5:7])
    end = utc_now()
    end_y, end_m = end.year, end.month
    rows = []
    while (y, m) <= (end_y, end_m):
        ym = f"{y:04d}-{m:02d}"
        secs = month_secs.get(ym, 0)
        rows.append(
            {
                "month": ym,
                "idle_seconds": secs,
                "idle_days": round(secs / 86400, 2),
                "idle_hours": round(secs / 3600, 2),
            }
        )
        m += 1
        if m > 12:
            m = 1
            y += 1
    return rows


def idle_gaps() -> dict:
    """Operator idle = gap between audit_end and the next audit_start (stage_boundary).

    Falls back to gaps between consecutive window_ledger rows when stage_boundary
    events are sparse.
    """
    boundaries = []
    for e in _iter_jsonl(EVENTS) if EVENTS.exists() else []:
        if e.get("type") != "stage_boundary":
            continue
        dt = _parse_ts(e.get("ts"))
        if not dt:
            continue
        stage = e.get("state") or (e.get("data") or {}).get("stage")
        if stage not in ("audit_start", "audit_end"):
            # accept summary form stage_boundary:audit_end
            summary = str(e.get("summary") or "")
            if "audit_start" in summary:
                stage = "audit_start"
            elif "audit_end" in summary:
                stage = "audit_end"
            else:
                continue
        boundaries.append((dt, stage, e.get("root")))

    gaps = []
    last_end = None
    for dt, stage, root in sorted(boundaries, key=lambda x: x[0]):
        if stage == "audit_end":
            last_end = (dt, root)
        elif stage == "audit_start" and last_end is not None:
            secs = (dt - last_end[0]).total_seconds()
            if secs >= MIN_IDLE_SECONDS:
                gaps.append(
                    {
                        "from": last_end[0].isoformat(timespec="seconds").replace("+00:00", "Z"),
                        "to": dt.isoformat(timespec="seconds").replace("+00:00", "Z"),
                        "seconds": int(secs),
                        "after_root": last_end[1],
                        "before_root": root,
                    }
                )
            last_end = None

    # ledger fallback if no stage_boundary gaps
    if not gaps and LEDGER.exists():
        prev = None
        for r in _iter_jsonl(LEDGER):
            dt = _parse_ts(r.get("recorded_at"))
            if not dt:
                continue
            if prev is not None:
                secs = (dt - prev[0]).total_seconds()
                if secs >= MIN_IDLE_SECONDS:
                    gaps.append(
                        {
                            "from": prev[0].isoformat(timespec="seconds").replace("+00:00", "Z"),
                            "to": dt.isoformat(timespec="seconds").replace("+00:00", "Z"),
                            "seconds": int(secs),
                            "after_root": prev[1],
                            "before_root": r.get("root"),
                            "source": "ledger_gap",
                        }
                    )
            prev = (dt, r.get("root"))

    total_idle = sum(g["seconds"] for g in gaps)
    # current idle: time since youngest artifact if translation is not on
    act = activity_status()
    current_idle = None
    if not act["translation_on"] and act["youngest_artifact_age_seconds"] is not None:
        current_idle = act["youngest_artifact_age_seconds"]

    # last completed idle gap (not the open current idle)
    last_gap = gaps[-1] if gaps else None
    last_idle_seconds = last_gap["seconds"] if last_gap else None

    by_month = _idle_by_month(gaps, current_idle)
    # Keep payload bounded: full list is for the expand-on-click UI; recent is 1:1 with windows.
    recent = gaps[-RECENT_LIST_LEN:]

    return {
        "measured": bool(gaps) or current_idle is not None,
        "min_idle_seconds": MIN_IDLE_SECONDS,
        "list_len": RECENT_LIST_LEN,
        "gap_count": len(gaps),
        "total_idle_seconds": total_idle,
        "total_idle_hours": round(total_idle / 3600, 2) if gaps else 0,
        "mean_gap_seconds": _mean([g["seconds"] for g in gaps]),
        "current_idle_seconds": current_idle,
        "last_idle_seconds": last_idle_seconds,
        "last_idle": last_gap,
        "idle_by_month": by_month,
        "recent_gaps": recent,
        "all_gaps": gaps,
    }


def calendar(store_speed_data: dict, gaps: list | None = None) -> dict:
    """Day cells for a contribution-style heatmap (last CALENDAR_DAYS) + idle (K7)."""
    return ks.calendar_with_idle(
        store_speed_data,
        LEDGER,
        gaps or [],
        CALENDAR_DAYS,
        _heat_level,
        utc_now,
    )


def _heat_level(n: int) -> int:
    if n <= 0:
        return 0
    if n < 5:
        return 1
    if n < 25:
        return 2
    if n < 100:
        return 3
    return 4


def web_changelog() -> dict:
    """Parse recent version sections from RussianTranslation/CHANGELOG.md."""
    if not CHANGELOG.exists():
        return {"measured": False, "entries": []}
    text = CHANGELOG.read_text(encoding="utf-8", errors="replace")
    # ## [1.111.5] - 2026-07-31   or ## [Unreleased]
    ver_re = re.compile(r"^## \[([^\]]+)\](?:\s*-\s*(\d{4}-\d{2}-\d{2}))?\s*$", re.M)
    bullet_re = re.compile(r"^###\s+(.+)$", re.M)
    matches = list(ver_re.finditer(text))
    entries = []
    for i, m in enumerate(matches[: CHANGELOG_VERSIONS + 2]):  # skip Unreleased if empty
        ver = m.group(1)
        date = m.group(2)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end]
        bullets = []
        for bm in bullet_re.finditer(body):
            title = bm.group(1).strip()
            # first prose paragraph after the heading (up to blank line)
            after = body[bm.end() :]
            para = after.split("\n\n", 1)[0]
            para = re.sub(r"\s+", " ", para).strip()
            if len(para) > 280:
                para = para[:277] + "…"
            bullets.append({"title": title, "summary": para})
            if len(bullets) >= CHANGELOG_BULLETS_PER:
                break
        if ver.lower() == "unreleased" and not bullets:
            continue
        entries.append({"version": ver, "date": date, "bullets": bullets})
        if len(entries) >= CHANGELOG_VERSIONS:
            break
    return {
        "measured": True,
        "source": "RussianTranslation/CHANGELOG.md",
        "url": "https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CHANGELOG.md",
        "entries": entries,
    }


def main():
    act = activity_status()
    speed = store_speed()
    ledger = ledger_cost_speed()
    idle = idle_gaps()
    cal = calendar(speed, gaps=idle.get("all_gaps") or idle.get("recent_gaps") or [])
    clog = web_changelog()
    econ = economy_band()
    spend = (econ.get("spend") if isinstance(econ, dict) else None) or {"measured": False}

    all_rows = ledger.get("all_rows") or ks.load_ledger_rows(LEDGER)
    op = ks.operator_strip(WINDOW_STATUS, speed, act)
    yld = ks.yield_quality(all_rows)
    gates = ks.gate_summary(EVENTS)
    instr = ks.instrumentation_coverage(all_rows)
    health = ks.health_ribbon(PILOT_OUT)
    quality = ks.quality_slice(PILOT_OUT, all_rows, EVENTS)
    cost_h = ks.cost_honesty(econ if isinstance(econ, dict) else {}, spend)
    eta = ks.eta_verb(RT, speed)

    # H2218 residual slices (B1 / B9 / B10) — additive keys on kitchen v2.
    subscription = ks.load_subscription(SUBSCRIPTION)
    idle_reasons = ks.annotate_idle_reasons(
        idle.get("all_gaps") or [],
        log_path=IDLE_REASON_LOG,
        ledger_rows=all_rows,
        health=health if isinstance(health, dict) else {},
    )
    # Publish reason-annotated gaps (bounded lists) instead of bare gaps.
    annotated_all = idle_reasons.get("annotated_gaps") or idle.get("all_gaps") or []
    idle_pub = dict(idle)
    idle_pub["all_gaps"] = annotated_all
    idle_pub["recent_gaps"] = annotated_all[-RECENT_LIST_LEN:]
    idle_pub["reasons"] = {
        k: v
        for k, v in idle_reasons.items()
        if k != "annotated_gaps"
    }
    # last_idle picks up reason when present
    if idle_pub.get("last_idle") and annotated_all:
        idle_pub["last_idle"] = annotated_all[-1]
    parity = ks.article_site_parity(STORE, ARTICLE_SITE)

    orch_db = next((p for p in ORCHESTRATOR_DB_CANDIDATES if p.exists()), None)
    collision = ks.collision_guard(EVENTS, orchestrator_db=orch_db)

    # Drop bulk rows from published JSON (keep aggregates only).
    ledger_pub = {k: v for k, v in ledger.items() if k != "all_rows"}

    data = {
        "generated_at": utc_now_iso(),
        "schema": "pwg.kitchen.v2",
        "schema_note": (
            "H2218 additive keys: cost.subscription, idle.reasons, article_parity; "
            "H2229 collision_guard (OPT-8 lease/store-hit banner) "
            "(still pwg.kitchen.v2 — non-breaking)"
        ),
        "repo_url": "https://github.com/gasyoun/SanskritLexicography/blob/master",
        "site_url": "https://gasyoun.github.io/SanskritLexicography/",
        "progress_url": "https://gasyoun.github.io/SanskritLexicography/progress/",
        "local_ops_note": (
            "For sub-second run/gate telemetry on the residential machine, run "
            "`python RussianTranslation/src/pilot/dashboard_server.py` (default "
            "http://127.0.0.1:8765/, polls every 5s)."
        ),
        "activity": act,
        "operator": op,
        "yield_quality": yld,
        "gates": gates,
        "instrumentation": instr,
        "health": health,
        "quality": quality,
        "eta": eta,
        "article_parity": parity,
        "collision_guard": collision,
        "speed": {
            "cards_last_hour": speed.get("last_hour"),
            "cards_last_24h": speed.get("last_24h"),
            "mean_cards_per_active_day_14d": speed.get("mean_cards_per_active_day_14d"),
            "mean_wall_clock_minutes": ledger.get("mean_wall_clock_minutes"),
            "wall_clock_sample_n": ledger.get("wall_clock_sample_n"),
            "newest_card_at": speed.get("newest_card_at"),
            "oldest_card_at": speed.get("oldest_card_at"),
            "measured": bool(speed.get("measured") or ledger.get("measured")),
        },
        "cost": {
            "mean_tokens_per_window": ledger.get("mean_tokens_per_window"),
            "windows_in_ledger": ledger.get("windows"),
            "economy": econ,
            "spend": spend,
            "honesty": cost_h,
            "subscription": subscription,
            "measured": bool(
                ledger.get("measured")
                or econ.get("measured")
                or subscription.get("measured")
            ),
        },
        "idle": idle_pub,
        "calendar": cal,
        "changelog": clog,
        "list_len": RECENT_LIST_LEN,
        "recent_windows": ledger_pub.get("recent") or [],
        "last_window": ledger_pub.get("last_window"),
    }

    out_path = OUT / "kitchen_data.json"
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"kitchen_data.json written ({data['generated_at']}).")

    # B4 — append-only quality/fidelity/judge timeseries (one row per build date).
    qts_path = OUT / "quality_timeseries.json"
    qts = ks.quality_timeseries_append(
        qts_path, quality, data["generated_at"], data["generated_at"][:10]
    )
    print(f"quality_timeseries.json: {len(qts['snapshots'])} snapshot(s).")
    print(
        f"  translation_on={act['translation_on']}  "
        f"cards_24h={speed.get('last_24h')}  "
        f"mean_min/window={ledger.get('mean_wall_clock_minutes')}  "
        f"idle_gaps={idle.get('gap_count')}  "
        f"idle_known_reasons={idle_reasons.get('known_reason_count')}  "
        f"subscription={subscription.get('measured')}  "
        f"article_parity={parity.get('measured')}  "
        f"health={health.get('last_verdict')}  "
        f"yield_clean={yld.get('clean_windows')}/{yld.get('windows')}  "
        f"collision_blocked={collision.get('blocked')}  "
        f"collision_n={collision.get('collision_count')}  "
        f"changelog_entries={len(clog.get('entries') or [])}"
    )


if __name__ == "__main__":
    main()
