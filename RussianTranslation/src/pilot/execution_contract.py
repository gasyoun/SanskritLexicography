#!/usr/bin/env python
"""Profile-bound manifest-v2 validation and global active-call serialization."""
import hashlib
import json
import os
import tempfile

SCHEMA_V1 = 'pwg.headless_execution_manifest.v1'
SCHEMA_V2 = 'pwg.headless_execution_manifest.v2'
PROVENANCE_CLASSES = {'real', 'synthetic_control'}


def canonical_config_dir(path):
    return os.path.normcase(os.path.realpath(os.path.abspath(path)))


def config_dir_fingerprint(path):
    canonical = canonical_config_dir(path)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def validate_manifest(manifest, require_v2=False):
    schema = manifest.get('schema')
    if schema == SCHEMA_V1 and not require_v2:
        return
    if schema != SCHEMA_V2:
        raise ValueError('production requires %s (got %r)' % (SCHEMA_V2, schema))
    execution = manifest.get('execution') or {}
    required = ('profile_slot', 'config_dir_fingerprint', 'execution_route',
                'executor_lane', 'validation_method', 'model_identifier')
    missing = [name for name in required if not isinstance(execution.get(name), str)
               or not execution[name].strip()]
    if missing:
        raise ValueError('manifest v2 missing execution field(s): %s' % ', '.join(missing))
    if len(execution['config_dir_fingerprint']) != 64:
        raise ValueError('manifest v2 has malformed config-directory fingerprint')
    keys = (manifest.get('meta') or {}).get('selected_keys') or []
    classes = manifest.get('key_provenance')
    if not isinstance(classes, dict) or set(classes) != set(keys):
        raise ValueError('manifest v2 key_provenance must exactly cover selected_keys')
    unknown = {key: value for key, value in classes.items()
               if value not in PROVENANCE_CLASSES}
    if unknown:
        raise ValueError('manifest v2 has unknown provenance class(es): %r' % unknown)
    if execution['model_identifier'] != manifest.get('model'):
        raise ValueError('manifest v2 model identifier disagrees with executable model')


def validate_profile(manifest, config_dir, only_profile=None):
    validate_manifest(manifest, require_v2=True)
    execution = manifest['execution']
    if only_profile and execution['profile_slot'] != only_profile:
        raise ValueError('profile mismatch: manifest=%s --only-profile=%s'
                         % (execution['profile_slot'], only_profile))
    actual = config_dir_fingerprint(config_dir)
    if actual != execution['config_dir_fingerprint']:
        raise ValueError('config-directory fingerprint mismatch for profile %s'
                         % execution['profile_slot'])


class ActiveCallClaim:
    """Cross-process one-active-call claim keyed by credential-directory fingerprint."""
    def __init__(self, fingerprint, root=None):
        self.root = root or os.path.join(tempfile.gettempdir(), 'pwg-active-calls')
        self.path = os.path.join(self.root, fingerprint + '.lock')
        self.owned = False

    def __enter__(self):
        os.makedirs(self.root, exist_ok=True)
        try:
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise RuntimeError('profile already has an active model call')
        with os.fdopen(fd, 'w', encoding='utf-8') as fh:
            json.dump({'pid': os.getpid()}, fh)
            fh.flush()
            os.fsync(fh.fileno())
        self.owned = True
        return self

    def __exit__(self, _typ, _value, _tb):
        if self.owned:
            try:
                os.unlink(self.path)
            except FileNotFoundError:
                pass
            self.owned = False
