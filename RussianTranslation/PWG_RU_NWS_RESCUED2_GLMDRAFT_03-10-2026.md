# NWS rescued glosses — store check + GLM-5.3 draft cards (03-10-2026)

_Created: 03-10-2026 · Last updated: 03-10-2026_

Follow-up to the H5707 review / H5712 fix wave (owner-strip fix, corpus scan
found 2 rescued glosses). MG's question: re-translate now (no new cloud
account yet) or translate in GLM-5.3 and compare?

## Verdict first: there is nothing to re-translate — and nothing to compare against yet

Both words are **absent from the promoted store**: an exact headword query
against the TM mirror (`pwg-ru-data/tm/pwg_ru_translated.jsonl`, 11 519 rows)
returns zero rows for `DanaMjaya`/`jIvaMjIvaka` (they appear only *inside*
other entries' Sanskrit citations). The H5712 Delivery line "the 2 rescued
glosses were already translated truncated upstream" was an assumption —
**wrong**, correcting it here. Consequences:

1. **No damaged Russian rows exist.** The residual self-heals: when these
   words are translated, they will go through the fixed masking (PR [#2367](https://github.com/gasyoun/SanskritLexicography/pull/2367)).
2. When a new cloud account exists, these two words are a clean **A/B probe**:
   identical input, Claude lane vs the GLM drafts below (free).

Queue reality check (probe, not assumption):

- `DanaMjaya` — frequency rank **594** of 94 075 (1 017 attestations): the
  frequency queue will reach it; no acceleration needed for 2 words.
- `jIvaMjIvaka` — **absent from `pwg_freq_order.tsv`** (NWS-only word, no PWG
  headword of its own): it will NEVER be reached by the frequency windows; it
  needs a non-frequency path (NWS-only mini-window or inclusion when a PWG
  host word pulls it in).

## The two rescued units — exact inputs

Extraction: packed NWS layer (`pwg-ru-data/layers/nws.tar.gz`) → `nws_split`
→ `mask_nws_gloss` at origin/master `340ef6e3` (post-fix).

### 1. DanaMjaya (dhanaṃjaya) — Kulkarni sub-source, English gloss

- lemma `dhanaṃjaya / dhanañjaya`, tag `Gen , unsp`, owner `Kulkarni 1951 : 69`, detected lang **en**.
- FULL: `s.v. dhanañjaya (Kulkarni 1951: 69). (pw) > Gen , unsp > N of a lexicographer. s.v. dhanaṃjaya (pw). Kulkarni 1951 : 69`
- OLD input (what the LLM would have seen): `s.v. dhanañjaya (` — **effectively nothing**.
- NEW prose: `s.v. dhanañjaya ( : 69). (pw) >, unsp > N of a lexicographer. s.v. dhanaṃjaya (pw)` (keep: `Kulkarni 1951`).

### 2. jIvaMjIvaka (jīvaṃjīvaka) — Dalal sub-source, German gloss

- lemma `jīvaṃjīvaka / jīvañjīvaka`, tag `Kāv , unsp`, owner `Renou 1954 (2) : 120`, detected lang **de**.
- FULL: `s. auch jīvañjīvaka (Renou 1954 (2): 120). (pw) > Kāv , unsp > as n. of a kind of literary borrowing. Dalal 1934, S. 77, Z. 3 . s. auch jīvaṃjīvaka (pw). Renou 1954 (2) : 120`
- OLD input: `s. auch jīvañjīvaka (` — nothing.
- NEW prose: full gloss minus the trailing owner cite (cross-refs and the
  Dalal page reference retained as `keep`/sigla).

## GLM-5.3 draft cards (DRAFT — not promotable)

Translated in-session by GLM-5.3 (`account:zai-individual-coding-plan`, ZCode)
per the stage-1 prompt rules ([1_perevod.txt](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru_prompts/1_perevod.txt)):
German/English prose translated, sigla and cross-references kept verbatim,
lexicographic abbreviations by the Russian tradition (s. v. → см.).

**DanaMjaya (draft-ru):** см. dhanañjaya (Kulkarni 1951 : 69; PW). — Gen,
unsp. — **[Кулкарни: «имя лексикографа» — НЕ ПОДТВЕРЖДАЕТСЯ, см. корректуру ниже].** — см. также dhanaṃjaya (PW)

**jIvaMjIvaka (draft-ru):** см. также jīvañjīvaka (Renou 1954 (2) : 120; PW). —
Kāv, unsp. — **как название одного из видов литературного заимствования**
(Dalal 1934, S. 77, Z. 3). — см. также jīvaṃjīvaka (PW)

Route honesty: these drafts are **not** promotable cards. The promoter's
contract requires the headless execution route; an in-session model output
(GLM or otherwise) has no honest route stamp here. They live in this doc as
the A/B reference for whenever a real lane translates these words. Nothing
was written to any store.

## Fact-check correction (MG, 03-10-2026): «имя лексикографа» — uncorroborated claim

MG rejected the DanaMjaya draft line «имя лексикографа» («нет такого имени»).
Cross-check against the local csl-orig dictionaries confirms him — the claim
exists ONLY in Kulkarni's NWS gloss and in neither ancestor dictionary:

- **MW** `DanaMjaya` (mw.txt L99288–99300) has NO "lexicographer" sense. Its
  author-sense reads «of the author of the *Dala-rūpaka* &c. (see below)»
  (CDSL's spelling; = PWG's *Daśarūpaka*, the dramaturgy treatise — its author
  is a dramatist/theorist). The dictionaries appear as SEPARATE headwords:
  `DanaMjayakośa` / `DanaMjayanāmamālā` / `DanaMjayanighaṇṭu` = "N. of
  dictionaries" — titles, with no author named Dhanaṃjaya.
- **PWG** `DanaMjaya` 2〉h〉 likewise: «auch N. pr. des Verfassers des
  *Daśarūpaka*. {#˚niGaRwu#} Titel eines Wörterbuchs … {#˚saMgraha#} Titel
  eines Werkes» — author of the Daśarūpaka + dictionary/work TITLES, no
  «Lexikograph».

Verdict: Kulkarni's "N of a lexicographer" is a **lossy/incorrect condensation**
(most plausibly of MW's "author of the Daśarūpaka &c." + the "N. of
dictionaries" title entries collapsed into "lexicographer"). The corrected
draft line above marks it as uncorroborated; the final card should carry the
corroborated content («имя автора „Даша-рупаки"»), drop or flag the
lexicographer claim per editorial ruling. This is also an **erratum candidate**
for the consolidated NWS erratum flow ([NWS_ERRATUM_EMAIL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/NWS_ERRATUM_EMAIL.md))
— but that list is deliberately consolidated and sent by hand, so adding/
sending is MG's call, not done here.

## Recommended next step

Do nothing now for `DanaMjaya` (the frequency queue owns it; rank 594). For
`jIvaMjIvaka`, fold it into the first available NWS-side pass (it has no
frequency path at all). When either lands, diff the lane's Russian against
the drafts above — that comparison IS the GLM-vs-Claude quality probe MG
asked about, at zero extra cost. The DanaMjaya card that lands must use the
corrected line (corroborated Daśarūpaka attribution), not «имя лексикографа».

_Гасунс_
