#!/usr/bin/env python
r"""refresh_tm_mirror.py — H3627: bring the pwg-ru-data TM mirror back in step with the src store.

The mirror `pwg-ru-data/tm/pwg_ru_translated.jsonl` is a straight copy of the canonical
`RussianTranslation/src/pwg_ru_translated.jsonl` — that is the contract
`restore_store_rows_from_mirror.py` ends on (`shutil.copy2(src, mirror)`). Any store write
that removes rows — H2996's 159-row wrong-entry quarantine, the in-place
`durg_a~~h0_zz_sch` key1 repair — leaves the mirror holding rows the store no longer
serves. A re-ingest window run with `--tm=auto` would then re-serve exactly the cards just
quarantined; that is the trap defect requeues avoid by always passing `--no-tm`.

Refreshing is a copy, so the only real risk is copying AWAY a row that exists only in the
mirror and is genuinely wanted. Three guards run before the copy, and any one of them stops
it (`--force` overrides, deliberately loudly):

  G1 human-touched — a mirror-only row with `reviewer` set, or a `review_status` outside
     the machine set, is a human verdict the copy would destroy.
  G2 content-loss  — a mirror-only row whose `ru` text appears nowhere in the store is
     content the copy would destroy. Id churn (a re-parse that moved `sense_tag` or edited
     `de`, both of which feed the row id) is not loss: the same `ru` is still in the store.
  G3 shrink        — a store smaller than the mirror by more than `--max-drop` rows is a
     truncated store, not a repair.

A mirror-only row can also be *superseded* — the store carries a newer translation of the
same sense whose `ru` is not byte-identical, so G2 cannot see the survivor. That is a
judgment call, so it is not inferred: `--ack-superseded FILE` names the exact rows a
session has read and adjudicated, and G2 keeps blocking on everything else. Prefer it over
`--force`, which waives the guard wholesale and leaves nothing to audit.

  python src/refresh_tm_mirror.py [--src PATH] [--mirror PATH] [--apply] [--force]
                                  [--ack-superseded FILE] [--max-drop N] --handoff H####

Dry-run by default: prints the classification and the guard verdicts, writes nothing.
`--selftest` runs the guards over synthetic fixtures.
"""
import argparse
import collections
import hashlib
import io
import json
import os
import shutil
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from store_path import canonical_data_repo, canonical_store  # noqa: E402
# H3658: mirror + ledger resolve off the MAIN checkout, never the executing worktree.
DATA = canonical_data_repo(HERE)
# H3658: the ONE canonical store (H255 loss mode) - not this checkout's possibly-stale copy.
DEFAULT_SRC = canonical_store(os.path.join(HERE, 'pwg_ru_translated.jsonl'))
DEFAULT_MIRROR = os.path.join(DATA, 'tm', 'pwg_ru_translated.jsonl')
DEFAULT_LEDGER = os.path.join(DATA, 'tm', 'mirror_refresh_ledger.jsonl')

# review_status values that mean "no human has ruled on this row"
MACHINE_STATUS = frozenset(['ai_translated', 'auto_promoted', 'pending', 'draft', None, ''])


def rid(row):
    """Row identity, byte-identical to audit_store_gates.row_id and
    restore_store_rows_from_mirror.rid — the three must agree or the diffs disagree."""
    return (row.get('key1') or '', row.get('subcard') or '',
            row.get('sense_tag') or '', (row.get('de') or '')[:80])


def load(path):
    with io.open(path, encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def norm_ru(text):
    return ' '.join((text or '').split())


def classify(src_rows, mirror_rows, quarantine_ids=frozenset(), superseded_ids=frozenset()):
    """Split the mirror-only rows into quarantined / id-churn / superseded / unexplained."""
    src_ids = set(rid(r) for r in src_rows)
    src_ru = collections.Counter(norm_ru(r.get('ru')) for r in src_rows)
    src_ru.pop('', None)
    only_mirror = [r for r in mirror_rows if rid(r) not in src_ids]
    mirror_ids = set(rid(r) for r in mirror_rows)
    only_src = [r for r in src_rows if rid(r) not in mirror_ids]

    buckets = {'quarantined': [], 'id_churn': [], 'superseded': [], 'unexplained': []}
    for row in only_mirror:
        if rid(row) in quarantine_ids:
            buckets['quarantined'].append(row)
        elif src_ru.get(norm_ru(row.get('ru')), 0):
            buckets['id_churn'].append(row)
        elif rid(row) in superseded_ids:
            buckets['superseded'].append(row)
        else:
            buckets['unexplained'].append(row)
    return {'only_mirror': only_mirror, 'only_src': only_src, 'buckets': buckets}


def run_guards(src_rows, mirror_rows, report, max_drop):
    """Return a list of (name, ok, detail). ok=False blocks the copy."""
    guards = []

    human = [r for r in report['only_mirror']
             if r.get('reviewer') or r.get('review_status') not in MACHINE_STATUS]
    guards.append(('G1 human-touched', not human,
                   '%d mirror-only row(s) carry a human verdict' % len(human) if human
                   else 'no mirror-only row carries a reviewer or a non-machine review_status'))

    lost = report['buckets']['unexplained']
    acked = len(report['buckets']['superseded'])
    guards.append(('G2 content-loss', not lost,
                   '%d mirror-only row(s) have `ru` text found nowhere in the store' % len(lost)
                   if lost else
                   'every mirror-only row is quarantined, id-churn, or acknowledged '
                   'superseded (%d acked)' % acked))

    drop = len(mirror_rows) - len(src_rows)
    guards.append(('G3 shrink', drop <= max_drop,
                   'store is %d rows smaller than the mirror (cap %d)' % (drop, max_drop)))
    return guards


def _verdicts(src_rows, mirror_rows, report, max_drop):
    return dict((g[0], g[1]) for g in run_guards(src_rows, mirror_rows, report, max_drop))


def selftest():
    def row(key1, sub, tag, de, ru, **kw):
        r = {'key1': key1, 'subcard': sub, 'sense_tag': tag, 'de': de, 'ru': ru,
             'review_status': 'ai_translated', 'reviewer': None}
        r.update(kw)
        return r

    state = {'ok': 0, 'total': 0}

    def check(name, cond):
        state['total'] += 1
        if cond:
            state['ok'] += 1
        print('  %-46s %s' % (name, 'ok' if cond else 'FAIL'))

    # 1. clean no-op: identical stores, all guards green
    a = [row('k', 's', '1', 'de1', 'ru1')]
    rep = classify(a, list(a))
    check('identical stores -> no only_mirror', not rep['only_mirror'])
    check('identical stores -> all guards pass',
          all(g[1] for g in run_guards(a, list(a), rep, 5)))

    # 2. a quarantined row is explained by the quarantine file
    src = [row('k', 's', '1', 'de1', 'ru1')]
    mir = src + [row('bad', 's2', '1', 'de2', 'ru2')]
    rep = classify(src, mir, set([rid(mir[1])]))
    check('quarantined row -> bucket quarantined', len(rep['buckets']['quarantined']) == 1)
    check('quarantined row -> guards pass', all(g[1] for g in run_guards(src, mir, rep, 5)))

    # 3. id churn: sense_tag moved and `de` was re-parsed, same `ru` still in the store
    src = [row('k', 's', 'header', 'de-NEW', 'same russian text')]
    mir = [row('k', 's', '1', 'de-OLD', 'same  russian   text')]
    rep = classify(src, mir)
    check('id churn -> bucket id_churn', len(rep['buckets']['id_churn']) == 1)
    check('id churn -> G2 passes', _verdicts(src, mir, rep, 5)['G2 content-loss'])

    # 4. real content loss blocks
    src = [row('k', 's', '1', 'de1', 'ru1')]
    mir = src + [row('k2', 's2', '1', 'de2', 'ONLY IN MIRROR')]
    rep = classify(src, mir)
    check('unexplained row -> bucket unexplained', len(rep['buckets']['unexplained']) == 1)
    check('unexplained row -> G2 blocks', not _verdicts(src, mir, rep, 5)['G2 content-loss'])

    # 5. an empty `ru` must not launder a mirror-only row into id_churn
    src = [row('k', 's', '1', 'de1', '')]
    mir = src + [row('k2', 's2', '1', 'de2', '')]
    rep = classify(src, mir)
    check('empty ru -> not laundered as id_churn', len(rep['buckets']['unexplained']) == 1)

    # 5b. an acknowledged superseded row passes G2; an unacknowledged sibling still blocks
    src = [row('k', 's', '1', 'de1', 'ru1')]
    gone = row('k2', 's2', '1', 'de2', 'OLD PASS, SUPERSEDED')
    other = row('k3', 's3', '1', 'de3', 'GENUINELY LOST')
    mir = src + [gone, other]
    rep = classify(src, mir, frozenset(), set([rid(gone)]))
    check('acked row -> bucket superseded', len(rep['buckets']['superseded']) == 1)
    check('unacked sibling -> still unexplained', len(rep['buckets']['unexplained']) == 1)
    check('unacked sibling -> G2 still blocks', not _verdicts(src, mir, rep, 5)['G2 content-loss'])
    rep = classify(src, mir, frozenset(), set([rid(gone), rid(other)]))
    check('all acked -> G2 passes', _verdicts(src, mir, rep, 5)['G2 content-loss'])

    # 5c. an ack must not override a human verdict — G1 outranks it
    src = [row('k', 's', '1', 'de1', 'ru1')]
    human_row = row('k2', 's2', '1', 'de2', 'txt', reviewer='MG', review_status='human_approved')
    mir = src + [human_row]
    rep = classify(src, mir, frozenset(), set([rid(human_row)]))
    check('acked but human-touched -> G1 still blocks',
          not _verdicts(src, mir, rep, 5)['G1 human-touched'])

    # 6. a human verdict blocks even when the `ru` survives
    src = [row('k', 's', 'header', 'de-NEW', 'txt')]
    mir = [row('k', 's', '1', 'de-OLD', 'txt', reviewer='MG', review_status='human_approved')]
    rep = classify(src, mir)
    check('human-touched mirror-only row -> G1 blocks',
          not _verdicts(src, mir, rep, 5)['G1 human-touched'])

    # 7. an oversized shrink blocks
    src = [row('k', 's', '1', 'de1', 'ru1')]
    mir = [row('k%d' % i, 's', '1', 'de%d' % i, 'ru1') for i in range(20)]
    rep = classify(src, mir)
    check('shrink past --max-drop -> G3 blocks', not _verdicts(src, mir, rep, 5)['G3 shrink'])

    # 8. rid agrees with the audit tool's row_id on a realistic row
    long_de = 'x' * 200
    check('rid truncates de at 80 chars', rid(row('k', 's', '1', long_de, 'r'))[3] == 'x' * 80)

    print('selftest %d/%d' % (state['ok'], state['total']))
    return 0 if state['ok'] == state['total'] else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--src', default=DEFAULT_SRC)
    ap.add_argument('--mirror', default=DEFAULT_MIRROR)
    ap.add_argument('--quarantine', default=os.path.normpath(os.path.join(
        HERE, '..', 'reports', 'pwg_ru_wrong_entry_quarantine.jsonl')),
        help='quarantine jsonl whose rows explain expected mirror-only rows')
    ap.add_argument('--ack-superseded', default=None,
                    help='jsonl of mirror-only rows a session has read and adjudicated as '
                         'superseded by a newer store row; matched on the same row id')
    ap.add_argument('--ledger', default=DEFAULT_LEDGER)
    ap.add_argument('--handoff', default=None,
                    help='handoff ID that owns this refresh; stamped into the mirror backup '
                         'filename and the ledger row. H3658: this defaulted to H3627, so '
                         'every later refresh silently mislabelled its own provenance.')
    ap.add_argument('--max-drop', type=int, default=500)
    ap.add_argument('--apply', action='store_true', help='actually copy src over the mirror')
    ap.add_argument('--force', action='store_true', help='copy even if a guard blocks')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    if not args.handoff:
        # H3658: was `default='H3627'`, so every refresh after that handoff stamped the
        # wrong provenance into the mirror backup filename and the ledger row. Required for
        # a real run; --selftest above needs no provenance and returns before this.
        ap.error('--handoff is required (the H### that owns this refresh)')

    src_rows = load(args.src)
    mirror_rows = load(args.mirror)
    quarantine_ids = set()
    if os.path.exists(args.quarantine):
        quarantine_ids = set(rid(r) for r in load(args.quarantine))
        print('quarantine  %s  rows=%d' % (args.quarantine, len(quarantine_ids)))

    superseded_ids = set()
    if args.ack_superseded:
        superseded_ids = set(rid(r) for r in load(args.ack_superseded))
        print('ack-superseded %s  rows=%d' % (args.ack_superseded, len(superseded_ids)))

    report = classify(src_rows, mirror_rows, quarantine_ids, superseded_ids)
    b = report['buckets']
    print('src     %s  rows=%d' % (args.src, len(src_rows)))
    print('mirror  %s  rows=%d' % (args.mirror, len(mirror_rows)))
    print('only_src=%d only_mirror=%d' % (len(report['only_src']), len(report['only_mirror'])))
    print('  mirror-only quarantined  %d' % len(b['quarantined']))
    print('  mirror-only id-churn     %d' % len(b['id_churn']))
    print('  mirror-only superseded   %d  (acknowledged)' % len(b['superseded']))
    print('  mirror-only unexplained  %d' % len(b['unexplained']))
    for r in b['unexplained'][:20]:
        print('    ! %s | %s | %s | %s' % (r.get('key1'), r.get('subcard'),
                                           r.get('sense_tag'), (r.get('ru') or '')[:60]))

    guards = run_guards(src_rows, mirror_rows, report, args.max_drop)
    print('guards:')
    blocked = False
    for name, good, detail in guards:
        print('  %-18s %-6s %s' % (name, 'PASS' if good else 'BLOCK', detail))
        blocked = blocked or not good

    if blocked and not args.force:
        print('\nBLOCKED — a guard refused. Re-read the rows above; --force overrides.')
        return 1
    if blocked:
        print('\n--force: copying past a blocking guard.')

    if not args.apply:
        print('\nDRY RUN — nothing written. Re-run with --apply to refresh the mirror.')
        return 0

    stamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    before_sha = sha256_file(args.mirror)
    backup = '%s.%s.%s.bak' % (args.mirror, args.handoff.lower(), stamp)
    shutil.copy2(args.mirror, backup)
    shutil.copy2(args.src, args.mirror)
    after_sha = sha256_file(args.mirror)
    entry = {'handoff': args.handoff, 'ts': stamp,
             'action': 'mirror refreshed from src store',
             'src_rows': len(src_rows), 'mirror_rows_before': len(mirror_rows),
             'mirror_rows_after': len(load(args.mirror)),
             'only_mirror_dropped': len(report['only_mirror']),
             'dropped_quarantined': len(b['quarantined']),
             'dropped_id_churn': len(b['id_churn']),
             'dropped_superseded_acked': len(b['superseded']),
             'dropped_unexplained': len(b['unexplained']),
             'ack_superseded_file': (os.path.basename(args.ack_superseded)
                                     if args.ack_superseded else None),
             'only_src_added': len(report['only_src']),
             'forced': bool(args.force),
             'mirror_sha_before': before_sha, 'mirror_sha_after': after_sha,
             'backup': os.path.basename(backup)}
    with io.open(args.ledger, 'a', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    print('\nrefreshed. backup=%s' % os.path.basename(backup))
    print('mirror sha %s -> %s' % (before_sha[:12], after_sha[:12]))
    print('ledger += %s' % args.ledger)
    return 0


if __name__ == '__main__':
    sys.exit(main())
