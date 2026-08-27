# ROADMAP — VedaWeb 2.0 data reuse across the Sanskrit Lexicon repos

_Created: 03-07-2026 · Last updated: 27-08-2026_

> **Truth-pass 27-08-2026** (Grok 4.6 `grok-4.6`). Closed references checked against the combined registry. Kept in place ([FINDINGS §475](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) clause 3). Not archived.

Scope ruled by M.G. 03-07-2026 (4 decisions, elicited in-session): **full breadth**
(validation + persistent feed + GRA crosswalk + meter/translation layers) · feed home =
**VisualDCS** · GRA crosswalk **queued** · roadmap doc lives **here** (the Sanskrit-data
hub repo). Authored by Fable 5 (`claude-fable-5`).

## Where we stand (prior-art verdict: COMPLETE — all roadmap phases done)

Phases 0–4 are closed. Hub surfaces that still consume the results (ZALIZNYAK a–f
emission, Karaoke meter seeds, Elizarenkova RU witness, PWG gloss witness) live
**outside** this roadmap and are tracked on their own handoffs.

- **Probe + feed + GRA crosswalk + rights + accent validation** — all landed (see
  phases below). Core VisualDCS feed:
  [`VisualDCS/non-derived/vedaweb/`](https://github.com/gasyoun/VisualDCS/tree/main/non-derived/vedaweb).
- **Accent rules + validation:** WhitneyRoots
  [crosswalk/accent_rules.json](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/accent_rules.json)
  + [crosswalk/accent_validation.json](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/accent_validation.json)
  + [docs/ACCENT_VALIDATION_REPORT.md](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/ACCENT_VALIDATION_REPORT.md)
  — **17/19 cells GO, 0 NO-GO** ([PR #24](https://github.com/gasyoun/WhitneyRoots/pull/24),
  T8c resolved [PR #29](https://github.com/gasyoun/WhitneyRoots/pull/29) / H115).

## Phases

### Phase 0 — on-ramp ✅ DONE

Probe + rules + spec, as above. Handoff for the validation run exists:
[H063](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H063-Sonnet_WhitneyRoots_accent_validation_02.07.26.md).

### Phase 1 — bulk export → registered VisualDCS feed (unblocks everything) ✅ DONE 08-07-2026

- [x] One bulk export per core resource + full catalog → committed under
  [`VisualDCS/non-derived/vedaweb/`](https://github.com/gasyoun/VisualDCS/tree/main/non-derived/vedaweb)
  ([PR #17](https://github.com/gasyoun/VisualDCS/pull/17), Sonnet 5 `claude-sonnet-5`)
  with provenance [README](https://github.com/gasyoun/VisualDCS/blob/main/non-derived/vedaweb/README.md)
  (CC BY 4.0 attribution), registered in `non-derived/INDEX.md` + PROJECT_INTERLINKS.
  Handoff:
  [H096](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H096-Sonnet_VisualDCS_vedaweb_feed_export_03.07.26.md).

```
Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H096-Sonnet_VisualDCS_vedaweb_feed_export_03.07.26.md and execute it.
```

Sonnet-tier chat in `GitHub\VisualDCS`.

### Phase 2 — WhitneyRoots accent-validation run — ✅ DONE 03-07-2026 (H115 polish 05-07-2026); hub tick 01-08-2026

- [x] Score the 18 rules / 19 cells against attested RV accents; per-cell GO/NO-GO for
  the ZALIZNYAK a–f accent-axis emission
  ([ZALIZNYAK_INDEX.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ZALIZNYAK_INDEX.md)).
  **Result: 17/19 cells GO, 2 measurement-only (thin evidence), 0 NO-GO** — ZALIZNYAK a–f
  emission cleared on the GO cells. `T8c·oxytone` resolved to 100% by H115 (rule gap for
  pratyáñc-type añc-compounds, not lemma noise). Deliverables:
  [`crosswalk/accent_validation.json`](https://github.com/gasyoun/WhitneyRoots/blob/main/crosswalk/accent_validation.json) +
  [`docs/ACCENT_VALIDATION_REPORT.md`](https://github.com/gasyoun/WhitneyRoots/blob/main/docs/ACCENT_VALIDATION_REPORT.md),
  landed via [WhitneyRoots PR #24](https://github.com/gasyoun/WhitneyRoots/pull/24)
  (Sonnet 5 `claude-sonnet-5`) + follow-up
  [WhitneyRoots PR #29](https://github.com/gasyoun/WhitneyRoots/pull/29) / H115.
  FINDINGS §1 + §54 via [SanskritLexicography PR #104](https://github.com/gasyoun/SanskritLexicography/pull/104).
  Handoff:
  [H063](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H063-Sonnet_WhitneyRoots_accent_validation_02.07.26.md)
  (archived ✅). Hub checkbox was stale until
  [PR #951](https://github.com/gasyoun/SanskritLexicography/pull/951); summary polish +
  COMPLETE verdict under
  [H2099](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2099-Grok_SanskritLexicography_vedaweb-phase2-tick_01.08.26.md)
  (`/drain tier 1`, Grok 4.5).

🔴 EXECUTED: [H063-Sonnet_WhitneyRoots_accent_validation_02.07.26.md](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H063-Sonnet_WhitneyRoots_accent_validation_02.07.26.md)

### Phase 3 — GRA (Grassmann) ↔ VedaWeb crosswalk — ✅ DONE 08-07-2026

- [x] VedaWeb's own Grassmann linking (`id_gra`) confirmed to equal the Grassmann `<L>`
  entry number in `csl-orig/v02/gra/gra.txt` — crosswalk built entirely from local data,
  no text-matching needed. Landed:
  [`gra_vedaweb_crosswalk.tsv`](https://github.com/gasyoun/VisualDCS/blob/main/non-derived/vedaweb/gra_vedaweb_crosswalk.tsv) +
  [`GRA_CROSSWALK.md`](https://github.com/gasyoun/VisualDCS/blob/main/non-derived/vedaweb/GRA_CROSSWALK.md)
  ([PR #18](https://github.com/gasyoun/VisualDCS/pull/18), merged). Coverage: 9,945/12,785
  GRA entries (77.8%), 9,475/11,108 unique headwords (85.3%) attested ≥1× in RV. Issue open:
  [sanskrit-lexicon/GRA#52](https://github.com/sanskrit-lexicon/GRA/issues/52)
  (`content-enhancement`, Major Enhancements milestone). Finding logged:
  [FINDINGS.md §72](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
  (renumbered from §63 on 11-07-2026).
  Handoff: [H097](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H097-Sonnet_VisualDCS_gra_vedaweb_crosswalk_03.07.26.md).

```
Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H097-Sonnet_VisualDCS_gra_vedaweb_crosswalk_03.07.26.md and execute it.
```

Sonnet-tier chat in `GitHub\VisualDCS`.

### Phase 4 — meter + translation layers triage — ✅ DONE 08-07-2026, rights CONFIRMED same day

- [x] Full 36-layer inventory confirmed (Elizarenkova Russian layer real, 10,551
  Cyrillic-text stanzas; a VedaWeb-generated metrical-scansion layer with per-pada
  long/short marks + meter-type label, both sample-exported and field-mapped). **Rights
  finding: only 2/36 catalog resources carry an explicit `license` field** — the blanket
  "CC BY 4.0 for everything" framing above (Standing constraints) was an unverified
  assumption at triage time; see
  [FINDINGS.md §73](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
  (renumbered from §64 on 11-07-2026).
  Triage originally parked all 4 meter/translation candidates DECIDE pending confirmation
  (Elizarenkova RU explicitly in-copyright to ~2078, Renou to ~2036). Full table + per-
  consumer effort estimates:
  [`VisualDCS/non-derived/vedaweb/LAYERS_TRIAGE.md`](https://github.com/gasyoun/VisualDCS/blob/main/non-derived/vedaweb/LAYERS_TRIAGE.md).
  Handoff: [H098](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H098-Sonnet_VisualDCS_vedaweb_meter_translations_triage_03.07.26.md).
- [x] **Rights confirmed same day** — [H359](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H359-Sonnet_Uprava_vedaweb_rights_outreach_send_08.07.26.md)'s
  outreach email to VedaWeb (Prof. Kölligan/Reinöhl) got an explicit written reply: all 4
  candidate layers (Metrical Data 2024, Elizarenkova RU, Geldner de, Grassmann de)
  confirmed **CC BY 4.0**, same terms as H096's already-landed layers — retroactively
  confirming H096's blanket claim too. VedaWeb also confirmed the 34-null-license gap is a
  metadata omission, not an absence of rights, and will backfill it. Consumer handoffs
  minted: [H360](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H360-Sonnet_SanskritKaraoke_vedaweb_metrical_verse_seeds_08.07.26.md)
  (SanskritKaraoke meter), [H361](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H361-Sonnet_SanskritLexicography_vedaweb_elizarenkova_ru_witness_08.07.26.md)
  (RussianTranslation RU witness), [H362](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H362-Sonnet_VisualDCS_vedaweb_geldner_grassmann_pwg_gloss_08.07.26.md)
  (PWG German gloss witness).

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
