#!/usr/bin/env python
"""classify_run.py — mechanical clean / code-failure / infra-confounded verdict for one
Workflow window, read from the returned payload ALONE (H462).

  python src/pilot/classify_run.py wf_output.json
  python src/pilot/classify_run.py wf_output.json --json

Why: H437/H442 had to apply the code-vs-infra rule by hand ("if connection errors recur,
record as infra-confounded, not a code failure") to numbers that were themselves
hand-counted from transcript log lines. Since H462 the harness summary RETURNS
kill_timeouts / conn_errors / heal_calls / kill_bisect_blocked, so the whole adjudication
is computable from the payload:

  clean            null_keys and partial_keys empty AND budget_kill_switch not tripped.
  infra-confounded conn_errors >= 1, OR kill_timeouts >= max(3, 25%% of agents_spent) —
                   the recurring-transport / mass-kill-timeout signature of a degraded
                   generation environment (H442 launches 1-3). An infra-confounded window
                   says NOTHING about the harness code: do not tune budgets on it.
  code-failure     nulls or a budget trip with NO infra signal — the harness itself
                   (kill gate, heal budget, schema, keys) is the suspect.

A payload generated before H462 carries no counters and is UNCLASSIFIABLE — that is the
honest answer, not a guess; regenerate the harness and rerun.

BOTH LANES (G10, H2173): the counters above are the JS harness's names. The live headless
CLI emits the same facts under `heal_agents_spent` / `translate_agents_spent` /
`budget_stops`, so `normalize_summary` maps them on before adjudication. Until H2173 it
did not, and every headless window — i.e. every live window — answered "unclassifiable".

Exit codes: 0 clean · 1 code-failure · 2 infra-confounded · 3 unclassifiable/bad input.
"""
import argparse
import json
import math
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from workflow_payload import load_json, find_results_container

# Infra-signal thresholds (documented above; keep in sync with the docstring).
INFRA_CONN_MIN = 1
INFRA_KILL_MIN = 3
INFRA_KILL_FRAC = 0.25

TELEMETRY_FIELDS = ('kill_timeouts', 'conn_errors', 'heal_calls')
VERDICT_EXIT = {'clean': 0, 'code-failure': 1, 'infra-confounded': 2}

# G10 (H2173, audit F-B7). This classifier was written against the JS harness summary
# (H462) and never re-read when the live route moved to the headless CLI (H1110). Three
# of its inputs simply do not exist in `headless_worker`'s summary, so on the LIVE lane
# it was not merely reading one dead key — it was inert end to end:
#
#   heal_calls                 -> absent; headless emits `heal_agents_spent`
#   agents_spent               -> absent; headless emits the two pools separately
#   budget_kill_switch_tripped -> absent; headless emits `budget_stops`
#
# `heal_calls` is in TELEMETRY_FIELDS, so every headless payload answered
# "unclassifiable" (the honest refusal, but for the wrong reason — the counters WERE
# there under other names), and had that gate been passed, `agents_spent = 0` would have
# collapsed the kill threshold to its floor and `tripped` would have read False on a
# window that really did exhaust its budget. Normalising here — rather than renaming the
# emitter's keys — keeps every historical JS payload classifiable at its original
# vocabulary, which is the whole point of the tool.
HEADLESS_ALIASES = {
    'heal_calls': ('heal_agents_spent',),
}


def normalize_summary(summary):
    """Map a headless-lane summary onto the classifier's H462 vocabulary (G10).

    Returns a NEW dict; the caller's payload is never mutated. JS-lane keys always win
    when present — an explicit value is never overwritten by a derived one.
    """
    if not isinstance(summary, dict):
        return summary
    norm = dict(summary)
    for canonical, aliases in HEADLESS_ALIASES.items():
        if norm.get(canonical) is None:
            for alias in aliases:
                if summary.get(alias) is not None:
                    norm[canonical] = summary[alias]
                    break
    if norm.get('agents_spent') is None:
        pools = [summary.get('translate_agents_spent'), summary.get('heal_agents_spent')]
        if any(p is not None for p in pools):
            norm['agents_spent'] = sum(p or 0 for p in pools)
    if norm.get('budget_kill_switch_tripped') is None and summary.get('budget_stops') is not None:
        # A headless `budget_stop` IS the kill switch firing: `_budget_ok` refused a spawn
        # because a manifest agent ceiling was reached, and the card was failed with
        # `budget_exceeded`. Same event the JS lane reports as the boolean.
        norm['budget_kill_switch_tripped'] = bool(summary['budget_stops'])
        norm['budget_stops'] = summary['budget_stops']
    return norm


def extract_summary(payload):
    container = find_results_container(payload) or {}
    for src in (container, payload if isinstance(payload, dict) else {}):
        s = src.get('summary')
        if isinstance(s, dict):
            return s
    return None


def classify(summary):
    """Pure verdict from one harness `summary` dict. Returns (verdict, reasons, signals).

    Accepts either lane's summary shape: the H462 JS vocabulary as written, or the
    headless-CLI vocabulary via `normalize_summary` (G10).
    """
    summary = normalize_summary(summary)
    missing = [f for f in TELEMETRY_FIELDS if f not in summary]
    if missing:
        return ('unclassifiable',
                ['payload predates H462 — summary lacks %s; regenerate the harness'
                 % ', '.join(missing)], {})
    agents = summary.get('agents_spent') or 0
    kills = summary.get('kill_timeouts') or 0
    conns = summary.get('conn_errors') or 0
    nulls = summary.get('null_keys')
    if nulls is None:
        nulls = [None] * (summary.get('null') or 0)
    partials = summary.get('partial_keys') or []
    tripped = bool(summary.get('budget_kill_switch_tripped'))
    kill_ceiling = max(INFRA_KILL_MIN, int(math.ceil(INFRA_KILL_FRAC * agents)))
    signals = {
        'agents_spent': agents,
        # H462 payloads predate the split-pool refactor, so these remain optional.
        # Echo them when present without making historical payloads unclassifiable.
        'translate_agents_spent': summary.get('translate_agents_spent'),
        'max_translate_agents': summary.get('max_translate_agents'),
        'translate_budget_tripped': summary.get('translate_budget_tripped'),
        'heal_agents_spent': summary.get('heal_agents_spent'),
        'max_heal_agents': summary.get('max_heal_agents'),
        'heal_budget_tripped': summary.get('heal_budget_tripped'),
        'kill_timeouts': kills,
        'conn_errors': conns,
        'heal_calls': summary.get('heal_calls'),
        'kill_bisect_blocked': summary.get('kill_bisect_blocked'),
        'null_cards': len(nulls),
        'partial_cards': len(partials),
        'partial_keys': list(partials),
        'budget_kill_switch_tripped': tripped,
        # G10: the headless lane's own counter, echoed so a reader can tell a normalised
        # trip from a JS-lane boolean without re-opening the payload.
        'budget_stops': summary.get('budget_stops'),
        'infra_kill_threshold': kill_ceiling,
    }
    reasons = []
    if not nulls and not partials and not tripped:
        reasons.append('all cards returned, budget switch untripped')
        if conns or kills:
            reasons.append('non-blocking infra noise: %d conn-error(s), %d kill-timeout(s)'
                           % (conns, kills))
        return 'clean', reasons, signals
    infra = []
    if conns >= INFRA_CONN_MIN:
        infra.append('%d connection error(s) (>= %d)' % (conns, INFRA_CONN_MIN))
    if kills >= kill_ceiling:
        infra.append('%d kill-timeout(s) >= max(%d, %d%% of %d agents) = %d'
                     % (kills, INFRA_KILL_MIN, int(INFRA_KILL_FRAC * 100), agents, kill_ceiling))
    if infra:
        reasons.extend(infra)
        reasons.append('degraded generation environment — result says nothing about the '
                       'harness code; do not tune budgets on this run (H442 rule)')
        return 'infra-confounded', reasons, signals
    reasons.append('%d null card(s), %d partial card(s), tripped=%s, with NO infra signal '
                   '(%d conn-errors, %d kill-timeouts < %d)' %
                   (len(nulls), len(partials), tripped, conns, kills, kill_ceiling))
    reasons.append('suspect the harness itself: kill gate, heal budget, schema, or key matching')
    return 'code-failure', reasons, signals


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('wf_output', help='saved Workflow payload (wf_output.json)')
    ap.add_argument('--json', action='store_true', help='emit the verdict as JSON only')
    args = ap.parse_args(argv)
    try:
        payload = load_json(args.wf_output)
    except (OSError, ValueError) as e:
        print('unclassifiable: cannot read payload: %s' % e, file=sys.stderr)
        return 3
    summary = extract_summary(payload)
    if summary is None:
        print('unclassifiable: no summary dict found in payload', file=sys.stderr)
        return 3
    verdict, reasons, signals = classify(summary)
    if args.json:
        print(json.dumps({'verdict': verdict, 'reasons': reasons, 'signals': signals},
                         ensure_ascii=False, indent=2))
    else:
        print('verdict: %s' % verdict)
        for r in reasons:
            print('  - %s' % r)
        if signals:
            print('  signals: %s' % json.dumps(signals, ensure_ascii=False))
    return VERDICT_EXIT.get(verdict, 3)


if __name__ == '__main__':
    sys.exit(main())
