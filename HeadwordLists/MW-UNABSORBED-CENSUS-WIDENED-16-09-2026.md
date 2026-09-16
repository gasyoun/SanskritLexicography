# MW-unabsorbed census, widened — every class, every supplement layer, with a part-of-speech cross-cut

_Created: 16-09-2026 · Last updated: 16-09-2026_

H5011 (OxAlpha), follow-up to [csl-corrections#119](https://github.com/sanskrit-lexicon/csl-corrections/issues/119)
(MG ruling 16-09-2026: «mint a handoff with all such cases, in all parts of speech, widen the
findings. What else remains unabsorbed by MW?»). Companion to the base artefacts:
[`MW-NACHTRAG-TYPOLOGY-15-09-2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-NACHTRAG-TYPOLOGY-15-09-2026.md),
[`MW_NACHTRAG_UPTAKE_AND_PROVENANCE_DETAILS_15-09-2026.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW_NACHTRAG_UPTAKE_AND_PROVENANCE_DETAILS_15-09-2026.md)
and [`MW-NACHTRAG-ADJUDICATION-15-09-2026.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-NACHTRAG-ADJUDICATION-15-09-2026.tsv).

Builder: [`mw_unabsorbed_census.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw_unabsorbed_census.py)
(deterministic, stdlib-only, ~8 s, re-runnable). Outputs:
[`MW-UNABSORBED-CENSUS-HOMONYM-EXTENSIONS-16-09-2026.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-UNABSORBED-CENSUS-HOMONYM-EXTENSIONS-16-09-2026.tsv) ·
[`MW-UNABSORBED-CENSUS-POS-CLASS-16-09-2026.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-UNABSORBED-CENSUS-POS-CLASS-16-09-2026.tsv) ·
[`MW-UNABSORBED-CENSUS-ALL-LAYERS-16-09-2026.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-UNABSORBED-CENSUS-ALL-LAYERS-16-09-2026.tsv).

## 0 · Method — locked, and why

**Base.** "pw volume 7" = every `pw.txt` entry whose `<pc>` begins `7-` — the Nachträge volume,
35,581 entries. This is *not* the `sup_7` `<info>` tag layer (13,208 entries): the two overlap
but are not identical, and the base artefacts' §10 count was computed on the volume-7 base.

**Homonym marker.** 1,921 volume-7 entries carry an explicit `<hom>N.</hom>` anywhere in the
body; only 1,666 carry it as the entry's *own* marker (rest are mid-body cross-references such as
`= <hom>3.</hom> {#aNga#}`), and 1,685 carry the structured `<h>N` attribute on the `<L>` line.
The recompute below uses the **body `<hom>` tag** (the handoff's literal wording) and reports the
own-marker variant as a sensitivity.

**MW max homonym.** For a candidate `k1`, the highest `<h>N` among MW99 entries whose `k1`
matches, **excluding the MW99 annexure** (`<info n="sup"/>`) — a *main-body* homonym count. This
is **canary-locked**: `kārin` has MW main-body homonyms 1 (`kArin`) and 2 (`kAri/n`, the variant
spelling) ⇒ max **2**; the annexure's `kārin` `<h>3` (fr. √kF, "scattering, destroying") is a
*different derivation*, not the same homonym. The annexure-inclusive max is reported as a
sensitivity flag per row (`annexure_covers`).

**Class definition.** A **homonym-extension** = a volume-7 entry with `hom ≥ 2` (hom 1 is the base
word, never an extension) whose word MW99 already heads and whose `hom` **exceeds** MW's
main-body max for that `k1`.

**POS.** `<lex>` values in the entry body, normalised to `m./n./f./adj./mfn./part./ind./pron.`
(+`adv.`/other); `<info lex="m:f:n"/>` read as fallback. Same-tradition corroboration (`sch`,
`pwg`) excluded throughout, per the typology doc §4.

## 1 · The homonym-extension class — 571, with a POS cross-cut

| metric | value |
|---|--:|
| pw volume-7 entries | 35,581 |
| … with an explicit `<hom>N.</hom>` | 1,921 |
| … spanning a word MW99 already heads | 1,779 |
| **homonym-extensions (hom ≥ 2 > MW main max)** | **571** |
| … of which MW's *annexure* carries a homonym number ≥ N | 563 (⚠ numbering artifact — see §5) |
| … with no such annexure number | 8 |
| DCS corpus-attested (band ≥ 1) | 374 (65.5 %) |
| DCS common+ (band ≥ 3) | 204 (35.7 %) |
| present in the sup_7 adjudication pool | 0 (the classes are disjoint) |

**The stale figure.** The base artefacts (§10 of the typology doc) stated **564**. The
deterministic recompute gives **571**; the count is method-sensitive within a narrow band
(498–626, §5), and 564 sits inside it — closest to the annexure-inclusive variant (563) and to
the body-tag variant (571). The handoff asked for a deterministic recompute; 571 is that number,
and the 7-row spread is a definitional artifact, not a data change.

**POS cross-cut of the 571** ([TSV](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-UNABSORBED-CENSUS-POS-CLASS-16-09-2026.tsv)):

| POS | n | share |
|---|--:|--:|
| `adj.` | 296 | 51.8 % |
| (no `<lex>` tag) | 129 | 22.6 % |
| `m.` | 69 | 12.1 % |
| `f.` | 28 | 4.9 % |
| `n.` | 27 | 4.7 % |
| `adv.` | 20 | 3.5 % |
| other | 2 | 0.4 % |

**Reading:** the unabsorbed homonym-extension class is **adjectives first, by a wide margin**
(half the class), then masculine nouns. Unlike the generic extension class (§2), it is
**77 % POS-tagged** — the Nachträge's homonym-bearing stubs carry a `<lex>` far more often than
bare new headwords do. The class is **disjoint from the adjudication pool** (0/571 in the sup_7
missing-candidate TSV): these are words MW *already heads*, so they never entered the
"missing-entry" pipeline — corroboration/MAHĀVY columns are therefore structurally empty for it,
and POS + DCS are the only usable evidence axes.

**Examples (top DCS band):** `aBi` (√abhí, `adj.`, hom 2, MW max 1) ·
[`aNga` hom 3, MW max 2](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pw/pw.txt#L599176) ·
[`as` hom 5, MW max 3](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pw/pw.txt#L612262) ·
`dAna` hom 5, MW max 3 · `hfdaya` hom 2, MW max 0 · `mArga` (both `f.` and `m.` rows) ·
`karaRa`/`karRa` hom 2, MW max 0.

## 2 · The broader extension class — 4,688 sup_7 headwords already in the PW main body

sup_7 unique headwords **13,094**; **4,688 (35.8 %)** extend a headword already present in the PW
main body; **8,406 (64.2 %)** are genuinely new. (Entry-basis, per the uptake doc: 4,790 of
13,208 = 36 % — same figure, entry vs unique-headword base.)

**POS cross-cut of the 4,688** — and here the refutation criterion fires:

| POS | n | share |
|---|--:|--:|
| **(no `<lex>` tag)** | **4,011** | **85.6 %** |
| `m.` | 228 | 4.9 % |
| `n.` | 150 | 3.2 % |
| `f.` | 144 | 3.1 % |
| `adj.` | 141 | 3.0 % |
| `adv.` | 14 | 0.3 % |

**Verdict: the POS cross-cut of the broad extension class is refuted by sparsity.** 85.6 % of the
sup_7 extension entries carry no `<lex>` tag at all — the Nachträge record many of these as bare
cross-reference stubs (`{#enta#}¦ 6.`) with no grammatical label. Reporting a POS distribution over
the remaining 14 % would be forcing counts on a non-representative sample, so this doc **reports
the sparsity instead** (per the handoff's own refutation clause). The homonym-extension class
(§1) is the one where POS tabulation is actually informative.

## 3 · Widened to ALL supplement layers — and what is newly covered here

Per-layer splits ([TSV](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-UNABSORBED-CENSUS-ALL-LAYERS-16-09-2026.tsv)):

| layer | unique | in PW main body (extensions) | new headwords | `<hom>`-tagged | in MW72 | in MW99 | skipped by both |
|---|--:|--:|--:|--:|--:|--:|--:|
| `sup_1` | 1,755 | 765 | 990 | 62 | 342 | 991 | 758 |
| `sup_2` | 1,464 | 530 | 934 | 40 | 259 | 757 | 703 |
| `sup_3` | 1,712 | 707 | 1,005 | 70 | 361 | 1,136 | 573 |
| `sup_4` | 1,016 | 359 | 657 | 45 | 180 | 669 | 347 |
| `sup_5` | 2,192 | 1,056 | 1,136 | 140 | 564 | 1,568 | 615 |
| `sup_6` | 1,229 | 522 | 707 | 70 | 264 | 808 | 420 |
| **`sup_7`** | **13,094** | **4,688** | **8,406** | **541** | **2,892** | **8,955** | **4,112** |

**Every unabsorbed-by-MW class, with counts and evidence:**

| class | n | source | newly covered in H5011? |
|---|--:|---|---|
| **homonym/sense extensions** (numbering-based) | **571** | this script, §1 | **NEW** |
| extensions of PW main-body words | 4,688 | §2 | base-covered (sup_7); **NEW per-layer split for sup_1…sup_6** |
| new headwords never absorbed | 8,406 | §3 | base-covered (sup_7); **NEW per-layer for sup_1…sup_6** |
| MW72-never-seen (absent both editions) | 4,112 | [`MW72-CLASSES-ADJUDICATION-15-09-2026.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW72-CLASSES-ADJUDICATION-15-09-2026.tsv) | base |
| dropped between editions | 27 | same | base |
| variant/fold forms in MW | 610 | [`MW-STARRED-NACHTRAG-ADJUDICATION-14-09-2026.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-STARRED-NACHTRAG-ADJUDICATION-14-09-2026.tsv) (`variant-form-in-MW`) | base |
| fold-twin flagged (weakest) | 227 | adjudication TSV | base |
| starred sweep residue | 2,743 | starred TSV (`confirmed-missing`) | base |
| confirmed-missing (sup_7 pool) | 2,782 | adjudication TSV | base |

**Answer to «what else remains unabsorbed by MW?»** Beyond the already-enumerated new headwords,
the unabsorbed material decomposes into: **(a)** 571 homonym/sense-extensions of words MW already
heads (§1) — the class the base artefacts flagged but never POS-profiled; **(b)** 4,688 sup_7
extensions of PW main-body words (§2), with the same per-layer profile now computed for
sup_1…sup_6; **(c)** the 4,112 MW72-never-seen and 27 dropped-between-editions classes (base
artefacts, H4884); **(d)** the 610 variant-form-in-MW and 227 fold-twin rows (weakest claims); and
**(e)** the 2,743 starred-sweep confirmed-missing residue. The one genuinely *new class* this
handoff adds is **(a)** — homonym-extensions resolved by *numbering* rather than by headword
absence, disjoint from every prior pool.

## 4 · Reproduction

```sh
python HeadwordLists/mw_unabsorbed_census.py
# reads csl-orig/v02/{pw,mw,mw72}/… (CSL_ORIG_V02) + VisualDCS/dcs_lemma_summary.json (DCS_LEMMA_JSON)
# + HeadwordLists/MW-NACHTRAG-ADJUDICATION-15-09-2026.tsv  ·  ~8 s, stdlib only
```

## 5 · Caveats and unknowns

1. **MW `<h>` vs pw `<hom>` comparability is unproven** (the handoff lists it as an unknown). The
   571 rests on the main-body-max reading the canary pins; the count moves to **563** if MW's
   *annexure* homonym numbers are allowed to count, **507** on the `<h>`-attribute base, **498** on
   the entry-own-marker base, and **626** if MW-headedness is not required. All are in the TSV via
   the `annexure_covers` / `pos_set` / `mw_*_max_hom` columns.
2. **`annexure_covers = yes` is a numbering coincidence, not semantic coverage.** `kārin` is the
   proof: MW's annexure `kārin³` ("scattering, destroying") is a *different* word from the pw
   homonym 3, yet the flag reads `yes`. Do not read the 563 as "MW absorbed them".
3. **POS sparsity** — the broad extension class (§2) is 85.6 % untagged; its POS distribution is
   not representative and is not claimed.
4. **DCS coverage bias** — texts skew Buddhist/epic; band ≥ 1 is not "well attested".
5. **Deliberate exclusion vs oversight** for the Buddhist/Mahāvyutpatti layer remains undecided
   (base artefact caveat, unchanged).

## 6 · Canaries (own-data)

- **`kāritra`** — `confirmed-missing`, corroborated `bhs;sch`, MAHĀVY 245/844, pw `7-331-d`
  ([ADJ#L2900](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-NACHTRAG-ADJUDICATION-15-09-2026.tsv#L2900)) — **reproduces**, and correctly has *no* `<hom>`
  (it is not a homonym-extension). ✓
- **`kārin³`** — homonym-extension at pw volume-7 `7-331-d`
  ([pw.txt#L620966](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pw/pw.txt#L620966)),
  hom 3, **MW main max 2** ⇒ extension
  ([extension TSV line 516](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/MW-UNABSORBED-CENSUS-HOMONYM-EXTENSIONS-16-09-2026.tsv#L516)). ✓

_Гасунс_
