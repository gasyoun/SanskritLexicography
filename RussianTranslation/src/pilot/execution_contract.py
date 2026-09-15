#!/usr/bin/env python
"""Profile-bound manifest-v2 validation and global active-call serialization."""
import collections
import datetime
import hashlib
import json
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

# H2254: the ONE authoritative production per-call subprocess ceiling, in milliseconds.
#
# Owner ruling 03-08-2026: the ceiling may stand at a bounded 300 000 ms. That is an ABSOLUTE
# MAXIMUM, not a licence to raise it further -- any future increase needs a new owner ruling
# backed by measured evidence. Lower operator ceilings remain valid and are the normal case.
#
# WHY IT LIVES HERE and not in `headless_worker`: #983 showed the ceiling was enforced in five
# independent places (`headless_worker.HARD_TIMEOUT_MS`, `gen_opt_harness2.KILL_CEIL_MS`, the
# `KILL_CEIL_MS` baked into every generated `run_pilot_wf.*.js`, each sealed manifest's
# `budgets.timeout_ceil_ms`, and the operator's own `--timeout`) and that raising ONE of them
# is inert. `headless_worker_selftest.test_kill_ceiling_in_step_with_harness` pinned two of
# them EQUAL, which catches drift but still leaves two copied literals to drift. This module
# is imported by both the generator and the executor already, so both now IMPORT the number
# instead of restating it -- the handoff's "prefer generation/import/checks over copied
# constants". The parity selftest is deliberately KEPT: it is now a guard against someone
# re-introducing a literal, which is the failure it was written for.
#
# The second half of the fix is that exceeding it is a REFUSAL, not a silent clamp. Before
# H2254 every route did `min(operator, ceil, HARD)`, so a manifest or an operator asking for
# 7 200 s got 300 s and no signal: the request was wrong, the run looked normal, and the
# discrepancy only ever surfaced by reading the effective timeout out of a subprocess call.
#
# H2313 owner ruling 06-08-2026 (the measured-evidence raise H2254 anticipated):
# 300 000 ms was killing HEALTHY card spawns, not hung ones. Reading every committed
# pwg_ru card-phase envelope (h2189/h2250/h2251, see
# `h2313_timeout_distribution.py` and `pwg_ru/h2313/HARD_TIMEOUT_MS_RECALIBRATE_06-08-2026.md`)
# gives 16 completed spawns spanning wall_ms 49 404-511 908 (p50=189 327, p90=276 521,
# p95=342 997, p99=478 125) against 4 censored (killed-before-completion) spawns at
# 300 000 ms x3 and 900 000 ms x1. The old 300 000 ms ceiling sits inside the completed
# distribution (below p90), so it was manufacturing failures on the slow-but-healthy tail,
# not screening hangs.
#
# New ceiling: 600 000 ms = p99 (478 125 ms) + ~25% margin, comfortably above the observed
# completed max (511 908 ms) -- the chosen percentile is p99-with-margin, not a round-number
# guess. This is NOT claimed to be a clean hang/slow separator: the one 900 000 ms censored
# spawn proves a call can still be running well past 600 000 ms, and there is no way to tell
# from total wall-clock alone whether that spawn was slow-but-alive or genuinely hung -- a
# total-wall cap cannot make that distinction from a single constant. What this raise DOES
# claim: it stops killing calls that finish inside the range every other completed call
# finished in. Separating "hung" from "very slow" for real needs a no-output-progress
# watchdog (kill on stalled output, not on total elapsed time), left as residual work.
#
# Per the 03-08-2026 ruling above: any FUTURE increase past this needs its own owner ruling
# backed by measured evidence, same as this one was.
PRODUCTION_HARD_TIMEOUT_MS = 600000


def assert_timeout_within_ceiling(value_ms, source, ceiling_ms=PRODUCTION_HARD_TIMEOUT_MS):
    """Fail closed on a per-call timeout request above the production hard maximum.

    ``value_ms`` of ``None`` (unset) passes -- absence is not a request. Anything at or below
    the ceiling passes: LOWER operator ceilings stay valid, which is the whole point of having
    a maximum rather than a fixed value. ``ceiling_ms`` is a parameter only so tests can pin
    the boundary arithmetic without monkeypatching a module constant.
    """
    if value_ms is None:
        return
    try:
        requested = int(value_ms)
    except (TypeError, ValueError):
        raise ValueError('%s: per-call timeout must be an integer number of milliseconds '
                         '(got %r)' % (source, value_ms))
    if requested > ceiling_ms:
        raise ValueError(
            '%s requests %d ms, above the %d ms production hard maximum (H2254 owner ruling '
            '03-08-2026). This is REFUSED, not clamped: a silently clamped request runs at a '
            'bound the operator never asked for. Lower the request, or obtain a new owner '
            'ruling backed by measured evidence.' % (source, requested, ceiling_ms))


# H2878 (issue #1680, FINDINGS §378): the no-output-progress window, in milliseconds.
#
# This is NOT a second ceiling and NOT a re-fit of PRODUCTION_HARD_TIMEOUT_MS (H2299 ban).
# It measures a DIFFERENT quantity. The hard timeout bounds TOTAL WALL CLOCK; this bounds
# the longest stretch during which the spawn produced no result bytes. The comment above
# PRODUCTION_HARD_TIMEOUT_MS states the reason in full and names this as its own residual:
# a total-wall cap "cannot make that distinction from a single constant. Separating 'hung'
# from 'very slow' for real needs a no-output-progress watchdog (kill on stalled output,
# not on total elapsed time), left as residual work."
#
# 90 000 ms is the H2878 handoff's ruled default. It is deliberately NOT derived from the
# H2313 wall distribution -- deriving a stalled-output window from total-wall percentiles
# would be the exact category error this constant exists to end. It is a liveness bound:
# a healthy streaming spawn that has said nothing for a minute and a half is not slow, it
# is stopped. PRODUCTION_HARD_TIMEOUT_MS remains the last-resort backstop underneath it.
PRODUCTION_NO_OUTPUT_PROGRESS_MS = 90000

# The two kill reasons a bounded spawn can report. They are DISTINCT on purpose: before
# H2878 every killed call came back as a bare `timeout`, so a hung route and a call the
# production lane would still have been waiting on were the same event row (the 13-08 c1
# reading -- 300 198 ms, 0 output bytes -- is exactly that shape).
KILLED_REASON_HARD_TIMEOUT = 'hard_timeout'
KILLED_REASON_NO_OUTPUT_PROGRESS = 'no_output_progress'
KILLED_REASONS = (KILLED_REASON_HARD_TIMEOUT, KILLED_REASON_NO_OUTPUT_PROGRESS)

# WHICH `--output-format` values can emit PARTIAL output before the call ends.
#
# This set is the whole reason the watchdog is not armed blind. Every production spawn in
# this tree (`headless_worker`, `_probe_call`, `gen_opt_harness2`) runs
# `claude -p --output-format json`, which buffers the entire CLI result envelope and writes
# it in ONE burst when the call finishes. On that shape stdout is legitimately 0 bytes for
# the whole call, and the H2313 evidence says a healthy card spawn runs 49 404-511 908 ms
# (p50 189 327). Arming a 90 s stalled-output window against it would kill every healthy
# call -- the identical defect H2313 diagnosed in the 300 000 ms ceiling ("killing HEALTHY
# card spawns, not hung ones"), only six times more aggressive. `stream-json` is the format
# that emits incrementally, and on it the window means what it says.
#
# So the window is DERIVED from the spawn's output format rather than pinned by a literal
# at each call site: a lane that switches to `stream-json` arms the watchdog by doing so,
# and no lane can arm it against a buffered format by copying a constant.
STREAMING_OUTPUT_FORMATS = frozenset({'stream-json'})

# H4528 (10-09-2026 handoff, measured 14-09-2026): `stream-json` ALONE is NOT incremental
# enough, and the interlock above armed on it. Without `--include-partial-messages` the CLI
# emits one line per COMPLETED message -- `system/init` at start, then nothing until a whole
# assistant turn has finished generating. Measured two ways, zero paid calls:
#   * the real CLI 2.1.251 against a local fake Messages API: plain stream-json went 18 170 ms
#     silent in an 18 800 ms call; with partial messages the longest silence was 3 030 ms,
#     exactly the injected time-to-first-token;
#   * the 31 committed success envelopes (pwg_ru/h4528/): `ttft_ms` -- the CLI's time to the
#     first COMPLETE message, i.e. plain stream-json's silence -- reaches 391 798 ms (p50
#     62 487) and exceeds 90 000 ms on 9 of 31 HEALTHY calls. Arming 90 s on plain stream-json
#     would have killed 29 % of them.
# So arming now requires the token-stream flag, and the decision is read from the ACTUAL argv
# (`progress_window_ms_for_argv`) rather than from a format name a call site could mislabel.
TOKEN_STREAM_FLAG = '--include-partial-messages'
#: The exact output arguments that make a spawn emit token-level progress on stdout.
#: `--verbose` is required by the CLI for stream-json under `-p`.
TOKEN_STREAM_OUTPUT_ARGS = ('--output-format', 'stream-json', '--verbose', TOKEN_STREAM_FLAG)
#: The historical buffered output arguments (one envelope, written at the end).
BUFFERED_OUTPUT_ARGS = ('--output-format', 'json')


def progress_window_ms_for(output_format, window_ms=PRODUCTION_NO_OUTPUT_PROGRESS_MS,
                           partial_messages=False):
    """The no-output-progress window to ARM for a spawn with this ``--output-format``.

    Returns ``window_ms`` only for a format that emits TOKEN-level output -- `stream-json`
    WITH ``--include-partial-messages`` (H4528) -- and ``None`` (observe only, never kill)
    for everything else, including plain `stream-json`, which buffers per message. ``None``
    does not mean "unmeasured": the runner still records ``bytes_seen`` and ``quiet_ms`` for
    every spawn, which is what turns a future arming decision into a reading, not a guess.
    """
    if output_format in STREAMING_OUTPUT_FORMATS and partial_messages:
        return window_ms
    return None


def output_shape_of_argv(argv):
    """``(output_format, partial_messages)`` of a Claude CLI argv. Format defaults to 'text'."""
    argv = list(argv or ())
    fmt = 'text'
    for i, arg in enumerate(argv):
        if arg == '--output-format' and i + 1 < len(argv):
            fmt = argv[i + 1]
        elif isinstance(arg, str) and arg.startswith('--output-format='):
            fmt = arg.split('=', 1)[1]
    return fmt, TOKEN_STREAM_FLAG in argv


def progress_window_ms_for_argv(argv, window_ms=PRODUCTION_NO_OUTPUT_PROGRESS_MS):
    """The window to arm for the spawn this argv WILL run -- derived, never declared."""
    fmt, partial = output_shape_of_argv(argv)
    return progress_window_ms_for(fmt, window_ms, partial_messages=partial)


# H4528: how a KILLED call is classified when nothing account-level was said on the way out.
# Before, both bounds came back as the one word 'timeout' and only a side field
# (`killed_reason`) told them apart; every counter, requeue rule and report keyed on the word.
# A no-output-progress kill is a different event -- the spawn went silent, it did not merely
# run long -- so it gets its own classification, shared by the paid lane and the probe so
# both halves of the gate name it identically (the PR #1837 refusal-split pattern).
KILL_CLASS_HARD_TIMEOUT = 'timeout'
KILL_CLASS_NO_PROGRESS = 'no_progress_kill'
KILL_CLASSES = (KILL_CLASS_HARD_TIMEOUT, KILL_CLASS_NO_PROGRESS)


def kill_classification(killed_reason):
    """'no_progress_kill' for a stalled-output kill, else the historical 'timeout'."""
    if killed_reason == KILLED_REASON_NO_OUTPUT_PROGRESS:
        return KILL_CLASS_NO_PROGRESS
    return KILL_CLASS_HARD_TIMEOUT


def assert_progress_window_below_ceiling(window_ms, source,
                                         ceiling_ms=PRODUCTION_HARD_TIMEOUT_MS):
    """Fail closed on a progress window at or above the total-wall ceiling.

    A window that is not STRICTLY below the hard timeout can never fire -- the backstop
    would always kill first -- so configuring one is a silent no-op, which is precisely the
    failure mode #983 catalogued for the ceiling itself. ``None`` (observe only) passes.
    """
    if window_ms is None:
        return
    try:
        requested = int(window_ms)
    except (TypeError, ValueError):
        raise ValueError('%s: no-output-progress window must be an integer number of '
                         'milliseconds (got %r)' % (source, window_ms))
    if requested <= 0:
        raise ValueError('%s requests a %d ms no-output-progress window; a non-positive '
                         'window would kill every spawn on its first poll' % (source, requested))
    if requested >= ceiling_ms:
        raise ValueError(
            '%s requests a %d ms no-output-progress window, at or above the %d ms total-wall '
            'ceiling. It could never fire -- the hard timeout would always kill first -- so '
            'this is REFUSED rather than accepted as a silent no-op.'
            % (source, requested, ceiling_ms))


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
    # H2254: refuse a sealed budget above the production hard maximum BEFORE any model
    # subprocess starts. Checked ahead of the schema branch on purpose -- a v1 manifest is
    # still executable through `--allow-historical-v1`, and the ceiling is a money guard, not
    # a schema nicety, so it must bind on every executable shape.
    assert_timeout_within_ceiling((manifest.get('budgets') or {}).get('timeout_ceil_ms'),
                                  'manifest budgets.timeout_ceil_ms')
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
        # H4915: one held claim is ONE readiness-probe attempt, however many calls it covers
        # (live_probe's warm-up + measured pair, a latency sweep's whole series). The first
        # `_probe_call` under the claim spends the ration and flips this; the rest ride on it.
        self.ration_admitted = False

    def is_live_canonical_for(self, fingerprint):
        """Return True only for the live claim at the one process-wide lock path.

        A caller-supplied claim rooted in another directory can carry the same
        filename while protecting a different kernel object. Paid-call
        primitives therefore compare the normalized full path, not merely the
        basename or fingerprint text.
        """
        expected = ActiveCallClaim(fingerprint).path
        normalize = lambda path: os.path.normcase(os.path.realpath(os.path.abspath(path)))
        return self._fh is not None and normalize(self.path) == normalize(expected)

    def __enter__(self):
        os.makedirs(self.root, exist_ok=True)
        fh = open(self.path, 'a+b')
        try:
            _os_lock_nb(fh)
        except OSError:
            fh.close()
            raise RuntimeError('profile already has an active model call')
        self._fh = fh
        self.ration_admitted = False
        return self

    def __exit__(self, _typ, _value, _tb):
        fh, self._fh = self._fh, None
        if fh is not None:
            _os_unlock(fh)
            fh.close()


# H4915 (15-09-2026): the readiness-probe ration, enforced in code. The standing ration is at
# most 2 probe attempts per UTC day per profile, at least 6 h apart. On 15-09 c1 was probed three
# times in one UTC day (01:35Z, 14:23Z, 14:26:55Z). Two things let the third one through:
# `ActiveCallClaim` only serialises calls that OVERLAP, and the probe log is split across evidence
# roots (explicit `--evidence-dir` -> `$PWG_EVIDENCE_DIR` -> checkout), so a session reading one
# root could not see the other root's row. The ledger below lives in ONE machine-wide place, beside
# the active-call lock dir, and it is keyed by the same config-directory fingerprint. There is no
# env override on purpose: a per-session root would split the count again.
PROBE_RATION_MAX_PER_UTC_DAY = 2
PROBE_RATION_MIN_GAP_S = 6 * 3600


def probe_ration_root():
    return os.path.join(tempfile.gettempdir(), 'pwg-probe-ration')


def _utc(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc)


def _utc_iso(ts):
    return _utc(ts).strftime('%Y-%m-%dT%H:%M:%SZ')


def _next_utc_midnight(ts):
    day = _utc(ts).date() + datetime.timedelta(days=1)
    return datetime.datetime(day.year, day.month, day.day,
                             tzinfo=datetime.timezone.utc).timestamp()


class ProbeRationRefused(RuntimeError):
    """A readiness probe the ration forbids. Raised BEFORE any spawn or call reservation.

    Deliberately NOT a SystemExit: a ration refusal is not a health verdict. The probe CLIs read a
    SystemExit from `live_probe` as a NO-GO reading, and `probe_fleet --drop-unhealthy` would
    silently drop the profile as unhealthy."""

    def __init__(self, message, next_legal_ts=None):
        RuntimeError.__init__(self, message)
        self.next_legal_ts = next_legal_ts          # None: no legal time until a human repairs
        self.next_legal_utc = None if next_legal_ts is None else _utc_iso(next_legal_ts)


class ProbeRation:
    """Per-profile ledger of readiness-probe attempts, one JSONL file per fingerprint.

    Callers check and record while they hold the profile's `ActiveCallClaim`. That kernel lock
    already serialises every probe on one profile across processes, so check-then-append cannot
    race. A row that cannot be parsed fails CLOSED: the refusal names the file and line, because
    guessing an attempt's time guards paid spend worse than a stopped profile does."""

    def __init__(self, root=None):
        self.root = root or probe_ration_root()

    def path(self, fingerprint):
        return os.path.join(self.root, fingerprint + '.jsonl')

    def attempts(self, fingerprint):
        path = self.path(fingerprint)
        try:
            with open(path, encoding='utf-8') as fh:
                lines = fh.read().splitlines()
        except FileNotFoundError:
            return []
        stamps = []
        for number, line in enumerate(lines, 1):
            if not line.strip():
                continue
            try:
                stamps.append(float(json.loads(line)['ts']))
            except (ValueError, TypeError, KeyError) as exc:
                raise ProbeRationRefused(
                    'probe ration ledger %s line %d is unreadable (%s); refusing the probe '
                    'rather than guessing when the last attempt was. Repair the line by hand '
                    '(H4915).' % (path, number, exc))
        return sorted(stamps)

    def next_legal(self, fingerprint, now):
        """Earliest time >= now at which one more attempt is legal."""
        stamps = self.attempts(fingerprint)
        legal = now
        if stamps:
            legal = max(legal, stamps[-1] + PROBE_RATION_MIN_GAP_S)
        while sum(1 for ts in stamps if _utc(ts).date() == _utc(legal).date()) \
                >= PROBE_RATION_MAX_PER_UTC_DAY:
            legal = _next_utc_midnight(legal)
        return legal

    def check(self, fingerprint, now, label=None):
        stamps = self.attempts(fingerprint)
        legal = self.next_legal(fingerprint, now)
        if legal <= now:
            return
        today = _utc(now).date()
        same_day = [ts for ts in stamps if _utc(ts).date() == today]
        reasons = []
        if len(same_day) >= PROBE_RATION_MAX_PER_UTC_DAY:
            reasons.append('%d attempt(s) already on UTC day %s (max %d)'
                           % (len(same_day), today.isoformat(), PROBE_RATION_MAX_PER_UTC_DAY))
        if stamps and now - stamps[-1] < PROBE_RATION_MIN_GAP_S:
            reasons.append('last attempt at %s is under %d h old'
                           % (_utc_iso(stamps[-1]), PROBE_RATION_MIN_GAP_S // 3600))
        raise ProbeRationRefused(
            'probe ration: profile %s -- %s. Next legal attempt: %s. No call was made and no '
            'reservation was spent. Ledger: %s (H4915)'
            % (label or fingerprint[:12], '; '.join(reasons) or 'ration exhausted',
               _utc_iso(legal), self.path(fingerprint)), legal)

    def record(self, fingerprint, now, purpose=None, account=None):
        """Append one attempt. Raises on a failed write: an unrecorded attempt must not spawn."""
        os.makedirs(self.root, exist_ok=True)
        row = {'ts': now, 'utc': _utc_iso(now), 'purpose': purpose, 'account': account,
               'pid': os.getpid()}
        with open(self.path(fingerprint), 'a', encoding='utf-8') as fh:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n')
            fh.flush()
            os.fsync(fh.fileno())
