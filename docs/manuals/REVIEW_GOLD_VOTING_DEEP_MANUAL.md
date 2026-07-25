# Review / gold / voting-sheet deep manual — the human-judgment subsystem

_Created: 25-07-2026 · Last updated: 25-07-2026_

The subsystem deep manual for the RussianTranslation **human-review machinery**:
the G5/G6/G7 release gates, the 14-script gold chain, the HTML voting sheets,
and the H1404 **binding standard** that ties every downloaded `decisions.json`
to the exact sheet generation it was voted in. Authored by Fable 5
(`claude-fable-5`) under
[H1404](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1404-Fable_SanskritLexicography_deep-manual-review-gold-voting-wave1_20.07.26.md)
per the org deep-manual template
([ARCHITECTURE_ORG_DEEP_MANUALS_FABLE_WAVES.md](https://github.com/gasyoun/Uprava/blob/main/docs/ARCHITECTURE_ORG_DEEP_MANUALS_FABLE_WAVES.md)).
Audience: the maintainer running review rounds, and (chapter 8, in Russian) the
human reviewer clicking the sheets. The pipeline-side sibling is
[RUSSIANTRANSLATION_DEEP_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RUSSIANTRANSLATION_DEEP_MANUAL.md);
gate arithmetic is owned by
[HUMAN_REVIEW_MINIMIZATION.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/HUMAN_REVIEW_MINIMIZATION.md)
— this manual documents it and never redefines it.

All commands below run from
[`RussianTranslation/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation)
and were actually executed 25-07-2026 during authoring; their outputs are
quoted verbatim (evidence ledger in the sibling
[REVIEW_GOLD_VOTING_DEEP_MANUAL.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/REVIEW_GOLD_VOTING_DEEP_MANUAL.meta.md)).

## 1. Orientation — the whole loop on one screen

```text
generate sheet (stamped + locked)      python src/build_g5_review_sheet.py
        │                              python src/build_g6_mqm_gold_sheet.py
        ▼
human votes in browser (a/r/d keys, notes; localStorage autosaves)
        │  Download / Save-to-folder → <sheet_id>_decisions.json
        ▼
validate BEFORE anything is applied    python src/validate_decisions.py <file>
        │  (schema + sheet_id→lock + content_hash + id set; exit 1 = rejected)
        ▼
apply through the gate's own tools     python src/apply_decisions.py <file>
        │  G5 → merge into src/_review_queue.csv → run_batch.py validate_review
        │  G6 → 11-column CSV → gold_ingest.py (explicit out path)
        ▼
gate arithmetic                        python src/preflight_remaining_gates.py
```

Five rules that prevent every historical failure in this subsystem:

1. **No export is applied unvalidated.** `apply_decisions.py`'s first act is
   the validator; a file that cannot be bound to a committed lock never touches
   a queue or a gold label.
2. **Never regenerate a voted sheet in place** (voted.md item 2). Regeneration
   mints a new `content_hash`; old exports then stop validating strictly — by
   design.
3. **Sheets are local, locks are committed.** The HTML embeds unpublished RU
   (public repo) and stays gitignored; the metadata-only
   `review/locks/<sheet_id>.lock.json` is the durable, committable anchor.
4. **The fenced files are fenced.**
   [`review/voted.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/voted.md)
   and
   [`review/decisions.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/decisions.md)
   are human review-ledger entries — no agent edits them, ever.
5. **One instrument per gate** (ruling D6, §5.2) — stop maintaining four
   competing methodologies.

## 2. Component map — gates, scripts, artifacts

### 2.1 The release gates (owned by HUMAN_REVIEW_MINIMIZATION.md)

| Gate | Job | Volume | Instrument (D6) | Done-check |
|---|---|---|---|---|
| G5 | bulk print-readiness decisions over the promoted store | 11,163 `ai_translated` rows (25-07-2026) | approve/reject/defer sheet → `src/_review_queue.csv` | `run_batch.py validate_review` + ≥1 print-ready row |
| G6 | human gold labels for quality measurement | 320-row stratified sample (fixed; do NOT expand to 11k) | MQM-style 6-label typology sheet | `gold_status.py` 320/320 + `gold_validate.py` |
| G7 | independent second review + agreement | 80 of the 320 | agreement queue + Cohen κ | `gold_agreement.py` release mode (needs ≥1 κ pair) |
| G10 | edition cut | — | — | waits for G5/G6/G7 |

### 2.2 The 14-script gold chain (`src/gold_*.py`)

Verified 25-07-2026 against the code (defaults quoted from argparse/constants):

| Stage | Script | In → out | Key contract |
|---|---|---|---|
| frame | `gold_sample.py` | `corpus_lexicon.jsonl` → `src/gold_sample.jsonl` | `[N]` positional, default 300, SEED 42 |
| frame | `gold_recall_sample.py` | lexicon + strata → `src/recall_sample.jsonl` | subcommands `coverage`/`sample [N]` (N 32) |
| frame | `gold_sample_en.py` | store `en` layer → `gold/reviewer_sheet_en.csv` | `--n 300 --seed 42`; has `--selftest` |
| scaffold | `gold_aggregate.py` | LLM-judge workflow JSON → `gold/gold_set.jsonl` + `precision_report.md` | Wilson z=1.96; labels GOOD={correct, lemma-variant, proper-name} |
| scaffold | `gold_review_csv.py` | `gold/gold_set.jsonl` → `gold/_human_gold_review.csv` | 16 columns, utf-8-sig, blank human fields |
| packet | `gold_packet.py` | review CSV → `gold/reviewer_packets/gold_packet_NNN_NNN.csv` | `--batch-size 40` |
| packet | `gold_packet_verify.py` | scaffold + packets | exact once-coverage on `(id, slp1)` |
| status | `gold_status.py` | review CSV | 320/320 completeness report (G6 done-check) |
| ingest | `gold_validate.py` | review CSV | 11 required cols; 6-label vocab; `--expect 320` |
| ingest | `gold_ingest.py` | validated CSV → `gold/human_gold_labels.jsonl` | **hard 320-unique-ids check on the default out path only** — pass an explicit out path for partial packets |
| G7 | `gold_double_review_queue.py` | filled CSV → `gold/_double_review_queue.csv` | `--sample-size 80`, stratified round-robin |
| G7 | `gold_double_review_verify.py` | queue CSV | second-columns blank, count == sample-size, stratum balance ≤1 |
| G7 | `gold_ingest_double_review.py` | filled wide CSV → long rows merged into labels jsonl | second reviewer must differ; dedup on `(id, reviewer_id)` |
| report | `gold_agreement.py` | labels jsonl → `human_precision_report.md` + `double_review_agreement.md` | unweighted Cohen κ over the FIRST TWO labels per id; `--fixture` is the test escape |

Support cast: `triage_review_queue.py` (G5 bucketing of judge verdicts — see
§5.3 for the generations trap), `run_batch.py` (`review_csv` /
`validate_review` / `review_report` — the G5 lane),
`preflight_remaining_gates.py` (gate roll-up), `fidelity_sample*.py` (the
LLM-judged fidelity track — adjacent, NOT part of G5/G6/G7).

### 2.3 Sheet-side components (the H1404 binding standard)

| Piece | File | Role |
|---|---|---|
| Emitter | `csl_pyutil.render_review_sheet` v0.3.1 (external, pinned) | the ONE sheet template (V1–V8 standard); never forked |
| Repo lookups | [`src/review_sheet_standard.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/review_sheet_standard.py) | V4 entry links, SLP1→IAST, shared config, `DA_RATING` |
| Binding | [`src/review_binding.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/review_binding.py) | `content_hash()` · `stamp()` · `write_lock()` · retro locks |
| Schema | [`schemas/decisions.schema.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/schemas/decisions.schema.json) | the export shape, `content_hash` required |
| Gate | [`src/validate_decisions.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/validate_decisions.py) | refuses unbound/mismatched/drifted exports |
| Router | [`src/apply_decisions.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/apply_decisions.py) | validator-first; G5→run_batch, G6→gold_ingest |
| Locks | `review/locks/<sheet_id>.lock.json` (tracked) | sheet_id + hash + card ids; the durable anchor |
| Generators | `build_g5_review_sheet.py` · `build_g6_mqm_gold_sheet.py` · `build_h180_review_sheets.py` · `build_kochergina_sheet.py` · `build_renou_pilot_sheet.py` · `h178_eval_bakeoff.py` | all stamp + lock at generation time |

## 3. The sheet lifecycle, stage by stage

### 3.1 Generate (stamped + locked)

```text
$ python src/build_g5_review_sheet.py --n 150            # needs the gitignored queue+store
G5 sheet: 150 cards -> ...\review\g5_batch1_sheet.html
  sha256:cea166b52217843f3edc3b0167eea3be10d3c582ba23feb3dd77c2d220caae5a
  lock -> ...\review\locks\g5-live-queue-batch1-2026-07-25.lock.json

$ python src/build_g6_mqm_gold_sheet.py                  # gold_set.jsonl is tracked
G6 sheet: 20 cards -> ...\review\g6_mqm_starter_sheet.html
  sha256:e69ca47823561958855e3a7db071a0233b6a6c24ce73aa7afa3fcdd86d84b454
  lock -> ...\review\locks\g6-mqm-gold-starter-2026-07-25.lock.json
```

What `stamp()` does (all additive string surgery on stable anchors — the same
technique the emitter's own `_add_standard()` uses, because csl-pyutil is
external/pinned and its export payload is hardcoded with no hash hook):

1. computes `content_hash` = `sha256:` over the **pre-stamp** HTML,
   LF-normalized (the stamp is derived data, not content);
2. injects `var CONTENT_HASH = "sha256:…";` beside **every** `var SHEET_ID`
   declaration (the bakeoff widget splice is a second IIFE with its own);
3. patches **every** export payload site — the emitter's core download, its
   auto-save `exportPayload()`, its strict-review payload, and
   `h178_eval_bakeoff.py`'s spliced RUBRIC_JS all share the one literal
   `{ sheet_id: SHEET_ID, ` — to also emit `content_hash`;
4. renders a visible `bound sha256:…` chip beside the header's sheet_id, so
   the human can eyeball the binding (voted.md item 8: «и мне и агенту»);
5. `write_lock()` commits the identity: sheet_id, hash, card ids, gate, mode.

Double-stamping is refused loudly (`--selftest` proves it): a stamped document
would otherwise hash the stamp into itself.

### 3.2 Vote

Open the sheet from `file://`, vote with clicks or `a`/`r`/`d` +
arrow keys; notes autosave to localStorage under `review-sheet:<sheet_id>`.
The two starter sheets run the strict-review layer: the export carries
`reviewer`, `reviewedAt`, `complete`; the G6 sheet refuses download until all
20 cards are voted and every reject has a note; the G5 sheet allows partial
exports (`complete: false`) but still requires reject notes.

### 3.3 Validate — the four demonstrated refusals

`validate_decisions.py` checks, in order, each with a named exit-1 reason:
JSON parse → schema (via `jsonschema` when importable, else a field-identical
stdlib fallback — the repo deliberately does not depend on jsonschema) →
sheet_id resolves to a lock → `content_hash` equals the lock's → item ids
exactly equal the lock's ids. Recorded selftest run (25-07-2026):

```text
$ python src/validate_decisions.py --selftest
  ok accepts a genuine bound export
  ok rejects a hand-corrupted sheet_id [binding]
  ok rejects a mismatched content_hash [binding]
  ok rejects a schema-invalid file (bad decision enum) [schema]
  ok structural fallback accepts the genuine export
  ok structural fallback rejects the bad enum
  ok rejects an unbound (no content_hash) export [binding]
  ok refuses --allow-legacy against a stamped-mode lock [binding]
  ok --allow-legacy accepts a legacy export against a retro lock AND logs it
  ok rejects item-id drift vs the lock [binding]
validate_decisions selftest OK
```

And against the real pre-standard file (the unbound `review/decisions.json`,
sheet_id `h178_da`, 30 votes of 07-07-2026):

```text
$ python src/validate_decisions.py review/decisions.json
REJECTED review/decisions.json
  binding: UNBOUND export — no content_hash. Pre-standard files pass only via
  --allow-legacy (logged), never silently.
$ python src/validate_decisions.py review/decisions.json --allow-legacy
WARNING: legacy unbound export accepted via --allow-legacy (logged to review/locks/allow_legacy.log)
OK: decisions.json bound to sheet 'h178_da' (sha256:2081832d8086…; 30 items, 30 decided)
```

The `--allow-legacy` escape works ONLY against a `mode: retro-unstamped` lock
(minted from the pre-standard sheet's source-of-record HTML with
`python src/review_binding.py retro-lock <sheet.html>`), and every acceptance
is appended to `review/locks/allow_legacy.log`. A rights/correctness gate never
fails open.

### 3.4 Apply — gate-routed, validator-first

```text
$ python src/apply_decisions.py <export.json> [--gate G5|G6] [--dry-run]
```

Gate comes from the lock (`--gate` overrides; a pilot/retired sheet with no
gate is PARKED, exit 2, never guessed). G5: votes merge into
`src/_review_queue.csv` (approve→`approved`, reject→`reject`,
defer→`needs_review`, reviewer required, notes appended), then
`run_batch.py validate_review` runs — print-ready integrity
(`key_match`/`placeholders_ok`) stays run_batch's job. G6: votes convert to the
11-column CSV (approve = confirm the shown LLM label; reject = the correct
label is the FIRST word of the note; defer = `needs_adjudication=true`;
`rating` 1–2/3/4–5 → confidence low/medium/high), then `gold_ingest.py` runs
with an explicit out path (`gold/decisions_<sheet_id>.labels.jsonl`) so the
320-gate stays with the full set. Unmatched ids, an unparseable reject label,
or a missing reviewer abort BEFORE anything is written.

## 4. Design rationale — why it is shaped this way

**Why a content hash and not just sheet_id (voted.md item 8).** The emitter
already stamps `sheet_id` into sheet and export — and it was not enough,
because a sheet_id names a *series*, not a *generation*. The Renou pilot made
this concrete: the tracked
[`sanskritlexicography-renou-hypotheses_pilot_decisions.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/sanskritlexicography-renou-hypotheses_pilot_decisions.json)
carries `sheet_id: renou-pilot-2026-07-02` (v1), while the tracked HTML beside
it is `renou-pilot-v2-2026-07-19` — same series, different generation, and the
v1 HTML no longer exists, so nothing can prove which card texts those 3 votes
were cast against. The hash closes exactly that hole: votes bind to the
byte-exact document the reviewer saw. The v1 export is the standing example of
an unprovable binding — it has no lock, is not grandfathered, and stays
rejected by design.

**Why the lock file, not the HTML, is the anchor.** Sheets are gitignored
(unpublished RU, public repo) and `/decisions-apply` conventionally deletes a
closed sheet. The lock is the smallest committable object that outlives both:
identity + hash + id set, no card bodies (one nuance: card ids are echoed
verbatim, and a few store sense_tags carry short structural labels like
«грамматическая рубрика» — rubric names, not translation content; ruled
publishable in the 25-07-2026 `/publish-safety-check`).

**Why repo-side, not in csl-pyutil.** The emitter is an external pinned
package consumed by four repos; its payload sites are stable string anchors.
Stamping post-render keeps the byte-identical-fixture contract of the package
intact and needs no upstream release to evolve. Proposing a native
`content_hash` hook upstream is a recorded follow-up, not a blocker (R2).

**Why the validator refuses instead of warning.** The org's known failure mode
is over-claimed close-outs; a warning that can be scrolled past becomes a
silent hole. Named exit-1 reasons, and a logged single-purpose escape flag,
make every exception an audit-trail entry instead.

### 4.1 The per-gate instrument ruling (D6) — and the retired pilots

The h178 bake-off (19-07-2026) ran four instruments over the SAME 30 glosses.
Ruling D6 (MG, 20-07-2026) matches one instrument to each gate's job and
retires the rest — the sheets stay on disk as audit history, never deleted:

| Instrument | Pilot sheet | Verdict | Rationale |
|---|---|---|---|
| approve/reject/defer | (baseline of every sheet) | **G5's instrument** | G5 is a bulk print/no-print decision; a scale adds cost, not information |
| MQM error typology | `h178_mqm_sheet.html` | **G6's instrument** (as the 6-label set) | gold needs *typed* errors for precision arithmetic; the 6 labels are exactly `gold_validate.py`'s vocabulary |
| Direct Assessment 1–5 | `h178_da_sheet.html` | retired as a gate instrument | the DA vote's real yield was the V1–V8 sheet-standard meta-notes, not the scores; `DA_RATING` survives as an optional emitter layer for future quality-scale pilots |
| Likert | `h178_likert_sheet.html` | retired | ordinal agreement without typed defects feeds no gate's arithmetic |
| pairwise | `h178_pairwise_sheet.html` | retired | O(n²) comparisons; no gate consumes a ranking |

G7 keeps its own instrument: the double-review queue + Cohen κ
(`gold_agreement.py`, unweighted, first-two-labels-per-id, 6-label margins).

### 4.2 The queue-generations lesson (found while building the G5 starter)

The 2026-06 G5 queue (217 rows) was judge-annotated and triaged; the current
queue (11,163 rows) was regenerated from the full promoted store with
`row:`-shaped review_ids and **zero** judge annotations, and the store dropped
its `ord` fields — so every legacy `ord:N` id is now unresolvable by
`run_batch.py validate_review`. Consequences, all applied in H1404:
`triage_review_queue.py` now carries `review_id` in its CSV and tolerates
ord-less generations (its old `int(ord)` sort crashed on them); the 32
judge-flagged defect rows were routed — not retranslated — into
[`review/G5_REJECT_REQUEUE_AUDIT.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/G5_REJECT_REQUEUE_AUDIT.md);
and the G5 starter sheet samples the LIVE queue (round-robin across roots),
not the dead one. The general rule: **a review artifact is only as durable as
the id scheme it is keyed on — bind to review_id, never to a positional ord.**

## 5. Failure modes — symptom → cause → cure

| Symptom | Cause | Cure |
|---|---|---|
| `REJECTED … UNBOUND export — no content_hash` | pre-standard export, or export produced by an unstamped sheet | if genuinely legacy: mint a retro lock from the source-of-record HTML, re-run with `--allow-legacy` (logged); otherwise regenerate the sheet through a stamping generator |
| `REJECTED … unknown sheet_id` | no lock committed for that sheet | the sheet was generated before the standard or outside a generator — `python src/review_binding.py retro-lock <sheet.html> --gate G5\|G6` |
| `REJECTED … content_hash mismatch` | sheet regenerated after the votes were cast (voted.md item 2 violated) | do NOT force-apply; recover the generation the votes belong to, or re-vote on the current one |
| `REJECTED … item-id drift` | export hand-edited, or ids changed between generations | treat as corrupt; re-export from the browser |
| `sheet is already stamped … re-stamping refused` | `stamp()` called on stamped HTML | regenerate from the generator; never stamp twice |
| `gold_ingest`: `expected 320 unique gold ids` on a starter packet | default out path triggers the full-set gate | always pass an explicit out jsonl for partial packets (`apply_decisions.py` does) |
| `run_batch validate_review`: `<id>: not found in store` | id scheme mismatch (e.g. legacy `ord:N` vs `row:` store) | see §4.2 — rebuild the sheet from the live queue |
| `review validation failed: … review_id required` | decisions merged without reviewer | strict-review sheets carry `reviewer`; else pass `--reviewer` |
| CSV read garbles the first column | G5/G6 CSVs are utf-8-**sig** | always `encoding="utf-8-sig"` (every chain script already does) |
| votes vanished after a sheet remake | localStorage key is `review-sheet:<sheet_id>` | keep sheet_id stable across remakes (the Kochergina generator even splices a key-migration shim); votes survive, but the hash changes — item 2 still applies |
| pre-commit blocks the commit | `review_changelog_guard.py`: a `RussianTranslation/*REVIEW*/*AUDIT*` doc staged without `RussianTranslation/CHANGELOG.md` | stage the changelog entry in the same commit (R9) |

## 6. Provenance and the rights boundary

- The repo is PUBLIC. Sheets embed unpublished RU translation → **gitignored**
  (`review/g5_*_sheet.html`, `review/g6_*_sheet.html`, plus the older
  per-family patterns). Locks, schema, generators, this manual → committed.
- Exactly **two** sheets are tracked (D7, re-derived from
  `git ls-files 'RussianTranslation/review/*.html'` 25-07-2026):
  the Kochergina 4-row correction sheet and the Renou 70-card pilot — both
  sample-sized scholarly excerpts, kept tracked deliberately; the false "all
  sheets are gitignored" claim in RUSSIANTRANSLATION_DEEP_MANUAL.md §9 was
  amended in this pass. `/publish-safety-check` verdict for all H1404 surfaces:
  **GO** (25-07-2026, recorded in the metadoc).
- Downloaded exports (`review/*_decisions.json`) are personal working
  artifacts — gitignored by pattern; the tracked exceptions are historical
  evidence files. `review/voted.md` and `review/decisions.md` are the human's
  ledger: fenced, never edited by agents.

## 7. Maintainer appendix

**Adding a new sheet generator** (the whole standard in five lines):

```python
from csl_pyutil import render_review_sheet
from review_binding import stamp, write_lock
from review_sheet_standard import standard_config
doc = render_review_sheet(items, config, extras=True)
doc, chash = stamp(doc)                       # then write doc to review/…
write_lock(config["sheet_id"], chash, [it["id"] for it in items],
           config["generated"], gate="G5", source_html=out_path)
```

Add the HTML's gitignore pattern if the sheet embeds store text; register the
sheet in
[Uprava/REVIEW_SHEETS_INDEX.md](https://github.com/gasyoun/Uprava/blob/main/REVIEW_SHEETS_INDEX.md)
(naming rule: `<repo-slug>-<topic>_<scope>_review.html`, or the gate-prefixed
form used here); pick ONE instrument per §4.1 — a new instrument needs a new
ruling, not a new pilot zoo.

**Keeping this manual honest.** Every count above is stamped with its as-of
date; re-derive, never trust: tracked-sheet set via `git ls-files`, queue/store
sizes via the files themselves, selftests via
`python src/review_binding.py --selftest`,
`python src/validate_decisions.py --selftest`,
`python src/apply_decisions.py --selftest` (all three green as of 25-07-2026).
On substantive edits: tick the metadoc backlog, add a revision row, bump the
staleness block. The freshness detector
([Uprava/tools/manual_staleness.py](https://github.com/gasyoun/Uprava/blob/main/tools/manual_staleness.py))
reads the metadoc from origin — it reports FRESH only after merge.

**Deliberate non-goals.** This manual does not redefine gate arithmetic
(HUMAN_REVIEW_MINIMIZATION.md owns it), does not cover the LLM-judged fidelity
track (`fidelity_sample*.py` — see the pipeline manual), and does not schedule
the retranslation of the routed G5 defects (fenced downstream handoff, §4.2).

## 8. Глава для рецензента — как голосовать, чтобы голос засчитался

Эта глава — по-русски, потому что голосует человек. Она отвечает на два ваших
же пункта из
[voted.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/voted.md):
**пункт 8** («Нужен стандарт для листов голосования… Как потом понять, что
decisions.JSON относится именно к h178_da_sheet.html — и мне и агенту?») — им
стал стандарт привязки H1404, описанный ниже; и **пункт 2** («сначала
отработать голоса первого листа, потом перегенерировать остальные») — теперь
это не только дисциплина, но и механика: перегенерация меняет хэш, и старые
голоса перестают проходить строгую проверку.

**Путь клика, шаг за шагом:**

1. Откройте лист двойным кликом (он лежит в
   `SanskritLexicography\RussianTranslation\review\`, например
   `g6_mqm_starter_sheet.html`). Всё работает локально, без сети.
2. В шапке видны `sheet_id` и метка `bound sha256:…` — это «паспорт» листа.
   Именно эти два значения попадут в ваш экспорт и позволят агенту доказать,
   что голоса относятся к этому файлу (ваш пункт 8).
3. Голосуйте кнопками на карточке или клавишами: `a` — approve, `r` — reject,
   `d` — defer; стрелки ↓/↑ — следующая/предыдущая карточка. Голоса
   сохраняются в браузере сами (localStorage) — закрыть и продолжить завтра
   можно без потерь.
4. Заметки: на G6-листе при reject **первым словом заметки** пишите правильный
   ярлык из шести (`correct`, `lemma-variant`, `proper-name`, `partial`,
   `wrong-sense`, `hallucinated`), дальше — почему. Скрипт применения читает
   именно первое слово; без него reject не применится.
5. Впишите себя в поле «Reviewer» (иначе строгий лист не отдаст файл).
6. Жмите «Save to folder…» один раз — дальше файл будет обновляться сам при
   каждом голосе; либо «Download decisions.json» в конце. Файл называется
   `<sheet_id>_decisions.json` — сохраняйте его туда, куда указывает плашка в
   шапке листа (для стартовых листов: `RussianTranslation\review\`).
7. Дальше — дело агента: `validate_decisions.py` проверит привязку,
   `apply_decisions.py` применит голоса через штатные инструменты гейта.
   Файл, который не привязывается к листу, будет отвергнут с named-причиной —
   и это правильно: лучше отвергнутый экспорт, чем голоса, применённые не к
   тем карточкам.

**Правило пункта 2 в новой механике:** пока голоса листа не отработаны
(`apply_decisions` завершился зелёным), лист не перегенерируется. Если
перегенерировать раньше — хэш изменится, и строгая проверка честно скажет:
«голоса были поданы по другому поколению листа». Это не поломка, это защита
вашего труда.

_Dr. Mārcis Gasūns_
