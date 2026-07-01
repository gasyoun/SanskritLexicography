#!/usr/bin/env python
r"""Promote translated workflow cards into the canonical translated store (the print bridge).

The keystone convergence step. Until now the translated wf_output.*.json cards were STRANDED:
export_interop.py builds the citable TEI/OntoLex edition from src/assembled_cards.jsonl and the
translated store src/pwg_ru_translated.jsonl, but NOTHING wrote the harness translations into that
store. This script does: it ingests every wf_output*.json, extracts each non-null card's senses,
stamps per-card provenance, and writes one store row per sense keyed by the HEADWORD key1 (the
join key export_interop uses — wf cards key on the sub-card key `root~~h0_..`, but meta.root is the
plain SLP1 headword that matches assembled_cards.jsonl).

Rows are written with review_status='ai_translated' — NOT 'approved'. export_interop's
approved_store() gate only exports {approved, human_reviewed}, so promoted translations reach the
store (and unblock G5 review counting) WITHOUT silently publishing unreviewed AI as a citable
edition. G5 human review flips a row to 'approved', and only then does it export.

Supersede mode (default): the new store replaces the old run_batch store (which is entirely
'legacy_needs_review' and therefore exported zero rows anyway). The prior file is backed up to
<store>.legacy.bak unless --no-backup.

  python src/promote_final_cards.py                 # promote -> src/pwg_ru_translated.jsonl
  python src/promote_final_cards.py --dry-run        # report coverage, write nothing
  python src/promote_final_cards.py --glob 'wf_output.sd.*.json'   # a subset

Coverage is reported honestly: per-root card counts plus a WARNING for roots whose per-root file
is a requeue subset (the full Slice-C originals were overwritten; re-run or recover them, then
re-run this script — it is idempotent and supersede-safe).
"""
import argparse
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # the RussianTranslation repo root
DEFAULT_STORE = os.path.join(HERE, 'pwg_ru_translated.jsonl')
DEFAULT_GLOB = 'wf_output*.json'
MODEL = 'sonnet'                                    # the harness pins model:'sonnet' (gen_opt_harness2)


def load_wf(path):
    with open(path, encoding='utf-8') as f:
        wrapper = json.load(f)
    result = wrapper.get('result')
    if isinstance(result, str):
        result = json.loads(result)
    if result is None:
        result = wrapper
    return result


def collect_cards(paths):
    """sub-card key -> {card, meta, wf_file}. Non-null wins; both-non-null keeps first + logs."""
    best, conflicts, null_keys = {}, [], set()
    for path in paths:
        try:
            res = load_wf(path)
        except (OSError, json.JSONDecodeError) as e:
            print('  skip (unreadable): %s (%s)' % (os.path.basename(path), e))
            continue
        meta = res.get('meta') or {}
        for r in res.get('results') or []:
            key = r.get('key')
            card = r.get('card')
            if not key:
                continue
            if not card:
                null_keys.add(key)
                continue
            if key in best:
                conflicts.append(key)
                continue                            # keep first-seen non-null
            best[key] = {'card': card, 'meta': meta, 'wf_file': os.path.basename(path)}
    null_keys -= set(best)                          # a key non-null somewhere isn't a null
    return best, conflicts, sorted(null_keys)


def provenance(entry, subkey):
    meta = entry['meta']
    hashes = (meta.get('input_hashes') or {}).get(subkey) or {}
    return {
        'model': MODEL,
        'generator': meta.get('generator'),
        'schema_version': meta.get('schema_version'),
        'root': meta.get('root'),
        'safe_root': meta.get('safe_root'),
        'rootmap_sha256': meta.get('rootmap_sha256'),
        'input_raw_sha256': hashes.get('raw_sha256'),
        'input_portrait_sha256': hashes.get('portrait_sha256'),
        'generated_at': meta.get('generated_at'),
        'wf_file': entry['wf_file'],
        'promoted_by': 'promote_final_cards.py',
    }


def rows_for(subkey, entry, review_status):
    card = entry['card']
    key1 = entry['meta'].get('root')               # the join key into assembled_cards.jsonl
    prov = provenance(entry, subkey)
    for rec in card.get('records') or []:
        for sense in rec.get('senses') or []:
            ru = sense.get('russian')
            if not ru:
                continue
            yield {
                'key1': key1,
                'subcard': subkey,
                'iast': card.get('iast'),
                'h': rec.get('h'),
                'sense_tag': sense.get('tag'),
                'ru': ru,
                'de': sense.get('german'),
                'equivalence_type': sense.get('equivalence_type'),
                'source_type': sense.get('source_type'),
                'stratum': sense.get('stratum'),
                'differentia': sense.get('differentia'),
                'review_status': review_status,
                'reviewer': None,
                'provenance': prov,
            }


def selftest():
    import tempfile
    meta = {'root': 'pA', 'safe_root': 'p_a', 'generator': 'gen_opt_harness2.batched-masked',
            'schema_version': 'v1', 'rootmap_sha256': 'abc', 'generated_at': '2026-06-29T00:00:00Z',
            'input_hashes': {'p_a~~h5_00_pwg00': {'raw_sha256': 'r1', 'portrait_sha256': 'p1'}}}
    entry = {'card': {'key1': 'p_a~~h5_00_pwg00', 'iast': 'pā', 'records': [
        {'h': 'pā', 'senses': [
            {'tag': '1', 'russian': 'пить', 'german': 'trinken', 'equivalence_type': 'equivalent',
             'source_type': 'attested', 'stratum': 'Vedic', 'differentia': ''},
            {'tag': '2', 'russian': '', 'german': 'x'},          # no russian -> skipped
        ]}]}, 'meta': meta, 'wf_file': 'wf_output.sc.pA.json'}
    rows = list(rows_for('p_a~~h5_00_pwg00', entry, 'ai_translated'))
    assert len(rows) == 1, 'a sense without russian must be skipped'
    r = rows[0]
    assert r['key1'] == 'pA', 'key1 must be the HEADWORD meta.root, not the sub-card key'
    assert r['subcard'] == 'p_a~~h5_00_pwg00' and r['ru'] == 'пить' and r['de'] == 'trinken'
    assert r['review_status'] == 'ai_translated', 'must not auto-approve (G5 gate)'
    p = r['provenance']
    assert p['model'] == 'sonnet' and p['rootmap_sha256'] == 'abc'
    assert p['input_raw_sha256'] == 'r1' and p['generated_at'], 'provenance must be complete'
    # collect_cards: a non-null card wins over a null for the same sub-card key.
    d = tempfile.mkdtemp()
    nullf = os.path.join(d, 'wf_output.sc.x.json')
    fullf = os.path.join(d, 'wf_output.x.json')
    with open(nullf, 'w', encoding='utf-8') as f:
        json.dump({'meta': meta, 'results': [{'key': 'p_a~~h5_00_pwg00', 'card': None}]}, f)
    with open(fullf, 'w', encoding='utf-8') as f:
        json.dump({'meta': meta, 'results': [{'key': 'p_a~~h5_00_pwg00', 'card': entry['card']}]}, f)
    best, _conf, nulls = collect_cards([nullf, fullf])
    assert 'p_a~~h5_00_pwg00' in best, 'non-null must win over null for the same key'
    assert nulls == [], 'a key non-null in any file is not a null'
    print('promote_final_cards selftest OK')


def main():
    if '--selftest' in sys.argv[1:]:
        return selftest()
    ap = argparse.ArgumentParser()
    ap.add_argument('--glob', default=DEFAULT_GLOB, help='wf_output glob, relative to repo root')
    ap.add_argument('--store', default=DEFAULT_STORE)
    ap.add_argument('--review-status', default='ai_translated')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--no-backup', action='store_true')
    ap.add_argument('--merge', action='store_true',
                    help='MERGE into the existing store by headword (key1): replace only the '
                         'roots present in THIS run, keep every other root. Use for a per-root '
                         'catch-up — the default full overwrite WIPES any root whose wf_output '
                         'file is no longer on disk (the gam-RU loss mode).')
    args = ap.parse_args()

    paths = sorted(glob.glob(os.path.join(ROOT, args.glob)))
    if not paths:
        sys.exit('no wf_output files matched %s under %s' % (args.glob, ROOT))
    print('ingesting %d wf_output file(s)' % len(paths))
    best, conflicts, null_keys = collect_cards(paths)

    rows, per_root = [], {}
    for subkey, entry in sorted(best.items()):
        n = 0
        for row in rows_for(subkey, entry, args.review_status):
            rows.append(row)
            n += 1
        root = entry['meta'].get('root')
        per_root.setdefault(root, {'cards': 0, 'rows': 0})
        per_root[root]['cards'] += 1
        per_root[root]['rows'] += n

    # Coverage report — honest about partial (requeue-subset) roots.
    print('\n=== PROMOTION COVERAGE ===')
    print('non-null cards promoted : %d' % len(best))
    print('sense rows              : %d' % len(rows))
    print('distinct headwords      : %d' % len(per_root))
    print('null sub-cards skipped  : %d' % len(null_keys))
    if conflicts:
        print('duplicate non-null keys : %d (kept first-seen)' % len(conflicts))
    thin = sorted(r for r, v in per_root.items() if v['cards'] <= 5)
    if thin:
        print('\n⚠ roots with <=5 promoted cards (likely a requeue-subset / partial file — the full')
        print('  output was overwritten; re-run that root and re-run this script to complete it):')
        print('  ' + ', '.join('%s(%d)' % (r, per_root[r]['cards']) for r in thin))

    # --merge: keep every root NOT in this run; replace only the promoted roots. Guards
    # against the full-overwrite wipe when only a subset of wf_output files is on disk.
    kept = 0
    if args.merge and os.path.exists(args.store):
        promoted_roots = {r['key1'] for r in rows}
        keep_rows = []
        with open(args.store, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                e = json.loads(line)
                if e.get('key1') not in promoted_roots:
                    keep_rows.append(e)
        kept = len(keep_rows)
        print('\nMERGE: replacing %d root(s) %s; keeping %d row(s) from other roots'
              % (len(promoted_roots), sorted(promoted_roots), kept))
        rows = keep_rows + rows

    if args.dry_run:
        print('\n(dry run — no store written)')
        return

    if os.path.exists(args.store) and not args.no_backup:
        bak = args.store + ('.premerge.bak' if args.merge else '.legacy.bak')
        os.replace(args.store, bak)
        print('\nbacked up prior store -> %s' % os.path.basename(bak))
    with open(args.store, 'w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    print('wrote canonical translated store -> %s (%d rows, review_status=%s)'
          % (args.store, len(rows), args.review_status))
    print('NOTE: rows are %s, NOT approved — export_interop keeps them out of the citable'
          % args.review_status)
    print('      edition until G5 human review flips review_status to approved.')


if __name__ == '__main__':
    main()
