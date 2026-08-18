# H2889 — gate packet

_Created: 18-08-2026 · Last updated: 18-08-2026_

**Verdict: PARTIAL.**
**Frozen commit:** `af58b3b01836e7e888b066b1cd499c3ee53dc602`
· **Executor:** Opus 5 (`claude-opus-5`) at maximum effort
· **Handoff:** [H2889](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2889-Opus_PWG_pwg-translation-comprehensive-code-review_16.08.26.md)

PARTIAL, not PASS, and the reasons are named in §5 rather than left implicit. Under this
handoff's own rule — *"Missing evidence is INCONCLUSIVE, never PASS"* — a review that
returned 19 mechanism-without-reproduction findings and deviated on one commissioned lens
cannot claim PASS, however much of it is solid.

## 1. Manifest coverage — 100 %

[`H2889_REVIEW_MANIFEST.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2889/H2889_REVIEW_MANIFEST.tsv)

| | Count |
|---|---:|
| First-party Python files enumerated (`ast`, 0 parse errors) | 561 |
| In scope by transitive closure from a proven entrypoint | **361** |
| Out of scope, each with the verdict *no proven live edge* | 200 |
| Non-Python first-party artifacts on a live edge (workflows, units, schemas, prompts) | 49 |
| **Manifest rows** | **610** |
| **Rows with an explicit disposition** | **610 (100 %)** |

No row carries "not looked at". The two dispositions are `reviewed` (410) and
`not-applicable` (200), and every `not-applicable` row names why.

**Coverage is not the same as depth**, and the distinction is recorded rather than blurred.
Manifest coverage is 100 %; reading depth is uneven and each lane's `read_summary` in
[`H2889_FINDINGS.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2889/H2889_FINDINGS.json)
states what it opened and what it did not. The clearest case: contour 6 had 129 in-scope
files and opened roughly 29 of them, and says so.

Three repositories the commission named as candidates — `pwgxml`, `csl-apidev`,
`csl-websanlexicon` — have **no live edge** at the frozen commit and are excluded with that
evidence. Eleven sibling repos do have proven edges and are listed with the first
`file:line` proving each in
[`H2889_RUNTIME_DEPENDENCY_GRAPH_2026-08.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2889/H2889_RUNTIME_DEPENDENCY_GRAPH_2026-08.md).

## 2. Baseline and final gates — no review regressions

Identical command list both times: the offline gate set from
[`.github/workflows/ci.yml`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/ci.yml)
plus `python -m pytest tests -q`, run with `RUNNER_TEMP` pointed at a scratch directory.

| | Baseline (before) | Final (after) |
|---|---|---|
| Commands | 84 | 84 |
| **PASS** | **81** | **81** |
| **FAIL** | **3** | **3** |
| Wall | 554.9 s | 500.4 s |
| `pytest tests -q` | 207 passed, 9 skipped | 207 passed, 9 skipped |

**The same three, and only the same three.** Zero regressions introduced by this review,
which is the point of taking a baseline at all.

| # | Command | Pre-existing? |
|---|---|---|
| 1 | `python src/build_g5_review_sheet.py --selftest` | yes — `csl-pyutil` version drift, finding `L-2` |
| 2 | `python src/pilot/window_selftest.py` | yes — 210/211 subtests pass; the one failure is #3 |
| 3 | `python src/pilot/lang_parity_check.py` | yes — **also RED on GitHub Actions**, finding `L-1`, issue #1799 |

Detail, diagnosis and the CI history: [`H2889_BASELINE_GATES_2026-08.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2889/H2889_BASELINE_GATES_2026-08.md).

## 3. Findings and verification

| | Count |
|---|---:|
| Reported by nine lanes + the lead | **68** |
| **CONFIRMED** | **29** |
| **PLAUSIBLE** (mechanism traced, reproduction not closed) | **19** |
| **REFUTED** (preserved with the refutation) | **20** |
| Contested between lenses, each adjudicated in one written ruling | 14 |
| Final severity | 2 P0 · 13 P1 · 36 P2 · 17 P3 |
| Verifier verdicts collected | **93** |
| Findings short of their verifier quota | **0** |

Design: two independent refute-primed lenses per P0/P1 (correctness; reproduction), one
per P2/P3. Verifiers were instructed that *"I could not prove it wrong"* is PLAUSIBLE,
never CONFIRMED. Ten verifier agents died on connection errors and were **re-dispatched**
rather than their findings being reported unverified.

The pass did real work: nearly a third of what the lanes reported did not survive, one P0
fell to P3, one to P1, one P1 gained a factor-of-300 correction to its blast radius, and
one finding turned out to be two.

## 4. Issues opened

One per coherent root cause, deduplicated against the 30 open issues in the repo before
filing.

| Issue | Covers | Severity |
|---|---|---|
| [#1798](https://github.com/gasyoun/SanskritLexicography/issues/1798) | Both shipped interop artifacts stale + corrupt; G9 gate blind | P0 (`L-9`, `C7-1`, `C7-2`, `C7-3`) |
| [#1799](https://github.com/gasyoun/SanskritLexicography/issues/1799) | CI red on `master`, four stale lang-parity hashes | P1 (`L-1`) |
| [#1800](https://github.com/gasyoun/SanskritLexicography/issues/1800) | Promote claim guards the write, not the read-modify-write | P1 (`C5-1`, `C5-2`, `C5-3`, `C5-4`) |
| [#1801](https://github.com/gasyoun/SanskritLexicography/issues/1801) | `~~h<N>` type confusion → 24.5 % of mappable rows carry the wrong printed column | P1 (`C1-1`) |
| [#1802](https://github.com/gasyoun/SanskritLexicography/issues/1802) | Rights metadata contradicts itself across the DE edition | P1/P2 (`C7-5`, `C7-7`) |
| [#1803](https://github.com/gasyoun/SanskritLexicography/issues/1803) | Nine gates whose PASS means "nothing was checked" | P2/P3 (nine ids) |
| [#1804](https://github.com/gasyoun/SanskritLexicography/issues/1804) | Provenance asserted not measured; 41 modules still guess sibling paths | P2/P3 (`L-3`, `L-4`, `L-5`, `L-6`, `C2-3`, `C2-4`) |

No issue was filed for a PLAUSIBLE or REFUTED finding.

## 5. Residual uncertainty — the reasons this is PARTIAL

1. **19 findings are PLAUSIBLE.** The code trace holds; no verifier reached the failure
   from a live entry point. They are recorded, not claimed as defects, and not filed.
2. **One commissioned lens was run centrally, not per finding.** The commission asked for
   three independent refute-primed lenses on every P0–P2. The third (prior-art /
   current-state) was run **once by the lead across all 68 findings** against the repo's
   FINDINGS / CONTRADICTIONS / DEAD_ENDS / LAUNCH_FUCKUPS / LANG_PARITY registries and the
   Uprava handoff corpus, because it is a corpus search rather than a code trace. This is a
   deviation, recorded as one.
3. **Reading depth is uneven across lanes** (§1). Manifest coverage is complete; per-file
   reading is not, and the per-lane summaries are the honest record.
4. **Six of eight published interchange checksums cannot be verified from the repo.**
   `release/pwg_tm/SHA256SUMS` lists five files; two verify byte-for-byte against tracked
   copies (`canonical.v1.jsonl` = `b9ad8e9ff9…`, `loss_ledger.json`), and three are
   gitignored, published only to Zenodo/GitHub Releases. Same for the three
   `pwg_de_sidecars` entries. **Zero mismatches were found** — but three of the five and
   all three sidecars are unverifiable without fetching the release.
5. **The static closure does not follow dynamic imports**, and data-file edges are proven by
   literal rather than by execution. Neither was observed to matter; absence of observation
   is not proof.
6. **Two lanes and ten verifiers died on connection errors mid-run.** All were re-dispatched
   and all returned; no finding rests on a truncated agent.

## 6. Constraints honoured

| Constraint | Evidence |
|---|---|
| **No paid model/API calls** | Every executed command is a `--selftest` / `--verify` / fixture path or a read-only probe. The gate matrix is the CI list verbatim. |
| **No production mutation** | All work in a linked worktree at `origin/master`; the live store was opened read-only for census. Final `git status` in the worktree shows only this review's own new files. |
| **`csl-orig` read-only** | Read for measurement (123,366 records) only; no correction prepared, no PR to that repo. |
| **No secrets logged** | The two `sk-` strings in the tree are synthetic selftest fixtures; `data_migrate.py` plants one deliberately and asserts the scanner catches it. |
| **Review-only, no production fixes** | This branch carries five documents and no code change. |

## 7. Export-consumer smoke — every published format, real artifacts

| Artifact | Consumer check | Verdict |
|---|---|---|
| `corpus_tm/public_full.jsonl` | parse every line | **PASS** — 2,392 records, 0 unparseable |
| `reverse_index.jsonl` | parse + required keys | **PASS** — 209,319 records |
| `pwg_tm_canonical/canonical.v1.jsonl` | parse every line | **PASS** — 2,392 records |
| `pwg_tm_canonical/priority_5000.jsonl` | parse every line | **PASS** — 5,000 records |
| `corpus_tm/public_full.tmx` | XML well-formed | **PASS** — 2,175 `<tu>` |
| `tei_lex0.xml` | XML well-formed | PASS — 120,173 `<entry>` — **but see #1798: 12,374 duplicate `xml:id`** |
| `ontolex.ttl` | `rdflib` parse | PASS — 649,746 triples — **but 12,374 merged subjects, #1798** |
| `shapes.ttl`, `pwg_de_lexicon_h1350_demo.ttl` | `rdflib` parse | **PASS** — 49 / 20,077 triples |
| `corpus_tm/manifest.json` | recompute all 3 checksums | **PASS** — all three verify byte-for-byte |

That last row is the counterweight worth stating: the corpus bundle is byte-verifiable and
its rights metadata is careful. The failure is specific to the two interop artifacts, not
general to the release.

## 8. Definition of done — status

- [x] Runtime dependency graph, commit-pinned, with evidence for every edge
- [x] Frozen manifest, 100 % dispositioned
- [x] Baseline **and** final gate packets, pre-existing failures separated from regressions
- [x] Comprehensive report + machine-readable confirmed/plausible/refuted findings
- [x] Own-data evidence (11,603-row store census, 123,366-record `pwg.txt`, real release artifacts)
- [x] Export-consumer smoke over every published format
- [x] Independent verification for every P0–P2; quota shortfall **0**
- [x] Owning-repo issues for every confirmed P0–P2, deduplicated by root cause
- [x] Review PR green, no production writes, no paid calls, shared checkout clean
- [ ] **PASS** — withheld; PARTIAL for the six reasons in §5

_Dr. Mārcis Gasūns_
