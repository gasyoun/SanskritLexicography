#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Live progress/kitchen dashboard refresh — residential machine entrypoint.

WHY LOCAL, NOT CI: progress + kitchen numbers are derived from gitignored
RussianTranslation artifacts (store, window_ledger, events). GitHub Actions
never sees them. This script:

  1. Detects whether a translation campaign is *on* (store / window_status /
     ledger mtime within --active-within seconds, default 15 min).
  2. While on (or always with --force / --once), rebuilds:
       progress_dashboard/progress_data.json
       progress_dashboard/progress_timeseries.json
       progress_dashboard/kitchen_data.json
  3. Publishes HTML+JSON to origin/gh-pages under progress/ only — never spams
     master with minute-level commits.
  4. Sleeps --interval seconds (default 60) and repeats when in loop mode.

Usage:
  # one shot (rebuild + publish if active or --force)
  python progress_dashboard/live_refresh.py --once --force

  # loop while translation is on (stops after --idle-stop consecutive idle ticks)
  python progress_dashboard/live_refresh.py

  # rebuild only, no git push (local preview)
  python progress_dashboard/live_refresh.py --once --no-publish --force

Data root: by default the main checkout next to this worktree is used when the
worktree lacks gitignored artifacts. Override with PWG_DATA_ROOT.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
REPO = HERE.parent  # SanskritLexicography checkout (may be a worktree)

PUBLISH = [
    "index.html",
    "progress_data.json",
    "progress_timeseries.json",
    "kitchen_data.json",
]


def log(msg: str) -> None:
    stamp = datetime.now().isoformat(timespec="seconds")
    line = f"[{stamp}] {msg}"
    print(line, flush=True)
    try:
        log_path = HERE / "live_refresh.log"
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass


def run(cmd, cwd, check=True):
    log("$ " + " ".join(str(c) for c in cmd))
    return subprocess.run(cmd, cwd=cwd, check=check)


def resolve_data_root(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).resolve()
    env = os.environ.get("PWG_DATA_ROOT")
    if env:
        return Path(env).resolve()
    # Prefer the canonical main checkout when this is a worktree without the store.
    main = Path(r"C:\Users\user\Documents\GitHub\SanskritLexicography")
    store_here = REPO / "RussianTranslation" / "src" / "pwg_ru_translated.jsonl"
    store_main = main / "RussianTranslation" / "src" / "pwg_ru_translated.jsonl"
    if not store_here.exists() and store_main.exists():
        return main
    return REPO


def is_translation_on(data_root: Path, active_within: int) -> tuple[bool, int | None]:
    paths = [
        data_root / "RussianTranslation" / "src" / "pwg_ru_translated.jsonl",
        data_root / "RussianTranslation" / "src" / "pilot" / "output" / "window_status.json",
        data_root / "RussianTranslation" / "src" / "pilot" / "output" / "window_ledger.jsonl",
        data_root / "RussianTranslation" / "src" / "pilot" / "output" / "dashboard_events.jsonl",
        data_root / "RussianTranslation" / "src" / "pilot" / "output" / "coordinator" / "dashboard.json",
    ]
    now = time.time()
    ages = []
    for p in paths:
        try:
            ages.append(int(now - p.stat().st_mtime))
        except OSError:
            continue
    if not ages:
        return False, None
    youngest = min(ages)
    return youngest <= active_within, youngest


def rebuild(data_root: Path) -> Path:
    """Run builders into a fresh temp copy of progress_dashboard HTML+scripts."""
    env = os.environ.copy()
    env["PWG_DATA_ROOT"] = str(data_root)
    # Build into THIS checkout's progress_dashboard/ so source HTML stays canonical.
    for script in ("build_progress_data.py", "build_kitchen_data.py"):
        cmd = [sys.executable, str(HERE / script)]
        log(f"build: {' '.join(cmd)}  PWG_DATA_ROOT={data_root}")
        subprocess.run(cmd, cwd=str(REPO), check=True, env=env)
    return HERE


def payload_fingerprint(dash_dir: Path) -> str:
    h = hashlib.sha256()
    for name in PUBLISH:
        p = dash_dir / name
        if not p.exists():
            h.update(f"missing:{name}\n".encode())
            continue
        h.update(name.encode())
        h.update(b"\0")
        h.update(p.read_bytes())
        h.update(b"\0")
    return h.hexdigest()[:16]


def publish_gh_pages(dash_dir: Path) -> bool:
    """Copy built files to a throwaway gh-pages worktree and push if changed."""
    run(["git", "fetch", "origin", "gh-pages"], REPO)
    tmp = Path(tempfile.mkdtemp(prefix="progress-live-"))
    wt = tmp / "pages"
    try:
        run(
            ["git", "worktree", "add", "--detach", str(wt), "origin/gh-pages"],
            REPO,
        )
        dest = wt / "progress"
        dest.mkdir(exist_ok=True)
        for name in PUBLISH:
            src = dash_dir / name
            if src.exists():
                shutil.copy2(src, dest / name)
            elif name == "kitchen_data.json":
                log(f"warn: {name} missing — publish without it")
        # nojekyll already at root; nothing else
        run(["git", "add", "progress"], wt)
        diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=wt)
        if diff.returncode == 0:
            log("gh-pages: no content change")
            return False
        msg = (
            "chore(progress-dashboard): live kitchen refresh "
            + datetime.now().strftime("%Y-%m-%d %H:%M")
        )
        run(["git", "commit", "-m", msg], wt)
        run(["git", "push", "origin", "HEAD:gh-pages"], wt)
        log("gh-pages: published progress/")
        return True
    finally:
        subprocess.run(
            ["git", "worktree", "remove", "--force", str(wt)],
            cwd=REPO,
            capture_output=True,
        )
        shutil.rmtree(tmp, ignore_errors=True)


def tick(args, data_root: Path, last_fp: str | None) -> str | None:
    on, age = is_translation_on(data_root, args.active_within)
    log(
        f"activity: translation_on={on} youngest_age={age}s "
        f"(threshold={args.active_within}s) force={args.force}"
    )
    if not on and not args.force and not args.once_idle_ok:
        return last_fp

    dash = rebuild(data_root)
    fp = payload_fingerprint(dash)
    if fp == last_fp and not args.force_publish:
        log(f"payload unchanged ({fp}) — skip publish")
        return fp

    if args.no_publish:
        log(f"built {fp}; --no-publish set")
        return fp

    published = publish_gh_pages(dash)
    if published:
        log(f"published fingerprint={fp}")
    return fp


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--once", action="store_true", help="single rebuild cycle then exit")
    ap.add_argument(
        "--force",
        action="store_true",
        help="rebuild even if translation looks idle",
    )
    ap.add_argument(
        "--once-idle-ok",
        action="store_true",
        help="with --once, rebuild even when idle (alias of --force for one-shot)",
    )
    ap.add_argument("--no-publish", action="store_true", help="rebuild only, no gh-pages push")
    ap.add_argument(
        "--force-publish",
        action="store_true",
        help="push even when payload fingerprint is unchanged",
    )
    ap.add_argument("--interval", type=int, default=60, help="seconds between ticks (default 60)")
    ap.add_argument(
        "--active-within",
        type=int,
        default=15 * 60,
        help="seconds: artifact younger than this ⇒ translation on (default 900)",
    )
    ap.add_argument(
        "--idle-stop",
        type=int,
        default=5,
        help="in loop mode, exit after N consecutive idle ticks (default 5; 0=never)",
    )
    ap.add_argument("--data-root", default=None, help="override PWG_DATA_ROOT")
    args = ap.parse_args()
    if args.once_idle_ok:
        args.force = True

    data_root = resolve_data_root(args.data_root)
    log(f"=== live_refresh start repo={REPO} data_root={data_root} ===")
    last_fp = None
    idle_streak = 0

    while True:
        on, _age = is_translation_on(data_root, args.active_within)
        if not on and not args.force:
            idle_streak += 1
            log(f"idle streak {idle_streak}/{args.idle_stop or '∞'}")
            if args.once:
                log("idle + --once without --force: nothing to do")
                break
            if args.idle_stop and idle_streak >= args.idle_stop:
                log("idle-stop reached — exiting loop")
                break
            time.sleep(args.interval)
            continue

        idle_streak = 0
        try:
            last_fp = tick(args, data_root, last_fp)
        except subprocess.CalledProcessError as e:
            log(f"ERROR: command failed: {e}")
            if args.once:
                raise
        except Exception as e:  # noqa: BLE001
            log(f"ERROR: {e}")
            if args.once:
                raise

        if args.once:
            break
        # After a successful active tick, drop --force so we only continue while live.
        args.force = False
        time.sleep(args.interval)

    log("=== live_refresh done ===")


if __name__ == "__main__":
    main()
