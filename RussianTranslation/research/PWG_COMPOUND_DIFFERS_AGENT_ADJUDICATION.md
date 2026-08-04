# PWG vs MW compound `differs` — agent adjudication of all 4,226 rows (H1681)

_Created: 26-07-2026 · Last updated: 26-07-2026_

> **§8 supersedes the counts in §3–§6.** Both upstream extractors named in §4 have since
> been repaired (H1703) and the queue re-adjudicated against the repaired inputs. §3–§6
> record what H1681 measured on the defective inputs and are kept as the audit trail of
> how the defects were found; the live numbers are in [§8](#8-h1703-refresh--the-queue-re-adjudicated-after-both-repairs).

Adjudicator: [`src/pilot/adjudicate_compound_differs.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/adjudicate_compound_differs.py),
Opus 5 1M (`claude-opus-5[1m]`), Claude Code.
Mandate: [VOTING_SHEET_SCREENING_AUDIT_26-07-2026.md §11](https://github.com/gasyoun/Uprava/blob/main/docs/VOTING_SHEET_SCREENING_AUDIT_26-07-2026.md)
(H1664 triage, verdict HYBRID-В2). Precedent: [H1657](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1657-Opus_SanskritLexicography_acc-ncc-p2-agent-adjudication-49k_26.07.26.md).
Outputs: [`research/pwg_compound_differs_adjudication.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/pwg_compound_differs_adjudication.tsv)
(4,226 verdicts) ·
[`research/pwg_compound_differs_promotion_plan.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/pwg_compound_differs_promotion_plan.json).

**Nothing here writes the store.** No `derivation.compound.members` value changed, no
`human_reviewed` flag was set, and the 200-card blind arm was not touched.

## 1. What this queue actually is

The `differs` queue is not a list of rows where one dictionary got a compound wrong.
It is two dictionaries answering two different questions, plus four extractor defects:

| Side | Field | Source | Convention |
|---|---|---|---|
| PWG | `compound_members_pwg` | [`SanskritGrammar/data/pwg_compound_split/`](https://github.com/gasyoun/SanskritGrammar/blob/main/data/pwg_compound_split/README.md), mined from PWG's etymology parenthesis `{#aMsatrakoSa#}¦ ({#aMsatra#} + {#koSa#})` | the compound's underlying members **as lexemes**, in lemma form |
| index | `compound_members` | [`src/mw_compounds.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/mw_compounds.py), Funderburk's em-dash segmentation of MW `<k2>` = `a/Msa—tra—koSa` | a **surface segmentation** that concatenates back to the headword |

That is measurable, not asserted: the index members concatenate to the headword exactly
in **4,215/4,226** rows (99.7 %), the PWG members in **81/4,226** (1.9 %). So on a row
like `agnijihva` — PWG `agni + jihvA`, MW `agni + jihva` — neither side is wrong; PWG
names the lexeme *jihvā*, MW spells the segment as it stands after sandhi.

## 2. Method

Both shipped member lists are re-derived from the dictionaries they claim to report,
**in memory** — no upstream file is rewritten (H1657's pattern; re-deriving the queue is
an explicit non-goal here):

1. **PWG, bracket-aware.** The entry's own top-level chain is read from the balanced
   parenthesis after `¦`, with every `[...]` sub-analysis masked out, and within each
   `+`-part only the first `{#…#}` counted as a member (what follows is PWG's annotation
   of it: `<lex>f.</lex> von {#agamya#}`, `<ab>acc.</ab> von {#agni#}`, `= {#loman#}`).
   Joined to each row by the exact `L_id` that produced the shipped split, via
   [`pwg_lid_hom_map`](https://github.com/gasyoun/SanskritGrammar/blob/main/data/pwg_lid_hom_map/README.md)
   — homonym-precise, so `durakṣa` 1 and 2 are not confused.
2. **MW, variant-aware.** `<k2>` is split on `;` first (MW lists variants there), then on
   the em-dash. The hyphen is kept, not stripped: `-` is MW marking a juncture where it
   deliberately does **not** put a member boundary (`a-kAma—karSana`), which is evidence.
3. **Member attestation.** Each member is looked up in the union of the PWG/MW/GRA `<k1>`
   headword lists (206,462 headwords,
   [`HeadwordLists/now-2026/`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/now-2026/README.md)).
   "Is this segment a word at all" is the single most decisive piece of evidence in the
   ladder.
4. **DCS frequency** (`src/pwg_freq_order.tsv`) rides along on every verdict row as a
   covariate. It is deliberately **not** a stratum — see §5.

Every verdict row carries the PWG parenthesis verbatim, the raw MW `<k2>`, the re-derived
splits, the rule, and a one-clause reason, so any row can be re-audited without re-deriving
it.

## 3. Verdicts

| Verdict | rows | share | = sheet vote |
|---|---:|---:|---|
| `pwg_members-right` | 3,724 | 88.1 % | approve |
| `index_members-right` | 180 | 4.3 % | reject |
| `unresolved` | 322 | 7.6 % | defer |

By rule (first match wins; tier 1 = provenance defects, tier 2 = convention):

| # | rule | verdict | rows | ground |
|---|---|---|---:|---|
| 1 | `pwg_layer_no_headword_paren` | index | 82 | PWG states no chain for *this* headword; the shipped members came from a neighbouring parenthesis (`{#aDikazAzwika#}¦ <lex>adj.</lex> von {#aDikazazwi#} ({#aDika#} + {#zazwi#})` — those members compose `aDikazazwi`) |
| 2 | `pwg_layer_inner_chain` | index | 75 | the shipped members are the inner bracketed sub-analysis (`a + kftta`), not PWG's top-level chain (`akftta + ruc`) |
| 3 | `pwg_layer_unparsed_chain` | index | 5 | PWG's parenthesis does not resolve to a chain, so the shipped members are unverifiable |
| 4 | `mw_variant_fusion` | PWG | 10 | MW's `<k2>` lists `;`-separated variants and the extractor fused them (`gaRa—kAri; gaRakAri` → member `kArigaRakAri`) |
| 5 | `both_layers_defective` | unresolved | 1 | neither side reports its own source faithfully |
| 6 | `pwg_member_typo_in_source` | index | 12 | PWG's own text spells a non-word one edit from MW's attested member (`{#deva#} + {#sda#}` for *sūda*, `{#eka#} + {#hasaM#}` for *haṃsa*) — a pwg.txt transcription typo |
| 7 | `pwg_lexeme_vs_mw_suffixed_tail` | PWG | 323 | same cut; MW's last segment is PWG's lexeme plus a secondary suffix that derives the whole compound (`agra + dAna` vs `agra + dAnin`) |
| 8 | `same_split_pwg_lemma_form` | PWG | 3,018 | same cut, members differ only in form — MW gives the sandhi surface, PWG the lexeme (`sant`/`saj`, `payas`/`payo`, `brahman`/`brahma`, `jihvA`/`jihva`) |
| 9 | `mw_cut_absorbs_initial_vowel` | PWG | 63 | MW's segment is PWG's member minus its initial vowel, eaten at the seam (`akza` → `kza`, `aSva` → `'Sva`, avagraha still in the `<k2>`) |
| 10 | `mw_anusvara_right_of_boundary` | PWG | 12 | MW puts the linking anusvāra right of the cut and hyphenates it (`jala—M-gama`); PWG keeps the accusative first member (`jalam + gama`) |
| 11 | `privative_scope_disputed` | unresolved | 15 | PWG negates the whole compound (`a + kAmakarSana`), MW's hyphen binds the privative to member 1 (`a-kAma—karSana`) — two readings, nothing settles it |
| 12 | `mw_cut_leaves_nonword` | PWG | 277 | the cuts differ and every PWG member is attested while MW's is not a word (`mahA + arha` vs `mahA + rha`) |
| 13 | `pwg_cut_leaves_nonword` | index | 6 | the mirror case |
| 14 | `cut_moved_both_readings_lexical` | unresolved | 253 | the cuts differ and **both** readings decompose into attested headwords (`tridiva + okas` vs `tri + divOkas`) — a genuine lexicographic disagreement |
| 15 | `cut_moved_neither_reading_lexical` | unresolved | 9 | neither reading is lexical throughout |
| 16 | `mw_splits_derivational_suffix` | PWG | 14 | MW gives `-maya`/`-tA` its own member (`sarva—veda—maya`); a secondary suffix applies to the finished compound, it is not one of the words compounded |
| 17 | `mw_splits_bound_morph` | PWG | 7 | MW cuts finer and the extra piece is not a word (`go—zWa—pati` for *goṣṭha-pati*) |
| 18 | `granularity_ic_vs_full_decomposition` | unresolved | 28 | MW decomposes a lexicalised member further and every piece is attested (`go—tra—vfkza` vs `gotra + vfkza`) — immediate constituents vs full decomposition is a convention neither entry states |
| 19 | `granularity_pwg_finer` | unresolved | 2 | the mirror case |
| 20 | `arity_differs_no_alignment` | unresolved | 14 | different arity and neither list is a merge of the other |

## 4. Four upstream defects, and how far they reach

Measured over the whole of each source, not just this queue. Neither is repaired here —
both are routed as `[integrity]` issues.

| Defect | Where | In this queue | Whole dataset |
|---|---|---:|---|
| top-level chain not bracket-aware; the first `+`-chain in the entry head can be an inner sub-analysis or a *different word's* parenthesis | [`SanskritGrammar/scripts/pwg_compound_split.py`](https://github.com/gasyoun/SanskritGrammar/blob/main/scripts/pwg_compound_split.py) | 162 rows (3.8 %) | **344/16,738 rows ship the wrong chain (2.06 %)**, a further **368 (2.20 %) are unverifiable** — 4.25 % of a dataset advertised as high-precision splitter gold and consumed by kosha + SanskritSpellCheck |
| `_clean_member` strips `;` **and** the space, fusing MW's `;`-separated `<k2>` variants into one bogus member | [`src/mw_compounds.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/mw_compounds.py) | 10 rows | **41/106,603 MW compound records (0.04 %)**, every one producing a member that is not a word |
| transcription typos inside PWG's own member strings (`sda`, `hasaM`, `Bade`, `preDa`, `ktatu`) | `csl-orig/v02/pwg/pwg.txt` | 12 rows | not swept beyond this queue; candidates for the monthly csl-orig batch, never patched directly |
| the blind arm's sheet is unbound and has a duplicate card | H1628 generator | — | see §6 |

## 5. Promotion plan — what the existing 200-card arm can and cannot price

Gate: per-stratum **Wilson 95 % lower bound ≥ 0.90** on agent precision, measured against
the human vote of the blind arm; promoted rows are stamped provenance `agent`, never
`human_reviewed`; nothing promotes before the vote lands. Strata are the rules of §3;
strata under 25 rows pool into `residual-undersized`.

| stratum | rows | arm cards | max Wilson-95 lb if the human agrees with every arm card | promotable |
|---|---:|---:|---:|---|
| `same_split_pwg_lemma_form` | 3,018 | 138 | 0.973 | **yes** |
| `pwg_lexeme_vs_mw_suffixed_tail` | 323 | 17 | 0.816 | no |
| `mw_cut_leaves_nonword` | 277 | 11 | 0.741 | no |
| `cut_moved_both_readings_lexical` | 253 | 9 | 0.701 | no |
| `residual-undersized` | 107 | 12 | 0.758 | no |
| `pwg_layer_no_headword_paren` | 82 | 6 | 0.610 | no |
| `pwg_layer_inner_chain` | 75 | 4 | 0.510 | no |
| `mw_cut_absorbs_initial_vowel` | 63 | 0 | — | unpriceable |
| `granularity_ic_vs_full_decomposition` | 28 | 9 | 0.701 | no |

**So the 200 votes close 3,018 of 4,226 rows (71.4 %), not all of them.** A stratum needs
**≥ 35 arm cards** to clear 0.90 even at 100 % agreement, and the H1628 sample was drawn
before these strata existed — it is stratified by length × DCS frequency × member-count,
which cuts across the rule strata rather than along them. Two consequences, both worth
recording rather than papering over:

- Banding the big rule by DCS frequency (the H1628 stratifier) is **strictly harmful
  here**: it splits the ~140 arm cards into roughly 74/25/23/18 and none of the four
  bands can reach 0.90, so ~1,400 rows would lose any route to promotion. DCS frequency
  therefore rides as a covariate, not a stratum.
- The remaining 1,208 rows stay `needs_human`. Pricing them needs a **second, rule-
  stratified arm of ~35 cards per unpriced rule (≈ 280 cards)** — a follow-on, not this
  handoff, and cheaper than the 4,026 votes the queue originally implied.

## 6. The blind arm had two defects — ✅ repaired 26-07-2026 by MG's `re-cut` ruling

H1681 as executed was forbidden to modify the 200-card sheet, so it reported both defects
below and routed them to [H1703](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1703-Opus_SanskritLexicography_compound-differs-second-arm-and-sheet-binding_26.07.26.md).
**MG ruled option (a), re-cut**, the same day, so the generator was fixed and the sheet
re-drawn from the same `seed=1628`:

- `dedupe_by_card_id()` collapses derivation-layer rows that share a `(k1, hom)` card id
  **before** sampling; the frame is now 4,123 rows, one per card id.
- `--write` now calls `stamp()` + `write_lock()`, so the sheet carries a content hash and
  `review/locks/sanskritlexicography-pwg-compound-differs_stratified200.lock.json` is
  committed. Bound at `sha256:31c106bb13cd2bad…`, 200 distinct ids, gate `G6-compound`.
- The HTML stays gitignored (it embeds store text); the `generated` string is pinned to
  `26-07-2026` so whoever regenerates it reproduces the exact bytes the lock binds.

The arm numbers in §5 are the re-cut sheet's. What follows is the diagnosis, kept because
the second arm (H1703) must not repeat it:

1. **No lock, no content-hash stamp.**
   [`compound_differs_review_sample.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/compound_differs_review_sample.py)
   renders the sheet but never calls `stamp()` / `write_lock()`, and
   `review/locks/sanskritlexicography-pwg-compound-differs_stratified200.lock.json` does
   not exist. Per the H1404 binding standard,
   [`validate_decisions.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/validate_decisions.py)
   rejects any export whose `sheet_id` does not resolve to a committed lock — so the 200
   votes, once cast, **cannot be validated or applied**.
2. **A duplicate card**, and behind it a queue-wide row-vs-card mismatch. The old frame
   had 200 rows but 199 distinct `(k1, hom)` keys (`duHsTita` twice). Deduping the whole
   queue showed the scale: **the 4,226 `differs` rows are 4,123 distinct card ids** — 98
   keys carry 2–3 rows, because `headword_index.tsv` holds a row per part-of-speech
   reading (`agraRI` as `adj.` and as `m.`; 2,383 of its keys are multi-row overall)
   while a card id is only `(k1, hom)`. The adjudication is unaffected in substance: all
   103 duplicate rows agree with their twin on both members and verdict (0 disagreements),
   because a compound's analysis does not depend on the entry's `lex`. The verdict TSV
   still carries one row per queue row; **the count to quote for cards is 4,123.**

## 7. Non-goals and limitations

- **Non-goals** (from the handoff): voting the 200 sheet, applying anything to the store,
  re-deriving the `differs` queue, repairing either upstream extractor.
- `seam_compatible` is a deliberately weak, checkable proxy for "same cut, different
  spelling" (prefix agreement + a ±2 length window + an explicit glide rule), not a sandhi
  engine. It errs toward calling a pair the same member; the blind arm prices exactly that.
- The typo rule (§3 #6) excludes any pair that is seam-compatible, which also excludes a
  handful of genuine typos whose shape looks like a sandhi alternant (`{#vaja#}` for
  *vaṭa*); those land in rule #8 and would be promoted with a typo in the member string.
  Known, measured at ~2 rows, and the reason it is written down rather than smoothed over.
- Member attestation uses `<k1>` headword lists, which do not list every stem form
  (`jIvant`, `bfhant`), so "unattested" is evidence, not proof.

## 8. H1703 refresh — the queue re-adjudicated after both repairs

Both extractor defects in §4 are fixed and merged, and this pass re-ran the whole chain
against the repaired inputs — `pwg_compound_split.py` →
`pwg_derivation_layer.py` → `adjudicate_compound_differs.py --write`.

| repair | PR | effect on its own dataset |
|---|---|---|
| PWG chain not bracket-aware / not headword-anchored ([SanskritGrammar#527](https://github.com/gasyoun/SanskritGrammar/issues/527)) | [SanskritGrammar#529](https://github.com/gasyoun/SanskritGrammar/pull/529) | 17,112 rows (was 16,745): 16,094 unchanged · **139 members corrected** · 512 dropped as unresolvable · 879 added that the old head-scan missed |
| MW `<k2>` variant fusion ([#801](https://github.com/gasyoun/SanskritLexicography/issues/801)) | this PR | **41/106,603** MW records corrected, 22 of them arity-corrected; 36 `headword_index.tsv` rows, `paradigm_stats.tsv` + `reverse_paradigm_index.json` regenerated |

### 8.1 The queue did not shrink — it moved, and grew

H1703 predicted "either repair shrinks the `differs` queue". Measured, it does not: the
repairs remove defect-driven rows **and** add genuine new comparisons, and the second
effect is larger.

| | cards |
|---|---:|
| `differs` cards before | 4,123 |
| left the queue (now `agrees`, `index-only`, or no PWG chain at all) | −118 |
| entered (163 brand-new PWG comparisons + 74 that had no PWG chain before + 4 from `agrees`) | +241 |
| **`differs` cards after** | **4,246** (4,353 rows) |
| of the cards that stayed, PWG members corrected | 42 |

### 8.2 The three defect strata are gone

| rule | H1681 (defective inputs) | H1703 (repaired) |
|---|---:|---:|
| `pwg_layer_inner_chain` | 75 | **0** |
| `pwg_layer_no_headword_paren` | 82 | **2** |
| `pwg_layer_unparsed_chain` | 5 | **0** |
| `mw_variant_fusion` | 10 | **0** |
| `both_layers_defective` | 1 | **0** |

Those 173 rows were the queue paying for extractor bugs. What is left is what the queue
was always supposed to be: 3,152 rows of "same cut, different spelling", plus genuine
convention and lexicographic disagreements. Verdicts are now
`pwg_members-right` 3,975 (91.3 %) · `unresolved` 354 (8.1 %) ·
`index_members-right` 24 (0.6 %).

### 8.3 Two arms, and what each can price

The H1628 arm samples along length × DCS-frequency × member-count, which cuts across the
adjudicator's rules — it lands 139 of its cards in one stratum and 0–16 in each of the
rest. The second arm
([`compound_differs_arm2_sample.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/compound_differs_arm2_sample.py),
seed 1703) is stratified on the rules themselves, drawn **disjointly** from arm 1, 35
cards per unpriced stratum — 35 because `wilson_lower(35, 35) = 0.901` and
`wilson_lower(34, 34) = 0.898`, so 35 is the smallest arm that can clear the gate at all.

| stratum | rows | arm 1 cards / max lb | arm 2 cards / max lb | pooled | basis |
|---|---:|---|---|---:|---|
| `same_split_pwg_lemma_form` | 3,152 | 139 / **0.973** | — | 0.973 | wilson (arm 1) |
| `pwg_lexeme_vs_mw_suffixed_tail` | 334 | 16 / 0.806 | 36 / **0.904** | 0.931 | wilson (arm 2) |
| `mw_cut_leaves_nonword` | 293 | 11 / 0.741 | 35 / **0.901** | 0.923 | wilson (arm 2) |
| `cut_moved_both_readings_lexical` | 263 | 10 / 0.722 | 36 / **0.904** | 0.923 | wilson (arm 2) |
| `mw_anusvara_right_of_boundary` | 107 | 1 / 0.207 | 37 / **0.906** | 0.908 | wilson (arm 2) |
| `residual-undersized` | 106 | 10 / 0.722 | 36 / **0.904** | 0.923 | wilson (arm 2) |
| `mw_cut_absorbs_initial_vowel` | 67 | 0 / — | 36 / **0.904** | 0.904 | wilson (arm 2) |
| `granularity_ic_vs_full_decomposition` | 31 | 9 / 0.701 | 22 | 31 | **census** |

Read the two "max lb" columns as *the best that arm can do* — the bound if the human
agrees with every card in it; the actual bound comes from the actual votes.

Two things worth stating plainly:

- **Every stratum now has a promotion route.** Before this pass, 3,018 of 4,226 rows
  could be promoted and 1,208 could not be priced at all, whatever the human did. Now
  all 4,353 rows sit in a priceable stratum.
- **The 31-row stratum is promotable by census, not by inference.** Arm 1's 9 cards plus
  arm 2's 22 cover every row in it, so there is nothing to extrapolate to — its Wilson
  bound (0.890) is irrelevant, and the plan says `promotion_basis: census` rather than
  pretending the interval cleared.

### 8.4 Both sheets are bound, and the binding was tested

Item 1 of H1703 existed because the H1628 sheet rendered without `stamp()`/`write_lock()`,
so `validate_decisions.py` would have rejected the export *after* 200 votes were spent.
Both sheets now carry a committed lock, and this pass verified the binding end-to-end on
a synthetic export rather than assuming it:

| export | arm 1 | arm 2 |
|---|---|---|
| complete, correct hash | **accepted** (200 items) | **accepted** (232 items) |
| tampered `content_hash` | rejected — "votes cast against a different generation" | rejected |
| one vote missing | rejected — item-id drift | rejected |
| one unknown card id | rejected — item-id drift | rejected |

Arm 2's card ids come from the **lock**, not the frame TSV, for the same reason: the lock
is what the human's export will be checked against, so it is the only list that can pay
out. An unbound sheet is counted as pricing nothing.

**9 of arm 1's 200 cards are no longer in the queue** — they were drawn before the
repairs and are now `agrees` or have no PWG chain. They are reported in the plan
(`cards_left_the_queue`), and votes on them will simply not apply. Arm 1 was NOT re-cut a
second time: its lock was committed hours earlier under the human `re-cut` ruling, its
139 `same_split` cards still price that stratum at 0.973, and re-cutting would invalidate
a live lock to recover 9 cards.

### 8.5 Arm 1 no longer reproduces from `master` — and a generator can no longer rewrite a live lock in silence

A sheet generator reads **live** data. Arm 1's frame comes from
`pwg_derivation_layer.tsv`, which the two repairs rewrote — so re-running
`compound_differs_review_sample.py --write` on current `master` does not reproduce the
committed sheet, it draws a **different 200 cards** and rewrites the live lock. Measured:
the committed lock is `sha256:31c106bb…`, a re-run on `master` renders `sha256:68a6297b…`.
Votes already cast would stop validating, and nothing would have said so until
`validate_decisions.py` rejected the export — after the human spent them. Same failure
shape as the unbound sheet of Item 1, one step later in the pipeline.

Two things follow, both applied:

- **Arm 1 reproduces at [v1.83.0](https://github.com/gasyoun/SanskritLexicography/releases/tag/v1.83.0)**
  (commit `c84db1d7`), where it renders `sha256:31c106bb…` byte-for-byte — verified.
  Regenerate it there, never on `master`. Arm 2 reproduces on `master`
  (`sha256:f765faf4…`, verified).
- **`review_binding.write_lock()` now refuses** to overwrite a lock binding a different
  content hash, raising `LockCollision` with both hashes and the recovery path. A
  same-hash rewrite still succeeds, so honest idempotent regeneration is unaffected; a
  deliberate re-cut passes `force=True` / `REVIEW_LOCK_FORCE=1`. This protects **every**
  sheet in the estate, not only these two.

### 8.6 Blindness

Arm 2 is stratified **by the adjudicator's own rule**, so it would be trivially
self-fulfilling if a card showed it. The rendered card carries the two member lists, the
source PWG parenthesis, the source MW `<k2>`, and the same neutral badges as arm 1 —
never the stratum, the rule, the agent's verdict or its reason. Those live in the frame
TSV, which is the sample-design audit trail, not the voting surface. A selftest asserts
that no card JSON contains any of those fields.

## Reproduce

```sh
python src/pilot/adjudicate_compound_differs.py --selftest   # parsers + 8 rule fixtures
python src/pilot/adjudicate_compound_differs.py --report     # counts, writes nothing
python src/pilot/adjudicate_compound_differs.py --write      # verdicts TSV + plan JSON
python src/pilot/compound_differs_review_sample.py --write   # arm 1 — ONLY at v1.83.0 (see §8.5)
python src/pilot/compound_differs_arm2_sample.py --selftest  # allocation + blindness
python src/pilot/compound_differs_arm2_sample.py --write     # draw + stamp + lock arm 2
```

Upstream, in the `SanskritGrammar` sibling, before any of the above:

```sh
python scripts/pwg_compound_split.py --selftest
python scripts/pwg_compound_split.py
python src/pwg_derivation_layer.py        # back in RussianTranslation
```

Needs the `csl-orig` and `SanskritGrammar` siblings (read-only); override with
`CSL_ORIG_ROOT` / `SANSKRITGRAMMAR_ROOT`.

_Dr. Mārcis Gasūns_
