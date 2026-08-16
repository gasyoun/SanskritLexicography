# Kochergina 1987 — tracked corrections

_Created: 15-08-2026 · Last updated: 16-08-2026_

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
| 1 | ओकस् `okas` | Sense «родина» is **unattested** — drop or flag it. Final wording, settled against Elizarenkova (see § `okas` closure): primary **«привычное, излюбленное место; дом, обиталище»**; secondary, derived from it, **«отрада, удовольствие»**. | recorded | Annotate with «привычное (излюбленное) место, дом» first and «отрада, удовольствие» second; never «родина». |
| 2 | ओक्य `okya` | Remove the logically impossible derived sense «связанный с родиной» (it inherits the unattested sense of row 1). Prefer «домашний, уютный» over the doubtful «родной». | recorded | Use «домашний, уютный»; treat «родной» as doubtful and «связанный с родиной» as invalid. |
| 3 | गुद `guda` | **Sense order:** кишки → (толстая кишка) → прямая кишка, задний проход. «Анус» stays **secondary**, on PWG + Borissov + KEWA/EWA (Mayrhofer); the Vasmer Slavic-cognate etymology does **not** promote it to primary. **Register rider** (see § `guda` closure): in the classical Ayurvedic layer the secondary sense is the *only* one in use, and its Russian is «прямая кишка», not «анус». | recorded | Order senses intestines-first, but carry the register rider: for an Ayurvedic text read `guda` as «прямая кишка / задний проход», and expect `antra`/`sthūlāntra`/`pakvāśaya` — not `guda` — for «кишки». |
| 3b | गुद `guda` — gender | Proposed «fix gender m.pl. → f.pl. (RV 10.163.3)». **REFUTED** by H779's canonical re-verification: Kochergina already carries a separate `gudā` f. entry, so there is no gender defect to fix. | refuted | None. Do not re-raise; the f. form is already present as its own entry. |
| 4 | स्फिच् `sphic` / स्फिगी `sphigī` | Add the missing `sphic` lemma — **44 occurrences**, more frequent than `sphij`'s 6. Fix the cross-reference direction to `sphigī = sphij`, per Böhtlingk. | recorded | Treat `sphic` as a real headword; follow `sphigī → sphij`, not the reverse. |

## Cross-check closures (16-08-2026)

Both cross-checks MG requested on the vote (17-07-2026) were read against published
sources on 16-08-2026 under
[H2863](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2863-Opus_SanskritLexicography_kochergina-guda-druzhinin-crosscheck_16.08.26.md).
Neither re-opens the vote; both settle the Russian wording, and each **revises one premise
the vote carried forward**.

### `okas` — Elizarenkova, all 12 RV attestations

Source: the local **rvlinks** build,
[rvlinks/rvhymns/](https://github.com/sanskrit-lexicon/rvlinks/tree/main/rvhymns) — one file per
hymn, carrying Elizarenkova's Russian beside Geldner and Griffith, verse-granular, for all
1 028 hymns. Nothing was re-translated; every rendering below is hers as published.

| Locus | Form | Elizarenkova's Russian |
|---|---|---|
| [RV 1.66.3](https://sanskrit-lexicon.github.io/rvlinks/rvhymns/rv01.066.html#rv01.066.03) | `óko ná` | «приятен, как **привычное место**» |
| [RV 1.91.13](https://sanskrit-lexicon.github.io/rvlinks/rvhymns/rv01.091.html#rv01.091.13) | `svá okyè` | «как юноша в своем **доме**» |
| [RV 1.104.5](https://sanskrit-lexicon.github.io/rvlinks/rvhymns/rv01.104.html#rv01.104.05) | `óko ná ácchā sádanam` | «пришла в его (жилище), как к себе **домой**» |
| [RV 1.132.5](https://sanskrit-lexicon.github.io/rvlinks/rvhymns/rv01.132.html#rv01.132.05) | `okyàm` | «стремятся создать себе **дом** поэтические мысли» |
| [RV 1.173.11](https://sanskrit-lexicon.github.io/rvlinks/rvhymns/rv01.173.html#rv01.173.11) | `ókaḥ` | «пригоняет (бога) в **дом**» |
| [RV 2.19.1](https://sanskrit-lexicon.github.io/rvlinks/rvhymns/rv02.019.html#rv02.019.01) | `óko dadhe` | «**находил удовольствие**» |
| [RV 3.42.8](https://sanskrit-lexicon.github.io/rvlinks/rvhymns/rv03.042.html#rv03.042.08) | `svá okyè` | «чтобы ты пил сому в своем **доме**» |
| [RV 8.25.17](https://sanskrit-lexicon.github.io/rvlinks/rvhymns/rv08.025.html#rv08.025.17) | `pūrvā́ṇy okyā̀` | «старые **привычные** заветы» |
| [RV 8.49.3](https://sanskrit-lexicon.github.io/rvlinks/rvhymns/rv08.049.html#rv08.049.03) | `ánv okyàm` | «по **приятной привычке**» |
| [RV 8.72.14](https://sanskrit-lexicon.github.io/rvlinks/rvhymns/rv08.072.html#rv08.072.14) | `svám okyàm` | «знают свое **излюбленное место**» |
| [RV 9.86.45](https://sanskrit-lexicon.github.io/rvlinks/rvhymns/rv09.086.html#rv09.086.45) | `okyáḥ` | — (no Russian in the rvlinks build; Geldner «gern bleibend») |
| [RV 10.44.9](https://sanskrit-lexicon.github.io/rvlinks/rvhymns/rv10.044.html#rv10.044.09) | `okyàm` | «пусть будет тебе большое **удовольствие**» |

**Verdict.** «Родина» appears at **none** of the twelve. Elizarenkova's Russian occupies
exactly two poles — *привычное / излюбленное место, дом* (8 loci) and *приятная привычка,
удовольствие* (3 loci) — and RV 8.49.3 «по **приятной привычке**» puts both in one phrase,
which is why they are one sense and not two: the word names a **habitual place, and the
ease of being in it**. Her own note on RV 1.66.3 makes the same point from the other side,
glossing `óka-` as «привычное место» and linking it to `durókaśociḥ` «к чьему пламени
трудно привыкнуть».

**Premise revised.** Row 1 previously read «primary sense is *pleasure, delight* (RV-only);
*dwelling / resting place* is secondary» — an ordering taken from Böhtlingk's etymology
(√uc «привыкать»). Elizarenkova's translational practice **inverts** it: place-sense at 8
of 11 rendered loci, pleasure-sense at 3. The etymological priority stands as etymology;
it is not the priority a Russian **equivalent** should be listed in. Row 1 now leads with
the place-sense.

### `guda` — the Ayurvedic register

Two halves, and the disappointing half first.

**Druzhinin's Aṣṭāṅgahṛdaya translation was not found in the repos**, confirming the gap
the handoff flagged: it is in no repo under `GitHub/`. The 79-file Ayurveda course transcript set in
Uprava was searched and **does not name him anywhere** (0 hits across all 79 files), so no
term choice in it can be attributed to him. What that corpus *does* establish — and this
is reported as an anonymous AHS-teaching source, not as Druzhinin — is that its Russian
for the organ, in the basti/suppository passages where AHS uses `guda`, is consistently
**«прямая кишка»**; «кишки» is never used for that referent. Nothing further from
`stenogrammy/` is quoted or characterised here: it is 152-FZ personal data and this file is
public.

**Located the same day, and it changes nothing — for a reason worth recording.** MG
supplied the translation: it exists off-git as a live Google Doc (URL in the private hub,
[Uprava PROJECT_INTERLINKS](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md)
§ Corpus & morphology feeds — it is a third party's unpublished work in progress, so it is
not mirrored into this public repo). It is exactly the shape this kind of cross-check
wants: Devanagari → IAST → word-by-word Russian with each Sanskrit lemma in parentheses →
smooth Russian, 49 `ТЕКСТ` blocks. But it covers **Sūtrasthāna 1–4 only**
(`āyuṣkāmīya` · `dinacaryā` · `ṛtucaryā` · `roganutpādanīya`), and `guda` first occurs at
**Sū. 6**. Searched: **zero** occurrences in Devanagari, IAST, or Russian. Its single
anorectal mention is a footnote on *ānāha* rendering the region «область ануса» and
pointing the reader at AHS Nid. 7.46–52 — one of the chapters that *does* carry `guda`,
and one this edition has not reached.

So the corpus verdict below stands unchanged, and the residual narrows from *find the
translation* to *wait for it to reach Sū. 6, Nid. 7 or Cik. 8* — the chapters where the
word actually lives.

**And that wait is now cancelled.** MG, 16-08-2026: *«the translation will never reach
Cik. 8, it's too slow. So we can compare with the German and English translations only, but
no Russian.»* The Russian lane for AHS lexical cross-checks is therefore **closed**, not
pending — recorded as [DEAD_ENDS §14](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md),
the same species as its §13 (a plan waiting on a Russian translation that is not coming).

The replacement lane, and its honest state:

| Language | Source | Status |
|---|---|---|
| German | Luise Hilgenberg & Willibald Kirfel, *Vāgbhaṭa's Aṣṭāṅgahṛdayasaṃhitā: ein altindisches Lehrbuch der Heilkunde*, Leiden 1941 — the complete German | **Not held.** Not on disk, not on archive.org, in no hub. Acquisition-blocked. |
| English | [Dominik Wujastyk, Penguin 2003](https://en.wikipedia.org/wiki/Ashtanga_Hridayam) (ISBN 0-14-044824-1) | Held nowhere here, and **selected passages only** — not the whole text, so it may not reach the `guda` chapters either. |
| English | Srikantha Murthy, Krishnadas Academy — a complete English | **Candidate, bibliographically unverified** in this pass. Verify before planning on it. |

So German is the primary lane and both are acquisition-blocked. Because that is a real
stop rather than a quick read, it is carried as its own handoff rather than left as a line
here — see § On the German/English lane below.

**What is available today, at no acquisition cost,** is DCS's own lemma-gloss layer,
[`dcs-conllu/lookup/dictionary.csv`](https://github.com/gasyoun/dcs-conllu/tree/main/lookup)
(180 178 rows). It cannot give per-locus rendering — only a translation can — but it
independently reproduces the distinctions this closure established by hand:
`guda` mn "an intestine; entrail; rectum; anus", `gudā` f **"the bowels"** (= Elizarenkova's
«кишок»), `vaniṣṭhu` m "**the rectum**; Dickdarm" (confirming the §544 correction
mechanically), `pāyu` mn "**the anus**", `sthūlāntra` n "the larger intestine near the anus".
Recorded as [FINDINGS §546](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).
Note what that table shows: DCS's *gloss order* for `guda` is intestine-first, matching the
corrected Kochergina row, while AHS *usage* is anorectal throughout — the lexicon and the
register disagree exactly as the rider says.

**The corpus half is decisive on its own.** DCS's lemma-annotated Aṣṭāṅgahṛdayasaṃhitā
carries `guda` in **30 of its 120 files, 79 occurrences** (the handoff's «42 files» was an
over-count; corrected here from the annotation itself). Across all 79 the referent is the
**anorectal outlet**, never the intestines, and the text says so explicitly:

- `gudaḥ sthūlāntrasaṃśrayaḥ` (Nid. 7) and `sthūlāntrabaddhaḥ … gudaḥ` (Śār. 4) — the
  `guda` is *seated in / bound to* the large intestine, therefore **is not** it.
- `meḍhrayonigudair adhaḥ` (Nid. 3) — grouped with penis and vagina as a **lower orifice**.
- `gudaniḥsaraṇam`, `gudabhraṃśa`, `gudaṃ bhraṣṭaṃ … praveśayet` (Sū. 18, Cik. 9, Kalpa. 3)
  — **prolapse, and pushing it back in**. Only an outlet prolapses.
- `gude praṇihitaḥ snehaḥ`, `vartim asmai gude`, `gude nāḍyā vinirdhamet` (Kalpa. 5,
  Cik. 8) — the **enema/suppository route**.
- `arśāṃsi tasmād ucyante gudamārganirodhataḥ` (Nid. 7) — haemorrhoids named from
  obstruction of the *guda-passage*.

«Кишки» in that text is `antra` / `sthūlāntra` / `pakvāśaya` / `koṣṭha`, all of which occur
**contrastively alongside** `guda`.

**Verdict — corroboration and contradiction, split by register.** The vote's ruling holds
where it was made: in the Vedic layer Elizarenkova renders `gudā́bhyaḥ` at
[RV 10.163.3](https://sanskrit-lexicon.github.io/rvlinks/rvhymns/rv10.163.html#rv10.163.03)
as «из твоих **кишок**», so intestines-first is right for the entry as a whole. But in the
classical Ayurvedic layer the intestinal sense does not occur at all, and the Russian that
matches the usage is «прямая кишка» — a term the vote's «кишки → толстая кишка → анус»
chain skipped over. Hence the register rider on row 3 rather than a re-ordering.

**Premise corrected.** The attestation memo
[NAGARI_LIST_2013_ATTESTATION_VS_GLOSS_OKAS_GUDA.md](https://github.com/gasyoun/Uprava/blob/main/history/NAGARI_LIST_2013_ATTESTATION_VS_GLOSS_OKAS_GUDA.md)
records the 2013 thread as having Elizarenkova rendering `guda` «прямая кишка» at
RV 10.163.3. She does not: «прямая кишка» is her rendering of `vaniṣṭhóḥ` in the same pāda,
and `gudā́bhyaḥ` is «кишок». Geldner aligns the same way (`Därmen` / `Mastdarm`); Griffith
conflates them. This is a verse-granular-vs-pāda-granular misalignment of exactly the class
[H2850](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2850-Opus_SanskritLexicography_rv-citation-pada-alignment-elizarenkova-rvlinks_15.08.26.md)
exists to eliminate.

### On H2850

H2850's alignment was **not consumed, because it does not exist yet** — its registry row is
still open, no machinery has been built. What this pass did instead is use the *source*
H2850 names, the local rvlinks build, at pāda granularity by hand, and it confirms two
things for that handoff: the build covers all 1 028 hymns with Russian/German/English side
by side (so it, not the two-Mandala
[SamudraManthanam](https://github.com/gasyoun/SamudraManthanam/blob/main/Index/Updater/Data/01_rigveda.no_tags)
extract, is the right substrate), and RV 10.163.3 above is a ready-made worked specimen of
the misalignment it is meant to catch.

## Revision history

| Date | Change | Model |
|---|---|---|
| 15-08-2026 | Store created; four H798 votes recorded, `guda` gender logged as refuted, two cross-checks left open | Opus 5 (`claude-opus-5`) |
| 16-08-2026 | `okas` cross-check closed against Elizarenkova over all 12 RV attestations (rvlinks); row 1 → `recorded`, place-sense promoted over pleasure-sense, «родина» confirmed unattested | Opus 5 (`claude-opus-5`) |
| 16-08-2026 | `guda` cross-check closed against the DCS Aṣṭāṅgahṛdayasaṃhitā annotation (79 occurrences / 30 files); row 3 → `recorded` with an Ayurvedic-register rider. Druzhinin's own translation not located; the RV 10.163.3 attribution in the 2013 memo corrected | Opus 5 (`claude-opus-5`) |
| 16-08-2026 | Druzhinin's translation located off-git (MG); covers Sūtrasthāna 1–4 only and contains `guda` zero times, so the verdict is unchanged. Registered in Uprava PROJECT_INTERLINKS; residual narrowed to "wait for Sū. 6 / Nid. 7 / Cik. 8" | Opus 5 (`claude-opus-5`) |

_Dr. Mārcis Gasūns_
