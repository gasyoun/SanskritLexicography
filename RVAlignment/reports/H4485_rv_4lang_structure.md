# H4485 — RV 4-lang html → structure table, validation, reading-pack verdict

_Created: 13-09-2026 · Last updated: 13-09-2026_

Handoff: [H4485-OxAlpha_SanskritLexicography_rv-4lang-layer_09.09.26.md](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4485-OxAlpha_SanskritLexicography_rv-4lang-layer_09.09.26.md) · Executor: OxAlpha (opencode/z-ai/glm-5.3-flash), 13-09-2026 (second attempt — first session died on provider timeouts before any write, verifier FAIL recorded in the handoff).

## 1. Provenance

| Fact | Value |
|---|---|
| Primary source | `RV_sa-hn-ru-de-en_1.html` (local: `~/Documents/GitHub/rvlinks/`; **never committed** — derived data only) |
| Size / sha256 | 12 432 949 B · `00534391f84388b716040496cd3ae46a05e4b052535f2b0e0ba229d9028231d0` |
| Origin | Ṛgveda 4-language alignment compiled by Dr. Mārcis Gasūns, June 2018 (yadisk `RV/RV_sa-hn-ru-de-en.html`); `_1` = upstream cleanup of one bad character at the last verse ([rvlinks readme](https://github.com/sanskrit-lexicon/rvlinks/blob/gh-pages/readme.org)) |
| Parser (this repo) | [RVAlignment/tools/h4485_parse_rv_4lang.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RVAlignment/tools/h4485_parse_rv_4lang.py) — stdlib-only, **faithful** (no source characters repaired) |
| Derived outputs | [RVAlignment/data/rv_4lang_alignment.jsonl](https://github.com/gasyoun/SanskritLexicography/blob/master/RVAlignment/data/rv_4lang_alignment.jsonl) (10 552 records, 11.4 MB) · [RVAlignment/data/rv_4lang_sample20.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/RVAlignment/data/rv_4lang_sample20.tsv) (human-readable sample) |

Reproduce:

```bash
python3 RVAlignment/tools/h4485_parse_rv_4lang.py --selftest
python3 RVAlignment/tools/h4485_parse_rv_4lang.py \
  --input ~/Documents/GitHub/rvlinks/RV_sa-hn-ru-de-en_1.html \
  --outdir RVAlignment/data --sample 20
```

## 2. Structure table (html → layer)

Verse blocks are anchored by `<p class="stamp">rvMM.HHH.VV</p>`; each block carries exactly five `<p class="…">` layers:

| CSS class | Content | Script | Source (per CSS comments in the html) | Count | Empty |
|---|---|---|---|---|---|
| `stamp` | verse locator `rvMM.HHH.VV` | ASCII | compiler | 10 552 | 0 |
| `sa` | Vedic saṃhitāpāṭha, accented | Devanāgarī + accents | Vedic text | 10 552 | 0 |
| `hn` | IAST romanization of `sa` | Latin + diacritics | compiler | 10 552 | 0 |
| `ru` | Russian translation | Cyrillic | **Elizarenkova** (CSS comment) | 10 552 | 0 (926 lacunae, §5) |
| `de` | German translation | Latin | **Geldner** (CSS comment) | 10 552 | 0 |
| `en` | English translation | Latin | **Griffith** (CSS comment) | 10 552 | 0 |

Classes `pp` (padapāṭha), `no`, `comm` are defined in the CSS but occur **0 times** in this file.

## 3. Census

**10 552 verses · 1 028 hymns · maṇḍalas 1–10** — matches both the upstream rvlinks count ("10552 verses found, 1028 hymns") and the canonical RV totals. Per-maṇḍala counts equal the standard RV figures (incl. valakhīlī inside maṇḍala 8):

| Maṇḍala | Hymns | Verses |
|---|---|---|
| 1 | 191 | 2 006 |
| 2 | 43 | 429 |
| 3 | 62 | 617 |
| 4 | 58 | 589 |
| 5 | 87 | 727 |
| 6 | 75 | 765 |
| 7 | 104 | 841 |
| 8 | 103 | 1 716 |
| 9 | 114 | 1 108 |
| 10 | 191 | 1 754 |
| **Σ** | **1 028** | **10 552** |

## 4. Mechanical validation (whole file, not just sample)

| Check | Result |
|---|---|
| Stamp format `rv\d\d.\d\d\d.\d\d` + unique keys | 10 552/10 552 unique, 0 malformed |
| Verse-number continuity per hymn (1..k sequential) | 0 violations |
| Per-hymn 5-layer completeness | 10 552 × 5 fields present, 0 empty |
| Script-class check (`sa` has Devanāgarī; `hn`/`de`/`en` Latin-only; `ru` Cyrillic-bearing, Devanāgarī-free) | `sa` 0 bad · `hn` 0 · `de` 0 · `en` 0 · `ru` 926 flagged → §5 (source lacunae, not parse defects) |
| Private-use character inventory (`sa` only) | `U+E003` ×6 372 · `U+E009` ×664 · `U+E007` ×664 — §5 |
| Selftest (fixture: parse, entity, continuity, script-class, PUA-faithfulness) | `SELFTEST PASS (9 checks)` |

### 20-verse validation (deterministic: first verse of each maṇḍala + seed-4485 random 10)

`rv01.001.01 rv02.001.01 rv03.001.01 rv04.001.01 rv05.001.01 rv06.001.01 rv07.001.01 rv08.001.01 rv09.001.01 rv10.001.01 rv09.107.06 rv07.015.11 rv07.081.06 rv01.140.05 rv10.117.01 rv05.004.11 rv01.100.05 rv01.018.07 rv04.021.08 rv01.187.03` — **20/20 PASS** (all five layers non-empty; per-layer script checks green). Human-readable table: [rv_4lang_sample20.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/RVAlignment/data/rv_4lang_sample20.tsv).

## 5. Data-quality findings (documented, deliberately NOT repaired)

1. **Private-use characters in `sa`** (upstream font artifacts, present in the `_1` source; per rvlinks/rvtest.py repair functions):
   - `U+E003` ×6 372 — intended **visarga** (U+0903) written after accent; renders as tofu in generic fonts.
   - `U+E007` ×664 + `U+E009` ×664 — font-editing pair around Devanāgarī stanza digits 1/3 (upstream temp6 maps them to digit + udātta + anudātta).
   - The parser is **faithful**: these pass through unchanged into the JSONL so no source information is destroyed. A normalization layer (→ clean visarga/udātta) is a separate, later decision.
2. **Russian lacunae — 926 verses (8.78 %)** where `ru` carries a filler instead of Elizarenkova prose: **921** × literal `-ru-` placeholder + **5** × romanization-repeat (e.g. rv01.032.13). Distribution: maṇḍala 9 = 306, 10 = 279, 8 = 259, 1 = 62, 4 = 9, 5 = 9, 3 = 1, 7 = 1 — consistent with the late-published Elizarenkova volumes (IX–X) and the valakhīlī. Effective Russian coverage: **9 626 verses (91.2 %)**. Any RV reading pack must surface this as "no RU yet" per verse, never as a silent gap.

## 6. Verdict vs kosha reading-pack family

| Family member | What it is | RV 4-lang overlaps? |
|---|---|---|
| `gita-reading-pack` | Bhagavadgītā, all 18 adhyāyas (gold) | different text |
| `dcs-reading-pack-nala-1..3` | Nalopākhyāna layers from DCS | different text |
| `bloomfield-rv-citations` | RV **pratīka citations** (Vedic Concordance) | same Veda, different layer (citations, not verse-aligned translations) |
| `reading-pack-difficulty` / `-metre` | derived scoring axes | orthogonal |

**Verdict: NEW pack.** A verse-aligned five-layer RV (sa + IAST + RU + DE + EN, 10 552 verses) exists nowhere in the kosha registry; the only RV-adjacent dataset (`bloomfield-rv-citations`) is a citations/pratīka layer, not a reading pack.

**Kosha manifest: SKIP verdict (for now).** The registry row would need the derived JSONL to be published/fetchable; it currently lives only in this repo (html stays local by design). Register `rv-4lang-reading-pack` **after** this PR merges and the JSONL gets a fetchable home (kosha mirror or release). Residual tracked: GTD `@DO` row, registration is a mechanical follow-up.

_Dr. Mārcis Gasūns_
