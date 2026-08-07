# Griffith 1896 EN of-record is misaligned against its own key for RV 8.49–8.103

_Created: 07-08-2026 · Last updated: 07-08-2026_

Code review of the H2334 EN citation-TM pilot ([`src/citation_tm.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/citation_tm.py),
shipped in [v1.144.15](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/CHANGELOG.md),
[PR #1182](https://github.com/gasyoun/SanskritLexicography/pull/1182)). Opus 5 (`claude-opus-5`), H2361.

## The defect

`lookup(prefix, locus, lang='en')` maps a PWG `ṚV.` citation to a Griffith
stanza through [`_canonical_to_griffith_loc`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/citation_tm.py),
whose whole content is: strip the zero-pad off the mandala, keep sūkta and verse
as they are. `01_rigveda:1.1` → `1.1.1`. The identity of sūkta/verse across the
two keyings is the load-bearing assumption, and it is pinned by exactly two
selftest units — `1.1.1` and `10.90.1`.

It does not hold. In **mandala 8 from sūkta 49 on**, the English column of
[`pwg_ru/griffith_en_1896.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/griffith_en_1896.json)
does not address the stanza its own `location` names. `lookup('ṚV.', '8,60,1', lang='en')`
returns `status=hit`, `rights_flag=pd` and a fluent, plausible English verse —
of the **wrong hymn**. There is no signal at the call site.

This is the failure class the module itself already treats as fatal on the
Rāmāyaṇa side: the `_RAMA_GORRESIO_BOOKS` comment says in as many words that an
in-range locus keyed into the wrong recension "would return the WRONG verse's
translation silently", and books 3–6 are held `UNMAPPED` for exactly that
reason. The EN pilot got the opposite treatment — a `hit`.

## Evidence

The Sanskrit at the same key is in `corpus.db` (`#sa` lines), so each stanza can
be checked against its own original without reading English against Russian.

| Griffith key | Sanskrit at the SAME key (`#sa`) | Griffith English at that key | verdict |
|---|---|---|---|
| `8.48.1` | `svādor abhakṣi vayasaḥ sumedhāḥ` | "WISELY have I enjoyed the savoury viand" | aligned |
| `8.49.1` | `abhi pra vaḥ surādhasam indram arca` | "AGNI, come hither with thy fires" (= `8.60.1`) | **wrong stanza** |
| `8.60.1` | `agna ā yāhy agnibhir` | "O AGNI, with thy mighty wealth guard us from all malignity" | **wrong stanza** |
| `8.92.1` | `pāntam ā vo andhasa indram abhi pra gāyata` | "THAT noblest Furtherer hath appeared" (= `8.103.1`) | **wrong stanza** |
| `8.103.1` | `adarśi gātuvittamo` | "IN offerings poured to you, O Indra-Varuna" (= `8.59.1`) | **wrong stanza** |

The shape is the vālakhilya block: the corpus keys the eleven vālakhilya hymns
**inline** at 8.49–8.59 (the Aufrecht numbering PWG cites in), the English column
carries them **appended at the end**, and everything between shifts by eleven.

Scoped language-independently — a stanza whose Sanskrit opens on a deity stem
should carry that deity's name in the English at the same key — by
[`src/audit_griffith_en_alignment.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/audit_griffith_en_alignment.py):

| block | agreed/anchored | rate |
|---|---|---|
| mandalas 1–7, 9, 10 | 3 809 / 4 152 | 87–94% (aligned; the residue is ordinary translation looseness) |
| 8.1–8.48 | 436 / 473 | 92.2% (aligned) |
| **8.49–8.103** | **73 / 368** | **19.8%** |

**678 of 10 552 stanzas (6.4%)** are affected — every `ṚV.` citation PWG makes
in 8,49–8,103. The RU lane is *not* affected: `_fetch_ru` reads the corpus, whose
`#ru` and `#sa` columns agree throughout.

Reproduce:

```
cd RussianTranslation
python src/audit_griffith_en_alignment.py --selftest   # exits 1 on 8.49-8.103
```

## Why the selftest missed it

The H2334 EN block pins `1.1.1` and `10.90.1` — both outside the break, and both
asserted on `status`, `rights_flag`, `griffith_location` and a **character
count**. A char count cannot distinguish the right verse from a wrong one of
similar length. Nothing in the pilot ever compared the English against the
Sanskrit or the Russian at the same key, which is the only check that would have
caught this, and which costs one query per stanza.

## Fix, in the order it should be applied

1. **Refuse the range before anything else** — `lookup(lang='en')` should return
   a typed miss (`en-numbering-unverified`) for mandala 8, sūkta ≥ 49, exactly as
   `_rama_gorresio` refuses rather than guesses. A wrong `hit` is worse than a
   miss; this is the module's own stated house rule.
2. **Repair the asset upstream.** The JSON was extracted by `rv_griffith_extract.py`
   (H1843) from `rvlinks/RV_sa-hn-ru-de-en_1.html`; the English column drifts
   against the row skeleton there. The other language columns in that source
   should be re-checked for the same drift before any of them is promoted to an
   of-record lane.
3. **Gate it.** Wire `audit_griffith_en_alignment.py --selftest` into the CI lane
   once the block is repaired — it is written to fail on exactly this shape.

Until 1 or 2 lands, no EN card generation should consult the citation TM for
`ṚV.`. Nothing does today: [`corpus_gate._citation_reuse`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/corpus_gate.py)
still calls `consult_card(*fields)` with the default `lang='ru'`, so the pilot
has no live consumer — which is the only reason this has not already reached a
card.

_Dr. Mārcis Gasūns_
