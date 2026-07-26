#!/usr/bin/env python
"""Recoverable promotion journal for the PWG-RU canonical-store transaction.

The journal seals the bytes a promotion intends to install before the canonical
store is replaced.  Startup reconciliation can consequently distinguish:

* the old store hash: retry the prepared replacement;
* the expected new hash: adopt a replacement whose phase update was interrupted;
* any other hash: fail closed and require operator investigation.

This module deliberately does not use the historical ``promotion_receipt``
scaffold.  A receipt described key presence after the fact; this journal seals
the complete before/after byte identity before mutation.
"""
from __future__ import annotations

import argparse
import ctypes
import datetime
import hashlib
import json
import os
import sys
import tempfile
from typing import Any, Callable, Mapping

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
if SRC not in sys.path:
    sys.path.insert(0, SRC)
from promote_lock import PromoteClaim  # noqa: E402

SCHEMA = 'pwg.promotion_journal.v1'
COORDINATOR_STATE_SCHEMA = 'pwg.sla_coordinator.state.v1'
PROMOTION_REGISTRY_SCHEMA = 'pwg.sla_coordinator.artifact.v1'
PHASES = (
    'prepared',
    'store_committed',
    'derived_validated',
    'coordinator_committed',
    'complete',
)
_PHASE_INDEX = {name: i for i, name in enumerate(PHASES)}


class JournalError(RuntimeError):
    """The journal is malformed or an attempted transition is unsafe."""


class UnrelatedStoreError(JournalError):
    """The live store matches neither the sealed before nor after identity."""


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(
        timespec='seconds').replace('+00:00', 'Z')


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def file_fingerprint(path: str, *, missing_ok: bool = False) -> dict[str, Any]:
    """Return an exact SHA/size/row fingerprint for *path*.

    ``rows`` is the count of non-empty lines, matching the canonical JSONL
    store's row semantics.  Missing optional derived files are represented
    explicitly rather than conflated with an empty file.
    """
    absolute = os.path.abspath(path)
    if not os.path.exists(absolute):
        if missing_ok:
            return {
                'path': absolute, 'exists': False, 'sha256': None,
                'bytes': 0, 'rows': 0,
            }
        raise FileNotFoundError(absolute)
    digest = hashlib.sha256()
    size = 0
    rows = 0
    with open(absolute, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            digest.update(chunk)
            size += len(chunk)
            rows += sum(1 for line in chunk.splitlines() if line.strip())
    # A line spanning chunks could be counted twice by splitlines. Canonical
    # rows are small today, but compute rows exactly to keep this primitive true.
    with open(absolute, 'rb') as fh:
        rows = sum(1 for line in fh if line.strip())
    return {
        'path': absolute, 'exists': True, 'sha256': digest.hexdigest(),
        'bytes': size, 'rows': rows,
    }


def bytes_fingerprint(path: str, payload: bytes) -> dict[str, Any]:
    return {
        'path': os.path.abspath(path),
        'exists': True,
        'sha256': sha256_bytes(payload),
        'bytes': len(payload),
        'rows': sum(1 for line in payload.splitlines() if line.strip()),
    }


def aggregate_files(paths: list[str]) -> dict[str, Any]:
    """Seal ordered clean-output files into one deterministic aggregate hash."""
    files = []
    for path in sorted(os.path.abspath(p) for p in paths):
        fp = file_fingerprint(path)
        files.append({
            'path': fp['path'], 'sha256': fp['sha256'], 'bytes': fp['bytes'],
        })
    canonical = json.dumps(files, ensure_ascii=False, sort_keys=True,
                           separators=(',', ':')).encode('utf-8')
    return {'sha256': sha256_bytes(canonical), 'count': len(files), 'files': files}


def canonical_path(path: str) -> str:
    """Canonical comparison spelling for a filesystem target."""
    return os.path.normcase(os.path.realpath(os.path.abspath(path)))


def _fsync_directory(path: str) -> None:
    """Durably persist a POSIX rename's directory entry."""
    if os.name == 'nt':
        return
    directory = os.path.dirname(os.path.abspath(path)) or '.'
    flags = os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0)
    fd = os.open(directory, flags)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def fsync_existing_path(path: str) -> None:
    """Re-establish file and directory durability before adopting a projection."""
    # Windows' CRT rejects fsync() on a read-only descriptor (EBADF).
    fd = os.open(path, os.O_RDWR)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    _fsync_directory(path)


def durable_replace(source: str, destination: str) -> None:
    """Replace *destination* durably or fail loudly.

    Windows' ordinary ``os.replace`` does not request write-through semantics.
    MoveFileExW with both REPLACE_EXISTING and WRITE_THROUGH closes that gap.
    POSIX uses rename followed by a mandatory parent-directory fsync.
    """
    source = os.path.abspath(source)
    destination = os.path.abspath(destination)
    if os.name == 'nt':
        move_file = ctypes.WinDLL('kernel32', use_last_error=True).MoveFileExW
        move_file.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32]
        move_file.restype = ctypes.c_int
        movefile_replace_existing = 0x1
        movefile_write_through = 0x8
        if not move_file(source, destination,
                         movefile_replace_existing | movefile_write_through):
            raise ctypes.WinError(ctypes.get_last_error())
        return
    os.replace(source, destination)
    _fsync_directory(destination)


def atomic_write_bytes(path: str, payload: bytes) -> str:
    """Fsync temporary bytes and durably replace *path*."""
    absolute = os.path.abspath(path)
    directory = os.path.dirname(absolute) or '.'
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        prefix='.%s.' % os.path.basename(absolute), suffix='.tmp', dir=directory)
    try:
        with os.fdopen(fd, 'wb') as fh:
            fh.write(payload)
            fh.flush()
            os.fsync(fh.fileno())
        durable_replace(tmp, absolute)
    except BaseException:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise
    return absolute


def stable_json_bytes(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
            + '\n').encode('utf-8')


def atomic_write_json(path: str, value: Mapping[str, Any]) -> str:
    """Durably replace *path* with stable JSON."""
    return atomic_write_bytes(path, stable_json_bytes(value))


def fault(hook: Callable[[str], None] | None, point: str) -> None:
    """Invoke an injectable crash hook used only by offline/temp tests."""
    if hook is not None:
        hook(point)


def load(path: str) -> dict[str, Any]:
    with open(path, encoding='utf-8') as fh:
        journal = json.load(fh)
    validate(journal)
    return journal


def validate(journal: Mapping[str, Any]) -> None:
    if journal.get('schema') != SCHEMA:
        raise JournalError('unsupported journal schema %r' % journal.get('schema'))
    if journal.get('phase') not in PHASES:
        raise JournalError('invalid journal phase %r' % journal.get('phase'))
    for key in ('promotion_id', 'model_identifier', 'review_status',
                'artifact_timestamp'):
        if not isinstance(journal.get(key), str) or not journal[key]:
            raise JournalError('journal.%s must be a non-empty string' % key)
    lease_ids = journal.get('lease_ids')
    bindings = journal.get('bindings')
    leases = journal.get('leases')
    if (not isinstance(lease_ids, list) or not lease_ids
            or any(not isinstance(value, str) or not value for value in lease_ids)
            or lease_ids != sorted(set(lease_ids))):
        raise JournalError('journal.lease_ids must be a sorted unique non-empty list')
    if not isinstance(bindings, Mapping) or sorted(bindings) != lease_ids:
        raise JournalError('journal.bindings must exactly cover lease_ids')
    if not isinstance(leases, Mapping) or sorted(leases) != lease_ids:
        raise JournalError('journal.leases must exactly cover lease_ids')
    for lease_id in lease_ids:
        binding = bindings[lease_id]
        metrics = leases[lease_id]
        if not isinstance(binding, Mapping) or not isinstance(metrics, Mapping):
            raise JournalError('%s binding/metrics must be objects' % lease_id)
        for name in ('run_id', 'attempt_id'):
            value = binding.get(name)
            if value is not None and (not isinstance(value, str) or not value):
                raise JournalError('%s.%s must be null or a non-empty string'
                                   % (lease_id, name))
            if metrics.get(name) != value:
                raise JournalError('%s metrics/binding %s mismatch' % (lease_id, name))
        clean = metrics.get('clean_output')
        subcards = metrics.get('subcard_keys')
        if (not isinstance(clean, Mapping)
                or not isinstance(clean.get('sha256'), str)
                or not isinstance(clean.get('count'), int)):
            raise JournalError('%s missing clean-output hash/count' % lease_id)
        if (not isinstance(subcards, list) or not subcards
                or subcards != sorted(set(subcards))
                or metrics.get('subcards') != len(subcards)):
            raise JournalError('%s has invalid sealed subcards' % lease_id)
    expected_run_ids = {
        lease_id: bindings[lease_id]['run_id']
        for lease_id in lease_ids if bindings[lease_id].get('run_id')
    }
    if journal.get('run_ids') != expected_run_ids:
        raise JournalError('journal.run_ids does not match exact bindings')
    clean_output = journal.get('clean_output')
    union_subcards = sorted(
        key for lease_id in lease_ids for key in leases[lease_id]['subcard_keys'])
    if (not isinstance(clean_output, Mapping)
            or clean_output.get('subcards') != union_subcards
            or clean_output.get('subcard_count') != len(union_subcards)
            or clean_output.get('card_count') != len(union_subcards)):
        raise JournalError('journal.clean_output does not match per-lease subcards')
    store = journal.get('store')
    if not isinstance(store, Mapping):
        raise JournalError('journal.store must be an object')
    for key in ('path', 'before_sha256', 'expected_after_sha256'):
        if not isinstance(store.get(key), str) or not store[key]:
            raise JournalError('journal.store.%s must be a non-empty string' % key)
    for key in ('before_rows', 'expected_after_rows'):
        if isinstance(store.get(key), bool) or not isinstance(store.get(key), int):
            raise JournalError('journal.store.%s must be an int' % key)
    if store['path'] != canonical_path(store['path']):
        raise JournalError('journal.store.path is not canonical: %s' % store['path'])
    backup = store.get('backup')
    if not isinstance(backup, Mapping) or not backup.get('path'):
        raise JournalError('journal.store.backup is required')
    if backup['path'] != canonical_path(backup['path']):
        raise JournalError('journal.store.backup.path is not canonical')
    if (backup.get('sha256') != store['before_sha256']
            or backup.get('rows') != store['before_rows']
            or backup.get('bytes') != store.get('before_bytes')):
        raise JournalError('journal.store.backup does not seal the before store')
    report = journal.get('report')
    if not isinstance(report, Mapping):
        raise JournalError('journal.report must seal the deterministic report')
    if (report.get('promotion_id') != journal['promotion_id']
            or report.get('leases') != leases
            or report.get('journal_phase') != 'store_committed'
            or report.get('model_identifier') != journal['model_identifier']
            or report.get('review_status') != journal['review_status']
            or report.get('clean_output_sha256') != clean_output.get('sha256')
            or report.get('store_sha256') != store['expected_after_sha256']):
        raise JournalError('journal.report does not match sealed promotion intent')
    if (report.get('report_path') is not None
            and report['report_path'] != canonical_path(report['report_path'])):
        raise JournalError('journal.report.report_path is not canonical')
    if _PHASE_INDEX[journal['phase']] >= _PHASE_INDEX['derived_validated']:
        derived = journal.get('derived')
        if (not isinstance(derived, Mapping) or derived.get('errors')
                or not all(isinstance(derived.get(kind), Mapping)
                           for kind in ('denylist', 'card_tm', 'fragment_tm'))
                or not derived['card_tm'].get('validated')
                or not derived['fragment_tm'].get('validated')):
            raise JournalError('derived_validated journal lacks validated sealed artifacts')
    if _PHASE_INDEX[journal['phase']] >= _PHASE_INDEX['coordinator_committed']:
        coordinator = journal.get('coordinator')
        if (not isinstance(coordinator, Mapping)
                or not isinstance(coordinator.get('intent'), Mapping)
                or not coordinator.get('committed_at')):
            raise JournalError(
                'coordinator_committed journal lacks sealed coordinator evidence')


def _immutable_projection(journal: Mapping[str, Any]) -> dict[str, Any]:
    """Fields that must be byte-identical on a retry of ``prepare``."""
    return {
        'schema': journal.get('schema'),
        'promotion_id': journal.get('promotion_id'),
        'lease_ids': journal.get('lease_ids'),
        'run_ids': journal.get('run_ids'),
        'bindings': journal.get('bindings'),
        'model_identifier': journal.get('model_identifier'),
        'review_status': journal.get('review_status'),
        'clean_output': journal.get('clean_output'),
        'store': journal.get('store'),
        'leases': journal.get('leases'),
        'report': journal.get('report'),
    }


def prepare(
    path: str,
    *,
    promotion_id: str | None,
    lease_ids: list[str],
    run_ids: Mapping[str, str] | None,
    bindings: Mapping[str, Mapping[str, str | None]],
    model_identifier: str,
    review_status: str,
    clean_output: Mapping[str, Any],
    store: Mapping[str, Any],
    leases: Mapping[str, Any],
    report: Mapping[str, Any],
    fault_hook: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    """Create a durable PREPARED journal, or verify an idempotent retry."""
    if not promotion_id:
        raise JournalError('prepare requires an explicit stable promotion_id')
    now = utc_now()
    sealed_store = dict(store)
    sealed_store['path'] = canonical_path(str(sealed_store['path']))
    if isinstance(sealed_store.get('backup'), Mapping):
        sealed_store['backup'] = dict(sealed_store['backup'])
        sealed_store['backup']['path'] = canonical_path(
            str(sealed_store['backup']['path']))
        sealed_store['backup_path'] = sealed_store['backup']['path']
    candidate = {
        'schema': SCHEMA,
        'promotion_id': promotion_id,
        'phase': 'prepared',
        'lease_ids': sorted(lease_ids),
        'run_ids': dict(sorted((run_ids or {}).items())),
        'bindings': {key: dict(bindings[key]) for key in sorted(bindings)},
        'model_identifier': model_identifier,
        'review_status': review_status,
        'clean_output': dict(clean_output),
        'store': sealed_store,
        'leases': dict(leases),
        'report': dict(report),
        'derived': {
            'denylist': None,
            'card_tm': None,
            'fragment_tm': None,
            'validated_at': None,
            'observations': [],
            'errors': [],
            'error_history': [],
        },
        'coordinator': {'intent': None, 'committed_at': None, 'error': None},
        'artifact_timestamp': now,
        'created_at': now,
        'updated_at': now,
        'history': [{'phase': 'prepared', 'at': now}],
    }
    validate(candidate)
    if os.path.exists(path):
        existing = load(path)
        if _immutable_projection(existing) != _immutable_projection(candidate):
            raise JournalError(
                'existing journal does not match this promotion intent: %s' % path)
        fault(fault_hook, 'prepared')
        return existing
    atomic_write_json(path, candidate)
    fault(fault_hook, 'prepared')
    return candidate


def _advance(
    path: str,
    next_phase: str,
    *,
    expected_phase: str | None = None,
    updates: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Durably advance exactly one phase; same-phase re-entry is idempotent."""
    if next_phase not in PHASES:
        raise JournalError('unknown next phase %r' % next_phase)
    journal = load(path)
    current = journal['phase']
    if current == next_phase:
        return journal
    if expected_phase is not None and current != expected_phase:
        raise JournalError('phase is %s, expected %s' % (current, expected_phase))
    if _PHASE_INDEX[next_phase] != _PHASE_INDEX[current] + 1:
        raise JournalError('refusing non-adjacent phase transition %s -> %s'
                           % (current, next_phase))
    if updates:
        for key, value in updates.items():
            journal[key] = value
    now = utc_now()
    journal['phase'] = next_phase
    journal['updated_at'] = now
    journal.setdefault('history', []).append({'phase': next_phase, 'at': now})
    validate(journal)
    atomic_write_json(path, journal)
    return journal


def verify_backup(journal: Mapping[str, Any], *, required: bool) -> None:
    sealed = journal['store']['backup']
    path = sealed['path']
    if not os.path.isfile(path):
        if required:
            raise JournalError('sealed promotion backup is missing: %s' % path)
        return
    observed = file_fingerprint(path)
    for field in ('sha256', 'rows', 'bytes'):
        if observed[field] != sealed[field]:
            raise JournalError('sealed promotion backup %s mismatch' % field)


def verify_committed_store(journal: Mapping[str, Any]) -> dict[str, Any]:
    """Require the live canonical store to equal this journal's sealed result."""
    store = journal['store']
    observed = file_fingerprint(store['path'], missing_ok=True)
    if (not observed['exists']
            or observed['sha256'] != store['expected_after_sha256']
            or observed['rows'] != store['expected_after_rows']
            or observed['bytes'] != store['expected_after_bytes']):
        raise UnrelatedStoreError(
            'committed promotion journal no longer matches live store '
            '(observed=%s expected=%s)'
            % (observed.get('sha256'), store['expected_after_sha256']))
    verify_backup(journal, required=True)
    return observed


def reconcile(
    path: str,
    *,
    adopt_after: bool = True,
    store_claim_held: bool = False,
) -> dict[str, Any]:
    """Inspect/adopt store state using the journal's sealed before/after hashes."""
    journal = load(path)
    if journal['phase'] == 'complete':
        return {
            'promotion_id': journal['promotion_id'],
            'phase': 'complete',
            'observed': None,
            'action': 'terminal_complete',
        }
    if not store_claim_held:
        with PromoteClaim(journal['store']['path']):
            return reconcile(
                path, adopt_after=adopt_after, store_claim_held=True)
    store = journal['store']
    observed = file_fingerprint(store['path'], missing_ok=True)
    before = store['before_sha256']
    after = store['expected_after_sha256']
    if not observed['exists']:
        raise UnrelatedStoreError('canonical store is missing: %s' % store['path'])
    result = {
        'promotion_id': journal['promotion_id'],
        'phase': journal['phase'],
        'observed': observed,
        'action': None,
    }
    if journal['phase'] == 'prepared':
        if observed['sha256'] == before and observed['rows'] == store['before_rows']:
            verify_backup(journal, required=False)
            result['action'] = 'retry_store_replace'
            return result
        if (observed['sha256'] == after
                and observed['rows'] == store['expected_after_rows']):
            verify_backup(journal, required=True)
            result['action'] = 'adopt_store_commit'
            if adopt_after:
                journal = _advance(path, 'store_committed', expected_phase='prepared')
                result['phase'] = journal['phase']
            return result
        raise UnrelatedStoreError(
            'live store hash is neither sealed before nor expected-after '
            '(observed=%s before=%s after=%s)'
            % (observed['sha256'], before, after))
    verify_committed_store(journal)
    if journal['phase'] in ('derived_validated', 'coordinator_committed'):
        verify_sealed_artifacts(journal)
    if journal['phase'] == 'coordinator_committed':
        reconcile_coordinator(
            path, adopt_after=False, store_claim_held=True)
    result['action'] = 'already_store_committed'
    return result


def mark_store_committed(
    path: str,
    *,
    store_claim_held: bool = False,
) -> dict[str, Any]:
    """Verify the expected bytes are live, then durably mark STORE_COMMITTED."""
    result = reconcile(
        path, adopt_after=True, store_claim_held=store_claim_held)
    if result['action'] not in ('adopt_store_commit', 'already_store_committed'):
        raise JournalError('store still has before hash; replacement has not committed')
    return load(path)


def mark_derived_validated(
    path: str,
    *,
    denylist_path: str | None = None,
    card_tm_path: str | None = None,
    fragment_tm_path: str | None = None,
    errors: list[str] | None = None,
    lang: str = 'ru',
    fault_hook: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    """Seal derived artifacts and advance after successful validation."""
    journal = load(path)
    if journal['phase'] == 'complete':
        return journal
    if _PHASE_INDEX[journal['phase']] >= _PHASE_INDEX['derived_validated']:
        verify_sealed_artifacts(journal)
        return journal
    if journal['phase'] != 'store_committed':
        raise JournalError('derived validation requires store_committed, got %s'
                           % journal['phase'])
    if not denylist_path or not card_tm_path or not fragment_tm_path:
        raise JournalError(
            'derived validation requires denylist plus existing validated '
            'card and fragment TM paths')
    try:
        try:
            import translation_memory as tm
        except ImportError:
            from pilot import translation_memory as tm
        card_ok, card_stats = tm.validate_tm_file(lang, card_tm_path, kind='card')
        frag_ok, frag_stats = tm.validate_tm_file(
            lang, fragment_tm_path, kind='fragment')
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise JournalError('derived TM validation failed: %s' % exc) from exc
    if not tm.validation_ok(card_stats) or not tm.validation_ok(frag_stats):
        raise JournalError(
            'derived TM validation failed: card=%s fragment=%s'
            % (dict(card_stats), dict(frag_stats)))
    with open(card_tm_path, encoding='utf-8') as fh:
        card_payload = json.load(fh)
    if card_payload.get('built_at') != journal['artifact_timestamp']:
        raise JournalError(
            'card TM built_at %r does not match journal artifact timestamp %r'
            % (card_payload.get('built_at'), journal['artifact_timestamp']))
    derived = dict(journal.get('derived') or {})
    current_errors = list(derived.get('errors') or [])
    supplied_errors = list(errors or [])
    if supplied_errors:
        derived.setdefault('error_history', []).extend(supplied_errors)
        current_errors.extend(supplied_errors)
    if current_errors:
        raise JournalError('derived artifacts have unresolved errors: %s'
                           % current_errors)
    now = journal['artifact_timestamp']
    card_fp = file_fingerprint(card_tm_path)
    card_fp.update({'validated': True, 'valid_rows': card_ok,
                    'validation_stats': dict(card_stats), 'validated_at': now})
    frag_fp = file_fingerprint(fragment_tm_path)
    frag_fp.update({'validated': True, 'valid_rows': frag_ok,
                    'validation_stats': dict(frag_stats), 'validated_at': now})
    deny_fp = file_fingerprint(denylist_path, missing_ok=True)
    deny_fp['validated_at'] = now
    derived.update({
        'denylist': deny_fp,
        'card_tm': card_fp,
        'fragment_tm': frag_fp,
        'validated_at': now,
        'errors': current_errors,
    })
    result = _advance(path, 'derived_validated', expected_phase='store_committed',
                      updates={'derived': derived})
    fault(fault_hook, 'derived')
    return result


def verify_sealed_artifacts(journal_or_path: Mapping[str, Any] | str) -> None:
    """Re-fingerprint every artifact sealed at DERIVED_VALIDATED."""
    journal = (load(journal_or_path) if isinstance(journal_or_path, str)
               else dict(journal_or_path))
    if _PHASE_INDEX[journal['phase']] < _PHASE_INDEX['derived_validated']:
        raise JournalError('derived artifacts are not yet sealed')
    derived = journal.get('derived') or {}
    if derived.get('errors'):
        raise JournalError('derived artifacts have unresolved errors: %s'
                           % derived['errors'])
    for kind in ('denylist', 'card_tm', 'fragment_tm'):
        sealed = derived.get(kind)
        if not isinstance(sealed, Mapping):
            raise JournalError('missing sealed derived artifact %s' % kind)
        observed = (file_fingerprint(sealed['path'], missing_ok=True)
                    if sealed.get('path') else {
                        'path': None, 'exists': False, 'sha256': None,
                        'bytes': 0, 'rows': 0,
                    })
        for field in ('path', 'exists', 'sha256', 'bytes', 'rows'):
            if observed.get(field) != sealed.get(field):
                raise JournalError(
                    'sealed %s changed after validation (%s: %r != %r)'
                    % (kind, field, observed.get(field), sealed.get(field)))


def record_derived_observation(
    path: str,
    kind: str,
    *,
    artifact_path: str | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    """Durably record one derived-side effect without advancing its phase.

    This is used immediately after denylist/TM work so a crash before the full
    derived-validation barrier still leaves timestamps, hashes, and errors.
    """
    if kind not in ('denylist', 'card_tm', 'fragment_tm'):
        raise JournalError('unknown derived artifact kind %r' % kind)
    journal = load(path)
    if journal['phase'] != 'store_committed':
        raise JournalError('derived observations require store_committed, got %s'
                           % journal['phase'])
    derived = dict(journal.get('derived') or {})
    observation = (file_fingerprint(artifact_path, missing_ok=True)
                   if artifact_path else {'path': None, 'exists': False,
                                          'sha256': None, 'bytes': 0, 'rows': 0})
    observation['observed_at'] = utc_now()
    observation['error'] = error
    derived[kind] = observation
    derived.setdefault('observations', []).append({
        'kind': kind, **observation,
    })
    errors = [value for value in list(derived.get('errors') or [])
              if not value.startswith('%s: ' % kind)]
    if error:
        message = '%s: %s' % (kind, error)
        errors.append(message)
        derived.setdefault('error_history', []).append(message)
    derived['errors'] = errors
    journal['derived'] = derived
    journal['updated_at'] = utc_now()
    atomic_write_json(path, journal)
    return journal


def _require_utc_second_timestamp(value: Any, field: str) -> None:
    if not isinstance(value, str):
        raise JournalError('%s must be a UTC second timestamp' % field)
    try:
        parsed = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')
    except ValueError as exc:
        raise JournalError('%s must be a UTC second timestamp' % field) from exc
    if parsed.strftime('%Y-%m-%dT%H:%M:%SZ') != value:
        raise JournalError('%s must be a UTC second timestamp' % field)


def _validate_promotion_registry_projection(
    journal_path: str,
    journal: Mapping[str, Any],
    expected_state: Mapping[str, Any],
    lease_outcomes: Mapping[str, Any],
    registry_path: str,
    registry_events: list[Mapping[str, Any]],
) -> dict[str, Any]:
    """Return the canonical registry projection or refuse an incomplete seal.

    The coordinator owns the event builder, but importing it here would create
    a cycle.  Keep this exact mirror deliberately small: the promoted event is
    derived from the already-sealed journal plus the coordinator state bytes
    that will be committed in the same transaction.
    """
    artifact_timestamp = journal['artifact_timestamp']
    _require_utc_second_timestamp(
        artifact_timestamp, 'journal.artifact_timestamp')
    if not isinstance(registry_path, str) or not registry_path:
        raise JournalError('promotion registry path must be a non-empty string')
    if expected_state.get('schema') != COORDINATOR_STATE_SCHEMA:
        raise JournalError('expected coordinator state has unsupported schema')
    state_leases = expected_state.get('leases')
    if not isinstance(state_leases, list):
        raise JournalError('expected coordinator state leases must be a list')
    leases_by_id = {}
    for lease in state_leases:
        if not isinstance(lease, Mapping):
            raise JournalError('expected coordinator state lease is not an object')
        lease_id = lease.get('id')
        if (not isinstance(lease_id, str) or not lease_id
                or lease_id in leases_by_id):
            raise JournalError(
                'expected coordinator state has invalid/duplicate lease id')
        leases_by_id[lease_id] = lease

    journal_absolute = os.path.abspath(journal_path)
    report = journal['report']
    store = journal['store']
    store_before = report.get('store_rows_before')
    store_after = report.get('store_rows_after')
    if (store_before != store['before_rows']
            or store_after != store['expected_after_rows']):
        raise JournalError(
            'journal report store row metrics do not match sealed store')
    bundle_store_delta = store_after - store_before

    last_promotion = expected_state.get('last_promotion')
    expected_last_promotion = {
        'promotion_id': journal['promotion_id'],
        'journal': journal_absolute,
        'lease_outcomes': dict(lease_outcomes),
        'model_identifier': journal['model_identifier'],
        'store_sha256': store['expected_after_sha256'],
        'committed_at': artifact_timestamp,
    }
    if last_promotion != expected_last_promotion:
        raise JournalError(
            'expected coordinator state has inconsistent last_promotion')
    if expected_state.get('updated_at') != artifact_timestamp:
        raise JournalError(
            'expected coordinator state timestamp does not match journal artifact')

    expected_events = []
    for lease_id in journal['lease_ids']:
        outcome = lease_outcomes[lease_id]
        if outcome not in ('promoted', 'promoted_partial'):
            raise JournalError(
                '%s has invalid coordinator lease outcome %r'
                % (lease_id, outcome))
        lease = leases_by_id.get(lease_id)
        if lease is None:
            raise JournalError(
                'expected coordinator state lacks lease %s' % lease_id)
        metrics = journal['leases'][lease_id]
        clean_files = (metrics.get('clean_output') or {}).get('files') or []
        if (len(clean_files) != 1
                or not isinstance(clean_files[0], Mapping)
                or not clean_files[0].get('path')
                or not clean_files[0].get('sha256')):
            raise JournalError(
                '%s registry projection requires one sealed clean output'
                % lease_id)
        for field in ('kind', 'target', 'artifact_dir'):
            if not isinstance(lease.get(field), str) or not lease[field]:
                raise JournalError(
                    'expected coordinator lease %s lacks %s'
                    % (lease_id, field))
        expected_lease_facts = {
            'state': outcome,
            'promoted_at': artifact_timestamp,
            'promotion_id': journal['promotion_id'],
            'promotion_journal': journal_absolute,
            'model_version': journal['model_identifier'],
            'store_before': store_before,
            'store_after': store_after,
            'store_delta': metrics['store_delta'],
            'bundle_store_delta': bundle_store_delta,
            'promoted_subcards': metrics['subcards'],
            'promoted_rows': metrics['rows'],
            'rows_added': metrics['rows_added'],
            'rows_replaced': metrics['rows_replaced'],
            'clean_count': metrics['subcards'],
            'clean_output_sha256': clean_files[0]['sha256'],
        }
        for field, expected_value in expected_lease_facts.items():
            if lease.get(field) != expected_value:
                raise JournalError(
                    'expected coordinator lease %s has inconsistent %s'
                    % (lease_id, field))
        binding = journal['bindings'][lease_id]
        if binding.get('run_id') is not None:
            attempts = lease.get('run_attempts')
            completed = attempts[-1] if isinstance(attempts, list) and attempts else {}
            if (completed.get('run_id') != binding['run_id']
                    or completed.get('run_operation_id') != binding.get('attempt_id')):
                raise JournalError(
                    'expected coordinator lease %s lacks sealed run binding'
                    % lease_id)
        expected_events.append({
            'schema': PROMOTION_REGISTRY_SCHEMA,
            'ts': artifact_timestamp,
            'lease_id': lease_id,
            'event': 'promoted',
            'kind': lease['kind'],
            'target': lease['target'],
            'state': outcome,
            'artifact_dir': lease['artifact_dir'],
            'data': {
                'glob': clean_files[0]['path'],
                'journal': journal_absolute,
                'store_before': store_before,
                'store_after': store_after,
                'store_delta': metrics['store_delta'],
                'bundle_store_delta': bundle_store_delta,
                'rows_added': metrics['rows_added'],
                'rows_replaced': metrics['rows_replaced'],
                'batch_subcards': metrics['subcards'],
                'batch_rows': metrics['rows'],
                'promotion_id': journal['promotion_id'],
            },
        })

    supplied = [dict(row) for row in registry_events]
    if supplied != expected_events:
        raise JournalError(
            'registry events do not match canonical promotion projection')
    return {
        'path': canonical_path(registry_path),
        'events': expected_events,
    }


def prepare_coordinator_commit(
    path: str,
    *,
    state_path: str,
    expected_state_bytes: bytes,
    lease_outcomes: Mapping[str, Any],
    promotion_marker: Any,
    registry_path: str,
    registry_events: list[Mapping[str, Any]],
    store_claim_held: bool = False,
    fault_hook: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    """Seal exact coordinator state bytes before the coordinator-state replace."""
    journal = load(path)
    if not store_claim_held:
        with PromoteClaim(journal['store']['path']):
            return prepare_coordinator_commit(
                path,
                state_path=state_path,
                expected_state_bytes=expected_state_bytes,
                lease_outcomes=lease_outcomes,
                promotion_marker=promotion_marker,
                registry_path=registry_path,
                registry_events=registry_events,
                store_claim_held=True,
                fault_hook=fault_hook,
            )
    if _PHASE_INDEX[journal['phase']] < _PHASE_INDEX['derived_validated']:
        raise JournalError('coordinator intent requires derived_validated, got %s'
                           % journal['phase'])
    if journal['phase'] != 'complete':
        verify_committed_store(journal)
        verify_sealed_artifacts(journal)
    if promotion_marker != journal['promotion_id']:
        raise JournalError('coordinator promotion marker must equal journal promotion_id')
    if not isinstance(lease_outcomes, Mapping):
        raise JournalError('coordinator lease outcomes must be an object')
    if sorted(lease_outcomes) != journal['lease_ids']:
        raise JournalError('coordinator lease outcomes must exactly cover journal leases')
    if (not isinstance(registry_events, list) or not registry_events
            or len(registry_events) != len(journal['lease_ids'])
            or any(not isinstance(row, Mapping) for row in registry_events)):
        raise JournalError('registry events must be one non-empty object per lease')
    event_lease_ids = [row.get('lease_id') for row in registry_events]
    if (any(not isinstance(lease_id, str) or not lease_id
            for lease_id in event_lease_ids)
            or sorted(event_lease_ids) != journal['lease_ids']):
        raise JournalError('registry events must exactly cover journal leases')
    try:
        expected_state = json.loads(expected_state_bytes.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise JournalError('expected coordinator state must be UTF-8 JSON') from exc
    if not isinstance(expected_state, Mapping):
        raise JournalError('expected coordinator state must be a JSON object')
    registry = _validate_promotion_registry_projection(
        path, journal, expected_state, lease_outcomes,
        registry_path, registry_events)

    def _contains(value: Any, wanted: Any) -> bool:
        if value == wanted:
            return True
        if isinstance(value, Mapping):
            return any(_contains(child, wanted) for child in value.values())
        if isinstance(value, list):
            return any(_contains(child, wanted) for child in value)
        return False

    if not _contains(expected_state, promotion_marker):
        raise JournalError('expected coordinator state lacks the promotion marker')
    if not _contains(expected_state, dict(lease_outcomes)):
        raise JournalError('expected coordinator state lacks exact lease outcomes')
    state_path = canonical_path(state_path)
    expected = bytes_fingerprint(state_path, expected_state_bytes)
    coordinator = dict(journal.get('coordinator') or {})
    existing = coordinator.get('intent')
    if existing is not None:
        retry_projection = {
            'state_path': state_path,
            'expected': expected,
            'lease_outcomes': dict(lease_outcomes),
            'promotion_marker': promotion_marker,
            'registry': registry,
        }
        sealed_projection = {
            key: existing.get(key) for key in retry_projection
        }
        if sealed_projection != retry_projection:
            raise JournalError('coordinator state intent changed on retry')
        fault(fault_hook, 'coordinator_prepared')
        return journal
    before = file_fingerprint(state_path, missing_ok=True)
    intent = {
        'state_path': state_path,
        'before': before,
        'expected': expected,
        'lease_outcomes': dict(lease_outcomes),
        'promotion_marker': promotion_marker,
        'registry': registry,
        'prepared_at': journal['artifact_timestamp'],
    }
    coordinator['intent'] = intent
    journal['coordinator'] = coordinator
    journal['updated_at'] = utc_now()
    atomic_write_json(path, journal)
    fault(fault_hook, 'coordinator_prepared')
    return journal


def reconcile_coordinator(
    path: str,
    *,
    adopt_after: bool = True,
    store_claim_held: bool = False,
    fault_hook: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    """Reconcile/adopt a crash after coordinator state was durably saved."""
    journal = load(path)
    if journal['phase'] == 'complete':
        return {
            'phase': 'complete', 'observed': None,
            'action': 'terminal_complete',
        }
    if not store_claim_held:
        with PromoteClaim(journal['store']['path']):
            return reconcile_coordinator(
                path, adopt_after=adopt_after, store_claim_held=True,
                fault_hook=fault_hook)
    verify_committed_store(journal)
    verify_sealed_artifacts(journal)
    intent = (journal.get('coordinator') or {}).get('intent')
    if not isinstance(intent, Mapping):
        raise JournalError('coordinator state intent is not sealed')
    observed = file_fingerprint(intent['state_path'], missing_ok=True)
    before = intent['before']
    expected = intent['expected']
    result = {'phase': journal['phase'], 'observed': observed, 'action': None}
    expected_match = all(observed.get(field) == expected.get(field)
                         for field in ('path', 'exists', 'sha256', 'bytes', 'rows'))
    before_match = all(observed.get(field) == before.get(field)
                       for field in ('path', 'exists', 'sha256', 'bytes', 'rows'))
    if journal['phase'] == 'derived_validated':
        if before_match:
            result['action'] = 'write_coordinator_state'
            return result
        if expected_match:
            result['action'] = 'adopt_coordinator_commit'
            if adopt_after:
                coordinator = dict(journal['coordinator'])
                coordinator.update({
                    'committed_at': utc_now(), 'error': None,
                    'observed': observed,
                })
                journal = _advance(
                    path, 'coordinator_committed',
                    expected_phase='derived_validated',
                    updates={'coordinator': coordinator})
                result['phase'] = journal['phase']
                fault(fault_hook, 'coordinator_adopted')
            return result
        raise JournalError(
            'coordinator state matches neither sealed before nor expected hash')
    if not expected_match:
        raise JournalError('committed coordinator state no longer matches sealed hash')
    result['action'] = 'already_coordinator_committed'
    return result


def commit_coordinator_state(
    path: str,
    expected_state_bytes: bytes,
    *,
    store_claim_held: bool = False,
    fault_hook: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    """Durably save the sealed coordinator bytes, then adopt the commit."""
    journal = load(path)
    if not store_claim_held:
        with PromoteClaim(journal['store']['path']):
            return commit_coordinator_state(
                path, expected_state_bytes, store_claim_held=True,
                fault_hook=fault_hook)
    intent = (journal.get('coordinator') or {}).get('intent')
    if not isinstance(intent, Mapping):
        raise JournalError('coordinator state intent is not sealed')
    if sha256_bytes(expected_state_bytes) != intent['expected']['sha256']:
        raise JournalError('coordinator payload does not match sealed expected hash')
    reconciled = reconcile_coordinator(
        path, adopt_after=False, store_claim_held=True)
    if reconciled['action'] == 'write_coordinator_state':
        atomic_write_bytes(intent['state_path'], expected_state_bytes)
        fault(fault_hook, 'coordinator_state_saved')
    return reconcile_coordinator(
        path, adopt_after=True, store_claim_held=True,
        fault_hook=fault_hook)


def mark_coordinator_committed(
    path: str,
    *,
    error: str | None = None,
    store_claim_held: bool = False,
    fault_hook: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    """Adopt only an exact, previously sealed coordinator state."""
    if error:
        raise JournalError('coordinator commit error: %s' % error)
    journal = load(path)
    if journal['phase'] == 'complete':
        return journal
    if not store_claim_held:
        with PromoteClaim(journal['store']['path']):
            return mark_coordinator_committed(
                path, error=error, store_claim_held=True,
                fault_hook=fault_hook)
    result = reconcile_coordinator(
        path, adopt_after=True, store_claim_held=True,
        fault_hook=fault_hook)
    if result['action'] not in ('adopt_coordinator_commit',
                                'already_coordinator_committed'):
        raise JournalError('coordinator state still has its before hash')
    return load(path)


def verify_registry_projection(journal: Mapping[str, Any]) -> None:
    """Require one exact durable registry event per lease before COMPLETE."""
    intent = (journal.get('coordinator') or {}).get('intent')
    registry = (intent or {}).get('registry') if isinstance(intent, Mapping) else None
    if not isinstance(registry, Mapping):
        raise JournalError('coordinator intent lacks sealed registry projection')
    path = registry.get('path')
    expected = registry.get('events')
    if (not isinstance(path, str) or not path
            or not isinstance(expected, list) or not expected):
        raise JournalError('sealed registry projection is malformed')
    try:
        raw = open(path, 'rb').read()
    except OSError as exc:
        raise JournalError('sealed registry projection is unreadable: %s' % exc) from exc
    if raw and not raw.endswith(b'\n'):
        raise JournalError('sealed registry projection is not newline-terminated')
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError as exc:
        raise JournalError('sealed registry projection is not UTF-8') from exc
    rows = []
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise JournalError(
                'sealed registry projection has malformed JSON at line %d'
                % line_number) from exc
        if not isinstance(row, Mapping):
            raise JournalError(
                'sealed registry projection line %d is not an object'
                % line_number)
        rows.append(row)
    for event in expected:
        matches = sum(row == event for row in rows)
        if matches != 1:
            raise JournalError(
                'sealed registry event must exist exactly once (observed %d)'
                % matches)
    fsync_existing_path(path)


def mark_complete(
    path: str,
    *,
    store_claim_held: bool = False,
    fault_hook: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    journal = load(path)
    if journal['phase'] == 'complete':
        return journal
    if not store_claim_held:
        with PromoteClaim(journal['store']['path']):
            return mark_complete(
                path, store_claim_held=True, fault_hook=fault_hook)
    # The canonical store remains part of the live transaction until COMPLETE.
    # A third-party write after DERIVED_VALIDATED must block, never be blessed by
    # merely rechecking TMs and coordinator state.
    verify_committed_store(journal)
    verify_sealed_artifacts(journal)
    reconcile_coordinator(
        path, adopt_after=False, store_claim_held=True)
    verify_registry_projection(journal)
    result = _advance(path, 'complete', expected_phase='coordinator_committed')
    fault(fault_hook, 'final_journal_update')
    return result


def advance(
    path: str,
    next_phase: str,
    *,
    denylist_path: str | None = None,
    card_tm_path: str | None = None,
    fragment_tm_path: str | None = None,
) -> dict[str, Any]:
    """Safely advance through the validated public phase API."""
    if next_phase == 'store_committed':
        return mark_store_committed(path)
    if next_phase == 'derived_validated':
        return mark_derived_validated(
            path, denylist_path=denylist_path, card_tm_path=card_tm_path,
            fragment_tm_path=fragment_tm_path)
    if next_phase == 'coordinator_committed':
        return mark_coordinator_committed(path)
    if next_phase == 'complete':
        return mark_complete(path)
    raise JournalError('public advance cannot target %r' % next_phase)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n', 1)[0])
    sub = parser.add_subparsers(dest='command', required=True)
    inspect_p = sub.add_parser('inspect')
    inspect_p.add_argument('journal')
    reconcile_p = sub.add_parser('reconcile')
    reconcile_p.add_argument('journal')
    reconcile_p.add_argument('--no-adopt', action='store_true')
    advance_p = sub.add_parser('advance')
    advance_p.add_argument('journal')
    advance_p.add_argument('phase', choices=PHASES[1:])
    advance_p.add_argument('--denylist')
    advance_p.add_argument('--card-tm')
    advance_p.add_argument('--fragment-tm')
    coord_prepare = sub.add_parser('coordinator-prepare')
    coord_prepare.add_argument('journal')
    coord_prepare.add_argument('--state', required=True)
    coord_prepare.add_argument('--expected-state', required=True)
    coord_prepare.add_argument('--outcomes', required=True)
    coord_prepare.add_argument('--marker', required=True)
    coord_prepare.add_argument('--registry', required=True)
    coord_prepare.add_argument('--registry-events', required=True)
    coord_commit = sub.add_parser('coordinator-commit')
    coord_commit.add_argument('journal')
    coord_commit.add_argument('--expected-state', required=True)
    coord_reconcile = sub.add_parser('coordinator-reconcile')
    coord_reconcile.add_argument('journal')
    coord_reconcile.add_argument('--no-adopt', action='store_true')
    args = parser.parse_args(argv)
    try:
        if args.command == 'inspect':
            result = load(args.journal)
        elif args.command == 'reconcile':
            result = reconcile(args.journal, adopt_after=not args.no_adopt)
        elif args.command == 'coordinator-prepare':
            with open(args.expected_state, 'rb') as fh:
                expected_state = fh.read()
            with open(args.outcomes, encoding='utf-8') as fh:
                outcomes = json.load(fh)
            with open(args.registry_events, encoding='utf-8') as fh:
                registry_events = json.load(fh)
            result = prepare_coordinator_commit(
                args.journal, state_path=args.state,
                expected_state_bytes=expected_state,
                lease_outcomes=outcomes, promotion_marker=args.marker,
                registry_path=args.registry,
                registry_events=registry_events)
        elif args.command == 'coordinator-commit':
            with open(args.expected_state, 'rb') as fh:
                expected_state = fh.read()
            result = commit_coordinator_state(args.journal, expected_state)
        elif args.command == 'coordinator-reconcile':
            result = reconcile_coordinator(
                args.journal, adopt_after=not args.no_adopt)
        else:
            if args.phase == 'store_committed':
                result = mark_store_committed(args.journal)
            elif args.phase == 'derived_validated':
                result = mark_derived_validated(
                    args.journal, denylist_path=args.denylist,
                    card_tm_path=args.card_tm, fragment_tm_path=args.fragment_tm)
            elif args.phase == 'coordinator_committed':
                result = mark_coordinator_committed(args.journal)
            else:
                result = mark_complete(args.journal)
    except (JournalError, OSError, json.JSONDecodeError) as exc:
        print('REFUSED: %s' % exc, file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
