#!/usr/bin/env python
"""audit_coverage.py — FREE deterministic coverage gate (zero LLM tokens).

Part of the "Python at max, LLM at minimum" QA strategy (TOKEN_OPTIMIZATION_2026-06-27.md):
the LLM judge's only irreplaceable job is catching *mistranslation*; everything mechanical
is checked in Python for free. This gate catches the most common non-mechanical failure the
markup gate misses — a card that silently DROPS or FABRICATES senses.

For each card in wf_output.json vs its <stem>.raw.txt it compares:
  raw sense markers  = max(count '〉' U+3009 sense glyph, count '<div n=')   [PWG sense divs]
  card senses        = sum(len(record.senses)) in the produced card
and flags:
  COVERAGE-LOW(c/r)  card has < 0.80 * raw senses   (senses silently dropped)
  COVERAGE-OVER(c/r) card has > 1.50 * raw senses   (senses fabricated / over-split)
Cards with 0 raw markers (NWS / supplement / single-gloss cards) are not sense-divided —
coverage is reported as 'n/a', never failed.

  python audit_coverage.py wf_output.json            # audits every card in the workflow output

Exit non-zero if any card is flagged (CI-usable); re-queue flagged cards.
"""
import json, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, 'pilot', 'input')

LOW, OVER = 0.80, 1.50
DIVN = re.compile(r'<div n=')


def find_results(o):
    if isinstance(o, dict):
        if isinstance(o.get('results'), list):
            return o['results']
        for v in o.values():
            r = find_results(v)
            if r is not None:
                return r
    if isinstance(o, list):
        for v in o:
            r = find_results(v)
            if r is not None:
                return r
    return None


def raw_markers(stem):
    p = os.path.join(IN, stem + '.raw.txt')
    if not os.path.exists(p):
        return None
    t = open(p, encoding='utf-8').read()
    body = t.split('===', 2)[-1]
    return max(body.count('〉'), len(DIVN.findall(body)))


def main():
    wf = sys.argv[1] if len(sys.argv) > 1 else 'wf_output.json'
    results = find_results(json.load(open(wf, encoding='utf-8'))) or []
    print('=== coverage audit (%d cards) ===' % len(results))
    print('%-28s %-8s %-8s %s' % ('unit', 'raw', 'card', 'flag'))
    fails = []
    for res in results:
        k = res.get('key')
        c = res.get('card') or {}
        cs = sum(len(rec.get('senses', [])) for rec in c.get('records', []))
        rm = raw_markers(k)
        if not c:
            print('%-28s %-8s %-8s %s' % (k, '-', '0', 'NO-CARD')); fails.append(k); continue
        if not rm:
            flag = 'NO-RAW' if rm is None else 'ok (not sense-divided)'
            print('%-28s %-8s %-8d %s' % (k, 'n/a', cs, flag))
            if rm is None:
                fails.append(k)
            continue
        # absolute-difference guard: a ±1 sense gap on a tiny card is sub-sense splitting /
        # merging, not a real drop/fabrication — require a meaningful absolute gap too.
        flag = ''
        if cs < rm * LOW and (rm - cs) >= 2:
            flag = 'COVERAGE-LOW(%d/%d)' % (cs, rm)
        elif cs > rm * OVER and (cs - rm) >= 3:
            flag = 'COVERAGE-OVER(%d/%d)' % (cs, rm)
        print('%-28s %-8d %-8d %s' % (k, rm, cs, flag or 'ok'))
        if flag:
            fails.append(k)
    print('\n%s: %d/%d covered%s' % (
        'PASS' if not fails else 'FAIL', len(results) - len(fails), len(results),
        '' if not fails else ' | flagged: ' + ', '.join(fails)))
    sys.exit(0 if not fails else 1)


if __name__ == '__main__':
    main()
