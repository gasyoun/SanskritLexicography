#!/usr/bin/env python
"""Deterministic NWS split-preview audit for one dictionary section.

Self-contained driver for the per-section NWS attribution audit (the same one
run interactively for sections a–i). One command audits a whole letter:

  python nws_audit_section.py <letter>      # e.g. j, k, l, … (or A-section: a)

It (1) builds scale_manifest.<letter>.json via scale_route.py if missing,
(2) generates the merged pilot inputs (resumable — skips existing), then
(3) runs the deterministic nws_split parse over every NWS fragment and reports:

  • roman-cite BLEEDS  — the av-class F12-slide cause (`<tag> ; Name : roman >`
    bleeding onto the next gloss). Expect 0; any hit is worth a look (the owner
    is usually still correct, but flag it).
  • NO-OWNER entries   — split() found no closing cite. Split into benign
    empty-segments vs real losses, the latter bucketed by KNOWN-LIMITATION
    class (Meister `(2.1)`, roman page, Böhtlingk `*NNN`, page-less x-ref) or
    OTHER (investigate OTHER by hand).
  • OWNER-MAP cross-check — the injected `PRE-PARSED OWNER MAP` layer's entry
    count and `[NWS: ?]` count must match the split-preview one-for-one, and
    residual-contamination must be 0 (proves the nws_owner_map debleed held).

Exit code is always 0 (audit is informational); OTHER no-owner cases > 0 are
printed in full so a human can classify them. Owner field is never modified.

Known limitations (do NOT try to "fix" in nws_split — each was tried and
reverted because admitting the token destabilises segment/owner alignment):
  Meister 1988 (2.1) : N   — `.` inside a parenthetical volume number
  Walter 1893 : XLVII      — roman-numeral page
  Böhtlingk 1887 : *163    — asterisk-prefixed page
  page-less cross-reference (`s.v. X (pw)` with no `Name : page`) — benign.
"""
import os, re, sys, json, subprocess
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import nws_split as N
from safe_filename import safe_name

HERE = os.path.dirname(os.path.abspath(__file__))
# H1386 P3f: PWG_INPUT_DIR points a hermetic harness at a sandbox input dir.
INP = os.environ.get('PWG_INPUT_DIR') or os.path.join(HERE, 'pilot', 'input')
OUT = os.path.join(HERE, 'pilot', 'output')

BLEED = re.compile(r'^[\s,;]*[^>]*?;\s*[A-ZÀ-ÖØ-ÞĀ-ỿ][^>:]*?\s:\s[\dIVXLCDM]+[A-Za-z]?\s*>\s*')


def classify(g):
    if 'Meister' in g:
        return 'Meister (2.1)'
    if re.search(r':\s*\*\d', g):
        return 'Böhtlingk *NNN'
    if re.search(r':\s*[IVXLCDM]+\b', g):
        return 'roman page'
    if not re.search(r'\s:\s', g):
        return 'page-less x-ref'
    return 'OTHER'


def ensure_inputs(section):
    if not os.path.exists(os.path.join(OUT, 'scale_manifest.%s.json' % section)):
        print('· building scale_manifest.%s.json …' % section)
        subprocess.run([sys.executable, os.path.join(HERE, 'scale_route.py'), section],
                       cwd=HERE, check=True)
    print('· generating merged inputs (resumable) …')
    subprocess.run([sys.executable, os.path.join(HERE, '_pilot_gen_merged.py'),
                    '--manifest', section], cwd=HERE, check=True)


def audit(section):
    keys = [e['key1'] for e in json.load(
        open(os.path.join(OUT, 'scale_manifest.%s.json' % section), encoding='utf-8'))]
    n_with = n_ent = 0
    bleeds, noown = [], []
    map_entries = map_q = map_resid = 0
    for k in keys:
        frag = N.nws_fragment(k)
        if not frag:
            continue
        n_with += 1
        for e in N.split(frag):
            n_ent += 1
            if not e['owners']:
                noown.append((k, e['gloss']))
            if BLEED.match(e['gloss']):
                bleeds.append((k, BLEED.match(e['gloss']).group(0).strip()))
        p = os.path.join(INP, safe_name(k) + '.raw.txt')
        try:
            txt = open(p, encoding='utf-8').read()
        except OSError:
            continue
        m = re.search(r'PRE-PARSED OWNER MAP.*\Z', txt, re.S)
        if m:
            body = m.group(0)
            map_entries += len(re.findall(r'^\s*\d+\. \[NWS:', body, re.M))
            map_q += len(re.findall(r'\[NWS: \?\]', body))
            if re.search(r'\d+\. \[NWS:[^\]]*\][^\n]*; [A-ZÀ-ÖŚṚ][^\n]*? : [IVXLCDM]+\b', body):
                map_resid += 1
            if re.search(r'\{#[\s,;–-]*#\}', body):
                map_resid += 1

    empty = [x for x in noown if not x[1].strip()]
    nonempty = [x for x in noown if x[1].strip()]
    from collections import Counter
    by_cls = Counter(classify(g) for _, g in nonempty)

    print('\n=== NWS split-preview audit — %s-section ===' % section)
    print('keys total            : %d' % len(keys))
    print('keys with NWS fragment: %d' % n_with)
    print('total NWS entries     : %d' % n_ent)
    print('roman-cite BLEEDS     : %d' % len(bleeds))
    for k, s in bleeds[:20]:
        print('   ~ %-14s [%s]' % (k, s[:44]))
    print('no-owner entries      : %d  (benign empty %d, real %d)'
          % (len(noown), len(empty), len(nonempty)))
    for cl, c in by_cls.most_common():
        print('   %-16s %d' % (cl, c))
    for k, g in nonempty:
        if classify(g) == 'OTHER':
            print('   ?? OTHER  %-12s …%s' % (k, g[-56:]))
    pct = (100.0 * len(nonempty) / n_ent) if n_ent else 0.0
    print('real-loss rate        : %.2f%%' % pct)
    print('owner-map cross-check : %d entries, %d [NWS: ?]  (split-preview: %d / %d)'
          % (map_entries, map_q, n_ent, len(noown)))
    ok = (map_entries == n_ent and map_q == len(noown) and map_resid == 0)
    print('owner-map residual contamination: %d' % map_resid)
    print('cross-check %s' % ('OK — map matches split-preview, 0 residual'
                              if ok else 'MISMATCH — investigate'))
    other = sum(1 for _, g in nonempty if classify(g) == 'OTHER')
    print('\nSUMMARY: %s-section — %d bleeds, %d real no-owner (%.2f%%), %d OTHER to classify, '
          'cross-check %s'
          % (section, len(bleeds), len(nonempty), pct, other, 'OK' if ok else 'MISMATCH'))


def main():
    if len(sys.argv) < 2 or len(sys.argv[1]) != 1:
        sys.exit('usage: python nws_audit_section.py <letter>   (e.g. j)')
    section = sys.argv[1]
    ensure_inputs(section)
    audit(section)


if __name__ == '__main__':
    main()
