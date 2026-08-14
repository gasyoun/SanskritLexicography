#!/usr/bin/env python
"""Snapshot unique unfilled definition_gloss rows from a wave dir."""
from __future__ import annotations

import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import pwg_tm_generate as Gen  # noqa: E402


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    out_dir = argv[0] if argv else Gen.DEFAULT_OUT
    q_path = os.path.join(out_dir, 'quarantine.jsonl')
    dest = argv[1] if len(argv) > 1 else os.path.join(out_dir, 'needed_drafts.jsonl')
    rows = []
    with open(q_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            rows.append(row)
    unique = Gen.unique_unfilled_rows(rows)
    gloss = [r for r in unique if r['fragment_class'] == 'definition_gloss']
    sense = [r for r in unique if r['fragment_class'] == 'sense']
    os.makedirs(os.path.dirname(dest) or '.', exist_ok=True)
    Gen.C.write_jsonl(dest, gloss)
    print(json.dumps({
        'quarantine_rows': len(rows),
        'unique_unfilled_total': len(unique),
        'unique_gloss': len(gloss),
        'unique_sense': len(sense),
        'gloss_occurrences': sum(r.get('n_same_source') or 1 for r in gloss),
        'out': dest,
    }, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
