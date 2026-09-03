# GAPS — the Sanskrit-data known-unknowns frontier

_Created: 08-07-2026 · Last updated: 03-09-2026_

**Epistemic sibling of [`FINDINGS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).** FINDINGS is what is *known*. This file is its **negative space** — the act FINDINGS cannot hold: **not-yet-knowing**, the frontier of things we have explicitly NOT measured. The moment a gap is measured, it **graduates** to a FINDINGS row (delete it here, cite the finding there). One of the seven episteme registries minted under [H356](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H356-Opus_csl-corrections_epistemic-sibling-registries_08.07.26.md); the full set is on the [episteme dashboard](https://gasyoun.github.io/SanskritLexicography/episteme/). Its infra twin is [`Uprava/GAPS.md`](https://github.com/gasyoun/Uprava/blob/main/GAPS.md).

**How to read a row.** Every row opens with two glyphs:

- **Importance dot** (identical scale to FINDINGS): 🔴 3 high · 🟠 2 medium · 🟡 1 minor — here the dot rates the **value if measured** (what it would unblock).
- **Origin marker:** ⚙️ auto (a set-difference script emitted this — a dataset with no FINDINGS row) · ✍️ human (a session flagged it).

Then `Why it matters:`, `Blocker:`, `How to close:`, and a `> **Source:**` line.

**Auto-seed:** [`seed_gaps.py`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/seed_gaps.py) does a set-difference — datasets present in [`FEATURES_INDEX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md) / [`kosha` manifest](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json) that have **no** FINDINGS row, plus the "per-layer statistics still to compute" backlog named in [`DATA_LAYERS_CENSUS.md`](https://github.com/gasyoun/Uprava/blob/main/DATA_LAYERS_CENSUS.md).

---

## A. Blocked on data we don't yet have
*Gaps that stay open until an outage lifts, more correction eras accrue, or a walled dataset is downloaded — the blocker is data, not method.*

### §2. Error population of 40 of 43 dictionaries
🟠 ✍️ **We have NOT estimated the error-prone-record population for 40 of 43 dicts.**
Why it matters: correction-campaign planning currently assumes convergence; only PW (~14% done), MW (~10%), BUR are estimable — the other 40 have <10 two-era recaptures.
Blocker: needs a corpus rerun / more overlapping corrections — Chapman mark–recapture requires ≥10 two-era recaptures per dict.
How to close: accumulate a second correction era per dict, or use a different estimator; owner csl-observatory `error_recapture.md` (paper A48).
↔ Interlinks: [RECIPES §6](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) (correction loci census) is the per-dict correction-density base this estimate builds on · [ASSUMPTIONS §6](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) (a correction queue stays valid) is the perishability that makes a second era hard to accrue.
> **Source:** [FINDINGS §46](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#46-twelve-years-of-corrections-cover-only-1014--of-the-estimated-error-population) · [csl-observatory](https://github.com/sanskrit-lexicon/csl-observatory) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09)

### §3. Heritage inflected-form morphology XML — never ingested
🟠 ✍️ **We have NOT ingested Heritage's inflected-form morphology XML (1,286,615 forms / 32,837 stems).**
Why it matters: would be a third morphology witness (3× kosha's vidyut-built 426,410 forms); unblocks Heritage roadmap Phase 4; `heritage_forms_oracle` is only a partial alignment without it.
Blocker: data access — the XML is NOT in either git repo (GitHub mirror or INRIA GitLab); only downloadable behind the Anubis wall from `sanskrit.inria.fr/DATA/XML/{SL,WX}_morph.xml.gz` (v3.81).
How to close: a human browser download of the two `.xml.gz` URLs (bookmarked in §51), then ingest; LGPLLR-vs-BY-SA composition @DECIDE first.
↔ Interlinks: a third morphology witness stresses [ASSUMPTIONS §1](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) (DCS lemma == CDSL headword — the very join whose 18.6% unlinked residue Heritage could cover) · [DEAD_ENDS §2](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) (corpus present-class attribution) is why an independent morphology source, not corpus inference, is needed.
> **Source:** [FINDINGS §47](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#47-heritage-data-is-acquirable-despite-the-anubis-wall--via-a-github-mirror-the-morphology-xml-is-not-in-it) + [§51](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#51-huet-correspondence-predates-this-session-2021--the-morphology-xml-gate-was-already-resolved-in-writing-direct-download-urls-recovered) · [SanskritLexicography](https://github.com/gasyoun/SanskritLexicography) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09)

### §19. Which prompt, glossary and script bytes produced the 10,773 pre-04-07-2026 pwg_ru rows
> **BOUNDED 03-09-2026 — the gap can no longer grow.** H3982 (Opus 5 `claude-opus-5`),
> commit [`d12ef193e33b`](https://github.com/gasyoun/SanskritLexicography/commit/d12ef193e33bcc76c1e27a65298538f691ff727d), shipped the
> forward half of [SPEC §2.3](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/SPEC_PWG_RU_PROVENANCE_BACKFILL_31-08-2026.md):
> every newly written store row now carries `source_commit` + `worktree_dirty`, and
> `pipeline_version.stamp()` archives each component's bytes to a content-addressed
> [blob store](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/pipeline_blobs/README.md)
> at the moment the hash is computed. Runs against an uncommitted tree — the root cause
> of this gap — stay legal but can no longer hide, and every future `*_sha` expands back
> into real files. **The 10,773 already-lost rows are unchanged and remain lost**: this
> caps the gap at its current size, it does not close it, and the (a)/(b) fork below is
> still an open human ruling.

🔴 ✍️ **We do NOT know — and on current evidence cannot know — which tooling produced 93.5 % of the pwg_ru store.** Those rows carry `prompt_version: "1.0.0"` and `backfilled: true` with no content hash behind any of it ([FINDINGS §621](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md), [#1804](https://github.com/gasyoun/SanskritLexicography/issues/1804)). The obvious repair — recompute each component's hash from the repository as it stood at the row's `generated_at` — was tested against the 737 rows that *do* carry measured hashes and reproduced **1 of 9 stamp classes (20 of 737 rows)**, because the pipeline is routinely run against an uncommitted working tree.
Why it matters: a prompt or glossary defect found today cannot be scoped — the affected and unaffected rows are indistinguishable, so any such finding forces an all-or-nothing re-translation decision over 10,773 rows instead of a targeted one. It also caps what an evidence-graded publication can claim about that portion of the store.
Blocker: **the bytes no longer exist anywhere we can read them.** Git holds only what was committed; `pipeline_versions.json` keeps the current frozen SHA per component, not a history; the surviving workflow sidecars record input hashes and no component identity. This is a data gap, not a method gap — no cleverer script closes it.
How to close: only two paths, both acts, not analyses — (a) re-translate the era under a measuring pipeline, which is paid work with its own authorization; or (b) accept the loss permanently and mark the rows `provenance_class: "asserted"` per [SPEC_PWG_RU_PROVENANCE_BACKFILL_31-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/SPEC_PWG_RU_PROVENANCE_BACKFILL_31-08-2026.md), so the store states the limit instead of hiding it. Forward-facing prevention (component blob archive + `source_commit`/`worktree_dirty` stamps) was specified there and **shipped 03-09-2026** (H3982, commit [`d12ef193e33b`](https://github.com/gasyoun/SanskritLexicography/commit/d12ef193e33bcc76c1e27a65298538f691ff727d)), so the gap is now bounded at 10,773 rows and cannot grow.
↔ Interlinks: nine further rows (`key1='vid'`, `autosplit_requeue.topup`) have no input identity at all and cannot even be re-derived; the input half of the asserted era *is* corroborated for 10,100 of 10,773 rows by the surviving sidecars, so this gap is about tooling identity only.
> **Source:** [reports/PWG_RU_PROVENANCE_CENSUS_31-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/PWG_RU_PROVENANCE_CENSUS_31-08-2026.md) · [FINDINGS §621](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) · [H3750](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3750-Opus_SanskritLexicography_pwg-provenance-census_30.08.26.md) (Opus 5 `claude-opus-5`). — SanskritLexicography · 2026-08-31

## B. Blocked on a tool or method, not data
*The data is in hand; what's missing is a statistics pass, a schema-aware parse, or a validated lookup that doesn't exist yet.*

### §4. Homonym token frequency beyond the 26+5 splittable groups
🟡 ✍️ **We have NOT attributed token frequency for the 33 of 38 DCS-lumped homonym groups that share a present class.**
> **CEILING MEASURED 27-07-2026 → [FINDINGS §494](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) (38 single-lemma_id lumps; adjudication still open). H1747.**
Why it matters: token-level "N in this sense · M for the lemma" displays are impossible for these without sense/gloss adjudication; it is the ceiling on per-sense frequency accuracy.
Blocker: no tool — gaṇa is undistinguishing (unaccented corpus, §8); needs manual gloss adjudication (DCS `meanings` ↔ Warnemyr gloss).
How to close: extend the coverage≥0.55 gloss-mapping approach in `crosswalk/token_attribution.json`; owner WhitneyRoots.
↔ Interlinks: [ASSUMPTIONS §3](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) (giant verb root at homonym index 0) is the record-reach premise that must hold to even enumerate these groups · [DEAD_ENDS §2](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) (corpus present-class attribution) is the refuted shortcut — gaṇa can't disambiguate them · [GLOSSARY "homonym index"](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md) defines the ordinal in play.
> **Source:** [FINDINGS §2](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#2-homonym-token-splitting-has-a-hard-morphological-ceiling) · [WhitneyRoots](https://github.com/gasyoun/WhitneyRoots) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09)

### §5. `Stopovye` parallel-passage bundle vs full export — never content-diffed

> **GRADUATED 27-07-2026 → [FINDINGS §492](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) (Stopovye subset census vs Polnorazmernye). H1735 Grok 4.5 (grok-4.5). Do not re-measure; residual open work is only what the finding still flags.**
🟡 ✍️ **We have NOT content-diffed the 1.17 GB `PARA/Stopovye` bundle against `dcs-parallel-passages-full` (506,787 rows).**
Why it matters: it is the largest single derived-data bundle in VisualDCS; whether it is a stop-word-filtered variant or independent data determines if it is separately citable; its row count is still `null` (no schema-aware parse).
Blocker: no tool — needs a schema-aware per-file alignment parse, not a line count.
How to close: parse the per-passage CSV records, diff against the full-export sample; owner VisualDCS / manifest `stopovye-parallel-passages`.
↔ Interlinks: [DEAD_ENDS §6](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) (OccId/sent_id as a key) is the passage-id keying trap this schema-aware diff must avoid · [ASSUMPTIONS §2](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) (one transliteration keys all DCS files) is the keying premise any DCS-side alignment leans on.
> **Source:** [kosha](https://github.com/gasyoun/kosha) [datasets.json](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json) `stopovye-parallel-passages` note (H291) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09)

### §6. Cyrillic-only Sanskrit name glossaries — no join key exists
🟠 ✍️ **We have NOT (and cannot safely) build a Cyrillic→SLP1 key for the 3 fully-Cyrillic name glossaries.**
> **SEED INVENTORY 27-07-2026 → [FINDINGS §495](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) (61 IAST-bearing seeds / 47 pure-Cyrillic; rules still unsafe). H1746.**
Why it matters: 3 of 6 SamudraManthanam name indices (Потапова, Эрман-Темкин, Бадь Kadambari) are 100% Cyrillic — blocked from any pwg_ru corpus_gate reuse.
Blocker: no tool that is safe — practical Russian transcription collapses dental/retroflex (т = त and ट); a rule-based converter manufactures wrong keys for exactly the retroflex-bearing epic names.
How to close: a proper-noun lookup table validated against a Sanskrit onomasticon (not character rules), checked as its own artifact first.
↔ Interlinks: [DEAD_ENDS §5](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) (NFD-normalization as a key) is the same class of lossy character-rule bridge that manufactures wrong keys here · [GLOSSARY "SLP1 vs IAST"](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md) frames the scheme mismatch a Cyrillic→SLP1 map would have to cross.
> **Source:** [FINDINGS §60](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#60-practical-russian-transcription-of-sanskrit-names-has-no-safe-reverse-transliteration) · [RussianTranslation](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09)

---

### §16. 289 rows of the live pwg_ru store carry an `Instr.`→`Ins.` / `Akk.`→`Acc.` case-label rewrite that no repo script produces and the mirror lacks
> **CLOSED 27-08-2026 — MG ruling: `Instr.` stays canonical.** [H3591](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3591-Fable_pwg-ru-data_pwg-ru-store-instr-restore_27.08.26.md) (Fable 5 `claude-fable-5`) restored 309 rows from the mirror via [`src/restore_store_rows_from_mirror.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/restore_store_rows_from_mirror.py), kept the 22 H3361 rows, refreshed `pwg-ru-data/tm/` (commit [c9f664b](https://github.com/gasyoun/pwg-ru-data/commit/c9f664b)); proof: `audit_store_gates.py` `changed_ru=0`, `<ab>Ins.</ab>`=0 / `<ab>Instr.</ab>`=478 in both stores, hard flags unchanged (5), H3500 scan OK. Ledger: `pwg-ru-data/tm/h3591_restore_ledger.jsonl`. The writer of the rewrite remains unidentified — the drift is closed, its origin is not.
✅ **We do NOT know what rewrote 289 `ru` rows of `RussianTranslation/src/pwg_ru_translated.jsonl` between 17:25 and 23:03 on 25-08-2026.** Exactly half the `<ab>Instr.</ab>` occurrences (239/478) became `<ab>Ins.</ab>`, plus `Akk.`→`Acc.` and trailing-dot insertions in `zz_nws`/`zz_sch`/`zz_pw` sub-cards; the [`pwg-ru-data/tm/`](https://github.com/gasyoun/pwg-ru-data/tree/main/tm) mirror (H3500's 11 598-row state) is uniform `Instr.`, and no script in SanskritLexicography, pwg-ru-data or the H3361 window dir writes `Ins.`. The repo canon runs the other way ([`pwg_ab.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ab.py) `RENAME_ALIASES = {'Ins.': 'Instr.'}`), so render is unaffected but the store is half-normalised away from its own canonical label and the mirror is one window (+18 ids) and one rewrite behind.
Why it matters: refreshing the mirror from src cements an unowned half-rewrite; re-normalising src from the mirror discards a change someone may have intended. Either way the released TM pack must not be cut from a store whose label set is non-uniform.
Blocker: no writer identified; no provenance stamp changed on the 289 rows (only `ru`).
How to close: a human should decide the canonical case-label set (`Instr.` per `pwg_ab.py`, or the Latin `Ins.`/`Acc.` family); then run the chosen normalisation over the WHOLE store with a ledger row, refresh the mirror, and re-run [`audit_store_gates.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/audit_store_gates.py) to prove `changed_ru=0`.
> **Source:** [FINDINGS §589](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) · [reports/PWG_RU_TRANSLATION_STORE_AUDIT_27-08-2026.md §3](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/PWG_RU_TRANSLATION_STORE_AUDIT_27-08-2026.md) · [H3590](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3590-Fable_RussianTranslation_pwg-ru-translation-store-audit_27.08.26.md) (Fable 5 `claude-fable-5`, 27-08-2026)

### §17. Nothing gates a *promoted* pwg_ru fragment on its own surface form — untranslated German and translated `<ab>` tokens both reached the promoted tier
> **CLOSED 28-08-2026 — graduated to [FINDINGS §601](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).** [H3644](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3644-Grok_SanskritLexicography_pwg-ru-gaps17-defect-repair_28.08.26.md) (Grok 4.6 `grok-4.6`) added `GLOSS-DE-RESIDUE` and `AB-MUTATED` to [`pwg.tm.gate.v1`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_gates.py). Census of the frozen H2684 n=400 sample: **6 GLOSS-DE-RESIDUE** (includes `upakrama` / `AtmasAt`) **+ 81 AB-MUTATED** (includes `taruRa`; dominated by `recurring_formula` expansions such as `<ab>demin.</ab>` → `<ab>уменьш.</ab>`). The predicates now fail promotion; the dump is unchanged.
🟡 **We do NOT know how many promoted Wave-1/2 fragments carry source-language residue or a translated metalanguage abbreviation, because no gate ever asks.** Two of the ten H2684 serious-error rows are exactly this: `upakrama` 4〉 and `AtmasAt` reached **promoted** while still carrying untranslated `{%Antritt, Anfang, Beginn%}`, `{%beginnt%}` and `{%an sich, zu sich, auf sich%}` spans, and `taruRa` reached promoted with `<ab>v. a.</ab>` rendered as `<ab>т. е.</ab>` — against the standing house convention that `<ab>` tokens are copied verbatim, never expanded. Both are one-line mechanical predicates on the target string alone; neither exists.
Why it matters: these need no judge, no model and no source comparison — a German `{%…%}` span in a Russian target, and an `<ab>` target differing from its `<ab>` source, are decidable by inspection. Every such row that reaches promoted is a defect the expensive independent gate has to spend its sample budget rediscovering, and the H2684 sample says at least 3 of 400 promoted rows are of this kind.
Blocker: none technical — the predicates are trivial; the gate would be a Wave-2 write, which [H2877](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2877-Opus_RussianTranslation_pwg-tm-w1-serious-error-10-repair_16.08.26.md) was explicitly fenced against making.
How to close: add both assertions to `pwg.tm.gate.v1` — promotion requires zero German `{%…%}` spans in the target, and every `<ab>…</ab>` target byte-identical to its source — then run them over the promoted tier as a census and graduate the count to a FINDINGS row.
> **Source:** [pwg_ru/PWG_TM_W1_SERIOUS10_TAXONOMY_REPAIR_27-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/PWG_TM_W1_SERIOUS10_TAXONOMY_REPAIR_27-08-2026.md) · [FINDINGS §590](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) · [H2877](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2877-Opus_RussianTranslation_pwg-tm-w1-serious-error-10-repair_16.08.26.md) (Opus 5 `claude-opus-5`) · [PR #1911](https://github.com/gasyoun/SanskritLexicography/pull/1911). — SanskritLexicography · 2026-08-27

### §18. The fragmentizer splits DISCONTINUOUS glosses at `<is>` boundaries, orphaning fragments that cannot be translated at all
🟠 **We do NOT know how many pwg_ru gloss fragments are half of a gloss whose other half sits across an `<is>`…`</is>` span.** PWG `viSveSa` 2 reads `{%die%} <is>Viśve Devāḥ</is> {%zur Gottheit habend%}` — ONE gloss, "having the Viśve Devāḥ as deity". [`pwg_tm_fragmentize.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_fragmentize.py) emits `{%die%}` as a standalone `definition_gloss`, a bare German definite article with no lexical content. Russian has no articles, so **no faithful word-level target exists**, and [H3628](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3628-Opus_RussianTranslation_pwg-tm-w1-serious10-translate_28.08.26.md) measured all three candidates against the independent judge: inventing a word is the original H2684 serious defect, eliding to `{%%}` scores `sense_absent_or_inverted` (serious), and keeping the German scores `german_residue` (non-serious). No option is correct; the least-bad one was kept.
Why it matters: every such fragment is permanently unpromotable, and the pipeline cannot tell the difference between "this gloss was translated badly" and "this is not a gloss". One row in a 400-sample cost the fidelity floor 0.25 points; the population is unmeasured, and any `<is>`-interrupted gloss in PWG produces the same shape — `<is>` marks source/siglum text, which is common inside definitions.
Blocker: none technical — a census is a grep over the source side; the repair is a fragmentizer change, and re-fragmenting is a Wave-2+ act.
How to close: count source-side glosses whose `{%…%}` spans are separated only by an `<is>…</is>` run, graduate the number to a FINDINGS row, then rejoin those spans into one fragment BEFORE fragmenting so the gloss is translated as a unit.
> **Source:** [pwg_ru/PWG_TM_W1_SERIOUS10_TRANSLATED_GATE_28-08-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/PWG_TM_W1_SERIOUS10_TRANSLATED_GATE_28-08-2026.md) · [H3628](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3628-Opus_RussianTranslation_pwg-tm-w1-serious10-translate_28.08.26.md) (Opus 5 `claude-opus-5`). — SanskritLexicography · 2026-08-28
> **CLOSED 31-08-2026 — graduated to [FINDINGS §619](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).** [H3753](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3753-Sonnet_SanskritLexicography_pwg-fragmentizer-rejoin_30.08.26.md) (Sonnet 5 `claude-sonnet-5`) censused the live TM publication (2,392 records / 11,129 senses): **73 `<is>`-interrupted gloss events in 58 senses across 53 records**, then rejoined those spans into one `{%...%}` fragment before extraction (`_rejoin_is_interrupted_glosses` in [`pwg_tm_fragmentize.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_fragmentize.py)), RED-pinned on the `viSveSa` case. Live re-fragmentize: `definition_gloss` 15,781 → 15,708, total fragments 112,133 → 112,060 (−73, exact). Re-fragmenting/re-promoting the existing store stays Wave-2+, out of scope here.

## ⚙️ Auto-seeded candidates (unconfirmed — `seed_gaps.py`, 08-07-2026)

Surfaced by [`seed_gaps.py`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/seed_gaps.py) as a set-difference over the [kosha manifest](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json): datasets that exist but carry **no** FINDINGS row measuring them. These are `⚙️ auto` **candidates** — a human confirms (→ `✍️`, promote to FINDINGS once measured) or deletes. Row counts are the manifest's; the "why it matters" is a first pass to be sharpened.

### §7. `dcs-stem-cooccurrence-full` (353,352 stem-pair rows) is uncharacterised

> **GRADUATED 27-07-2026 → [FINDINGS §488](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) (stem co-occurrence degree distribution). H1735 Grok 4.5 (grok-4.5). Do not re-measure; residual open work is only what the finding still flags.**
🟡 ⚙️ **We have the full Sanskrit-stem co-occurrence table (353,352 pairs, IDs 1–222342) but NO FINDINGS row on what its network structure shows.**
Why it matters: a corpus-wide collocation graph would ground compound-formation, synonym-cluster, and semantic-field claims that are currently asserted per-lemma; feeds any distributional-semantics analysis.
Blocker: no tool — needs a graph/statistics pass (degree distribution, top collocates, hapax rate), not a row count.
How to close: load the pair table, compute the obvious network statistics, append a FINDINGS row; owner VisualDCS.
↔ Interlinks: [RECIPES §2](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) (DCS↔CDSL crosswalk) is the join a collocation graph would enrich into dictionary-grounded semantic fields · [GLOSSARY "form_key"](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md) is the keying the stem-pair rows must share to align.
> **Source:** manifest `dcs-stem-cooccurrence-full` (H291) · [kosha](https://github.com/gasyoun/kosha) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · auto (seed_gaps.py)

### §8. DCS syntagmatic collocation tables (Прил. 6 + 7) are unanalysed

> **GRADUATED 27-07-2026 → [FINDINGS §489](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) (sintagmatic appendix-6 nested in appendix-7). H1735 Grok 4.5 (grok-4.5). Do not re-measure; residual open work is only what the finding still flags.**
🟡 ⚙️ **We have the per-lemma collocate tables — all-corpus (`dcs-sintagmatic-appendix7`, 82,800 rows) and per-historical-period (`dcs-sintagmatic-appendix6-periods`, 19,076 rows, 7 files) — but NO FINDINGS row comparing them.**
Why it matters: the period-split vs all-corpus pair is exactly the data to test whether collocations are epoch-stable (the varga question §62, but at the lexical layer); a genuine diachronic-collocation finding.
Blocker: no tool — needs a per-period vs all-corpus diff; the appendix7 copy also has a byte-different UTF-16LE Cyrillic twin (H291) to dedup first.
How to close: align the period files against the all-corpus table, measure collocation drift; owner VisualDCS.
↔ Interlinks: [CONTRADICTIONS §2](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md) is the same epoch-stability question one layer up (vargas) whose χ² method this reuses at the lexical layer · [RECIPES §4](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) (varga diachrony) is the diachronic-comparison pass to mirror.
> **Source:** manifest `dcs-sintagmatic-appendix7` / `dcs-sintagmatic-appendix6-periods` (H291) · [kosha](https://github.com/gasyoun/kosha) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · auto (seed_gaps.py)

### §9. `heritage-forms-crosswalk-extras` disagreement classes are uncounted

> **GRADUATED 27-07-2026 → [FINDINGS §490](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) (Heritage×kosha disagreement classes). H1735 Grok 4.5 (grok-4.5). Do not re-measure; residual open work is only what the finding still flags.**
🟡 ⚙️ **We have the Heritage form-level crosswalk extras (1,037,239 rows, incl. a `heritage_forms_oracle_disagreements` form→disagreement-class table) but NO FINDINGS row on how often Heritage and kosha disagree, or on what.**
Why it matters: the disagreement rate + its classes are the missing quality metric for the Heritage morphology witness ([GAPS §3](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md)); tells us whether to trust Heritage forms as an oracle.
Blocker: data tier — `restricted` (Heritage LGPLLR composition), so the count is publishable but the rows aren't public.
How to close: tally the disagreement-class distribution, append a FINDINGS row (rate only); owner SanskritLexicography HeadwordLists.
↔ Interlinks: [ASSUMPTIONS §1](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) (DCS lemma == CDSL headword) is the join whose quality this disagreement rate would quantify · [GLOSSARY "headword vs lemma"](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md) defines the form/lemma distinction the disagreement classes turn on.
> **Source:** manifest `heritage-forms-crosswalk-extras` (H291) · [kosha](https://github.com/gasyoun/kosha) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · auto (seed_gaps.py)

### §10. Which-dictionary routing benchmark has single-annotator gold, no κ
🟠 ⚙️ **The 24-scenario routing shared-task benchmark (`which-dictionary-routing-benchmark`) has single-annotator gold (Fable 5, one pass) — NO inter-annotator agreement measured over its 44-code answer space.**
> **PARTIAL 27-07-2026 → [FINDINGS §493](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) (Grok second pass κ=1.0; human IAA still open). H1745.**
Why it matters: a shared-task benchmark with no κ can't quantify its own gold reliability, which caps the credibility of any leaderboard result built on it (csl-guides `/about/shared-tasks`).
Blocker: needs a second independent annotation pass (see `/gold-adjudicate`), not just a rerun.
How to close: second-annotate the 24 scenarios, compute κ + a confusion table, append a FINDINGS row.
↔ Interlinks: [CONTRADICTIONS §7](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md) is the same "two independent passes disagree" reliability worry, there for a correlation instead of a gold set · [GLOSSARY "ls source map"](https://github.com/gasyoun/SanskritLexicography/blob/master/GLOSSARY.md) frames the dictionary-code answer space κ would be computed over.
> **Source:** manifest `which-dictionary-routing-benchmark` (H281) · [kosha](https://github.com/gasyoun/kosha)/[csl-guides](https://github.com/sanskrit-lexicon/csl-guides) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · auto (seed_gaps.py)

### §11. `dcs-verb-form-frequency-prelim` is flagged preliminary, never finalised

> **GRADUATED 27-07-2026 → [FINDINGS §491](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) (verb-form prelim is unlabeled XLS). H1735 Grok 4.5 (grok-4.5). Do not re-measure; residual open work is only what the finding still flags.**
🟡 ⚙️ **The DCS verb-form frequency table (106 rows) is explicitly `preliminary` in the manifest — NO FINDINGS row, and no final version.**
Why it matters: verb forms are the top of the frequency dictionary (roots dominate §64/§16); a finalised verb-form frequency would directly feed the freq-first translation queue.
Blocker: unclear — the "preliminary" marker's reason isn't recorded (coverage? method?); needs the owner to state what makes it non-final.
How to close: identify the preliminary caveat, finalise or document why it can't be, append a FINDINGS row; owner VisualDCS.
↔ Interlinks: [ASSUMPTIONS §4](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) (a PWG-key worklist covers the universe) and [ASSUMPTIONS §3](https://github.com/gasyoun/SanskritLexicography/blob/master/ASSUMPTIONS.md) (the verb-root record) are the root-frequency premises a finalised verb-form table would feed the freq-first translation queue.
> **Source:** manifest `dcs-verb-form-frequency-prelim` (H291) · [kosha](https://github.com/gasyoun/kosha) · [08-07-2026](https://github.com/gasyoun/SanskritLexicography/commits/master?since=2026-07-08&until=2026-07-09) · auto (seed_gaps.py)

---

## Conclusions

- **The frontier sorts by blocker, not by topic.** §1–§3 wait on **data we don't have** (a VedaWeb outage, more correction eras, a walled Heritage download); §4–§6 wait on a **tool or method that doesn't exist yet** (gloss-level token adjudication, a schema-aware bundle parse, a validated Cyrillic→SLP1 onomasticon). Naming the blocker type is what tells a reader whether the gap needs a human download or a coding pass.
- **The 🟠 rows are the pipeline-unblockers.** §2 (error population), §3 (Heritage morphology), §6 (Cyrillic name keys), §10 (routing κ) each free a whole downstream — and Heritage as a third morphology witness (§3) is the single biggest unlock, gated only on a browser download + a licence @DECIDE.
- **§5, §7–§9, §11 graduated 27-07-2026 (H1735)** → FINDINGS §488–§492. Remaining auto-seed candidate: §10 (routing κ, needs second annotator). §1–§4, §6, §12–§14 stay open on data/method/external blockers.
- **Where they point:** a measured gap graduates to a [FINDINGS](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) row; several here would also settle a live [CONTRADICTIONS](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md) row (§1→§1, §8→§2) or ride a method already sketched in [RECIPES](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md).

### §12. Сундараканда: стихи песней 2 и 28 — пропуск оцифровки или воля переводчика?
🔴 ✍️ **Мы НЕ знаем, почему в оцифрованном переводе Леонова песнь 2 содержит 55/58 стихов, а песнь 28 — 19/20.**
Why it matters: блокирует полный печатный мастер тома ЛП ([BOOK_BUILD_REPORT.md](https://github.com/gasyoun/CommentaryStrategies/blob/main/data/book/BOOK_BUILD_REPORT.md) флагует обе песни); от ответа зависит, чинить оцифровку или фиксировать лакуну в аппарате.
Blocker: ответить может только М. Леонов — задача 1 его [issue №58](https://github.com/gasyoun/CommentaryStrategies/issues/58); руководство доставлено 10-07-2026, эскалация с 17-07-2026 (GTD @WAITING).
How to close: письмо Леонова → либо влить присланные стихи (агентная сессия), либо пометить «сознательное решение» в аппарате — и строка градуирует в FINDINGS/BOOK_BUILD_REPORT.
> **Source:** ✍️ H497 role-guide session, 10-07-2026 (Fable 5 `claude-fable-5`); registered via /artifact-propagate epistemic pass 11-07-2026.

### §14. Which `-ī` stems are the monosyllabic type, and which `-at` citations are genuine `-ant` stems?
🟠 ✍️ **We do NOT know, from DCS alone, how to split two declension classes the corpus pools.**
Why it matters: the `-ī` bucket of the nominal grid (E51, 65,332 tokens) mixes the polysyllabic devī/nadī type with the monosyllabic śrī/strī/dhī type, which takes different endings in the strong cases — so its per-cell ending list is a blend of two paradigms presented as one. The `-ant` bucket (48,074) likewise pools `-ant`/`-vant`/`-mant` with the master's own `-at`/`-vat`/`-mat` citations of the same stems (`bhagavant` and `bhagavat` are two `lemma_id`s), which is harmless for counting but hides how many distinct stems there really are.
Blocker: method/signal, not data — DCS tags case, number and gender and nothing about stem shape or syllable count; the citation form is all there is, and it is ambiguous exactly where the split matters. H1472 deliberately made no guess rather than encode a plausible-looking rule.
How to close: bring an external lexical signal — syllable count off a transliteration-aware segmenter for the `-ī` split, and a dictionary class tag (MW/PWG grammar field, or `lemma.grammar` extended) for the `-at`/`-ant` merge. Then re-bucket, re-run the G2 reconciliation, and the row graduates to a FINDINGS measurement of how big each true class is.
> **Source:** ✍️ [H1472](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1472-Opus_VisualDCS_nominal-paradigm-case-number-dashboard_22.07.26.md), 27-07-2026 (Opus 5 `claude-opus-5[1m]`); registered via /artifact-propagate epistemic pass.

### §15. BLI B1 gold pass-1 labels not yet collected — real P@1/P@5/MRR on the stratified frame is unmeasured
🟡 ✍️ **We do NOT yet have MG's pass-1 Russian equivalence labels for the 500-row stratified BLI frame, so H2402's per-stratum scorer has only ever run against a fixture.**
Why it matters: the whole point of [H2401](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2401-Fable_SanskritLexicography_bli-b1-gold-set-design_07.08.26.md)'s frame is a *measured* per-(band × POS) P@1/P@5/MRR for `corpus_lexicon.jsonl` — until labels land, ACL roadmap B1 has a scorer and a frame but no real number.
Blocker: human annotation — 500 cards, one sitting, via the review sheet.
How to close: MG votes [`sanskritlexicography-bli_gold_b1_500_review.html`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/build_bli_gold_b1_500_sheet.py) (row in [`Uprava/REVIEW_SHEETS_INDEX.md`](https://github.com/gasyoun/Uprava/blob/main/REVIEW_SHEETS_INDEX.md)), the decisions land as `gold_ru`, then [`bli_score_stratified.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/eval/bli_score_stratified.py) runs against the real frame instead of its fixture.
↔ Interlinks: closes once [H2402](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2402-Sonnet_SanskritLexicography_bli-b1-p1-mrr-scorer_07.08.26.md)'s scorer re-runs on real labels; pass-2 (frozen model as annotator 2) is a separate, later handoff per protocol §5.
> **Source:** ✍️ [H2551](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2551-Sonnet_SanskritLexicography_bli-b1-gold-annotation-sheet-500_10.08.26.md), 12-08-2026 (Sonnet 5 `claude-sonnet-5`); registered via /artifact-propagate.

---

### §13. No Russian Uttarakāṇḍa (or Kiṣkindhā, or Yuddha) exists — 1,765 PWG `R.` book-7 citations wait on a translator

🟠 ✍️ **We have NOT got, and cannot compute, a Russian translation of record for Rāmāyaṇa kāṇḍas 4, 6 and 7.**

Why it matters: `citation_tm` reuse is live for `R.` books 1–2 (Schlegel, direct) and 3–6 (Gorresio, via the H1656/H1689 content concordance), but every book-7 lookup — **1,765** plain `R.` citations in the full digitisation, 4.5% of the `R.` mass — returns `ru-translation-unpublished`. Kāṇḍa 6 is the sharpest case: H1656's map already pairs 2,295 Gorresio verses with yuddha loci, so the day a Russian yuddhakāṇḍa is ingested, 288 store references become reusable with **no further alignment work**.

Blocker: **external and human** — not data, not method. Gryntser's academic translation stopped after book 3; Leonov's covers Sundara. [RussianRamayana](https://github.com/gasyoun/RussianRamayana) `data/project-status.json`: book IV `blocked` (awaiting Serebryany's introduction), V `in-progress` (manuscript ~2027), VI `draft-ready` (~2029). Book VII is not in the pipeline.

How to close: watch the RussianRamayana project status; on ingest, key the RU against the **vulgate** numbering PWG cites rather than the critical text currently in `07_ramayana-uttarakanda.jsonl` ([CONTRADICTIONS §9](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)) — that choice decides whether any Bombay concordance is needed at all ([DEAD_ENDS §13](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md)).
> **Source:** [H1705](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1705-Opus_SanskritLexicography_ramayana-bombay-book7-etext_26.07.26.md) · [`pwg_ru/COVERED_TEXTS_RU.md` § kāṇḍas 4/6/7](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/COVERED_TEXTS_RU.md) · 27-07-2026 · Opus 5 1M `claude-opus-5[1m]`


_Dr. Mārcis Gasūns_
