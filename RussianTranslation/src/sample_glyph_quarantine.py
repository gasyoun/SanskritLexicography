#!/usr/bin/env python
"""Sample the pwg_ru glyph quarantine (H1350 / §447) — report only, no re-translate.

MG ruling 29-07-2026: sample ~200 rows before any mass re-translation of the
~10,881-row flag set. This script draws a stratified sample and classifies each
row into mechanical buckets (no LLM, no store write).

  python src/sample_glyph_quarantine.py
  python src/sample_glyph_quarantine.py --n 200 --seed 20260801

Outputs:
  reports/pwg_ru_glyph_quarantine_sample_<date>.json
  pwg_ru/H_GLYPH_QUARANTINE_SAMPLE_REPORT_<date>.md  (caller may rename)

The quarantine reason is almost always "card sense-count changed under corrected
〉 splitter" — this is a *segmentation* flag, not a measured RU-quality failure.
"""
from __future__ import annotations

import argparse
import collections
import datetime
import hashlib
import json
import os
import random
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(HERE)
DEFAULT_QUAR = os.path.join(RT, 'reports', 'pwg_ru_glyph_quarantine.jsonl')
DEFAULT_AUDIT = os.path.join(RT, 'reports', 'pwg_sense_glyph_audit.json')


def load_jsonl(path):
    rows = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def stable_bucket(key1, n_buckets=10):
    h = hashlib.sha256((key1 or '').encode('utf-8')).hexdigest()
    return int(h[:8], 16) % n_buckets


def sample_stratified(rows, n, seed):
    """Stratify by key1 hash bucket so we do not over-sample one lemma family."""
    by_b = collections.defaultdict(list)
    for r in rows:
        by_b[stable_bucket(r.get('key1') or '')].append(r)
    rng = random.Random(seed)
    for b in by_b:
        rng.shuffle(by_b[b])
    # round-robin across buckets
    out = []
    buckets = sorted(by_b.keys())
    idx = {b: 0 for b in buckets}
    while len(out) < n and any(idx[b] < len(by_b[b]) for b in buckets):
        for b in buckets:
            if len(out) >= n:
                break
            i = idx[b]
            if i < len(by_b[b]):
                out.append(by_b[b][i])
                idx[b] = i + 1
    return out


def classify_row(row, audit_by_key1):
    """Mechanical class — never invents RU quality labels."""
    reason = (row.get('reason') or '').strip()
    key1 = row.get('key1') or ''
    deltas = audit_by_key1.get(key1) or []
    max_new = max((d.get('new_sense_count') or 0) for d in deltas) if deltas else None
    max_old = max((d.get('old_sense_count') or 0) for d in deltas) if deltas else None
    changed = any(d.get('changed') for d in deltas) if deltas else None

    if 'sense-count changed' in reason or 'splitter' in reason:
        bucket = 'segmentation_flag'
    elif reason:
        bucket = 'other_reason'
    else:
        bucket = 'missing_reason'

    return {
        'key1': key1,
        'subcard': row.get('subcard'),
        'h': row.get('h'),
        'sense_tag': row.get('sense_tag'),
        'reason': reason,
        'class': bucket,
        'audit_key1_changed': changed,
        'audit_max_old_senses': max_old,
        'audit_max_new_senses': max_new,
        # Explicit: sample does NOT assert the RU text is bad
        'ru_quality_verdict': 'unknown_not_measured',
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--quarantine', default=DEFAULT_QUAR)
    ap.add_argument('--audit', default=DEFAULT_AUDIT)
    ap.add_argument('--n', type=int, default=200)
    ap.add_argument('--seed', type=int, default=20260801)
    ap.add_argument('--out-json', default='')
    ap.add_argument('--out-md', default='')
    args = ap.parse_args()

    rows = load_jsonl(args.quarantine)
    audit_by_key1 = collections.defaultdict(list)
    if os.path.isfile(args.audit):
        with open(args.audit, encoding='utf-8') as f:
            audit = json.load(f)
        for d in audit.get('per_record_deltas') or []:
            if d.get('key1'):
                audit_by_key1[d['key1']].append(d)

    n = min(args.n, len(rows))
    sample = sample_stratified(rows, n, args.seed)
    classified = [classify_row(r, audit_by_key1) for r in sample]
    class_counts = collections.Counter(c['class'] for c in classified)
    unique_keys = len({c['key1'] for c in classified})
    with_audit = sum(1 for c in classified if c['audit_key1_changed'] is not None)

    today = datetime.date.today().isoformat()
    payload = {
        'schema': 'pwg_ru_glyph_quarantine_sample/0.1',
        'date': today,
        'seed': args.seed,
        'n_requested': args.n,
        'n_sampled': len(classified),
        'population': len(rows),
        'unique_key1_in_sample': unique_keys,
        'class_counts': dict(class_counts),
        'with_audit_join': with_audit,
        'ruling': (
            'Sample-first before mass re-translate (MG 29-07-2026 weekly @DECIDE). '
            'Quarantine is a segmentation/sense-count flag, not a gold RU defect label.'
        ),
        'sample': classified,
    }

    out_json = args.out_json or os.path.join(
        RT, 'reports', 'pwg_ru_glyph_quarantine_sample_%s.json' % today)
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write('\n')

    out_md = args.out_md or os.path.join(
        RT, 'pwg_ru', 'H_GLYPH_QUARANTINE_SAMPLE_REPORT_%s.md' % today.replace('-', ''))
    lines = [
        '# Glyph quarantine sample — %d of %d (report only)' % (len(classified), len(rows)),
        '',
        '_Created: %s · Last updated: %s_' % (
            datetime.date.today().strftime('%d-%m-%Y'),
            datetime.date.today().strftime('%d-%m-%Y')),
        '',
        '**Model:** Grok 4.5 (`grok-4.5`) · offline Sonnet-tier batch · **no re-translate**',
        '',
        '## Ruling',
        '',
        payload['ruling'],
        '',
        '## Method',
        '',
        '- Population: [`reports/pwg_ru_glyph_quarantine.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/pwg_ru_glyph_quarantine.jsonl) (%d rows).' % len(rows),
        '- Sample size: **%d** (seed=%d), stratified by SHA-256(`key1`) mod 10 round-robin.' % (len(classified), args.seed),
        '- Join: optional [`pwg_sense_glyph_audit.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/pwg_sense_glyph_audit.json) per-key1 sense-count deltas.',
        '- Script: [`src/sample_glyph_quarantine.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/sample_glyph_quarantine.py).',
        '',
        '## Results',
        '',
        '| Metric | Value |',
        '|---|---:|',
        '| Population | %d |' % len(rows),
        '| Sampled | %d |' % len(classified),
        '| Unique key1 in sample | %d |' % unique_keys,
        '| Rows with audit join | %d |' % with_audit,
        '',
        '### Class counts (mechanical)',
        '',
        '| Class | n | Meaning |',
        '|---|---:|---|',
    ]
    meanings = {
        'segmentation_flag': 'Sense-count changed under corrected 〉 splitter — not a RU-text gold fail',
        'other_reason': 'Non-default quarantine reason string',
        'missing_reason': 'Empty reason field',
    }
    for cls, cnt in sorted(class_counts.items(), key=lambda x: (-x[1], x[0])):
        lines.append('| `%s` | %d | %s |' % (cls, cnt, meanings.get(cls, '')))
    lines.extend([
        '',
        '## Interpretation',
        '',
        '1. **Do not treat the 93%% population flag as "93%% bad Russian."** Every sampled '
        'row that carries the default reason is a *segmentation* quarantine candidate; '
        '`ru_quality_verdict` is deliberately `unknown_not_measured`.',
        '2. **Mass re-translate is not authorised** by this sample alone. Next step if '
        'RU quality is in doubt: a human/paid read of a smaller nested sample of the '
        'segmentation_flag class (e.g. 30 cards), not a full paid re-run of 10k rows.',
        '3. Machine-readable sample: `%s`.' % os.path.relpath(out_json, RT).replace('\\', '/'),
        '',
        '_Dr. Mārcis Gasūns_',
        '',
    ])
    os.makedirs(os.path.dirname(out_md), exist_ok=True)
    with open(out_md, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))

    print('sampled %d / %d -> %s' % (len(classified), len(rows), out_json))
    print('report  -> %s' % out_md)
    for cls, cnt in sorted(class_counts.items()):
        print('  %s: %d' % (cls, cnt))
    return 0


if __name__ == '__main__':
    sys.exit(main() or 0)
