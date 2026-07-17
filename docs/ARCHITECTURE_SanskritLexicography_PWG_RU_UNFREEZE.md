# ARCHITECTURE — PWG_RU_UNFREEZE (SanskritLexicography)

_Created: 17-07-2026 · Last updated: 17-07-2026_

The design, against real files and real data shapes. Index + rulings: [PLAN_SanskritLexicography_PWG_RU_UNFREEZE_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_PWG_RU_UNFREEZE_2026H2.md).

Every shape below was read off `origin/master` at [`64054959`](https://github.com/gasyoun/SanskritLexicography/commit/64054959) or measured against the local store on 17-07-2026. Nothing here is assumed.

---

## 1. The assets this plan consumes (and must not rebuild)

| Asset | Real path | What it already gives us |
|---|---|---|
| Canonical RU store | `RussianTranslation/src/pwg_ru_translated.jsonl` — **local-only, gitignored** (root [`.gitignore`](https://github.com/gasyoun/SanskritLexicography/blob/master/.gitignore) line 29, `RussianTranslation/src/*.jsonl`) | 11,603 rows. Fields: `key1`, `h`, `iast`, `de`, `ru`, `grammar`-adjacent, `layer`, `stratum`, `provenance`, `review_status`, `source_type`, `subcard`, `page`, `volume`, … |
| Deterministic sense counter + SAN-LOSS guard | [`src/pilot/sense_count.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/sense_count.py) | `count_source_senses`, cross-reference-hardened (H960). **Language-neutral** — imported by RU *and* EN audit paths. |
| Generation harness | [`src/pilot/gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py) | Emits the JS harness. Owns `accept()`, `restoreCard`, both soft guards, `summary` telemetry. |
| Guard behavioural test | [`src/pilot/accept_sensecount_test.js`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/accept_sensecount_test.js) | Extracts the **real** `accept()` from a generated harness (cannot drift) and asserts soft/hard behaviour both ways. |
| Cohort machinery | [`nominals_worklist.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/nominals_worklist.py) · [`verb_worklist.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/verb_worklist.py) · [`no_pwg_scale_plan.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/no_pwg_scale_plan.py) | The three cohorts already exist as code. **Do not invent a fourth definition.** |
| Frozen evidence | [`pwg_ru/h911/`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h911/) · [`h963/`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h963/) · [`h1070/`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1070/) | Committed, SHA-pinned. The offline substrate for W1-A and W1-B. |
| Audit paths | [`audit_window.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py) (RU) · [`audit_window_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window_en.py) (EN) | Per-window clean/requeue classification. |
| Run history | [`src/pilot/RUN_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_LOG.md) | Per-window outcomes incl. the H858 residual-bug list. |
| Parity ledger | [`LANG_PARITY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md) + [`lang_parity_check.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/lang_parity_check.py) | Every RU/EN fix classified SHARED / INTENTIONAL-DIVERGENCE / GAP, hash-pinned. |
| Gate pins | [`window_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_selftest.py) | 135/135 on master. Already pins `const SANLOSS_HARD_REJECT = false` as a literal needle (line ~695). |
| Marker tool | [`src/mark_reconstructed_headwords.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/mark_reconstructed_headwords.py) | PR #517's stamper. SHA-pinned to its own report; refuses if reality moved. |

---

## 2. W1-A — cohort clean-rate measurement

### 2.1 The cohort partition — bound to what exists

Measured store distribution (17-07-2026, `layer` field, n=11,603):

| `layer` | rows | Cohort |
|---|--:|---|
| `pwg` | 5,594 | **pwg-native** — splits into `nominal` / `root_upasarga` by key shape |
| `pw` | 5,205 | **no_pwg** (supplement chain) |
| `nws` | 432 | **no_pwg** |
| `sch` | 210 | **no_pwg** |
| `pwkvn` | 162 | **no_pwg** |

So `no_pwg` = `layer ∈ {pw, sch, nws, pwkvn}` = **6,009 rows**; `pwg` = 5,594. This is the H255 lane boundary as [`no_pwg_scale_plan.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/no_pwg_scale_plan.py) already draws it — read, not invented.

Within `pwg`, the `nominal` vs `root/upasarga` split follows the generator's own structural distinction, documented in [`nominals_worklist.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/nominals_worklist.py)'s docstring:

> a **nominal** headword has no rootmap — it generates a single flat card (`_pilot_gen_merged.py` accepts any headword key via `form_key`). Where the verb worklist reads the vetted verb-root file and expands each root through a rootmap into homonym/sense/prefix sub-cards…

So: **`root_upasarga` = the key resolves to a rootmap** (the `verbs01` `pwg_preverb1.txt` universe `verb_worklist.py` reads); **`nominal` = it does not**. The partition is a lookup against existing files, not a regex guess at key shape. Rows resolving to neither are **`unassigned`** and reported, never silently binned.

> Two exclusions, both stated in the report rather than buried:
> **(a) `provenance.h_reconstructed == true` (468 rows)** — their `h` is derived and homonym-collapsed onto 14 heads, so any `h`-keyed cohort join would smear them across cohorts. Excluded from rates, counted separately.
> **(b) `stratum` is not a cohort.** It is chronological (`Vedic` / `Classical` / `Epic`…, 8,142 rows empty). Anyone reaching for it as a cohort key is reading the wrong field.

### 2.2 Where "clean" comes from

**Clean rate is not in the store.** Every row carries `review_status: ai_translated` (all 11,603 — measured; there is no human-reviewed row to compare against). So a clean rate cannot be read off the store and must be joined from audit evidence:

- **`no_pwg`**: already computed. [`h911_quality_economy_census.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h911/h911_quality_economy_census.json) → `families.H255_no_pwg_workflow.population_audit_clean_rate` = *"per-window 41%-69% (median ~62%); EXCLUDES w1 infra-crippled first run"*. **Consume this figure; do not recompute it.**
- **`pwg` cohorts**: joined from [`RUN_LOG.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_LOG.md) per-window entries + the H818 acceptance-canary family in the same census.

The report is therefore an **evidence join with per-cohort provenance and an explicit n**, not a fresh audit run. A cohort whose n is too small to separate 62% from 80% must say **`INSUFFICIENT_EVIDENCE`** — that is a real, permitted verdict, and it is *not* a licence to generate more.

### 2.3 Shape of the output

New script `RussianTranslation/src/pilot/cohort_clean_rates.py`, stdlib-only, `sys.stdout.reconfigure(encoding='utf-8')`, pure read:

```
python src/pilot/cohort_clean_rates.py --out pwg_ru/h1112/cohort_clean_rates.json
```

```jsonc
{
  "schema": "pwg_ru.cohort_clean_rates.v1",
  "store_rows": 11603,
  "excluded": { "h_reconstructed": 468, "unassigned": 0 },
  "bar": 0.80,
  "cohorts": {
    "no_pwg":         { "rows": 6009, "clean_rate": 0.62, "n_windows": 10,
                        "range": [0.41, 0.69], "verdict": "BELOW_BAR",
                        "evidence": "pwg_ru/h911/h911_quality_economy_census.json#families.H255_no_pwg_workflow" },
    "nominal":        { "rows": 0, "verdict": "INSUFFICIENT_EVIDENCE|BELOW_BAR|CLEARS_BAR", "evidence": "..." },
    "root_upasarga":  { "rows": 0, "verdict": "...", "evidence": "..." }
  },
  "economy": "NOT_MEASURABLE — tokens/cost not_recoverable from frozen evidence (h911 census `not_recoverable_note`)",
  "drain_recommendation": "…names a cohort or names none…"
}
```

Every `clean_rate` carries the artifact path it came from. A number without provenance is a defect.

### 2.4 The D-1 debt worklist + regression guard

Same deliverable, because the exclusion in §2.1(a) already computes the set:

- `pwg_ru/h1112/h_reconstructed_worklist.jsonl` — the 468 keys, their derived `h`, and the 14 heads they collapse onto. **This is the standing re-translation worklist** (D-1), and it is the artifact a future authorized live run consumes.
- A regression guard in [`window_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_selftest.py): assert the store's `h_reconstructed` count is **exactly 468** unless a re-translation manifest documents a *decrease*. The failure mode being guarded is precise and has already happened once: `h is None` fell 468→0 and the defect became unfindable by the only query that could see it. A count that silently drops must **fail a test**, not go unnoticed.

---

## 3. W1-B — offline false-flag measurement for the two soft guards

### 3.1 What is actually there

Read from [`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py) (line numbers as of `64054959`):

| Line | Content |
|---|---|
| 48 | `from sense_count import count_source_senses` |
| 1547 | `const SANLOSS_HARD_REJECT = false` |
| 1558 | `const TNMASK_HARD_REJECT = false` |
| 1650 | `const accept = (c, k) => {` |
| 1656-1665 | `{Tn}` multiset check **before** `restoreCard` — soft, `TNMASK_MISMATCHES++` |
| 1666 | `c = restoreCard(c, k)` |
| 1668-1673 | `<ls>`/`{#` fidelity check — **hard**, rejects |
| 1682-1697 | SAN-LOSS shortfall — soft, `SANLOSS_SHORTFALLS++`, `if (SANLOSS_HARD_REJECT) { … return null }` |
| 2135 | both counters ride out in `summary` for [`classify_run.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/classify_run.py) |

The harness's own comment states the gating rule plainly:

> *flipping `SANLOSS_HARD_REJECT=true` (owner-gated, after the live measurement) turns each shortfall into the same deterministic requeue as an ls/sk fidelity-reject.*

The ordering is load-bearing: `{Tn}` (soft) → `restoreCard` → `<ls>`/`{#` (hard) → SAN-LOSS (soft). The fidelity-reject fires **first**; a card rejected there never reaches the SAN-LOSS counter. Any false-flag rate must be computed over cards that *survived* the fidelity gate, or it is measuring the wrong denominator.

### 3.2 The measurement — frozen evidence, not live traffic

The harness comment says "after the live measurement", and live capacity is D-3-blocked. But the quantity needed — *of the cards this guard would have rejected, how many were actually fine?* — is a property of **(source card, emitted card)** pairs, and those pairs are frozen and SHA-pinned in [`h963/`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h963/) (`campaign_cards.jsonl`, `artifact_manifest.sha256`) and the promoted store. So the measurement is offline:

1. For each frozen (source, emitted) pair, recompute `count_source_senses(source)` and the emitted top-level sense count with the **real** extraction path — reuse [`accept_sensecount_test.js`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/accept_sensecount_test.js)'s technique of pulling `accept()` verbatim out of a generated harness so the measurement cannot drift from the generator.
2. Partition the flagged set: **true drop** (a source sense genuinely absent from the output) vs **false flag** (the sense is present but the counter miscounts — the H960 cross-reference class, `gam~~h2_31_pari` 2→1, `s_ud~~h0_05_pra` 4→2, `_a_srayatva` 2→0).
3. Same for `TNMASK`, whose known false-flag class is different and must not be pooled: a model writing literal `<ls>..</ls>` instead of `{Tn}` **self-expansion**, not a drop.

Output `pwg_ru/h1112/softguard_falseflag_rate.json`, and a **recommendation only**. The flip is owner-gated; W1-B does not touch either `const`. The plan's autonomy contract makes this explicit, and [`window_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_selftest.py) pins the literal `const SANLOSS_HARD_REJECT = false` — an agent flipping it fails the repo's own gate, which is the intended backstop.

**Honest limit, to be stated in the report:** frozen evidence is a *sample of one route under one payload regime*. A rate computed on it bounds the false-flag class; it does not prove the live rate. The report says so; the owner decides with that caveat visible.

---

## 4. W1-C — the H858 `grammar`-field `{Tn}` stranding fix

**The bug, exactly** ([RUN_LOG.md:909](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_LOG.md)):

> **`grammar`-field stranding** (`gokzuraka`, real): the model can echo a `{Tn}` in the `grammar` field, but `restoreCard` restores only german/russian → a live stranded anchor. Fix = restore the grammar field too (harness change, future-only; can't reclaim `gokzuraka` — no placeholder map saved).

Live recurrence confirmed on a fresh `gokzuraka` card, promoted with a literal un-restored `{T2}` in `grammar`.

**Design.** In [`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py)'s emitted `restoreCard`, extend the restore to the `grammar` field using the same placeholder map already used for `german`/`russian`. Deliberately narrow:

- **Interaction with the `{Tn}` multiset guard is the whole point.** The soft `TNMASK` check runs *before* `restoreCard` and compares `cardTokens(c)` to `tokensOf(INPUTS[k].skeleton)` — a `{Tn}` echoed into `grammar` is *present* in the multiset, so TNMASK passes it, and then `restoreCard` fails to restore it. The two facts compose into exactly the observed defect: token accounted for, token stranded. Fixing `restoreCard` closes it at the right layer; tightening TNMASK would not.
- `gokzuraka` itself is **not reclaimable** — no placeholder map was saved. The fix is forward-only and must not pretend otherwise.
- Repair of already-promoted stranded cards is **out of scope** (store mutation → escalate). W1-C additionally emits a **detection query** so the blast radius is known: count promoted rows whose `grammar` matches `/\{T\d+\}/`.

---

## 5. W1-D — H1070's three EN guards

Verbatim from [`PWG_EN_FU1_SCALEUP_GO_NO_GO_2026-07-17.md §3`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h1070/PWG_EN_FU1_SCALEUP_GO_NO_GO_2026-07-17.md):

| # | Defect | Guard | Hard? | Lands in |
|---|---|---|---|---|
| 1 | German homographs/polysemes at gloss level (r155 «braut»→"betroth"; r119 «Vergleich»→"comparison"). *No deterministic gate can see these* | German-polyseme checklist line under `term-mistranslation` (Vergleich, braut/Braut, gelten, Zug, anführen, …) + one prompt rule | soft (judge) | [`gen_fidelity_judge_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_fidelity_judge_en.py) + [`tr_en.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/tr_en.txt) |
| 2 | **`{#..#}` token loss inside `<F>` footnotes** (r102 dropped `{#uc#}`; the fidelity guard demonstrably did not fire) | Extend the restore-time `{#..#}` count check to include footnote content | **HARD — the only hard condition** | accept path in [`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/gen_opt_harness2.py); HARD flag in [`audit_window_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window_en.py) if the accept-path fix is deferred |
| 3 | Untranslated cross-ref/NWS residue (12/170 rows) | Extend the DE-RESIDUE gate to flag pure-cross-ref rows + NWS `{#..#}`-wrapped German as a **soft** class, so coverage stats stop counting them as translated | soft | DE-RESIDUE gate |

**Guard 2 deserves care**: `accept()`'s `countOf(c, /\{#/g)` already counts `{#` occurrences over the whole restored card — so a footnote `{#uc#}` *should* be counted. That r102 dropped one and the guard did not fire means the failure is upstream of the count (masking/restore of `<F>` content), not in the comparison. **Diagnose before patching the counter** — patching a counter that is already right would be the wrong fix, and H1070 flags this as the one silent-loss class.

**Parity.** Guard 2 touches `accept()`, which is **shared** RU/EN — `sense_count.py` is already language-neutral and imported by both audit paths. Every change gets a [LANG_PARITY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md) row classified SHARED / INTENTIONAL-DIVERGENCE / GAP, hash-refreshed **only** via `lang_parity_check.py --update-hash`.

**Hard constraint:** `promote_en.py` must not run. The store carries **0 EN rows** (verified 17-07 against 11,603 rows) and this wave does not change that.

---

## 6. W1-E — ReverseDictionary: what can and cannot be built

### 6.1 The blocking fact

Two independent problems, both verified today:

1. **The canonical list is not in the repo.** [`ACL_DH_COMPATIBILITY_ANALYSIS.md:124`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/ACL_DH_COMPATIBILITY_ANALYSIS.md) cites `.doc.pdf/266820-reverse-Gasuns.txt`; `.doc.pdf/` actually contains four `.mdx` files (`Last on Page`, `Reverse-Kochergina`, `Reverse-Palsule-Dhatu-Index`, `Rplot03`) and a `Sorting-Samples/` dir. **The 266,820-line file is absent** — this is the H736 loss-risk finding, and it means no subset can be *built* today, let alone published.
2. **The subtraction is undecidable on available data.** [§5's own caveat](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/ACL_DH_COMPATIBILITY_ANALYSIS.md):

> the other five "clear risk" sources — Stchoupak–Nitti–Renou, Turner *CDIAL*, Mylius, Kochergina, Pujol — **never appear as a marked source-code in the file at all** … **14,471 is therefore a lower bound**, not a final figure … Establishing a tighter bound would need per-source headword lists for the five silent sources (not available in this folder).

So `H` (Edgerton, 12,552) + `P` (Vettam Mani, 1,919) = 14,471 is what *can* be subtracted. Kochergina et al. cannot be — a Kochergina-only headword coinciding in form with a PWK headword was silently absorbed as unmarked.

### 6.2 What W1-E therefore builds

1. **Dataset recovery** — locate `266820-reverse-Gasuns.txt` (git history, `.doc` drafts at 250,026 / 255,882, local disk), verify its line count, and back it up. If it cannot be found, **that is the deliverable's finding** and it escalates as data loss. This is the H736 finding turned into an action.
2. **A rights ledger**, `ReverseDictionary/RIGHTS_LEDGER.md` — every source in one of three buckets, and the third bucket is the point:
   - **PD** (subtractable, safe)
   - **In-copyright, marked** — `H` Edgerton 12,552 · `P` Vettam Mani 1,919 (subtractable)
   - **In-copyright, UNMARKED — cannot be isolated**: Stchoupak–Nitti–Renou, Turner, Mylius, Kochergina, Pujol. *This bucket is why a PD-only subset cannot be certified today.*
3. **Subset tooling** (`build_pd_subset.py`) that emits the subset **plus a rights-residue statement**, so if a human later rules "publish", the artifact ships with its own honest bound rather than a bare PD claim.
4. **Flag the live exposure**: [`Reverse-Kochergina.mdx`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/.doc.pdf/) (701 KB) is an in-copyright source sitting on public `master` — the H734 class. **Flag only**; removing it is a human call via `/publish-safety-check`.

**W1-E does not publish.** The ruling says publish the PD-only subset; the data says the PD-only subset cannot be identified. The plan delivers everything up to the gate and hands the human a sharper `@DECIDE` than the one they have now.

---

## 7. W1-F — backlog triage

No new tooling. Run `/handoff-registry-audit` against [`handoffs/README.md`](https://github.com/gasyoun/Uprava/blob/main/handoffs/README.md), scoped to this repo's **30 live rows** (22 🟡 + 8 🔵, measured 17-07-2026), re-validated against post-#511 `origin/master`.

The audit's judgment call per row: **superseded** (archive), **still live** (keep/re-mint), **executed but unmarked** (close). Known supersessions to apply, both already documented: **H963 → H1110** (H1110's own text: *"It supersedes H963 as the engineering/live resume point"*), and **H994 → H963** (already archived as a stale-clone duplicate).

The waste this repays is concrete and in the record: the H858 session re-ran 4 headwords (`asaMskfta`/`darvī`/`glāna`/`hasita`) whose deterministic failure was already documented in the RUN_LOG one entry away, at ~$0.30 — because the fuller residual list sat in a different entry than the one the session read.

---

## 8. Data-shape reference

Store row (measured, field list verbatim):

```
column · de · differentia · equivalence_type · evidence · evidence_summary · h · iast ·
key1 · layer · page · page_all · pc_all · provenance · review_status · ru · sense_tag ·
source_type · stratum · subcard · volume
```

`provenance` after [PR #517](https://github.com/gasyoun/SanskritLexicography/pull/517), on the 468:

```jsonc
{
  "generator": "gen_opt_harness2.batched-masked",   // ORIGINAL generator — unchanged by #517
  "h_reconstructed": true,                          // 468 rows
  "iast_reconstructed": true,                       // 462 rows
  "grammar_defaulted_empty": true                   // 468 rows
}
```

Measured `provenance.generator` distribution: `gen_opt_harness2.batched-masked` 11,538 · `autosplit_requeue.topup` 65.

`review_status`: `ai_translated` on **all** 11,603 rows — there is no human-reviewed comparison set in the store.

`source_type`: `attested` 10,635 · `lexicographic` 623 · `mixed` 92 · `null` 253.

---

_Dr. Mārcis Gasūns_
