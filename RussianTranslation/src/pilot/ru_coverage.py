#!/usr/bin/env python
r"""RU coverage gate — flag any root whose RU translation is silently partial. No LLM.

The RU catch-up gap (gam sat at 6/127 sub-cards for weeks, invisible) happened because
nothing checked RU completeness per root against the intended card set. This does.

For each root it compares the RU store (src/pwg_ru_translated.jsonl, keyed by sub-card) to
the intended sub-card set = the EN store's meta.selected_keys (the rootmap card list; the EN
run enumerates every sub-card, so it is the authoritative per-root denominator). Prints a
per-root RU% and exits non-zero if any root is below --min (default 90), so it can gate CI /
a pre-promote check.

  python src/pilot/ru_coverage.py               # report; exit 1 if any root < 90% RU
  python src/pilot/ru_coverage.py --min 100     # require full RU coverage
  python src/pilot/ru_coverage.py --keys gam    # list gam's missing RU sub-cards (for a catch-up)
"""
import argparse
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)

if SRC not in sys.path:
    sys.path.insert(0, SRC)

from store_path import canonical_store  # noqa: E402

# B09 (H1339): resolve the ONE canonical store, exactly like promote_final_cards /
# translation_memory — a fresh-worktree run (the sanctioned branch-contention pattern)
# used to read the worktree-LOCAL path, so this anti-silent-partial gate silently
# measured an EMPTY store and its verdicts were fiction.
RU_STORE = canonical_store(os.path.join(SRC, 'pwg_ru_translated.jsonl'))
# The EN denominator artifacts live beside the store's checkout, not this one's — derive
# the repo root from the RESOLVED store so numerator and denominator come from the same
# checkout (under a PWG_RU_STORE test override this points at the override's tree, which
# is exactly what a hermetic test wants).
REPO = os.path.dirname(os.path.dirname(os.path.abspath(RU_STORE)))


def ru_by_root():
    roots = {}
    if not os.path.exists(RU_STORE):
        return roots
    with open(RU_STORE, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            root = (r.get('key1') or r.get('subcard') or '').split('~~')[0]
            roots.setdefault(root, set()).add(r.get('subcard'))
    return roots


def intended_by_root():
    """root -> set(sub-card keys) from each EN store's meta.selected_keys (the rootmap set).

    Returns (intended, corrupt): `corrupt` is [(root, error)] for EN files that exist but do
    not parse. A corrupt denominator MUST NOT silently drop the root (that is the exact blind
    spot that hid gam 6/127) — the caller surfaces it loudly and fails."""
    out = {}
    corrupt = []
    for fp in glob.glob(os.path.join(REPO, 'wf_output.en.*.json')):
        root = os.path.basename(fp).replace('wf_output.en.', '').replace('.json', '')
        try:
            d = json.load(open(fp, encoding='utf-8'))
        except (OSError, json.JSONDecodeError) as e:
            corrupt.append((root, str(e)))
            continue
        out[root] = set(d.get('meta', {}).get('selected_keys') or [])
    return out, corrupt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--min', type=float, default=90.0, help='fail if any root RU%% below this')
    ap.add_argument('--keys', metavar='ROOT', help='print the missing RU sub-card keys for ROOT')
    ap.add_argument('--root', metavar='ROOT', help='restrict the coverage report to one root')
    ap.add_argument('--warn-only', action='store_true',
                    help='advisory mode: print coverage but always exit 0 (used by save_and_audit)')
    ap.add_argument('--strict-denominator', action='store_true',
                    help='also fail when a root has RU cards but no EN denominator to verify against')
    args = ap.parse_args()

    ru = ru_by_root()
    intended, corrupt_en = intended_by_root()

    if args.root:
        ru = {k: v for k, v in ru.items() if k == args.root}
        intended = {k: v for k, v in intended.items() if k == args.root}
        corrupt_en = [c for c in corrupt_en if c[0] == args.root]

    if args.keys:
        root = args.keys
        miss = [k for k in sorted(intended.get(root, set())) if k not in ru.get(root, set())]
        print(','.join(miss))
        return

    roots = sorted(set(ru) | set(intended), key=str.lower)
    print('%-8s %6s %6s %6s  %s' % ('root', 'RU', 'intend', 'RU%', 'flag'))
    worst = 100.0
    partial = []
    unverifiable = []      # RU cards present but NO EN denominator to check against
    for root in roots:
        have = ru.get(root, set())
        want = intended.get(root, set())
        # No EN denominator. A root with RU cards here is UNVERIFIABLE, not exempt — surface
        # it loudly (this is exactly how gam 6/127 stayed invisible). A root with no RU cards
        # AND no denominator is simply not started; report it plainly.
        if not want:
            if have:
                unverifiable.append((root, len(have)))
                print('%-8s %6d %6s %6s  %s' % (root, len(have), '?', '?',
                                                'UNVERIFIABLE (no EN denom)'))
            else:
                print('%-8s %6d %6s %6s  %s' % (root, 0, '?', '?', '(not started)'))
            continue
        pct = 100.0 * len(have & want) / len(want)
        flag = '' if pct >= args.min else 'LOW'
        if pct < 100:
            partial.append((root, pct, len(have), len(want)))
        worst = min(worst, pct)
        print('%-8s %6d %6d %5.0f%%  %s' % (root, len(have), len(want), pct, flag))

    print('\npartial RU roots (<100%%): %d' % len(partial))
    for root, pct, h, w in sorted(partial, key=lambda x: x[1]):
        print('  %-8s %5.0f%%  (%d/%d)  catch-up: python src/pilot/ru_coverage.py --keys %s'
              % (root, pct, h, w, root))

    # Loud, non-silent surfacing of the two ways the denominator can be absent.
    if corrupt_en:
        print('\n⚠ CORRUPT EN denominator file(s) — cannot verify these root(s):')
        for root, err in corrupt_en:
            print('  wf_output.en.%s.json  %s' % (root, err))
    if unverifiable:
        print('\n⚠ UNVERIFIABLE: %d root(s) have RU cards but NO EN denominator — coverage'
              % len(unverifiable))
        print('  cannot be computed (the exact blind spot that hid gam 6/127). Build the EN')
        print('  denominator (wf_output.en.<root>.json) before trusting these as complete:')
        for root, n in unverifiable:
            print('    %-8s %d RU cards, denominator unknown' % (root, n))

    below = [p for p in partial if p[1] < args.min]
    # A corrupt denominator is a hard data defect the gate exists to catch -> always fail.
    # A partial root below --min -> fail. Missing (but not corrupt) denominators fail only
    # under --strict-denominator, since the EN track legitimately lags the RU track.
    fail_reasons = []
    if below:
        fail_reasons.append('%d root(s) below %.0f%% RU coverage' % (len(below), args.min))
    if corrupt_en:
        fail_reasons.append('%d corrupt EN denominator file(s)' % len(corrupt_en))
    if args.strict_denominator and unverifiable:
        fail_reasons.append('%d unverifiable root(s) (no EN denominator)' % len(unverifiable))

    if fail_reasons and not args.warn_only:
        print('\nFAIL: %s' % '; '.join(fail_reasons))
        sys.exit(1)
    if fail_reasons:
        print('\nWARN (advisory): %s' % '; '.join(fail_reasons))
    else:
        print('\nOK: all roots >= %.0f%% RU coverage%s' % (
            args.min, '' if not unverifiable else ' (some roots unverifiable — see above)'))


if __name__ == '__main__':
    main()
