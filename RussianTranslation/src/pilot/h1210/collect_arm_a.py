#!/usr/bin/env python
r"""H1210 arm A — lift each chunk's Workflow return value out of its task-output file.

A 54-card chunk's return value is megabytes of JSON; pasting it through the session would
burn the context the run exists to inform. The Workflow tool already persists the full
return value to `<tasks>/<taskId>.output` ({summary, agentCount, result, usage...}), so
this pulls `result` out to a slice_result file that `h1209/canonical_audit.py` and
`ab_report.py` consume directly, and accumulates the per-chunk usage block into arm A's
telemetry (token/agent/duration accounting the Workflow journal does not otherwise expose
per role).

Usage:
  python src/pilot/h1210/collect_arm_a.py <chunk_tag> <task_output.json> [more...]
  python src/pilot/h1210/collect_arm_a.py --telemetry-out src/pilot/h1210/arm_a.telemetry.json
"""
import argparse
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))


def collect(tag, path):
    d = json.load(open(path, encoding='utf-8'))
    res = d.get('result')
    if not isinstance(res, dict) or 'results' not in res:
        sys.exit('FAIL: %s carries no workflow result object (keys: %s)'
                 % (path, list(d)))
    res['arm'] = 'A_claude_native'
    res['chunk'] = tag
    out = os.path.join(HERE, 'arm_a.%s.slice_result.json' % tag)
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
        f.write('\n')
    # Per-agent rows carry `model`, `tokens`, `durationMs` and `state` — so the controller
    # TOKEN share (not just its call share) is measurable here. H1209 named that as an
    # explicit gap ("the Workflow journal records no per-role TOKEN split"); it is in the
    # task-output progress block, one level up from the journal.
    roles = {}
    lat = []
    models = {}
    for row in (d.get('workflowProgress') or []):
        if row.get('type') != 'workflow_agent':
            continue
        role = 'controller' if str(row.get('label', '')).startswith('control:') else 'worker'
        # The template pins ALIASES (model:'sonnet'/'opus'), which resolve to whatever the
        # tier currently is — so the run's real model id is a MEASUREMENT, not a constant.
        # H1846 proved why: the 13-card fill ran months-of-versions later than the original
        # 87 and its controller alias resolved to a different Opus. Record what actually ran.
        if row.get('model'):
            models.setdefault(role, set()).add(str(row['model']))
        r = roles.setdefault(role, {'agents': 0, 'tokens': 0, 'errors': 0, 'duration_ms': 0})
        r['agents'] += 1
        r['tokens'] += row.get('tokens') or 0
        r['duration_ms'] += row.get('durationMs') or 0
        if row.get('state') == 'error':
            r['errors'] += 1
        if role == 'worker' and row.get('durationMs'):
            lat.append(row['durationMs'])
    usage = {k: d.get(k) for k in ('agentCount', 'totalTokens', 'totalToolCalls')}
    usage = {k: v for k, v in usage.items() if v is not None}
    usage['chunk'] = tag
    usage['cards'] = len(res['results'])
    usage['roles'] = roles
    usage['agents_error'] = sum(r['errors'] for r in roles.values())
    usage['models'] = {k: sorted(v) for k, v in models.items()}
    usage['worker_latency_ms'] = sorted(lat)
    usage['durationMs'] = max((row.get('lastProgressAt') or 0)
                              for row in (d.get('workflowProgress') or [])
                              if row.get('type') == 'workflow_agent') - \
        min((row.get('queuedAt') or 0)
            for row in (d.get('workflowProgress') or [])
            if row.get('type') == 'workflow_agent') if roles else 0
    print('%s: %d cards -> %s (usage %s)' % (tag, len(res['results']), os.path.basename(out),
                                             usage))
    return usage


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pairs', nargs='*', help='<tag> <task_output.json> [<tag> <path> ...]')
    ap.add_argument('--telemetry-out', default=os.path.join(HERE, 'arm_a.telemetry.json'))
    a = ap.parse_args()
    if len(a.pairs) % 2:
        sys.exit('FAIL: arguments must be <tag> <path> pairs')

    usages = []
    for i in range(0, len(a.pairs), 2):
        usages.append(collect(a.pairs[i], a.pairs[i + 1]))

    prev = {}
    if os.path.exists(a.telemetry_out):
        prev = json.load(open(a.telemetry_out, encoding='utf-8'))
    chunks = {u['chunk']: u for u in (prev.get('chunks') or [])}
    for u in usages:
        chunks[u['chunk']] = u
    chunks = [chunks[k] for k in sorted(chunks)]

    n_results = 0
    for p in sorted(glob.glob(os.path.join(HERE, 'arm_a.chunk*.slice_result.json'))):
        n_results += len(json.load(open(p, encoding='utf-8'))['results'])

    # Derive the arm's model string from what the chunks actually recorded, and say so
    # honestly when the chunks disagree (H1846: the 13-card fill ran on a later controller
    # tier than the original 87 — a hardcoded string would have quietly misattributed it).
    LEGACY = 'workers claude-sonnet-5 / controller claude-opus-4-8'
    measured, unmeasured = [c for c in chunks if c.get('models')], [c for c in chunks
                                                                    if not c.get('models')]
    per_role = {}
    for c in measured:
        for role, ids in c['models'].items():
            per_role.setdefault(role, set()).update(ids)
    derived = ' / '.join('%ss %s' % (role, ' + '.join(sorted(ids)))
                         for role, ids in sorted(per_role.items()))
    if measured and unmeasured:
        # The exact H1846 case: some chunks recorded their real ids, the pre-existing ones
        # did not. Naming BOTH populations with their card counts is the only honest form —
        # collapsing them to one string misattributes whichever population is silent.
        # NB: the unmeasured half is described by the LEGACY constant, never by
        # `prev['model']` — that field may already hold a composed string, and feeding it
        # back in nests one composition inside the next on every re-collection.
        model_str = ('%d chunk(s)/%d cards measured: %s | %d chunk(s)/%d cards not recorded '
                     '(pre-H1846 collection), documented as: %s'
                     % (len(measured), sum(c.get('cards', 0) for c in measured), derived,
                        len(unmeasured), sum(c.get('cards', 0) for c in unmeasured), LEGACY))
    elif measured:
        model_str = derived + (' (MIXED across chunks — see per-chunk `models`)'
                               if any(len(v) > 1 for v in per_role.values()) else '')
    else:                                        # pre-H1846 telemetry carries no per-chunk models
        model_str = LEGACY if ' measured: ' in str(prev.get('model') or '') \
            else (prev.get('model') or LEGACY)

    telem = {
        'schema': 'pwg.h1210_arm_telemetry.v1',
        'arm': 'A_claude_native',
        'model': model_str,
        'cards': n_results,
        'chunks': chunks,
        'agents_total': sum(c.get('agentCount', 0) for c in chunks),
        'agents_error': sum(c.get('agents_error', 0) for c in chunks),
        'tokens': {
            'subagent_tokens': sum(c.get('totalTokens', 0) for c in chunks),
            'worker_tokens': sum((c.get('roles', {}).get('worker') or {}).get('tokens', 0)
                                 for c in chunks),
            'controller_tokens': sum((c.get('roles', {}).get('controller') or {}).get('tokens', 0)
                                     for c in chunks),
        },
        'controller_token_share_pct': None,
        'wall_clock_s': round(sum(c.get('durationMs', 0) for c in chunks) / 1000.0, 1),
        'wall_clock_note': 'sum of per-chunk Workflow durations; chunks partly overlapped, '
                           'so this is agent-time, not calendar time',
        'cost': {},
        'usd_note': 'subscription lane (Workflow agent() on the session plan) — no per-call '
                    'USD is exposed, so $/clean is reported as n/a rather than guessed; '
                    'token counts are the comparable quantity',
    }
    tot = telem['tokens']['worker_tokens'] + telem['tokens']['controller_tokens']
    telem['controller_token_share_pct'] = (
        round(100.0 * telem['tokens']['controller_tokens'] / tot, 1) if tot else None)
    lat = sorted(x for c in chunks for x in (c.get('worker_latency_ms') or []))
    telem['latency_s_per_card_median'] = round(lat[len(lat) // 2] / 1000.0, 1) if lat else None
    telem['worker_latency_s'] = {'min': round(lat[0] / 1000.0, 1),
                                 'p90': round(lat[int(len(lat) * 0.9)] / 1000.0, 1),
                                 'max': round(lat[-1] / 1000.0, 1)} if lat else None
    with open(a.telemetry_out, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(telem, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print('wrote %s (%d chunks, %d cards, %d agents, %d subagent tokens)'
          % (a.telemetry_out, len(chunks), telem['cards'], telem['agents_total'],
             telem['tokens']['subagent_tokens']))


if __name__ == '__main__':
    main()
