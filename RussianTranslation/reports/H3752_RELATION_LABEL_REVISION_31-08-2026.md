# H3752 (W5) — the relation label re-derived from its own attachment result

_Created: 31-08-2026 · Last updated: 31-08-2026_

Wave unit W5 of the [Claude Code hardening wave](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_CLAUDE_HARDENING_WAVE_2026H2.md), closing the code half of [issue #1736](https://github.com/gasyoun/SanskritLexicography/issues/1736). Executed by Opus 5 (`claude-opus-5`) after W1 ([H3748](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3748-Opus_SanskritLexicography_gate-evidence-contract_30.08.26.md), [PR #1993](https://github.com/gasyoun/SanskritLexicography/pull/1993)).

## 1. The defect, restated in one line

`subtype` was assigned from the **layer** and never re-read after the attachment lookup ran, so **4,187 rows** said `restate` — "PW пересказывает *этот* смысл PWG" — while the same row's `target_sense` read `*new`, the pipeline's own marker for *no such sense was identified*.

Wave 1 ([H2879](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2879-Opus_SanskritLexicography_placement-axis-split-w1_16.08.26.md)) added the `placement` boolean beside the label and **deliberately left the label alone** ([REGLUE_SPEC §10](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/REGLUE_SPEC.md): "duplicating one fact across two fields guarantees they drift apart"). That reasoning is right about duplication and wrong about this field: every surface that reads `subtype` **on its own** — the sheet chips, `relationships_rollup.tsv`, the published "86 % of the re-glue is PWG paraphrase" headline — never saw the boolean. The fix is therefore not a second field. It is that `subtype` becomes a **function of the placement result**, computed once, at one site, immediately after the placement block.

## 2. Census first (PLAN ruling 14) — the population holds

[`src/h3752_relation_label_census.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/h3752_relation_label_census.py), read-only, over the live 11,519-row store:

| mode (issue #1736) | rows | share |
|---|---:|---:|
| **A** — `*new` by construction (no leading number on the supplement's own tag) | 5,168 | 81.7 % |
| **B** — dangling target (`out_of_range` 387 + `not_found` 134) | 521 | 8.2 % |
| **C** — target really found | 637 | 10.1 % |

Against the issue's 16-08-2026 measurement — the ruling-14 halt test:

| | live | issue #1736 | divergence |
|---|---:|---:|---:|
| `restate` rows | 5,199 | 5,054 | ×1.03 |
| `restate` + `*new` (**the headline**) | **4,187** | **4,132** | **×1.01** |
| `restate` dangling | 450 | 404 | ×1.11 |
| `restate` found | 562 | 518 | ×1.08 |

Worst divergence ×1.11, far under the ×2 halt. **The rewrite half is authorised**; the issue's premise is confirmed, not merely repeated.

## 3. What changed — and the two things that deliberately did not

Three labels name a PWG **sense** as the other end of the relation, and each gains an unplaced twin used when no target was identified:

| label | placed | unplaced | twin |
|---|---:|---:|---|
| `restate` | 562 | **4,637** | `restate_unplaced` |
| `nws_at_sense` | 6 | **317** | `nws_at_sense_unplaced` |
| `a2a` | 10 | **112** | `a2a_unplaced` |
| | **578** | **5,066** | |

**`direction` and `op` are untouched.** "The PW layer abridges PWG" and "this row restates rather than adds" are properties of the layer and of the row, true whether or not a target was located. Keeping them is what separates this from issue #1736's rejected **variant B**, which would have dropped the ＋/≈/✕ distinction from ~90 % of supplements. Gate W5c proves no relabelled row lost them.

**Three subtypes were deliberately NOT suffixed**, each for a different reason:

- `sch_star`, `derived_sense`, `foreign_fragment` — additive. They assert a *new* sense, not a relation *to* one; having no target is their normal state.
- `pw_correct` — grounded in the gender index, a separate lookup that already succeeded. Its evidence does not come from `placement`. (Measured: its single corpus row is placed anyway.)
- `pwg_internal_correction` — wave 2 ([H2880](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2880-Opus_SanskritLexicography_pwg-internal-corrections-w2_16.08.26.md), REGLUE_SPEC §11.3) ruled on exactly this case: a bare `Nachtrag` is unplaced by design, and the placed/unplaced distribution is one of that wave's published results. Reopening it was not this handoff's mission.

## 4. Anti-drift — wave 1's objection, answered mechanically

§10 was right that two fields carrying one fact drift apart. They cannot here, and that is asserted rather than asserted-in-prose:

- One computation site. `subtype` is rewritten from `placement` in the same expression that produced it, inside `classify_edition_rel`.
- `placement_label_consistent(subtype, placement)` states the invariant: the suffix is present **exactly** when a sense-asserting relation has no identified target — both directions.
- Gate **W5a** in [`src/placement_axis_check.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/placement_axis_check.py) applies it to every sidecar row and is a **STOP**, not a note. It was **RED at 5,066 rows** against the pre-fix sidecar — the RED-pin the wave's test bar (PLAN ruling 10) requires — and is 0 after.
- Consumers never learn a second vocabulary: `base_subtype()` resolves a twin back to the label their tables are keyed on, so `TYPOLOGY`, `CLASS_OF` and the h180 strata keep one row per relation kind. A twin falling through to a default would have painted the exact rows this issue is about as green ＋ additions — pinned by a selftest in [`build_reglue_sheet_v2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_reglue_sheet_v2.py).

## 5. The store was NOT rewritten — measured, not assumed

The handoff and [ARCHITECTURE §2](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/ARCHITECTURE_SanskritLexicography_CLAUDE_HARDENING_WAVE.md) expect a *ledgered store rewrite + mirror refresh*. The census answers where the label actually lives:

- `pwg_ru_translated.jsonl` carries an `edition_rel` field on **86 rows** — 76 `pwg`/`base` and 10 `pwg`/`pwg_internal_correction`. Neither is sense-asserting, so **0 canonical-store rows change**. Proved twice: the census's own store pass, and gate A5 run with the sha pinned (`--store-sha 58c2172…`, `--store-rows 11519`) — byte-identical.
- The mirror carries store rows and `ru` bodies. This change touches **no `ru`**, so a mirror refresh is a no-op, not a skipped step: `audit_store_gates.py` before and after is **byte-identical output**, including `only_src=0 only_mirror=0 changed_ru=0`. (Independent reason not to touch it: W4/H3751 held the mirror mid-flight during this run.)
- The label lives in the **derived** sidecar `src/pwg_ru_relationships.jsonl` (gitignored) and its committed summary `pwg_ru/relationships_rollup.tsv`. That does not make the ledger optional — 5,000 rows changing meaning with no before/after record is exactly the unledgered mutation ruling 14 exists to catch.

**Ledger:** `pwg-ru-data/tm/h3752_relabel_ledger.jsonl` — a header row (rule, both sha256s, move counts) plus **5,066 entries**, each with `row_key`, before/after label, and the `placement` / `placement_reason` / `target_sense` the new label rests on. Rows join on the H3300 `row_key`, never the bare `(subcard, sense_tag)` pair: 132 pairs repeat here (595 rows under them) and a bare-pair join would ledger the wrong sibling ([FINDINGS §551](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)). **All 5,066 moves are in scope** (a placed label becoming its own twin on an unplaced row); **0 out-of-scope moves**.

The sidecar also grew 6,320 → 6,326 rows because it had been stale since 28-08-2026. Those 6 are counted as `added_rows`, never as label changes.

## 6. Proof

| claim | command | result |
|---|---|---|
| classifier contract, incl. the RED pin | `python src/edition_rel.py --selftest` | OK |
| census reproducible + the ×2 halt arithmetic | `python src/h3752_relation_label_census.py --selftest` | PASS |
| ledger joins on `row_key`, scopes every move | `python src/h3752_relabel_ledger.py --selftest` | PASS |
| **W5a RED before the fix** | `placement_axis_check.py` on the pre-fix sidecar | **exit 1, 5,066 rows** |
| all gates after | `placement_axis_check.py --store-rows 11519 --store-sha 58c2172…` | **exit 0** |
| store byte-identical | gate A5, sha pinned | PASS |
| store audit unmoved | `audit_store_gates.py` before vs after | byte-identical (3 pre-existing SAN-LOSS flags, unchanged) |
| waves 1–3 untouched | A1–A9, W2a–W2d, W3a–W3e, W7a–W7c | all 0 |

## 7. What this does NOT do

- **It does not increase the checkable population.** 637 placed rows before, 637 after. The vote sheet draws only from checkable (= placed) pairs, so its cards and their labels are unchanged — the sheet is not re-cut and no lock is re-bound.
- **It does not fix the attachment itself.** Mode B (521 dangling rows) is issue #1736's **variant D**, content alignment gloss-to-sense, explicitly orthogonal and out of scope. The three human questions the issue posed are answered here as: **variant C**, **suffix** (the boolean already exists from wave 1, so the label was the missing half), and **mode B stays a recorded reason, not a build failure** — it is already split into `out_of_range` (387, the renumbering phenomenon this project documents) versus `not_found` (134, the only genuinely unexplained bucket).
- **`a2a` carries a caveat in the open:** it is Nachträge-to-Nachträge, so its true other end may be another addendum, while `placement` is measured only against the PWG skeleton. `a2a_unplaced` is honest under either reading — it says no target was identified — but it is not evidence that a PWG sense was sought and missed.

_Dr. Mārcis Gasūns_
