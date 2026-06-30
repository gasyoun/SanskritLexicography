#!/usr/bin/env python
r"""Tri-lingual (German source / Russian / English) comparison for the PWG->EN pilot.

Joins the RU per-root output (wf_output.sc.<root>.json, german+russian) with the EN
per-root output (wf_output.en.<root>.json, german+english) by (sub-card key, sense index)
and prints/writes a German|Russian|English table — the pilot deliverable proving the
tri-lingual edition works on the already-done roots.

  python src/pilot/trilingual_sample.py vad                 # print vad sample
  python src/pilot/trilingual_sample.py --all --out FILE     # all done roots -> markdown
"""
import argparse
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))            # RussianTranslation repo root

_TAG = re.compile(r'<[^>]+>')
_SK = re.compile(r'\{#.*?#\}|\{%.*?%\}')


def plain(s):
    """Strip markup/Sanskrit so the gloss prose is readable in the comparison."""
    if not s:
        return ''
    s = _SK.sub('', _TAG.sub('', s))
    return re.sub(r'\s{2,}', ' ', s).strip(' ;,.—-')


def load(tag, root):
    fp = os.path.join(ROOT, 'wf_output.%s.%s.json' % (tag, root))
    if not os.path.exists(fp):
        return {}
    out = {}
    for r in json.load(open(fp, encoding='utf-8')).get('results') or []:
        c = r.get('card')
        if c:
            out[r['key']] = c
    return out


def rows_for(root):
    ru, en = load('sc', root), load('en', root)
    rows = []
    for key in sorted(set(ru) | set(en)):
        rc, ec = ru.get(key), en.get(key)
        rsen = [s for rec in (rc or {}).get('records', []) for s in rec.get('senses', [])] if rc else []
        esen = [s for rec in (ec or {}).get('records', []) for s in rec.get('senses', [])] if ec else []
        for i in range(max(len(rsen), len(esen))):
            de = plain((rsen[i] if i < len(rsen) else esen[i] if i < len(esen) else {}).get('german'))
            rr = plain(rsen[i].get('russian')) if i < len(rsen) else ''
            ee = plain(esen[i].get('english')) if i < len(esen) else ''
            if de or rr or ee:
                rows.append((key, de, rr, ee))
    return rows


def done_roots():
    roots = set()
    for fp in glob.glob(os.path.join(ROOT, 'wf_output.en.*.json')):
        roots.add(os.path.basename(fp)[len('wf_output.en.'):-len('.json')])
    return sorted(roots)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root', nargs='?')
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--out')
    ap.add_argument('--limit', type=int, default=8)
    args = ap.parse_args()
    roots = done_roots() if args.all else [args.root]
    lines = []
    for root in roots:
        rows = rows_for(root)
        lines.append('\n## %s — %d aligned sense rows (DE source / RU / EN)\n' % (root, len(rows)))
        for key, de, rr, ee in rows[:args.limit]:
            lines.append('- **%s**' % key)
            lines.append('  - DE: %s' % de[:200])
            lines.append('  - RU: %s' % rr[:200])
            lines.append('  - EN: %s' % ee[:200])
    text = '\n'.join(lines)
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            f.write('# PWG tri-lingual pilot sample (DE source -> RU + EN)\n' + text + '\n')
        print('wrote %s (%d roots)' % (args.out, len(roots)))
    else:
        print(text)


if __name__ == '__main__':
    main()
