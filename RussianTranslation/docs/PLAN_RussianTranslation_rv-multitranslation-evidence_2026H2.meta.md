# PLAN_RussianTranslation_rv-multitranslation-evidence_2026H2 — metadoc

_Created: 29-07-2026 · Last updated: 29-07-2026_

Companion record for [PLAN_RussianTranslation_rv-multitranslation-evidence_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/docs/PLAN_RussianTranslation_rv-multitranslation-evidence_2026H2.md)
and its four layer docs (ROADMAP / ARCHITECTURE / IMPLEMENTATION / VERIFICATION).

## Purpose

The execution-ready `/ask` plan for the **Rig-Veda multi-translation evidence layer**: a
lemma-keyed join of the Ṛgveda against Grassmann 1876–77, Geldner 1951–57, Elizarenkova
1989–99 and Griffith 1896, a typed divergence taxonomy over them, an advisory word-level
alignment layer, and the wiring that makes all of it visible to the PWG→RU and PWG→EN
pipeline. It is the doc the wave-1 execution handoffs point at.

## Audience

A fresh execution agent (Sonnet for wave 1a, Opus for wave 1b) running unattended, and a human
for the single gated fork (the 100-stanza divergence-class vote).

## Provenance

- Authored 29-07-2026 by Opus 5 (`claude-opus-5[1m]`) via the `/ask` skill.
- Interview: 4 rounds (goal/ownership/scope/EN · architecture forks · rights/wisdomlib/format/scale ·
  verification + autonomy) — 17 rulings, all in the PLAN decisions table.
- Audit basis: direct inspection of the committed feeds, not inference. Every count in
  ARCHITECTURE §1 and VERIFICATION §2 was measured on 29-07-2026 by reading
  `VisualDCS/non-derived/vedaweb/*.json`, `rvlinks/RV_sa-hn-ru-de-en_1.html`, the
  SamudraManthanam commentary files and `Uprava/PROJECT_INTERLINKS.md`.
- Prior art traced to H096 (VedaWeb bulk export), H097 (GRA crosswalk), H362 (PWG gloss
  crosswalk + the two German translations), H361 (Elizarenkova), H522 (Type-D concordance),
  H1457 A3/A5 (the alignment gate and the Vecalign pilot).

## Key decisions this plan rests on

Deliverable = both, strictly sequential (working layer first, citable dataset second); owner =
`RussianTranslation`, not VisualDCS; scope = Ṛgveda only until it is entirely finished, then
Atharvaveda; EN = Griffith now, Jamison–Brereton later as gold; granularity = deterministic
spine + advisory word-level layer; divergence = typed taxonomy; pipeline entry = all three
points at once and not for Russian only; rights = not a blocker, everything in the open repo;
Renou = locus index + 368 quotations now, full EVP not before 2027; wisdomlib = all four roles;
storage = normalised JSONL + generated TSV; scale = pilot → human gate → full run. Full table
in the PLAN.

## What this plan discovered that changed its own design

Three audit findings materially reshaped the plan and are worth keeping visible:

1. **The dictionary anchor already exists per token.** `lemmatization.json`'s
   `transformContext` carries `id_gra`, `id_pwg` and `id_mw` on each of the 164,758 Ṛgvedic
   tokens. The planned "attach dictionary IDs" step collapsed into a field read.
2. **Geldner is missing exactly four stanzas (RV 10.106.5–8).** The `omitted_by_one` class has
   known ground truth before any model runs, which turned it from a taxonomy label into a
   regression test.
3. **The denormalised data model would have been ~65 MB in git.** Measured average stanza
   lengths (152–171 characters × four translations × 164,758 occurrences) forced the split into
   a stanza table plus a lemma-occurrence table, ~18 MB.

## Improvement backlog (ranked)

1. After spike S1, replace the "unmatched Griffith loci ≤ 2 %" assumption in VERIFICATION §4
   with the measured number.
2. After the 300-token gold, re-examine whether the `agreement >= 0.20` gate from
   [ALIGN_GATE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ALIGN_GATE.md)
   transfers to Vedic — it was calibrated on 30 rows of mined running text with one negative.
3. If the divergence gate fails at 80 %, record the collapsed 3-class taxonomy here as the
   ruling rather than leaving the 5-class version standing as if it had been validated.
4. When wave 2 opens, write the rights-subsetting step as its own spec — R10 deferred it, it
   did not remove it.
5. When wave 3 (Atharvaveda) opens, check VedaWeb's AV coverage first; this plan asserts only
   that `avlinks` has the text, not that a translation layer exists to join to.

## Limitations

- The word-level layer's feasibility is genuinely unproven for Vedic. LaBSE's weakness on
  transliterated Sanskrit is a measured finding in the repo already; the 85 %-per-language bar
  is a real gate that layer B may not clear, and the plan is built to survive that.
- The divergence taxonomy's separability (`lexical_variant` vs `semantic_shift`) is assumed, not
  demonstrated. Spike S2 exists precisely because it might not hold.
- Renou locus resolution runs against plain-text commentary with no markup; the unresolved
  share is unknown until the parser runs.
- The plan follows a human ruling that rights do not gate the work and that everything lands in
  one open repo. The consequences are recorded in PLAN §5 and risk K6 rather than argued;
  wave 2's DOI release will meet a `/publish-safety-check` gate that this posture does not
  pre-clear.

## Revision history

| Date | Change | By |
|---|---|---|
| 29-07-2026 | Created — `/ask` interview (4 rounds, 17 rulings) + full audit; five layer docs authored; handoffs H1843/H1844 minted | Opus 5 (`claude-opus-5[1m]`) |

_Dr. Mārcis Gasūns_
