#!/usr/bin/env python
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from execution_contract import (ActiveCallClaim, SCHEMA_V2, config_dir_fingerprint,
                                validate_manifest, validate_profile)
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
        assert verdict_for(29999, 0, 6000, 'warmup', schema_valid=True)[0] == 'GO'
        assert verdict_for(30000, 0, 6000, 'warmup', schema_valid=True)[0] == 'NO-GO'
        assert verdict_for(1000, 0, 6000, 'warmup', schema_valid=None)[0] == 'NO-GO'
    print('execution_contract_selftest: PASS')


if __name__ == '__main__':
    main()
