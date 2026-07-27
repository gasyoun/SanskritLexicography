#!/usr/bin/env python
"""probe_dcs_text_scheme.py — H1691 evidence collector (DCS side).

For each candidate DCS text named on a `DCS-HAS-UNMAPPED` row of
[`pwg_ls_dcs_text_crosswalk_backlog.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/pwg_ls_dcs_text_crosswalk_backlog.tsv),
dump the shape of its citation address so it can be compared against PWG's:

  * `chapter.ref` — how many components, whether any is a NAMED (non-numeric)
    section (the `numeric_address()` abstention condition H1670 introduced), and
    the observed range of the leading component;
  * `sentence.sent_counter` — presence rate and numeric range, i.e. whether the
    address bottoms out at a verse or only at a chapter.

This is EVIDENCE ONLY. It emits no verdict and maps nothing: the DCS shape is one
of the two sources a scheme verdict needs, the other being PWG's own `pwgbib`
entry plus sampled real `<ls>` strings (`probe_pwg_ls_scheme.py`). A name match
is not a crosswalk — see the H1670 rejections recorded in `PWG_TO_DCS_TEXT`.

Usage:
  python probe_dcs_text_scheme.py [--backlog PATH] [--dcs PATH]
                                  [--min-share 0.05] [--text NAME]...
                                  [--out PATH]
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


def ref_shape(ref):
    """'Rām, Bā, 6' -> 'SIGLUM|named|num'; the coarse pattern a crosswalk must match."""
    parts = [p.strip() for p in (ref or '').split(',')]
    out = []
    for i, p in enumerate(parts):
        if i == 0:
            out.append('SIGLUM')
        elif p.isdigit():
            out.append('num')
        elif not p:
            out.append('empty')
        else:
            out.append('named')
    return '|'.join(out)


def profile(con, name):
    tid = con.execute('SELECT text_id FROM text WHERE name=?', (name,)).fetchone()
    if not tid:
        return None
    tid = tid[0]
    chapters = con.execute(
        'SELECT chapter_id, ref FROM chapter WHERE text_id=?', (tid,)).fetchall()
    shapes = collections.Counter(ref_shape(r) for _c, r in chapters)
    lead, second = [], []
    for _c, r in chapters:
        parts = [p.strip() for p in (r or '').split(',')]
        if len(parts) > 1 and parts[1].isdigit():
            lead.append(int(parts[1]))
        if len(parts) > 2 and parts[2].isdigit():
            second.append(int(parts[2]))
    n_sent, n_counter = con.execute("""
        SELECT COUNT(*), SUM(CASE WHEN s.sent_counter IS NOT NULL
                                   AND TRIM(s.sent_counter)<>'' THEN 1 ELSE 0 END)
        FROM sentence s JOIN chapter c ON c.chapter_id=s.chapter_id
        WHERE c.text_id=?""", (tid,)).fetchone()
    counters = [r[0] for r in con.execute("""
        SELECT s.sent_counter FROM sentence s JOIN chapter c
        ON c.chapter_id=s.chapter_id WHERE c.text_id=? AND s.sent_counter<>''
        LIMIT 4000""", (tid,))]
    cnum = [int(_NUM.search(x).group(0)) for x in counters if x and _NUM.search(x)]
    tok = con.execute("""SELECT COUNT(*) FROM token t JOIN sentence s
        ON s.id=t.sentence_id JOIN chapter c ON c.chapter_id=s.chapter_id
        WHERE c.text_id=?""", (tid,)).fetchone()[0]
    return {
        'dcs_text': name,
        'tokens': tok,
        'chapters': len(chapters),
        'ref_shapes': shapes.most_common(6),
        'has_named_section': any('named' in s for s in shapes),
        'lead_min': min(lead) if lead else None,
        'lead_max': max(lead) if lead else None,
        'lead_distinct': len(set(lead)),
        'second_max': max(second) if second else None,
        'sentences': n_sent,
        'sent_counter_pct': round(100.0 * (n_counter or 0) / n_sent, 1) if n_sent else 0.0,
        'counter_max_sampled': max(cnum) if cnum else None,
        'sample_refs': [r for _c, r in chapters[:6]],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--backlog', default=os.path.join(
        HERE, 'pwg_ls_dcs_text_crosswalk_backlog.tsv'))
    ap.add_argument('--dcs', default=None)
    ap.add_argument('--min-share', type=float, default=0.05)
    ap.add_argument('--text', action='append', default=[],
                    help='profile these DCS texts instead of the backlog')
    ap.add_argument('--out', default=os.path.join(HERE, 'h1691_dcs_scheme_profiles.json'))
    a = ap.parse_args()

    dcs = a.dcs or find_up('VisualDCS', 'src', 'DCS-data-2026', 'dcs_full.sqlite')
    con = sqlite3.connect('file:%s?mode=ro' % dcs.replace('\\', '/'), uri=True)

    if a.text:
        names = list(dict.fromkeys(a.text))
    else:
        names = []
        with open(a.backlog, encoding='utf-8', newline='') as fh:
            for r in csv.DictReader(fh, delimiter='\t'):
                if (r['status'] == 'DCS-HAS-UNMAPPED'
                        and float(r['share_pct']) >= a.min_share
                        and r['dcs_text'] and r['dcs_text'] not in names):
                    names.append(r['dcs_text'])

    out = {}
    for nm in names:
        p = profile(con, nm)
        if p is None:
            print('NOT IN DCS: %s' % nm, file=sys.stderr)
            continue
        out[nm] = p
        print('%-34s %7s tok %5d ch  lead<=%-5s ctr %5.1f%% (max %-5s) %s'
              % (nm[:34], format(p['tokens'], ','), p['chapters'],
                 p['lead_max'], p['sent_counter_pct'], p['counter_max_sampled'],
                 'NAMED-SECTION' if p['has_named_section'] else ''))
    con.close()
    with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=True)
    print('wrote %s (%d texts)' % (a.out, len(out)), file=sys.stderr)


if __name__ == '__main__':
    main()
