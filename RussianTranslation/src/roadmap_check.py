#!/usr/bin/env python3
"""Validate the machine-readable scientific-hardening roadmap.

This is intentionally lightweight: it uses only the standard library so the
roadmap can be checked on any clone before a release or review handoff.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROADMAP = ROOT / "roadmap" / "scientific_hardening.json"
GATES = ROOT / "roadmap" / "quality_gates.jsonl"

EXPECTED_SCHEMA_VERSION = "pwg_ru.scientific_hardening.v1"
REQUIRED_PHASE_IDS = {
    "phase_1_repair_audit_defects",
    "phase_2_reharvest_a_slice",
    "phase_3_promote_apresjan_microstructure",
    "phase_4_gold_set_and_double_review",
    "phase_5_schema_ci_exports_edition_cut",
}
ALLOWED_PHASE_STATUS = {"done", "partly_done", "next", "planned", "blocked"}
ALLOWED_GATE_STATUS = {"passing", "partial", "not_started", "blocked", "failing"}


def fail(message: str) -> None:
    print(f"ROADMAP CHECK FAILED: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        fail(f"missing {path}")
    except json.JSONDecodeError as e:
        fail(f"invalid JSON in {path}: {e}")


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    try:
        with path.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as e:
                    fail(f"invalid JSONL in {path}:{line_no}: {e}")
    except FileNotFoundError:
        fail(f"missing {path}")
    return rows


def require_unique_ids(kind: str, rows: list[dict]) -> set[str]:
    seen: set[str] = set()
    for row in rows:
        row_id = row.get("id")
        if not isinstance(row_id, str) or not row_id:
            fail(f"{kind} row without string id: {row!r}")
        if row_id in seen:
            fail(f"duplicate {kind} id {row_id}")
        seen.add(row_id)
    return seen


def main() -> int:
    roadmap = load_json(ROADMAP)
    gate_rows = load_jsonl(GATES)

    if roadmap.get("schema_version") != EXPECTED_SCHEMA_VERSION:
        fail("unexpected schema_version")

    phases = roadmap.get("phases")
    if not isinstance(phases, list):
        fail("phases must be a list")
    phase_ids = require_unique_ids("phase", phases)
    missing_phases = REQUIRED_PHASE_IDS - phase_ids
    if missing_phases:
        fail(f"missing phase ids: {sorted(missing_phases)}")

    for phase in phases:
        if phase.get("status") not in ALLOWED_PHASE_STATUS:
            fail(f"bad status for phase {phase.get('id')}: {phase.get('status')}")
        for field in ("deliverables", "exit_criteria"):
            if not isinstance(phase.get(field), list) or not phase[field]:
                fail(f"phase {phase.get('id')} needs non-empty {field}")

    gates = roadmap.get("quality_gates")
    if not isinstance(gates, list):
        fail("quality_gates must be a list")
    gate_ids = require_unique_ids("gate", gates)
    jsonl_gate_ids = require_unique_ids("jsonl gate", gate_rows)
    if gate_ids != jsonl_gate_ids:
        fail(
            "roadmap quality_gates and quality_gates.jsonl disagree: "
            f"json={sorted(gate_ids)} jsonl={sorted(jsonl_gate_ids)}"
        )

    for gate in gates:
        if gate.get("status") not in ALLOWED_GATE_STATUS:
            fail(f"bad status for gate {gate.get('id')}: {gate.get('status')}")
        if not isinstance(gate.get("blocks_print"), bool):
            fail(f"gate {gate.get('id')} needs boolean blocks_print")
        if not isinstance(gate.get("evidence"), list) or not gate["evidence"]:
            fail(f"gate {gate.get('id')} needs evidence")

    modern_policy = roadmap.get("modern_source_policy", {})
    policy_text = modern_policy.get("policy", "").lower()
    if "publishable body text" not in policy_text:
        fail("modern-source policy must explicitly allow publishable body text")
    if modern_policy.get("publication_blocker") is not False:
        fail("modern-source policy must not be a publication blocker")
    if modern_policy.get("source_attribution_required") is not True:
        fail("modern-source policy must require attribution/provenance")

    blocking = [g for g in gates if g.get("blocks_print") and g.get("status") != "passing"]
    print(
        "ROADMAP CHECK: OK | "
        f"phases={len(phases)} gates={len(gates)} "
        f"blocking_not_passing={len(blocking)}"
    )
    if blocking:
        print("Blocking gates not yet passing: " + ", ".join(g["id"] for g in blocking))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
