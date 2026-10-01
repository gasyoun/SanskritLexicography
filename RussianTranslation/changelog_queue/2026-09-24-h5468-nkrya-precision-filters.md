- H5468: **three precision filters for the NKRYa ipm audit, and the drain's first 345
  verdicts landed.** H5262's 30-flag spot-check found 6 of 30 flags were measurement
  artifacts rather than gloss defects; four of the six classes are now filtered at source
  in [h5262_ipm_audit.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/h5262_ipm_audit.py).
  **(1) Ellipsis fragments.** PWG prints a prefix series elliptically and the Russian gloss
  keeps the shape — «срезающий, разрезающий, -ламывающий»; the token after the hyphen is
  half a word, so pymorphy3 invents a lemma («ламывать», «грызать») that NKRYa can only
  answer 0 to. `CYR_WORD` starts matching *after* the hyphen, so the fragment was invisible
  until `extract` began inspecting the character in front of each match (`finditer`, not
  `findall`); an internal hyphen («столько-то») is consumed by the token itself and never
  trips the test. **15 fragments** skipped over the 11,534-card store.
  **(2) Sentence-internal capitals are proper names.** pymorphy's `Name`/`Surn`/`Geox`
  grammemes miss Indic onomastics — «Сарасвати» parses as a verb «сарасватить». A surface
  token with no lowercase witness anywhere is now read as a name when it is capitalised
  sentence-internally even once, or capitalised in ≥2 segment-initial occurrences (PWG-RU
  glosses open lowercase, so a repeated initial capital is onomastics). A lemma is dropped
  only when **all** its surface forms are such tokens: **2 lemmas** dropped.
  **(3) An explicit term list** for what neither test catches — a Sanskrit term in Russian
  scholarly prose («бодхисаттв» → mis-lemmatised «бодхисаттво») whose ipm measures how often
  the corpus discusses Indology, not whether the gloss reads:
  [data/h5262_term_skiplist.txt](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/data/h5262_term_skiplist.txt),
  seeded with the one term the spot-check witnessed and carrying its own evidence bar (an
  over-broad list hides real defects). Census **4,912 → 4,901** lemmas.
  **(4) At the `flag` stage**, a hyphenated lemma is now `unverifiable-compound` whatever
  number comes back, not only on a zero — the spot-check caught «столько-то» flagged RARE
  on a 5-hit portrait, a frequent pronoun undercounted by the same NKRYa tokenization that
  makes the zero case unverifiable. Selftest 22 → 33 checks, one per filter and one for the
  intact-neighbour case («разрезающий» survives, «-ламывающий» does not); still fully
  offline. The ledger carries the live drain's first **345 of 4,901** verdicts (136 flags:
  ABSENT 14 · RARE 119 · ARCHAIC 7) with its 957 cache files; the drain itself is rate-
  limited at ~60 calls/hour per account and continues. Residual: «десятикратное» (pymorphy
  reads the adjective as a noun) is a fifth artifact class no filter here catches.
