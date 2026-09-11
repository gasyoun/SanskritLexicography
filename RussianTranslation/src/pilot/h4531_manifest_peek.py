#!/usr/bin/env python
"""H4531: describe the generated probe manifest without dumping its prompt bytes."""
from __future__ import annotations

import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

path = sys.argv[1]
with open(path, encoding='utf-8') as handle:
    manifest = json.load(handle)
print('schema:', manifest.get('schema'))
print('top keys:', sorted(manifest))
print('selected_keys:', len(manifest.get('selected_keys') or []))
batches = manifest.get('batches') or []
print('batches:', len(batches), 'first:', json.dumps(batches[0], ensure_ascii=False)[:300])
print('prompt bytes:', len(manifest.get('prompt') or ''))
print('output_schema top:', sorted((manifest.get('output_schema') or {}).keys()))
print('model:', manifest.get('model'))
print('placeholder_maps:', len(manifest.get('placeholder_maps') or {}))
