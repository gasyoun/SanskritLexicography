#!/usr/bin/env python
"""Refresh a frozen sample from current promoted/quarantine by fragment_id."""
from __future__ import annotations

import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


def main():
    sample_path = sys.argv[1]
    out_dir = sys.argv[2]
    dest = sys.argv[3] if len(sys.argv) > 3 else sample_path
    sample = [json.loads(l) for l in open(sample_path, encoding='utf-8') if l.strip()]
    want = {r['fragment_id']: i for i, r in enumerate(sample) if r.get('fragment_id')}
    found = {}
    for name in ('promoted.jsonl', 'quarantine.jsonl'):
        path = os.path.join(out_dir, name)
        with open(path, encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                row = json.loads(line)
                fid = row.get('fragment_id')
                if fid in want:
                    found[fid] = row
                    if len(found) == len(want):
                        break
        if len(found) == len(want):
            break
    updated = 0
    missing = 0
    out_rows = []
    for row in sample:
        fid = row.get('fragment_id')
        if fid in found:
            out_rows.append(found[fid])
            updated += 1
        else:
            out_rows.append(row)
            missing += 1
    with open(dest, 'w', encoding='utf-8', newline='\n') as f:
        for row in out_rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    unfilled = sum(
        1 for r in out_rows
        if (r.get('generation') or {}).get('origin') == 'unfilled'
        or not (r.get('target_string') or '').strip())
    print(json.dumps({
        'sample': len(out_rows),
        'refreshed': updated,
        'missing_in_store': missing,
        'still_unfilled': unfilled,
    }, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
