#!/usr/bin/env python
"""h1691_handcheck.py — pull the NEW locus rows a text map addition produced, in
the form a human/agent actually has to read to accept or reject it.

H1670's Rāmāyaṇa false positives (one PWG tuple matching the same sarga/verse in
seven different books) were caught by reading rows, not by a summary statistic —
so a mapping is not accepted here until >=10 of its rows have been read. For each
sampled row this prints the two things the check needs side by side:

  * the PWG side — headword, sense id, the GERMAN gloss, and the sense's own
    `<ls>` strings for that abbreviation, so the claimed address can be confirmed
    to be one PWG actually cites on THAT sense (not merely somewhere in the entry);
  * the DCS side — the passage's full address, its sandhied text, and the DCS
    lemma's English meanings.

Rows are drawn from the NEW run minus the BASELINE run, so only what the mapping
actually added is inspected. Deterministic: rows are taken at a fixed stride, no
sampling and no RNG.

Usage:
  python h1691_handcheck.py --new run_h1691/... --base run_h1670/... --loci PATH
                            --text "Kirātārjunīya" [--n 10]
"""
import argparse
import collections
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))


def read_conc(path):
    rows = []
    with open(path, encoding='utf-8') as f:
        hdr = f.readline().rstrip('\n').split('\t')
        idx = {c: i for i, c in enumerate(hdr)}
        for line in f:
            p = line.rstrip('\n').split('\t')
            if len(p) < len(hdr):
                continue
            rows.append({c: p[i] for c, i in idx.items()})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--new', required=True)
    ap.add_argument('--base', required=True)
    ap.add_argument('--loci', default=os.path.join(HERE, 'pwg_sense_loci.all.tsv'))
    ap.add_argument('--text', action='append', default=[])
    ap.add_argument('--abbrev', action='append', default=[],
                    help='the PWG abbrev that maps to --text, same order')
    ap.add_argument('--n', type=int, default=10)
    ap.add_argument('--summary', action='store_true')
    a = ap.parse_args()

    base = {(r['slp1'], r['hom'], r['sense_id'], r['locus'], r['lemma'])
            for r in read_conc(a.base)}
    new = [r for r in read_conc(a.new)
           if r['method'].startswith('locus')
           and (r['slp1'], r['hom'], r['sense_id'], r['locus'],
                r['lemma']) not in base]

    by_text = collections.defaultdict(list)
    for r in new:
        by_text[r['locus'].split(',')[0].strip()].append(r)

    # PWG glosses + <ls> for the senses we will print.
    # ⚠️ A sense_id can occur on MORE THAN ONE row: PWG's Nachträge repeat a sense
    # to add to it, and `sense_loci_core.load_pwg_senses()` UNIONS their loci —
    # which is the sense the aligner actually matched against. Keeping only the
    # last row (the naive dict assignment) shows the addendum's one citation and
    # hides the main entry's, which makes a correct match read as a false
    # positive. Union here exactly as the loader does.
    wanted = {(r['slp1'], r['hom'], r['sense_id']) for r in new}
    pwg = {}
    with open(a.loci, encoding='utf-8') as f:
        hdr = f.readline().rstrip('\n').split('\t')
        idx = {c: i for i, c in enumerate(hdr)}
        for line in f:
            p = line.rstrip('\n').split('\t')
            k = (p[idx['slp1']], p[idx['hom']], p[idx['sense_id']])
            if k not in wanted:
                continue
            gloss, ls = p[idx['gloss_de']], p[idx['ls_loci']]
            cur = pwg.get(k)
            if cur is None:
                pwg[k] = [gloss, [x.strip() for x in ls.split(';') if x.strip()]]
            else:
                if gloss and gloss not in cur[0]:
                    cur[0] = (cur[0] + ' / ' + gloss) if cur[0] else gloss
                for x in (y.strip() for y in ls.split(';')):
                    if x and x not in cur[1]:
                        cur[1].append(x)

    if a.summary:
        # Mechanical half of the check, over EVERY new row rather than a sample:
        # does the DCS address the row claims actually appear as an <ls> on that
        # very sense? This is the property H1670's Rāmāyaṇa false positives
        # violated, so a text scoring below 100% here needs its misses read.
        print('%-30s %7s %7s %7s' % ('DCS text', 'rows', 'cited', 'pct'))
        for t in sorted(by_text, key=lambda x: -len(by_text[x])):
            rows = by_text[t]
            ok = 0
            for r in rows:
                k = (r['slp1'], r['hom'], r['sense_id'])
                _g, ls = pwg.get(k, ('', []))
                tail = ','.join(x.strip() for x in r['locus'].split(',')[2:])
                tail = tail.replace(' ', '')
                for x in ls:
                    d = ''.join(ch for ch in x if ch.isdigit() or ch == ',').strip(',')
                    if d == tail:
                        ok += 1
                        break
            print('%-30s %7d %7d %6.1f%%'
                  % (t[:30], len(rows), ok, 100.0 * ok / len(rows)))
        return

    texts = a.text or sorted(by_text, key=lambda t: -len(by_text[t]))
    abbr = dict(zip(a.text, a.abbrev)) if a.abbrev else {}
    print('NEW locus rows over baseline: %d, across %d texts\n' % (len(new), len(by_text)))
    for t in texts:
        rows = by_text.get(t, [])
        print('=' * 78)
        print('%s — %d new locus rows' % (t, len(rows)))
        print('=' * 78)
        if not rows:
            continue
        step = max(1, len(rows) // a.n)
        for r in rows[::step][:a.n]:
            k = (r['slp1'], r['hom'], r['sense_id'])
            gloss_de, ls = pwg.get(k, ('', []))
            ab = abbr.get(t)
            # the address the aligner claims, as PWG would write it
            tail = ','.join(x.strip() for x in r['locus'].split(',')[2:])
            hits = [x for x in ls
                    if ab and x.upper().rstrip('.').startswith(ab.upper())
                    and ''.join(ch for ch in x if ch.isdigit() or ch == ',')
                        .strip(',') == tail.replace(' ', '')]
            print('- %s (hom %s) sense %s   [%s, conf %s]  %s'
                  % (r['slp1'], r['hom'] or '-', r['sense_id'], r['method'],
                     r['conf'], 'CITED-ON-SENSE ✓' if hits else 'ls-match: see list'))
            print('    PWG gloss : %s' % gloss_de[:150])
            print('    PWG <ls>  : %s' % '; '.join(ls[:14]))
            print('    DCS locus : %s' % r['locus'])
            print('    DCS sent  : %s' % r['sent'][:150])
            print('    DCS gloss : %s' % r['gloss'][:130])
            print()


if __name__ == '__main__':
    main()
