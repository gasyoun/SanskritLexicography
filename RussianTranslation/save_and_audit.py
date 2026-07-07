#!/usr/bin/env python
r"""Save a Workflow task-output JSON to wf_output.<tag>.<root>.json, then audit it.

  python save_and_audit.py <root> <task_output_file> [tag] [--no-audit] [--merge] [--force]

tag defaults to 'sc' (Slice C); pass 'sd' etc. for other slices — the tag used to
be hard-coded to 'sc', which silently misfiled every non-sc slice. With audit on
(the default) it shells to src/pilot/audit_window.py and prints the gate summary,
so the script name is honest; pass --no-audit to save only (the bulk-save case).

OVERWRITE GUARD: a requeue save once clobbered a fuller per-root file with its small
subset (the Slice-C recovery gap, HANDOFF_2026-06-30_slicec_recovery.md). So saving a
file with FEWER non-null cards than the existing one is REFUSED unless --force. For a
requeue, use --merge: new non-null cards fill the existing file by result key (the full
set is preserved, nulls are filled).
"""
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    positional = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if len(positional) < 2:
        sys.exit("usage: python save_and_audit.py <root> <task_output_file> [tag] [--no-audit]")
    root, task_file = positional[0], positional[1]
    tag = positional[2] if len(positional) > 2 else "sc"

    with open(task_file, encoding="utf-8") as f:
        wrapper = json.load(f)
    result = wrapper.get("result")
    if isinstance(result, str):
        result = json.loads(result)
    if result is None:                      # direct (non-wrapped) workflow result
        result = wrapper

    # A batch thunk that THROWS (e.g. StructuredOutput retry cap exceeded) makes
    # parallel() yield null for that slot, and grouped.flat() leaves the null in
    # `results`. Drop those null entries so the file is well-formed for the audit
    # + promote_en chain; the dropped batch's cards are simply absent (they surface
    # as missing keys in a requeue diff against the rootmap).
    dropped = sum(1 for r in (result.get("results") or []) if not r)
    if dropped:
        result["results"] = [r for r in result["results"] if r]
        print(f"NOTE: dropped {dropped} null result slot(s) from a failed batch thunk")

    out_path = os.path.join(HERE, f"wf_output.{tag}.{root}.json")

    def nn(res):                                  # non-null card count
        return sum(1 for r in (res.get("results") or []) if r and r.get("card"))

    new_nn = nn(result)
    if os.path.exists(out_path):
        try:
            existing = json.load(open(out_path, encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            existing = None
        old_nn = nn(existing) if isinstance(existing, dict) else 0
        if isinstance(existing, dict) and "--merge" in flags:
            # Better-attempt-wins (H304): "latest requeue wins" is WRONG — a requeue can
            # regress a card (gam h0_63_sam_0 went 2->3->7 missing fragments). Rank:
            # any card > none; complete > partial; fewer missing fragments > more.
            # Ties go to the NEW attempt (fresh gen, same completeness).
            def q(r):
                c = (r or {}).get("card")
                if not c:
                    return (0, 0, 0)
                partial = bool(c.get("partial") or (r or {}).get("partial"))
                missing = len(c.get("missing_fragments")
                              or (r or {}).get("missing_fragments") or [])
                return (1, 0 if partial else 1, -missing)

            by_key = {r.get("key"): r for r in (existing.get("results") or [])}
            kept_better = []
            for r in result.get("results") or []:
                k = r.get("key")
                if k not in by_key:
                    by_key[k] = r                    # new keys append
                elif r.get("card") and q(r) >= q(by_key[k]):
                    by_key[k] = r                    # equal-or-better non-null replaces
                elif r.get("card"):
                    kept_better.append(k)            # worse attempt: keep the prior card
            existing["results"] = list(by_key.values())
            result = existing                        # keep the full-set meta; write merged
            print(f"Merged into {os.path.basename(out_path)}: {old_nn} -> {nn(result)} non-null")
            if kept_better:
                print("kept better prior attempt for: " + ", ".join(kept_better))
        elif old_nn > new_nn and "--force" not in flags:
            sys.exit(f"REFUSED: {os.path.basename(out_path)} has {old_nn} non-null cards; new has "
                     f"only {new_nn}. Use --merge to fill nulls, or --force to overwrite.")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

    cards = result.get("results", [])
    null_count = sum(1 for r in cards if not r.get("card"))
    print(f"Saved {out_path}: {len(cards)} cards, {null_count} null")

    if "--no-audit" in flags:
        return
    # The RU gate (audit_window.py) is .merged.md/RU-specific; the EN track has its own
    # sibling that audits the wf_output.en.*.json per-sense english fields.
    if tag == "en":
        # Strict-by-default in the save path (FL2): a null/hard/crashed gate must fail the
        # save rather than slide through as report-only. A machine-readable report is always
        # written. Pass --lenient to save an EN window without gating.
        audit = os.path.join(HERE, "src", "pilot", "audit_window_en.py")
        report_path = os.path.join(HERE, "src", "pilot", "output", f"audit_en.{root}.report.json")
        cmd = [sys.executable, audit, out_path, "--report", report_path]
        if "--lenient" not in flags:
            cmd.append("--strict")
    else:
        audit = os.path.join(HERE, "src", "pilot", "audit_window.py")
        cmd = [sys.executable, audit, out_path, "--root", root]
    if not os.path.exists(audit):
        print(f"({os.path.basename(audit)} not found — saved only)")
        return
    p = subprocess.run(cmd, text=True, encoding="utf-8", timeout=1800)

    # RU path: also run the anti-silent-partial coverage gate for this root (FL3). Advisory
    # (--warn-only) because it reads the promoted store (pwg_ru_translated.jsonl), which this
    # save has not updated yet — so it reflects the root's CURRENT store completeness and
    # surfaces a known-partial or unverifiable root (the gam 6/127 blind spot) without failing
    # the save. A corrupt/missing EN denominator is reported loudly, never silently exempted.
    if tag != "en":
        cov = os.path.join(HERE, "src", "pilot", "ru_coverage.py")
        if os.path.exists(cov):
            print("\n=== RU coverage (advisory, current store) ===")
            subprocess.run([sys.executable, cov, "--root", root, "--warn-only"],
                           text=True, encoding="utf-8", timeout=1800)
    sys.exit(p.returncode)


if __name__ == "__main__":
    main()
