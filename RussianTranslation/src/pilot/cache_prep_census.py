#!/usr/bin/env python
"""H2704 — first-200 TM/retrieval census + sealed 50-miss and L3 cohorts.

Zero provider calls. Experimental TM may live only under the sealed run root.
H2675 live sidecars are not deterministic retrieval (they are paid PREP outputs).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
H1210 = os.path.join(HERE, 'h1210')
for path in (HERE, H1210, os.path.dirname(HERE)):
    if path not in sys.path:
        sys.path.insert(0, path)

import autosplit_requeue as autosplit  # noqa: E402
import cache_baseline_freeze as freeze  # noqa: E402
import cache_identity as ident  # noqa: E402
import cache_reuse as reuse  # noqa: E402
import prep_pack  # noqa: E402
from store_path import canonical_sidecar  # noqa: E402

RT = os.path.dirname(os.path.dirname(HERE))
REPO = os.path.dirname(RT)
H2675 = os.path.join(RT, 'experiments', 'H2675_w1_prep')
EXP_DIR = os.path.join(RT, 'experiments', 'pwg_cache_economy', 'h2704_prep')
MAIN_RT = r'C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation'
MAIN_ASSEMBLED = os.path.join(MAIN_RT, 'src', 'assembled_cards.jsonl')
MAIN_INPUT = os.path.join(MAIN_RT, 'src', 'pilot', 'input')
MAIN_STORE = os.path.join(MAIN_RT, 'src', 'pwg_ru_translated.jsonl')

FIRST_N = 200
PREP_N = 50
L3_N = 100
PREP_SALT = 'h2704-prep-50-v1'
L3_SALT = 'h2704-l3-100-v1'
COMMITTED_PREP_DIRS = (
    os.path.join(HERE, 'h1210', 'prep_samples_h2439'),
    os.path.join(HERE, 'h1210', 'prep_samples_h2489'),
    os.path.join(HERE, 'h1210', 'h2591', 'prep'),
    os.path.join(HERE, 'h1210', 'h2630', 'prep'),
)


class CensusError(ValueError):
    pass


def size_class(n_bytes):
    if n_bytes >= prep_pack.MONSTER_BYTES:
        return 'monster'
    if n_bytes >= 4000:
        return 'large'
    if n_bytes >= 1500:
        return 'medium'
    return 'small'


def poly_class(n_senses):
    return 'poly' if n_senses >= prep_pack.POLYSEMY_SENSE_FLOOR else 'sparse'


def stable_hex(salt, key1):
    return ident.sha256_bytes('%s:%s' % (salt, key1))


def load_first200_keys():
    path = os.path.join(H2675, 'H2675_drain_head_5k.worklist.json')
    with open(path, encoding='utf-8') as handle:
        body = json.load(handle)
    keys = list(body.get('keys') or [])
    if len(keys) < FIRST_N:
        raise CensusError('worklist shorter than 200: %d' % len(keys))
    return keys[:FIRST_N], keys


def committed_prep_keys():
    out = {}
    for directory in COMMITTED_PREP_DIRS:
        if not os.path.isdir(directory):
            continue
        for name in os.listdir(directory):
            if not name.endswith('.json') or name.endswith('.context.json'):
                continue
            path = os.path.join(directory, name)
            try:
                pack = json.load(open(path, encoding='utf-8'))
            except (OSError, ValueError):
                continue
            key1 = pack.get('key1')
            if key1 and key1 not in out:
                out[key1] = path
    return out


def raw_for_key(key1, slot):
    """Prefer production input raw; else assembled skeleton bytes."""
    try:
        from window_common import input_paths, sha256_file
    except Exception:
        input_paths = None
        sha256_file = None
    if input_paths and os.path.isdir(MAIN_INPUT):
        raw_path, _portrait = input_paths(key1, input_dir=MAIN_INPUT)
        if not os.path.isfile(raw_path):
            try:
                from safe_filename import safe_name
                raw_path, _portrait = input_paths(
                    safe_name(key1), input_dir=MAIN_INPUT)
            except Exception:
                raw_path = None
        if raw_path and os.path.isfile(raw_path):
            text = open(raw_path, encoding='utf-8').read()
            digest = sha256_file(raw_path) if sha256_file else ident.sha256_bytes(text)
            return {
                'kind': 'input_raw',
                'path': raw_path,
                'text': text,
                'raw_sha256': digest,
            }
    text = slot.get('skeleton') or ''
    return {
        'kind': 'assembled_skeleton',
        'path': None,
        'text': text,
        'raw_sha256': ident.sha256_bytes(text) if text else None,
    }


def fragment_texts(raw_text):
    if not raw_text:
        return []
    try:
        planned = autosplit.plan(raw_text)
    except Exception:
        return []
    return [part[2] for part in planned if part[2]]


def resolve_item(key1, slot, committed, run_dir, tm_card, tm_frag):
    raw = raw_for_key(key1, slot)
    item = {
        'key1': key1,
        'raw_sha256': raw['raw_sha256'],
        'fragments': fragment_texts(raw['text']),
    }
    hit = reuse.resolve(
        item,
        run_dir=run_dir,
        lang='ru',
        canonical_card_tm=tm_card,
        canonical_frag_tm=tm_frag,
    )
    tier = hit['tier']
    if tier == 'generation' and key1 in committed:
        tier = 'evidence'
        hit = {
            'tier': 'evidence',
            'source': 'committed_prep',
            'calls': 0,
            'hit': {'path': committed[key1]},
            'advisory': True,
        }
    if tier in ('provider_cache', 'generation'):
        tier = 'miss'
    n_bytes = int(slot.get('bytes') or 0)
    n_senses = int(slot.get('source_senses') or 0)
    return {
        'key1': key1,
        'tier': tier,
        'source': hit.get('source'),
        'calls': hit.get('calls'),
        'advisory': bool(hit.get('advisory')),
        'raw_kind': raw['kind'],
        'raw_sha256': raw['raw_sha256'],
        'n_fragments': len(item['fragments']),
        'bytes': n_bytes,
        'source_senses': n_senses,
        'size_class': size_class(n_bytes),
        'poly_class': poly_class(n_senses),
        'monster': n_bytes >= prep_pack.MONSTER_BYTES,
        'q4': n_bytes >= prep_pack.MONSTER_BYTES,
        'selection_hex': stable_hex(PREP_SALT, key1),
    }


def allocate_stratified(rows, n, salt):
    """Proportional allocation by (size, poly), remainder by stratum hash."""
    if n <= 0 or not rows:
        return []
    groups = {}
    for row in rows:
        groups.setdefault((row['size_class'], row['poly_class']), []).append(row)
    for key in groups:
        groups[key].sort(key=lambda r: (r['selection_hex'], r['key1']))
    total = len(rows)
    quotas = {}
    assigned = 0
    for key, members in groups.items():
        quota = (n * len(members)) // total
        quotas[key] = min(quota, len(members))
        assigned += quotas[key]
    leftover_keys = sorted(
        groups,
        key=lambda k: (stable_hex(salt, '%s|%s' % k), k),
    )
    while assigned < n:
        progressed = False
        for key in leftover_keys:
            if quotas[key] < len(groups[key]):
                quotas[key] += 1
                assigned += 1
                progressed = True
                if assigned >= n:
                    break
        if not progressed:
            break
    chosen = []
    for key in leftover_keys:
        chosen.extend(groups[key][:quotas[key]])
    chosen.sort(key=lambda r: (r['selection_hex'], r['key1']))
    return chosen[:n]


def write_json(path, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(ident.canonical_dumps(body))
        if not body:
            handle.write('\n')


def build_census(run_dir):
    os.makedirs(run_dir, exist_ok=True)
    first200, all_keys = load_first200_keys()
    assembled_path = MAIN_ASSEMBLED
    if not os.path.isfile(assembled_path):
        assembled_path = os.path.join(RT, 'src', 'assembled_cards.jsonl')
    if not os.path.isfile(assembled_path):
        raise CensusError('assembled_cards.jsonl missing')
    drain_dir = os.path.join(RT, 'experiments', 'H2675_w1_prep')
    if drain_dir not in sys.path:
        sys.path.insert(0, drain_dir)
    import build_drain_head as drain  # noqa: E402
    slots = drain.load_assembled_de(assembled_path)
    missing = [k for k in first200 if k not in slots]
    if missing:
        raise CensusError('first-200 keys missing assembled DE: %s' % missing[:8])
    committed = committed_prep_keys()
    tm_card = canonical_sidecar(os.path.join(HERE, 'translation_memory.ru.json'))
    tm_frag = canonical_sidecar(os.path.join(HERE, 'translation_memory.frag.ru.jsonl'))
    rows = [
        resolve_item(key, slots[key], committed, run_dir, tm_card, tm_frag)
        for key in first200
    ]
    counts = {
        'whole_card_tm': 0,
        'fragment_tm': 0,
        'evidence': 0,
        'miss': 0,
    }
    for row in rows:
        counts[row['tier']] = counts.get(row['tier'], 0) + 1
    misses = [row for row in rows if row['tier'] == 'miss']
    selected = allocate_stratified(misses, PREP_N, PREP_SALT)
    if len(selected) < PREP_N:
        raise CensusError('only %d misses; cannot seal 50 PREP pairs' % len(selected))

    l3_pool = []
    for key in all_keys[FIRST_N:]:
        slot = slots.get(key)
        if not slot:
            continue
        n_bytes = int(slot.get('bytes') or 0)
        n_senses = int(slot.get('source_senses') or 0)
        if n_bytes >= prep_pack.MONSTER_BYTES:
            continue
        l3_pool.append({
            'key1': key,
            'bytes': n_bytes,
            'source_senses': n_senses,
            'size_class': size_class(n_bytes),
            'poly_class': poly_class(n_senses),
            'monster': False,
            'q4': False,
            'selection_hex': stable_hex(L3_SALT, key),
        })
    l3 = allocate_stratified(l3_pool, L3_N, L3_SALT)
    if len(l3) < L3_N:
        raise CensusError('L3 pool too small: %d' % len(l3))

    census = {
        'schema': 'pwg.cache_prep_census.v1',
        'handoff': 'H2704',
        'n_first200': FIRST_N,
        'counts': counts,
        'fuzzy_advisory_only': True,
        'h2675_sidecars_excluded_from_evidence': True,
        'rows': rows,
        'canonical_tm_card': tm_card if os.path.isfile(tm_card) else None,
        'canonical_tm_frag': tm_frag if os.path.isfile(tm_frag) else None,
    }
    prep_manifest = {
        'schema': 'pwg.cache_prep_50.v1',
        'handoff': 'H2704',
        'salt': PREP_SALT,
        'n': PREP_N,
        'max_base_calls': PREP_N * 2,
        'requested_model': 'deepseek-v4-flash',
        'keys': [row['key1'] for row in selected],
        'rows': selected,
    }
    l3_manifest = {
        'schema': 'pwg.cache_l3_100.v1',
        'handoff': 'H2704',
        'salt': L3_SALT,
        'n': L3_N,
        'max_base_calls': L3_N * 2,
        'cost_ceiling_usd': 25.0,
        'exclude_q4': True,
        'exclude_monster': True,
        'requested_model': 'deepseek-v4-flash',
        'keys': [row['key1'] for row in l3],
        'rows': l3,
        'pool_size': len(l3_pool),
    }
    for body in (census, prep_manifest, l3_manifest):
        body['manifest_sha256'] = ident.sha256_bytes(ident.canonical_bytes(
            {k: v for k, v in body.items() if k != 'manifest_sha256'}
        ))
    return census, prep_manifest, l3_manifest


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-dir', default=os.path.join(EXP_DIR, 'run'))
    args = ap.parse_args(argv)
    os.makedirs(EXP_DIR, exist_ok=True)
    census, prep_manifest, l3_manifest = build_census(args.run_dir)
    write_json(os.path.join(EXP_DIR, 'census.json'), census)
    write_json(os.path.join(EXP_DIR, 'prep50.manifest.json'), prep_manifest)
    write_json(os.path.join(EXP_DIR, 'l3.manifest.json'), l3_manifest)
    print('census whole_card=%d fragment=%d evidence=%d miss=%d'
          % (census['counts']['whole_card_tm'],
             census['counts']['fragment_tm'],
             census['counts']['evidence'],
             census['counts']['miss']))
    print('sealed prep50=%d l3=%d' % (len(prep_manifest['keys']),
                                      len(l3_manifest['keys'])))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
