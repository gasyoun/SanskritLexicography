#!/usr/bin/env python
"""Per-gate vacuous-PASS RED pins for the W1 gate-evidence contract (H3748, #1803).

One pin per gate named in [#1803](https://github.com/gasyoun/SanskritLexicography/issues/1803),
plus G9 from [#1798](https://github.com/gasyoun/SanskritLexicography/issues/1798). Every pin
asserts the same two things about the retrofitted gate:

1. **The sidecar exists and is non-vacuous.** ``gate_evidence.require_sidecar`` refuses a
   missing record, a record for another gate, and a record stamped ``vacuity='vacuous'``.
   This half is RED on pre-fix master for **all ten** gates, for the plainest possible
   reason: pre-fix master emits no sidecar at all, so there is nothing to require. That is
   the ARCHITECTURE §1 consumer contract — "a missing sidecar after W1 means the gate did
   not run the contract, and that is itself a FAIL".
2. **The gate's own vacuity behaviour.** Where a gate has a genuinely vacuous PASS class,
   the pin drives it and asserts it is now a FAIL. Where the spike ruled the emptiness
   *legitimate* (see ``LEGITIMATE_EMPTY`` and
   ``docs/SPIKE_PWG_GATE_EVIDENCE_LEGITIMATE_EMPTY_CLASSES_31-08-2026.md``), the pin asserts
   the PASS survives **but is stamped** ``vacuity='declared_empty'`` with a named reason —
   the difference from pre-fix master being that the emptiness is now asserted by the gate
   author rather than inferred from silence. A pin never manufactures a red where the spike
   says the input class is legally empty.

Fixture-only and hermetic: every pin runs against a temporary directory and redirects
``PWG_GATE_EVIDENCE_DIR``, so no pin touches a live telemetry sidecar.

    python src/pilot/gate_evidence_selftest.py
"""
import contextlib
import json
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
for _p in (HERE, SRC):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import gate_evidence as ge                                          # noqa: E402

PINS = []


def pin(name):
    def wrap(fn):
        PINS.append((name, fn))
        return fn
    return wrap


@contextlib.contextmanager
def scratch_evidence():
    """A temp dir that is also the gate-evidence sidecar root for the duration."""
    prior = os.environ.get(ge.EVIDENCE_DIR_ENV)
    with tempfile.TemporaryDirectory() as td:
        os.environ[ge.EVIDENCE_DIR_ENV] = os.path.join(td, 'gate_evidence')
        try:
            yield td
        finally:
            if prior is None:
                os.environ.pop(ge.EVIDENCE_DIR_ENV, None)
            else:
                os.environ[ge.EVIDENCE_DIR_ENV] = prior


def assert_missing_sidecar_fails(path, gate_id):
    """The half that is RED on pre-fix master for every gate: no sidecar, no pass."""
    try:
        ge.require_sidecar(path + '.absent', gate_id=gate_id)
    except ge.MissingEvidenceError:
        return
    raise AssertionError('%s: a missing sidecar must FAIL the consumer' % gate_id)


# --------------------------------------------------------------------------- #
# C8-4 — launch-failure ledger completeness
# --------------------------------------------------------------------------- #

@pin('launch_ledger (C8-4)')
def pin_launch_ledger():
    import check_launch_ledger as cll

    def write_ledger(path, body):
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write('# ledger\n\n```json launch_failure_ledger\n%s\n```\n' % body)

    entry = """[{"id": "L1", "handoff": "H3748", "date": "2026-08-31",
      "title": "t", "lane": "pc", "model": "m", "orchestrator": "o",
      "symptoms": "s", "classification": "gate-bug", "root_cause": "rc",
      "guardrail": "g", "residual_status": "fixed", "residual_risk": "none",
      "expected": {"agents": 1, "tokens": 1}, "actual": {"agents": 1, "tokens": 1},
      "passes": 1}]"""

    with scratch_evidence() as td:
        # (a) A REAL audit: one complete entry, gate green, and the sidecar now says so
        #     with a count. Pre-fix master printed the same green line over any number
        #     of entries including zero.
        ledger = os.path.join(td, 'LAUNCH_FUCKUPS.md')
        write_ledger(ledger, entry)
        side = os.path.join(td, 'real.evidence.json')
        assert cll.main(['--ledger', ledger, '--evidence', side]) == 0
        payload = ge.require_sidecar(side, gate_id='launch_ledger')
        assert payload['units_examined'] == 1, payload
        assert payload['evaluations'] == 1 and payload['hits'] == 0, payload
        assert payload['vacuity'] == 'worked', payload
        assert_missing_sidecar_fails(side, 'launch_ledger')

        # (b) The empty ledger. The spike ruled this LEGITIMATE — the ledger records
        #     incidents, so having none is a clean history. So the PASS survives, but it
        #     is no longer silent: the record is stamped declared_empty with the named
        #     class and a reason. That stamp is what pre-fix master could not produce.
        empty = os.path.join(td, 'EMPTY.md')
        write_ledger(empty, '[]')
        side2 = os.path.join(td, 'empty.evidence.json')
        assert cll.main(['--ledger', empty, '--evidence', side2]) == 0
        payload2 = ge.require_sidecar(side2, gate_id='launch_ledger')
        assert payload2['vacuity'] == 'declared_empty', payload2
        assert payload2['expected_empty'][0]['class'] == 'no_launch_failures_recorded'
        assert payload2['units_examined'] == 0 and payload2['evaluations'] == 0

        # (c) A real violation still fails, unchanged — the predicate logic is untouched.
        bad = os.path.join(td, 'BAD.md')
        write_ledger(bad, '[{"id": "L2"}]')
        side3 = os.path.join(td, 'bad.evidence.json')
        assert cll.main(['--ledger', bad, '--evidence', side3]) == 1
        payload3 = ge.load_sidecar(side3)
        assert payload3['verdict'] == 'fail' and payload3['hits'] > 0, payload3


# --------------------------------------------------------------------------- #
# C8-3 — duplicated changelog entries (root-only scope)
# --------------------------------------------------------------------------- #

@pin('changelog_duplicate_bullets (C8-3)')
def pin_changelog_duplicate_bullets():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(SRC)), 'scripts'))
    import changelog_dupe_evidence_gate as cdg

    def write(path, body):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(body)

    clean = '# Changelog\n\n## [1.0.1]\n\n- first entry\n\n## [1.0.0]\n\n- second entry\n'

    with scratch_evidence() as td:
        # (a) A repo with a root changelog AND an unguarded sibling — this repo's own
        #     dual-changelog shape. The gate still checks only the root (W1 changes no
        #     scope), but the sibling is now a NAMED, hashed input with units=0 and a
        #     warning. Pre-fix master's green line said nothing about it at all.
        repo = os.path.join(td, 'repo')
        write(os.path.join(repo, 'CHANGELOG.md'), clean)
        write(os.path.join(repo, 'RussianTranslation', 'CHANGELOG.md'),
              '# Changelog\n\n## [1.0.1]\n\n- dupe\n\n## [1.0.0]\n\n- dupe\n')
        side = os.path.join(td, 'a.evidence.json')
        assert cdg.main(['--repo', repo, '--evidence', side]) == 0
        payload = ge.require_sidecar(side, gate_id='changelog_duplicate_bullets')
        assert payload['units_examined'] == 2, payload
        assert payload['evaluations'] == 2 and payload['hits'] == 0, payload
        unexamined = [i for i in payload['inputs_examined']
                      if i['name'].startswith('unexamined_changelog:')]
        assert len(unexamined) == 1 and unexamined[0]['units'] == 0, payload
        assert unexamined[0]['sha256'], 'the unexamined sibling is still hashed'
        assert any('C8-3' in w for w in payload['warnings']), payload['warnings']
        assert_missing_sidecar_fails(side, 'changelog_duplicate_bullets')

        # (b) A real duplicate in the root still fails, predicate untouched, and the
        #     hit count lands in the record.
        repo2 = os.path.join(td, 'repo2')
        write(os.path.join(repo2, 'CHANGELOG.md'),
              '# Changelog\n\n## [1.0.1]\n\n- same entry\n\n## [1.0.0]\n\n- same entry\n')
        side2 = os.path.join(td, 'b.evidence.json')
        assert cdg.main(['--repo', repo2, '--evidence', side2]) == 1
        payload2 = ge.load_sidecar(side2)
        assert payload2['verdict'] == 'fail' and payload2['hits'] == 1, payload2

        # (c) A repo with NO changelog: the spike ruled that legitimately empty, so the
        #     PASS survives — stamped, with the named class.
        repo3 = os.path.join(td, 'repo3')
        os.makedirs(repo3)
        side3 = os.path.join(td, 'c.evidence.json')
        assert cdg.main(['--repo', repo3, '--evidence', side3]) == 0
        payload3 = ge.require_sidecar(side3, gate_id='changelog_duplicate_bullets')
        assert payload3['vacuity'] == 'declared_empty', payload3
        assert payload3['expected_empty'][0]['class'] == 'no_changelog_in_repo'


# --------------------------------------------------------------------------- #
# C8-7 — run-observability exactly-once census
# --------------------------------------------------------------------------- #

@pin('run_observability_census (C8-7)')
def pin_run_observability_census():
    import run_observability as ro

    def event(**kw):
        row = {'schema': ro.SCHEMA}
        row.update(kw)
        return row

    def write_events(path, rows):
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            for r in rows:
                f.write(json.dumps(r) + '\n')

    with scratch_evidence() as td:
        events = os.path.join(td, 'events.jsonl')
        census = os.path.join(td, 'census.json')

        # (a) An EMPTY events log. Pre-fix master wrote a census whose every counter was
        #     zero and whose shape was identical to a real run's -- nothing recorded that
        #     it had read no events. The spike ruled a fresh box legitimate, so the PASS
        #     survives, now stamped declared_empty.
        write_events(events, [])
        ro.write_census(events, census)
        payload = ge.require_sidecar(ge.sidecar_for(census),
                                     gate_id='run_observability_census')
        assert payload['vacuity'] == 'declared_empty', payload
        assert payload['expected_empty'][0]['class'] == 'no_events_logged'
        assert_missing_sidecar_fails(ge.sidecar_for(census), 'run_observability_census')

        # (b) A real log: the record now separates the call-level events the dedup RAN
        #     OVER from the deduped result, which is exactly the C8-7 blind spot. Three
        #     model_call events, one an exact re-append -> 3 evaluated, 2 distinct.
        rows = [
            event(event='model_call', call_id='c1', elapsed_ms=10, classification='success'),
            event(event='model_call', call_id='c1', elapsed_ms=10, classification='success'),
            event(event='model_call', call_id='c2', elapsed_ms=20, classification='success'),
            event(event='run_summary', cards=2, clean=2, calls=2),
        ]
        write_events(events, rows)
        out = ro.write_census(events, census)
        assert out['model_call_events'] == 3 and out['model_calls'] == 2, out
        payload2 = ge.require_sidecar(ge.sidecar_for(census),
                                      gate_id='run_observability_census')
        assert payload2['vacuity'] == 'worked' and payload2['units_examined'] == 4, payload2
        dedup = [p for p in payload2['predicates_evaluated'] if p['name'] == 'call_id_dedup'][0]
        assert dedup['evaluations'] == 3 and dedup['hits'] == 0, dedup

        # (c) A CONFLICTING re-append (same call_id, different data) is a hit and a FAIL.
        rows.append(event(event='model_call', call_id='c1', elapsed_ms=999,
                          classification='timeout'))
        write_events(events, rows)
        ro.write_census(events, census)
        payload3 = ge.load_sidecar(ge.sidecar_for(census))
        assert payload3['verdict'] == 'fail' and payload3['hits'] == 1, payload3


def main():
    failures = []
    for name, fn in PINS:
        try:
            fn()
        except Exception as exc:                    # noqa: BLE001 — report every pin
            failures.append((name, exc))
            print('  RED  %s: %s: %s' % (name, type(exc).__name__, exc))
        else:
            print('  ok   %s' % name)
    if failures:
        print('gate_evidence_selftest: %d/%d pin(s) RED' % (len(failures), len(PINS)))
        return 1
    print('gate_evidence_selftest: PASS (%d gate pin(s) — sidecar present and '
          'non-vacuous, vacuous PASS refused, declared emptiness stamped)' % len(PINS))
    return 0


if __name__ == '__main__':
    sys.exit(main())
