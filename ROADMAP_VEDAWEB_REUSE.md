# ROADMAP — VedaWeb 2.0 data reuse across the Sanskrit Lexicon repos

_Created: 03-07-2026 · Last updated: 03-07-2026_

Scope ruled by M.G. 03-07-2026 (4 decisions, elicited in-session): **full breadth**
(validation + persistent feed + GRA crosswalk + meter/translation layers) · feed home =
**VisualDCS** · GRA crosswalk **queued** · roadmap doc lives **here** (the Sanskrit-data
hub repo). Authored by Fable 5 (`claude-fable-5`).

## Where we stand (prior-art verdict: PARTIAL)

**No VedaWeb data has been integrated anywhere yet.** What exists is the on-ramp:

- **Probe, confirmed turnkey 2026-06-29** —
  [FINDINGS.md §1](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md):
  live API at `vedaweb.uni-koeln.de/api` (FastAPI, OpenAPI at `/api/openapi.json`), four
  core Rig-Veda resources identified with IDs (Casaretto et al. 2025 accented word-split
  `66695e4a14f6d337f7788740`; lemmatization `679b7da2d5b833a67f64b3f7`; accented
  Scarlata–Widmer/Lubotsky text `66695c4b14f6d337f778873f`; Lubotsky padapāṭha
  `668ba4460b5942c9849a8684`), bulk `GET /api/resources/{id}/export`, **CC BY 4.0**,
  in-ecosystem (C-SALT/CDSL). §41: the platform migrated to Tekst; the old app was
  archived 16-02-2026 — the 2.0 API is the only live target.
- **First consumer built (rules side):** WhitneyRoots
  [crosswalk/accent_rules.json](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/accent_rules.json)
  (18 Whitney rules, 19-cell matrix,
  [v1.1.0](https://github.com/gasyoun/WhitneyRoots/releases/tag/v1.1.0)) + the
  Sonnet-runnable
  [docs/ACCENT_VALIDATION_SPEC.md](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/ACCENT_VALIDATION_SPEC.md),
  merged via [WhitneyRoots PR #23](https://github.com/gasyoun/WhitneyRoots/pull/23).
- **The gap:** zero exports on disk; no registered feed in
  [PROJECT_INTERLINKS.md](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md)
  (the spec caches to gitignored `scratch/`); GRA / meter / translation surfaces untouched.

## Phases

### Phase 0 — on-ramp ✅ DONE

Probe + rules + spec, as above. Handoff for the validation run exists:
[H063](https://github.com/gasyoun/Uprava/blob/main/handoffs/H063-Sonnet_WhitneyRoots_accent_validation_02.07.26.md).

### Phase 1 — bulk export → registered VisualDCS feed (unblocks everything) ✅ DONE 08-07-2026

- [x] One bulk export per core resource + full catalog → committed under
  [`VisualDCS/non-derived/vedaweb/`](https://github.com/gasyoun/VisualDCS/tree/main/non-derived/vedaweb)
  ([PR #17](https://github.com/gasyoun/VisualDCS/pull/17), Sonnet 5 `claude-sonnet-5`)
  with provenance [README](https://github.com/gasyoun/VisualDCS/blob/main/non-derived/vedaweb/README.md)
  (CC BY 4.0 attribution), registered in `non-derived/INDEX.md` + PROJECT_INTERLINKS.
  Handoff:
  [H096](https://github.com/gasyoun/Uprava/blob/main/handoffs/H096-Sonnet_VisualDCS_vedaweb_feed_export_03.07.26.md).

```
Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H096-Sonnet_VisualDCS_vedaweb_feed_export_03.07.26.md and execute it.
```

Sonnet-tier chat in `GitHub\VisualDCS`.

### Phase 2 — WhitneyRoots accent-validation run (already queued as H063)

- [ ] Score the 18 rules / 19 cells against attested RV accents; per-cell GO/NO-GO for
  the ZALIZNYAK a–f accent-axis emission
  ([ZALIZNYAK_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ZALIZNYAK_INDEX.md)).
  Independent of Phase 1 (its spec can hit the live API), but if the feed has landed,
  read from it instead.

```
Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H063-Sonnet_WhitneyRoots_accent_validation_02.07.26.md and execute it.
```

Sonnet-tier chat in `GitHub\WhitneyRoots`.

### Phase 3 — GRA (Grassmann) ↔ VedaWeb crosswalk — gated on Phase 1

- [ ] Check VedaWeb's own Grassmann linking first (consume, don't rebuild), then GRA
  headwords × lemmatization export → crosswalk TSV + coverage report in the VisualDCS
  feed dir; ONE `content-enhancement` issue on
  [sanskrit-lexicon/GRA](https://github.com/sanskrit-lexicon/GRA) proposing entry→RV
  deep links. Handoff:
  [H097](https://github.com/gasyoun/Uprava/blob/main/handoffs/H097-Sonnet_VisualDCS_gra_vedaweb_crosswalk_03.07.26.md).

```
Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H097-Sonnet_VisualDCS_gra_vedaweb_crosswalk_03.07.26.md and execute it.
```

Sonnet-tier chat in `GitHub\VisualDCS`.

### Phase 4 — meter + translation layers triage — gated on Phase 1 catalog

- [ ] Inventory what 2.0 actually serves (translations incl. a possible Elizarenkova
  Russian layer — verify, don't assume; metrical annotations; per-layer license), map
  each viable layer to its consumer (SanskritKaraoke meter,
  [RussianTranslation](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation)
  RU context, German translations as PWG gloss witness), GO/NO-GO memo; GO items get
  their own minted H### handoffs. Handoff:
  [H098](https://github.com/gasyoun/Uprava/blob/main/handoffs/H098-Sonnet_VisualDCS_vedaweb_meter_translations_triage_03.07.26.md).

```
Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H098-Sonnet_VisualDCS_vedaweb_meter_translations_triage_03.07.26.md and execute it.
```

Sonnet-tier chat in `GitHub\VisualDCS`.

## Dependency order

Phase 1 first (single API hit, everything downstream reads the feed). Phase 2 may run in
parallel with Phase 1 (self-contained spec). Phases 3 and 4 strictly after Phase 1.
Follow-on (outside this roadmap, already tracked): the a–f accent-mobility emission into
ZALIZNYAK_INDEX is gated on Phase 2's per-cell GO/NO-GO.

## Standing constraints

- **License:** CC BY 4.0 — every landed file attributes "VedaWeb 2.0, Universität zu
  Köln" + the specific annotation resource (Casaretto et al. 2025 where applicable).
  Translation layers may carry their own terms — Phase 4 verifies per layer.
- **Advisory only:** VedaWeb-derived signal is never written into reviewed/human data
  (spines, `headword_index.tsv`, app data) — the I/VI accent-collapse lesson.
- **API politeness:** bulk exports over per-form queries; cache; back off on 429.
- **Provenance:** every executing session states model tier + exact version per step.

_Dr. Mārcis Gasūns_
