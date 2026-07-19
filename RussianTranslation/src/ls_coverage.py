# -*- coding: utf-8 -*-
r"""<ls> link-enrichment coverage over the four H1307 citation classes.

Walks the PWG article corpus, extracts every `<ls n="PFX">VIS</ls>` citation,
and reports per class -- Pāṇini `P.`, `Spr.` (1st ed), `Spr. (II)` (2nd ed),
`DHĀTUP.` -- four numbers:

  total              <ls> occurrences of the class
  linked             resolve to a live-verified href (ls_resolver.generate_href)
  tooltip'd          have hover text (a pwgbib source title, or the Spr. (II) saying)
  full_text_enriched carry the recognized full text (Spr. (II) only: saying in the
                     Indische Sprüche corpus)

DENOMINATOR. The deliverable counts the RU *store*'s occurrences when the store
(`src/pwg_ru_translated.jsonl`, gitignored) is present on this machine. When it is
absent (Prerequisite 1 of H1307), the count falls back to the full source
`../csl-orig/v02/pwg/pwg.txt` -- the whole PWG corpus, a superset of the RU subset
-- and the substitution is stamped in the report. Pass --store / --pwg to override.

  python src/ls_coverage.py [--store PATH] [--pwg PATH] [--out PATH] [--md]

Raw per-class JSON is written to a gitignored path (default pwg_ru/eval/
ls_coverage.json); only the aggregate markdown table (--md, also printed) is meant
to be committed (into ABBREVIATIONS_RU.md).
"""
import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import date

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ls_resolver as lsr        # noqa: E402
import pwg_sources as pwgsrc     # noqa: E402
import spr_fulltext as spr       # noqa: E402

REPO = os.path.dirname(HERE)                                   # RussianTranslation/
GH = os.path.normpath(os.path.join(HERE, '..', '..', '..'))    # GitHub/ (csl-orig is a sibling repo)
STORE = os.path.join(HERE, 'pwg_ru_translated.jsonl')
PWG = os.path.join(GH, 'csl-orig', 'v02', 'pwg', 'pwg.txt')
DEFAULT_OUT = os.path.join(REPO, 'pwg_ru', 'eval', 'ls_coverage.json')

_LS = re.compile(r'<ls\b([^>]*)>(.*?)</ls>', re.S)
_N_ATTR = re.compile(r'\bn\s*=\s*"([^"]*)"')

CLASSES = ['P.', 'Spr.', 'Spr. (II)', 'DHĀTUP.']


def classify(n_attr, visible):
    """Return the H1307 class of one <ls>, or None if it is some other siglum.

    `Spr. (II)` is counted ONLY when a saying NUMBER follows the 2nd-ed marker
    (`Spr. (II) <digit>`) — this is edition-critical AND excludes the stale-
    attribute artifact where a 1st-ed continuation ref carries a bled-over
    `n="Spr. (II)"` but a visible `(I) 1649` (the real edition is 1st); those
    route to plain `Spr.` where they belong. Tested before plain `Spr.`."""
    s = re.sub(r'\s+', ' ', ('%s %s' % (n_attr or '', visible or '')).strip())
    s = re.sub(r'<[^>]+>', '', s)
    if re.match(r'^Spr\.\s*\(II\)\s*[0-9]', s):
        return 'Spr. (II)'
    if re.match(r'^Spr\.', s):
        return 'Spr.'
    if re.match(r'^P\.', s):
        return 'P.'
    if re.match(r'^DH[ĀA]TUP\.', s):
        return 'DHĀTUP.'
    return None


def _has_tooltip(n_attr, visible, cls):
    if cls == 'Spr. (II)' and spr.tooltip(n_attr, visible):
        return True
    for cand in (n_attr, pwgsrc.source_key(visible or '')):
        if cand and pwgsrc.resolve(cand):
            return True
    return False


def iter_store(store_path):
    """Yield (n_attr, visible) from every <ls> in the RU store's DE source fields."""
    with open(store_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            for fld in ('de', 'de_raw', 'ru'):
                for m in _LS.finditer(r.get(fld) or ''):
                    nm = _N_ATTR.search(m.group(1))
                    yield (nm.group(1) if nm else None), m.group(2)


def iter_pwg(pwg_path):
    """Yield (n_attr, visible) from every <ls> in raw pwg.txt."""
    with open(pwg_path, encoding='utf-8') as f:
        for line in f:
            for m in _LS.finditer(line):
                nm = _N_ATTR.search(m.group(1))
                yield (nm.group(1) if nm else None), m.group(2)


def compute(pairs):
    per = {c: Counter() for c in CLASSES}
    # full-form P. (3-param a,p,s) tracked separately for the DoD metric
    pfull = Counter()
    for n_attr, vis in pairs:
        cls = classify(n_attr, vis)
        if cls is None:
            continue
        c = per[cls]
        c['total'] += 1
        url = lsr.generate_href('pwg', n_attr, (vis or '').strip())
        if url:
            c['linked'] += 1
        if _has_tooltip(n_attr, vis, cls):
            c['tooltip'] += 1
        if cls == 'Spr. (II)':
            if spr.second_ed_num(n_attr, vis) is not None and spr.saying(spr.second_ed_num(n_attr, vis)):
                c['enriched'] += 1
        if cls == 'P.':
            s = re.sub(r'\s+', ' ', ('%s %s' % (n_attr or '', vis or '')).strip())
            s = re.sub(r'<[^>]+>', '', s)
            if re.match(r'^P\.\s*[0-9]+\s*,\s*[0-9]+\s*,\s*[0-9]+', s):
                pfull['total'] += 1
                if url:
                    pfull['linked'] += 1
    return per, pfull


def pct(num, den):
    return (100.0 * num / den) if den else 0.0


def md_table(per, pfull, source_label):
    L = []
    L.append('| class | total | linked | linked % | tooltip | full-text enriched |')
    L.append('|---|--:|--:|--:|--:|--:|')
    for c in CLASSES:
        d = per[c]
        enr = ('%d' % d['enriched']) if c == 'Spr. (II)' else '— (n/a)'
        L.append('| `%s` | %d | %d | %.1f%% | %d | %s |' % (
            c, d['total'], d['linked'], pct(d['linked'], d['total']), d['tooltip'], enr))
    L.append('')
    L.append('- **Full-form Pāṇini `P. a,p,s` (3-param):** %d / %d linked (%.1f%%) — the H1307 DoD target.'
             % (pfull['linked'], pfull['total'], pct(pfull['linked'], pfull['total'])))
    d2 = per['Spr. (II)']
    L.append('- **`Spr. (II) N` (2nd ed):** %d / %d linked (%.1f%%), %d full-text enriched (%.1f%% of linked).'
             % (d2['linked'], d2['total'], pct(d2['linked'], d2['total']),
                d2['enriched'], pct(d2['enriched'], d2['linked'])))
    L.append('')
    L.append('_Denominator: %s. Generated by `src/ls_coverage.py` on %s._'
             % (source_label, date.today().strftime('%d-%m-%Y')))
    return '\n'.join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--store', default=STORE)
    ap.add_argument('--pwg', default=PWG)
    ap.add_argument('--out', default=DEFAULT_OUT)
    ap.add_argument('--md', action='store_true', help='print the aggregate markdown table')
    args = ap.parse_args()

    if os.path.exists(args.store):
        pairs = iter_store(args.store)
        source_label = 'RU store `src/pwg_ru_translated.jsonl`'
        substituted = False
    elif os.path.exists(args.pwg):
        pairs = iter_pwg(args.pwg)
        source_label = ('full source `csl-orig/v02/pwg/pwg.txt` (RU store absent on '
                        'this machine — SUBSTITUTION per H1307 Prerequisite 1; counts the '
                        'whole PWG corpus, a superset of the RU-translated subset)')
        substituted = True
    else:
        sys.exit('neither store (%s) nor pwg.txt (%s) is present' % (args.store, args.pwg))

    per, pfull = compute(pairs)

    out = {
        'generated': date.today().strftime('%d-%m-%Y'),
        'denominator': source_label,
        'substituted_pwg_for_store': substituted,
        'classes': {c: dict(per[c]) for c in CLASSES},
        'panini_full_form_3param': dict(pfull),
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    sys.stderr.write('raw coverage JSON -> %s\n' % args.out)

    table = md_table(per, pfull, source_label)
    if args.md:
        print(table)
    else:
        sys.stderr.write(table + '\n')


if __name__ == '__main__':
    main()
