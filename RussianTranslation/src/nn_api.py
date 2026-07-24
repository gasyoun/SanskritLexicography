#!/usr/bin/env python
r"""H1457 Spike S1 -- thin adapter over external/local embedding + QE models for
the Sa->Ru TM technical-hardening track (A2, A5).

Smoke-tested in-env 22-07-2026 (Sonnet 5, `claude-sonnet-5`), see
research/nn_api_smoketest.md for the full log. Summary:

  embed -- sentence-transformers/LaBSE, LOCAL (downloaded once from the public
           HF hub, no token needed, no per-call network dependency after that).
           SERVES. Cosine separates a true Sa/Ru pair (0.31-0.58) from a
           mismatched one (0.10) on a 3-pair probe.
  qe    -- COMET-QE does NOT serve in this environment:
             1. `unbabel-comet` fails to install: its numpy<2 pin has no cp314
                wheel and there is no C compiler on this machine to build one
                from source (meson: no cl/gcc/clang found).
             2. The hosted HF Inference API path (`router.huggingface.co/
                hf-inference/...`) 401s unauthenticated -- COMET-QE is a
                gated/licensed checkpoint, not on the free tier.
             3. The LLM-as-judge fallback (DeepSeek or Claude) needs a key;
                neither a DEEPSEEK_API_KEY (`.env`, per build_corpus_lexicon.py)
                nor an Anthropic key is present in this environment.
           Per the plan's stop condition this BLOCKS A2 (COMET-QE calibration);
           A2 is marked preliminary/blocked, tm_grade.py keeps --qe proxy as
           the shipped default. A5 (embedding aligner) is NOT blocked -- embed
           serves.

Usage:
    python nn_api.py --smoketest      # re-run the probe, print the log
"""
import hashlib
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(HERE, '.nn_api_cache')

EMBED_MODEL = 'sentence-transformers/LaBSE'


def _cache_path(kind, key):
    h = hashlib.sha256(key.encode('utf-8')).hexdigest()[:24]
    return os.path.join(CACHE_DIR, '%s-%s.json' % (kind, h))


def _cache_get(kind, key):
    p = _cache_path(kind, key)
    if os.path.exists(p):
        return json.load(open(p, encoding='utf-8'))
    return None


def _cache_put(kind, key, value):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(_cache_path(kind, key), 'w', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False)


_embed_model = None


def _embed_model_instance():
    """First call downloads LaBSE from the public HF hub (no token needed);
    every call after that -- including from a fresh process -- loads purely
    from the local cache. HF's metadata HEAD requests occasionally hit a
    transient network blip on this host (SSL EOF / DNS hiccups seen during
    H1457); once the weights are cached, forcing HF_HUB_OFFLINE for that
    retry avoids paying for a metadata round-trip we don't need."""
    global _embed_model
    if _embed_model is None:
        os.environ.setdefault('HF_HUB_DISABLE_SYMLINKS_WARNING', '1')
        from sentence_transformers import SentenceTransformer
        try:
            _embed_model = SentenceTransformer(EMBED_MODEL)
        except Exception as e:
            cache_hint = os.path.join(os.path.expanduser('~'), '.cache', 'huggingface',
                                      'hub', 'models--sentence-transformers--LaBSE')
            if os.path.isdir(cache_hint):
                sys.stderr.write('nn_api: online load failed (%s) -> retrying from '
                                 'local cache (HF_HUB_OFFLINE)\n' % e)
                os.environ['HF_HUB_OFFLINE'] = '1'
                _embed_model = SentenceTransformer(EMBED_MODEL)
            else:
                raise
    return _embed_model


def embed(texts):
    """List[str] -> List[List[float]] (768-d LaBSE vectors). Disk-cached per
    input string so repeated calls (e.g. across A5 pilot re-runs) cost one
    forward pass per distinct string. Real, local -- no external API call."""
    if isinstance(texts, str):
        texts = [texts]
    out = [None] * len(texts)
    todo_idx, todo_txt = [], []
    for i, t in enumerate(texts):
        hit = _cache_get('embed-%s' % EMBED_MODEL.replace('/', '_'), t)
        if hit is not None:
            out[i] = hit
        else:
            todo_idx.append(i)
            todo_txt.append(t)
    if todo_txt:
        model = _embed_model_instance()
        vecs = model.encode(todo_txt).tolist()
        for i, t, v in zip(todo_idx, todo_txt, vecs):
            out[i] = v
            _cache_put('embed-%s' % EMBED_MODEL.replace('/', '_'), t, v)
    return out


def embed_available():
    try:
        _embed_model_instance()
        return True
    except Exception as e:
        sys.stderr.write('nn_api: embed unavailable (%s)\n' % e)
        return False


def qe(sa, ru):
    """Reference-free QE score for (sa, ru) in [0,1], or None if no QE backend
    serves in this environment. See module docstring: COMET-QE (package + HF
    Inference API) and the LLM-judge fallback all fail to serve here -- this
    is the honest, logged result, not a silent stub."""
    return None


def qe_available():
    return False


def cosine(a, b):
    import math
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


# ------------------------------------------------------------------ smoketest
PROBE_SA = [
    'dharmakSetre kurukSetre',
    'karma',
    'yogaH karmasu kauSalam',
    'Sabda',
    'AtmA',
]
PROBE_RU = [
    'на поле дхармы, на поле Куру',
    'действие',
    'йога есть искусность в действиях',
    'звук',
    'атман, я',
]
PROBE_MISMATCH_RU = 'слон идёт в лес по широкой дороге'


def smoketest():
    report = {'embed': {'model': EMBED_MODEL, 'available': False},
              'qe': {'available': False, 'reason': None}}
    if embed_available():
        va = embed(PROBE_SA)
        vb = embed(PROBE_RU)
        vc = embed([PROBE_MISMATCH_RU])[0]
        pairs = [round(cosine(a, b), 4) for a, b in zip(va, vb)]
        mismatch = [round(cosine(a, vc), 4) for a in va]
        report['embed']['available'] = True
        report['embed']['true_pair_cosine'] = pairs
        report['embed']['mismatch_cosine'] = mismatch
        report['embed']['separates'] = min(pairs) > max(mismatch)
        print('embed: LaBSE serves in-env. true-pair cosine %s vs mismatch %s '
              '-> separates=%s' % (pairs, mismatch, report['embed']['separates']))
    else:
        print('embed: no backend serves in this environment')

    report['qe']['reason'] = ('unbabel-comet: no cp314 numpy wheel + no local '
                               'compiler; HF Inference API: 401 unauthenticated '
                               '(gated checkpoint); LLM-judge fallback: no '
                               'DEEPSEEK_API_KEY/.env or Anthropic key present')
    print('qe: no backend serves in this environment (%s)' % report['qe']['reason'])
    return report


def main():
    import argparse
    ap = argparse.ArgumentParser(description='nn_api smoke-test (H1457 spike S1)')
    ap.add_argument('--smoketest', action='store_true')
    a = ap.parse_args()
    if a.smoketest:
        smoketest()
        return 0
    ap.print_help()
    return 1


if __name__ == '__main__':
    sys.exit(main())
