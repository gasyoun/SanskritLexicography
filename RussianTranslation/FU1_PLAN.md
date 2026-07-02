# FU1 — full DCS-frequency EN run: locked plan (2026-06-30)

_Created: 30-06-2026 · Last updated: 02-07-2026_

Resume spec for the PWG→English **bulk** follow-up (FU1) after FU2 (audit gate) and FU3
(tri-lingual merge) shipped. **Real Max-quota spend** — run in a Max/Workflow session at
**≤3-wide concurrency**. All six design decisions below are MG-locked (2026-06-30); do not
re-litigate. This file is the *decision/rationale* record; the step-by-step **execution runbook**
is [`HANDOFF_2026-06-30_pwg_en_fu1_run.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/HANDOFF_2026-06-30_pwg_en_fu1_run.md). Parent:
[`HANDOFF_2026-06-30_pwg_en_followups.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/HANDOFF_2026-06-30_pwg_en_followups.md).

## Locked decisions

| # | Decision | Choice | Consequence |
|---|---|---|---|
| 1 | Architecture | **Bilingual for new roots, EN-only for already-RU'd** | FU1's scope is exactly the already-RU'd roots → **this tranche is EN-only + `promote_en.py` merge**. The bilingual single-pass (RU+EN in one workflow call, identical segmentation, one metadata set) is the standing policy for *future* freq roots beyond current RU coverage — adopt it the moment RU and EN extend together. |
| 2 | Model tier + version | **Sonnet 4.6 (`claude-sonnet-4-6`) generate + Opus 4.8 (`claude-opus-4-8`) judge** | Generate with `gen_opt_harness2.py --lang=en` (pins alias `model:'sonnet'` → resolved Sonnet 4.6); add an Opus 4.8 judge pass. Report tier **AND version** at every step, resolving the alias to its version (models change). Per [[feedback_state_model_tier]]. |
| 3 | Scope | **Match current RU coverage** | EN for the roots already in the store, no new RU work. Worklist below. |
| 4 | Validation | **Audit + Opus judge + human gold sample** | FU2 deterministic gate on all + Opus judge on all + a human-validated stratified gold sample with documented inter-annotator agreement (Cohen κ) and error rate. The citable-resource bar. |
| 5 | Provenance | **Full per-sense** | Each EN sense records model tier, Opus judge verdict + score, `generated_at`, harness SHA, and whether an MW reference was used. |
| 6 | Ground truth | **Faithful to the PWG German** | The gold standard is correct rendering of the German source sense. Monier-Williams is a **cross-check only**, never the standard (it is a different dictionary). PWG sense order is preserved (Renou-badge rule, never re-sort). |

## Scope worklist — 30 roots / 1,260 subcards / 5,259 sense rows

Already-RU'd roots with **no EN yet** (the 16 pilot roots are done; their store-only residue is
just ~22 nulls + a few key mismatches — backfill opportunistically, not a priority). None exceed
the 512 KB `scriptPath` limit (max 96 subcards), so **no `--keys` split is required**.

Freq order (run sequentially or ≤3 at a time):
`nI yA dA han car viS jYA vas hA vA diS mA vah iz muc su Ap jan banD man Sru siD vac ji paS brU laB jIv As gam`

| root | subcards | root | subcards | root | subcards |
|---|---:|---|---:|---|---:|
| nI | 96 | vA | 50 | banD | 31 |
| yA | 88 | diS | 48 | man | 29 |
| dA | 82 | mA | 41 | Sru | 28 |
| han | 78 | vah | 39 | siD | 28 |
| car | 71 | iz | 36 | vac | 28 |
| viS | 56 | muc | 34 | ji | 27 |
| jYA | 55 | su | 34 | paS | 27 |
| vas | 55 | Ap | 33 | brU | 23 |
| hA | 54 | jan | 33 | laB | 18 |
| | | | | jIv | 17 |
| | | | | As | 15 |
| | | | | gam | 6 |

**Cost estimate:** ≈ 1,260 cards × ~\$0.033/card (Step-1 Sonnet rate) ≈ **\$42 generation**, plus the
Opus judge pass. Confirm against live cost after the first 2–3 roots.

⚠️ **siD carries a known RU sense-dupe defect** (h1 parts pwg02 over-produce senses already in
pwg00/pwg03 — see `.ai_state.md`); the EN run will mirror it. Run the EN sense-dupe gate and expect
the same FAIL until the RU-side h1 dedup lands.

## Per-root loop (no deviation)

```sh
git rev-parse --abbrev-ref HEAD          # MUST be recover/slicec-top3-pat-ga-vad, not master
python src/pilot/root_window_status.py <root>            # confirm rootmap + masked inputs exist
python src/pilot/gen_opt_harness2.py <root> --lang=en --out=src/pilot/run_pilot_wf.en_<root>.js  # NB: --lang=en (with '='); space form silently falls back to RU
# → run via in-chat Workflow tool, ≤3-wide
python save_and_audit.py <root> <task-output-file> en    # runs audit_window_en.py (FU2), no --no-audit
```
Then once a slice of roots is done:
```sh
python src/promote_en.py                 # attach en + en_provenance onto the RU store rows
python src/annotate_dcs_freq.py          # re-attach dcs_freq (language-agnostic, idempotent)
```

## To BUILD before the Max run (no quota — agent-doable now)

1. **Opus EN judge** — an `en` analog of the RU judge. Rubric = **faithful to the PWG German**
   (does the `english` correctly render the `{%German%}` sense?), with markup/sigla preservation
   and sense-order integrity as hard sub-checks; MW divergence is a soft cross-check, never a
   fail. Per-sense verdict ∈ {ok, minor, wrong} + score + one-line reason. Stratified or full.
2. **Provenance-aware merge** — extend `promote_en.py` to attach, alongside `en`, an
   **`en_provenance`** block per row: `{model:'sonnet', judge:{model:'opus', verdict, score},
   generated_at, harness_sha256, mw_used:bool}` (mirrors the RU `provenance` block; keeps `en` a
   plain string so `export_interop.py` is unaffected). `review_status` stays `ai_translated`.
3. **Gold-sample harness** — stratified sampler over the EN store, strata = DCS freq band ×
   `source_type` × `stratum`, fixed seed, target n (propose ~300 senses for a tight CI on the
   error rate). Emits a blank reviewer sheet (de + en + headword, *MW hidden* to avoid anchoring)
   for MG + one second annotator, then a scorer computing **Cohen κ** and the point error rate
   with CI. Ground truth = faithful-to-German. Output a short METHODS note for the citable layer.

## Failure taxonomy — DharmaMitra crosswalk (documentation only, added 02-07-2026)

MG decision 02-07-2026: adopt DharmaMitra's failure-class vocabulary as shared terminology for this
rubric, both for internal alignment and — separately — for citation-grade use. Full mapping
(including which parts are citable vs. not) lives in
[`TAXONOMY_DHARMAMITRA.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/TAXONOMY_DHARMAMITRA.md).
No gate semantics change and no judging is re-run — this is vocabulary alignment on the existing
7-class rubric from the [S7 gold-sample judgment](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/FABLE_JUDGE_S7_2026-07-02.md#failure-classes-all-severities).

| our class | DharmaMitra alias (workshop-form vocabulary, internal use only) | published equivalent (citable: MQM/GEMBA-MQM) |
|---|---|---|
| `addition` | hallucinated or invented content | accuracy: addition |
| `mw-tm-contamination` | hallucinated or invented content (cross-source subtype) | accuracy: addition |
| `term-mistranslation` | vocabulary/terminology · ambiguous/polysemous terms | terminology / accuracy: mistranslation |
| `grammar` | grammar and syntax errors | fluency: grammar |
| `omission` | *(no form counterpart)* | accuracy: omission |
| `register-drift` | register/tone | fluency: register |
| `markup-loss` | *(no form or MQM counterpart — our own markup artifact)* | *(none)* |

DharmaMitra's form also names two document-level failure modes we don't yet score at
sense-row/card granularity — *context awareness across sentences* and *consistency/coherence across
a passage* — noted as future judge-pass candidates, not applied retroactively to FU1/S7 results.

## Done criteria

- All 30 roots EN-translated, FU2 audit run per root (0 hard flags target), EN merged with
  `en_provenance`, `dcs_freq` re-annotated.
- Opus judge run on all; verdicts inlined.
- Gold sample double-annotated, κ + error rate documented; G5 human review flips approved rows
  to `review_status='approved'` (only then does `export_interop.py` publish them).
