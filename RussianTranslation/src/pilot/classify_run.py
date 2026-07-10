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

  clean            null_keys empty AND budget_kill_switch not tripped.
  infra-confounded conn_errors >= 1, OR kill_timeouts >= max(3, 25%% of agents_spent) —
                   the recurring-transport / mass-kill-timeout signature of a degraded
                   generation environment (H442 launches 1-3). An infra-confounded window
                   says NOTHING about the harness code: do not tune budgets on it.
  code-failure     nulls or a budget trip with NO infra signal — the harness itself
                   (kill gate, heal budget, schema, keys) is the suspect.

A payload generated before H462 carries no counters and is UNCLASSIFIABLE — that is the
honest answer, not a guess; regenerate the harness and rerun.

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


def extract_summary(payload):
    container = find_results_container(payload) or {}
    for src in (container, payload if isinstance(payload, dict) else {}):
        s = src.get('summary')
        if isinstance(s, dict):
            return s
    return None


def classify(summary):
    """Pure verdict from one harness `summary` dict. Returns (verdict, reasons, signals)."""
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
    tripped = bool(summary.get('budget_kill_switch_tripped'))
    kill_ceiling = max(INFRA_KILL_MIN, int(math.ceil(INFRA_KILL_FRAC * agents)))
    signals = {
        'agents_spent': agents,
        'kill_timeouts': kills,
        'conn_errors': conns,
        'heal_calls': summary.get('heal_calls'),
        'kill_bisect_blocked': summary.get('kill_bisect_blocked'),
        'null_cards': len(nulls),
        'budget_kill_switch_tripped': tripped,
        'infra_kill_threshold': kill_ceiling,
    }
    reasons = []
    if not nulls and not tripped:
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
    reasons.append('%d null card(s), tripped=%s, with NO infra signal (%d conn-errors, '
                   '%d kill-timeouts < %d)' % (len(nulls), tripped, conns, kills, kill_ceiling))
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
