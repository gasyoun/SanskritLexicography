# PWG→RU pipeline capability audit — 3-account concurrency · per-sense evidence provenance · case-government · per-sense genre (H335)

_Created: 08-07-2026 · Last updated: 09-07-2026 (H397)_

Audit-only pass answering MG's four capability questions of 08-07-2026
([H335](https://github.com/gasyoun/Uprava/blob/main/handoffs/H335-Fable_RussianTranslation_pipeline-capability-audit_08.07.26.md)).
No pipeline behavior changed; the one new file is the deterministic census script
[`src/government_census.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/government_census.py)
(selftest-gated, read-only over the source). Audited by Fable 5 (`claude-fable-5`);
code discovery ran through three read-only Explore subagents (same model); every
load-bearing claim spot-verified against the code by the orchestrating session.
Store numbers measured on the live gitignored `src/pwg_ru_translated.jsonl`
(11,261 rows, 08-07-2026).

| Workstream | Question | Verdict | Effort to close |
|---|---|---|---|
| [W1](#w1--3-account-concurrency-safety) | Is the pipeline safe under 3 concurrent Max accounts? | **MISSING** (unsafe same-clone; per-clone runs safe until merge) | M — protocol is free, hardening ~1 session |
| [W2](#w2--per-sense-evidence-provenance) | "Which senses did Grintser/Kossovich support?" queryable? | **MISSING** (evidence assembled then discarded; gate never ran) | M — deterministic backfill, ~1–2 sessions |
| [W3](#w3--case-government-управление) | How many government markers in PWG; queryable per sense? | **PARTIAL** (schema slot exists, 0 populated; census now done: **3,853 markers**) | S — extractor+backfill ~1 session |
| [W4](#w4--per-sense-genre-attribution) | "Which senses occur in kāvya?" | **PARTIAL — mostly EXISTS** (per-sense Renou state already shipped; literal genre is one join away) | S — join+query ~1 session |

---

## W1 — 3-account concurrency safety

**Verdict: MISSING.** There is **no locking anywhere on the direct production
path**. The only lock in the tree is a `mkdir`-based `DirLock` in
[`src/pilot/coordinator.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/coordinator.py)
(lines 92–129: atomic `os.mkdir` lock dirs `.state.lock`/`.promotion.lock`,
30 s spin, PID-based staleness) — but the documented production loop
([RUN_FREQ_MAX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md),
the `/pwg-drain` skill) calls `gen_opt_harness2.py` → `audit_window.py` →
`requeue_from_audit.py` → `promote_final_cards.py` → `translation_memory.py`
**directly**, bypassing the coordinator entirely. Its PID-based stale-lock logic
is also meaningless across clones/machines, so even opting in does not
coordinate 3 accounts on 3 clones.

### Collision matrix

Classification: **safe** · **LWW** (last-writer-wins loss) · **TORN**
(interleaved/corrupt appends) · **LOCKED** (coordinator-guarded, opt-in only).
"3-same-clone" = three accounts in one working tree; "3-clones" = three
worktrees/clones that later converge on the shared store via git or promote.

| File | Writer | Mode | Name | 3-same-clone | 3-clones |
|---|---|---|---|---|---|
| `src/pwg_ru_translated.jsonl` (THE store) | [`promote_final_cards.py:323-370`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_final_cards.py) | read-modify-rewrite; atomic tmp+`os.replace`; fixed-name `.premerge.bak` | singleton | **LWW** — no lock between guard-read and replace; concurrent promote also overwrites the other's `.bak`, destroying the recovery copy | **LWW at merge** (store is gitignored — no git merge protects it) |
| `translation_memory.<lang>.json` | `translation_memory.py:333` | full rewrite from whole store | singleton/lang | **LWW** (snapshot of indeterminate store state) | regenerable — safe if rebuilt once after merge |
| `translation_memory.frag.<lang>.jsonl` | `:515-518` | read-dedupe-**append** | singleton/lang | **TORN** (Windows appends not atomic) | regenerable |
| `translation_memory.denylist.jsonl` | [`requeue_from_audit.py:71-81`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/requeue_from_audit.py) | bare append | singleton | **TORN** — and reader silently *drops* torn lines (`load_denylist` skips `JSONDecodeError`), so a lost denylist row silently re-enables TM reuse of gate-rejected content | needs union-merge |
| `src/pilot/output/window_status.{json,md}`, `audit_window.report.{json,md}`, `judge_sample.keys.txt` | [`window_reports.py:227-426`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_reports.py) | full rewrite every audit | singleton | **LWW** — 3 accounts auditing 3 windows clobber each other's status | safe (per-clone) |
| `requeue.keys.txt` (+ `.transient`/`.defect`) | `window_reports.py:428-436` | full rewrite | singleton | **LWW + TOCTOU**: `requeue_from_audit.py` reads it back; a concurrent audit rewriting it between write and read requeues the *wrong window's* keys | safe |
| `window_ledger.jsonl` | `window_reports.py:148` | bare append | singleton | **TORN** | needs union-merge |
| `run_pilot_wf.opt2.js` (default `--out` omitted) | [`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py) via `window_common.py:1742` | full rewrite | singleton by default; `--out=…wNN.js` per-window | **LWW** — account B regenerates the harness account A is about to run | safe |
| `wf_output*.json` | operator/session-written (harness JS has no `fs` write) | n/a | operator-chosen | safe **iff** per-window names are used (discipline, not code) | safe |
| `verb_batch_worklist.json` / `nominal_batch_worklist.json` | [`verb_worklist.py:106`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/verb_worklist.py) / [`nominals_worklist.py:280`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/nominals_worklist.py) | full rewrite | singleton | **LWW** (advisory — regenerable) | safe |
| `layer_version_log.jsonl`, `failures/auto_failures.jsonl` | `layer_versions.py:176` / `failure_capture.py:84` | bare append | singleton | **TORN** | needs union-merge |
| coordinator `state.json`, `dashboard.json`, `artifacts/<lease>/` | `coordinator.py:158-600` | tmp+replace under `DirLock`; per-lease artifact dirs | per-lease | **LOCKED** (single machine only) | lock does not span clones |
| `LAUNCH_FUCKUPS.md`, `.ai_state.md`, `RUN_LOG.md` | human/session-edited markdown | git-tracked | singleton | git conflict = visible, recoverable | safe (git merges) |

**What breaks first:** not the exotic paths — the **first shared audit**. Two
accounts auditing in one clone cross-contaminate `window_status.json` and the
requeue TOCTOU can requeue another window's keys within minutes. The **worst**
break is two `promote_final_cards.py --merge` runs racing: last writer silently
discards the first writer's promoted rows *and* both `.premerge.bak` copies
point at the same name, so the loss is unrecoverable except from `wf_output`
re-promotion.

### Recommended 3-account operating protocol (no code changes needed)

1. **One worktree per account, never a shared clone.** All state paths are
   repo-relative, so per-clone runs are disk-isolated for free. (This is
   already the org's worktree-isolation discipline — extend it from "per
   handoff" to "per account".)
2. **Shard by root, via the worklist, before starting.** Partition
   `verb_worklist.py --top N` output into 3 disjoint slices (e.g. round-robin
   by rank) and pin each account to its slice in its session brief. Root-level
   sharding guarantees disjoint rootmaps, inputs, TM *card* keys, and requeue
   sets. Verified limitation: the **fragment TM** is content-addressed across
   roots (a fragment shared byte-for-byte between a root and a derived noun is
   deliberately reused), so two accounts *can* both add the same fsha — but
   `build_frags` dedupes on read, so cross-account duplication is benign
   **only if** the sidecars are rebuilt by one owner (rule 3).
3. **Single-promoter rule.** Only ONE designated account (or a final
   consolidation session) runs `promote_final_cards.py --merge` and the TM
   rebuilds; the other two stop at "audited clean, `wf_output.<window>.json`
   saved + committed pointer in RUN_LOG". Promotion is cheap and deterministic
   from `wf_output` files, so serializing it costs minutes and removes the
   worst LWW hazard entirely.
4. **≤3-wide stays GLOBAL, not per-account.** The Slice-D collapse (117
   transient nulls at ~18 concurrent root Workflows) is a *server-side* cliff;
   3 accounts × 3-wide = 9 concurrent root harnesses ≈ ~100+ peak agents is in
   the danger band. Under 3 accounts, each runs **1 root at a time** (3 total
   in flight org-wide), and any single account may go 3-wide only when the
   other two are idle.
5. **Per-window `--out` and `wf_output.<window>.json` names always** (already
   the `no_pwg_scale_plan.py` convention) — never the bare defaults.

### Minimal hardening list (if/when 3-account production becomes routine)

- **H-1 (highest value): claim files for promotion.** An `O_EXCL` claim
  (`store.promote.lock`, mint-style create + PID+host+timestamp payload) around
  the read-guard-write window in `promote_final_cards.py`, plus a unique
  timestamped `.bak` name (`.premerge.<UTC>.bak`). ~30 lines, kills the only
  unrecoverable-loss path.
- **H-2: per-window output namespacing.** `audit_window.py --window-tag <tag>`
  routing `window_status`/reports/requeue to `output/<tag>/…` (default `tag` =
  root name). Removes the same-clone clobber class wholesale; `requeue_from_audit`
  reads from the same tag dir (closes the TOCTOU).
- **H-3: append hygiene.** Write JSONL appends as a single `os.write` of one
  encoded line (or take H-1's claim file); teach `load_denylist` to WARN on a
  torn line instead of silently skipping — a silently dropped denylist row is
  a correctness hole even single-account (crash mid-append).
- **H-4 (optional): route 3-account runs through the coordinator** and extend
  `DirLock` staleness to host+PID; per-lease `artifacts/<id>/` isolation
  already exists there. Bigger lift; only worth it if the account count grows
  past 3.

Cross-checked against the H214 tree-intermix incident and
`feedback_multiagent_worktree_contention` (org memory): both are *session*-level
collisions this protocol subsumes; H189's cost gates and the TM denylist rule
are unaffected by sharding.

---

## W2 — per-sense evidence provenance

**Verdict: MISSING** — and cheaper to close than assumed, because the evidence
assembly is fully deterministic and local.

### Ground truth (verified 08-07-2026)

- [`corpus_gate.build_card`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/corpus_gate.py)
  (lines 360–371) assembles **seven evidence lanes**, all joined on
  `form_key(slp1)`:

  | Lane | Sources (entries) | Card field |
  |---|---|---|
  | INDEP (correctness authorities) | `koch` 29,177 · `kna` 3,271 · `fri` 8,151 · `smirnov` 3,547 | `independent_glosses` |
  | REF (human PWG→RU reference) | `kow` 13,488 | `kow_reference` |
  | SPECIALIST (evidence-only, unpublishable) | `grin12` 457 · `grin3` 206 (Гринцер, via [`build_glossaries.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_glossaries.py)) | `specialist_glosses` |
  | SENSE (Hindi disambiguation) | `apte_hi` 111,235 · `vedic_rituals_hi` 6,166 | `hindi_sense` |
  | Kosha synonyms | `kosha_syn` 88,839 | `skd_vcp_synonyms` |
  | Botanical | `meulenbeld_plants` 453 | `latin_binomials` |
  | Corpus | SamudraManthanam `web/corpus.db` (read-only FTS) | `corpus_examples` |

  (The prompt's "пять словников" = 4 INDEP + KOW.)
- **The stage-4 gate has never run.** `pwg_ru_prompts/4_korpus_proverka.txt`
  says so explicitly («Запуск ещё НЕ выполнялся»); `build_card` has no caller
  outside corpus_gate's own CLI. The verdict schema
  (`correctness/matched_source/corroborated_by/…`) exists only in the prompt.
- **0 of 11,261 store rows** carry `evidence`, `government`, `labels`, `renou`,
  or `renou_oldest`. The store row (one row per sense,
  [`promote_final_cards.rows_for`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_final_cards.py)
  lines 156–190) has 15 top-level fields; no evidence lane of any kind. A
  legacy `attested:[{source,code,gloss,publishable}]` field existed in the
  superseded `run_batch.py` path — the *shape* is prior art, the data is gone.
- **Re-assembly is deterministic, LLM-free, and offline** from `key1` alone:
  `build_card` reads only the local `*.jsonl` gate sources + `corpus.db`.
  `corpus_gate.py lookup <key1>` already prints every lane for one key — the
  natural entry point.

### Spec — `evidence` per sense

**Schema** (new optional array on `$defs.sense` in
[`schemas/pwg_ru_final_card.schema.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/schemas/pwg_ru_final_card.schema.json)
+ the same field on flat store rows):

```json
"evidence": [
  {"source": "grin12",          // koch|kna|fri|smirnov|kow|grin12|grin3|
                                 //  apte_hi|vedic_rituals_hi|kosha_syn|
                                 //  meulenbeld|corpus|leonov (reserved)
   "relation": "supports",      // supports|provides|contradicts|silent
   "gloss_ref": "падма-…",      // the matched gloss / synonym / passage id
   "match": "lemma"}            // lemma|stem (SENSE lane matches on both)
]
```

- `relation` semantics: `provides` = source has this exact equivalent;
  `supports` = head-token overlap with the sense's `ru` above the gate's
  Jaccard threshold (reuse `corpus_gate.heuristic`, threshold 0.5);
  `contradicts` = source has glosses for the lemma, none overlapping any
  sense; `silent` = lemma absent (record once per lemma, not per sense, to
  avoid 7× row bloat — representable as a lemma-level `evidence_summary`).
- **Population**: a new deterministic `annotate_evidence.py` (sibling of
  `annotate_renou.py`): stream store rows → `build_card(key1)` → per-lane
  match against the row's `ru`/`de` → write sidecar or in-place field. Zero
  LLM. The per-sense supports/contradicts split IS a heuristic (token
  overlap) — label it as such in the field docs; the LLM-judged
  `relation` upgrade is exactly what the never-run 4_korpus gate would add,
  and slots into the same field without schema change.
- **Retrofit vs forward-only — recommendation: RETROFIT ALL 11,261 rows.**
  It is a pure offline join (~minutes of compute), no re-translation, no
  Workflow spend. Forward-only would leave the already-translated 46 roots +
  nominal windows permanently unqueryable for no saving. (Parked as `@DECIDE`
  since MG owns the schema-shape call; see the fork table at the end.)
- **Query layer** — one CLI answers MG's literal questions:
  `python src/annotation_report.py <key1>[~~subcard[#sense_tag]]` → everything
  known about the lemma/subcard/sense (translation fields, layer, provenance,
  evidence lanes, government, renou, genres);
  `python src/annotation_report.py --by-source grin12 --relation supports`
  → all senses Grintser supported. Reads store + sidecars only.
- **Leonov**: reserve `source: "leonov"` now (777-note Sundarakāṇḍa apparatus,
  org memory `project_sundara_commentary_apparatus`); it becomes a lane only
  when that apparatus ships as a machine-usable glossary — do not build.

### W2 retrofit — EXECUTED 08-07-2026 (H337)

**Verdict now: DELIVERED.** [`src/annotate_evidence.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/annotate_evidence.py)
(deterministic, LLM-free) backfilled all **11,261** store rows (145 distinct
lemmas/roots currently translated); [`src/annotation_report.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/annotation_report.py)
answers MG's queries. Schema (D1): optional `evidence[]` on `$defs.sense` +
lemma-level `evidence_summary` on `$defs.card` ([`schemas/pwg_ru_final_card.schema.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/schemas/pwg_ru_final_card.schema.json)).
**2,239 rows (19.9%) carry ≥1 per-sense evidence entry.**

Per-source tally (provides/supports = sense-level; contradicts/silent/present =
lemma-level over the 145 lemmas); the annotation is deterministic code (no model
tier), run by Opus 4.8 (`claude-opus-4-8`):

| source | provides | supports | contradicts | silent | present |
|---|--:|--:|--:|--:|--:|
| koch | 143 | 560 | 14 | 79 | 0 |
| kna | 824 | 494 | 9 | 89 | 0 |
| fri | 23 | 15 | 10 | 126 | 0 |
| smirnov | 530 | 489 | 4 | 103 | 0 |
| kow | 202 | 359 | 9 | 116 | 0 |
| grin12 | 0 | 0 | 1 | 144 | 0 |
| grin3 | 0 | 0 | 0 | 145 | 0 |
| apte_hi | 0 | 0 | 0 | 60 | 85 |
| vedic_rituals_hi | 0 | 0 | 0 | 140 | 5 |
| kosha_syn | 0 | 0 | 0 | 114 | 31 |
| meulenbeld | 0 | 0 | 0 | 144 | 1 |
| corpus | 0 | 0 | 0 | 53 | 92 |

**Honest caveat on the Grintser query.** MG's literal question ("which senses did
Grintser support") is now *answerable* but currently *near-empty*: the store today
holds 145 verb-roots + nominal windows, while the Гринцер glossaries (grin12/grin3,
457+206 entries) are **Rāmāyaṇa proper-noun** vocabularies — silent for ~all
current-store roots (grin12 hits 1 lemma, grin3 hits 0). The machinery is in place
and populates as name-lemmas/nominals are translated; the near-empty result faithfully
reflects the current store content, not a defect. `silent` deliberately folds "absent"
together with "present but no usable Russian meaning gloss" (Smirnov citation-lists,
Kossovich bare transliteration); a source is marked `contradicts` only when it carries
a real Russian gloss overlapping no sense — avoiding false-disagreement claims.

### W2 extension — koch `см. X` cross-reference resolution — EXECUTED 09-07-2026 (H397)

**Verdict: DELIVERED.** H337 measured koch (Кочергина) at the whole-dictionary level:
**4,048 / 29,177 (13.9%)** entries carry no usable Russian meaning gloss, and
**3,472 of those are bare `см. X` cross-references** (a redirect with no meaning of
its own — `-aSrika` -> "см. अश्रि अश्रिक -aśrika" = "see aśri"), classified `silent`
because the redirect target's real meaning lives under a *different* headword.
[`src/koch_xref.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/koch_xref.py)
resolves the pointer instead of reporting silence: ~94% of koch entries open with
their own Devanagari headword immediately followed by `/iast/`
(`रूपधारिन् /rūpa-dhārin/ ...`) — harvested across all of koch.jsonl, that
self-describing prefix doubles as a Devanagari → SLP1 crosswalk with no external
transliterator needed (reuses koch's own data). A `см. X` target's Devanagari token
is looked up in that crosswalk and joined back into koch's own key1 index for the
resolved gloss, chain-safe up to 2 hops with a visited-set cycle guard; unresolvable
pointers are left untouched (still `silent` — never fabricated).

**koch.jsonl-level resolution** (`python src/koch_xref.py --report`):

| | count | % of bare xrefs |
|---|--:|--:|
| koch entries | 29,177 | — |
| Devanagari head crosswalk (collisions: 4, first-wins) | 27,447 | — |
| bare `см. X` xrefs | 3,472 | 100% |
| **resolved** | **3,204** | **92.3%** |
| unresolved (stay `silent`) | 268 | 7.7% |

Target was ≥2,500/3,471 (H397 handoff stop condition) — met at 92.3%.

`annotate_evidence.py`'s `gather()` calls `resolve_koch_lane()` on the koch lane
before `best_relation`/`source_meaning_tokens` run (`--no-resolve-xref` reproduces
H337 exactly). Store-level backfill re-run (145 lemmas currently translated — only
some hold a koch xref, so the store-level lift is smaller than the dictionary-wide
92.3%, but real):

| source | provides (before→after) | supports (before→after) | contradicts (before→after) | silent (before→after) |
|---|--:|--:|--:|--:|
| koch | 143 → 155 (+12) | 560 → 578 (+18) | 14 → 17 (+3) | 79 → 74 (−5) |

All other lanes (kna/fri/smirnov/kow/grin12/grin3/apte_hi/vedic_rituals_hi/kosha_syn/meulenbeld/corpus)
unchanged — H397 touches only the koch lane. `rows with >=1 evidence` rose
2,239 → 2,269 (+30, 19.9% → 20.1%). Resolved glosses carry a `«см.→» ` provenance
prefix in `gloss_ref` so the annotation report shows they came from a redirect, not
a direct koch gloss. Spot-checked 20 randomly-sampled resolved xrefs (`random.seed(42)`
over the 3,204): all 20 targets matched the redirect's stated Devanagari headword with
no fabricated meaning (e.g. `चञ्चू /cañcū/ см. चञ्चु` → `चञ्चु /cañcu/ f. клюв- нос`;
`वेश्या /veśyā/ см. वेशवधू` → `वेशवधू /veśa-vadhū/ f. 1) любовница 2) куртизанка`).
Annotated by Sonnet 5 (`claude-sonnet-5`). Pinned by
`test_koch_xref_resolution` (`koch_xref.py`'s own pure-function `--selftest`, no
koch.jsonl file IO so it runs in CI). LANG_PARITY: `koch_xref_resolution_h397`,
INTENTIONAL-DIVERGENCE (koch is Sanskrit→Russian only, same basis as
`evidence_retrofit_annotate_h337`).

---

## W3 — case-government (управление)

**Verdict: PARTIAL.** The schema slot `government` exists
(`$defs.sense.government`, schema lines 117–161) — **0 of 11,261 rows populate
it**, nothing extracts it, no prompt rule mentions it, no query reads it. The
phenomenon is now counted (below); extraction is deterministic.

### W3(a) — census of the phenomenon in PWG (the substantive table)

Produced by [`src/government_census.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/government_census.py)
on raw `csl-orig/v02/pwg/pwg.txt` (csl-orig HEAD `78cbb257` baseline; never
masked skeletons), 08-07-2026, Fable 5 (`claude-fable-5`) authoring the
deterministic script; numbers are exact regex counts, not model output.
Marker = parenthesized case group `(<ab>loc.</ab>)` /
`(<ab>loc.</ab> und <ab>gen.</ab>)` or prose `mit (dem/der) <ab>case</ab>`;
`<ls>` spans excluded before matching.

| metric | value |
|---|---|
| PWG entries scanned | 123,366 |
| sense units scanned | 288,991 |
| **government markers, total occurrences** | **3,853** |
| … parenthesized, single case (the `snih (loc.)` shape) | 2,309 |
| … parenthesized, case **variation** (`loc. und gen.` / `oder`) | 40 |
| … prose `mit <ab>case</ab>` phrases | 1,504 |
| (parenthesized nom./voc. — citation-form notes, segregated) | 68 |
| **entries with ≥1 government marker** | **1,476** |
| **sense units with ≥1 government marker** | **3,222** |

Parenthesized single-case distribution: acc 1,102 · loc 385 · instr 270 ·
gen 245 · abl 190 · dat 117. Variation groups (40): acc+loc 12 · dat+loc 6 ·
instr+gen 3 · loc+gen 2 (incl. `snih`) · …; connector `oder` ≈ `und`.
Mit-phrase distribution: acc 635 · gen 318 · loc 197 · instr 125 · abl 120 ·
dat 108. By POS (entry-level): verb 417 of 2,971 root entries (14.0%) ·
adj 327 · nominal 241 · indecl 64 · unclassifiable-head 427. The top
marker-bearing entries are exactly the giant roots: `sTA` 113 · `yuj` 88 ·
`vart` 68 · `i` 58 · `gam`/`BU` 42.

**Direct answer to MG:** «сколько таких помет в PWG» — **≈3,853 explicit
government markers, on ≈3,222 senses in ≈1,476 entries**; of those, the strict
`snih`-shaped parenthesized class is 2,349 (2,309 single + 40 variation).
These are a deterministic **floor**: prose statements without a case
abbreviation (e.g. "mit abl. instr. oder gen." counts its first case only —
see caveats) are undercounted, never overcounted.

**Live-store backfill surface (measured):** 510 of 11,261 rows carry ≥1 marker
in their `de` field (619 occurrences). The Russian side preserves all of a
row's markers in only 375 rows (mit-phrases get translated into prose) — so
**backfill must parse `de`, never `ru`**.

### W3(c) — validation (`/spot-check-sample` protocol)

- **Sample**: the `snih` card + 30 hits drawn from all 3,853 with
  `random.seed(335)` (deterministic; population = census TSV minus the
  segregated nongov class). Method: for each hit, read ±130 chars of raw
  source context and judge whether the marker genuinely states case government.
- **`snih`**: both reference shapes caught exactly — `(<ab>loc.</ab>)` on
  sense 2 ("sich heften auf") and `(<ab>loc.</ab> und <ab>gen.</ab>)`
  ("Zuneigung empfinden zu"), unit `div2.s1`, kind `paren-single` +
  `paren-variation loc+gen`.
- **Result: 30/30 genuine government markers** (verbs: "begehren mit dem acc."
  kāṅkṣ; "wohnen in, mit loc." vas; "Jmd (gen.) Stand halten" sthā; adjectives
  governing gen.: samadhura, paurvārdha; numeral zaṣṭi mit gen.; indeclinables:
  pṛthak mit abl.). Zero false positives in the sample.
- **Two systematic caveats** (documented, deterministic):
  1. *Attribution altitude*: markers inside `<div n="p">` prefix blocks attach
     to the prefixed verb (e.g. `vyati-ruh` mit acc. under `ruh`), and a few to
     a subordinate lemma inside the article (`agre` mit gen. under `sTA`). The
     pipeline's sub-card split is already per-prefix, so store-level backfill
     inherits correct attribution for free; the raw-source census reports at
     entry level.
  2. *Multi-case continuation undercount*: `mit <ab>abl.</ab> <ab>instr.</ab>
     oder <ab>gen.</ab>` (pṛthak) is counted as one abl mit-phrase — the
     continuation cases are dropped. Affects prose phrases only, not the
     parenthesized class.

### W3(b) — wire-up spec

1. **Extraction is deterministic, never model-invented**: reuse the census
   regexes as `extract_government(de_text) -> [{cases:[…], variation:bool,
   connector:'und'|'oder'|None, kind:'paren'|'mit', span}]`. Single shared
   helper consumed by backfill + prompt-gate.
2. **Backfill existing rows**: `annotate_government.py` streams the store,
   parses each row's `de`, writes `government` (schema slot, currently a free
   string — recommend structuring as the extractor's output list serialized,
   or tightening the schema to an object; `@DECIDE` on shape below). 510 rows
   populate immediately; no LLM, no re-translation.
3. **Future windows**: add one prompt HARD-RULE line ("copy the parenthesized
   case abbreviation into `government` verbatim; never invent one") + a free
   audit gate: extractor(de) vs extractor(ru-or-field) mismatch ⇒ flag (same
   class as the markup-fidelity gate — cheap, deterministic).
4. **Query layer** (folds into `annotation_report.py`, W2):
   - all senses requiring loc.: filter `government.cases ⊇ [loc] ∧ ¬variation`;
   - senses allowing variation: `variation == true` (the 40 + future rows);
   - **verbs never governing gen.**: aggregate over each verb's senses —
     `layer=='pwg' ∧ pos=='verb'`, group by `key1`, keep roots where no sense's
     `government.cases` contains `gen` AND ≥1 sense carries any marker (the
     "AND attested" clause matters: a verb with zero markers is *unknown*, not
     "never governs gen." — the report must keep the two answers separate).

---

## W4 — per-sense genre attribution

**Verdict: PARTIAL — mostly EXISTS.** This is the pleasant surprise of the
audit: the per-sense citation→work→era machinery **already shipped**, and MG's
kāvya query needs one join plus a query command, not a build.

### What already exists (don't rebuild)

- [`src/ls_source_map.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_source_map.json)
  — 45 PWG-cited works, each with `genre` (25 curated labels: "Kāvya — kathā"
  for Kathās., "Kāvya — Mahākāvya (Kālidāsa)" for Ragh., "Veda — Saṃhitā" for
  ṚV., …), `period`, `renou` (I–V), signed `date`, `corpus_works` (DCS slugs).
  **Coverage: the 45 works account for ~559k of PWG's 801,788 `<ls>`
  occurrences (~70%)**; the long tail of other sigla falls through untagged.
- [`src/renou.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou.py) +
  [`src/annotate_renou.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/annotate_renou.py)
  — already write **per-sense** `renou` (multi-label I–V) and `renou_oldest`
  (state of the earliest-dated citation) by parsing each sense's own `<ls>`
  sigla. [`src/sense_stratum.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/sense_stratum.py)
  emits the same per-sense era feed straight from raw PWG
  (`pwg_sense_stratum.jsonl`: `renou_oldest/renou_youngest/stratum_label/
  date_min/date_max/n_dated_citations`).
- Senses retain their `<ls>` markup **verbatim** in the store (`sense.german`
  / flat-row `de`), so per-sense work lists derive from the store alone —
  `annotate_renou.sense_text()` is the working precedent.
- The per-LEMMA DCS axis ([`build_dcs_freq_dims.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_dcs_freq_dims.py) /
  [`annotate_dcs_freq.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/annotate_dcs_freq.py))
  is a **different, frequency-weighted lane**: ~22 register codes + 5-era
  rollup per lemma from the DCS corpus, via VisualDCS
  `dcs_texts_clean.json` (288 texts, 18 genre labels) crosswalked by
  `build_dcs_renou.py`. Known caveat re-confirmed
  ([CODE_REVIEW_2026-07-04.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CODE_REVIEW_2026-07-04.md) line 57):
  silent lemma loss on genre join-key miss at `build_dcs_freq_dims.py:133`.

### The gap and its spec

What's missing is only the **literal genre label per sense** and the query:

1. `annotate_genres.py` (sibling of `annotate_renou.py`, ~an afternoon):
   per sense, `genres = sorted({ls_source_map[siglum].genre for siglum in
   keys_in_text(sense)})` — reuse `renou.keys_in_text` verbatim for siglum
   normalization. Optionally also a coarse rollup (`kavya/veda/sastra/purana/
   epic/kosha`) since MG's question is at the coarse level.
2. Second lane, clearly labeled: the DCS per-lemma register vector as
   `dcs_registers` (frequency-weighted, corpus-attested) — never merged into
   the citation-derived `genres`, because the two answer different questions
   ("PWG cites this sense from kāvya" vs "the lemma is corpus-frequent in
   kāvya"). Fix-or-log the silent join-key loss before trusting lane 2.
3. Queries (into `annotation_report.py`): "all senses attested in kāvya"
   (`any(g.startswith('Kāvya') for g in genres)`); the converse "senses
   attested ONLY in veda" (`genres ≠ ∅ ∧ all(g.startswith('Veda'))` — again
   keeping *no-citation/unmapped-citation* senses as "unknown", never "only").
4. Coverage growth is data work, not code: extending `ls_source_map.json`
   beyond 45 works (next candidates by citation mass are visible in the
   census TSV / `pwg_sources.py`). Each added work lifts per-sense coverage
   mechanically.

**Genre taxonomy — genuine fork (`@DECIDE`, recommendation attached):** three
vocabularies exist (25-label curated ls_source_map · 18-label DCS · ~22
register codes). **Recommendation:** keep `ls_source_map`'s 25 curated labels
as the canonical per-sense vocabulary (they are already hierarchical —
"Kāvya — kathā" prefix-matches to coarse kāvya), keep DCS labels inside the
`dcs_registers` lane untranslated, and never invent a fourth taxonomy;
`build_dcs_renou.GENRE_RENOU` remains the only crosswalk.

---

## Forks parked for MG (`@DECIDE`) — with recommendations

| # | Fork | Recommendation |
|---|---|---|
| 1 | **Evidence schema shape** (W2): sidecar file vs in-store field; `silent` per-lemma vs per-sense | in-store optional field + lemma-level `evidence_summary` for silence; sidecar only if store size becomes an issue |
| 2 | **Retrofit vs forward-only** (W2, W3): backfill the 11,261 existing rows? | RETROFIT — both backfills are deterministic offline joins, no LLM/Workflow spend |
| 3 | **Genre taxonomy** (W4): whose labels are canonical per-sense? | `ls_source_map` 25 curated labels canonical; DCS-18 stays in its own lane |
| 4 | **`government` field shape** (W3): free string (current schema) vs structured object | structured (`cases[]/variation/connector/kind`) — the queries in W3(b)4 need it |

## Follow-up handoffs

Minted this pass (each MG-independent except where its `@DECIDE` is noted
inside): W1 hardening H-1..H-3 · W2 evidence retrofitter + `annotation_report`
· W3 government extractor + backfill + prompt rule · W4 genre join + queries.
See the registry rows in
[Uprava/handoffs/README.md](https://github.com/gasyoun/Uprava/blob/main/handoffs/README.md)
for the starter lines.

## W5 — LLM→Python migration surface (which stages can shed the model)

Added 09-07-2026 (Opus 4.8, `claude-opus-4-8`) answering "what LLM work here can
become deterministic Python?" The pipeline already runs a strong Python floor —
masking/unmasking
([`src/pwg_mask.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_mask.py)),
the markup-fidelity gate
([`src/audit_translation.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/audit_translation.py)),
and the LLM-free evidence/government joins (W2/W3). The question is where the
model is still doing work code could do.

### Measured, not asserted — the Stage-4 claim was tested and largely fails

A first pass ranked **Stage 4 (corpus/terminology check,
[`4_korpus_proverka.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru_prompts/4_korpus_proverka.txt))**
as the biggest Python win, on the theory that its verdict is re-deriving
overlaps
[`src/corpus_gate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/corpus_gate.py)
already computes. That is **wrong**, for two reasons:

1. **No ground truth exists.** Stage 4 has *never been run* — its header says
   *"Запуск ещё НЕ выполнялся"* and there are zero stage-4 verdict files on disk.
   So the requested "how often does `corpus_gate` agree with the Opus verdict?"
   has nothing to compare against.

2. **The deterministic precheck under-fires massively.** Running
   `corpus_gate.deterministic_precheck` over the live store
   (`src/pwg_ru_translated.jsonl`, 11,261 rows / 145 a-section lemmas):

   | precheck route | rows | share | destination |
   |---|---|---|---|
   | `pass` (Python auto-decides) | 669 | **5.9%** | no LLM |
   | `review` (has gloss, low overlap) | 8,560 | 76.0% | → LLM |
   | `no-check` (no independent gloss) | 2,032 | 18.0% | → LLM |

   The `review` bucket's head-term overlap is **mean 0.04, median 0.00** against a
   0.50 threshold — i.e. an independent Russian gloss usually exists but shares
   almost no surface tokens with our translation. The reason is intrinsic, not a
   threshold bug: even **two agreeing human dictionaries** on the same headword
   clear Jaccard ≥ 0.6 in only ~5% of pairs and sit at ≈0 overlap 84% of the time
   (38 dict pairs over the store keys — thin, but the direction matches
   `corpus_gate`'s own docstring note *"low overlap is the norm even between
   agreeing human dictionaries"*). Synonymy, morphology, and differentia phrasing
   defeat token overlap. **Stage 4's verdict is irreducibly synonym-aware — it
   stays LLM.** Only ~6% is safely auto-decidable now; lemmatization (Vidyut /
   pymorphy) + thesaurus expansion might lift that, but not to a majority.

### What genuinely can shed the model (format & structure, not meaning)

These win because they check *invariants* — anchor counts, tag membership, set
diffs — never lexical agreement, so the overlap problem above does not apply:

| Candidate | Move | Why it works where Stage 4 didn't |
|---|---|---|
| **Stage 2 mechanical criteria** ([`2_qa_sudya_opus.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru_prompts/2_qa_sudya_opus.txt)) | Extend `audit_translation.py` to the full `{Tn}`-anchor count/order + no-unmasking + `<ab>`-token-intact check and run it as a **blocking pre-gate**; strip those criteria from the judge rubric | The prompt already declares these *"НЕ должно влиять на вердикт"* — they are deterministic invariants the judge is wastefully re-checking. Removes a failure class from the LLM and shrinks tokens; enables dropping to one judge on the Python-passed set |
| **Stage 5/6 structural guards** (no fabricated sense/tag; tags match raw; no duplicate senses; `[new]` only if absent from earlier layer) | Python **set-diff** of output sense/tag set vs the raw German sense/tag set, as a pre/post gate | Structure membership is decidable from the raw card; leaves the judge only *semantic* fabrication (meaning present but wrong) |
| **TM / near-dup reuse** ([`src/pilot/translation_memory.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/translation_memory.py)) | Serve byte-identical / trivially-normalized source cards from TM with **no LLM call** — dedup before spend | Pure string identity; measure the freq-run dup rate to size the win |

**Irreducibly LLM** (cannot be Python): the DE/EN/FR→RU gloss translation and
Apresjan synonym discrimination (Stages 1/3/5/6), the Stage-4 terminology
verdict (measured above), and the semantic half of the Stage-2 judge on the
format-clean residue.

**Re-ranked recommendation:** do the Stage-2 mechanical pre-gate and the
Stage-5/6 structural set-diff first — they are deterministic by construction.
Do **not** build a deterministic Stage-4 verdict; if Stage 4 is built at all,
build it LLM-first with `corpus_gate` supplying evidence, and only auto-accept
the ~6% high-overlap tail.

### BUILT — Stage-2 mechanical pre-gate (H405, 09-07-2026)

[`src/stage2_pregate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/stage2_pregate.py)
implements the first recommendation. Given a `(de, ru)` card pair it hard-fails
the format invariants the judge prompt already declares must not affect the
verdict — untranslatable-span preservation (LS/SAN/AB/IS/LEX/LANG, category
regexes kept in sync with `pwg_mask.PAIRED` by `--selftest`), `{Tn}` anchor
multiset equality, stranded/never-restored `{Tn}`, unmask-leak — and emits
`NO-RUSSIAN` as a **soft warning** (not a block), because a `{%…%}`-with-no-Cyrillic
card is as often a form-citation apparatus stub (`Mit {%paripra%}, <ls>…</ls>`)
as a real untranslated defect. Failed cards are requeued, never judged; the
judge rubric can then drop the mechanical criteria. Language-agnostic → **SHARED**
in [LANG_PARITY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md)
(`stage2_mechanical_pregate_h405`); pinned by an 11-case `--selftest`.

Measured over the live store (`src/pwg_ru_translated.jsonl`, 11,261 rows,
09-07-2026, Opus 4.8 `claude-opus-4-8`):

| gate outcome | cards | share | destination |
|---|---|---|---|
| CLEAN | 11,230 | 99.72% | → judge |
| WARN (`NO-RUSSIAN`) | 20 | 0.18% | → judge, flagged |
| **FAIL (hard)** | **11** | **0.10%** | requeue — never judged |

Hard-failure breakdown: `AB-LOSS` 6, `SAN-LOSS` 4, `STRANDED-ANCHOR` 2, `LS-LOSS`
1 (a card may trip several), concentrated on giant verb-root entries (`banD`,
`dA`, `mA`, `paS`, `pat`) plus 2 real mask-restore bugs (a `{T196}`/`{T235}` left
stranded in already-promoted output). The headline value is **not** cutting judge
volume — the merged pipeline is 99.7% clean, so nearly everything still reaches
the judge — it is (a) a **cheaper, correct-by-construction rubric** (the judge no
longer re-checks or mis-checks format) and (b) a **deterministic defect catch**
that surfaced 13 genuine format defects in supposedly-promoted data on its first
run.

**Wired (09-07-2026).** `stage2_pregate.py` gained a `--wf <wf_output.json>`
window-gate mode (emits `FLAGGED_JSON` of hard fails over the same
`.raw.txt`/`.merged.md` file pairs the fidelity gate reads) and is registered in
[`src/pilot/audit_window.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py)'s
gate list as `stage2_mechanical`, so a hard-failed card now joins the window
requeue. The mechanical-criteria block was stripped from both judge prompts
([`2_qa_sudya_opus.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru_prompts/2_qa_sudya_opus.txt)
and its YandexGPT twin) — replaced with a note that the pre-gate guarantees
anchor/markup integrity, so the judge rules only on semantics (`anchors` kept
as an emergency backstop). The **EN** auditor
([`audit_window_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window_en.py))
audits in-process per-card, not via the file-pair subprocess model, so its
wiring is a tracked GAP (`stage2_pregate_en_wiring_h405` in
[LANG_PARITY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md)).

## LANG_PARITY

`government_census.py` reads the raw PWG source below the `--lang` branch and
never touches RU/EN-specific code — classified **SHARED** in
[LANG_PARITY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md)
(entry `government_census`).

_Dr. Mārcis Gasūns_
