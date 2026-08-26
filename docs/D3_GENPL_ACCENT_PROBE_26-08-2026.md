# D3 gen.pl accent probe — the derivative ī/ū `-nām` split at full-corpus n

_Created: 26-08-2026 · Last updated: 26-08-2026_

**Executor:** Claude Code Fable 5 (`claude-fable-5`) · handoff [H3555](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3555-Fable_SanskritLexicography_d3-genpl-accent-probe_26.08.26.md) · closes [GAPS §1](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md), rules [CONTRADICTIONS §1](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md).

## The question

In the genitive plural of long-ī/ū feminine stems, is the udātta thrown
forward onto the ending (`-īnā́m`, Whitney §319a: "in RV the accent of such
words is usually … thrown forward upon the ending", his example `bahvīnā́m`)
or kept on the stem vowel (`-ī́nām`, as Whitney's own §320/§356 paradigms
print: `rathī́nām`, `nadī́nām`)? Whitney gives both answers, which is
[FINDINGS §42](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#42-whitney-self-contradicts-on-derivative-ī-stem-genpl-accent)
and the open row [CONTRADICTIONS §1](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md).
The prior corpus evidence was n=2 (`rathī́nām`, `vadhū́nām` — the
[RECIPES §1](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md)
validation pass), which [H3538](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3538-Fable_SanskritLexicography_contradictions-adjudication-wave-1_25.08.26.md)
adjudicated INCONCLUSIVE at ruling strength, naming this probe as the
discriminating experiment.

## Data and method

- **Corpus:** Zurich morphologically glossed Rigveda (Casaretto et al. 2025)
  — `rigveda/versions/zurich.xlsx` in the public
  [VedaWebProject/vedaweb-data](https://github.com/VedaWebProject/vedaweb-data)
  GitHub mirror (CC BY 4.0; the same resource the VedaWeb 2.0 API serves as
  corpus `66695e4a14f6d337f7788740`). 164,768 token rows with per-token
  case/number/gender and classical lemma. The API host
  `vedaweb.uni-koeln.de` remains WAF-blocked (HTTP 418, re-probed
  26-08-2026); the mirror is Tier 1 primary data and fully replaces the API
  for bulk pulls.
- **Script:** [`d3_genpl_probe.py`](https://github.com/gasyoun/WhitneyRoots/blob/main/scripts/d3_genpl_probe.py)
  (WhitneyRoots `scripts/`). Filter to Gen. + Pl. tokens (2,159 in the
  corpus), keep forms whose accent-stripped NFC skeleton ends in
  `[īū][nṇ]ām` (477), classify each by where the acute sits:
  `stem_final` (`-ī́nām`), `ending` (`-īnā́m`), `accent_elsewhere`
  (barytone — acute earlier in the word), split into Section A (lemma
  itself ends in ī/ū) and Section B (feminine token under a non-ī/ū lemma
  — catches devī́-declension feminines lemmatized under the base
  adjective/participle stem, plus i/u-stem feminine nouns as control).
- **Token dump:** all 477 hits with locus, pāda, form, lemma, gender,
  lemma type and class are in the JSON the script writes
  (`d3_genpl_hits.json`), reproducible from the mirror in one run.

## Section A — lemma ends in long ī/ū (71 tokens)

**Oxytone derivative stems: 44/44 tokens stem-final (`-ī́nām`), zero
exceptions.**

| Lemma | Gender | n | Form | Class |
|---|---|---|---|---|
| nadī́- | f. | 20 | nadī́nām | stem_final |
| tanū́- | f. | 15 | tanū́nām | stem_final |
| rathī́- | m. | 2 | rathī́nām | stem_final |
| yātujū́- | m. | 2 | yātujū́nām | stem_final |
| ahī́- | f. | 1 | ahī́nām | stem_final |
| hiraṇyavī́- | f. | 1 | hiraṇyavī́nām | stem_final |
| puruṣī́- | f. | 1 | puruṣī́ṇām | stem_final |
| pūrvasū́- | f. | 1 | pūrvasū́nām | stem_final |
| vadhū́- | f. | 1 | vadhū́nām | stem_final |

**Barytone stems: 19/19 accent-elsewhere** (the acute never moves):
óṣadhī- ×9, śácī- ×4 (śácīnām ×3, one unaccented śacīnām), daívī- ×2,
ódatī-, śyā́vī-, rópuṣī- (rópuṣīṇām), áruṣī- (áruṣīṇām) ×1 each.

**Monosyllabic roots: 8/8 ending-accented** — dhī́- ×7 (dhīnā́m), śrī́- ×1
(śrīṇā́m). This is Whitney's separate §355 monosyllabic-shift rule, not the
derivative-stem cell.

## Section B — feminine tokens under a non-ī/ū lemma (179 tokens)

**devī́-declension feminines of adjectives/participles — the §319a word
class — are genuinely mixed** (~9 ending vs ~11 stem-final tokens):

| Lemma (base stem) | Form | n | Class |
|---|---|---|---|
| bahú- | bahvīnā́m | 2 | ending — **Whitney §319a's own example, confirmed** (01.095.04, 06.075.05) |
| √bhā- | vibhātīnā́m | 2 | ending |
| √i- 1 | āyatīnā́m ×2, parāyatīnā́m ×1 | 3 | ending |
| √bhañj- | abhibhañjatīnā́m | 1 | ending |
| √bhuj- 2 | bhuñjatīnā́m | 1 | ending |
| aruṇá- | aruṇī́nām | 1 | stem_final |
| babhrú- | babhrū́ṇām | 1 | stem_final |
| bībhatsú- | bībhatsū́nām | 1 | stem_final |
| √devay- | devayatī́nām | 1 | stem_final |
| √i- 1 | yatī́nām | 1 | stem_final |
| kanyā̀- ~ kanī́n- | kanī́nām | 6 | stem_final |

**i-stem (and u-stem) feminine NOUNS massively throw the accent forward**
(the regular §316/§342 gen.pl with inserted `n` after a lengthened vowel):
carṣaṇí- ×35, matí- ×23, kṣití- ×15, kr̥ṣṭí- ×12, durmatí- ×5, sumatí- ×4,
dhenú- ×3, saptatí-/suṣṭutí- ×2 each, dhautí-/navatí-/puṣṭí-/rayí- ×1 each
— all `-īnā́m`/`-ūnā́m` ending-accented.

**máh- f. is the one genuinely mixed single lemma:** mahī́nām ×4 stem-final
(05.045.03, 08.019.31, 09.102.01, 10.134.01) vs mahīnā́m ×1 ending
(03.001.12).

**Barytone feminines never move** (43 tokens accent-elsewhere): śáśvatīnām
×11, mā́nuṣīṇām ×8, jánīnām ×3, īyúṣīṇām/eyúṣīṇām ×3, yātumátīnām ×2,
pŕ̥ṣatīnām ×2, návyasīnām ×2, plus 12 singleton lemmas.

**Non-feminine control** (masc./neut. i/u-stems, §342 lengthening):
ending 99 · accent_elsewhere 126 · stem_final 2 — the ordinary i/u gen.pl
behaves as the paradigms say.

## Ruling

**Whitney §319a and §320/§356 are both correct; their scopes are disjoint —
the "self-contradiction" dissolves under word-class control.**

1. **Independent derivative ī/ū-stem nouns** (nadī́-, tanū́-, rathī́-,
   vadhū́- …) keep the accent on the stem vowel: **44/44 oxytone tokens
   stem-final, zero exceptions.** §320/§356's printed `rathī́nām, nadī́nām`
   is exactly what the corpus attests.
2. **devī́-declension feminines of adjectives and participles** — the word
   class §319a is actually about, with its own example `bahvī́` — genuinely
   vacillate: `bahvīnā́m` ×2 attested ending-accented exactly as §319a
   prints, alongside participial forms on both sides (~9 ending vs ~11
   stem-final tokens). Whitney's hedged "usually" is real corpus-level
   vacillation inside this class, not an error.
3. **Monosyllabic roots** (dhī́-, śrī́-) shift by the separate §355 rule
   (8/8 ending). **Barytones** (óṣadhī-, śácī-, śáśvant- …) never move
   (62/62 accent-elsewhere across both sections).
4. **máh-** is the single genuinely mixed lemma (4:1) and stays a
   per-lemma variant.

Consequences: the D3 cell of the ZALIZNYAK a–f accent axis emits
**stem_final for derivative ī/ū-stem noun lemmas** as a rule (not merely a
per-lemma variant), with a per-lemma variant reserved for the
devī́-declension adjective/participle class and máh-. The hypothesized
adjective (`bahvī́`) vs noun (`nadī́`) split from
[GAPS §1](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md)
is real and now measured. Evidence tier: **Tier 1** (primary corpus count,
whole-corpus census, reproducible script).

## Provenance funnel

2,159 gen.pl tokens in the corpus → 477 in long-ī/ū + `nām` shape →
Section A 71 (of which oxytone derivative 44, barytone 19, monosyllabic 8)
+ Section B feminine 179 + Section B non-feminine control 227.

_Dr. Mārcis Gasūns_
