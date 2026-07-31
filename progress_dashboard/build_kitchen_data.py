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
  - calendar   day-bucketed card + window activity (heatmap)
  - changelog  recent version bullets from RussianTranslation/CHANGELOG.md

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

# "Translation is on" if any of these artifacts moved within this window.
ACTIVE_WITHIN_SECONDS = 15 * 60
# Gaps shorter than this between audit stages are not counted as idle (pipeline churn).
MIN_IDLE_SECONDS = 120
# Calendar depth shown on the public page.
CALENDAR_DAYS = 120
# Changelog entries kept for the web feed.
CHANGELOG_VERSIONS = 12
CHANGELOG_BULLETS_PER = 4


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
    for r in rows[-80:]:
        pm = r.get("production_metrics") or {}
        mins = pm.get("wall_clock_minutes")
        tok = pm.get("max_output_tokens") or pm.get("output_tokens") or pm.get("total_tokens")
        if isinstance(mins, (int, float)) and mins > 0:
            minutes.append(float(mins))
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
                "wall_clock_minutes": mins,
                "tokens": tok,
            }
        )
    return {
        "measured": True,
        "windows": len(rows),
        "recent_windows_shown": len(recent),
        "mean_wall_clock_minutes": _mean(minutes),
        "mean_tokens_per_window": _mean(tokens),
        "last_window": recent[-1] if recent else None,
        "recent": recent[-12:],
    }


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
            return {
                "measured": True,
                "source": "generation_api_probe_log.jsonl",
                "schema": data.get("schema"),
                "summary": summary,
            }
        except Exception as e:  # noqa: BLE001
            return {"measured": False, "error": str(e)[:200]}
    try:
        data = json.loads(ECONOMY.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return {"measured": False, "error": str(e)[:200]}
    return {
        "measured": True,
        "source": "economy_ledger.json",
        "schema": data.get("schema"),
        "summary": data.get("summary") or data.get("aggregate") or data,
    }


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

    return {
        "measured": bool(gaps) or current_idle is not None,
        "min_idle_seconds": MIN_IDLE_SECONDS,
        "gap_count": len(gaps),
        "total_idle_seconds": total_idle,
        "total_idle_hours": round(total_idle / 3600, 2) if gaps else 0,
        "mean_gap_seconds": _mean([g["seconds"] for g in gaps]),
        "current_idle_seconds": current_idle,
        "recent_gaps": gaps[-15:],
    }


def calendar(store_speed_data: dict, ledger_rows_hint: int = 0) -> dict:
    """Day cells for a contribution-style heatmap (last CALENDAR_DAYS)."""
    by_day = dict(store_speed_data.get("cards_by_day") or {})
    # overlay window counts from ledger
    windows_by_day: dict[str, int] = {}
    for r in _iter_jsonl(LEDGER) if LEDGER.exists() else []:
        d = _day(r.get("recorded_at"))
        if d:
            windows_by_day[d] = windows_by_day.get(d, 0) + 1

    end = utc_now().date()
    start = end - timedelta(days=CALENDAR_DAYS - 1)
    cells = []
    cur = start
    while cur <= end:
        iso = cur.isoformat()
        cards = by_day.get(iso, 0)
        wins = windows_by_day.get(iso, 0)
        cells.append({"date": iso, "cards": cards, "windows": wins, "level": _heat_level(cards)})
        cur += timedelta(days=1)
    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "days": CALENDAR_DAYS,
        "cells": cells,
        "max_cards": max((c["cards"] for c in cells), default=0),
        "active_days": sum(1 for c in cells if c["cards"] or c["windows"]),
    }


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
    cal = calendar(speed)
    clog = web_changelog()
    econ = economy_band()

    data = {
        "generated_at": utc_now_iso(),
        "schema": "pwg.kitchen.v1",
        "repo_url": "https://github.com/gasyoun/SanskritLexicography/blob/master",
        "site_url": "https://gasyoun.github.io/SanskritLexicography/",
        "progress_url": "https://gasyoun.github.io/SanskritLexicography/progress/",
        "local_ops_note": (
            "For sub-second run/gate telemetry on the residential machine, run "
            "`python RussianTranslation/src/pilot/dashboard_server.py` (default "
            "http://127.0.0.1:8765/, polls every 5s)."
        ),
        "activity": act,
        "speed": {
            "cards_last_hour": speed.get("last_hour"),
            "cards_last_24h": speed.get("last_24h"),
            "mean_cards_per_active_day_14d": speed.get("mean_cards_per_active_day_14d"),
            "mean_wall_clock_minutes": ledger.get("mean_wall_clock_minutes"),
            "newest_card_at": speed.get("newest_card_at"),
            "measured": bool(speed.get("measured") or ledger.get("measured")),
        },
        "cost": {
            "mean_tokens_per_window": ledger.get("mean_tokens_per_window"),
            "windows_in_ledger": ledger.get("windows"),
            "economy": econ,
            "measured": bool(ledger.get("measured") or econ.get("measured")),
        },
        "idle": idle,
        "calendar": cal,
        "changelog": clog,
        "recent_windows": ledger.get("recent") or [],
        "last_window": ledger.get("last_window"),
    }

    out_path = OUT / "kitchen_data.json"
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"kitchen_data.json written ({data['generated_at']}).")
    print(
        f"  translation_on={act['translation_on']}  "
        f"cards_24h={speed.get('last_24h')}  "
        f"mean_min/window={ledger.get('mean_wall_clock_minutes')}  "
        f"idle_gaps={idle.get('gap_count')}  "
        f"changelog_entries={len(clog.get('entries') or [])}"
    )


if __name__ == "__main__":
    main()
