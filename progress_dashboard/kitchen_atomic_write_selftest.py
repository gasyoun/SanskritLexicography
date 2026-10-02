#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H5582/H5625 selftest — dashboard JSON writes are atomic (tmp + os.replace).

Covers the single shared writer kitchen_slices._atomic_write_text (H5582):
quality_timeseries_append and — since H5625 — the JSON writes of
build_kitchen_data.py / build_progress_data.py. Proves:

  1. helper-parity   — ONE shared helper: kitchen_slices._atomic_write_text;
                       neither builder carries a local copy, and each
                       builder's main() routes its writes through it
                       (H5625 closes H5534's unfinished merge — the old
                       "PR #2360" reference was a registry error, no such PR
                       ever landed).
  2. byte-parity     — atomic output is byte-identical to Path.write_text.
  3. failure path    — if os.replace fails, the old target survives intact
                       and no tmp litter is left behind; the error propagates.
  4. CRASH SIMULATION — a child process is hard-killed (SIGKILL) mid-write
                       while looping quality_timeseries_append over a
                       pre-seeded ~20 MB snapshots payload; after every kill
                       the target still parses as valid JSON. Never truncated.

Hermetic: writes only under tempfile.mkdtemp(); reads no repo data.
Exit 0 = PASS, nonzero = FAIL.

Run:  python progress_dashboard/kitchen_atomic_write_selftest.py
"""

from __future__ import annotations

import importlib.util
import json
import os
import random
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import kitchen_slices as ks  # noqa: E402

_BLOB = 5000
_SEED_SNAPSHOTS = 4000  # ~20 MB on disk once serialized
_ROUNDS = 5


def _load_module(name: str):
    """Load a sibling build script as a module by path (no package context)."""
    path = _HERE / f"{name}.py"
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def inspect_source(func) -> str:
    import inspect

    return inspect.getsource(func)


# ---------------------------------------------------------------- tests
def test_helper_parity():
    # H5625 post-merge contract: ONE shared helper in kitchen_slices; the
    # builders carry no local copy and route their JSON writes through it.
    assert ks._atomic_write_text.__module__ == "kitchen_slices", (
        "kitchen_slices._atomic_write_text went missing — the shared helper "
        "must stay defined exactly once, in kitchen_slices"
    )
    for name in ("build_kitchen_data", "build_progress_data"):
        mod = _load_module(name)
        assert mod is not None, f"could not load {name}"
        local = getattr(mod, "_atomic_write_text", None)
        assert local is None or local.__module__ == "kitchen_slices", (
            f"{name} carries its own _atomic_write_text — keep ONE shared "
            "helper in kitchen_slices (H5582/H5625), never two copies"
        )
        assert "_atomic_write_text" in inspect_source(mod.main), (
            f"{name}.main no longer routes its JSON writes through "
            "kitchen_slices._atomic_write_text"
        )
        print(f"PASS: test_helper_parity — {name}.main routes through the shared helper")


def test_byte_parity():
    quality = {
        "fidelity": {"precision": 0.97, "n": 123},
        "judge_coverage": {"pct": 88.5},
        "clean_windows": 41,
        "crashes": 2,
    }
    with tempfile.TemporaryDirectory() as td:
        a = Path(td) / "via_atomic.json"
        b = Path(td) / "via_plain.json"
        ts_a = ks.quality_timeseries_append(a, quality, "2026-10-01T00:00:00Z", "2026-10-01")
        manual = json.dumps(ts_a, ensure_ascii=False, indent=2) + "\n"
        b.write_text(manual, encoding="utf-8")
        assert a.read_bytes() == b.read_bytes(), "atomic output is not byte-identical to write_text"
        assert list(a.parent.glob(".*.tmp")) == [], "tmp litter left behind"
    print("PASS: test_byte_parity")


def test_replace_failure_keeps_old_target():
    with tempfile.TemporaryDirectory() as td:
        target = Path(td) / "quality_timeseries.json"
        target.mkdir()  # os.replace(file -> dir) must fail
        old_listing = sorted(p.name for p in target.iterdir())
        raised = None
        try:
            ks.quality_timeseries_append(
                target,
                {"fidelity": {"precision": 1.0, "n": 1}},
                "2026-10-01T00:00:00Z",
                "2026-10-01",
            )
        except OSError as exc:  # IsADirectoryError on POSIX, PermissionError on Windows
            raised = exc
        assert raised is not None, "os.replace failure did not propagate"
        assert target.is_dir(), "old target was damaged by a failed replace"
        assert sorted(p.name for p in target.iterdir()) == old_listing
        litter = [p.name for p in Path(td).glob(f".{target.name}.*.tmp")]
        assert litter == [], f"tmp litter left behind on failure: {litter}"
    print("PASS: test_replace_failure_keeps_old_target")


# ------------------------------------------------------- child crash loop
def _child(target_str: str) -> int:
    """Loop quality_timeseries_append over a big seeded payload until killed."""
    target = Path(target_str)
    marker = target.parent / ".ready_h5582"
    seed = [
        {"date": f"2026-{1 + i // 28:02d}-{1 + i % 28:02d}", "blob": "x" * _BLOB}
        for i in range(_SEED_SNAPSHOTS)
    ]
    target.write_text(json.dumps({"snapshots": seed}), encoding="utf-8")
    quality = {"fidelity": {"precision": 0.5, "n": 1}}
    marker.write_text("1", encoding="utf-8")
    day = 1
    while True:
        ks.quality_timeseries_append(
            target, quality, "2026-10-01T00:00:00Z", f"2026-10-{day:02d}"
        )
        day = 1 if day >= 28 else day + 1
    return 0  # pragma: no cover — never reached


def test_hard_kill_mid_write_leaves_valid_json():
    with tempfile.TemporaryDirectory() as td:
        workdir = Path(td)
        target = workdir / "quality_timeseries.json"
        marker = workdir / ".ready_h5582"
        litter_total = 0
        for r in range(_ROUNDS):
            marker.unlink(missing_ok=True)
            proc = subprocess.Popen(
                [
                    sys.executable,
                    os.path.abspath(__file__),
                    "--child",
                    str(target),
                ],
                cwd=str(workdir),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            deadline = time.monotonic() + 120.0
            while not marker.exists() and time.monotonic() < deadline:
                if proc.poll() is not None:
                    raise AssertionError(
                        "child died before readiness: "
                        + proc.stderr.read().decode(errors="replace")
                    )
                time.sleep(0.005)
            assert marker.exists(), "child never signalled readiness"
            time.sleep(random.uniform(0.001, 0.030))
            proc.kill()  # hard kill: SIGKILL / TerminateProcess
            proc.wait(timeout=15)
            try:
                data = json.loads(target.read_text(encoding="utf-8"))
                assert isinstance(data.get("snapshots"), list)
                assert data["snapshots"], "snapshots must survive a mid-write kill"
            except json.JSONDecodeError as exc:
                raise AssertionError(
                    f"round {r}: target truncated after hard kill: {exc}"
                ) from exc
            litter_total += len(list(workdir.glob(f".{target.name}.*.tmp")))
            for stale in workdir.glob(f".{target.name}.*.tmp"):
                stale.unlink()
        print(
            f"PASS: test_hard_kill_mid_write_leaves_valid_json "
            f"({_ROUNDS} kill rounds; tmp litter (kills inside write phase): {litter_total})"
        )


def main() -> int:
    if len(sys.argv) > 2 and sys.argv[1] == "--child":
        return _child(sys.argv[2])
    test_helper_parity()
    test_byte_parity()
    test_replace_failure_keeps_old_target()
    test_hard_kill_mid_write_leaves_valid_json()
    print("\nALL PASS: kitchen_atomic_write_selftest (H5582)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
