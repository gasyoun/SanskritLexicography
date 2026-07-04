# PWG→RU/EN pipeline — history: solutions, failures, current state

_Created: 04-07-2026 · Last updated: 04-07-2026_

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
failures. This is why every subsequent runbook — including [H151](https://github.com/gasyoun/Uprava/blob/main/handoffs/H151_SanskritLexicography_pwg_ru_verb_batch_drain.md),
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
[H151](https://github.com/gasyoun/Uprava/blob/main/handoffs/H151_SanskritLexicography_pwg_ru_verb_batch_drain.md)
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

## Recurring failure patterns (read this before assuming something new is broken)

These are the failure *shapes* that have recurred across the project — if a
future session hits something that smells like one of these, it is very
likely the SAME class, not a new bug:

- **Wide concurrency collapses the whole run.** >3 simultaneous root
  Workflows → server-side rate limiting → transient nulls (Slice D: 117 of
  them). Fix is process discipline (≤3-wide), not code.
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

## Current state (as of this session, 04-07-2026)

- Store: `src/pwg_ru_translated.jsonl` (RU spine) + a parallel EN store,
  both local-only/gitignored, both TM-backed.
- 46 verb roots promoted before this session's drain began; drain target is
  all 703 DCS-attested remaining, via the standing [H151](https://github.com/gasyoun/Uprava/blob/main/handoffs/H151_SanskritLexicography_pwg_ru_verb_batch_drain.md)
  handoff, one root at a time, ≤3-wide.
- Gate stack: `audit_window.py` (RU) mechanically verified clean against its
  own historical false positives (Phase 6); `audit_window_en.py` (EN) has
  NOT yet received the same fixes — tracked as a GAP in `LANG_PARITY.md`.
- Cost/performance: `perf_preflight.py` gives a now-accurate agent-count
  estimate (fixed this session); TM (card + fragment level) is the main
  standing cost lever; `OUTPUT_BUDGET=90` is the calibrated default.
- Process discipline (all MG-locked, do not re-litigate): opt2 canonical
  harness, ≤3-wide concurrency, `--no-tm` mandatory on requeue, lang-fix
  parity classification mandatory before closing a session, drive the
  Workflow from the Claude Code session (not a manual Max-surface save).

## Where to go next

- **Doing the actual drain right now?** → [`src/pilot/RUN_FREQ_MAX.md`](src/pilot/RUN_FREQ_MAX.md)
  is the exact loop, verbatim.
- **Touching RU or EN-specific code?** → [`LANG_PARITY.md`](LANG_PARITY.md)'s
  policy: classify SHARED / INTENTIONAL-DIVERGENCE / GAP before closing out.
- **What's queued/in-flight/blocked right now?** → [`.ai_state.md`](.ai_state.md),
  the live journal (this document doesn't replace it — it's the map, not the
  territory).
- **A closed one-off investigation from mid-2026-06?** →
  [`archive/closed_investigations/`](archive/closed_investigations/README.md).

_Dr. Mārcis Gasūns_
