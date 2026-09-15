# H4744 — BHS x MW and x DCS Buddhist-texts key2 crosswalk (report of record)

_Created: 15-09-2026 · Last updated: 15-09-2026_

Sibling census B8 (batch-1 xwalk wave). First crosswalk for the BHS dictionary (Edgerton): all 18,188 `now-2026` BHS key2 headwords joined against MW key2, PWG key2 and the Buddhist loci of the pinned DCS corpus. Companion of the retired H4808 — the MW/PWG Buddhist-dictionary gap measure it asked for falls out of the same TSV.

## Artifact

| File | What it is |
|---|---|
| [bhs_dcs_mw_key2_crosswalk.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/bhs_dcs_mw_key2_crosswalk.tsv) | 18,188 rows, one per BHS key2: `bhs_key2 · mw_tier · pwg_tier · dcs_lemma_id · dcs_bhs_tokens · dcs_bhs_loci · dcs_tier · dcs_lemma_hits` (sha256 `c9d15269…ef13369`) |
| [bhs_dcs_mw_key2_crosswalk_stats.json](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/bhs_dcs_mw_key2_crosswalk_stats.json) | machine-readable tallies, 30-entry deterministic sample, locus table, input provenance |
| [bhs_dcs_mw_key2_crosswalk.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/bhs_dcs_mw_key2_crosswalk.py) | builder — re-run regenerates both artifacts byte-identically |

## Headline numbers

- **MW gap (the H4808 measure): 13,604 of 18,188 BHS headwords (74.8%) have NO Monier-Williams entry at any tier**; 4,584 link (exact 2,422 · form_key 427 · marker_strip 1,472 · marker_strip+form_key 263).
- **PWG gap: 13,305 (73.2%)**; 4,883 link (exact 3,877 · form_key 517 · marker_strip 449 · ms+fk 40). PWG edges out MW on Buddhist vocabulary by 299 headwords.
- **DCS Buddhist-locus attestation: 3,171 BHS headwords (17.4%) are attested in DCS's 20 Buddhist texts**, carrying **130,416 tokens** of the 285,109 locus tokens; 2,807 of them sit in the hybrid register (see locus classes), 364 only in Buddhist-classical works.
- BHS key2 register artifacts block naive joins: 3,114 keys (17.1%) carry `-` (2,707), `˚` (210) or `()` (320) markers — hence the marker_strip tiers.

## DCS Buddhist loci (register classes)

| Class | Texts |
|---|---|
| `pm-excluded` (fenced off by the H1000 period map, FINDINGS §87) | Divyāvadāna · Aṣṭasāhasrikā · Saddharmapuṇḍarīkasūtra |
| `bhs-hybrid` | Lalitavistara · Avadānaśataka · Saṅghabhedavastu · Laṅkāvatārasūtra |
| `buddhist-classical` | Abhidharmakośa(+bhāṣya) · Bodhicaryāvatāra · Buddhacarita · Mūlamadhyamakārikāḥ · Prasannapadā · Nyāyabindu · Saundarānanda · Śikṣāsamuccaya · Viṃśatikā(kārikā+vṛtti) · Acintyastava · Āryāsaptaśatī |

The `dcs_bhs_loci` column names the exact text(s) per row, so any consumer can re-cut the boundary (e.g. `pm-excluded` only) without a rebuild.

## Method (tiered matching, house crosswalk rules)

1. **T1 exact** — SLP1 string equality after `sanskrit_util.to_slp1` (DCS lemmas are IAST; transcoded, never re-spelled locally).
2. **T2 form_key** — `slp1_form_key` fold (anusvāra→homorganic nasal, final visarga drop).
3. **T3 marker_strip** — strip `[˚()\-]` from both sides, exact compare (BHS's bound-stem `˚` and hyphenated-compound conventions).
4. **T4 marker_strip+form_key.**
Each tier reported separately; strongest tier wins. DCS side restricted to the 20 Buddhist texts (285,109 tokens, 13,565 distinct lemmas); 300 keys match >1 DCS lemma (homographs; 273 at 2 hits, 27 at ≥3) — the max-token lemma travels in the TSV, `dcs_lemma_hits` counts the rest.

## Verification (30-entry sample — PASS)

Deterministic stride-607 sample in the stats JSON, all tiers represented. Independent re-checks: TSV-vs-JSON tally equality (MW and DCS), `lābhin`/`aBisaMboDi` grep-confirmed in raw MW/BHS files, lemma texts of 220451 (`abhisaṃbodhi`), 156931 (`grahaṇa`), 44846 (`upaga`), 80918 (`lābhin`) confirmed against the DB. Negative control: `upāyakauśalya` is genuinely absent from the DCS lemma inventory — BHS `upAya-kOSalya` is honestly `unlinked` on the DCS side (no derivation guessing, per FINDINGS §453 doctrine).

## Limitations

- The join measures **headword-level** attestation. BHS key2 lists many inflection-derived headwords (absolutives, agent nouns) that DCS lemmatizes under a base — unlinked ≠ unattested, it means "no key-level match".
- Tier-3/4 links through `˚`/`-`/`()` strips are mechanical; a consumer wanting only full-form links should filter `mw_tier='exact'` etc.
- DCS Buddhist coverage is what it is — 20 texts, 285k tokens; the 17.4% attestation is a floor, not a census of Buddhist Sanskrit usage.

_Гасунс_
