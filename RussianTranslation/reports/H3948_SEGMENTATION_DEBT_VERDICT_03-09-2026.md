# H3948 — segmentation-debt verdict: 0 of the 12 «resolvable» rows can be rewritten

_Created: 03-09-2026 · Last updated: 03-09-2026_

Ruling being executed (MG, 03-09-2026, option 2 of the three-option brief):

> Переписать те же 12 строк и одновременно оформить явный долг: пометить 2 210 неразрешимых карточек как «сегментация под вопросом» в отчёте (не в store), чтобы следующая оплаченная волна знала, куда не наступать — час-два плюс один список, зато неопределённость перестаёт быть невидимой.

**Result in one line: half B shipped and widened (2 222 rows, not 2 210); half A is answered in the negative — none of the 12 rows reads «однозначно», so rewriting any of them would mean inventing a tier the printed source does not assign, which is the H3948 Fail condition.** The RU store was never opened for writing; its sha256 is asserted identical before and after every pass.

## 1. What the 12 rows actually are

[FINDINGS §453](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) split the 3 212 affected store rows into 12 tag-resolved-and-changed · 990 tag-resolved-unchanged · 2 210 tag-unresolved. The 12 were the candidate rewrite set. They sit on seven `key1`s:

| subcard | sense_tag | class | review_status |
|---|---|---|---|
| `gam~~h0_01_sec_1_1` | `1h` | parent-split | ai_translated |
| `gam~~h2_01_sec_1` | `1g` | parent-split | ai_translated |
| `h_a~~h0_00_pwg00` | `3c` | parent-split | ai_translated |
| `h_a~~h1_20_vi` | `3c` | parent-split | ai_translated |
| `han~~h0_11_a_bi` | `4a` | parent-split | ai_translated |
| `han~~h0_16__a_0` | `4a` | parent-split | ai_translated |
| `han~~h0_22_vy_a` | `4a` | parent-split | ai_translated |
| `han~~h0_36_vini` | `4a` | parent-split | ai_translated |
| `si_d~~h1_00_pwg02` | `2d` | parent-split | ai_translated |
| `vad~~h0_zz_pw00` | `1a` | parent-split | ai_translated |
| `vas~~h4_00_pwg01` | `4b` | parent-split | ai_translated |
| `yat~~h0_00_pwg00` | `5h` | parent-split | ai_translated |

## 2. Three independent lines of evidence, all pointing the same way

1. **Every one of the 12 is a parent-sense split, not a retag.** [`pwg_four_tier_rewrite_inspect.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_four_tier_rewrite_inspect.py) re-segments each affected `key1` under the pre-H3948 and post-H3948 marker sets. For all seven keys the diff is `ids disappeared: (none)` — only new greek children appear (`gam` → `1gα…1hγ`, `hA` → `3cα 3cβ 3cγ 3eα 3eβ 5aα 5aβ 5aγ`, `han` → `4aα 4aβ 4aγ`, `siD` → `2dα 2dβ 2dγ`, `vad` → `1aα 1aβ`, `vas` → `4bα 4bβ 4bγ`, `yat` → `5hα 5hβ`). The row's own id survives while its body moves into α/β/γ, so there is no vacated id to remap onto and **no single new id owns the row's text**: `rows_with_a_unique_post_h3948_home: 0`.

2. **A mechanical RU split is unavailable for 9 of the 12.** [`pwg_four_tier_ru_split_probe.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_four_tier_ru_split_probe.py) counts greek/latin/digit/roman markers in `de` and in `ru` per row. Only **3 / 12** carry the same greek-marker count on both sides (`h_a~~h1_20_vi`, `vas~~h4_00_pwg01`, `yat~~h0_00_pwg00`). For the other nine the Russian text simply does not carry the boundary the German does, so a split would have to be guessed sentence by sentence.

3. **Decisively: `sense_tag` is not a sense-path field at all.** [`pwg_sense_tag_agreement.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_sense_tag_agreement.py) compares each tag's last component with the marker the row's own `de` opens with, store-wide: **84.7 %** agreement (4 772 agree / 257 disagree over 5 636 comparable rows of 11 462). Among the debt rows the field takes **1 857 distinct raw shapes** (943 after normalisation), of which only 155 are path-shaped at all. The rest are free-form provenance labels from earlier extraction passes: `mit-TN-N` (74), `pref-*` (71), `caus-N` (62), `N-N` (56), `pw_N_N` (52), `NWS-N` (50), `main` (40), `pw_N` (37), `TN` (30), `XN.N` (23), plus `intro`, `cross-ref`, `grammar-intro`, `verb.N`, `PPP-siddha-N`, `Mit {#ni#} — N`. **A tier cannot be read from a label that never encoded one.**

### 2a. The greek-tag census — one printed tier, seven spellings

A direct scan of the store for `sense_tag`s containing a greek letter returns **15 rows** (method: full-store JSONL scan, 03-09-2026; `pwg_sense_tag_agreement.py`'s own `tag_carries_greek` counter says **14** because it counts only rows it could compare — both numbers are reported per the H3948 rule, and the 15 is the store-wide figure):

```
gam~~h0_01_sec_1_0 | 1 α)
gam~~h0_01_sec_1_0 | β
gam~~h0_01_sec_1_0 | 1γ
gam~~h0_01_sec_1_0 | δ)
iz~~h0_zz_pwkvn    | passivisch Infinitiv 4eβ
vad~~h0_00_pwg01   | PPP α) gesagt, gesprochen
vad~~h0_00_pwg01   | PPP β) angeredet, angesprochen
vas~~h4_00_pwg01   | 4b-α
vas~~h4_00_pwg01   | 4b-β
vas~~h4_00_pwg01   | 4b-γ
vi_s~~h0_39_pra_1  | 5a-α
vi_s~~h0_39_pra_1  | 5a-β
vi_s~~h0_39_pra_1  | 5b-α
vi_s~~h0_39_pra_1  | 5b-β
```

Four rows of the **same** `subcard` spell the same tier four different ways (`1 α)`, `β`, `1γ`, `δ)`); elsewhere the same tier appears as `4b-α`, as `5a-α`, and twice with German prose glued in front of it. That is an uncontrolled vocabulary by direct inspection, not an inference from an agreement rate.

## 3. Two facts that soften the verdict

- **No paid work is at stake in these 12.** All twelve carry `review_status=ai_translated`, `reviewer=None` — machine output. The blanket "paid human-reviewed" framing holds for the store at large, not for this set.
- **The store is already segmented at or below the greek tier.** Ten of the 15 greek-tagged rows sit on these same seven keys (`gam` 4, `vas` 3, `vad` 2, `yat` 1), and several candidate rows' `de` already opens with `— γ)`. H3948's parser change did not orphan content; it exposed **stale labels**.

## 4. What shipped instead of a rewrite

[`pwg_four_tier_row_debt.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_four_tier_row_debt.py) emits one unified debt surface of **2 222** rows flagged `сегментация под вопросом` — the 12 join the debt as their own class rather than being guessed at:

| class | rows | why it cannot be resolved |
|---|---|---|
| `tag-not-a-sense-path` | 2 067 | the tag is a provenance label, not an enumeration |
| `sense-path-unresolved` | 143 | path-shaped tag, but no matching pre-H3948 id for this `key1` |
| `parent-split` | 12 | the id survived; the body moved into greek children |

By tag vocabulary: `free-form-provenance-label` 1 996 · `sense-path-like` 155 (= 143 + 12) · `prefix-subentry-label` 71.

Artifacts:

- [`reports/H3948_segmentation_debt.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H3948_segmentation_debt.tsv) — 2 222 rows + header, one line per card, with `class`, `tag_vocabulary`, `column`, `page`, `volume`, `review_status`.
- [`reports/H3948_segmentation_debt.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H3948_segmentation_debt.json) — the same rows plus rollups, the per-class `reason` prose and the 84.7 % measurement.
- [`reports/H3948_four_tier_rewrite_candidates.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H3948_four_tier_rewrite_candidates.json) — the 12, carrying the evidence a rewrite would have needed: the row's own `de` digest, the pre-/post-H3948 digest lists for its `sense_tag`, and which new ids (none) carry byte-identical gloss text.

## 5. The fence held

`store_never_written: true`; `store_sha256` recorded as `19fcf5258e5ea384…`, byte-identical to the figure in the original H3948 store-impact report; `assert sha_before == sha_after` guards every pass. The debt scan independently reproduces H3948's 12 / 990 / 2 210 buckets and 331 changed `key1` over 123 366 corpus records, so the two measurements cross-validate.

## 6. What a next paid wave should be told

The TSV is the "where not to step" list. For the 12 `parent-split` rows specifically, the work is not a relabel but a **human re-reading of the printed column** to decide which α/β/γ child each Russian sentence belongs to — roughly a dozen columns of PWG. Whether to fund that pass, and whether to fund a broader repair of `sense_tag` into a controlled vocabulary (the 2 067 `tag-not-a-sense-path` rows), is a decision a human should make; nothing in the store changes until then.

_Dr. Mārcis Gasūns_
