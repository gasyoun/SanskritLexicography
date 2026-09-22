# H5069 — mandated Codex Astra review and adjudication of its disagreements

_Created: 22-09-2026 · Last updated: 22-09-2026_

The independent review that the audit
[H5069_SOURCE_SUPPORT_AUDIT_30_SENSES_20-09-2026.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h5069/H5069_SOURCE_SUPPORT_AUDIT_30_SENSES_20-09-2026.md)
left PENDING, run and graded. The adjudication of where the reviewer and the executor differ is
below; every call is checked against the primary German and Russian strings, not against either
side's prose.

## The run

1. **Reviewer:** Codex CLI `codex-cli 0.153.4`, model `gpt-6-astra`, provider openai, reasoning
   effort high. It is the reviewer the mint names, a different model family from the executor
   (Claude Opus 5 `claude-opus-5`). Started 22-09-2026 10:41 UTC, first attempt, after the
   quota reset.
2. **Blinding:** the run's working directory held exactly two files, copied from `origin/master`
   at `efce74dd9`: `REVIEWER_BRIEF.md` and `review_packet.jsonl` (sha256 `55971f0392f4996e…`).
   No manifest, key, verdict table or report was present. The run log was checked afterwards:
   every shell command ran inside that directory, and every file the reviewer's scripts opened was
   the packet, the brief or its own output.
3. **Command:**

   ```bash
   codex exec --skip-git-repo-check -c model_reasoning_effort='"high"' --sandbox workspace-write "Read REVIEWER_BRIEF.md and carry out exactly what it asks over every item in review_packet.jsonl. Write reviewer_verdicts.json here."
   ```

4. **Output:** [reviewer_verdicts.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h5069/reviewer_verdicts.json)
   (sha256 `676c7869b175f63e…`), 32 rows, every row with quoted evidence.

## Control gate — PASS

```bash
python src/h5069_source_support_audit.py score pwg_ru/h5069/reviewer_verdicts.json
```

```
H5069.control:pos:001    positive  expected=addition   got=addition    DETECTED
H5069.control:neg:001    negative  expected=faithful   got=faithful    CLEAN
real records graded by reviewer: 30
CONTROL GATE: PASS
```

The reviewer convicted the planted assertion, quoting the decisive word: German *ein Gewebe
auflösen* turned into «распускать **шёлковую** ткань», with nothing in the span licensing silk.
It also cleared the licensed re-wording. In its `challenged_control` field it named the planted
item as synthetic, and gave a refutation condition: provenance showing the wording was already
in the published record. The brief required it to challenge a control and name what would
prove it wrong, and it did both.

## Agreement on the 30 real records — 20 / 30

The ten disagreements fall into three kinds. Only the third kind changes what gets corrected.

1. **Vocabulary, not meaning (R10, R17, and the structural half of R13).** The executor's
   `conflation` here means a **span boundary moved**: Russian `{%…%}` spans merged, so a grammar
   label or a German span re-anchors, while the executor itself notes the meaning survives. The
   brief asked the reviewer about meaning only, so it answered `faithful`. Both are right about
   different questions. **Ruling:** meaning is faithful. The span misalignment stands as a
   markup finding. It is already counted corpus-wide in the audit's `poolcheck`, and it is not
   a source-support error.
2. **The reviewer quoted other spans and never reached the executor's claim (R16, R20, R07).**
   A `faithful` that quotes different words is silent on the executor's finding, not a
   refutation of it. Each case was adjudicated from the primary strings (next section).
3. **The reviewer found a defect the executor scored faithful, or scored lower (R23, R29, R07's
   second span, R13, R12, R18).** These are adjudicated below. Three are upheld and become new
   staged corrections. Two are rejected, and one confirms an existing correction.

## Adjudication, row by row

| Row | Executor | Reviewer | Primary evidence | Ruling | Refutation criterion |
|---|---|---|---|---|---|
| R20 `adhi-vid` | addition (C01) | faithful | DE `{%die erste Frau%} (acc.) {%durch eine zweite Frau%} (instr.) {%hintansetzen%}` → RU `{%ставить первую жену%} (acc.) {%позади второй жены%} (instr.)` | **C01 upheld, reclassified.** «ставить позади» does carry the sense of subordinating her, so the reviewer is right that the gist survives. But «позади» takes the genitive and makes the second wife a position, not the means (*durch*). The retained (instr.) label then describes a phrase that is not instrumental. This is a lost grammatical role (`omission` of the means relation), not an invented meaning. The proposed fix «оттеснять … второй женой» is licensed either way. | A reading of «позади второй жены» as instrumental of means in Russian. |
| R16 `yat` | addition (C02) | faithful | DE `{%verbünden, vereinigen%}` → RU `{%союзить, объединять%}` | **C02 upheld; its reason is corrected.** The audit called «союзить» "not a Russian verb". Strictly, transitive «союзить» exists, but only in shoemaking: Dal, s.v. СОЮЗ, has «союзить сапоги … обшить сверху кожей носок», and [ru.wiktionary «союзить»](https://ru.wiktionary.org/wiki/союзить) gives only «обшивать обувь союзками». The "ally" sense exists only as the reflexive, intransitive «союзиться с кем», which cannot render transitive *verbünden* (to unite two peoples). The reviewer quoted other spans of this record. | A dictionary attesting transitive «союзить» = "to unite in alliance". |
| R18 `vah` | omission (C03) | addition | DE `{%ziehend folgen%}` → RU `{%следовать, влекомый/тянущийся вослед%}` | **C03 upheld, and strengthened.** Both sides convict the same span. The executor flags an unresolved translator alternative. The reviewer adds that «влекомый» is passive ("being pulled"), while *ziehend* is active (pulling/drawing while following). The proposal «тянуться вослед» removes the passive but not the whole problem. The human voting on the review sheet should know that the active sense of *ziehend* favours «следовать, таща за собой», and the C03 note now says so. | A reading of *ziehend folgen* in which the follower is the one drawn. |
| R07 `saṃhan` | omission (C05, C06) | addition | DE `{#meGAH#} {%zusammenhängend%}` → RU `{%связный, последовательный%}` | **C05 and C06 stand** (the reviewer did not address those spans). **The reviewer's new finding is upheld as C07.** *zusammenhängend* said of clouds means cohering/massed. «последовательный» (consecutive, logically consistent) is licensed by nothing in the span. | A PWG usage where *zusammenhängend* glosses succession or consistency. |
| R23 `avabandh` | faithful | addition | DE `{#Bartari prAkprOQapraRayAvabadDaM manaH#} {%hängend an%}` → RU `«свисающий на»` | **Upheld as C08.** The example is a mind attached to a husband by earlier love, and *hängend an* is figurative there. «свисающий» asserts physical downward hanging, which neither the gloss nor the example licenses. The executor's structural finding (guillemets substituted for `{%…%}`) stands alongside it. | A reading of «свисающий на» as "attached to (someone)" in Russian usage. |
| R29 `anubrū` | faithful (medium) | addition | DE sense 1 `{%hersagen, recitiren%}` → RU `произносить вслед, рецитировать`. The same record's sense 4 gives *nachsprechen* → «повторять вслед за кем-л.» | **Upheld as C09.** The executor licensed «вслед» from the preverb *anu-*. The reviewer's counter is decisive: PWG keeps "saying after" for sense 4, so reading it into sense 1 erases a sense boundary the source draws. The executor had already marked this row as a possible low-severity addition. | PWG sense 1 of *anu-brū* carrying "after/following" in its own gloss. |
| R13 `āgam` | conflation | omission | DE `{#Agamita#} {%gelesen%}` → RU `{#Agamita#} {%читается%}` | **Reviewer rejected.** Here *gelesen* is PWG's textual-criticism formula ("the reading *Āgamita* is found"). «читается» is the standard Russian philological equivalent. It is not a present-tense passive that drops a completed result. The executor's structural `conflation` (two spans merged around a grammar label) stands on its own evidence. | A PWG convention in which *gelesen* after a Sanskrit form means "having been read" as a lexical sense. |
| R12 `apayā` | addition (medium) | faithful | DE caus. `{%entführen, rauben%}` → RU `{%похищать, уводить силой%}` | **Executor's `addition` withdrawn.** *entführen* + *rauben* together are "lead away" + "seize by force". The force that «силой» asserts is inside *rauben*. The reviewer is right, and nothing was staged for this row. | A reading of *rauben* here that excludes seizure by force. |

Rows R10 and R17 are covered by kind 1 above. Their meaning is faithful, their structural
finding stands, and nothing is staged for them.

## What changed in `corrections_proposed.tsv`

1. **C01**: `defect_class` is now `lost_grammatical_role` instead of `unsupported_assertion`.
   The proposed Russian is unchanged.
2. **C02**: the `why` text is corrected from "not a Russian verb" to "attested only in the
   shoemaking sense; the alliance sense is reflexive-only". Proposal unchanged.
3. **C03**: the `why` text now records the reviewer's point about agency (passive «влекомый»
   against active *ziehend*).
4. **C07 (R07), C08 (R23), C09 (R29)** added. Each was found by the reviewer and upheld in
   adjudication, so the defect has independent support from both sides.
5. Nothing is applied. All nine stay staged for the existing human-voted review-sheet path, as
   the mint requires. The sample is purposive, so no corpus error rate follows from nine out of
   thirty.

## Limitations of this adjudication

1. The adjudicator is the executor's own model family, Claude Opus 5 `claude-opus-5`, in a later
   session. For the rows where it sides with the executor (C01, C02, R13), independence rests on
   quoted primary strings and, for C02, on two external dictionaries. Anyone can check those
   without trusting either model.
2. Citations and German-side correctness were not checked, the same limitation as the audit.
3. Dal was consulted through a web rendering of the entry (gufo.me), not a printed page.

_Гасунс_
