#!/usr/bin/env python
"""Shared bounded-best-effort process-tree runner (H818 D-J).

Both the headless worker's generation calls and the orchestrator's probe/worker subprocess
calls spawn the SAME Windows claude launcher — ``node cli-wrapper.cjs``, which ``spawnSync``'s
the native claude binary as a CHILD. The stdlib timeout kill (``TerminateProcess`` on the
immediate node process) leaves that binary ORPHANED, still holding the API call — the observed
multi-minute 'hang' as kill-timeouts accumulate orphans. This module is the single home for the
tree-kill runner so every claude-spawning kill point (worker calls, the outer worker subprocess,
``live_probe``, ``profile_status``, the presplit-canary worker) shares one implementation.
"""
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


def windows_hidden_flags():
    """subprocess creationflags that suppress the transient console window ``taskkill``/``tasklist``
    would otherwise flash on Windows (``CREATE_NO_WINDOW``). Returns 0 (no-op) on POSIX so the same
    call is safe everywhere. Shared by proc_tree's taskkill and the selftests' tasklist so all three
    sites behave consistently."""
    if os.name == 'nt':
        return getattr(subprocess, 'CREATE_NO_WINDOW', 0)
    return 0


def terminate_tree(proc, deadline):
    """**Bounded best-effort** tree termination — NOT race-free (tree enumeration still races
    process exit/spawn; correctness is what the parent->child->grandchild regression test asserts).
    Invoked WHILE ``proc`` is still alive so the tree is enumerable. ``taskkill /PID <pid> /T /F``
    reaps the live tree on Windows (acceptable for this known-stable wrapper tree); ``killpg`` the
    session group on POSIX. Always falls back to ``proc.kill()`` if the parent is still alive.
    Returns a short diagnostic string on cleanup trouble, else None — the caller keeps the primary
    ``timeout`` classification regardless."""
    if proc.poll() is not None:
        return None
    trouble = None
    if os.name == 'nt':
        budget = max(1.0, deadline - time.monotonic())
        try:
            subprocess.run(['taskkill', '/PID', str(proc.pid), '/T', '/F'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=budget,
                           creationflags=windows_hidden_flags())   # no console-window flicker
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as exc:
            trouble = 'taskkill:%s' % type(exc).__name__
    else:
        import signal as _signal
        try:
            os.killpg(os.getpgid(proc.pid), _signal.SIGKILL)
        except (ProcessLookupError, PermissionError, OSError) as exc:
            trouble = 'killpg:%s' % type(exc).__name__
    if proc.poll() is None:                            # always fall back if the parent still lives
        try:
            proc.kill()
        except OSError as exc:
            trouble = (trouble or '') + ';proc.kill:%s' % type(exc).__name__
    return trouble


def run_tree_kill(argv, input=None, timeout=None, text=True, encoding='utf-8',
                  capture_output=False, cwd=None, env=None, **_ignored):
    """Drop-in for ``subprocess.run`` (Popen + ``communicate(timeout=)``) that, on timeout,
    performs bounded best-effort termination of the ENTIRE process tree instead of just the
    immediate child — so a killed call is bounded and no orphaned native binary keeps holding the
    API call (H818 defect D-J). Terminates the tree while the parent is still alive, then drains
    the pipes and reaps the parent using the REMAINING kill budget to an absolute deadline (a small
    grace beyond the call budget, not an independent fixed window). Cleanup trouble is attached
    diagnostically to the raised ``subprocess.TimeoutExpired`` — the caller still records exactly
    one ``timeout`` event."""
    pipe = subprocess.PIPE if capture_output else None
    popen_kw = dict(stdin=subprocess.PIPE, stdout=pipe, stderr=pipe,
                    text=text, encoding=encoding, cwd=cwd, env=env)
    if os.name == 'nt':
        popen_kw['creationflags'] = getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0)
    else:
        popen_kw['start_new_session'] = True          # own process group -> killpg reaches children
    proc = subprocess.Popen(argv, **popen_kw)
    start = time.monotonic()
    try:
        out, err = proc.communicate(input=input, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        grace = min(10.0, (timeout or 0) * 0.1 + 2.0)  # small, proportional, capped cleanup grace
        deadline = start + (timeout or 0) + grace
        trouble = terminate_tree(proc, deadline)
        try:
            remaining = max(0.5, deadline - time.monotonic())
            out, err = proc.communicate(timeout=remaining)     # drain pipes + reap within budget
        except subprocess.TimeoutExpired:
            trouble = (trouble or '') + ';reap-timeout'
            try:
                proc.kill()
                proc.communicate(timeout=2)
            except (OSError, subprocess.TimeoutExpired):
                pass
        if trouble:
            exc.cleanup_trouble = trouble              # diagnostic only; classification stays 'timeout'
        raise
    return subprocess.CompletedProcess(argv, proc.returncode, out, err)
