# -*- coding: utf-8 -*-
r"""Build the `DHĀTUP. x,y` -> Palsule concordance (H1333).

WHY THIS SHAPE. H1333's §Prerequisites asked whether MG's supplied XLS carries a
Böhtlingk coordinate per row. Inspected 07-09-2026: it does NOT. The file is
Palsule's *artha* (meaning) index — 8171 rows of `<artha> : ⎷<root> <pada>` with a
Palsule page (`P166`…) — keyed on the ROOT, never on a gaṇa,serial pair. So the
branch-2 path applies, but with a better join key than the (gaṇa, dhātu) one the
handoff sketched:

  PWG is itself Böhtlingk. A `<ls>DHĀTUP. x,y</ls>` citation stands inside the
  article OF THE ROOT it numbers, and that article's `<k1>` key IS the dhātu in
  SLP1. So the (x,y) -> root half of the crosswalk is *read off Böhtlingk's own
  text*, not guessed by a normalizing join — no ablaut normalization needed, and
  the H328 negative result (a naive it-stripped join matched 454/930) does not
  bind this half.

Only the second half — root -> Palsule row — is a join, and it is a join on the
root's citation form in two independent transliterations (SLP1 headword vs the
XLS's IAST `Корень` column), which is exactly what `_norm()` below reconciles.

AMBIGUITY FILTER (load-bearing). A coordinate is kept only when every PWG article
citing it agrees on the root. A DHĀTUP. coordinate quoted inside a *noun* article
would otherwise contribute a false root; the disagreement filter drops those
coordinates entirely rather than picking a winner. Conflicts are counted and
reported, never silently resolved.

Raw XLS stays local (gitignored `pwg_ru/eval/`); the DERIVED table is what ships.

  python src/build_dhatup_palsule.py [--xls PATH] [--pwg PATH] [--out PATH]
"""
import argparse
import json
import os
import re
import sys
import unicodedata
from collections import defaultdict
from datetime import date

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.dirname(HERE)
from sibling_root import sibling_root  # noqa: E402
GH = sibling_root(HERE)

DEFAULT_XLS = os.path.join(REPO, 'pwg_ru', 'eval', 'Palsule_Artha_24_01_2014.xlsx')
DEFAULT_PWG = os.path.join(GH, 'csl-orig', 'v02', 'pwg', 'pwg.txt')
DEFAULT_OUT = os.path.join(HERE, 'data', 'dhatup_palsule.json')

_L = re.compile(r'^<L>(\d+)<pc>[^<]*<k1>([^<]*)<k2>')
_DHATUP = re.compile(r'<ls\b[^>]*>\s*DH[ĀA]TUP\.\s*(\d+)\s*,\s*(\d+)')
#: A `DHĀTUP. x,y` continuation carried on the n= attribute with a bare visible
#: number (`<ls n="DHĀTUP. 26,">91</ls>`) — same citation, different splitting.
_DHATUP_N = re.compile(r'<ls\b[^>]*\bn\s*=\s*"DH[ĀA]TUP\.\s*(\d+)\s*,\s*"[^>]*>\s*(\d+)')
#: A part-of-speech tag on the head line marks a NOMINAL article. Böhtlingk gives
#: such an article the dhātupāṭha coordinate only to say "this noun glosses that
#: root" (`{#loqana#}¦ <lex>n.</lex> … als Erkl. von {#bAD#} <ls>DHĀTUP. 2,4</ls>`)
#: — the coordinate belongs to the root, not to the noun. Root articles carry no
#: <lex> on the head line (they carry the finite form, and often a √).
_HEAD_LEX = re.compile(r'<lex\b')

#: SLP1 -> IAST for the root citation form only (consonants + simple vowels).
_S2I = {
    'A': 'ā', 'I': 'ī', 'U': 'ū', 'f': 'ṛ', 'F': 'ṝ', 'x': 'ḷ', 'X': 'ḹ',
    'E': 'ai', 'O': 'au', 'M': 'ṃ', 'H': 'ḥ',
    'K': 'kh', 'G': 'gh', 'N': 'ṅ', 'C': 'ch', 'J': 'jh', 'Y': 'ñ',
    'w': 'ṭ', 'W': 'ṭh', 'q': 'ḍ', 'Q': 'ḍh', 'R': 'ṇ',
    'T': 'th', 'D': 'dh', 'P': 'ph', 'B': 'bh',
    'S': 'ś', 'z': 'ṣ',
}


def slp1_root_iast(s):
    """The root's SLP1 citation form -> IAST (accents/markup already stripped)."""
    return ''.join(_S2I.get(c, c) for c in s)


def _norm(s):
    """Join key: NFC IAST, lowercased, stripped of the XLS's ⎷ mark, of pada
    letters, of trailing homonym digits, of whitespace and of hyphens."""
    if not s:
        return ''
    s = unicodedata.normalize('NFC', s)
    s = s.replace('⎷', '').replace('√', '')
    s = re.sub(r'[\s\-·]', '', s)
    s = re.sub(r'\d+$', '', s)
    return s.lower()


def read_palsule(xls):
    """Palsule artha index -> {norm_root: {'root_iast', 'pages', 'arthas'}}.

    Sheet `Лист1`: # | Text | page | Описание(=artha) | Корень с метками |
    Корень | Метки(pada V/H) | ... . One root owns many artha rows; we keep the
    root's page set and its artha glosses in file order."""
    import openpyxl
    wb = openpyxl.load_workbook(xls, read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]
    by_root = {}
    rows = 0
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 0:
            continue
        if not row or len(row) < 7:
            continue
        num, _text, page, artha, _marked, root, pada = row[:7]
        if not root:
            continue
        rows += 1
        key = _norm(str(root))
        if not key:
            continue
        rec = by_root.setdefault(key, {
            'root_iast': str(root).replace('⎷', '').strip(),
            'pages': [], 'arthas': [], 'pada': [], 'nums': [],
        })
        p = (str(page).strip() if page else '')
        if p and p not in rec['pages']:
            rec['pages'].append(p)
        a = (str(artha).strip() if artha else '')
        if a and a not in rec['arthas']:
            rec['arthas'].append(a)
        pd = (str(pada).strip() if pada else '')
        if pd and pd not in rec['pada']:
            rec['pada'].append(pd)
        if num is not None:
            rec['nums'].append(str(num).strip())
    wb.close()
    return by_root, rows


def read_pwg_coords(pwg):
    """pwg.txt -> ({coord: {root_slp1: n_headline_citations}}, n_entries_seen).

    HEAD-LINE WEIGHTING. Böhtlingk gives a root its dhātupāṭha coordinate on the
    article's OWN head line (`{#aNg#}¦, {#a/Ngati#} … <ls>DHĀTUP. 5,38</ls>`).
    The same coordinate also turns up deeper inside derivative/noun articles that
    merely quote it. We record both, but a head-line citation outranks a body one
    when a coordinate has several claimants — an empirical discriminator, not a
    guess: it is where the lexicographer states the numbering."""
    coords = defaultdict(lambda: defaultdict(lambda: [0, 0, 0]))   # [head, body, head_nominal]
    key = None
    at_head = False
    entries = 0
    with open(pwg, encoding='utf-8') as f:
        for line in f:
            m = _L.match(line)
            if m:
                key = m.group(2)
                at_head = True
                entries += 1
                continue
            if line.startswith('<LEND>'):
                key = None
                continue
            if key is None:
                continue
            slot = 0 if at_head else 1
            nominal = bool(at_head and _HEAD_LEX.search(line))
            for rx in (_DHATUP, _DHATUP_N):
                for mm in rx.finditer(line):
                    coord = '%s,%s' % (mm.group(1), mm.group(2))
                    coords[coord][key][slot] += 1
                    if nominal:
                        coords[coord][key][2] += 1
            at_head = False
    return coords, entries


def build(xls, pwg):
    palsule, xls_rows = read_palsule(xls)
    coords, entries = read_pwg_coords(pwg)

    table = {}
    conflicts = []
    unmatched = []
    resolved_by_head = 0
    for coord, roots in sorted(coords.items(), key=lambda kv: [int(x) for x in kv[0].split(',')]):
        if len(roots) > 1:
            head = [r for r, c in roots.items() if c[0]]
            if len(head) > 1:
                # Drop the nominal head-line claimants (`<lex>` articles quoting the
                # coordinate as a gloss); what survives is the verbal article.
                verbal = [r for r in head if not roots[r][2]]
                if verbal:
                    head = verbal
            if len(head) != 1:
                # No single head-line claimant -> not safely attributable. Drop it;
                # never pick a winner by citation count.
                conflicts.append({'coord': coord, 'roots': sorted(roots),
                                  'head_claimants': sorted(head)})
                continue
            resolved_by_head += 1
            root_slp1 = head[0]
        else:
            root_slp1 = next(iter(roots))
        root_iast = slp1_root_iast(root_slp1)
        rec = palsule.get(_norm(root_iast))
        if not rec:
            unmatched.append({'coord': coord, 'root_slp1': root_slp1,
                              'root_iast': root_iast})
            continue
        table[coord] = {
            'root_slp1': root_slp1,
            'root_iast': root_iast,
            'palsule_root': rec['root_iast'],
            'pages': rec['pages'],
            'pada': rec['pada'],
            'arthas': rec['arthas'][:8],
            'artha_count': len(rec['arthas']),
        }

    stats = {
        'built': date.today().strftime('%d-%m-%Y'),
        'source_xls': os.path.basename(xls),
        'source_pwg': os.path.relpath(pwg, GH),
        'xls_artha_rows': xls_rows,
        'xls_distinct_roots': len(palsule),
        'pwg_entries': entries,
        'coords_cited': len(coords),
        'coords_conflicted': len(conflicts),
        'coords_resolved_by_head_line': resolved_by_head,
        'coords_unmatched': len(unmatched),
        'coords_linked': len(table),
        'match_rate': round(100.0 * len(table) / len(coords), 1) if coords else 0.0,
    }
    return table, stats, conflicts, unmatched


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xls', default=DEFAULT_XLS)
    ap.add_argument('--pwg', default=DEFAULT_PWG)
    ap.add_argument('--out', default=DEFAULT_OUT)
    a = ap.parse_args()

    table, stats, conflicts, unmatched = build(a.xls, a.pwg)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    payload = {
        '_README': ('DHĀTUP. gaṇa,serial -> Palsule artha-index record. Built by '
                    'src/build_dhatup_palsule.py (H1333). The coordinate->root half '
                    'is read off PWG itself (the citation sits in the root\'s own '
                    'article, <k1> is the dhātu); only root->Palsule is a join. '
                    'Coordinates whose citing articles disagree on the root are '
                    'DROPPED, not guessed.'),
        '_stats': stats,
        'table': table,
    }
    with open(a.out, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=1, sort_keys=False)
        f.write('\n')
    for k, v in stats.items():
        print('%-22s %s' % (k, v))
    print('wrote %s' % a.out)
    if conflicts:
        print('sample conflicts: %s' % json.dumps(conflicts[:5], ensure_ascii=False))
    if unmatched:
        print('sample unmatched: %s' % json.dumps(unmatched[:8], ensure_ascii=False))


if __name__ == '__main__':
    main()
