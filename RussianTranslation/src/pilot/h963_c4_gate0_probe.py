#!/usr/bin/env python3
"""H963 Gate-0: ONE fresh dated D-K health attempt for the c4 profile.

Single-profile c4 only. Runs the repository's own D-K two-phase protocol
(`max_account_orchestrator.live_probe`) at >= v1.9.17 (natural, schema-carrying,
load-representative prompt) against the exact generation model.

Evidence discipline: exactly ONE attempt. Both the warm-up and the measured
reading are emitted to the append-only events log BEFORE any fail-closed exit,
so a NO-GO leaves the same immutable trace as a PASS. No retry, no re-warm,
no reroll. The historical NO-GO (warm-up 29 743 ms / measured 52 815 ms,
15-07-2026) is NOT overwritten or reinterpreted -- this is a new dated reading.

Gate rule applied here is STRICTER than live_probe's own gate: live_probe
excludes the warm-up from the ceiling, but the H963 c4 resume brief requires
that EITHER reading at >= 30 000 ms is a NO-GO. Both are reported.
"""
import json
import os
import shutil
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import max_account_orchestrator as mao  # noqa: E402
from headless_worker import claude_argv_prefix  # noqa: E402


def resolve_claude_bin():
    """D-R: the repo default ``--claude-bin 'claude'`` is a BARE name, so
    ``claude_argv_prefix`` resolves the shim dir via ``abspath('claude')`` -> the CWD,
    finds no ``node_modules`` there, and falls back to ``['claude']`` -- which Windows
    CreateProcess cannot launch (the real file is a ``.cmd`` shim). Resolve to the real
    shim path so the prefix reaches its intended ``[node, cli*.cjs]`` form."""
    if os.name != "nt":
        return "claude"
    for cand in (shutil.which("claude.cmd"), shutil.which("claude"),
                 os.path.join(os.environ.get("APPDATA", ""), "npm", "claude.cmd")):
        if cand and os.path.isfile(cand) and os.path.splitext(cand)[1].lower() == ".cmd":
            return cand
    return "claude"


CONFIG_DIR = r"D:\ClaudeTools\profiles\claude4\.claude"
ACCOUNT = "c4"
RUN_ID = "h963-c4-single-profile-gate0-2026-07-16"
EVENTS = HERE / "output" / "h963_c4_gate0_probe_events.jsonl"
PAYLOAD_BYTES = 6491          # repo default; actual prompt 6828 B (H909 runbook, v1.9.19)
CEILING_MS = mao.PROBE_LATENCY_CEILING_MS   # 30 000
STRICT_CEILING_MS = 30_000    # resume brief: EITHER reading >= this is NO-GO

EVENTS.parent.mkdir(parents=True, exist_ok=True)

# Belt-and-suspenders: pin the store to a scratch path so nothing can touch the
# canonical 11,605-row store. (live_probe makes no store write by construction.)
os.environ["PWG_RU_STORE"] = str(HERE / "output" / "h963_c4_gate0_scratch_store.jsonl")

CLAUDE_BIN = resolve_claude_bin()
ARGV_PREFIX = claude_argv_prefix(CLAUDE_BIN)

prompt = mao._probe_prompt(PAYLOAD_BYTES)
actual_prompt_bytes = len(prompt.encode("utf-8"))

print("=" * 72)
print("H963 Gate-0 — single-profile c4 D-K health attempt")
print("=" * 72)
print("date (UTC)        : %s" % time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
print("profile           : %s  (%s)" % (ACCOUNT, CONFIG_DIR))
print("exact model       : %s" % mao.EXACT_GEN_MODEL)
print("payload_bytes arg : %d" % PAYLOAD_BYTES)
print("actual prompt B   : %d  (floor %d B / 5 KiB=5120)" % (actual_prompt_bytes, mao.PROBE_MIN_PAYLOAD_BYTES))
print("ceiling           : %d ms (strict: either reading >= %d ms => NO-GO)" % (CEILING_MS, STRICT_CEILING_MS))
print("run_id            : %s" % RUN_ID)
print("events            : %s" % EVENTS)
print("claude bin        : %s" % CLAUDE_BIN)
print("resolved argv     : %s" % ARGV_PREFIX)
print("-" * 72)

if actual_prompt_bytes < 5120:
    print("RESULT: NO-GO — payload undersized (%d B < 5 KiB)" % actual_prompt_bytes)
    raise SystemExit(2)

# PRE-FLIGHT (no call made): never spend the one no-reroll attempt on a mis-resolved
# binary. A bare ['claude'] fallback is the D-R defect and is NOT a health reading.
if os.name == "nt" and (len(ARGV_PREFIX) != 2 or not ARGV_PREFIX[0].lower().endswith("node.exe")):
    print("PRE-FLIGHT ABORT (no probe call made, no attempt consumed):")
    print("  claude_argv_prefix(%r) -> %s" % (CLAUDE_BIN, ARGV_PREFIX))
    print("  expected [<node.exe>, <cli*.cjs>]; a bare fallback cannot be launched by")
    print("  CreateProcess. This is a tooling-resolution defect (D-R), NOT a c4 health signal.")
    raise SystemExit(3)

verdict_exc = None
t0 = time.monotonic()
try:
    measured_ms = mao.live_probe(
        CONFIG_DIR,
        claude=CLAUDE_BIN,
        payload_bytes=PAYLOAD_BYTES,
        model=mao.EXACT_GEN_MODEL,
        latency_ceiling_ms=CEILING_MS,
        events_path=str(EVENTS),
        run_id=RUN_ID,
        account=ACCOUNT,
    )
except SystemExit as exc:
    verdict_exc = str(exc)
    measured_ms = None
wall_s = time.monotonic() - t0

print("wall clock        : %.1f s" % wall_s)
print("-" * 72)

# Re-read the append-only events log: it holds BOTH readings even on a fail-closed exit.
readings = []
if EVENTS.exists():
    for line in EVENTS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("run_id") == RUN_ID and row.get("event") == "probe_call":
            readings.append(row)

print("RAW READINGS (append-only telemetry, this run_id):")
for r in readings:
    print("  purpose=%-8s elapsed_ms=%-7s classification=%-10s output_bytes=%s"
          % (r.get("purpose"), r.get("elapsed_ms"), r.get("classification"), r.get("output_bytes")))

by_purpose = {r.get("purpose"): r for r in readings}
warm = by_purpose.get("warmup")
meas = by_purpose.get("measured")

print("-" * 72)
fails = []
if verdict_exc:
    print("live_probe fail-closed: %s" % verdict_exc)

CONN_ERR_CLASSES = {"process", "timeout"}
for label, r in (("warm-up", warm), ("measured", meas)):
    if r is None:
        fails.append("%s reading absent (probe stopped before it ran)" % label)
        continue
    cls = r.get("classification")
    ms = r.get("elapsed_ms")
    if cls != "success":
        fails.append("%s classification=%s (not success)" % (label, cls))
    if cls in CONN_ERR_CLASSES:
        fails.append("%s connection/process error (%s)" % (label, cls))
    if isinstance(ms, int) and ms >= STRICT_CEILING_MS:
        fails.append("%s latency %d ms >= %d ms ceiling" % (label, ms, STRICT_CEILING_MS))

print()
if fails:
    print("GATE-0 VERDICT: NO-GO")
    for f in fails:
        print("  - %s" % f)
    print()
    print("STOP. No canary. No production window. No reroll.")
    raise SystemExit(1)

print("GATE-0 VERDICT: PASS")
print("  warm-up  %d ms (success)" % warm["elapsed_ms"])
print("  measured %d ms (success), strictly below %d ms" % (meas["elapsed_ms"], STRICT_CEILING_MS))
raise SystemExit(0)
