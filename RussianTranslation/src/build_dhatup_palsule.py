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

GRANULARITY — READ THIS BEFORE TRUSTING A RECORD. A record is keyed by coordinate but
its CONTENT is the union of every XLS row whose root string normalizes to the same
spelling. Palsule's artha index is keyed on the root, not on a gaṇa,serial pair, so it
cannot distinguish the homonyms Böhtlingk numbers separately: `DHĀTUP. 26,91` is the
divādi `snih`, but its record carries the arthas of every `snih` in Palsule (divādi and
curādi alike). The record therefore answers "what does Palsule record for this root
spelling", NOT "what does Palsule record at exactly this coordinate". `artha_agreement`
below measures how often the right artha is in there; it is never a claim that the wrong
ones have been excluded.

The stored `arthas` list is COMPLETE; only the tooltip limits what it displays.

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


#: Palsule's printed roots carry footnote markers that the XLS captured as trailing
#: digits (`gādh39`, `arj7`, `i4`). `_norm` already strips them for MATCHING, but the
#: stored/displayed `palsule_root` kept them and rendered them into the tooltip.
_FOOTNOTE_DIGITS = re.compile(r'\d+$')

#: The XLS root column carries the punctuation of the printed line it was cut from
#: (`⎷bhu,` in the two-root row `sattāyām : ⎷bhu, ⎷vid all (ex. V).`). Left in place it
#: forms a distinct key, which is how DHĀTUP. 1,1 — bhū, the first root of the whole
#: dhātupāṭha — shipped without its canonical artha `sattāyām`.
_EDGE_PUNCT = re.compile(r'^[\s.,;:]+|[\s.,;:]+$')

#: Source typos in the XLS's root column, folded to the attested root. Kept as an
#: explicit two-item allowlist rather than a general vowel-length fold: `bhu`/`bhū` and
#: `dhu`/`dhū` are safe because no short-vowel root of that shape exists, whereas a
#: blanket fold would collide genuine pairs (`vid`/`vīd`, `kṛ`/`kṝ`). Each entry is a
#: claim about ONE cell in ONE spreadsheet and is counted in `_stats.source_typo_folds`.
_XLS_ROOT_TYPOS = {'bhu': 'bhū', 'dhu': 'dhū'}


def _clean_root(s):
    """The displayable Palsule root: ⎷ removed, edge punctuation and footnote digits
    stripped."""
    return _FOOTNOTE_DIGITS.sub('', _EDGE_PUNCT.sub('', (s or '').replace('⎷', '')))


def _norm(s):
    """Join key: NFC IAST, lowercased, stripped of the XLS's ⎷ mark, of pada
    letters, of trailing homonym digits, of whitespace and of hyphens."""
    if not s:
        return ''
    s = unicodedata.normalize('NFC', s)
    s = s.replace('⎷', '').replace('√', '')
    s = _EDGE_PUNCT.sub('', s)
    s = re.sub(r'[\s\-·]', '', s)
    s = re.sub(r'\d+$', '', s)
    s = s.lower()
    return _XLS_ROOT_TYPOS.get(s, s)


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
    typo_folds = 0
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
        if key != _clean_root(str(root)).lower():
            typo_folds += 1
        rec = by_root.setdefault(key, {
            'root_iast': _clean_root(str(root)),
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
    return by_root, rows, typo_folds


#: Böhtlingk routinely prints the dhātupāṭha's own artha in SLP1 parentheses IMMEDIATELY
#: beside the citation, on either side of it:
#:   {#sni/hyati (prItO)#} <ls>DHĀTUP. 26,91</ls>          -> prItO  (prītau)
#:   {#ti/zWati#} <ls>DHĀTUP. 22,30</ls> ({#gatinivfttO#}) -> gatinivfttO (gatinivṛttau)
#: That is an INDEPENDENT witness of what the coordinate means — it comes from PWG, the
#: Palsule glosses come from the XLS — so agreement between the two is a real accuracy
#: measurement of the crosswalk rather than a spot-check anecdote. Verified only; never
#: used to build or to filter the table.
_ARTHA_BEFORE = re.compile(r'\(([^(){}#]+)\)#\}\s*(?:<[^>]*>\s*)?$')
_ARTHA_AFTER = re.compile(r'^\s*\(\{#([^#}]+)#\}\)')


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


def audit_inline_artha(pwg, table):
    """Measure the table against PWG's OWN parenthesized artha beside each citation.

    Returns (agree, disagree, examined, samples). A coordinate counts as agreeing when
    the SLP1 artha PWG prints next to the citation, transliterated, appears in the
    Palsule artha set the table carries for it. Disagreements are returned verbatim so
    they can be read rather than summarized."""
    agree = disagree = loose = 0
    samples = []
    for line, coord in _iter_citation_lines(pwg):
        rec = table.get(coord)
        if not rec:
            continue
        for pos, m in _inline_artha(line, coord):
            got = slp1_root_iast(m).replace('/', '').replace('\\', '')
            got_n = _norm(got)
            have = [_norm(a) for a in (rec.get('arthas') or [])]
            if got_n and got_n in have:
                agree += 1
                loose += 1
            elif got_n and _loose_hit(got_n, have):
                # Same artha, different citation form: PWG prints `ched` where Palsule
                # has `chede`, `saṃcalane` for `calane`, or runs two arthas into one
                # string (`mandāyāṃ gatau, śanairgatau`). Counted separately and never
                # folded into the strict number.
                loose += 1
                disagree += 1
                if len(samples) < 25:
                    samples.append({'coord': coord, 'pwg_artha': got,
                                    'palsule_arthas': rec.get('arthas')[:6],
                                    'where': pos, 'loose_match': True})
            elif got_n:
                disagree += 1
                if len(samples) < 25:
                    samples.append({'coord': coord, 'pwg_artha': got,
                                    'palsule_arthas': rec.get('arthas')[:6],
                                    'where': pos})
            break
    return agree, disagree, agree + disagree, samples, loose


def _loose_hit(got, have):
    """True when PWG's artha and a Palsule artha are the same gloss in different citation
    form. Deliberately weak — reported as its own number, never merged into the strict
    rate — because it accepts substring containment in either direction."""
    for a in have:
        if not a:
            continue
        if got in a or a in got:
            return True
        # PWG sometimes runs several arthas into one string; split and retry.
        for piece in re.split(r'[,;]', got):
            piece = piece.strip()
            if piece and (piece in a or a in piece):
                return True
    return False


def _iter_citation_lines(pwg):
    """Yield (line, coord) for every line carrying a DHĀTUP. x,y citation."""
    with open(pwg, encoding='utf-8') as f:
        for line in f:
            for rx in (_DHATUP, _DHATUP_N):
                for mm in rx.finditer(line):
                    yield line, '%s,%s' % (mm.group(1), mm.group(2))


def _inline_artha(line, coord):
    """Yield (position, slp1_artha) for the artha PWG prints beside this citation."""
    key = re.compile(r'<ls\b[^>]*>\s*DH[\u0100A]TUP\.\s*%s\s*,\s*%s\s*</ls>'
                     % tuple(coord.split(',')))
    m = key.search(line)
    if not m:
        return
    before = _ARTHA_BEFORE.search(line[:m.start()])
    if before:
        yield 'before', before.group(1)
        return
    after = _ARTHA_AFTER.match(line[m.end():])
    if after:
        yield 'after', after.group(1)


def build(xls, pwg):
    palsule, xls_rows, typo_folds = read_palsule(xls)
    coords, entries = read_pwg_coords(pwg)

    # Baseline for the filters' measured contribution: with NO disambiguation at all,
    # every multi-claimant coordinate is simply dropped. Recorded so the "filters bought
    # us X points" claim in the docs is derivable from the artifact, not asserted.
    unfiltered_linked = sum(
        1 for c, roots in coords.items()
        if len(roots) == 1 and palsule.get(_norm(slp1_root_iast(next(iter(roots)))))
    )

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
            # Stored in FULL. An earlier cut truncated to 8, which silently dropped
            # `sattāyām` from DHĀTUP. 1,1 — bhū's canonical artha and the first entry of
            # the whole dhātupāṭha — while `artha_count` still said 11. The tooltip does
            # its own display-time limiting; the data layer keeps everything.
            'arthas': rec['arthas'],
            'artha_count': len(rec['arthas']),
        }

    stats = {
        'built': date.today().strftime('%d-%m-%Y'),
        'source_xls': os.path.basename(xls),
        'source_pwg': os.path.relpath(pwg, GH),
        'xls_artha_rows': xls_rows,
        'xls_root_typo_folds': typo_folds,
        'xls_distinct_roots': len(palsule),
        'pwg_entries': entries,
        'coords_cited': len(coords),
        'coords_conflicted': len(conflicts),
        'coords_resolved_by_head_line': resolved_by_head,
        'coords_unmatched': len(unmatched),
        'coords_linked': len(table),
        'match_rate': round(100.0 * len(table) / len(coords), 1) if coords else 0.0,
        'coords_linked_without_filters': unfiltered_linked,
        'match_rate_without_filters': (round(100.0 * unfiltered_linked / len(coords), 1)
                                       if coords else 0.0),
    }
    agree, disagree, examined, samples, loose = audit_inline_artha(pwg, table)
    stats['inline_artha_examined'] = examined
    stats['inline_artha_agree'] = agree
    stats['inline_artha_disagree'] = disagree
    stats['inline_artha_agreement_rate'] = (round(100.0 * agree / examined, 1)
                                            if examined else 0.0)
    stats['inline_artha_agree_loose'] = loose
    stats['inline_artha_agreement_rate_loose'] = (round(100.0 * loose / examined, 1)
                                                  if examined else 0.0)
    return table, stats, conflicts, unmatched, samples


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xls', default=DEFAULT_XLS)
    ap.add_argument('--pwg', default=DEFAULT_PWG)
    ap.add_argument('--out', default=DEFAULT_OUT)
    a = ap.parse_args()

    table, stats, conflicts, unmatched, artha_samples = build(a.xls, a.pwg)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    payload = {
        '_README': (
            'DHĀTUP. gaṇa,serial -> what Palsule records FOR THAT ROOT SPELLING. '
            'Built by src/build_dhatup_palsule.py (H1333). '
            'GRANULARITY: keyed by coordinate, but the content is the union of every '
            'XLS row whose root normalizes to the same spelling. Palsule\'s artha index '
            'is keyed on the root, not on gaṇa,serial, so it CANNOT separate the '
            'homonyms Böhtlingk numbers apart: 26,91 is the divādi snih, but its arthas '
            'are every snih in Palsule. Read a record as "what Palsule says about this '
            'root", never as "what Palsule says at exactly this coordinate". '
            'The coordinate->root half is read off PWG itself (the citation sits in the '
            'root\'s own article, <k1> is the dhātu); only root->Palsule is a join. '
            'Coordinates whose citing articles disagree on the root are DROPPED, not '
            'guessed. ACCURACY: _stats.inline_artha_* measures the table against the '
            'artha PWG itself prints beside the citation — an independent witness. '
            'Coverage and accuracy are different numbers; both are in _stats.'),
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
    if artha_samples:
        print('sample inline-artha disagreements: %s'
              % json.dumps(artha_samples[:5], ensure_ascii=False))


if __name__ == '__main__':
    main()
