# H2889 — baseline gate matrix

_Created: 18-08-2026 · Last updated: 18-08-2026_

**Frozen commit:** `af58b3b01836e7e888b066b1cd499c3ee53dc602` (`origin/master`, 18-08-2026)
· **Executor:** Opus 5 (`claude-opus-5`), maximum effort
· **Handoff:** [H2889](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2889-Opus_PWG_pwg-translation-comprehensive-code-review_16.08.26.md)

This is the **baseline**, taken before the review touched anything, so that a failure
found later can be attributed to the code rather than to the review. It separates
pre-existing failures from review regressions, which is the whole point of taking it.

**No paid model calls were made.** Every command below is a `--selftest`, `--verify`,
`--check` or fixture path lifted verbatim from
[`.github/workflows/ci.yml`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/ci.yml)
plus the `pytest` suite. Nothing wrote to a production store; the runner's temp directory
stood in for `$RUNNER_TEMP`.

## Environment

| | Review box (this run) | GitHub Actions (`CI` workflow) |
|---|---|---|
| OS | Windows 10 Pro 10.0.19045 | `ubuntu-latest` |
| Python | 3.14.4 | 3.11 |
| pytest | 9.0.3 | from `requirements.txt` |
| `csl-pyutil` | **0.14.0** (user site-packages) | **v0.7.0** (pinned in the workflow) |
| Sibling repos | present under `Documents/GitHub/` — but the run is in a **worktree** at `Documents/SanskritLexicography-h2889-763615`, so the three-levels-up guess misses them | absent (single-repo checkout) |
| Working directory | `C:/Users/user/Documents/SanskritLexicography-h2889-763615/RussianTranslation` | `RussianTranslation` |

The `csl-pyutil` row is not incidental. The repo's own
[`requirements.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/requirements.txt)
declares `csl-pyutil @ git+https://github.com/sanskrit-lexicon/csl-pyutil@main` — a moving
branch — while CI installs `v0.7.0`. The two are seven minor versions apart, and the
difference is load-bearing: one gate fails here and passes there for that reason alone.

## Result

**84 commands · 81 PASS · 3 FAIL · 554.9 s wall.**
All three failures are **pre-existing at the frozen commit** — none was introduced by this
review, and two of them reproduce on GitHub Actions.

| # | Command | Verdict | s | Pre-existing? |
|---|---|---|---:|---|
| 1 | `python src/build_g5_review_sheet.py --selftest` | **FAIL rc=1** | 0.81 | yes — environment-dependent, see B-1 |
| 2 | `python src/pilot/window_selftest.py` | **FAIL rc=1** (210/211 subtests pass) | 62.45 | yes — same root as #3 |
| 3 | `python src/pilot/lang_parity_check.py` | **FAIL rc=1** | 1.62 | yes — **also RED on GitHub Actions** |
| — | the other 81 commands | PASS | 490.0 | — |
| — | `python -m pytest tests -q` (inside the 81) | PASS — **207 passed, 9 skipped** | 104.0 | — |

## The three failures, diagnosed

### B-1 · `build_g5_review_sheet.py --selftest` — the unpinned sibling

```
ValueError: screening= is required when extras=True (H1649). Pass a mapping with
deterministic/lookup/agent/human counts, evidence_path, and rules.
  csl_pyutil/review_sheet.py:2166  <- render_review_sheet
  src/build_g5_review_sheet.py:254 <- _selftest
```

The caller passes `extras=True` without `screening=`. `csl-pyutil` 0.7.0 tolerated that;
0.14.0 refuses it. Because CI pins 0.7.0 and `requirements.txt` says `@main`, **CI is green
on a version no one who follows `requirements.txt` will have**. The selftest's first six
assertions pass, so this is not a broken feature — it is a caller that has fallen behind a
first-party dependency, invisibly, because the two declarations disagree. Carried as a
finding, not merely a baseline note.

### B-2 / B-3 · the cross-language parity ledger is stale — and CI is RED because of it

`lang_parity_check.py` reports four ledger rows whose recorded file hashes no longer match
the files:

| Ledger row | File that moved | Recorded → actual |
|---|---|---|
| `headless_execution_manifest_h818` | `src/pilot/max_account_orchestrator_selftest.py` | `585be93bce0a…` → `54f6b6959fca…` |
| `headless_execution_manifest_h818` | `src/pilot/run_observability.py` | `ec103ba3be97…` → `ca612d3aa998…` |
| `h1339_requeue_materialisation_unattended` | `src/pilot/max_account_orchestrator.py` | `a34a78645665…` → `f0fefdd3048b…` |
| `h1386_resume_recovery_and_medium50` | `src/pilot/max_account_orchestrator.py` | `a34a78645665…` → `f0fefdd3048b…` |

`window_selftest.py` embeds the same check as `test_lang_parity_ledger_complete`, so it
fails for the same reason — 210 of its 211 subtests pass and only the parity one is red.

This is **the same failure GitHub Actions is reporting on `master`**. CI history:

| Run | Commit | Verdict |
|---|---|---|
| [32109682764](https://github.com/gasyoun/SanskritLexicography/actions/runs/32109682764) 18-08 07:03 | `af58b3b01` (the frozen commit) | **failure** — `FAILED (1): test_lang_parity_ledger_complete` |
| [32108713246](https://github.com/gasyoun/SanskritLexicography/actions/runs/32108713246) 18-08 06:51 | `5f3a098f9` | **failure** |
| 18-08 06:14 | `69cad3b5e` | **failure** — first red |
| 17-08 16:41 | `a74890ea9` | success |

The lane went red at `69cad3b5e` ("H3029: land the three preservation branches") and two
further commits landed on top of the red without the gate being restored. The parity gate
is the one guard against a fix reaching the RU path and never the EN path — the failure
mode [`LANG_PARITY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md)
records three real instances of. It is currently not guarding anything. Carried as a
finding.

## What "PASS" here does and does not mean

- It means the **81 commands ran to a zero exit at this commit on this box**, and that a
  later failure in one of them is attributable to a change made after this run.
- It does **not** mean the gates are adequate. Several of them self-skip when a sibling
  checkout is absent (`g5_card_render.py` prints `pwgab table absent — csl-pywork not
  checked out` and exits 0). A gate that passes by declining to check is a green light with
  no evidence behind it; those are contour-6 material and are treated as findings where the
  skip is silent, not merely as baseline noise.
- The 9 skipped `pytest` cases are counted, not hidden: they are the optional-dependency
  and sibling-checkout cases.

## Reproduce

All three helper scripts are read-only and live in the session scratchpad; they take the
worktree path and an output path and write JSON:

| Step | Script | Output |
|---|---|---|
| Enumerate + parse 561 files | `graph.py <worktree> graph.json` | import / subprocess / env / path edges |
| Seed + close | `closure.py <worktree> <dir>` | `seeds.json`, `closure.json` |
| Manifest | `manifest.py <worktree> <dir> <tsv>` | [`H2889_REVIEW_MANIFEST.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2889/H2889_REVIEW_MANIFEST.tsv) |
| Gate matrix | `baseline_gates.py <worktree>/RussianTranslation baseline_gates.json` | the table above |

To re-take the baseline without the scripts, run the command list in
[`.github/workflows/ci.yml`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/ci.yml)
under `working-directory: RussianTranslation` with `RUNNER_TEMP` pointed at a scratch
directory, then `python -m pytest tests -q`.

The final gate re-run, after the review, is recorded in
[`H2889_GATE_PACKET_2026-08.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2889/H2889_GATE_PACKET_2026-08.md).

_Dr. Mārcis Gasūns_
