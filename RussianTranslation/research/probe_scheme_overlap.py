#!/usr/bin/env python
"""probe_scheme_overlap.py — H1691 scheme-correspondence test.

Given a candidate pair (PWG abbrev, DCS text), answer ONE question with a number:
**do PWG's citation tuples land on addresses that exist in that DCS text?**

If the two numbering schemes correspond, the addresses PWG cites should mostly
exist on the DCS side; if PWG cites pages, a different recension, or a different
work, they mostly should not. The test therefore separates the four H1670
rejection classes from a real crosswalk without relaxing anything the aligner
does — it reuses `numeric_address()` and the same digits-only PWG tuple that
`wanted_addresses()` builds, and it decides nothing on its own.

Reported per pair:

  arity_match   share of PWG tuples whose LENGTH equals a DCS address length
                that text actually produces (a 2-tuple against a 3-component
                DCS address can never satisfy verse_equal())
  hit_verse     share of PWG tuples present in the text's verse-level address set
  hit_chapter   share present only at chapter level (weaker corroboration)
  ceiling       hit_verse expressed in citations, not distinct tuples — the most
                grounded senses this mapping could possibly add

A high hit rate is evidence of scheme correspondence, NOT of sense identity: the
passage must still instantiate the gloss, which is the hand-check step and cannot
be automated. A low rate is decisive the other way — if the addresses do not even
exist, no amount of matching will find them.

Usage:
  python probe_scheme_overlap.py --loci PATH --pair "KIR=Kirātārjunīya" [--pair ...]
  python probe_scheme_overlap.py --loci PATH --verdicts pwg_ls_dcs_scheme_verdicts.tsv
"""
import argparse
import collections
import csv
import json
import os
import re
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
_NUM = re.compile(r'\d+')


def find_up(*rel):
    d = HERE
    for _ in range(6):
        d = os.path.dirname(d)
        for base in (d, os.path.join(d, 'GitHub')):
            p = os.path.join(base, *rel)
            if os.path.exists(p):
                return p
    return None


def dcs_address_sets(con, name):
    """-> (verse_addrs, chapter_addrs, n_abstained) using the aligner's own
    numeric_address() rule, so what this counts is exactly what the locus tier
    could ever see."""
    tid = con.execute('SELECT text_id FROM text WHERE name=?', (name,)).fetchone()
    if not tid:
        return None
    verse, chap, abstain = set(), set(), 0
    for ref, cnt in con.execute("""
            SELECT c.ref, s.sent_counter FROM sentence s
            JOIN chapter c ON c.chapter_id=s.chapter_id WHERE c.text_id=?""",
            (tid[0],)):
        parts = [p.strip() for p in (ref or '').split(',')]
        if any(not p.isdigit() for p in parts[1:]):
            abstain += 1
            continue
        nums = [int(p) for p in parts[1:]]
        c = str(cnt).strip() if cnt is not None else ''
        if c.isdigit():
            verse.add(tuple(nums + [int(c)]))
        chap.add(tuple(nums))
    return verse, chap, abstain


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--loci', default=os.path.join(HERE, 'pwg_sense_loci.all.tsv'))
    ap.add_argument('--kosha', default=None)
    ap.add_argument('--dcs', default=None)
    ap.add_argument('--pair', action='append', default=[],
                    help='ABBREV=DCS Text Name')
    ap.add_argument('--verdicts', default=None,
                    help='TSV with pwg_abbrev + dcs_text_true columns')
    ap.add_argument('--rank', action='store_true',
                    help='rank the candidate against EVERY DCS text (confound-free)')
    ap.add_argument('--null', type=int, default=0, metavar='N',
                    help='also test each abbrev against the N largest DCS texts it '
                         'is NOT paired with — the accidental-collision floor a real '
                         'correspondence has to clear')
    ap.add_argument('--out', default=os.path.join(HERE, 'h1691_scheme_overlap.json'))
    a = ap.parse_args()

    kosha = a.kosha or find_up('kosha')
    sys.path.insert(0, os.path.join(kosha, 'scripts'))
    import sense_loci_core as slc

    pairs = []
    for p in a.pair:
        ab, _, tx = p.partition('=')
        pairs.append((ab.upper().strip().rstrip('.'), tx.strip()))
    if a.verdicts:
        with open(a.verdicts, encoding='utf-8', newline='') as fh:
            for r in csv.DictReader(fh, delimiter='\t'):
                tx = (r.get('dcs_text_true') or '').strip()
                if tx and tx.lower() not in ('', 'none', '-'):
                    pairs.append((r['pwg_abbrev'], tx))
    pairs = list(dict.fromkeys(pairs))
    want = {ab for ab, _ in pairs}

    # PWG side — one streaming pass
    tuples = collections.defaultdict(collections.Counter)
    with open(a.loci, encoding='utf-8') as f:
        hdr = f.readline().rstrip('\n').split('\t')
        idx = {c: i for i, c in enumerate(hdr)}
        for line in f:
            p = line.rstrip('\n').split('\t')
            if len(p) <= idx['ls_loci']:
                continue
            for raw in p[idx['ls_loci']].split(';'):
                raw = raw.strip()
                if not raw:
                    continue
                ab, loc = slc.split_ls(raw)
                key = (ab or '').upper().strip().rstrip('.')
                if key in want:
                    tuples[key][tuple(int(x) for x in _NUM.findall(loc))] += 1

    dcs = a.dcs or find_up('VisualDCS', 'src', 'DCS-data-2026', 'dcs_full.sqlite')
    con = sqlite3.connect('file:%s?mode=ro' % dcs.replace('\\', '/'), uri=True)
    cache, out = {}, []
    for ab, tx in pairs:
        if tx not in cache:
            cache[tx] = dcs_address_sets(con, tx)
        got = cache[tx]
        if got is None:
            print('%-20s -> %-32s  TEXT NOT IN DCS' % (ab, tx))
            continue
        verse, chap, abstain = got
        tc = tuples.get(ab, collections.Counter())
        distinct = [t for t in tc if t]
        n_cit = sum(tc[t] for t in distinct)
        dcs_arities = {len(t) for t in verse} | {len(t) for t in chap}
        arity_ok = [t for t in distinct if len(t) in dcs_arities]
        hitv = [t for t in distinct if t in verse]
        hitc = [t for t in distinct if t not in verse and t in chap]
        cit_v = sum(tc[t] for t in hitv)
        row = {
            'pwg_abbrev': ab, 'dcs_text': tx,
            'pwg_citations': n_cit, 'pwg_distinct_tuples': len(distinct),
            'pwg_arity_hist': collections.Counter(len(t) for t in distinct).most_common(4),
            'dcs_arities': sorted(dcs_arities),
            'dcs_verse_addrs': len(verse), 'dcs_chapter_addrs': len(chap),
            'dcs_sentences_abstained': abstain,
            'arity_match_pct': round(100.0 * len(arity_ok) / len(distinct), 1) if distinct else 0.0,
            'hit_verse_pct': round(100.0 * len(hitv) / len(distinct), 1) if distinct else 0.0,
            'hit_chapter_pct': round(100.0 * len(hitc) / len(distinct), 1) if distinct else 0.0,
            'ceiling_citations_at_verse': cit_v,
            'ceiling_citation_pct': round(100.0 * cit_v / n_cit, 1) if n_cit else 0.0,
        }
        out.append(row)
        print('%-20s -> %-30s  n=%-6d arity %5.1f%%  verse %5.1f%%  chap %5.1f%%  '
              'ceiling %d cit (%.1f%%)'
              % (ab, tx[:30], len(distinct), row['arity_match_pct'],
                 row['hit_verse_pct'], row['hit_chapter_pct'],
                 cit_v, row['ceiling_citation_pct']))

    # ---- competitive rank -------------------------------------------------- #
    # The plain hit rate is confounded by address-space SIZE: a 2-tuple like
    # (5,25) exists in almost any large text, so "the address exists" is cheap
    # evidence against the Mahābhārata and expensive against an 18-sarga poem.
    # The confound-free question is competitive: of all 270 DCS texts, is the
    # candidate the one that best explains THESE tuples? A correct crosswalk
    # ranks at or near the top; a name-match coincidence does not.
    if a.rank:
        alltexts = [r[0] for r in con.execute('SELECT name FROM text ORDER BY name')]
        print('\n--- competitive rank among all %d DCS texts ---' % len(alltexts))
        for row in out:
            ab = row['pwg_abbrev']
            tc = tuples.get(ab, collections.Counter())
            distinct = [t for t in tc if t]
            if not distinct:
                continue
            board = []
            for nm in alltexts:
                if nm not in cache:
                    cache[nm] = dcs_address_sets(con, nm)
                v, _c, _a2 = cache[nm]
                if not v:
                    continue
                board.append((100.0 * sum(1 for t in distinct if t in v) / len(distinct), nm))
            board.sort(reverse=True)
            pos = next((i + 1 for i, (_s, nm) in enumerate(board)
                        if nm == row['dcs_text']), None)
            row['rank_of_candidate'] = pos
            row['rank_field'] = len(board)
            row['top3'] = [{'text': nm, 'hit_pct': round(s, 1)} for s, nm in board[:3]]
            print('%-20s -> %-28s rank %3s/%d   top: %s'
                  % (ab, row['dcs_text'][:28], pos, len(board),
                     ', '.join('%s %.0f%%' % (nm[:22], s) for s, nm in board[:3])))

    # ---- null model ------------------------------------------------------- #
    # A hit rate only means something against the rate the SAME PWG tuples get
    # on a text they demonstrably do not cite. Nothing is calibrated by hand:
    # the floor is measured, per abbrev, on the largest unrelated DCS texts.
    if a.null:
        big = [r[0] for r in con.execute("""
            SELECT x.name FROM text x JOIN chapter c ON c.text_id=x.text_id
            JOIN sentence s ON s.chapter_id=c.chapter_id
            GROUP BY x.name ORDER BY COUNT(*) DESC LIMIT ?""", (a.null + 6,))]
        print('\n--- null model: same tuples vs unrelated texts ---')
        for row in out:
            ab = row['pwg_abbrev']
            tc = tuples.get(ab, collections.Counter())
            distinct = [t for t in tc if t]
            if not distinct:
                continue
            rates = []
            for nm in big:
                if nm == row['dcs_text'] or len(rates) >= a.null:
                    continue
                if nm not in cache:
                    cache[nm] = dcs_address_sets(con, nm)
                v, _c, _ab2 = cache[nm]
                rates.append(100.0 * sum(1 for t in distinct if t in v) / len(distinct))
            row['null_max_pct'] = round(max(rates), 1) if rates else None
            row['null_mean_pct'] = round(sum(rates) / len(rates), 1) if rates else None
            row['signal_over_null'] = (round(row['hit_verse_pct'] / row['null_max_pct'], 1)
                                       if row.get('null_max_pct') else None)
            print('%-20s -> %-30s verse %5.1f%%  null max %5.1f%% mean %5.1f%%  x%s'
                  % (ab, row['dcs_text'][:30], row['hit_verse_pct'],
                     row['null_max_pct'], row['null_mean_pct'],
                     row['signal_over_null']))
    con.close()
    with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print('\nwrote %s (%d pairs)' % (a.out, len(out)), file=sys.stderr)


if __name__ == '__main__':
    main()
