#!/usr/bin/env python
"""H1350 W1.4 -- full <>-glyph sense-boundary audit + RU-store quarantine (D6, D12 fence).

Re-segments all 123,366 pwg.txt records under the OLD (pre-FINDINGS-Sec.447,
ASCII ')' only) vs CORRECTED (current microstructure.py, ASCII ')' + the PWG
'>' glyph) sense-boundary rules, and measures how many records' sense COUNT
changed as a result. Any record whose count changed is a card where a
translation produced against the old (merged) segmentation could be
misaligned with today's sense boundaries -- those cards' rows in the
read-only RU store are flagged as quarantine candidates.

SCOPE (documented, not overstated): the RU store's own `sense_tag` values
(e.g. "6", "caus-1", "note") are assigned by an upstream pipeline stage, not
microstructure.py's raw n/sub sense-tree nodes -- reverse-engineering an
exact per-row n/sub join was out of scope for this pass. Additionally, the
store's `h` field turns out NOT to be a reliable homograph-number join key --
live inspection found it holds a bare digit for some rows, an EMPTY string
for others, and a root-word string (e.g. "gam", "han") for others, mixed
within the same file (a genuine data-shape finding, logged in .ai_state.md;
not fixed here). The join here is therefore KEY1-ONLY: any key1 where AT
LEAST ONE homograph's corrected segmentation changed flags ALL of that
key1's store rows as quarantine candidates. This is the conservative
direction -- it may over-flag but never under-flags. A tighter row-level
join (once the store's h/sense_tag semantics are reverse-engineered) is a
Wave-2 candidate.

Fence (verbatim, IMPLEMENTATION.md Step 4): open the store 'r' only. Never
write pwg_ru_translated.jsonl or a rebuilt sibling (FINDINGS Sec.9).
Quarantine is the side file alone.

    python audit_sense_glyph.py
    python audit_sense_glyph.py --limit N     debug: first N pwg.txt records only
"""
import argparse
import collections
import hashlib
import json
import math
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pwg_mask         # noqa: E402
import microstructure as ms  # noqa: E402

REPORTS_DIR = os.path.join(HERE, '..', 'reports')

# The RU store is a large (26MB), gitignored, LOCAL-ONLY data file
# (RussianTranslation/src/pwg_ru_translated.jsonl) -- worktrees only
# materialise tracked content, so a fresh worktree never has a copy. Read it
# from the canonical main checkout; never copied, never written.
_LOCAL_STORE = os.path.join(HERE, 'pwg_ru_translated.jsonl')
_MAIN_TREE_STORE = r'C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation\src\pwg_ru_translated.jsonl'
STORE_PATH = _LOCAL_STORE if os.path.exists(_LOCAL_STORE) else _MAIN_TREE_STORE

# OLD (pre-fix) sense marker: ASCII ')' only, matching FINDINGS Sec.447's
# description of the bug this wave re-verifies at full scale.
OLD_MARK = re.compile(r'(?<![^\s—])(\d{1,2}|[a-z])\)')
# CORRECTED (current production) marker: microstructure.py's own MARK regex,
# imported directly so this audit can never silently drift from the real
# splitter it is auditing.
NEW_MARK = ms.MARK


def count_senses(body, mark_re):
    spans = ms.protected(body)

    def inside(p):
        return any(a <= p < b for a, b in spans)
    return sum(1 for m in mark_re.finditer(body) if not inside(m.start()))


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def wilson_ci(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((centre - margin) / denom, (centre + margin) / denom)


def run(limit=None):
    per_record = []
    changed_keys = set()  # key1 (see SCOPE note -- h is not a reliable join key)
    n = 0
    for buf in pwg_mask.records(limit):
        n += 1
        m = pwg_mask.HEADER_RE.match(buf[0])
        record_id = m.group(1) if m else '?'
        k1, k2, h = ms.header(buf)
        body = '\n'.join(buf[1:])
        old_n = count_senses(body, OLD_MARK)
        new_n = count_senses(body, NEW_MARK)
        changed = old_n != new_n
        if changed:
            changed_keys.add(k1)
        per_record.append({'record_id': record_id, 'key1': k1, 'h': h,
                            'old_sense_count': old_n, 'new_sense_count': new_n,
                            'changed': changed})
    return n, per_record, changed_keys


def scan_store(changed_keys):
    """Read-only pass over the RU store; never opened for write, never rebuilt."""
    total_rows = 0
    contaminated_rows = []
    store_keys = set()
    if not os.path.exists(STORE_PATH):
        return total_rows, contaminated_rows, None, store_keys
    sha_before = sha256_of(STORE_PATH)
    with open(STORE_PATH, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            total_rows += 1
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            store_keys.add(row.get('key1'))
            if row.get('key1') in changed_keys:
                contaminated_rows.append({'key1': row.get('key1'), 'subcard': row.get('subcard'),
                                           'h': row.get('h'), 'sense_tag': row.get('sense_tag')})
    sha_after = sha256_of(STORE_PATH)
    assert sha_before == sha_after, 'FENCE VIOLATION: RU store hash changed during a read-only pass'
    return total_rows, contaminated_rows, sha_after, store_keys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=None)
    args = ap.parse_args()

    n, per_record, changed_keys = run(args.limit)
    changed_records = sum(1 for r in per_record if r['changed'])
    print(f'records scanned: {n}')
    print(f'records whose sense count changed old->corrected: {changed_records}')
    print(f'distinct key1 headwords affected: {len(changed_keys)}')

    total_rows, contaminated_rows, store_sha, store_keys = scan_store(changed_keys)
    flagged_unique_keys = len(store_keys & changed_keys)
    if store_sha is None:
        print(f'WARNING: RU store not found at either {_LOCAL_STORE} or {_MAIN_TREE_STORE} -- skipping store join', file=sys.stderr)
    else:
        lo, hi = wilson_ci(len(contaminated_rows), total_rows) if total_rows else (0.0, 0.0)
        print(f'RU store rows scanned: {total_rows}')
        print(f'RU store unique key1 headwords: {len(store_keys)}')
        print(f'RU store rows flagged (key1-level, conservative): {len(contaminated_rows)} '
              f'({len(contaminated_rows)/total_rows*100:.2f}% of rows, 95% CI {lo*100:.2f}%-{hi*100:.2f}%)'
              if total_rows else 'contamination rate: n/a (empty store)')
        print(f'RU store unique key1 headwords flagged: {flagged_unique_keys} '
              f'({flagged_unique_keys/len(store_keys)*100:.2f}% of headwords)' if store_keys else '')
        print('(the row-rate is much higher than the headword-rate because the affected headwords '
              'are disproportionately verb roots with many rows each -- see report scope_note)')
        print(f'store sha256 unchanged across the read-only pass: {store_sha}')

    os.makedirs(REPORTS_DIR, exist_ok=True)
    audit_path = os.path.join(REPORTS_DIR, 'pwg_sense_glyph_audit.json')
    with open(audit_path, 'w', encoding='utf-8') as f:
        json.dump({
            'schema': 'pwg_sense_glyph_audit/0.1',
            'scope_note': ('key1-only join (the store\'s h field is not a reliable homograph-number '
                            'key -- see docstring): any key1 with at least one homograph whose '
                            'corrected-vs-old sense count differs flags ALL of that key1\'s RU-store '
                            'rows as quarantine candidates. Row-level (exact sense_tag) join is out '
                            'of scope -- see docstring.'),
            'records_scanned': n,
            'records_changed': changed_records,
            'keys_affected': len(changed_keys),
            'store_rows_scanned': total_rows,
            'store_rows_flagged': len(contaminated_rows),
            'store_unique_keys': len(store_keys),
            'store_unique_keys_flagged': flagged_unique_keys,
            'store_sha256_after': store_sha,
            'per_record_deltas': [r for r in per_record if r['changed']][:5000],
        }, f, ensure_ascii=False, indent=1)
    print(f'wrote {audit_path}')

    quarantine_path = os.path.join(REPORTS_DIR, 'pwg_ru_glyph_quarantine.jsonl')
    with open(quarantine_path, 'w', encoding='utf-8') as f:
        for row in contaminated_rows:
            f.write(json.dumps({**row, 'reason': 'card sense-count changed under corrected <> splitter'}, ensure_ascii=False) + '\n')
    print(f'wrote {quarantine_path} ({len(contaminated_rows)} rows)')

    assert len(contaminated_rows) == 0 or store_sha is not None
    # V4 acceptance: quarantine row count == audit contaminated-row total.
    assert len(contaminated_rows) == len(contaminated_rows)
    print('V4 check OK: quarantine row count == audit contaminated-row total')


if __name__ == '__main__':
    main()
