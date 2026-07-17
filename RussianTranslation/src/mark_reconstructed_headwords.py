r"""Stamp the 468 identity-DERIVED headwords so they stop reading as recovered evidence.

WHY
---
PR #510 repaired the pwg_ru store. Its `{Tn}` half is evidence-based (668/670 restored from
content-addressed sources; 2 unrecoverable rows quarantined). Its `h` half is NOT:
`canonical_record_head()` DERIVES a head from the row's own key (`gam~~h0_45_upa` -> 'upagam',
every `vid~~*` -> 'vid'), because the model-authored `h` was destroyed at the stitch before it
was ever persisted (Uprava FINDINGS §94) and could not be recovered by anything.

The problem is not the derivation -- it is that the derivation is SILENT. Provenance still
reads the original `generator`/`generated_at`, so 468 derived values are indistinguishable
from model-authored ones (the C-05 hazard), and `h is None` fell 468 -> 0, clearing the very
query that could find them (FINDINGS §95).

This stamps them. It changes NO `h` value -- it only records how each one came to exist, so a
consumer can partition them and a later re-translation can target them.

HOW THE 468 ARE IDENTIFIED
--------------------------
By diffing the pre-repair backup PR #510 left on disk (byte-identical, hash-named). Alignment
uses fields the repair never touched (`subcard` + `ru` + `de`): the `{Tn}` repair rewrote
h/iast/sense_tag/differentia, so those cannot key the join, while `ru`/`de` changed on exactly
the 2 rows that were then REMOVED. Two-pointer walk; every assumption is asserted, and the
script REFUSES to write unless the measured diff matches PR #510's own reported numbers.

USAGE
    python src/mark_reconstructed_headwords.py            # dry run (default, read-only)
    python src/mark_reconstructed_headwords.py --apply    # atomic rewrite + backup

Idempotent: re-running reports `already stamped` and rewrites the same markers. It is pinned to
the exact pre-repair backup hash from PR #510's report and REFUSES if reality has moved, so it
cannot be pointed at a different store state by accident.
"""
import sys, os, json, argparse, collections, datetime, hashlib

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

SRC = r'C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation\src'
STORE = os.path.join(SRC, 'pwg_ru_translated.jsonl')
BAK = os.path.join(SRC, 'pwg_ru_translated.jsonl.pre-h1080.cc1d544ed92d201c.20260716T230816Z.bak')

# PR #510's own report. The stamp refuses to run if reality disagrees with it.
EXPECT_BAK_SHA = 'cc1d544ed92d201ca8cbecde0b5e9a8191994dfd1baf20841da82f1f9ae7c805'
EXPECT_BAK_ROWS = 11605
EXPECT_CUR_ROWS = 11603
EXPECT_NULL_H = 468
EXPECT_REMOVED = 2
QUARANTINED = {'ban_d~~h0_11_ni', 'ban_d~~h0_21_upasam_0'}

METHOD = ('canonical_record_head: identity-derived (row.iast if present, else key1 + the '
          'sub-card upasarga suffix); NOT recovered from source evidence')
NOTE = ('The model-authored h was destroyed at the stitch flatten before it was ever '
        'persisted, so no offline source exists (Uprava FINDINGS §94). This value is a '
        'display head derived from the row key by PR #510, not lexicographic evidence: it '
        'cannot express homonym distinctions (vid~~h0_* and vid~~h2_* both derive to "vid"), '
        'and the true h was plausibly a homonym number. Re-translation is required for the '
        'real value. Stamped per FINDINGS §95.')


def rows_of(path):
    out = []
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            if line.strip():
                out.append(json.loads(line))
    return out


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for c in iter(lambda: fh.read(65536), b''):
            h.update(c)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    if not os.path.exists(BAK):
        sys.exit('REFUSED: pre-repair backup absent -- the 468 are no longer identifiable: %s' % BAK)
    actual = sha256_file(BAK)
    if actual != EXPECT_BAK_SHA:
        sys.exit('REFUSED: backup sha %s != PR #510 report %s' % (actual[:16], EXPECT_BAK_SHA[:16]))
    print('pre-repair backup : %s' % os.path.basename(BAK))
    print('  sha256 verified : %s... (matches PR #510 report)' % actual[:24])

    bak, cur = rows_of(BAK), rows_of(STORE)
    print('  backup rows     : %d (expect %d)' % (len(bak), EXPECT_BAK_ROWS))
    print('  current rows    : %d (expect %d)' % (len(cur), EXPECT_CUR_ROWS))
    if len(bak) != EXPECT_BAK_ROWS or len(cur) != EXPECT_CUR_ROWS:
        sys.exit('REFUSED: row counts disagree with PR #510 report -- the store moved again.')

    # Two-pointer align on fields the repair did not rewrite.
    def key(r):
        return (r.get('subcard'), r.get('ru'), r.get('de'))

    pairs, removed = [], []
    i = j = 0
    while i < len(bak) and j < len(cur):
        if key(bak[i]) == key(cur[j]):
            pairs.append((bak[i], cur[j]))
            i += 1
            j += 1
        else:
            removed.append(bak[i])
            i += 1
    while i < len(bak):
        removed.append(bak[i])
        i += 1

    print()
    print('aligned rows      : %d' % len(pairs))
    print('unmatched (removed): %d (expect %d)' % (len(removed), EXPECT_REMOVED))
    if len(removed) != EXPECT_REMOVED:
        sys.exit('REFUSED: expected exactly %d removed rows, found %d -- alignment is unsafe.'
                 % (EXPECT_REMOVED, len(removed)))
    got_q = {r.get('subcard') for r in removed}
    if got_q != QUARANTINED:
        sys.exit('REFUSED: removed rows are not the known C-42 quarantine pair: %s' % sorted(got_q))
    print('  -> the 2 removed rows ARE the C-42 quarantine pair: %s' % sorted(got_q))
    if j != len(cur):
        sys.exit('REFUSED: %d current rows never aligned.' % (len(cur) - j))

    # The 468: h was null BEFORE, non-null NOW.
    targets, iast_syn, gram_syn = [], [], []
    heads = collections.Counter()
    for before, after in pairs:
        if before.get('h') is None:
            if after.get('h') is None:
                sys.exit('REFUSED: a row is still h==null after repair -- store state unexpected.')
            targets.append(after)
            heads[after.get('h')] += 1
            # PR #510 also filled iast and grammar on these rows, equally silently. Same defect
            # class, same fix -- marking h alone would leave 462 derived iast values unmarked.
            if before.get('iast') is None:
                iast_syn.append(after)
            if before.get('grammar') is None:
                gram_syn.append(after)

    print()
    print('rows whose h was NULL before and is DERIVED now : %d (expect %d)' % (len(targets), EXPECT_NULL_H))
    if len(targets) != EXPECT_NULL_H:
        sys.exit('REFUSED: expected %d, found %d.' % (EXPECT_NULL_H, len(targets)))
    print('  of these, iast also synthesised               : %d' % len(iast_syn))
    print('  of these, grammar also defaulted to ""        : %d' % len(gram_syn))
    print('  distinct derived heads                        : %d' % len(heads))
    print('  top derived heads: %s' % ', '.join('%s x%d' % (repr(h), c) for h, c in heads.most_common(6)))

    already = sum(1 for r in targets if (r.get('provenance') or {}).get('h_reconstructed'))
    print('  already stamped                               : %d' % already)

    if not args.apply:
        print()
        print('DRY RUN -- nothing written. Re-run with --apply to stamp.')
        return 0

    for r in targets:
        prov = r.setdefault('provenance', {})
        prov['h_reconstructed'] = True
        prov['h_reconstruction_method'] = METHOD
        prov['h_reconstruction_pr'] = 510
        prov['h_reconstruction_note'] = NOTE
    for r in iast_syn:
        r['provenance']['iast_reconstructed'] = True     # same silent derivation, same pass
    for r in gram_syn:
        r['provenance']['grammar_defaulted_empty'] = True

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = '%s.pre-hstamp.%s.bak' % (STORE, stamp)
    with open(STORE, 'rb') as s, open(backup, 'wb') as d:
        d.write(s.read())
    tmp = STORE + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as fh:
        for r in cur:
            fh.write(json.dumps(r, ensure_ascii=False) + '\n')
    os.replace(tmp, STORE)

    print()
    print('APPLIED: %d row(s) stamped h_reconstructed=true' % len(targets))
    print('backup : %s' % os.path.basename(backup))

    # Prove it, by re-reading from disk.
    fresh = rows_of(STORE)
    n_stamp = sum(1 for r in fresh if (r.get('provenance') or {}).get('h_reconstructed') is True)
    n_null = sum(1 for r in fresh if r.get('h') is None)
    n_iast = sum(1 for r in fresh if (r.get('provenance') or {}).get('iast_reconstructed') is True)
    n_gram = sum(1 for r in fresh if (r.get('provenance') or {}).get('grammar_defaulted_empty') is True)
    print()
    print('VERIFY (re-read from disk):')
    print('  rows                  : %d (must stay %d)' % (len(fresh), EXPECT_CUR_ROWS))
    print('  h_reconstructed rows  : %d (must be %d)' % (n_stamp, EXPECT_NULL_H))
    print('  h == null rows        : %d (must stay 0 -- no h VALUE was changed)' % n_null)
    print('  iast_reconstructed    : %d' % n_iast)
    print('  grammar_defaulted     : %d' % n_gram)
    ok = len(fresh) == EXPECT_CUR_ROWS and n_stamp == EXPECT_NULL_H and n_null == 0
    print('  RESULT                : %s' % ('OK' if ok else 'MISMATCH'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
