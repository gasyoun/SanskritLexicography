# H2889 — PWG translation: comprehensive code and dependency review

_Created: 18-08-2026 · Last updated: 18-08-2026_

**Frozen commit:** `af58b3b01836e7e888b066b1cd499c3ee53dc602` (`origin/master`, 18-08-2026)
· **Executor:** Opus 5 (`claude-opus-5`) at maximum effort, driving nine read-only
specialist lanes and an adversarial verification pass
· **Handoff:** [H2889](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2889-Opus_PWG_pwg-translation-comprehensive-code-review_16.08.26.md)
· **Companions:** [dependency graph](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2889/H2889_RUNTIME_DEPENDENCY_GRAPH_2026-08.md)
· [manifest](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2889/H2889_REVIEW_MANIFEST.tsv)
· [baseline gates](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2889/H2889_BASELINE_GATES_2026-08.md)
· [gate packet](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2889/H2889_GATE_PACKET_2026-08.md)
· [machine-readable findings](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2889/H2889_FINDINGS.json)

## Executive verdict — PARTIAL

**The PWG translation system is broadly well-engineered and is shipping two corrupt
published artifacts.** Both statements are load-bearing and neither cancels the other.

68 findings were reported by nine specialist lanes and the lead. After an adversarial pass
in which every finding was handed to refute-primed verifiers who went to the lines and
tried to break it:

| | Count | What it means here |
|---|---:|---|
| **CONFIRMED** | **29** | traced independently and survived the attempt to refute it |
| **PLAUSIBLE** | **19** | the code trace holds, but no verifier reached the failure from a live entry point |
| **REFUTED** | **20** | died on inspection — preserved, with the refutation, in §6 |
| | **68** | 2 P0 · 13 P1 · 36 P2 · 17 P3 after adjudication |

**Nearly a third of what the lanes reported did not survive**, and the survivors changed
shape: one P0 fell to P3, one to P1, one P1 rose in precision by a factor of 300, and one
finding turned out to be two. Fourteen findings were contested between lenses and each
carries a written adjudication in §4.3 — no verdict was picked silently.

### The two P0s are one deliverable

`release/tei_lex0.xml` and `release/ontolex.ttl` are **both stale and both corrupt**, and
the gate that guards them reports both as validating:

| | `tei_lex0.xml` | `ontolex.ttl` |
|---|---:|---:|
| entries / `LexicalEntry` subjects | 120,173 | 120,173 |
| distinct ids / subjects | 106,082 | 106,082 |
| **duplicated** | **12,374** | **12,374** |

The XML case is invalid by the `xml:id` uniqueness rule and at least a validating parser
could catch it. The RDF case is worse: duplicate subjects are perfectly legal in RDF and
simply **merge**, so 14,091 entries' senses are silently unioned onto the wrong lexical
entry inside a 649,746-triple published graph, with no error anywhere. The artifacts are
released under a Zenodo DOI.

Three independent measurements pin the cause, and it is *not* a bug in the current
exporter:

1. Of the 12,374 duplicated ids, **12,373 have identical `<orth>`** — the same headword
   emitted repeatedly. Exactly **one** (`pwg-U`, for `U` and `U~`) is a genuine `safe_id`
   collapse.
2. Running the **current** `export_interop.py` over the **real** 120,172-card
   `assembled_cards.jsonl` yields exactly **one** duplicate, not 12,374. The uniquifier at
   `export_interop.py:134-135` works.
3. The shipped TEI has **120,173** entries against a stated source of **120,172** records —
   one more entry than the file it names as its origin.

So the artifacts predate the exporter now in the tree. `make_edition_cut` regenerates the
interop artifacts **only when absent** (C7-3, CONFIRMED), which is how they went stale, and
`validate_interop` counts entries and `text.count('ontolex:LexicalEntry')` instead of
checking uniqueness or parsing the graph (C7-1, CONFIRMED), which is why nothing noticed.
`rdflib` is already a dependency and is already used for exactly this in
`lod_acceptance.py`.

**Fix the gate before re-cutting the artifacts.** Re-cutting first would produce clean
bytes behind a blind gate, and the next drift would be equally invisible.

### Why PARTIAL and not PASS

- 19 findings are PLAUSIBLE, i.e. mechanism-without-reproduction. They are **not** claimed
  as defects.
- The commission asked for three independent lenses on every P0–P2. The third lens
  (prior-art / current-state) was run **once by the lead across all findings** rather than
  per finding, because it is a corpus search rather than a code trace. That is a deliberate
  deviation and is recorded as one, not presented as compliance.
- Contour 6 had 129 in-scope files and its lane opened roughly 29 of them; its read summary
  names what it did not read. Coverage of the *manifest* is 100 %; depth of reading is not
  uniform, and the per-lane read summaries are the honest record of that.
- Three baseline gate failures are pre-existing and one of them means **CI on `master` has
  been red for three consecutive pushes** (L-1, CONFIRMED). Every fix below has to land
  through that gate.

## 1. What was reviewed, and how the boundary was proven

The commission was a whole-system review of PWG translation and *every first-party
component it actually depends on* — with the explicit instruction that "whole-system" is
not licence to guess the boundary. So the boundary was computed, not asserted.

An `ast` pass over 561 Python files (0 parse errors) extracted imports, `subprocess` argv
heads, `os.environ` keys and path literals. Six classes of **proven entrypoint** seeded a
transitive closure: CI workflow invocations, `systemd` `ExecStart` targets, operator-skill
commands, `pytest` collection, live operating documents, and runtime `subprocess` spawns.
The closure reaches **361 of 561 files**; with the non-Python first-party artifacts on a
live edge the manifest holds **610 rows, 410 in scope, 100 % dispositioned**. The 200
files outside are not an unexamined remainder — each carries the verdict *no proven live
edge from a PWG-translation entrypoint*, individually, in the manifest.

Three repositories the commission named as candidates — `pwgxml`, `csl-apidev`,
`csl-websanlexicon` — have **no live edge at the frozen commit**: no import, no path
literal, no subprocess, no workflow reference. They are excluded with that evidence rather
than silently dropped. Eleven sibling repos *do* have proven edges and are listed with the
first file:line that proves each.

The structural fact that shaped everything below: the graph is **wide and shallow**.
Roughly three quarters of the in-scope files are entrypoints in their own right — an
`argparse` CLI with a `__main__`. There is almost no deep call stack, but there are ~270
independent front doors, each with its own path resolution, its own failure policy and its
own idea of what "pass" means. Consistency between them cannot be assumed anywhere. Every
systemic theme in §3 is a consequence of that shape.

## 2. Method, and its limits

- **Baseline first.** 84 offline gate commands (the CI list plus `pytest`) were run before
  the review touched anything: **81 PASS, 3 FAIL, 554.9 s**, all three failures
  pre-existing. No paid model calls were made at any point.
- **Nine specialist lanes**, one per commissioned contour, read-only, each returning
  line-anchored findings under one schema. Two lanes (6 and 9) died on a mid-response
  connection error and were re-run.
- **Adversarial verification.** Every P0/P1 finding was given two *independent*
  refute-primed verifiers on separate lenses (correctness of the invariant; reproduction of
  the failure). Every P2/P3 finding was given one. The third commissioned lens —
  prior-art / current-state — was run once by the lead across all findings against the
  repo's FINDINGS/CONTRADICTIONS/DEAD_ENDS/LAUNCH_FUCKUPS/LANG_PARITY registries and the
  Uprava handoff corpus, because that lens is a corpus search rather than a code trace and
  splitting it per finding would have bought nothing. **This is a deliberate deviation from
  the commissioned "three independent lenses per P0-P2" and is recorded as such**, not
  presented as compliance.
- **Verdicts are conservative by construction.** Verifiers were instructed that "I could
  not prove it wrong" is PLAUSIBLE, never CONFIRMED, and were handed the seven ways these
  findings usually die — including one the lead had already been caught by (a lock taken
  through a lazy import inside the function).

**What this review does not establish.** The closure is static: `importlib`/dynamic
imports are not followed (none was observed, which is not proof). Data-file edges are
proven by literal, not by execution — a path in a file shows the code *can* read it, not
that a given run did. Sibling-repo internals are out of scope; the edge is reviewed,
`csl-orig`'s own code is not. Several gates self-skip when a sibling checkout is absent,
so a lane running in this environment exercised the degraded path, not the full one, and
said so in its read summary.

## 3. Systemic themes — the findings are nine shapes, not fifty accidents

Ranked by how much of the review they explain.

### T1 · A gate whose PASS is indistinguishable from "nothing was checked"

The single largest family. A gate is scoped to a directory nothing writes to; a validator
counts a substring instead of parsing; a surveillance check reads a filename and an mtime
but never the file; a golden test regenerates its own goldens before comparing them; a
coverage report prints 0 % when the source was simply never built. In each case the green
light is real and the evidence behind it is absent. This is the most dangerous shape in
the system because it converts a missing check into a positive assurance, and because the
downstream reader — a `quality_gates.jsonl` row, an auto-merge label, an operator — has no
way to tell the two apart.

The **headline finding of this review is the compound case**: the published TEI-Lex0
artifact is genuinely corrupt (12,374 duplicated `xml:id` values), the gate that guards it
reports it as validating, and the mechanism that let the artifact go stale is a third
finding in the same contour. One theme, three findings, one broken deliverable.

### T2 · Path resolution that differs precisely in the environment the rules mandate

`sibling_root.py` exists because eleven modules each guessed
`os.path.join(HERE,'..','..','..')` — true only in the canonical checkout, false in a
`git worktree`, which this repo's own shared-main-tree rule *requires*. At the frozen
commit 13 files import the canonical resolver and **41 still guess**. The two regimes
coexist and disagree exactly where the workflow rules put every session. `store_path.py`
is the counter-example that proves the point: it handles the linked-worktree case
correctly, and its docstring names the incident (H255, 29 promotions silently lost) that
taught the lesson. The lesson was learned in one module and not propagated.

### T3 · A lock narrower than the read-modify-write window it protects

`PromoteClaim` is a real, well-built lock. Several callers take it around the *write* and
do the *read* outside it, so a concurrent promote lands between the two and is overwritten
by a stale snapshot. One path takes no claim at all. One appends unlocked while its twin
does a locked read-modify-replace, so an append landing in the window is deleted. The
common error is not "no locking" — it is a correct lock placed one step too late.

### T4 · `key1` treated as an identity the source does not have

PWG has 123,366 records and 13,900 headwords that own more than one of them. Repeatedly,
code keys on `key1` as though it were unique: a card's printed page/column is chosen from
an arbitrary homograph; a durable metadata API returns only the first record of a group; a
positional ordinal into a live upstream file is persisted as a stable record id; an
upstream-change worklist emits one hash for an N-row group. The dictionary's own data
model — one headword, many entries — is the thing the code keeps forgetting.

### T5 · Provenance asserted rather than measured

93 % of the live store carries `prompt_version: "1.0.0"` with no prompt hash behind it:
the version was stamped retrospectively. A source-commit lookup that fails returns the
string `'unknown'` rather than failing. Nine rows carry no input identity at all. Each of
these is individually small; together they mean that for most of the corpus, "which prompt
produced this row" is not a question the artifacts can answer.

### T6 · Unguarded process and operations boundaries

A `systemd` unit with a 600 s paid dispatch and no `TimeoutStartSec` (default 90 s); three
unguarded `ExecStart` lines where an ordinary refusal in step two skips the harvest in
step three; a paid A/B that kills a launcher and orphans the child still holding the API
call; subprocesses on the unattended drain path with no timeout at all.

### T7 · Cost and telemetry counted wrong

A weekly cost ceiling that ignores every dollar spent by a window that timed out; an
unkeyed usage append that double-counts a re-run; census counters that bypass the
exactly-once dedup they document.

### T8 · Rights and licence metadata that contradicts itself

The DE edition graph stamps one licence on the whole lexicon while its own pack ships
another; a citable export ignores the per-sense rights flag it is handed. This sits
against a repository that is otherwise careful about rights (see §5).

### T9 · A release cut over stale or unblocked bytes

Interop artifacts are regenerated only when *absent*, so a sha256-pinned "immutable"
edition can be cut over pre-fix bytes; and the readiness report computes the interop
verdict, prints it, and then leaves it out of the blocker list, so the same page can read
"blocked" on one row and "ready-to-cut" on another.

## 4. Findings

**68 findings reported · 29 CONFIRMED · 19 PLAUSIBLE · 0 CONTESTED · 20 REFUTED**

### 4.1 Confirmed

Every one of these was traced independently by two refute-primed verifiers (P0/P1) or one (P2/P3), each of which went to the lines and tried to break it.

| ID | Sev | Status | Defect | Anchor |
|---|---|---|---|---|
| `C7-1` | **P0** | CONFIRMED | validate_interop is the G9 gate but cannot detect the corruption it gates: ElementTree does not enforce xml:id uniqueness and the OntoLex check is a substring count | [`RussianTranslation/src/validate_interop.py:21`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/validate_interop.py#L21) |
| `L-9` | **P0** | CONFIRMED | Both shipped interop artifacts are stale and corrupt: 12,374 duplicated xml:id in tei_lex0.xml and the same 12,374 merged subjects in ontolex.ttl, while the G9 gate reports both as validating | [`RussianTranslation/release/tei_lex0.xml:5`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/tei_lex0.xml#L5) |
| `C1-1` | **P1** | CONFIRMED | `~~h<N>` in a subcard key is a 0-based index over homonym blocks, not a homonym number, so 1,278 of 5,211 mappable store rows carry a printed column that is not their own record's | [`RussianTranslation/src/pwg_page_index.py:167`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_page_index.py#L167) |
| `C5-1` | **P1** | CONFIRMED | promote_en reads the whole store outside the PromoteClaim and writes that snapshot back inside it — a concurrent promote is silently overwritten, recoverable only from the backup | [`RussianTranslation/src/promote_en.py:504`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_en.py#L504) |
| `C5-2` | **P1** | CONFIRMED | Two flags of the same promote entry point disagree on identical input: `--merge` refuses a 99.7% content-mass shed, `--ready-partial-report --apply` performs it silently | [`RussianTranslation/src/promote_final_cards.py:222`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_final_cards.py#L222) |
| `C7-3` | **P1** | CONFIRMED | make_edition_cut regenerates the interop artifacts only when ABSENT, so a sha256-pinned "immutable" edition can be cut over stale, pre-fix bytes | [`RussianTranslation/src/make_edition_cut.py:96`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/make_edition_cut.py#L96) |
| `C7-5` | **P1** | CONFIRMED | The DE edition graph stamps dct:license = Public Domain Mark 1.0 on the whole lexicon, contradicting its own pack licence (CC-BY-SA-4.0) and its own "project" rights posture for the NWS layer | [`RussianTranslation/src/export_de_edition.py:312`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/export_de_edition.py#L312) |
| `L-1` | **P1** | CONFIRMED | CI on master has been RED for three consecutive pushes at the cross-language parity gate, and two commits landed on top of the red | [`.github/workflows/ci.yml:236`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/ci.yml#L236) |
| `C1-6` | **P2** | CONFIRMED | The Nachträge adjacent-marker fix is applied only to the loci export; portrait() still misattributes ~2,310 back-references to sense 1 | [`RussianTranslation/src/microstructure.py:330`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/microstructure.py#L330) |
| `C2-2` | **P2** | CONFIRMED | The auto-promote surveillance heartbeat is satisfied by an empty or content-free spot-check report, because only the filename prefix and the mtime are ever read | [`RussianTranslation/src/pilot/lane_spotcheck_tick.py:69`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/lane_spotcheck_tick.py#L69) |
| `C2-5` | **P2** | CONFIRMED | Coverage report prints 0% corpus/dictionary coverage when the sources are simply not built | [`RussianTranslation/src/corpus_gate.py:659`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/corpus_gate.py#L659) |
| `C2-6` | **P2** | CONFIRMED | Re-glue skeleton drops a translated PWG sense on a normalised-tag collision, and the byte-identity gate cannot see it | [`RussianTranslation/src/build_reglue.py:122`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_reglue.py#L122) |
| `C3-4` | **P2** | CONFIRMED | prompt_rule_audit --fail-on-missing exits 0 when the audited prompt template is absent | [`RussianTranslation/src/pilot/prompt_rule_audit.py:993`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/prompt_rule_audit.py#L993) |
| `L-5` | **P2** | CONFIRMED | 93% of the promoted store carries retrospectively backfilled prompt/glossary/script versions with no hashes behind them | [`RussianTranslation/src/pwg_ru_translated.jsonl:1`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ru_translated.jsonl#L1) |
| `C4-3` | **P2** | CONFIRMED | h2189 paid A/B kills the node launcher with the stdlib timeout, orphaning the native Claude child that still holds the API call | [`RussianTranslation/src/pilot/h2189_profile_ab.py:198`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h2189_profile_ab.py#L198) |
| `C5-6` | **P2** | CONFIRMED | Retrieval eval leaks the reference translation into the with-TM arm: the hold-out exclusion is applied to the sample TM but not to the publication TM | [`RussianTranslation/src/tm_retrieval_eval.py:754`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_retrieval_eval.py#L754) |
| `C6-01` | **P2** | CONFIRMED | gold_agreement's release-mode guard is disarmed by any non-default input path, and two documented commands use one — so a kappa-free or LLM-panel agreement report can latch the G7 roll-up | [`RussianTranslation/src/preflight_remaining_gates.py:127`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/preflight_remaining_gates.py#L127) |
| `C6-05` | **P2** | CONFIRMED | Daily spot-check: an all-errors judge day exits clean and never trips the R4.1 freeze, contradicting its own 'inconclusive is never PASS' contract | [`RussianTranslation/src/pilot/spot_check_daily.py:227`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/spot_check_daily.py#L227) |
| `C7-2` | **P2** | CONFIRMED | safe_id() collapses two distinct key1 values onto one xml:id / RDF subject — exactly one live collision pair (`U` vs `U~`), and it is NOT the cause of the 12,374 duplicates in the shipped artifact | [`RussianTranslation/src/export_interop.py:36`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/export_interop.py#L36) |
| `C8-3` | **P2** | CONFIRMED | changelog-lint gate only inspects the ROOT changelog; RussianTranslation/CHANGELOG.md is unguarded and already carries the exact defect | [`scripts/changelog_duplicate_bullets.py:169`](https://github.com/gasyoun/SanskritLexicography/blob/master/scripts/changelog_duplicate_bullets.py#L169) |
| `C8-4` | **P2** | CONFIRMED | Launch-ledger CI gate cannot match a 4-digit handoff ID, so it can no longer flag any missing launch-failure entry | [`RussianTranslation/src/pilot/check_launch_ledger.py:28`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/check_launch_ledger.py#L28) |
| `C8-7` | **P2** | CONFIRMED | Census counters bypass the exactly-once dedup they are documented to obey, so a re-appended event inflates cards/clean/calls | [`RussianTranslation/src/pilot/run_observability.py:161`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/run_observability.py#L161) |
| `L-2` | **P2** | CONFIRMED | requirements.txt pins csl-pyutil to a moving branch while CI pins v0.7.0 — the repo is broken against its own declared dependency | [`requirements.txt:9`](https://github.com/gasyoun/SanskritLexicography/blob/master/requirements.txt#L9) |
| `C9-02` | **P2** | CONFIRMED | RUN_FREQ_MAX.md states 300 000 ms is the absolute per-call maximum and that --timeout defaults to 300; the code's ceiling and default are both 600 000 ms / 600 s | [`RussianTranslation/src/pilot/RUN_FREQ_MAX.md:752`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md#L752) |
| `C9-03` | **P2** | CONFIRMED | FAILURE_MODES kill-gate 'Calibrated constants' table and every budget it derives are unreproducible from the code it names | [`RussianTranslation/FAILURE_MODES_AND_KILL_GATE_2026-07-04.md:148`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/FAILURE_MODES_AND_KILL_GATE_2026-07-04.md#L148) |
| `C9-04` | **P2** | CONFIRMED | DATA_LICENSE.md says CITATION.cff stays at 'version: unreleased' until the edition cut is archived and a DOI registered; the committed CITATION.cff carries version 1.144.36 with a release date and no DOI | [`RussianTranslation/DATA_LICENSE.md:52`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/DATA_LICENSE.md#L52) |
| `C3-1` | **P3** | CONFIRMED | prompt_compiler.selftest() rewrites its own committed goldens before comparing them, so the golden half of the test can never fail — the compiler-vs-builder oracle is what actually guards prompt assembly | [`RussianTranslation/src/pilot/prompt_compiler.py:343`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/prompt_compiler.py#L343) |
| `C9-05` | **P3** | CONFIRMED | PIPELINE_HISTORY.md, last updated 10-08-2026, still asserts the 'NOTHING runs past 3 min (MG)' standing ruling was not relaxed — four days after the ceiling was ruled up to 10 min | [`RussianTranslation/PIPELINE_HISTORY.md:37`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md#L37) |
| `C9-06` | **P3** | CONFIRMED | Ruling D2 requires a machine-preview caveat on every citation of the lane and the export layer grades machine-preview 'non-citable'; CITATION.cff carries no such caveat | [`RussianTranslation/DECISIONS_PWG_RU_QUALITY_BAR.md:75`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/DECISIONS_PWG_RU_QUALITY_BAR.md#L75) |

### 4.2 Plausible — real mechanism, reproduction not closed

The code trace holds but no verifier got from a live entry point to the failure, or the two lenses did not both confirm. These are **not** actionable as defects without the missing reproduction; they are recorded so the next pass does not re-derive them.

| ID | Sev | Status | Defect | Anchor |
|---|---|---|---|---|
| `C2-1` | **P1** | PLAUSIBLE | Weekly cost ceiling silently ignores every dollar spent by a window that times out | [`RussianTranslation/src/pilot/nonstop_scheduler.py:211`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/nonstop_scheduler.py#L211) |
| `C3-2` | **P1** | PLAUSIBLE | provenance.pipeline.prompt_version stamped on every promoted row does not cover the prompt that produced the row | [`RussianTranslation/src/pipeline_versions.json:10`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pipeline_versions.json#L10) |
| `C5-3` | **P1** | PLAUSIBLE | lane_guard's automatic store revert rewrites the whole canonical store with NO PromoteClaim at all | [`RussianTranslation/src/pilot/lane_guard.py:76`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/lane_guard.py#L76) |
| `C5-4` | **P1** | PLAUSIBLE | TM denylist has an asymmetric lock: denials are appended unlocked while unblocks do a locked read-modify-REPLACE, so a denial landing in the window is silently deleted | [`RussianTranslation/src/pilot/translation_memory.py:368`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/translation_memory.py#L368) |
| `C7-4` | **P1** | PLAUSIBLE | release_readiness computes the interop verdict, prints it, and then omits it from the edition blockers — G10 can read "ready-to-cut" on the same report whose G9 row reads "blocked" | [`RussianTranslation/src/release_readiness.py:110`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/release_readiness.py#L110) |
| `C1-5` | **P2** | PLAUSIBLE | _stale_for emits one key1 and one input_raw_sha256 for an N-row group, so N-1 rows are re-checked against the wrong hash | [`RussianTranslation/src/pilot/watch_upstream.py:243`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/watch_upstream.py#L243) |
| `C2-3` | **P2** | PLAUSIBLE | verb_worklist reads a worktree-local store, so already-promoted roots are re-queued as un-translated | [`RussianTranslation/src/pilot/verb_worklist.py:30`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/verb_worklist.py#L30) |
| `C3-3` | **P2** | PLAUSIBLE | is_sanskrit gates on a diacritic, so undiacriticized Sanskrit in {%…%} is sent to the German→Russian translator | [`RussianTranslation/src/compile_translatable.py:110`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/compile_translatable.py#L110) |
| `C3-5` | **P2** | PLAUSIBLE | fix_german_connectives --store rewrites German phrases inside «…» verbatim quotes that its own detector deliberately masks out | [`RussianTranslation/src/pilot/fix_german_connectives.py:122`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/fix_german_connectives.py#L122) |
| `C5-5` | **P2** | PLAUSIBLE | A freshly created promote claim is momentarily empty, and an empty claim file is judged stale — two promoters can hold the store claim at once | [`RussianTranslation/src/promote_lock.py:140`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_lock.py#L140) |
| `C6-03` | **P2** | PLAUSIBLE | Headline human-gold precision + Wilson 95% CI computed as if an equal-allocation stratified sample were i.i.d. | [`RussianTranslation/src/gold_agreement.py:94`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/gold_agreement.py#L94) |
| `C7-6` | **P2** | PLAUSIBLE | export_ontolex tags every exported sense @ru regardless of its actual language — German, English and Sanskrit strings ship as Russian-language literals | [`RussianTranslation/src/export_interop.py:170`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/export_interop.py#L170) |
| `C8-5` | **P2** | PLAUSIBLE | Dependabot auto-merge falls back to an unconditional squash-merge that bypasses every check | [`.github/workflows/dependabot-auto-merge.yml:35`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/dependabot-auto-merge.yml#L35) |
| `C1-2` | **P3** | PLAUSIBLE | watch_upstream never routes `removed` headwords to the stale worklist, and advances layer state past them — a latent notification gap, with no observed trigger in the whole upstream history | [`RussianTranslation/src/pilot/watch_upstream.py:276`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/watch_upstream.py#L276) |
| `C1-7` | **P3** | PLAUSIBLE | A mid-file unclosed <L> silently discards a record, while the same condition at EOF is warned about | [`RussianTranslation/src/pwg_mask.py:130`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_mask.py#L130) |
| `C4-1` | **P3** | PLAUSIBLE | The Lane-C CI card gate's wf_output scope (`gatelogs/`) does not match where the coordinator writes wf_output — a latent scope bug in an unwired Wave-2 stub | [`RussianTranslation/src/pilot/ci_gate_runner.py:86`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/ci_gate_runner.py#L86) |
| `C4-2` | **P3** | PLAUSIBLE | BoundedSupervisor's terminal checkpoint records a consumed-but-uncompleted window as neither completed nor pending — an accounting slip, not a dropped unit | [`RussianTranslation/src/pilot/bounded_supervisor.py:331`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/bounded_supervisor.py#L331) |
| `C8-2` | **P3** | PLAUSIBLE | No ExecStart line in the orchestrator unit carries a `-` prefix, so a non-zero `run-once` skips `record-done` for that tick — real in the unit file, but the unit is deployed nowhere | [`RussianTranslation/deploy/pwg-ru-max-orchestrator.service:12`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/deploy/pwg-ru-max-orchestrator.service#L12) |
| `C8-8` | **P3** | PLAUSIBLE | Published probe log states a retired 30 s ceiling and drops the policy column, destroying the per-row provenance the module mandates | [`RussianTranslation/src/pilot/probe_log.py:352`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/probe_log.py#L352) |

### 4.3 Contested — lenses disagreed, adjudicated here

One lens confirmed and one refuted. The lead's adjudication line for each is below the table; no verdict was picked silently.

| ID | Sev | Status | Defect | Anchor |
|---|---|---|---|---|

### 4.4 Refuted — preserved with the refutation

Kept deliberately. A refuted finding that is deleted gets re-derived by the next reviewer; the refutation is the durable asset.

| ID | Sev | Status | Defect | Anchor |
|---|---|---|---|---|
| `C1-3` | **P1** | REFUTED | `ord` is a positional index into a live upstream file but is persisted as a stable record identity | [`RussianTranslation/src/run_batch.py:161`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/run_batch.py#L161) |
| `C8-1` | **P1** | REFUTED | Orchestrator unit has no TimeoutStartSec: systemd kills a 600 s paid dispatch at the 90 s default | [`RussianTranslation/deploy/pwg-ru-max-orchestrator.service:10`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/deploy/pwg-ru-max-orchestrator.service#L10) |
| `C1-4` | **P2** | REFUTED | The `gloss-langs` durable-metadata API returns only the first of a key1's records; 17,284 records are unreachable | [`RussianTranslation/src/pwg_mask.py:421`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_mask.py#L421) |
| `L-4` | **P2** | REFUTED | 41 modules still resolve sibling repos by the three-levels-up guess that sibling_root.py was written to replace, and 12 of them are on the PWG lane | [`RussianTranslation/src/sibling_root.py:6`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/sibling_root.py#L6) |
| `C2-4` | **P2** | REFUTED | Nominal worklist's verb-exclusion list silently empties outside the main checkout, queueing verbs into the nominal drain | [`RussianTranslation/src/pilot/nominals_worklist.py:85`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/nominals_worklist.py#L85) |
| `C4-4` | **P2** | REFUTED | cloud_window's usage ledger is an unkeyed append — a re-run of the same window double-counts its token/cost telemetry | [`RussianTranslation/src/pilot/cloud_window.py:118`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/cloud_window.py#L118) |
| `L-3` | **P2** | REFUTED | run_batch._pwg_commit() silently records pwg_src_commit='unknown' whenever the run is in a git worktree — the isolation the org's own rules mandate | [`RussianTranslation/src/run_batch.py:62`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/run_batch.py#L62) |
| `C6-04` | **P2** | REFUTED | Provenance 'academic rigor index' denominator drops exactly the cards with no provenance | [`RussianTranslation/src/pilot/evolution_stats.py:204`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/evolution_stats.py#L204) |
| `C6-06` | **P2** | REFUTED | Gold item identity is a positional enumerate index, so re-running the sampler re-binds every human label to a different alignment | [`RussianTranslation/src/gold_sample.py:66`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/gold_sample.py#L66) |
| `C6-07` | **P2** | REFUTED | det_gate passes a card that emitted ZERO senses, and reports coverage 1.0, when the source has <=1 declared sense and no masked spans | [`RussianTranslation/src/pilot/h1210/det_gate.py:102`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/h1210/det_gate.py#L102) |
| `C7-7` | **P2** | REFUTED | The citable TEI/OntoLex export ignores the per-sense `publishable` rights flag it is handed, so a rights-unconfirmed source would ship into the release | [`RussianTranslation/src/export_interop.py:92`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/export_interop.py#L92) |
| `C8-6` | **P2** | REFUTED | Monthly Cologne-drift alert can never open its first issue: an empty gh --jq lookup returns the string "null" | [`.github/workflows/upstream-watch.yml:74`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/upstream-watch.yml#L74) |
| `C4-5` | **P3** | REFUTED | Every coordinator subprocess on the unattended drain path runs with no timeout — the nonstop loop has no watchdog against a wedged child | [`RussianTranslation/src/pilot/max_account_orchestrator.py:189`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/max_account_orchestrator.py#L189) |
| `C4-6` | **P3** | REFUTED | economy_ledger.write_ledger reads the import-time FROZEN_LOG, defeating the lazy --data-root seam it documents two lines above | [`RussianTranslation/src/pilot/economy_ledger.py:316`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/economy_ledger.py#L316) |
| `L-6` | **P3** | REFUTED | Nine promoted rows from autosplit_requeue.topup carry no input identity at all | [`RussianTranslation/src/pilot/autosplit_requeue.py:1`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/autosplit_requeue.py#L1) |
| `C6-02` | **P3** | REFUTED | G5 print gate is unblocked by one print-ready row — REFUTED: that is the documented criterion, and the finding's scale was fabricated | [`RussianTranslation/src/preflight_remaining_gates.py:123`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/preflight_remaining_gates.py#L123) |
| `C7-8` | **P3** | REFUTED | The LOD acceptance gate's "no placeholder example.org IRI" invariant only inspects the object position, so a placeholder namespace on entry subjects passes | [`RussianTranslation/src/lod_acceptance.py:121`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/lod_acceptance.py#L121) |
| `L-8` | **P3** | REFUTED | build_article_site interpolates iast and root into innerHTML unescaped in two places while escaping in four others | [`RussianTranslation/src/pilot/build_article_site.py:880`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_article_site.py#L880) |
| `L-7` | **P3** | REFUTED | coordinator.prepare writes a run artifact into the source tree and it is not gitignored | [`RussianTranslation/src/pilot/window_common.py:45`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_common.py#L45) |
| `C9-01` | **P3** | REFUTED | cohort_clean_rates.py hardcodes the superseded 80% bar — REFUTED: it is a date-frozen evidence deliverable, and 'fixing' it would falsify the measurement the ruling cites | [`RussianTranslation/DECISIONS_PWG_RU_QUALITY_BAR.md:47`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/DECISIONS_PWG_RU_QUALITY_BAR.md#L47) |

## 5. What holds — stated because a review that only lists defects misleads

These are not consolation prizes; each is load-bearing and each was checked, not assumed.

- **[`src/store_write.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/store_write.py)
  is the best-engineered thing in the system.** Four real guarantees — `PromoteClaim`
  across the whole read-guard-write window, `O_EXCL` fsynced per-run backups that refuse to
  overwrite a prior recovery artifact, fsync-then-`os.replace`, LF-only bytes — and each
  one names the incident that motivated it. The T3 findings are cases that did not route
  through it, which is an adoption gap, not a design failure.
- **[`src/store_path.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/store_path.py)
  solves the worktree problem correctly**, and documents the 29 lost promotions that taught
  it. It is the reason T2 is a propagation finding rather than an unknown.
- **[`release/pwg_tm/coverage.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/pwg_tm/coverage.json)
  publishes against its own interest.** It records a **failed** independent gate
  (`serious_error 0.0250 > 0.01`), states that Wave-1 fragments are therefore *not* in the
  four-format green release, and carries `silent_drops: 0` with full exclusion-reason
  counts. That is what honest measurement looks like.
- **Rights handling in the corpus bundle is careful.** Per-record `rights_status`,
  `rights_basis`, `reuse_policy`; grey full-text kept local and gitignored by construction;
  the rights table sourced by path and its row count recorded. All three
  `release/corpus_tm/manifest.json` checksums verify byte-for-byte.
- **The secret-scanning path is tested, not merely present.**
  [`data_migrate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/data_migrate.py)
  plants a credential in a temp tree and asserts the scanner finds it, then asserts a
  mutated clone surfaces as a HASH MISMATCH and a racing writer as a mismatch rather than a
  silent pass.
- **The offline byte-identity control is genuinely executed.** `h1339_offline_bench.py`
  runs with a pinned signature in CI, and the comment above it explains — at length, and
  correctly — why a hash quoted in prose and never re-run is not a control.

## 6. Refuted by the lead, before any lane saw them

Preserved because a refutation that is deleted gets re-derived by the next reviewer.

**The promoted store contains duplicate sense identities with conflicting Russian translations.**

- **Verdict:** REFUTED
- **Evidence:** (key1, subcard, sense_tag) collides on 573 rows, but sense_tag is not the identity key. Adding the German source gives (key1, subcard, sense_tag, de) = 11,598 distinct of 11,603. The 5 residual duplicates form 4 groups (han, vas x3, vid, dah) and in every one the ru text is byte-identical AND equal to the de text -- untranslated structural stubs like '<div n="m">- <ab>Caus.</ab>'. Zero conflicting translations.
- **Kept as:** a bounded P3 redundancy at most; not a data-integrity defect

**The published release checksums do not verify (SHA256SUMS reported mismatches).**

- **Verdict:** REFUTED -- the first probe was wrong, not the data
- **Evidence:** The initial run resolved names against release/fixture/de_edition/, a different build. Excluding fixtures: zero mismatches anywhere. release/corpus_tm/manifest.json's three hashes (public_full.jsonl, public_full.tmx, derived_only.sample.jsonl) all verify byte-for-byte, and release/pwg_tm/SHA256SUMS's canonical.v1.jsonl matches the tracked copy under release/pwg_tm_canonical/ exactly (b9ad8e9ff9...). The remaining 6 checksummed interchange files are gitignored and published only to Zenodo/GitHub Releases, so they are unverifiable from the repo alone -- a stated limitation, not a mismatch.
- **Kept as:** a reproducibility note in the gate packet

**A live API key is committed in the tracked tree.**

- **Verdict:** REFUTED
- **Evidence:** The only matches are synthetic fixtures inside selftests: data_inventory.py:267 ('sk-secret') and data_migrate.py:278 ('sk-abcdefghijklmnopqrstuvwx123456'), both written into a TemporaryDirectory. data_migrate.py:277-280 plants the credential deliberately and asserts secrets_scan() finds it -- the secret-scanning path is tested, not leaking.
- **Kept as:** credit, not a finding

**mark_reconstructed_headwords.py and ru_style_sweep.py rewrite the canonical store without the H2146 promote lock.**

- **Verdict:** REFUTED
- **Evidence:** Both hold PromoteClaim across the backup/replace window -- mark_reconstructed_headwords.py:175-185 and ru_style_sweep.py:349-371. A static 'imports store_write' heuristic missed them because the import is lazy and inside the function. ru_style_sweep additionally re-checks the store sha before os.replace.
- **Kept as:** a caution about the heuristic, not a defect

## 7. Remediation order

Ordered by *what a fix unblocks*, not by severity alone.

1. **Restore the merge gate.** The cross-language parity ledger is stale and CI has been
   red for three pushes; every other fix below lands through that gate. Re-check the four
   SHARED verdicts, `--update-hash` each, and require green before merge.
2. **Re-cut the corrupt published artifact — but fix its gate first.** Making
   `validate_interop` assert `xml:id` uniqueness and parse the Turtle with `rdflib` (already
   a dependency, already used in `lod_acceptance.py`) must precede the re-cut, or the next
   drift is equally invisible.
3. **Close the false-green family (T1).** Each is a small, local, independently testable
   fix, and each one currently converts an unchecked condition into a positive assurance.
4. **Widen the promote claim to cover the read (T3).** Mechanical and low-risk; the correct
   pattern already exists in `store_write.locked_store_rewrite`.
5. **Propagate `sibling_root()` to the remaining 41 callers (T2)**, and add a lint that
   fails a new three-levels-up literal.
6. **Fix the `key1`-as-identity family (T4)** — the largest correctness surface, and the
   one that most needs a human lexicographer's ruling on what the right identity is.
7. **Everything else**, grouped by root cause in the follow-up handoffs.

## 8. Human decisions this review deliberately does not make

- **What a card's printed page should be when its `key1` owns several PWG records.**
  Omitting the scalar field, flagging it ambiguous, or picking a rule are all defensible;
  this is a lexicographic ruling, not a code fix.
- **Which licence the DE edition graph should carry.** The contradiction is a fact; the
  resolution is a rights decision a human should make.
- **Whether the 10,792 backfilled provenance rows should be re-derived or simply annotated
  as unmeasurable.** Re-deriving invents a second guess; annotating admits a permanent gap.
- **Whether the corrupt TEI should be re-cut in place or superseded with a new version and
  a public erratum**, given it is published alongside a DOI.

_Dr. Mārcis Gasūns_
