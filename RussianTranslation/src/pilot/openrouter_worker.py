#!/usr/bin/env python
r"""Minimal OpenRouter/DeepSeek client + E1 sample freezer (H2175 step 15, R2.3/R3.4).

STAGED, not scheduled: cheap external lanes earn a production role ONLY through a
pre-registered A/B win (ruling R2.3). This module ships the two build-behind-flag
pieces Wave 3 needs:

  * a minimal chat-completions client (stdlib urllib, no new dependency) for
    DeepSeek (``$DEEPSEEK_API_KEY``, base https://api.deepseek.com) and OpenRouter
    (``$OPENROUTER_API_KEY``, base https://openrouter.ai/api/v1). Key VALUES come
    from env/.secrets only (R5.2: DeepSeek key lives in ORS-FAQ/.env; OpenRouter
    key in the Systema prod .env) — never from a repo file;
  * ``--freeze-sample``: the FROZEN, stratified ~40-card E1 sample manifest +
    pre-declared verdict rule under <data-root>/experiments/E1_deepseek_vs_c4/.
    Frozen means: written once with a fixed seed, layer-stratified from the store,
    and never regenerated after the experiment starts (the manifest carries its
    own sha256 over the key list).

No org-canonical LLM-HTTP client existed to reuse (SHARED_CODE checked in the
architecture pass — verdict BUILD).
"""
import argparse
import hashlib
import json
import os
import random
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
for p in (HERE, SRC):
    if p not in sys.path:
        sys.path.insert(0, p)

from store_path import canonical_store   # noqa: E402

SCHEMA_SAMPLE = 'pwg.e1_sample_manifest.v1'

PROVIDERS = {
    'deepseek': {'base': 'https://api.deepseek.com', 'key_env': 'DEEPSEEK_API_KEY',
                 'default_model': 'deepseek-chat'},
    'openrouter': {'base': 'https://openrouter.ai/api/v1',
                   'key_env': 'OPENROUTER_API_KEY',
                   'default_model': 'deepseek/deepseek-chat'},
}

VERDICT_RULE = """# E1 pre-declared verdict rule (frozen BEFORE any arm runs — R2.3)

_Created: 02-08-2026 · Last updated: 02-08-2026_

**Question.** Does a DeepSeek draft earn a production DRAFT role in the PWG→RU
pipeline at its price point?

**Arms.** A = c4 (subscription Claude CLI) draft; B = DeepSeek draft. SAME frozen
sample (`sample_manifest.json`, seed 20260802, layer-stratified), same gate suite,
same blinded judge protocol (judge never sees the arm label).

**Verdict (pre-declared, ruling R2.3 / VERIFICATION doc):** DeepSeek wins a
production draft role **iff** its deterministic gate-pass rate is within 5
percentage points of c4's on the frozen sample **AND** the blinded judge severity
distribution is not worse at p<0.05 (Mann–Whitney U on per-card max severity).
Otherwise DeepSeek gets, at most, mechanical-QA lanes. No post-hoc rule changes;
a rule change = a NEW pre-registered experiment.

_Dr. Mārcis Gasūns_
"""


def api_key(provider, env=None):
    env = env if env is not None else os.environ
    key = env.get(PROVIDERS[provider]['key_env'])
    if not key:
        raise SystemExit('openrouter_worker: %s is not set — key values live in '
                         'env/.secrets only (R5.2), never in a repo'
                         % PROVIDERS[provider]['key_env'])
    return key


def chat(provider, messages, model=None, temperature=0.2, timeout=120,
         opener=None, env=None):
    """One chat-completions call -> (text, usage_dict). opener is injectable."""
    conf = PROVIDERS[provider]
    payload = json.dumps({'model': model or conf['default_model'],
                          'messages': messages,
                          'temperature': temperature}).encode('utf-8')
    req = urllib.request.Request(
        conf['base'] + '/chat/completions', data=payload,
        headers={'Content-Type': 'application/json',
                 'Authorization': 'Bearer ' + api_key(provider, env=env)})
    open_fn = opener or urllib.request.urlopen
    t0 = time.time_ns()
    with open_fn(req, timeout=timeout) as resp:
        body = json.loads(resp.read().decode('utf-8'))
    t1 = time.time_ns()
    text = body['choices'][0]['message']['content']
    u = body.get('usage') or {}
    usage = {'input_tokens': u.get('prompt_tokens'),
             'output_tokens': u.get('completion_tokens'),
             'provider': provider, 'model': model or conf['default_model'],
             'duration_ms': (t1 - t0) / 1e6}
    return text, usage


def freeze_sample(store, out_dir, size=40, seed='20260802'):
    """Layer-stratified frozen sample of store subcards -> sample_manifest.json.

    Refuses to overwrite an existing manifest: FROZEN means frozen."""
    manifest_path = os.path.join(out_dir, 'sample_manifest.json')
    if os.path.exists(manifest_path):
        raise SystemExit('E1 sample already frozen at %s — a frozen sample is never '
                         'regenerated (R2.3); delete deliberately if the experiment '
                         'must restart from zero' % manifest_path)
    by_layer = {}
    with open(store, encoding='utf-8') as f:
        for line in f:
            try:
                row = json.loads(line)
            except ValueError:
                continue
            sub, layer = row.get('subcard'), row.get('layer') or '?'
            if sub:
                by_layer.setdefault(layer, set()).add(sub)
    total = sum(len(v) for v in by_layer.values())
    if not total:
        raise SystemExit('E1 freeze: store %s yielded no subcards' % store)
    rng = random.Random('e1:' + seed)
    picked = []
    for layer in sorted(by_layer):
        pool = sorted(by_layer[layer])
        quota = max(1, round(size * len(pool) / total))
        picked.extend((layer, k) for k in rng.sample(pool, min(quota, len(pool))))
    picked = picked[:size]
    keys = sorted(k for _l, k in picked)
    manifest = {
        'schema': SCHEMA_SAMPLE, 'frozen_at': int(time.time()), 'seed': seed,
        'store': os.path.abspath(store), 'requested_size': size,
        'strata': {layer: sum(1 for l2, _k in picked if l2 == layer)
                   for layer in sorted(by_layer)},
        'keys': keys,
        'keys_sha256': hashlib.sha256('\n'.join(keys).encode('utf-8')).hexdigest(),
    }
    os.makedirs(out_dir, exist_ok=True)
    with open(manifest_path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
        f.write('\n')
    rule_path = os.path.join(out_dir, 'VERDICT_RULE.md')
    if not os.path.exists(rule_path):
        with open(rule_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(VERDICT_RULE)
    return manifest_path, manifest


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--freeze-sample', action='store_true',
                    help='freeze the E1 stratified sample manifest (once)')
    ap.add_argument('--store', default=None)
    ap.add_argument('--out-dir', default=None,
                    help='experiments/E1_deepseek_vs_c4 dir (with --freeze-sample)')
    ap.add_argument('--size', type=int, default=40)
    ap.add_argument('--probe', choices=sorted(PROVIDERS),
                    help='one tiny live call to verify the key works (spends cents)')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.freeze_sample:
        if not args.out_dir:
            ap.error('--freeze-sample requires --out-dir')
        store = args.store or canonical_store(
            os.path.join(SRC, 'pwg_ru_translated.jsonl'))
        path, manifest = freeze_sample(store, args.out_dir, size=args.size)
        print('E1 sample frozen: %d keys, strata %s -> %s'
              % (len(manifest['keys']), manifest['strata'], path))
        return 0
    if args.probe:
        text, usage = chat(args.probe, [{'role': 'user', 'content': 'Say OK.'}])
        print(json.dumps({'text': text[:80], 'usage': usage}, ensure_ascii=False))
        return 0
    ap.print_help()
    return 0


def selftest():
    import io
    import tempfile

    class FakeResp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def fake_open(req, timeout=None):
        assert req.get_header('Authorization') == 'Bearer test-key-123'
        assert 'chat/completions' in req.full_url
        sent = json.loads(req.data.decode('utf-8'))
        assert sent['messages'][0]['content'] == 'hi'
        return FakeResp(json.dumps({
            'choices': [{'message': {'content': 'привет'}}],
            'usage': {'prompt_tokens': 5, 'completion_tokens': 2}}).encode('utf-8'))

    env = {'DEEPSEEK_API_KEY': 'test-key-123'}
    text, usage = chat('deepseek', [{'role': 'user', 'content': 'hi'}],
                       opener=fake_open, env=env)
    assert text == 'привет' and usage['input_tokens'] == 5
    assert usage['provider'] == 'deepseek'
    # missing key fails loudly with the R5.2 pointer, never a silent None
    try:
        api_key('openrouter', env={})
        raise AssertionError('missing key must SystemExit')
    except SystemExit as exc:
        assert 'OPENROUTER_API_KEY' in str(exc)

    with tempfile.TemporaryDirectory() as td:
        store = os.path.join(td, 'store.jsonl')
        with open(store, 'w', encoding='utf-8', newline='\n') as f:
            for i in range(80):
                f.write(json.dumps({'subcard': 'k%02d' % i,
                                    'layer': 'pwg' if i < 60 else 'nws'}) + '\n')
        out = os.path.join(td, 'E1')
        path, manifest = freeze_sample(store, out, size=40)
        assert len(manifest['keys']) <= 40 and manifest['strata']['pwg'] >= 25
        assert manifest['strata'].get('nws'), 'minority layer must be represented'
        assert os.path.exists(os.path.join(out, 'VERDICT_RULE.md'))
        # frozen means frozen: a second freeze refuses
        try:
            freeze_sample(store, out, size=40)
            raise AssertionError('re-freeze must refuse')
        except SystemExit as exc:
            assert 'never regenerated' in str(exc)
        # determinism: same seed on a fresh dir -> same keys
        path2, manifest2 = freeze_sample(store, os.path.join(td, 'E1b'), size=40)
        assert manifest2['keys_sha256'] == manifest['keys_sha256']
    print('openrouter_worker selftest: PASS (client shape + auth, R5.2 loud missing '
          'key, stratified deterministic freeze, refuse-refreeze)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
