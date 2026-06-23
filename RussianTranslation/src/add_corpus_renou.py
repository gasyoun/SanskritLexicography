#!/usr/bin/env python
"""add_corpus_renou.py — fold a raw IAST Sanskrit text into the lemma→Renou index.

DCS gives lemmatised attestations; for texts NOT in DCS (e.g. GRETIL e-texts) we
have no lemmatiser, so we fold word-FORMS at a given Renou state. A form becomes a
useful enrichment only when it equals a dictionary headword form (exact match at
lookup time), so recall is lower than DCS's lemmas — but it is purely additive and
never destructive. Re-runnable: a text already folded (tracked in the index's
'__sources__' meta) is skipped unless --force.

  python add_corpus_renou.py TEXT.txt --name "Skandapurāṇa: Revākhaṇḍa (GRETIL)" \
         --renou III --date 1100 [--index dcs_lemma_renou.json] [--force] [--report]
"""
import json, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import renou  # STATES / _ORDER ordering only

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INDEX = os.path.join(HERE, 'dcs_lemma_renou.json')
_ORDER = {s: i for i, s in enumerate(renou.STATES)}

# IAST letter run = a Sanskrit word-form. Keeps the standard IAST diacritics and
# the avagraha; everything else (digits, daṇḍa, '/', markers, punctuation) splits.
_WORD = re.compile(r"[a-zāīūṛṝḷḹṅñṭḍṇśṣṁṃḥ́̃’']+")


def forms_in_text(text):
    """Distinct lowercased word-forms in a GRETIL-style IAST plaintext body."""
    # drop everything before the GRETIL '# Text' marker (the header block)
    m = re.search(r'(?m)^#\s*Text\s*$', text)
    if m:
        text = text[m.end():]
    forms = set()
    for tok in _WORD.findall(text.lower()):
        tok = tok.strip("’'")
        # drop reference sigla / speaker-tag debris and 1-char noise
        if len(tok) >= 2 and any(c in 'aāiīuūṛṝḷḹeo' for c in tok):
            forms.add(tok)
    return forms


def load_index(path):
    idx = json.load(open(path, encoding='utf-8'))
    sources = idx.pop('__sources__', [])
    return idx, sources


def fold(idx, sources, forms, name, state, date, force):
    if name in sources and not force:
        return {'skipped': True}
    added_new = updated = 0
    for f in forms:
        e = idx.get(f)
        if e is None:
            idx[f] = {'renou': [state], 'renou_oldest': state,
                      'oldest_date': date, 'oldest_text': name,
                      'n_texts': 1, 'form_level': True}
            added_new += 1
        else:
            states = set(e['renou'])
            if state not in states:
                states.add(state)
                e['renou'] = sorted(states, key=_ORDER.get)
                updated += 1
            # only move the 'oldest' EARLIER — a late khaṇḍa never ages a word up
            if date is not None and (e['oldest_date'] is None or date < e['oldest_date']):
                e['oldest_date'] = date
                e['oldest_text'] = name
                e['renou_oldest'] = state
    if name not in sources:
        sources.append(name)
    return {'skipped': False, 'forms': len(forms),
            'added_new': added_new, 'updated_existing': updated}


def save_index(path, idx, sources):
    out = dict(idx)
    out['__sources__'] = sources
    tmp = path + '.tmp'
    json.dump(out, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, sort_keys=True)
    os.replace(tmp, path)


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); return
    txt = args[0]
    name = state = None
    date = None
    index_path = DEFAULT_INDEX
    force = report_only = False
    i = 1
    while i < len(args):
        a = args[i]
        if a == '--name':
            name = args[i + 1]; i += 2
        elif a == '--renou':
            state = args[i + 1]; i += 2
        elif a == '--date':
            date = int(args[i + 1]); i += 2
        elif a == '--index':
            index_path = args[i + 1]; i += 2
        elif a == '--force':
            force = True; i += 1
        elif a == '--report':
            report_only = True; i += 1
        else:
            raise SystemExit('unknown option: %s' % a)
    if not name or state not in renou.STATES:
        raise SystemExit('require --name and --renou I|II|III|IV|V')

    forms = forms_in_text(open(txt, encoding='utf-8').read())
    idx, sources = load_index(index_path)
    pre = len(idx)
    res = fold(idx, sources, forms, name, state, date, force)
    if res.get('skipped'):
        print('already folded: %s (use --force to re-apply)' % name); return
    print('text: %s  → state %s  date %s' % (name, state, date))
    print('  distinct word-forms: %d' % res['forms'])
    print('  NEW form keys added: %d' % res['added_new'])
    print('  existing index lemmas that GAINED state %s: %d' % (state, res['updated_existing']))
    print('  index size: %d → %d' % (pre, len(idx)))
    if report_only:
        print('  (report only — index not written)')
        return
    save_index(index_path, idx, sources)
    print('→ %s  (sources: %s)' % (os.path.basename(index_path), ', '.join(sources)))


if __name__ == '__main__':
    main()
