#!/usr/bin/env python
"""Density-aware router + coverage-first ordering for the pwg_ru scale-up.

Classifies each headword into the HEAVY path (full per-sense discrimination +
Opus judge — for polysemous / corpus-backed cards) or the LIGHT path (one
lightweight Sonnet pass — for the 1-sense long tail), and emits a coverage-first
ordered manifest the scale driver consumes.

  python scale_route.py [a|all]      # a = a-section (default), all = whole dict
"""
import json, os, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import pwg_mask
import corpus_gate as cg
import corpus_harvest as ch

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'pilot', 'output')
MARK = re.compile(r'(?<![^\s—(])(\d{1,2})\)')   # top-level sense markers in the raw body


def heavy(c):
    return c['n_senses'] >= 3 or c['corpus'] >= 3 or c['dict'] >= 2 or c['n_records'] > 1


def main():
    section = sys.argv[1] if len(sys.argv) > 1 else 'a'
    idx = ch.index()
    didx = cg.load_index()
    cards = {}
    for buf in pwg_mask.records():
        m = pwg_mask.HEADER_RE.match(buf[0])
        if not m:
            continue
        k1, k2 = m.group(3), m.group(4)
        if section != 'all' and k1[:1] not in ('a', 'A'):
            continue
        body = '\n'.join(buf[1:])
        c = cards.setdefault(k1, {'k2': k2, 'n_records': 0, 'n_senses': 0})
        c['n_records'] += 1
        c['n_senses'] += len(set(MARK.findall(body)))
    for k1, c in cards.items():
        c['corpus'] = len(idx.get(cg.form_key(k1), []))
        indep, kow = cg.lookup(didx, k1, c['k2'])
        c['dict'], c['kow'] = len(indep), len(kow)
        c['covered'] = bool(c['corpus'] or c['dict'] or c['kow'])
        c['path'] = 'heavy' if heavy(c) else 'light'
    # coverage-first: covered before uncovered; heavy before light; densest first
    order = sorted(cards.items(),
                   key=lambda kv: (not kv[1]['covered'], kv[1]['path'] != 'heavy',
                                   -(kv[1]['corpus'] + kv[1]['n_senses'] * 50 + kv[1]['dict'] * 100)))
    os.makedirs(OUT, exist_ok=True)
    manifest = [{'key1': k, 'path': c['path'], 'covered': c['covered'],
                 'n_records': c['n_records'], 'n_senses': c['n_senses'],
                 'corpus': c['corpus'], 'dict': c['dict'], 'kow': c['kow']} for k, c in order]
    mpath = os.path.join(OUT, 'scale_manifest.%s.json' % section)
    json.dump(manifest, open(mpath, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)

    npath = collections.Counter(c['path'] for c in cards.values())
    ncov = sum(1 for c in cards.values() if c['covered'])
    heavy_cov = sum(1 for c in cards.values() if c['path'] == 'heavy' and c['covered'])
    print('section %s: %d headwords' % (section, len(cards)))
    print('  HEAVY (full discrimination + judge): %d  | LIGHT (single pass): %d'
          % (npath['heavy'], npath['light']))
    print('  covered (dict/corpus/KOW reuse): %d (%.0f%%)' % (ncov, 100.0 * ncov / max(len(cards), 1)))
    print('  → coverage-first core (heavy & covered, done first): %d' % heavy_cov)
    print('  manifest → %s' % os.path.basename(mpath))
    print('  first 12 in run order:')
    for e in manifest[:12]:
        print('    %-14s %-6s sens=%-2d rec=%d corpus=%-4d dict=%d'
              % (e['key1'], e['path'], e['n_senses'], e['n_records'], e['corpus'], e['dict']))


if __name__ == '__main__':
    main()
