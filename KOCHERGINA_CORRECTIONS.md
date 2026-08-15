# Kochergina 1987 — tracked corrections

_Created: 15-08-2026 · Last updated: 15-08-2026_

Corrections to **В. А. Кочергина, Санскритско-русский словарь (1987)** and to the
learnsanskrit.ru dictionary derived from it. Created under
[H798](https://github.com/gasyoun/Uprava/blob/main/handoffs/H798-Sonnet_SanskritLexicography_h779-apply-okas-guda-sphic-decisions_12.07.26.md)
after [FINDINGS §539](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
established that no such store existed anywhere in the org.

## Why this file exists rather than a row in CORRECTIONS

[CORRECTIONS](https://github.com/sanskrit-lexicon/CORRECTIONS) is the project's correction
audit trail, but it is keyed by **CDSL dictionary codes** — its `dictionaries/`
tree and `cfr.tsv` cover `ACC … SKD`, the dictionaries Cologne publishes.
Kochergina 1987 is a third-party Russian dictionary Cologne does not host: it has
no code, no `dictionaries/` slot and zero `cfr.tsv` rows there (only a stray
29 006-line headword list,
[`Kochergina-1987_29007.txt`](https://github.com/sanskrit-lexicon/CORRECTIONS/blob/main/Kochergina-1987_29007.txt),
which carries headwords with no entry bodies and so cannot hold a correction).
This store is deliberately lightweight and lives in the repo that **consumes**
Kochergina, not in the one that corrects Cologne.

**This file corrects nothing automatically.** Kochergina is not ours to edit; these
are adjudicated findings *about* its entries, kept so that (a) work consuming
Kochergina glosses does not silently inherit a known-wrong sense, and (b) a future
report upstream to learnsanskrit.ru has a source of record.

## Who consumes Kochergina here

The **BLI B1 gold set** carries a `Kochergina` gloss on **500 of its 500 cards**
(sheet [`bli_gold_b1_500`](https://gasyoun.github.io/vote/sheets/bli_gold_b1_500.html),
handoff H2551), and that set feeds P@1/P@5/MRR scoring (H2402). A sense-level error
here propagates into gold and then into the retrieval metric — which is exactly why
the store was created now rather than deferred.

## Status vocabulary

- **recorded** — the correction is adjudicated and complete; nothing further is owed.
- **recorded (wording open)** — the defect is settled, the final Russian sense wording
  awaits a named cross-check.
- **refuted** — the proposed correction was checked and is *not* a defect. Kept
  deliberately: a refuted claim must not be re-raised as if new.

## Corrections

Source vote: sheet_id `uprava-nagari2013-okas-guda-sphic_4lemmas`, all four **approve**
(decided 2026-07-12T10:39:30Z; re-decided with added notes 2026-07-17T16:30Z).
Attestation evidence:
[Uprava/history/NAGARI_LIST_2013_ATTESTATION_VS_GLOSS_OKAS_GUDA.md](https://github.com/gasyoun/Uprava/blob/main/history/NAGARI_LIST_2013_ATTESTATION_VS_GLOSS_OKAS_GUDA.md).

| # | Lemma | Correction | Status | Consumer action |
|---|---|---|---|---|
| 1 | ओकस् `okas` | Sense «родина» is **unattested** — drop or flag it. Primary sense is «pleasure, delight» (RV-only); «dwelling / resting place» is secondary. | recorded (wording open) | Do not annotate «родина» as a valid Russian equivalent. Final wording of the primary sense awaits the Elizarenkova cross-check below. |
| 2 | ओक्य `okya` | Remove the logically impossible derived sense «связанный с родиной» (it inherits the unattested sense of row 1). Prefer «домашний, уютный» over the doubtful «родной». | recorded | Use «домашний, уютный»; treat «родной» as doubtful and «связанный с родиной» as invalid. |
| 3 | गुद `guda` | **Sense order:** кишки → (толстая кишка) → анус. «Анус» stays **secondary**, on PWG + Borissov + KEWA/EWA (Mayrhofer); the Vasmer Slavic-cognate etymology does **not** promote it to primary. | recorded (wording open) | Order senses intestines-first. Awaits the Druzhinin cross-check below before the Ayurvedic-register wording is final. |
| 3b | गुद `guda` — gender | Proposed «fix gender m.pl. → f.pl. (RV 10.163.3)». **REFUTED** by H779's canonical re-verification: Kochergina already carries a separate `gudā` f. entry, so there is no gender defect to fix. | refuted | None. Do not re-raise; the f. form is already present as its own entry. |
| 4 | स्फिच् `sphic` / स्फिगी `sphigī` | Add the missing `sphic` lemma — **44 occurrences**, more frequent than `sphij`'s 6. Fix the cross-reference direction to `sphigī = sphij`, per Böhtlingk. | recorded | Treat `sphic` as a real headword; follow `sphigī → sphij`, not the reverse. |

## Open cross-checks (MG, 17-07-2026)

These were requested on the vote itself and are **research, not transcription** — each
needs a reading session, and neither blocks the rows above from being honoured.

| Lemma | Cross-check | Why it matters |
|---|---|---|
| `okas` | How **Elizarenkova** renders the RV loci in her published Ригведа translation. | The primary sense is RV-only, so her rendering is the strongest available Russian precedent and may be worth quoting directly in the applied note. |
| `guda` | How **Druzhinin** renders it in his Aṣṭāṅgahṛdaya translation. | Ayurvedic register is where the intestinal-vs-anal distinction is medically load-bearing. The 108-class Ayurveda transcript corpus is an available cross-check source. |

## Revision history

| Date | Change | Model |
|---|---|---|
| 15-08-2026 | Store created; four H798 votes recorded, `guda` gender logged as refuted, two cross-checks left open | Opus 5 (`claude-opus-5`) |

_Dr. Mārcis Gasūns_
