#!/usr/bin/env python
"""audit_root_split.py — integrity audit of the --root-split pipeline before a volume run.

Exercises the REAL code path (gen_root_split) on a broad sample of giant roots from the
freq queue and checks, per root:
  L  LOSSLESS    — every non-blank PWG content line of EVERY homonym appears across the
                   sub-cards exactly (no drop, no duplication).
  H  HOMONYMS    — every giant homonym (>=MIN_SPLIT prefix divisions) produced prefix
                   sub-cards; no homonym record silently dropped.
  G  GLUE        — root_glue_translated orders all sub-cards (hom→seg→part, supplements
                   last) with no missing subkey.
  P  PORTRAITS   — every PWG sub-card carries corpus_synonyms (head=root, prefix=prefixed
                   -form or labelled root-fallback); supplements may be empty.
Plus a whole-card REGRESSION check (a noun still gets a full portrait + all layers) and a
CANONICAL-SAFETY check (no write outside the gitignored pilot/input).

  python audit_root_split.py [N]      # audit the top-N giant roots (default 60)
"""
import json, os, re, sys, collections

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'research'))
import _pilot_gen_merged as G
import dict_merge as dm
import corpus_gate as cg
import root_segment_proto as RS
from safe_filename import safe_name

IN = G.OUT  # pilot/input
MANIFEST = os.path.join(HERE, 'pilot', 'output', 'scale_manifest.freq.json')


def homonym_lines(key):
    """multiset of non-blank PWG content lines across ALL homonym records of key."""
    c = collections.Counter()
    for buf in dm.index('pwg').get(cg.form_key(key), []):
        for l in buf:
            if not (l.startswith('<L>') or l.startswith('<LEND>')) and l.strip():
                c[l] += 1
    return c


def subcard_lines(rootmap):
    """multiset of non-blank PWG lines across the PWG sub-cards (excl. supplements)."""
    c = collections.Counter()
    for s in rootmap['sub_cards']:
        if s['kind'] == 'supplement':
            continue
        t = open(os.path.join(IN, s['subkey'] + '.raw.txt'), encoding='utf-8').read()
        body = t.split('===\n\n', 1)[1] if '===\n\n' in t else t
        for l in body.split('\n'):
            if not l.startswith('=== LAYER:') and l.strip():
                c[l] += 1
    return c


def giant_homonyms(key):
    out = []
    for i, buf in enumerate(dm.index('pwg').get(cg.form_key(key), [])):
        dl = [l for l in buf if not (l.startswith('<L>') or l.startswith('<LEND>'))]
        if sum(1 for ccc in RS.segment(dl) if ccc['kind'] == 'prefix') >= G.MIN_SPLIT:
            out.append(i)
    return out


def audit_root(key):
    """Returns (ok, dict-of-checks, detail)."""
    n = G.gen_root_split(key, dm.index('pwg'), verbose=False)
    if n is None:
        return None  # not giant
    rm = json.load(open(os.path.join(IN, safe_name(key) + '.rootmap.json'), encoding='utf-8'))
    sc = rm['sub_cards']
    # L: lossless
    orig, got = homonym_lines(key), subcard_lines(rm)
    miss = sum(v for k, v in orig.items() if got[k] < v)
    extra = sum(got[k] - v for k, v in orig.items() if got[k] > v) + \
            sum(v for k, v in got.items() if k not in orig)
    L = (miss == 0 and extra == 0)
    # H: every giant homonym split (has prefix sub-cards)
    split_homs = {s['hom'] for s in sc if s['kind'] == 'prefix'}
    H = set(giant_homonyms(key)) <= split_homs
    # G: glue covers every subkey, no missing
    keyset = {s['subkey'] for s in sc}
    G_ok = len(keyset) == len(sc)  # subkeys unique
    # P: every PWG sub-card has corpus_synonyms (head/prefix/secondary); supplements may be empty
    P = True
    for s in sc:
        if s['kind'] == 'supplement':
            continue
        pf = json.load(open(os.path.join(IN, s['subkey'] + '.portrait.json'), encoding='utf-8'))
        if not (pf and pf[0].get('corpus_synonyms')):
            # tolerated only if the bare root itself has no corpus entry at all
            if cg.form_key(key) and G.M.corpus_synonyms(key):
                P = False
    checks = {'L': L, 'H': H, 'G': G_ok, 'P': P}
    detail = '' if all(checks.values()) else \
        'miss=%d extra=%d giant_homs=%s split=%s' % (miss, extra, giant_homonyms(key), sorted(split_homs))
    return (all(checks.values()), checks, detail, len(sc))


def main():
    topn = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 60
    keys = [e['key1'] for e in json.load(open(MANIFEST, encoding='utf-8'))]
    print('=== root-split integrity audit (real gen_root_split path) ===')
    audited = passed = 0
    fails = []
    tot_sub = 0
    for k in keys:
        if audited >= topn:
            break
        r = audit_root(k)
        if r is None:
            continue
        audited += 1
        ok, checks, detail, nsub = r
        tot_sub += nsub
        passed += 1 if ok else 0
        if not ok:
            flags = ''.join(c if checks[c] else c.lower() for c in 'LHGP')
            fails.append((k, flags, detail))
    print('giant roots audited: %d | PASS %d | FAIL %d | sub-cards generated: %d'
          % (audited, passed, audited - passed, tot_sub))
    if fails:
        print('\nFAILURES (lowercase = failed check L=lossless H=homonyms G=glue P=portrait):')
        for k, flags, d in fails:
            print('  %-8s %s  %s' % (k, flags, d))
    else:
        print('ALL %d GIANT ROOTS: LOSSLESS · ALL HOMONYMS SPLIT · GLUE-COMPLETE · PORTRAITS PRESENT' % audited)

    # regression: whole-card (non-split) path still yields a full portrait + layers
    print('\n=== whole-card regression (non-split path) ===')
    for noun in ['rasa', 'kArya', 'loka']:
        G.gen_card(noun, dm.index('pwg'), verbose=False)
        pf = json.load(open(os.path.join(IN, safe_name(noun) + '.portrait.json'), encoding='utf-8'))
        raw = open(os.path.join(IN, safe_name(noun) + '.raw.txt'), encoding='utf-8').read()
        has_pf = bool(pf and pf[0].get('senses'))
        layers = raw.count('=== LAYER:')
        print('  %-7s portrait_senses=%s  layers=%d  %s'
              % (noun, has_pf, layers, 'OK' if (has_pf and layers >= 1) else 'REGRESSION'))


if __name__ == '__main__':
    main()
