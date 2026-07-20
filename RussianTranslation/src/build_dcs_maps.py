#!/usr/bin/env python
"""build_dcs_maps.py — context-free DCS form->lemma and lemma->root maps (SLP1-keyed).

The corpus (corpus_lexicon.jsonl) stores only surface SLP1 forms with no lemma. To roll
a Sa->Ru glossary up from surface forms to lemmas and roots we need a lemmatizer. DCS
(VisualDCS dcs_full.sqlite, 5.69M annotated tokens, IAST) is the join backbone.

Because the glossary AGGREGATES over occurrences, we build a *context-free* map rather
than a per-passage alignment (which would fight 270 texts' mismatched ref schemes):

  dcs_form2lemma.tsv : form_slp1 \\t lemma_slp1 \\t upos \\t count     (all attested pairs)
  dcs_lemma2root.tsv : lemma_slp1 \\t root_slp1 \\t how                 (verb lemmas only)

Root derivation avoids preverb sandhi (uddhf<-ut, saMgam<-sam): we build DCS's own root
inventory R = simple verb lemmas (empty `preverbs`, verbal grammar) and pick the LONGEST
member of R that is a suffix of the prefixed lemma. Grounded in DCS, not blind stripping.

  python build_dcs_maps.py  [path/to/dcs_full.sqlite]
"""
import os, sys, sqlite3, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB = os.path.normpath(os.path.join(
    HERE, '..', '..', '..', 'VisualDCS', 'src', 'DCS-data-2026', 'dcs_full.sqlite'))
OUT_DIR = os.path.normpath(os.path.join(HERE, '..', 'glossary'))

_tc = {}
def to_slp1(s):
    """IAST -> SLP1 with a memo cache; returns '' on empty/None.

    indic_transliteration is imported lazily so this module (and its pure
    helper derive_lemma2root) can be imported for unit tests without the heavy
    transliteration dependency installed."""
    if not s:
        return ''
    v = _tc.get(s)
    if v is None:
        from indic_transliteration import sanscript
        try:
            v = sanscript.transliterate(s, sanscript.IAST, sanscript.SLP1)
        except Exception:
            v = ''
        _tc[s] = v
    return v


def derive_lemma2root(verb_lemmas, roots_by_len):
    """Pure lemma->root derivation, split into resolved vs pseudo-root rows.

    verb_lemmas : dict lemma_slp1 -> has_preverb (bool).
    roots_by_len: root inventory (simple verb lemmas), sorted longest-first.

    Returns (resolved, unresolved, counts):
      resolved   = [(lemma, root, how)]  how in {'self','suffix'} — real roots.
      unresolved = [(lemma, lemma, 'unresolved')] — prefixed lemmas for which no
                   root suffix matched. These self-map, so counting them as roots
                   inflates the root inventory with pseudo-roots (W1.1); the
                   caller writes them to a SEPARATE file, out of the root layer.
      counts     = Counter of how-tags (incl. 'unresolved' = excluded count).
    """
    resolved, unresolved = [], []
    counts = collections.Counter()
    for ls, has_pre in sorted(verb_lemmas.items()):
        if not has_pre:
            resolved.append((ls, ls, 'self'))          # lemma IS a root
            counts['self'] += 1
            continue
        root = ''
        for r in roots_by_len:
            if r != ls and ls.endswith(r) and len(r) >= 2:
                root = r
                break
        if root:
            resolved.append((ls, root, 'suffix'))
            counts['suffix'] += 1
        else:
            unresolved.append((ls, ls, 'unresolved'))  # pseudo-root — not a root
            counts['unresolved'] += 1
    return resolved, unresolved, counts

def is_verbal(grammar):
    """DCS grammar string marks a verb by pada codes like '1.P.', '6.Ā.'."""
    return bool(grammar) and ('P.' in grammar or 'Ā.' in grammar)

def main():
    db = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DB
    os.makedirs(OUT_DIR, exist_ok=True)
    con = sqlite3.connect(db)

    # ---- form -> lemma (distinct pairs with occurrence counts) ----
    print('[1/3] grouping token (form,lemma,upos)...', file=sys.stderr)
    f2l_path = os.path.join(OUT_DIR, 'dcs_form2lemma.tsv')
    npairs = 0
    with open(f2l_path, 'w', encoding='utf-8', newline='\n') as out:
        out.write('form_slp1\tlemma_slp1\tupos\tcount\n')
        q = ("select form, lemma, upos, count(*) c from token "
             "where form is not null and lemma is not null "
             "group by form, lemma, upos")
        for form, lemma, upos, c in con.execute(q):
            fs, ls = to_slp1(form), to_slp1(lemma)
            if not fs or not ls:
                continue
            out.write(f'{fs}\t{ls}\t{upos or ""}\t{c}\n')
            npairs += 1
    print(f'      wrote {npairs} form->lemma pairs -> {f2l_path}', file=sys.stderr)

    # ---- root inventory + lemma -> root ----
    print('[2/3] building root inventory from lemma table...', file=sys.stderr)
    # verbal lemmas: (lemma_slp1, has_preverb, grammar_verbal)
    verb_lemmas = {}   # lemma_slp1 -> has_preverb(bool)
    roots = set()      # simple verb lemmas = root inventory
    for lemma, grammar, preverbs in con.execute(
            'select lemma, grammar, preverbs from lemma'):
        if not is_verbal(grammar):
            continue
        ls = to_slp1(lemma)
        if not ls:
            continue
        has_pre = bool(preverbs and preverbs.strip())
        verb_lemmas[ls] = has_pre
        if not has_pre:
            roots.add(ls)

    # roots sorted by length desc for longest-suffix match
    roots_by_len = sorted(roots, key=len, reverse=True)
    print(f'      {len(verb_lemmas)} verb lemmas; {len(roots)} simple roots',
          file=sys.stderr)

    print('[3/3] deriving lemma -> root (longest root-suffix)...', file=sys.stderr)
    resolved, unresolved, counts = derive_lemma2root(verb_lemmas, roots_by_len)
    # Real roots (self + suffix) -> the map the rollup counts as the root layer.
    l2r_path = os.path.join(OUT_DIR, 'dcs_lemma2root.tsv')
    with open(l2r_path, 'w', encoding='utf-8', newline='\n') as out:
        out.write('lemma_slp1\troot_slp1\thow\n')
        for lemma, root, how in resolved:
            out.write(f'{lemma}\t{root}\t{how}\n')
    # W1.1: pseudo-roots (prefixed lemmas that self-map because no root suffix
    # matched) are split OUT so the rollup no longer counts them as roots. They
    # stay recorded for audit and remain reachable as lemmas in the lemma layer.
    unres_path = os.path.join(OUT_DIR, 'dcs_lemma2root_unresolved.tsv')
    with open(unres_path, 'w', encoding='utf-8', newline='\n') as out:
        out.write('lemma_slp1\troot_slp1\thow\n')
        for lemma, root, how in unresolved:
            out.write(f'{lemma}\t{root}\t{how}\n')
    print(f'      lemma->root: {dict(counts)} -> {l2r_path}', file=sys.stderr)
    print(f'      excluded {counts["unresolved"]} pseudo-roots -> {unres_path}',
          file=sys.stderr)

if __name__ == '__main__':
    main()
