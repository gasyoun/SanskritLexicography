# PWG→RU pipeline capability audit — 3-account concurrency · per-sense evidence provenance · case-government · per-sense genre (H335)

_Created: 08-07-2026 · Last updated: 08-07-2026_

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

## LANG_PARITY

`government_census.py` reads the raw PWG source below the `--lang` branch and
never touches RU/EN-specific code — classified **SHARED** in
[LANG_PARITY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md)
(entry `government_census`).

_Dr. Mārcis Gasūns_
