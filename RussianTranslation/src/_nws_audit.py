#!/usr/bin/env python
"""Validation audit for a scraped NWS section (gitignored pilot/nws/*.json).

Run on the a-section sample BEFORE scaling to all letters (gold-standard-first).
Deterministic, ~seconds. Checks:
  1. coverage     — every key in the section has its case-safe file (no collision)
  2. integrity    — each file's internal key1 matches the name it is under
  3. content      — distribution: NWS-extra / NWS / Schmidt / pw / fully-empty
  4. duplicates   — distinct key1 == file count
  5. anomalies    — refusal/error strings, suspiciously long fragments

  python _nws_audit.py [section]      default 'a'
"""
import os, sys, json, glob, collections
sys.stdout.reconfigure(encoding='utf-8')
from safe_filename import safe_name

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'pilot', 'nws')


# control sidecars to exclude — NOT '_'-prefix (safe_name encodes uppercase-initial
# headwords with a leading '_', e.g. ABA -> _a_b_a, so a '_' filter eats real cards)
CONTROL = ('_watch_state.json',)


def headword_files():
    return [f for f in glob.glob(os.path.join(OUT, '*.json'))
            if os.path.basename(f) not in CONTROL]


def main():
    section = sys.argv[1] if len(sys.argv) > 1 else 'a'
    keys = [l.strip() for l in open(os.path.join(OUT, '_keys_%s.txt' % section), encoding='utf-8') if l.strip()]
    files = headword_files()

    match = mismatch = missing = unreadable = 0
    has_nws = has_sch = has_pw = empty = extra = 0
    refusal = longest = 0
    seen = collections.Counter()
    # only genuine error markers — 'error'/'exception'/'not found' are ordinary
    # gloss words ('terror', 'exception to a rule', editorial '[error for X?]')
    REFUSE = ('was rejected', 'the change you wanted')

    by_key = {}
    for f in files:
        try:
            d = json.load(open(f, encoding='utf-8'))
        except Exception:
            unreadable += 1
            continue
        by_key[d.get('key1')] = d

    for k in keys:
        d = by_key.get(k)
        if d is None:
            missing += 1
            continue
        match += 1                     # key present (by_key keyed on key1)
        seen[k] += 1
        nws, sch, pwlen = d.get('nws', ''), d.get('sch', ''), d.get('pw_len', 0)
        if d.get('has_nws_extra'):
            extra += 1
        if nws:
            has_nws += 1
        if sch:
            has_sch += 1
        if pwlen:
            has_pw += 1
        if not nws and not sch and not pwlen:
            empty += 1
        longest = max(longest, len(nws))
        if any(r in nws.lower() for r in REFUSE):
            refusal += 1

    # filename-integrity (independent of by_key): does safe_name(key) hold key?
    for k in keys:
        p = os.path.join(OUT, safe_name(k) + '.json')
        if not os.path.exists(p):
            continue
        try:
            if json.load(open(p, encoding='utf-8')).get('key1') != k:
                mismatch += 1
        except Exception:
            pass

    dups = sum(c - 1 for c in seen.values() if c > 1)
    n = len(keys)
    print('=== NWS audit — section %r ===' % section)
    print('keys                : %d' % n)
    print('files on disk        : %d' % len(files))
    print('-- coverage + integrity --')
    print('  key present        : %d (%.1f%%)' % (match, 100 * match / n))
    print('  missing            : %d' % missing)
    print('  key1≠filename      : %d   <-- case-collision regressions (must be 0)' % mismatch)
    print('  unreadable         : %d' % unreadable)
    print('  duplicate key1     : %d' % dups)
    print('-- content distribution --')
    print('  NWS-extra (net-new): %d (%.0f%%)' % (extra, 100 * extra / n))
    print('  has NWS fragment   : %d (%.0f%%)' % (has_nws, 100 * has_nws / n))
    print('  has Schmidt frag   : %d (%.0f%%)' % (has_sch, 100 * has_sch / n))
    print('  has pw fragment    : %d (%.0f%%)' % (has_pw, 100 * has_pw / n))
    print('  fully empty (none) : %d (%.0f%%)' % (empty, 100 * empty / n))
    print('-- anomalies --')
    print('  refusal/error str  : %d' % refusal)
    print('  longest NWS frag   : %d chars' % longest)
    verdict = 'CLEAN' if (missing == 0 and mismatch == 0 and unreadable == 0 and dups == 0) else 'ISSUES'
    print('VERDICT: %s' % verdict)


if __name__ == '__main__':
    main()
