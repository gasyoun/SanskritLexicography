#!/usr/bin/env python
"""H2675 — Flash PREP --live drain-head runner.

First 200 is a hard gate (D22): skeleton JSON parse ≥80% or stop scale-out.
Every HTTP call is appended to JSONL. tm_fence.may_write is never true.
Uses H2674 client + 32768 cap. Thinking stays off (PREP).

Usage (from RussianTranslation):
  python experiments/H2675_w1_prep/run_prep_live.py --phase first200
  python experiments/H2675_w1_prep/run_prep_live.py --phase scale --only-if-gate
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
RT = os.path.abspath(os.path.join(HERE, '..', '..'))
H1210 = os.path.join(RT, 'src', 'pilot', 'h1210')
if H1210 not in sys.path:
    sys.path.insert(0, H1210)

import deepseek_arm as ds  # noqa: E402
import prep_pack  # noqa: E402

from build_drain_head import (  # noqa: E402
    MAIN_ASSEMBLED,
    load_assembled_de,
    manifest_input,
)

DEFAULT_ENV = r'C:\Users\user\Documents\GitHub\ORS-FAQ\.env'
DEFAULT_STORE = r'C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation\src\pwg_ru_translated.jsonl'
PARSE_FLOOR = 0.80
USD_PER_CARD_STOP = 0.04


def _load_json(path: str) -> dict:
    with open(path, encoding='utf-8') as handle:
        return json.load(handle)


def _write_json(path: str, obj: dict) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as handle:
        json.dump(obj, handle, ensure_ascii=False, indent=1)
        handle.write('\n')


def score_sidecars(out_dir: str, keys: list[str]) -> dict:
    n = len(keys)
    n_sidecar = 0
    n_parse = 0
    n_length = 0
    n_null = 0
    n_fence_write = 0
    n_store_write = 0
    routes = {}
    park_notes = {}
    sample_paths = []
    missing = []
    for key1 in keys:
        try:
            from safe_filename import safe_name
            stem = safe_name(key1)
        except Exception:  # noqa: BLE001
            stem = key1
        path = os.path.join(out_dir, '%s.json' % stem)
        if not os.path.exists(path):
            missing.append(key1)
            continue
        n_sidecar += 1
        if len(sample_paths) < 20:
            sample_paths.append(path)
        pack = _load_json(path)
        if (pack.get('tm_fence') or {}).get('may_write') is True:
            n_fence_write += 1
        if pack.get('store_write') is True:
            n_store_write += 1
        live = (pack.get('producer') or {}).get('live_call') or {}
        if live.get('parse_ok') is True:
            n_parse += 1
        if live.get('finish_reason') == 'length':
            n_length += 1
        if live.get('ok') is not True:
            n_null += 1
        route = pack.get('route_hint') or 'unknown'
        routes[route] = routes.get(route, 0) + 1
        if route == 'park':
            for note in (pack.get('hard_flags') or {}).get('notes') or []:
                park_notes[note] = park_notes.get(note, 0) + 1
    parse_pct = (100.0 * n_parse / n) if n else 0.0
    sidecar_pct = (100.0 * n_sidecar / n) if n else 0.0
    return {
        'n': n,
        'n_sidecar': n_sidecar,
        'sidecar_pct': round(sidecar_pct, 2),
        'n_parse_ok': n_parse,
        'parse_pct': round(parse_pct, 2),
        'n_length': n_length,
        'n_null': n_null,
        'n_missing': len(missing),
        'n_tm_fence_write': n_fence_write,
        'n_store_write': n_store_write,
        'routes': routes,
        'park_notes': park_notes,
        'sample_paths': sample_paths,
        'missing_head': missing[:20],
        'parse_floor': PARSE_FLOOR,
        'parse_gate': (n_parse / n) >= PARSE_FLOOR if n else False,
        'sidecar_gate': sidecar_pct >= 95.0,
    }


def _write_batch_manifest(keys: list[str], assembled: dict, path: str) -> str:
    inputs = {}
    for key1 in keys:
        slot = assembled.get(key1)
        if not slot:
            continue
        inputs[key1] = manifest_input(slot)
    manifest = {
        'schema': 'pwg.headless_execution_manifest.v1',
        'meta': {
            'generator': 'H2675 run_prep_live.py',
            'n': len(inputs),
            'manifest_authoritative': True,
        },
        'inputs': inputs,
    }
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as handle:
        json.dump(manifest, handle, ensure_ascii=False)
        handle.write('\n')
    return path


def run_batch(keys: list[str], *, out_dir: str, manifest_path: str,
              journal_path: str, env_file: str, store: str, workers: int) -> None:
    if ds.DEFAULT_MAX_TOKENS < 32768:
        raise SystemExit('FAIL: DEFAULT_MAX_TOKENS=%s (need 32768)' % ds.DEFAULT_MAX_TOKENS)
    ds.refuse_if_peak()
    argv = [
        '--keys', ','.join(keys),
        '--manifest', manifest_path,
        '--manifest-authoritative',
        '--live',
        '--store', store,
        '--out-dir', out_dir,
        '--journal', journal_path,
        '--env-file', env_file,
        '--workers', str(workers),
        '--model', ds.DEFAULT_MODEL,
    ]
    rc = prep_pack.main(argv)
    if rc:
        raise SystemExit('prep_pack --live exited %s' % rc)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--phase', choices=('first200', 'scale', 'score'), default='first200')
    ap.add_argument('--only-if-gate', action='store_true')
    ap.add_argument('--env-file', default=DEFAULT_ENV)
    ap.add_argument('--store', default=DEFAULT_STORE)
    ap.add_argument('--workers', type=int, default=32)
    ap.add_argument('--batch-size', type=int, default=80)
    ap.add_argument('--max-keys', type=int, default=None,
                    help='scale only this many remaining keys (resume-safe)')
    ap.add_argument('--assembled', default=MAIN_ASSEMBLED)
    args = ap.parse_args(argv)

    wl_path = os.path.join(HERE, 'H2675_drain_head_5k.worklist.json')
    if not os.path.exists(wl_path):
        raise SystemExit('missing worklist — run build_drain_head.py first')
    worklist = _load_json(wl_path)
    keys = list(worklist.get('keys') or [])
    out_dir = os.path.join(RT, 'prep', 'h2675')
    journal_path = os.path.join(HERE, 'calls.jsonl')
    first200_path = os.path.join(HERE, 'first200.stats.json')
    os.makedirs(out_dir, exist_ok=True)

    if args.phase == 'score':
        stats = score_sidecars(out_dir, keys[:200])
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return 0 if stats['parse_gate'] else 2

    if args.phase == 'scale' and args.only_if_gate:
        if not os.path.exists(first200_path):
            raise SystemExit('no first200.stats.json — run --phase first200')
        gate = _load_json(first200_path)
        if not gate.get('parse_gate'):
            print('D22 STOP: first-200 parse %.2f%% < 80%% — no scale-out'
                  % gate.get('parse_pct', 0), flush=True)
            return 2

    print('assembled index…', flush=True)
    assembled = load_assembled_de(args.assembled)

    if args.phase == 'first200':
        batch = keys[:200]
        man = os.path.join(HERE, 'H2675_first200.manifest.json')
        if not os.path.exists(man):
            _write_batch_manifest(batch, assembled, man)
        print('first200 n=%d workers=%d cap=%s model=%s'
              % (len(batch), args.workers, ds.DEFAULT_MAX_TOKENS, ds.DEFAULT_MODEL),
              flush=True)
        t0 = time.time()
        run_batch(batch, out_dir=out_dir, manifest_path=man,
                  journal_path=journal_path, env_file=args.env_file,
                  store=args.store, workers=args.workers)
        wall = time.time() - t0
        stats = score_sidecars(out_dir, batch)
        stats['phase'] = 'first200'
        stats['wall_s'] = round(wall, 1)
        stats['workers'] = args.workers
        stats['max_tokens'] = ds.DEFAULT_MAX_TOKENS
        stats['model'] = ds.DEFAULT_MODEL
        usd = _journal_usd(journal_path, batch)
        stats['usd_total'] = usd
        stats['usd_per_card'] = round(usd / len(batch), 6) if batch else 0.0
        stats['usd_per_card_stop'] = USD_PER_CARD_STOP
        if stats['usd_per_card'] > USD_PER_CARD_STOP:
            stats['cost_stop'] = True
            stats['cost_stop_note'] = '>$0.04/card — do not scale; thinking already off'
        _write_json(first200_path, stats)
        print(json.dumps({k: stats[k] for k in (
            'n', 'n_sidecar', 'sidecar_pct', 'n_parse_ok', 'parse_pct',
            'n_length', 'usd_total', 'usd_per_card', 'parse_gate',
            'n_store_write', 'n_tm_fence_write', 'wall_s',
        )}, ensure_ascii=False, indent=2), flush=True)
        if stats['n_store_write'] or stats['n_tm_fence_write']:
            raise SystemExit('FAIL: TM/store write claimed')
        if not stats['parse_gate']:
            print('D22 STOP: parse %.2f%% < 80%% — no remaining 4800 --live'
                  % stats['parse_pct'], flush=True)
            return 2
        if stats.get('cost_stop'):
            print('COST STOP: $%.4f/card > $0.04 — no scale-out' % stats['usd_per_card'])
            return 3
        return 0

    # scale remaining after a passing first-200
    start = 200
    remaining = keys[start:]
    # resume: drop keys that already have sidecars
    still = []
    for key1 in remaining:
        try:
            from safe_filename import safe_name
            stem = safe_name(key1)
        except Exception:  # noqa: BLE001
            stem = key1
        if not os.path.exists(os.path.join(out_dir, '%s.json' % stem)):
            still.append(key1)
    remaining = still
    if args.max_keys is not None:
        remaining = remaining[: args.max_keys]
    t0 = time.time()
    for i in range(0, len(remaining), args.batch_size):
        ds.refuse_if_peak()
        batch = remaining[i:i + args.batch_size]
        # skip keys that already have a sidecar (resume)
        todo = []
        for key1 in batch:
            try:
                from safe_filename import safe_name
                stem = safe_name(key1)
            except Exception:  # noqa: BLE001
                stem = key1
            if not os.path.exists(os.path.join(out_dir, '%s.json' % stem)):
                todo.append(key1)
        if not todo:
            print('batch %d-%d already on disk' % (start + i, start + i + len(batch)),
                  flush=True)
            continue
        man = os.path.join(HERE, 'run', 'manifest_%05d.json' % (start + i))
        _write_batch_manifest(todo, assembled, man)
        print('scale batch offset=%d n=%d' % (start + i, len(todo)), flush=True)
        run_batch(todo, out_dir=out_dir, manifest_path=man,
                  journal_path=journal_path, env_file=args.env_file,
                  store=args.store, workers=args.workers)
    wall = time.time() - t0
    stats = score_sidecars(out_dir, keys)
    stats['phase'] = 'scale'
    stats['wall_s'] = round(wall, 1)
    usd = _journal_usd(journal_path, keys)
    stats['usd_total'] = usd
    stats['usd_per_card'] = round(usd / max(stats['n_sidecar'], 1), 6)
    _write_json(os.path.join(HERE, 'scale.stats.json'), stats)
    print(json.dumps({k: stats[k] for k in (
        'n', 'n_sidecar', 'sidecar_pct', 'n_parse_ok', 'parse_pct',
        'usd_total', 'usd_per_card', 'n_store_write', 'n_tm_fence_write',
    )}, ensure_ascii=False, indent=2), flush=True)
    if stats['n_store_write'] or stats['n_tm_fence_write']:
        raise SystemExit('FAIL: TM/store write claimed')
    return 0


def _journal_usd(path: str, keys: list[str]) -> float:
    if not os.path.exists(path):
        return 0.0
    wanted = set(keys)
    usd = 0.0
    with open(path, encoding='utf-8') as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if row.get('key1') not in wanted:
                continue
            card = row.get('price_card') or 'pre-1608'
            _, prices = ds.prices_for(ds.DEFAULT_MODEL, card=card)
            miss = row.get('prompt_tokens') or 0
            # prefer explicit cache split when present
            c_miss = row.get('cache_miss_tokens')
            c_hit = row.get('cache_hit_tokens') or 0
            if c_miss is None:
                c_miss = miss
            out = row.get('completion_tokens') or 0
            usd += (c_miss / 1e6 * prices['cache_miss_in']
                    + c_hit / 1e6 * prices['cache_hit_in']
                    + out / 1e6 * prices['out'])
    return round(usd, 4)


if __name__ == '__main__':
    sys.exit(main())
