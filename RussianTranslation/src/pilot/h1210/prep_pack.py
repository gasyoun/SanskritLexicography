#!/usr/bin/env python
r"""H2439 prep-pack — cheap Flash PREP sidecars before Opus (map mode A).

Writes ``prep/{key}.json`` only. NEVER writes the TM store, NEVER promotes cards
(R4.3a: promoter path alone owns the store).

Modes
-----
* **dry** (default when no API key / ``--dry``): deterministic skeleton from a
  key list or H1210 worklist — lands schema-valid sidecars for smoke tests.
* **live** (``--live`` + ``DEEPSEEK_API_KEY``): optional Flash call to fill
  sense inventory / hard-flags / RU skeleton. Still sidecar-only.

Usage
-----
  python src/pilot/h1210/prep_pack.py --keys-file keys.txt --out-dir prep --dry
  python src/pilot/h1210/prep_pack.py --worklist H1210_ab100_worklist....json \
      --out-dir prep --limit 5 --dry
  python src/pilot/h1210/prep_pack.py --selftest

Schema of record: ``prep_pack.schema.json`` (same directory).
Org map: Uprava docs/DEEPSEEK_V4_FLASH_0731_ORG_LANE_MAP_2026-08.md §3.1.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import deepseek_arm as ds  # noqa: E402

SCHEMA_ID = 'pwg.prep_pack.v1'
SCHEMA_PATH = os.path.join(HERE, 'prep_pack.schema.json')


def empty_pack(key1: str, *, model: str | None = None, mode: str = 'dry') -> dict:
    """Schema-valid empty / dry prep-pack for one key."""
    return {
        'schema': SCHEMA_ID,
        'key1': key1,
        'produced_at': int(time.time()),
        'producer': {
            'tool': 'prep_pack.py',
            'mode': mode,
            'model': model or ds.DEFAULT_MODEL,
            'price_table': {
                'cache_miss_in': ds.PRICE_CACHE_MISS_IN,
                'cache_hit_in': ds.PRICE_CACHE_HIT_IN,
                'out': ds.PRICE_OUT,
            },
        },
        'sense_inventory': [],
        'tm_fuzzy_hits': [],
        'compound_candidates': [],
        'citation_normalize': [],
        'hard_flags': {
            'polysemy': False,
            'no_pwg': False,
            'monster_length': False,
            'notes': [],
        },
        'ru_skeleton': None,
        'route_hint': 'prep_only',  # controller_only | full_worker | prep_only | park
        'store_write': False,  # hard invariant — never True from this tool
    }


def load_keys(args) -> list[str]:
    keys: list[str] = []
    if args.worklist:
        with open(args.worklist, encoding='utf-8') as f:
            wl = json.load(f)
        keys.extend(wl.get('keys') or [])
    if args.keys_file:
        with open(args.keys_file, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    keys.append(line.split()[0])
    if args.keys:
        keys.extend(k for k in args.keys.split(',') if k)
    # de-dupe, preserve order
    seen = set()
    out = []
    for k in keys:
        if k not in seen:
            seen.add(k)
            out.append(k)
    if args.limit is not None:
        out = out[: args.limit]
    return out


def write_pack(out_dir: str, pack: dict) -> str:
    if pack.get('store_write') is True:
        raise SystemExit('prep_pack: refusing store_write=True (R4.3a fence)')
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, '%s.json' % pack['key1'])
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(pack, f, ensure_ascii=False, indent=1)
        f.write('\n')
    return path


def produce_dry(keys: list[str], out_dir: str, model: str) -> list[str]:
    paths = []
    for k in keys:
        pack = empty_pack(k, model=model, mode='dry')
        # Cheap length-proxy hard-flag from key shape alone (no DE text in dry).
        if len(k) >= 24:
            pack['hard_flags']['monster_length'] = True
            pack['hard_flags']['notes'].append('dry: key1 length >= 24 (proxy only)')
            pack['route_hint'] = 'full_worker'
        paths.append(write_pack(out_dir, pack))
    return paths


def produce_live(keys: list[str], out_dir: str, model: str, env_file: str | None) -> list[str]:
    """Optional Flash call: fill ru_skeleton + flags. Still no store write."""
    env = ds.load_env_file(env_file)
    key = os.environ.get('DEEPSEEK_API_KEY') or env.get('DEEPSEEK_API_KEY')
    if not key:
        raise SystemExit('prep_pack --live needs DEEPSEEK_API_KEY (or use --dry)')
    base = (os.environ.get('DEEPSEEK_BASE_URL') or env.get('DEEPSEEK_BASE_URL')
            or 'https://api.deepseek.com')
    client = ds.DeepSeek(base, key, model, max_tokens=1024, timeout=120)
    paths = []
    system = (
        'You are a PWG German dictionary PREP worker. Return ONE JSON object only:\n'
        '{"sense_count_estimate": int, "hard_flags": {"polysemy": bool, "monster_length": bool,'
        ' "notes": [str]}, "ru_skeleton": [str] or null, "route_hint":'
        ' "controller_only"|"full_worker"|"prep_only"|"park"}.\n'
        'No store writes. No final translation. JSON only.'
    )
    for k in keys:
        pack = empty_pack(k, model=model, mode='live')
        text, call = client.chat(
            system,
            'Prep headword key1=%s (SLP1). Estimate sense count and hard flags only.' % k,
            'prep:%s' % k,
        )
        pack['producer']['live_call'] = {
            'ok': text is not None,
            'latency_s': (call or {}).get('latency_s'),
            'error': (call or {}).get('error'),
        }
        if text:
            try:
                obj, _repair = ds.extract_json(text)
            except ValueError as e:
                pack['hard_flags']['notes'].append('live parse fail: %s' % e)
                pack['route_hint'] = 'full_worker'
            else:
                sc = obj.get('sense_count_estimate')
                if isinstance(sc, int) and sc > 0:
                    pack['sense_inventory'] = [
                        {'i': i, 'de_anchor': None, 'note': 'estimate_only'}
                        for i in range(sc)
                    ]
                hf = obj.get('hard_flags') or {}
                for field in ('polysemy', 'monster_length'):
                    if field in hf:
                        pack['hard_flags'][field] = bool(hf[field])
                if isinstance(hf.get('notes'), list):
                    pack['hard_flags']['notes'].extend(str(n) for n in hf['notes'])
                if obj.get('ru_skeleton') is not None:
                    pack['ru_skeleton'] = obj.get('ru_skeleton')
                rh = obj.get('route_hint')
                if rh in ('controller_only', 'full_worker', 'prep_only', 'park'):
                    pack['route_hint'] = rh
        pack['store_write'] = False
        paths.append(write_pack(out_dir, pack))
    return paths


def selftest() -> int:
    import tempfile

    with open(SCHEMA_PATH, encoding='utf-8') as f:
        schema = json.load(f)
    assert schema.get('$id') == SCHEMA_ID or schema.get('title')
    pack = empty_pack('testKey', mode='dry')
    assert pack['schema'] == SCHEMA_ID
    assert pack['store_write'] is False
    assert pack['producer']['price_table']['cache_miss_in'] == 0.14
    assert pack['producer']['price_table']['cache_hit_in'] == 0.0028
    assert pack['producer']['price_table']['out'] == 0.28
    assert pack['producer']['model'] == 'deepseek-v4-flash'
    # price constants live on deepseek_arm
    assert ds.PRICE_CACHE_MISS_IN == 0.14
    assert ds.PRICE_CACHE_HIT_IN == 0.0028
    assert ds.PRICE_OUT == 0.28
    assert ds.DEFAULT_MODEL == 'deepseek-v4-flash'
    with tempfile.TemporaryDirectory() as td:
        paths = produce_dry(['short', 'aVeryLongHeadwordProxyTokenXX'], td, ds.DEFAULT_MODEL)
        assert len(paths) == 2
        long_pack = json.load(open(paths[1], encoding='utf-8'))
        assert long_pack['hard_flags']['monster_length'] is True
        assert long_pack['store_write'] is False
        # refuse store_write=True
        bad = empty_pack('x')
        bad['store_write'] = True
        try:
            write_pack(td, bad)
            raise AssertionError('store_write=True must refuse')
        except SystemExit as e:
            assert 'R4.3a' in str(e) or 'store_write' in str(e)
    print('prep_pack selftest: PASS (schema constants, dry write, R4.3a fence)')
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--worklist', default=None,
                    help='H1210-style worklist JSON with a keys[] array')
    ap.add_argument('--keys-file', default=None)
    ap.add_argument('--keys', default=None, help='comma-separated key1 list')
    ap.add_argument('--out-dir', default=None, help='directory for prep/{key}.json')
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--model', default=None)
    ap.add_argument('--env-file', default=None)
    ap.add_argument('--dry', action='store_true', default=False,
                    help='deterministic sidecars, no API (default if not --live)')
    ap.add_argument('--live', action='store_true',
                    help='call DeepSeek Flash; still sidecar-only')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.out_dir:
        ap.error('--out-dir is required (writes prep sidecars only; never the TM store)')
    keys = load_keys(args)
    if not keys:
        ap.error('no keys — pass --worklist, --keys-file, or --keys')
    model = args.model or os.environ.get('DEEPSEEK_MODEL') or ds.DEFAULT_MODEL
    if args.live:
        paths = produce_live(keys, args.out_dir, model, args.env_file)
        mode = 'live'
    else:
        paths = produce_dry(keys, args.out_dir, model)
        mode = 'dry'
    print('prep_pack %s: wrote %d sidecar(s) under %s (store_write=never)'
          % (mode, len(paths), args.out_dir))
    for p in paths[:5]:
        print('  ', p)
    if len(paths) > 5:
        print('  ... +%d more' % (len(paths) - 5))
    return 0


if __name__ == '__main__':
    sys.exit(main())
