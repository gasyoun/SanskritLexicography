Read ORCHESTRATION_4ACCOUNT_MAX.md and PIPELINE_AUDIT_2026-07_H818.md completely.

Execute the H818 Windows live acceptance on the currently checked-out PR #416 branch using the owner-authenticated Max profile already present in CLAUDE_CONFIG_DIR.

Be aware that the needed FIX lives in another branch. Go to it, no use to replicate old errors

Constraints:
- exact generation model claude-sonnet-5;
- RU-only no_pwg;
- one account and strictly sequential execution;
- do not inspect, print, copy, or modify credentials;
- do not run any A/B experiments;
- do not provision Linux;
- stop immediately on authentication failure, malformed output, manifest drift, duplicate/lost key, promotion conflict, non-positive store delta, or failed probe;
- retain run_events.jsonl, bug_census.json, manifests, statuses, hashes, audit reports, requeue artifacts, latency/call/retry/quota metrics, and per-attempt logs.

Sequence:
1. Verify PR #416 code and run all offline gates.
2. Initialize the dedicated Max profile and require both auth status and the repository ≥5 KB exact-model live probe to pass.
3. Build a known-heavy presplit manifest and run the non-promoting `presplit-canary`; prove fragment recovery and fidelity. Never import or promote this canary.
4. Run and promote a fresh deterministic 1-headword no_pwg canary.
5. Run and promote a fresh deterministic 10-headword stage.
6. Run and promote one fresh 20-headword window.
7. Prepare the deterministic next 100 unpromoted headwords as five disjoint 20-headword windows.
8. Execute windows 1 and 2, deliberately stop/restart the scheduler, run recovery, then execute windows 3–5.
9. Audit and serialize promotion after every production window; verify canonical store and TM after every promotion.
10. Produce the final H818 GO/NO-GO report and update the audit/history/journals with measured evidence.

Do not mark the PR ready and do not begin H841/H842/H843 unless every H818 GO criterion passes. If a criterion fails, classify it deterministically, preserve its requeue artifact, report NO-GO, and stop.