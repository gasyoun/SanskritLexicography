#!/usr/bin/env python
r"""Inject the slice payload into the controller-worker Workflow template.

Workflow scripts have no filesystem access, so the payload is embedded as a `const`.
Building it here (not by hand) keeps the 81 KB JSON out of the tool-call surface.

Usage: python inject_payload.py <template.js> <slice_args.json> <out_run.js>
"""
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

tpl_path, args_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
tpl = open(tpl_path, encoding='utf-8').read()
payload = json.load(open(args_path, encoding='utf-8'))
# Compact, valid JS literal (JSON is a subset of JS object syntax).
lit = json.dumps(payload, ensure_ascii=False)
marker_start = '/*__PAYLOAD__*/ null /*__END__*/'
if marker_start not in tpl:
    sys.exit('payload marker not found in template')
out = tpl.replace(marker_start, lit)
with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(out)
print('wrote', out_path, len(out), 'bytes;', len(payload['cards']), 'cards embedded')
