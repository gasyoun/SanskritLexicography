# Maturity audit — SanskritLexicography data estate

_Created: 22-10-2026 (H6397) · Audited tree: `origin/master` @ 87d6218e (PR #2452) · Audit run: OxAlpha (opencode/z-ai/glm-5.3-flash)_

## Frame (committed first)

Report-only maturity audit of the SanskritLexicography data estate — the largest scholarly surface and upstream conveyor of the csl-corrections pipeline. The audit repairs nothing; findings mint or cite handoffs. Five axes, each scored 0–5 against an explicit threshold rule, headline = mean, plus top-3 levers.

| Axis | Question | Threshold rule (score 5 = …) | Score |
|---|---|---|---|
| 1. Data-layer integrity | gold sets, keys, schema drift, generated-artifact sync (H6384 rekey defect class) | …all integrity gates exit 0 and every generated artifact is in sync with its source at probe time | **3** |
| 2. Pipeline reproducibility | can exports be regenerated from source with one command | …the documented one-command regen runs end-to-end and refuses (non-zero) when the source is absent | **2** |
| 3. Test & gate coverage | pins/selftests on data transforms; are gates required | …every data-transform contract is pinned, the pin doc count matches reality, and all gates are required on master | **3** |
| 4. Docs truth | entry-format contracts match the data | …every sampled documented claim (BOM, filename grammar, counts) verifies true with zero drift | **4** |
| 5. Conveyor health | merge latency, rework rate from git/API history | …median merge latency <24h, no PR >7d, rework share <10% | **5** |

Method: every number below carries its source command and UTC timestamp; probes ran on a session worktree off `origin/master` (87d6218e); the regen probe was actually attempted (acceptance rule). Probe box: Linux, no live csl-orig clone (csl-orig is commit-fenced; read-side regen source lives on the authoring estate at `~/Documents/GitHub/csl-orig/v02/`).

## Headline verdict: **3.4 / 5** (mean of 3+2+3+4+5 = 17/20)

The estate is a fast, well-pinned conveyor (axis 5) sitting on data layers whose generated artifacts are stale (axis 1) and whose headline export pipeline fails open (axis 2). Nothing here blocks the csl-corrections conveyor today, but a silent no-op regen or an unnoticed dashboard drift can ship as "green".

## Top-3 levers

1. **Make the export regen fail closed.** `HeadwordLists/headword_diff.py` exits 0 when the live source is missing or empty (probes 2026-10-22T04:52:42Z and 04:55:49Z below) — a regen run can no-op and still look green. Fix = non-zero exit + loud message on missing source / zero lists regenerated, stable output filenames (no key-count renames per regen), per-family BOM preservation on write. This is exactly handoff **H6518** (minted 12-10-2026 as a fan-out of this audit; reconciled in Uprava eaf40ca00) — still the highest-value data-layer lever.
2. **Wire the epistemic/generated-artifact gate into required CI.** `python3 tools/epistemic_integrity_check.py` FAILED at probe time (2026-10-22T04:52:42Z: two dashboards 301 ≠ 302 FINDINGS headings) while master CI was green (2026-10-22T04:52:57Z) — the gate exists but is not required, so drift lives on main. Fan-out **H6517** (closed: PR #2415, Uprava 6f38c825a) repaired the 10-12 instance; the class recurs (295≠300 on 12-10 → 301≠302 on 22-10), so the durable fix is the required gate + regen-in-same-PR rule, not one-off regens.
3. **Machine-check the doc-count contract.** CLAUDE.md pins "**222 pins**" (line 33, updated 06-10-2026, re-measured 201→222 on 12-10 per H6517 close); actual collect today = **226** (2026-10-22T04:52:42Z) — the "verify the pin count, never retype it" rule (H5426) is prose, not a CI check, and drifted again within 10 days. Lever: a CI assertion that the CLAUDE.md pin sentence equals `run_offline_suite.py --collect-only` sum; same class-coverage extension for H6384 (gold-sample key uniqueness asserted by pin, not by re-run).

## Axis 1 — Data-layer integrity: **3/5**

Probes (all commands run in worktree `/tmp/opencode/SanskritLexicography/wt-h6397`, tree 87d6218e):

- **Generated-artifact sync — FAIL.** `2026-10-22T04:52:28Z; timeout 120 python3 tools/epistemic_integrity_check.py` → `EPISTEMIC INTEGRITY: FAIL — 2 defect(s)`: `findings_dashboard/data.json total=301 != 302 distinct FINDINGS headings`; `epistemic_dashboard/epistemic.json core.total=301 != 302` (302 headings scanned). Exit code 1 (verified separately: `…; echo $?` → 1 at 04:52:42Z). Same defect class as the 12-10 probe (295≠300, H6517 evidence) — the drift regenerated once has recurred with new content (PRs #2415–#2452 landed without regen).
- **Gold-set key uniqueness (H6384 rekey defect class) — CLEAN here.** `2026-10-22T04:54:26Z; awk -F'\t' … data/definition_typology_gold.tsv` → `rows=79 distinct_dict|l_id=79 dup_keys=0 schema_bad_rows=0`. The H6384 event_id rekey (177 git-layer gold event_ids re-keyed; root cause: recipe lacked path/kind fields → id collisions; Uprava commits 16700cbf5/3c7fa5591) lives in the read-side register/sheet, not in this repo; the in-repo gold set shows no rekey-class collision at probe time. Threshold honesty: this is one gold set probed, not a census — no in-repo machine gate asserts gold-key uniqueness, so the class is covered by probe, not by gate.
- **Frozen-snapshot hygiene — minor finding.** `ls HeadwordLists/then-2014/MW-unique-key2-*` (2026-10-22T04:54:26Z) → two variants `MW-unique-key2-198220.txt` and `MW-unique-key2-198231.txt` (11 entries apart) inside the frozen 2014 reference directory; the filename grammar does not say which is current. No corruption, but a consumer picking "the" key2 file must guess.

Score 3, not lower: keys are collision-free where probed and the integrity gate exists and catches drift loudly (exit 1). Not 5: two generated dashboards are stale on master right now, and the rekey class has probe-only (not gate) coverage.

## Axis 2 — Pipeline reproducibility: **2/5**

The documented one-command regen is `python headword_diff.py now` (claude-config `/headword-export-regen`, fetched `gh api repos/gasyoun/claude-config/contents/commands/headword-export-regen.md` 2026-10-22T04:54:52Z), reading live `~/Documents/GitHub/csl-orig/v02/<dir>/<dir>.txt` (override `CSL_ORIG_V02`), diffing against read-only `then-2014/`, contract "filename's N must equal its line count".

- **Attempt 1 (missing source):** `2026-10-22T04:52:42Z; python3 HeadwordLists/headword_diff.py` on this box (no csl-orig clone) → exit **0**, output rows `VEI-unique-key1-3703.txt … no csl-orig source (PD not in csl-orig)`, artifacts written anyway (`NOW_VS_THEN.md`, `HeadwordLists/_diff/`). A sourceless regen reports success.
- **Attempt 2 (bogus source):** `2026-10-22T04:55:49Z; CSL_ORIG_V02=/tmp/opencode/nonexistent-csl-orig python3 HeadwordLists/headword_diff.py` → exit **0** again. The exporter cannot fail.
- Full end-to-end regen against live csl-orig was **not executable on this probe box** (no local csl-orig; csl-orig is commit-fenced and absent here) — recorded as the attempt's outcome, per acceptance. The 12-10 probes (H6518 evidence) add the regen-rename defect: with a real source, every regen renames changed files (MW key1 194084→194083, AP 88867→88872), so reruns churn filenames instead of diffing in place, and regenerated key1 lost the then-2014 BOM (610a61 vs efbbbf).

Score 2: the command exists, is documented, and produces real diffs when the source is present. Not 5, and not higher than 2: fail-open exits on missing/bogus source (verified twice above), unstable output names, BOM-state loss — reproducibility today depends on the operator noticing silence.

## Axis 3 — Test & gate coverage on data transforms: **3/5**

- **Pin census:** `2026-10-22T04:52:42Z; python3 tests/run_offline_suite.py --collect-only -q` (summed over the 11 listed test files) → **TOTAL_PINS=226**, suite `exit 0 · network disabled`. CI evidence: `2026-10-22T04:52:57Z; gh run list --repo gasyoun/SanskritLexicography --branch master --limit 8` → all 8 recent master runs `success` (latest h6590 run 2026-10-22T01:20:46Z), including the offline contract-pins job and `utf8_gate` UTF-8 validity job.
- **Coverage shape:** 226 literal record-count/vector pins over the in-scope data modules (`tests/OFFLINE_CONTRACT_PINS_08-09-2026.md` is the evidence doc; CLAUDE.md §What-this-repo-is) — record floors on every headword list is genuine transform coverage.
- **Gaps:** (a) the pin count is doc-quoted by hand (222 vs 226 drift, axis-4 lever 3); (b) `epistemic_integrity_check.py` and dashboard regen are **not** required master checks — its FAIL coexists with green CI (probes above); (c) H6384-class gold-key uniqueness has no pin; (d) the exporter selftest exists (`HeadwordLists/headword_diff_selftest.py`) but does not cover the missing-source exit contract (else axis 2 would fail CI).

Score 3: strong pin lattice + green CI; not 5 because the gates that catch the two live findings (dashboard drift, fail-open regen) sit outside the required set.

## Axis 4 — Docs truth for entry-format contracts: **4/5**

Sampled documented claims, each verified against the data (worktree 87d6218e):

- **BOM contract — TRUE.** CLAUDE.md §Encoding: `MW-unique-key1-193978.txt` has BOM `EF BB BF`, key2 sibling does not. Probe `2026-10-22T04:53:46Z; head -c3 … | od -An -tx1`: key1 = `ef bb bf`, key2 = `61 0a 61` (no BOM). Matches the doc exactly; also confirms the exported-files-BOM warning in AGENTS.md generated block.
- **Filename grammar — TRUE.** `{DICT}-unique-{key1|key2}-{N}.txt`, N = entry count. Probe `2026-10-22T04:54:26Z; grep -c ""` on 4 sampled files → MW key1 N=193978=entries, MW key2 198220=entries, AP 36030=entries, SCH accents 20247=entries — all MATCH. (Probe-method note: `wc -l` undercounts by 1 because the last line carries no trailing newline; `grep -c ""` is the correct meter — the doc's "N must equal its line count" holds under that reading. A first `wc -l` pass read as DRIFT; recorded here so the verifier does not repeat the artifact.)
- **key1 vs key2 semantics, dictionary codes, era split (then-2014/now-2026) — consistent** with the files present in both directories (sampled listings, 04:53–04:54Z).
- **Stale doc number — the one defect.** CLAUDE.md line 33 "222 pins" vs actual 226 (probe 04:52:42Z); "Last updated: 06-10-2026", re-measured 12-10 at 222 (H6517 close). Drift +4 in 10 days.

Score 4: the format contracts a consumer would act on (BOM, keys, counts) are all true today; the count sentence is stale, and only the count sentence.

## Axis 5 — Conveyor health: **5/5**

From the GitHub API (network source; queries verbatim, run 2026-10-22T04:54:52Z):

| Metric | Value | Query |
|---|---|---|
| Merge latency, last 100 merged PRs (median) | **0.1 h** (6 min) | `gh pr list --state merged --limit 100 --json number,createdAt,mergedAt` → per-PR `mergedAt − createdAt`, median |
| P90 merge latency | 1.4 h | same dataset, p90 |
| Merged < 1 h | 89 / 100 | same dataset, count |
| Merged > 7 days | **0** | same dataset, count |
| Rework share (fix/revert/repair-titled among last 100 merged) | **8.0%** (8/100) | `gh pr list --state merged --limit 100 --json number,title` → regex `\b(fix|revert|repair|redo)\b` on title, 04:55:49Z |
| Master CI | green | `gh run list --branch master --limit 8`, all `success`, 04:52:57Z |

Conveyor numbers also contextualize the axes above: 100 merges in a ~12-day window (PRs #2363–#2452) is exactly the velocity that regenerates dashboard drift (axis 1) and pin drift (axis 4) faster than prose rules catch it. Threshold met on all three axes of the rule (median <24h ✓, none >7d ✓, rework <10% ✓) → 5.

## Probe inventory (verifier opens first)

1. `reports/MATURITY_DATA_ESTATE_2026-10-10.md` on master — this file; frame committed in header first (commit 0553edc7).
2. Reproducibility transcript — axis 2, attempts 1 and 2, with exit codes and timestamps (04:52:42Z, 04:55:49Z).
3. Conveyor metrics table — axis 5, queries verbatim (04:54:52Z, 04:55:49Z).
4. `python3 tools/epistemic_integrity_check.py` on master — expect FAIL 301≠302 until the dashboards are regenerated (gate itself healthy, exit 1).

## Findings → handoffs

- **H6517** (ci-regreen-pin-claim, minted 12-10-2026 as fan-out of this audit) — closed: PR #2415, dashboards regreened, pins measured 201→222 (Uprava 6f38c825a). Recurrence of the class is this report's lever 2.
- **H6518** (now2026-regen-write-contract, same fan-out) — reconciled (Uprava eaf40ca00); its three behaviors (fail-closed exit, stable names, BOM preservation) are re-confirmed unmet by probes 04:52:42Z / 04:55:49Z — this report's lever 1.
- New finding minted by this pass: pin-sentence drift 222→226 (axis 4) + non-required epistemic gate (axis 3) — folded into lever 3; mint a small handoff at close time if not already covered by H6517's follow-through.
