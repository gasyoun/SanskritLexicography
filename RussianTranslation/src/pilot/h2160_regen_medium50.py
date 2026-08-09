#!/usr/bin/env python3
"""H2160 — re-prepare the five medium50 windows so the H2160 presplit fix takes effect.

The `h1447-m50-w{1..5}` artifacts on disk were generated BEFORE the H2160 correction to
`gen_opt_harness2._presplit_hit`, so their `presplit_keys` were computed with the per-card
fail-solo citation floor masked by the larger batch budget. w1 in particular came out with
`presplit_keys: []` and three whole-card batches whose calls are abandoned at the kill
ceiling every time.

This regenerates each window's harness + execution manifest with the SAME invocation the
coordinator's `prepare` uses (`gen_opt_harness2.py <root> --nominal --no-grammar
--keys=... --out=... --manifest-out=...` plus the profile binding), reading every argument
back out of the existing manifest so nothing is re-typed by hand. It then reports the
before/after `presplit_keys` and batch shape, and the new manifest SHA-256 that the
`headless_worker.py --manifest-sha256` argument needs.

By default it writes to a SEPARATE output directory and touches nothing the coordinator
state points at; pass --in-place to overwrite the prepared artifacts.

Usage:
    python src/pilot/h2160_regen_medium50.py --dry-run
    python src/pilot/h2160_regen_medium50.py --windows h1447-m50-w1 --in-place
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = Path(__file__).resolve().parent
BASE = Path('src/pilot/output/coordinator/artifacts')
WINDOWS = [f'h1447-m50-w{i}' for i in range(1, 6)]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def invocation(man: dict, window: str, out_js: Path, out_manifest: Path,
               config_dir: str | None = None) -> list[str]:
    """Rebuild the coordinator `prepare` command line from the manifest itself."""
    meta = man.get('meta') or {}
    execu = man.get('execution') or {}
    keys = meta.get('selected_keys') or sorted((man.get('inputs') or {}).keys())
    root = meta.get('root') or f'nominal_{window}'
    cmd = [sys.executable, str(HERE / 'gen_opt_harness2.py'), root,
           '--nominal', '--no-grammar',
           '--keys=%s' % ','.join(keys),
           '--out=%s' % out_js,
           '--manifest-out=%s' % out_manifest]
    slot = execu.get('profile_slot')
    if slot:
        cmd += ['--profile-slot=%s' % slot]
        # The manifest records only the config-dir FINGERPRINT, never the path, so the path
        # is supplied by the caller and verified against that fingerprint after regeneration.
        cfg = config_dir or execu.get('config_dir')
        if cfg:
            cmd += ['--config-dir=%s' % os.path.abspath(cfg)]
        cmd += ['--execution-route=%s' % (execu.get('execution_route') or 'claude-cli-headless'),
                '--executor-lane=%s' % (execu.get('executor_lane') or 'serial'),
                '--validation-method=%s' % (execu.get('validation_method')
                                            or 'audit_window+final_schema')]
    return cmd


def shape(man: dict) -> dict:
    inputs = man.get('inputs') or {}
    batches = man.get('batches') or []
    return {
        'presplit_keys': sorted(man.get('presplit_keys') or []),
        'n_batches': len(batches),
        'batched_keys': sorted(k for b in batches for k in (b if isinstance(b, list) else (b.get('keys') or []))),
        'n_inputs': len(inputs),
        'timeout_ceil_ms': (man.get('budgets') or {}).get('timeout_ceil_ms'),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--artifacts', default=str(BASE))
    ap.add_argument('--windows', nargs='*', default=WINDOWS)
    ap.add_argument('--outdir', default='src/pilot/output/h2160-regen')
    ap.add_argument('--in-place', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--config-dir', default=os.environ.get('CLAUDE_CONFIG_DIR'),
                    help='profile config dir; must reproduce the manifest config_dir_fingerprint')
    args = ap.parse_args()

    artifacts = Path(args.artifacts)
    rc = 0
    for w in args.windows:
        src_manifest = artifacts / w / f'execution_manifest.{w}.json'
        if not src_manifest.exists():
            print(f'{w}: MANIFEST MISSING at {src_manifest}')
            rc = 1
            continue
        before = json.loads(src_manifest.read_text(encoding='utf-8'))

        if args.in_place:
            out_dir = artifacts / w
        else:
            out_dir = Path(args.outdir) / w
            out_dir.mkdir(parents=True, exist_ok=True)
        out_js = out_dir / f'run_pilot_wf.{w}.js'
        out_manifest = out_dir / f'execution_manifest.{w}.json'

        cmd = invocation(before, w, out_js, out_manifest, args.config_dir)
        print(f'=== {w} ===')
        print('  before:', json.dumps(shape(before), ensure_ascii=False))
        if args.dry_run:
            print('  cmd:', ' '.join(cmd))
            continue
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        if proc.returncode != 0:
            print(f'  REGEN FAILED rc={proc.returncode}')
            print('  stdout:', (proc.stdout or '')[-2000:])
            print('  stderr:', (proc.stderr or '')[-2000:])
            rc = 1
            continue
        after = json.loads(out_manifest.read_text(encoding='utf-8'))
        print('  after :', json.dumps(shape(after), ensure_ascii=False))
        fp_before = (before.get('execution') or {}).get('config_dir_fingerprint')
        fp_after = (after.get('execution') or {}).get('config_dir_fingerprint')
        if fp_before != fp_after:
            print(f'  ⚠ config_dir_fingerprint DRIFT: {fp_before} -> {fp_after} '
                  f'(the regenerated manifest is bound to a different profile)')
            rc = 1
        else:
            print('  config_dir_fingerprint: unchanged ✓')
        print('  manifest:', out_manifest)
        print('  manifest_sha256:', sha256_file(out_manifest))
        print('  harness_sha256 :', sha256_file(out_js))
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
