#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H5534 selftest — dashboard JSON writes are atomic (tmp file + os.replace).

Proves the crash-safety property of the atomic writers now used by
build_kitchen_data.py / build_progress_data.py:

  1. helper-parity   — both build scripts carry a byte-identical helper.
  2. byte-parity     — atomic output is byte-identical to Path.write_text.
  3. failure path    — if os.replace fails, the old target survives intact
                       and no tmp litter is left behind.
  4. CRASH SIMULATION — a child process is hard-killed (TerminateProcess /
                       SIGKILL) mid-write while looping atomic writes of an
                       ~80 MB JSON payload; after every kill the target file
                       still parses as valid JSON. Never truncated.
  5. contrast (informational) — the same kill loop against the OLD plain
                       Path.write_text; expected to produce at least one
                       truncated target. Not a hard assert (timing-sensitive),
                       printed as evidence the vulnerability was real.

Hermetic: writes only under tempfile.mkdtemp(); reads no repo data.
Exit 0 = PASS, nonzero = FAIL.

Run:  python progress_dashboard/atomic_write_selftest.py
"""

from __future__ import annotations

import importlib.util
import inspect
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

_HERE = Path(__file__).resolve().parent
_BLOB_BYTES = 80 * 1024 * 1024
_ROUNDS = 8


def _load_module(name: str):
    """Load a build script as a module by path (no package context needed)."""
    path = _HERE / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------- child mode
def _child(mode: str, target: str) -> int:
    """Loop-write a big JSON payload until the parent kills us."""
    mod = _load_module("build_progress_data")
    if mode == "atomic":
        write = mod._atomic_write_text
    else:  # "plain" — the OLD pre-H5534 behavior, for the contrast loop

        def write(p, t):
            Path(p).write_text(t, encoding="utf-8")

    text = json.dumps({"gen": 0, "blob": "x" * _BLOB_BYTES}, ensure_ascii=False) + "\n"
    p = Path(target)
    # Signal readiness *after* the expensive startup+dumps, right before the
    # write loop, so the parent's kill lands inside the write phase.
    marker = p.parent / f".ready_{mode}"
    marker.write_text("1", encoding="utf-8")
    gen = 0
    while True:
        write(p, text)
        gen += 1
    return 0  # pragma: no cover — never reached


def _kill_rounds(mode: str, workdir: Path, rounds: int) -> tuple[int, int]:
    """Spawn a writer child, hard-kill it mid-write, validate the target.

    The parent waits for the child's readiness marker (written immediately
    before the write loop), then kills after a 1–30 ms delay — the kill
    therefore lands inside the write phase, not during interpreter startup.

    Returns (truncated, tmp_litter) where tmp_litter counts leftover sibling
    tmp files — litter > 0 proves at least one kill landed INSIDE the write
    phase (between tmp-create and replace), not between two writes.
    """
    target = workdir / f"target_{mode}.json"
    marker = workdir / f".ready_{mode}"
    target.write_text(json.dumps({"gen": -1}), encoding="utf-8")
    truncated = 0
    for r in range(rounds):
        marker.unlink(missing_ok=True)
        proc = subprocess.Popen(
            [sys.executable, os.path.abspath(__file__), "--child", mode, str(target)],
            cwd=str(workdir),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        deadline = time.monotonic() + 60.0
        while not marker.exists() and time.monotonic() < deadline:
            if proc.poll() is not None:
                raise AssertionError(
                    f"[{mode}] child died before readiness: {proc.stderr.read().decode(errors='replace')}"
                )
            time.sleep(0.005)
        assert marker.exists(), f"[{mode}] child never signalled readiness"
        time.sleep(random.uniform(0.001, 0.030))
        was_running = proc.poll() is None
        proc.kill()  # hard kill: SIGKILL / TerminateProcess
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:  # pragma: no cover
            proc.terminate()
            proc.wait(timeout=15)
        try:
            json.loads(target.read_text(encoding="utf-8"))
            ok = True
        except Exception:  # noqa: BLE001 — any decode/parse failure is truncation
            ok = False
            truncated += 1
        tag = "valid" if ok else "TRUNCATED"
        print(f"    [{mode}] round {r + 1}/{rounds}: killed_running={was_running} -> {tag}")
    litter = len(list(workdir.glob(f".{target.name}.*.tmp")))
    return truncated, litter


# ---------------------------------------------------------------- test parts
def test_helper_and_byte_parity() -> None:
    bpd = _load_module("build_progress_data")
    kit = _load_module("build_kitchen_data")
    src_bpd = inspect.getsource(bpd._atomic_write_text)
    src_kit = inspect.getsource(kit._atomic_write_text)
    assert src_bpd == src_kit, "atomic-write helpers drifted between the two build scripts"

    tmp = Path(tempfile.mkdtemp(prefix="h5534_parity_"))
    try:
        text = json.dumps({"a": "тест — ✓", "n": 1}, ensure_ascii=False, indent=2) + "\n"
        via_atomic = tmp / "atomic.json"
        via_write_text = tmp / "plain.json"
        bpd._atomic_write_text(via_atomic, text)
        via_write_text.write_text(text, encoding="utf-8")
        assert via_atomic.read_bytes() == via_write_text.read_bytes(), (
            "atomic writer output diverges from Path.write_text bytes"
        )
        leftovers = list(tmp.glob("*.tmp"))
        assert not leftovers, f"tmp litter left after a successful write: {leftovers}"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("  PASS helper parity + byte parity + no tmp litter")


def test_failure_path() -> None:
    bpd = _load_module("build_progress_data")
    tmp = Path(tempfile.mkdtemp(prefix="h5534_failure_"))
    target = tmp / "t.json"
    target.write_text('{"old": true}\n', encoding="utf-8")
    real_replace = os.replace

    def boom(a, b):  # noqa: ANN001
        raise OSError("simulated os.replace failure")

    os.replace = boom
    try:
        try:
            bpd._atomic_write_text(target, '{"new": true}\n')
            raise AssertionError("os.replace failure was swallowed")
        except OSError:
            pass
    finally:
        os.replace = real_replace
    assert target.read_text(encoding="utf-8") == '{"old": true}\n', "old target was damaged"
    assert not list(tmp.glob("*.tmp")), "tmp file not cleaned up after failure"
    shutil.rmtree(tmp, ignore_errors=True)
    print("  PASS failure path: old target intact, tmp cleaned")


def test_crash_simulation(workdir: Path) -> bool:
    """Hard assert: atomic writer never leaves truncated JSON. Returns contrast result."""
    print(f"  crash-simulating {_ROUNDS} kill rounds (atomic) ...")
    trunc_atomic, litter_atomic = _kill_rounds("atomic", workdir, _ROUNDS)
    assert trunc_atomic == 0, (
        f"ATOMIC GUARANTEE BROKEN: {trunc_atomic} truncated target(s) after hard kills"
    )
    assert litter_atomic > 0, (
        "SIMULATION INEFFECTIVE: no kill landed inside the write phase "
        "(0 leftover tmp files) — evidence would be inconclusive; "
        "raise _BLOB_BYTES / lower the kill delay"
    )
    print(
        f"  PASS crash simulation: every post-kill target was valid JSON; "
        f"{litter_atomic} leftover tmp file(s) prove kill(s) landed mid-write"
    )

    print(f"  contrast loop ({_ROUNDS} kill rounds, old plain write_text) ...")
    trunc_plain, _litter_plain = _kill_rounds("plain", workdir, _ROUNDS)
    if trunc_plain > 0:
        print(f"  CONTRAST CONFIRMED: plain write_text produced {trunc_plain} truncated target(s)")
        return True
    print(
        "  contrast inconclusive this run (no kill landed mid-write); "
        "the atomic guarantee itself was still proven above"
    )
    return False


def main() -> int:
    random.seed(5534)
    print(f"H5534 atomic-write selftest (python {sys.version.split()[0]}, {sys.platform})")
    test_helper_and_byte_parity()
    test_failure_path()
    workdir = Path(tempfile.mkdtemp(prefix="h5534_crash_"))
    contrast_hit = False
    try:
        contrast_hit = test_crash_simulation(workdir)
    finally:
        tmp_leftovers = sorted(p.name for p in workdir.glob(".*.tmp"))
        print(
            f"  tmp litter after hard kills: {len(tmp_leftovers)} file(s) "
            "(expected >0 for killed writers; harmless siblings, target untouched)"
        )
        shutil.rmtree(workdir, ignore_errors=True)
    print(f"SELFTEST PASS (H5534) — atomic writes survive hard kills; contrast_truncated={contrast_hit}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "--child":
        sys.exit(_child(sys.argv[2], sys.argv[3]))
    sys.exit(main())
