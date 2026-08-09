#!/usr/bin/env python
import os
import subprocess
import sys
import tempfile
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from execution_contract import (ActiveCallClaim, PRODUCTION_HARD_TIMEOUT_MS, SCHEMA_V2,
                                bind_output_meta, config_dir_fingerprint, validate_manifest,
                                validate_profile)
import probe_log
from probe_log import verdict_for


def fixture(config_dir):
    return {
        'schema': SCHEMA_V2,
        'model': 'claude-sonnet-5',
        'meta': {'selected_keys': ['real', 'canary']},
        'execution': {
            'profile_slot': 'c4',
            'config_dir_fingerprint': config_dir_fingerprint(config_dir),
            'execution_route': 'claude-cli-headless',
            'executor_lane': 'serial-whole-card',
            'validation_method': 'audit_window+final_schema',
            'model_identifier': 'claude-sonnet-5',
        },
        'key_provenance': {'real': 'real', 'canary': 'synthetic_control'},
    }


def main():
    with tempfile.TemporaryDirectory() as d:
        cfg = os.path.join(d, 'profile')
        os.makedirs(cfg)
        manifest = fixture(cfg)
        validate_manifest(manifest, require_v2=True)
        output_meta = {'selected_keys': ['real', 'canary']}
        bind_output_meta(output_meta, manifest)
        assert output_meta['execution'] == manifest['execution']
        assert output_meta['provenance_classes'] == manifest['key_provenance']
        assert output_meta['execution_manifest_schema'] == SCHEMA_V2
        try:
            bind_output_meta({'selected_keys': ['foreign']}, manifest)
        except ValueError:
            pass
        else:
            raise AssertionError('foreign workflow output keys were contract-bound')
        validate_profile(manifest, cfg, 'c4')
        try:
            validate_profile(manifest, cfg, 'c1')
        except ValueError:
            pass
        else:
            raise AssertionError('profile-slot mismatch passed')
        other = os.path.join(d, 'other'); os.makedirs(other)
        try:
            validate_profile(manifest, other, 'c4')
        except ValueError:
            pass
        else:
            raise AssertionError('config-directory mismatch passed')
        locks = os.path.join(d, 'locks')
        with ActiveCallClaim(manifest['execution']['config_dir_fingerprint'], locks):
            try:
                with ActiveCallClaim(manifest['execution']['config_dir_fingerprint'], locks):
                    pass
            except RuntimeError:
                pass
            else:
                raise AssertionError('two concurrent c4 claims were admitted')
        with ActiveCallClaim(manifest['execution']['config_dir_fingerprint'], locks):
            pass
        # H2173 G10: these three pinned 29999/30000 as the boundary, which silently encoded
        # `verdict_for`'s then-default policy (`production_v1`). That default was itself the
        # F-B4 defect — it stayed at v1 while CURRENT_POLICY advanced to v2 and then v3 — so
        # the assertions passed for the wrong reason and would have had to be re-typed on
        # every ceiling bump. Derive the boundary from the live policy instead; the INTENT
        # (strictly-under passes, at-the-ceiling fails, an unvalidated schema always fails)
        # is unchanged and now cannot go stale.
        _live_ceil = probe_log.POLICIES[probe_log.CURRENT_POLICY]['latency_ceil_ms']
        assert verdict_for(_live_ceil - 1, 0, 6000, 'warmup', schema_valid=True)[0] == 'GO'
        assert verdict_for(_live_ceil, 0, 6000, 'warmup', schema_valid=True)[0] == 'NO-GO'
        assert verdict_for(1000, 0, 6000, 'warmup', schema_valid=None)[0] == 'NO-GO'
        # The retired policies must still judge at their historical numbers — rows stamped
        # with them were genuinely gated there, and re-pointing a name falsifies that record.
        assert verdict_for(30000, 0, 6000, 'warmup', schema_valid=True,
                           policy='production_v1')[0] == 'NO-GO'
        assert verdict_for(29999, 0, 6000, 'warmup', schema_valid=True,
                           policy='production_v1')[0] == 'GO'

        # --- Phase-2 pins (R8 dup keys, P-1 batches subset, P-3 route enforce, R9 stale lock) ---
        # R8: duplicate selected_keys rejected (multiset), not silently deduped by set().
        dup = fixture(cfg); dup['meta']['selected_keys'] = ['real', 'real', 'canary']
        try:
            validate_manifest(dup, require_v2=True)
        except ValueError as e:
            assert 'duplicate' in str(e), e
        else:
            raise AssertionError('R8: duplicate selected_keys admitted')

        # P-1: a batch/presplit key outside selected_keys is refused before any spawn.
        stray = fixture(cfg); stray['batches'] = [['real', 'ghost']]
        try:
            validate_manifest(stray, require_v2=True)
        except ValueError as e:
            assert 'selected_keys' in str(e) and 'ghost' in str(e), e
        else:
            raise AssertionError('P-1: batch key outside selected_keys admitted')
        strayp = fixture(cfg); strayp['presplit_keys'] = ['ghost']
        try:
            validate_manifest(strayp, require_v2=True)
        except ValueError:
            pass
        else:
            raise AssertionError('P-1: presplit key outside selected_keys admitted')
        okb = fixture(cfg); okb['batches'] = [['real', 'canary']]
        validate_manifest(okb, require_v2=True)         # fully inside selected_keys -> valid

        # P-3: a foreign execution_route is refused AT EXECUTION (validate_profile), not run.
        foreign = fixture(cfg); foreign['execution']['execution_route'] = 'workflow'
        try:
            validate_profile(foreign, cfg, 'c4')
        except ValueError as e:
            assert 'execution_route' in str(e), e
        else:
            raise AssertionError('P-3: foreign execution_route executed')

        # R9 KERNEL-backed lock -- this is ALSO the P-2 pin ("two concurrent launches on one
        # fingerprint serialise"): a live SEPARATE process holding it refuses a second acquisition,
        # so cross-process concurrency on one profile is bounded to 1 regardless of the manifest's
        # advisory max_wide/stagger. Forcibly terminating the holder releases the lock IMMEDIATELY
        # (no TTL, no PID probe, no stale adoption). A leftover lock file may remain but must not
        # represent ownership.
        srcdir = os.path.dirname(os.path.abspath(__file__))
        fp = manifest['execution']['config_dir_fingerprint']
        r9 = os.path.join(d, 'r9'); os.makedirs(r9)
        ready = os.path.join(d, 'holder.ready')
        holder_code = (
            'import sys, os, time; sys.path.insert(0, %r);'
            'from execution_contract import ActiveCallClaim;'
            'c = ActiveCallClaim(%r, %r); c.__enter__();'
            'open(%r, "w").close(); time.sleep(120)'
        ) % (srcdir, fp, r9, ready)
        holder = subprocess.Popen([sys.executable, '-c', holder_code])
        try:
            for _ in range(200):
                if os.path.exists(ready):
                    break
                time.sleep(0.05)
            assert os.path.exists(ready), 'R9: holder process never acquired the lock'
            try:
                with ActiveCallClaim(fp, r9):
                    raise AssertionError('R9: acquired a lock held by a live separate process')
            except RuntimeError:
                pass
        finally:
            holder.kill()
            holder.wait()
        with ActiveCallClaim(fp, r9):        # kernel released it on death -> immediate reacquire
            pass
    _test_h2254_timeout_ceiling_boundary()
    print('execution_contract_selftest: PASS')


def _test_h2254_timeout_ceiling_boundary():
    """H2254: `validate_manifest` refuses a sealed budget above the production maximum.

    This is the layer the executor's own guard cannot cover on its own: a manifest is
    validated by `coordinator`, by `max_account_orchestrator` and by `headless_worker`, and
    only the last one constructs an engine. A ceiling enforced solely in the engine would let
    the two planning routes accept a manifest they will later be unable to run.

    Boundary values are derived from the constant, never restated -- FINDINGS §518: a test
    that writes 300001 as a literal keeps asserting a dead number after the next ruling.
    """
    ceiling = PRODUCTION_HARD_TIMEOUT_MS
    with tempfile.TemporaryDirectory() as d:
        cfg = os.path.join(d, 'profile')
        os.makedirs(cfg)
        for value in (None, 1, ceiling - 1, ceiling):
            manifest = fixture(cfg)
            if value is not None:
                manifest['budgets'] = {'timeout_ceil_ms': value}
            validate_manifest(manifest, require_v2=True)     # accepted: at or below maximum
        over = fixture(cfg)
        over['budgets'] = {'timeout_ceil_ms': ceiling + 1}
        try:
            validate_manifest(over, require_v2=True)
        except ValueError as exc:
            assert 'REFUSED' in str(exc) and str(ceiling) in str(exc), str(exc)
        else:
            raise AssertionError('validate_manifest accepted a %d ms ceiling above the %d ms '
                                 'production maximum' % (ceiling + 1, ceiling))
        # A v1 manifest is still executable via --allow-historical-v1, so the money guard must
        # bind there too -- it is checked ahead of the schema branch for exactly this reason.
        legacy = {'schema': 'pwg.headless_execution_manifest.v1',
                  'budgets': {'timeout_ceil_ms': ceiling + 1}}
        try:
            validate_manifest(legacy, require_v2=False)
        except ValueError:
            pass
        else:
            raise AssertionError('a v1 manifest bypassed the ceiling refusal')
    print('  H2254 manifest ceiling: <=%d accepted, %d refused (v1 and v2)'
          % (ceiling, ceiling + 1))


if __name__ == '__main__':
    main()
