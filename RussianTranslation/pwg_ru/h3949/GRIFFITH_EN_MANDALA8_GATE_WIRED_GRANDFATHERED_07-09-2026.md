# Griffith EN alignment selftest wired into CI; mandala 8 sukta 49-103 grandfathered, not repaired

_Created: 07-09-2026 · Last updated: 07-09-2026_

H3949, following up [H2361](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h2361/GRIFFITH_EN_RV_MANDALA8_VALAKHILYA_MISALIGNMENT_07-08-2026.md).
Sonnet 5 (`claude-sonnet-5`).

## What changed

1. [`src/audit_griffith_en_alignment.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/audit_griffith_en_alignment.py)
   `--selftest` is now wired into `.github/workflows/ci.yml` (job "RussianTranslation
   gates", step "Griffith EN alignment gate (H2361/H3949)"). It SKIPs cleanly when
   `corpus.db` is not checked out (the normal CI case, since it lives in
   `SamudraManthanam`), so this is a no-op gate in CI today and a real gate anywhere
   `SAMUDRA_CORPUS_DB` points at a live checkout.
2. `mandala 8` and `  8.49-8.103` are now GRANDFATHERED by name and date in the
   script's `GRANDFATHERED` dict — printed as `GRANDFATHERED ...` (not silently
   dropped), and excluded from the set that can fail the run. Any other block
   falling below the 70% floor still fails the gate exactly as before (proven by
   deliberately zeroing mandala 1's agreement count and confirming exit 1, then
   reverting).

## What did NOT change, and why

H2361's mission read the RV 8.49-8.103 break as a single vālakhilya-block offset
(11 hymns) and asked H3949 to resolve it: "re-key the EN column against the row
key it actually belongs to." That constant-shift hypothesis was checked and is
**false** beyond the first two hymns after the vālakhilya block:

| Griffith's own sukta (before any rekey) | → would-be corpus sukta (+11) | Griffith's real verse count | corpus verse count | constant-shift verdict |
|---|---|---|---|---|
| 60 | 71 | 15 | 15 | matches |
| 61 | 72 | 18 | 18 | matches |
| 66-80 (partial run) | 77-91 | (several) | (several) | matches |
| **81** | **92** | **9** | **33** | **mismatch** |
| 82 | 93 | 9 | 34 | mismatch |
| 85 | 96 | 9 | 21 | mismatch |
| 92 | 103 | 14 | 14 | matches (coincidence at the tail boundary) |

Full table: 31 of 44 hymns in Griffith's 49-92 range do **not** land on the verse
count a constant +11 shift predicts (script: `find_offset.py` / `full_map_check.py`,
not committed — reproducible from `griffith_en_1896.json` + `corpus.db` per the
method below). The shape is consistent with Griffith's published hymn *boundaries*
diverging from the critical/PWG (Aufrecht-descended) numbering across the whole
stretch — not only where the vālakhilya hymns are inserted — which is a much
larger philological correspondence problem than a single offset constant.

Per the handoff's own ambiguity policy — "leave it unaligned, mark it, and count
it — a wrong alignment is worse than a declared gap" — and its own stated
fallback ("scope the gate to the diff and grandfather the known break explicitly,
named and dated") this was the evidenced choice over guessing a rekey that would
make ~70% of the relabeled block wrong with a plausible-looking deity name still
matching by chance on the anchor check.

## Reproduce the investigation

```
cd RussianTranslation
python src/audit_griffith_en_alignment.py --selftest   # exits 0, prints GRANDFATHERED lines
```

Method used to rule out the constant offset: for each Griffith sukta `S` in
49..92, compare `len([v for v in griffith_en_1896.json if sukta==S and text != '-en-'])`
against `len([v for v in corpus.db#sa if sukta==S+11])`. A real constant-offset
repair would need every one of the 44 to match; 13 do.

## RU lane control (unaffected, evidence)

`#ru` and `#sa` in `corpus.db` are read from the same source row and were checked
directly (not inferred): 340/344 anchored stanzas in 8.49-8.103 carry the deity
name in Russian at the same key (98.8%), 0 rows missing `#ru`. `_fetch_ru` in
`citation_tm.py` is untouched by this pass.

## Evidence of done

- CI run: see [`.github/workflows/ci.yml`](https://github.com/gasyoun/SanskritLexicography/blob/master/.github/workflows/ci.yml)
  step "Griffith EN alignment gate (H2361/H3949)" — next push/PR CI run is the
  live green proof; local run above reproduces the same exit 0.
- Deliberately broken run: mandala 1's agreement count was forced to 0 locally,
  confirmed `FAIL mandala 1: 0/981 = 0.0% < 70% floor` and exit 1, then reverted
  (not committed — the revert is the diff you see in this PR).
- Per-mandala report before and after this change is byte-identical (the change
  is to the gate's verdict logic, not the underlying data): `8.49-8.103` is
  `73/368 = 19.8%` in both.

## Residual (not closed by this handoff)

Repairing RV 8.49-8.103 for real needs a hymn-by-hymn correspondence table between
Griffith's 1896 published numbering and the critical/PWG numbering — built from
the printed edition or a scholarly concordance, not inferred from stanza counts
alone (counts alone are ambiguous where hymns of the same length sit adjacent).
That is out of scope for this handoff's effort band; flagged for a future handoff
if the EN lane for this range is ever needed by a real consumer (none exists
today — [`corpus_gate._citation_reuse`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/corpus_gate.py)
still defaults to `lang='ru'`).

_Dr. Mārcis Gasūns_
