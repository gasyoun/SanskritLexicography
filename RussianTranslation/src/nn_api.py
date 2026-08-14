#!/usr/bin/env python
r"""H1457 Spike S1 -- thin adapter over external/local embedding + QE models for
the Sa->Ru TM technical-hardening track (A2, A5).

Smoke-tested in-env 22-07-2026 (Sonnet 5, `claude-sonnet-5`), see
research/nn_api_smoketest.md for the full log. Summary:

  embed -- sentence-transformers/LaBSE, LOCAL (downloaded once from the public
           HF hub, no token needed, no per-call network dependency after that).
           SERVES. Cosine separates a true Sa/Ru pair (0.31-0.58) from a
           mismatched one (0.10) on a 3-pair probe.
  qe    -- two named backends, never confused:
             * labse  -- SERVES locally via the same LaBSE embedder (H2686).
                         This is genuine semantic QE. It is NOT COMET.
             * comet  -- still does NOT serve (no cp314 unbabel-comet wheel;
                         gated HF checkpoint is not a silent fallback).
           tm_grade.py --qe labse is the genuine path. --qe comet must keep
           returning the proxy with name 'proxy' until a real comet path
           serves. Proxy rho=-0.0351 stays labelled preliminary.

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
_embed_error = None


def _embed_model_instance():
    """First call downloads LaBSE from the public HF hub (no token needed);
    every call after that -- including from a fresh process -- loads purely
    from the local cache. HF's metadata HEAD requests occasionally hit a
    transient network blip on this host (SSL EOF / DNS hiccups seen during
    H1457); once the weights are cached, forcing HF_HUB_OFFLINE for that
    retry avoids paying for a metadata round-trip we don't need.

    A failed load is cached for the process (H2686): pagefile exhaustion
    (WinError 1455) otherwise retried on every qe_available() probe.
    """
    global _embed_model, _embed_error
    if _embed_model is not None:
        return _embed_model
    if _embed_error is not None:
        raise _embed_error
    os.environ.setdefault('HF_HUB_DISABLE_SYMLINKS_WARNING', '1')
    from sentence_transformers import SentenceTransformer
    try:
        _embed_model = SentenceTransformer(EMBED_MODEL)
        return _embed_model
    except Exception as e:
        cache_hint = os.path.join(os.path.expanduser('~'), '.cache', 'huggingface',
                                  'hub', 'models--sentence-transformers--LaBSE')
        if os.path.isdir(cache_hint):
            sys.stderr.write('nn_api: online load failed (%s) -> retrying from '
                             'local cache (HF_HUB_OFFLINE)\n' % e)
            try:
                os.environ['HF_HUB_OFFLINE'] = '1'
                _embed_model = SentenceTransformer(EMBED_MODEL)
                return _embed_model
            except Exception as e2:
                _embed_error = e2
                raise e2
        _embed_error = e
        raise


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


QE_LABSE_BACKEND = 'labse'
QE_LABSE_MODEL = EMBED_MODEL
QE_COMET_BACKEND = 'comet'
# Affine map for cosine -> [0,1] reporting. Rank-based calibration (Spearman)
# is invariant to this strictly increasing transform.
def _cosine_to_unit(c):
    return max(0.0, min(1.0, (float(c) + 1.0) / 2.0))


def qe_labse(src, mt):
    """Reference-free semantic QE via LaBSE cosine(src, mt).

    Named backend: sentence-transformers/LaBSE. This is NOT COMET-QE and must
    never be labelled comet. Returns (score_unit, raw_cosine).
    """
    va, vb = embed([src or '', mt or ''])
    raw = cosine(va, vb)
    return _cosine_to_unit(raw), raw


def qe_comet(sa, ru):
    """COMET-QE if a real comet path serves; otherwise None. Never substitutes
    LaBSE or the proxy under this name."""
    return None


def qe(sa, ru, backend=QE_LABSE_BACKEND):
    """Reference-free QE score in [0,1], or None if that named backend does
    not serve. `backend='comet'` still returns None here (no wheel / no gated
    HF token). `backend='labse'` uses the local LaBSE embedder when it serves.
    """
    if backend == QE_COMET_BACKEND:
        return qe_comet(sa, ru)
    if backend == QE_LABSE_BACKEND:
        if not embed_available():
            return None
        score, _raw = qe_labse(sa, ru)
        return score
    raise ValueError('unknown QE backend %r (not comet, not labse)' % backend)


def qe_available(backend=QE_LABSE_BACKEND):
    """Liveness for a *named* backend. Default is labse, not comet -- callers
    that want COMET must pass backend='comet' and will get False until a real
    comet path serves. This split exists so tm_grade --qe comet cannot stamp
    a LaBSE score as COMET."""
    if backend == QE_COMET_BACKEND:
        return qe_comet('a', 'b') is not None
    if backend == QE_LABSE_BACKEND:
        return embed_available()
    return False


def qe_backend_receipt(backend=QE_LABSE_BACKEND):
    """Machine-readable liveness receipt. Never claims comet when labse served."""
    available = qe_available(backend)
    rec = {
        'backend': backend,
        'available': bool(available),
        'model': QE_LABSE_MODEL if backend == QE_LABSE_BACKEND else None,
        'labelled_as_comet': False,
        'mock': False,
    }
    if backend == QE_COMET_BACKEND:
        rec['reason'] = (
            'unbabel-comet: no cp314 numpy wheel + no local compiler; '
            'HF Inference API: gated checkpoint, not used as a silent fallback'
        )
        rec['model'] = 'Unbabel/wmt22-cometkiwi-da'
    elif backend == QE_LABSE_BACKEND:
        rec['reason'] = None if available else 'LaBSE embedder failed to load'
        rec['score_space'] = 'cosine mapped by (c+1)/2 into [0,1]; Spearman uses ranks'
    return rec


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

    comet = qe_backend_receipt(QE_COMET_BACKEND)
    labse = qe_backend_receipt(QE_LABSE_BACKEND)
    report['qe'] = {
        'comet': comet,
        'labse': labse,
        'available': labse['available'],
        'active_backend': QE_LABSE_BACKEND if labse['available'] else None,
        'reason': None if labse['available'] else labse['reason'],
    }
    if labse['available']:
        scores = []
        for sa, ru in zip(PROBE_SA, PROBE_RU):
            unit, raw = qe_labse(sa, ru)
            scores.append({'sa': sa, 'ru': ru, 'cosine': round(raw, 4),
                           'unit': round(unit, 4)})
        mismatch_unit, mismatch_raw = qe_labse(PROBE_SA[0], PROBE_MISMATCH_RU)
        report['qe']['true_pair'] = scores
        report['qe']['mismatch'] = {'cosine': round(mismatch_raw, 4),
                                    'unit': round(mismatch_unit, 4)}
        print('qe: labse SERVES (%s). true-pair unit %s vs mismatch %.4f'
              % (QE_LABSE_MODEL, [s['unit'] for s in scores], mismatch_unit))
        print('qe: comet does NOT serve (%s) -- not labelled as comet'
              % comet['reason'])
    else:
        print('qe: no genuine backend serves (labse=%s; comet=%s)'
              % (labse['reason'], comet['reason']))
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
