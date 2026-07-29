#!/usr/bin/env python
r"""H1210 — lift a control-round Workflow return value out of its task-output file.

Twin of `collect_arm_a.py`, for the standalone shared-controller runs: pulls `result`
(the {arm, round, verdicts[]} object `control_template.js` returns) into the verdicts file
`arm_b_control.py apply` consumes, and reports the controller's own token/agent usage so
arm B's controller spend is accounted the same way arm A's is.

Usage:
  python src/pilot/h1210/extract_verdicts.py <task_output.json> <out_verdicts.json>
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


def main():
    if len(sys.argv) != 3:
        sys.exit('usage: extract_verdicts.py <task_output.json> <out_verdicts.json>')
    d = json.load(open(sys.argv[1], encoding='utf-8'))
    res = d.get('result')
    if not isinstance(res, dict) or 'verdicts' not in res:
        sys.exit('FAIL: %s carries no control result (keys: %s)' % (sys.argv[1], list(d)))
    agents = [r for r in (d.get('workflowProgress') or []) if r.get('type') == 'workflow_agent']
    res['usage'] = {
        'agents': len(agents),
        'errors': sum(1 for r in agents if r.get('state') == 'error'),
        'tokens': d.get('totalTokens'),
        'duration_ms': sum(r.get('durationMs') or 0 for r in agents),
        'models': sorted({r.get('model') for r in agents if r.get('model')}),
    }
    with open(sys.argv[2], 'w', encoding='utf-8', newline='\n') as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
        f.write('\n')
    ok = sum(1 for v in res['verdicts'] if (v.get('verdict') or {}).get('ok'))
    null = sum(1 for v in res['verdicts'] if v.get('verdict') is None)
    print('wrote %s: round %s, %d verdicts (%d ok, %d rejected, %d null), %s tokens'
          % (os.path.basename(sys.argv[2]), res.get('round'), len(res['verdicts']), ok,
             len(res['verdicts']) - ok - null, null, res['usage']['tokens']))


if __name__ == '__main__':
    main()
