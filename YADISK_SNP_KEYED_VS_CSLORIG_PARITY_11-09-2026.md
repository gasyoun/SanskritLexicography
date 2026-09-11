# SNP keyed text vs csl-orig v02/snp — 453-entry parity validation (H4535)

_Created: 11-09-2026 · Last updated: 11-09-2026_

**Handoff:** [H4535](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4535-OxAlpha_SanskritLexicography_snp-keyed-upgrade-cslorig_11.09.26.md) (OxAlpha lane — `openrouter/deepseek/deepseek-v4.1-flash`) · **Class:** data · **Ran:** 11-09-2026, ~05:10–06:40Z, Mac box

## Verdict

**NO UPGRADE EXISTS — csl-orig v02/snp strictly supersedes the yadisk keyed file.**
The yadisk `1974-SNP/snp.txt` (453 `<H1>`-keyed entries, 09-2014) and the current
[`csl-orig/v02/snp/snp.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/snp/snp.txt)
are the **same digitization lineage** — identical L 1–453, identical pc, identical SLP1
headwords, 451/453 entries character-identical after encoding folding — and the csl-orig
copy is the **newer stage**: modern meta-line format (meta2 Feb 2018, `<div n="lb"/>`
removal 12-2021), IAST entry bodies, the full two-part work preserved around the entries,
one typo fixed, and the end-matter correctly unkeyed instead of glued into an entry body.
Filing the yadisk file as a replacement would **destroy** those refinements — the upgrade
proposed by [census §7 item 2](https://github.com/gasyoun/SanskritLexicography/blob/master/YADISK_05_SANSKRIT_LEXICON_TREES_CENSUS_10-09-2026.md)
is rejected on evidence.

## Why the census row 11 verdict was a false positive

Census §3 row 11 recorded csl-orig snp as «plain unkeyed, 0 `<H1>`, 0 key2» and flagged
«upgrade candidate». Those two tags exist **only** in the old 2014 pseudo-XML format; the
current file keys every entry with `<L>…<pc>…<k1>…<k2>` meta lines + `<LEND>` (the
format snp-meta2.txt documents since 19-02-2018). The census's own §8 limitation —
«"overlap" verdicts rest on counterpart-size + format evidence, not byte-level diff» —
is exactly what bit here.

## Evidence

### 1. Entry counts (re-derived from sources, not quoted)

| Surface | Count | Source |
|---|---|---|
| yadisk snp.txt `<H1>` entries | **453** | `rclone copy yadisk:Sanskrityatina/05_Sanskrit-Lexicon/1974-SNP`, regex over file |
| csl-orig v02/snp/snp.txt `<L>` meta entries | **453** (L = 1…453, unique, contiguous) | local clone @ 30b2ae7+ |
| `<LEND>` terminators (current) | 453 | grep |

### 2. Per-entry keying parity (all 453)

- **L numbers**: identical 1–453 both sides.
- **pc (page-col refs)**: identical for all 453 (range 428–611; non-monotonic by design —
  part-2 entries, pp. 428–465 of the 1988 publication, follow part-1, pp. 521–611 of 1974).
- **Headwords**: yadisk `key2` = current `k1` for all 453 (and `k1=k2` in current, as meta2 states).

### 3. Body parity after encoding folding (453/453 compared)

Fold = strip markup/`[Page…]` markers, NFKD-strip diacritics, drop digits (the 2014
digit-encoding: `a1`=ā, `s2/s4`=ṣ/ś, `n2/n3`=ṇ/ṅ, `t2/d2`=ṭ/ḍ), lowercase.

- **451/453 entries character-identical.**
- **L2**: yadisk «Index Kewensis **disagress**» → current «**disagrees**» — typo fixed in current.
- **L440** (hintāla): yadisk glues the book's «Additions and Corrections» end-matter
  (~1159 folded chars, `<H/>Additions and Corrections …` abbreviations list) **inside the
  entry body** — a formation defect of the entries-only 2014 format. Current carries the
  same hintāla entry (36 folded chars, identical) and places the end-matter correctly as
  unkeyed `;`-comment sections after `<LEND>`.

### 4. Keyed-text structural validation (the 2014 file itself)

- All 453 entries match the full `<H1><h>§…§<key2>…</key2></h><body>…</body><tail><L>…</L><pc>…</pc></tail></H1>` shape; 0 malformed.
- Tag balance: `<i>` 1185/1185, `<h>` 453/453, `<key2>` 453/453, `<body>` 453/453.
- `key2` charset = valid SLP1 (proven by the 453/453 exact match with current `k1`, which
  meta2 documents as SLP1).

### 5. XML pipeline on the SURVIVING file (make_xml / generate_dict checks)

`python3 Uprava/tools/cologne_xml_validate.py --dict snp` (H2792 wrapper; mako via
throwaway venv — homebrew python is PEP-668-managed):

```
preflight ok (python=python3, mako importable, csl-websanlexicon present)
snp: PASS — All records parsed by ET
Summary: 1 PASS, 0 FAIL, 0 SKIP (of 1)
```

The current file generates valid XML end-to-end. The 2014 H1 format is not input to the
v02 pipeline at all (superseded format).

### 6. Provenance chain

- yadisk file mtime 09-09/10-09-**2014** (old format, entries-only).
- [snp-meta2.txt](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/snp/snp-meta2.txt)
  19-02-2018: documents the meta-line format **and quotes `<L>8<pc>524<k1>atasI` — which
  is byte-identical to yadisk entry L8 `atasI` pc 524** after markup mapping
  (`<i>atasi1</i> <lb/>LINUM USITATISSIMUM LINN.` → `{%atasī%}¦ <div n="lb"/><bot>…</bot>`).
- meta2 notes `<div n="lb"/>` removal 12-15-**2021** — current file postdates that cleanup.
- [snpheader.xml](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/snp/snpheader.xml):
  «Meulenbeld's Sanskrit names of plants and their botanical equivalents, 1974, 1988» —
  the two-part work the current file preserves in full (6054 lines incl. front matter,
  introduction sections, Additions & Corrections), vs 452 entry-only lines on yadisk.

## Delivery (five fields)

- **Changed:** census §3 row 11 verdict (upgrade candidate → superseded/false positive,
  dated note + link here); §7 item 2 closed as resolved-no-action. **No csl-orig change** —
  no PR filed there, none needed.
- **Unchanged:** csl-orig v02/snp (untouched — validated healthy as-is); yadisk originals
  (derived-only rule).
- **Checks:** counts + parity + structure commands as in §1–§4 above; `--dict snp` XML PASS
  in §5. All re-derived from fetched sources (yadisk via rclone; csl-orig local clone
  fetched to latest origin/main).
- **Risks:** body folding strips digits+diacritics — a residual within-entry digit/space
  transposition would survive folding in theory; the 451 exact identities + lineage
  evidence make material divergence unlikely, but a verifier may re-run folding with a
  stricter digit-aware map. The two L2/L440 diffs are fully explained.
- **Inspect:** this file; census row 11; `git log` of v02/snp in csl-orig; the
  cologne_xml_validate output above.

_Verifier (data class H4358): a DIFFERENT session re-derives §1–§2 counts and §5 PASS._
_Dr. Mārcis Gasūns_
