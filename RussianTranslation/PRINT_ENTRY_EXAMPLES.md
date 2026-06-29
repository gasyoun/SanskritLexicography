# Print Entry Examples Review

Date: 2026-06-28

Purpose: test [PRINT_ENTRY_SPEC.md](PRINT_ENTRY_SPEC.md) against real local
merged cards before building a print renderer. These examples are layout and QA
prototypes only. They are not print-ready publication text until the relevant
G5/G6/G7/G10 gates pass.

Source policy: examples below use existing local merged Markdown cards under
`src/pilot/output/`. They do not use current `wf_output.json`, because that
workflow output is stale against the current `sTA` rootmap.

## Example 1 — agni

Source file: `src/pilot/output/agni.merged.md`

Status note: real local merged output; rich standard headword with PWG, PW,
Nachträge, and NWS layers. Not print-ready until reviewed.

### Compact Printed-Entry Mockup

```text
agni [m.]

1. Feuer. AK. 1,1,1,48. H. 1099. MED. n. 1. ṚV. 1,12,6. 7,1,4.
   RU: огонь.
   [attested; Vedic]

2. Feuersbrunst. M. 8,108. 4,118.
   RU: пожар.
   [attested; Epic / early-Classical]

4. der Gott des Feuers. Über seine Stellung in der älteren Theologie vgl. NIR. 7,8.
   RU: бог огня. О его положении в древней теологии ср. NIR. 7,8.
   [attested; Vedic]

5. das Feuer im Magen, Verdauungskraft.
   RU: пищеварительный огонь, пищеварительная сила.
   [attested; Classical]

Nachträge:
   Z. 16: read {#AvasaTya#}.
   {#agneH puram#}: "город Агни", pilgrimage-place name. MBH. 13,1729.

NWS:
   [NWS: MW : 5] sacrificial fire; gastric fluid; gold; Plumbago; letter r substitute.
   [NWS: Geldner 1907 : 2] Feuer und der Gott des Feuers; Pl.: Opferfeuer; Flammen.
   [NWS: Rivelex (1) : 25] natural fire, ritual fire, fire god functions.
```

### Layout Observations

- The main PWG table is readable as a printed entry only if long citation runs
  are compacted or moved to a smaller apparatus style.
- The `differentia` lines are valuable editorial evidence, but should be hidden
  from the main printed body unless the edition chooses an explicit "editorial
  note" layer.
- Nachträge must remain visible as patches; silently folding `AvasaTya` into
  the main entry would lose the correction history.
- NWS rows need one-owner-one-row display, otherwise MW/Geldner/Rivelex evidence
  becomes anonymous.

### Missing Decisions

| issue | owner |
|---|---|
| How many citations stay inline before overflow into apparatus? | renderer |
| Whether corpus `differentia` prints, moves to notes, or stays digital-only. | human_editor |
| How to display PW/PWKVN/SCH layer summaries without making the print entry unreadable. | renderer |

## Example 2 — akṣara

Source file: `src/pilot/output/akzara.merged.md`

Status note: real local merged output for a complex flagship case. It carries
adjective, masculine, feminine, and neuter structures plus PW/PWKVN/SCH
corrections. Not print-ready until reviewed.

### Compact Printed-Entry Mockup

```text
akṣara [adj.; m.; f. akṣarā; n.]

1. adj. unvergänglich. ṚV. 6,16,35. MUṆḌ. UP. 1,2,13. BHAG. 15,16. M. 2,84.
   RU: непреходящий, нетленный.
   [attested; Vedic / Epic]

2a. m. Schwert. H. ś. 143.
   RU: меч.
   [lexicographic]

3. f. akṣarā — Laut, Ton, Wort, Rede. ṚV. 3,31,6. 7,15,9. 7,36,7.
   RU: звук, тон, слово, речь.
   [attested; Vedic]

4b. n. das Bleibende, Einfache in der Sprache:
   α Wort; β Silbe; γ die heilige Silbe om; δ Laut, Buchstab; ε Vocal.
   RU: слово; слог; священный слог om; звук, буква; гласный звук.

4f. die höchste Gottheit, der letzte Grund alles Seins.
   RU: высшее божество, конечная основа всего бытия.

Nachträge:
   Correct pratyuvāca citation.
   Add Schriftstück / schriftliches Document; time-measure = 1/5 Kāṣṭhā.

NWS:
   [NWS: MW : 3] letter; name of Brahma; final beatitude; religious austerity.
   [NWS: Graßmann 1873 (1996) : 6] nicht zerrinnend; Himmel/Aetherraum; Wasser; Wort/Silbe.
   [NWS: NṚV 1 : 8 / NṚV 2A : 9] das Unvergängliche, especially Opferwort.
```

### Layout Observations

- `akṣara` proves the print renderer needs nested sense labels (`4b-α`,
  `4b-β`, etc.), not only flat numbers.
- Homonym/gender information must stay near the headword and also near the
  relevant sense block; otherwise `adj.`, `m.`, `f.`, and `n.` readings blur.
- PW's restructuring and deletion notes are editorially important, but too long
  for a compact main entry unless treated as a layer note.

### Missing Decisions

| issue | owner |
|---|---|
| How to typeset Greek-style sublabels α/β/γ in a consistent Sanskrit dictionary style. | renderer |
| Whether deleted/secondary PW/SCH items print inline or in an apparatus. | human_editor |
| Whether philosophical senses such as brahman/mokṣa receive domain labels in print. | schema/data |

## Example 3 — ap

Source file: `src/pilot/output/ap.merged.md`

Status note: protected hand-authored / NWS-sensitive pilot card. It is useful
for print layout because it contains homonym splits, `{%...%}` behavior, and
many one-owner NWS rows. Not print-ready until reviewed.

### Compact Printed-Entry Mockup

```text
ap

Homonym 1 — {#ap#}, verbal root
1. eine ausser Gebrauch gekommene Verbalwurzel...
   RU: вышедший из употребления глагольный корень...

PW 1. {%thätig sein, arbeiten%}. {#apo/ ya/dagne va/nepu#} <ls>ṚV. 3,6,7</ls>.
   RU: быть деятельным, трудиться. {#apo/ ya/dagne va/nepu#} ṚV. 3,6,7.

Homonym 2 — {#a/p#}, noun "дело, труд"
PW 2. {%Werk%}. <ab>Gen.</ab> {#apa/s#} <ls>ṚV. 1,151,4</ls>.
   RU: дело, труд. Gen. {#apa/s#} ṚV. 1,151,4.

Homonym 3 — {#a/p#} f., water/waters
1. {%Wasser, Gewässer%}; only plural in Classical, occasional singular in Veda.
   RU: вода, воды; в классическом языке только pl., in Veda occasional sg.

NWS:
   [NWS: Rivelex (1) : 252] {#ap#}: erreichen, erlangen / reach, gain -> достигать, обретать.
   [NWS: Graßmann 1873 (1996) : 70] {#áp#}: Wasser, Gewässer -> вода, воды.
   [NWS: Olivelle 2015 : 41] water ordeal; water-fort -> испытание водой; водяная крепость.
   [NWS: MW : 47 (s.v. ap)] derivative sublemmas such as {#apaHsaMvarta#}, {#apkftsna#}.
```

### Layout Observations

- `ap` needs explicit homonym blocks. A flat alphabetical print entry would
  hide the distinction between obsolete verbal root, work/deed noun, and waters.
- The renderer must know that German `{%Wasser, Gewässer%}` is source gloss
  markup, while Latin/English/binomial literals may remain literal.
- NWS rows are the strongest argument for compact owner badges; full owner
  prose in every line will be too wide for print.
- Protected/hand-authored examples should remain marked as prototypes unless
  their review provenance is present.

### Missing Decisions

| issue | owner |
|---|---|
| Whether `<ab>Gen.</ab>` prints as `Gen.` inline or as an abbreviated grammatical badge. | renderer |
| How to represent bilingual/multilingual NWS source glosses without overloading the main Russian entry. | human_editor |
| How protected hand-authored cards are marked in digital provenance but suppressed in print body. | production_audit |

## Cross-Example Findings

| priority | finding | recommended fix | owner |
|---|---|---|---|
| P0 blocks scale/print | Examples are real local cards but not reviewed print-ready rows. | Keep all examples labeled prototype until G5/G6/G7/G10 pass. | human_editor |
| P1 slows production | Long citation runs will dominate printed pages if kept fully inline. | Define citation compaction rules before renderer work. | renderer |
| P1 slows production | NWS rows need a stable compact visual grammar. | Use owner badges plus one row per source owner. | renderer |
| P1 slows production | Complex entries need nested sense labels and homonym blocks. | Renderer must support nested labels, not just flat `1,2,3`. | renderer |
| P2 improves scholarly polish | `differentia` is valuable but may be too technical for main print. | Keep in digital apparatus unless editor chooses a visible "choice note" style. | human_editor |

