#!/usr/bin/env python
"""annotation_report.py — query everything known about a pwg_ru lemma / subcard / sense.

The single query surface over the annotated store (H335 W2). It reads the store and
its in-store annotations only; it degrades gracefully on any absent optional field
(evidence not yet retrofitted, no renou/government/genre, etc.). H338 (government) and
H339 (genre) fold their queries into this CLI, so new lanes print automatically as
they populate.

  python annotation_report.py <selector>
        Print every field on the matching store row(s): translation (ru / de / layer /
        equivalence_type / source_type / stratum / differentia), government, renou /
        renou_oldest, genre / dcs_freq (when present), provenance, and the evidence
        lanes (per-sense evidence[] + the lemma's evidence_summary).
        <selector> = <key1>[~~subcard][#sense_tag]; a bare key1 matches by key1, a
        longer string matches the subcard exactly or as a prefix, #tag filters the sense.

  python annotation_report.py --by-source grin12 [--relation supports|provides]
        Every sense whose evidence[] carries that source (optionally that relation) —
        answers MG's literal question "which senses did Grintser (grin12/grin3) /
        Kossovich (kow) support/provide?".

  python annotation_report.py --source-summary
        Per-source provides / supports / contradicts / silent / present tallies over
        the whole store (the same table annotate_evidence.py prints after a backfill).

  python annotation_report.py --silent-for <key1>
        The lemma-level evidence_summary for one lemma: which authorities are silent /
        contradict / corroborate it.
"""
import argparse, json, os, sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
STORE = os.path.join(HERE, 'pwg_ru_translated.jsonl')

RU_SOURCES = ['koch', 'kna', 'fri', 'smirnov', 'kow', 'grin12', 'grin3']
NONRU_LANES = ['apte_hi', 'vedic_rituals_hi', 'kosha_syn', 'meulenbeld', 'corpus']


def load_rows(store):
    if not os.path.exists(store):
        sys.stderr.write('store not found: %s (it is gitignored — regenerate via the bridge)\n' % store)
        raise SystemExit(2)
    rows = []
    with open(store, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def parse_selector(sel):
    tag = None
    if '#' in sel:
        sel, tag = sel.split('#', 1)
    return sel, tag


def row_matches(row, sel, tag):
    if tag is not None and (row.get('sense_tag') or '') != tag:
        return False
    sub = row.get('subcard') or ''
    return row.get('key1') == sel or sub == sel or sub.startswith(sel)


def _line(label, value):
    if value in (None, '', [], {}):
        return
    print('  %-16s %s' % (label + ':', value))


def print_row(row):
    print('── %s  %s  [%s]  sense %s ─────────────'
          % (row.get('key1'), row.get('subcard'), row.get('layer') or '?', row.get('sense_tag')))
    _line('iast', row.get('iast'))
    _line('h', row.get('h'))
    _line('ru', row.get('ru'))
    _line('de', row.get('de'))
    _line('equivalence', row.get('equivalence_type'))
    _line('source_type', row.get('source_type'))
    _line('stratum', row.get('stratum'))
    _line('differentia', row.get('differentia'))
    _line('government', row.get('government'))          # H338 (folds in when populated)
    _line('renou', row.get('renou'))
    _line('renou_oldest', row.get('renou_oldest'))
    _line('genre', row.get('genre'))                    # H339 (folds in when populated)
    if row.get('dcs_freq'):
        f = row['dcs_freq']
        _line('dcs_freq', 'band %s · genre %s · era %s' % (f.get('band'), f.get('genre'), f.get('era')))
    _line('review_status', row.get('review_status'))
    prov = row.get('provenance') or {}
    _line('model', prov.get('model_version') or prov.get('model'))

    ev = row.get('evidence')
    if ev is None:
        print('  evidence:        (not retrofitted — run annotate_evidence.py)')
    elif not ev:
        print('  evidence:        (none supports/provides this sense)')
    else:
        print('  evidence:')
        for e in ev:
            print('    [%s] %-9s %s' % (e.get('source'), e.get('relation'), (e.get('gloss_ref') or '')[:120]))
    summ = row.get('evidence_summary')
    if summ:
        present = ', '.join(p['source'] for p in summ.get('present') or [])
        print('  lemma evidence:  supports=%s | contradicts=%s | present=%s | silent=%s'
              % (','.join(summ.get('supports_senses') or []) or '-',
                 ','.join(summ.get('contradicts') or []) or '-',
                 present or '-', ','.join(summ.get('silent') or []) or '-'))


def cmd_lookup(rows, sel):
    key, tag = parse_selector(sel)
    hits = [r for r in rows if row_matches(r, key, tag)]
    if not hits:
        print('no store row matches %r' % sel)
        return
    for r in hits:
        print_row(r)
    print('\n%d matching sense row(s).' % len(hits))


def cmd_by_source(rows, source, relation):
    n = 0
    for r in rows:
        for e in r.get('evidence') or []:
            if e.get('source') != source:
                continue
            if relation and e.get('relation') != relation:
                continue
            n += 1
            print('%s  %s  #%s  [%s]  %s'
                  % (r.get('key1'), r.get('subcard'), r.get('sense_tag'),
                     e.get('relation'), (r.get('ru') or '')[:70]))
    rel = (' with relation=%s' % relation) if relation else ''
    print('\n%d sense(s) where %s appears in evidence%s.' % (n, source, rel))


def cmd_source_summary(rows):
    tally = {c: Counter() for c in RU_SOURCES + NONRU_LANES}
    seen_lemma = {}                                     # key1 -> summary (count each lemma once)
    for r in rows:
        for e in r.get('evidence') or []:
            src, rel = e.get('source'), e.get('relation')
            if src in tally and rel in ('provides', 'supports'):
                tally[src][rel] += 1
        summ = r.get('evidence_summary')
        k = r.get('key1')
        if summ and k not in seen_lemma:
            seen_lemma[k] = summ
    for summ in seen_lemma.values():
        for c in summ.get('contradicts') or []:
            tally.get(c, Counter())['contradicts'] += 1
        for c in summ.get('silent') or []:
            tally.get(c, Counter())['silent'] += 1
        for p in summ.get('present') or []:
            tally.get(p['source'], Counter())['present'] += 1
    print('store rows: %d | lemmas with a summary: %d' % (len(rows), len(seen_lemma)))
    print('  %-18s %8s %8s %11s %8s %8s' % ('source', 'provides', 'supports', 'contradicts', 'silent', 'present'))
    for code in RU_SOURCES + NONRU_LANES:
        t = tally[code]
        print('  %-18s %8d %8d %11d %8d %8d'
              % (code, t['provides'], t['supports'], t['contradicts'], t['silent'], t['present']))


def cmd_silent_for(rows, key1):
    summ = next((r.get('evidence_summary') for r in rows
                 if r.get('key1') == key1 and r.get('evidence_summary')), None)
    if not summ:
        print('no evidence_summary for %r (not retrofitted, or lemma absent)' % key1)
        return
    print('lemma %s evidence_summary:' % key1)
    print('  supports (>=1 sense): %s' % (', '.join(summ.get('supports_senses') or []) or '-'))
    print('  contradicts        : %s' % (', '.join(summ.get('contradicts') or []) or '-'))
    print('  present (corrob.)  : %s' % (', '.join(p['source'] for p in summ.get('present') or []) or '-'))
    print('  silent             : %s' % (', '.join(summ.get('silent') or []) or '-'))
    print('  evidence_status    : %s | corpus_status: %s'
          % (summ.get('evidence_status'), summ.get('corpus_status')))


def main():
    ap = argparse.ArgumentParser(description='Query the annotated pwg_ru store.')
    ap.add_argument('selector', nargs='?', help='<key1>[~~subcard][#sense_tag]')
    ap.add_argument('--store', default=STORE)
    ap.add_argument('--by-source', help='source code (koch/kna/fri/smirnov/kow/grin12/grin3)')
    ap.add_argument('--relation', choices=['provides', 'supports'])
    ap.add_argument('--source-summary', action='store_true')
    ap.add_argument('--silent-for', help='key1 whose lemma evidence_summary to print')
    args = ap.parse_args()

    rows = load_rows(args.store)
    if args.source_summary:
        return cmd_source_summary(rows)
    if args.silent_for:
        return cmd_silent_for(rows, args.silent_for)
    if args.by_source:
        return cmd_by_source(rows, args.by_source, args.relation)
    if args.selector:
        return cmd_lookup(rows, args.selector)
    ap.print_help()


if __name__ == '__main__':
    main()
