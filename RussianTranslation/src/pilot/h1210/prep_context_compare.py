#!/usr/bin/env python
r"""H2591 — bounded baseline-vs-PREP qualification on sealed Flash PREP contexts.

What this is
------------
A **qualification**, not a rollout. Eight predeclared PWG cards are translated twice —
arm **A** with the production prompt exactly as `headless_worker.build_prompt` emits it,
arm **B** with those same bytes plus **one** canonical delimited `pwg.prep_context.v1`
block — and the two arms are compared on audited-card count, wall time, tokens, credit
equivalent, and enumerated defect classes. ``n=8`` is descriptive; it can reject a bad
context design or justify a larger pre-registered experiment. It can never grant a
production route.

What it must never do (fences, enforced in ``--check`` and again at call time)
-----------------------------------------------------------------------------
* never call DeepSeek — PREP is precomputed input, read from sealed contexts;
* never write ``pwg_ru_translated.jsonl``, a TM sidecar, the store, the promotion
  journal, or a production default;
* never treat a fuzzy or same-key TM hit as exact-content reuse;
* never auto-retry an ambiguous or charged call;
* never exceed eight pairs / sixteen irreversible calls.

Why arm B appends rather than splices
-------------------------------------
``build_prompt`` is stable-left (H2191): ``preamble + translation + grammar + [nws] +
card blocks``. Appending the PREP block after the card block keeps arm A's bytes an
**exact prefix** of arm B's, so "identical base prompt bytes across arms" is not a
promise in prose but a one-line assertion (``prompt_b.startswith(prompt_a)``) plus a
delimiter-count check. Splicing the context into the head would move the production
bytes and price two different prompts — the H2011 trap
(`a manifest that validates, runs, bills, and tests a prompt production never uses`).

Determinism
-----------
The sealed plan binds the manifest SHA-256, the eight keys with their strata, both arms'
prompt hashes, each context's ``context_sha256`` and ``prep_semantic_sha256``, the model
id, the output limit, and the output-schema hash — and **excludes observation time**, so
re-planning from the same manifest and contexts replays byte-identically
(``plan_sha256`` is stable). Envelopes and the receipt carry timings; the plan does not.

Dependency injection
--------------------
``execute()`` takes a ``caller`` — ``caller(argv, prompt, timeout) -> CallResult`` — so
the hermetic selftest drives every branch (model substitution, missing usage, reservation
exhaustion, crash/resume, exact-once finalization) with zero network and zero spend. The
production caller is :func:`cli_caller`, which is argv-for-argv what
``h2158_route_ab.call_cli`` builds.

Usage (offline first, always)::

    python src/pilot/h1210/prep_context_compare.py --selftest
    python src/pilot/h1210/prep_context_compare.py --select --out-dir OUT
    python src/pilot/h1210/prep_context_compare.py --plan --manifest M --context-dir C --out-dir OUT
    python src/pilot/h1210/prep_context_compare.py --check --plan-file OUT/plan.json
    python src/pilot/h1210/prep_context_compare.py --execute --plan-file OUT/plan.json
    python src/pilot/h1210/prep_context_compare.py --receipt --plan-file OUT/plan.json

Handoff: [H2591](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2591-Opus_SanskritLexicography_pwg-flash-prep-claude-bounded-context-compare_12.08.26.md).
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
PILOT = os.path.dirname(HERE)
SRC = os.path.dirname(PILOT)
for _path in (HERE, PILOT, SRC):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import det_gate                                              # noqa: E402
import prep_pack                                             # noqa: E402
import pwg_mask                                              # noqa: E402
from sense_count import count_source_senses                  # noqa: E402
from call_reservation import (                               # noqa: E402
    CallLimitReached, CallReservationLedger, telemetry_from_cli_wrapper,
    unevaluable_telemetry)
from headless_worker import (                                # noqa: E402
    bare_cli_cwd, build_fragment_prompt, build_prompt, card_by_key, card_token_multiset,
    claude_argv_prefix, parse_cli_wrapper, structured_from_wrapper, token_multiset)

PLAN_SCHEMA = 'pwg.prep_context_comparison_plan.v1'
RECEIPT_SCHEMA = 'pwg.prep_context_comparison.v1'
ENVELOPE_SCHEMA = 'pwg.prep_context_comparison_envelope.v1'

#: The one model both arms must request AND return. A substitution stops the run.
REQUIRED_MODEL = 'claude-opus-5'
#: Output ceiling, identical across arms; part of the plan hash.
OUTPUT_LIMIT = 16000
#: Eight pairs, two calls each — the DEFAULT sample size. There is no flag to RAISE this.
#: A plan may seal a SMALLER `pair_count` (H2630's Option A seals 4, because production takes
#: only four of this pool's cards whole), and everything downstream reads the ceiling off the
#: plan rather than off this module, so a sealed plan can never be executed against a
#: different ceiling than the one it was checked under.
MAX_CALLS = 16
PAIR_COUNT = 8


def plan_pair_count(plan: dict) -> int:
    """The sealed sample size. Absent means 8 — H2591/H2612 plans predate the key."""
    return int(plan.get('pair_count') or PAIR_COUNT)


def plan_max_calls(plan: dict) -> int:
    """The sealed call ceiling. Always 2 x pair_count; read from the plan, never assumed."""
    return int(plan.get('max_calls') or MAX_CALLS)

#: Canonical PREP block delimiters. Exactly one opener and one closer may appear in a
#: B-arm prompt; the A-arm prompt must contain neither.
PREP_OPEN = '=== PREP CONTEXT (advisory; non-promotable; TM writes forbidden) ==='
PREP_CLOSE = '=== END PREP CONTEXT ==='

STRATA = ('simple', 'polysemous', 'markup_heavy', 'long_monster')

#: The two call SHAPES production uses. `whole` sends one card per call; `fragment` sends one
#: presplit GROUP per call, which is what production does for 44 of this pool's 48 cards
#: (H2598 measured 4 whole-card / 44 presplit). The lane is sealed INTO the plan, never a
#: runtime flag — a comparison whose call shape could change between --check and --execute
#: would be measuring two different things under one hash. Plans sealed before the fragment
#: lane existed carry no `lane` key and read as `whole`, so their sealed hashes still replay.
LANES = ('whole', 'fragment')

#: Pre-declared group-selection rule, recorded verbatim in the plan for the same reason
#: SELECTION_RULE is: the sample must be fixed before any output is seen.
GROUP_SELECTION_RULE = {
    'pool': 'every fragment group of every key in the manifest\'s `presplit_keys` — one '
            'group is exactly one production agent call',
    'unit': 'a UNIT is one group: uid `<key1>#g<group_index>`, called once per arm',
    'exclusions': [
        'groups of keys production does NOT presplit: those cards go whole, and the '
        'whole-card lane already measures them',
    ],
    'strata': {
        'multi_fragment': 'groups carrying 2+ fragments — the "one call, several senses" '
                          'shape, ranked by fragment count descending',
        'solo_fragment': 'groups carrying exactly 1 fragment — the "one call, one sense" '
                         'shape, ranked by (key1, group_index) ascending',
    },
    'order': [
        'take 4 groups from each stratum, not 8 by size alone: measured on the H2591 '
        'manifest, 31 of 46 groups (67 %) are SOLO, so a sample ranked by size only would '
        'draw entirely from the multi-fragment minority — the same "measures the lane it '
        'is not about" error H2598 caught in the whole-card lane, one level down',
        'AT MOST 2 groups per parent card, applied across both strata — without it a single '
        'citation-dense card (samIpa: 31 solo groups) supplies the whole sample',
        'if a stratum cannot fill its 4, take the shortfall from the other stratum and '
        'record the substitution; if the per-card cap blocks the sample, relax it to 3 then '
        '4 and record that too — never hide a thin draw',
    ],
    'frozen': 'units are sealed into plan.json before any call; a failed group is never replaced',
}

#: Pre-declared pool rule for the WHOLE-CARD lane (H2630, Option A). Unlike SELECTION_RULE
#: and GROUP_SELECTION_RULE this is not a *sampling* rule at all: production takes exactly
#: four of this pool's 48 cards whole, so the four ARE the lane. Recorded verbatim in the
#: plan for the same reason the other two are — what was taken, and why, fixed before any
#: output is seen.
WHOLE_CARD_POOL_RULE = {
    'pool': 'every key production does NOT presplit, classified with production\'s own '
            'predicate gen_opt_harness2._presplit_hit at its own cite floor and sense '
            'budget — read from the module, never restated here',
    'unit': 'a UNIT is one whole card, called once per arm, exactly as the whole lane does',
    'census_not_sample': 'the whole-card pool holds exactly as many cards as the plan takes, '
                         'so this is the POPULATION of the 8 % lane, not a draw from it. No '
                         'stratification is possible or needed; the four strata of '
                         'SELECTION_RULE collapse by construction.',
    'exclusions': [
        'synthetic fixtures and content duplicates, on SELECTION_RULE\'s terms — the pool '
        'is the same 48 distinct real cards, only classified rather than ranked',
        'every card production presplits: those go through the fragment lane, which H2612 '
        'qualifies separately',
    ],
    'known_bias': 'whole-card cards are citation-light by construction — that is WHY '
                  'production takes them whole — so this lane cannot exhibit the '
                  'citation-dense failure mode at all',
    'frozen': 'keys are sealed into plan.json before any call; a failed card is never replaced',
}

#: Pre-declared, order-sensitive selection rule. Recorded verbatim in the plan so the
#: sample can never be re-chosen after seeing output.
SELECTION_RULE = {
    'pool': 'every key with both <key>.raw.txt and <key>.portrait.json in the pilot input dir',
    'exclusions': [
        'synthetic fixtures: any key whose stem starts with a SYNTHETIC_PREFIXES entry '
        '(the curated canary is a control, not a real card; H2591 requires eight REAL cards)',
        'content duplicates: cards whose raw bytes hash identically are ONE card under two '
        'spellings (e.g. vyavasTA / vyavas_t_a). Keeping both would silently halve the '
        'sample — three cards masquerading as six. The lexicographically first key1 wins.',
    ],
    'metrics': {
        'bytes': 'len(raw.encode("utf-8"))',
        'placeholders': 'len(pwg_mask.mask(raw)[1])',
        'source_senses': 'sense_count.count_source_senses(raw)',
        'ls': 'raw.count("<ls")',
        'content_sha256': 'sha256(raw.encode("utf-8")) — the dedupe key, not a stratifier',
    },
    'order': [
        'long_monster: bytes >= 12000 (prep_pack.MONSTER_BYTES); if fewer than 2 qualify, '
        'the 2 largest by bytes. Tie-break key1 ascending.',
        'markup_heavy: of the remainder, the 2 highest placeholders. Tie-break key1 ascending.',
        'polysemous: of the remainder, source_senses >= 6 (prep_pack.POLYSEMY_SENSE_FLOOR), '
        'the 2 highest source_senses; if fewer than 2 qualify, the 2 highest overall. '
        'Tie-break key1 ascending.',
        'simple: of the remainder, the 2 smallest bytes among source_senses <= 2 and '
        'placeholders <= 2; if fewer than 2 qualify, the 2 smallest bytes overall. '
        'Tie-break key1 ascending.',
    ],
    'frozen': 'keys are sealed into plan.json before any call; a failed card is never replaced',
}


class FenceFailure(RuntimeError):
    """A fail-closed condition. Never downgraded to a warning, never retried.

    ``report`` carries whatever the check had already established when the gate fired, so a
    blocked run still leaves per-condition evidence instead of a bare refusal string. It
    cannot loosen the gate: ``--execute`` keys off ``ok``, which a blocked report never has.
    """

    def __init__(self, message, report=None):
        super().__init__(message)
        self.report = report


# --------------------------------------------------------------------------- hashing

def canonical_bytes(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':')).encode('utf-8')


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode('utf-8'))


def sha256_file(path: str) -> str:
    with open(path, 'rb') as handle:
        return sha256_bytes(handle.read())


def atomic_json(path: str, value) -> str:
    """Write once, never silently overwrite with different bytes (immutable artifact)."""
    encoded = json.dumps(value, ensure_ascii=False, indent=1, sort_keys=True) + '\n'
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    if os.path.exists(path):
        with open(path, encoding='utf-8') as handle:
            if handle.read() != encoded:
                raise FenceFailure('immutable artifact would change: %s' % path)
        return path
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(encoded)
    os.replace(tmp, path)
    return path


# --------------------------------------------------------------------------- selection

#: Curated synthetic controls that live beside real cards in the pilot input dir. They ride
#: the production path deliberately (H2245) but they are not evidence about real PWG text.
SYNTHETIC_PREFIXES = ('dq_canary', '_selftest', 'synthetic')


def card_metrics(raw: str) -> dict:
    return {
        'bytes': len(raw.encode('utf-8')),
        'placeholders': len(pwg_mask.mask(raw)[1]),
        'source_senses': count_source_senses(raw),
        'ls': raw.count('<ls'),
        'content_sha256': sha256_text(raw),
    }


def default_input_dir() -> str:
    """First pilot root that actually holds `input/`.

    In a linked worktree the pilot tree exists but `input/` is gitignored and lives only
    on the main checkout, so taking `_pilot_dirs()[0]` blindly yields an empty pool and a
    selection that "succeeds" over nothing. A worktree also carries an EMPTY `input/`, so
    existence is not enough — the directory must actually hold cards.
    """
    for pilot in prep_pack._pilot_dirs():
        candidate = os.path.join(pilot, 'input')
        if os.path.isdir(candidate) and any(
                name.endswith('.raw.txt') for name in os.listdir(candidate)):
            return candidate
    raise FenceFailure('no pilot input/ directory found on any known pilot root')


def pool_metrics(input_dir: str) -> dict[str, dict]:
    """Real, content-distinct cards in ``input_dir``, with their metrics.

    Two exclusions, both learned from the actual directory rather than assumed: it holds
    the curated canary fixture beside real cards, and it holds several cards TWICE under a
    transliterated and a safe-name spelling with byte-identical raws (``vyavasTA`` /
    ``vyavas_t_a``). Selecting from the bare listing produced a "stratified eight" that was
    really five cards — three of them counted twice — which would have made every
    per-stratum claim in the receipt false.
    """
    out, seen_content = {}, {}
    for name in sorted(os.listdir(input_dir)):
        if not name.endswith('.raw.txt'):
            continue
        key = name[:-len('.raw.txt')]
        if key.startswith(SYNTHETIC_PREFIXES):
            continue
        if not os.path.exists(os.path.join(input_dir, key + '.portrait.json')):
            continue
        with open(os.path.join(input_dir, name), encoding='utf-8', errors='replace') as handle:
            raw = handle.read()
        metrics = card_metrics(raw)
        first = seen_content.get(metrics['content_sha256'])
        if first is not None:
            out[first].setdefault('duplicate_spellings', []).append(key)
            continue
        seen_content[metrics['content_sha256']] = key
        out[key] = metrics
    return out


def select_keys(metrics: dict[str, dict], fallbacks: dict | None = None) -> dict[str, list[str]]:
    """Apply SELECTION_RULE. Deterministic: ties always break on key1 ascending.

    ``fallbacks`` (optional sink) records, per stratum, whether the qualifying predicate
    was satisfiable at all. A stratum that fell back is still two cards — but they are
    "the two most X available", not "two cards that met the X threshold", and a receipt
    that blurred those would overstate what the sample covers.
    """
    remaining = dict(metrics)

    def take(name, rank, predicate=None, count=2):
        pool = [k for k in sorted(remaining) if predicate is None or predicate(remaining[k])]
        fell_back = len(pool) < count
        if fell_back:                               # documented fallback: drop the predicate
            pool = sorted(remaining)
        pool.sort(key=lambda k: (rank(remaining[k]), k))
        picked = pool[:count]
        for key in picked:
            remaining.pop(key, None)
        if fallbacks is not None:
            fallbacks[name] = fell_back
        return picked

    chosen = {
        'long_monster': take('long_monster', lambda m: -m['bytes'],
                             lambda m: m['bytes'] >= prep_pack.MONSTER_BYTES),
        'markup_heavy': take('markup_heavy', lambda m: -m['placeholders']),
        'polysemous': take('polysemous', lambda m: -m['source_senses'],
                           lambda m: m['source_senses'] >= prep_pack.POLYSEMY_SENSE_FLOOR),
        'simple': take('simple', lambda m: m['bytes'],
                       lambda m: m['source_senses'] <= 2 and m['placeholders'] <= 2),
    }
    flat = [k for stratum in STRATA for k in chosen[stratum]]
    if len(set(flat)) != PAIR_COUNT:
        raise FenceFailure('selection did not yield %d distinct keys: %r' % (PAIR_COUNT, flat))
    return chosen


def select_whole_card_keys(metrics: dict[str, dict]) -> list[str]:
    """Apply WHOLE_CARD_POOL_RULE: the keys production takes WHOLE, in a fixed order.

    Classification is production's own `_presplit_hit`, called exactly as
    `h2598/b2_whole_card_pool.py` calls it — the thresholds live in that module and are
    never restated here, so if production retunes them this lane's membership moves with it
    instead of silently going stale.
    """
    import gen_opt_harness2                                  # noqa: WPS433

    whole = []
    for key in sorted(metrics):
        value = metrics[key]
        cite_hit, sense_hit = gen_opt_harness2._presplit_hit(
            value['ls'], value['source_senses'], gen_opt_harness2.OUTPUT_BUDGET)
        if not (cite_hit or sense_hit):
            whole.append(key)
    if not whole:
        raise FenceFailure('no card in this pool is taken whole by production — there is no '
                           'whole-card lane to qualify here')
    return whole


def paired_order(keys: list[str]) -> list[dict]:
    """A1,B1,B2,A2,A3,B3,B4,A4,… — alternating pair order against temporal drift.

    Every key is called once per arm; the arm that goes FIRST alternates by pair index, so
    a monotone drift (warming caches, degrading service) cannot load onto one arm.
    """
    steps = []
    for index, key in enumerate(keys):
        first, second = ('A', 'B') if index % 2 == 0 else ('B', 'A')
        steps.append({'ordinal': 2 * index + 1, 'arm': first, 'key': key, 'pair': index})
        steps.append({'ordinal': 2 * index + 2, 'arm': second, 'key': key, 'pair': index})
    return steps


# --------------------------------------------------------------------------- prompts

def context_block(context: dict) -> str:
    """One canonical, delimited PREP block. Canonical JSON so bytes are replayable."""
    return ('\n\n' + PREP_OPEN + '\n'
            + canonical_bytes(context).decode('utf-8') + '\n'
            + PREP_CLOSE + '\n')


def unit_id(key: str, group_index: int) -> str:
    """The fragment lane's unit address. `#` cannot occur in a key1, so it never collides."""
    return '%s#g%d' % (key, group_index)


def unit_parent(card: dict, uid: str) -> str:
    """The key1 a unit belongs to. Whole-lane plans predate `key1` here and ARE their key."""
    return card.get('key1') or uid


def manifest_group(manifest: dict, key: str, group_index: int) -> list:
    groups = (manifest.get('fragment_groups') or {}).get(key) or []
    if group_index < 0 or group_index >= len(groups):
        raise FenceFailure('manifest carries no group %d for %r' % (group_index, key))
    return groups[group_index]


def select_groups(manifest: dict, relaxations: list | None = None,
                  pair_count: int = PAIR_COUNT) -> list[dict]:
    """Apply GROUP_SELECTION_RULE. Deterministic: ties always break on (key1, index) ascending.

    ``relaxations`` (optional sink) records each per-card cap that had to be loosened, so a
    sample drawn from a thin pool says so in the plan instead of looking like a clean draw.
    """
    pool = []
    for key in sorted(manifest.get('presplit_keys') or []):
        for index, group in enumerate((manifest.get('fragment_groups') or {}).get(key) or []):
            pool.append({'key1': key, 'group_index': index, 'fragments': len(group)})
    if not pool:
        raise FenceFailure('manifest declares no presplit keys — there is no fragment lane '
                           'to qualify here')
    multi = sorted((u for u in pool if u['fragments'] > 1),
                   key=lambda u: (-u['fragments'], u['key1'], u['group_index']))
    solo = sorted((u for u in pool if u['fragments'] == 1),
                  key=lambda u: (u['key1'], u['group_index']))
    share = pair_count // 2

    def draw(cap):
        chosen, per_card, notes = [], {}, []
        for stratum, ranked, want in (('multi_fragment', multi, share),
                                      ('solo_fragment', solo, share)):
            taken = 0
            for unit in ranked:
                if taken >= want or per_card.get(unit['key1'], 0) >= cap:
                    continue
                per_card[unit['key1']] = per_card.get(unit['key1'], 0) + 1
                chosen.append(dict(unit, stratum=stratum))
                taken += 1
            if taken < want:
                notes.append({'stratum': stratum, 'drawn': taken, 'wanted': want})
        # Backfill the shortfall from whichever stratum still has room, in rank order.
        if len(chosen) < pair_count:
            picked = {(u['key1'], u['group_index']) for u in chosen}
            for stratum, ranked in (('multi_fragment', multi), ('solo_fragment', solo)):
                for unit in ranked:
                    if len(chosen) == pair_count:
                        break
                    if (unit['key1'], unit['group_index']) in picked:
                        continue
                    if per_card.get(unit['key1'], 0) >= cap:
                        continue
                    per_card[unit['key1']] = per_card.get(unit['key1'], 0) + 1
                    chosen.append(dict(unit, stratum=stratum, substituted=True))
                    picked.add((unit['key1'], unit['group_index']))
        return chosen, notes

    for cap in (2, 3, 4):
        chosen, notes = draw(cap)
        if len(chosen) == pair_count:
            if relaxations is not None:
                if cap > 2:
                    relaxations.append({'per_card_cap': cap, 'reason':
                                        'fewer than %d groups survive a cap of 2' % pair_count})
                relaxations.extend(dict(note, reason='stratum could not fill its share; the '
                                        'shortfall was substituted from the other stratum')
                                   for note in notes)
            return sorted(chosen, key=lambda u: (-u['fragments'], u['key1'], u['group_index']))
    raise FenceFailure('manifest yields only %d selectable groups, need %d'
                       % (len(pool), pair_count))


def production_prompt(manifest: dict, card: dict, uid: str) -> str:
    """Arm A for either lane: the production builder's bytes, untouched.

    Whole lane is `build_prompt`; fragment lane is `build_fragment_prompt`, the same function
    `pwg_batch` and `headless_worker` call to issue a real presplit call. Neither is
    re-implemented here — arm A means "what production would send", and the only way to keep
    that true across releases is to call production's own builder.
    """
    key = unit_parent(card, uid)
    if (card.get('lane') or 'whole') == 'whole':
        return build_prompt(manifest, [key])
    group = manifest_group(manifest, key, card['group_index'])
    return build_fragment_prompt(manifest, key, group, list(card['indices']))


def arm_prompts(manifest: dict, key: str, context: dict, card: dict | None = None
                ) -> tuple[str, str]:
    """(arm A, arm B). A is production, untouched; B is A plus exactly one PREP block."""
    prompt_a = production_prompt(manifest, card or {}, key)
    if PREP_OPEN in prompt_a or PREP_CLOSE in prompt_a:
        raise FenceFailure('production prompt already contains a PREP delimiter for %r' % key)
    prompt_b = prompt_a + context_block(context)
    if not prompt_b.startswith(prompt_a):
        raise FenceFailure('arm B is not a byte-exact extension of arm A for %r' % key)
    if prompt_b.count(PREP_OPEN) != 1 or prompt_b.count(PREP_CLOSE) != 1:
        raise FenceFailure('arm B must carry exactly one PREP block for %r' % key)
    return prompt_a, prompt_b


# --------------------------------------------------------------------------- plan

def load_contexts(context_dir: str, keys: list[str]) -> dict[str, dict]:
    """Read + re-verify each sealed context. A hash that does not replay is fatal."""
    out = {}
    for key in keys:
        try:
            from safe_filename import safe_name           # noqa: WPS433
            stem = safe_name(key)
        except Exception:                                  # noqa: BLE001
            stem = key
        path = os.path.join(context_dir, '%s.context.json' % stem)
        if not os.path.exists(path):
            raise FenceFailure('sealed context missing for %r: %s' % (key, path))
        with open(path, encoding='utf-8') as handle:
            value = json.load(handle)
        prep_pack.verify_compact_context(value)            # schema + hash + TM fence
        if value.get('key1') != key:
            raise FenceFailure('context key mismatch: %r carries %r' % (key, value.get('key1')))
        out[key] = {'path': path, 'context': value}
    return out


def unit_specs(manifest: dict, lane: str, relaxations: list | None = None,
               pair_count: int = PAIR_COUNT) -> list[dict]:
    """The plan's units, in sealed order: one card per unit (whole) or one group (fragment)."""
    if lane == 'whole':
        keys = list(manifest.get('inputs') or {})
        if len(keys) != pair_count:
            raise FenceFailure('manifest must carry exactly %d keys, found %d'
                               % (pair_count, len(keys)))
        return [{'uid': key, 'key1': key, 'lane': 'whole'} for key in keys]
    specs = []
    for unit in select_groups(manifest, relaxations, pair_count):
        key, index = unit['key1'], unit['group_index']
        group = manifest_group(manifest, key, index)
        specs.append({'uid': unit_id(key, index), 'key1': key, 'lane': 'fragment',
                      'group_index': index, 'indices': list(range(len(group))),
                      'group_fragments': len(group), 'stratum': unit['stratum']})
    return specs


def build_plan(manifest_path: str, context_dir: str, *, model: str = REQUIRED_MODEL,
               output_limit: int = OUTPUT_LIMIT, selection: dict | None = None,
               lane: str = 'whole', pair_count: int = PAIR_COUNT) -> dict:
    """Seal the immutable plan. Carries no clock reading, so it replays byte-identically."""
    if lane not in LANES:
        raise FenceFailure('unknown lane %r; expected one of %r' % (lane, list(LANES)))
    if not isinstance(pair_count, int) or not 1 <= pair_count <= PAIR_COUNT:
        raise FenceFailure('pair_count must be an int in 1..%d; a plan may shrink the '
                           'sample, never grow it past the ceiling this rig was '
                           'authorized for' % PAIR_COUNT)
    manifest_sha = sha256_file(manifest_path)
    with open(manifest_path, encoding='utf-8') as handle:
        manifest = json.load(handle)
    relaxations = []
    specs = unit_specs(manifest, lane, relaxations, pair_count)
    keys = [spec['uid'] for spec in specs]
    contexts = load_contexts(context_dir, sorted({spec['key1'] for spec in specs}))

    cards, prompts = {}, {}
    for spec in specs:
        key, parent = spec['uid'], spec['key1']
        context = contexts[parent]['context']
        evidence = context.get('source_evidence') or {}
        card = {
            'context_path': os.path.relpath(contexts[parent]['path'],
                                            os.path.dirname(manifest_path)),
            'context_sha256': context['context_sha256'],
            'prep_semantic_sha256': context['prep_semantic_sha256'],
            'source_kind': evidence.get('kind'),
            'source_sha256': evidence.get('sha256'),
            'manifest_sha256_in_context': evidence.get('manifest_sha256'),
            'route_hint': context.get('route_hint'),
            'sense_count': context.get('sense_count'),
            'skeleton_tokens': det_gate.TOK.findall(
                manifest['inputs'][parent].get('skeleton') or ''),
            'source_senses': manifest['inputs'][parent].get('source_senses'),
        }
        if spec['lane'] == 'fragment':
            group = manifest_group(manifest, parent, spec['group_index'])
            card.update({
                'lane': 'fragment', 'key1': parent,
                'group_index': spec['group_index'], 'indices': list(spec['indices']),
                'group_fragments': spec['group_fragments'], 'stratum': spec['stratum'],
                # Each fragment is scored against ITS OWN skeleton, exactly as
                # `headless_worker.heal_group` accepts a fragment in production. Scoring a
                # fragment against the whole-card token map would read as mass loss and
                # invert the verdict.
                'fragments': [
                    {'index': index, 'frag_key': '%s_f%d' % (parent, index),
                     'skeleton_tokens': det_gate.TOK.findall(group[index].get('skeleton') or '')}
                    for index in spec['indices']],
            })
        prompt_a, prompt_b = arm_prompts(manifest, key, context, card)
        prompts[key] = {
            'A': {'sha256': sha256_text(prompt_a), 'bytes': len(prompt_a.encode('utf-8'))},
            'B': {'sha256': sha256_text(prompt_b), 'bytes': len(prompt_b.encode('utf-8'))},
        }
        cards[key] = card

    plan = {
        'schema': PLAN_SCHEMA,
        'handoff': 'H2591',
        'design': 'paired 8-card baseline(A) vs PREP(B) qualification; n=8 is descriptive',
        'manifest_path': os.path.abspath(manifest_path),
        'manifest_sha256': manifest_sha,
        'model': model,
        'output_limit': output_limit,
        'output_schema_sha256': sha256_bytes(canonical_bytes(manifest.get('output_schema'))),
        'max_calls': 2 * pair_count,
        'selection_rule': SELECTION_RULE,
        'strata': selection or {},
        'keys': keys,
        'order': paired_order(keys),
        'cards': cards,
        'prompts': prompts,
        'prep_delimiters': {'open': PREP_OPEN, 'close': PREP_CLOSE},
        'argv_sha256': sha256_bytes(canonical_bytes(
            [a for a in build_argv({'model': model}, manifest) if a != 'claude'])),
        'known_non_equivalences': [
            'whole-card single call per arm: production would PRESPLIT six of these eight '
            'cards into fragments (the generator reported 47 expected agent calls for this '
            'manifest). The prompt BYTES are production bytes, the call SHAPE is not. Both '
            'arms are affected identically, so the paired A-vs-B comparison is unharmed; '
            'the absolute wall-clock and token figures are NOT production figures and must '
            'not be quoted as such.',
            'manifest schema is pwg.headless_execution_manifest.v1 (unbound): this rig does '
            'not run through the coordinator/profile lane, so it carries no profile slot. '
            'It is a measurement rig, never a bulk execution path.',
            'the manifest declares model claude-sonnet-5 as the LANE default; both arms '
            'explicitly request %s and the returned model is attested per call.' % model,
        ],
        'go_rule': ('GO only if PREP loses at most one additional audited card AND improves '
                    'wall time or total non-cache tokens by more than 10%; otherwise NO-GO'),
        'fences': ['no deepseek call', 'no store/TM/promotion/default write',
                   'fuzzy TM hit is never exact-content reuse', 'no automatic retry',
                   'no expansion beyond eight pairs'],
    }
    if lane != 'whole':
        # Keyed only on the fragment lane so a whole-card plan sealed before this lane
        # existed still recomputes its ORIGINAL hash — H2591's sealed plan must keep
        # verifying, and a plan whose hash moves under a refactor is not a sealed plan.
        plan['lane'] = lane
        plan['handoff'] = 'H2612'
        plan['design'] = ('paired 8-GROUP baseline(A) vs PREP(B) qualification on the '
                          'fragment lane; one group is one production agent call; n=8 is '
                          'descriptive')
        plan['group_selection_rule'] = GROUP_SELECTION_RULE
        plan['group_selection_relaxations'] = relaxations
        plan['known_non_equivalences'] = [
            'the call SHAPE is production\'s here — one presplit group per call, via '
            'headless_worker.build_fragment_prompt — but the rig still does not run through '
            'the coordinator/profile lane, so it carries no profile slot, no heal/bisect '
            'ladder and no kill gate. A group that would be healed or bisected in production '
            'is simply recorded as failed here. Both arms are affected identically, so the '
            'paired A-vs-B comparison is unharmed; absolute figures are not production '
            'figures.',
            'PREP context is per-CARD, and a fragment call carries only part of that card, '
            'so arm B gives a group the whole card\'s context. That is the design under '
            'test, not a defect — but it means arm B\'s context block does not shrink with '
            'the group, and a cost comparison must read it that way.',
            'manifest schema is pwg.headless_execution_manifest.v1 (unbound): a measurement '
            'rig, never a bulk execution path.',
            'the manifest declares model claude-sonnet-5 as the LANE default; both arms '
            'explicitly request %s and the returned model is attested per call.' % model,
        ]
    if pair_count != PAIR_COUNT:
        # Keyed the same way `lane` is, and for the same reason: a plan sealed at the default
        # eight must recompute its ORIGINAL hash, so the key only appears when it carries
        # information. H2630's Option A is the first plan to seal it.
        plan['pair_count'] = pair_count
        plan['handoff'] = 'H2630'
        plan['design'] = (
            'paired %d-card baseline(A) vs PREP(B) qualification on the WHOLE-CARD lane, '
            'the %d cards production does not presplit; n=%d is descriptive and the four '
            'strata collapse — see whole_card_pool_rule' % (pair_count, pair_count, pair_count))
        plan['whole_card_pool_rule'] = WHOLE_CARD_POOL_RULE
        plan['known_non_equivalences'] = [
            'production does not PRESPLIT these %d cards (H2598 measured 4 whole / 44 '
            'presplit, and this manifest\'s presplit_keys is empty), but it does BATCH them: '
            'the generator packs them 2-per-agent-call, so production issues 2 calls where '
            'this rig issues %d per arm. The prompt bytes are production\'s and the cards are '
            'un-split, but "whole-card lane" means un-split, NOT one-card-per-call — an '
            'earlier draft of this rig claimed the call shape was production\'s here, and the '
            'manifest refutes it. Both arms are affected identically, so the paired A-vs-B '
            'comparison is unharmed; absolute wall-clock and token figures are not production '
            'figures and must not be quoted as such.' % (pair_count, pair_count),
            'what this buys is a verdict about the 8 %% lane only; the 92 %% lane is H2612.',
            'n=%d, not 8: the whole-card pool holds exactly %d cards, so the sample is the '
            'POPULATION of this lane rather than a draw from it. There is no sampling error '
            'to quote and no strata to balance — both are properties of a census, not '
            'weaknesses to route around, but the loss of statistical power relative to n=8 '
            'is real and a receipt must not read as if it were an eight-card result.'
            % (pair_count, pair_count),
            'whole-card cards are citation-light BY CONSTRUCTION (they fall under the '
            'presplit predicate\'s cite floor and sense budget), so this lane cannot exhibit '
            'the citation-dense failure mode at all. A clean result here is not evidence '
            'about dense cards.',
            'manifest schema is pwg.headless_execution_manifest.v1 (unbound): a measurement '
            'rig, never a bulk execution path.',
            'the manifest declares model claude-sonnet-5 as the LANE default; both arms '
            'explicitly request %s and the returned model is attested per call.' % model,
        ]
        plan['fences'] = ['no deepseek call', 'no store/TM/promotion/default write',
                          'fuzzy TM hit is never exact-content reuse', 'no automatic retry',
                          'no expansion beyond %d pairs' % pair_count]
    plan['plan_sha256'] = sha256_bytes(canonical_bytes(
        {k: v for k, v in plan.items() if k != 'plan_sha256'}))
    return plan


def resolve_manifest(plan: dict, manifest_path: str | None = None) -> str:
    """Locate the sealed manifest, verifying it by CONTENT rather than by path.

    The plan records the absolute path it was sealed from, which is a fact about one
    machine's disk at one moment — a per-handoff worktree that gets garbage-collected the
    moment its PR lands. Identity, though, is `manifest_sha256`, so a relocated checkout is
    not a broken plan. Resolution order: an explicit `--manifest`, the sealed absolute path,
    then the same basename beside the plan. Whichever is found must hash to the sealed
    digest — a path override can move the file, never change which bytes count.
    """
    sealed = plan['manifest_path']
    candidates = [manifest_path] if manifest_path else []
    candidates.append(sealed)
    candidates.append(os.path.join(os.path.dirname(os.path.abspath(plan['__plan_file__']))
                                   if plan.get('__plan_file__') else os.getcwd(),
                                   os.path.basename(sealed)))
    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            if sha256_file(candidate) != plan['manifest_sha256']:
                raise FenceFailure(
                    'manifest at %s does not match the sealed SHA-256 — these are different '
                    'bytes, not a relocated file' % candidate)
            return candidate
    raise FenceFailure('sealed manifest not found; tried: %r' % [c for c in candidates if c])


def verify_plan_hash(plan: dict) -> None:
    claimed = plan.get('plan_sha256')
    recomputed = sha256_bytes(canonical_bytes(
        {k: v for k, v in plan.items()
         if k not in ('plan_sha256', '__plan_file__')}))
    if claimed != recomputed:
        raise FenceFailure('plan hash mismatch: sealed %r recomputed %r' % (claimed, recomputed))


# --------------------------------------------------------------------------- billing

def credit_evidence(manifest: dict) -> tuple[bool, str | None]:
    """Affirmative local evidence that the Max Agent SDK credit was claimed.

    Absent it, billing is UNKNOWN — never silently priced from ``total_cost_usd`` — and
    ``--execute`` refuses without explicit human authorisation.
    """
    execution = manifest.get('execution') or {}
    claimed = execution.get('agent_sdk_credit_claimed') is True
    evidence = execution.get('agent_sdk_credit_claim_evidence')
    if claimed and isinstance(evidence, str) and evidence.strip():
        return True, evidence.strip()
    return False, None


# --------------------------------------------------------------------------- check

def check(plan: dict, *, ledger_path: str, run_id: str, authorize_unknown_billing: bool = False,
          forbid_network: bool = True, manifest_path: str | None = None) -> dict:
    """Offline, fail-closed. Returns the check report; raises FenceFailure on any breach.

    ``forbid_network`` installs a socket trap for the duration, so "this made no transport
    call" is proven by the process refusing to make one, not asserted in prose.
    """
    verify_plan_hash(plan)
    report = {'schema': 'pwg.prep_context_comparison_check.v1',
              'plan_sha256': plan['plan_sha256'], 'conditions': {}, 'network_calls': 0}

    trap = _NetworkTrap() if forbid_network else None
    if trap:
        trap.install()
    try:
        resolved = resolve_manifest(plan, manifest_path)
        report['manifest_resolved_at'] = resolved
        with open(resolved, encoding='utf-8') as handle:
            manifest = json.load(handle)

        # (1) one immutable manifest source + manifest SHA per key
        for key in plan['keys']:
            card = plan['cards'][key]
            if unit_parent(card, key) not in (manifest.get('inputs') or {}):
                raise FenceFailure('key %r absent from the manifest inputs' % key)
            if card['source_kind'] != 'execution_manifest':
                raise FenceFailure('context for %r is not manifest-sourced: %r'
                                   % (key, card['source_kind']))
            if card['manifest_sha256_in_context'] != plan['manifest_sha256']:
                raise FenceFailure('context for %r binds a different manifest SHA' % key)
            if not card['source_sha256']:
                raise FenceFailure('context for %r carries no source SHA' % key)
        report['conditions']['immutable_manifest_source'] = True

        # (2) valid, hash-replay-identical pwg.prep_context.v1
        # Keyed by UNIT, not by card: on the fragment lane several units share one parent
        # card's context, and each unit's sealed hash must be re-verified in its own right.
        contexts = {}
        base = os.path.dirname(resolved)
        for key in plan['keys']:
            path = os.path.normpath(os.path.join(base, plan['cards'][key]['context_path']))
            with open(path, encoding='utf-8') as handle:
                value = json.load(handle)
            prep_pack.verify_compact_context(value)
            if value['context_sha256'] != plan['cards'][key]['context_sha256']:
                raise FenceFailure('context for %r no longer replays its sealed hash' % key)
            if value['prep_semantic_sha256'] != plan['cards'][key]['prep_semantic_sha256']:
                raise FenceFailure('semantic PREP hash drifted for %r' % key)
            contexts[key] = value
        report['conditions']['context_hash_replay'] = True

        # (3)+(4)+(5) prompt identity, single PREP block, shared schema/model/limit
        for key in plan['keys']:
            card = plan['cards'][key]
            prompt_a, prompt_b = arm_prompts(manifest, key, contexts[key], card)
            if sha256_text(prompt_a) != plan['prompts'][key]['A']['sha256']:
                raise FenceFailure('arm A prompt drifted from the sealed hash for %r' % key)
            if sha256_text(prompt_b) != plan['prompts'][key]['B']['sha256']:
                raise FenceFailure('arm B prompt drifted from the sealed hash for %r' % key)
            # Re-derived from the production builder a SECOND time, independently of
            # `production_prompt`, so "arm A is untouched production" is a check and not a
            # restatement of the line that just built it.
            parent = unit_parent(card, key)
            if (card.get('lane') or 'whole') == 'fragment':
                expected = build_fragment_prompt(
                    manifest, parent, manifest_group(manifest, parent, card['group_index']),
                    list(card['indices']))
            else:
                expected = build_prompt(manifest, [parent])
            if prompt_a != expected:
                raise FenceFailure('arm A is not the untouched production prompt for %r' % key)
        if plan['model'] != REQUIRED_MODEL:
            raise FenceFailure('plan model is not %s: %r' % (REQUIRED_MODEL, plan['model']))
        if plan['output_schema_sha256'] != sha256_bytes(
                canonical_bytes(manifest.get('output_schema'))):
            raise FenceFailure('output schema drifted from the sealed hash')
        if not isinstance(plan['output_limit'], int) or plan['output_limit'] <= 0:
            raise FenceFailure('output limit must be a positive integer')
        argv_sha = sha256_bytes(canonical_bytes(
            [a for a in build_argv(plan, manifest) if a != 'claude']))
        if argv_sha != plan['argv_sha256']:
            raise FenceFailure('argv drifted from the sealed hash — the arms would no '
                               'longer share schema/model/output limit')
        report['conditions']['prompt_schema_model_limit_identity'] = True
        report['conditions']['arm_a_production_unchanged'] = True
        report['conditions']['arm_b_single_prep_block'] = True

        # (6) TM fence on every context
        for key, value in contexts.items():
            policy = value.get('tm_policy') or {}
            if value.get('promotable') is not False or policy.get('may_write') is not False:
                raise FenceFailure('context for %r crossed the promotion/TM fence' % key)
            for hit in value.get('tm_hits') or []:
                if hit.get('match_type') != 'exact_content_sha' and hit.get('may_auto_reuse'):
                    raise FenceFailure('context for %r treats a fuzzy hit as reusable' % key)
        report['conditions']['tm_fence_intact'] = True

        # (7) fresh reservation ledger at the ceiling THIS plan sealed (2 x pair_count).
        # Read from the plan, never from the module: a plan checked at one ceiling and
        # executed at another is exactly the hole the sealed-plan discipline exists to close.
        ceiling = plan_max_calls(plan)
        if ceiling != 2 * plan_pair_count(plan):
            raise FenceFailure('sealed ceiling %d does not match 2 x pair_count %d'
                               % (ceiling, plan_pair_count(plan)))
        ledger = CallReservationLedger(ledger_path, run_id, max_calls=ceiling)
        snapshot = ledger.snapshot()
        if int(snapshot.get('calls_spent') or 0) != 0:
            raise FenceFailure('reservation run %r is not fresh (%d spent)'
                               % (run_id, snapshot['calls_spent']))
        if snapshot.get('max_calls') != ceiling:
            raise FenceFailure('reservation ceiling is not %d' % ceiling)
        report['conditions']['fresh_reservation_ledger'] = True

        # (8) billing evidence, or an explicit human authorisation
        claimed, evidence = credit_evidence(manifest)
        report['billing'] = {'max_agent_sdk_credit_claimed': claimed,
                             'credit_claim_evidence': evidence,
                             'billing_mode': 'max_agent_sdk_credit' if claimed else 'unknown_gateway',
                             'authorized_unknown_billing': bool(authorize_unknown_billing)}
        if not claimed and not authorize_unknown_billing:
            report['conditions']['billing_attributable_or_authorized'] = False
            raise FenceFailure(
                'no local evidence that the Max Agent SDK credit was claimed — billing is '
                'UNKNOWN; a human must authorize with --authorize-unknown-billing before '
                '--execute (missing cash USD does not invalidate token evidence, but it '
                'may not be silently priced from total_cost_usd)', report=report)
        report['conditions']['billing_attributable_or_authorized'] = True
    finally:
        if trap:
            report['network_calls'] = trap.calls
            trap.remove()
    if report['network_calls']:
        raise FenceFailure('the offline check attempted %d transport call(s)'
                           % report['network_calls'])
    report['ok'] = True
    return report


class _NetworkTrap:
    """Make an offline claim falsifiable: any socket connect during --check is a failure."""

    def __init__(self):
        self.calls = 0
        self._saved = None

    def install(self):
        import socket
        self._saved = socket.socket.connect
        trap = self

        def refuse(self_socket, *args, **kwargs):           # noqa: ANN001
            trap.calls += 1
            raise FenceFailure('offline check attempted a network connection')

        socket.socket.connect = refuse

    def remove(self):
        import socket
        if self._saved is not None:
            socket.socket.connect = self._saved
            self._saved = None


# --------------------------------------------------------------------------- calling

class CallResult(dict):
    """``{'returncode', 'stdout', 'stderr', 'wall_ms'}`` — whatever the caller produced."""


def cli_caller(argv, prompt, timeout, *, cwd=None, env=None) -> CallResult:
    """The production route: `claude -p --output-format json --json-schema …`."""
    started = time.monotonic()
    try:
        proc = subprocess.run(argv, input=prompt, text=True, encoding='utf-8',
                              capture_output=True, timeout=timeout,
                              cwd=cwd or bare_cli_cwd(), env=env or dict(os.environ))
    except subprocess.TimeoutExpired:
        return CallResult(returncode=None, stdout='', stderr='timeout',
                          wall_ms=int(timeout * 1000), timed_out=True)
    return CallResult(returncode=proc.returncode, stdout=proc.stdout or '',
                      stderr=proc.stderr or '', timed_out=False,
                      wall_ms=int((time.monotonic() - started) * 1000))


def build_argv(plan: dict, manifest: dict, claude_bin: str = 'claude') -> list[str]:
    """Identical argv for both arms — only stdin differs.

    Arm-independence is how "identical schema, model id and output limit across arms" is
    *enforced* rather than promised: there is no per-arm branch here, so the plan pinning
    ``argv_sha256`` pins every one of them at once. Turn count is deliberately NOT capped —
    H2250 measured one clean card taking three turns, so a `--max-turns 1` cap would
    truncate long cards in both arms and turn a length effect into a fake quality signal.
    """
    return claude_argv_prefix(claude_bin) + [
        '-p', '--output-format', 'json',
        '--json-schema', json.dumps(manifest['output_schema'], ensure_ascii=False,
                                    separators=(',', ':')),
        '--model', plan['model'],
        '--permission-mode', 'plan',
    ]


def audit_fragment_group(plan: dict, uid: str, structured: dict) -> dict:
    """Score a fragment GROUP exactly as production accepts one.

    `headless_worker.heal_group` accepts a fragment on two conditions and no others: the
    returned card is addressable at `<key>_f<index>`, and its `{Tn}` multiset equals that
    fragment's own skeleton's. Reusing that rule verbatim is the whole point — an audit
    invented here would be scoring the lane against a standard production does not apply,
    and scoring a fragment against the WHOLE card's token map (the obvious shortcut) reads
    as mass loss on every fragment and would invert the verdict.

    Coverage is fragments accepted over fragments requested, so a partially-returned group
    is a number rather than a bare failure.
    """
    card = plan['cards'][uid]
    fragments = card['fragments']
    by_key = card_by_key(structured.get('cards') or [])
    defects, issues, accepted = [], [], 0
    for fragment in fragments:
        returned = by_key.get(fragment['frag_key'])
        if not returned:
            defects.append('missing-or-mismatched-fragment-key')
            issues.append('%s: missing-or-mismatched-fragment-key' % fragment['frag_key'])
            continue
        if not isinstance(returned.get('records'), list) or not returned['records']:
            defects.append('schema: fragment carries no records[]')
            issues.append('%s: no records[]' % fragment['frag_key'])
            continue
        expected = collections.Counter(fragment['skeleton_tokens'])
        if card_token_multiset(returned) != expected:
            defects.append('fragment-fidelity-reject')
            issues.append('%s: fragment-fidelity-reject' % fragment['frag_key'])
            continue
        accepted += 1
    coverage = (accepted / len(fragments)) if fragments else None
    return {'schema_ok': all(not d.startswith('schema') for d in defects),
            'audited': accepted == len(fragments) and bool(fragments),
            'coverage': coverage, 'defects': sorted(set(defects)), 'issues': issues,
            'fragments_requested': len(fragments), 'fragments_accepted': accepted}


def audit_result(plan: dict, key: str, structured: dict) -> dict:
    """Schema shape + the deterministic PWG audit. Never rerolled — a failure is evidence."""
    if (plan['cards'].get(key, {}).get('lane') or 'whole') == 'fragment':
        return audit_fragment_group(plan, key, structured)
    defects = []
    card = None
    for candidate in structured.get('cards') or []:
        if candidate.get('key1') == key or candidate.get('key') == key:
            card = candidate
            break
    if card is None:
        cards = structured.get('cards') or []
        card = cards[0] if len(cards) == 1 else None
    if card is None:
        return {'schema_ok': False, 'audited': False, 'coverage': None,
                'defects': ['schema: no card for %s' % key], 'issues': []}
    if not isinstance(card.get('records'), list) or not card['records']:
        defects.append('schema: card carries no records[]')
    context = {'key1': key,
               'skeleton_tokens': list(plan['cards'][key]['skeleton_tokens']),
               'source_senses': plan['cards'][key]['source_senses'] or 0}
    verdict = det_gate.deterministic_audit(card, context, field='russian')
    for issue in verdict['issues']:
        defects.append(issue.split(':')[0].strip())
    return {'schema_ok': not defects or all(not d.startswith('schema') for d in defects),
            'audited': not verdict['issues'] and not defects,
            'coverage': verdict['coverage'], 'defects': sorted(set(defects)),
            'issues': verdict['issues']}


def execute(plan: dict, *, ledger_path: str, run_id: str, out_dir: str,
            caller=cli_caller, claude_bin: str = 'claude', timeout: float = 1800.0,
            billing: dict | None = None, manifest_path: str | None = None) -> dict:
    """Run the sealed order. Reserve BEFORE every call; finalize exactly once, after."""
    verify_plan_hash(plan)
    resolved = resolve_manifest(plan, manifest_path)
    with open(resolved, encoding='utf-8') as handle:
        manifest = json.load(handle)
    contexts = {}
    base = os.path.dirname(resolved)
    for key in plan['keys']:
        with open(os.path.normpath(os.path.join(base, plan['cards'][key]['context_path'])),
                  encoding='utf-8') as handle:
            contexts[key] = prep_pack.verify_compact_context(json.load(handle))
    # On the fragment lane several units share one parent card, so `contexts` is keyed by
    # UNIT: the same context object legitimately appears under more than one uid.

    ledger = CallReservationLedger(ledger_path, run_id, max_calls=plan_max_calls(plan))
    argv = build_argv(plan, manifest, claude_bin)
    billing = billing or {'max_agent_sdk_credit_claimed': False, 'credit_claim_evidence': None}
    os.makedirs(out_dir, exist_ok=True)

    envelopes, stopped = [], None
    for step in plan['order']:
        key, arm = step['key'], step['arm']
        envelope_path = os.path.join(out_dir, 'call.%02d.%s.%s.json'
                                     % (step['ordinal'], arm, _stem(key)))
        if os.path.exists(envelope_path):                  # crash/resume: never re-spend
            with open(envelope_path, encoding='utf-8') as handle:
                envelopes.append(json.load(handle))
            continue

        prompt_a, prompt_b = arm_prompts(manifest, key, contexts[key], plan['cards'][key])
        prompt = prompt_a if arm == 'A' else prompt_b
        prompt_sha = sha256_text(prompt)
        if prompt_sha != plan['prompts'][key][arm]['sha256']:
            raise FenceFailure('prompt drifted from the sealed hash: %s/%s' % (key, arm))

        try:
            reservation = ledger.reserve(
                'h2591-prep-context-compare', detail='%s/%s' % (key, arm),
                idempotency_key='%s:%d' % (plan['plan_sha256'], step['ordinal']))
        except CallLimitReached as exc:
            stopped = 'reservation_ceiling: %s' % exc
            break

        result = caller(argv, prompt, timeout)
        wrapper, parse_error = None, None
        try:
            wrapper = parse_cli_wrapper(result.get('stdout') or '')
        except ValueError as exc:
            parse_error = str(exc)[:400]

        returned_model = (wrapper or {}).get('modelUsage') or (wrapper or {}).get('model')
        if isinstance(returned_model, dict):
            returned_model = next(iter(returned_model), None)

        telemetry = (telemetry_from_cli_wrapper(
            wrapper, max_agent_sdk_credit=True,
            credit_claimed=bool(billing.get('max_agent_sdk_credit_claimed')),
            credit_claim_evidence=billing.get('credit_claim_evidence'))
            if wrapper is not None else unevaluable_telemetry())

        cross = usage_cross_check(telemetry, wrapper)
        telemetry, recovery = recover_usage(telemetry, wrapper, cross)

        structured, audit, failure = None, None, None
        if result.get('timed_out'):
            # MUST precede the parse check. A timed-out call returns empty stdout, which
            # never parses — so with `parse_error` first the `timeout` class was
            # unreachable by construction and every abandoned call was filed as
            # `malformed_envelope`, i.e. "the provider sent garbage" when the truth is "we
            # stopped waiting". Found by H2612's own run: ordinal 1 sat for the full 1800 s
            # and was recorded as a malformed envelope.
            failure = 'timeout'
        elif parse_error:
            failure = 'malformed_envelope'
        elif result.get('returncode'):
            # H2591: a non-zero exit is its OWN class. Five of that run's seven zero-usage
            # calls were rc=1 refusals whose `result` held an error string, and lumping
            # them under `unstructured_result` made a provider refusal look like a model
            # quality defect on a dense card.
            failure = 'cli_error_exit'
        elif cross.get('agree') is False and not recovery:
            # Strictly more informative than `missing_usage`, so it must classify FIRST:
            # a contradiction proves the tokens existed and the accounting block was
            # dropped, where `missing_usage` only says the block read empty. A RECOVERED
            # call is exempt — the number was retrieved from the validated second source,
            # so there is nothing unsound left downstream to stop for.
            failure = 'usage_contradiction'
        elif not usage_evaluable(telemetry):
            failure = 'missing_usage'
        else:
            try:
                structured = structured_from_wrapper(wrapper)
            except ValueError as exc:
                failure = 'unstructured_result'
                parse_error = str(exc)[:400]
            else:
                audit = audit_result(plan, key, structured)

        envelope = {
            'schema': ENVELOPE_SCHEMA,
            'plan_sha256': plan['plan_sha256'],
            'ordinal': step['ordinal'], 'pair': step['pair'], 'arm': arm, 'key1': key,
            'requested_model': plan['model'], 'returned_model': returned_model,
            'prompt_sha256': prompt_sha,
            'prompt_bytes': len(prompt.encode('utf-8')),
            'context_sha256': plan['cards'][key]['context_sha256'] if arm == 'B' else None,
            'wall_ms': result.get('wall_ms'),
            'returncode': result.get('returncode'),
            'failure_class': failure,
            'detail': parse_error,
            'terminal': {name: (wrapper or {}).get(name) for name in TERMINAL_FIELDS},
            'usage_cross_check': cross,
            'usage_recovery': recovery,
            # For a call that yielded no structured card the returned STRING is the
            # evidence; H2591 kept only the parse error, so five failures could never be
            # diagnosed after the fact. Truncated, never dropped.
            'raw_result': (None if structured is not None else
                           str((wrapper or {}).get('result')
                               or (result.get('stdout') or ''))[:4000]),
            'telemetry': telemetry,
            'result_sha256': (sha256_bytes(canonical_bytes(structured))
                              if structured is not None else None),
            'audit': audit,
        }
        ledger.finalize(reservation, telemetry, evidence={
            'prompt_sha256': prompt_sha,
            'result_sha256': envelope['result_sha256'],
            'returned_model': returned_model,
            'ordinal': step['ordinal'],
        })
        atomic_json(envelope_path, envelope)
        envelopes.append(envelope)

        # Stop conditions — a stopped run is evidence, never an automatic retry.
        if returned_model and plan['model'] not in str(returned_model):
            stopped = 'model_substitution: requested %s, returned %r' % (
                plan['model'], returned_model)
            break
        if failure == 'timeout':
            # Ordered ahead of the unattested check because it EXPLAINS it: an abandoned
            # call names no model for an obvious reason, and reporting "paid call returned
            # no model" for a call we stopped waiting on points the next session at the
            # wrong thing. Both stop the run; only one of them says what happened.
            stopped = ('timeout at ordinal %d after %.0f s — the call did not return '
                       'within the rig\'s timeout' % (step['ordinal'],
                                                      (result.get('wall_ms') or 0) / 1000))
            break
        if not returned_model:
            # H2591 call 09 was reserved, finalized and PAID while naming no model at all,
            # and the substitution guard above waved it through because absence is not
            # substitution. A call nobody can attribute is not a weaker measurement than a
            # substituted one — it is an unattributable one, so it stops the run at call
            # time rather than being discovered at receipt time. This is deliberately
            # stricter than the `cli_error_exit` continue-rule one line down: a provider
            # refusal that still names its model is a verdict on one call, whereas an
            # unattested call leaves the ledger holding spend it cannot assign.
            stopped = 'model_unattested at ordinal %d: paid call returned no model' % (
                step['ordinal'],)
            break
        if failure in ('missing_usage', 'malformed_envelope'):
            stopped = '%s at ordinal %d' % (failure, step['ordinal'])
            break
        if failure == 'usage_contradiction':
            # Two independent token sources disagreeing is an accounting integrity breach,
            # not a slow call: whichever one is wrong, the comparison downstream is already
            # unsound. An rc=1 refusal, by contrast, is recorded and the run continues —
            # it is a provider verdict on one call, not evidence that the ledger is lying.
            stopped = ('usage_contradiction at ordinal %d: %s'
                       % (step['ordinal'], cross['contradiction']))
            break

    usage = ledger.usage()
    return {'envelopes': envelopes, 'stopped': stopped, 'ledger_usage': usage,
            'calls_spent': ledger.spent()}


#: Envelope fields that classify HOW a call ended. H2591 captured none of them, which is
#: why its seven zero-usage calls could not be told apart at the time: five were `rc=1`
#: refusals (zero usage is the documented fail-closed contract there) and two were `rc=0`
#: successes with a valid audited card and no tokens. One `subtype`/`terminal_reason`
#: reading would have split them on the spot.
TERMINAL_FIELDS = ('type', 'subtype', 'is_error', 'stop_reason', 'terminal_reason',
                   'api_error_status', 'num_turns', 'session_id', 'total_cost_usd',
                   'duration_ms', 'duration_api_ms')

#: `modelUsage` carries per-model token counts independently of the top-level `usage`
#: block. Measured 12-08-2026: on a healthy call the two agree exactly. Reading BOTH turns
#: a zeroed `usage` beside a populated `modelUsage` into a detectable contradiction rather
#: than a silent hole — which is what a token comparison needs, since a hole reads as a
#: measurement and deflates whichever arm receives it.
MODEL_USAGE_KEYS = {
    'input_tokens': 'inputTokens',
    'output_tokens': 'outputTokens',
    'cache_read_tokens': 'cacheReadInputTokens',
    'cache_creation_tokens': 'cacheCreationInputTokens',
}


def model_usage_tokens(wrapper) -> dict | None:
    """Token totals summed across every model in `modelUsage`, or None if absent."""
    blocks = (wrapper or {}).get('modelUsage')
    if not isinstance(blocks, dict) or not blocks:
        return None
    out = {name: 0 for name in MODEL_USAGE_KEYS}
    seen = False
    for block in blocks.values():
        if not isinstance(block, dict):
            continue
        seen = True
        for ours, theirs in MODEL_USAGE_KEYS.items():
            value = block.get(theirs)
            if isinstance(value, (int, float)) and value >= 0:
                out[ours] += int(value)
    return out if seen else None


def recover_usage(telemetry: dict, wrapper, cross: dict) -> tuple[dict, dict | None]:
    """Adopt `modelUsage` when the top-level `usage` block was DROPPED, and say so.

    H2591 left "2 of 16 calls reported zero usage on a clean exit" as its unexplained
    class, and B1 could only call it intermittent. H2612's measured run identified it:
    ordinal 5 came back `type: result`, `subtype: success`, `terminal_reason: completed`,
    `is_error: false`, `num_turns: 2`, `total_cost_usd: 0.4029715`, a full audited card —
    and a top-level `usage` block of all zeros beside a `modelUsage` reporting 73 620
    tokens. The tokens were spent and counted; only the accounting block was dropped.

    So this one direction of disagreement is no longer an unexplained integrity breach, and
    halting on it throws away a measurement that exists. `modelUsage` is a VALIDATED source
    here — B1 measured the two agreeing exactly on healthy calls — so adopting it recovers
    the number rather than inventing one. Every recovery is recorded on the envelope; a run
    that leans on it says so in its receipt.

    Deliberately narrow: ONLY zero-usage-beside-populated-modelUsage recovers. Any other
    disagreement (both populated and different, or `usage` populated while `modelUsage` is
    zero) stays unexplained and still stops the run.
    """
    if cross.get('agree') is not False:
        return telemetry, None
    if cross.get('usage_total') or not cross.get('model_usage_total'):
        return telemetry, None                      # not the known-dropped-block direction
    theirs = model_usage_tokens(wrapper)
    if not theirs:
        return telemetry, None
    recovered = dict(telemetry)
    recovered.update(theirs)
    recovered['cost_evaluable'] = True
    accounting = dict(recovered.get('accounting') or {})
    if accounting:
        accounting.update(theirs)
        accounting['usage_evaluable'] = True
        accounting['usage_source'] = 'modelUsage'
        recovered['accounting'] = accounting
    recovered['usage_source'] = 'modelUsage'
    return recovered, {
        'reason': 'top-level usage block was dropped; modelUsage carried the real counts',
        'adopted': theirs, 'model_usage_total': cross['model_usage_total'],
    }


def usage_cross_check(telemetry: dict, wrapper) -> dict:
    """Compare the two independent token sources and name any disagreement."""
    mine = {name: int(telemetry.get(name) or 0) for name in MODEL_USAGE_KEYS}
    theirs = model_usage_tokens(wrapper)
    report = {'usage_total': sum(mine.values()),
              'model_usage_total': None if theirs is None else sum(theirs.values()),
              'model_usage_present': theirs is not None,
              'agree': None, 'contradiction': None}
    if theirs is None:
        return report
    report['agree'] = mine == theirs
    if not report['agree']:
        report['contradiction'] = (
            'usage=%r modelUsage=%r' % (mine, theirs)
            if report['usage_total'] else
            'top-level usage is all-zero while modelUsage reports %d token(s) — the '
            'accounting block was dropped, not the spend' % sum(theirs.values()))
    return report


def usage_evaluable(telemetry: dict) -> bool:
    """Token evidence present — deliberately NOT the same question as observed cash.

    Under a claimed Max Agent SDK credit ``usage_accounting`` sets ``observed_cash_usd``
    to null on purpose, so ``cost_evaluable`` is False for every healthy call: the CLI's
    ``total_cost_usd`` is a list/credit equivalent, never cash. Stopping the run on that
    would abort a correctly-attributed credit run at call 1. What must stop the run is
    *missing or corrupt usage*, which is exactly ``accounting.usage_evaluable``.
    """
    accounting = telemetry.get('accounting')
    if isinstance(accounting, dict) and 'usage_evaluable' in accounting:
        if accounting['usage_evaluable'] is not True:
            return False
    elif not telemetry.get('cost_evaluable'):
        return False
    # H2591 measured run: `usage_evaluable` checks the SHAPE of the usage block, not whether
    # it says anything. Seven of sixteen calls came back with every counter zeroed — two of
    # them having produced a full card that passed the deterministic audit at coverage 1.0,
    # which is arithmetically impossible. A zero-filled dict is *missing* usage wearing the
    # costume of present usage, and it is worse than an absent one: it silently deflates
    # whichever arm receives it, so the token comparison reads as a measurement instead of
    # as a hole. A completed call always consumes tokens; all-zero means the envelope did
    # not report them.
    return any(int(telemetry.get(name) or 0) > 0 for name in
               ('input_tokens', 'output_tokens', 'cache_read_tokens', 'cache_creation_tokens'))


def credit_equivalent(telemetry: dict) -> float:
    """The list/credit equivalent for one call, kept apart from observed cash."""
    accounting = telemetry.get('accounting')
    if isinstance(accounting, dict):
        for name in ('credit_equivalent_usd', 'list_equivalent_usd', 'observed_cash_usd'):
            if accounting.get(name) is not None:
                return float(accounting[name])
        return 0.0
    return float(telemetry.get('observed_cost_usd') or 0.0)


def _stem(key: str) -> str:
    try:
        from safe_filename import safe_name                 # noqa: WPS433
        return safe_name(key)
    except Exception:                                       # noqa: BLE001
        return key


# --------------------------------------------------------------------------- receipt

def _arm_totals(envelopes: list[dict], arm: str) -> dict:
    rows = [e for e in envelopes if e['arm'] == arm]
    finished = [e for e in rows if e.get('audit')]
    tokens = {name: 0 for name in ('input_tokens', 'output_tokens',
                                   'cache_read_tokens', 'cache_creation_tokens')}
    credit, wall, defects = 0.0, 0, []
    for row in rows:
        telemetry = row.get('telemetry') or {}
        for name in tokens:
            tokens[name] += int(telemetry.get(name) or 0)
        credit += credit_equivalent(telemetry)
        wall += int(row.get('wall_ms') or 0)
        defects.extend((row.get('audit') or {}).get('defects') or [])
        if row.get('failure_class'):
            defects.append(row['failure_class'])
    classes = {}
    for name in defects:
        classes[name] = classes.get(name, 0) + 1
    return {
        'calls': len(rows),
        'usage_unevaluable_calls': sum(
            1 for e in rows if not usage_evaluable(e.get('telemetry') or {})),
        'unattested_model_calls': sum(
            1 for e in rows if e.get('returned_model') != REQUIRED_MODEL),
        'audited_pass': sum(1 for e in finished if e['audit']['audited']),
        'schema_pass': sum(1 for e in finished if e['audit']['schema_ok']),
        'wall_ms_total': wall,
        'tokens': tokens,
        'non_cache_tokens': tokens['input_tokens'] + tokens['output_tokens'],
        'credit_equivalent_usd': round(credit, 6),
        'defect_classes': dict(sorted(classes.items())),
    }


def paired_deltas(envelopes: list[dict]) -> dict:
    """Wall/token margins over the units where BOTH arms returned schema.

    This is the only comparison that is about translating the same unit twice. Arm TOTALS
    are not: a failed call still contributes its wall time, so an arm that fails slowly
    hands the other arm a margin that has nothing to do with translation quality or speed.
    Both sealed runs to date fired a GO on exactly that artefact.

    Also reports how many units each arm won, because a margin carried by one unit out of
    seven is a different claim from a margin that holds across them.
    """
    produced = {arm: {e['key1']: e for e in envelopes
                      if e['arm'] == arm and e.get('result_sha256')}
                for arm in ('A', 'B')}
    units = sorted(set(produced['A']) & set(produced['B']))
    wall = {'A': 0, 'B': 0}
    tokens = {'A': 0, 'B': 0}
    faster = 0
    for unit in units:
        for arm in ('A', 'B'):
            row = produced[arm][unit]
            telemetry = row.get('telemetry') or {}
            wall[arm] += int(row.get('wall_ms') or 0)
            tokens[arm] += (int(telemetry.get('input_tokens') or 0)
                            + int(telemetry.get('output_tokens') or 0))
        if (produced['B'][unit].get('wall_ms') or 0) < (produced['A'][unit].get('wall_ms') or 0):
            faster += 1
    return {
        'units': units,
        'unit_count': len(units),
        'wall_ms_total': dict(wall),
        'non_cache_tokens': dict(tokens),
        'wall_ms_relative_gain': _relative_gain(wall['A'], wall['B']),
        'non_cache_token_relative_gain': _relative_gain(tokens['A'], tokens['B']),
        'prep_faster_units': faster,
        'basis': ('units where BOTH arms returned schema; arm totals are reported too but '
                  'are NOT the GO basis — a failed call contributes wall time and rewards '
                  'the arm that fails faster'),
    }


def build_receipt(plan: dict, run: dict, *, check_report: dict) -> dict:
    """`pwg.prep_context_comparison.v1` — the GO/NO-GO the handoff closes on."""
    envelopes = run['envelopes']
    arm_a, arm_b = _arm_totals(envelopes, 'A'), _arm_totals(envelopes, 'B')
    pair_count, ceiling = plan_pair_count(plan), plan_max_calls(plan)
    complete = (run['calls_spent'] == ceiling and not run['stopped']
                and arm_a['calls'] == pair_count and arm_b['calls'] == pair_count)

    lost = arm_a['audited_pass'] - arm_b['audited_pass']
    wall_gain = _relative_gain(arm_a['wall_ms_total'], arm_b['wall_ms_total'])
    token_gain = _relative_gain(arm_a['non_cache_tokens'], arm_b['non_cache_tokens'])
    paired = paired_deltas(envelopes)
    # The GO now keys off the PAIRED margin, over the units where BOTH arms returned
    # schema. Twice in a row the arm totals fired a GO that decomposition then withdrew:
    # H2591's +26.9 % was mostly the difference between how long each arm took to FAIL, and
    # H2612's +10.21 % rested on one arm-A refusal — remove it and the same margin inverts
    # to -8.85 %, while the honest paired figure is +4.25 %. An arm total silently rewards
    # the arm that fails FASTER, which is the opposite of what is being qualified.
    paired_wall = paired['wall_ms_relative_gain']
    paired_token = paired['non_cache_token_relative_gain']
    improves = (paired_wall is not None and paired_wall > 0.10) or \
               (paired_token is not None and paired_token > 0.10)

    # A GO must rest on evidence that exists. Token totals built over calls whose usage came
    # back zero-filled are not a measurement, and a wall-time margin is not a substitute:
    # in the H2591 run the margin was mostly the difference between how long each arm's
    # FAILED calls took to fail, which says nothing about translating a card. So any
    # unevaluable usage or unattested model forces INCONCLUSIVE, ahead of the GO arithmetic.
    holes = (arm_a['usage_unevaluable_calls'] + arm_b['usage_unevaluable_calls']
             + arm_a['unattested_model_calls'] + arm_b['unattested_model_calls'])
    if not complete or (arm_a['audited_pass'] == 0 and arm_b['audited_pass'] == 0):
        verdict = 'INCONCLUSIVE'
    elif holes:
        verdict = 'INCONCLUSIVE'
    elif lost <= 1 and improves:
        verdict = 'GO'
    else:
        verdict = 'NO-GO'

    receipt = {
        'schema': RECEIPT_SCHEMA,
        'handoff': plan.get('handoff', 'H2591'),
        'plan_sha256': plan['plan_sha256'],
        'manifest_sha256': plan['manifest_sha256'],
        'model_requested': plan['model'],
        'models_returned': sorted({str(e.get('returned_model')) for e in envelopes}),
        'n': pair_count,
        'lane': plan.get('lane', 'whole'),
        'evidence_class': ('descriptive qualification at n=%d — NOT production evidence; '
                           'a GO authorizes only a separately minted, larger, '
                           'pre-registered experiment, never a route switch' % pair_count),
        'calls_spent': run['calls_spent'],
        'call_ceiling': ceiling,
        'stopped': run['stopped'],
        'complete': complete,
        'comparison_order': [
            'schema + deterministic audit pass count',
            'attributable total wall time and model calls',
            'input/output/cache token deltas',
            'list/credit equivalent when evaluable',
            'enumerated defect classes, including SAN-LOSS and false TM reuse',
        ],
        'arm_a_baseline': arm_a,
        'arm_b_prep': arm_b,
        'deltas': {
            'audited_cards_lost_by_prep': lost,
            'wall_ms_relative_gain': wall_gain,
            'non_cache_token_relative_gain': token_gain,
            'basis': 'ARM TOTALS — reported for continuity, NOT the GO basis (see paired_deltas)',
        },
        'paired_deltas': paired,
        'billing': check_report.get('billing'),
        'go_rule': plan['go_rule'],
        'evidence_holes': {
            'usage_unevaluable_calls': (arm_a['usage_unevaluable_calls']
                                        + arm_b['usage_unevaluable_calls']),
            'unattested_model_calls': (arm_a['unattested_model_calls']
                                       + arm_b['unattested_model_calls']),
            'effect': ('any hole forces INCONCLUSIVE — a token comparison over zero-filled '
                       'usage is a hole wearing the costume of a measurement'),
            # Not a hole, but not silent either: a run that leans on the recovered second
            # source has to say which calls it leaned on, or the token axis looks uniformly
            # first-hand when part of it was reconstructed.
            'usage_recovered_from_model_usage': [
                {'ordinal': e['ordinal'], 'arm': e['arm'], 'key1': e['key1'],
                 'model_usage_total': (e.get('usage_recovery') or {}).get('model_usage_total')}
                for e in envelopes if e.get('usage_recovery')],
        },
        'verdict': verdict,
        'promotion': {'store_written': False, 'tm_written': False,
                      'promotion_journal_written': False, 'production_default_changed': False},
        'per_call': [{'ordinal': e['ordinal'], 'arm': e['arm'], 'key1': e['key1'],
                      'audited': (e.get('audit') or {}).get('audited'),
                      'coverage': (e.get('audit') or {}).get('coverage'),
                      'failure_class': e.get('failure_class'),
                      'wall_ms': e.get('wall_ms'),
                      'result_sha256': e.get('result_sha256')} for e in envelopes],
    }
    receipt['receipt_sha256'] = sha256_bytes(canonical_bytes(
        {k: v for k, v in receipt.items() if k != 'receipt_sha256'}))
    return receipt


def _relative_gain(baseline, candidate):
    """Positive = the candidate arm is cheaper/faster. None when unevaluable."""
    if not baseline or candidate is None:
        return None
    return round((baseline - candidate) / baseline, 4)


# --------------------------------------------------------------------------- CLI

def _load_plan(path: str) -> dict:
    with open(path, encoding='utf-8') as handle:
        plan = json.load(handle)
    verify_plan_hash(plan)
    # Recorded AFTER the hash check and never re-hashed: where the plan happens to sit
    # is context for resolution, not part of what the plan asserts.
    plan['__plan_file__'] = os.path.abspath(path)
    return plan


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--select', action='store_true',
                    help='apply SELECTION_RULE to the input dir and print/seal the 8 keys')
    ap.add_argument('--pool', choices=('stratified', 'whole-card'), default='stratified',
                    help='which pool --select draws from: stratified (SELECTION_RULE, the '
                         '8-card draw) or whole-card (WHOLE_CARD_POOL_RULE — every card '
                         'production takes whole, i.e. the CENSUS of the 8%% lane)')
    ap.add_argument('--pair-count', type=int, default=None,
                    help='sample size to seal into the plan; defaults to %d. May only be '
                         'LOWERED (Option A seals 4, the size of the whole-card pool).'
                         % PAIR_COUNT)
    ap.add_argument('--plan', action='store_true', help='seal the immutable plan')
    ap.add_argument('--lane', choices=LANES, default='whole',
                    help='call SHAPE to qualify: whole (one card per call, the 8%% lane) or '
                         'fragment (one presplit group per call, the 92%% lane). Sealed into '
                         'the plan at --plan time; --check and --execute read it from there.')
    ap.add_argument('--check', action='store_true', help='offline fail-closed verification')
    ap.add_argument('--execute', action='store_true', help='spend up to 16 reserved calls')
    ap.add_argument('--receipt', action='store_true', help='emit the GO/NO-GO receipt')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--input-dir', default=None)
    ap.add_argument('--manifest', default=None)
    ap.add_argument('--context-dir', default=None)
    ap.add_argument('--out-dir', default=None)
    ap.add_argument('--plan-file', default=None)
    ap.add_argument('--run-id', default='h2591')
    ap.add_argument('--claude-bin', default='claude')
    ap.add_argument('--timeout', type=float, default=1800.0)
    ap.add_argument('--authorize-unknown-billing', action='store_true',
                    help='human authorization to proceed with billing classified UNKNOWN')
    args = ap.parse_args(argv)

    if args.selftest:
        from prep_context_compare_selftest import selftest    # noqa: WPS433
        return selftest()

    if args.select and args.pool == 'whole-card':
        input_dir = args.input_dir or default_input_dir()
        metrics = pool_metrics(input_dir)
        keys = select_whole_card_keys(metrics)
        value = {'schema': 'pwg.prep_context_comparison_selection.v1',
                 'pool': 'whole-card', 'input_dir': os.path.abspath(input_dir),
                 'pool_size': len(metrics), 'whole_card_pool_rule': WHOLE_CARD_POOL_RULE,
                 'keys': keys, 'pair_count': len(keys),
                 # Stated, not implied: this is the population of the lane, so the four
                 # strata of SELECTION_RULE do not apply and are not silently omitted.
                 'strata': {}, 'strata_collapsed': True,
                 'metrics': {k: metrics[k] for k in keys}}
        if args.out_dir:
            atomic_json(os.path.join(args.out_dir, 'selection.json'), value)
        print(json.dumps(value, ensure_ascii=False, indent=1))
        return 0

    if args.select:
        input_dir = args.input_dir or default_input_dir()
        metrics = pool_metrics(input_dir)
        fallbacks = {}
        chosen = select_keys(metrics, fallbacks)
        value = {'schema': 'pwg.prep_context_comparison_selection.v1',
                 'input_dir': os.path.abspath(input_dir), 'pool_size': len(metrics),
                 'selection_rule': SELECTION_RULE, 'strata': chosen,
                 'stratum_predicate_fell_back': fallbacks,
                 'metrics': {k: metrics[k] for stratum in STRATA for k in chosen[stratum]}}
        if args.out_dir:
            atomic_json(os.path.join(args.out_dir, 'selection.json'), value)
        print(json.dumps(value, ensure_ascii=False, indent=1))
        return 0

    if args.plan:
        if not (args.manifest and args.context_dir and args.out_dir):
            ap.error('--plan needs --manifest, --context-dir and --out-dir')
        selection = None
        selection_blob = None
        selection_path = os.path.join(args.out_dir, 'selection.json')
        if os.path.exists(selection_path):
            with open(selection_path, encoding='utf-8') as handle:
                selection_blob = json.load(handle)
            selection = selection_blob.get('strata')
        pair_count = args.pair_count
        if pair_count is None:
            # A whole-card selection.json seals its own size; nothing else may change it.
            pair_count = int((selection_blob or {}).get('pair_count') or PAIR_COUNT)
        plan = build_plan(args.manifest, args.context_dir, selection=selection,
                          lane=args.lane, pair_count=pair_count)
        path = atomic_json(os.path.join(args.out_dir, 'plan.json'), plan)
        print('sealed plan %s  lane=%s  plan_sha256=%s'
              % (path, plan.get('lane', 'whole'), plan['plan_sha256']))
        if plan.get('lane') == 'fragment':
            for uid in plan['keys']:
                card = plan['cards'][uid]
                print('  %-16s %2d fragment(s)  %-15s A=%d B=%d bytes'
                      % (uid, card['group_fragments'], card['stratum'],
                         plan['prompts'][uid]['A']['bytes'],
                         plan['prompts'][uid]['B']['bytes']))
            for note in plan['group_selection_relaxations']:
                print('  RELAXED: %s' % json.dumps(note, ensure_ascii=False, sort_keys=True))
        return 0

    if args.check:
        plan = _load_plan(args.plan_file)
        out_dir = args.out_dir or os.path.dirname(os.path.abspath(args.plan_file))
        # A breach still leaves a durable artifact: "the gate fired, here is which condition
        # and why" is evidence a later session needs, and writing it cannot loosen the gate
        # because --execute refuses anything whose report is not ok.
        try:
            report = check(plan, ledger_path=os.path.join(out_dir, 'call_reservation.json'),
                           run_id=args.run_id, manifest_path=args.manifest,
                           authorize_unknown_billing=args.authorize_unknown_billing)
        except (FenceFailure, SystemExit) as exc:
            report = dict(getattr(exc, 'report', None) or {})
            report.update({'schema': 'pwg.prep_context_comparison_check.v1',
                           'plan_sha256': plan['plan_sha256'], 'ok': False,
                           'blocked_by': str(exc)})
            atomic_json(os.path.join(out_dir, 'check.json'), report)
            print(json.dumps(report, ensure_ascii=False, indent=1))
            return 3
        atomic_json(os.path.join(out_dir, 'check.json'), report)
        print(json.dumps(report, ensure_ascii=False, indent=1))
        return 0

    if args.execute:
        plan = _load_plan(args.plan_file)
        out_dir = args.out_dir or os.path.dirname(os.path.abspath(args.plan_file))
        with open(os.path.join(out_dir, 'check.json'), encoding='utf-8') as handle:
            report = json.load(handle)
        if report.get('plan_sha256') != plan['plan_sha256'] or not report.get('ok'):
            raise FenceFailure('--execute requires a passing --check for THIS plan')
        run = execute(plan, ledger_path=os.path.join(out_dir, 'call_reservation.json'),
                      run_id=args.run_id, out_dir=os.path.join(out_dir, 'envelopes'),
                      claude_bin=args.claude_bin, timeout=args.timeout,
                      billing=report.get('billing'), manifest_path=args.manifest)
        print('calls spent %d/%d  stopped=%r'
              % (run['calls_spent'], plan_max_calls(plan), run['stopped']))
        return 0 if not run['stopped'] else 1

    if args.receipt:
        plan = _load_plan(args.plan_file)
        out_dir = args.out_dir or os.path.dirname(os.path.abspath(args.plan_file))
        with open(os.path.join(out_dir, 'check.json'), encoding='utf-8') as handle:
            report = json.load(handle)
        envelope_dir = os.path.join(out_dir, 'envelopes')
        envelopes = []
        for name in sorted(os.listdir(envelope_dir)) if os.path.isdir(envelope_dir) else []:
            if name.endswith('.json'):
                with open(os.path.join(envelope_dir, name), encoding='utf-8') as handle:
                    envelopes.append(json.load(handle))
        ledger = CallReservationLedger.open_existing(
            os.path.join(out_dir, 'call_reservation.json'), args.run_id)
        run = {'envelopes': envelopes, 'stopped': None, 'ledger_usage': ledger.usage(),
               'calls_spent': ledger.spent()}
        receipt = build_receipt(plan, run, check_report=report)
        atomic_json(os.path.join(out_dir, 'comparison_receipt.json'), receipt)
        print(json.dumps(receipt, ensure_ascii=False, indent=1))
        return 0

    ap.error('choose one of --select / --plan / --check / --execute / --receipt / --selftest')
    return 2


if __name__ == '__main__':
    sys.exit(main())
