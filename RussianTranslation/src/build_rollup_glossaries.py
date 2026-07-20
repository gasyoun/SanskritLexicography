#!/usr/bin/env python
"""build_rollup_glossaries.py — Stage D: lemma-level and root-level Sa->Ru glossaries.

Joins the surface glossary (Stage A) to the DCS form->lemma / lemma->root maps (Stage B)
to answer "how is <lemma> / <root> translated into Russian" across ALL its attested forms.

  lemma_glossary.*   every DCS lemma (noun stem / verb lemma) -> aggregated Ru renderings,
                     the surface forms feeding it, works/registers, upos.  (the stem/lemma layer)
  root_glossary.*    verb roots only (lemma->root via DCS root inventory) -> aggregated Ru.
                     nominal lemmas have no verbal root here (documented in typology).
  surface_dcs_misses.tsv   surface forms with NO DCS lemma -> feeds Stage C (Vidyut).
  ambiguity_homographs.tsv forms whose top DCS lemmas span different upos / are close in count.

Join key normalization: leading avagraha/apostrophe stripped on both sides ('gacCat==gacCat)
so elided-initial DCS forms match un-elided corpus forms. Homographs: the surface form's Ru
distribution is attributed to its HIGHEST-COUNT DCS lemma (primary); alternates are recorded
in the ambiguity report, not double-counted.

  python build_rollup_glossaries.py
"""
import os, re, sys, json, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
G = os.path.normpath(os.path.join(HERE, '..', 'glossary'))
MD_LEMMA = os.path.join(G, 'md', 'lemma')
MD_ROOT = os.path.join(G, 'md', 'root')

_ava = re.compile(r"^['’‘]+")
def norm(k):
    return _ava.sub('', k or '')

_reg = re.compile(r'^\d+_')
def register(work):
    return _reg.sub('', work or '')

def bucket(s):
    # case-FOLD to upper: Windows' filesystem is case-insensitive, so 'a'/'A' shard files
    # collide and truncate each other. Fold them into one shard (see build_surface_glossary).
    if not s:
        return '_'
    return s[0].upper() if re.match(r'[A-Za-z]', s[0]) else '_other'


def parse_lemma2root(lines):
    """lemma_slp1 -> root_slp1 from a dcs_lemma2root.tsv, EXCLUDING self-mapped
    `unresolved` pseudo-roots (W1.1). `lines` is any iterable incl. the header
    row. Robust whether or not build_dcs_maps already split the pseudo-roots into
    their own file: an `unresolved` how-tag is dropped here regardless."""
    l2r = {}
    it = iter(lines)
    next(it, None)                         # header
    for line in it:
        p = line.rstrip('\n').split('\t')
        if len(p) < 2:
            continue
        if len(p) >= 3 and p[2] == 'unresolved':
            continue                       # pseudo-root -> not a root
        l2r[p[0]] = p[1]
    return l2r


def homograph_alts(cands):
    """Every alternate homograph candidate worth recording for a surface form.

    cands: [(lemma, upos, count, source)] sorted by count desc; cands[0] is the
    primary. Returns [(alt_lemma, alt_upos, alt_count)] for each *later*
    candidate whose upos differs from the primary OR whose count is >= 50% of the
    primary's (W1.2 — the full trail; the earlier code inspected only cands[1],
    so a genuine 3rd+ homograph was silently dropped). Primary attribution is
    unchanged; only the alternates trail grows."""
    if len(cands) < 2:
        return []
    _plem, pupos, pcnt, _ps = cands[0]
    out = []
    for (l2, u2, c2, _s) in cands[1:]:
        if u2 != pupos or c2 >= 0.5 * pcnt:
            out.append((l2, u2, c2))
    return out


def load_maps():
    """form_norm -> [(lemma,upos,count,source)...] sorted desc; lemma -> root.

    DCS is primary; vidyut (Stage C) supplements ONLY forms DCS missed, tagged source.
    """
    f2l = collections.defaultdict(list)
    with open(os.path.join(G, 'dcs_form2lemma.tsv'), encoding='utf-8') as f:
        next(f)
        for line in f:
            p = line.rstrip('\n').split('\t')
            if len(p) < 4:
                continue
            form, lemma, upos, cnt = p[0], p[1], p[2], int(p[3])
            f2l[norm(form)].append((lemma, upos, cnt, 'dcs'))
    for k in f2l:
        f2l[k].sort(key=lambda x: -x[2])
    with open(os.path.join(G, 'dcs_lemma2root.tsv'), encoding='utf-8') as f:
        l2r = parse_lemma2root(f)          # W1.1: pseudo-roots excluded from the root layer
    dcs_keys = frozenset(f2l)          # snapshot BEFORE vidyut -> stable DCS-miss detection
    # vidyut fallback: add only for form keys DCS did not resolve
    vpath = os.path.join(G, 'vidyut_form2lemma.tsv')
    if os.path.exists(vpath):
        added = 0
        with open(vpath, encoding='utf-8') as f:
            next(f)
            for line in f:
                p = line.rstrip('\n').split('\t')
                if len(p) < 3:
                    continue
                form, lemma, pos = p[0], p[1], p[2]
                nk = norm(form)
                if nk in f2l:
                    continue
                f2l[nk].append((lemma, pos, 1, 'vidyut'))
                if pos == 'verb':          # vidyut dhatu lemma IS its own root
                    l2r.setdefault(lemma, lemma)
                added += 1
        print(f'    vidyut supplement: +{added} forms', file=sys.stderr)
    roots_set = set(l2r.values())
    lemmas_set = {lem for cands in f2l.values() for (lem, _, _, _) in cands}
    return f2l, l2r, roots_set, lemmas_set, dcs_keys


_mark = re.compile(r'[+\-]')
def marker_recover(slp1, f2l, l2r, roots_set, lemmas_set):
    """Corpus forms carry morpheme marks (A+gam = ā+√gam). Recover a lemma from the
    marked structure: (1) the joined string may already be a known form; (2) the rightmost
    element is often a bare root or lemma. Returns (lemma, upos, root_or_None) or None."""
    if '+' not in slp1 and '-' not in slp1:
        return None
    parts = [p for p in _mark.split(slp1) if p]
    if not parts:
        return None
    joined = norm(''.join(parts))
    cands = f2l.get(joined)
    if cands:                                   # e.g. A+gam -> Agam is a known form
        lemma, upos, _, _ = cands[0]
        return lemma, upos, l2r.get(lemma)
    right = norm(parts[-1])
    if right in roots_set:                      # rightmost is a bare verb root
        return right, 'verb', right
    if right in lemmas_set:                      # rightmost is a known lemma (stem)
        return right, 'noun', l2r.get(right)
    return None


def new_acc():
    return {'ru': collections.Counter(), 'forms': collections.Counter(),
            'works': collections.Counter(), 'upos': collections.Counter(),
            'lemmas': collections.Counter(), 'src': collections.Counter()}


def emit(table, path_base, md_dir, key_name, title, extra_lemmas=False):
    """Write .jsonl + .tsv + per-letter .md for a lemma/root accumulator table."""
    jf = open(path_base + '.jsonl', 'w', encoding='utf-8', newline='\n')
    tf = open(path_base + '.tsv', 'w', encoding='utf-8', newline='\n')
    tf.write(f'{key_name}\tru\tn\tn_total\tn_forms\tupos\n')
    buckets = collections.defaultdict(list)
    for key in sorted(table):
        a = table[key]
        total = sum(a['ru'].values())
        regs = collections.Counter()
        for w, c in a['works'].items():
            regs[register(w)] += c
        rec = {key_name: key, 'n': total,
               'upos': dict(a['upos'].most_common()),
               'source': dict(a['src'].most_common()),
               'n_forms': len(a['forms']),
               'forms': dict(a['forms'].most_common(50)),
               'registers': dict(regs.most_common()),
               'translations': [{'ru': ru, 'n': c} for ru, c in a['ru'].most_common()]}
        if extra_lemmas:
            rec['lemmas'] = dict(a['lemmas'].most_common())
        jf.write(json.dumps(rec, ensure_ascii=False) + '\n')
        upos = ','.join(u for u, _ in a['upos'].most_common())
        for ru, c in a['ru'].most_common():
            tf.write(f'{key}\t{ru}\t{c}\t{total}\t{len(a["forms"])}\t{upos}\n')
        buckets[bucket(key)].append((key, rec))
    jf.close(); tf.close()
    for letter, items in sorted(buckets.items()):
        with open(os.path.join(md_dir, f'{letter}.md'), 'w',
                  encoding='utf-8', newline='\n') as mf:
            mf.write(f'# {title} — `{letter}`\n\n{len(items)} entries.\n\n')
            for key, rec in items:
                head = f"### `{key}`  (n={rec['n']}, {rec['n_forms']} forms)"
                if rec['upos']:
                    head += '  ·  ' + '/'.join(rec['upos'])
                mf.write(head + '\n\n')
                for t in rec['translations'][:60]:
                    mf.write(f"- {t['ru']}  · n={t['n']}\n")
                mf.write('\n')
    return len(buckets)


def main():
    os.makedirs(MD_LEMMA, exist_ok=True)
    os.makedirs(MD_ROOT, exist_ok=True)
    print('[D] loading DCS maps...', file=sys.stderr)
    f2l, l2r, roots_set, lemmas_set, dcs_keys = load_maps()
    print(f'    {len(f2l)} normalized DCS form keys, {len(l2r)} lemma->root', file=sys.stderr)

    lemma_tab = collections.defaultdict(new_acc)
    root_tab = collections.defaultdict(new_acc)
    # DCS-miss list = stable input to the Vidyut stage (independent of whether it has run)
    dcs_misses = open(os.path.join(G, 'surface_dcs_misses.tsv'), 'w',
                      encoding='utf-8', newline='\n')
    dcs_misses.write('form_slp1\tsa\tn\ttop_ru\n')
    # unresolved = forms no tier could lemmatize (DCS + Vidyut + marker) -> typology input
    unresolved = open(os.path.join(G, 'surface_unresolved.tsv'), 'w',
                      encoding='utf-8', newline='\n')
    unresolved.write('form_slp1\tsa\tn\ttop_ru\n')
    amb = open(os.path.join(G, 'ambiguity_homographs.tsv'), 'w',
               encoding='utf-8', newline='\n')
    amb.write('form_slp1\tprimary_lemma\tprimary_upos\tprimary_n\talt_lemma\talt_upos\talt_n\n')

    n_forms = n_hit = n_miss = n_amb = n_mark = 0
    with open(os.path.join(G, 'surface_glossary.jsonl'), encoding='utf-8') as f:
        for line in f:
            d = json.loads(line)
            slp1 = d['slp1']
            nk = norm(slp1)
            top_ru = d['translations'][0]['ru'] if d['translations'] else ''
            if nk not in dcs_keys:                       # DCS could not lemmatize it
                dcs_misses.write(f"{slp1}\t{d['sa']}\t{d['n']}\t{top_ru}\n")
            cands = f2l.get(nk)
            if not cands:
                # tier 3: recover from corpus morpheme markers (A+gam = a+gam)
                rec = marker_recover(slp1, f2l, l2r, roots_set, lemmas_set)
                if rec:
                    lem, upos, root = rec
                    if root:
                        l2r.setdefault(lem, root)
                    cands = [(lem, upos, 1, 'marker')]
                    n_mark += 1
                else:
                    unresolved.write(f"{slp1}\t{d['sa']}\t{d['n']}\t{top_ru}\n")
                    n_miss += 1
                    continue
            n_hit += 1
            lemma, upos, lcnt, source = cands[0]
            # ambiguity: EVERY later candidate of a different upos or within 50%
            # count of the primary (W1.2 — the full homograph trail, not just the
            # single runner-up). Primary attribution is unchanged; alternates only.
            alts = homograph_alts(cands)
            if alts:
                for l2, u2, c2 in alts:
                    amb.write(f'{slp1}\t{lemma}\t{upos}\t{lcnt}\t{l2}\t{u2}\t{c2}\n')
                n_amb += 1
            # per-form Ru distribution and works
            ru_counts = {t['ru']: t['n'] for t in d['translations']}
            works = collections.Counter()
            for t in d['translations']:
                for w, c in t.get('works', {}).items():
                    works[w] += c
            # attribute to primary lemma
            la = lemma_tab[lemma]
            for ru, c in ru_counts.items():
                la['ru'][ru] += c
            la['forms'][slp1] += d['n']
            la['works'].update(works)
            la['upos'][upos] += d['n']
            la['src'][source] += d['n']
            # roll up to root (verbal lemmas only)
            root = l2r.get(lemma)
            if root:
                ra = root_tab[root]
                for ru, c in ru_counts.items():
                    ra['ru'][ru] += c
                ra['forms'][slp1] += d['n']
                ra['works'].update(works)
                ra['upos'][upos] += d['n']
                ra['lemmas'][lemma] += d['n']
                ra['src'][source] += d['n']
            n_forms += 1
    dcs_misses.close(); unresolved.close(); amb.close()
    print(f'[D] surface forms: hit={n_hit} (marker-recovered={n_mark}) miss={n_miss} '
          f'(hit%={100*n_hit/(n_hit+n_miss):.1f}); homograph-flagged={n_amb}',
          file=sys.stderr)
    print(f'[D] {len(lemma_tab)} lemmas, {len(root_tab)} roots', file=sys.stderr)

    nb = emit(lemma_tab, os.path.join(G, 'lemma_glossary'), MD_LEMMA,
              'lemma_slp1', 'Lemma glossary (Sa→Ru)')
    print(f'[D] lemma_glossary written ({nb} md letters)', file=sys.stderr)
    nb = emit(root_tab, os.path.join(G, 'root_glossary'), MD_ROOT,
              'root_slp1', 'Root glossary (Sa→Ru)', extra_lemmas=True)
    print(f'[D] root_glossary written ({nb} md letters)', file=sys.stderr)

if __name__ == '__main__':
    main()
