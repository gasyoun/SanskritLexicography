#!/usr/bin/env python
"""Crash-durable, cross-process reservations for paid model calls.

A reservation is the spend decision: it is persisted before the caller is allowed to
spawn, and is never refunded.  This deliberately counts a crash between reserve() and
process creation conservatively.
"""
import contextlib
import json
import math
import os
import threading
import time
import uuid

SCHEMA = 'pwg.call_reservation.v1'
TOKEN_FIELDS = ('input_tokens', 'output_tokens', 'cache_read_tokens',
                'cache_creation_tokens', 'subagent_tokens')
# H2079 / #945: the CLI result envelope's OWN timings, recorded beside the tokens. Wall clock alone
# cannot say whether a slow call was a slow route or an in-CLI retry storm (a rate-limited CLI hangs
# rather than reporting 429 — Uprava FINDINGS §270), which is what made the 15-07 / 16-07 / 31-07 c4
# readings unusable as route evidence and left a published "~65 s CLI startup" claim untestable.
# `duration_api_ms` is the discriminator, and it was already sitting in the envelope, parsed and
# discarded one line away.
#
# OPTIONAL and OMITTED when absent — never emitted as an explicit None. `_read()` re-validates every
# stored item and `finalize()` compares an already-finalized item against a freshly normalized one,
# so a ledger written before this change must round-trip byte-identically or those invariants trip.
DURATION_FIELDS = ('duration_ms', 'duration_api_ms')


def _valid_number(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and value >= 0)


def normalize_telemetry(value):
    """Validate one call's final telemetry and return its canonical representation."""
    if not isinstance(value, dict):
        raise ValueError('call telemetry must be an object')
    evaluable = value.get('cost_evaluable')
    if not isinstance(evaluable, bool):
        raise ValueError('call telemetry cost_evaluable must be boolean')
    out = {'cost_evaluable': evaluable}
    for name in TOKEN_FIELDS:
        number = value.get(name, 0)
        if not _valid_number(number):
            raise ValueError('%s must be finite, non-negative and non-boolean' % name)
        out[name] = number
    cost = value.get('observed_cost_usd', 0)
    if not _valid_number(cost):
        raise ValueError('observed_cost_usd must be finite, non-negative and non-boolean')
    if evaluable and 'observed_cost_usd' not in value:
        raise ValueError('evaluable telemetry requires observed_cost_usd')
    out['observed_cost_usd'] = cost
    # H2079 / #945: carried only when the envelope actually reported them, so pre-H2079 ledgers
    # normalize to exactly the bytes they already hold. Validated like any other number, but a bad
    # timing never affects `cost_evaluable` — evaluability is a statement about COST, and demoting a
    # run because a duration was malformed would be a new, unrelated failure mode.
    for name in DURATION_FIELDS:
        if value.get(name) is None:
            continue
        if not _valid_number(value[name]):
            raise ValueError('%s must be finite, non-negative and non-boolean' % name)
        out[name] = value[name]
    return out


def unevaluable_telemetry():
    return normalize_telemetry({'cost_evaluable': False})


def telemetry_from_cli_wrapper(wrapper):
    """Extract trustworthy CLI usage without ever admitting invalid numeric telemetry."""
    if not isinstance(wrapper, dict):
        return unevaluable_telemetry()
    usage = wrapper.get('usage')
    valid = isinstance(usage, dict)
    values = {}
    mapping = {
        'input_tokens': 'input_tokens',
        'output_tokens': 'output_tokens',
        'cache_read_tokens': 'cache_read_input_tokens',
        'cache_creation_tokens': 'cache_creation_input_tokens',
    }
    for target, source in mapping.items():
        raw = usage.get(source, 0) if isinstance(usage, dict) else 0
        if not _valid_number(raw):
            valid = False
            raw = 0
        values[target] = raw
    values['subagent_tokens'] = sum(values.values())
    cost = wrapper.get('total_cost_usd')
    if not _valid_number(cost):
        valid = False
        cost = 0
    values['observed_cost_usd'] = cost
    values['cost_evaluable'] = valid
    # H2079 / #945: the envelope's own timings, deliberately read AFTER `valid` is settled and never
    # folded into it. A missing/garbage duration leaves the call fully cost-evaluable; it just means
    # this particular reading cannot be decomposed into route time vs in-CLI backoff.
    for name in DURATION_FIELDS:
        raw = wrapper.get(name)
        if _valid_number(raw):
            values[name] = raw
    return normalize_telemetry(values)


def _empty_usage():
    return {
        'input_tokens': 0, 'output_tokens': 0, 'cache_read_tokens': 0,
        'cache_creation_tokens': 0, 'subagent_tokens': 0,
        'observed_cost_usd': 0.0, 'cost_evaluable': True,
        'finalized_calls': 0, 'unevaluable_calls': 0, 'pending_calls': 0,
    }


class CallLimitReached(RuntimeError):
    pass


_THREAD_LOCKS = {}
_THREAD_LOCKS_GUARD = threading.Lock()


def _thread_lock(path):
    key = os.path.normcase(os.path.abspath(path))
    with _THREAD_LOCKS_GUARD:
        return _THREAD_LOCKS.setdefault(key, threading.RLock())


@contextlib.contextmanager
def _os_lock(path):
    """Serialize both threads and processes on Windows and POSIX."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    local = _thread_lock(path)
    with local:
        fh = open(path, 'a+b')
        try:
            if os.name == 'nt':
                import msvcrt
                fh.seek(0, os.SEEK_END)
                if fh.tell() == 0:
                    fh.write(b'\0')
                    fh.flush()
                fh.seek(0)
                msvcrt.locking(fh.fileno(), msvcrt.LK_LOCK, 1)
            else:
                import fcntl
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
            yield
        finally:
            try:
                fh.seek(0)
                if os.name == 'nt':
                    import msvcrt
                    msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
            finally:
                fh.close()


def _read(path):
    if not os.path.exists(path):
        return {'schema': SCHEMA, 'runs': {}}
    with open(path, encoding='utf-8') as f:
        value = json.load(f)
    if (not isinstance(value, dict) or value.get('schema') != SCHEMA
            or not isinstance(value.get('runs'), dict)):
        raise ValueError('call reservation ledger schema mismatch: %s' % path)
    for run_id, run in value['runs'].items():
        if not isinstance(run_id, str) or not run_id or not isinstance(run, dict):
            raise ValueError('call reservation ledger has an invalid run: %s' % path)
        limit = run.get('max_calls')
        if limit is not None and (
                isinstance(limit, bool) or not isinstance(limit, int) or limit < 0):
            raise ValueError('%s: saved max_calls is invalid' % run_id)
        reservations = run.get('reservations')
        spent = run.get('calls_spent')
        next_ordinal = run.get('next_ordinal')
        if (not isinstance(reservations, list)
                or isinstance(spent, bool) or not isinstance(spent, int) or spent < 0
                or spent != len(reservations)
                or isinstance(next_ordinal, bool)
                or not isinstance(next_ordinal, int)
                or next_ordinal != spent + 1):
            raise ValueError('%s: reservation counters are inconsistent' % run_id)
        ids, idempotency_keys, ordinals = set(), set(), []
        for item in reservations:
            if (not isinstance(item, dict)
                    or not isinstance(item.get('reservation_id'), str)
                    or not item['reservation_id']
                    or item['reservation_id'] in ids
                    or isinstance(item.get('ordinal'), bool)
                    or not isinstance(item.get('ordinal'), int)
                    or not isinstance(item.get('purpose'), str)
                    or not item['purpose']):
                raise ValueError('%s: reservation entry is invalid' % run_id)
            ids.add(item['reservation_id'])
            ordinals.append(item['ordinal'])
            idempotency_key = item.get('idempotency_key')
            if idempotency_key is not None:
                if (not isinstance(idempotency_key, str) or not idempotency_key
                        or idempotency_key in idempotency_keys):
                    raise ValueError('%s: reservation idempotency key is invalid' % run_id)
                idempotency_keys.add(idempotency_key)
            if item.get('finalized'):
                normalize_telemetry(item.get('telemetry'))
                evidence = item.get('finalization_evidence')
                if evidence is not None and not isinstance(evidence, dict):
                    raise ValueError('%s: finalization evidence is invalid' % run_id)
        if ordinals != list(range(1, spent + 1)):
            raise ValueError('%s: reservation ordinals are inconsistent' % run_id)
        # ``usage`` was added to the same v1 schema after the original
        # reservation-only deployment.  Its one supported migration is handled
        # by _initialize; once present it must exactly equal the reservations.
        usage = run.get('usage')
        if usage is not None:
            expected = _empty_usage()
            expected['pending_calls'] = 0
            for item in reservations:
                if not item.get('finalized'):
                    expected['pending_calls'] += 1
                    continue
                telemetry = normalize_telemetry(item['telemetry'])
                for name in TOKEN_FIELDS:
                    expected[name] += telemetry[name]
                expected['observed_cost_usd'] += telemetry['observed_cost_usd']
                expected['finalized_calls'] += 1
                if not telemetry['cost_evaluable']:
                    expected['unevaluable_calls'] += 1
            expected['cost_evaluable'] = (
                expected['pending_calls'] == 0
                and expected['unevaluable_calls'] == 0)
            if usage != expected:
                raise ValueError('%s: cumulative usage is inconsistent' % run_id)
    return value


def _durable_replace(source, destination):
    """Publish a ledger update with write-through rename semantics."""
    if os.name == 'nt':
        import ctypes
        from ctypes import wintypes
        move = ctypes.WinDLL('kernel32', use_last_error=True).MoveFileExW
        move.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD]
        move.restype = wintypes.BOOL
        # REPLACE_EXISTING | WRITE_THROUGH
        if not move(source, destination, 0x1 | 0x8):
            raise OSError(ctypes.get_last_error(), 'MoveFileExW failed', destination)
        return
    os.replace(source, destination)
    directory = os.path.dirname(os.path.abspath(destination)) or '.'
    flags = os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0)
    fd = os.open(directory, flags)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _write(path, value):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = '%s.tmp.%d.%s' % (path, os.getpid(), uuid.uuid4().hex)
    try:
        with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(value, f, ensure_ascii=False, indent=1)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
        _durable_replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


class CallReservationLedger:
    """One run's view of a ledger shared by all probes and workers."""

    def __init__(self, path, run_id, max_calls=None):
        if not path:
            raise ValueError('call reservation path is required')
        if not run_id:
            raise ValueError('call reservation run_id is required')
        if max_calls is not None and (
                isinstance(max_calls, bool) or not isinstance(max_calls, int) or max_calls < 0):
            raise ValueError('max_calls must be a non-negative integer or None')
        self.path = os.path.abspath(path)
        self.lock_path = self.path + '.lock'
        self.run_id = str(run_id)
        self.max_calls = max_calls
        self._initialize()

    @classmethod
    def open_existing(cls, path, run_id):
        """Open an existing run without making up or changing its ceiling."""
        absolute = os.path.abspath(path)
        with _os_lock(absolute + '.lock'):
            run = _read(absolute)['runs'].get(str(run_id))
            if run is None:
                raise ValueError('call reservation run missing: %s' % run_id)
            max_calls = run.get('max_calls')
        return cls(absolute, run_id, max_calls)

    def _initialize(self):
        with _os_lock(self.lock_path):
            data = _read(self.path)
            run = data['runs'].get(self.run_id)
            if run is None:
                run = {'max_calls': self.max_calls, 'calls_spent': 0,
                       'next_ordinal': 1, 'reservations': [], 'usage': _empty_usage()}
                data['runs'][self.run_id] = run
                _write(self.path, data)
                return
            saved = run.get('max_calls')
            if saved != self.max_calls:
                raise ValueError(
                    'call reservation max_calls mismatch for run %s: saved=%r requested=%r'
                    % (self.run_id, saved, self.max_calls))
            if 'usage' not in run:
                # Forward-compatible adoption of a v1 reservation-only file.
                usage = _empty_usage()
                usage['pending_calls'] = sum(
                    not item.get('finalized') for item in run.get('reservations', []))
                usage['cost_evaluable'] = usage['pending_calls'] == 0
                run['usage'] = usage
                _write(self.path, data)

    def reserve(self, purpose, profile=None, detail=None, idempotency_key=None):
        """Atomically spend one call slot and return its durable reservation.

        ``idempotency_key`` is optional for legacy callers.  When supplied, a
        replay returns the one existing reservation only when all caller-bound
        fields still match.  The lookup and first reservation share the same
        cross-process lock, so two competing prepares cannot double-spend.
        """
        if idempotency_key is not None and (
                not isinstance(idempotency_key, str) or not idempotency_key):
            raise ValueError('idempotency_key must be a non-empty string')
        with _os_lock(self.lock_path):
            data = _read(self.path)
            run = data['runs'].get(self.run_id)
            if run is None:
                raise ValueError('call reservation run disappeared: %s' % self.run_id)
            if idempotency_key is not None:
                existing = next((row for row in run.get('reservations', [])
                                 if row.get('idempotency_key') == idempotency_key), None)
                if existing is not None:
                    expected = {
                        'purpose': str(purpose),
                        'profile': None if profile is None else str(profile),
                        'detail': None if detail is None else str(detail),
                    }
                    actual = {name: existing.get(name) for name in expected}
                    if actual != expected:
                        raise ValueError(
                            'idempotent reservation replay changed bound fields')
                    return dict(existing)
            spent = int(run.get('calls_spent') or 0)
            limit = run.get('max_calls')
            if limit is not None and spent >= int(limit):
                raise CallLimitReached(
                    'model call ceiling reached for run %s (%d/%d)'
                    % (self.run_id, spent, int(limit)))
            ordinal = int(run.get('next_ordinal') or (spent + 1))
            item = {
                'reservation_id': uuid.uuid4().hex,
                'ordinal': ordinal,
                'reserved_at_ns': time.time_ns(),
                'pid': os.getpid(),
                'purpose': str(purpose),
            }
            if profile is not None:
                item['profile'] = str(profile)
            if detail is not None:
                item['detail'] = str(detail)
            if idempotency_key is not None:
                item['idempotency_key'] = idempotency_key
            run.setdefault('reservations', []).append(item)
            run['calls_spent'] = spent + 1
            run['next_ordinal'] = ordinal + 1
            usage = run.setdefault('usage', _empty_usage())
            usage['pending_calls'] = int(usage.get('pending_calls') or 0) + 1
            usage['cost_evaluable'] = False
            _write(self.path, data)
            return dict(item)

    def finalize(self, reservation, telemetry, evidence=None):
        """Idempotently attach telemetry and optional response-bound evidence."""
        normalized = normalize_telemetry(telemetry)
        if evidence is not None:
            if not isinstance(evidence, dict):
                raise ValueError('finalization evidence must be an object')
            # Detach from caller-owned mutable values and require JSON-safe data.
            evidence = json.loads(json.dumps(
                evidence, ensure_ascii=False, sort_keys=True, separators=(',', ':')))
        reservation_id = (reservation.get('reservation_id')
                          if isinstance(reservation, dict) else reservation)
        if not reservation_id:
            raise ValueError('reservation_id is required for finalization')
        with _os_lock(self.lock_path):
            data = _read(self.path)
            run = data['runs'].get(self.run_id)
            if run is None:
                raise ValueError('call reservation run disappeared: %s' % self.run_id)
            item = next((row for row in run.get('reservations', [])
                         if row.get('reservation_id') == reservation_id), None)
            if item is None:
                raise ValueError('unknown call reservation: %s' % reservation_id)
            if item.get('finalized'):
                if item.get('telemetry') != normalized:
                    raise ValueError('reservation already finalized with different telemetry')
                if item.get('finalization_evidence') != evidence:
                    raise ValueError(
                        'reservation already finalized with different evidence')
                return dict(item)
            item['finalized'] = True
            item['finalized_at_ns'] = time.time_ns()
            item['telemetry'] = normalized
            if evidence is not None:
                item['finalization_evidence'] = evidence
            usage = run.setdefault('usage', _empty_usage())
            for name in TOKEN_FIELDS:
                usage[name] = usage.get(name, 0) + normalized[name]
            usage['observed_cost_usd'] = (
                usage.get('observed_cost_usd', 0.0) + normalized['observed_cost_usd'])
            usage['finalized_calls'] = int(usage.get('finalized_calls') or 0) + 1
            usage['pending_calls'] = max(0, int(usage.get('pending_calls') or 0) - 1)
            if not normalized['cost_evaluable']:
                usage['unevaluable_calls'] = int(usage.get('unevaluable_calls') or 0) + 1
            usage['cost_evaluable'] = (
                int(usage.get('pending_calls') or 0) == 0
                and int(usage.get('unevaluable_calls') or 0) == 0)
            _write(self.path, data)
            return dict(item)

    def snapshot(self):
        with _os_lock(self.lock_path):
            run = _read(self.path)['runs'].get(self.run_id)
            if run is None:
                raise ValueError('call reservation run missing: %s' % self.run_id)
            return json.loads(json.dumps(run))

    def spent(self):
        return int(self.snapshot().get('calls_spent') or 0)

    def usage(self):
        return dict(self.snapshot().get('usage') or _empty_usage())


def run_ids(path):
    """Return existing run IDs without creating a run."""
    lock_path = os.path.abspath(path) + '.lock'
    with _os_lock(lock_path):
        return sorted(_read(os.path.abspath(path))['runs'])
