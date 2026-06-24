#!/usr/bin/env python
"""verify_root_glue.py — INDEPENDENT adversarial check of the root SPLIT/GLUE machinery.

Does NOT trust root_segment_proto's own 3-root self-test. It re-derives the checks
corpus-wide and separates two properties the self-test conflates:

  A. LOSSLESSNESS (hard invariant)   — glue(segment(data)) == data, for EVERY record.
     This is near-tautological (partition + concatenation), so it is necessary but NOT
     sufficient: it can be TRUE while the segmentation is wrong. Treated as a hard gate.

  B. SEGMENTATION CORRECTNESS (warn) — do the boundary regexes actually find the real
     sub-card boundaries? Measured by how many `<div n="p">` / `<div n="m">` lines the
     detectors match vs miss across pwg.txt, with the missed lines classified by their
     `<ab>` label. A miss = a block silently merged into the PRECEDING sub-card
     (mis-attribution + size bloat), not lost text — so a WARN, escalatable with --strict.

  C. GLUE COMPLETENESS (hard when present) — for any pilot/input/*.rootmap.json, every
     sub_card has a UNIQUE subkey (so glue cannot drop/overwrite one) and is keyed
     (subkey+kind), so root_glue_translated emits exactly one section per sub_card.
     NOTE: seg_index is deliberately non-contiguous (sentinel for supplement layers;
     `part` splits over-long heads) and may tie — glue orders by (seg_index, part) with a
     stable sort, so ties are fine. Contiguity is NOT the invariant; subkey uniqueness is.

  python verify_root_glue.py            # corpus scan + named giant roots + rootmaps
  python verify_root_glue.py --strict   # treat segmentation mis-grouping as a failure too

Known finding (2026-06-24): `<div n="m">` never occurs in pwg.txt (SEC_RE is dead); the
caus./desid./intens./partic. blocks are encoded `<div n="p">— <ab>caus.</ab>…` and so are
mis-grouped. Reported by Check B; the fix lives in root_segment_proto.py (owned elsewhere).
"""
import os, re, sys, json, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'research'))
sys.path.insert(0, HERE)
import root_segment_proto as RS                       # noqa: E402  segment()/glue()/read_record()
from safe_filename import safe_name                    # noqa: E402

PWG = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'csl-orig', 'v02', 'pwg', 'pwg.txt'))
INP = os.path.join(HERE, 'pilot', 'input')
NAMED_GIANT = ['55166', '21814', '72578']              # bhū + both gam homonyms (the doc's probes)
DIVP = re.compile(r'^<div n="p">')
DIVM = re.compile(r'^<div n="m">')
ABLAB = re.compile(r'^<div n="p">\s*—?\s*<ab>([^<]+)</ab>')
SECLABELS = {'caus.', 'desid.', 'intens.', 'partic.', 'pass.', 'insens.'}


def iter_records(path):
    """Stream pwg.txt once -> (L, k1, datalines) per <L>…<LEND> record."""
    L = k1 = None
    data = []
    inrec = False
    with open(path, encoding='utf-8') as f:
        for ln in f:
            ln = ln.rstrip('\r\n')
            if ln.startswith('<L>'):
                m = re.match(r'<L>([^<]*)<', ln)
                L = m.group(1) if m else None
                mk = re.search(r'<k1>([^<]*)', ln)
                k1 = mk.group(1) if mk else '?'
                data = []
                inrec = True
            elif ln.startswith('<LEND>'):
                if inrec:
                    yield L, k1, data
                inrec = False
            elif inrec:
                data.append(ln)


def check_lossless_and_segmentation(strict):
    n_rec = n_lossy = 0
    np_raw = np_recognized = n_secondary = 0
    missed = collections.Counter()
    worst = []
    for L, k1, data in iter_records(PWG):
        has_p = any(DIVP.match(l) for l in data)
        if not has_p and not any(DIVM.match(l) for l in data):
            continue                                   # only records with sub-card boundaries
        n_rec += 1
        cards = RS.segment(data)
        if RS.glue(cards) != data:
            n_lossy += 1
            worst.append((L, k1))
        # A <div n="p"> line is RECOGNISED iff it begins a sub-card (prefix or secondary).
        starts = {c['lines'][0] for c in cards if c['lines']}
        n_secondary += sum(1 for c in cards if c['kind'] == 'secondary')
        for l in data:
            if DIVP.match(l):
                np_raw += 1
                if l in starts:
                    np_recognized += 1
                else:
                    m = ABLAB.match(l)
                    missed[m.group(1).strip() if m else '(no <ab> label)'] += 1
    np_miss = np_raw - np_recognized
    print('## A. Losslessness (hard invariant)')
    print('   records with boundaries scanned : %d' % n_rec)
    print('   round-trip FAILURES             : %d  -> %s'
          % (n_lossy, 'PASS' if n_lossy == 0 else 'FAIL ' + ', '.join('%s/%s' % w for w in worst[:10])))
    print('## B. Segmentation correctness (warn%s)' % (', escalated by --strict' if strict else ''))
    print('   <div n="p"> total / recognised-as-boundary / NOT-split : %d / %d / %d (%.1f%%)'
          % (np_raw, np_recognized, np_miss, 100.0 * np_miss / max(np_raw, 1)))
    print('   secondary sub-cards split out (caus/desid/intens/partic/pass/insens): %d' % n_secondary)
    if missed:
        print('   still-merged <div n="p"> labels: '
              + ', '.join('%s=%d' % (k, v) for k, v in missed.most_common(8)))
    seclike = sum(v for k, v in missed.items() if k.strip().rstrip('.').lower() in SECLABELS)
    print('   => %d secondary-conjugation blocks still merged into the preceding sub-card.' % seclike)
    lossless_ok = n_lossy == 0
    seg_ok = seclike == 0                              # all caus/desid/intens/partic now split
    return lossless_ok, seg_ok, seclike


def check_glue_completeness():
    maps = [f for f in os.listdir(INP) if f.endswith('.rootmap.json')] if os.path.isdir(INP) else []
    print('## C. Glue completeness (hard when rootmaps present)')
    if not maps:
        print('   no pilot/input/*.rootmap.json yet — skipped (run _pilot_gen_merged.py --root-split)')
        return True
    bad = 0
    for fn in sorted(maps):
        rm = json.load(open(os.path.join(INP, fn), encoding='utf-8'))
        subs = rm.get('sub_cards', [])
        keys = [s.get('subkey') for s in subs]
        uniq = len(set(keys)) == len(keys) and all(keys)
        keyed = all(s.get('subkey') and s.get('kind') for s in subs)
        ties = len(subs) - len({(s.get('seg_index'), s.get('part', 0)) for s in subs})
        ok = bool(subs) and uniq and keyed
        flag = '' if ok else '  <-- BAD'
        # Only print the per-file line when something is off; otherwise summarise.
        if not ok:
            print('   %-40s sub_cards=%d uniq_subkey=%s keyed=%s%s'
                  % (fn, len(subs), uniq, keyed, flag))
        bad += 0 if ok else 1
        check_glue_completeness.ties = getattr(check_glue_completeness, 'ties', 0) + ties
    print('   %d rootmap(s): %d with unique keyed subkeys, %d bad; %d (seg_index,part) ties '
          '(stable-sorted, OK)' % (len(maps), len(maps) - bad, bad, getattr(check_glue_completeness, 'ties', 0)))
    return bad == 0


def main():
    strict = '--strict' in sys.argv
    print('verify_root_glue — independent SPLIT/GLUE audit (source: pwg.txt)\n')
    lossless_ok, seg_ok, sec = check_lossless_and_segmentation(strict)
    print()
    glue_ok = check_glue_completeness()
    print('\n## Verdict')
    print('   A losslessness   : %s' % ('PASS' if lossless_ok else 'FAIL'))
    print('   B segmentation   : %s (%d secondary block(s) still merged)'
          % ('PASS' if seg_ok else 'WARN', sec))
    print('   C glue complete  : %s' % ('PASS' if glue_ok else 'FAIL'))
    hard_ok = lossless_ok and glue_ok and (seg_ok or not strict)
    print('   => %s' % ('ALL GATES PASS' if hard_ok else 'GATE FAILURE'))
    return 0 if hard_ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
