# Maturity audit — SanskritLexicography data estate

_Created: 22-10-2026 (H6397) · Audited tree: `origin/master` @ 87d6218e (PR #2452) · Audit run: OxAlpha (opencode/z-ai/glm-5.3-flash)_

## Frame (committed first)

Report-only maturity audit of the SanskritLexicography data estate — the largest scholarly surface and upstream conveyor of the csl-corrections pipeline. The audit repairs nothing; findings mint or cite handoffs. Five axes, each scored 0–5 against an explicit threshold rule, headline = mean, plus top-3 levers.

| Axis | Question | Threshold rule (score 5 = …) | Score |
|---|---|---|---|
| 1. Data-layer integrity | gold sets, keys, schema drift, generated-artifact sync (H6384 rekey defect class) | …all integrity gates exit 0 and every generated artifact is in sync with its source at probe time | TBD |
| 2. Pipeline reproducibility | can exports be regenerated from source with one command | …the documented one-command regen runs end-to-end and refuses (non-zero) when the source is absent | TBD |
| 3. Test & gate coverage | pins/selftests on data transforms; are gates required | …every data-transform contract is pinned, the pin doc count matches reality, and all gates are required on master | TBD |
| 4. Docs truth | entry-format contracts match the data | …every sampled documented claim (BOM, filename grammar, counts) verifies true with zero drift | TBD |
| 5. Conveyor health | merge latency, rework rate from git/API history | …median merge latency <24h, no PR >7d, rework share <10% | TBD |

Method: every number below carries its source command and UTC timestamp; probes ran on a session worktree off `origin/master` (87d6218e); the regen probe was actually attempted (acceptance rule). Probe box: Linux, no live csl-orig clone (csl-orig is commit-fenced; read-side regen source lives on the authoring estate at `~/Documents/GitHub/csl-orig/v02/`).
