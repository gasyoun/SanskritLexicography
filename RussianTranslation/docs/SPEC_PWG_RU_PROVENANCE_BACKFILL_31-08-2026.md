# SPEC — pwg_ru provenance backfill: field semantics, evidence per era, ledger format

_Created: 31-08-2026 · Last updated: 03-09-2026_

> **§2.3 is IMPLEMENTED as of 03-09-2026** — commit
> [`d12ef193e33b`](https://github.com/gasyoun/SanskritLexicography/commit/d12ef193e33bcc76c1e27a65298538f691ff727d) (H3982,
> Opus 5 `claude-opus-5`). The rest of this spec — the era-A ruling, the ledger, the
> `provenance_class` write — remains design only and unauthorized. See §2.3 below for
> what shipped and the one naming change.

**Design only apart from §2.3. Nothing else here is authorized to run.** Wave unit **W3** of the
[CLAUDE hardening wave](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_CLAUDE_HARDENING_WAVE_2026H2.md)
delivers the census and this specification; executing any store write below is a
separate, separately-authorized act ([H3750](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3750-Opus_SanskritLexicography_pwg-provenance-census_30.08.26.md),
Opus 5 `claude-opus-5`, [#1804](https://github.com/gasyoun/SanskritLexicography/issues/1804)).

Premise, measured in
[PWG_RU_PROVENANCE_CENSUS_31-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/PWG_RU_PROVENANCE_CENSUS_31-08-2026.md):
10,773 of 11,519 store rows (93.5 %) assert a pipeline provenance they never
measured, 9 carry no identity at all, and the asserted era's tooling identity fails
reconstruction against 8 of the 9 stamp classes that could test it.

## 1. The rule this spec exists to enforce

A field whose name ends in `_sha` is a **measurement of bytes that existed**. It is
written by the process that read those bytes, at the moment it read them, and never
by anything else. The 2026-07-04 backfill broke that rule in the mildest possible way
— it wrote only `*_version` strings — and the store still lost the ability to
separate affected rows from unaffected ones, because a version string with no hash
behind it is indistinguishable from a measurement to every reader.

**Therefore: no backfill may ever write `prompt_sha`, `glossary_sha` or
`script_sha`.** Whatever is recovered later goes in a differently-named block whose
name says it is a reconstruction, and carries the method that produced it.

## 2. Field semantics

### 2.1 `provenance.provenance_class` (new, every row)

One of `measured` · `asserted` · `absent`, defined exactly as
[`provenance_census.classify()`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/provenance_census.py)
defines it — the census is the reference implementation, not a second opinion:

| value | condition |
|---|---|
| `measured` | all three of `pipeline.prompt_sha` / `glossary_sha` / `script_sha` present |
| `asserted` | a pipeline block without all three (`backfilled: true`, or a partial stamp) |
| `absent` | no `generated_at` **and** no `input_raw_sha256` / `input_portrait_sha256` |

Writing it into the store is a convenience for consumers, not new knowledge; it must
be derived by the census code, never hand-set. A row whose stored class disagrees
with the freshly-computed one is a hard gate failure, not a warning.

### 2.2 `provenance.pipeline_reconstruction` (new, only where evidence exists)

Never merged into `provenance.pipeline`. Shape:

| field | meaning |
|---|---|
| `schema` | `pwg_ru.pipeline_reconstruction.v1` |
| `method` | named, enumerated: `git_commit_at_generation` · `sidecar_recovered` · `component_blob_archive` — never free prose |
| `evidence` | what was actually read: commit id, sidecar path + its own sha256, archive blob id |
| `confidence` | `high` only when the method reproduces a **measured** stamp of the same era in validation; `low` otherwise; there is no `medium` |
| `validation` | `{"tested_against": <n measured stamps>, "reproduced": <n>}` — the numbers that justify `confidence`, copied from the run that produced them |
| `prompt_sha_reconstructed` / `glossary_sha_reconstructed` / `script_sha_reconstructed` | the recovered values, under names no reader can mistake for measurements |
| `reconstructed_at`, `tool_version`, `ledger_id` | when, by what, and the ledger row that authorizes it |

`confidence: high` is currently **unreachable for era A** — the validation numbers are
1 of 9 (§4). A method that scores like that may still be recorded, at `low`, but it
may not be used to answer "which rows did prompt defect X touch".

### 2.3 What a row must carry going forward (the real fix) — ✅ IMPLEMENTED 03-09-2026

> Shipped by H3982 in commit
> [`d12ef193e33b`](https://github.com/gasyoun/SanskritLexicography/commit/d12ef193e33bcc76c1e27a65298538f691ff727d):
> both items below now run inside
> [`pipeline_version.stamp()`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pipeline_version.py),
> the single chokepoint every newly written store row passes through, so "every row
> going forward" needed no change at any call site and no legacy row was touched.
> Archive contract:
> [`reports/pipeline_blobs/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/pipeline_blobs/README.md).
> Acceptance evidence: a canary run against a deliberately dirty tree
> ([`reports/H3982_CANARY_FORWARD_PROVENANCE_03-09-2026.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H3982_CANARY_FORWARD_PROVENANCE_03-09-2026.json))
> — `worktree_dirty: true`, `dirty_component_sha` present, and all three recorded
> component hashes resolving to archived bytes
> (`forward_unresolved: []`), reproducible with
> `python src/canary_forward_provenance.py`.
>
> **One field was renamed against the text below: `source_worktree_dirty` shipped as
> `worktree_dirty`** (with `source_commit` carrying the `source_` sense for the pair).
> H3982 is the later document and its acceptance wording is the operative lock; the
> spec name is superseded, not silently ignored. `dirty_component_sha` is written only
> when the tree is in fact dirty.


The census's root cause is that the pipeline runs against an uncommitted working
tree, so the committed history cannot describe it. Two additions close that, and both
belong to the generation path, not to a backfill:

1. `provenance.pipeline.source_commit` + `source_worktree_dirty` (bool) +
   `dirty_component_sha` — the commit the run *believed* it was on, plus an explicit
   statement that the bytes differed from it. A run on a dirty tree stays legal; a run
   that hides it does not.
2. **Component blob archive.** When `stamp()` computes a component hash it also writes
   the component bytes, once, to a content-addressed store
   (`RussianTranslation/reports/pipeline_blobs/<sha>.zip`, ~tens of KB per distinct
   set, 9 distinct sets in two months). Every future `*_sha` then resolves to
   recoverable bytes instead of to a hash nobody can expand. This is the only
   mechanism that would have made the era-A loss recoverable, and it is cheap.

### 2.4 `wf_file` must stop being a name

1,025 rows point at the generic `wf_output.json`, four copies of which exist on disk;
673 of them already fail input-hash corroboration because the name resolves to
whatever ran last. A pointer to evidence must be content-addressed:
`provenance.wf_file_sha256` beside the name, and a promote that refuses a sidecar
whose content hash does not match the row's input hashes.

## 3. Evidence source per era

| era | rows | evidence that exists | what may be written | what may NOT be written |
|---|---:|---|---|---|
| **A — asserted** (2026-06-29 .. 2026-07-04T05:43Z) | 10,773 | input hashes (10,100 corroborated by surviving sidecars); generation timestamps; the legacy sidecars in [`archive/legacy_runtime_2026-07-04/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/archive) which carry **no** component identity | `provenance_class: "asserted"`, `tooling_recoverable: false`, a pointer to the census | any `*_sha`; any reconstructed component hash at `confidence: high` |
| **B — measured** (2026-07-04T20:36Z ..) | 737 | the three content hashes per row, 9 distinct stamp classes | nothing — the era is already correct | anything at all: do not touch rows that carry a measurement |
| **C — absent** (undated) | 9 | none: `generated_at`, `input_raw_sha256`, `input_portrait_sha256` all null; no sidecar | `provenance_class: "absent"` and exclusion from every evidence-weighted use | any invented timestamp or input hash — including one "derived" from a neighbouring row |

Era C's nine rows are `key1='vid'` sub-cards from `autosplit_requeue.topup`. The
forward half of their fix is a refusal, not a repair: a promote whose row carries a
null input hash must fail, so the class cannot grow. Re-translating the nine is the
only way to give them provenance, and that is a paid act with its own authorization.

## 4. Why the obvious backfill is refused

`--reconstruct` was run precisely so this refusal would be a measurement:
recomputing `component_sha` over the manifest's file sets at all 99 commits that
touched a component between 2026-06-01 and 2026-09-01 reproduces **1 of 9** measured
stamp classes (20 of 737 rows, 2.7 %) under both the loose and the strict test. The
loose test accepts a hash from any commit in the window, including commits made after
the row was generated, and still fails eight classes.

A method that is wrong about the era it *can* be checked against must not be applied
to the era it cannot. Writing git-derived hashes onto 10,773 rows would replace one
assertion with a larger, better-dressed assertion — the exact defect #1804 reports.

**The honest verdict for era A is a permanent one:** its tooling identity is lost.
That is recorded as [GAPS §19](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md),
not as a task waiting for a cleverer script.

## 5. Ledger format

Any store write derived from this spec follows the H3591 pattern already used by
[`H2996_key1_repair_apply_ledger.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H2996_key1_repair_apply_ledger.jsonl):
an append-only JSONL beside the report, one object per touched row, written **before**
the store is rewritten, so the store delta can be proven equal to the ledger.

`RussianTranslation/reports/PWG_RU_PROVENANCE_BACKFILL_LEDGER_<DD-MM-YYYY>.jsonl`:

```json
{"schema": "pwg_ru.provenance_backfill.v1", "handoff": "H####", "run_id": "prov-bf-001",
 "applied_at": "2026-09-01T10:00:00Z", "tool_version": "provenance_census.py@<sha>",
 "store_line": 4711, "key1": "Ap", "subcard": "_ap~~h0_00_pwg00",
 "field": "provenance.provenance_class", "old": null, "new": "asserted",
 "method": "census_classification", "evidence": "PWG_RU_PROVENANCE_CENSUS_31-08-2026.json",
 "confidence": "high"}
```

Rules, all mechanical:

1. One object per `(store_line, field)`. No object may set two fields.
2. `old` is the value read in the same pass that wrote `new`; a row whose `old` no
   longer matches at apply time aborts the whole run (the store moved under the ledger).
3. The run is bracketed by
   [`audit_store_gates.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src) before and after;
   **store delta == ledger, exactly**, hard flags unchanged. A diff without its ledger
   row is the wave's declared halt condition.
4. Writes go through the H2146/H3350 locked writer (`store_write.locked_store_rewrite`)
   and the canonical store resolved by
   [`store_path.canonical_store()`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/store_path.py) —
   never a worktree-local copy (the H255 loss class).
5. The `pwg-ru-data/tm/` mirror refresh is the **last** step, never the first.

## 6. Acceptance for a future execution handoff

1. `provenance_class` present on all 11,519 rows and equal to the freshly-computed
   class for every one of them.
2. Zero new `*_sha` values anywhere in the store; `git diff` of the store shows only
   the fields this spec names.
3. Ledger row count == store delta count, proven by `audit_store_gates.py` before/after.
4. The nine era-C rows excluded from evidence-weighted use, and a RED-pinned test that
   a promote with a null input hash fails.
5. The census re-run reproduces the same three class counts on the rewritten store,
   with `asserted` unchanged at 10,773 — a backfill that "improves" the number has
   invented evidence.

_Dr. Mārcis Gasūns_
