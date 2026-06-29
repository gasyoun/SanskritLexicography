#!/usr/bin/env python
"""Grammar layer for pwg_ru — join a PWG verb-root headword to its Whitney record.

Reuses the WhitneyRoots crosswalk (grammar × corpus × MW/Apte, 24k FAIR triples) —
DON'T re-scrape Whitney/Wiki, and DON'T fork that repo (it has an external actor). We
CONSUME its published `crosswalk/roots.csv` and materialize a slim, SLP1-keyed grammar
lookup locally (`src/whitney_grammar.json`) so the pwg_ru pipeline carries the grammar
layer without a run-time dependency on the sibling repo.

  python src/whitney_grammar.py --build        (re)materialize whitney_grammar.json from the sibling crosswalk
  python src/whitney_grammar.py --show gam      show the grammar block for a root (joins by SLP1)

Programmatic: `from whitney_grammar import grammar_for; grammar_for('gam')`.
"""
import csv
import json
import os
import sys
import unicodedata


def _deaccent(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s or '')
                   if unicodedata.category(c) != 'Mn')

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
WROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'WhitneyRoots'))
CROSSWALK = os.path.join(WROOT, 'crosswalk', 'roots.csv')
GRAMMAR_REFS = os.path.join(WROOT, 'src', 'grammar_refs.json')
LOCAL = os.path.join(HERE, 'whitney_grammar.json')
TOP_FORMS = 10
SNIPPET_CHARS = 160        # trim grammar_refs' noisy char-window snippets
MAX_EXC = 12               # cap stored exceptions; high-freq roots (as, i) over-match
MAX_EXC_FLAG = 6           # cap labels shown in the irregularities flag string


def _load_exceptions():
    """Index Whitney exception citations by whitney_no from the sibling
    WhitneyRoots/src/grammar_refs.json (built by grammar_ref_builder.py). The
    grammar_refs `id` equals the crosswalk `whitney_no` (verified 930/930). Returns
    {whitney_no: [{'label', 'section', 'snippet'}]} for is_exception refs only.
    Empty dict if the sibling file is absent (build still succeeds without it)."""
    if not os.path.exists(GRAMMAR_REFS):
        return {}
    data = json.load(open(GRAMMAR_REFS, encoding='utf-8'))
    out = {}
    for wid, rec in data.items():
        excs = []
        for ref in rec.get('grammar_refs', []):
            if not ref.get('is_exception'):
                continue
            snip = (ref.get('snippet') or '').strip()
            if len(snip) > SNIPPET_CHARS:
                snip = snip[:SNIPPET_CHARS].rstrip() + '…'
            excs.append({'label': ref.get('label') or ('§%s' % ref.get('section')),
                         'section': ref.get('section'), 'snippet': snip})
        if excs:
            out[str(wid)] = excs
    return out


def _pairs(cell, sep='|'):
    out = []
    for part in (cell or '').split(sep):
        part = part.strip()
        if ':' in part:
            k, v = part.rsplit(':', 1)
            out.append((k.strip(), v.strip()))
    return out


def irregularities(rec):
    """Derive a grammar-exception annotation level from the raw record."""
    flags = []
    cls = rec.get('class') or ''
    if '|' in cls:
        flags.append('multi_class:%s' % cls)            # >1 gaṇa (e.g. gam I|II)
    if rec.get('class_uncertain'):
        flags.append('class_uncertain')                  # Whitney's "ROMAN ?"
    if not cls or cls == '—':
        flags.append('class_unrecorded')                 # defective OR capture gap — verify
    # root-final nasal loss in the PPP (gam -> gatá, han -> hatá, man -> matá): the "m/n expelled"
    root, ppp = rec.get('root_slp1') or '', rec.get('ppp') or ''
    if root[-1:] in ('m', 'n') and ppp and (root[:-1] + 'ta') == _deaccent(ppp):
        flags.append('root_final_nasal_loss(%s→%s)' % (root, ppp))
    return flags


def _block(row, exceptions=None):
    rec = {
        'whitney_no': row['whitney_no'],
        'root_iast': row['root_iast'],
        'root_slp1': row['root_slp1'],
        'homonym': row.get('homonym') or '',
        'class': row.get('class') or '',
        'class_uncertain': row.get('class_uncertain') or '',
        'ppp': row.get('ppp') or '',
        'period_tags': [p for p in (row.get('period_tags') or '').split('|') if p],
        'dcs_freq': int(row['dcs_freq']) if (row.get('dcs_freq') or '').isdigit() else 0,
        'mw_id': row.get('mw_id') or '',
        'apte_id': row.get('apte_id') or '',
        'attested_forms': [{'form': f, 'freq': int(n) if n.isdigit() else 0}
                           for f, n in _pairs(row.get('attested_forms'))][:TOP_FORMS],
        'section_refs': {cat: rng for cat, rng in _pairs(row.get('section_refs'))},
        'source': 'WhitneyRoots/crosswalk/roots.csv (Whitney §§ + warnemyr; CC-BY-SA)',
    }
    rec['irregularities'] = irregularities(rec)
    # Fold in Whitney's actual exception paragraphs (grammar_refs.json), joined by
    # whitney_no. These are real §-citations of "except/irregular/anomalous" wording.
    excs = (exceptions or {}).get(str(rec['whitney_no']))
    if excs:
        total = len(excs)
        rec['whitney_exceptions'] = excs[:MAX_EXC]
        if total > MAX_EXC:
            rec['whitney_exceptions_total'] = total      # signals over-matched high-freq root
        uniq = list(dict.fromkeys(e['label'] for e in excs if e.get('label')))
        shown = ', '.join(uniq[:MAX_EXC_FLAG])
        if len(uniq) > MAX_EXC_FLAG:
            shown += ', +%d more' % (len(uniq) - MAX_EXC_FLAG)
        if shown:
            rec['irregularities'].append('whitney_exception(%s)' % shown)
    return rec


def build():
    if not os.path.exists(CROSSWALK):
        sys.exit('crosswalk not found: %s (clone gasyoun/WhitneyRoots as a sibling)' % CROSSWALK)
    exceptions = _load_exceptions()
    by_slp1 = {}
    for row in csv.DictReader(open(CROSSWALK, encoding='utf-8')):
        by_slp1.setdefault(row['root_slp1'], []).append(_block(row, exceptions))
    json.dump(by_slp1, open(LOCAL, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    n_exc = sum(1 for recs in by_slp1.values() for r in recs if r.get('whitney_exceptions'))
    print('wrote %s — %d roots (%d records); %d records carry Whitney exception §§ (%s)' %
          (LOCAL, len(by_slp1), sum(len(v) for v in by_slp1.values()), n_exc,
           'grammar_refs.json found' if exceptions else 'grammar_refs.json ABSENT — no exceptions folded'))


_CACHE = None


def _load():
    global _CACHE
    if _CACHE is None:
        if not os.path.exists(LOCAL):
            build()
        _CACHE = json.load(open(LOCAL, encoding='utf-8'))
    return _CACHE


def grammar_for(slp1, homonym=None):
    """Return the grammar block(s) for an SLP1 root. With homonym, the single match
    (Whitney homonym index); without, all homonyms (caller disambiguates)."""
    recs = _load().get(slp1, [])
    if homonym is not None:
        recs = [r for r in recs if r.get('homonym') == str(homonym)] or recs
    return recs


def main():
    args = sys.argv[1:]
    if '--build' in args:
        build(); return
    if '--show' in args:
        slp1 = args[args.index('--show') + 1]
        recs = grammar_for(slp1)
        if not recs:
            print('no Whitney record for %r' % slp1); return
        print(json.dumps(recs, ensure_ascii=False, indent=2))
        return
    print(__doc__)


if __name__ == '__main__':
    main()
