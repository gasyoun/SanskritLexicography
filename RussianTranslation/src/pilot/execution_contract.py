#!/usr/bin/env python
"""Profile-bound manifest-v2 validation and global active-call serialization."""
import collections
import hashlib
import os
import tempfile

# R9: a KERNEL-backed exclusive lock, released automatically by the OS on process death. POSIX uses
# fcntl.flock; Windows uses an msvcrt byte-range lock. Both are held for as long as the file handle
# is open and are dropped by the kernel when the holder dies -- no PID probing, TTL or stale
# adoption. Non-blocking acquisition raises OSError on contention.
if os.name == 'nt':
    import msvcrt

    def _os_lock_nb(fh):
        fh.seek(0, os.SEEK_END)
        if fh.tell() == 0:
            fh.write(b'\0')          # msvcrt locks a byte range; guarantee byte 0 exists
            fh.flush()
        fh.seek(0)
        msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)

    def _os_unlock(fh):
        try:
            fh.seek(0)
            msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
        except OSError:
            pass
else:
    import fcntl

    def _os_lock_nb(fh):
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    def _os_unlock(fh):
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass

SCHEMA_V1 = 'pwg.headless_execution_manifest.v1'
SCHEMA_V2 = 'pwg.headless_execution_manifest.v2'
PROVENANCE_CLASSES = {'real', 'synthetic_control'}
# P-3: the only execution route this headless executor can actually run. A v2 manifest declaring
# any other route (generation refuses it, but a hand-edited manifest could carry one) is refused at
# execution time, not run unmodified.
HEADLESS_ROUTE = 'claude-cli-headless'


def canonical_config_dir(path):
    return os.path.normcase(os.path.realpath(os.path.abspath(path)))


def config_dir_fingerprint(path):
    canonical = canonical_config_dir(path)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def validate_manifest(manifest, require_v2=False):
    # P-1: batches/presplit must not drive a model call for a key outside selected_keys -- else a
    # manifest whose batches name a key outside the declared set is billed anyway (selected_keys
    # gates enqueue; this gates dispatch). Applies to any executable manifest (v1 and v2).
    selected = (manifest.get('meta') or {}).get('selected_keys') or []
    if selected:
        driven = set()
        for batch in manifest.get('batches') or []:
            driven.update(batch)
        driven.update(manifest.get('presplit_keys') or [])
        stray = sorted(driven - set(selected))
        if stray:
            raise ValueError('manifest drives a call for key(s) outside selected_keys: %s'
                             % ', '.join(stray[:10]))
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
    keys = list(selected)
    # R8: reject duplicate selected_keys with explicit multiset semantics -- set(classes)==set(keys)
    # admitted a duplicated key (billed once, double-counted downstream). Counter, not keys.count().
    dupes = sorted(k for k, n in collections.Counter(keys).items() if n > 1)
    if dupes:
        raise ValueError('manifest v2 selected_keys has duplicate key(s): %s' % ', '.join(dupes))
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
    # P-3: enforce the declared route at EXECUTION, not just at generation. The headless executor
    # runs only the claude-cli-headless route; a hand-edited manifest declaring a foreign route is
    # refused here, not run unmodified ("generation-time refusal is birth control, not a gate").
    if execution['execution_route'] != HEADLESS_ROUTE:
        raise ValueError('headless executor refuses execution_route=%r (executable route is %r)'
                         % (execution['execution_route'], HEADLESS_ROUTE))
    if only_profile and execution['profile_slot'] != only_profile:
        raise ValueError('profile mismatch: manifest=%s --only-profile=%s'
                         % (execution['profile_slot'], only_profile))
    actual = config_dir_fingerprint(config_dir)
    if actual != execution['config_dir_fingerprint']:
        raise ValueError('config-directory fingerprint mismatch for profile %s'
                         % execution['profile_slot'])


def bind_output_meta(meta, manifest):
    """Stamp a workflow result with the same v2 contract used to launch it."""
    validate_manifest(manifest, require_v2=True)
    if set(meta.get('selected_keys') or []) != set(
            (manifest.get('meta') or {}).get('selected_keys') or []):
        raise ValueError('workflow metadata keys disagree with execution manifest')
    meta['execution_manifest_schema'] = SCHEMA_V2
    meta['execution'] = dict(manifest['execution'])
    meta['provenance_classes'] = dict(manifest['key_provenance'])
    return meta


class ActiveCallClaim:
    """R9: a KERNEL-backed one-active-call lock keyed by the config-directory fingerprint.

    An exclusive OS advisory lock (fcntl.flock on POSIX, an msvcrt byte-range lock on Windows) is
    held on an open file handle for the claim's lifetime. The KERNEL releases it automatically when
    the holder dies -- a tree-kill on a call timeout, a crash -- so there is NO PID probe, TTL,
    deletion or stale adoption (the permanent-DoS class the old bare O_EXCL created: __exit__ never
    ran after a tree-kill, so the lock file survived forever, blocking the profile indefinitely).

    The lock FILE is a diagnostic artifact; its existence never represents ownership -- only the
    live OS lock does -- so a leftover file after a crash is harmless: the next process locks it
    immediately. Non-blocking acquisition raises a typed RuntimeError on contention.
    """
    def __init__(self, fingerprint, root=None):
        self.root = root or os.path.join(tempfile.gettempdir(), 'pwg-active-calls')
        self.path = os.path.join(self.root, fingerprint + '.lock')
        self._fh = None

    def __enter__(self):
        os.makedirs(self.root, exist_ok=True)
        fh = open(self.path, 'a+b')
        try:
            _os_lock_nb(fh)
        except OSError:
            fh.close()
            raise RuntimeError('profile already has an active model call')
        self._fh = fh
        return self

    def __exit__(self, _typ, _value, _tb):
        fh, self._fh = self._fh, None
        if fh is not None:
            _os_unlock(fh)
            fh.close()
