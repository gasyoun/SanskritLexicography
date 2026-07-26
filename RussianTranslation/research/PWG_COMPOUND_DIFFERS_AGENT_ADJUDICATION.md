# PWG vs MW compound `differs` — agent adjudication of all 4,226 rows (H1681)

_Created: 26-07-2026 · Last updated: 26-07-2026_

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
| `same_split_pwg_lemma_form` | 3,018 | 140 | 0.973 | **yes** |
| `pwg_lexeme_vs_mw_suffixed_tail` | 323 | 15 | 0.796 | no |
| `mw_cut_leaves_nonword` | 277 | 15 | 0.796 | no |
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
  here**: it splits the 140 arm cards into 74/25/23/18 and none of the four bands can
  reach 0.90, so ~1,400 rows would lose any route to promotion. DCS frequency therefore
  rides as a covariate, not a stratum.
- The remaining 1,208 rows stay `needs_human`. Pricing them needs a **second, rule-
  stratified arm of ~35 cards per unpriced rule (≈ 280 cards)** — a follow-on, not this
  handoff, and cheaper than the 4,026 votes the queue originally implied.

## 6. The blind arm itself has two defects (reported, not touched)

H1681 is forbidden to modify the 200-card sheet. Both of these block the vote from
landing, so they are named here and routed on:

1. **No lock, no content-hash stamp.**
   [`compound_differs_review_sample.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/compound_differs_review_sample.py)
   renders the sheet but never calls `stamp()` / `write_lock()`, and
   `review/locks/sanskritlexicography-pwg-compound-differs_stratified200.lock.json` does
   not exist. Per the H1404 binding standard,
   [`validate_decisions.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/validate_decisions.py)
   rejects any export whose `sheet_id` does not resolve to a committed lock — so the 200
   votes, once cast, **cannot be validated or applied**.
2. **A duplicate card.** The frame TSV has 200 rows but **199 distinct `(k1, hom)` keys**:
   `duHsTita` appears twice (the derivation layer carries two rows for that key), so two
   cards share one id. All arm counts in §5 are over the 199 distinct ids.

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

## Reproduce

```sh
python src/pilot/adjudicate_compound_differs.py --selftest   # parsers + 8 rule fixtures
python src/pilot/adjudicate_compound_differs.py --report     # counts, writes nothing
python src/pilot/adjudicate_compound_differs.py --write      # verdicts TSV + plan JSON
```

Needs the `csl-orig` and `SanskritGrammar` siblings (read-only); override with
`CSL_ORIG_ROOT` / `SANSKRITGRAMMAR_ROOT`.

_Dr. Mārcis Gasūns_
