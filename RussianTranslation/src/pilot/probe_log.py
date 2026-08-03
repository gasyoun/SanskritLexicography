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
# H462: a trivial one-word probe exercises NONE of the failing path — measured 10-07-2026,
# a 3.3s GO probe preceded a window that still degraded (2 conn-errors, 7 kill-timeouts,
# 6 at the 180s KILL_CEIL on 1.2-8.0KB skeletons). A warm-up may only authorize a launch
# if its prompt carried a skeleton-sized payload; use `probe_log.py prompt` to get one.
PAYLOAD_FLOOR_BYTES = 5 * 1024

KINDS = ('warmup', 'launch', 'abort')
VERDICTS = ('GO', 'NO-GO')
# THE ONE SOURCE OF TRUTH FOR PROBE CEILINGS (H2118, #946). Every gate derives its ceiling
# from this table; nothing hard-codes a probe ceiling anywhere else in the tree. Before H2118
# there were THREE independent copies of the number (`probe_log` 30 000,
# `max_account_orchestrator` 65 000, `coordinator` 65 000) kept in lockstep by comments rather
# than by code — and they had already fallen out of step.
#
# ⚠️ ONE POLICY NAME PER CEILING VALUE — never re-point an existing name. H2095 (#946) recorded
# the defect this rule exists to prevent: the ceiling moved 30 000 -> 33 000 -> 65 000 in a single
# day (31-07-2026) while the token stayed `production_v1`, so rows judged 2.2x apart all claim the
# same policy and a `policy` token stopped being sufficient provenance. Bumping the name is how a
# reader tells which gate judged a row; that is the whole point of the token.
#
# `production_v1` (30 000) is therefore FROZEN at its historical value, not "the old wrong one" —
# every row stamped `production_v1` before 31-07-2026 was genuinely judged at 30 000, and moving
# this number would retroactively falsify those rows.
#
# ⚠️ `production_v2` (65 000) IS NOT A DERIVED NUMBER — it is MG's 31-07-2026 ruling, and
# FINDINGS §270 established it was calibrated partly against rate-limit BACKOFF rather than route
# latency (a rate-limited CLI hangs instead of reporting 429, so the readings behind it may be
# measuring retry delay). H2118 could not re-derive it: the paired same-moment quota check that
# would make new readings trustworthy was unavailable, and at that date not one probe row in the
# tree carried the `duration_api_ms` H2095 added. Superseded by `production_v3`; do NOT edit it —
# rows stamped `production_v2` were genuinely judged at 65 000.
#
# ✅ `production_v3` IS DERIVED — H2138 (#946), 02-08-2026, from the 8-reading measured c4 series
# (5 of them decomposable). Reproduce with `python src/pilot/h2138_ceiling_derive.py`, which
# carries the readings and the two rules. Two ceilings, because ONE NUMBER CANNOT DO THE JOB:
#
#     wall elapsed_ms  =  duration_api_ms  +  api_gap_ms
#                         (route health)     (in-CLI scaffolding)
#
# and they move independently — the api/wall ratio measured 0.25..0.72, so no fixed factor
# converts one into the other (H2174). The 02-08 12:46 reading is the proof: the FASTEST API
# time ever recorded on c4 (16 445 ms) failed the 65 000 ms wall gate on 49 846 ms of
# scaffolding. At 65 000 the gate passed 2/8 — its median reading sat ~12 s ABOVE the ceiling,
# so it failed ~75 % of the time at ~$1.09 a pull and was a lottery, not a gate.
#
#   `latency_ceil_ms` 80 000 = worst LEGITIMATE call = healthy-route max (29 069) + largest
#                              scaffolding tax ever observed (49 846), rounded up.
#   `api_ceil_ms`     45 000 = healthy-route cluster max (29 069) x 1.5. A SECOND, INDEPENDENT
#                              fail condition (h2152 §5.2 item 2; H2174 "option C") — an ADDED
#                              guard the wall number never had.
#
# The clock is NOT reopened here: v3 still gates on wall `elapsed_ms` per MG's 02-08-2026 ruling
# (H2160 option A). Honest limit: the ROUTE guard changes no historical verdict, because the one
# degraded-route reading (69 137 ms api) also breached the wall ceiling. It is a FORWARD guard
# for a class the series proves exists but has not yet seen in isolation.
POLICIES = {
    'production_v1': {'latency_ceil_ms': 30_000, 'api_ceil_ms': None, 'conn_error_ceil': 0,
                      'payload_floor_bytes': PAYLOAD_FLOOR_BYTES,
                      'require_schema_valid': True},
    'production_v2': {'latency_ceil_ms': 65_000, 'api_ceil_ms': None, 'conn_error_ceil': 0,
                      'payload_floor_bytes': PAYLOAD_FLOOR_BYTES,
                      'require_schema_valid': True},
    'production_v3': {'latency_ceil_ms': 80_000, 'api_ceil_ms': 45_000, 'conn_error_ceil': 0,
                      'payload_floor_bytes': PAYLOAD_FLOOR_BYTES,
                      'require_schema_valid': True},
}
# The policy the live dispatch + receipt gates run under. Importers derive their ceiling from
# `POLICIES[CURRENT_POLICY]` rather than restating the number, so a future bump is one edit here.
CURRENT_POLICY = 'production_v3'


def ceiling_for(policy=CURRENT_POLICY):
    """The latency ceiling of `policy`, for importers that must not hard-code it."""
    if policy not in POLICIES:
        raise ValueError('unknown probe policy %r' % policy)
    return POLICIES[policy]['latency_ceil_ms']


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


def verdict_for(latency_ms, conn_errors, payload_bytes=None, kind=None,
                policy=CURRENT_POLICY, schema_valid=None, api_ms=None):
    """The mechanical gate. Returns (verdict, reason).

    G10 (H2173, audit F-B4): this default was frozen at `production_v1` while
    `CURRENT_POLICY` advanced twice (v2, then v3). The failure was quiet in the safe
    direction — v1's 30 000 ms wall ceiling is the STRICTEST of the three, so the default
    lane judged live readings against a retired number and stamped the row `production_v1`.
    Nothing was wrongly admitted, but the receipts named a policy that had not gated the
    live route since 31-07-2026, and the v3 `api_ceil_ms` guard never ran at all (v1
    carries none). Defaults now track `CURRENT_POLICY`, so a ceiling bump is still the one
    edit the table promises; callers that must pin a historical policy pass it explicitly.

    `latency_ms` is wall `elapsed_ms` — the gating clock, MG 02-08-2026 (H2160 option A).
    `api_ms` is the envelope's `duration_api_ms`, checked against the policy's
    `api_ceil_ms` as a SECOND, INDEPENDENT fail condition (H2138). A policy with
    `api_ceil_ms: None`, or a reading that carries no `duration_api_ms`, gates on wall
    alone exactly as before — absent instrumentation must not silently change a verdict.
    """
    if policy not in POLICIES:
        raise ValueError('unknown probe policy %r' % policy)
    spec = POLICIES[policy]
    if conn_errors is not None and conn_errors > spec['conn_error_ceil']:
        return 'NO-GO', f'{conn_errors} connection error(s) > {spec["conn_error_ceil"]}'
    if latency_ms is None or latency_ms >= spec['latency_ceil_ms']:
        return 'NO-GO', f'latency {latency_ms}ms is not < {spec["latency_ceil_ms"]}ms'
    api_ceil = spec.get('api_ceil_ms')
    if api_ceil is not None and api_ms is not None and api_ms >= api_ceil:
        return 'NO-GO', (f'route latency {api_ms}ms is not < {api_ceil}ms '
                         f'(duration_api_ms; wall was within its own ceiling)')
    # H462: only a load-representative warm-up may authorize a launch. A missing
    # payload size is treated as trivial — the burden of proof is on the probe.
    if kind == 'warmup' and (payload_bytes is None or payload_bytes < spec['payload_floor_bytes']):
        return 'NO-GO', (f'probe not load-representative: payload '
                         f'{payload_bytes or 0}B < {spec["payload_floor_bytes"]}B '
                         f'(use `probe_log.py prompt`)')
    if kind == 'warmup' and spec['require_schema_valid'] and schema_valid is not True:
        return 'NO-GO', 'representative schema payload did not validate'
    return 'GO', '%s: within ceilings, load-representative schema payload' % policy


def cmd_append(a):
    # G10 (H2173): `api_ms` was a `verdict_for` parameter with no CLI path, so the v3
    # route guard could never fire on the append path — the one path that writes receipts.
    auto, reason = verdict_for(a.latency_ms, a.conn_errors, a.payload_bytes, a.kind,
                               a.policy, a.schema_valid, api_ms=getattr(a, 'api_ms', None))
    verdict = a.verdict or auto
    if a.verdict and a.verdict != auto:
        raise SystemExit('REFUSED: stated verdict %s contradicts mechanical %s (%s)'
                         % (a.verdict, auto, reason))
    row = {
        'ts': a.ts or _now(),
        'kind': a.kind,
        'verdict': verdict,
        'gate_reason': reason,
        'policy': a.policy,
        'lane': a.lane,
        'window': a.window,
        'handoff': a.handoff,
        'run_id': a.run_id,
        'probe': {
            'latency_ms': a.latency_ms,
            # H2095/H2138 decomposition: wall = duration_api_ms + in-CLI scaffolding.
            # Recorded when the caller has it, so a row can be re-judged against a future
            # policy instead of being stuck as one opaque wall number.
            'api_ms': getattr(a, 'api_ms', None),
            'conn_errors': a.conn_errors,
            'payload_bytes': a.payload_bytes,
            'agent_model': a.agent_model,
            'schema_valid': a.schema_valid,
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
    # B15 (H1339): an outcome row whose EVERY structured field is null is unusable by any
    # scripted rate/economy math (w08/w08_rq1/w09 rendered em-dashes and corrupted the rate
    # tables). First try recovering the figures from the free-text note (the same key=int
    # pairs economy_ledger.parse_note_kv reads); if nothing structured can be recovered
    # either, REFUSE the row -- never append all-null telemetry that reads as measured.
    structured = {'cards': a.cards, 'clean': a.clean, 'agents': a.agents, 'tokens': a.tokens,
                  'kill_timeouts': a.kill_timeouts, 'conn_errors': a.conn_errors}
    if all(v is None for v in structured.values()):
        import economy_ledger
        kv = economy_ledger.parse_note_kv(getattr(a, 'note', '') or '')
        # H1386 P3j: `or` loses a falsy clean=0 (the B15-motivating degraded-window case,
        # a REAL all-rejected figure) -- only a genuinely-absent key falls through to ok.
        recovered = {'cards': kv.get('cards'),
                     'clean': kv.get('clean') if kv.get('clean') is not None else kv.get('ok'),
                     'agents': kv.get('agents'), 'tokens': kv.get('tokens'),
                     'kill_timeouts': kv.get('kill_timeouts'),
                     'conn_errors': kv.get('conn_errors')}
        if all(v is None for v in recovered.values()):
            raise SystemExit(
                'REFUSED: outcome for %r carries no structured field at all (and none '
                'recoverable from the note). Pass at least one of --cards/--clean/--agents/'
                '--tokens/--kill-timeouts/--conn-errors -- an all-null outcome row corrupts '
                'every scripted rate computation over the log.' % a.run_id)
        for name, value in recovered.items():
            if getattr(a, name, None) is None and value is not None:
                setattr(a, name, value)
        print('note-kv recovery: %s' % {k: v for k, v in recovered.items() if v is not None})
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


def cmd_prompt(a):
    """Emit a deterministic load-representative probe prompt (>= PAYLOAD_FLOOR_BYTES).

    Shaped like a real masked band-4 skeleton: multi-KB of German sense lines with {Tn}
    placeholders, asking for a Russian rendering — so the probe exercises the same
    long-prompt / long-generation path that actually degrades, not a one-word ping.
    """
    sense = ('— %d) {T%d} der Zustand des %s, Verfassung, Lage; auch übertragen von '
             'Verhältnissen des Lebens und der Gesellschaft {T%d}; mit näherer Bestimmung '
             'im Instrumental oder im Compositum vorangehend {T%d}.\n')
    words = ['Wassers', 'Feuers', 'Windes', 'Geistes', 'Körpers', 'Landes', 'Volkes',
             'Rechtes', 'Opfers', 'Himmels']
    body = []
    i = 0
    while sum(len(s.encode('utf-8')) for s in body) < PAYLOAD_FLOOR_BYTES + 1024:
        i += 1
        body.append(sense % (i, 3 * i - 2, words[i % len(words)], 3 * i - 1, 3 * i))
    skeleton = ''.join(body)
    prompt = (
        'PROBE (load-representative, not production): translate the masked German sense '
        'lines below into Russian, keeping every {Tn} placeholder exactly where it stands. '
        'Return only the translated lines.\n\n=== CARD probe~~h462 ===\n' + skeleton)
    print(prompt)
    print(f'\n--- probe payload: {len(prompt.encode("utf-8"))} bytes '
          f'(floor {PAYLOAD_FLOOR_BYTES}); time the agent() call, then record with:\n'
          f'    python src/pilot/probe_log.py append --kind warmup '
          f'--latency-ms <ms> --conn-errors <n> --payload-bytes {len(prompt.encode("utf-8"))} ...',
          file=sys.stderr)
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
        f'Gate (per [`Uprava/SERVER_OUTAGES.md`](https://github.com/gasyoun/Uprava/blob/main/SERVER_OUTAGES.md)',
        f'+ H462): 0 `Connection closed mid-response`, latency < {LATENCY_CEIL_MS // 1000}s, and the',
        f'warm-up prompt must be load-representative — >= {PAYLOAD_FLOOR_BYTES} bytes of skeleton-shaped',
        'payload (`python src/pilot/probe_log.py prompt`). A trivial one-word probe said GO on',
        '10-07-2026 and the window still degraded; payload size is now part of the verdict.',
        '',
        '## Readings',
        '',
        '| ts (UTC) | kind | verdict | latency | conn-err | payload | window | H### | note |',
        '|---|---|---|---:|---:|---:|---|---|---|',
    ]
    for r in rows:
        if r.get('kind') == 'outcome':
            continue
        p = r.get('probe') or {}
        lat = p.get('latency_ms')
        pb = p.get('payload_bytes')
        out.append('| {} | {} | {} | {} | {} | {} | {} | {} | {} |'.format(
            r['ts'], r['kind'], r['verdict'],
            f'{lat/1000:.1f}s' if isinstance(lat, int) else '—',
            _cell(p.get('conn_errors')),
            f'{pb}B' if isinstance(pb, int) else '—',
            _cell(r.get('window')),
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
    p.add_argument('--payload-bytes', type=int,
                   help='probe prompt size in bytes; a warmup below %d B (or without '
                        'this flag) is NO-GO — see `probe_log.py prompt` (H462)'
                        % PAYLOAD_FLOOR_BYTES)
    p.add_argument('--agent-model', default='claude-sonnet-5')
    # G10 (F-B4): tracks CURRENT_POLICY, not a frozen literal — see `verdict_for`.
    p.add_argument('--policy', choices=sorted(POLICIES), default=CURRENT_POLICY)
    p.add_argument('--api-ms', type=int,
                   help='envelope duration_api_ms; checked against the policy api_ceil_ms '
                        '(H2138 second, independent fail condition). Omit when the reading '
                        'carries no decomposition — the gate then falls back to wall alone.')
    p.add_argument('--schema-valid', action='store_true', default=None,
                   help='measured response passed the representative output schema')
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

    p = sub.add_parser('prompt', help='emit a load-representative (>=5KB) probe prompt (H462)')
    p.set_defaults(func=cmd_prompt)

    p = sub.add_parser('render', help='rewrite the Markdown table from the JSONL')
    p.set_defaults(func=cmd_render)

    a = ap.parse_args()
    sys.exit(a.func(a))


if __name__ == '__main__':
    main()
