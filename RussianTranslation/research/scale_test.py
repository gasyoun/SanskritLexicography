#-*- coding:utf-8 -*-
"""scale_test.py — run the PWG root segmenter across ALL verbs01 verb roots.

Turns the bhū/gam probes into corpus-wide confidence: for every PWG root that verbs01
found to carry upasargas, segment its record and assert a LOSSLESS round-trip, and compare
the slicer's prefix-division count against verbs01's vetted upasarga count (the FP gap that
analysis #2 predicted — raw <div n=p> >= true upasargas).

Single pass over pwg.txt (don't re-scan 53MB per root).

  python scale_test.py [pwg.txt] [pwg_preverb1.txt]
"""
from __future__ import print_function
import os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import root_segment_proto as RS                              # noqa: E402

PWG = os.path.join(HERE, '..', '..', '..', 'csl-orig', 'v02', 'pwg', 'pwg.txt')
PREVERB = os.path.join(HERE, '..', '..', '..', 'PWG', 'verbs01', 'pwg_preverb1.txt')


def main():
    pwg = sys.argv[1] if len(sys.argv) > 1 else PWG
    preverb = sys.argv[2] if len(sys.argv) > 2 else PREVERB
    # targets: L -> (k1, reported #upasargas) for Cases with upasargas
    targets = {}
    with open(preverb, encoding='utf-8') as f:
        for line in f:
            m = re.match(r';; Case \d+: L=(\S+?), k1=(\S+?),.*#upasargas=(\d+)', line)
            if m and int(m.group(3)) > 0:
                targets[m.group(1)] = (m.group(2), int(m.group(3)))
    # one pass over pwg.txt collecting the target records
    recs = {}
    cur, curL = None, None
    with open(pwg, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\r\n')
            if line.startswith('<L>'):
                m = re.search(r'<L>(\S+?)<', line)
                curL = m.group(1) if m else None
                cur = [line] if curL in targets else None
            elif cur is not None:
                cur.append(line)
                if line.startswith('<LEND>'):
                    recs[curL] = cur
                    cur = None
    # segment + verify each
    n = lossless = 0
    tot_pfx = tot_rep = 0
    fails, gaps, biggest = [], 0, []
    for L, (k1, rep) in targets.items():
        block = recs.get(L)
        if not block or len(block) < 2:
            fails.append((L, k1, 'record not found'))
            continue
        data = block[1:-1]
        cards = RS.segment(data)
        ok = ([ln for c in cards for ln in c['lines']] == data)
        npfx = sum(1 for c in cards if c['kind'] == 'prefix')
        n += 1
        lossless += ok
        if not ok:
            fails.append((L, k1, 'NOT lossless'))
        tot_pfx += npfx
        tot_rep += rep
        if npfx != rep:
            gaps += 1
        biggest.append((npfx, k1, L, rep))
    biggest.sort(reverse=True)
    print('PWG root segmenter — scale test over %d verbs01 roots' % len(targets))
    print('  records found & segmented: %d' % n)
    print('  LOSSLESS round-trips:      %d / %d  (%s)'
          % (lossless, n, 'ALL PASS' if lossless == n else '*** %d FAIL ***' % (n - lossless)))
    print('  prefix sub-cards (slicer): %d   vs verbs01 vetted upasargas: %d  (slicer >= vetted, the FP gap)'
          % (tot_pfx, tot_rep))
    print('  roots where slicer count != vetted count: %d (FP-guard candidates)' % gaps)
    print('  biggest roots (slicer prefix-cards / vetted): '
          + ', '.join('%s %d/%d' % (k, p, r) for p, k, L, r in biggest[:8]))
    if fails:
        print('  FAILURES (%d):' % len(fails))
        for L, k1, why in fails[:20]:
            print('    L=%s k1=%s : %s' % (L, k1, why))


if __name__ == '__main__':
    main()
