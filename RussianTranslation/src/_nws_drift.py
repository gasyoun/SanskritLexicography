#!/usr/bin/env python
"""NWS snapshot drift vs current csl-orig — 'how stale is NWS's ~2013 base?'

NWS bundles pw (Böhtlingk) + Schmidt as a ~2013 Cologne (Malten) snapshot. csl-orig
holds today's Cologne pw/sch (years of issue-driven corrections since). Both digitize
the SAME print, so comparing them measures what Cologne corrected since NWS forked.

We have, per scraped a-card: full `sch` text, full `nws` text, and `pw_len` (only the
length of NWS's pw fragment was stored). So:
  • SCH  — coverage drift (presence) + content drift (token Jaccard, both IAST/Latin)
  • PW   — coverage drift (presence) + a coarse length-delta (full text not stored)

  python _nws_drift.py [section]      default 'a'
"""
import os, re, sys, json, glob, collections
sys.stdout.reconfigure(encoding='utf-8')

import dict_merge as dm
import corpus_gate as cg

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'pilot', 'nws')
CONTROL = ('_watch_state.json',)
_TOK = re.compile(r"[a-zāīūṛṝḷḹṅñṭḍṇśṣṃḥ]+", re.I)


def tokens(text):
    """Content token set, with the two boilerplates stripped so we compare CONTENT
    not formatting: csl-orig's trailing {part=,seq=,type=,n=} metadata, and NWS's
    '― Schmidt S. NN (show scan)' / '― pw Vol...' provenance tail."""
    t = text or ''
    t = re.sub(r'\{[a-zñ]+=[^}]*\}', ' ', t)                       # csl-orig metadata block
    t = re.split(r'[―—]\s*(?:Schmidt|pw|NWS|nws)\b', t)[0]         # NWS provenance tail
    t = re.sub(r'\(?\s*show scan\s*\)?', ' ', t, flags=re.I)
    t = re.sub(r'<[^>]+>', ' ', t)                                  # tags / <ls>
    t = re.sub(r'\{[%#]|[%#]\}|[¦{}]', ' ', t)                      # {% %} markup
    return set(m.group(0).lower() for m in _TOK.finditer(t) if len(m.group(0)) > 1)


def jaccard(a, b):
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def orig_text(records):
    return ' '.join(records) if records else ''


def main():
    section = sys.argv[1] if len(sys.argv) > 1 else 'a'
    cards = {}
    for f in glob.glob(os.path.join(OUT, '*.json')):
        if os.path.basename(f) in CONTROL:
            continue
        try:
            d = json.load(open(f, encoding='utf-8'))
            cards[d['key1']] = d
        except Exception:
            pass

    sch_idx, pw_idx = dm.index('sch'), dm.index('pw')

    def joined(idx, k):
        return ' '.join('\n'.join(b[1:]) for b in idx.get(cg.form_key(k), []))

    n = len(cards)
    sch = collections.Counter()      # both / nws_only / orig_only / neither
    pw = collections.Counter()
    sims = []                         # SCH content Jaccard for in-both
    pwlen_delta = []                  # (nws_pw_len, orig_pw_len) for in-both
    changed_examples, missing_examples = [], []

    for k, d in cards.items():
        nws_sch, nws_pw = bool(d.get('sch')), bool(d.get('pw_len'))
        o_sch, o_pw = joined(sch_idx, k), joined(pw_idx, k)
        os_has, op_has = bool(o_sch.strip()), bool(o_pw.strip())

        sch[('both' if nws_sch and os_has else 'nws_only' if nws_sch else 'orig_only' if os_has else 'neither')] += 1
        pw[('both' if nws_pw and op_has else 'nws_only' if nws_pw else 'orig_only' if op_has else 'neither')] += 1

        if nws_sch and os_has:
            s = jaccard(tokens(d['sch']), tokens(o_sch))
            sims.append(s)
            if s < 0.5 and len(changed_examples) < 6:
                changed_examples.append((k, round(s, 2)))
        if nws_pw and op_has:
            pwlen_delta.append((d['pw_len'], len(o_pw)))
        if os_has and not nws_sch and len(missing_examples) < 6:
            missing_examples.append(k)

    print('=== NWS drift vs current csl-orig — section %r (%d headwords) ===' % (section, n))
    print('\n-- SCH (Schmidt) coverage --')
    for kk in ('both', 'nws_only', 'orig_only', 'neither'):
        print('  %-9s %6d (%4.1f%%)' % (kk, sch[kk], 100 * sch[kk] / n))
    print('   nws_only  = NWS keeps a Schmidt entry csl-orig no longer indexes (stale/restructured)')
    print('   orig_only = csl-orig added/now-indexes Schmidt material NWS\'s 2013 snapshot lacked')
    if sims:
        b = collections.Counter()
        for s in sims:
            b['identical (≥.95)' if s >= .95 else 'minor (.8-.95)' if s >= .8 else 'moderate (.5-.8)' if s >= .5 else 'major (<.5)'] += 1
        print('\n-- SCH content drift (token Jaccard, %d in-both) --' % len(sims))
        for lab in ('identical (≥.95)', 'minor (.8-.95)', 'moderate (.5-.8)', 'major (<.5)'):
            print('  %-18s %6d (%4.1f%%)' % (lab, b[lab], 100 * b[lab] / len(sims)))
        print('  mean Jaccard: %.3f' % (sum(sims) / len(sims)))
        print('  sample changed (key, sim):', changed_examples)
    print('\n-- PW (Böhtlingk) coverage --')
    for kk in ('both', 'nws_only', 'orig_only', 'neither'):
        print('  %-9s %6d (%4.1f%%)' % (kk, pw[kk], 100 * pw[kk] / n))
    if pwlen_delta:
        big = sum(1 for a, b2 in pwlen_delta if b2 and abs(a - b2) / max(b2, 1) > 0.5)
        print('  pw length |Δ|>50%% (coarse — full pw text not stored): %d / %d (%.1f%%)'
              % (big, len(pwlen_delta), 100 * big / len(pwlen_delta)))
    print('\n  (SCH orig_only sample — Cologne has, NWS snapshot lacks:', missing_examples, ')')


if __name__ == '__main__':
    main()
