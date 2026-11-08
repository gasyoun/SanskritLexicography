# Griffith en-1896 ASSET column realigned for RV 8.49–8.103 (h2361 step 2 / H6590)

_Created: 22-10-2026 · Last updated: 22-10-2026_

Executor: OxAlpha pool worker 3 (opencode/z-ai/glm-5.3-flash) · Handoff:
[H6590](https://github.com/gasyoun/Uprava/blob/main/handoffs/H6590-OxAlpha_SanskritLexicography_griffith-en-asset-column-repair_13.10.26.md)
· Residual of [FINDINGS §524](../../FINDINGS.md), measured in
[h2361](../h2361/GRIFFITH_EN_RV_MANDALA8_VALAKHILYA_MISALIGNMENT_07-08-2026.md),
refusal half closed by H5706 (PR #2368).

## What was wrong

The rvlinks EN column (`RV_sa-hn-ru-de-en_1.html`, compiled 2018) was aligned to
the stamp grid in **Griffith's own print order**, but the corpus keys mandala 8
in the critical/PWG numbering with the eleven vālakhilya hymns INLINE at
8.49–8.59. Griffith prints them APPENDED after his main series. So from stamp
8.49 on, every `<p class="en">` held a verse of the wrong hymn: 678 of 10,552
stanzas (6.4%) read a confident wrong translation. h2361 measured **19.8%**
deity-anchor agreement on 8.49–8.103 vs 87–94% elsewhere; H5706 refused the
range at the lookup layer until the asset was repaired.

## The correspondence (how it was derived)

1. Griffith's published Book 8 hymn sizes (his own numbering, Wikisource text
   of the 1896 translation, hymns 49–103 fetched and parsed):
   `[20,18,12,12,12,12,15,21,19,18,15, 15,18,18,15,16,12,11,10,9,10, 9,9,9,9,9,5,6,6,7,6,7, 33,33,12,9,21,15,12,8,12,16,22,14, 10,10,10,10,8,8,5,5,4,3,7]`
2. Critical/PWG mandala-8 hymn sizes (fixture DB) are the SAME sequence shifted
   by eleven: `c_k = g_{k-11}` for k = 60…103, and `c_k = g_{k+44}` for the
   vālakhilya k = 49…59. One exception: critical 8.93 has 34 verses where
   Griffith printed 33 (his text basis merges/omits one verse).
3. Deity-anchor verification pinned the order at 24 hymns (100% hymn-level
   agreement, e.g. C60←g49, C61←g50, C92←g81 (0.96), C102←g91 (0.92),
   C103←g92, C49←g93, C51←g95, C53←g97, C54←g98, C59←g103), and verse-count
   equality + bijectivity + print order leave no freedom for the rest.

**Repair rule:** `repaired(8, k, v) = source(8, inv(k), v)` where
`inv(k) = k+44` for k 49–59, `k−11` for k 60–102, `92` for k = 103.
Texts are moved verbatim (provenance unchanged); `location` keys never move.

## Before / after (audit gate, fixture DB, placeholder-aware)

`-en-` rows are the rvlinks declared-gap marker (no Griffith text exists for
that stanza — his text basis is shorter than the critical text in this stretch,
e.g. his 8.60 has 15 verses vs critical 20). They are skipped, not counted as
disagreements; a declared gap is not a displaced column. The gate still fails
the PRE-repair asset hard under the same semantics (27.9%), so the semantics
change does not mask the defect class.

| block | before (H3949 semantics) | before (placeholder-aware) | after (placeholder-aware) |
|---|---|---|---|
| 8.1–8.48 | 436/473 = 92.2% | 436/472 = 92.4% | 436/472 = 92.4% |
| **8.49–8.103** | **73/368 = 19.8%** | **73/262 = 27.9%** | **245/262 = 93.5%** |
| mandala 8 (whole) | 509/841 = 60.5% | 509/734 = 69.3% | 681/734 = 92.8% |
| mandalas 1–7, 9, 10 | 87.3–94.4% | 88.0–95.1% | 88.0–95.1% (unchanged) |

`python src/audit_griffith_en_alignment.py --selftest` → exit 0, **no
grandfather**: `alignment gate: no anchored block below the 70% floor`.

Per-hymn after-state (placeholder-aware), hymns with any anchored verse all
≥70% except tiny-N noise (8.58: 0/1, 8.73: 0/2 — verses whose Griffith text is
a declared gap or ordinary translation looseness at n≤2).

## Row movement ledger (for the verifier)

- 522 rows of 8.49–8.103 changed text: 392 real→real moves, 65 real→`-en-`
  and 65 `-en-`→real (the truncation boundaries), and — computed against the
  pre-repair blob — 0 real rows changed outside this span (verified:
  outside-span changed = 0).
- 457 real-text rows before → 457 real-text rows after (none invented, none
  dropped; texts only move).
- 221 rows in the span are `-en-` declared gaps after the repair (Griffith's
  text basis genuinely lacks those stanzas, e.g. C92 rows 16–33, C93 v34,
  C60 rows 16–20).
- Everything outside 8.49–8.103 is byte-identical.

## Lookup-layer lift (same pass, gate green first)

- H5706's `en-numbering-unverified` typed miss for mandala 8, sūkta ≥ 49 is
  removed from `src/citation_tm.py` — exactly on h5706's own close-out
  condition (lift only in a pass where the selftest is green).
- `citation_tm.py selftest`: all checks green; content-pinned hits
  `8,49,1` («TO you will I sing Indra's praise…»), `8,60,1`
  («AGNI, come hither with thy fires…» — the verse h2361 caught misfiled at
  8.49.1), `8,103,1` («THAT noblest Furtherer…»); 8,48,1 pre-block control
  still hits; declared-gap `8,60,16` misses cleanly, never serving `-en-`.
- LANG_PARITY `citation_tm_ru_translation_of_record` re-derived and hash
  re-pinned (verdict INTENTIONAL-DIVERGENCE stands; refusal lifted).

## Risks / known residuals

- 221 declared-gap rows: no EN exists in the source; consumers get a clean
  miss. Filling them would need a different Griffith source — out of scope.
- C93 (34 critical verses vs 33 Griffith): v34 has no EN (declared gap);
  verse-level identity held v1–v33 on the anchors checked.
- Griffith's text basis (Aufrecht-line) can merge/split verses vs the critical
  text; the gate's block-level agreement (93.5%) is the DoD bar, per-verse
  perfection is not claimed.
- `SamudraManthanam/web/corpus.db` is absent on this box (628 MB free disk);
  all runs used the committed fixture `tests/fixtures/rigveda_sa_fixture.db`
  (H3949: same numbers as the real DB, verified at build time) — the same DB
  the CI gate uses.

_Dr. Mārcis Gasūns_
