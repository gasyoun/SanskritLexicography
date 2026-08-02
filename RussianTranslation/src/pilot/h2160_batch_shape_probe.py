#!/usr/bin/env python3
"""H2160 — offline shape probe for the non-terminating whole-card `b0` translate call.

The `b0` call in the medium50 windows dies at every ceiling tried (180 044 ms, then
300 073 ms), so it is non-terminating rather than slow. Before spending a paid call on
the question, this reads the five prepared `h1447-m50-w{1..5}` execution manifests
OFFLINE and answers, per window:

  * what `b0` actually contains (keys, skeleton bytes, <ls> citation units, fragments),
  * how the harness's own citation-weighted budget scores that batch against
    `OUTPUT_BUDGET` (the emit cap the batch lane sizes to),
  * whether the structural presplit triggers WOULD have fired for those keys
    (`presplit_keys` is `[]` in all five manifests today),
  * how `b0` compares with the heal-lane calls that demonstrably DO terminate.

No network, no paid call, no store write. Read-only.

Usage:
    python src/pilot/h2160_batch_shape_probe.py [--artifacts DIR] [--json OUT]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

DEFAULT_ARTIFACTS = Path('src/pilot/output/coordinator/artifacts')
WINDOWS = [f'h1447-m50-w{i}' for i in range(1, 6)]


def load_manifest(artifacts: Path, window: str) -> dict:
    p = artifacts / window / f'execution_manifest.{window}.json'
    with p.open(encoding='utf-8') as fh:
        return json.load(fh)


def batch_rows(man: dict) -> list[dict]:
    """One row per batch in the manifest, with the shape numbers that drive the emit size."""
    inputs = man.get('inputs') or {}
    frag_groups = man.get('fragment_groups') or {}
    rows = []
    for b in man.get('batches') or []:
        if isinstance(b, dict):
            bid = b.get('id') or b.get('batch_id') or b.get('name')
            keys = b.get('keys') or b.get('cards') or []
            lane = b.get('lane') or b.get('kind') or 'translate'
        else:
            bid, keys, lane = None, list(b), 'translate'
        ls_total = 0
        skel_bytes = 0
        nfrag_total = 0
        per_key = []
        for k in keys:
            rec = inputs.get(k) or {}
            ls = rec.get('ls')
            ls_n = len(ls) if isinstance(ls, list) else (int(ls) if isinstance(ls, int) else 0)
            skel = rec.get('skel') or rec.get('skeleton') or ''
            skel_n = len(skel.encode('utf-8')) if isinstance(skel, str) else 0
            frags = frag_groups.get(k) or []
            nfrag = sum(len(g) for g in frags) if frags and isinstance(frags[0], list) else len(frags)
            ls_total += ls_n
            skel_bytes += skel_n
            nfrag_total += nfrag
            per_key.append({'key': k, 'ls': ls_n, 'skel_bytes': skel_n, 'nfrag': nfrag})
        rows.append({
            'batch': bid,
            'lane': lane,
            'n_keys': len(keys),
            'keys': list(keys),
            'cite_units': ls_total + len(keys),  # harness sizes on (1 + <ls>) per card
            'skel_bytes': skel_bytes,
            'n_fragments': nfrag_total,
            'per_key': per_key,
        })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--artifacts', default=str(DEFAULT_ARTIFACTS))
    ap.add_argument('--json', dest='json_out', default=None)
    args = ap.parse_args()

    artifacts = Path(args.artifacts)
    report: dict = {'windows': {}}

    for w in WINDOWS:
        try:
            man = load_manifest(artifacts, w)
        except FileNotFoundError:
            print(f'{w}: MANIFEST MISSING')
            continue
        budgets = man.get('budgets') or {}
        runtime = man.get('runtime') or {}
        rows = batch_rows(man)
        report['windows'][w] = {
            'presplit_keys': man.get('presplit_keys'),
            'timeout_ceil_ms': budgets.get('timeout_ceil_ms'),
            'budgets': budgets,
            'runtime_keys': sorted(runtime.keys()),
            'n_inputs': len(man.get('inputs') or {}),
            'batches': rows,
        }

        print(f'=== {w} ===')
        print(f'  inputs={len(man.get("inputs") or {})}  presplit_keys={man.get("presplit_keys")}')
        print(f'  timeout_ceil_ms={budgets.get("timeout_ceil_ms")}  budgets={budgets}')
        for r in rows:
            print(f'  [{r["batch"]}] lane={r["lane"]} n_keys={r["n_keys"]} '
                  f'cite_units={r["cite_units"]} skel_bytes={r["skel_bytes"]} '
                  f'n_fragments={r["n_fragments"]}')
            for pk in r['per_key']:
                print(f'      - {pk["key"]}: ls={pk["ls"]} skel_bytes={pk["skel_bytes"]} nfrag={pk["nfrag"]}')
        print()

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'wrote {args.json_out}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
