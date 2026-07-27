# ACC × NCC P2 — agent adjudication of all 49,019 Tier C/D rows

_Created: 26-07-2026 · Last updated: 26-07-2026_

Handoff [H1657](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1657-Opus_SanskritLexicography_acc-ncc-p2-agent-adjudication-49k_26.07.26.md)
· executor **Opus 5 1M (`claude-opus-5[1m]`)** · ruling **MG, 26-07-2026, option В2**
· supersedes the human-adjudication half of
[H264](https://github.com/gasyoun/Uprava/blob/main/handoffs/H264-Sonnet_SanskritLexicography_acc_ncc_p2_adjudication_06.07.26.md)
(its P0/P1 lineage is untouched).

MG's 09-07-2026 ruling — **full coverage, no sampling** — is not reversed. All
49,019 Tier C/D rows carry a verdict. What changed is who casts it: an agent
with cited evidence, with the human's minutes spent measuring *the adjudicator*
on a 686-card stratified sample instead of re-deciding each row.

---

## 0. The headline is not the adjudication

Before a single Tier C/D row could be judged, the candidate file had to be read
closely — and it does not mean what P1 thought it meant.

[`parse_ncc.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/parse_ncc.py)
derives its `match_key` as `slp1_simplify(to_slp1(iast))` from the **raw NCC
headword**, which is capitalised — `Kalāpatattvārṇava`. `to_slp1` is
case-preserving and does not map an uppercase IAST initial, so the capital
survives into the SLP1 string, where `slp1_simplify` reads it as a **different
SLP1 letter**:

| NCC headword | key P1 used | key it should be | what the capital became |
|---|---|---|---|
| Kalāpatattvārṇava | `khalapatattvarnava` | `kalapatattvarnava` | `K` = kh |
| Rāmāyaṇa | `namayana` | `ramayana` | `R` = ṇ |
| Yogasūtra | `nogasutra` | `yogasutra` | `Y` = ñ |
| Ekāvalī | `aikavali` | `ekavali` | `E` = ai |
| Bhāgavata | `bhhagavata` | `bhagavata` | `B` = bh |
| Śivastotra | `śivastotra` | `sivastotra` | `Ś` not transliterated at all |

**Measured over the shipped `ncc.jsonl`: 91,548 of 152,526 keys (60.0%) are
wrong**; 20,571 (13.5%) still contain non-ASCII characters that no ACC key can
ever match.

This has two separate consequences, and they pull in opposite directions.

### 0.1 Precision side — Tier D is almost entirely an artefact

40,757 of Tier D's 43,666 rows (**93.3%**) are pairs whose titles are
**exactly identical** once the NCC key is derived correctly. The inserted `h`
(or the ṅ/ñ/ṇ fold) is the entire edit distance P1 measured. They are
Tier-A-grade matches wearing a Tier D label.

| Tier C/D row class, on repaired keys | rows |
|---|---:|
| exact title match after repair | 40,757 |
| equal under the nasal/geminate fold P1 already accepts as Tier B | 615 |
| genuinely different titles (the real adjudication problem) | 7,647 |
| **total** | **49,019** |

### 0.2 Recall side — thousands of true links were never proposed at all

Where the corruption changes the **first letter**, P1's first-letter blocking
(Tier D) and its prefix bisect (Tier C) never compared the pair, so **no
candidate row exists to adjudicate**. Re-deriving the keys correctly and
re-running only the exact-key join:

| exact-key (Tier A) overlap | distinct keys |
|---|---:|
| as P1 shipped | 8,397 |
| with NCC keys repaired | **22,775** |
| never proposed as candidates | **14,379** |

That is a **171% increase in the exact-match tier alone**, before any fuzzy
tier is re-run. Every `Rāmāyaṇa`, every `Yoga-`, every `Ś-` initial work in NCC
is currently invisible to the crosswalk.

**This was out of scope here** — H1657's non-goals forbid re-running P1 matching
or changing tier definitions, and this pass did not touch
`crosswalk_candidates.jsonl.gz` or any tier. It was filed as
[integrity issue #779](https://github.com/gasyoun/SanskritLexicography/issues/779)
and queued as its own handoff. **What it meant for the numbers below:** the
crosswalk was adjudicated at ~64% of its achievable exact-match recall, and no
verdict in this report changed that.

### 0.1 Resolved — repaired and re-run, 26-07-2026 (H1671)

[H1671](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1671-Opus_SanskritLexicography_acc-ncc-p0p1-ncc-key-repair-rerun_26.07.26.md)
fixed `parse_ncc.match_key_for` (case-fold + NFC before transliteration) and re-ran
P0 → P1 → P2 on the corrected keys. §0's predictions held on the re-run, to the row:
the 40,757 exact-after-repair pairs became **Tier A upstream**, and the exact-key
overlap went 8,397 → 22,775 distinct keys.

**Everything from §1 onwards therefore describes the PRE-REPAIR run**, kept as the
record of what was adjudicated on 26-07-2026 and of how the defect was found. It is
not the current state of the crosswalk. For that, and for the full before/after
migration, see [`NCC_KEY_REPAIR_MIGRATION_2026.md`](NCC_KEY_REPAIR_MIGRATION_2026.md);
for current counts, [`P1_COUNTS.md`](P1_COUNTS.md) / [`P2_COUNTS.md`](P2_COUNTS.md).

| | this report (pre-repair) | after H1671 |
|---|---:|---:|
| Tier C/D rows adjudicated | 49,019 | 10,614 |
| rule 1 `exact_after_key_repair` | 40,757 | 0 |
| rule 2 `fold_after_key_repair` | 615 | 0 |
| approve / reject | 41,947 / 7,072 | 920 / 9,694 |
| `works_crosswalk.tsv` rows | 120,241 | 249,802 |

Two consequences for anything built on this report:

- **The 686-card spot-check sample described below is void**, and so is any vote
  cast against it. It was drawn from a population that no longer exists — 3,550 of
  its rows are not candidates at all any more. It was never voted (no
  `decisions.json` was ever saved beside it), so no human work was discarded. Its
  replacement is a fresh 698-card sample over 17 strata.
- **The precision figures below were never measured**, only planned; no stratum
  cleared a bar, so no row from this run was ever promoted into the crosswalk.

---

## 1. The adjudicator

[`adjudicate_p2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/adjudicate_p2.py)
is a rule ladder, not a per-row language-model call — a deliberate choice, and
the report states it plainly rather than implying 49,019 individual model
judgements. Every rule fires on evidence read out of the two catalogue entries,
and every verdict carries that evidence, so any row can be re-audited without
re-deriving it. The first rule that matches wins.

| # | rule | verdict | rows | ground |
|---:|---|---|---:|---|
| 1 | `exact_after_key_repair` | approve | 40,757 | repaired keys identical — the same evidence on which Tier A's 107,815 rows were auto-accepted |
| 2 | `fold_after_key_repair` | approve | 615 | equal under P1's own Tier B nasal/geminate fold |
| 3 | `stem_variant` | approve | 215 | `-nāman`/`-nāma`: one title cited in stem vs nominative form |
| 4 | `person_vs_work` | reject | 3,064 | one side is a person (poet, king, pupil-of), the other a work — not the same catalogue object |
| 5 | `commentary_extension` | reject | 144 | the longer title adds ṭīkā/vṛtti/bhāṣya/vyākhyā — a commentary is a different work from its base |
| 6 | `different_author` | reject | 437 | both catalogues name an author and the names disagree |
| 7 | `shared_citation` | approve | 334 | both entries cite the same manuscript witness |
| 8 | `same_author_prefix` | approve | 26 | same author and one title properly extends the other |
| 9 | `manual_extension_unsupported` | reject | 184 | adds vidhi/prayoga/paddhati/stotra with nothing corroborating |
| 10 | `prefix_extension_unsupported` | reject | 2,062 | Tier C prefix containment only, extra segment substantive |
| 11 | `edit_distance_unsupported` | reject | 1,181 | repaired titles still differ, no shared witness or author |

**41,947 approve · 7,072 reject · 49,019 total. Zero rows skipped.**

Two evidence extractors were deliberately made more tolerant than the ones in
`parse_acc.py`/`parse_ncc.py`, because the shipped `sigla` arrays intersected on
only 260 of the 7,647 hard rows: a looser citation shape that catches ACC's
comma form (`Oudh XIX, 86` against NCC's `Oudh XIX. 86`), and a siglum alias
table (ACC `Ulwar 2196` = NCC `Alwar 2196`). Those are read-only additions
inside the adjudicator; the P0 parsers are untouched.

### What the ladder is weakest at

- **Rule 1 inherits Tier A's own risk**: two genuinely different works that
  share a title (`Viṣṇusahasranāma` is several distinct texts) are approved.
  This is the accepted Tier A/B policy applied consistently, not a new
  looseness — but at 40,757 rows it is the single largest thing the human
  sample is measuring.
- **Rule 4's person detector is heuristic** — a regex over descriptive phrases
  plus NCC's `--Title` work-list shape. It gets the verdict right more often
  than it gets the *reason* right.
- **`manual_extension_unsupported` is the genuinely mixed class** — a
  `-pūjāvidhāna` is sometimes the same text as the bare `-pūjā` and sometimes
  not. It rejects by default and is stratified separately so the sample prices
  exactly that.

---

## 2. The spot-check sample — sized before it was drawn

[`build_p2_spotcheck_sheet.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/build_p2_spotcheck_sheet.py)
draws **686 cards across 16 strata** (population 49,019; seed 16572026, fixed).
Sizing was fixed before the draw: **n = 50 for approve strata** (promotion
gates on those), **n = 40 for reject strata**, census below that.

Strata are `tier × rule × score band`, with two documented departures:

- **Score band is dropped for the three title-identity rules.** For those the
  P1 score is the edit distance between the ACC key and a *corrupted* NCC key —
  a measure of how badly `parse_ncc.py` mangled the headword, not of how well
  the works match. Banding on it would stratify on noise.
- **Undersized strata are pooled a whole group at a time** (band → tier+rule →
  rule). A census of 6 rows has a Wilson lower bound of 0.61 even at 6/6, so it
  could never clear a bar however right the agent was.

**The sheet is blind.** It shows the same card the full 49,019-row sheet
shows, with no agent verdict anywhere in the DOM. Agent verdicts live in
`p2_spotcheck_manifest.json`, which the gate joins against the returned votes.
Showing the verdict would measure agreement with a visible answer, and every
precision figure downstream would be an anchoring artefact.

The sheet is written to `review/sanskritlexicography-acc_ncc_p2_spotcheck.html`
(0.36 MB). `review/` is gitignored, so like the original 22 MB sheet it is
local-only — regenerate with the command in §5.

---

## 3. The bar — the one question for a human

Per H1657 deliverable 5 the precision bar is **not the agent's to pick**: it
decides how many of 49,019 rows enter a citable dataset, and that is a
scholarly standard, not a statistic. Here is the distribution and the
consequence, stated in rows.

Precision is published per stratum as a **Wilson 95 % lower bound**, never a
point estimate (the discipline H1470 ratified: a stratum at 3/3 = 1.000 has a
lower bound near 0.44 and has proved nothing).

**Best case any sample of this size can produce** — every stratum votes perfect:

| bar | approve rows promoted | approve rows held | reject rows published |
|---:|---:|---:|---:|
| 0.80 | 41,947 | 0 | 7,072 |
| 0.85 | 41,947 | 0 | 7,072 |
| 0.90 | 41,921 | 26 | 7,072 |
| 0.95 | **0** | 41,947 | 0 |
| 0.98 | **0** | 41,947 | 0 |

**A bar of 0.95 promotes nothing, however good the adjudicator is.** At n = 50
the highest attainable lower bound is 0.929; at n = 40 it is 0.912. That is a
fact about the sample size, not about the rules. Reaching a 0.95 bar would
require roughly n = 80 per stratum — about 1,400 cards instead of 686 — which
is a larger ask and a separate decision.

So the live question is a choice between:

- **0.90** — the tightest bar this sample can actually clear. Costs the tiny
  `same_author_prefix-alltiers` stratum (26 rows) even on a perfect vote.
- **0.85** — clears every stratum on a perfect vote and still fails any
  stratum that comes back below ~86 % agreement.
- **0.95 or above** — a deliberate decision to promote nothing now and re-draw
  a ~1,400-card sample first.

A human decides. Full per-stratum table with the bound at 0, 1 and 2 errors:
[`P2_PRECISION.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/works_catalogue/P2_PRECISION.md).

---

## 4. State of the outputs right now

No votes have been returned, so **no stratum is measured and nothing is
promoted**. That is the designed state, not an unfinished one — H1657's
non-goals forbid promoting on an unmeasured stratum however plausible the rows
look.

| file | rows | what it is |
|---|---:|---|
| `works_crosswalk.tsv` | 120,241 | Tier A (107,815) + Tier B (12,426) auto-accepted, exactly as before |
| `works_crosswalk_rejected.tsv` | 0 | confirmed non-matches — empty until reject strata are measured |
| `works_crosswalk_agent_proposed.tsv` | **49,019** | every Tier C/D row with the verdict the agent proposed, promotable without re-adjudication |
| `p2_agent_verdicts.jsonl.gz` | 49,019 | the evidence ledger — both entries verbatim, matched span, tier, score, rule, one-clause reason |

**Rows left agent-proposed and not promoted: 49,019 (41,947 proposed approve,
7,072 proposed reject).** Stated here rather than buried, per the acceptance
criteria. On a 0.90 bar with a perfect vote that becomes 41,921 promoted and 26
held; the arithmetic is in §3.

`apply_p2_decisions.py` gained one destination (`works_crosswalk_agent_proposed.tsv`)
and a provenance passthrough — it remains the single application path, per the
handoff's own instruction not to invent a second one.

---

## 5. Reproduce

```
python HeadwordLists/works_catalogue/adjudicate_p2.py
python HeadwordLists/works_catalogue/build_p2_spotcheck_sheet.py
python HeadwordLists/works_catalogue/p2_precision_gate.py
python HeadwordLists/works_catalogue/apply_p2_decisions.py \
        HeadwordLists/works_catalogue/p2_gated_decisions.json
```

Once the 686 votes come back as `sanskritlexicography-acc_ncc_p2_spotcheck_decisions.json`:

```
python HeadwordLists/works_catalogue/p2_precision_gate.py <votes.json> --bar <ruled bar>
python HeadwordLists/works_catalogue/apply_p2_decisions.py \
        HeadwordLists/works_catalogue/p2_gated_decisions.json
```

The gate **refuses to run without an explicit `--bar`** — there is no default,
because a default would silently make the promotion threshold an engineering
choice.

---

## 6. Limitations

- The adjudicator is a rule ladder authored from inspection of the data, not
  49,019 individual model judgements. Its precision is therefore *measured*,
  not asserted — which is the entire point of §2 and §3.
- Rule 1 carries Tier A's same-title-different-work risk at 40,757 rows.
- The recall hole in §0.2 is untouched and dominates every count here: no
  amount of P2 adjudication recovers a pair P1 never proposed.
- A human `defer` on a spot-check card counts against the agent in the gate,
  not as agreement — declining to confirm is not confirmation.

_Dr. Mārcis Gasūns_
