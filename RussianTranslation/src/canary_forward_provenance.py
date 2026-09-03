#!/usr/bin/env python
r"""H3982 acceptance canary: does a REAL promote run stamp resolvable forward provenance?

The forward half of SPEC_PWG_RU_PROVENANCE_BACKFILL_31-08-2026.md 2.3 is only worth
anything if it survives the actual writing path, not just a unit test. So this runs
`promote_final_cards.py` as a subprocess -- the same CLI a drain window uses -- against a
DELIBERATELY DIRTY working tree, into a scratch store, and then asserts on the rows that
came out the other end:

  1. every promoted row carries `provenance.pipeline.source_commit` (the commit the run
     BELIEVED it was on) and `worktree_dirty: true` (it was not that commit's bytes);
  2. every `<name>_sha` those rows record resolves to a real blob in the archive.

(2) is the half that is easy to fake and worthless to fake: a stamp naming a hash that
expands to nothing is the era-A provenance hole one layer down, which is the failure this
whole handoff exists to close. The canary therefore checks resolution, not presence.

Safety: `--init-store` into a temp file, never the canonical store, so no human-reviewed
overlay row is read or rewritten. The blob archive IS the real one by default (populating
it is the point); `--blob-dir` isolates that too when you only want the assertions.

    python canary_forward_provenance.py [--blob-dir DIR] [--report PATH] [--keep]

Exit 0 = every assertion held. Non-zero = the forward path is not doing its job.
"""
import argparse
import glob as globmod
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import pipeline_version  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CANARY_REL = os.path.join('reports', 'h3982_canary')
MODEL_VERSION = 'claude-opus-5'

CARD = {
    'meta': {
        'root': 'agni', 'safe_root': 'agni',
        'generator': 'gen_opt_harness2.batched-masked', 'schema_version': 'v1',
        'rootmap_sha256': 'c' * 64, 'generated_at': '2026-09-03T00:00:00Z',
        'selected_keys': ['agni~~h0_00_pwg00'],
        'execution_manifest_schema': 'pwg.headless_execution_manifest.v2',
        'execution': {'profile_slot': 'c4', 'config_dir_fingerprint': 'f' * 64,
                      'execution_route': 'claude-cli-headless',
                      'executor_lane': 'serial-whole-card',
                      'validation_method': 'audit_window+final_schema',
                      'model_identifier': MODEL_VERSION},
        'provenance_classes': {'agni~~h0_00_pwg00': 'real'},
        'input_hashes': {'agni~~h0_00_pwg00': {'raw_sha256': '1' * 64,
                                               'portrait_sha256': '2' * 64}},
    },
    'results': [{'key': 'agni~~h0_00_pwg00', 'card': {
        'key1': 'agni~~h0_00_pwg00', 'iast': 'agni', 'notes': '', 'records': [
        {'h': 'agni', 'grammar': '', 'senses': [
            {'tag': '1', 'russian': 'огонь', 'german': '{%Feuer%}',
             'equivalence_type': 'equivalent', 'source_type': 'lexicographic',
             'stratum': '', 'differentia': ''},
        ]}]}}],
}


def _dirty_marker(path):
    """An untracked file is enough to make `git status --porcelain` non-empty."""
    with open(path, 'w', encoding='utf-8') as f:
        f.write('H3982 canary: this file exists so the tree is provably dirty.\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--blob-dir', help='isolate the archive (default: the real one)')
    ap.add_argument('--report', help='write the evidence JSON here')
    ap.add_argument('--keep', action='store_true', help='keep the scratch store')
    args = ap.parse_args()

    env = dict(os.environ)
    if args.blob_dir:
        env['PWG_RU_BLOB_DIR'] = os.path.abspath(args.blob_dir)
    archive_dir = env.get('PWG_RU_BLOB_DIR') or pipeline_version.blob_archive_dir()

    canary_dir = os.path.join(ROOT, CANARY_REL)
    os.makedirs(canary_dir, exist_ok=True)
    card_path = os.path.join(canary_dir, 'wf_output.h3982_canary.json')
    with open(card_path, 'w', encoding='utf-8') as f:
        json.dump(CARD, f, ensure_ascii=False, indent=1)
    _dirty_marker(os.path.join(canary_dir, 'DIRTY_MARKER.txt'))

    state = pipeline_version.git_source_state(ROOT)
    if state.get('worktree_dirty') is not True:
        sys.exit('canary precondition failed: tree is not dirty (%r)' % state)

    store = tempfile.mkstemp(prefix='h3982_canary_store_', suffix='.jsonl')[1]
    os.remove(store)
    cmd = [sys.executable, os.path.join(HERE, 'promote_final_cards.py'),
           '--glob', os.path.join(CANARY_REL, 'wf_output.h3982_canary.json'),
           '--store', store, '--init-store', '--no-backup',
           '--gen-model-version', MODEL_VERSION]
    env['PWG_RU_STORE'] = store
    proc = subprocess.run(cmd, cwd=HERE, env=env, capture_output=True,
                          encoding='utf-8', errors='replace')
    sys.stderr.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    if proc.returncode:
        sys.exit('promote_final_cards.py exited %d' % proc.returncode)

    rows = [json.loads(ln) for ln in open(store, encoding='utf-8') if ln.strip()]
    if not rows:
        sys.exit('canary promoted nothing -- there is no provenance to check')

    checked, hashes = 0, set()
    for r in rows:
        pl = (r.get('provenance') or {}).get('pipeline') or {}
        assert pl.get('source_commit'), 'row %s has no source_commit' % r.get('key1')
        assert pl.get('worktree_dirty') is True, \
            'row %s must record the dirty tree it was produced by' % r.get('key1')
        assert pl.get('dirty_component_sha'), 'a dirty row must identify its delta'
        for name in pipeline_version.COMPONENTS:
            sha = pl.get('%s_sha' % name)
            assert sha, 'row %s missing %s_sha' % (r.get('key1'), name)
            if sha == 'na':
                continue
            blob = pipeline_version.resolve_blob(sha, archive_dir=archive_dir)
            assert blob, 'RECORDED-BUT-UNRESOLVABLE %s_sha=%s -- the gap one layer down' \
                % (name, sha)
            hashes.add(sha)
        checked += 1

    cov = pipeline_version.store_blob_coverage(store, archive_dir=archive_dir)
    assert cov['forward_rows'] == len(rows) and not cov['forward_unresolved'], cov

    evidence = {
        'schema': 'pwg_ru.h3982_canary.v1',
        'rows_promoted': len(rows), 'rows_checked': checked,
        'source_commit': rows[0]['provenance']['pipeline']['source_commit'],
        'worktree_dirty': True,
        'dirty_component_sha': rows[0]['provenance']['pipeline']['dirty_component_sha'],
        'component_hashes_resolved': sorted(hashes),
        'archive_dir': archive_dir,
        'coverage': cov,
        'store': store,
    }
    if args.report:
        with open(args.report, 'w', encoding='utf-8') as f:
            json.dump(evidence, f, ensure_ascii=False, indent=1, sort_keys=True)
            f.write('\n')
    print(json.dumps(evidence, ensure_ascii=False, indent=1, sort_keys=True))
    if not args.keep:
        os.remove(store)
        for extra in globmod.glob(store + '*'):
            os.remove(extra)
    shutil.rmtree(canary_dir, ignore_errors=True)
    print('H3982 canary OK: %d row(s), %d component blob(s) all resolvable'
          % (len(rows), len(hashes)))
    return 0


if __name__ == '__main__':
    sys.exit(main() or 0)
