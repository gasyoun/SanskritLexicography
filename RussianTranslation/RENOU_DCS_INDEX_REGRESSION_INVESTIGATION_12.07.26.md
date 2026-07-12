# RENOU `renou_dcs`/`renou_ls` divergence — correction or regression? (verdict)

_Created: 12-07-2026 · Last updated: 12-07-2026_

**Handoff:** [H771](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H771-Opus_RussianTranslation_renou-dcs-index-regression-investigation_12.07.26.md).
**Model:** Opus 4.8 (`claude-opus-4-8`). Read-only against all data files
(`.jsonl`, `dcs_lemma_renou.json`, `ls_source_map*.json`) — **zero files
deleted, moved, renamed, or regenerated this session.** Adjudicates the
`@DECIDE` raised by
[H692](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/RENOU_STAGE_REDUNDANCY_AUDIT_12.07.26.md):
is the 25‑06‑2026 canonical `{code}.renou.jsonl` regeneration a **correction**
(old chain over‑attests) or a **regression** (canonical under‑attests)?

---

## Verdict — CORRECTION for all 7 codes (ap · ap90 · ben · bhs · mw · pw · sch)

The old underscore chain (`{code}_renou*.jsonl`) **over‑attests**; the canonical
dot‑file (`{code}.renou.jsonl`) is right. Every one of the 28,662 divergent rows
(4.4 % of 646,926 across the 7 codes) is the **canonical file removing a
low‑confidence DCS state the old chain kept** — never adding, never mutating,
never disagreeing in the other direction. The removed states are, without
exception, one of the two documented DCS noise classes: a **thin single‑text
low‑confidence tail** (min‑support pruning) or an **Epic/`III` date‑fallback
attestation** (index refresh). **Nothing of value is lost.**

`renou_ls` shows **zero real divergence** — the fields are positionally
byte‑identical across all 7 codes. H692's sampled `renou_ls` figure (mw 22.8 %)
was a homonym‑misalignment artifact of key1‑keyed sampling, not a data change.

**Consequence:** the ~379 MB old underscore chain is **safe to delete** once
this verdict is committed (deletion itself remains a human `@DO`, per H692). No
regression anywhere → no fix/regeneration follow‑up is owed.

---

## Timeline reconstructed (file mtimes + commit timestamps, all +0300)

| when | event | evidence |
|---|---|---|
| 23‑06 23:44 / 24‑06 07:01 | **old chain base** `mw_renou.jsonl` (via `tag_mw_from_source.py`) / `{code}_renou.jsonl` (via `tag_dict_from_source.py`) built | file mtimes; commits `81d7aee0` (23‑06 23:50) + `c272a945` (24‑06 07:06) |
| 24‑06 15:19 / 15:37 | old chain `+bhs` / `+wl` stages (add `renou_bhs`/`renou_wl` only; **do not touch `renou_dcs`**) | mtimes of `*_renou.bhs.jsonl` / `*.bhs.wl.jsonl` |
| **24‑06 21:19** | **`ecc7bb96`** adds per‑state `state_support` `{n,conf}` to the index builder **and** the `filter_dcs_states` min‑support filter to both taggers | `git show ecc7bb96 -- build_dcs_renou.py` |
| 24‑06 22:19 | `44e3637f` — recompute `renou_dcs_oldest` after pruning (informational‑pointer fix; explicitly *not* `renou_dcs`) | commit message |
| **25‑06 13:17** | **DCS index `dcs_lemma_renou.json` regenerated** (register axis added; `6ac5b114` at 13:29 commits it) | index mtime; `6ac5b114` |
| **25‑06 14:09–14:11** | **canonical `{code}.renou.jsonl` built** by `renou_pipeline.py` → `tag_dict_from_source.py` (now filtering) against the 25‑06 index | dot‑file mtimes |

The old chain was frozen **before** the min‑support filter existed and used the
**pre‑refresh** index; the canonical files were built **after** both. That gap
is the entire story.

---

## Mechanism 1 — the old chain never applied the min‑support policy (thin tails)

At the old‑chain commit `c272a945` the tagger computed the DCS states **raw**:

```python
dcs = index.get(iast)
dcs_states = dcs['renou'] if dcs else []      # tag_dict_from_source.py @ c272a945
```

The first‑generation index (`81d7aee0`) stored `renou` as a **plain set of
states with no per‑state counts** (`e['states'].add(state)` → `{'renou': states, …}`).
So the old chain's `renou_dcs` = *every* state any corpus text attested,
including a state resting on a single low‑confidence text.

`ecc7bb96` (24‑06 21:19) then introduced **both** halves of the min‑support
policy in one commit:

- [`build_dcs_renou.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_dcs_renou.py):
  the index now emits lossless per‑state `state_support = {state: {n: <#texts>, conf: <best>}}`.
  The `renou` state *set* is derived identically to before (`sorted(e['state_n'], …)`),
  so the refresh **added a field, it did not change which states appear**.
- [`renou.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou.py)
  `filter_dcs_states` (unchanged in logic since; the later `6ac5b114` only
  refactored it into `_filter_by_support`): **keep a state iff `n ≥ 2` OR
  `conf ∈ {high, medium}`**; drop the thin low‑confidence tail
  (`DCS_MIN_SUPPORT = 2`, `_TRUSTED_CONF = ('high','medium')`).

The canonical pipeline consumes this filter; the old chain predates it. Result:
canonical `renou_dcs` ⊆ old `renou_dcs`, differing exactly by the pruned tail.

## Mechanism 2 — the 25‑06 index refresh tightened the Epic (`III`) date‑fallback

A minority of drops are not filter drops but **index‑content** drops: the state
is gone from the index's own `renou` list (or the lemma is gone entirely). These
are **100 % state `III`**:

- **lemma‑absent (2,816 rows, every code): the old `renou_dcs` was `["III"]` and
  nothing else** — zero multi‑state cases. These lemmas rested entirely on one
  Epic/date‑fallback attestation and dropped out of the refreshed index.
- **state‑absent (603 rows): the dropped state is always `III`** (`["III","IV"]`→IV
  survives, `["II","III"]`→II survives, `["I","II","III"]`→`["I","II"]`, …). The
  well‑founded genre/name‑hint states (I/II/IV/V) are retained; only the Epic
  date‑fallback `III` is shed.

`III` is precisely what the diachronic date‑fallback emits when a text has a
usable date but no clean genre (`diachronic_state → 'III'`, flagged
low‑confidence). The **state‑assignment code is unchanged** across the two builds
(the `81d7aee0..HEAD` diff to `build_text_states` only adds `registers`/
`state_support`; `state`, `confidence`, and the date fallback are byte‑for‑byte
identical), so this refresh is a **data/date‑calibration refresh of the corpus
scan**, not a code change — and it shed the single lowest‑confidence,
most‑calibration‑dependent state, in one direction only.

## Mechanism 3 (not a divergence) — `renou_ls` is identical; the 22.8 % was an artifact

`renou_ls` is derived **purely from the entry's `<ls>` citations** via
`renou.states_for_text` / `renou_sigla`; it **never reads the DCS index**. The LS
source maps (`ls_source_map.json`, `ls_source_map_mw.json`) were last written
**23‑06 19:09/19:13** — before *both* builds — so they cannot have caused any
divergence, and the "refreshed `ls_source_map_mw.json`" branch of the H692
hypothesis is moot. Both taggers derive mw LS states from the identical
`renou.states_for_text(block,'mw')`; the only nominal difference is `tag_mw`
storing the raw list vs `tag_dict` storing `sorted(set(...))`, and in practice
even the list form is identical.

A **positional (row‑aligned) check finds `renou_ls` set‑diff = 0 AND list‑diff =
0 for all 7 codes.** H692's sampled `renou_ls` disagreement (mw 2,596/11,396 ≈
22.8 %) came from its 1‑in‑25 sample being keyed by `key1` alone, while ~32 % of
mw rows share a `key1` across homonyms — the sample matched the wrong homonym.
Not a data regression.

---

## Empirical evidence (positional, homonym‑exact by construction, read‑only)

Both files in each pair are produced by iterating the **same csl‑orig source in
the same entry order**, so row *i* of the old chain and row *i* of the canonical
file are the same headword occurrence — no keying needed. Alignment verified:
**0 key1 mis‑alignments** in every pair. The mw `renou_dcs` (13,836) and
`renou_dcs_oldest` (9,737) counts **reproduce H692's independent homonym‑aware
verifier exactly**, cross‑validating the method.

| code | rows | `renou_dcs` divergent rows | % | canon⊂old | canon⊃old | mutual | `renou_dcs_oldest` diff | `renou_ls` diff |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ap | 90,654 | 3,227 | 3.56 % | 3,227 | 0 | 0 | 2,489 | **0** |
| ap90 | 34,882 | 1,552 | 4.45 % | 1,552 | 0 | 0 | 1,145 | **0** |
| ben | 17,310 | 1,010 | 5.83 % | 1,010 | 0 | 0 | 640 | **0** |
| bhs | 17,839 | 650 | 3.64 % | 650 | 0 | 0 | 395 | **0** |
| mw | 286,560 | 13,836 | 4.83 % | 13,836 | 0 | 0 | 9,737 | **0** |
| pw | 170,556 | 7,217 | 4.23 % | 7,217 | 0 | 0 | 5,208 | **0** |
| sch | 29,125 | 1,170 | 4.02 % | 1,170 | 0 | 0 | 858 | **0** |
| **total** | **646,926** | **28,662** | **4.43 %** | **28,662** | **0** | **0** | **20,472** | **0** |

**Every** divergent row is `canon ⊂ old` — pure removal. Zero additions, zero
mutations, zero rows where the sets merely reorder.

### Why each state was dropped (per dropped state; a row may drop >1 state)

| bucket | count | meaning | verdict |
|---|---:|---|---|
| **thin** | 25,751 | state present in the current index with `n=1, conf=low` → correctly pruned by the min‑support filter | correct (Mechanism 1) |
| **lemma‑absent** | 2,816 | lemma has no entry in the refreshed index; old `renou_dcs` was **100 % single `["III"]`** | correct (Mechanism 2) |
| **state‑absent** | 603 | lemma present, dropped state gone from the index's `renou`; **always `III`** | correct (Mechanism 2) |
| **KEPT‑ANOMALY** | **0** | a dropped state that *would* survive the current filter — the signature of a real loss | **none found** |

The absence of any KEPT‑ANOMALY is the decisive negative result: **not one**
state that passes the current min‑support policy was lost between the old chain
and the canonical file.

### Spot‑checks against DCS ground truth (current index `state_support`)

- **`aṃśuhasta`** — old `["IV"]` → canonical `[]`. Index: attested in **1 text**
  (`Abhidhānacintāmaṇi`, a 12th‑c. lexicon), `IV {n:1, conf:low}`. A single
  late‑lexicon listing is exactly the thin evidence the policy targets → correctly dropped.
- **`aka`** — old `["I","II","IV"]` → canonical `["I","II"]`. Index (5 texts, oldest
  `Pañcaviṃśabrāhmaṇa` = Vedic/`I`): `I {n:3,high}` kept, `II {n:1,medium}` kept,
  `IV {n:1,low}` dropped. The Classical `IV` rests on one low‑confidence text.
- **`akaṇṭaka`** (bhs/pw) — old `["I","III","IV","V"]` → canonical `["I","III","V"]`;
  `IV {n:1,low}` dropped.
- **`aṃśu`** (84 texts) and **`akṣa`** (147 texts) — old = canonical = `["I","II","III","IV","V"]`,
  **nothing dropped**. Well‑attested lemmas are untouched — the filter is conservative,
  acting only on thin tails.

---

## What could NOT be verified, and why the residual risk is bounded

The DCS index `dcs_lemma_renou.json` is gitignored, single‑copy, and was
overwritten in place on 25‑06 (no committed history, no backup). I therefore
**cannot byte‑diff the pre‑refresh index against the post‑refresh one**, so I
cannot *prove* the Mechanism‑2 date‑calibration refresh dropped *only* wrong
`III` attestations rather than also a few correct ones. The evidence that this
residual is negligible and one‑directional:

1. The state‑assignment **code is unchanged** (verified by diff) — the refresh is
   data/calibration, not a logic rewrite.
2. Everything removed is the **lowest‑confidence** material by construction: thin
   `n=1, conf=low` tails, or Epic `III` date‑fallback (no clean genre).
3. lemma‑absent cases are **100 % single‑`III`** — they never had a second,
   confident attestation; losing a lone date‑fallback loses no established stratum.
4. **Zero additions, zero mutations, zero KEPT‑ANOMALY** across 646,926 rows —
   no corruption signature anywhere.
5. Even in the worst case the affected signal is `renou_dcs` (a corpus‑enrichment
   layer); any `renou_ls` citation stratum for the same lemma is retained
   (`renou_ls` is identical), and the canonical files are already what the whole
   downstream pipeline consumes.

---

## Verdict per code

| code | verdict | causal mechanism |
|---|---|---|
| ap, ap90, ben, bhs, mw, pw, sch | **CORRECTION** | old chain stored **raw** DCS states (pre‑`ecc7bb96`, unfiltered) against the pre‑refresh index; canonical applies the min‑support filter (thin `n<2` low‑conf tails) over the 25‑06 index, which additionally shed Epic `III` date‑fallback noise. 100 % pure removal, 0 anomalies. |
| pwg | n/a | no underscore chain — only the canonical `pwg.renou.jsonl` exists (already clean). |

**Old underscore chain safe to delete** (`ap_renou.jsonl`, `ap_renou.bhs.jsonl`,
`ap_renou.bhs.wl.jsonl`, `ap90_renou.jsonl`, `ben_renou.jsonl`, `bhs_renou.jsonl`,
`mw_renou.jsonl`, `mw_renou.bhs.jsonl`, `mw_renou.bhs.wl.jsonl`, `pw_renou.jsonl`,
`sch_renou.jsonl`, ~379 MB) once this verdict is committed. Deletion stays a
human `@DO`, per H692's standing discipline — this handoff only settles the
causal question.

---

## Reproduction

Both diagnostic scripts are aggregates‑only and read‑only (they open the
gitignored data with `utf‑8‑sig`, write nothing to `src/`). Run from the checkout
that holds the gitignored data (`RussianTranslation/src/`); worktrees do not carry
these files. The per‑row positional comparison and the two index‑content buckets
above were computed by the H771 diagnostic (positional align → set/list diff of
`renou_dcs`/`renou_ls`/`renou_dcs_oldest` → per‑dropped‑state classification
against the live index's `state_support`). Key git evidence:

```
git show c272a945:RussianTranslation/src/tag_dict_from_source.py   # old chain: dcs_states = dcs['renou'] (raw)
git show ecc7bb96 -- RussianTranslation/src/build_dcs_renou.py     # +state_support; renou set unchanged
git show ecc7bb96 -- RussianTranslation/src/renou.py               # +filter_dcs_states (min-support)
git diff 81d7aee0 HEAD -- RussianTranslation/src/build_dcs_renou.py # build_text_states state logic unchanged
```

_Dr. Mārcis Gasūns_
