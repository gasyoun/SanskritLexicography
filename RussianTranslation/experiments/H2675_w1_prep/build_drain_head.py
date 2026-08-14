#!/usr/bin/env python
"""H2675 — drain-head worklist: assembled live-DE keys, no sidecar, freq order.

Reads the main-checkout assembled_cards.jsonl + pwg_freq_order.tsv (gitignored
data lives only on the canonical clone). Writes a 5k worklist and optional
execution-manifest inputs for --manifest-authoritative.

Usage (from RussianTranslation):
  python experiments/H2675_w1_prep/build_drain_head.py --limit 5000
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.abspath(os.path.join(HERE, '..', '..'))
H1210 = os.path.join(RT, 'src', 'pilot', 'h1210')
if H1210 not in sys.path:
    sys.path.insert(0, H1210)

import prep_pack  # noqa: E402

MAIN_RT = r'C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation'
MAIN_ASSEMBLED = os.path.join(MAIN_RT, 'src', 'assembled_cards.jsonl')
MAIN_FREQ = os.path.join(MAIN_RT, 'src', 'pwg_freq_order.tsv')

SIDECAR_DIRS = (
    os.path.join(RT, 'prep'),
    os.path.join(MAIN_RT, 'prep'),
    os.path.join(H1210, 'prep_samples_h2439'),
    os.path.join(H1210, 'prep_samples_h2489'),
    os.path.join(H1210, 'h2591', 'prep'),
    os.path.join(H1210, 'h2630', 'prep'),
)


def _safe_stem(key1: str) -> str:
    try:
        from safe_filename import safe_name
        return safe_name(key1)
    except Exception:  # noqa: BLE001
        return key1


def existing_sidecar_keys() -> set[str]:
    out = set()
    for d in SIDECAR_DIRS:
        if not os.path.isdir(d):
            continue
        for name in os.listdir(d):
            if not name.endswith('.json'):
                continue
            path = os.path.join(d, name)
            try:
                pack = json.load(open(path, encoding='utf-8'))
            except (OSError, ValueError):
                continue
            k = pack.get('key1')
            if k:
                out.add(k)
    return out


def load_freq_order(path: str) -> list[tuple[int, str, int]]:
    rows = []
    with open(path, encoding='utf-8') as handle:
        header = handle.readline()
        if 'k1_slp1' not in header:
            raise SystemExit('freq tsv missing k1_slp1 header: %s' % path)
        for line in handle:
            parts = line.rstrip('\n').split('\t')
            if len(parts) < 3:
                continue
            try:
                order = int(parts[0])
                count = int(parts[2])
            except ValueError:
                continue
            key1 = parts[1]
            if key1:
                rows.append((order, key1, count))
    return rows


def load_assembled_de(path: str) -> dict[str, dict]:
    """key1 -> {skeleton, source_senses, bytes, n_records}."""
    out = {}
    with open(path, encoding='utf-8') as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            key1 = row.get('key1')
            if not key1:
                continue
            recs = row.get('records') or []
            blobs = []
            for rec in recs:
                sk = (rec.get('de_skeleton') or '').strip()
                if sk:
                    blobs.append(sk)
            if not blobs:
                continue
            skeleton = '\n'.join(blobs)
            tags = prep_pack.SENSE_TAG_RE.findall(skeleton)
            n = len(set(tags)) if tags else 0
            if n <= 0:
                n = 1
            slot = out.get(key1)
            if slot is None:
                out[key1] = {
                    'skeleton': skeleton,
                    'source_senses': n,
                    'bytes': len(skeleton.encode('utf-8')),
                    'n_records': len(blobs),
                }
            else:
                slot['skeleton'] = slot['skeleton'] + '\n' + skeleton
                slot['source_senses'] += n
                slot['bytes'] += len(skeleton.encode('utf-8'))
                slot['n_records'] += len(blobs)
    return out


def manifest_input(slot: dict) -> dict:
    return {
        'skeleton': slot['skeleton'],
        'portrait': '',
        'source_senses': slot['source_senses'],
        'complexity': {
            'len_bytes': slot['bytes'],
            'n_senses': slot['source_senses'],
            'complex': slot['bytes'] >= prep_pack.MONSTER_BYTES,
            'score': slot['source_senses'],
        },
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--assembled', default=MAIN_ASSEMBLED)
    ap.add_argument('--freq', default=None)
    ap.add_argument('--limit', type=int, default=5000)
    ap.add_argument('--out-dir', default=HERE)
    args = ap.parse_args(argv)

    freq_path = args.freq
    if freq_path is None:
        for cand in (MAIN_FREQ, os.path.join(RT, 'src', 'pwg_freq_order.tsv')):
            if os.path.exists(cand):
                freq_path = cand
                break
    if not freq_path or not os.path.exists(freq_path):
        raise SystemExit('no pwg_freq_order.tsv')
    if not os.path.exists(args.assembled):
        raise SystemExit('no assembled_cards.jsonl at %s' % args.assembled)

    print('freq: %s' % freq_path, flush=True)
    print('assembled: %s' % args.assembled, flush=True)
    freq = load_freq_order(freq_path)
    print('freq rows: %d' % len(freq), flush=True)
    assembled = load_assembled_de(args.assembled)
    print('assembled live-DE keys: %d' % len(assembled), flush=True)
    already = existing_sidecar_keys()
    print('existing sidecars: %d' % len(already), flush=True)

    selected = []
    skipped_no_de = 0
    skipped_sidecar = 0
    for order, key1, count in freq:
        slot = assembled.get(key1)
        if not slot:
            skipped_no_de += 1
            continue
        if key1 in already:
            skipped_sidecar += 1
            continue
        selected.append({
            'rank': order,
            'key1': key1,
            'count_all': count,
            'source_senses': slot['source_senses'],
            'bytes': slot['bytes'],
            'monster': slot['bytes'] >= prep_pack.MONSTER_BYTES,
        })
        if len(selected) >= args.limit:
            break

    os.makedirs(args.out_dir, exist_ok=True)
    worklist = {
        'schema': 'h2675.drain_head.v1',
        'source': [
            'pwg_freq_order.tsv',
            'assembled_cards.jsonl (live DE)',
        ],
        'n': len(selected),
        'limit_requested': args.limit,
        'freq_rows': len(freq),
        'assembled_live_de': len(assembled),
        'existing_sidecars': len(already),
        'skipped_no_de': skipped_no_de,
        'skipped_sidecar': skipped_sidecar,
        'n_monster': sum(1 for r in selected if r['monster']),
        'keys': [r['key1'] for r in selected],
        'rows': selected,
    }
    wl_path = os.path.join(args.out_dir, 'H2675_drain_head_5k.worklist.json')
    with open(wl_path, 'w', encoding='utf-8', newline='\n') as handle:
        json.dump(worklist, handle, ensure_ascii=False, indent=1)
        handle.write('\n')
    print('wrote %s n=%d monsters=%d' % (wl_path, worklist['n'], worklist['n_monster']),
          flush=True)

    first = selected[:200]
    first_inputs = {r['key1']: manifest_input(assembled[r['key1']]) for r in first}
    first_manifest = {
        'schema': 'pwg.headless_execution_manifest.v1',
        'meta': {
            'generator': 'H2675 build_drain_head.py',
            'purpose': 'W1 Flash PREP --live first-200 gate',
            'n': len(first),
            'manifest_authoritative': True,
        },
        'inputs': first_inputs,
    }
    man_path = os.path.join(args.out_dir, 'H2675_first200.manifest.json')
    with open(man_path, 'w', encoding='utf-8', newline='\n') as handle:
        json.dump(first_manifest, handle, ensure_ascii=False)
        handle.write('\n')
    print('wrote %s bytes=%d' % (man_path, os.path.getsize(man_path)), flush=True)

    inventory = {
        'schema': 'h2675.drain_head.inventory.v1',
        'n_worklist': worklist['n'],
        'n_first200': len(first),
        'n_monster_all': worklist['n_monster'],
        'n_monster_first200': sum(1 for r in first if r['monster']),
        'skipped_no_de': skipped_no_de,
        'skipped_sidecar': skipped_sidecar,
        'assembled_live_de': len(assembled),
        'first20': [r['key1'] for r in selected[:20]],
    }
    inv_path = os.path.join(args.out_dir, 'H2675_drain_head.inventory.json')
    with open(inv_path, 'w', encoding='utf-8', newline='\n') as handle:
        json.dump(inventory, handle, ensure_ascii=False, indent=1)
        handle.write('\n')
    print(json.dumps(inventory, ensure_ascii=False), flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
