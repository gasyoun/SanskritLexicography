#!/usr/bin/env python
r"""H3 (H1940 Phase 2) byte-impact probe — the measurement the ruling requires BEFORE landing.

Compares, byte for byte, what the three checkpoint writers produce today against what
`window_common.atomic_write_json` would produce if they were routed through it. The ruling
is: route through (option B) only if no difference flows into a gate-pinned hash; otherwise
fall back to inline fsync (option A) and record the call + reason.

  python src/pilot/h3_byte_probe.py
"""
import json
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
from selftest_isolation import guard as _isolation_guard  # noqa: E402
_isolation_guard()

import window_common as wc  # noqa: E402

PAYLOAD = {
    'schema': 'pwg.window_status.v1',
    'lease': 'no_pwg_w02',
    'cards': 3,
    'failures': {'_a_dikya': 'translation-fidelity-reject'},
    'unicode': 'ā ī ū ṛ ṝ',
    'nested': {'keys': ['a', 'b'], 'ok': True},
}


def current_atomic_json(path, payload):
    """Byte-for-byte what headless_worker.atomic_json does today."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + '.tmp.%d' % os.getpid()
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write('\n')
    os.replace(tmp, path)


def describe(raw):
    return {
        'bytes': len(raw),
        'crlf': raw.count(b'\r\n'),
        'lf_total': raw.count(b'\n'),
        'trailing_newline': raw.endswith(b'\n'),
    }


def main():
    with tempfile.TemporaryDirectory() as td:
        a = os.path.join(td, 'current.json')
        b = os.path.join(td, 'routed.json')
        current_atomic_json(a, PAYLOAD)
        wc.atomic_write_json(b, PAYLOAD)
        raw_a, raw_b = open(a, 'rb').read(), open(b, 'rb').read()

    print('platform os.linesep : %r' % os.linesep)
    print('current atomic_json          : %s' % describe(raw_a))
    print('window_common.atomic_write_json: %s' % describe(raw_b))
    print('identical bytes              : %s' % (raw_a == raw_b))
    if raw_a != raw_b:
        print('\nfirst divergence:')
        for i, (x, y) in enumerate(zip(raw_a, raw_b)):
            if x != y:
                print('  offset %d: current=%r routed=%r' % (i, bytes([x]), bytes([y])))
                print('  current head: %r' % raw_a[max(0, i - 12):i + 12])
                print('  routed  head: %r' % raw_b[max(0, i - 12):i + 12])
                break
        else:
            print('  (common prefix identical; lengths differ %d vs %d)'
                  % (len(raw_a), len(raw_b)))
    print('\nVERDICT: %s' % (
        'route-through is byte-safe (option B, no hash impact)' if raw_a == raw_b else
        'route-through CHANGES BYTES — B needs a newline pin + trailing newline, '
        'else fall back to A'))


if __name__ == '__main__':
    main()
