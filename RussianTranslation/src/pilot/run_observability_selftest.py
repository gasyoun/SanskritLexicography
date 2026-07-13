#!/usr/bin/env python
import json
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import run_observability as o


def main():
    with tempfile.TemporaryDirectory() as td:
        events = os.path.join(td, 'events.jsonl')
        o.append_event(events, run_id='r1', lease_id='w1', key='k1', attempt=1,
                       account='acc1', manifest_hash='a' * 64, stage='worker',
                       event='model_call', classification='timeout', elapsed_ms=100)
        o.append_event(events, run_id='r1', lease_id='w1', key='k1', attempt=2,
                       account='acc1', stage='worker', event='model_call',
                       classification='timeout', elapsed_ms=20)
        o.append_event(events, run_id='r1', stage='acceptance', event='run_summary',
                       classification='no_go', cards=2, clean=1, calls=2,
                       retries=1, fidelity_rejects=1, unaccounted_keys=['k2'])
        census = o.build_census(o.read_events(events))
        assert census['latency_ms'] == {'p50': 20, 'p95': 100, 'max': 100}
        assert census['repeated_by_key']['k1'] == {'timeout': 2}
        assert census['clean_rate'] == .5 and census['unaccounted_keys'] == ['k2']
        try:
            o.append_event(events, prompt='secret')
        except ValueError:
            pass
        else:
            raise AssertionError('unsafe prompt field was accepted')
        out = os.path.join(td, 'bug_census.json')
        assert o.write_census(events, out)['schema'] == 'pwg.bug_census.v1'
        assert json.load(open(out, encoding='utf-8'))['calls'] == 2
    print('run_observability_selftest: PASS')


if __name__ == '__main__':
    main()
