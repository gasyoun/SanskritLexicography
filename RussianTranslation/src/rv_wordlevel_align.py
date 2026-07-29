#!/usr/bin/env python
r"""rv_wordlevel_align.py -- layer B of ruling R5 (H1844 C4, IMPLEMENTATION step 10).

For a Rigvedic token and a given translation of its stanza, propose the span of that
translation which renders it, with a per-pair confidence.

**No new aligner is written here** (ARCHITECTURE Sec.4, W1.9). This module parameterises
the committed SimAlign-style aligner in
[`src/tm_align.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tm_align.py)
(`embed_aligner_factory` -- contextual subword embeddings, token-level max-pool, mutual
argmax links) for the token -> span case. The alignment model is a recorded PARAMETER
(`--model`, default the factory's own `bert-base-multilingual-cased`), never a silent
re-tune.

Layer B is ADVISORY by construction (R5 / ARCHITECTURE Sec.5): every emitted row carries
`confidence` and `low_confidence`, and nothing here is ever written into reviewed pwg_ru
data. The only file this enriches is the layer's own `rv_lemma_occurrences.jsonl`.

Emission rule (IMPLEMENTATION step 10 marked defaults):
  * translation absent/empty, or no candidate words   -> no row
  * best confidence < ALIGN_GATE                      -> no row ("absence is a cleaner
                                                         signal than noise")
  * otherwise                                         -> row, `low_confidence` set when the
                                                         aligner's own mutual-argmax link
                                                         does not confirm the pairing
The FULL observed confidence distribution -- including the rows the gate dropped -- is
written to the run log, because the marked default is to *record* the distribution and
re-calibrate only against the step-11 gold, as a separate evidence-backed step.

  python src/rv_wordlevel_align.py align --stanzas 150
  python src/rv_wordlevel_align.py enrich
  python src/rv_wordlevel_align.py selftest
"""
import argparse
import collections
import json
import os
import random
import re
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT_ROOT = os.path.normpath(os.path.join(HERE, '..'))
PWG_RU_DIR = os.path.join(RT_ROOT, 'pwg_ru')
RUN_DIR = os.path.join(PWG_RU_DIR, 'h1844')

STANZA_PATH = os.path.join(PWG_RU_DIR, 'rv_stanza_translations.jsonl')
LEMMA_PATH = os.path.join(PWG_RU_DIR, 'rv_lemma_occurrences.jsonl')
WORDLEVEL_OUT = os.path.join(PWG_RU_DIR, 'rv_wordlevel.jsonl')
RUN_LOG = os.path.join(RUN_DIR, 'wordlevel_run_log.md')

TRANSLATORS = [
    'grassmann_de_1876', 'geldner_de_1951', 'elizarenkova_ru_1989', 'griffith_en_1896',
]
# Target language per translator -- the per-language precision bar of R14 is scored over
# these buckets (de is carried by two translators, ru and en by one each).
TRANSLATOR_TARGET = {
    'grassmann_de_1876': 'de', 'geldner_de_1951': 'de',
    'elizarenkova_ru_1989': 'ru', 'griffith_en_1896': 'en',
}

# H1457 A3 calibrated gate, carried over unchanged. ALIGN_GATE.md is explicit that this
# was calibrated on 30 rows of mined running text with exactly ONE known negative, and
# LABSE_ALIGN.md records the embedding backend being weak on transliterated Sanskrit.
# The marked default is to KEEP 0.20 for the first pass and record the distribution --
# re-calibration belongs to a separate, evidence-backed step against the step-11 gold.
ALIGN_GATE = 0.20

WORD_RE = re.compile(r'[^\W\d_]+', re.UNICODE)
DEFAULT_STANZAS = 150
DEFAULT_SEED = 1844


def tokenize_translation(text):
    return WORD_RE.findall(text or '')


# --------------------------------------------------------------------- loading
def load_stanzas():
    rows = {}
    with open(STANZA_PATH, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rec = json.loads(line)
                rows[rec['location']] = rec
    return rows


def load_stanza_tokens():
    """location -> [ {token_index, form, lemma}, ... ] ordered by token_index.

    Rebuilt from the layer's own rv_lemma_occurrences.jsonl rather than re-reading the
    VedaWeb feed -- same information, and it keeps this step inside the fence (R17).
    """
    by_loc = collections.defaultdict(list)
    with open(LEMMA_PATH, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            lemma = rec['lemma']
            for occ in rec['occurrences']:
                by_loc[occ['location']].append({
                    'token_index': occ['token_index'], 'form': occ['form'], 'lemma': lemma,
                })
    for loc in by_loc:
        by_loc[loc].sort(key=lambda t: t['token_index'])
    return by_loc


def sample_locations(stanza_tokens, stanzas, n, seed):
    """Stratified by mandala, proportional, seeded -- same discipline as the pilot
    sampler in rv_divergence_type.py."""
    by_mandala = collections.defaultdict(list)
    for loc in stanza_tokens:
        by_mandala[stanzas[loc]['mandala']].append(loc)
    total = sum(len(v) for v in by_mandala.values())
    quotas, remainders = {}, []
    for m in sorted(by_mandala):
        exact = n * len(by_mandala[m]) / total
        quotas[m] = int(exact)
        remainders.append((exact - int(exact), m))
    for _, m in sorted(remainders, reverse=True)[:n - sum(quotas.values())]:
        quotas[m] += 1
    rng = random.Random(seed)
    picked = []
    for m in sorted(by_mandala):
        pool = sorted(by_mandala[m])
        picked.extend(rng.sample(pool, min(quotas[m], len(pool))))
    return sorted(picked, key=lambda l: [int(x) for x in l.split('.')])


# ------------------------------------------------------------------- alignment
def align_stanza(aligner, sa_tokens, translation_words):
    """-> [ {token_index, best_j, confidence, mutual} ] for every sa token, unfiltered.

    One call into the committed aligner; the filtering/gating happens in the caller so
    the run log can see the pre-gate distribution.
    """
    sa_words = [t['form'] for t in sa_tokens]
    if not sa_words or not translation_words:
        return []
    sim, links = aligner(sa_words, translation_words)
    if not sim:
        return []
    out = []
    for i, t in enumerate(sa_tokens):
        row = sim[i]
        best_j = max(range(len(row)), key=lambda j: row[j])
        out.append({'token_index': t['token_index'], 'form': t['form'], 'lemma': t['lemma'],
                    'best_j': best_j, 'confidence': float(row[best_j]),
                    'mutual': (i, best_j) in links})
    return out


def cmd_align(a):
    import tm_align

    stanzas = load_stanzas()
    stanza_tokens = load_stanza_tokens()
    locations = sample_locations(stanza_tokens, stanzas, a.stanzas, a.seed)
    print('align: %d stanzas selected (seed %d)' % (len(locations), a.seed))

    aligner = tm_align.embed_aligner_factory(a.model)
    if aligner is None:
        sys.exit('align: the committed embedding aligner is unavailable in this environment '
                 '(transformers/torch or the model failed to load). Layer B cannot run; '
                 'spine A is unaffected.')
    print('align: aligner ready (model=%s, layer=%s)' % (aligner.model_id, aligner.layer))

    os.makedirs(RUN_DIR, exist_ok=True)
    dist_all = collections.Counter()
    dist_by_target = collections.defaultdict(collections.Counter)
    emitted = dropped = skipped_absent = 0
    mutual_count = 0
    t0 = time.time()

    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    with open(a.out, 'w', encoding='utf-8', newline='\n') as out:
        for n, loc in enumerate(locations, 1):
            sa_tokens = stanza_tokens[loc]
            for translator in TRANSLATORS:
                t = stanzas[loc]['translations'][translator]
                if t['status'] != 'present':
                    skipped_absent += 1
                    continue
                words = tokenize_translation(t['text'])
                target = TRANSLATOR_TARGET[translator]
                for r in align_stanza(aligner, sa_tokens, words):
                    bucket = _bucket(r['confidence'])
                    dist_all[bucket] += 1
                    dist_by_target[target][bucket] += 1
                    if r['confidence'] < ALIGN_GATE:
                        dropped += 1
                        continue
                    if r['mutual']:
                        mutual_count += 1
                    out.write(json.dumps({
                        'location': loc, 'token_index': r['token_index'],
                        'form': r['form'], 'lemma': r['lemma'],
                        'translator': translator, 'target': target,
                        'span': words[r['best_j']], 'span_word_index': r['best_j'],
                        'confidence': round(r['confidence'], 4),
                        'low_confidence': not r['mutual'],
                        'aligner_model': aligner.model_id, 'aligner_layer': aligner.layer,
                    }, ensure_ascii=False) + '\n')
                    emitted += 1
            if n % 10 == 0 or n == len(locations):
                el = time.time() - t0
                print('  %d/%d stanzas  %.1fs elapsed  %.1fs/stanza  %d rows'
                      % (n, len(locations), el, el / n, emitted))

    total = sum(dist_all.values())
    print('align: %d candidate alignments, %d emitted, %d dropped below the %.2f gate'
          % (total, emitted, dropped, ALIGN_GATE))
    print('  mutual-argmax confirmed: %d of %d emitted (%.1f%%)'
          % (mutual_count, emitted, 100.0 * mutual_count / emitted if emitted else 0))
    _write_run_log(a, aligner, locations, total, emitted, dropped, skipped_absent,
                   mutual_count, dist_all, dist_by_target, time.time() - t0)
    print('  rows -> %s' % a.out)
    print('  run log -> %s' % a.run_log)
    return 0


BUCKETS = ['[0,0.1)', '[0.1,0.2)', '[0.2,0.3)', '[0.3,0.4)', '[0.4,0.5)',
           '[0.5,0.6)', '[0.6,0.7)', '[0.7,0.8)', '[0.8,0.9)', '[0.9,1.0]']


def _bucket(c):
    if c >= 0.9:
        return BUCKETS[-1]
    idx = max(0, min(9, int(c * 10)))
    return BUCKETS[idx]


def _write_run_log(a, aligner, locations, total, emitted, dropped, skipped_absent,
                   mutual_count, dist_all, dist_by_target, elapsed):
    lines = []
    lines.append('# rv_wordlevel_align.py run log (H1844 step 10, layer B)')
    lines.append('')
    lines.append('_Created: 29-07-2026 · Last updated: 29-07-2026_')
    lines.append('')
    lines.append('Aligner: the committed `tm_align.embed_aligner_factory` (SimAlign-style '
                 'contextual subword alignment), model `%s`, hidden layer %s. No new aligner '
                 'was written (ARCHITECTURE §4, W1.9).' % (aligner.model_id, aligner.layer))
    lines.append('')
    lines.append('| Quantity | Value |')
    lines.append('|---|--:|')
    lines.append('| Stanzas aligned | %d |' % len(locations))
    lines.append('| Sampling | stratified by maṇḍala, proportional, seed %d |' % a.seed)
    lines.append('| Translator-stanza pairs skipped (not `present`) | %d |' % skipped_absent)
    lines.append('| Candidate token→span alignments | %d |' % total)
    lines.append('| Emitted (confidence ≥ %.2f) | %d |' % (ALIGN_GATE, emitted))
    lines.append('| Dropped below the gate | %d |' % dropped)
    lines.append('| Mutual-argmax confirmed, of emitted | %d (%.1f%%) |'
                 % (mutual_count, 100.0 * mutual_count / emitted if emitted else 0))
    lines.append('| Wall clock | %.1f s (%.2f s/stanza) |'
                 % (elapsed, elapsed / len(locations) if locations else 0))
    lines.append('')
    lines.append('## Observed confidence distribution (pre-gate)')
    lines.append('')
    lines.append('Recorded per the step-10 marked default: keep the 0.20 gate for the first '
                 'pass, record what the distribution actually looks like, and re-calibrate '
                 'only against the step-11 gold as a separate evidence-backed step.')
    lines.append('')
    lines.append('| Bucket | All | de | ru | en |')
    lines.append('|---|--:|--:|--:|--:|')
    for b in BUCKETS:
        lines.append('| %s | %d | %d | %d | %d |'
                     % (b, dist_all[b], dist_by_target['de'][b],
                        dist_by_target['ru'][b], dist_by_target['en'][b]))
    lines.append('')
    lines.append('_Dr. Mārcis Gasūns_')
    lines.append('')
    path = getattr(a, 'run_log', RUN_LOG)
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))


# --------------------------------------------------------------------- enrich
def cmd_enrich(a):
    """Fill rv_lemma_occurrences.jsonl's `wordlevel` field from rv_wordlevel.jsonl.

    Rewritten atomically via a temp file; the spine is generated, never hand-edited
    (ARCHITECTURE §5).
    """
    if not os.path.exists(WORDLEVEL_OUT):
        sys.exit('no %s -- run `align` first' % WORDLEVEL_OUT)
    by_key = collections.defaultdict(dict)
    with open(WORDLEVEL_OUT, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            by_key[(r['location'], r['token_index'])][r['translator']] = {
                'span': r['span'], 'confidence': r['confidence'],
                'low_confidence': r['low_confidence'],
            }
    tmp = LEMMA_PATH + '.tmp'
    filled = 0
    with open(LEMMA_PATH, encoding='utf-8') as src, \
            open(tmp, 'w', encoding='utf-8', newline='\n') as dst:
        for line in src:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            for occ in rec['occurrences']:
                hit = by_key.get((occ['location'], occ['token_index']))
                if hit:
                    occ['wordlevel'] = hit
                    filled += 1
            dst.write(json.dumps(rec, ensure_ascii=False) + '\n')
    os.replace(tmp, LEMMA_PATH)
    print('enrich: %d occurrences given a wordlevel block -> %s' % (filled, LEMMA_PATH))
    return 0


# ------------------------------------------------------------------- selftest
def selftest():
    assert tokenize_translation('Agni, den Priester!') == ['Agni', 'den', 'Priester']
    assert tokenize_translation('Агни призываю я') == ['Агни', 'призываю', 'я']
    assert tokenize_translation('') == []
    assert tokenize_translation(None) == []

    assert _bucket(0.0) == '[0,0.1)'
    assert _bucket(0.25) == '[0.2,0.3)'
    assert _bucket(0.95) == '[0.9,1.0]'
    assert _bucket(1.0) == '[0.9,1.0]'

    # a stub aligner: token i prefers translation word i, similarity decreasing
    def stub(sa_words, tr_words):
        sim = [[1.0 - 0.3 * abs(i - j) for j in range(len(tr_words))]
               for i in range(len(sa_words))]
        links = {(i, i) for i in range(min(len(sa_words), len(tr_words)))}
        return sim, links

    toks = [{'token_index': 0, 'form': 'agním', 'lemma': 'agní-'},
            {'token_index': 1, 'form': 'īḷe', 'lemma': 'īḍ-'}]
    rows = align_stanza(stub, toks, ['Agni', 'preise'])
    assert len(rows) == 2
    assert rows[0]['best_j'] == 0 and rows[1]['best_j'] == 1
    assert all(r['mutual'] for r in rows)
    assert rows[0]['confidence'] == 1.0

    # empty sides produce nothing rather than a guess (step-10 marked default)
    assert align_stanza(stub, toks, []) == []
    assert align_stanza(stub, [], ['Agni']) == []

    assert set(TRANSLATOR_TARGET.values()) == {'de', 'ru', 'en'}
    assert len(TRANSLATORS) == 4
    print('rv_wordlevel_align selftest OK -- tokenizer (Latin+Cyrillic), confidence '
          'buckets, argmax/mutual extraction, empty-side abstention, target map')
    return 0


def main():
    ap = argparse.ArgumentParser(description='RV word-level layer B (H1844 step 10)')
    sub = ap.add_subparsers(dest='cmd', required=True)

    al = sub.add_parser('align', help='token -> span alignment over a seeded stanza sample')
    al.add_argument('--stanzas', type=int, default=DEFAULT_STANZAS)
    al.add_argument('--seed', type=int, default=DEFAULT_SEED)
    al.add_argument('--model', default=None,
                    help='alignment model id (default: the committed factory default)')
    al.add_argument('--out', default=WORDLEVEL_OUT,
                    help='output path; give each model arm its own file so a pilot can '
                         'compare alignment models without overwriting the other arm')
    al.add_argument('--run-log', default=RUN_LOG)

    sub.add_parser('enrich', help='write wordlevel blocks into rv_lemma_occurrences.jsonl')
    sub.add_parser('selftest', help='deterministic asserts, no model, no network')

    a = ap.parse_args()
    if a.cmd == 'align':
        return cmd_align(a)
    if a.cmd == 'enrich':
        return cmd_enrich(a)
    return selftest()


if __name__ == '__main__':
    sys.exit(main())
