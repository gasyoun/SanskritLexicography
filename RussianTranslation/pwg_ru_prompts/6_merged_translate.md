# pwg_ru — merged-layer translate prompt (LOCKED v1, 2026-06-17)

The translation stage for the **full supplement chain** (PWG + PW + SCH + PWKVN +
NWS), producing ONE consolidated Russian entry per headword. Supersedes the PWG-only
[`5_corpus_translate.md`](5_corpus_translate.md) for merged cards. Hardened from the
2026-06-17 a-section pilot (`aṃśa`, `anna`) — see the five guards below, each tied to
a real judge finding.

## Conventions (unchanged)
- REGISTER: scholarly-philological Russian, faithful to the source's density.
- Translate to Russian ONLY the German (and NWS-layer English) gloss prose.
- KEEP VERBATIM: Sanskrit (IAST/Devanāgarī in `{#…#}`/`{%…%}`); literary sigla
  (ṚV., MBH., AK., MW, R., TS., …); German grammar abbrevs (m./f./n./Pl./Du./v.l.).
- TWO-SOURCE PRINCIPLE: text-cited sense = `attested`; kośa/grammarian-only =
  `lexicographic`.

## Task
Build the sense tree from the **PWG MAIN** entry; render every numbered/lettered
sense to Russian. Then FOLD IN the other layers (PW revision, SCH/PWKVN supplements,
NWS cumulative addendum), each net-new fact attributed in brackets `[PW]`/`[Schmidt]`/
`[PWKVN]`/`[NWS]`. Use `portrait.json` `corpus_synonyms` as the primary word-choice
evidence; discriminate near-synonyms à la Apresjan.

## The five HARD guards (each from a pilot judge finding)

1. **No editorial-intent fabrication.** Attribute *facts* to layers, but NEVER narrate
   *why* a layer changed something. Forbidden: "[PW] omits X as unreliable", "dropped
   because…". PW/SCH simply do or don't carry a thing — state the presence/absence,
   not a motive. *(anna: invented "[PW] omits Sonne as unreliable".)*

2. **Don't label "[new]" without checking the earlier layer.** Only mark a sense as a
   layer's net-new addition if it is genuinely ABSENT from the earlier layers. A sense
   that already exists in PW (e.g. its sense 2c) is not a "[PW new]" — it is just PW's
   structure. Never re-list the same sense twice. *(anna: framed PW's own 2c "Wolke"
   as a brand-new addition and duplicated it.)*

3. **Keep every NWS sub-source's gloss with its OWN label.** NWS aggregates many
   sub-dictionaries (Grassmann, NṚV, MW, Olivelle, Keller, TAK, Hoernle, Sircar…).
   Do NOT swap or merge which sub-source owns which gloss. *(aṃśa: paired Keller 2006:198
   — the "shoulder" entry — with Olivelle's "numerator" sense.)*

4. **Render EVERY NWS sub-sense — do not condense the condensed.** NWS is already a
   "Kleines Zitat"; dropping its sub-senses loses net-new coverage. Render all of them.
   *(aṃśa: dropped real NWS senses — Rivelex/Renou "tire au sort", Vishva Bandhu
   "degree = 360th part", the Meyer "inheritance share" block.)*

5. **State cross-layer gender/structure deltas plainly, in one place.** When PW changes
   gender or restructures (e.g. PWG `m.`+`n.` → PW `n.` only → NWS re-adds an `m.`
   proper-name sense), say exactly that as a single clear note — don't scatter
   contradictory `m.`/`n.` fragments across senses. *(anna: m./n. layering muddled.)*

Plus the original four (still in force): NO content fabrication · COMPLETE coverage ·
SIGLA UNTOUCHED (no German/English leaks into the Russian) · ALL records incl.
Nachträge. And: **discrimination must be built only from `portrait.json`
`corpus_synonyms.candidates`** — do not add register-synonyms absent from that evidence
*(anna: added "прокормление", not a candidate; missed corpus-attested рис/зерно/блюдо)*.

## Pilot result (baseline)
- `aṃśa` — severity **2** (publishable after light edits): 0 content fabrication, sigla
  15/15, PWG+PW coverage complete, PW/SCH/PWKVN consolidated correctly, `{{Lbody}}`
  dropped. Fix: Keller/Olivelle attribution; restore dropped NWS senses.
- `anna` — severity **3**: 0 content fabrication, but two editorial-intent/[new]
  meta-claims (guards 1–2) + weak discrimination (corpus-grounding) + m./n. delta.

→ With guards 1–5 the recurring defects are addressed; re-run before scaling to the
full a-section.
