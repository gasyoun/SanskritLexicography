# CONTRADICTIONS adjudication — wave 1 verdict table

_Created: 26-08-2026 · Last updated: 26-08-2026_

Ruling pass over the open rows of
[SanskritLexicography/CONTRADICTIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)
and [Uprava/CONTRADICTIONS.md](https://github.com/gasyoun/Uprava/blob/main/CONTRADICTIONS.md)
under **H3538 (Fable 5) — Adjudicate open CONTRADICTIONS rows with stated evidence tier
(wave 1)** ([handoff](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3538-Fable_SanskritLexicography_contradictions-adjudication-wave-1_25.08.26.md)).
Executor: Claude Code Fable 5 (`claude-fable-5`), 26-08-2026. Evidence tiers per the org
ladder: **Tier 1** = canonical artifact counted/read directly (source files, git history);
**Tier 2** = derived/generated surface (exports, mirrors, cached JSON, published
measurements); **Weak** = naming/temporal coincidence or unverified note — never carries a
verdict alone. Standing rule applied throughout: **missing evidence is INCONCLUSIVE, never
PASS.**

## Verdicts — SanskritLexicography (12 rows adjudicated)

| Row | Contradiction (short) | Evidence tier | Verdict 26-08-2026 |
|---|---|---|---|
| §1 | Whitney §319a vs §356 (gen.pl accent of derivative ī/ū-stems) | Tier 2, n=2 | **INCONCLUSIVE at ruling strength** — corpus evidence is two tokens; discriminating probe = extend [RECIPES §1](https://github.com/gasyoun/SanskritLexicography/blob/master/RECIPES.md) Whitney accent validation to every such gen.pl token in the accented RV corpus (same pass that closes [GAPS §1](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md)) |
| §2 | Varga stability: 2014 prose vs measured drift | Tier 2 ×2 | **Provisional pick CONFIRMED** — two independent derived surfaces agree against the 2014 prose; stays 🟡 only because the Table 5 / П9 correction is a canonical-text change that parks for review |
| §4 | Transliteration-policy conflict (two MG-authored policy statements) | Tier 1 for what each document says | **Human-gated, not agent-rulable** — a pending policy choice; a human should decide, via the H1303 inventory → per-token proposal → ratification-sheet path. No agent ruling made |
| §5 | Root inventory: human-facing notes vs vidyut dhātupāṭha | Tier 1 | **Provisional pick CONFIRMED** — the vidyut dhātupāṭha is the canonical machine artifact; amending the human-facing root notes is an editorial change that parks for review |
| §6 | Tag-effect direction: single-lemma exemplar vs full-corpus census | Tier 2 | **Provisional pick CONFIRMED** — the full-corpus classifier census (SKD 53.3 % / 46.7 %, VCP 77.6 %) subsumes the n=1 hand-picked exemplar |
| §7 | Correlation measured twice with different values | Tier 2 ×2 | **Provisional pick CONFIRMED** — both runs derived; the paper's run supersedes, and both agree on the only load-bearing conclusion (flat, school-bound) |
| §9 | Rāmāyaṇa kāṇḍas 6–7: `SOUTHERN_FILES` label vs critical-edition text | Tier 2 ×2 vs Weak | **Ruled: the text wins over the label** — concordance kāṇḍa 7: 2,688/2,690 at identical `sarga.verse` (95.5 % scoring 1.0); kāṇḍa 6: 99.8 % vs 1.2–3.0 % for kāṇḍas 1/2/3/5; the label is a mislabel. Relabel parks for a review sheet against [issue #822](https://github.com/gasyoun/SanskritLexicography/issues/822); row stays 🟡 until that lands |
| §10 | Merged-TSV line count 323,426 vs headword count 323,425 | Tier 1 | **✅ RULED — both true under different scopes**; line 1 is the header row (`slp1 · iast · n_dicts · dicts · gender · fem_fold`), data rows = 323,425 = headword count of record |
| §11 | kosha.db table-count censuses disagree | Tier 2 ×2, different builds | **INCONCLUSIVE** — no kosha.db build exists on this box; probe = one dated `scripts/build_db.py` rebuild with per-table `COUNT(*)` published |
| §12 | PWG+PWK+SCH totals 285,799 vs 285,950 | Tier 1 | **✅ RULED — both are exact naive sums of the SAME now-2026 lists at two pipeline stages** (union-ingested vs raw export); 151-key collapse (PWG −28, PWK −35, SCH −88); vintage/key-mixing hypothesis REFUTED |
| §13 | corpus_lexicon.jsonl line count 1,091,528 vs 1,093,391 | Tier 2 both; discriminating artifact absent | **INCONCLUSIVE** — canonical file absent, local twin is a 134-byte git-LFS pointer (`size 290543363`); probe = pull the LFS object (or MG-disk copy) and `wc -l` |
| §14 | "No verse cited by all 11 dictionaries" — real or resolver artifact? | Tier 2 partial | **INCONCLUSIVE at ruling strength** — partly mechanical given MW's 5-text resolver lane; the claim must carry the resolver qualifier wherever quoted until the 10-dict (or apparatus-fed) re-run lands |

§3 and §8 were already ✅ ruled before this wave and were not touched.

## Verdicts — Uprava (2 rows adjudicated)

| Row | Contradiction (short) | Evidence tier | Verdict 26-08-2026 |
|---|---|---|---|
| §2 | CDSL throttle vs hard-down | Tier 1 per probe for its own moment; Weak across moments | **Reclassified as flapping** (like §1) — no one-time verdict possible or needed; resolution = re-probe via [RECIPES §2](https://github.com/gasyoun/Uprava/blob/main/RECIPES.md) before every use. Fresh probe: HTTP 200 in 0.445 s at 2026-08-26T04:33:42Z |
| §4 | Handoff-ID collision "SOLVED" vs "keeps happening" | Tier 1 (git history + dated FINDINGS rows) | **✅ RULED — both true under different scopes**: the same-ID `O_EXCL` race has zero recurrences since 06-07-2026 ([FINDINGS §221](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md): 1 anomaly in 801 mint commits, and it was a distinct-ID tree clobber, commit `b4fcdb6d`); the collision *class* recurs through other mechanisms ([FINDINGS §452](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md): false-death re-mint drew both H3051 and H3052; [§220](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md): all three checkpoints mis-timed until `posttooluse_claim_recheck.py`). A guard proves only the mechanism it checks |

## Parked (canonical/gold changes never applied directly)

1. SL §2 — Table 5 / П9 numeric correction in the reviewed paper text.
2. SL §5 — amending the human-facing root notes to match the vidyut dhātupāṭha.
3. SL §9 — relabelling `SOUTHERN_FILES` for kāṇḍas 6–7 (against
   [issue #822](https://github.com/gasyoun/SanskritLexicography/issues/822)).

Each stays a registry-row note until its review sheet lands; nothing canonical was edited
in this pass.

## Counting discrepancies vs the handoff

1. The handoff said "11 marked open/unresolved" in SL — the actual open set on
   26-08-2026 was **12 rows** (§1, §2, §4, §5, §6, §7, §9, §10, §11, §12, §13, §14).
2. Uprava's "2 status-open" (§2, §4) was correct, but its Conclusions block still listed
   §9 as 🔴 although §9 was resolved 16-08-2026 — that stale bullet was rewritten in the
   same pass.

## Cross-registry check (GAPS / ASSUMPTIONS)

No GAPS or ASSUMPTIONS entry in either repo was made stale by these rulings: the
INCONCLUSIVE and flapping outcomes preserve exactly the probes those entries already name
([SL GAPS §1](https://github.com/gasyoun/SanskritLexicography/blob/master/GAPS.md) remains
the discriminating probe for SL §1;
[Uprava GAPS §2 / ASSUMPTIONS §2](https://github.com/gasyoun/Uprava/blob/main/GAPS.md)
still correctly describe the unmeasured throttle mechanism behind Uprava §2).

_Dr. Mārcis Gasūns_
