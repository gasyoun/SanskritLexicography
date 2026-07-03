#!/usr/bin/env python
"""Audit and conservatively mark PWG-RU translation provenance.

The translated store is one JSON object per sense.  Exact model IDs belong in
`provenance.model_version`; ambiguous legacy aliases stay unresolved and get an
explicit note so later tools do not confuse a guess with a version.
"""
import argparse
import collections
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_STORE = os.path.join(HERE, 'pwg_ru_translated.jsonl')
UNRESOLVED_FIELD = 'model_version_unresolved'
UNRESOLVED_NOTE_FIELD = 'model_version_note'


def iter_rows(path):
    with open(path, encoding='utf-8') as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            yield lineno, json.loads(line)


def unresolved_note(prov):
    alias = prov.get('model') or 'unknown'
    date = prov.get('generated_at') or 'unknown-date'
    wf_file = prov.get('wf_file') or 'unknown-wf'
    return "version unresolved - alias %r at %s (wf_file=%s)" % (alias, date, wf_file)


def audit(path):
    stats = collections.Counter()
    by_model = collections.Counter()
    by_wf = collections.Counter()
    missing_examples = []
    unresolved_examples = []
    rows = []
    for lineno, row in iter_rows(path):
        stats['rows'] += 1
        prov = row.get('provenance') or {}
        en_prov = row.get('en_provenance') or {}
        model_key = (prov.get('model'), prov.get('model_version'))
        by_model[model_key] += 1
        if en_prov:
            stats['en_provenance_rows'] += 1
            if en_prov.get('model_version'):
                stats['en_versioned_rows'] += 1
        if prov.get('model_version'):
            stats['ru_versioned_rows'] += 1
        else:
            stats['ru_missing_model_version'] += 1
            if len(missing_examples) < 5:
                missing_examples.append((lineno, row.get('key1'), row.get('subcard'),
                                         prov.get('model'), prov.get('generated_at'),
                                         prov.get('wf_file')))
        if prov.get(UNRESOLVED_FIELD):
            stats['ru_unresolved_marked_rows'] += 1
            if len(unresolved_examples) < 5:
                unresolved_examples.append((lineno, row.get('key1'), row.get('subcard'),
                                            prov.get(UNRESOLVED_NOTE_FIELD)))
        if not prov.get('input_raw_sha256'):
            stats['missing_input_raw_sha256'] += 1
        if not prov.get('input_portrait_sha256'):
            stats['missing_input_portrait_sha256'] += 1
        if prov.get('partial_card'):
            stats['partial_card_rows'] += 1
        by_wf[(prov.get('wf_file'), prov.get('generated_at'), prov.get('model'),
               prov.get('model_version'))] += 1
        rows.append(row)
    return {
        'stats': stats,
        'by_model': by_model,
        'by_wf': by_wf,
        'missing_examples': missing_examples,
        'unresolved_examples': unresolved_examples,
        'rows': rows,
    }


def mark_unresolved(rows):
    changed = 0
    for row in rows:
        prov = row.get('provenance')
        if not isinstance(prov, dict):
            continue
        if prov.get('model_version'):
            continue
        if prov.get(UNRESOLVED_FIELD) and prov.get(UNRESOLVED_NOTE_FIELD):
            continue
        prov[UNRESOLVED_FIELD] = True
        prov[UNRESOLVED_NOTE_FIELD] = unresolved_note(prov)
        changed += 1
    return changed


def write_rows(path, rows):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    os.replace(tmp, path)


def print_report(result):
    stats = result['stats']
    print('=== TRANSLATION PROVENANCE AUDIT ===')
    print('store rows                         : %d' % stats['rows'])
    print('RU rows with exact model_version   : %d' % stats['ru_versioned_rows'])
    print('RU rows missing model_version      : %d' % stats['ru_missing_model_version'])
    print('RU unresolved rows already marked  : %d' % stats['ru_unresolved_marked_rows'])
    print('rows missing input_raw_sha256      : %d' % stats['missing_input_raw_sha256'])
    print('rows missing input_portrait_sha256 : %d' % stats['missing_input_portrait_sha256'])
    print('partial-card rows                  : %d' % stats['partial_card_rows'])
    print('EN provenance rows                 : %d' % stats['en_provenance_rows'])
    print('EN rows with exact model_version   : %d' % stats['en_versioned_rows'])
    print()
    print('Top RU model/version groups:')
    for (model, version), n in result['by_model'].most_common(12):
        print('  %6d  model=%r model_version=%r' % (n, model, version))
    print()
    print('Top workflow/date/model groups:')
    for (wf_file, generated_at, model, version), n in result['by_wf'].most_common(12):
        print('  %6d  %s  %s  model=%r version=%r' %
              (n, generated_at or 'unknown-date', wf_file or 'unknown-wf', model, version))
    if result['missing_examples']:
        print()
        print('First missing-version examples:')
        for ex in result['missing_examples']:
            print('  line=%s key1=%s subcard=%s model=%s generated_at=%s wf_file=%s' % ex)
    if result['unresolved_examples']:
        print()
        print('First unresolved-note examples:')
        for ex in result['unresolved_examples']:
            print('  line=%s key1=%s subcard=%s note=%s' % ex)


def selftest():
    import tempfile
    d = tempfile.mkdtemp()
    path = os.path.join(d, 'store.jsonl')
    rows = [
        {'key1': 'a', 'subcard': 'a~~1', 'ru': 'x', 'de': 'y',
         'provenance': {'model': 'sonnet', 'input_raw_sha256': 'raw',
                        'input_portrait_sha256': 'portrait', 'generated_at': '2026-06-29T00:00:00Z',
                        'wf_file': 'wf_output.sc.a.json'}},
        {'key1': 'b', 'subcard': 'b~~1', 'ru': 'x', 'de': 'y',
         'provenance': {'model': 'sonnet', 'model_version': 'claude-sonnet-5',
                        'input_raw_sha256': 'raw2', 'input_portrait_sha256': 'portrait2'}},
    ]
    write_rows(path, rows)
    result = audit(path)
    assert result['stats']['rows'] == 2
    assert result['stats']['ru_missing_model_version'] == 1
    changed = mark_unresolved(result['rows'])
    assert changed == 1
    write_rows(path, result['rows'])
    reread = audit(path)
    assert reread['stats']['ru_versioned_rows'] == 1
    assert reread['stats']['ru_missing_model_version'] == 1
    assert reread['stats']['ru_unresolved_marked_rows'] == 1
    first = reread['rows'][0]['provenance']
    assert first[UNRESOLVED_FIELD] is True
    assert 'claude-sonnet' not in first.get(UNRESOLVED_NOTE_FIELD, '')
    assert 'model_version' not in first
    print('audit_translation_provenance selftest OK')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--store', default=DEFAULT_STORE)
    ap.add_argument('--write', action='store_true',
                    help='mark legacy rows whose model alias cannot be resolved; no guessing')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not os.path.exists(args.store):
        sys.exit('no store %r' % args.store)
    result = audit(args.store)
    print_report(result)
    if args.write:
        changed = mark_unresolved(result['rows'])
        write_rows(args.store, result['rows'])
        print()
        print('wrote %s; marked %d legacy row(s) unresolved' % (args.store, changed))
    else:
        print()
        print('(report only; pass --write to mark unresolved legacy rows)')


if __name__ == '__main__':
    main()
