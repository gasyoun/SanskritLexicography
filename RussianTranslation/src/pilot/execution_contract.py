#!/usr/bin/env python
"""Profile-bound manifest-v2 validation and global active-call serialization."""
import hashlib
import json
import os
import tempfile
import time

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
    # R8: reject duplicate selected_keys -- set(classes)==set(keys) admits a duplicated key (billed
    # once, double-counted downstream), so compare lengths (multiset semantics) before launch.
    if len(keys) != len(set(keys)):
        dupes = sorted({k for k in keys if keys.count(k) > 1})
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


def _pid_alive(pid):
    """Best-effort cross-platform liveness. POSIX: os.kill(pid, 0). Windows: OpenProcess +
    GetExitCodeProcess -- os.kill on Windows can TerminateProcess, so it is never used here."""
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False
    if pid <= 0:
        return False
    if os.name == 'nt':
        import ctypes
        PROCESS_QUERY_LIMITED_INFORMATION, STILL_ACTIVE = 0x1000, 259
        k32 = ctypes.windll.kernel32
        handle = k32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            return False
        try:
            code = ctypes.c_ulong()
            if k32.GetExitCodeProcess(handle, ctypes.byref(code)):
                return code.value == STILL_ACTIVE
            return True
        finally:
            k32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True                       # exists, but no permission to signal
    except OSError:
        return False
    return True


class ActiveCallClaim:
    """Cross-process one-active-call claim keyed by credential-directory fingerprint.

    R9 (C-09/H818): a bare O_EXCL lock is NOT crash-safe. The orchestrator tree-kills the lock
    holder on a call timeout (a routine path, not a rare crash), so `__exit__` never runs and the
    lock would survive forever -- a permanent self-inflicted DoS on a credential profile. A
    contended claim therefore reclaims a lock whose owner PID is dead, or (unreadable/legacy lock)
    one older than STALE_SECS -- well past the 180 s call ceiling. It NEVER reclaims a live holder.
    """
    STALE_SECS = 300

    def __init__(self, fingerprint, root=None):
        self.root = root or os.path.join(tempfile.gettempdir(), 'pwg-active-calls')
        self.path = os.path.join(self.root, fingerprint + '.lock')
        self.owned = False

    def _stale(self):
        try:
            info = json.load(open(self.path, encoding='utf-8'))
        except (OSError, ValueError):
            info = None
        if isinstance(info, dict) and info.get('pid') is not None:
            if not _pid_alive(info.get('pid')):
                return True                                   # dead holder -> immediate reclaim
            ts = info.get('ts')
            return ts is not None and (time.time() - float(ts)) > self.STALE_SECS
        # unreadable / legacy lock (no pid): fall back to file age
        try:
            return (time.time() - os.path.getmtime(self.path)) > self.STALE_SECS
        except OSError:
            return False

    def __enter__(self):
        os.makedirs(self.root, exist_ok=True)
        for _ in range(2):
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                if self._stale():
                    try:
                        os.unlink(self.path)      # reclaim abandoned lock; retry the O_EXCL create
                    except FileNotFoundError:
                        pass
                    continue
                raise RuntimeError('profile already has an active model call')
            with os.fdopen(fd, 'w', encoding='utf-8') as fh:
                json.dump({'pid': os.getpid(), 'ts': time.time()}, fh)
                fh.flush()
                os.fsync(fh.fileno())
            self.owned = True
            return self
        raise RuntimeError('profile already has an active model call')

    def __exit__(self, _typ, _value, _tb):
        if self.owned:
            try:
                os.unlink(self.path)
            except FileNotFoundError:
                pass
            self.owned = False
