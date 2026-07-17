#!/usr/bin/env python
"""Production harness v2 — BATCHED + MASKED, canonical output.

Folds the two measured wins (TLONLY_PROTOTYPE.md) into the production path:
  - BATCHING: several cards per agent() call (amortizes the ~27k-token system-prompt
    cache-create that dominates cost — measured -89% on small cards).
  - MASKING: each card's raw is pwg_mask-skeletonized so the model reads/echoes the
    compact {Tn} form, not full citation lists. {Tn} restored to exact source markup
    IN THE JS before returning, so the result is already a canonical wf_output.json
    (rich per-card schema unchanged) — no new operator assembly step, audit_window.py
    consumes it as-is.

Quality parity: reuses the FULL production CONV+TR prompt (all HARD RULES, NWS owner
map, Nachträge, microstructure) with a MASKED/BATCHED preamble that overrides only the
input-format + markup-verbatim specifics ("keep {Tn} verbatim" instead of "{#..#}/<ls>").

Usage:  python src/pilot/gen_opt_harness2.py <root> [--keys=k1,k2] [--budget=N] [--out=PATH]
        [--no-selfheal] [--selfheal-budget=12]  # selfheal ON by default (MG 2026-07-02)
        [--no-binary-split]                     # binary-split ON by default (MG 2026-07-02)
        [--output-budget=N|off]                 # citation-weighted batching, DEFAULT 90
                                                # (calibrated 2026-07-03, see
                                                # KNOB_CALIBRATION_2026-07-03.md);
                                                # 'off' or an explicit --budget=N = byte mode
        [--tm[=PATH] | --no-tm]                 # content-addressed translation memory:
                                                # default auto-uses translation_memory.<lang>.json
                                                # when present; --no-tm opts out.
        [--suggest-tm[=PATH]]                   # advisory suggestions; never skip agent calls
        [--suggest-profile=semantic|german|sanskrit|balanced]
        (--selfheal / --binary-split still accepted as no-ops for documented runbooks)
Writes: src/pilot/run_pilot_wf.opt2.js  (or --out=PATH — use a per-root/per-chat path to
        avoid the gen->copy race when several chats generate harnesses concurrently)
"""
import datetime
import json
import math
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from window_common import INP, REPO, SRC, input_paths, load_json, read_text, rootmap_path, sha256_file, write_text
from agent_budget import derive_agent_budget
import pwg_mask
import card_fields                                    # C-01: the one restore/promote field set
from autosplit_requeue import plan as split_plan     # deterministic per-card sense/citation split
from sense_count import count_source_senses           # H920/H960 deterministic top-level source-sense count
sys.path.insert(0, SRC)
from safe_filename import safe_name
from execution_contract import SCHEMA_V2, bind_output_meta, config_dir_fingerprint
from whitney_grammar import grammar_for
from nominal_grammar import nominal_grammar_for

SELFHEAL = True    # DEFAULT ON since 2026-07-02 (MG decision after the S10 live validation —
                   #  4/4 vas keys recovered, ji 8->48 senses; ARCHITECTURE_AUDIT_2026-07-02.md).
                   #  On a card the batch can't translate, auto-split it in-harness
                   #  (deterministic split precomputed here) and translate the fragments, then
                   #  stitch back — no manual requeue. --no-selfheal restores the old behavior.
SELFHEAL_GROUP_BUDGET = 12   # --selfheal-budget=N: fragments are grouped (in document order) into
                   #  this many "citation-weighted units" (1 + <ls> count) per heal agent() call —
                   #  citation count, NOT byte size, drives StructuredOutput complexity, and masking
                   #  already shrinks fragment bytes far below what predicts failure (a dense card's
                   #  own fragments can total <4KB and still be the exact complexity that failed as
                   #  a whole card). A single fragment at/above the budget (e.g. a tier-2 citation
                   #  chunk near autosplit_requeue.LS_BUDGET=18) still gets its own call; several
                   #  light (low-<ls>) fragments share one call, cutting a 13-fragment card to a
                   #  handful of calls instead of 13, without recombining the dense units that
                   #  caused the original failure.
# --- presplit-PRIMARY fragment lane budget (H189, 2026-07-05) ----------------------
# SELFHEAL_GROUP_BUDGET=12 above is deliberately conservative: it groups the fragments of
# a card that ALREADY FAILED as a whole card, so small safe groups matter more than
# amortization. But a PRESPLIT card is routed to the fragment lane as its PRIMARY path
# (it never attempts the whole-card batch), and in nominal-window runs EVERY card can be
# presplit — so grouping them at 12 means each ~25-30k-token framework prompt is amortized
# across only ~2-3 fragments per agent() call. The pril10_w1 blow-up (H189): 8 heads ->
# 448 fragments -> 174 groups (~2.6 frags/group) -> the framework re-cached ~230x ->
# cache-write was 60% of a $80 / 3-card bill. The fix: group PRESPLIT cards at a budget
# close to the proven-safe whole-card ceiling instead. A single fragment-lane agent() call
# can safely emit as much as the batch lane already emits for a whole card (OUTPUT_BUDGET=90
# citation-units / SENSE_PRESPLIT_BUDGET=20 senses); staying just UNDER both keeps the same
# retry-cap safety while packing ~6x more fragments per call. Measured on pril10_w1's real
# fragment weights: 60/18 takes 174 -> 69 groups (kAla 32->11, antara 32->9), i.e. the
# framework is re-cached ~2.5x fewer times, at zero new output-size risk (each group stays
# smaller than a batch the batch lane already runs). The heal-of-a-failed-whole-card path
# keeps SELFHEAL_GROUP_BUDGET; only the presplit-PRIMARY grouping uses these.
PRESPLIT_GROUP_CITE_BUDGET = 60  # --presplit-group-budget=N: citation-weighted (1+<ls>) cap
                   #  per presplit-lane agent() call. 60 < OUTPUT_BUDGET 90 -> each call is
                   #  strictly lighter than a batch the batch lane already handles.
PRESPLIT_GROUP_SENSE_CAP = 18    # AND at most this many fragments (== senses emitted) per call,
                   #  so a run of many tiny (0-<ls>) fragments can't silently pack >18 senses
                   #  into one call and re-trigger the sense-density failure. 18 < the
                   #  SENSE_PRESPLIT_BUDGET=20 whole-card ceiling, with margin.
BINARY_SPLIT = True   # DEFAULT ON since 2026-07-02 (MG decision): when a whole batch call
                   #  fails/comes back malformed (not just individual cards inside it), bisect
                   #  the still-pending cards into two halves and retry each half recursively
                   #  (own 2-attempt budget each) instead of re-submitting the identical full
                   #  batch — isolates a single poison card without re-billing the cards around
                   #  it. Bottoms out at single cards, which fall through to selfheal as before.
                   #  --no-binary-split restores the flat-retry loop.
OUTPUT_BUDGET = 90 # DEFAULT 90 citation-weighted units since 2026-07-03 (raised from the
                   #  untuned S10-era 60 after a calibration A/B on the hA root: 90 clearly
                   #  won on both cost and quality — 60 agents/4.03M tok/496s vs 60's
                   #  66 agents/4.68M tok/1082s, both 56/56 ok with 0 null — see
                   #  KNOB_CALIBRATION_2026-07-03.md): size the main batches by estimated
                   #  OUTPUT complexity (1 + <ls> count per card — same metric as
                   #  --selfheal-budget) instead of INPUT bytes (skeleton+portrait). Input
                   #  bytes don't predict StructuredOutput failure (TOKEN_LEVER_FINDING_2026-06-30:
                   #  the portrait-slim byte lever was a non-lever); citation density does.
                   #  Byte mode is still reachable: an EXPLICIT --budget=N (without
                   #  --output-budget) or --output-budget=off — keeps documented byte-budget
                   #  invocations (e.g. FU1 --budget=6000) exact.
SENSE_PRESPLIT_BUDGET = 20  # --sense-presplit-budget=N (0/off to disable). SECOND, orthogonal
                   #  presplit trigger added 2026-07-04 (H155, tyaj~~h0_zz_pw stall). The
                   #  citation metric (1 + <ls>) predicts whole-card StructuredOutput failure for
                   #  CITATION giants (150-<ls> pwg00 heads) but is BLIND to SENSE-dense cards: a
                   #  PW addenda card that compresses a whole root article (base verb + Caus/Desid
                   #  + every prefix combination) can carry ~35 senses in only ~11 <ls>, so its
                   #  1+<ls>=12 weight ranks it as one of the LIGHTEST cards while its actual
                   #  output surface (dozens of {tag,german,russian} sense objects + reproducing
                   #  ~140 masked tokens in exact positions) is the HEAVIEST — deterministically
                   #  blowing the retry cap as a whole card (tyaj~~h0_zz_pw: 35 senses, stalled
                   #  ~7 min retrying the identical call before MG stopped it; the gam~~h0_zz_pw01
                   #  precedent hit the cap and only recovered via selfheal). A card whose
                   #  deterministic FRAGMENT count (== sense-units the model must emit) exceeds
                   #  this budget is routed STRAIGHT to the proven fragment lane, same as the
                   #  citation giants — converting up-to-5 doomed retries + binary-split cascade
                   #  into zero. Threshold 20 sits on a clean shelf: only ~0.2% of cards carry
                   #  >20 senses (survey 2026-07-04), and every known-good whole-card head is far
                   #  below it (sam 6, pari 8). Senses are far heavier per unit than citations
                   #  (sam translates fine at 34 <ls>), so this budget is intentionally much
                   #  lower than OUTPUT_BUDGET and independent of byte/citation batching mode.
PRESPLIT_SOLO_CITE_FLOOR = 40  # --presplit-solo-cite-floor=N. The CITATION presplit trigger
                   #  compares (1 + <ls>) to the per-batch OUTPUT_BUDGET, which correctly catches
                   #  the 150-<ls> pwg00 heads when the budget is the default 90 — but DEGENERATES
                   #  under --output-budget=1 (the no-PWG single-card lane): there the budget is 1,
                   #  so ANY card with >=1 citation "exceeds" it and is force-routed to the fragment
                   #  heal lane. Those tiny cards (H255 presplit cohort: 1-11 <ls>, 307-1131 B) then
                   #  die on the heal groups' byte-scaled kill budgets (~60 s) instead of getting a
                   #  whole-card attempt — a misfire, since the SAME cards translate whole fine (sam
                   #  is fine at 34 <ls>). So the cite trigger fires only when (1+<ls>) exceeds
                   #  max(OUTPUT_BUDGET, this floor): a card genuinely fails-solo (>=40 citation-units,
                   #  well above the whole-card-safe 34 and below the 150 giants), not merely because
                   #  the batch holds one card. For OUTPUT_BUDGET >= 40 (default 90) nothing changes.
# --- wall-clock kill gate (H155 follow-up, 2026-07-04) ----------------------------
# The structural presplit triggers above catch the KNOWN whole-card failure drivers
# (citation + sense density) BEFORE a run. The kill gate is the runtime BACKSTOP for
# the drivers we haven't characterized yet (gloss-prose volume, masked-token count,
# multi-layer nesting, novel shapes — see FAILURE_MODES_AND_KILL_GATE_2026-07-04.md):
# every schema-bearing agent() call is budgeted a wall-clock allowance scaled to its
# complexity, and a call that runs past KILL_FACTOR x its expected time is abandoned
# (the harness stops blocking and routes its cards to the bounded fragment lane)
# instead of waiting out the full ~5-deep StructuredOutput retry cap (the ~7-min
# tyaj~~h0_zz_pw stall MG stopped by hand). Implemented in-JS with setTimeout (a
# RELATIVE timer — Date.now() is banned in Workflow scripts); AbortController is
# unavailable in the runtime, so an abandoned call keeps running in the background
# until it dies on its own cap — we stop WAITING on it, which is the win.
# Budget model (fitted from the tyaj --no-tm benchmark, 13 agent calls, 2026-07-04):
# a call's expected ms ~= KILL_BASE_MS + KILL_SLOPE_MS * skel_bytes, where skel_bytes =
# the summed MASKED-SKELETON byte length of the call's cards/fragments. Skeleton bytes
# are the best single time predictor because the model's OUTPUT is ~2x the skeleton (echo
# the german + write the russian), and they are a natural COMPOSITE of every driver in
# FAILURE_MODES_AND_KILL_GATE_2026-07-04.md — citations (as {Tn}), senses (more lines),
# and gloss prose all land in the skeleton. Benchmark: legit main-batch calls ran
# ~25 ms/skel_byte (max ~44 on a slow-variance call), 16-84 s wall-clock. The SLOPE below
# is set ABOVE the observed ceiling and then KILL_FACTOR is applied on top, so no legit
# call (even a +50% variance one) is ever killed, while a doomed stall (the ~7-min
# zz_pw retry-cap loop = ~5x normal) blows past. Budget = KILL_FACTOR * (BASE + SLOPE *
# skel_bytes), clamped to [KILL_FLOOR_MS, KILL_CEIL_MS]. Conservative first cut on
# purpose (a false kill costs one selfheal, but we still want zero of them on rollout);
# tighten with --kill-factor once real runs confirm the envelope.
KILL = True                 # --no-kill disables; --kill-factor=N tunes the multiple
KILL_FACTOR = 2.0           # MG's "200%": kill a call at 2x its expected-for-complexity time
KILL_BASE_MS = 20000        # fixed per-call latency (model spin-up + fixed framing). Lowered
                            #  from 30000 (H189): 30s was fitted to WHOLE-CARD batch calls; the
                            #  fragment lane (now the primary path for presplit cards) has less
                            #  fixed framing, and MG's directive is that a subcard >~60 s is
                            #  already suspicious.
KILL_SLOPE_MS = 45          # ms per masked-skeleton byte (above the ~44 ms/byte observed ceiling)
KILL_FLOOR_MS = 45000       # H189 recalibration (MG: ">~60 s per subcard is suspicious; >3 min
                            #  unacceptable"). Was 120000 (2 min) — far too loose for a single
                            #  fragment: it guaranteed nothing was killed before 2 min even for a
                            #  tiny call, so the pril10_w1 fragments ran 3-6.5 min each. 45 s floor
                            #  + BASE/SLOPE puts a tiny fragment's hard-kill at ~60-70 s.
KILL_CEIL_MS = 180000       # hard ceiling — NOTHING runs past 3 min (MG). Was 480000 (8 min); the
                            #  worst pril10_w1 agent ran 390 s (6.5 min) inside the old ceiling. On
                            #  kill the call is abandoned and its cards fall to the bounded fragment
                            #  lane / binary-split, so a killed unit is REQUEUED, never silently
                            #  lost (see resolveGroup/healGroup below).
# --- live budget kill-switch (H189, 2026-07-05) -----------------------------------
# The per-call kill gate above bounds ANY SINGLE agent() call, but nothing bounded the
# WHOLE WINDOW: pril10_w1 spawned 230 agents (est. 174) and burned 42 M tokens before MG
# killed it by hand. H189 added one shared MAX_AGENTS counter; H442/H462 then proved that
# sharing it between whole-card translation and fragment recovery makes the per-card heal
# cap unreachable on an all-heal window. The generated runtime now has two independently
# derived pools: translate calls (including binary-split retries) and heal calls. The
# translate ceiling remains proportional to its preflight batch count; the heal ceiling is
# the sum of the already-bounded per-card heal ceilings, so a window cannot starve recovery
# before those card-level guards can bind. ``agent_budget.py`` owns the pure derivation.
KILL_SWITCH = True          # --no-kill-switch disables; --max-agents=N overrides the combined total
MAX_AGENTS_FACTOR = 3.0     # translate pool: abort past 3x the whole-card batch estimate
                            #  (pril10_w1 was 230/174 = 1.3x before the manual kill — 3x leaves
                            #  ample room for legitimate binary-split/heal while still catching a
                            #  true runaway well before a $80 outcome).
MAX_AGENTS_HEADROOM = 10    # additive jitter allowance so a TINY window (expected 1-2) whose one
                            #  hard card binary-splits into ~5-7 heal agents isn't false-aborted —
                            #  replaces the old flat floor of 40, which was far too loose for
                            #  small/medium words (they never legitimately approach 40, so the
                            #  floor let their runaways run unchecked to 40). H189 follow-up.
MAX_AGENTS_OVERRIDE = None  # --max-agents=N: combined ceiling allocated across both pools
# --- low-width staggered dispatch (H255/H811, 2026-07-12) --------------------------
# The top-level dispatch fans every batch into the Workflow runtime, which runs ~min(16,
# cores-2) ~= 10 concurrently. H255 w07 proved that on a *degraded* generation API this
# self-inflates: a tiny single-fragment card that completes in ~54s ALONE (measured, isolated
# schema-carrying probe) blows past even the 180s kill CEIL at ~10-wide (32/36 kill-timeouts,
# 128-500B skeletons). MAX_WIDE caps the concurrent dispatch units so a requeue keeps each
# card near its isolated latency; STAGGER_MS spaces the first MAX_WIDE starts so the degraded
# API isn't hit by a thundering herd. 0 = unbounded (default; uses the runtime parallel()).
MAX_WIDE = 0                # --max-wide=N: at most N translateBatch/healOnly units in flight
STAGGER_MS = 0              # --stagger-ms=M: delay between the first MAX_WIDE worker starts
# --- per-card heal budget (H442, 2026-07-10) --------------------------------------
# The window-level MAX_AGENTS switch above stops a runaway, but it is a SHARED pool: it
# cannot stop ONE dense card from spending the WHOLE window budget before the other cards
# ever run. On dense band-4 nominal singletons (the medium50 test, H317/H389/H437) this is
# the dominant failure: a card whose heal group keeps failing bisects 3-attempts-then-halve
# recursively (a single 12-fragment group can spawn ~45 agent() calls: 3 + 2*3 + 4*3 + ...),
# and because selfHeal cards run in one shared parallel() pool against one shared AGENTS_SPENT
# counter, 3-4 such cards exhaust MAX_AGENTS between them and the remaining ~9 cards are nulled
# `budget-kill-switch` UN-ATTEMPTED and requeued (H437: w1b 61/61 agents, 1 clean, 9 transient
# -null). Measured cost profile: ~2 M tokens per window buys ~1 clean card. The fix is a PER-CARD
# ceiling on heal agent() calls, threaded through healGroup's recursion: once a single card's
# own heal spend crosses its budget, healGroup stops retrying/bisecting and returns a PARTIAL
# card (resolved fragments kept, the rest recorded as missing_fragments for a targeted requeue)
# instead of consuming the shared window budget. A dense card thus FAILS FAST + CHEAP to partial,
# leaving the window budget for the cards that can heal cleanly. Sized off the card's own group
# count (its happy-path is ~1 call/group), mirroring the window MAX_AGENTS_FACTOR philosophy one
# level down: perCardMax = ceil(nGroups * PER_CARD_HEAL_FACTOR) + PER_CARD_HEAL_HEADROOM.
PER_CARD_HEAL_BUDGET = True  # --no-per-card-heal-budget disables (restores the unbounded per-card heal)
PER_CARD_HEAL_FACTOR = 1.5   # --per-card-heal-factor=N: heal calls a single card may spend =
                             #  ceil(its group count * this) + headroom. Static h317_w1b budget sizing:
                             #  at the initial conservative 3.0/4, the 12-card window's per-card caps
                             #  summed far above its 61-agent window budget, so the cap redistributed
                             #  spend but still let dense cards push the shared switch. 1.5/3 keeps caps
                             #  near a card's happy-path group count (one call/group) plus one retry or
                             #  bisection allowance; it must still be validated by a live h317_w1b run
                             #  before declaring H442 fixed. e.g. 2 groups -> 6, 5 -> 11, 7 (yuvan) -> 14.
PER_CARD_HEAL_HEADROOM = 3   # additive floor so a 1-2 group card whose group needs a bisection
                             #  (3 attempts + 2 halves) isn't capped below a legitimate heal.
# --- kill-timeout no-bisect guard (H442, 2026-07-10) ------------------------------
# healGroup bisects a group that fails, identically whether the failure was a MALFORMED
# response (soft — a bigger group is genuinely harder, halves may parse) or a KILL-TIMEOUT
# (the call ran past its wall-clock budget). The H442 w1b re-measure isolated that bisecting
# on kill-timeout is often pure waste: when the CALLS are slow (transient infra), each
# bisection just spawns SMALLER fragments that hit the same KILL_FLOOR (45s) and die again —
# e.g. vicitra g1 -> g1/A,g1/B -> g1/A/A,g1/A/B,g1/B/A,g1/B/B, an 11-byte fragment killed at
# 45s (58 of 61 w1b calls were kill-timeouts, 0 clean out of the 4 presplit cards). Therefore
# the first kill-timeout on a heal group routes the unresolved fragments straight to the cheap
# transient requeue instead of recursively spending more heal calls. Soft-failure (malformed)
# bisection is still allowed — only kill-timeout-triggered recursion is blocked.
KILL_TIMEOUT_NO_BISECT = True
# --- harness-size guard (H189 / F-harness-size-limit) -----------------------------
# The emitted harness inlines every card that can reach agent() (TM-resolved and
# degenerate-pass-through rows are self-contained), so its byte size scales with live
# translation payload and CAN exceed the Workflow `scriptPath` cap (the `i` 204-card harness
# = 567 KB > 512 KB, EVOLUTION_TIMELINE F-harness-size-limit; pril10_w1 = 1.03 MB). The
# generator now measures the emitted size and, when it exceeds MAX_HARNESS_BYTES, prints a
# LOUD warning plus a concrete key-disjoint sub-window split (the exact --keys=... for each
# piece) so the limit is surfaced at GENERATION, not discovered at launch. Warn (not hard
# refuse) by default because some large single-root harnesses do launch via other surfaces;
# --refuse-oversize makes it a hard error for unattended/automated callers.
MAX_HARNESS_BYTES = 480000  # ~480 KB, a safety margin under the 512 KB scriptPath cap
REFUSE_OVERSIZE = False     # --refuse-oversize: exit nonzero instead of warning when oversize


def grammar_text(root):
    """Compact, token-light grammar block for the root (Whitney), injected ONCE per run.
    The whole root's sub-cards share its conjugation, so this is far cheaper than a
    per-portrait block. Empty string if the root has no Whitney record (e.g. non-roots)."""
    recs = grammar_for(root)
    if not recs:
        return ''
    lines = ['=== GRAMMAR (Whitney) — the root\'s conjugation; use to inform grammatical '
             'notes and FLAG irregular/defective forms; NEVER let grammar override a corpus- '
             'or German-attested sense ===']
    amb = len(recs) > 1
    for r in recs:
        hom = ('/%s' % r['homonym']) if r['homonym'] else ''
        forms = ', '.join('%s' % f['form'] for f in r['attested_forms'][:6])
        secs = ', '.join('%s §%s' % (k, v) for k, v in list(r['section_refs'].items())[:8])
        lines.append('root %s%s (Whitney no.%s): class %s%s, PPP %s, periods %s'
                     % (r['root_iast'], hom, r['whitney_no'], r['class'],
                        ' [class uncertain]' if r['class_uncertain'] else '', r['ppp'],
                        '/'.join(r['period_tags'])))
        if r['irregularities']:
            lines.append('  irregularities: %s' % '; '.join(r['irregularities']))
        if forms:
            lines.append('  corpus-attested forms: %s' % forms)
        if secs:
            lines.append('  Whitney §§ per form-category: %s' % secs)
    if amb:
        lines.append('(NOTE: %d Whitney homonyms — pick the one matching the sense; '
                     'do not conflate.)' % len(recs))
    return '\n'.join(lines) + '\n\n'


def nominal_grammar_text(slp1, lex):
    """Compact nominal grammar block for a non-root headword, injected once per batch.

    Parallel to grammar_text() for verb roots. Returns an empty string if lex is
    unknown/missing. For compounds, includes MW member segmentation.
    """
    if not slp1 or not lex:
        return ''
    try:
        rec = nominal_grammar_for(slp1, lex)
    except Exception:
        return ''
    lines = ['=== GRAMMAR (Whitney nominal) — the headword\'s declension class and §§; '
             'use to inform grammatical notes and flag irregular forms; '
             'NEVER let grammar override a corpus- or German-attested sense ===']
    lines.append('headword %s [%s]: %s, Whitney %s (paradigm %s)'
                 % (slp1, lex, rec['stem_class'],
                    rec['declension_sections'], rec.get('paradigm_section') or '—'))
    if rec.get('compound_members'):
        lines.append('  compound members (MW k2): %s → %s'
                     % (slp1, ' + '.join(rec['compound_members'])))
        lines.append('  compound formation: %s' % rec['compound_sections'])
    if rec.get('irregularities'):
        lines.append('  flags: %s' % '; '.join(rec['irregularities']))
    lines.append('  derivation ref: %s' % rec['derivation_sections'])
    return '\n'.join(lines) + '\n\n'


def die(msg):
    sys.exit('FAIL: %s' % msg)


def parse_args(argv):
    if not argv:
        die('usage: gen_opt_harness2.py <root> [--keys=..] [--budget=N] [--lean] '
            '[--nominal] [--no-grammar]')
    # budget = bytes (skeleton+portrait) packed per agent call. Higher = fewer agent calls =
    # fewer ~30k-token fixed-framework payments per root (the dominant cost). 12000 measured
    # ~-25% agent calls vs the old 9000 while keeping batches within the tested 13-14-card range;
    # the post-restore fidelity guard nulls any degraded card -> requeue, so it can't silently
    # corrupt. Further bumps (16-18k) are available but should be retry-rate-validated on a Max
    # run first. See TOKEN_LEVER_FINDING_2026-06-30.md (portrait-slim was a non-lever).
    root, keyfilter, budget, lean, nws_gate = argv[0], None, 12000, False, False
    nominal, grammar_on = False, True
    keylist = None                     # ordered keys (nominal mode preserves order)
    out_path = None                    # --out=PATH overrides the default opt2.js (avoids the
    manifest_path = None               # --manifest-out=PATH emits the canonical headless contract
    lang, mw_tm = 'ru', None           # --lang en + --mw-tm=PATH: PWG->English pilot (MG 2026-06-30)
    tm = '__auto__'                    # default auto: use translation_memory.<lang>.json if present;
                                       #  no sidecar = no-op with a loud summary. --no-tm disables.
    suggest_tm = '__auto__'            # suggestion memory: advisory prompt context only
    suggest_profile = 'semantic'       # MG prior: semantic-tag/register channel first
    profile_slot = config_dir = execution_route = executor_lane = validation_method = None
    synthetic_keys = set()
    tm_auto = True
    budget_explicit = output_explicit = False
    for a in argv[1:]:                 # gen->copy race when several chats generate at once)
        if a.startswith('--keys='):
            keylist = [k for k in a.split('=', 1)[1].split(',') if k]
            keyfilter = set(keylist)
        elif a.startswith('--budget='):
            budget = int(a.split('=', 1)[1])
            budget_explicit = True
        elif a.startswith('--out='):
            out_path = a.split('=', 1)[1]
        elif a.startswith('--manifest-out='):
            manifest_path = a.split('=', 1)[1]
        elif a.startswith('--profile-slot='):
            profile_slot = a.split('=', 1)[1]
        elif a.startswith('--config-dir='):
            config_dir = a.split('=', 1)[1]
        elif a.startswith('--execution-route='):
            execution_route = a.split('=', 1)[1]
        elif a.startswith('--executor-lane='):
            executor_lane = a.split('=', 1)[1]
        elif a.startswith('--validation-method='):
            validation_method = a.split('=', 1)[1]
        elif a.startswith('--synthetic-keys='):
            synthetic_keys = {k for k in a.split('=', 1)[1].split(',') if k}
        elif a.startswith('--lang='):
            lang = a.split('=', 1)[1].strip().lower()
        elif a.startswith('--mw-tm='):
            mw_tm = a.split('=', 1)[1]
        elif a == '--tm':
            tm = '__default__'          # resolved to translation_memory.<lang>.json after the loop
            tm_auto = False
        elif a.startswith('--tm='):
            tm = a.split('=', 1)[1]
            tm_auto = (tm == 'auto')
            if tm_auto:
                tm = '__auto__'
        elif a == '--no-tm':
            tm = None
            tm_auto = False
            suggest_tm = None
        elif a == '--suggest-tm':
            suggest_tm = '__default__'
        elif a.startswith('--suggest-tm='):
            suggest_tm = a.split('=', 1)[1]
        elif a.startswith('--suggest-profile='):
            suggest_profile = a.split('=', 1)[1].strip().lower()
        elif a == '--lean':
            lean = True
        elif a == '--nws-gate':
            nws_gate = True
        elif a == '--nominal':
            nominal = True
        elif a == '--no-grammar':
            grammar_on = False
        elif a == '--selfheal':
            globals()['SELFHEAL'] = True     # default since 2026-07-02; kept for documented runbooks
        elif a == '--no-selfheal':
            globals()['SELFHEAL'] = False
        elif a.startswith('--selfheal-budget='):
            globals()['SELFHEAL_GROUP_BUDGET'] = int(a.split('=', 1)[1])
        elif a.startswith('--sense-presplit-budget='):
            v = a.split('=', 1)[1].strip().lower()
            globals()['SENSE_PRESPLIT_BUDGET'] = None if v in ('off', '0', 'none') else int(v)
        elif a.startswith('--presplit-solo-cite-floor='):  # H255/H823: citation-presplit floor so --output-budget=1 doesn't force tiny cards into the heal lane
            globals()['PRESPLIT_SOLO_CITE_FLOOR'] = int(a.split('=', 1)[1])
        elif a == '--no-kill':
            globals()['KILL'] = False
        elif a == '--kill':
            globals()['KILL'] = True         # default; kept for documented runbooks
        elif a.startswith('--kill-factor='):
            globals()['KILL_FACTOR'] = float(a.split('=', 1)[1])
        elif a == '--binary-split':
            globals()['BINARY_SPLIT'] = True # default since 2026-07-02; kept for documented runbooks
        elif a == '--no-binary-split':
            globals()['BINARY_SPLIT'] = False
        elif a.startswith('--output-budget='):
            v = a.split('=', 1)[1].strip().lower()
            globals()['OUTPUT_BUDGET'] = None if v in ('off', '0', 'none') else int(v)
            output_explicit = True
        elif a.startswith('--presplit-group-budget='):   # H189: citation cap per presplit-lane call
            globals()['PRESPLIT_GROUP_CITE_BUDGET'] = int(a.split('=', 1)[1])
        elif a.startswith('--presplit-sense-cap='):       # H189: fragment (sense) cap per call
            globals()['PRESPLIT_GROUP_SENSE_CAP'] = int(a.split('=', 1)[1])
        elif a == '--no-kill-switch':                     # H189: disable the window budget switch
            globals()['KILL_SWITCH'] = False
        elif a == '--kill-switch':
            globals()['KILL_SWITCH'] = True               # default; kept for documented runbooks
        elif a.startswith('--max-agents='):               # H189: absolute agent()-count ceiling override
            globals()['MAX_AGENTS_OVERRIDE'] = int(a.split('=', 1)[1])
        elif a == '--no-per-card-heal-budget':            # H442: disable the per-card heal ceiling
            globals()['PER_CARD_HEAL_BUDGET'] = False
        elif a == '--per-card-heal-budget':
            globals()['PER_CARD_HEAL_BUDGET'] = True       # default; kept for documented runbooks
        elif a.startswith('--per-card-heal-factor='):      # H442: tune the per-card heal-call multiple
            globals()['PER_CARD_HEAL_FACTOR'] = float(a.split('=', 1)[1])
        elif a.startswith('--per-card-heal-headroom='):
            globals()['PER_CARD_HEAL_HEADROOM'] = int(a.split('=', 1)[1])
        elif a == '--refuse-oversize':                    # H189: hard-error instead of warn when oversize
            globals()['REFUSE_OVERSIZE'] = True
        elif a.startswith('--max-harness-bytes='):
            globals()['MAX_HARNESS_BYTES'] = int(a.split('=', 1)[1])
        elif a.startswith('--max-wide='):                 # H255/H811: cap concurrent dispatch units (<=N-wide) for the degraded-API requeue lane
            globals()['MAX_WIDE'] = int(a.split('=', 1)[1])
        elif a.startswith('--stagger-ms='):               # H255/H811: delay between the first MAX_WIDE worker starts (thundering-herd guard)
            globals()['STAGGER_MS'] = int(a.split('=', 1)[1])
    if budget_explicit and not output_explicit:
        # An explicit --budget=N with no --output-budget means the caller wants BYTE-mode
        # batching (backward compat: every pre-2026-07-02 documented invocation that tuned
        # --budget did so under byte semantics — silently reinterpreting it would change
        # every runbook's batch shape).
        globals()['OUTPUT_BUDGET'] = None
    if lang not in ('ru', 'en'):
        die('unknown --lang %r (ru|en)' % lang)
    if lang == 'en' and mw_tm is None:
        mw_tm = os.path.join(SRC, 'mw_en_tm.json')      # default MW translation-memory feed
    if tm in ('__default__', '__auto__'):
        tm = os.path.join(os.path.dirname(INP), 'translation_memory.%s.json' % lang)
    if suggest_tm in ('__default__', '__auto__'):
        suggest_tm = os.path.join(os.path.dirname(INP), 'translation_memory.suggest.%s.jsonl' % lang)
    if suggest_profile not in ('semantic', 'german', 'sanskrit', 'balanced'):
        die('unknown --suggest-profile %r (semantic|german|sanskrit|balanced)' % suggest_profile)
    return (root, keyfilter, keylist, budget, lean, nws_gate, nominal, grammar_on,
            out_path, manifest_path, lang, mw_tm, tm, tm_auto, suggest_tm, suggest_profile,
            profile_slot, config_dir, execution_route, executor_lane, validation_method,
            synthetic_keys)


def extract_nws(tr):
    """Pull HARD RULE 5 (the long NWS owner-map block) out of TR so the JS injects it only
    into NWS-bearing batches. SAFE — does not touch the markup-fidelity rule. (rule3 intact)"""
    nws_m = re.search(r'5\. NWS LAYER.*?(?=\n\nRENDERING GUIDANCE)', tr, re.S)
    if not nws_m:
        die('could not locate HARD RULE 5 (NWS) block')
    nws_block = nws_m.group(0)
    tr2 = tr.replace(nws_block, '5. NWS LAYER — present only for NWS sub-source cards; '
                     'when an NWS owner-map block appears in a card, follow its rule shown there.')
    return tr2, nws_block


def compress_rule3(tr):
    """Compress HARD RULE 3 (markup-verbatim) to a {Tn}-verbatim line. REJECTED by the A/B
    (regressed markup fidelity — AB_TEST_LEAN_TR.md); kept only behind --lean for the record."""
    tr2, n = re.subn(
        r'3\. SIGLA UNTOUCHED.*?(?=\n4\. ALL RECORDS)',
        '3. KEEP {Tn} VERBATIM — every untranslatable span (Sanskrit, sigla, abbreviations) is '
        'masked as a {Tn} placeholder; keep every {Tn} unchanged and in its original order, and '
        'never type any Sanskrit, siglum, or markup yourself (Python restores them).\n',
        tr, count=1, flags=re.S)
    if n != 1:
        die('could not compress HARD RULE 3 (markup-verbatim) block')
    return tr2


def _group_by_budget(items, sizer, budget, count_cap=None):
    """Greedily group `items` (kept in order) into batches whose summed sizer() stays
    <= budget; a single oversize item still gets its own group (never dropped).

    count_cap (H189): when set, also close a group once it already holds count_cap
    items, regardless of summed size — so a run of many tiny (size-1) items can't pack
    an unbounded COUNT into one group. Needed for the presplit fragment lane, where the
    item count == senses the model must emit and a group of 40 size-1 fragments would
    re-trigger the very sense-density failure presplit exists to avoid. Default None
    preserves the original size-only behavior for every existing caller.
    """
    groups, cur, sz = [], [], 0
    for it in items:
        isz = sizer(it)
        if cur and (sz + isz > budget or (count_cap and len(cur) >= count_cap)):
            groups.append(cur); cur, sz = [], 0
        cur.append(it); sz += isz
    if cur:
        groups.append(cur)
    return groups


def _presplit_hit(ls, nfrag, cite_budget):
    """Shared predicate: does a card's CITATION density (1+<ls> over the output budget)
    or SENSE density (fragment count over SENSE_PRESPLIT_BUDGET) route it to the
    presplit-primary fragment lane? Returns (cite_hit, sense_hit). Kept in one place so
    the frags-loop grouping choice and the presplit-list construction can never drift
    (H189 — before this, the two sites replicated the condition independently)."""
    # Floor the citation trigger at PRESPLIT_SOLO_CITE_FLOOR so --output-budget=1 (no-PWG lane)
    # doesn't force every citation-bearing card into the heal lane — only genuine fail-solo
    # citation giants presplit. For OUTPUT_BUDGET >= the floor (default 90) this is a no-op.
    cite_hit = cite_budget is not None and (1 + ls) > max(cite_budget, PRESPLIT_SOLO_CITE_FLOOR)
    sense_hit = SENSE_PRESPLIT_BUDGET is not None and nfrag > SENSE_PRESPLIT_BUDGET
    return cite_hit, sense_hit


def selected_keys(root, keyfilter):
    path, _ = rootmap_path(root)
    if not path:
        die('no rootmap for %r' % root)
    keys = [s['subkey'] for s in (load_json(path).get('sub_cards') or [])]
    if keyfilter:
        keys = [k for k in keys if k in keyfilter or k.split('~~')[-1] in keyfilter]
        if not keys:
            die('no sub-cards matched --keys')
    return path, keys


# POS priority shared with enrich_portrait_nominal_grammar (prefer concrete gender).
_GENDER_PRIORITY = ('m.', 'f.', 'n.', 'm.n.', 'm.f.', 'f.n.', 'm.f.n.',
                    'adj.', 'adv.', 'indecl.', 'ind.', 'interj.')


def _slp1_lex_for_key(k):
    """Read (SLP1 key1, lex tag) from a card's portrait JSON.

    The card key `k` is a safe-name FILE stem (input files are stored under
    safe_name(SLP1); input_paths uses the literal stem). The true SLP1 — needed
    for the compound join and the grammar display — is the portrait's `key1`
    field, NOT the mangled stem. Returns ('', '') if the portrait is unreadable.
    """
    _, pp = input_paths(k)
    try:
        port = load_json(pp)
    except Exception:
        return '', ''
    e = port[0] if isinstance(port, list) and port else port
    if not isinstance(e, dict):   # empty-list portrait ([]) or unexpected shape -> no grammar key
        return '', ''             # (the real tyaj~~h0_zz_pw / addenda shape; keymap falls back to k)
    slp1 = e.get('key1') or e.get('slp1') or ''
    val = e.get('lex') or e.get('pos') or e.get('gender') or ''
    if isinstance(val, (list, tuple)):
        tags = [str(t).strip() for t in val if str(t).strip()]
        lex = next((g for g in _GENDER_PRIORITY if g in tags), tags[0] if tags else '')
    else:
        lex = str(val).strip()
    return slp1, lex


def _card_grammar_text(k):
    """Per-card nominal grammar block, keyed by the portrait's true SLP1 (key1)."""
    slp1, lex = _slp1_lex_for_key(k)
    return nominal_grammar_text(slp1, lex)


def extract_conv_tr():
    src = read_text(os.path.join(REPO, 'src', 'pilot', 'run_pilot_wf.js'))
    m = re.search(r'const TR = `(.*?)`\n', src, re.S)
    if not m:
        die('could not extract TR block from run_pilot_wf.js')
    return m.group(1)  # TR already embeds ${CONV}; we resolve CONV below


def conv_text():
    src = read_text(os.path.join(REPO, 'src', 'pilot', 'run_pilot_wf.js'))
    m = re.search(r'const CONV = `(.*?)`\n', src, re.S)
    if not m:
        die('could not extract CONV block')
    return m.group(1)


MASK_PREAMBLE = """=== MASKED + BATCHED REGIME (read first — overrides input-format details below) ===
You are given SEVERAL headwords at once, each in its own '=== CARD <key> ===' block.
Each card's source German has been MASKED: every untranslatable span (Sanskrit {#..#},
source refs <ls>, abbreviations <ab>, italic <is>, grammar <lex>) is replaced by a {Tn}
placeholder token. You see ONLY the translatable German gloss prose + {Tn} tokens + the
sense numbering. A Python post-step restores every {Tn} to its exact original markup.

Therefore, wherever the rules below say "keep {#..#}/<ls>/<ab> verbatim" or "reproduce
the markup delimiters EXACTLY", that now means: **keep every {Tn} placeholder verbatim,
unchanged and in its original order** — never invent, renumber, drop, expand, merge, or
alter a {Tn}, and never type any Sanskrit, siglum, or markup yourself. In the `german`
field, reproduce the masked skeleton you were given for that sense EXACTLY (its German +
its {Tn} tokens). In the `russian` field, put your translation, placing the relevant {Tn}
tokens where the source cited a masked span. Translate EACH card; return one object per
headword in `cards`, with `key1` matching its '=== CARD <key> ===' header. Omit nothing.

"""


def _rename_sense_field(schema, old, new):
    """Deep-copy the card schema with the per-sense translation field renamed (russian->
    english) wherever it appears in `properties` / `required`. Used for the --lang en path."""
    import copy
    s = copy.deepcopy(schema)

    def walk(d):
        if isinstance(d, dict):
            props = d.get('properties')
            if isinstance(props, dict) and old in props:
                props[new] = props.pop(old)
            req = d.get('required')
            if isinstance(req, list) and old in req:
                d['required'] = [new if x == old else x for x in req]
            for v in d.values():
                walk(v)
        elif isinstance(d, list):
            for x in d:
                walk(x)
    walk(s)
    return s


def _ref_names(node):
    """$ref targets ('#/$defs/name' -> 'name') found anywhere under `node`."""
    names = []
    if isinstance(node, dict):
        ref = node.get('$ref')
        if isinstance(ref, str) and ref.startswith('#/$defs/'):
            names.append(ref[len('#/$defs/'):])
        for v in node.values():
            names.extend(_ref_names(v))
    elif isinstance(node, list):
        for v in node:
            names.extend(_ref_names(v))
    return names


def _reachable_defs(defs, start):
    """Subset of `defs` transitively reachable via $ref from `start`.

    pwg_ru_final_card.schema.json is shared with the judge step, so its $defs
    also carry judge/judge_issue. The translate-only CARDS_SCHEMA never
    references them (its root is 'card', not the judge-report wrapper) — left
    in, they were dead weight that pushed the per-call StructuredOutput schema
    over the Workflow tool's safety-classifier size threshold, blocking every
    agent() call before any model invocation (0 tokens spent, confirmed via
    isolated schema-only tests 2026-07-03).
    """
    seen, stack = set(), [start]
    while stack:
        name = stack.pop()
        if name in seen or name not in defs:
            continue
        seen.add(name)
        stack.extend(_ref_names(defs[name]))
    return {k: v for k, v in defs.items() if k in seen}


# Fields present on the final card/sense/record schema but added AFTER generation, by a
# deterministic annotator script — never by the translating model. Keeping them in the
# per-call StructuredOutput schema only adds dead weight: H428 measured the full reachable
# schema (post-H335/H405/H422 growth) at 10,940 chars, over the Workflow tool's safety-
# classifier size threshold (every agent() call blocked pre-generation, 0 tokens, H388/H389).
# Stripping these from the *generation* schema only — the promote/annotate scripts below
# still add them back onto the promoted card from the unmodified schema file on disk.
_POST_GENERATION_SENSE_FIELDS = (
    'government',       # annotate_government.py / government_census.py (H335 W3)
    'labels',            # planned diasystem-label annotator (Dimension 2); no generation-time
                         # prompt or annotator currently populates it either, but it is not
                         # model-generated, so it does not belong in the generation schema
    'renou', 'renou_oldest',  # annotate_renou.py
    'evidence',          # annotate_evidence.py
)
_POST_GENERATION_RECORD_FIELDS = (
    'renou_oldest_sense',  # annotate_renou.py
)
_POST_GENERATION_CARD_FIELDS = (
    'evidence_summary',  # annotate_evidence.py
    'stats',             # annotate_stats.py
)


def _strip_post_generation_fields(defs):
    """Deep-copy `defs` with every post-generation-added field removed from `properties`
    (and `required`, though none of them are required today). See H428 /
    Uprava/FINDINGS.md §30."""
    import copy
    defs = copy.deepcopy(defs)
    for def_name, fields in (
        ('card', _POST_GENERATION_CARD_FIELDS),
        ('record', _POST_GENERATION_RECORD_FIELDS),
        ('sense', _POST_GENERATION_SENSE_FIELDS),
    ):
        node = defs.get(def_name)
        if not node:
            continue
        props = node.get('properties', {})
        for f in fields:
            props.pop(f, None)
        req = node.get('required')
        if isinstance(req, list):
            node['required'] = [r for r in req if r not in fields]
    return defs


def mw_tm_block(root, mw_tm_path):
    """The MW English translation-memory block injected once per root (en pilot). '' if none."""
    if not mw_tm_path or not os.path.exists(mw_tm_path):
        return ''
    tm = load_json(mw_tm_path).get(root)
    if not tm:
        return ''
    return ('=== MW REFERENCE (English translation memory — Monier-Williams\' own glosses for '
            'this root; TERMINOLOGY CROSS-CHECK ONLY: candidate vocabulary to confirm the WORDING '
            'of a sense the German already attests. ADJUDICATE against the German + corpus, follow '
            'PWG\'s sense order, do not copy blindly. NEVER copy an MW phrase, parenthetical, or '
            'sense into the English unless the German licenses it — if MW has detail the German '
            'lacks (e.g. a domain note "(as heavenly bodies)"), OMIT it) ===\n%s\n\n' % tm)


_DEGENERATE_WORDS = {
    's', 'siehe', 's.', 'vgl', 'vgl.', 'vergl', 'vergl.', 'u', 'und',
    'ff', 'fgg', 'fg', 'fg.', 'fgg.', 'nachtrage', 'nachträge',
}
_DEGENERATE_CORRECTION_RE = re.compile(r'\b(lies|lesen|streichen)\b', re.I)


def _portrait_key_iast(portrait_text, key):
    try:
        p = json.loads(portrait_text)
    except Exception:
        return key
    rows = p if isinstance(p, list) else [p]
    for row in rows:
        if isinstance(row, dict):
            return row.get('iast') or row.get('key1') or key
    return key


def _portrait_source_profile(portrait_text):
    """The `source_profile` a portrait declares (H214: 'no_pwg_supplement_chain'), or None
    for an ordinary PWG-rooted portrait. This is the AUTHORITATIVE no-PWG signal — only a
    truly PWG-less headword's portrait carries it — so it disambiguates a no-PWG supplement
    card from a PWG root-split supplement sub-card whose raw looks identical."""
    try:
        rows = json.loads(portrait_text)
    except Exception:
        return None
    rows = rows if isinstance(rows, list) else [rows]
    for r in rows:
        if isinstance(r, dict) and r.get('source_profile'):
            return r.get('source_profile')
    return None


# A supplement LAYER marker in a raw card (PW / SCH / PWKVN / NWS). The trailing space after
# "PW" is load-bearing: it matches "PW — …" but NOT "PWG …" (PWG has no space) or "PWKVN …".
_SUPP_LAYER_RE = re.compile(r'=== LAYER: (?:PW |SCH|PWKVN|NWS)')


def card_source_profile(raw, portrait_text=None):
    """H214 per-card source-material profile, stamped on every promoted row:

      'no_pwg_supplement_chain' — no PWG layer AND the headword has no PWG base (portrait-flagged)
      'pwg_with_supplements'    — ONE card carrying BOTH a PWG layer and >=1 supplement layer
                                  (the MIXED whole-card shape from gen_card — filter for this to
                                  find all mixed cards)
      'pwg_only'                — only PWG layer(s) (pure base card / root-split head sub-card)
      'pwg_supplement_subcard'  — a supplement-only sub-card of a PWG root-split headword (its
                                  headword DOES have a PWG base elsewhere, so it is NOT no-PWG)

    Returns None when the raw carries no LAYER markers (degenerate/unknown). The portrait's
    explicit no-PWG flag wins first, so a root-split supplement sub-card (empty portrait) is
    never mis-tagged as no-PWG."""
    if _portrait_source_profile(portrait_text) == 'no_pwg_supplement_chain':
        return 'no_pwg_supplement_chain'
    has_pwg = '=== LAYER: PWG' in raw
    has_supp = bool(_SUPP_LAYER_RE.search(raw))
    if has_pwg and has_supp:
        return 'pwg_with_supplements'
    if has_pwg:
        return 'pwg_only'
    if has_supp:
        return 'pwg_supplement_subcard'
    return None


def degenerate_passthrough_card(key, raw, portrait_text, field='russian'):
    """Conservative no-LLM lane for cross-reference/supplement stubs.

    These cards contain citation/reference markup but no German gloss prose to translate.
    False negatives are fine (normal harness handles them); false positives are not, so the
    classifier intentionally admits only tiny non-gloss stubs with no gloss blocks or senses.
    """
    if not raw or len(raw) > 900:
        return None
    if '{%' in raw or '<div' in raw or re.search(r'\b\d+\)', raw):
        return None
    if not (re.search(r'\{#[^}]+#\}', raw) or '<ls' in raw or '<ab>' in raw):
        return None
    body = re.sub(r'^=== LAYER:.*?===\s*', '', raw, flags=re.S).strip()
    if not body:
        return None
    if _DEGENERATE_CORRECTION_RE.search(body):
        return None
    probe = re.sub(r'\{#[^}]*#\}', ' ', body)
    probe = re.sub(r'\{%[^}]*%\}', ' ', probe)
    probe = re.sub(r'<[^>]+>', ' ', probe)
    probe = re.sub(r'\[[^\]]+\]', ' ', probe)
    words = [w.lower().strip('.:,;()') for w in re.findall(r'[A-Za-zÄÖÜäöüß]+\.?', probe)]
    words = [w for w in words if w]
    norm = [w.replace('ä', 'a').replace('ö', 'o').replace('ü', 'u').replace('ß', 'ss')
            for w in words]
    if len(words) > 8 or any((w not in _DEGENERATE_WORDS and n not in _DEGENERATE_WORDS)
                             for w, n in zip(words, norm)):
        return None
    sense = {
        'tag': 'xref',
        'german': body,
        field: body,
        'equivalence_type': 'explanatory',
        'source_type': 'lexicographic',
        'stratum': '',
        'differentia': 'Deterministic pass-through: cross-reference stub with no translatable gloss.',
    }
    return {
        'key1': key,
        'iast': _portrait_key_iast(portrait_text, key),
        'records': [{'h': None, 'senses': [sense]}],
        'notes': '',
        'degenerate_passthrough': True,
    }


def tm_card_sane(card, lang, field, raw):
    """Cheap guard before exact TM auto-serve. The source SHA does the hard compatibility work;
    this catches malformed/legacy sidecar rows before they become zero-token output."""
    if not isinstance(card, dict):
        return False, 'card is not an object'
    if not card.get('records'):
        return False, 'card has no records'
    n_senses = 0
    for rec in card.get('records') or []:
        for s in rec.get('senses') or []:
            n_senses += 1
            if not (s.get(field) or '').strip():
                return False, 'sense missing %s' % field
    if not n_senses:
        return False, 'card has no senses'
    ls = sum(((s.get('german') or '').count('<ls') for rec in card.get('records') or []
              for s in rec.get('senses') or []))
    sk = sum(((s.get('german') or '').count('{#') for rec in card.get('records') or []
              for s in rec.get('senses') or []))
    if ls != raw.count('<ls'):
        return False, '<ls> count drift'
    if sk != raw.count('{#'):
        return False, '{# count drift'
    return True, ''


def tm_senses_sane(senses, field):
    if not senses:
        return False
    for s in senses:
        if not isinstance(s, dict) or not (s.get(field) or '').strip():
            return False
    return True


def build(root, keys, rootmap, budget, lean=False, nws_gate=False,
          nominal=False, grammar_on=True, lang='ru', mw_tm_path=None, tm_path=None,
          tm_auto=False, suggest_tm_path=None, suggest_profile='semantic',
          return_manifest=False, profile_slot=None, config_dir=None,
          execution_route=None, executor_lane=None, validation_method=None,
          synthetic_keys=None):
    field = 'english' if lang == 'en' else 'russian'   # the per-sense translation field
    nws_block = ''
    if lang == 'en':
        # PWG->English pilot: a self-contained EN prompt (tr_en.txt). The masked-inline
        # regime + field mechanics are carried by MASK_PREAMBLE (no file-reading block to
        # neutralize, no lean/nws variants — full mode only).
        tr = read_text(os.path.join(REPO, 'src', 'pilot', 'tr_en.txt'))
    else:
        conv = conv_text()
        tr = extract_conv_tr().replace('${CONV}', conv)
        # CRITICAL: the production TR tells the model "INPUTS for headword KEY (read both):
        # KEYFILE.raw.txt / .portrait.json" — i.e. to READ files. In the masked-inline regime
        # that makes the model call file tools and list the input dir (the yuj retry/cost blowup,
        # 2026-06-29). Strip it so the only inputs are the inlined masked cards.
        tr, n = re.subn(
            r'INPUTS for headword KEY \(read both\):.*?\.portrait\.json[^\n]*',
            'INPUTS for each headword are INLINED below per card (its masked German skeleton + '
            'portrait). Do NOT open files, do NOT call any tools, do NOT list directories, do NOT '
            'supply senses from memory — translate EXACTLY what is inlined, nothing else.',
            tr, count=1, flags=re.S)
        if n != 1:
            die('could not neutralize the TR file-reading block (expected 1 match, got %d)' % n)
        # A/B variants. --nws-gate: safe (rule 3 kept, only NWS gated). --lean: also compresses
        # rule 3 (REJECTED — regressed fidelity; kept for the record only).
        if lean:
            tr = compress_rule3(tr)
            tr, nws_block = extract_nws(tr)
        elif nws_gate:
            tr, nws_block = extract_nws(tr)
    schema = load_json(os.path.join(REPO, 'schemas', 'pwg_ru_final_card.schema.json'))
    if field != 'russian':
        schema = _rename_sense_field(schema, 'russian', field)
    # BOTH EN and RU paths: keep only the essential per-sense fields required (tag +
    # source german + the translation). The 4 annotator fields (equivalence_type,
    # source_type, stratum, differentia) become optional. On the citation-dense
    # main-head pwg cards, requiring all 7 fields (2 of them enums) per sense —
    # dozens of senses per card — is a huge structured-output surface where one
    # truncated/mismatched field invalidates the whole card and burns the
    # StructuredOutput retry cap (this recovered many dense heads on the EN run).
    # The annotator fields stay best-effort (the model still fills them on most
    # cards; they are re-derivable downstream). validate_final_card_schema.py was
    # relaxed to match, so RU cards with a missing annotator field still validate.
    schema['$defs']['sense']['required'] = ['tag', 'german', field]
    defs = _strip_post_generation_fields(schema['$defs'])
    defs = _reachable_defs(defs, 'card')
    card_ref = {'$ref': '#/$defs/card'}
    batch_schema = {
        'type': 'object', 'additionalProperties': False, 'required': ['cards'],
        'properties': {'cards': {'type': 'array', 'minItems': 1, 'items': card_ref}},
        '$defs': defs,
    }

    inputs, phmaps, input_hashes, raws, portraits = {}, {}, {}, {}, {}
    for k in keys:
        rp, pp = input_paths(k)
        if not (os.path.exists(rp) and os.path.exists(pp)):
            die('missing input for %s' % k)
        raw = read_text(rp)
        portrait = read_text(pp)
        skel, ph, _ = pwg_mask.mask(raw)
        if pwg_mask.restore(skel, ph) != raw:
            die('mask round-trip not lossless for %s' % k)
        inputs[k] = {'skeleton': skel, 'portrait': portrait,
                     'ls': raw.count('<ls'), 'sk': raw.count('{#'),
                     'senses': raw.count('〉'),  # '〉' sense-delimiter count — coarse
                                                     # output-complexity signal for the kill budget
                     # H960: deterministic distinct top-level source-sense count (cross-reference
                     # hardened; see sense_count._OPEN_PREFIX). Consumed by accept()'s SAN-LOSS
                     # shortfall telemetry — distinct from the coarse 'senses' kill-budget signal.
                     'source_senses': count_source_senses(raw),
                     'nws': 1 if 'NWS' in raw else 0}
        raws[k] = raw
        portraits[k] = portrait
        phmaps[k] = ph
        input_hashes[k] = {'raw_sha256': sha256_file(rp), 'portrait_sha256': sha256_file(pp)}

    # --tm: content-addressed pre-resolution. A card whose masked-input SHA is already in the
    # translation memory is served from cache (ZERO agent() calls) instead of re-translated —
    # no manual --keys scoping needed. Keyed on input_raw_sha256 (recorded per store row,
    # recomputed here), so it survives sub-card key renames and can NEVER reuse a stale
    # translation (changed source -> different SHA -> cache miss -> re-translate). TM-hit keys
    # are removed from every translate lane below (batches / presplit / selfheal frags).
    tm_resolved = {}
    if tm_path and os.path.exists(tm_path):
        import translation_memory as _tm
        cache = _tm.load_tm(lang, tm_path)
        for k in keys:
            hit = cache.get('%s:%s' % (lang, input_hashes[k]['raw_sha256']))
            if hit:
                ok, why = tm_card_sane(hit.get('card'), lang, field, raws[k])
                if not ok:
                    print('  tm: refusing cached %s (%s)' % (k, why))
                    continue
                tm_resolved[k] = hit['card']
        print('  tm: %d/%d cards pre-resolved from %s (0 tokens)%s'
              % (len(tm_resolved), len(keys), os.path.basename(tm_path),
                 '' if tm_resolved else ' — no source-SHA matches (all cards will translate)'))
    elif tm_path:
        print('  tm: %s not found — no pre-resolution (run translation_memory.py build)' % tm_path)
    tm_keys = set(tm_resolved)

    suggest_tm = {}
    if suggest_tm_path and os.path.exists(suggest_tm_path):
        import translation_memory as _tm
        all_suggestions = _tm.load_ranked_suggestions(lang, suggest_tm_path,
                                                      profile=suggest_profile, limit=5)
        for k in keys:
            root_key = k.split('~~', 1)[0]
            rows = (all_suggestions.get(k) or []) + (all_suggestions.get(root_key) or [])
            if rows:
                suggest_tm[k] = _tm.rank_suggestions(rows, profile=suggest_profile, limit=5)
        if suggest_tm:
            print('  suggest-tm: %d card(s) carry advisory suggestion(s) from %s (profile=%s)'
                  % (len(suggest_tm), os.path.basename(suggest_tm_path), suggest_profile))

    degenerate_resolved = {}
    for k in keys:
        if k in tm_keys:
            continue
        card = degenerate_passthrough_card(k, raws[k], portraits[k], field)
        if card:
            degenerate_resolved[k] = card
    degenerate_keys = set(degenerate_resolved)
    if degenerate_keys:
        print('  degenerate: %d/%d cross-reference stub(s) accounted with no LLM: %s'
              % (len(degenerate_keys), len(keys), ','.join(sorted(degenerate_keys))))

    # --selfheal: precompute a per-card fragment fallback (deterministic sense/citation split).
    # The JS uses it only for cards the batch could not translate; each fragment is masked here
    # so the in-harness path reuses the same {Tn} restore. Only cards that actually split (>=2
    # fragments) get a fallback; unsplittable cards fall through (the batch retry already tried).
    # Fragments are then GROUPED (by masked-skeleton bytes, document order preserved) into
    # SELFHEAL_GROUP_BUDGET-sized batches, so the JS heal issues one agent() call per GROUP
    # instead of per fragment (a 13-fragment card was costing 13 calls / ~2.2M tok; grouping
    # amortizes the ~30k fixed system-prompt overhead across several fragments per call).
    # --tm fragment reuse: alongside the whole-card cache above, load the per-fragment
    # sidecar. Each deterministic plan() fragment is content-addressed (its exact chunk
    # text, header included — see translation_memory.frag_address); a cached fragment is
    # served WITHOUT an agent() call inside selfHeal, so a partially-failed giant card
    # re-runs only its still-missing fragments (and a fragment shared byte-for-byte across
    # a root and its derived noun is reused). Enabled by the same --tm switch; a missing
    # sidecar is simply a no-op (all fragments translate as before).
    frag_cache, frag_file = {}, None
    if tm_path:
        import translation_memory as _tm
        frag_file = os.path.join(os.path.dirname(tm_path),
                                 os.path.basename(_tm.frag_tm_path(lang)))
        frag_cache = _tm.load_frag_tm(lang, frag_file)
        if frag_cache:
            print('  frag-tm: %d cached fragment(s) available from %s'
                  % (len(frag_cache), os.path.basename(frag_file)))

    frags, phf, frag_tm, frag_n = {}, {}, {}, {}
    if SELFHEAL:
        import translation_memory as _tm
        for k in keys:
            if k in tm_keys or k in degenerate_keys:  # cached/pass-through whole card — no heal fallback needed
                continue
            pl = split_plan(read_text(input_paths(k)[0]))
            if len(pl) < 2:
                print('  selfheal: %s has no fallback (card does not split — <2 fragments)' % k)
                continue
            fl = []
            for si, _pi, t in pl:
                fsk, fph, _ = pwg_mask.mask(t)
                if pwg_mask.restore(fsk, fph) != t:
                    fl = []
                    # loud, not silent: the card will have NO heal fallback at run time,
                    # so a batch failure on it is unrecoverable in-harness
                    print('  selfheal: %s fallback DROPPED (fragment mask round-trip lossy)' % k)
                    break
                fsha = _tm.frag_address(lang, t)
                cached = frag_cache.get(fsha)
                if cached and not tm_senses_sane(cached.get('senses'), field):
                    print('  frag-tm: refusing cached fragment for %s (%s)' % (k, fsha[:12]))
                    cached = None
                # si (sense_ord from split_plan) travels with the fragment into FRAGS so the
                # JS heal path can tell "these fragments are all citation-batches of the SAME
                # source sense" apart from "these are genuinely different senses" — without it,
                # the model tags each fragment independently and fabricates fresh incrementing
                # tags for citation continuations that carry no sense-boundary marker of their
                # own (see PIPELINE_HISTORY.md fragment-tag-collision entry).
                fl.append({'skeleton': fsk, 'ls': t.count('<ls'), 'sk': t.count('{#'),
                           'ph': fph, 'fsha': fsha, 'si': si,
                           'tm': cached.get('senses') if cached else None})
            if not fl:
                continue
            frag_n[k] = len(pl)   # raw deterministic fragment count == sense-units the model
                                  # must emit; drives the sense-density presplit trigger below
            # H189: a card that WILL be routed to presplit uses the fragment lane as its
            # PRIMARY path (no whole-card attempt), so group it at a budget close to the
            # proven-safe whole-card ceiling — the ~27k framework then amortizes across many
            # fragments per call instead of ~2-3. A card without a presplit hit keeps the
            # conservative SELFHEAL_GROUP_BUDGET (it only reaches these groups via the
            # heal-of-a-failed-whole-card path, where small safe groups matter more).
            _cite_hit, _sense_hit = _presplit_hit(inputs[k]['ls'], frag_n[k], OUTPUT_BUDGET)
            if _cite_hit or _sense_hit:
                groups = _group_by_budget(fl, lambda it: 1 + it['ls'],
                                          PRESPLIT_GROUP_CITE_BUDGET,
                                          count_cap=PRESPLIT_GROUP_SENSE_CAP)
            else:
                groups = _group_by_budget(fl, lambda it: 1 + it['ls'], SELFHEAL_GROUP_BUDGET)
            frags[k] = [[{'skeleton': it['skeleton'], 'ls': it['ls'], 'sk': it['sk'],
                          'fsha': it['fsha'], 'si': it['si']} for it in g] for g in groups]
            phf[k] = [[it['ph'] for it in g] for g in groups]
            # FRAG_TM[k]: same group shape, each slot = cached restored senses or null.
            # Only emitted when this card has at least one cached fragment (keeps the JS lean
            # and lets the summary count reuse). A fully-cached card heals at ZERO agent calls.
            gview = [[it['tm'] for it in g] for g in groups]
            if any(slot for grp in gview for slot in grp):
                frag_tm[k] = gview

    # Pre-split router (MG decision 2026-07-02): a card whose output complexity alone is
    # near-certain to blow the StructuredOutput retry cap as a whole card is routed STRAIGHT to
    # the proven selfheal fragment path at run time instead of letting it fail first (every one
    # of those up-to-5 retries + the binary-split cascade is paid-for waste). TWO orthogonal
    # triggers, because two independent things drive whole-card failure:
    #   (a) CITATION density — 1 + <ls> exceeds the whole per-batch output budget (the 125-150
    #       <ls> pwg00 heads failed even solo — HANDOFF_2026-07-01_pwg_en_fu1_finalize.md).
    #   (b) SENSE density — the deterministic fragment count (== sense-objects the model must
    #       emit) exceeds SENSE_PRESPLIT_BUDGET. A PW addenda card can pack ~35 senses into ~11
    #       <ls>, so (a) sees weight 12 and waves it through while its real output surface is the
    #       heaviest of the root — the tyaj~~h0_zz_pw stall (H155, 2026-07-04). Independent of
    #       byte/citation batching mode: a sense-dense card fails whole regardless of how the
    #       OTHER cards are batched.
    # Only cards with a usable fragment fallback are routed; unsplittable ones keep the old
    # solo-batch try.
    presplit = []
    if SELFHEAL:
        cite_budget = OUTPUT_BUDGET  # None in byte mode -> citation trigger off, sense trigger stays
        for k in keys:
            if k in tm_keys or k in degenerate_keys or k not in frags:
                continue
            cite_hit, sense_hit = _presplit_hit(inputs[k]['ls'], frag_n.get(k, 0), cite_budget)
            if not (cite_hit or sense_hit):
                continue
            presplit.append(k)
            why = []
            if cite_hit:
                why.append('%d <ls> exceeds output budget %d' % (inputs[k]['ls'], cite_budget))
            if sense_hit:
                why.append('%d senses/fragments exceed sense budget %d'
                           % (frag_n[k], SENSE_PRESPLIT_BUDGET))
            print('  presplit: %s (%s) -> direct fragment translation' % (k, '; '.join(why)))
    batch_keys = [k for k in keys if k not in presplit and k not in tm_keys and k not in degenerate_keys]

    # --output-budget=N (default 60): size batches by citation-weighted OUTPUT complexity
    # (1 + <ls> per card) instead of input bytes — bytes don't predict StructuredOutput
    # failure (a dense card's masked bytes can be small while its sense/citation count is
    # what blows the retry cap). Byte mode (explicit --budget=N / --output-budget=off)
    # keeps the original input-byte behavior.
    #
    # Fallback isolation (2026-07-04, collateral-null fix): a card with NO selfheal fallback
    # (split_plan() < 2 fragments, or a lossy fragment mask — see the `frags` loop above)
    # has zero recovery if its batch hard-fails the retry cap. Left mixed into ordinary
    # batches, such a card's survival depends entirely on which OTHER cards happen to share
    # its batch — a dense card WITH a fallback can blow the whole-batch retry cap, and the
    # small no-fallback card goes down with it for reasons unrelated to its own content
    # (observed 2026-07-04 vid run: 10/10 null cards traced to 2 batches that hard-failed,
    # every null a no-fallback card in one of them). Group no-fallback keys into their OWN
    # batch(es), separate from fallback-having keys, so a batch-wide hard failure never takes
    # down an unrelated card that had nothing to do with causing it. A no-fallback batch can
    # still fail on its own content, but that failure is then attributable to itself, not to
    # a neighbor.
    if SELFHEAL:
        fallback_keys = [k for k in batch_keys if k in frags]
        no_fallback_keys = [k for k in batch_keys if k not in frags]
    else:
        fallback_keys, no_fallback_keys = batch_keys, []
    if OUTPUT_BUDGET is not None:
        sizer = lambda k: 1 + inputs[k]['ls']
        budget_n = OUTPUT_BUDGET
    else:
        sizer = lambda k: len(inputs[k]['skeleton']) + len(inputs[k]['portrait'])
        budget_n = budget
    batches = (_group_by_budget(fallback_keys, sizer, budget_n)
               + _group_by_budget(no_fallback_keys, sizer, budget_n))
    if no_fallback_keys:
        print('  fallback-isolation: %d no-selfheal-fallback card(s) routed to %d dedicated batch(es), '
              'separate from %d fallback-having card(s)'
              % (len(no_fallback_keys), len(_group_by_budget(no_fallback_keys, sizer, budget_n)),
                 len(fallback_keys)))

    # Grammar injection. Root mode: one shared GRAMMAR block (the root conjugation,
    # identical across sub-cards) before CONV_TR; GRAMMARS empty. Nominal mode: each
    # headword has its OWN block (distinct stem class / compound members), so inject
    # PER CARD via GRAMMARS and leave the shared block empty. --no-grammar = arm A.
    if nominal:
        single_grammar = ''
        grammars = {k: _card_grammar_text(k) for k in keys} if grammar_on else {}
    else:
        single_grammar = grammar_text(root) if grammar_on else ''
        grammars = {}
    if lang == 'en':                                    # inject MW TM once per root (root mode)
        single_grammar = mw_tm_block(root, mw_tm_path) + single_grammar

    # Preflight-parity agent estimate (one call per batch + one per presplit fragment group).
    # The runtime budget is planned separately: whole-card translation/binary-split calls use
    # the translate pool; every selfheal-capable card contributes its own bounded ceiling to
    # the recovery pool. This removes the H442/H462 shared-counter starvation class.
    agent_expected = len(batches) + sum(len(frags.get(k, [None])) for k in presplit)
    runtime_keys = set(batch_keys) | set(presplit)
    runtime_inputs = {k: inputs[k] for k in keys if k in runtime_keys}
    runtime_phmaps = {k: phmaps[k] for k in keys if k in runtime_keys}
    runtime_suggest_tm = {k: v for k, v in suggest_tm.items() if k in runtime_keys}
    budget_plan = derive_agent_budget(
        len(batches),
        {k: len(v) for k, v in frags.items() if v},
        enabled=KILL_SWITCH,
        translate_factor=MAX_AGENTS_FACTOR,
        translate_headroom=MAX_AGENTS_HEADROOM,
        per_card_heal_budget=bool(PER_CARD_HEAL_BUDGET and SELFHEAL),
        per_card_heal_factor=PER_CARD_HEAL_FACTOR,
        per_card_heal_headroom=PER_CARD_HEAL_HEADROOM,
        max_agents_override=MAX_AGENTS_OVERRIDE,
    )

    # H214: per-card source-material profile, stamped on promoted rows via
    # meta.source_profiles (promote_final_cards.provenance reads it per sub-card). Window-level
    # meta.source_profile intentionally stays narrow for compatibility with the H214 contract:
    # only an all-no-PWG window is marked; ordinary/mixed PWG windows remain null.
    source_profiles = {k: card_source_profile(raws.get(k, ''), portraits.get(k)) for k in keys}
    _distinct = {p for p in source_profiles.values() if p}
    source_profile = 'no_pwg_supplement_chain' if _distinct == {'no_pwg_supplement_chain'} else None

    meta = {
        'schema_version': 'pwg_ru.workflow_meta.v1', 'generator': 'gen_opt_harness2.batched-masked',
        'generated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(
            timespec='seconds').replace('+00:00', 'Z'),
        'root': root, 'safe_root': safe_name(root), 'lang': lang,
        # H390 Phase 1: the model actually pinned on the translate agent() calls,
        # recorded authoritatively in the run's own meta so the window ledger can
        # stamp it per window (previously the model was invisible to the ledger —
        # the blocker that made the Fable-vs-Sonnet A/B question uncomputable).
        # EN pins the exact version; RU keeps the historical 'sonnet' alias (see the
        # model-pin substitution below), so this records what was *requested*, which
        # is the honest thing to attribute.
        'gen_model': 'claude-sonnet-5',
        'source_profile': source_profile,
        'source_profiles': source_profiles,
        'mode': 'nominal_masked' if nominal else 'batched_masked',
        # Nominal mode: `root` is only a window LABEL (e.g. pril10_w1), never a real headword,
        # and result rows are keyed by the safe-name file stem (k_ala, r_upa). promote_final_cards
        # keys the store row on meta.nominal + nominal_keymap[stem] -> true SLP1 headword; without
        # these two fields it would fall back to meta.root and mis-key every card to the label.
        'nominal': nominal,
        'nominal_keymap': ({k: (_slp1_lex_for_key(k)[0] or k) for k in keys} if nominal else None),
        'grammar_layer': ('nominal' if nominal else 'root') if grammar_on else 'none',
        'selected_keys': keys, 'batches': batches, 'batch_count': len(batches),
        'rootmap_sha256': sha256_file(rootmap) if rootmap else None,
        'input_hashes': input_hashes,
        # H191: INPUTS/PH now carry only cards reachable by a real agent() call.
        # TM-resolved and degenerate-pass-through rows remain accounted through
        # TM_RESOLVED/DEGENERATE_RESOLVED plus the full input_hashes map.
        'input_payload_keys': sorted(runtime_keys),
        'selfheal': SELFHEAL, 'selfheal_group_budget': SELFHEAL_GROUP_BUDGET if SELFHEAL else None,
        'selfheal_cards': {k: len(v) for k, v in frags.items()} if SELFHEAL else {},
        'binary_split': BINARY_SPLIT, 'output_budget': OUTPUT_BUDGET,
        'sense_presplit_budget': SENSE_PRESPLIT_BUDGET if SELFHEAL else None,
        'kill': KILL,
        'kill_gate': ({'factor': KILL_FACTOR, 'base_ms': KILL_BASE_MS, 'slope_ms': KILL_SLOPE_MS,
                       'floor_ms': KILL_FLOOR_MS, 'ceil_ms': KILL_CEIL_MS} if KILL else None),
        # Split agent pools: translate/binary-split cannot be starved by recovery already in
        # flight, and recovery cannot hit a shared ceiling before the per-card caps can bind.
        'kill_switch': KILL_SWITCH,
        'agent_budget_strategy': budget_plan.strategy,
        'max_agents': budget_plan.max_agents,
        'max_translate_agents': budget_plan.max_translate_agents,
        'max_heal_agents': budget_plan.max_heal_agents,
        'translate_agent_expected': budget_plan.translate_expected,
        'heal_budget_groups': budget_plan.heal_groups,
        'heal_budget_cards': budget_plan.heal_cards,
        'max_agents_factor': MAX_AGENTS_FACTOR,
        'max_agents_headroom': MAX_AGENTS_HEADROOM,
        # H255/H811 low-width staggered dispatch: <=MAX_WIDE concurrent units (0 = unbounded).
        'max_wide': MAX_WIDE,
        'stagger_ms': STAGGER_MS,
        # H442 per-card heal budget: caps the heal agent() calls ONE card may spend so a dense
        # card fails fast to partial instead of monopolizing the shared window MAX_AGENTS pool.
        'per_card_heal_budget': (PER_CARD_HEAL_BUDGET and SELFHEAL),
        'per_card_heal_factor': PER_CARD_HEAL_FACTOR if (PER_CARD_HEAL_BUDGET and SELFHEAL) else None,
        'per_card_heal_headroom': PER_CARD_HEAL_HEADROOM if (PER_CARD_HEAL_BUDGET and SELFHEAL) else None,
        # H442: kill-timeout-triggered bisection is blocked (soft/malformed bisection stays
        # allowed) so a slow-call cascade can't split toward doomed tiny fragments.
        'kill_timeout_no_bisect': bool(KILL_TIMEOUT_NO_BISECT and KILL and SELFHEAL),
        # H189 presplit-lane amortization budgets (fragments packed per agent() call).
        'presplit_group_cite_budget': PRESPLIT_GROUP_CITE_BUDGET,
        'presplit_group_sense_cap': PRESPLIT_GROUP_SENSE_CAP,
        'presplit_keys': presplit,
        'tm': os.path.basename(tm_path) if tm_path else None,
        'tm_auto': bool(tm_auto),
        'tm_available': bool(tm_path and os.path.exists(tm_path)),
        'tm_cards': len(tm_keys),
        'tm_hits': sorted(tm_keys),
        'frag_tm': os.path.basename(frag_file) if (frag_cache and tm_path) else None,
        'frag_tm_cards': sorted(frag_tm),
        'frag_tm_fragments': sum(sum(1 for grp in v for s in grp if s) for v in frag_tm.values()),
        'suggest_tm': os.path.basename(suggest_tm_path) if (suggest_tm_path and os.path.exists(suggest_tm_path)) else None,
        'suggest_profile': suggest_profile,
        'suggest_tm_cards': sorted(runtime_suggest_tm),
        'suggest_tm_top': {k: [{'source_kind': r.get('source_kind'),
                                'rank_profile': r.get('rank_profile'),
                                'rank_score': r.get('rank_score'),
                                'score_de_fragment': r.get('score_de_fragment'),
                                'score_sa_headword': r.get('score_sa_headword'),
                                'score_semantic_tag': r.get('score_semantic_tag'),
                                'text': (r.get('text') or '')[:80]}
                               for r in v]
                           for k, v in runtime_suggest_tm.items()},
        'degenerate_passthrough_keys': sorted(degenerate_keys),
        # A presplit card is routed to the fragment lane, i.e. len(frags[k]) agent() calls
        # (one per fragment group), NOT one — frags[k] always exists for a presplit key (the
        # router only routes cards already present in frags). Undercounting this as len(presplit)
        # made a 150-<ls> giant "cost 1 agent" in every preflight (observed: vid's real run spent
        # 102 agents against a 13-agent preflight estimate, almost entirely from its 5 presplit
        # giants each needing ~10-20 fragment calls). This is still an optimistic floor — it
        # ignores retries and whole-batch selfheal fallback on non-presplit cards.
        'agent_expected_after_tm': agent_expected,
    }
    print('  lanes: tm_cards=%d frag_tm_cards=%d degenerate_passthrough=%d agent_expected_after_tm=%d'
          % (meta['tm_cards'], len(meta['frag_tm_cards']),
             len(meta['degenerate_passthrough_keys']), meta['agent_expected_after_tm']))

    bound = bool(profile_slot or config_dir)
    if bound and not (profile_slot and config_dir):
        raise ValueError('manifest v2 requires both profile_slot and config_dir')
    if bound and (execution_route or 'claude-cli-headless') != 'claude-cli-headless':
        raise ValueError('profile-bound manifest v2 production is CLI/headless-only')
    synthetic_keys = set(synthetic_keys or [])
    if synthetic_keys - set(keys):
        raise ValueError('synthetic keys are outside selected_keys')
    execution = ({
        'profile_slot': profile_slot,
        'config_dir_fingerprint': config_dir_fingerprint(config_dir),
        'execution_route': execution_route or 'claude-cli-headless',
        'executor_lane': executor_lane or 'serial-whole-card',
        'validation_method': validation_method or 'audit_window+final_schema',
        'model_identifier': 'claude-sonnet-5',
    } if bound else None)
    key_provenance = ({
        k: ('synthetic_control' if k in synthetic_keys else 'real') for k in keys
    } if bound else None)
    execution_manifest = {
        'schema': SCHEMA_V2 if bound else 'pwg.headless_execution_manifest.v1',
        'meta': meta,
        'field': field,
        'model': 'claude-sonnet-5',
        'execution': execution,
        'key_provenance': key_provenance,
        'prompt': {
            'preamble': MASK_PREAMBLE.replace('`russian`', '`%s`' % field),
            'grammar': single_grammar,
            'grammars': grammars,
            'translation': tr,
            'nws_rule': nws_block,
        },
        'output_schema': batch_schema,
        'batches': batches,
        'inputs': runtime_inputs,
        'placeholder_maps': runtime_phmaps,
        'fragment_groups': frags,
        'fragment_placeholder_maps': phf,
        'fragment_tm': frag_tm,
        'tm_resolved': tm_resolved,
        'degenerate_resolved': degenerate_resolved,
        'suggestions': runtime_suggest_tm,
        'presplit_keys': presplit,
        'runtime': {
            'binary_split': bool(BINARY_SPLIT),
            'per_card_heal_budget': bool(PER_CARD_HEAL_BUDGET and SELFHEAL),
            'per_card_heal_factor': PER_CARD_HEAL_FACTOR,
            'per_card_heal_headroom': PER_CARD_HEAL_HEADROOM,
            'kill_timeout_no_bisect': bool(KILL_TIMEOUT_NO_BISECT and KILL and SELFHEAL),
            'whole_attempts': 2,
            'fragment_attempts': 3,
        },
        'budgets': {
            'timeout_floor_ms': KILL_FLOOR_MS,
            'timeout_ceil_ms': KILL_CEIL_MS,
            'max_translate_agents': budget_plan.max_translate_agents,
            'max_heal_agents': budget_plan.max_heal_agents,
            'max_wide': MAX_WIDE,
            'stagger_ms': STAGGER_MS,
        },
    }
    # The workflow output must carry the same promotion contract as its execution
    # manifest. Otherwise audit can verify the launch while promotion cannot
    # independently distinguish a real card from a synthetic control.
    if bound:
        bind_output_meta(meta, execution_manifest)

    js = """// AUTO-DERIVED v2 (batched + masked, canonical output) from run_pilot_wf.js - root=%(root)s.
// Several masked cards per agent call; {Tn} restored to source markup in-JS so the
// returned result is a canonical wf_output.json. See TLONLY_PROTOTYPE.md.
export const meta = {
  name: '%(name_prefix)s-opt2-%(root)s',
  description: 'batched+masked translation-only PWG->%(tgt_lang)s; amortized per-call overhead + masked I/O, {Tn} restored in-JS to canonical cards',
  phases: [{ title: 'Translate', detail: '%(gen_label)s: N masked cards per call -> rich cards; {Tn} restored to markup' }],
}

const CONV_TR = %(tr)s
const PREAMBLE = %(preamble)s
const GRAMMAR = %(grammar)s
const GRAMMARS = %(grammars)s
const NWS_RULE = %(nws)s
const CARDS_SCHEMA = %(schema)s
const BATCHES = %(batches)s
const INPUTS = %(inputs)s
const PH = %(phmaps)s
const FRAGS = %(frags)s
const PHF = %(phf)s
const BINARY_SPLIT = %(binary_split)s
const PRESPLIT = %(presplit)s
// Wall-clock kill gate (H155 follow-up). See FAILURE_MODES_AND_KILL_GATE_2026-07-04.md.
const KILL = %(kill)s
const KILL_FACTOR = %(kill_factor)s
const KILL_BASE_MS = %(kill_base_ms)s
const KILL_SLOPE_MS = %(kill_slope_ms)s
const KILL_FLOOR_MS = %(kill_floor_ms)s
const KILL_CEIL_MS = %(kill_ceil_ms)s
// H189 live budget kill-switch, split after H442/H462: whole-card translation/binary-split
// and fragment recovery spend independent pools. One runaway recovery cascade can no longer
// consume the capacity required to attempt the remaining primary batches; the recovery pool
// is the sum of the per-card heal ceilings, so those card-level guards are reachable.
const KILL_SWITCH = %(kill_switch)s
const MAX_AGENTS = %(max_agents)s
const MAX_TRANSLATE_AGENTS = %(max_translate_agents)s
const MAX_HEAL_AGENTS = %(max_heal_agents)s
// H255/H811 low-width staggered dispatch: cap the concurrent translateBatch/healOnly units so
// a degraded generation API isn't hit ~10-wide (the Workflow runtime cap) — a tiny card that
// takes ~54s ALONE is inflated past the 180s kill CEIL under contention. 0 = unbounded.
const MAX_WIDE = %(max_wide)s
const STAGGER_MS = %(stagger_ms)s
// H442 per-card heal budget: a per-card ceiling on heal agent() calls, threaded through
// healGroup's bisection recursion. Unlike MAX_AGENTS (a shared window pool), this stops ONE
// dense card from spending the whole window budget: once a card's own heal spend crosses
// ceil(nGroups * PER_CARD_HEAL_FACTOR) + PER_CARD_HEAL_HEADROOM, healGroup stops retrying/
// bisecting and returns the resolved fragments as a PARTIAL card (rest -> missing_fragments,
// targeted-requeue-able). A dense card thus fails fast + cheap, leaving budget for cards that
// can heal cleanly (H437: 3-4 dense cards were exhausting 61/61 agents, starving ~9 others).
const PER_CARD_HEAL_BUDGET = %(per_card_heal_budget)s
const PER_CARD_HEAL_FACTOR = %(per_card_heal_factor)s
const PER_CARD_HEAL_HEADROOM = %(per_card_heal_headroom)s
// H442: a KILL-TIMEOUT must not drive healGroup's bisection. A soft/malformed failure
// still bisects (a bigger group is genuinely harder; halves may parse), but a killed group
// routes unresolved fragments straight to the cheap transient requeue instead of halving
// toward tiny fragments that hit the same 45s floor.
const KILL_TIMEOUT_NO_BISECT = %(kill_timeout_no_bisect)s
// --tm: cards pre-resolved from the content-addressed translation memory (source-SHA hit).
// Emitted verbatim as canonical rows with tm:true and NO agent() call — their markup is
// already restored (they come from the promoted store), so they bypass restore/accept.
const TM_RESOLVED = %(tm_resolved)s
// Conservative no-LLM lane for tiny cross-reference/supplement stubs that contain no
// translatable German gloss. These are accounted rows, not skipped keys.
const DEGENERATE_RESOLVED = %(degenerate_resolved)s
// --tm fragment reuse: FRAG_TM[k] mirrors FRAGS[k]'s group shape; each slot is either a
// cached fragment's ALREADY-RESTORED senses (served with NO agent() call inside selfHeal)
// or null (translate it). A fully-cached card heals at zero cost; a partial giant card
// re-runs only its still-missing fragments. Empty ({}) unless --tm found a fragment sidecar.
const FRAG_TM = %(frag_tm)s
// Suggestion TM is advisory only: it may seed wording/evidence in the prompt, but it NEVER
// pre-resolves a card and therefore never changes tm_hits, batches, or agent accounting.
const SUGGEST_TM = %(suggest_tm)s
const META = %(meta)s

const restore = (t, ph) => (t || '').replace(/\\{T(\\d+)\\}/g, (m, n) => (ph[+n - 1] !== undefined ? ph[+n - 1] : m))
const countOf = (card, re) => { let n = 0; for (const rec of (card.records || [])) for (const s of (rec.senses || [])) n += ((s.german || '').match(re) || []).length; return n }
// H1152 guard 2: countOf() above ONLY ever reads the `german` SOURCE-echo field — it was
// built to verify the model copied the masked German verbatim, never to verify the
// TRANSLATION. countOfField lets accept() run the identical count over the actual
// target-language field (`english`/`russian`) too, so a {Tn} that survives in `german`
// but is silently dropped from the translation (H1070 r102: {#uc#} in a <F> footnote
// survived `german` 33/33 but vanished from `english`, 32/33 -- invisible to countOf()
// because it never looks at the translation field at all) is no longer invisible.
const countOfField = (card, field, re) => { let n = 0; for (const rec of (card.records || [])) for (const s of (rec.senses || [])) n += ((s[field] || '').match(re) || []).length; return n }
// Failure ledger: key -> last-known reason a card/fragment is unresolved. Every path that
// nulls a card MUST leave a reason here — a bare null is indistinguishable downstream
// between a hard agent() throw, a fidelity reject, and the model omitting the card,
// which is exactly the ambiguity that made a week of failures undiagnosable. Surfaced
// per-row (results[].error) and in summary.failures.
const FAIL = {}
const noteFail = (k, why) => { FAIL[k] = String(why).slice(0, 300) }
// --- wall-clock kill gate ---------------------------------------------------------
// Budget each schema-bearing agent() call a wall-clock allowance scaled to its output
// volume (skelBytes = summed masked-skeleton length of its cards/fragments — the model's
// output is ~2x this, and it's a natural composite of every failure driver); a call that
// runs past KILL_FACTOR x its expected time is abandoned so the caller can fall to the
// bounded fragment lane instead of waiting out the full StructuredOutput retry cap.
// setTimeout is a RELATIVE timer (Date.now() is banned in the runtime); AbortController
// is unavailable, so an abandoned call keeps running in the background until it dies on
// its own cap — we stop BLOCKING on it, which is the whole point.
class KillTimeout extends Error {}
const isKill = e => (e instanceof KillTimeout) || (e && /kill-timeout/.test(String(e && e.message)))
const killBudgetMs = skelBytes => Math.min(KILL_CEIL_MS, Math.max(KILL_FLOOR_MS, KILL_FACTOR * (KILL_BASE_MS + KILL_SLOPE_MS * skelBytes)))
const skelBytesOfKeys = keys => keys.reduce((n, k) => n + (INPUTS[k] ? INPUTS[k].skeleton.length : 0), 0)
// H220: a SINGLE card with no selfheal fallback (single-fragment supplement / nominal card
// that does not split) has NO smaller lane for the kill gate to route to — abandoning it on
// the byte-scaled budget is pure loss. Such a card still returns a VALID card, only slower
// than a tiny skeleton's budget predicts: the fixed per-call StructuredOutput latency
// (~55-105 s) dominates, independent of skeleton size. The no-PWG w1 run killed 6/6 nulls
// this way (kill-timeout 53-104 s, all would have passed accept). Give a no-fallback single
// the CEIL budget so it is only abandoned on a true >CEIL hang.
// H255/H823 extension: give ANY single-card batch the CEIL, not just no-fallback ones. The
// original rule kept a SPLITTABLE single on the aggressive byte-scaled gate because "a kill
// routes to fragment heal" — but the heal groups run on the SAME byte-scaled budgets, so on a
// slow API BOTH the whole-card attempt AND the heal lane kill on the ~55-105 s fixed latency,
// and the card is a permanent null anyway (the H255 presplit-cohort loss). A lone card has no
// batch-mates to starve, so it should get the full CEIL on its ONE whole-card attempt (it
// either lands within the fixed latency or genuinely hangs) instead of being abandoned into a
// heal lane that is no better budgeted. Multi-card BATCHES keep the byte-scaled gate (there a
// kill legitimately routes to binary-split, and one slow card must not hold up its mates).
// SHARED (keys on FRAGS, no RU/EN branching).
const hasFallback = k => Array.isArray(FRAGS[k]) && FRAGS[k].length > 0
const killBudgetForCur = cur => (cur.length === 1) ? KILL_CEIL_MS : killBudgetMs(skelBytesOfKeys(cur))
// Split-pool budget state. Labels beginning `heal:` are recovery; every other call is primary
// translation (including resolveGroup binary splits). BudgetExceeded is deliberately NOT an
// isKill(): a kill routes to recovery, whereas a pool stop must issue zero more calls in that
// lane. AGENTS_SPENT remains the backwards-compatible total telemetry counter.
class BudgetExceeded extends Error {}
let AGENTS_SPENT = 0
let BUDGET_TRIPPED = false
let TRANSLATE_AGENTS_SPENT = 0
let HEAL_AGENTS_SPENT = 0
let TRANSLATE_BUDGET_TRIPPED = false
let HEAL_BUDGET_TRIPPED = false
// H462 telemetry: COUNTERS ONLY, no behavioural change. The two decisive numbers of every
// launch post-mortem — the kill-timeout count and the 'Connection closed mid-response'
// count — previously existed only as console.log strings and were hand-counted from
// transcripts into LAUNCH_FUCKUPS.md ('58 of 61 kill-timeouts', '3 conn-errors'). Returned
// in `summary` so the orchestrator and classify_run.py read them mechanically instead.
// CONN_ERRORS counts THROWN transport errors; agent() can also RETURN NULL on a terminal
// API error after retries — those stay visible as agent-returned-null in summary.failures,
// so a zero here is 'no thrown transport error', not 'network provably healthy'.
let KILL_TIMEOUTS = 0
let CONN_ERRORS = 0
let HEAL_CALLS = 0
let KILL_BISECT_BLOCKED = 0
// H960 SAN-LOSS shortfall telemetry: TELEMETRY ONLY, no behavioural change (SOFT rollout).
// accept() records — but does NOT reject on — a card whose emitted top-level sense count
// falls short of the source's deterministic (cross-reference-hardened) source_senses. This
// is the whole-dropped-sense signal the <ls>/{# fidelity guard is blind to (H920's deferred
// deepest fix). It is soft-first so live traffic can measure the true drop-vs-false-flag
// balance before the reject+requeue is armed; flipping SANLOSS_HARD_REJECT=true (owner-gated,
// after the live measurement) turns each shortfall into the same deterministic requeue as an
// ls/sk fidelity-reject. Counter + per-card details ride in `summary` for classify_run.py.
const SANLOSS_HARD_REJECT = false
let SANLOSS_SHORTFALLS = 0
const SANLOSS_DETAIL = []
// H960 grammar-{Tn} multiset telemetry: TELEMETRY ONLY, no behavioural change (SOFT rollout).
// The main-path accept() <ls>/{# count check is blind to a dropped GRAMMAR <lex> {Tn} (or any
// masked span carrying neither an <ls> nor a {#) — the exact gap the heal path's acceptFrag
// already guards with a full {Tn}-multiset compare. accept() records — but does NOT reject on —
// a card whose emitted {Tn} multiset differs from its source skeleton's. Soft-first so live
// traffic can measure the drop-vs-self-expansion mix (a model that writes literal <ls>..</ls>
// instead of {Tn} also trips this) before the reject is armed; flipping TNMASK_HARD_REJECT=true
// (owner-gated) turns each mismatch into the same deterministic requeue as an ls/sk reject.
const TNMASK_HARD_REJECT = false
let TNMASK_MISMATCHES = 0
const TNMASK_DETAIL = []
const isConn = e => !!(e && !(e instanceof KillTimeout) && /connection closed|connection error|econnreset|econnrefused|socket hang up|fetch failed|network error/i.test(String(e && e.message)))
async function agentKill(prompt, opts, skelBytes, budgetMsOverride) {
  const healLane = !!(opts && opts.label && /^heal:/.test(String(opts.label)))
  const lane = healLane ? 'heal' : 'translate'
  const spent = healLane ? HEAL_AGENTS_SPENT : TRANSLATE_AGENTS_SPENT
  const ceiling = healLane ? MAX_HEAL_AGENTS : MAX_TRANSLATE_AGENTS
  if (KILL_SWITCH && ceiling != null && spent >= ceiling) {
    BUDGET_TRIPPED = true
    if (healLane) HEAL_BUDGET_TRIPPED = true
    else TRANSLATE_BUDGET_TRIPPED = true
    throw new BudgetExceeded('budget-kill-switch[' + lane + ']: hit ' + ceiling + ' agent() calls; lane remainder requeued')
  }
  AGENTS_SPENT++
  if (healLane) HEAL_AGENTS_SPENT++
  else TRANSLATE_AGENTS_SPENT++
  // heal-lane spend: every healGroup label starts 'heal:' (bisection halves inherit the
  // prefix), so this counts real heal agent() calls against the whole window — the
  // per-card view stays on selfHeal's cardBudget.spent.
  if (healLane) HEAL_CALLS++
  if (!KILL) return agent(prompt, opts)   // kill gate off = counters best-effort (never in production)
  const ms = (budgetMsOverride != null) ? budgetMsOverride : killBudgetMs(skelBytes)
  let timer
  const guard = new Promise((_, rej) => { timer = setTimeout(() => rej(new KillTimeout('kill-timeout ' + Math.round(ms / 1000) + 's @ skelBytes=' + skelBytes)), ms) })
  try { return await Promise.race([agent(prompt, opts), guard]) }
  catch (e) { if (isKill(e)) KILL_TIMEOUTS++; else if (isConn(e)) CONN_ERRORS++; throw e }
  finally { clearTimeout(timer) }
}
// Masked-token multiset of a text: the {Tn} placeholders it carries, order-insensitive.
// Two texts with equal token multisets restore to identical citation/markup content.
const tokensOf = t => ((t || '').match(/\\{T\\d+\\}/g) || []).sort().join(' ')
const cardTokens = card => { let a = []; for (const rec of (card.records || [])) { a = a.concat((rec.grammar || '').match(/\\{T\\d+\\}/g) || []); for (const s of (rec.senses || [])) a = a.concat((s.german || '').match(/\\{T\\d+\\}/g) || []) } return a.sort().join(' ') }
// Index a returned cards[] by its self-declared key1 (the prompt requires key1 to echo the
// '=== CARD <key> ===' header). Used to match responses by KEY first, position second —
// positional-only matching silently misassigns every card after an omitted/reordered one.
const byKey1 = cards => { const m = {}; for (const c of cards) if (c && c.key1 !== undefined && !(c.key1 in m)) m[c.key1] = c; return m }
const exactCard = (cards, km, expected, fallbackIndex) => {
  if (km[expected] !== undefined) return km[expected]
  const c = cards[fallbackIndex]
  return (c && c.key1 === expected) ? c : null
}
// C-01: which fields carry {Tn} and must be unmasked is NOT re-typed here -- it is injected
// from card_fields.js_restore_spec(field), the same constant the Python lane restores from
// and promote_final_cards refuses on. Hand-maintaining this list on each lane is exactly how
// card.iast / rec.h / s.tag / s.differentia came to be promoted with their placeholders intact.
const RESTORE_SPEC = %(restore_spec)s
// H1152 guard 2: the per-sense target-language field name ('english'/'russian'), so accept()
// can run countOfField over the actual translation, not just the `german` source echo.
const TARGET_FIELD = '%(field)s'
// C-02: rebuild records[] from healed senses, preserving each sense's [h, grammar] owner.
// The stitch used to emit `records: [{ senses }]` — no h, no grammar — which violates
// schemas/pwg_ru_final_card.schema.json (record.required = {h, grammar, senses}) and made the
// promote path write h: null. It also collapsed real homonyms (79 sub-cards carry more than
// one distinct h). Consecutive senses sharing an owner stay in one record; a change of owner
// opens the next, so document order — and the whole-card fidelity counts — are unchanged.
// The Python twin is headless_worker.stitch_records; keep them behaviourally identical.
function stitchRecords(senses, owners) {
  const out = []
  for (let i = 0; i < senses.length; i++) {
    const [h, grammar] = owners[i] || [null, null]
    const last = out[out.length - 1]
    if (!last || last.h !== h || last.grammar !== grammar) out.push({ h, grammar, senses: [senses[i]] })
    else last.senses.push(senses[i])
  }
  return out
}
function restoreCard(card, k) {
  const ph = PH[k] || []
  for (const f of RESTORE_SPEC.card) if (typeof card[f] === 'string') card[f] = restore(card[f], ph)
  for (const rec of (card.records || [])) {
    for (const f of RESTORE_SPEC.record) if (typeof rec[f] === 'string') rec[f] = restore(rec[f], ph)
    for (const s of (rec.senses || [])) {
      for (const f of RESTORE_SPEC.sense) if (typeof s[f] === 'string') s[f] = restore(s[f], ph)
    }
  }
  return card
}
// Per-card grammar (nominal mode): each headword carries its own block. Empty in root
// mode (the shared GRAMMAR is injected once before CONV_TR) and in the --no-grammar arm.
const suggestionBlock = k => {
  const rows = SUGGEST_TM[k] || []
  if (!rows.length) return ''
  const scoreBits = r => [
    'de=' + (r.score_de_fragment ?? 'n/a'),
    'sa=' + (r.score_sa_headword ?? 'n/a'),
    'tag=' + (r.score_semantic_tag ?? 'n/a'),
    'combined=' + (r.score_combined ?? r.score ?? 'n/a')
  ].join(' ')
  return '\\n--- advisory translation-memory suggestions (SUGGEST ONLY: may seed weak evidence; do not copy unsupported senses; mark provenance if used) ---\\n' +
    rows.map(r => '[' + (r.source_kind || 'suggestion') + ' ' + scoreBits(r) + ' ' + (r.provenance_note || '') + '] ' + (r.text || '')).join('\\n')
}
const cardBlock = k => (GRAMMARS[k] || '') + '\\n\\n=== CARD ' + k + ' ===\\n--- masked German (translatable only; {Tn}=masked span) ---\\n' + INPUTS[k].skeleton + suggestionBlock(k) + '\\n--- portrait (evidence) ---\\n' + INPUTS[k].portrait

const accept = (c, k) => {
  if (!c) return null
  // H960 grammar-{Tn} multiset guard (soft). BEFORE restore (the {Tn} placeholders are gone
  // after restoreCard): a dropped grammar <lex> {Tn} carries neither an <ls> nor a {#, so the
  // count check below is blind to it — but the {Tn} multiset is not. This is the heal path's
  // acceptFrag check (which has run in production without incident) brought to the main path.
  // SOFT by default: record telemetry, do NOT reject; arming is TNMASK_HARD_REJECT (owner-gated).
  {
    const tok = cardTokens(c), want = tokensOf(INPUTS[k].skeleton)
    if (tok !== want) {
      TNMASK_MISMATCHES++
      TNMASK_DETAIL.push({ key: k, got: tok, want: want })
      if (TNMASK_HARD_REJECT) { noteFail(k, 'tnmask-reject: {Tn} multiset [' + tok + '] != [' + want + ']'); return null }
      log('{Tn} multiset mismatch (soft): ' + k + ' — kept, telemetry only')
    }
  }
  c = restoreCard(c, k)
  // Fidelity guard: restored <ls>/{#..#} counts MUST match the source — a mismatch
  // means misalignment / dropped {Tn}. Reject -> deterministic requeue, never emit garbled.
  const ls = countOf(c, /<ls\\b/g), sk = countOf(c, /\\{#/g)
  if (ls !== INPUTS[k].ls || sk !== INPUTS[k].sk) {
    noteFail(k, 'fidelity-reject: <ls> ' + ls + '/' + INPUTS[k].ls + ', {# ' + sk + '/' + INPUTS[k].sk)
    return null
  }
  // H1152 guard 2: the check above counts <ls>/{#..#} ONLY in the `german` source-echo
  // field (countOf's hard-coded `s.german` read) -- it proves the model faithfully copied
  // the masked German back out, never that the TRANSLATION preserved the same spans. A
  // {Tn} can be dropped from the translation field alone with zero effect on the check
  // above (this is the H960/H911 `dropped_sanskrit_span` gap, already known and detected
  // as a LOW/report-only RU-side signal in prompt_rule_audit.markup_sigla_risks, but never
  // wired as a HARD, blocking check on the generation path for either language). Root
  // cause, confirmed against the live H1070 r102 row (vac~~h0_00_pwg00, {#uc#} inside a
  // <F> footnote): `german` carried 33/33 expected {#..#} spans (this check passed clean)
  // while `english` carried only 32/33 -- the drop happened ONLY in the field this guard
  // never inspects. Run the identical count over the actual target-language field so a
  // translation-only drop can no longer hide behind a clean source echo.
  const lsT = countOfField(c, TARGET_FIELD, /<ls\\b/g), skT = countOfField(c, TARGET_FIELD, /\\{#/g)
  if (lsT !== INPUTS[k].ls || skT !== INPUTS[k].sk) {
    noteFail(k, 'translation-fidelity-reject: <ls> ' + lsT + '/' + INPUTS[k].ls + ', {# ' + skT + '/' + INPUTS[k].sk)
    return null
  }
  // H960 SAN-LOSS shortfall guard (H920's deferred deepest fix). The ls/sk fidelity check
  // above is blind to a whole dropped sense that carries neither a citation nor a {#..#} span
  // (darvI 2/3). Compare the emitted top-level sense count to the source's deterministic,
  // cross-reference-hardened source_senses (stamped Python-side). exp<1 (unnumbered supplement)
  // is skipped, and only a shortfall (emitted < exp) is flagged — a faithful split that yields
  // MORE senses never trips it. SOFT by default: record telemetry, do NOT reject; arming the
  // reject is SANLOSS_HARD_REJECT (owner-gated, after live measurement of the false-flag rate).
  const exp = INPUTS[k].source_senses
  if (exp > 0) {
    const emitted = (c.records || []).reduce((n, rec) => n + ((rec.senses || []).length), 0)
    if (emitted < exp) {
      SANLOSS_SHORTFALLS++
      SANLOSS_DETAIL.push({ key: k, expected: exp, emitted: emitted, dropped: exp - emitted })
      if (SANLOSS_HARD_REJECT) {
        noteFail(k, 'sanloss-reject: senses ' + emitted + '/' + exp)
        return null
      }
      log('SAN-LOSS shortfall (soft): ' + k + ' senses ' + emitted + '/' + exp + ' — kept, telemetry only')
    }
  }
  return c
}

// Resolve one heal GROUP (indices into `grp`), trying the whole group up to 3 attempts;
// if it still has >1 unresolved fragment, bisect and resolve each half independently with
// its own fresh 3-attempt budget — this is the safety net a grouped call needs: a live run
// on brU showed a 2-fragment group (ud) fail all 3 attempts and lose BOTH fragments, where
// the pre-grouping one-fragment-per-call design would only have risked one. Bisection falls
// back toward that safer granularity only when a group actually struggles, so the happy path
// (group succeeds) keeps the full cost saving. Returns a {idx: card} map, or null if any
// fragment never resolved even as a singleton.
async function healGroup(k, idxs, grp, label, budget) {
  const resolved = {}
  const fkey = fi => k + '_f' + fi
  // H442 per-card heal budget: `budget` is a shared mutable {spent,max} owned by the CARD
  // (selfHeal creates one and passes the same object into every group + every bisection
  // recursion). Once the card's own heal spend crosses budget.max, stop starting new calls
  // and return the resolved fragments as partial — the card's remaining fragments requeue,
  // but it never keeps consuming the shared window MAX_AGENTS pool. budget==null (or
  // --no-per-card-heal-budget) restores the old unbounded behavior.
  const budgetExhausted = () => budget && budget.max != null && budget.spent >= budget.max
  // Accept a returned fragment only if its masked-token multiset matches the fragment's
  // skeleton — the heal path previously accepted fragments UNCHECKED (the main path's
  // accept() fidelity guard had no heal-side sibling), so a misaligned/mangled fragment
  // could be stitched into a partial card with no gate downstream reading it.
  const acceptFrag = (c, fi) => {
    if (!c) return false
    if (cardTokens(c) !== tokensOf(grp[fi].skeleton)) {
      noteFail(fkey(fi), 'fragment-fidelity-reject: {Tn} multiset mismatch')
      return false
    }
    resolved[fi] = c
    return true
  }
  let pending = idxs.slice()
  let killedOut = false   // H442: did this group's attempt loop end on a kill-timeout?
  for (let att = 0; att < 3 && pending.length; att++) {
    if (budgetExhausted()) {
      pending.forEach(fi => noteFail(fkey(fi), 'per-card-heal-budget: card ' + k + ' hit ' + budget.max + ' heal calls — partial, requeue remaining'))
      break   // fail fast to partial; the card stops consuming the shared window budget
    }
    if (budget) budget.spent++   // account this call against the card's own ceiling
    const blocks = pending.map(i => '\\n\\n=== CARD ' + fkey(i) + ' (fragment ' + (i + 1) + '/' + grp.length + ') ===\\n--- masked German (translatable only; {Tn}=masked span) ---\\n' + grp[i].skeleton).join('')
    const prompt = PREAMBLE + GRAMMAR + CONV_TR + blocks
    const gskel = pending.reduce((n, fi) => n + (grp[fi].skeleton ? grp[fi].skeleton.length : 0), 0)
    let res
    try {
      res = await agentKill(prompt, { label: label + '[' + pending.length + ']' + (att ? '(r' + att + ')' : ''), phase: 'Translate', schema: CARDS_SCHEMA, model: '%(model)s', tools: [] }, gskel)
    } catch (e) {
      if (!isKill(e)) throw e   // real hard failure — propagate (caught by selfHeal's per-group try)
      killedOut = true
      if (KILL_TIMEOUT_NO_BISECT) KILL_BISECT_BLOCKED++   // H462: telemetry only
      pending.forEach(fi => noteFail(fkey(fi), e.message))
      log(label + ': kill-timeout-no-bisect: ' + e.message + ' — abandoned, requeueing ' + pending.length + ' fragment(s)')
      break   // stop retrying this group; kill-timeout fragments requeue instead of bisecting
    }
    if (res && Array.isArray(res.cards)) {
      const km = byKey1(res.cards)
      // Fragments may arrive reordered, but a positional fallback is safe only when the
      // fallback card still echoes the exact fragment key and passes the token multiset guard.
      pending.forEach((fi, idx) => {
        const fk = fkey(fi)
        const cand = exactCard(res.cards, km, fk, idx)
        if (!cand) { noteFail(fk, 'missing-or-mismatched-fragment-key'); return }
        acceptFrag(cand, fi)
      })
    } else {
      pending.forEach(fi => noteFail(fkey(fi), res ? 'malformed-response (no cards[])' : 'agent-returned-null'))
    }
    pending = pending.filter(fi => !resolved[fi])
  }
  // H442 kill-timeout no-bisect: a group that ended on a kill-timeout is treated as
  // transiently slow, not too big. Leave unresolved fragments as `missing` for requeue.
  const killBisectBlocked = killedOut && KILL_TIMEOUT_NO_BISECT
  if (killBisectBlocked && pending.length > 1) {
    log(label + ': kill-timeout-no-bisect: not bisecting ' + pending.length + ' fragment(s), routing to transient requeue')
  }
  if (pending.length > 1 && !budgetExhausted() && !killBisectBlocked) {
    const mid = Math.ceil(pending.length / 2)
    // Guard each half independently: an unguarded Promise.all rejects wholesale when one
    // half hard-throws, discarding the OTHER half's already-resolved fragments — the same
    // one-late-failure-wipes-earlier-work class fixed at the selfHeal and translateBatch
    // levels (PR #38/#40), recurring inside the bisection itself.
    // H442: the same `budget` object flows into both halves, so the card's ceiling bounds the
    // TOTAL bisection cascade (both halves share one counter), not each half independently.
    const [a, b] = await Promise.all([
      healGroup(k, pending.slice(0, mid), grp, label + '/A', budget).catch(e => { pending.slice(0, mid).forEach(fi => noteFail(fkey(fi), 'heal-hard-failure: ' + (e && e.message || e))); return null }),
      healGroup(k, pending.slice(mid), grp, label + '/B', budget).catch(e => { pending.slice(mid).forEach(fi => noteFail(fkey(fi), 'heal-hard-failure: ' + (e && e.message || e))); return null }),
    ])
    if (a) Object.assign(resolved, a.resolved)
    if (b) Object.assign(resolved, b.resolved)
    pending = pending.filter(fi => !resolved[fi])
  }
  // Partial credit WITHIN the group too: return what resolved plus the exact missing
  // fragment indices — the old contract (null unless ALL fragments resolved) discarded a
  // group's resolved siblings over one stubborn fragment, the same all-or-nothing shape
  // PR #40 removed one level up.
  return { resolved, missing: pending }
}

// --selfheal fallback: a card the batch could not translate is split (deterministically,
// precomputed in FRAGS) into fragments, GROUPED into budget-sized batches (fragment-grouping
// tier), then each group is translated in ONE agent() call (several fragments per call, same
// multi-card-per-prompt pattern as translateBatch) and the fragments' senses are stitched into
// one card. Groups that never resolve (even solo, after healGroup's own bisection) are SKIPPED,
// not fatal to the whole card — a giant flat headword with no rootmap (e.g. large nominal
// stems like kAla/ka/SrI) can need 40+ groups, where requiring every one to succeed drives
// joint success probability toward zero even at a high per-group success rate. A partial
// result (missing_groups > 0) is still returned so downstream sense-coverage gates
// (audit_coverage.py / ru_coverage.py) can measure and flag exactly what's missing — the same
// philosophy the pipeline already uses for partial per-root RU coverage, just applied within
// one oversized card. Only returns null if NOTHING resolved at all. A partial card carries
// partial:true + missing_fragments (exact 'gN:fM' ids) + missing_groups/total_groups so a
// follow-up can requeue JUST the failed pieces instead of re-running the whole card.
async function selfHeal(k) {
  // H220 observability: a no-fallback selfHeal is the LAST resort after an upstream failure
  // (kill-timeout / missing-or-mismatched-key / fidelity-reject). Don't clobber that specific
  // reason with the generic 'no-selfheal-fallback' — the overwrite hid a kill-gate mass-kill
  // behind a misleading message for a whole session. Only set it when nothing failed yet.
  const groups = FRAGS[k]; if (!groups || !groups.length) { if (!FAIL[k]) noteFail(k, 'no-selfheal-fallback (card did not split or a fragment mask was lossy)'); return null }
  // H442 per-card heal budget: one shared {spent,max} for THIS card, threaded into every group's
  // healGroup and its bisection recursion. max scales off the card's own group count (happy path
  // is ~1 call/group), so a dense card that keeps bisecting fails fast to partial at its ceiling
  // instead of draining the shared window MAX_AGENTS pool and starving the other cards. Disabled
  // (max:null) restores the old unbounded per-card heal.
  const cardBudget = PER_CARD_HEAL_BUDGET
    ? { spent: 0, max: Math.ceil(groups.length * PER_CARD_HEAL_FACTOR) + PER_CARD_HEAL_HEADROOM }
    : { spent: 0, max: null }
  const ftm = FRAG_TM[k] || []            // --tm: per-group cached-senses-or-null, mirrors FRAGS[k]
  const senses = []
  const owners = []             // C-02: parallel to `senses` — the [h, grammar] each came from
  const missingFragments = []   // 'g<gi+1>:f<fi>' identifiers — persisted on the card so a
                                // targeted requeue of JUST the failed fragments is possible
                                // from wf_output alone (the inline path previously recorded
                                // only a count, making a follow-up a full re-run)
  const fragProv = []           // {fsha, senses} per FRESHLY-resolved fragment — harvested by
                                // translation_memory.py build-frags into the fragment TM so the
                                // next run reuses it (ground truth captured at the moment of success)
  // siTag: canonical tag per source sense_ord (FRAGS[k][gi][i].si), fixed to whatever tag the
  // FIRST fragment of that sense_ord reports. Citation-batch continuations of the same oversized
  // sense carry no sense-boundary marker of their own, so the model tags them independently and
  // fabricates fresh incrementing numbers (1,2,3...) that then collide with a sibling rootmap
  // part's REAL different senses in audit_sense_dupes.py's cross-part check. Forcing every
  // fragment sharing a sense_ord onto the same tag is the fix (see PIPELINE_HISTORY.md).
  const siTag = {}
  const applyTag = (si, s) => {
    if (si === undefined || si === null) return
    if (siTag[si] === undefined) siTag[si] = s.tag
    else s.tag = siTag[si]
  }
  for (let gi = 0; gi < groups.length; gi++) {
    const grp = groups[gi]
    const gph = (PHF[k] || [])[gi] || []
    const gtm = ftm[gi] || []
    // Fragments already in the TM are served directly (no agent() call); heal only the rest.
    // A fully-cached group issues zero calls; a partial giant card re-runs only what's missing.
    const uncached = []
    for (let i = 0; i < grp.length; i++) { if (!gtm[i]) uncached.push(i) }
    // A hard agent() failure inside healGroup (thrown, not returned — see translateBatch's
    // comment) must be caught HERE, per group: uncaught, it unwinds out of this whole loop and
    // discards every earlier group's already-accumulated senses along with it (observed live —
    // 45 agent calls ran, several groups plausibly succeeded, yet the card still came back with
    // ZERO senses because one later group's hard failure wiped the local `senses` array before
    // selfHeal could return anything).
    let r = { resolved: {}, missing: [] }
    if (uncached.length) {
      try { r = await healGroup(k, uncached, grp, 'heal:' + k + '#g' + (gi + 1), cardBudget) }
      catch (e) { r = { resolved: {}, missing: uncached }; noteFail(k, 'heal-group-hard-failure g' + (gi + 1) + ': ' + (e && e.message || e)) }
    }
    for (const fi of (r.missing || [])) missingFragments.push('g' + (gi + 1) + ':f' + fi)
    for (let i = 0; i < grp.length; i++) {
      if (gtm[i]) {
        // cached senses are ALREADY restored to source markup (validated at their harvest run);
        // slot them in at their document position — do NOT re-restore (no {Tn} remain). Tag
        // normalization still applies: an older cache entry harvested before this fix may carry
        // a fabricated tag.
        // The fragment TM caches SENSES ONLY -- no record context survives it, so these carry
        // no h/grammar owner. Recorded as unknown rather than invented (C-02 boundary).
        for (const s of gtm[i]) { applyTag(grp[i].si, s); senses.push(s); owners.push([null, null]) }
        continue
      }
      const card = r.resolved[i]
      if (!card) continue   // an uncached fragment that never resolved — already in missingFragments
      const ph = gph[i] || []
      const fsenses = []
      for (const rec of (card.records || [])) {
        for (const f of RESTORE_SPEC.record) if (typeof rec[f] === 'string') rec[f] = restore(rec[f], ph)
        for (const s of (rec.senses || [])) {
          for (const f of RESTORE_SPEC.sense) if (typeof s[f] === 'string') s[f] = restore(s[f], ph)
          applyTag(grp[i].si, s)
          // C-02: keep the OWNING record's (h, grammar) alongside the sense. This loop used to
          // flatten records->senses and drop `rec`, so the stitch below had nothing left to
          // emit and every promoted row read h: null (403 of the 468 came from this lane).
          senses.push(s); owners.push([rec.h, rec.grammar]); fsenses.push(s)
        }
      }
      if (grp[i].fsha && fsenses.length) fragProv.push({ fsha: grp[i].fsha, senses: fsenses })
    }
  }
  if (!senses.length) { if (!FAIL[k]) noteFail(k, 'selfheal-nothing-resolved'); return null }
  const stitched = { key1: k, records: stitchRecords(senses, owners) }
  if (fragProv.length) stitched.frag_prov = fragProv
  if (!missingFragments.length) {
    // fidelity check only meaningful on a COMPLETE heal — a partial result legitimately has
    // fewer citations than the source. Per-fragment token checks already gated each piece;
    // this whole-card count is the belt over those suspenders.
    if (countOf(stitched, /<ls\\b/g) !== INPUTS[k].ls || countOf(stitched, /\\{#/g) !== INPUTS[k].sk) {
      noteFail(k, 'stitched-fidelity-reject: complete heal, but restored <ls>/{# counts drift from source')
      return null
    }
  } else {
    stitched.partial = true
    stitched.missing_fragments = missingFragments
    stitched.missing_groups = new Set(missingFragments.map(x => x.split(':')[0])).size
    stitched.total_groups = groups.length
    log('heal:' + k + ' partial — ' + missingFragments.length + ' fragment(s) missing (' + missingFragments.join(', ') + ')')
  }
  return stitched
}

phase('Translate')
// Try a group of cards up to 2 full-group attempts, retrying ONLY the cards still
// unresolved (positional within the shrinking pending set) — one missing/garbled card
// must not re-bill the rest. Returns { resolved, pending } (pending = still-unresolved).
// With BINARY_SPLIT off this is the whole retry story (unchanged from before); with it on,
// a group of >1 cards that still fails after 2 attempts is bisected and each half gets its
// own fresh 2-attempt budget — isolates a single poison card instead of re-billing the
// group around it identically on every retry.
async function resolveGroup(pending, label) {
  const resolved = {}
  let cur = pending.slice()
  for (let attempt = 0; attempt < 2 && cur.length; attempt++) {
    // lean mode: NWS_RULE is non-empty and injected only when the batch has an NWS card
    // (full mode: NWS_RULE is '' and the NWS rule already lives inside CONV_TR).
    const nws = (NWS_RULE && cur.some(k => INPUTS[k].nws)) ? ('\\n\\n' + NWS_RULE + '\\n') : ''
    const prompt = PREAMBLE + GRAMMAR + CONV_TR + nws + cur.map(cardBlock).join('')
    let res
    try {
      res = await agentKill(prompt, { label: label + '[' + cur.length + ']' + (attempt ? '(retry)' : ''), phase: 'Translate', schema: CARDS_SCHEMA, model: '%(model)s', tools: [] }, skelBytesOfKeys(cur), killBudgetForCur(cur))
    } catch (e) {
      if (!isKill(e)) throw e   // real hard failure — propagate as before (translateBatch -> selfheal)
      // Kill: stop RE-billing this whole call — a stall re-times-out identically. Mark the
      // still-pending cards and break so BINARY_SPLIT can isolate the slow one (smaller halves
      // get proportionally smaller budgets), bottoming out to selfHeal per card.
      cur.forEach(k => noteFail(k, e.message))
      log(label + ': ' + e.message + ' — abandoned, routing ' + cur.length + ' card(s) to split/heal')
      break
    }
    if (res && Array.isArray(res.cards)) {
      // Match responses by their echoed key1 ONLY. Positional fallback can silently put
      // content under the wrong headword when a model omits/reorders cards, especially for
      // zero-marker cross-reference stubs where count-based fidelity guards are blind.
      const km = byKey1(res.cards)
      // H220 nominal key-echo tolerance: a masked nominal / no-PWG card carries the CLEAN SLP1
      // headword in its portrait ('key1': "CAyA"), which pulls the model into echoing that
      // instead of the mangled sub-card stem in the '=== CARD <stem> ===' header
      // (_c_ay_a~~h0_zz_pw) — confirmed for leading/interior-underscore stems (_c_ay_a->CAyA,
      // g_ayatr_i->gAyatrI). Recover ONLY when the returned key1 equals nominal_keymap[stem]
      // AND that SLP1 maps to EXACTLY ONE pending stem in this batch (unambiguous) — then
      // re-key the card to the stem. Never positional; NULL for root (PWG) windows
      // (META.nominal false), so test_generated_harness_strict_key_matching stays honest.
      const NKM = (META.nominal && META.nominal_keymap) ? META.nominal_keymap : null
      cur.forEach((k, i) => {
        let cand = km[k]
        if ((cand === undefined || cand === null) && NKM && NKM[k] && NKM[k] !== k) {
          const slp1 = NKM[k]
          const rivals = cur.filter(x => NKM[x] === slp1)
          if (rivals.length === 1) {
            // The model may echo the CLEAN SLP1 headword alone (slp1), OR the SLP1 with the
            // sub-card suffix kept — 'avyAhata~~h0_zz_pw' for the stem 'avy_ahata~~h0_zz_pw'
            // (H255 avy_ahata: SLP1 headword, but the ~~<layer> suffix carried over). Both are
            // unambiguous re-keys to the stem; still gated on META.nominal + rivals===1.
            const sfx = k.includes('~~') ? k.slice(k.indexOf('~~')) : ''
            const hit = (km[slp1] !== undefined && km[slp1] !== null) ? km[slp1]
                      : (sfx && km[slp1 + sfx] !== undefined && km[slp1 + sfx] !== null) ? km[slp1 + sfx]
                      : null
            if (hit) { cand = hit; cand.key1 = k }
          }
        }
        if (cand === undefined || cand === null) { noteFail(k, 'missing-or-mismatched-key'); return }
        const c = accept(cand, k)
        if (c) resolved[k] = c
      })
    } else {
      cur.forEach(k => noteFail(k, res ? 'malformed-response (no cards[])' : 'agent-returned-null'))
    }
    cur = cur.filter(k => !resolved[k])
  }
  if (BINARY_SPLIT && cur.length > 1) {
    const mid = Math.ceil(cur.length / 2)
    // Each half guarded independently — an unguarded Promise.all rejects wholesale on one
    // half's hard throw and discards the other half's resolved cards (see healGroup).
    const empty = h => ({ resolved: {}, pending: h })
    const [a, b] = await Promise.all([
      resolveGroup(cur.slice(0, mid), label + '/A').catch(e => { cur.slice(0, mid).forEach(k => noteFail(k, 'batch-hard-failure: ' + (e && e.message || e))); return empty(cur.slice(0, mid)) }),
      resolveGroup(cur.slice(mid), label + '/B').catch(e => { cur.slice(mid).forEach(k => noteFail(k, 'batch-hard-failure: ' + (e && e.message || e))); return empty(cur.slice(mid)) }),
    ])
    Object.assign(resolved, a.resolved, b.resolved)
    cur = cur.filter(k => !resolved[k])
  }
  return { resolved, pending: cur }
}
async function translateBatch(batch, bi) {
  // A hard agent() failure (e.g. StructuredOutput retry cap exceeded, not just a malformed
  // response our own retry/heal loops already catch) throws instead of returning. Guard
  // resolveGroup AND selfHeal INDEPENDENTLY — a caller that wraps both in one try/catch
  // (as an earlier version of this fix did) swallows a whole-batch failure before --selfheal
  // ever runs, which defeats the fallback for exactly the cards that need it most (observed
  // live: a huge single-card nominal batch hard-failed the main attempt and the heal path,
  // with its precomputed fragment groups, never even got a chance to run). Both paths degrade
  // to "unresolved" on a hard failure — requeue-able, not fatal, and selfHeal still gets tried.
  const resolved = {}, healed = {}
  try {
    let pending = batch.slice()
    try {
      const r = await resolveGroup(batch, 'b' + bi)
      Object.assign(resolved, r.resolved); pending = r.pending
    } catch (e) {
      // fall through to --selfheal below with the full batch still pending
      log('b' + bi + ': whole-batch hard failure (' + (e && e.message || e) + ') — falling through to selfheal')
      batch.forEach(k => noteFail(k, 'batch-hard-failure: ' + (e && e.message || e)))
    }
    // self-healing tier: split-translate-stitch the cards the batch gave up on (no-op unless
    // --selfheal populated FRAGS). Runs only for the few still-failing cards.
    for (const k of pending) {
      let c = null
      try { c = await selfHeal(k) } catch (e) { c = null; noteFail(k, 'selfheal-hard-failure: ' + (e && e.message || e)) }
      if (c) { resolved[k] = c; healed[k] = 1 }
    }
  } catch (e) {
    // ABSOLUTE BACKSTOP — nothing above should throw, but if it does, the batch must
    // still return one row per input key. An uncaught throw here makes parallel() yield
    // null for the whole batch slot, and every key in it VANISHES from the results
    // (save_and_audit.py then drops the null slot on save — the exact silent-loss mode
    // this harness exists to prevent). Cards resolved before the throw are kept.
    batch.forEach(k => { if (!resolved[k] && !FAIL[k]) noteFail(k, 'batch-crash: ' + (e && e.message || e)) })
    log('b' + bi + ': unexpected batch crash (' + (e && e.message || e) + ') — returning accounted rows')
  }
  return batch.map(k => {
    const row = { key: k, card: resolved[k] || null, judge: null, judge_sonnet: null, escalated: !!healed[k] }
    if (!row.card && FAIL[k]) row.error = FAIL[k]
    return row
  })
}
// Pre-split lane (MG 2026-07-02): cards routed at GENERATION time straight to the fragment
// path — their whole-card attempt is a known loss (citation load alone exceeds the whole
// per-batch output budget; the 125-<ls> pwg00 heads failed the retry cap even solo), so
// skipping it converts up-to-5 paid retries into zero. Same selfHeal machinery, same
// partial-credit + missing_fragments contract; presplit:true marks the row's provenance.
async function healOnly(k) {
  let c = null
  try { c = await selfHeal(k) } catch (e) { c = null; noteFail(k, 'selfheal-hard-failure: ' + (e && e.message || e)) }
  const row = { key: k, card: c || null, judge: null, judge_sonnet: null, escalated: !!c, presplit: true }
  if (!row.card && FAIL[k]) row.error = FAIL[k]
  return [row]
}
// H255/H811 low-width staggered dispatch. Runs `thunks` with at most `width` in flight,
// spacing the first `width` starts by `staggerMs` so a degraded generation API isn't hit by
// a thundering herd. On a degraded API a tiny card that completes in ~54s ALONE is inflated
// past the 180s kill CEIL at ~10-wide (the Workflow runtime cap); at <=3-wide it keeps its
// isolated latency. width<=0 or >=len falls back to the runtime parallel(); a thrown thunk
// resolves to null (parallel() parity), and results stay index-aligned with `thunks`.
async function boundedParallel(thunks, width, staggerMs) {
  if (!width || width >= thunks.length) return parallel(thunks)
  const results = new Array(thunks.length).fill(null)
  let next = 0
  const worker = async () => {
    for (let idx = next++; idx < thunks.length; idx = next++) {
      try { results[idx] = await thunks[idx]() } catch (e) { results[idx] = null }
    }
  }
  const workers = []
  for (let w = 0; w < width; w++) {
    if (staggerMs && w > 0) await new Promise(r => setTimeout(r, staggerMs))
    workers.push(worker())
  }
  await Promise.all(workers)
  return results
}
// A Workflow session cannot prove which CLAUDE_CONFIG_DIR it billed or participate in
// the host-wide active-call lock. A profile-bound v2 artifact is therefore executable
// only through headless_worker.py; abort here before the first paid agent() call.
if (META.execution_manifest_schema === 'pwg.headless_execution_manifest.v2') {
  throw new Error('manifest-v2 production is CLI/headless-only; run the execution manifest')
}
// UNITS pairs each parallel slot with the exact keys it owes rows for, so the accounting
// backfill below stays index-correct with the presplit lane appended after the batches.
const UNITS = BATCHES.map((b, i) => ({ keys: b, run: () => translateBatch(b, i) }))
  .concat(PRESPLIT.map(k => ({ keys: [k], run: () => healOnly(k) })))
const grouped = await boundedParallel(UNITS.map(u => u.run), MAX_WIDE, STAGGER_MS)
// TOTAL ACCOUNTING INVARIANT: every selected key appears in `results` exactly once, no
// matter what failed above. parallel() resolves a thrown thunk to null — flat() would
// carry that null into results (crashing the summary below and silently dropping the
// batch's keys at save time). Synthesize accounted null rows for any such unit, then
// backfill any key that STILL isn't present (belt over suspenders).
const out = []
const seen = new Set()
// TM lane first: pre-resolved cards cost nothing and are already accounted for, so seed
// them before backfilling the translated units. tm:true marks provenance for the summary.
for (const k in TM_RESOLVED) { if (!seen.has(k)) { out.push({ key: k, card: TM_RESOLVED[k], judge: null, judge_sonnet: null, escalated: false, tm: true }); seen.add(k) } }
for (const k in DEGENERATE_RESOLVED) { if (!seen.has(k)) { out.push({ key: k, card: DEGENERATE_RESOLVED[k], judge: null, judge_sonnet: null, escalated: false, degenerate_passthrough: true }); seen.add(k) } }
grouped.forEach((rows, i) => {
  if (Array.isArray(rows)) {
    for (const r of rows) if (r && r.key && !seen.has(r.key)) { out.push(r); seen.add(r.key) }
  } else {
    log('u' + i + ': unit thunk resolved null — synthesizing accounted rows for its ' + UNITS[i].keys.length + ' key(s)')
    for (const k of UNITS[i].keys) if (!seen.has(k)) { out.push({ key: k, card: null, judge: null, judge_sonnet: null, escalated: false, error: FAIL[k] || 'batch-thunk-null' }); seen.add(k) }
  }
})
for (const k of META.selected_keys) if (!seen.has(k)) { out.push({ key: k, card: null, judge: null, judge_sonnet: null, escalated: false, error: FAIL[k] || 'unaccounted-key (should be impossible — report this)' }); seen.add(k) }
// Compact summary first so the orchestrator can read counts (ok/null/healed + the exact
// null keys to requeue) WITHOUT parsing the full results blob. results are still carried
// for save_and_audit/promote (the workflow runtime can't write files -> must be returned).
// `failures` maps every null key to its last-known reason; `partial_keys` lists healed
// cards that carry partial:true (usable but incomplete — see missing_fragments on the card).
const _ok = out.filter(r => r.card).length
const _failures = {}
for (const r of out) if (!r.card) _failures[r.key] = r.error || FAIL[r.key] || 'unknown'
const summary = { root: META.root, lang: META.lang, cards: out.length, ok: _ok,
                  null: out.length - _ok, healed: out.filter(r => r.escalated).length,
                  presplit: PRESPLIT.length, tm: out.filter(r => r.tm).length,
                  degenerate_passthrough: out.filter(r => r.degenerate_passthrough).length,
                  frag_tm_fragments: META.frag_tm_fragments || 0,
                  // Total counters stay backwards-compatible; lane counters make starvation
                  // and the binding pool directly observable.
                  agents_spent: AGENTS_SPENT, max_agents: (KILL_SWITCH ? MAX_AGENTS : null),
                  budget_kill_switch_tripped: BUDGET_TRIPPED,
                  translate_agents_spent: TRANSLATE_AGENTS_SPENT,
                  max_translate_agents: (KILL_SWITCH ? MAX_TRANSLATE_AGENTS : null),
                  translate_budget_tripped: TRANSLATE_BUDGET_TRIPPED,
                  heal_agents_spent: HEAL_AGENTS_SPENT,
                  max_heal_agents: (KILL_SWITCH ? MAX_HEAL_AGENTS : null),
                  heal_budget_tripped: HEAL_BUDGET_TRIPPED,
                  // H462: returned telemetry (previously log-only, hand-counted from
                  // transcripts). kill_bisect_blocked counts heal groups whose kill-timeout
                  // was routed to requeue instead of bisection (KILL_TIMEOUT_NO_BISECT).
                  kill_timeouts: KILL_TIMEOUTS, conn_errors: CONN_ERRORS,
                  heal_calls: HEAL_CALLS, kill_bisect_blocked: KILL_BISECT_BLOCKED,
                  // H960 SAN-LOSS shortfall telemetry (SOFT — no reject unless
                  // SANLOSS_HARD_REJECT). sanloss_shortfalls counts kept-but-short cards;
                  // sanloss_detail lists {key,expected,emitted,dropped} for the audit join.
                  sanloss_shortfalls: SANLOSS_SHORTFALLS, sanloss_hard_reject: SANLOSS_HARD_REJECT,
                  sanloss_detail: SANLOSS_DETAIL,
                  // H960 grammar-{Tn} multiset telemetry (SOFT — no reject unless TNMASK_HARD_REJECT).
                  tnmask_mismatches: TNMASK_MISMATCHES, tnmask_hard_reject: TNMASK_HARD_REJECT,
                  tnmask_detail: TNMASK_DETAIL,
                  null_keys: out.filter(r => !r.card).map(r => r.key),
                  partial_keys: out.filter(r => r.card && r.card.partial).map(r => r.key),
                  failures: _failures }
return { meta: META, summary, results: out }
""" % {
        'root': root, 'field': field, 'tr': json.dumps(tr, ensure_ascii=True),
        # C-01: the restore field set is INTERPOLATED from `card_fields`, never re-typed here.
        # This lane and the Python lane each kept their own hand-written list of what to
        # unmask; both listed three fields while promote read six, and 670 store rows landed
        # with a raw {Tn}. The JS cannot import Python, so the constant is injected instead.
        'restore_spec': card_fields.js_restore_spec(field),
        # Language-aware meta + model pin. EN path pins Sonnet 5 explicitly
        # (the bare 'sonnet' alias resolved to 4.6 on a prior run); RU path
        # keeps the 'sonnet' alias unchanged so the autonomous RU runs are untouched.
        'name_prefix': 'pwgen' if lang == 'en' else 'pwgru',
        'tgt_lang': 'English' if lang == 'en' else 'Russian',
        'gen_label': 'Sonnet 5' if lang == 'en' else 'Sonnet',
        'model': 'claude-sonnet-5',
        'preamble': json.dumps(MASK_PREAMBLE.replace('`russian`', '`%s`' % field), ensure_ascii=True),
        'grammar': json.dumps(single_grammar, ensure_ascii=True),
        'grammars': json.dumps(grammars, ensure_ascii=True),
        'nws': json.dumps(nws_block, ensure_ascii=True),
        'schema': json.dumps(batch_schema, ensure_ascii=True),
        'batches': json.dumps(batches), 'inputs': json.dumps(runtime_inputs, ensure_ascii=True),
        'phmaps': json.dumps(runtime_phmaps, ensure_ascii=True), 'meta': json.dumps(meta, ensure_ascii=True),
        'frags': json.dumps(frags, ensure_ascii=True), 'phf': json.dumps(phf, ensure_ascii=True),
        'binary_split': json.dumps(BINARY_SPLIT), 'presplit': json.dumps(presplit),
        'kill': json.dumps(KILL), 'kill_factor': json.dumps(KILL_FACTOR),
        'kill_base_ms': json.dumps(KILL_BASE_MS), 'kill_slope_ms': json.dumps(KILL_SLOPE_MS),
        'kill_floor_ms': json.dumps(KILL_FLOOR_MS), 'kill_ceil_ms': json.dumps(KILL_CEIL_MS),
        'kill_switch': json.dumps(KILL_SWITCH), 'max_agents': json.dumps(budget_plan.max_agents),
        'max_translate_agents': json.dumps(budget_plan.max_translate_agents),
        'max_heal_agents': json.dumps(budget_plan.max_heal_agents),
        'max_wide': json.dumps(MAX_WIDE), 'stagger_ms': json.dumps(STAGGER_MS),
        'per_card_heal_budget': json.dumps(PER_CARD_HEAL_BUDGET and SELFHEAL),
        'per_card_heal_factor': json.dumps(PER_CARD_HEAL_FACTOR), 'per_card_heal_headroom': json.dumps(PER_CARD_HEAL_HEADROOM),
        'kill_timeout_no_bisect': json.dumps(bool(KILL_TIMEOUT_NO_BISECT and KILL and SELFHEAL)),
        'tm_resolved': json.dumps(tm_resolved, ensure_ascii=True),
        'degenerate_resolved': json.dumps(degenerate_resolved, ensure_ascii=True),
        'frag_tm': json.dumps(frag_tm, ensure_ascii=True),
        'suggest_tm': json.dumps(runtime_suggest_tm, ensure_ascii=True),
    }
    for bad in ['readFileSync', 'fileURLToPath', 'import.meta']:
        if bad in js:
            die('residual node-ism: %s' % bad)
    return (js, batches, execution_manifest) if return_manifest else (js, batches)


def _even_chunks(seq, n):
    """Split `seq` into n contiguous, near-equal chunks (order preserved)."""
    n = max(1, min(n, len(seq)))
    q, r = divmod(len(seq), n)
    out, i = [], 0
    for j in range(n):
        take = q + (1 if j < r else 0)
        out.append(seq[i:i + take])
        i += take
    return out


def harness_size_report(root, keys, nominal, js_len, max_bytes):
    """H189 harness-size guard: if the emitted harness exceeds max_bytes (the Workflow
    scriptPath cap, F-harness-size-limit), compute a key-disjoint split into sub-windows
    each expected under the cap and return the human-facing warning lines + suggested
    commands. Returns (oversize: bool, lines: [str])."""
    if js_len <= max_bytes:
        return False, []
    # Leave headroom for the fixed framework (CONV_TR/PREAMBLE/SCHEMA) duplicated per
    # sub-window; 0.85 * cap keeps each piece safely under the real limit.
    n = max(2, int(math.ceil(js_len / (max_bytes * 0.85))))
    chunks = _even_chunks(list(keys), n)
    lines = ['HARNESS OVERSIZE: %d bytes > %d cap (Workflow scriptPath limit, F-harness-size-limit).'
             % (js_len, max_bytes),
             '  A harness this large cannot launch as one workflow. Split into %d key-disjoint '
             'sub-windows (regenerate each, verify each is under the cap):' % len(chunks)]
    prefix = ('--nominal --keys=' if nominal else '%s --keys=' % root)
    for i, ch in enumerate(chunks, 1):
        lines.append('  w%d: python src/pilot/gen_opt_harness2.py %s%s --out=run_pilot_wf.opt2.w%d.js'
                     % (i, prefix, ','.join(ch), i))
    lines.append('  Then merge the sub-window results (see _merge_subwindows.py / H189).')
    return True, lines


def dump_schema(lang='ru'):
    """H428 diagnostic: print the per-call generation StructuredOutput schema's reachable
    $defs and char length, so a schema-size regression is visible without a Workflow-tool
    probe. Mirrors the schema build() actually sends (field-rename + required-narrowing +
    post-generation-field strip + reachable-defs prune)."""
    field = 'english' if lang == 'en' else 'russian'
    schema = load_json(os.path.join(REPO, 'schemas', 'pwg_ru_final_card.schema.json'))
    if field != 'russian':
        schema = _rename_sense_field(schema, 'russian', field)
    schema['$defs']['sense']['required'] = ['tag', 'german', field]
    defs = _strip_post_generation_fields(schema['$defs'])
    defs = _reachable_defs(defs, 'card')
    batch_schema = {
        'type': 'object', 'additionalProperties': False, 'required': ['cards'],
        'properties': {'cards': {'type': 'array', 'minItems': 1, 'items': {'$ref': '#/$defs/card'}}},
        '$defs': defs,
    }
    s = json.dumps(batch_schema)
    print('lang=%s reachable $defs: %s' % (lang, sorted(defs.keys())))
    print('char length: %d' % len(s))
    print(s)


def main():
    if '--dump-schema' in sys.argv[1:]:
        lang = 'ru'
        for a in sys.argv[1:]:
            if a.startswith('--lang='):
                lang = a.split('=', 1)[1].strip().lower()
        dump_schema(lang)
        return
    (root, keyfilter, keylist, budget, lean, nws_gate, nominal, grammar_on,
     out_path, manifest_path, lang, mw_tm, tm, tm_auto, suggest_tm,
     suggest_profile, profile_slot, config_dir, execution_route, executor_lane,
     validation_method, synthetic_keys) = parse_args(sys.argv[1:])
    if nominal:
        # No rootmap: the headword keys ARE the cards, in the order given.
        if not keylist:
            die('--nominal requires an explicit --keys=k1,k2,... list')
        rootmap, keys = None, keylist
    else:
        rootmap, keys = selected_keys(root, keyfilter)
        if keylist:
            keys = [k for k in keylist if k in set(keys)]
    js, batches, manifest = build(root, keys, rootmap, budget, lean, nws_gate,
                                  nominal, grammar_on, lang, mw_tm, tm, tm_auto,
                                  suggest_tm, suggest_profile, return_manifest=True,
                                  profile_slot=profile_slot, config_dir=config_dir,
                                  execution_route=execution_route, executor_lane=executor_lane,
                                  validation_method=validation_method,
                                  synthetic_keys=synthetic_keys)
    out = os.path.abspath(out_path) if out_path else os.path.join(REPO, 'src', 'pilot', 'run_pilot_wf.opt2.js')
    # Write LF (not CRLF): the Workflow-tool approval rejects scripts containing
    # raw \r control chars, so a CRLF harness cannot be launched on Windows.
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(js)
    if manifest_path:
        manifest_out = os.path.abspath(manifest_path)
        os.makedirs(os.path.dirname(manifest_out), exist_ok=True)
        tmp = manifest_out + '.tmp'
        with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=1)
            f.write('\n')
        os.replace(tmp, manifest_out)
        print('wrote', manifest_out, '| execution manifest', manifest['schema'])
    mode = ('NOMINAL%s' % ('' if grammar_on else '/no-grammar')) if nominal else (
        'LEAN(rejected)' if lean else 'NWS-GATE' if nws_gate else 'full')
    print('wrote', out, len(js), 'bytes |', len(keys), 'cards in', len(batches), 'batches',
          '(sizes', [len(b) for b in batches], ') | mode', mode)
    # H189 harness-size guard: surface the scriptPath cap at generation, not at launch.
    oversize, lines = harness_size_report(root, keys, nominal, len(js), MAX_HARNESS_BYTES)
    if oversize:
        for ln in lines:
            print(ln)
        if REFUSE_OVERSIZE:
            die('refusing oversize harness (--refuse-oversize); split as shown above')


if __name__ == '__main__':
    main()
