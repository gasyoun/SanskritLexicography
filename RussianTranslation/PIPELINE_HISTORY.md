# PWG→RU/EN pipeline — history: solutions, failures, current state

_Created: 04-07-2026 · Last updated: 07-07-2026_

This is the orientation document for anyone (human or session) who needs the
**shape** of how this pipeline got here, without reading the full
[`.ai_state.md`](.ai_state.md) journal (1,400+ lines, chronological but not
narrated). Read this first; go to `.ai_state.md` for exact dates/PRs/numbers on
any specific claim below, and to [`src/pilot/RUN_FREQ_MAX.md`](src/pilot/RUN_FREQ_MAX.md)
for the current operating procedure.

## The shape of the problem

Translate all of PWG (Böhtlingk-Roth, the "Petersburg Dictionary") from its
German source into Russian (primary) and English (secondary), headword by
headword, preserving Sanskrit/citation markup exactly, at a scale (100,000+
headwords, tens of thousands of DCS-attested verb roots and nouns) where the
only economically viable translator is an LLM run through Claude's Workflow
tool — which means the entire discipline of this repo is about making that
LLM run *reliably*, *cheaply*, and *verifiably* at scale, not about the
translation task being intellectually hard per headword.

## Timeline

### Phase 0 — groundwork (through 2026-06-26)

Frequency-based prioritization (DCS-attested headwords ranked by corpus
frequency), a root/nominal grammar layer (Whitney concordance), and the first
judge-gate pass (38-unit test, 37/38 publishable) established that the
*translation quality* was fine — the open problem was entirely *process*.

### Phase 1 — first real production run, orchestrator built (06-26 → 06-27)

`sTA` (106 sub-cards) ran end-to-end through the Workflow tool for the first
time, disproving an early assumption that Max needed a human-driven session.
`audit_window.py` was built as the single canonical audit command (NWS
owner-map, markup fidelity, sense coverage, sense-duplicate gates, all free/
deterministic) — this is still the audit entry point today. **First real
failure mode found:** dense head-senses (`sTA`'s `pwg00`) blew the
per-card output budget; fixed with citation-batching + a dedicated
`audit_sense_dupes.py` gate to catch cross-part duplicate senses.

### Phase 2 — the cost crisis and its fix (06-27 → 06-29)

A "$16/root" cost estimate looked economically nonviable at 700+ roots. Root
cause: the **fixed per-card subagent system-prompt overhead** (~27-46K tokens
of `cache_create`, paid once per agent() call), not the translation content
itself. Fix: `gen_opt_harness2.py`, the batched+masked harness — mask each
card's untranslatable spans to `{Tn}` tokens, pack several cards per agent
call, restore markup in JS. Measured **-72% to -90% cost** on real roots.
Along the way: a retry-blowup bug (the model was calling file-read tools
against a design that inlines everything) cost yuj an extra 29%; the dense-
card splitter got a proper tier ladder (whole-retry → sense-split → citation-
split → self-heal fragments); German/Latin/Sanskrit gate false-positives were
found and fixed (~40 FPs, 1 real defect, out of the "untranslated German"
bucket). **gam, yuj, vid, han all completed Stage C on this harness** —
`vid` in particular first went through here at 42/55 clean, 3.20$, one of the
"documented residual" roots later fully closed in Phase 5.

### Phase 3 — bulk runs and the concurrency lesson (06-29 → 06-30)

Slices C and D bulk-translated 44 more roots. **The single most expensive
lesson of the whole project:** Slice D launched 18 roots as parallel
Workflows at once → ~140-250 peak concurrent Sonnet agents → 80+
`Server is temporarily limiting requests` 429s → **117 transient null
cards**. A single-root run at the same time measured **zero** transient
failures. This is why every subsequent runbook — including [H151](https://github.com/gasyoun/Uprava/blob/main/handoffs/H151-Sonnet_RussianTranslation_pwg_ru_verb_batch_drain_04.07.26.md),
the standing drain handoff this session executes under — hard-locks
**≤3-wide concurrency, roots one at a time**. Also this phase: a print-bridge
homograph-multiplication bug found and fixed, and `siD`'s sense_dupes
failure investigated and confirmed faithful-to-source (not over-production).

### Phase 4 — EN pilot, nominal grammar, dashboard (06-30 → 07-01)

The English translation path (FU1) launched in parallel to RU, immediately
surfacing that giant root-article heads (150-200+ `<ls>` citations) are
genuinely output-size-bound on Sonnet even solo — the **head-splitter /
self-heal fragment lane** (validated live: `ji~~h0_00_pwg00` recovered via an
8-fragment split → 48 senses) became load-bearing, not optional. A false
"needs head-splitting" heuristic based on card size was tested and refuted
(the 5 largest cards by `<ls>` count all passed; failure is retry-cap
variance, not size) — retry-first is correct, splitting is a last resort.
The nominal grammar layer (Whitney stem classes, Zaliznyak-style compact
inflection index, vidyut paradigm generation) shipped as **structured data**,
deliberately kept OUT of translation prompts after an A/B showed no
translation-quality gain from injecting it. `gam`'s RU translation, found
stuck at 6/127 (a staged run that was never finished, not data loss), was
caught by a new zero-LLM `ru_coverage.py` safety-net gate and caught up to
94/127 — this is also where the **sub-card-level (not root-level) promotion
merge** was built, after discovering root-level merge would have silently
wiped other roots' already-translated sub-cards.

### Phase 5 — translation memory and quality-gate hardening (07-01 → 07-02)

Content-addressed **translation memory** (TM) shipped at both the whole-card
level and, as a second increment, the **fragment level** — a still-failing
giant card can reuse just its already-translated fragments instead of
retranslating the whole thing, and a fragment shared byte-for-byte between a
root and its derived noun is reused across cards. This is the single biggest
standing cost lever in the pipeline today. In parallel, an independent
Fable-5 gold-sample judge session found the RU/EN quality baseline solid
(96-98.5% faithful) but flagged one dominant defect class — dropped
`{%..%}` gloss-pair markers — which fed into a "translate, don't annotate"
hard-rule tightening (S7) and 4 real gate bugs (FL1/FL2/FL3/FL5: grammar
lookup returning all homonyms instead of none on a miss, an EN strict-gate
that didn't actually fail on nulls, a coverage gate exempting corrupt
denominators, and an over-broad "no text signal" flag).

### Phase 6 — the gate-bug hunt and calibration (07-02 → 07-03)

The audit-tail closed 3 more deferred items (a fixture guard that could
clobber live status, an EN residual-completeness redefinition, a targeted
"topup" requeue for partial giants that avoids re-splitting a whole card).
A **live 4-arm calibration** on real Workflow runs settled `OUTPUT_BUDGET=90`
(vs the earlier 60) as measurably better (-9% agent calls, -14% tokens, -54%
wall-clock, same 0-null rate) and confirmed finer autosplit fragmentation
makes things *worse*, not better. Then the deepest single investigation of
the project: re-examining `gam`'s "documented residuals" from Phase 2 found
they weren't residuals at all — **3 real gate bugs**: a multi-layer PW/SCH
addenda card had its cross-reference continuations miscounted as numbered
senses (false `COVERAGE-OVER`); German capitalization was tripping a
Latin-binomial detector meant for species names; and a 3-letter gloss token
was matching as a substring *inside* an unrelated Sanskrit citation. Fixed,
pinned with selftests, re-audited `gam` from the *same* wf_output (no
re-translation needed) straight to **127/127 clean**. This is the moment the
gate stack went from "probably fine, some accepted residuals" to
"mechanically verified clean," and it's why the very next phase re-audited
every other already-promoted root against the fixed gates before scaling up.

### Phase 7 — scope ruling and the standing drain (07-03 → 07-04)

A full readiness audit (selftests green, TM fresh, every historical
silent-loss class fixed with a pinned test) concluded the pipeline was ready
to scale from "documented small batches" to **all 703 remaining
DCS-attested verb roots** (`verb_worklist.py` enumerates the set
reproducibly: 1,882-root universe ∩ 749 DCS-attested − 46 already promoted).
[H151](https://github.com/gasyoun/Uprava/blob/main/handoffs/H151-Sonnet_RussianTranslation_pwg_ru_verb_batch_drain_04.07.26.md)
became the standing, resumable drain handoff this and future sessions
execute against, one root at a time, with the exact RUN_FREQ_MAX loop.

### Phase 8 — this session (07-04): the drain begins, and 4 more real bugs found

Executing H151 surfaced its own set of process defects, found and fixed the
same session rather than worked around:

1. **A committed merge-conflict block** sat live in `.ai_state.md` on
   `origin/master` itself (`<<<<<<<`/`>>>>>>>` markers from a stashed-changes
   mishap) — fixed.
2. **`requeue_from_audit.py` never actually enforced `--no-tm`** on a
   defect/all requeue, despite the hard rule documented since the `gam`
   TM-staleness trap — the helper built the regeneration command without the
   flag. Fixed; TM could otherwise have silently re-served exactly the
   content a gate had just flagged.
3. **The RU/EN cost-estimate formula counted a presplit giant as costing 1
   agent call**, when presplit specifically means "too dense for one call,
   route to N fragment calls." A 150-`<ls>` giant was estimated at "1
   agent"; `vid`'s real first pass spent 102 agents against a 13-agent
   estimate. Fixed to use the fragment-group count already computed at
   harness-generation time.
4. **`window_provenance.stale_check()` compared result-key order, not set**
   — any run whose harness emitted results in completion order rather than
   rootmap-declared order (the normal case) was wrongly refused as
   `stale_artifact`, blocking gates/glue outright. Fixed to compare as sets.
5. **The presplit router was blind to SENSE density** (H155). `tyaj`'s drain
   stalled ~7 min on one agent retrying the identical call and never
   producing valid output — the `tyaj~~h0_zz_pw` PW addenda card compresses a
   whole root article (base verb + Caus/Desid + every prefix combination)
   into ~35 terse senses carrying only 11 `<ls>`, so its citation weight
   `1+<ls>=12` ranked it among the *lightest* cards while its real output
   surface (dozens of `{tag,german,russian}` sense objects + ~140 masked
   tokens to reproduce exactly) was the *heaviest* — it deterministically
   blew the whole-card StructuredOutput retry cap. The presplit router
   (built in Phase 5 for the 150-`<ls>` citation giants) only measured
   citations, so it waved this card through into a normal batch. Fixed by
   adding a second, orthogonal presplit trigger keyed on the deterministic
   fragment count (== sense-objects to emit) vs a new `SENSE_PRESPLIT_BUDGET`
   (20; only ~0.2% of cards exceed it, a clean shelf above every known-good
   whole-card head). Validated live: the `[sam, zz_pw]` pair that stalled now
   returns ok:2/null:0 with `zz_pw` healed complete via 4 fragment groups.
   The `_zz_pw` addenda class was a known StructuredOutput-cap trigger
   (`gam~~h0_zz_pw01` hit it before and only recovered via selfheal after the
   doomed retries); this makes the recovery *immediate* instead of paid-for.
6. **A wall-clock kill gate — the runtime backstop for the failure drivers
   we haven't turned into structural triggers yet** (H155 follow-up, MG:
   *"card complexity is sense-count — that's just one case; what else is
   possible? Add a gate: if a translation runs too long, kill it, don't wait
   for miracles"*). #5 fixes the *known* sense driver proactively, but the
   taxonomy in [`FAILURE_MODES_AND_KILL_GATE_2026-07-04.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/FAILURE_MODES_AND_KILL_GATE_2026-07-04.md)
   lists more (gloss-prose volume, masked-token count, multi-layer nesting,
   batch-level sums, and whatever hasn't surfaced) — any single-metric budget
   is blind to the others. So every schema-bearing `agent()` call is now raced
   against a `setTimeout` budget scaled to its masked-skeleton byte volume
   (the best time predictor — output ≈ 2× skeleton — measured from a 13-call
   `tyaj --no-tm` benchmark: legit calls ran ≤ 84 s at ~25 ms/byte). A call
   that overruns `KILL_FACTOR=2 ×` its expected time is abandoned and its cards
   fall to the bounded fragment lane, instead of waiting out the full ~5-deep
   retry cap. Runtime constraints shaped it: `setTimeout` works (a *relative*
   timer — `Date.now()` is banned), but `AbortController` is absent, so a
   killed call keeps running in the background until its own cap — the harness
   just stops *blocking* on it. Default ON (`--no-kill` / `--kill-factor=N`);
   proven by a zero-token behavioural test (9/9) + a static wiring selftest.
   **The discipline going forward:** when a new stall class appears in a real
   run, promote it from "caught by the kill gate" to its own structural
   trigger (as #5 did for senses) so the next occurrence spends zero doomed
   tokens.

A cross-language audit also found that 3 of the Phase-6 gate-bug fixes
never reached the EN audit path (a separate implementation,
`audit_window_en.py`, that reimplements its own gates rather than sharing
RU's) — tracked as a GAP in the new [`LANG_PARITY.md`](LANG_PARITY.md)
ledger (see below) rather than left to be silently rediscovered.
Additionally traced 100% of `vid`'s first-pass null cards to a single root
cause: an undersized (non-splittable) card shares a batch with denser
content, the batch blows its retry cap, and the small card has zero
recovery mechanism of its own — flagged as a follow-up, not yet fixed.

5. **Fragment-tag collision (SENSE-DUPE false positive) on giant single-sense
   heads.** `vid`'s homonym head `h0`'s giant single-sense part
   (`h0_00_pwg00`, source sense "1", 168 `<ls>` citations) is tier-2
   citation-split by `autosplit_requeue.plan()` into many fragments, ALL
   belonging to the same source sense (`sense_ord`/`si` == 0) — but
   `gen_opt_harness2.py`'s `FRAGS[k]` builder discarded that `sense_ord`
   (bound to `_si` and thrown away), so the JS `selfHeal()` heal path had no
   way to tell "these fragments are citation batches of ONE sense" from
   "these are genuinely different senses." Translating each fragment
   independently, the model fabricated fresh incrementing tags per fragment
   (2, 3, 4...) that then collided with a sibling rootmap part's REAL
   different senses in `audit_sense_dupes.py`'s cross-part duplicate check —
   a deterministic tagging artifact (reproduced identically across 2
   independent live requeue rounds), not model stochasticity. Fixed by
   threading `sense_ord` into `FRAGS` as `si` and normalizing every
   fragment's tag to its group's first-seen tag per `si` in JS `selfHeal()`
   (`siTag`/`applyTag`). Same-session, also hardened the SAME split path
   against a second, adjacent hypothesis: `_cit_parts()` decided its budget
   cuts purely on running `<ls>` counts with zero awareness of `{#...#}`
   Sanskrit-span state — a `<ls>...</ls>` span can never straddle a cut (a
   new `<ls>` can only open once the previous one closed), but `{#...#}`
   never contributed to the count at all, so a still-open `{#...#}` block
   could get torn across a cut forced by a later, unrelated `<ls>` tag. A
   torn span can no longer be matched by `pwg_mask`'s PAIRED regex, so its
   Sanskrit content passes through UNMASKED into the model's "translatable"
   prose — a plausible mechanism for the SAN-LOSS pattern observed on the
   same giant heads, though NOT empirically reproduced against the actual
   failing `vid` data (the run's raw fragment files were no longer present
   in-tree to inspect). Fixed defensively via `_span_open()`: defer the cut
   until the accumulated fragment text is `<ls>`/`{#..#}` balanced. Both
   fixes covered by new `window_selftest.py` fixtures
   (`test_selfheal_fragment_si_threaded_and_tags_normalized`,
   `test_cit_split_never_tears_open_span`). Same-shape risk: any other
   already-promoted or future-drained root with a citation-dense
   single-sense giant head (BU/yuj/as/sTA/i in the H151 queue are candidates)
   can hit the same tag-collision pattern — worth a SENSE-DUPE re-check on
   promoted cards once the fix has run.

### Phase 9 — nominal-side PWG-miss gap fixed; H214 no-PWG lane implemented (H206/H214, 07-05/07-06)

[`PWG_LAYER_COMBINATIONS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/PWG_LAYER_COMBINATIONS.md)
measured that **~36% of the local headword union carries zero PWG record**
(FINDINGS.md §61) — PWG does not define the headword universe alone; PW-only
headwords alone outnumber PWG-only ones 6-to-1. A follow-up code read of
[`src/pilot/nominals_worklist.py`](src/pilot/nominals_worklist.py) confirmed
this was an active drop, not just a theoretical risk: `build_worklist()`
split nominal candidates into `hits` (present in `dm.index('pwg')`) and
`misses` (everything else), and only `hits` ever fed `runnable_remaining` —
`misses` were reported in an aggregate `pwg_misses` count and then silently
excluded from the translation queue forever, even when a miss carried a real
PW, SCH, or PWKVN record (translatable content, not a non-word).

**Damage-scope count** — cross-checking every `miss_keys` entry from the 3
already-run nominal wordlists (Приложение 5, Приложение 10, Сборное ядро)
against `dm.index('pw'|'sch'|'pwkvn')`: of **1,743 total PWG misses**, **416**
(24%) DO have a real record in another local layer — dropped-but-translatable
— and 1,327 are true misses (absent from every local layer). Deduplicated
across the 3 wordlists (Сборное ядро overlaps pril5/pril10), that's **232
unique lemmas**.

**H206 fixed:** `build_worklist()` now splits `misses` into `other_layer_hits`
(tagged with which of `pw`/`sch`/`pwkvn` they hit) and `true_misses` (absent
everywhere), both surfaced in the payload and the committed `.coverage.md`
reports, instead of one undifferentiated `miss_keys` bucket.

**H214 implemented:** M.G. ruled the old portrait-design `@DECIDE`: PWG-missing
but PW/SCH/PWKVN/NWS-present lemmas are needed translations and should render as
standalone supplement-chain cards, without inventing a PWG base portrait or
sense tree. `_pilot_gen_merged.gen_no_pwg_card()` now reuses `dict_merge.merged()`
to emit one labeled sub-card per available non-PWG layer (`<safe>~~h0_zz_<layer>`),
with a minimal portrait carrying `source_profile: "no_pwg_supplement_chain"`.
`gen_opt_harness2.py` carries that marker into workflow meta, and
`promote_final_cards.py` carries it into row provenance alongside the first-class
`layer` field.

`nominals_worklist.py` deliberately keeps these separate from PWG-rooted
`runnable_remaining`: the payload now exposes `no_pwg_runnable`,
`no_pwg_runnable_count`, and `no_pwg_promoted_count`. That separation is
intentional because the rows rest on different-vintage source material, even
though they are now runnable through the nominal harness.

The 232 deduplicated lemmas remain documented in the committed
[`src/pilot/lexical_cores/pwg_miss_backfill_queue.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/lexical_cores/pwg_miss_backfill_queue.md)
backfill queue (key1/IAST/layer(s)/source wordlist(s)). **Do not rediscover this
as a fresh bug** — both the worklist drop and the render path are fixed; what
remains is ordinary lane scheduling/review.

### Phase 10 — nominal-lane cost post-mortem, verified twice, then the first 100-card window (H189 → H191 → H201, 07-05 → 07-06)

The `pril10_w1` nominal window blew its cost estimate; instead of shrugging, the
blowup got a full post-mortem
([`src/pilot/POSTMORTEM_pril10_w1.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/POSTMORTEM_pril10_w1.md),
H189, Opus 4.8 `claude-opus-4-8`, [PR #158](https://github.com/gasyoun/SanskritLexicography/pull/158)):
every hypothesis confirmed, the economics reproduced to the digit, and the fix
set landed as shared code — presplit-lane re-batching (174→69 fragment groups;
real `gam` replay 18→6 agents) plus the standing rule that `kAla`-class monster
windows are never bulk-run, they go to the human-budgeted defer lane. A second
model then **independently re-verified the post-mortem to the digit** (H191,
Codex/GPT-5, [PR #160](https://github.com/gasyoun/SanskritLexicography/pull/160)),
added three guardrail optimizations with selftests, and staged a
deliberately-shaped production window: 100 small nominal heads, 0 deferred
monsters ([`NOMINAL_W1_100SMALL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/NOMINAL_W1_100SMALL.md)).
That window then ran to completion (H201, gen Sonnet 5 `claude-sonnet-5`,
orchestration Opus 4.8, [PR #173](https://github.com/gasyoun/SanskritLexicography/pull/173)):
pass 1 was lost whole to a transient `Connection closed mid-response` outage
(the 19-agent kill switch fired exactly as designed), a clean rerun recovered
93/100, a 7-key transient requeue closed the rest — **100/100 cards promoted
(306 senses)**, the first at-scale proof of the nominal lane end to end.

### Phase 11 — the TM grows teeth: mined tier, batch scale, publication grade (H184 / H186 / H224 / H215, 07-05 → 07-06)

The translation memory stopped being just a byte-reuse cache and became a
curated, graded, exportable asset. Four increments:
[`src/build_glossaries.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_glossaries.py)
(H184, Sonnet 5 `claude-sonnet-5`) extracted 663 IAST-keyed entries from the
two machine-usable Гринцер Ramāyaṇa name-glossaries and wired them into
[`corpus_gate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/corpus_gate.py)
as an evidence-only `SPECIALIST` tier (the four unusable candidates are
documented, not silently dropped).
[`src/mine_running_text.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/mine_running_text.py)
(H186, Opus 4.8; extraction DeepSeek `deepseek-chat`,
[PR #187](https://github.com/gasyoun/SanskritLexicography/pull/187)) opened a
**second TM source**: Sa→Ru term glosses mined from Russian running prose into
a quarantined `mined` tier — never the clean 1.09M-pair `corpus_lexicon` — with
a never-invent prompt, a verbatim-in-passage guard, and a 30-row human
precision gate (97% correct equivalence) before scale was approved. H224
(Opus 4.8, [PR #190](https://github.com/gasyoun/SanskritLexicography/pull/190))
then batch-mined the whole SamudraManthanam folder: **10,132 mined pairs**.
Finally H215 (Opus 4.8, [PR #193](https://github.com/gasyoun/SanskritLexicography/pull/193) /
[PR #194](https://github.com/gasyoun/SanskritLexicography/pull/194)) made the
TM **publication-grade**: a TMX 1.4b exporter
([`src/build_tmx.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_tmx.py))
so the asset is consumable by standard CAT tooling, and a composite A/B/C
quality grader ([`src/tm_grade.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_grade.py))
so every TM row carries an evidence grade instead of implicit trust (grade
distribution logged as FINDINGS §60). H215's remaining slices (L0 segment
layer, oral-corpus ingest, FAIR release clearance) are open — the release
clearance is the real blocker.

### Phase 12 — the re-glue research track: addenda typology, learner apparatus, and the Arm-A/B verdict (H180, 07-05 → 07-06)

A parallel *research* track asked what a print-shaped PWG→RU edition should be
glued from. After a spec pass ([PR #172](https://github.com/gasyoun/SanskritLexicography/pull/172):
5 spec docs, NWS staleness measured at SCH Jaccard 0.992, paper A49
registered), the implementation landed as four deterministic, zero-LLM
builders: [`src/build_relationships.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_relationships.py)
classified **5,603** non-PWG sub-card senses into a provenance-relationship
typology (`restate` 5,054 · `nws_at_sense` 211 · `derived_sense` 98 · `a2a` 89 ·
`sch_star` 88 · `foreign_fragment` 62 · `pw_correct` 1);
[`src/build_learner_scores.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_learner_scores.py)
scored **106,079** PWG headwords by Russian-student-dictionary retention
(learner-core 22,772 = 21%); [`src/build_reglue.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_reglue.py)
re-glued 15/15 pilot headwords with **byte-identity asserted on every `ru`**
(re-glue is free — no re-translation); and
[`src/synth_de_first.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/synth_de_first.py)
assembled the synthesize-first (Arm B) inputs for a 10-word bake-off. Three
HTML review sheets went up for the human gates
([PR #191](https://github.com/gasyoun/SanskritLexicography/pull/191)); the
Arm-B model run + both-arms scoring
([PR #195](https://github.com/gasyoun/SanskritLexicography/pull/195)) returned
the verdict: **synthesize-first does not beat re-glue** — the deterministic
re-glue path stays the edition backbone. Getting that Arm-B run to finish is
what exposed every orchestration failure in the next phase.

### Phase 13 — the orchestration post-mortem and the dispatch wrapper (H234, 07-06)

**H234 implemented (06-07-2026):** the H180 Arm-B synthesis run (Opus 4.8
`claude-opus-4-8` orchestrating 10 async sub-agents) degenerated into a
~40-minute fiasco caught only by hand via file mtimes. Six distinct failures,
all now guarded by
[`src/synth_dispatch.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/synth_dispatch.py)
(deterministic dispatch-and-monitor wrapper, 7-case selftest, zero model call
in the wrapper itself):

1. **False-stall kill** — all 10 agents were judged stalled at ~6 min because
   their transcripts read 0 bytes, and were killed mid-work; on resume they had
   in fact read + analysed their inputs. Async-agent transcripts **buffer** —
   transcript size is NOT a liveness signal. The wrapper judges liveness by
   **output-file growth only**.
2. **Mid-stream API stalls under wide concurrency** — 7/10 resumed agents died
   with `API Error: Response stalled mid-stream`; 10 concurrent large Opus
   generations (26–212 KB inputs) is over the cliff, staggered waves of ~4 ran
   clean. The wrapper caps concurrency at 3 (hard cap 4) with staggered starts.
3. **34-minute silent hang** — the `car` agent last grew its transcript at
   17:45, wrote nothing, emitted no completion/failure signal, and a queued
   resume message was never delivered (a hung agent takes no tool rounds).
   Only a wall-clock guard catches this: the wrapper kills any attempt whose
   output file hasn't grown in 10 min (`--kill-after 600`).
4. **Watcher wiped gitignored outputs mid-build** — outputs written as bare
   untracked files under `pwg_ru/reglue/synth_outputs/` were deleted by the
   repo watcher while agents were still writing. The wrapper authors in a
   staging dir OUTSIDE the repo, lands atomically, and re-verifies the landed
   sha after a delay (the `/watcher-safe-commit` pattern), re-landing if wiped.
5. **Zombie overwrote a scored result** — a replacement `viS` agent produced
   the version that was scored (1597 `<ls>`); the old agent, never confirmed
   dead, finished 47 min later and silently overwrote it with a 1593-`<ls>`
   version. The wrapper confirms an attempt is dead (`wait()` returned) before
   re-dispatching, gives each attempt a private staging file, and seals a
   landed job — late output is discarded, never landed.
6. **Free-form generation of >~800-citation entries is unreliable** — `viS`
   (1597), `DA` (2116), `car` (1019) all stalled or truncated on free-form
   prose and only completed via programmatic assembly (verbatim fragment
   reorder). The wrapper routes inputs above `--assemble-over 800` `<ls>` to
   its deterministic zero-LLM assembler by default; `viS.de_synth.txt` was
   regenerated this way (1597 raw / 1525 unique `<ls>`, `synth_score.py` row
   byte-identical to the committed
   [`ARMB_SCORES.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/reglue/synth_outputs/ARMB_SCORES.tsv)).

Baseline for calibration: a clean single synthesis agent on the largest word
(`viS`) finishes in **under 3 minutes** — so a 10-minute output-file
kill-guard is generous, and "make agents faster" was never the problem.

The same session also ran a registry audit of every pwg_ru handoff: 10 stale
"queued" rows were verified done against merged-PR/`.ai_state` evidence and
rebucketed, leaving the truly-unapplied pwg_ru queue at exactly three
handoffs (H178 ACL verify-and-improve, H188 full pipeline audit, H220 no-PWG
throughput) plus one human `@DECIDE` (H143) — the registry, not the work,
had drifted.

### Phase 14 — no-PWG throughput and the launch-failure ledger (H220, 07-06 → 07-07)

H220 closed the no-PWG supplement-chain throughput gap with an actual
diagnostic Workflow run, not speculation: a 10-card no-PWG window first
measured the lane at ~40% yield, then root-caused the failures to two
different guardrail mistakes. **First**, the wall-clock kill gate was
calibrated on dense verb-root batches, where a slow schema call usually means
"too complex, fall to fragments"; a no-PWG supplement singleton has no
selfheal lane, and its fixed StructuredOutput latency can legitimately sit in
the same 55-105 s band the old byte-scaled budget treated as suspicious. Six
of six nulls were kill-timeouts, and four would have passed if allowed to
finish. **Second**, strict key matching dropped valid output when the portrait's
clean SLP1 `key1` pulled the model away from the mangled safe-name card header.

The fix is lane-specific, not global: no-fallback singles now receive the
180-second ceiling budget, nominal windows may re-key through a scoped
`nominal_keymap`, and the selfheal path preserves the real upstream failure
reason instead of overwriting it with `no-selfheal-fallback`. The same
diagnostic window reran at **10/10 ok, 0 kill-timeouts, 9 agents**, and the
232-lemma no-PWG backfill lane is unblocked for ordinary scheduling.

This phase also adds the post-launch discipline that the history itself had
been missing: [`LAUNCH_FUCKUPS.md`](LAUNCH_FUCKUPS.md) is now the mandatory
per-launch incident ledger, checked by
[`src/pilot/check_launch_ledger.py`](src/pilot/check_launch_ledger.py). This
file (`PIPELINE_HISTORY.md`) remains the curated narrative map; the ledger is
the exhaustive closeout register for Workflow/API failures, expected-vs-actual
economics, classification, guardrail, and residual risk.

## Post-launch discipline

Every Workflow/API launch that hits a failure, null wave, stall, kill,
stale-artifact refusal, cost drift, retry, or suspicious residual must get a
classified entry in [`LAUNCH_FUCKUPS.md`](LAUNCH_FUCKUPS.md) before the handoff
is closed. Use the compact typology there (`concurrency/api`,
`structured-output-limit`, `complexity-estimate-drift`,
`kill-gate-calibration`, `gate-bug`, `artifact/provenance`, `tm/cache`,
`filesystem/watcher`, `key/schema-mismatch`, `operator/process`,
`external-api`, `unknown`). A repeated `unknown` shape is not an accepted
residual; it becomes a bug-hunt handoff.

## Recurring failure patterns (read this before assuming something new is broken)

These are the failure *shapes* that have recurred across the project — if a
future session hits something that smells like one of these, it is very
likely the SAME class, not a new bug:

- **Wide concurrency collapses the whole run.** >3 simultaneous root
  Workflows → server-side rate limiting → transient nulls (Slice D: 117 of
  them). Fix is process discipline (≤3-wide), not code. The same cliff hit
  the H180 Arm-B fan-out as mid-stream API stalls at 10-wide (H234 #2).
- **An async agent's transcript size says nothing about liveness.**
  Transcripts buffer: 0 transcript bytes ≠ stalled (H234 #1 killed 10 healthy
  agents on that inference), and a growing transcript ≠ progress. The only
  trustworthy liveness signal is the agent's OUTPUT FILE growing; the only
  trustworthy completion signal is the output file + a content self-check
  (e.g. `<ls>` count).
- **A killed/failed agent is not dead until its death is observed.** Re-
  dispatching a replacement while the old agent may still be running invites
  a zombie to finish later and overwrite the good result (H234 #5). Confirm
  the kill, and give every attempt its own private output path — never two
  writers on one file.
- **Untracked/gitignored files in this repo are watcher-bait.** The repo
  watcher deletes untracked files, including an agent's half-written output
  (H234 #4). Any agent-facing output must be authored outside the repo and
  landed atomically with a post-land re-verify (`/watcher-safe-commit`
  pattern / `synth_dispatch.land_watcher_safe`).
- **TM/cache silently re-serves already-rejected content.** Any requeue path
  that doesn't explicitly disable the translation-memory lookup will hand
  back the exact content a gate just flagged, because TM addresses on input
  hash, not on pass/fail history.
- **A manual hand-off step between a Workflow run and its on-disk result is
  a loss point.** The H145 `vid` output was confirmed genuinely lost this
  way (the file that should have held the fresh translation stayed
  `meta.root: "gam"` from hours earlier). The fix is structural: drive the
  Workflow from the orchestrating Claude Code session so the result is
  captured programmatically, never a manual save step.
- **Gate false positives cluster around markup/language misclassification.**
  Every real gate-bug hunt so far (Phase 5's FL1-FL5, Phase 6's 3 bugs) has
  found the same shape: a heuristic built for one input class (a single
  numbered sense, an English gloss, a German capitalized word) fires wrong
  on a structurally similar but different input (a multi-layer addenda
  card, a French/Latin euphemism, a Sanskrit citation substring). Assume any
  "risk"/"residual" flag might be this before assuming it's a real
  translation defect.
- **A cost/size estimate that was never checked against a real run tends to
  be wrong in the direction of "too optimistic," specifically around
  fragment/giant-head fan-out.** Both the EN head-splitter myth (Phase 4)
  and this session's presplit-agent-count bug undercounted exactly the same
  kind of thing: a card that needs to be broken into many pieces was priced
  as if it were one piece.
- **A complexity metric tuned for one failure driver is blind to a second
  one.** The presplit router priced output complexity as `1+<ls>` (citation
  count), which correctly flags 150-`<ls>` citation giants but *silently
  waves through* SENSE-dense cards — a PW `_zz_` addenda card can pack ~35
  senses into ~11 `<ls>`, looking trivial by citations while being the
  heaviest card to actually emit. Symptom: one agent stuck retrying the
  identical `agent()` call for minutes on `root: must have required property
  'cards' / must NOT have additional properties` (the model can't emit the
  whole card as valid StructuredOutput, so it never returns `{cards:[…]}`).
  If a card looks light but has dozens of senses, it belongs in the fragment
  lane (H155 fix: the fragment-count trigger now routes it there). The
  `_zz_pw`/`_zz_sch` addenda class is the usual suspect.
- **A fix that lands on one language path doesn't automatically reach the
  other.** See [`LANG_PARITY.md`](LANG_PARITY.md), shipped this session
  specifically because this had already happened once (3 gate fixes,
  RU-only, undiscovered for a day).
- **Kill-gate calibration is lane-specific.** H220 proved that a budget tuned
  for dense verb batches false-kills no-fallback no-PWG singleton cards. Verb
  batch, nominal small, nominal monster, no-PWG single, synth fan-out, and
  external API mining launches keep separate calibration evidence; do not
  blindly promote one lane's timeout envelope to another.

## Current state (as of 07-07-2026)

- Store: `src/pwg_ru_translated.jsonl` (RU spine) + a parallel EN store,
  both local-only/gitignored, both TM-backed.
- 46 verb roots promoted before this session's drain began; drain target is
  all 703 DCS-attested remaining, via the standing [H151](https://github.com/gasyoun/Uprava/blob/main/handoffs/H151-Sonnet_RussianTranslation_pwg_ru_verb_batch_drain_04.07.26.md)
  handoff, one root at a time, ≤3-wide.
- Gate stack: `audit_window.py` (RU) mechanically verified clean against its
  own historical false positives (Phase 6); `audit_window_en.py` (EN) has
  NOT yet received the same fixes — tracked as a GAP in `LANG_PARITY.md`.
- Nominal lane: production-proven at 100/100 cards (Phase 10, H201); the
  PWG-miss drop is fixed, no-PWG supplement-chain cards render (Phase 9), and
  no-PWG singleton throughput is fixed/calibrated (Phase 14); the 232-lemma
  backfill queue is documented, awaiting ordinary scheduling.
- Cost/performance: `perf_preflight.py` gives a now-accurate agent-count
  estimate (fixed Phase 8); TM (card + fragment level) is the main
  standing cost lever; `OUTPUT_BUDGET=90` is the calibrated default.
- TM asset (Phase 11): clean 1.09M-pair `corpus_lexicon` + quarantined
  `mined` tier (10,132 pairs, 97%-precision-gated) + `SPECIALIST` glossary
  tier; every row gradeable A/B/C (`tm_grade.py`), exportable as TMX 1.4b
  (`build_tmx.py`). FAIR release clearance is the open blocker (H215 S3–S5).
- Edition backbone (Phase 12): deterministic re-glue won the Arm-A/B
  bake-off — synthesize-first is retired for composition; the addenda
  typology (5,603 senses) and learner scores (106,079 headwords) are built,
  three review sheets await votes.
- Multi-agent runs (Phase 13): every pwg_ru sub-agent fan-out goes through
  `src/synth_dispatch.py` (≤4 concurrency, 10-min output-file kill-guard,
  single-owner sealed outputs, watcher-safe landing) — bare fan-outs are
  banned.
- Process discipline (all MG-locked, do not re-litigate): opt2 canonical
  harness, ≤3-wide concurrency, `--no-tm` mandatory on requeue, lang-fix
  parity classification mandatory before closing a session, drive the
  Workflow from the Claude Code session (not a manual Max-surface save), and
  update/check `LAUNCH_FUCKUPS.md` before closing any launch-shaped handoff.

## Where to go next

- **Doing the actual drain right now?** → [`src/pilot/RUN_FREQ_MAX.md`](src/pilot/RUN_FREQ_MAX.md)
  is the exact loop, verbatim.
- **Touching RU or EN-specific code?** → [`LANG_PARITY.md`](LANG_PARITY.md)'s
  policy: classify SHARED / INTENTIONAL-DIVERGENCE / GAP before closing out.
- **A card/batch stalled, or wondering what else can blow the retry cap?** →
  [`FAILURE_MODES_AND_KILL_GATE_2026-07-04.md`](FAILURE_MODES_AND_KILL_GATE_2026-07-04.md):
  the full driver taxonomy + the wall-clock kill-gate design and calibration.
- **Closing a launch after failures or retries?** →
  [`LAUNCH_FUCKUPS.md`](LAUNCH_FUCKUPS.md) + `python src/pilot/check_launch_ledger.py
  --handoff H###` are the mandatory incident register and checker.
- **What's queued/in-flight/blocked right now?** → [`.ai_state.md`](.ai_state.md),
  the live journal (this document doesn't replace it — it's the map, not the
  territory).
- **A closed one-off investigation from mid-2026-06?** →
  [`archive/closed_investigations/`](archive/closed_investigations/README.md).

_Dr. Mārcis Gasūns_
