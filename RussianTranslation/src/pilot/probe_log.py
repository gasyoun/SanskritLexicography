#!/usr/bin/env python
"""Append-only environment-probe log for pwg_ru Workflow launches.

  python src/pilot/probe_log.py append --kind warmup --verdict GO \
      --latency-ms 3269 --conn-errors 0 --window h317_w1b --handoff H442 \
      --note "one trivial sonnet agent() call"

  python src/pilot/probe_log.py append --kind abort --verdict NO-GO ...
  python src/pilot/probe_log.py outcome --run-id wf_x --clean 0 --cards 12 ...
  python src/pilot/probe_log.py render          # rewrite the .md table
  python src/pilot/probe_log.py gate            # exit 1 if the last reading is NO-GO

Why this exists (and why it is NOT a fourth launch ledger):
LAUNCH_FUCKUPS.md, LAUNCH_STATS.md and RUN_LOG.md all key on *a launch having
happened*. A probe that says "do not launch" therefore leaves no trace, so the
harvested rates in LAUNCH_STATS.md have a survivorship-biased denominator, and
nobody can ask whether a pre-launch reading predicts the launch outcome. This
log keys on the *reading*, so aborted launches and green no-ops are both rows.

The probe itself is a Workflow `agent()` call, which only a Workflow-capable
session can fire; this module records the reading and enforces the gate.
"""
import argparse
import datetime as _dt
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))
JSONL = os.path.join(HERE, 'generation_api_probe_log.jsonl')
RENDERED = os.path.join(REPO_ROOT, 'GENERATION_API_PROBE_LOG.md')

# SERVER_OUTAGES.md row 29 (10-07-2026): a warm-up must show zero
# `Connection closed mid-response` and sub-30s latency before a ~2.2M-token launch.
LATENCY_CEIL_MS = 30_000
CONN_ERR_CEIL = 0

KINDS = ('warmup', 'launch', 'abort')
VERDICTS = ('GO', 'NO-GO')


def _now():
    return _dt.datetime.now(_dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def read_rows():
    if not os.path.exists(JSONL):
        return []
    rows = []
    with open(JSONL, encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _append(row):
    with open(JSONL, 'a', encoding='utf-8') as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + '\n')


def verdict_for(latency_ms, conn_errors):
    """The mechanical gate. Returns (verdict, reason)."""
    if conn_errors is not None and conn_errors > CONN_ERR_CEIL:
        return 'NO-GO', f'{conn_errors} connection error(s) > {CONN_ERR_CEIL}'
    if latency_ms is not None and latency_ms > LATENCY_CEIL_MS:
        return 'NO-GO', f'latency {latency_ms}ms > {LATENCY_CEIL_MS}ms'
    return 'GO', 'within ceilings'


def cmd_append(a):
    auto, reason = verdict_for(a.latency_ms, a.conn_errors)
    verdict = a.verdict or auto
    if a.verdict and a.verdict != auto and a.kind == 'warmup':
        print(f'WARN: stated verdict {a.verdict} disagrees with mechanical {auto} ({reason})',
              file=sys.stderr)
    row = {
        'ts': a.ts or _now(),
        'kind': a.kind,
        'verdict': verdict,
        'gate_reason': reason,
        'lane': a.lane,
        'window': a.window,
        'handoff': a.handoff,
        'run_id': a.run_id,
        'probe': {
            'latency_ms': a.latency_ms,
            'conn_errors': a.conn_errors,
            'agent_model': a.agent_model,
        },
        'orchestrator': a.orchestrator,
        # Comparability provenance: a TM sidecar that grew between runs silently
        # changes the agent count, so a "no trip" result is not attributable to a
        # code fix alone. Record it or the numbers lie by omission.
        'harness': {
            'max_agents': a.max_agents,
            'batches': a.batches,
            'agent_expected_after_tm': a.agent_expected,
            'frag_tm_cached': a.frag_tm_cached,
            'generated_from_commit': a.commit,
        },
        'note': a.note,
    }
    _append(row)
    print(f'{row["ts"]}  {a.kind:6s}  {verdict:5s}  {reason}')
    return 0


def cmd_outcome(a):
    """Attach a measured launch outcome to the most recent row for this run_id."""
    rows = read_rows()
    for row in reversed(rows):
        if row.get('run_id') == a.run_id:
            break
    else:
        raise SystemExit(f'no row with run_id={a.run_id!r}; append a launch row first')
    _append({
        'ts': _now(),
        'kind': 'outcome',
        'run_id': a.run_id,
        'window': row.get('window'),
        'handoff': row.get('handoff'),
        'outcome': {
            'cards': a.cards,
            'audit_clean': a.clean,
            'agents_used': a.agents,
            'subagent_tokens': a.tokens,
            'kill_timeouts': a.kill_timeouts,
            'conn_errors': a.conn_errors,
            'budget_kill_switch_tripped': a.tripped,
        },
        'note': a.note,
    })
    print(f'outcome recorded for {a.run_id}: {a.clean}/{a.cards} clean, tripped={a.tripped}')
    return 0


def cmd_gate(a):
    rows = [r for r in read_rows() if r.get('kind') == 'warmup']
    if not rows:
        print('NO-GO: no warm-up reading on record', file=sys.stderr)
        return 1
    last = rows[-1]
    if last['verdict'] != 'GO':
        print(f'NO-GO: last warm-up {last["ts"]} — {last["gate_reason"]}', file=sys.stderr)
        return 1
    print(f'GO: last warm-up {last["ts"]} — {last["gate_reason"]}')
    return 0


def _cell(v):
    return '—' if v in (None, '') else str(v)


def cmd_render(a):
    rows = read_rows()
    today = _dt.date.today().strftime('%d-%m-%Y')
    created = '10-07-2026'
    out = [
        '# Generation-API probe log — pwg_ru Workflow launches',
        '',
        f'_Created: {created} · Last updated: {today}_',
        '',
        'Append-only, machine-written. Source of truth is',
        '[`src/pilot/generation_api_probe_log.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/generation_api_probe_log.jsonl);',
        'regenerate this table with `python src/pilot/probe_log.py render`. Do not hand-edit.',
        '',
        'This log keys on the **reading**, not on a launch. A probe that blocked a launch',
        '(`abort` / `NO-GO`) is a row here, which is exactly what',
        '[`LAUNCH_STATS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LAUNCH_STATS.md)',
        'cannot see: its denominator counts only windows that actually launched.',
        '',
        f'Gate (per [`Uprava/SERVER_OUTAGES.md`](https://github.com/gasyoun/Uprava/blob/main/SERVER_OUTAGES.md)):',
        f'0 `Connection closed mid-response` and latency < {LATENCY_CEIL_MS // 1000}s.',
        '',
        '## Readings',
        '',
        '| ts (UTC) | kind | verdict | latency | conn-err | window | H### | note |',
        '|---|---|---|---:|---:|---|---|---|',
    ]
    for r in rows:
        if r.get('kind') == 'outcome':
            continue
        p = r.get('probe') or {}
        lat = p.get('latency_ms')
        out.append('| {} | {} | {} | {} | {} | {} | {} | {} |'.format(
            r['ts'], r['kind'], r['verdict'],
            f'{lat/1000:.1f}s' if isinstance(lat, int) else '—',
            _cell(p.get('conn_errors')), _cell(r.get('window')),
            _cell(r.get('handoff')), _cell(r.get('note'))))

    outcomes = [r for r in rows if r.get('kind') == 'outcome']
    if outcomes:
        out += ['', '## Measured launch outcomes', '',
                '| ts (UTC) | window | clean | agents | tokens | kill-timeouts | conn-err | tripped |',
                '|---|---|---:|---:|---:|---:|---:|:--:|']
        for r in outcomes:
            o = r['outcome']
            tok = o.get('subagent_tokens')
            out.append('| {} | {} | {}/{} | {} | {} | {} | {} | {} |'.format(
                r['ts'], _cell(r.get('window')), _cell(o.get('audit_clean')), _cell(o.get('cards')),
                _cell(o.get('agents_used')),
                f'{tok/1e6:.2f}M' if isinstance(tok, int) else '—',
                _cell(o.get('kill_timeouts')), _cell(o.get('conn_errors')),
                'yes' if o.get('budget_kill_switch_tripped') else 'no'))

    out += ['', '_Dr. Mārcis Gasūns_', '']
    with open(RENDERED, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(out))
    print(f'wrote {RENDERED} ({len([r for r in rows if r.get("kind") != "outcome"])} readings, '
          f'{len(outcomes)} outcomes)')
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest='cmd', required=True)

    p = sub.add_parser('append', help='record one probe / launch / abort reading')
    p.add_argument('--kind', choices=KINDS, required=True)
    p.add_argument('--verdict', choices=VERDICTS)
    p.add_argument('--latency-ms', type=int)
    p.add_argument('--conn-errors', type=int)
    p.add_argument('--agent-model', default='claude-sonnet-5')
    p.add_argument('--lane', default='nominal medium50 (band-4 singleton)')
    p.add_argument('--window')
    p.add_argument('--handoff')
    p.add_argument('--run-id')
    p.add_argument('--orchestrator')
    p.add_argument('--max-agents', type=int)
    p.add_argument('--batches', type=int)
    p.add_argument('--agent-expected', type=int)
    p.add_argument('--frag-tm-cached', type=int)
    p.add_argument('--commit')
    p.add_argument('--ts', help='override timestamp (backfill only)')
    p.add_argument('--note', default='')
    p.set_defaults(func=cmd_append)

    p = sub.add_parser('outcome', help='attach a measured outcome to a launch row')
    p.add_argument('--run-id', required=True)
    p.add_argument('--cards', type=int)
    p.add_argument('--clean', type=int)
    p.add_argument('--agents', type=int)
    p.add_argument('--tokens', type=int)
    p.add_argument('--kill-timeouts', type=int)
    p.add_argument('--conn-errors', type=int)
    p.add_argument('--tripped', action='store_true')
    p.add_argument('--note', default='')
    p.set_defaults(func=cmd_outcome)

    p = sub.add_parser('gate', help='exit 1 unless the last warm-up reading is GO')
    p.set_defaults(func=cmd_gate)

    p = sub.add_parser('render', help='rewrite the Markdown table from the JSONL')
    p.set_defaults(func=cmd_render)

    a = ap.parse_args()
    sys.exit(a.func(a))


if __name__ == '__main__':
    main()
