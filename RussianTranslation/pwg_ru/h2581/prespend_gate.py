#!/usr/bin/env python
"""H2581 pre-spend gate capture — offline, zero reservations, zero dispatches.

Records the two facts that decide whether the authorised two-call sitting may
proceed at all:

1. the four named offline selftests frozen at v1.144.32, and
2. the session's *route binding* — whether this harness is actually bound to
   ``https://router.cheap``, which is what the route ``router-cheap-agent``
   means (H2504 § Transport boundary).

Credential shape is booleans only; no token value is read, printed, or stored.
This script never reserves, never dispatches, and never touches the ledger.
"""

import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
PILOT = os.path.normpath(os.path.join(HERE, '..', '..', 'src', 'pilot'))
for _path in (PILOT, os.path.normpath(os.path.join(HERE, '..', '..', 'src'))):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from gateway_route import (  # noqa: E402
    GATEWAY_BASE_URL,
    GATEWAY_ROUTE,
    credential_status,
)

SELFTESTS = (
    ('gateway_canary_contract_selftest', '3/3'),
    ('gateway_attestation_selftest', '9/9'),
    ('gateway_external_selftest', '11/11'),
    ('gateway_route_selftest', '10/10'),
)


def run_selftests():
    rows = []
    for name, expected in SELFTESTS:
        proc = subprocess.run(
            [sys.executable, os.path.join(PILOT, '%s.py' % name)],
            capture_output=True, encoding='utf-8', cwd=PILOT)
        tail = [line for line in (proc.stdout or '').splitlines() if line.strip()]
        rows.append({
            'selftest': name,
            'expected_groups': expected,
            'exit_code': proc.returncode,
            'verdict_line': tail[-1] if tail else None,
            'passed': proc.returncode == 0,
        })
    return rows


def route_binding():
    """Is this session actually bound to the gateway under qualification?"""
    status = credential_status()
    return {
        'route_under_qualification': GATEWAY_ROUTE,
        'gateway_base_url': GATEWAY_BASE_URL,
        'credential_shape': status,
        'anthropic_env_names_present': sorted(
            name for name in os.environ if name.startswith('ANTHROPIC_')),
        'session_is_gateway_bound': bool(status['base_url_is_gateway']),
    }


def main():
    binding = route_binding()
    selftests = run_selftests()
    report = {
        'schema': 'pwg.h2581_prespend_gate.v1',
        'handoff': 'H2581',
        'reservations_made': 0,
        'dispatches_made': 0,
        'offline_selftests': selftests,
        'all_selftests_pass': all(row['passed'] for row in selftests),
        'route_binding': binding,
        'gate_verdict': (
            'PROCEED' if binding['session_is_gateway_bound']
            and all(row['passed'] for row in selftests)
            else 'ZERO_CALL_STOP'),
        'stop_reason': (
            None if binding['session_is_gateway_bound']
            else 'session_not_bound_to_gateway: sealing a dispatch from this '
                 'session as route=%s would be a false provenance claim'
                 % GATEWAY_ROUTE),
    }
    out = os.path.join(HERE, 'evidence', 'prespend_gate.json')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8', newline='\n') as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write('\n')
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report['gate_verdict'] == 'PROCEED' else 3


if __name__ == '__main__':
    sys.exit(main())
