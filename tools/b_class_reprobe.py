#!/usr/bin/env python3
"""Monthly scripted re-probe of the 13 class-B findings (verifiability.json).

Every class-B row of epistemic_dashboard/verifiability.json holds a claim about a
live external host (the H1362 ruling's "B — re-probeable" class). This tool runs
each row's own re-probe recipe as a cheap scripted check and writes the verdict +
last-verified stamp back per row (`reprobe` key), so a B-row claim can never go
silently stale — the failure mode this lane exists to defeat (H7593). A `stale`
verdict is data recorded loudly, not a crash: the monthly refresh commits it and
the findings dashboard renders it.

MUST run from the residential machine — several target hosts (Cologne, Inria,
archive.org pair routes) treat datacenter IPs differently (Uprava FINDINGS §1;
same constraint as findings_dashboard/probe_platforms.py). Wired monthly via
findings_dashboard/monthly_refresh.py.

Verdict vocabulary:
  verified     live probe reproduces the claim's true-signature
  stale        host answered, but the claim's signature changed — finding needs
               re-adjudication (recorded loudly in the dashboard)
  inconclusive network/runtime failure — no evidence about the claim; the row
               simply keeps its previous stamp until a run sees it

archive.org rows follow FINDINGS §651 mechanics: paired same-date items (the
correct-labelled one may be darked — the sibling is the route), 504-retries, and
"verify the masthead, never the item id".
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from b_class_reprobe_core import VERIF, VERDICTS, stamp  # noqa: E402
from b_class_reprobe_probes_a import (  # noqa: E402
    probe_41, probe_47, probe_48, probe_49, probe_50, probe_56, probe_57)
from b_class_reprobe_probes_b import (  # noqa: E402
    probe_68, probe_75, probe_95, probe_448, probe_451, probe_652)

PROBES = {'41': probe_41, '47': probe_47, '48': probe_48, '49': probe_49,
          '50': probe_50, '56': probe_56, '57': probe_57, '68': probe_68,
          '75': probe_75, '95': probe_95, '448': probe_448, '451': probe_451,
          '652': probe_652}


def main(argv):
    only = None
    skip_write = False
    args = list(argv)
    if '--skip-write' in args:
        args.remove('--skip-write')
        skip_write = True
    if args:
        only = args
    results = {}
    for hid in (only or B_IDS):
        fn = PROBES[hid]
        print(f'  §{hid} …')
        try:
            r = fn()
        except Exception as e:  # noqa: BLE001 - a failed probe is a recorded verdict
            r = {'verdict': 'inconclusive',
                 'detail': f'probe crashed: {e.__class__.__name__}: {str(e)[:150]}'}
        results[hid] = r
        print(f'    -> {r["verdict"]}: {r["detail"][:110]}')
    if skip_write:
        print('skip-write: verdicts printed, verifiability.json untouched')
        return 0
    d = json.loads(VERIF.read_text(encoding='utf-8'))
    now = stamp()
    for hid, r in results.items():
        d['findings'][hid]['reprobe'] = {'verdict': r['verdict'], 'checked_at': now,
                                         'detail': r['detail']}
    # Summary is FILE-truth (all stamped rows), not the run subset — a per-row
    # re-run must not shrink the board's counts.
    stamps = {fid: row['reprobe'] for fid, row in d['findings'].items()
              if isinstance(row.get('reprobe'), dict) and row['reprobe'].get('verdict')}
    d['b_reprobe'] = {'last_run': now, 'tool': 'tools/b_class_reprobe.py',
                      'probe_host': 'residential (local machine)',
                      'probed': sorted(results),
                      'verdicts': {v: sum(1 for s in stamps.values() if s.get('verdict') == v)
                                   for v in VERDICTS}}
    VERIF.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'wrote {VERIF}: ' + ', '.join(f'{k}={v}' for k, v in d['b_reprobe']['verdicts'].items()))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
