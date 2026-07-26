#!/usr/bin/env python
"""probe_pwg_ls_scheme.py — H1691 evidence collector (PWG side).

The twin of `probe_dcs_text_scheme.py`. For each `<ls>` source abbreviation it is
asked about, print the two things a scheme verdict needs from PWG:

  1. the FULL `pwgbib` entry — PWG's own Verzeichniss der Abkürzungen states the
     citation scheme in prose ("Es wird nach Maṇḍala, Sūkta und Ṛc citirt",
     "citirt nach Band, Seite und Zeile", "Es wird die WILSON'sche Uebersetzung
     citirt") and is the primary evidence;
  2. a sample of REAL `<ls>` locus strings drawn from the dictionary, with the
     observed component-count histogram and each component's range — which is
     what actually catches a prose entry that the dictionary does not follow, or
     an abbrev whose bib entry is missing entirely.

Emits no verdict; the adjudication is deliberately not automated (H1691, and the
four H1670 rejections that a name match would have accepted).

Usage:
  python probe_pwg_ls_scheme.py --loci pwg_sense_loci.all.tsv ABBREV [ABBREV...]
  python probe_pwg_ls_scheme.py --loci PATH --from-backlog [--min-share 0.05]
"""
import argparse
import collections
import csv
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, '..', 'src'))
sys.path.insert(0, SRC)

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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('abbrevs', nargs='*')
    ap.add_argument('--loci', default=os.path.join(HERE, 'pwg_sense_loci.all.tsv'))
    ap.add_argument('--kosha', default=None)
    ap.add_argument('--from-backlog', action='store_true')
    ap.add_argument('--backlog', default=os.path.join(
        HERE, 'pwg_ls_dcs_text_crosswalk_backlog.tsv'))
    ap.add_argument('--min-share', type=float, default=0.05)
    ap.add_argument('--sample', type=int, default=20)
    ap.add_argument('--out', default=os.path.join(HERE, 'h1691_pwg_ls_profiles.json'))
    a = ap.parse_args()

    kosha = a.kosha or find_up('kosha')
    sys.path.insert(0, os.path.join(kosha, 'scripts'))
    import sense_loci_core as slc
    import pwg_sources

    wanted = list(dict.fromkeys(x.upper().strip().rstrip('.') for x in a.abbrevs))
    if a.from_backlog:
        with open(a.backlog, encoding='utf-8', newline='') as fh:
            for r in csv.DictReader(fh, delimiter='\t'):
                if (r['status'] == 'DCS-HAS-UNMAPPED'
                        and float(r['share_pct']) >= a.min_share
                        and r['pwg_abbrev'] not in wanted):
                    wanted.append(r['pwg_abbrev'])
    want = set(wanted)

    # one streaming pass over every leaf-sense row
    samples = collections.defaultdict(list)
    counts = collections.Counter()
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
                if key not in want:
                    continue
                counts[key] += 1
                if len(samples[key]) < 4000:
                    samples[key].append((p[idx['slp1']], raw, loc))

    bib = pwg_sources.bib()
    out = {}
    for ab in wanted:
        rows = samples.get(ab, [])
        # component profile: every locus split on ',' -> numeric parts
        ncomp = collections.Counter()
        comp_max = collections.defaultdict(int)
        nonnum = collections.Counter()
        for _hw, _raw, loc in rows:
            parts = [x.strip() for x in loc.split(',') if x.strip()]
            ncomp[len(parts)] += 1
            for i, x in enumerate(parts):
                m = _NUM.search(x)
                if m:
                    comp_max[i] = max(comp_max[i], int(m.group(0)))
                if not x.replace('.', '').isdigit():
                    nonnum[x if len(x) < 14 else x[:14]] += 1
        entry = bib.get(ab) or bib.get(ab + '.') or pwg_sources.resolve(ab)
        step = max(1, len(rows) // a.sample) if rows else 1
        out[ab] = {
            'pwg_abbrev': ab,
            'citations_in_loci': counts.get(ab, 0),
            'pwgbib_entry': entry,
            'ncomp_hist': ncomp.most_common(6),
            'comp_max': {str(k): v for k, v in sorted(comp_max.items())},
            'nonnumeric_components': nonnum.most_common(8),
            'sample': [{'headword': h, 'ls': r} for h, r, _l in rows[::step][:a.sample]],
        }
        print('=' * 78)
        print('%s   %d citations' % (ab, counts.get(ab, 0)))
        print('  pwgbib: %s' % (entry if entry else '(NOT IN pwgbib)'))
        print('  components: %s   max per component: %s'
              % (ncomp.most_common(4), dict(sorted(comp_max.items()))))
        if nonnum:
            print('  non-numeric parts: %s' % nonnum.most_common(6))
        for h, r, _l in rows[::step][:a.sample]:
            print('    %-18s %s' % (h, r))
    with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=True)
    print('\nwrote %s (%d abbrevs)' % (a.out, len(out)), file=sys.stderr)


if __name__ == '__main__':
    main()
