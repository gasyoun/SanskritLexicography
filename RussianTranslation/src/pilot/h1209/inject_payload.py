#!/usr/bin/env python
r"""Inject the slice payload into the controller-worker Workflow template.

Workflow scripts have no filesystem access, so the payload is embedded as a `const`.
Building it here (not by hand) keeps the 81 KB JSON out of the tool-call surface.

H1386 D1: the emitted script is hard-checked against WORKFLOW_SCRIPT_CAP (the Workflow
tool's 512 KB scriptPath ceiling — RUN_LOG 2026-06-29 hit it at 567 KB, at submission,
with no earlier warning). An over-cap build is REFUSED here with the split remedy
(`prep_slice.py --chunk N`) instead of dying opaquely at Workflow submission.

Usage: python inject_payload.py <template.js> <slice_args.json> <out_run.js>
"""
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# The Workflow tool's script/scriptPath byte ceiling (maxLength 524288).
WORKFLOW_SCRIPT_CAP = 512 * 1024


def inject(tpl_path, args_path, out_path):
    tpl = open(tpl_path, encoding='utf-8').read()
    payload = json.load(open(args_path, encoding='utf-8'))
    # Compact, valid JS literal (JSON is a subset of JS object syntax).
    lit = json.dumps(payload, ensure_ascii=False)
    marker_start = '/*__PAYLOAD__*/ null /*__END__*/'
    if marker_start not in tpl:
        sys.exit('payload marker not found in template')
    out = tpl.replace(marker_start, lit)
    emitted = len(out.encode('utf-8'))
    if emitted > WORKFLOW_SCRIPT_CAP:
        sys.exit(
            'REFUSED: emitted script is %d bytes > WORKFLOW_SCRIPT_CAP %d (the Workflow '
            'tool submission ceiling). Split the slice first: re-run prep_slice.py with '
            '--chunk N (N >= %d) and inject each chunk payload separately.'
            % (emitted, WORKFLOW_SCRIPT_CAP, emitted // WORKFLOW_SCRIPT_CAP + 1))
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(out)
    print('wrote', out_path, emitted, 'bytes;', len(payload['cards']), 'cards embedded')


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit('usage: inject_payload.py <template.js> <slice_args.json> <out_run.js>')
    inject(sys.argv[1], sys.argv[2], sys.argv[3])
