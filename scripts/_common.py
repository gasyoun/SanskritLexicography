#!/usr/bin/env python3
"""Shared helpers for Uprava tools scripts.

H3283 context: before this module existed, ~50 scripts carried their own private
git()/gh() subprocess wrappers and ~234 call sites across tools/*.py had NO
timeout (one hung git/gh call blocked the whole tool forever). New code routes
subprocess work through run(); existing wrappers migrate opportunistically.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

DEFAULT_TIMEOUT = 60


def repo_root() -> Path:
    """The Uprava checkout holding THIS module (the script tree, per tree_guard)."""
    return Path(__file__).resolve().parent.parent


def github_root() -> Path:
    """Parent directory of the org clones.

    Derived from this file's location rather than Path.home() so it stays correct
    under D:-profile agent sessions where home-based resolution false-fails (H886).
    """
    return repo_root().parent


def run(
    cmd: list,
    cwd=None,
    *,
    timeout: float = DEFAULT_TIMEOUT,
    check: bool = False,
    env: dict | None = None,
    input_text: str | None = None,
) -> subprocess.CompletedProcess:
    """subprocess.run with utf-8 text I/O, captured output, and a MANDATORY timeout.

    Raises subprocess.TimeoutExpired when the deadline passes (caller decides
    retry vs fail); raises CalledProcessError only when check=True.
    """
    merged = os.environ.copy() if env is None else dict(env)
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd is not None else None,
        input=input_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=check,
        env=merged,
    )


def git(repo, *args: str, check: bool = False, timeout: float = DEFAULT_TIMEOUT,
        env: dict | None = None) -> subprocess.CompletedProcess:
    """git -C <repo> <args...> through run()."""
    return run(["git", "-C", str(repo), *args], check=check, timeout=timeout, env=env)


def gh(*args: str, check: bool = False, timeout: float = 120) -> subprocess.CompletedProcess:
    """GitHub CLI through run()."""
    return run(["gh", *args], check=check, timeout=timeout)


def force_utf8_stdio() -> None:
    """Best-effort stdout/stderr reconfigure; safe under redirected streams."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
