#!/usr/bin/env python
"""build_ls_text_crosswalk_backlog.py — H1670 Lever B.

Ranks every PWG `<ls>` source abbreviation by citation mass and says, for each,
whether the corpus side even exists:

  MAPPED            the aligner's PWG_TO_DCS_TEXT already points it at a DCS text
  DCS-HAS-UNMAPPED  DCS carries a text of that name, but no mapping exists — so
                    every citation is invisible to the locus tier for want of one
                    dictionary line, not for want of data
  DCS-LACKS         no DCS text plausibly matches — a genuine corpus gap that no
                    crosswalk can close

The middle class is the actionable backlog and the reason this script is
committed rather than run once: it is the work queue for
[H1691](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1691-Opus_kosha_pwg-dcs-text-crosswalk-beyond-five_26.07.26.md).

A name match is a CANDIDATE, never a crosswalk. `VP` resolves to Viṣṇupurāṇa and
DCS carries a Viṣṇupurāṇa, yet PWG cites Wilson's *translation* by page; `KĀTY.
ŚR` is Kātyāyana's Śrautasūtra, while DCS's look-alike is his *smṛti* — a
different work. So the output carries a `scheme_verified` column that only a
human/agent pass over the pwgbib entry may set, and the aligner maps nothing on
name resemblance alone.

⚠️ H1691 — the auto-generated candidate is WRONG IN BOTH DIRECTIONS, and neither
class may be quoted as a fact about the corpus:

  * false candidate — `candidates()` returns any name-alike and then picks the
    one with the MOST TOKENS, so `SĀṂKHYAK` was paired with the Sāṃkhyakārikā
    *bhāṣya* while DCS also carries the bare kārikā, and five abbreviations
    (TBR, ĀŚV. ŚR, ŚĀṄKH. BR, ŚĀṄKH. GṚHY, TAITT. ĀR/UP) were paired with a
    DIFFERENT WORK whose right one DCS also carries;
  * false `DCS-LACKS` — the match is computed on the resolved pwgbib entry,
    which is GERMAN PROSE. PWG names Pāṇini and Manu by author and language
    ("PĀṆINI'S acht Bücher grammatischer Regeln", "MANU'S Gesetzbuch"), never by
    Sanskrit title, so 21,305 + 20,605 citations — the two largest crosswalk
    wins in the dictionary — sat in the class labelled "a genuine corpus gap
    that no crosswalk can close".

So `dcs_text` is a HINT for a human pass, never an answer, and `DCS-LACKS` means
"no name-alike was found", not "DCS does not carry it". The adjudicated truth
lives in `pwg_ls_dcs_scheme_verdicts.tsv`, which this script now reads back: its
`dcs_text_true` overrides the guess and its `verdict` fills `scheme_verified`, so
regenerating the backlog never silently discards a verdict that was paid for.

Usage:
  python build_ls_text_crosswalk_backlog.py --loci PATH [--frame PATH] [--out PATH]
                                            [--verdicts PATH]
"""
import argparse
import collections
import os
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))


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
    ap.add_argument('--loci', required=True, help='pwg_sense_loci.all.tsv')
    ap.add_argument('--frame', default=None,
                    help='restrict to a frame file (default: every headword)')
    ap.add_argument('--dcs', default=None)
    ap.add_argument('--kosha', default=None)
    ap.add_argument('--out', default=os.path.join(
        HERE, 'pwg_ls_dcs_text_crosswalk_backlog.tsv'))
    ap.add_argument('--verdicts', default=os.path.join(
        HERE, 'pwg_ls_dcs_scheme_verdicts.tsv'),
        help='H1691 adjudications; overrides the auto-generated candidate')
    a = ap.parse_args()

    kosha = a.kosha or find_up('kosha')
    sys.path.insert(0, os.path.join(kosha, 'scripts'))
    import sense_loci_core as slc
    from build_sense_corpus_concordance import PWG_TO_DCS_TEXT

    wanted = None
    if a.frame:
        wanted = set()
        with open(a.frame, encoding='utf-8') as f:
            hdr = f.readline().rstrip('\n').split('\t')
            idx = {c: i for i, c in enumerate(hdr)}
            for line in f:
                p = line.rstrip('\n').split('\t')
                wanted.add((p[idx['slp1']], p[idx['hom']]))

    groups = slc.load_pwg_senses(a.loci)
    n = collections.Counter()
    for key, senses in groups.items():
        if wanted is not None and key not in wanted:
            continue
        for s in slc.leaves(senses):
            for raw in s.ls_raw:
                ab, _loc = slc.split_ls(raw)
                n[(ab or '').upper().strip().rstrip('.')] += 1
    total = sum(n.values())

    dcs = a.dcs or find_up('VisualDCS', 'src', 'DCS-data-2026', 'dcs_full.sqlite')
    con = sqlite3.connect(dcs)
    texts = [r[0] for r in con.execute('SELECT name FROM text')]
    tok = dict(con.execute("""SELECT x.name, COUNT(*) FROM token t
        JOIN sentence s ON s.id=t.sentence_id
        JOIN chapter c ON c.chapter_id=s.chapter_id
        JOIN text x ON x.text_id=c.text_id GROUP BY x.name"""))
    # a DCS text is tuple-comparable iff no chapter ref carries a NAMED section
    # (H1670 numeric_address); a named book collapses distinct passages together.
    unsafe = set()
    for name, ref in con.execute("""SELECT x.name, c.ref FROM chapter c
            JOIN text x ON x.text_id=c.text_id"""):
        for part in [p.strip() for p in (ref or '').split(',')[1:]]:
            if part and not part.isdigit():
                unsafe.add(name)
                break
    con.close()

    def candidates(source_name):
        if not source_name:
            return []
        base = source_name.split('(')[0].split(',')[0].strip().lower()
        if len(base) < 5:
            return []
        return [t for t in texts
                if t.lower().startswith(base[:7]) or base.startswith(t.lower()[:7])]

    # H1691 adjudications, if present: they carry the TRUE DCS text and the
    # verdict, and must survive a regeneration of this file.
    verdicts = {}
    if a.verdicts and os.path.exists(a.verdicts):
        import csv as _csv
        with open(a.verdicts, encoding='utf-8', newline='') as fh:
            for r in _csv.DictReader(fh, delimiter='\t'):
                verdicts[r['pwg_abbrev']] = r
        print('verdicts: %d adjudicated abbrevs from %s'
              % (len(verdicts), os.path.basename(a.verdicts)))

    rows = []
    cls_mass = collections.Counter()
    for ab, c in n.most_common():
        try:
            name = slc.resolve_ls(ab)['source_name']
        except Exception:
            name = None
        v = verdicts.get(ab)
        verdict = (v or {}).get('verdict', '')
        reason = (v or {}).get('reason', '')
        if ab in PWG_TO_DCS_TEXT:
            status, dcs_text = 'MAPPED', PWG_TO_DCS_TEXT[ab]
        elif v and (v.get('dcs_text_true') or '').strip():
            # adjudicated but not mapped — the corpus side EXISTS and is known,
            # the scheme is what failed. That is a different fact from both
            # "no mapping exists yet" and "DCS lacks the text".
            status = 'ADJUDICATED-' + (verdict.upper() or 'NO')
            dcs_text = v['dcs_text_true'].strip()
        else:
            cands = candidates(name)
            if cands:
                status = 'DCS-HAS-UNMAPPED'
                dcs_text = max(cands, key=lambda t: tok.get(t, 0))
            else:
                status, dcs_text = 'DCS-LACKS', ''
        cls_mass[status] += c
        rows.append({
            'pwg_abbrev': ab, 'citations': c,
            'share_pct': '%.4f' % (100.0 * c / total),
            'status': status, 'dcs_text': dcs_text,
            'dcs_tokens': tok.get(dcs_text, '') if dcs_text else '',
            'tuple_comparable': ('' if not dcs_text
                                 else ('no' if dcs_text in unsafe else 'yes')),
            'scheme_verified': ('yes' if ab in PWG_TO_DCS_TEXT
                                else (verdict if verdict else '')),
            'verdict_reason': reason.replace('\t', ' ').replace('\n', ' '),
            'pwgbib_source_name': (name or '').replace('\t', ' ')[:120],
        })

    cols = ['pwg_abbrev', 'citations', 'share_pct', 'status', 'dcs_text',
            'dcs_tokens', 'tuple_comparable', 'scheme_verified',
            'verdict_reason', 'pwgbib_source_name']
    with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\t'.join(cols) + '\n')
        for r in rows:
            f.write('\t'.join(str(r[c]) for c in cols) + '\n')

    print('%s <ls> citations, %d distinct abbrevs' % (format(total, ','), len(n)))
    for k, v in cls_mass.most_common():
        print('  %-18s %9s citations  %5.1f%%'
              % (k, format(v, ','), 100.0 * v / total))
    unmapped = [r for r in rows if r['status'] == 'DCS-HAS-UNMAPPED']
    safe = [r for r in unmapped if r['tuple_comparable'] == 'yes']
    print('  backlog: %d unmapped abbrevs (%d tuple-comparable), %s citations'
          % (len(unmapped), len(safe),
             format(sum(r['citations'] for r in unmapped), ',')))
    print('wrote %s' % a.out)


if __name__ == '__main__':
    main()
