#!/usr/bin/env python
"""Recall-side gold sampling for the corpus lexicon (companion to gold_sample.py).

gold_sample.py froze the PRECISION sample (are harvested pairs right?). This
script prepares the RECALL side: of the Sanskrit content words in a verse pair
the harvest DID process, how many made it into corpus_lexicon.jsonl?

  python gold_recall_sample.py coverage        group-level coverage: eligible
                                               corpus groups vs groups with >=1
                                               lexicon row (deterministic scan)
  python gold_recall_sample.py sample [N]      freeze a stratified sample of N
                                               processed groups (default 32,
                                               balanced across period; seed=42)
                                               -> recall_sample.jsonl (gitignored)

CORPUS_LEXICON_PATH overrides the lexicon location (the 290 MB jsonl is
gitignored, so a worktree checkout points this at the main clone's copy).

Per sampled group the working file carries the source Sanskrit verse, the
Russian translation, the group's harvested pairs, and a whitespace token list
of the Sanskrit text. Adjudication (human or frontier-model) labels every
token; the committed minimal result (tokens + labels, no bulk text) lands in
gold/recall_set.jsonl.
"""
import json, os, random, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import corpus_harvest as ch

HERE = os.path.dirname(os.path.abspath(__file__))
SM = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'SamudraManthanam',
                                   'web', 'corpus_builder', 'jsonl'))
LEX = os.environ.get('CORPUS_LEXICON_PATH') or os.path.join(HERE, 'corpus_lexicon.jsonl')
STRATA = json.load(open(os.path.join(HERE, 'corpus_strata.json'), encoding='utf-8'))
OUT = os.path.join(HERE, 'recall_sample.jsonl')
SEED = 42

CYR = re.compile('[Ѐ-ӿ]')
# strip daṇḍas, verse numbers, punctuation; keep IAST letters + avagraha
TOKEN_JUNK = re.compile(r"[।॥\d()\[\],;:!?«»\"']+")


def sa_tokens(text):
    toks = []
    for t in (text or '').split():
        t = TOKEN_JUNK.sub('', t).strip('-–—.')
        if t and not t.isdigit():
            toks.append(t)
    return toks


def lexicon_groups():
    """group -> {'period','work','pairs':[{sa,ru,slp1,kind}…]}."""
    groups = {}
    for line in open(LEX, encoding='utf-8'):
        try:
            r = json.loads(line)
        except Exception:
            continue
        g = r.get('group')
        if not g:
            continue
        d = groups.setdefault(g, {'work': r.get('work'),
                                  'period': ch.norm_period(r.get('period')),
                                  'pairs': []})
        d['pairs'].append({'sa': r.get('sa'), 'ru': r.get('ru'),
                           'slp1': r.get('slp1'), 'kind': r.get('kind')})
    return groups


def eligible_groups():
    """work -> set(groups) with a Sanskrit seg AND a Cyrillic-bearing ru seg."""
    per_work = {}
    for work in sorted(STRATA):
        f = os.path.join(SM, work + '.jsonl')
        if not os.path.exists(f):
            continue
        sa, ru = set(), set()
        for line in open(f, encoding='utf-8'):
            try:
                e = json.loads(line)
            except Exception:
                continue
            seg = e.get('seg', '')
            if seg == 'sa' and (e.get('text') or '').strip():
                sa.add(e.get('group'))
            elif seg == 'ru' and CYR.search(e.get('text') or ''):
                ru.add(e.get('group'))
        per_work[work] = sa & ru
    return per_work


def coverage():
    lex = lexicon_groups()
    processed_by_work = collections.defaultdict(set)
    for g, d in lex.items():
        processed_by_work[d['work']].add(g)
    elig = eligible_groups()
    per_period = collections.defaultdict(lambda: [0, 0])  # eligible, processed
    tot_e = tot_p = 0
    for work, groups in sorted(elig.items()):
        period = ch.norm_period(STRATA[work].get('period'))
        p = len(groups & processed_by_work.get(work, set()))
        per_period[period][0] += len(groups)
        per_period[period][1] += p
        tot_e += len(groups)
        tot_p += p
    print('period\teligible\tprocessed\tcoverage')
    for period in sorted(per_period, key=lambda x: ch.PERIOD_ORDER.get(x, 9)):
        e, p = per_period[period]
        print(f'{period}\t{e}\t{p}\t{p/e:.1%}' if e else f'{period}\t0\t0\t-')
    print(f'TOTAL\t{tot_e}\t{tot_p}\t{tot_p/tot_e:.1%}')
    orphan = sorted(w for w in processed_by_work if w not in elig)
    if orphan:
        print(f'(lexicon works outside strata/corpus: {orphan})')


def load_src(work):
    d = collections.defaultdict(dict)
    f = os.path.join(SM, work + '.jsonl')
    if os.path.exists(f):
        for line in open(f, encoding='utf-8'):
            try:
                e = json.loads(line)
            except Exception:
                continue
            g = e.get('group')
            seg = e.get('seg', '')
            if seg == 'sa':
                d[g]['sa'] = e.get('text')
            elif seg == 'ru':
                d[g]['ru'] = e.get('text')
    return d


def sample(n):
    lex = lexicon_groups()
    # recall is measured on the translation layer: keep groups with >=1
    # translation-kind pair (commentary alignment has its own precision stratum)
    cells = collections.defaultdict(list)
    for g, d in lex.items():
        if any(p['kind'] == 'translation' for p in d['pairs']):
            cells[d['period']].append(g)
    random.seed(SEED)
    per = max(1, n // len(cells))
    picked = []
    for period in sorted(cells, key=lambda x: ch.PERIOD_ORDER.get(x, 9)):
        picked += random.sample(sorted(cells[period]), min(per, len(cells[period])))
    src_cache = {}
    rows = []
    for g in picked:
        d = lex[g]
        work = d['work']
        if work not in src_cache:
            src_cache[work] = load_src(work)
        src = src_cache[work].get(g, {})
        rows.append({
            'group': g, 'work': work, 'period': d['period'],
            'src_sa': src.get('sa'), 'src_ru': src.get('ru'),
            'sa_tokens': sa_tokens(src.get('sa')),
            'pairs': [p for p in d['pairs'] if p['kind'] == 'translation'],
        })
    with open(OUT, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    n_tok = sum(len(r['sa_tokens']) for r in rows)
    print(f'wrote {len(rows)} groups / {n_tok} Sanskrit tokens -> {OUT}')
    for period in sorted(cells, key=lambda x: ch.PERIOD_ORDER.get(x, 9)):
        k = sum(1 for r in rows if r['period'] == period)
        print(f'  {period}: {k} groups (population {len(cells[period])})')


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ('coverage', 'sample'):
        sys.exit(__doc__)
    if sys.argv[1] == 'coverage':
        coverage()
    else:
        sample(int(sys.argv[2]) if len(sys.argv) > 2 else 32)


if __name__ == '__main__':
    main()
