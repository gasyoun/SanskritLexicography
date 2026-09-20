"""H4527 work item 1 — serial-vs-cohort acceptance comparison receipt (one-shot).

Compares the first CLEAN ACCEPTED window taken through the live cohort dispatch
(`bounded_staged_run --execute --cohort-path --cohort-width 1`, 20-09-2026) against
the last window taken through the SERIAL supervisor, on the three axes work item 1
names: sealed artifacts, journal advancement and promotion discipline.

What this receipt proves, and what it deliberately does NOT:

* It does NOT diff the same card through both routes, and no run can. A sub-card is
  translated once and promoted once; re-running an already-promoted key is not the
  serial route, it is a different window on different input.
* It does NOT compare two same-OUTCOME windows either, and this is the honest limit
  worth recording: the only serial-supervisor window on this box settled
  `needs_requeue`, while the cohort window settled `clean`. A file present on one
  side and absent on the other is therefore classified as OUTCOME-driven (a requeued
  window writes `requeue/`; a clean one writes `wf_output.clean.*`) rather than
  route-driven, and the receipt says so instead of scoring it as a mismatch.
* What it DOES prove is structural identity where the two routes can be compared at
  all: the same sealed-artifact file set once outcome-driven and content-hashed names
  are accounted for, the same JSON schemas, and — the strongest signal — the same
  `window_status.json` and `window_ledger.jsonl` FIELD SETS, which is where a route
  that advanced the journal differently would show it.
* Card-byte identity across widths 1/2/3 was proven offline by H1437 Phase 4
  (clean/requeue decisions, accepted order and store bytes byte-identical on
  simulated waves). This receipt is the live structural half of that claim, not a
  replacement for it.

Read-only. Spawns nothing, writes nothing, costs nothing.
"""

import json
import os
import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

_HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ARTIFACTS = os.path.join(_HERE, 'output', 'coordinator', 'artifacts')

SERIAL_LEASE = 'h4213can091108282902'
COHORT_LEASE = 'h4527sen08'

# A submitted_result carries a content hash in its name; two different cards can
# never share it, so the hash is normalised away before the file sets are compared.
_HASHED = re.compile(r'^submitted_result\.[0-9a-f]+\.json$')

# Files whose presence is decided by the window's OUTCOME, never by its route.
# A requeued window writes the requeue payloads; a clean one writes the clean
# sealed output. Counting these as route differences would be a false positive.
OUTCOME_DRIVEN = {'requeue/', 'wf_output.clean.<lease>.json'}


def _normalise(name, lease):
    name = name.replace(lease, '<lease>')
    if _HASHED.match(name):
        return 'submitted_result.<sha>.json'
    return name


def _lease_files(artifacts, lease):
    """{normalised filename -> schema_or_None}, or None when the lease is absent."""
    root = os.path.join(artifacts, lease)
    if not os.path.isdir(root):
        return None
    out = {}
    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name)
        if os.path.isdir(path):
            out[_normalise(name, lease) + '/'] = 'DIR'
            continue
        schema = None
        if name.endswith('.json'):
            try:
                with open(path, encoding='utf-8') as fh:
                    blob = json.load(fh)
                schema = blob.get('schema') if isinstance(blob, dict) else None
            except Exception as exc:                      # unreadable is a finding
                schema = 'unreadable:%s' % type(exc).__name__
        out[_normalise(name, lease)] = schema
    return out


def _json_keys(artifacts, lease, filename):
    path = os.path.join(artifacts, lease, filename)
    if not os.path.exists(path):
        return None
    with open(path, encoding='utf-8') as fh:
        blob = json.load(fh)
    return sorted(blob.keys()) if isinstance(blob, dict) else None


def _ledger_key_sets(artifacts, lease):
    """Ordered list of each journal row's field set — the shape of the advancement."""
    path = os.path.join(artifacts, lease, 'window_ledger.jsonl')
    if not os.path.exists(path):
        return None
    rows = []
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(sorted(json.loads(line).keys()))
            except Exception:
                rows.append(['<unparseable>'])
    return rows


def _status_outcome(artifacts, lease):
    path = os.path.join(artifacts, lease, 'window_status.json')
    if not os.path.exists(path):
        return {}
    with open(path, encoding='utf-8') as fh:
        blob = json.load(fh)
    return {
        'state': blob.get('state'),
        'clean_key_count': blob.get('clean_key_count'),
        'requeue_count': blob.get('requeue_count'),
        'requeue_keys': blob.get('requeue_keys'),
        'selected_key_count': blob.get('selected_key_count'),
        'profile': blob.get('profile'),
        'next_action': blob.get('next_action'),
    }


def compare(artifacts=None):
    artifacts = artifacts or DEFAULT_ARTIFACTS
    serial = _lease_files(artifacts, SERIAL_LEASE)
    cohort = _lease_files(artifacts, COHORT_LEASE)
    if serial is None or cohort is None:
        missing = [n for n, v in ((SERIAL_LEASE, serial), (COHORT_LEASE, cohort)) if v is None]
        return {'ok': False, 'reason': 'lease artifacts absent: %s' % ', '.join(missing)}

    serial_names, cohort_names = set(serial), set(cohort)
    only_serial = sorted(serial_names - cohort_names)
    only_cohort = sorted(cohort_names - serial_names)
    route_diff = sorted(set(only_serial + only_cohort) - OUTCOME_DRIVEN)
    schema_diff = sorted(n for n in (serial_names & cohort_names) if serial[n] != cohort[n])

    status_keys = {
        'serial': _json_keys(artifacts, SERIAL_LEASE, 'window_status.json'),
        'cohort': _json_keys(artifacts, COHORT_LEASE, 'window_status.json'),
    }
    ledger = {
        'serial': _ledger_key_sets(artifacts, SERIAL_LEASE),
        'cohort': _ledger_key_sets(artifacts, COHORT_LEASE),
    }
    status_identical = status_keys['serial'] == status_keys['cohort']
    ledger_identical = ledger['serial'] == ledger['cohort']

    return {
        'schema': 'pwg.h4527_acceptance_compare.v1',
        # A PASS means: no file difference that the window's OUTCOME does not explain,
        # no schema difference, and identical journal/status field sets.
        'ok': not route_diff and not schema_diff and status_identical and ledger_identical,
        'serial_lease': SERIAL_LEASE,
        'cohort_lease': COHORT_LEASE,
        'same_outcome': (_status_outcome(artifacts, SERIAL_LEASE).get('state')
                         == _status_outcome(artifacts, COHORT_LEASE).get('state')),
        'sealed_artifacts': {
            'shared_count': len(serial_names & cohort_names),
            'serial_only': only_serial,
            'cohort_only': only_cohort,
            'outcome_driven_differences': sorted(
                set(only_serial + only_cohort) & OUTCOME_DRIVEN),
            'route_driven_differences': route_diff,
            'schema_mismatches': schema_diff,
        },
        'journal_advancement': {
            'window_status_keys_identical': status_identical,
            'window_status_key_count': len(status_keys['cohort'] or []),
            'ledger_row_key_sets_identical': ledger_identical,
            'ledger_rows': {'serial': len(ledger['serial'] or []),
                            'cohort': len(ledger['cohort'] or [])},
        },
        'promotion_discipline': {
            'serial': _status_outcome(artifacts, SERIAL_LEASE),
            'cohort': _status_outcome(artifacts, COHORT_LEASE),
        },
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    result = compare(argv[0] if argv else None)
    print(json.dumps(result, ensure_ascii=False, indent=1))
    return 0 if result.get('ok') else 1


if __name__ == '__main__':
    raise SystemExit(main())
