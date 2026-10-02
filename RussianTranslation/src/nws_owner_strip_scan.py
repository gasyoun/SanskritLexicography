#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nws_owner_strip_scan.py — H5707 R1 corpus scan: quantify what the corrected
owner-cite strip changes vs the OLD first-occurrence cut.

OLD (pre-fix): re.sub(escape(owner-base) + r'.*$', '', g) — first occurrence,
no re.S. NEW (compile_translatable.mask_nws_gloss): last occurrence, re.S, and
only when it actually sits at the tail (fail toward no data loss).

Runs over the packed NWS layer (pwg-ru-data/layers/nws.tar.gz, one JSON per
word: {key1, iast, nws}) — no model calls, read-only, never writes the layer.

  python nws_owner_strip_scan.py [--tar PATH] [--limit N] [--samples K]
"""
import argparse
import io
import json
import os
import re
import sys
import tarfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nws_split as NS  # noqa: E402

DEF_TAR = '/Users/mac/Documents/GitHub/pwg-ru-data/layers/nws.tar.gz'


def _base(owner):
    return re.escape(owner.split(' (s.v')[0]).replace(r'\ ', r'\s*')


def old_cut(g, owner):
    """The pre-H5707 first-occurrence cut: returns the gloss after stripping."""
    if not owner:
        return g
    return re.sub(_base(owner) + r'.*$', '', g).rstrip(' .')


def new_cut_span(g, owner):
    """The H5707 tail-anchored cut: returns (gloss, cut_start|None)."""
    if not owner:
        return g, None
    base = _base(owner)
    last = None
    for last in re.finditer(base, g):
        pass
    if last and (len(g) - last.start()) <= 2 * len(base) + 40:
        return g[:last.start()].rstrip(' .'), last.start()
    return g, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tar', default=DEF_TAR)
    ap.add_argument('--limit', type=int, default=0, help='scan only the first N words')
    ap.add_argument('--samples', type=int, default=8)
    args = ap.parse_args()

    stats = {'words': 0, 'entries': 0, 'owned': 0, 'multi_occurrence': 0,
             'same': 0, 'rescued_truncation': 0, 'rescued_miss': 0,
             'shrank_cut': 0}
    samples = {'rescued_truncation': [], 'rescued_miss': [], 'shrank_cut': []}

    with tarfile.open(args.tar, 'r:gz') as tf:
        for member in tf:
            if not member.name.endswith('.json'):
                continue
            if args.limit and stats['words'] >= args.limit:
                break
            stats['words'] += 1
            try:
                item = json.load(tf.extractfile(member))
            except (ValueError, OSError):
                continue
            frag = item.get('nws') or ''
            if not frag:
                continue
            for e in NS.split(frag):
                stats['entries'] += 1
                owner = e['owners'][0] if e['owners'] else ''
                g = e['gloss']
                if not g:
                    continue
                base = _base(owner) if owner else None
                if base:
                    stats['owned'] += 1
                    occ = len(re.findall(base, g))
                    if occ >= 2:
                        stats['multi_occurrence'] += 1
                o = old_cut(g, owner)
                nw, cut_at = new_cut_span(g, owner)
                if o == nw:
                    stats['same'] += 1
                elif len(o) < len(nw):
                    # OLD destroyed text the NEW keeps (first-occurrence or
                    # no-re.S over-cut) — the silent translation-input loss
                    stats['rescued_truncation'] += 1
                    if len(samples['rescued_truncation']) < args.samples:
                        samples['rescued_truncation'].append(
                            (item.get('key1'), e.get('lemma'), g[:160],
                             'OLD:%r' % o[:80], 'NEW:%r' % nw[:80]))
                elif len(o) > len(nw):
                    # OLD kept text (cite not stripped) the NEW now strips
                    stats['rescued_miss'] += 1
                    if len(samples['rescued_miss']) < args.samples:
                        samples['rescued_miss'].append(
                            (item.get('key1'), e.get('lemma'), g[:160]))
                else:
                    stats['shrank_cut'] += 1

    print(json.dumps(stats, ensure_ascii=False, indent=1))
    for kind, rows in samples.items():
        print('\n== %s ==' % kind)
        for r in rows:
            print(' ', r)


if __name__ == '__main__':
    main()
