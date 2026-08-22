# FULL DH-STANDARDS AUDIT — PWG→RU (H3291)

_Created: 22-08-2026 · Last updated: 22-08-2026_

**Handoff:** [H3291](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3291-Fable_SanskritLexicography_pwgru-full-dh-audit_22.08.26.md) · **Executor:** Fable tier (`claude-fable-5` class), zero paid model calls.
**Audited revision:** `a552a529c` (release 1.144.91), worktree branch `fdh-audit-h3291`.
**Scope rulings (MG, 22-08-2026):** Axis A = full R15 re-gate n=400 · session may execute safe fixes AND cut the release if conformance is green (16-08 autonomy ruling) · human gates G5–G10 mapped for unlock economics only.
**Fence honoured:** no paid generation; live store read-only; csl-orig untouched.

---

## 1. Verdict in one paragraph

The published TM pack (`pwg-tm-canonical-v1.0.0`) is **genuinely DH-grade**: byte-identity holds across GitHub Release, Zenodo (DOI [10.5281/zenodo.21932901](https://doi.org/10.5281/zenodo.21932901)) and the committed hashes; all four interchange formats validate on the *released* bytes (TMX 1.4 well-formed with 2,392 `tu`; TEI Lex-0 with 953 entries / 2,392 senses; canonical JSONL 2,392 rows / 0 duplicate IDs; OntoLex conforms to its own SHACL under pyshacl); the datasheet discloses machine provenance honestly and withholds the failed wave. The H2684 wave-1 gate FAIL is **CONFIRMED honest** by independent re-adjudication of all 20 decisive fragments. The one serious finding: **wave-2's 162,107 promoted fragments are UNVERIFIABLE — the gitignored payload directory was deleted from disk and survives only as a receipt** (regenerable deterministically, since `drafted=0`). One documentation defect in the citable surface is fixed in this PR: [DATA_LICENSE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/DATA_LICENSE.md) scope enumeration.

## 2. Phase 0 — freeze observations

| Check | Result |
|---|---|
| Audited revision | `a552a529c` = origin/master at audit start |
| Store | `src/pwg_ru_translated.jsonl` sha256 `96afca3d:` · 11,603 rows · 26,192,368 B |
| Store-hash drift vs `.ai_state` record (`811bbc21:` of 16-08) | **Explained**: [#1776](https://github.com/gasyoun/SanskritLexicography/pull/1776) landed 56 voted wrong-entry repairs after 16-08; row count unchanged |
| Human overlay intact after drift | YES — the 5 reviewed rows (3 `approved` MG, 2 `needs_review` MG) verified present; H2891 tripwire exists ([#1781](https://github.com/gasyoun/SanskritLexicography/pull/1781)) |
| Durable-in-git substrate | `canonical.v1.jsonl`, both priority manifests/queues, `wave1_b_receipt/*` (sample+adjudication+report), `wave1_b_slice/*` — all tracked |

## 3. Axis A — quality evidence

### 3.1 Wave 1 (H2684): independent gate FAIL — CONFIRMED honest

Re-adjudication instrument: this auditor re-scored **all 20 decisive rows** (the 10 `serious_error=true`, the 2 `fidelity=fail`, the 8 `equivalence=fail non-serious`) out of the frozen [`adjudication400.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/pwg_tm_canonical/wave1_b_receipt/adjudication400.jsonl).

| grok-4.5 call | My verdict |
|---|---|
| 8 of 10 serious | **Confirmed unambiguous.** `{%die%}`→`{%боги%}`; `{%Jmd%}`→`{%поручать кому-л.%}` ×3; `mit … beginnt`→«имевший половую связь с»; `thun`→`класть` beside an untranslated main gloss; `<ab>v. a.</ab>`→`<ab>т. е.</ab>`; recurring template corruption inside idx381 |
| 2 of 10 serious | Borderline-overcalled (bare `{%gewachsen%}` idiom choice; severity inconsistency: identical `Jmd` corruption scored non-serious in a `sense` cell). Even **zeroing both**, serious error = 8/400 = **2.0% > 1.0% floor** → gate FAIL stands regardless |
| 2 fidelity fails | Confirmed (`ein Bein.` dropped; `<ab>N.</ab>` tag dropped on expansion) |
| 8 equivalence-fail non-serious | Confirmed — all residual-German apparatus prose (the H2787/H2876 metalanguage class) |

Judge independence verified: adjudicator `grok-4.5` ≠ producer `grok-4.6`; verdict tallies match [`quality_report.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/pwg_tm_canonical/wave1_b_receipt/quality_report.json) exactly (398/382/10).

**Named defect class for any regeneration:** the corrupted deterministic fill that renders the argument-slot placeholder `Jmd` as «поручать кому-л.» appears in ≥5 of the 20 decisive rows across two fragment classes — it is a *template* bug in the fill path, not model noise, and must be fixed before any wave re-promotion.

### 3.2 Wave 2 (H2727): UNVERIFIABLE — payload lost

[`wave2_b/reconciliation.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/pwg_tm_canonical/wave2_b_receipt/reconciliation.json) accounts 197,916/197,916 fragments (162,107 promoted / 35,809 quarantine / silent drops 0), but the gitignored dumps (`promoted.jsonl`, `quarantine.jsonl`, `gate_receipts.jsonl`, checkpoint) **do not exist on this machine**: absent from the main checkout, all three nested worktrees, both sibling checkouts, the Recycle Bin, and `~/.worktree-attic` does not exist. `pwg_tm_generate.py drain` has no merge step into any other store — the dumps were the only home. The drain memo itself records "Independent n=400 was **not** run".

Mitigation: `fill_stats.drafted = 0` (deterministic 158,807 · source-reuse 3,138 · sense-merge 420), so the whole wave is **regenerable from the committed queue + manifest + code with zero model calls** — after the §3.1 template bug is fixed.

### 3.3 Publication pack (2,392 records): verified end-to-end

`canonical.v1.jsonl` local bytes == committed hash == GitHub release asset == Zenodo file (size-exact); reconciliation reports `lost_field_records: 0`.

## 4. Axis B — standards conformance (on released bytes)

| Format | Check | Result |
|---|---|---|
| JSONL | parse, kinds, duplicate IDs | 2,392 rows, all `publication`, 0 dups ✅ |
| TMX 1.4b | XML well-formedness, version, tu count | v=`1.4`, 2,392 `tu` ✅ |
| TEI Lex-0 | well-formedness, structure | root `TEI`; 953 entries / **2,392 senses (= record count)** / 4,784 `cit` ✅ |
| OntoLex-Lemon/vartrans/PROV-O | pyshacl vs [`schemas/pwg_tm_ontolex.shacl.ttl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/schemas/pwg_tm_ontolex.shacl.ttl) | **conforms: True** ✅ |

⚠️ Calibration note to prevent future false alarms: [`release/shapes.ttl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/shapes.ttl) is the **LOD-graph contract (H350/E7)**, not the TM pack's shape set — validating the TM TTL against it yields 1,090 spurious `evidenceGrade` MinCount violations. The pack's own shapes are the schemas/ file above.

## 5. Axis C — FAIR / citability

| FAIR facet | State |
|---|---|
| Findable | Zenodo concept+version DOIs minted and **live** (verified via API 22-08); keywords, related identifiers (isIdenticalTo GitHub release, isSupplementTo repo, isPartOf software DOI) ✅ |
| Accessible | Open; files on both Zenodo and GitHub Release, byte-verified ✅ |
| Interoperable | Four formats, validated above ✅ |
| Reusable | CC BY 4.0 consistently declared (LICENSE-DATA, CITATION.cff, Zenodo); PD source marked; rebuild command in record ✅ |
| Honesty | Machine-translation disclosure present in DATASHEET + Zenodo description; wave-1 withholding rationale stated; sample-vs-population denominators separated ✅ |

One defect found (fixed in this PR):

- **D-C2** [DATA_LICENSE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/DATA_LICENSE.md) never names the released pack paths; PUBLISH_PACKET §1 flagged exactly this ("one-line addition"). Licence duality (pack CC BY 4.0 vs repo own-work CC BY-SA 4.0) is deliberate but was implicit.

Withdrawn during verification: an initial "D-C1 CITATION.cff affiliation mojibake" finding was a PowerShell console codepage display artifact — the committed file is correct UTF-8 and byte-identical across checkouts (`0fff06d0…`).

## 6. Axis D — rights / publish-safety posture

Green pack contains only own-machine-translation-of-PD-source rows; no corpus `ru` surfaces; rights facts recorded once per standing policy. Private-data boundary intact (`pwg-ru-data` still private; secrets scan fence stands). The 131 `needs_review` SamudraManthanam sources are outside this pack and remain a separate rights ledger ([PUBLISH_PACKET §2](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/PUBLISH_PACKET.md)) — unchanged, not a blocker here.

## 7. Known-defect impact verdicts (Phase E)

| Defect (recorded) | Blocks the published pack? | Verdict |
|---|---|---|
| Sidecar `(subcard, sense_tag)` key shadowing — 468/6,009 rows (H2880/FINDINGS §551) | No — affects h180-reglue review consumers only | Park → follow-up handoff |
| Non-reproducible lock `content_hash` (h180-reglue sheet) | No — review-artifact provenance only | Park → same handoff |
| `fragments.v1.jsonl` missing locally | No — regenerable from tracked `canonical.v1.jsonl` via [`pwg_tm_fragmentize.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_fragmentize.py); inventory sha pinned | Note only |
| Wave-2 payload loss | Yes — for any future wave-2 claim | **R1 below** |
| `row_metalanguage_ok` exported but no release-gate consumer (H2876 residue) | No | Existing next-step note |

## 8. Human-gate economics (G5–G10, mapping only)

| Gate | State | Cheapest unlock | Unlocks |
|---|---|---|---|
| G6 human gold | sheet built (320 cards, lock `h215-gold-full-320-2026-08-14`), 0 voted | **20-card MQM starter ≈ 20 min** | gold chain → COMET-QE calibration, WSD/BLI gold sets (H3172), G7 |
| G5 store review | decisions 5/11,163; print-ready 3 | vote existing sheets | print-ready growth → G10 |
| G7 double review | 0/80 | needs G6 first | G10 |
| G10 edition cut | none | G5+G6+G7 | finish-line B/C (print) |
| Reglue/Nachtrag/SCH votes | 47-card sheet rebuilt; 365 classified; 7 classified | dedicated voting gates | #1736 waves close |

## 9. Ranked remediation backlog

| # | Item | Fix shape | Where |
|---|---|---|---|
| R1 | Wave-2 verifiability | Fix the `Jmd` fill-template bug → regenerate wave 2 deterministically from tracked queue+manifest → fresh independent R15 n=400 with judge identity recorded | Minted follow-up handoff (Fable tier — gate judgment) |
| R2 | Sidecar key-shadowing + lock reproducibility | Make `(subcard, sense_tag)` unique; rebuild lock reproducibly; move published artifacts | Minted follow-up handoff (Sonnet tier) |
| R3 | D-C2 licence-scope enumeration | Fixed in this PR | This branch |
| R4 | Adjudication severity consistency | Pin a per-class severity rubric into `pwg_tm_quality.py` before the R1 re-gate | Fold into R1 |
| R5 | Wire `row_metalanguage_ok` into a release-gate consumer | One consumer call | Pre-existing note, unchanged |
| R6 | Human votes (G6 starter first) | ~20 min each | GTD @DO rows stand |

## 10. Evidence appendix

Byte identity: `gh release download pwg-tm-canonical-v1.0.0` → all five hashed assets match their shipped `SHA256SUMS`; released SHA256SUMS == committed copy; local `canonical.v1.jsonl` == released bytes. Zenodo API record 21932901 `state: done`, md5s size-matched. Validators: ElementTree parses (TMX/TEI), JSONL census, pyshacl 7.x `validate(..., advanced=True)` against `schemas/pwg_tm_ontolex.shacl.ttl`. Re-adjudication subsample: `wave1_b_receipt/adjudication400.jsonl` decisive rows, judged 22-08-2026 in-session (provenance: this memo, §3.1). Store overlay check: direct scan for `review_status != ai_translated`.

_Dr. Mārcis Gasūns_
