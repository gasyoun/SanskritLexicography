#!/usr/bin/env python
r"""H215 Slice 3 (part 2) -- word-alignment cross-check on the DeepSeek L1 pairs.

Slice 2's `alignment_confidence` was an honest PROXY (token-count plausibility),
weighted low, with a note: "the real SimAlign / awesome-align score lands in
Slice 3". This is that lander. For every DeepSeek L1 word-pair (slp1 <-> ru) it
asks an INDEPENDENT aligner "does this pairing actually hold in the parent verse?"
and writes a real per-unit `alignment_confidence` that tm_grade.py then consumes
in place of the proxy.

Two ideas of "confidence", one join key (`group`, from build_l0.py's L0 layer):

  proxy  (default, deterministic, runs on the FULL corpus, no model)
      GROUNDING cross-check against the L0 verse:
        sa_ground -- is the DeepSeek Sanskrit word actually a token of the L0
                     Sanskrit verse?  (form_key exact -> 1.0; stem/prefix -> 0.6)
        ru_ground -- are the DeepSeek Russian rendering's stems present in the L0
                     Russian segment?  (fraction of rendering stems found)
      confidence = 0.5*sa_ground + 0.5*ru_ground.  A hallucinated pair whose
      Sanskrit is not in the verse, or whose Russian is not in the translation,
      scores low -- exactly the signal grading wants, and strictly better than
      Slice 2's shape-only proxy.

  embed  (SimAlign-style, needs `transformers` + a multilingual model)
      Jalili Sabet et al. 2020: cosine-similarity of contextual subword
      embeddings between the sa tokens and ru tokens of the verse, argmax/itermax
      links. Per-unit confidence = the model's own max cosine between the sa token
      matching `slp1` and the ru tokens matching the rendering; plus whether the
      argmax alignment agrees. Absent the package/model we fall back to `proxy`,
      logged (same pattern as tm_grade.py's --qe comet hook).

  python tm_align.py cross    [--l0 P] [--l1 P] [--backend proxy|embed]
                              [--sample N] [--out sidecar.jsonl]
  python tm_align.py agree    [--align sidecar.jsonl]   grade-facing summary + dist
  python tm_align.py selftest                           deterministic asserts (no model)

Sidecar row: {tuid, group, slp1, kind, alignment_confidence, sa_ground, ru_ground,
              backend}. `tuid` is build_tmx.tuid(l1_row) so it joins the grade
sidecar and the TMX. Output lives under the gitignored release/corpus_tm/ (rights).

Model provenance: `proxy` is deterministic, no LLM. `embed` runs a multilingual
masked-LM (e.g. bert-base-multilingual-cased / XLM-R) locally -- record the exact
model id from the run log when you use it.
"""
import argparse
import collections
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import build_tmx        # tuid(), has_cyr(), iter_units() -- reuse the guards
import build_l0         # sa_tokens(), clean_* (L0 shape authority)
import corpus_gate as cg  # form_key(), ru_tokens() -- the canonical normalizers

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
DEFAULT_L0 = os.path.join(ROOT, 'release', 'corpus_tm', 'corpus_l0.jsonl')
DEFAULT_L1 = os.path.join(HERE, 'corpus_lexicon.jsonl')
DEFAULT_OUT = os.path.join(ROOT, 'release', 'corpus_tm', 'corpus_tm.align.jsonl')

VERSION = '0.1.0'
PREFIX_MIN = 4       # min shared prefix length for a stem/prefix sa match
SA_PARTIAL = 0.6     # confidence credit for a stem/prefix (not exact) sa match


# ------------------------------------------------------------------- L0 index
def _ru_stems(text):
    """Stemmed Russian content tokens, reusing corpus_gate's canonical tokenizer
    (drops markup/placeholders and a light inflectional ending)."""
    return cg.ru_tokens(text or '')


def load_l0_index(path):
    """group -> {'sa': set(form_key sa tokens), 'sa_pref': sorted list of tokens,
                 'ru_tr': set(ru stems), 'ru_comm': set(ru stems)}.
    Light: ~100k groups, sets of short strings."""
    if not os.path.exists(path):
        sys.exit('L0 file not found: %s (run build_l0.py build first)' % path)
    idx = {}
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            g = r.get('group')
            if not g:
                continue
            e = idx.setdefault(g, {'sa': set(), 'ru_tr': set(), 'ru_comm': set()})
            for t in build_l0.sa_tokens(r.get('slp1') or ''):
                fk = cg.form_key(t)
                if fk:
                    e['sa'].add(fk)
            stems = _ru_stems(r.get('ru'))
            if r.get('kind') == 'commentary':
                e['ru_comm'] |= stems
            else:
                e['ru_tr'] |= stems
    # precompute a sorted token list per group for prefix matching
    for e in idx.values():
        e['sa_pref'] = sorted(e['sa'])
    return idx


# ------------------------------------------------------------------- proxy backend
def sa_ground(l1_slp1, l0_entry):
    """Is the DeepSeek Sanskrit word grounded in the L0 verse? 1.0 exact form_key
    hit; SA_PARTIAL if it is a >=PREFIX_MIN-char prefix of (or contains) a verse
    token -- sandhi/inflection means the citation form rarely equals the surface
    form exactly, so a stem match is real but discounted; 0.0 if absent."""
    key = cg.form_key(l1_slp1 or '')
    if not key or not l0_entry:
        return 0.0
    sa = l0_entry['sa']
    if key in sa:
        return 1.0
    # Sandhi/inflection: the citation form (e.g. `karman`) and the verse surface
    # (`karmaRi`) share a STEM prefix, not a whole-token prefix -- credit a shared
    # leading run of >=PREFIX_MIN chars (discounted; not an exact hit).
    if len(key) >= PREFIX_MIN:
        for tok in l0_entry['sa_pref']:
            if _shared_prefix(key, tok) >= PREFIX_MIN:
                return SA_PARTIAL
    return 0.0


def _shared_prefix(a, b):
    n = 0
    for ca, cb in zip(a, b):
        if ca != cb:
            break
        n += 1
    return n


def ru_ground(l1_ru, l0_entry, kind):
    """Fraction of the DeepSeek Russian rendering's stems that appear in the L0
    Russian segment of the matching kind (translation vs commentary pool)."""
    if not l0_entry:
        return 0.0
    want = _ru_stems(l1_ru)
    if not want:
        return 0.0
    pool = l0_entry['ru_comm'] if kind == 'commentary' else l0_entry['ru_tr']
    if not pool and kind == 'commentary':   # some notes were dropped; fall back
        pool = l0_entry['ru_tr']
    hit = sum(1 for s in want if s in pool)
    return hit / len(want)


def proxy_confidence(l1, l0_entry):
    sg = sa_ground(l1.get('slp1'), l0_entry)
    rg = ru_ground(l1.get('ru'), l0_entry, l1.get('kind') or 'translation')
    return {'alignment_confidence': round(0.5 * sg + 0.5 * rg, 4),
            'sa_ground': round(sg, 4), 'ru_ground': round(rg, 4),
            'backend': 'proxy'}


# ------------------------------------------------------------------- embed backend
def embed_aligner_factory(model_id=None):
    """Return a SimAlign-style aligner over contextual subword embeddings, or None
    if transformers/torch or the model are unavailable (then caller uses proxy).
    Cosine(subword_i, subword_j) -> token-level max-pool -> argmax + itermax links
    and a per-(i,j) similarity used as the confidence. This IS the SimAlign method
    (Jalili Sabet 2020), implemented directly on transformers so we do not depend
    on the unmaintained `simalign` package."""
    model_id = model_id or os.environ.get('TM_ALIGN_MODEL', 'bert-base-multilingual-cased')
    try:
        import torch
        from transformers import AutoModel, AutoTokenizer
    except Exception as e:
        sys.stderr.write('embed: transformers/torch unavailable (%s) -> proxy\n' % e)
        return None
    try:
        tok = AutoTokenizer.from_pretrained(model_id)
        model = AutoModel.from_pretrained(model_id, output_hidden_states=True)
        model.eval()
    except Exception as e:
        sys.stderr.write('embed: model %s load failed (%s) -> proxy\n' % (model_id, e))
        return None

    LAYER = int(os.environ.get('TM_ALIGN_LAYER', '8'))

    def _token_embeds(words):
        """Contextual embedding per input word: mean of its subword vectors at
        hidden layer LAYER. Returns a (len(words), dim) tensor."""
        enc = tok(words, is_split_into_words=True, return_tensors='pt',
                  truncation=True, max_length=256)
        with torch.no_grad():
            hs = model(**enc).hidden_states[LAYER][0]        # (seq, dim)
        wids = enc.word_ids(0)
        buckets = collections.defaultdict(list)
        for pos, wid in enumerate(wids):
            if wid is not None:
                buckets[wid].append(hs[pos])
        vecs = []
        for wi in range(len(words)):
            if buckets.get(wi):
                vecs.append(torch.stack(buckets[wi]).mean(0))
            else:
                vecs.append(torch.zeros(hs.shape[-1]))
        return torch.nn.functional.normalize(torch.stack(vecs), dim=1)

    def align(sa_words, ru_words):
        """-> (sim matrix as list-of-lists, set of argmax+itermax (i,j) links)."""
        if not sa_words or not ru_words:
            return [], set()
        A = _token_embeds(sa_words)
        B = _token_embeds(ru_words)
        S = (A @ B.T)                                    # cosine, both normalized
        sim = S.tolist()
        # SimAlign "argmax": mutual argmax (intersection of row- and col-argmax).
        row_best = S.argmax(dim=1).tolist()
        col_best = S.argmax(dim=0).tolist()
        links = {(i, j) for i, j in enumerate(row_best) if col_best[j] == i}
        return sim, links

    align.model_id = model_id
    align.layer = LAYER
    return align


def embed_confidence(l1, l0_group_words, aligner, cache):
    """Confidence from the embedding aligner for one L1 pair. l0_group_words is
    (sa_words, ru_words) for the verse; `cache` memoizes the per-group sim/links so
    every L1 pair of a verse reuses one forward pass."""
    sa_words, ru_words = l0_group_words
    gid = id(l0_group_words)
    if gid not in cache:
        cache[gid] = aligner(sa_words, ru_words)
    sim, links = cache[gid]
    if not sim:
        return {'alignment_confidence': 0.0, 'sa_ground': 0.0, 'ru_ground': 0.0,
                'backend': 'embed', 'argmax_agree': 0}
    key = cg.form_key(l1.get('slp1') or '')
    want = _ru_stems(l1.get('ru'))
    si = [i for i, w in enumerate(sa_words)
          if cg.form_key(w) == key or (len(key) >= PREFIX_MIN and key in cg.form_key(w))]
    rj = [j for j, w in enumerate(ru_words) if w in want or _ru_stems(w) & want]
    if not si or not rj:
        return {'alignment_confidence': 0.0, 'sa_ground': float(bool(si)),
                'ru_ground': float(bool(rj)), 'backend': 'embed', 'argmax_agree': 0}
    best = max(sim[i][j] for i in si for j in rj)
    agree = int(any((i, j) in links for i in si for j in rj))
    return {'alignment_confidence': round(max(0.0, min(1.0, best)), 4),
            'sa_ground': 1.0, 'ru_ground': 1.0,
            'backend': 'embed', 'argmax_agree': agree}


# ------------------------------------------------------------------------- cross
def cmd_cross(a):
    if not os.path.exists(a.l1):
        sys.exit('L1 lexicon not found: %s (corpus_lexicon.jsonl is gitignored -- '
                 'build it first)' % a.l1)
    l0 = load_l0_index(a.l0)
    print('cross: %d L0 verse groups indexed' % len(l0))
    aligner = None
    if a.backend == 'embed':
        aligner = embed_aligner_factory(a.model)
        if aligner is None:
            print('cross: embed backend unavailable -> proxy on full corpus')
            a.backend = 'proxy'
        else:
            print('cross: embed backend ready (model=%s, layer=%s)'
                  % (aligner.model_id, aligner.layer))
    # embed needs the ordered verse words per group; proxy only needs the index.
    l0_words = load_l0_words(a.l0) if a.backend == 'embed' else {}
    dist = collections.Counter()
    conf_sum = grounded = n = no_l0 = 0
    cache = {}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, 'w', encoding='utf-8', newline='\n') as out:
        for l1 in build_tmx.iter_units(a.l1):
            g = l1.get('group')
            entry = l0.get(g)
            if entry is None:
                no_l0 += 1
            if a.backend == 'embed' and entry is not None:
                res = embed_confidence(l1, l0_words.get(g, ([], [])), aligner, cache)
            else:
                res = proxy_confidence(l1, entry)
            row = {'tuid': build_tmx.tuid(l1), 'group': g, 'slp1': l1.get('slp1'),
                   'kind': l1.get('kind'), **res}
            out.write(json.dumps(row, ensure_ascii=False) + '\n')
            c = res['alignment_confidence']
            conf_sum += c
            grounded += 1 if c > 0 else 0
            dist[_bucket(c)] += 1
            n += 1
            if a.sample and n >= a.sample:
                break
    print('cross: %d L1 pairs scored (backend=%s) -> %s' % (n, a.backend, a.out))
    if n:
        print('  mean alignment_confidence: %.4f   grounded (>0): %.1f%%'
              % (conf_sum / n, 100 * grounded / n))
        print('  L1 pairs with no L0 verse indexed: %d (%.1f%%) -- these score 0 for '
              'lack of a parent, not for being wrong' % (no_l0, 100 * no_l0 / n))
        for b in ('0.0', '(0,0.3]', '(0.3,0.6]', '(0.6,0.9]', '(0.9,1.0]'):
            print('  %-10s %8d  %5.1f%%' % (b, dist[b], 100 * dist[b] / n))
    return 0


def load_l0_words(path):
    """group -> (sa_words[], ru_words[]) ordered token lists for the embed aligner.
    Uses the translation segment's ru; commentary L1 pairs still align against the
    verse translation words (the shared semantic anchor)."""
    words = {}
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get('kind') != 'translation':
                continue
            g = r.get('group')
            sa = build_l0.sa_tokens(r.get('slp1') or '')
            ru = cg.ru_tokens(r.get('ru') or '')
            words[g] = (sa, sorted(ru))
    return words


def _bucket(c):
    if c == 0.0:
        return '0.0'
    if c <= 0.3:
        return '(0,0.3]'
    if c <= 0.6:
        return '(0.3,0.6]'
    if c <= 0.9:
        return '(0.6,0.9]'
    return '(0.9,1.0]'


def cmd_agree(a):
    if not os.path.exists(a.align):
        sys.exit('align sidecar not found: %s (run `cross` first)' % a.align)
    dist = collections.Counter()
    conf_sum = n = argmax_agree = argmax_seen = 0
    bykind = collections.defaultdict(lambda: [0, 0.0])
    with open(a.align, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            c = r.get('alignment_confidence', 0.0)
            conf_sum += c
            dist[_bucket(c)] += 1
            k = r.get('kind') or '?'
            bykind[k][0] += 1
            bykind[k][1] += c
            if 'argmax_agree' in r:
                argmax_seen += 1
                argmax_agree += int(r['argmax_agree'])
            n += 1
    if not n:
        sys.exit('agree: empty sidecar')
    print('agree: %d L1 pairs, mean alignment_confidence %.4f' % (n, conf_sum / n))
    for b in ('0.0', '(0,0.3]', '(0.3,0.6]', '(0.6,0.9]', '(0.9,1.0]'):
        print('  %-10s %8d  %5.1f%%' % (b, dist[b], 100 * dist[b] / n))
    print('  by kind:')
    for k in sorted(bykind):
        cnt, cs = bykind[k]
        print('    %-12s %8d  mean %.4f' % (k, cnt, cs / cnt))
    if argmax_seen:
        print('  embed argmax agreement: %.1f%% of %d pairs'
              % (100 * argmax_agree / argmax_seen, argmax_seen))
    return 0


# ------------------------------------------------------------------------ selftest
def selftest():
    # a tiny L0 index by hand: verse has sanskrit tokens {darma, arjuna}, ru
    # translation stems include 'дхарм','арджун', commentary stems 'поле'.
    import tempfile
    d = tempfile.mkdtemp(prefix='align_selftest_')
    l0p = os.path.join(d, 'corpus_l0.jsonl')
    with open(l0p, 'w', encoding='utf-8') as f:
        f.write(json.dumps({'group': 'g1', 'kind': 'translation',
                            'slp1': 'Darmakzetre arjunaH uvAca',
                            'ru': 'на поле дхармы Арджуна сказал'}, ensure_ascii=False) + '\n')
        f.write(json.dumps({'group': 'g1', 'kind': 'commentary',
                            'slp1': 'Darmakzetre arjunaH uvAca',
                            'ru': 'дхармакшетра означает священное поле'}, ensure_ascii=False) + '\n')
    idx = load_l0_index(l0p)
    e = idx['g1']
    assert 'Darma' not in e['sa'] and 'Darmakzetre' in e['sa'], e['sa']

    # exact-ish: 'arjuna' vs verse token 'arjunaH' -> prefix match (SA_PARTIAL)
    assert sa_ground('arjuna', e) == SA_PARTIAL, sa_ground('arjuna', e)
    # exact form_key hit
    assert sa_ground('Darmakzetre', e) == 1.0
    # a word not in the verse -> 0
    assert sa_ground('yoga', e) == 0.0

    # ru grounding: rendering 'дхарма' present in translation stems
    assert ru_ground('дхарма', e, 'translation') == 1.0, ru_ground('дхарма', e, 'translation')
    # rendering absent from translation -> 0
    assert ru_ground('колесница', e, 'translation') == 0.0
    # commentary rendering grounds against the commentary pool
    assert ru_ground('священное', e, 'commentary') == 1.0

    # composite: a well-grounded pair beats a hallucinated one
    good = proxy_confidence({'slp1': 'Darmakzetre', 'ru': 'дхармы', 'kind': 'translation'}, e)
    halluc = proxy_confidence({'slp1': 'yoga', 'ru': 'колесница', 'kind': 'translation'}, e)
    assert good['alignment_confidence'] > 0.6, good
    assert halluc['alignment_confidence'] == 0.0, halluc
    assert _bucket(0.0) == '0.0' and _bucket(1.0) == '(0.9,1.0]' and _bucket(0.5) == '(0.3,0.6]'
    print('tm_align selftest OK -- sa grounding (exact/prefix/miss), ru grounding, '
          'composite separates grounded vs hallucinated')
    return 0


def main():
    ap = argparse.ArgumentParser(description='Word-align cross-check for the Sa->Ru TM (H215 Slice 3)')
    sub = ap.add_subparsers(dest='cmd', required=True)

    c = sub.add_parser('cross', help='score every L1 pair vs its L0 verse -> align sidecar')
    c.add_argument('--l0', default=DEFAULT_L0)
    c.add_argument('--l1', default=DEFAULT_L1)
    c.add_argument('--out', default=DEFAULT_OUT)
    c.add_argument('--backend', choices=['proxy', 'embed'], default='proxy')
    c.add_argument('--model', default=None, help='embed backend HF model id')
    c.add_argument('--sample', type=int, default=None)

    g = sub.add_parser('agree', help='summary + confidence distribution of a sidecar')
    g.add_argument('--align', default=DEFAULT_OUT)

    sub.add_parser('selftest', help='deterministic asserts (no model)')

    a = ap.parse_args()
    if a.cmd == 'cross':
        return cmd_cross(a)
    if a.cmd == 'agree':
        return cmd_agree(a)
    if a.cmd == 'selftest':
        return selftest()
    return 1


if __name__ == '__main__':
    sys.exit(main())
