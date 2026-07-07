#!/usr/bin/env python
r"""H215 Slice 2 -- composite A/B/C grader for the corpus Sa->Ru translation memory.

Slice 1 (build_tmx.py) stamps every unit grade=C. This assigns the real
"publication-grade" A/B/C stamp from the four signals MG specified:

    grade = f( qe_score,             # reference-free quality estimate, per unit
               source_weight,        # per-work / per-translator trust prior (versioned)
               alignment_confidence, # aligner confidence for the Sa<->Ru pairing
               consensus )           # >=2 works agreeing on one (segment, key)

A -- publication / hard gloss: high composite AND corroborated (consensus >=2 that
     agree) OR human-adjudicated. Usable in a print card + as a citable gloss.
B -- corroborating: decent composite, single reference, aligned. Raises confidence,
     never decides alone (the current corpus-signal role in corpus_gate.py).
C -- usage / citation only: low composite, verse-level co-occurrence, oral/noisy.

Signal provenance in THIS slice (honest about what is real vs a proxy):
  * source_weight   -- REAL, from tm_source_weights.json (hand-ranked, versioned).
  * consensus       -- REAL, computed over the whole corpus: distinct works giving a
                       rendering for the same (passage, slp1) and how far they agree.
  * qe_score        -- pluggable: `proxy` (deterministic, reference-free heuristic,
                       the default so this runs with no model) or `comet` (COMET-QE
                       via unbabel-comet if installed -- the Slice hook). NOT trained.
  * alignment_confidence -- a Slice-2 PROXY (token-count plausibility). The real
                       SimAlign / awesome-align score lands in Slice 3; this is a
                       placeholder weighted low, documented so no one mistakes it for
                       a trained aligner output.

  python tm_grade.py grade [--in P] [--qe proxy|comet] [--sample N] [--out P]
                                          corpus_lexicon.jsonl -> grades sidecar + dist
  python tm_grade.py calibrate [--gold gold/gold_set.jsonl] [--in P]
                                          grade the labelled gold set, cross-tab vs label
  python tm_grade.py selftest             deterministic fixture asserts

The grades sidecar (tuid -> grade + score + signals, JSONL) is what build_tmx.py
consumes via `--grades` to stamp real grades. It is gitignored with the corpus.

Model provenance: deterministic (proxy QE) -- no LLM call unless --qe comet is chosen
and unbabel-comet is installed. Upstream alignments were DeepSeek (build_corpus_lexicon).
"""
import argparse
import collections
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import build_tmx  # tuid(), has_cyr(), iter_units() -- reuse, don't fork the guards

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
DEFAULT_IN = os.path.join(HERE, 'corpus_lexicon.jsonl')
DEFAULT_OUT = os.path.join(ROOT, 'release', 'corpus_tm', 'corpus_tm.grades.jsonl')
DEFAULT_GOLD = os.path.join(ROOT, 'gold', 'gold_set.jsonl')
WEIGHTS_PATH = os.path.join(HERE, 'tm_source_weights.json')

GRADER_VERSION = '0.1.0'

# Composite weights (versioned; sum to 1.0). qe + source dominate; the alignment
# proxy is deliberately small until Slice 3 supplies a real aligner score.
W = {'qe': 0.35, 'source': 0.30, 'consensus': 0.20, 'align': 0.15}

# Grade thresholds (calibrated against gold/gold_set.jsonl -- see `calibrate`).
T_A = 0.70   # composite floor for A (ALSO requires corroboration/adjudication)
T_B = 0.55   # composite floor for B
CONSENSUS_MIN_REFS = 2      # A needs >=2 works ...
CONSENSUS_MIN_AGREE = 0.50  # ... and >=50% of them agreeing on the modal rendering

# H215 Slice 4: oral units start from a lower base. The composite score carries a
# fixed penalty for the higher noise floor of live interpretation (translationese,
# paraphrase, hesitation), and build_tmx.oral_cap additionally forbids A unless a
# human adjudicated it. Versioned constant so the policy is auditable.
ORAL_PENALTY = 0.15

CYR_TOKEN = re.compile(r'[Ѐ-ӿ]+')
LATIN = re.compile(r'[A-Za-zĀ-ſḀ-ỿ]')
REJECT_RU = {'нет', 'неизвестно', '—', '-', '?', '...', '…'}


# ---------------------------------------------------------------- source weight
def load_weights(path=WEIGHTS_PATH):
    if os.path.exists(path):
        return json.load(open(path, encoding='utf-8'))
    return {}


def source_weight(rec, weights):
    """Trust prior in [0,1] for the unit's provenance. Exact `work` override wins,
    then a source-family substring rule, then a per-`kind` default."""
    work = rec.get('work') or ''
    bywork = weights.get('by_work', {})
    if work in bywork:
        return float(bywork[work])
    for frag, w in weights.get('by_work_contains', {}).items():
        if frag in work:
            return float(w)
    kind = rec.get('kind') or 'translation'
    return float(weights.get('by_kind', {}).get(kind,
                 weights.get('default', 0.6)))


# ------------------------------------------------------------------- qe backend
def qe_proxy(rec):
    """Deterministic, reference-free quality estimate in [0,1]. NOT a trained
    metric -- a transparent heuristic standing in for COMET-QE until --qe comet is
    available. Rewards a clean, short, Cyrillic lexical gloss; penalizes the shapes
    the never-invent lesson taught us to distrust (latin-in-gloss, echo, run-on)."""
    ru = (rec.get('ru') or '').strip()
    sa = (rec.get('sa') or '').strip()
    if not build_tmx.has_cyr(ru) or ru == sa or ru.lower() in REJECT_RU:
        return 0.0
    score = 0.7
    toks = CYR_TOKEN.findall(ru)
    ntok = len(toks)
    # a single SLP1 headword should map to a short gloss; long run-ons are noisier
    if ntok == 0:
        return 0.0
    if 1 <= ntok <= 3:
        score += 0.2
    elif ntok <= 6:
        score += 0.05
    else:
        score -= 0.15 + min(0.2, 0.02 * (ntok - 6))
    # latin letters bleeding into the Russian gloss = transliteration/markup leak
    latin = len(LATIN.findall(ru))
    if latin:
        score -= min(0.3, 0.05 * latin)
    # cyrillic coverage of the gloss (mostly-Cyrillic is good)
    cyr_chars = sum(len(t) for t in toks)
    frac_cyr = cyr_chars / max(1, len(ru.replace(' ', '')))
    score += 0.1 * (frac_cyr - 0.5)
    return max(0.0, min(1.0, score))


def qe_comet_factory():
    """Return a COMET-QE scorer if unbabel-comet is installed, else None. The
    reference-free model scores (src, mt) pairs; we feed the printed Sanskrit
    surface as src and the Russian as mt. This is the Slice hook -- absent the
    package we fall back to qe_proxy, logged."""
    try:
        from comet import download_model, load_from_checkpoint
    except Exception:
        return None
    try:
        model = load_from_checkpoint(download_model('Unbabel/wmt22-cometkiwi-da'))
    except Exception as e:
        sys.stderr.write('qe: comet import ok but model load failed (%s); '
                         'falling back to proxy\n' % e)
        return None

    def score(rec):
        data = [{'src': rec.get('sa') or rec.get('slp1') or '',
                 'mt': rec.get('ru') or ''}]
        try:
            out = model.predict(data, batch_size=8, gpus=0, progress_bar=False)
            return max(0.0, min(1.0, float(out['scores'][0])))
        except Exception:
            return qe_proxy(rec)
    return score


def make_qe(backend):
    if backend == 'comet':
        fn = qe_comet_factory()
        if fn is not None:
            return fn, 'comet'
        sys.stderr.write('qe: unbabel-comet not available -> using deterministic proxy\n')
    return qe_proxy, 'proxy'


# ---------------------------------------------------------------- align proxy
def align_proxy(rec):
    """Placeholder alignment confidence in [0,1] pending Slice 3's real aligner.
    A single SLP1 key aligning to 1-2 Russian tokens is a confident 1:1 pairing;
    a run-on Russian phrase for one key is a weaker alignment."""
    toks = CYR_TOKEN.findall(rec.get('ru') or '')
    n = len(toks)
    if n == 0:
        return 0.0
    if n <= 2:
        return 0.9
    if n <= 4:
        return 0.7
    if n <= 8:
        return 0.5
    return 0.3


# ------------------------------------------------------------------- consensus
def norm_ru(s):
    return re.sub(r'\s+', ' ', (s or '').strip().lower())


def seg_key(rec):
    """A segment identity that is shared across different translators of the SAME
    verse+word: (normalized passage, slp1). Works differ; passage+key is the anchor."""
    return (rec.get('passage') or '', rec.get('slp1') or '')


def build_consensus(path, limit=None):
    """One pass over the corpus: seg_key -> {work: normalized_ru}. Distinct works
    only (a work repeating a gloss is not corroboration)."""
    idx = collections.defaultdict(dict)
    n = 0
    for rec in build_tmx.iter_units(path):
        idx[seg_key(rec)][rec.get('work')] = norm_ru(rec.get('ru'))
        n += 1
        if limit and n >= limit:
            break
    return idx


def consensus_signal(rec, idx):
    """Return (n_refs, consensus_score in [0,1]). n_refs = distinct works giving a
    rendering for this (passage, key); consensus_score = share agreeing with the
    modal normalized rendering (0 when only one work has it)."""
    works = idx.get(seg_key(rec))
    if not works:
        return 1, 0.0
    n = len(works)
    if n < 2:
        return n, 0.0
    modal = collections.Counter(works.values()).most_common(1)[0][1]
    return n, modal / n


# ---------------------------------------------------------------- composite grade
def grade_unit(rec, weights, qe_fn, consensus_idx, adjudicated=False,
               align_override=None):
    qe = qe_fn(rec)
    src = source_weight(rec, weights)
    # Slice 3: a real tm_align.py cross-check score (tuid -> confidence) supersedes
    # the Slice-2 token-count proxy when supplied via `grade --align <sidecar>`.
    align = align_proxy(rec) if align_override is None else align_override
    n_refs, cons = consensus_signal(rec, consensus_idx)
    modality = rec.get('modality') or 'written'
    score = (W['qe'] * qe + W['source'] * src
             + W['consensus'] * cons + W['align'] * align)
    if modality == 'oral':
        score = max(0.0, score - ORAL_PENALTY)   # lowered base for live interpretation
    corroborated = n_refs >= CONSENSUS_MIN_REFS and cons >= CONSENSUS_MIN_AGREE
    if adjudicated and qe > 0:
        grade = 'A'
    elif score >= T_A and corroborated:
        grade = 'A'
    elif score >= T_B:
        grade = 'B'
    else:
        grade = 'C'
    # oral never reaches A on automatic signals alone -- only human adjudication.
    grade = build_tmx.oral_cap(grade, modality, adjudicated=adjudicated)
    return {'grade': grade, 'score': round(score, 4),
            'qe': round(qe, 4), 'source_weight': round(src, 4),
            'alignment_confidence': round(align, 4),
            'align_source': 'proxy' if align_override is None else 'tm_align',
            'consensus': round(cons, 4), 'n_refs': n_refs, 'modality': modality}


# ------------------------------------------------------------------------- cmds
def load_align(path):
    """tuid -> real alignment_confidence from a tm_align.py sidecar. Absent path ->
    empty map -> grade_unit falls back to the Slice-2 align proxy."""
    amap = {}
    if not path:
        return amap
    if not os.path.exists(path):
        sys.exit('align sidecar not found: %s (run tm_align.py cross first)' % path)
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get('tuid') and r.get('alignment_confidence') is not None:
                amap[r['tuid']] = float(r['alignment_confidence'])
    return amap


def cmd_grade(a):
    if not os.path.exists(a.inp):
        sys.exit('input not found: %s (corpus_lexicon.jsonl is gitignored -- build it '
                 'first)' % a.inp)
    weights = load_weights()
    qe_fn, qe_name = make_qe(a.qe)
    amap = load_align(getattr(a, 'align', None))
    if amap:
        print('grade: %d real tm_align confidences loaded (supersede the align proxy)'
              % len(amap))
    print('grade: building consensus index over %s ...' % os.path.basename(a.inp),
          flush=True)
    idx = build_consensus(a.inp)
    print('grade: %d distinct (passage,key) segments indexed' % len(idx))
    dist = collections.Counter()
    align_real = 0
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    n = 0
    with open(a.out, 'w', encoding='utf-8', newline='\n') as out:
        for rec in build_tmx.iter_units(a.inp):
            tid = build_tmx.tuid(rec)
            ov = amap.get(tid)
            if ov is not None:
                align_real += 1
            g = grade_unit(rec, weights, qe_fn, idx, align_override=ov)
            dist[g['grade']] += 1
            out.write(json.dumps({'tuid': tid, **g}, ensure_ascii=False) + '\n')
            n += 1
            if a.sample and n >= a.sample:
                break
    tot = sum(dist.values()) or 1
    print('grade: %d units graded (qe=%s, align=%s) -> %s'
          % (n, qe_name, 'tm_align %d/%d' % (align_real, n) if amap else 'proxy', a.out))
    for g in 'ABC':
        print('  %s  %8d  %5.1f%%' % (g, dist[g], 100 * dist[g] / tot))
    return 0


# Gold labels split into semantically-acceptable vs defective, for separation stats.
ACCEPTABLE = {'correct', 'lemma-variant', 'proper-name'}
DEFECTIVE = {'partial', 'wrong-sense', 'hallucinated'}


def cmd_calibrate(a):
    if not os.path.exists(a.gold):
        sys.exit('gold set not found: %s' % a.gold)
    weights = load_weights()
    qe_fn, qe_name = make_qe(a.qe)
    idx = build_consensus(a.inp) if os.path.exists(a.inp) else {}
    if not idx:
        print('calibrate: corpus absent -> consensus signal unavailable, n_refs=1 '
              '(grades reflect qe+source+align only; A gate cannot fire)')
    rows = [json.loads(l) for l in open(a.gold, encoding='utf-8') if l.strip()]
    by_label = collections.defaultdict(list)
    cross = collections.defaultdict(collections.Counter)
    for r in rows:
        g = grade_unit(r, weights, qe_fn, idx)
        by_label[r.get('label')].append(g['score'])
        cross[r.get('label')][g['grade']] += 1

    print('calibrate: %d gold rows, qe=%s, weights=%s' % (len(rows), qe_name, W))
    print('  thresholds: A>=%.2f (+corrob.), B>=%.2f' % (T_A, T_B))
    print('\n  label            n   mean_score   grade dist (A/B/C)')
    print('  ' + '-' * 58)
    accept_scores, defect_scores = [], []
    for label in sorted(by_label, key=lambda x: -sum(by_label[x]) / len(by_label[x])):
        s = by_label[label]
        mean = sum(s) / len(s)
        c = cross[label]
        print('  %-15s %3d   %.3f       %d/%d/%d'
              % (label, len(s), mean, c['A'], c['B'], c['C']))
        (accept_scores if label in ACCEPTABLE else
         defect_scores if label in DEFECTIVE else []).extend(s)
    if accept_scores and defect_scores:
        ma = sum(accept_scores) / len(accept_scores)
        md = sum(defect_scores) / len(defect_scores)
        auc = _auc(accept_scores, defect_scores)
        print('\n  separation: mean(acceptable)=%.3f  mean(defective)=%.3f  '
              'gap=%.3f' % (ma, md, ma - md))
        print('  ranking AUC (acceptable scored above defective): %.3f' % auc)
        # leakage: defective rows that reached A (should be ~0)
        a_leak = sum(cross[l]['A'] for l in DEFECTIVE)
        print('  defective-in-A leakage: %d (want 0)' % a_leak)
    return 0


def _auc(pos, neg):
    """Prob. a random acceptable scores >= a random defective (ties=0.5). O(n*m),
    fine for the 320-row gold set."""
    if not pos or not neg:
        return float('nan')
    wins = ties = 0
    for p in pos:
        for q in neg:
            if p > q:
                wins += 1
            elif p == q:
                ties += 1
    return (wins + 0.5 * ties) / (len(pos) * len(neg))


# ------------------------------------------------------------------------ selftest
FIXTURE_WEIGHTS = {'default': 0.6, 'by_kind': {'translation': 0.75, 'commentary': 0.6},
                   'by_work_contains': {'bhagavadgita': 0.85}}


def selftest():
    # a clean short gloss must score higher than a run-on / latin-contaminated one
    clean = {'slp1': 'karman', 'sa': 'karma', 'ru': 'действие', 'kind': 'translation',
             'work': 'bhagavadgita-sementsov', 'passage': '2.47'}
    runon = {'slp1': 'karman', 'sa': 'karma', 'ru': 'действие обязанность долг и так '
             'далее в широком смысле', 'kind': 'translation', 'work': 'x', 'passage': '9'}
    leak = {'slp1': 'deva', 'sa': 'devaH', 'ru': 'бог deva', 'kind': 'commentary',
            'work': 'x', 'passage': '1'}
    assert qe_proxy(clean) > qe_proxy(runon) > 0, 'clean must beat run-on'
    assert qe_proxy(clean) > qe_proxy(leak), 'clean must beat latin-leak'
    assert qe_proxy({'ru': 'deva', 'sa': 'deva', 'slp1': 'deva'}) == 0.0, 'echo -> 0'

    # source weight: work-contains override beats kind default
    assert source_weight(clean, FIXTURE_WEIGHTS) == 0.85
    assert source_weight(runon, FIXTURE_WEIGHTS) == 0.75

    # consensus: two works agreeing -> corroborated; disagreeing -> not
    idx = build_consensus_from_records([
        {'passage': '2.47', 'slp1': 'karman', 'ru': 'действие', 'sa': 'k', 'work': 'a'},
        {'passage': '2.47', 'slp1': 'karman', 'ru': 'Действие', 'sa': 'k', 'work': 'b'},
        {'passage': '3.1', 'slp1': 'yoga', 'ru': 'йога', 'sa': 'y', 'work': 'a'},
        {'passage': '3.1', 'slp1': 'yoga', 'ru': 'усилие', 'sa': 'y', 'work': 'b'},
    ])
    n, c = consensus_signal({'passage': '2.47', 'slp1': 'karman'}, idx)
    assert n == 2 and c == 1.0, 'agreeing works -> full consensus, got %s/%s' % (n, c)
    n2, c2 = consensus_signal({'passage': '3.1', 'slp1': 'yoga'}, idx)
    assert n2 == 2 and c2 == 0.5, 'split works -> 0.5 consensus, got %s/%s' % (n2, c2)

    # grade: corroborated clean gloss reaches A; identical unit w/o consensus is B;
    # a defective (echo) unit is C.
    qe_fn = qe_proxy
    gA = grade_unit(clean, FIXTURE_WEIGHTS, qe_fn, idx)
    assert gA['grade'] == 'A', 'corroborated clean gloss should be A, got %s' % gA
    gB = grade_unit(clean, FIXTURE_WEIGHTS, qe_fn, {})   # no consensus index
    assert gB['grade'] == 'B', 'uncorroborated clean gloss should be B, got %s' % gB
    gC = grade_unit(leak, FIXTURE_WEIGHTS, qe_fn, {})
    assert gC['grade'] in ('B', 'C') and gC['grade'] != 'A', 'leak must not be A'
    # adjudicated overlay forces A
    gAdj = grade_unit(runon, FIXTURE_WEIGHTS, qe_fn, {}, adjudicated=True)
    assert gAdj['grade'] == 'A', 'adjudicated unit should be A'

    # H215 Slice 4: an oral unit gets the lowered base -- same clean corroborated
    # gloss that reaches A when written is capped at B when oral, and its composite
    # carries the penalty; human adjudication still lifts it to A.
    oral = dict(clean, modality='oral')
    gOral = grade_unit(oral, FIXTURE_WEIGHTS, qe_fn, idx)
    assert gA['grade'] == 'A' and gOral['grade'] == 'B', \
        'oral corroborated gloss must cap at B, got %s (written was %s)' % (gOral['grade'], gA['grade'])
    assert gOral['score'] < gA['score'], 'oral penalty must lower the composite'
    assert gOral['modality'] == 'oral'
    gOralAdj = grade_unit(oral, FIXTURE_WEIGHTS, qe_fn, idx, adjudicated=True)
    assert gOralAdj['grade'] == 'A', 'human-adjudicated oral unit may reach A'
    print('tm_grade selftest OK -- qe ordering, source override, consensus, grade gates, oral cap')
    return 0


def build_consensus_from_records(recs):
    idx = collections.defaultdict(dict)
    for r in recs:
        idx[seg_key(r)][r.get('work')] = norm_ru(r.get('ru'))
    return idx


def main():
    ap = argparse.ArgumentParser(description='Composite A/B/C grader for the Sa->Ru TM (H215 Slice 2)')
    sub = ap.add_subparsers(dest='cmd', required=True)

    g = sub.add_parser('grade', help='corpus_lexicon.jsonl -> grades sidecar + distribution')
    g.add_argument('--in', dest='inp', default=DEFAULT_IN)
    g.add_argument('--out', dest='out', default=DEFAULT_OUT)
    g.add_argument('--qe', choices=['proxy', 'comet'], default='proxy')
    g.add_argument('--align', default=None,
                   help='tm_align.py sidecar -> real alignment_confidence per unit '
                        '(supersedes the Slice-2 proxy)')
    g.add_argument('--sample', type=int, default=None)

    c = sub.add_parser('calibrate', help='grade the labelled gold set, cross-tab vs label')
    c.add_argument('--gold', default=DEFAULT_GOLD)
    c.add_argument('--in', dest='inp', default=DEFAULT_IN)
    c.add_argument('--qe', choices=['proxy', 'comet'], default='proxy')

    sub.add_parser('selftest', help='deterministic fixture asserts')

    a = ap.parse_args()
    if a.cmd == 'grade':
        return cmd_grade(a)
    if a.cmd == 'calibrate':
        return cmd_calibrate(a)
    if a.cmd == 'selftest':
        return selftest()
    return 1


if __name__ == '__main__':
    sys.exit(main())
