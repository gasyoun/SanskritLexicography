# Nominal grammar A/B — per-card evidence appendix

Companion to [`NOMINAL_GRAMMAR_AB.md`](NOMINAL_GRAMMAR_AB.md). **Generated** from the artifacts (`src/pilot/output/wf_nominal_{A,B}.json`, `nominal_judge_verdicts.json`, `nominal_judge_mapping.json`) by `src/pilot/gen_ab_detail.py` — do not hand-edit.

Arm **A = grammar OFF** (baseline), arm **B = grammar ON** (nominal grammar block injected per card). The judge saw the two renderings blind, as "rendering 1/2"; the mapping is un-blinded below.

## Tally (un-blinded)

| dimension | A (OFF) wins | B (ON) wins | tie |
|---|---:|---:|---:|
| winner | 5 | 1 | 2 |
| correctness | 2 | 0 | 6 |
| completeness | 3 | 0 | 5 |
| register | 2 | 0 | 6 |
| grammar_notes | 4 | 1 | 3 |

**Overall: A (grammar OFF) wins 5, ties 2, B (grammar ON) wins 1.** B+ties = 3/8 = 37.5% < 50% → translation injection rejected.

## Per-card evidence

### abad_da (abaddha) — winner: **A — grammar OFF**

Per dimension (A/B/tie): correctness: A · completeness: A · register: tie · grammar_notes: A

**Judge reason:** At PWG·1 R1's "не связанный" preserves the literal "ungebunden/unbound" sense that the entry explicitly develops (PW 1 = nicht gebunden/angebunden, physical), whereas R2's "несвязный" collapses it to "incoherent," dropping the literal anchor; both handle the addenda identically, and R1's notes correctly track the literal→figurative progression.

<details><summary>German source · arm A (OFF) Russian · arm B (ON) Russian</summary>

**German source**

- `[PWG·1]` {#abadDa#}¦ (3. {#a + badDa#}) <lex>adj.</lex> {%ungebunden, ungereimt, sinnlos%} <ls>AK. 1,1,5,21.</ls> <ls>H. 267.</ls> {#bahvabadDapralApinaH#} <ls>N. 26,16.</ls>
- `[PW·1]` {#abadDa#}¦ <lex>Adj.</lex> <div n="1">— 1〉 {%nicht gebunden, — angebunden%} <ls>KULL. zu M. 8,342</ls>.
- `[PW·2]` <div n="1">— 2〉 {%ungereimt, sinnlos%}.
- `[PW(addendum)·1·ungezügelt]` {#a/badDa#}¦ 1〉 auch {%ungezügelt%}. {#manas#} <ls>TS. 3,1,1,2</ls>.<info n="sup_1"/>
- `[PW(addendum)·3]` {#abadDa#}¦ 3〉 {%noch nicht hervorgetreten, noch fehlend%} <ls>RAGH. 18,47</ls>.<info n="sup_2"/>
- `[PW(addendum)·I.1.2]` {#a/badDa#}¦ I. 1. 2.<info n="sup_7"/>
- `[SCH·1·ungezügelt]` {%ábaddha%}¦ 1. auch: ungezügelt. {%manas%} <ls>TS. 3,1,1,2.</ls> — 3. noch nicht hervorgetreten, noch fehlend, <ls>Ragh. 18,47.</ls> {part=,seq=3949,type=,n=4}
- `[PWKVN·1·ungezügelt]` {#a/badDa#}¦ 1〉 auch {%ungezügelt%}. {#manas#} <ls>TS. 3,1,1,2</ls>.
- `[PWKVN·3]` {#abadDa#}¦ 3〉 {%noch nicht hervorgetreten, noch fehlend%} <ls>RAGH. 18,47</ls>.
- `[PWKVN·I.1.2]` {#a/badDa#}¦ I. 1. 2.
- `[NWS·1]` {#abaddhamukha#} [Gen , unsp] Adj mfn foul-mouthed, scurrilous. Lex(MW) . MW : 59 (s.v. abaddha )

**Arm A (grammar OFF) — Russian**

- `[PWG·1]` {#abadDa#}¦ (3. {#a + badDa#}) <lex>adj.</lex> {%не связанный, бессвязный, бессмысленный%} <ls>AK. 1,1,5,21.</ls> <ls>H. 267.</ls> {#bahvabadDapralApinaH#} <ls>N. 26,16.</ls>
- `[PW·1]` {#abadDa#}¦ <lex>Adj.</lex> <div n="1">— 1〉 {%не связанный, — непривязанный%} <ls>KULL. zu M. 8,342</ls>.
- `[PW·2]` <div n="1">— 2〉 {%бессвязный, бессмысленный%}.
- `[PW(addendum)·1·ungezügelt]` {#a/badDa#}¦ 1〉 также {%необузданный%}. {#manas#} <ls>TS. 3,1,1,2</ls>.<info n="sup_1"/>
- `[PW(addendum)·3]` {#abadDa#}¦ 3〉 {%ещё не проявившийся, ещё отсутствующий%} <ls>RAGH. 18,47</ls>.<info n="sup_2"/>
- `[PW(addendum)·I.1.2]` {#a/badDa#}¦ I. 1. 2.<info n="sup_7"/>
- `[SCH·1·ungezügelt]` {%ábaddha%}¦ 1. также: необузданный. {%manas%} <ls>TS. 3,1,1,2.</ls> — 3. ещё не проявившийся, ещё отсутствующий, <ls>Ragh. 18,47.</ls> {part=,seq=3949,type=,n=4}
- `[PWKVN·1·ungezügelt]` {#a/badDa#}¦ 1〉 также {%необузданный%}. {#manas#} <ls>TS. 3,1,1,2</ls>.
- `[PWKVN·3]` {#abadDa#}¦ 3〉 {%ещё не проявившийся, ещё отсутствующий%} <ls>RAGH. 18,47</ls>.
- `[PWKVN·I.1.2]` {#a/badDa#}¦ I. 1. 2.
- `[NWS·1]` {#abaddhamukha#} [Gen , unsp] Adj mfn сквернословящий, бранливый. Lex(MW) . MW : 59 (s.v. abaddha )

**Arm B (grammar ON) — Russian**

- `[1]` {#abadDa#}¦ (3. {#a + badDa#}) <lex>adj.</lex> {%несвязный, нескладный, бессмысленный%} <ls>AK. 1,1,5,21.</ls> <ls>H. 267.</ls> {#bahvabadDapralApinaH#} <ls>N. 26,16.</ls>
- `[PW-1]` {#abadDa#}¦ <lex>Adj.</lex> <div n="1">— 1〉 {%несвязанный, — непривязанный%} <ls>KULL. zu M. 8,342</ls>. <div n="1">— 2〉 {%нескладный, бессмысленный%}.
- `[PW-Nachtrag-1]` {#a/badDa#}¦ 1〉 также {%необузданный%}. {#manas#} <ls>TS. 3,1,1,2</ls>.<info n="sup_1"/>
- `[PW-Nachtrag-3]` {#abadDa#}¦ 3〉 {%ещё не проявившийся, ещё отсутствующий%} <ls>RAGH. 18,47</ls>.<info n="sup_2"/>
- `[PW-ref]` {#a/badDa#}¦ I. 1. 2.<info n="sup_7"/>
- `[SCH-1]` {%ábaddha%}¦ 1. также: необузданный. {%manas%} <ls>TS. 3,1,1,2.</ls> — 3. ещё не проявившийся, ещё отсутствующий, <ls>Ragh. 18,47.</ls> {part=,seq=3949,type=,n=4}
- `[PWKVN-1]` {#a/badDa#}¦ 1〉 также {%необузданный%}. {#manas#} <ls>TS. 3,1,1,2</ls>.
- `[PWKVN-3]` {#abadDa#}¦ 3〉 {%ещё не проявившийся, ещё отсутствующий%} <ls>RAGH. 18,47</ls>.
- `[PWKVN-ref]` {#a/badDa#}¦ I. 1. 2.
- `[NWS-1]` {#abaddhamukha#} [Gen , unsp] Adj mfn сквернословящий, непристойно говорящий. Lex(MW) . MW : 59 (s.v. abaddha )

</details>

### abad_damu_ka (abaddhamukha) — winner: **A — grammar OFF**

Per dimension (A/B/tie): correctness: tie · completeness: tie · register: A · grammar_notes: A

**Judge reason:** Both correctly render the bahuvrīhi and all sigla/sources verbatim, but R2's PWG gloss «с распущенным ртом» better mirrors the German «ungebundenes Mundes» (and PW «loses Maul») than R1's looser «с несдержанными устами», and R2's notes give an explicit, correct combinatorial-differentia rationale (болтливый vs сквернословящий vs бранливый) tying each variant to its source. R1's PW «имеющий распущенный рот (злоязычный)» adds a parenthetical not in the German.

<details><summary>German source · arm A (OFF) Russian · arm B (ON) Russian</summary>

**German source**

- `[PWG·1]` {#abadDamuKa#}¦ ({#abadDa + muKa#}) <lex>adj.</lex> {%ungebundenes Mundes, geschwätzig, eine böse Zunge habend%} <ls>AK. 3,1,36.</ls> <ls>H. 351.</ls>
- `[PW·1]` *{#abadDamuKa#}¦ <lex>Adj.</lex> {%ein loses Maul habend%}.
- `[NWS·1]` {#abaddhamukha#} [Gen , unsp] Adj mfn foul-mouthed, scurrilous. Lex(MW) . MW : 59 (s.v. abaddha )
- `[NWS·2]` [Jin , unsp , 2. H. 12. Jh. , Gujarat] Adj mfn scurrilous. TriṣaŚaPuC 1. 5. 144

**Arm A (grammar OFF) — Russian**

- `[PWG·1]` {#abadDamuKa#}¦ ({#abadDa + muKa#}) <lex>adj.</lex> {%с распущенным ртом, болтливый, имеющий злой язык%} <ls>AK. 3,1,36.</ls> <ls>H. 351.</ls>
- `[PW·1]` *{#abadDamuKa#}¦ <lex>Adj.</lex> {%имеющий распущенный рот%}.
- `[NWS·1]` {#abaddhamukha#} [Gen , unsp] Adj mfn сквернословящий, бранливый. Lex(MW) . MW : 59 (s.v. abaddha )
- `[NWS·2]` [Jin , unsp , 2. H. 12. Jh. , Gujarat] Adj mfn бранливый, непристойный. TriṣaŚaPuC 1. 5. 144

**Arm B (grammar ON) — Russian**

- `[1]` {#abadDamuKa#}¦ ({#abadDa + muKa#}) <lex>adj.</lex> {%с несдержанными устами, болтливый, злоязычный%} <ls>AK. 3,1,36.</ls> <ls>H. 351.</ls>
- `[PW]` *{#abadDamuKa#}¦ <lex>Adj.</lex> {%имеющий распущенный рот (злоязычный)%}.
- `[NWS-1]` {#abaddhamukha#} [Gen , unsp] Adj mfn сквернословящий, непристойный. Lex(MW) . MW : 59 (s.v. abaddha )
- `[NWS-2]` [Jin , unsp , 2. H. 12. Jh. , Gujarat] Adj mfn непристойный, оскорбительный. TriṣaŚaPuC 1. 5. 144 . TŚPC 1 : 457

</details>

### abalya (abalya) — winner: **A — grammar OFF**

Per dimension (A/B/tie): correctness: A · completeness: tie · register: tie · grammar_notes: A

**Judge reason:** Core translation is identical and correct in both. Rendering 1's PW note correctly identifies the entry's actual point — two equivalent spelling/form variants ({#abalya^#} und {#a/balya#}) — whereas Rendering 2 misreads PW as confirming "both meanings," which the source does not show (PW gives form variants, not added senses).

<details><summary>German source · arm A (OFF) Russian · arm B (ON) Russian</summary>

**German source**

- `[PWG·1]` {#abalya^#}¦ (von {#abala#}) <lex>n.</lex> {%Schwäche, Krankheit%} <ls>ŚAT. BR. 3,2,1,10.</ls> <ls n="ŚAT. BR. 3,">6,1,29.</ls> <ls n="ŚAT. BR.">14,7,2,1</ls> (hier {#a/˚#}). = <ls>BṚH. ĀR. UP. 4,4,1.</ls>
- `[PW·1]` {#abalya^#} und {#a/balya#}¦ <lex>n.</lex> {%Schwäche, Krankheit%}.

**Arm A (grammar OFF) — Russian**

- `[PWG·1]` {#abalya^#}¦ (от {#abala#}) <lex>n.</lex> {%слабость, болезнь%} <ls>ŚAT. BR. 3,2,1,10.</ls> <ls n="ŚAT. BR. 3,">6,1,29.</ls> <ls n="ŚAT. BR.">14,7,2,1</ls> (здесь {#a/˚#}). = <ls>BṚH. ĀR. UP. 4,4,1.</ls>
- `[PW·1]` {#abalya^#} und {#a/balya#}¦ <lex>n.</lex> {%слабость, болезнь%}.

**Arm B (grammar ON) — Russian**

- `[1]` {#abalya^#}¦ (от {#abala#}) <lex>n.</lex> {%слабость, болезнь%} <ls>ŚAT. BR. 3,2,1,10.</ls> <ls n="ŚAT. BR. 3,">6,1,29.</ls> <ls n="ŚAT. BR.">14,7,2,1</ls> (здесь {#a/˚#}). = <ls>BṚH. ĀR. UP. 4,4,1.</ls>
- `[PW]` {#abalya^#} und {#a/balya#}¦ <lex>n.</lex> {%слабость, болезнь%}.

</details>

### abal_iya_ms (abalīyaṃs) — winner: **tie**

Per dimension (A/B/tie): correctness: tie · completeness: tie · register: tie · grammar_notes: tie

**Judge reason:** Both render "schwächer" identically as "более слабый", preserve all sigla, Sanskrit, and German glosses verbatim, and both correctly identify abalīyaṃs as the comparative of abala attested five times in ŚAT. BR.; the only difference is the cosmetic label tags ([1]/[PW] vs [PWG·1]/[PW·1]), which carry no semantic weight.

<details><summary>German source · arm A (OFF) Russian · arm B (ON) Russian</summary>

**German source**

- `[PWG·1]` {#a/balIyaMs#}¦ (3. {#a + ba˚#}) <lex>adj.</lex> {%schwächer%} <ls>ŚAT. BR. 1,3,2,14.</ls> <ls n="ŚAT. BR. 1,">6,3,7.</ls> <ls n="ŚAT. BR.">4,1,3,1.</ls> <ls n="ŚAT. BR.">5,4,4,15.</ls> <ls n="ŚAT. BR.">11,1,6,24.</ls>
- `[PW·1]` {#a/balIyaMs#}¦ <lex>Adj.</lex> {%schwächer%}.

**Arm A (grammar OFF) — Russian**

- `[PWG·1]` {#a/balIyaMs#}¦ (3. {#a + ba˚#}) <lex>adj.</lex> {%более слабый%} <ls>ŚAT. BR. 1,3,2,14.</ls> <ls n="ŚAT. BR. 1,">6,3,7.</ls> <ls n="ŚAT. BR.">4,1,3,1.</ls> <ls n="ŚAT. BR.">5,4,4,15.</ls> <ls n="ŚAT. BR.">11,1,6,24.</ls>
- `[PW·1]` {#a/balIyaMs#}¦ <lex>Adj.</lex> {%более слабый%}.

**Arm B (grammar ON) — Russian**

- `[1]` {#a/balIyaMs#}¦ (3. {#a + ba˚#}) <lex>adj.</lex> {%более слабый%} <ls>ŚAT. BR. 1,3,2,14.</ls> <ls n="ŚAT. BR. 1,">6,3,7.</ls> <ls n="ŚAT. BR.">4,1,3,1.</ls> <ls n="ŚAT. BR.">5,4,4,15.</ls> <ls n="ŚAT. BR.">11,1,6,24.</ls>
- `[PW]` {#a/balIyaMs#}¦ <lex>Adj.</lex> {%более слабый%}.

</details>

### aban_du (abandhu) — winner: **A — grammar OFF**

Per dimension (A/B/tie): correctness: tie · completeness: A · register: tie · grammar_notes: tie

**Judge reason:** Rendering 1 preserves the verbatim bilingual NWS:2 gloss ("не имеющий родственников; having no relatives") that the source kept, whereas Rendering 2 dropped the English half, a completeness loss; both are grammatically correct (Vedic adj.), and Rendering 2's slightly more precise main gloss "без родства" for Verwandtschaft does not outweigh the fidelity loss.

<details><summary>German source · arm A (OFF) Russian · arm B (ON) Russian</summary>

**German source**

- `[1]` {#abanDu/#}¦ (3. {#a + ba˚#}) <lex>adj.</lex> {%ohne Verwandtschaft, ohne Genossen%}: {#vayaM hi tvA\ banDu^mantamaba\nDavo\ viprA^sa indra yemi\ma#} <ls>ṚV. 8,21,4.</ls> <ls n="ṚV.">1,53,9.</ls> <ls>AV. 6,122,2.</ls>
- `[PW]` {#abanDu/#}¦ <lex>Adj.</lex> {%ohne Verwandte, — Genossen%}.
- `[NWS:1]` {#abandhú#} [Ved , unsp] keine Freunde (Verbündeten) besitzend. ṚV 8,21,4
- `[NWS:2]` [Ved , unsp] Adj mfn keine Verwandten habend; having no relatives. attr. ṚV 1,53,9 . präd. ṚV 8,21,4

**Arm A (grammar OFF) — Russian**

- `[1]` {#abanDu/#}¦ (3. {#a + ba˚#}) <lex>adj.</lex> {%без родни, без сотоварищей%}: {#vayaM hi tvA\ banDu^mantamaba\nDavo\ viprA^sa indra yemi\ma#} <ls>ṚV. 8,21,4.</ls> <ls n="ṚV.">1,53,9.</ls> <ls>AV. 6,122,2.</ls>
- `[PW]` {#abanDu/#}¦ <lex>Adj.</lex> {%без родственников, — сотоварищей%}.
- `[NWS:1]` {#abandhú#} [Ved , unsp] не имеющий друзей (союзников). ṚV 8,21,4 [NWS: Geldner 1907 (N) : 225]
- `[NWS:2]` [Ved , unsp] Adj mfn не имеющий родственников; having no relatives. attr. ṚV 1,53,9 . präd. ṚV 8,21,4 [NWS: Rivelex (1) : 307]

**Arm B (grammar ON) — Russian**

- `[1]` {#abanDu/#}¦ (3. {#a + ba˚#}) <lex>adj.</lex> {%без родства, без сотоварищей%}: {#vayaM hi tvA\ banDu^mantamaba\nDavo\ viprA^sa indra yemi\ma#} <ls>ṚV. 8,21,4.</ls> <ls n="ṚV.">1,53,9.</ls> <ls>AV. 6,122,2.</ls>
- `[PW]` {#abanDu/#}¦ <lex>Adj.</lex> {%без родственников, — сотоварищей%}.
- `[NWS:1]` {#abandhú#} [Ved , unsp] не имеющий друзей (союзников). ṚV 8,21,4
- `[NWS:2]` [Ved , unsp] Adj mfn не имеющий родственников. attr. ṚV 1,53,9 . präd. ṚV 8,21,4

</details>

### aba_d_a (abadhā) — winner: **B — grammar ON**

Per dimension (A/B/tie): correctness: tie · completeness: tie · register: tie · grammar_notes: B

**Judge reason:** The Russian translations are byte-identical (both "отрезок основания треугольника", same verbatim Sanskrit/sigla/refs), so correctness, completeness, and register tie; Rendering 1 edges ahead only on its differentia notes, which add a correct and relevant geometric clarification (the base-segment cut off by the altitude) plus the Colebrooke source, while Rendering 2's note is accurate but thinner.

<details><summary>German source · arm A (OFF) Russian · arm B (ON) Russian</summary>

**German source**

- `[1]` {#abaDA#}¦ <lex>f.</lex> {%Segment der Basis eines Dreiecks%} <ls>COLEBR. Alg. 70.</ls> = {#AbADA = avabaDA#} .
- `[PW]` {#abaDA#}¦ <lex>f.</lex> {%Segment der Basis eines Dreiecks%} <ls>LĪLĀV. 140</ls>.

**Arm A (grammar OFF) — Russian**

- `[1]` {#abaDA#}¦ <lex>f.</lex> {%отрезок основания треугольника%} <ls>COLEBR. Alg. 70.</ls> = {#AbADA = avabaDA#} .
- `[PW]` {#abaDA#}¦ <lex>f.</lex> {%отрезок основания треугольника%} <ls>LĪLĀV. 140</ls>.

**Arm B (grammar ON) — Russian**

- `[1]` {#abaDA#}¦ <lex>f.</lex> {%отрезок основания треугольника%} <ls>COLEBR. Alg. 70.</ls> = {#AbADA = avabaDA#} .
- `[PW]` {#abaDA#}¦ <lex>f.</lex> {%отрезок основания треугольника%} <ls>LĪLĀV. 140</ls>.

</details>

### abud_di (abuddhi) — winner: **A — grammar OFF**

Per dimension (A/B/tie): correctness: tie · completeness: A · register: A · grammar_notes: A

**Judge reason:** Both render the German glosses accurately and keep Sanskrit/sigla verbatim; the triple "неразумие/безрассудство/глупость" (R1) and "неразумие/бессмыслие/глупость" (R2) are both defensible. R1 wins on completeness and notes: it preserves the [1] preamble citation {#abudDiM gato rAjA#} <ls>R. 4,1,23.</ls> as a true source line and gives precise, correct differentiae distinguishing the three synonyms and the "ненамеренность" sense, plus the corpus-grounded "по глупости"; R2's notes are competent but the rendering reorders/relabels segments (PWG/Nachtrag tags) and its "non-mind→не-ум" gloss is slightly less natural than R1's register.

<details><summary>German source · arm A (OFF) Russian · arm B (ON) Russian</summary>

**German source**

- `[1]` {#abudDi#}¦ (3. {#a + bu˚#}) <lex>f.</lex> {%Unvernunft, Unverstand, Thorheit%}: {#abudDiM gato rAjA#} <ls>R. 4,1,23.</ls>
- `[NWS-1]` {#abuddhi#} [Reg , unsp] Subst f non-mind. JBrahmāṇḍaP Ed, S. 77, Z. 10
- `[PW-1〉]` <hom>1.</hom> {#abudDi#}¦ <lex>f.</lex> <div n="1">— 1〉 {%Unverstand, Thorheit%} <ls>MBH. 12,204,4</ls>.
- `[PW-2〉]` <div n="1">— 2〉 {%keine Absicht%}. <ab>Instr.</ab> {%ohne <ab n="Absicht">A.</ab>%}
- `[1]` {#abudDi#}¦ (wie eben) <lex>adj.</lex> {%unvernünftig, thöricht%} <ls>M. 3,104.</ls> Davon <ab>nom. abstr.</ab> {#˚tA#} = 1. {#abudDi#} <ls>R. 5,87,24.</ls>
- `[PW-2]` <hom>2.</hom> {#abudDi#}¦ <lex>Adj.</lex> {%unverständig, thöricht,%} Davon <ab>Nom. abstr.</ab> {#˚tA#} <lex>f.</lex> <ls>MBH. 3,3023</ls>. <ls>RĀJAT. 1,79</ls>.

**Arm A (grammar OFF) — Russian**

- `[1]` {#abudDi#}¦ (3. {#a + bu˚#}) <lex>f.</lex> {%неразумие, безрассудство, глупость%}: {#abudDiM gato rAjA#} <ls>R. 4,1,23.</ls>
- `[NWS-1]` {#abuddhi#} [Reg , unsp] Subst f «не-ум, отсутствие разума». JBrahmāṇḍaP Ed, S. 77, Z. 10. Ensink 1964 : 13
- `[PW-1〉]` <hom>1.</hom> {#abudDi#}¦ <lex>f.</lex> <div n="1">— 1〉 {%безрассудство, глупость%} <ls>MBH. 12,204,4</ls>.
- `[PW-2〉]` <div n="1">— 2〉 {%отсутствие намерения%}. <ab>Instr.</ab> {%без <ab n="Absicht">A.</ab>%}
- `[1]` {#abudDi#}¦ (wie eben) <lex>adj.</lex> {%неразумный, глупый%} <ls>M. 3,104.</ls> Davon <ab>nom. abstr.</ab> {#˚tA#} = 1. {#abudDi#} <ls>R. 5,87,24.</ls>
- `[PW-2]` <hom>2.</hom> {#abudDi#}¦ <lex>Adj.</lex> {%неразумный, глупый,%} Davon <ab>Nom. abstr.</ab> {#˚tA#} <lex>f.</lex> <ls>MBH. 3,3023</ls>. <ls>RĀJAT. 1,79</ls>.

**Arm B (grammar ON) — Russian**

- `[PWG 1]` 1. {#abudDi#}¦ (3. {#a + bu˚#}) <lex>f.</lex> {%неразумие, бессмыслие, глупость%}: {#abudDiM gato rAjA#} <ls>R. 4,1,23.</ls>
- `[PWG Nachtrag]` 2. {#abudDi#}¦ (как выше) <lex>adj.</lex> {%неразумный, глупый%} <ls>M. 3,104.</ls> Davon <ab>nom. abstr.</ab> {#˚tA#} = 1. {#abudDi#} <ls>R. 5,87,24.</ls>
- `[PW 1 — sense 1]` <hom>1.</hom> {#abudDi#}¦ <lex>f.</lex> <div n="1">— 1〉 {%бессмыслие, глупость%} <ls>MBH. 12,204,4</ls>.
- `[PW 1 — sense 2]` <div n="1">— 2〉 {%отсутствие умысла%}. <ab>Instr.</ab> {%без <ab n="Absicht">A.</ab>%}
- `[PW 2]` <hom>2.</hom> {#abudDi#}¦ <lex>Adj.</lex> {%неразумный, глупый,%} Davon <ab>Nom. abstr.</ab> {#˚tA#} <lex>f.</lex> <ls>MBH. 3,3023</ls>. <ls>RĀJAT. 1,79</ls>.
- `[NWS:1]` {#abuddhi#} [Reg , unsp] Subst f «не-ум», отсутствие ума. JBrahmāṇḍaP Ed, S. 77, Z. 10

</details>

### aciram (aciram) — winner: **tie**

Per dimension (A/B/tie): correctness: tie · completeness: tie · register: tie · grammar_notes: tie

**Judge reason:** Both render the gloss identically as «вскоре, скоро» (correct for «in Kurzem, bald»), keep all Sanskrit, sigla, and German verbatim, and both differentia notes correctly reject «немедля» (over-immediate) and «недавно» (retrospective) for the same valid reason. The renderings are substantively equivalent in every dimension.

<details><summary>German source · arm A (OFF) Russian · arm B (ON) Russian</summary>

**German source**

- `[1]` {#aciram#}¦ (<ab>acc.</ab> von {#acira#}) <lex>adv.</lex> {%in Kurzem, bald%}: {#svargato hi pitA vfdDastaTA mAtAciraM tava#} <ls>BRĀHMAṆ. 1,22.</ls> {#aciraM tApamupEzyase#} <ls>DRAUP. 5,20.</ls> <div n="v">— <ab>Vgl.</ab> {#acirAt, acireRa#} .

**Arm A (grammar OFF) — Russian**

- `[1]` {#aciram#}¦ (<ab>acc.</ab> von {#acira#}) <lex>adv.</lex> вскоре, скоро: {#svargato hi pitA vfdDastaTA mAtAciraM tava#} <ls>BRĀHMAṆ. 1,22.</ls> {#aciraM tApamupEzyase#} <ls>DRAUP. 5,20.</ls> <div n="v">— <ab>Vgl.</ab> {#acirAt, acireRa#} .

**Arm B (grammar ON) — Russian**

- `[1]` {#aciram#}¦ (<ab>acc.</ab> von {#acira#}) <lex>adv.</lex> {%вскоре, скоро%}: {#svargato hi pitA vfdDastaTA mAtAciraM tava#} <ls>BRĀHMAṆ. 1,22.</ls> {#aciraM tApamupEzyase#} <ls>DRAUP. 5,20.</ls> <div n="v">— <ab>Vgl.</ab> {#acirAt, acireRa#} .

</details>
