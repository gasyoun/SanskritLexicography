#!/usr/bin/env python
"""H2245: pin the canary manifest builder's OUTPUT SHAPE, offline, with zero paid calls.

``canary_manifest_build.py`` (H2174) closed the "nothing builds the canary manifest" gap,
but nothing pinned what it emits. That matters more here than for an ordinary generator:
the canary is a *synthetic control* whose whole diagnostic value rests on properties a
schema change could silently rot --

  * three senses, ``ls == 0`` and ``sk == 0`` -- the D-Q silent-SAN-LOSS geometry (H994).
    Dropping a sense keeps the ``accept()`` fidelity gate at ``0 == 0`` (it passes), so the
    SAN-LOSS soft guard is the ONLY thing that can catch the loss. A canary that acquired
    even one ``<ls>`` would start failing loudly for the wrong reason and stop testing the
    silent path at all;
  * ``key_provenance = synthetic_control`` -- what makes ``canary_gate`` refuse to judge a
    real window as a canary, and the promoter refuse to promote canary output (C-05);
  * a LIVE-COMPUTED ``config_dir_fingerprint`` -- the binding billing identity. A copied
    literal would let a manifest be fired against a profile it was never bound to.

This selftest builds into a scratch dir against a scratch ``--config-dir`` and asserts all
three, then diffs the fresh build against the committed golden artifact beside the fixture
(``dq_canary_puregloss~~h0_zz_pw.manifest.v2.json``) so a later session can see exactly what
changed. Two fields are volatile by construction and excluded from that diff: ``generated_at``
(a timestamp) and ``config_dir_fingerprint`` (machine-bound) -- the fingerprint is instead
asserted to equal the live hash of the scratch config dir, which is the stronger check.

Run standalone (``python src/pilot/canary_manifest_build_selftest.py``) or via
``window_selftest.py`` (``test_h2245_canary_manifest_builder``). Spends nothing.
"""
import copy
import json
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import canary_manifest_build as cmb                                      # noqa: E402
from execution_contract import (SCHEMA_V2, config_dir_fingerprint,       # noqa: E402
                                validate_manifest, validate_profile)

GOLDEN = os.path.join(cmb.REPO, 'pwg_ru', 'h994', 'canary',
                      cmb.CANARY_KEY + '.manifest.v2.json')
# Volatile by construction: a timestamp and a machine-bound hash. Excluded from the golden
# diff and checked separately (the fingerprint against a live re-hash, which is stricter).
VOLATILE = ('generated_at', 'config_dir_fingerprint')


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def strip_volatile(node):
    """Recursively drop the volatile fields so two builds are comparable."""
    if isinstance(node, dict):
        return {k: strip_volatile(v) for k, v in node.items() if k not in VOLATILE}
    if isinstance(node, list):
        return [strip_volatile(v) for v in node]
    return node


def build_into(tmp):
    """Build the canary manifest against a scratch profile dir. Zero paid calls."""
    config_dir = os.path.join(tmp, 'profile', '.claude')
    os.makedirs(config_dir)
    outdir = os.path.join(tmp, 'out')
    manifest_path, _harness, preflight, sha = cmb.build(
        'c4', config_dir, outdir, 'nominal_c4canary')
    with open(manifest_path, encoding='utf-8') as fh:
        return json.load(fh), config_dir, preflight, sha


def assert_contract(manifest, config_dir):
    """Both contract validators, on the real built artifact -- not a hand-written fixture."""
    validate_manifest(manifest, require_v2=True)
    validate_profile(manifest, config_dir, only_profile='c4')

    check(manifest['schema'] == SCHEMA_V2,
          'canary manifest must be %s, got %r' % (SCHEMA_V2, manifest.get('schema')))
    keys = manifest['meta']['selected_keys']
    check(keys == [cmb.CANARY_KEY],
          'canary manifest must select exactly the canary key, got %r' % (keys,))
    check(manifest['batches'] == [[cmb.CANARY_KEY]],
          'canary batches must drive exactly the one canary key, got %r' % (manifest['batches'],))
    check(manifest['key_provenance'] == {cmb.CANARY_KEY: 'synthetic_control'},
          'the canary MUST stay synthetic_control -- canary_gate and the promoter C-05 '
          'refusal both key off it; got %r' % (manifest['key_provenance'],))
    check(manifest['execution']['model_identifier'] == manifest['model'],
          'v2 execution model_identifier must equal the executable model')

    # The fingerprint is LIVE-COMPUTED, never a copied literal: re-hash the scratch dir this
    # build was bound to and require an exact match. A stale/copied literal cannot pass.
    live = config_dir_fingerprint(config_dir)
    check(manifest['execution']['config_dir_fingerprint'] == live,
          'config_dir_fingerprint is not the live hash of the bound config dir -- a copied '
          'literal would let this manifest fire against a profile it was never bound to')


def assert_canary_geometry(manifest):
    """The D-Q silent-SAN-LOSS geometry (H994) the control exists to exercise."""
    payload = manifest['inputs'][cmb.CANARY_KEY]
    check(payload['ls'] == 0 and payload['sk'] == 0,
          'the canary must carry ZERO <ls> and ZERO {#..#}: that is what makes a dropped '
          'sense INVISIBLE to the accept() fidelity gate (0 == 0 passes). Got ls=%r sk=%r'
          % (payload['ls'], payload['sk']))
    check(payload['senses'] == 3 and payload['source_senses'] == 3,
          'the canary must carry exactly 3 senses (the SAN-LOSS soft guard counts them); '
          'got senses=%r source_senses=%r' % (payload['senses'], payload['source_senses']))

    # Prompt shape (H2245 step 2): the canary rides the PRODUCTION masked-inline path, and on
    # pure gloss the mask is provably an IDENTITY transform -- zero placeholders emitted. That
    # is the whole reason no separate non-masked prompt variant is needed. If a future mask
    # change ever produced a placeholder here, the canary would stop being pure gloss and this
    # assertion is where that is caught.
    check(manifest['placeholder_maps'][cmb.CANARY_KEY] == [],
          'the pure-gloss canary must mask to ZERO {Tn} placeholders (identity transform); '
          'a non-empty map means the canary is no longer pure gloss: %r'
          % (manifest['placeholder_maps'][cmb.CANARY_KEY],))
    check(manifest['meta']['mode'] == 'nominal_masked',
          'the canary must ride the production nominal_masked prompt path, got %r'
          % (manifest['meta']['mode'],))


def assert_matches_golden(manifest):
    """Diff the fresh build against the committed known-good artifact."""
    if not os.path.exists(GOLDEN):
        raise AssertionError('golden canary manifest missing: %s' % GOLDEN)
    with open(GOLDEN, encoding='utf-8') as fh:
        golden = json.load(fh)
    validate_manifest(golden, require_v2=True)          # the committed artifact is itself valid

    fresh_cmp = strip_volatile(copy.deepcopy(manifest))
    golden_cmp = strip_volatile(copy.deepcopy(golden))
    if fresh_cmp != golden_cmp:
        differing = sorted(k for k in set(fresh_cmp) | set(golden_cmp)
                           if fresh_cmp.get(k) != golden_cmp.get(k))
        raise AssertionError(
            'builder output drifted from the committed golden manifest in %r.\n'
            'If the change is intended, regenerate the artifact:\n'
            '  python src/pilot/canary_manifest_build.py --profile-slot c4 '
            '--config-dir <dir> --outdir <tmp>\n'
            'and copy execution_manifest.canary.json over %s' % (differing, GOLDEN))


def selftest():
    with tempfile.TemporaryDirectory() as tmp:
        manifest, config_dir, preflight, sha = build_into(tmp)
        assert_contract(manifest, config_dir)
        assert_canary_geometry(manifest)
        assert_matches_golden(manifest)
        check(os.path.exists(preflight), 'builder did not emit the real lane preflight')
        check(len(sha) == 64, 'builder did not return a manifest sha256')
    return True


def main():
    selftest()
    print('canary_manifest_build_selftest: PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
