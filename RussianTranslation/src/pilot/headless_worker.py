#!/usr/bin/env python
"""Execute one PWG translation manifest through Claude Code headless mode."""
import argparse
import collections
import copy
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
_SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
from proc_tree import run_tree_kill, terminate_tree, windows_hidden_flags  # noqa: E402  (shared D-J tree-kill runner)
import card_fields  # noqa: E402  (C-01: the one restore/promote field set, shared with the JS lane)
import german_anchor  # noqa: E402  (H858 Part B: source-anchored repair of a dropped `german` span)
from window_common import portrait_key_iast  # noqa: E402  (B02: one iast derivation for both stitch twins)
from execution_contract import (ActiveCallClaim, PRODUCTION_HARD_TIMEOUT_MS, SCHEMA_V1,
                                SCHEMA_V2, assert_timeout_within_ceiling,
                                config_dir_fingerprint, validate_manifest,
                                validate_profile)  # noqa: E402
from call_reservation import (CallLimitReached, CallReservationLedger,
                              telemetry_from_cli_wrapper, unevaluable_telemetry)  # noqa: E402

AUTH_RE = re.compile(r'401|authentication|not logged in|invalid.*credential', re.I)
RATE_RE = re.compile(r'429|rate.?limit|usage limit|too many requests', re.I)
CONN_RE = re.compile(r'connection closed|econnreset|socket hang up|network error', re.I)
EXIT_AUTH = 20
EXIT_RATE_LIMIT = 21
EXIT_TIMEOUT = 22
EXIT_MALFORMED = 23
EXIT_CONTENT = 24

# R4 (C-15): the hard per-call subprocess ceiling. The bare operator default was 7200 s -- 40x
# this -- because `budgets.timeout_ceil_ms` was never read.
#
# 180000 -> 300000, 02-08-2026 (issue #983). The "NOTHING runs past 3 min (MG)" rule was
# RELAXED by an explicit human ruling, on measurement rather than preference: the first paid
# run since 25-07 produced ZERO cards because 12 of 16 calls were killed at exactly this
# ceiling (180 04x-180 23x ms, `reservation_timeline.py`). It is not tunable from below --
# heal groups were already at the arithmetic floor (six of nakzatra's eight held a SINGLE
# fragment) and single-fragment calls still hit it, because the kill gate
# clamp(KILL_BASE + 45*bytes, FLOOR, CEIL) saturates at CEIL for any fragment >~3.5 KB.
# Successful calls measured 120.4 / 132.0 / 134.5 / 164.3 s, i.e. 67% -> 91% of the old
# budget, so the margin was already gone and shrinking. 300 s gives ~1.8x headroom over the
# worst observed success while staying BELOW the 390 s (6.5 min) pril10_w1 agent that
# prompted the original ruling -- a middle path, deliberately not a revert to the 480000
# (8 min) this replaced. Must stay in step with `gen_opt_harness2.KILL_CEIL_MS`: the JS
# harness kills from the inside, so raising only this constant is inert.
#
# H2254 (03-08-2026 owner ruling): the literal moved to `execution_contract` and both this
# module and `gen_opt_harness2` now IMPORT it. The equality the #983 selftest pins is
# therefore true by construction; that test is kept as the guard against re-introducing a
# copied literal. Exceeding the ceiling is now a REFUSAL, not a silent clamp (see
# `execution_contract.assert_timeout_within_ceiling`).
HARD_TIMEOUT_MS = PRODUCTION_HARD_TIMEOUT_MS

# H2254: the operator default. It was 7200 (two hours) -- forty times the ceiling -- and
# survived only because every route clamped silently. With the clamp replaced by a refusal a
# two-hour default would refuse every ordinary invocation, so the default IS the ceiling:
# asking for nothing gets the maximum, and asking for more than the maximum is an error
# instead of a rounding. Any lower `--timeout` still binds exactly as before.
DEFAULT_TIMEOUT_S = HARD_TIMEOUT_MS // 1000

# H2254: the SUPERVISOR's wrapper timeout must sit strictly ABOVE the per-call ceiling.
#
# `max_account_orchestrator` spawns this worker under `run_tree_kill(..., timeout=timeout)`
# using the SAME number it passes down as `--timeout`. At the old 7200 s operator default
# that was harmless -- the outer bound was 24x the inner one -- but making the default equal
# the ceiling would have made them identical, and an outer bound equal to the inner one kills
# the worker at the exact moment its last call reaches its own ceiling: the tree dies during
# teardown, `--status-out` is never written, and a call that was legitimately killed at the
# ceiling becomes a worker that vanished without a status file (the H1 "crash without a
# status file" class the hardening backlog closed, re-opened from the outside).
#
# The headroom covers worker startup, manifest+preflight validation, prompt assembly and the
# atomic status/output writes -- all of it work that happens OUTSIDE the model call and is
# therefore not bounded by the per-call ceiling at all. 120 s is deliberately generous
# against measured startup (single-digit seconds): this bound exists to catch a wedged
# supervisor, not to be tight.
WRAPPER_TIMEOUT_HEADROOM_S = 120


def wrapper_timeout_s(per_call_timeout_s):
    """Outer tree-kill bound for a spawned worker, given its per-call ceiling."""
    return int(per_call_timeout_s) + WRAPPER_TIMEOUT_HEADROOM_S

# H2158 (#983, 02-08-2026): spawn the CLI from a BARE directory, not the repo.
#
# v1.127.0 measured why every call re-creates its cache: the prompt prefix is a stable ~29 k
# core plus a VOLATILE ~49 k segment that is re-written every call, and project-context
# injection (CLAUDE.md + git state) is what makes it volatile -- worth ~11-17 k tokens per
# call. Measured back-to-back on identical `--max-turns 1` calls: repo cwd $0.3036 / 26-29 s
# vs bare cwd $0.2040 / 19-20 s, i.e. **-33 % cost and -30 % wall clock**, and the only
# cross-call cache reuse in the whole experiment appeared in the bare arm (read +5 553 /
# create -5 553, exactly complementary).
#
# The wall-clock half is why this sits next to HARD_TIMEOUT_MS rather than in a cost note: a
# 30 % shorter call is 30 % more headroom against the ceiling that killed 12 of 16 calls.
# `proc_tree.run_tree_kill` already accepted `cwd` and passed it to Popen -- nothing ever
# supplied one, so the child silently inherited the repo.
#
# The directory is STABLE (not per-call): a fresh temp dir per call would give the model a
# different cwd string each time and re-break the very prefix this is stabilising.
BARE_CLI_CWD_NAME = 'pwg_ru_cli_cwd'

# H2249 (03-08-2026): fail safe on the ANCESTRY, not just on the immediate directory.
#
# H2158's walk rejected an ancestor carrying a bare `CLAUDE.md` or a `.git` -- but not one
# carrying `.claude\CLAUDE.md`, `.claude\CLAUDE.local.md` or `.claude\rules`. The directory it
# handed out lives under `%TEMP%`, i.e. under the Windows user profile, which is exactly where
# the operator's global memory sits: **32 779 B measured reaching EVERY paid call since
# H2158**, invisible because the spawn directory itself is empty. H2189's `--safe-mode` masks
# that (it disables memory discovery outright) but is opt-in, and masking is not fixing --
# every lane without the flag kept paying, and the helper kept claiming a bareness it did not
# have.
#
# The marker set and the walk are deliberately NOT re-implemented here:
# `h2189_min_profile.cwd_ancestry_scan` is the single source (the selftest already asserts
# through it), so a marker added there reaches the spawn path automatically instead of drifting
# into two half-updated lists.
#
# WHERE to look is derived, never hardcoded. `D:\ClaudeTools\pwg_ru_clean_cwd` was the H2189
# arm and a drive root outside the profile is the cheapest clean ancestry on this box -- but a
# drive letter baked into the source is a machine-specific path that silently degrades to None
# on any other machine. So the candidates are: an operator-named override, then the historical
# `%TEMP%` location (unchanged behaviour wherever temp is already clean, e.g. POSIX `/tmp`),
# then each FIXED filesystem root the OS reports, system drive last. Every candidate is
# verified before it is returned; none verifying returns None.
BARE_CLI_CWD_ENV = 'PWG_RU_CLI_CWD'
_BARE_CLI_CWD_CACHE = []


def _fixed_filesystem_roots():
    """Local fixed-disk roots, system drive last. Never guesses; degrades to no roots.

    Windows-only by design. On POSIX the temp dir already sits outside the user profile, so
    there is nothing to escape by climbing to a root -- and creating a directory at `/` is not
    something this helper should ever attempt. A bare `os.path.isdir('A:\\')` sweep is avoided
    because it can stall for seconds on a removable or disconnected network drive; ask the OS
    which letters are FIXED instead.
    """
    if os.name != 'nt':
        return []
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        mask = kernel32.GetLogicalDrives()
        drive_fixed = 3
        roots = [chr(ord('A') + i) + ':' + os.sep
                 for i in range(26)
                 if mask & (1 << i)
                 and kernel32.GetDriveTypeW(chr(ord('A') + i) + ':' + os.sep) == drive_fixed]
    except (AttributeError, OSError, ValueError):
        return []
    # The system drive is where corporate ACLs and antivirus policy are most likely to refuse a
    # root-level directory; try it only after the others. `makedirs` failure is not fatal
    # either way -- it just moves to the next candidate.
    system = (os.environ.get('SystemDrive')
              or os.path.splitdrive(os.environ.get('SystemRoot') or '')[0] or '')
    if system:
        key = os.path.normcase(system.rstrip(os.sep))
        roots.sort(key=lambda r: os.path.normcase(os.path.splitdrive(r)[0]) == key)
    return roots


def bare_cli_cwd_candidates():
    """Ordered spawn-directory candidates, deduplicated. Derived — no path is hardcoded."""
    cands = []
    override = os.environ.get(BARE_CLI_CWD_ENV)
    if override:
        cands.append(os.path.abspath(override))
    try:
        cands.append(os.path.join(tempfile.gettempdir(), BARE_CLI_CWD_NAME))
    except (AttributeError, OSError):
        pass
    cands.extend(os.path.join(root, BARE_CLI_CWD_NAME) for root in _fixed_filesystem_roots())
    seen = set()
    ordered = []
    for cand in cands:
        key = os.path.normcase(os.path.abspath(cand))
        if key not in seen:
            seen.add(key)
            ordered.append(cand)
    return ordered


def bare_cli_cwd_ancestry_clean(path):
    """Whether an ancestor walk from `path` finds nothing the CLI could inject as memory.

    Fails CLOSED: anything that stops the scan from running -- a moved `h2189_min_profile`,
    an unreadable directory -- counts as NOT clean, because "could not prove it" and "proved
    it clean" must never collapse into the same answer on the path that decides what the model
    is handed. The import is loud on failure for the same reason `resolve_safe_mode` is: a
    silent False here would cost H2158's measured -33 % on every call with no signal.
    """
    try:
        from h2189_min_profile import cwd_ancestry_scan
    except ImportError as exc:
        sys.stderr.write('H2249: cannot import h2189_min_profile.cwd_ancestry_scan (%s) -- '
                         'treating every spawn dir as unverified and inheriting the caller '
                         'cwd, i.e. paying the full project prefix.\n' % exc)
        sys.stderr.flush()
        return False
    try:
        return not cwd_ancestry_scan(path)
    except OSError:
        return False


def bare_cli_cwd():
    """A stable spawn directory whose ANCESTRY carries no project or operator memory.

    Fails SAFE: returns None -- the historical inherited-cwd behaviour -- rather than hand back
    a directory that still injects memory. The directory is STABLE (not per-call): a fresh temp
    dir per call would give the model a different cwd string each time and re-break the very
    prefix this is stabilising, so the answer is resolved once and cached.
    """
    if _BARE_CLI_CWD_CACHE:
        return _BARE_CLI_CWD_CACHE[0]
    resolved = None
    tried = []
    for cand in bare_cli_cwd_candidates():
        tried.append(cand)
        try:
            os.makedirs(cand, exist_ok=True)
        except OSError:
            continue        # unwritable root, ACL refusal, drive pulled -- try the next one
        if bare_cli_cwd_ancestry_clean(cand):
            resolved = cand
            break
    if resolved is None:
        sys.stderr.write('H2249: no spawn directory with a clean ancestry (tried %s) -- '
                         'inheriting the caller cwd and paying the full project prefix. Point '
                         '%s at a directory whose parents carry no CLAUDE.md/.claude/.git.\n'
                         % (', '.join(tried) or '<none>', BARE_CLI_CWD_ENV))
        sys.stderr.flush()
    _BARE_CLI_CWD_CACHE.append(resolved)
    return resolved


# H2189 (02-08-2026): the residual prefix tax `bare_cli_cwd()` cannot reach.
#
# Bare cwd removes PROJECT context. It does not remove the operator PROFILE bound as the
# CLI's config dir -- its skills, commands, agents and, above all, its SessionStart /
# UserPromptSubmit hooks. That is what `--safe-mode` reaches and a spawn directory never can.
#
# H2189 also found a SECOND leak, the memory files an ancestor walk from the spawn directory
# still finds (32 779 B on this box, every paid call). That one is NOT a profile problem and
# is fixed above by H2249: `bare_cli_cwd()` now verifies the whole ancestry through
# `h2189_min_profile.cwd_ancestry_scan`. `--safe-mode` masked it; it is no longer what stands
# between the operator's global CLAUDE.md and a paid call.
#
# Measured A/B (H2189, sequential, bare cwd, claude-sonnet-5, cold call):
#   trivial   paid 39 532 create / error_max_turns   safe-mode 4 712 create / completes
#   real card paid 60 140 create, 19 718 out, 254 s, $0.6921
#             safe 18 615 create, 10 040 out, 115 s, $0.2712   (-69 % create, -61 % cost,
#             -55 % wall) with IDENTICAL card content: 7 records / 13 senses on both, the
#             {Tn} masked-span token SET identical, 13/13 senses carrying Russian, zero
#             SAN-LOSS/UNMAPPED. The output halving is agent-loop overhead, not lost card.
#
# `--safe-mode` beat a dedicated minimal config dir (39 532 -> 36 092, only -8.7 %) and
# needs no second on-disk credential copy and no second `ActiveCallClaim` fingerprint.
# `--bare` was deliberately NOT adopted: it forces ANTHROPIC_API_KEY auth, i.e. moves this
# lane off the subscription identity, which is a human ruling and not a cache tweak.
#
# Shipped OPT-IN, default OFF -- the quality case then rested on n=1 per arm and one
# unattributed divergence (the free-text `tag` vocabulary differed between the two samples),
# and flipping a production default on that is the "flip without measured GO" H2189's own
# fail criteria forbid. H2251 (06-08-2026) bought the evidence and flipped it: see
# DEFAULT_CLI_SAFE_MODE below. Two of the numbers quoted just above are n=1 and did NOT
# replicate -- at n=6 per arm the output saving is -4.4 % (not -49 %) and wall is -12.3 %
# (not -55 %); create (-40 %) and the ceiling headroom did.
SAFE_MODE_FLAG = '--safe-mode'
_safe_mode_support = {}


def cli_supports_safe_mode(claude_bin='claude'):
    """Whether the installed CLI accepts --safe-mode. Cached; fails SAFE (unknown => False).

    A requested-but-unsupported flag would make every spawn die in argument parsing, i.e.
    turn a cost optimisation into a total outage. Probing `--help` once per binary is the
    cheap way to make the feature degrade to the historical behaviour instead.
    """
    if claude_bin in _safe_mode_support:
        return _safe_mode_support[claude_bin]
    supported = False
    try:
        proc = subprocess.run(claude_argv_prefix(claude_bin) + ['--help'],
                              capture_output=True, text=True, encoding='utf-8', timeout=60)
        supported = SAFE_MODE_FLAG in (proc.stdout or '')
    except (OSError, subprocess.SubprocessError, ValueError):
        supported = False
    _safe_mode_support[claude_bin] = supported
    return supported


# H2251 (06-08-2026): the default is now ON. H2189 shipped it OFF pending two things, and
# both were bought: a canary GO receipt produced ON the safe-mode arm (not inherited from a
# baseline), and a both-ways comparison large enough to rule the §4.2 `tag` divergence.
#
# What the measurement actually said, stated as measured rather than as hoped:
#   * the free-text `tag` vocabulary is NOT reproducible even with the flag held constant
#     (mean within-arm Jaccard distance 0.535 over 3 cards x 2 arms x 2 repeats; two
#     arm-cards were COMPLETELY disjoint against themselves). H2189's own stated closing
#     condition -- "if tag vocabulary varies run-to-run on the SAME arm, that settles it as
#     sampling noise" -- is therefore met. An arm-linked style component survives on top of
#     that instability and is recorded as a residual, not waved away;
#   * card CONTENT shows no arm effect and no loss: 12/12 draws had every sense carrying
#     Russian and zero SAN-LOSS/UNMAPPED, sense counts moved as much within an arm as
#     between arms, and on `nakzatra` the paid arm differed from ITSELF more than the two
#     arms differed from each other on the {Tn} set.
#
# The savings are smaller than H2189's n=1 headline: -40 % create / -22 % cost / -12 % wall
# at n=6 per arm, not -69/-61/-55. The decisive argument is the ceiling, not the price --
# on `sakft` the baseline ran 286 694 ms and 266 349 ms against the 300 000 ms production
# kill, i.e. twice within ~11 % of dying, where the safe arm ran 232 891 and 189 106.
#
# `False` remains a real, honoured value: an operator can still pin the historical spawn
# per manifest. Only ABSENT now means ON.
DEFAULT_CLI_SAFE_MODE = True


def resolve_safe_mode(manifest, claude_bin='claude'):
    """Return True when this run should spawn with --safe-mode.

    `execution.cli_safe_mode` in the manifest decides -- auditable, and it travels with the
    run receipt. Tri-state on purpose: absent takes DEFAULT_CLI_SAFE_MODE (ON since H2251),
    while an explicit `false` still pins the historical spawn, so the flip cannot silently
    override a manifest that deliberately opted out.
    """
    requested = (manifest.get('execution') or {}).get('cli_safe_mode')
    if requested is None:
        requested = DEFAULT_CLI_SAFE_MODE
    if not bool(requested):
        return False
    if not cli_supports_safe_mode(claude_bin):
        # Loud, not silent: a run that believes it is stripping the profile but is not
        # would report H2189's savings while paying the full tax.
        sys.stderr.write(
            'H2189: manifest requested execution.cli_safe_mode but the installed CLI (%s) '
            'does not advertise %s -- spawning WITHOUT it and paying the full profile '
            'prefix. Update the CLI or clear the manifest flag.\n' % (claude_bin, SAFE_MODE_FLAG))
        sys.stderr.flush()
        return False
    return True


def _is_npm_claude_placeholder(exe):
    """True only for npm's literal placeholder script (never for real PE or fixtures)."""
    try:
        with open(exe, 'rb') as fh:
            return b'native binary not installed' in fh.read(256)
    except OSError:
        return False


def ensure_windows_native_binary(base):
    """Self-heal npm's placeholder bin/claude.exe before spawn (Uprava FINDINGS §542).

    A reinstall that skips the native-binary download leaves npm's ~500-byte
    placeholder script, which dies at exec time with an opaque Windows error,
    indistinguishable in call envelopes from quota/auth failures. Fires only on
    the placeholder's own error-text signature -- never on real binaries or
    small hermetic-test fixtures; repairs via the package's own install.cjs and
    fails loud with the manual command when that cannot heal it.
    """
    if os.name != 'nt':
        return
    exe = os.path.join(base, 'bin', 'claude.exe')
    if not os.path.isfile(exe) or not _is_npm_claude_placeholder(exe):
        return
    node = shutil.which('node')
    if node:
        try:
            subprocess.run([node, 'install.cjs'], cwd=base,
                           capture_output=True, timeout=600)
        except (OSError, subprocess.SubprocessError):
            pass
    if os.path.isfile(exe) and not _is_npm_claude_placeholder(exe):
        return
    raise FileNotFoundError(
        'refusing to spawn against npm placeholder %s; install.cjs did not '
        'repair it -- run manually: node "%s"'
        % (exe, os.path.join(base, 'install.cjs')))


def claude_argv_prefix(claude_bin):
    """Return the argv prefix that invokes the Claude CLI directly (Windows-safe).

    On Windows the npm launcher is a ``.cmd``/``.ps1`` batch shim; Python routes it
    through cmd.exe, which reinterprets the ``<``/``>`` characters in a ``--json-schema``
    argument as redirection and caps the command line near 8191 chars — so a real card
    schema is corrupted and the call dies with "cannot find the file specified" (the
    H818 Windows live-acceptance D-A defect). Resolve such a shim to
    ``[node, <cli entry>.cjs]`` and invoke that directly, bypassing cmd.exe. A native
    executable, or any POSIX launcher, is returned unchanged.
    """
    resolved = claude_bin
    if not os.path.dirname(claude_bin):
        resolved = shutil.which(claude_bin)
        if not resolved:
            raise FileNotFoundError('Claude CLI %r is not resolvable on PATH' % claude_bin)
    if os.name != 'nt':
        return [resolved]
    if os.path.splitext(resolved)[1].lower() in ('.exe', '.com'):
        return [resolved]
    node = shutil.which('node')
    shim_dir = os.path.dirname(os.path.abspath(resolved)) or '.'
    base = os.path.join(shim_dir, 'node_modules', '@anthropic-ai', 'claude-code')
    ensure_windows_native_binary(base)
    entries = sorted(glob.glob(os.path.join(base, 'cli*.cjs')) +
                     glob.glob(os.path.join(base, 'cli*.js')))
    if node and entries:
        return [node, entries[0]]
    raise FileNotFoundError('refusing unresolved Windows Claude shim %r; Node CLI entry missing'
                            % resolved)


class HardFailure(Exception):
    def __init__(self, classification, code, detail=''):
        super().__init__(detail or classification)
        self.classification = classification
        self.code = code
        self.detail = detail


def sha256_path(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def validate_preflight_artifact(path, manifest=None, expected_sha256=None):
    """Fail closed on malformed, over-ceiling, drifted, or wrong-scope paid-call evidence."""
    if not path:
        raise ValueError('paid v2 execution requires --preflight')
    try:
        with open(path, 'rb') as f:
            preflight_bytes = f.read()
        if (expected_sha256
                and hashlib.sha256(preflight_bytes).hexdigest() != expected_sha256):
            raise ValueError('preflight hash changed before paid execution')
        data = json.loads(preflight_bytes.decode('utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError('preflight is unreadable: %s' % exc)
    if not isinstance(data, dict):
        raise ValueError('preflight top level must be an object')
    schema = data.get('schema')
    if schema == 'pwg.performance_preflight.v1':
        reports = [data]
    elif schema == 'pwg.performance_preflight.matrix.v1':
        reports = data.get('reports')
    else:
        raise ValueError('unsupported preflight schema: %r' % schema)
    if not isinstance(reports, list) or not reports:
        raise ValueError('preflight must contain nonempty reports')
    scoped = []
    for index, report in enumerate(reports):
        if not isinstance(report, dict):
            raise ValueError('preflight report %d is not an object' % index)
        gate = report.get('cost_gate')
        if not isinstance(gate, dict) or not isinstance(gate.get('over_ceiling'), bool):
            raise ValueError('preflight report %d has no boolean over_ceiling' % index)
        if gate['over_ceiling']:
            raise ValueError('preflight report %d is over ceiling' % index)
        if manifest is not None:
            if report.get('synthetic_probe_only'):
                raise ValueError(
                    'synthetic probe preflight cannot authorize manifest execution')
            keys = report.get('selected_keys')
            if (not isinstance(keys, list)
                    or not all(isinstance(key, str) and key for key in keys)
                    or len(keys) != len(set(keys))):
                raise ValueError(
                    'preflight report %d has missing/malformed selected_keys' % index)
            scoped.extend(keys)
    if manifest is not None:
        expected = list((manifest.get('meta') or {}).get('selected_keys') or [])
        if (len(scoped) != len(set(scoped))
                or sorted(scoped) != sorted(expected)):
            raise ValueError('preflight selected-key scope does not match manifest')
    return data


def atomic_json(path, payload):
    # H3 (H1940 Phase 2): os.replace is atomic but NOT durable -- a power loss between the
    # write and the disk flush leaves a valid-looking, truncated or empty status/output file,
    # and the orchestrator then re-audits the whole window. flush+fsync before the replace
    # gives the same durability window_common.atomic_write_text has always had.
    #
    # Deliberately INLINE rather than routed through window_common.atomic_write_json, which
    # is what the fixlog sketch proposed. Measured 31-07-2026 (src/pilot/h3_byte_probe.py):
    # routing through it changes these bytes -- CRLF instead of LF on Windows (atomic_write_text
    # passes no newline= to os.fdopen) and no trailing newline, 246 bytes vs 232 on the probe
    # payload, diverging at offset 1. Those bytes are hash-bound (window_status/output sidecars),
    # and the same shared writer also emits the execution manifest whose sha256_path digest is
    # manifest_sha256, plus the preflight evidence -- so pinning newline= there is a hash
    # migration across several gate-pinned artifacts, not a durability fix. Recorded as its own
    # item in Uprava FINDINGS §262; H3 stays surgical and byte-identical.
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + '.tmp.%d' % os.getpid()
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def suggestion_block(rows):
    if not rows:
        return ''
    lines = []
    for row in rows:
        scores = 'de=%s sa=%s tag=%s combined=%s' % (
            row.get('score_de_fragment', 'n/a'), row.get('score_sa_headword', 'n/a'),
            row.get('score_semantic_tag', 'n/a'),
            row.get('score_combined', row.get('score', 'n/a')))
        lines.append('[%s %s %s] %s' % (row.get('source_kind', 'suggestion'), scores,
                                        row.get('provenance_note', ''), row.get('text', '')))
    return ('\n--- advisory translation-memory suggestions (SUGGEST ONLY; do not copy '
            'unsupported senses) ---\n' + '\n'.join(lines))


def card_block(manifest, key):
    inp = manifest['inputs'][key]
    grammar = manifest['prompt'].get('grammars', {}).get(key, '')
    return (grammar + '\n\n=== CARD ' + key + ' ===\n'
            '--- masked German (translatable only; {Tn}=masked span) ---\n' +
            inp['skeleton'] + suggestion_block(manifest.get('suggestions', {}).get(key, [])) +
            '\n--- portrait (evidence) ---\n' + inp['portrait'])


def build_prompt(manifest, keys):
    """Assemble the production prompt STABLE-LEFT: framework first, volatile last.

    Order is `preamble + translation + grammar + [nws] + card blocks` (H2191, playbook
    PROMPT_CACHING_PWG_RU §3 rank 4 / §4 Step E).  ``preamble`` and ``translation`` are the
    only two segments that are byte-identical across every card of every window, so they
    sit leftmost: any provider-side prefix match (CLI partial reuse, Messages API
    ``cache_control`` breakpoint) sees the longest possible stable head before the
    per-window ``grammar`` block and the per-card blocks that change on every call.
    ``grammar`` moved right of ``translation`` because it is window-scoped (the root's
    conjugation / the headword's declension), not run-scoped.

    This is a REORDER, not compression: every segment that was sent before is still sent,
    byte-for-byte.  Trimming CONV_TR/NWS for cache was measured and rejected
    (``AB_TEST_LEAN_TR.md``) -- do not re-open it here.  ``nws`` stays after the whole
    framework so TR remains contiguous, and per-card grammar stays inside ``card_block``.
    """
    stable, volatile = prompt_blocks(manifest, keys)
    return stable + volatile


def prompt_blocks(manifest, keys):
    """Return the one-hour cache prefix and volatile suffix byte-exactly."""
    prompt = manifest['prompt']
    nws = prompt.get('nws_rule', '') if any(manifest['inputs'][k].get('nws') for k in keys) else ''
    stable = prompt['preamble'] + prompt['translation']
    volatile = (prompt.get('grammar', '') + ('\n\n' + nws + '\n' if nws else '')
                + ''.join(card_block(manifest, key) for key in keys))
    if stable + volatile != build_prompt_joined(manifest, keys):
        raise AssertionError('prompt block split changed build_prompt bytes')
    return stable, volatile


def build_prompt_joined(manifest, keys):
    """Historical prompt expression kept as an independent byte-identity oracle."""
    prompt = manifest['prompt']
    nws = prompt.get('nws_rule', '') if any(manifest['inputs'][k].get('nws') for k in keys) else ''
    return (prompt['preamble'] + prompt['translation'] + prompt.get('grammar', '') +
            ('\n\n' + nws + '\n' if nws else '') +
            ''.join(card_block(manifest, key) for key in keys))


def fragment_prompt_blocks(manifest, key, group, indices):
    blocks = []
    for index in indices:
        frag_key = '%s_f%d' % (key, index)
        blocks.append('\n\n=== CARD %s (fragment %d/%d) ===\n'
                      '--- masked German (translatable only; {Tn}=masked span) ---\n%s'
                      % (frag_key, index + 1, len(group), group[index]['skeleton']))
    prompt = manifest['prompt']
    stable = prompt['preamble'] + prompt['translation']
    card_grammar = (prompt.get('grammars') or {}).get(key, '')
    portrait = (manifest.get('inputs', {}).get(key) or {}).get('portrait') or ''
    volatile = (prompt.get('grammar', '') + card_grammar + ''.join(blocks)
                + '\n--- portrait (evidence) ---\n' + portrait)
    return stable, volatile


def build_fragment_prompt(manifest, key, group, indices):
    stable, volatile = fragment_prompt_blocks(manifest, key, group, indices)
    return stable + volatile


def parse_cli_wrapper(stdout):
    """Parse the Claude CLI JSON envelope without yet trusting its structured result.

    Usage/cost belongs to the paid invocation, not to the validity of ``cards[]``.  Keeping
    envelope parsing separate lets :meth:`HeadlessEngine.call` account for a malformed result
    before it retries.  An unreadable envelope is returned as a loud ``ValueError`` so the caller
    can mark the spawned call cost-unevaluable instead of silently pricing it at zero.
    """
    try:
        wrapper = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise ValueError('Claude output is not JSON: %s' % exc)
    if not isinstance(wrapper, dict):
        raise ValueError('Claude output envelope is not an object')
    return wrapper


class StructuredRefusal(ValueError):
    """The CLI returned a healthy envelope with NO structured channel and prose in `result`.

    H3157 / FINDINGS §498, repair (b). This is a MODEL REFUSAL, not malformed output, and the
    distinction is the whole point: `malformed_output` sends the next session hunting a schema
    or parser bug, when the actual cause is that the model declined to emit the structured
    result at all (on 19-08-2026, on `--permission-mode plan` grounds). The two are separable
    mechanically — a malformed structured channel is PRESENT but unparseable, whereas a refusal
    leaves `structured_output` ABSENT and puts prose where the JSON should be.

    Subclasses ValueError so every existing `except ValueError` path keeps working unchanged;
    only callers that care about the distinction need to look.
    """

    def __init__(self, message, prose=''):
        super().__init__(message)
        self.prose = prose


def structured_from_wrapper(wrapper):
    """Extract and validate the schema result from an already-accounted CLI envelope."""
    value = wrapper.get('structured_output')
    # H3157: remember whether the structured CHANNEL existed at all. `structured_output` absent
    # + non-JSON prose in `result` is a refusal (§498); a present-but-unparseable value is the
    # ordinary malformed case. Conflating them cost a session of parser-hunting.
    structured_absent = value is None
    if structured_absent:
        value = wrapper.get('result')
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError as exc:
            if structured_absent:
                raise StructuredRefusal(
                    'Claude emitted no structured_output and answered in prose — this is a '
                    'refusal, not malformed output (%s)' % exc, prose=value)
            raise ValueError('Claude result is not structured JSON: %s' % exc)
    if not isinstance(value, dict) or not isinstance(value.get('cards'), list):
        if structured_absent and isinstance(value, str):
            raise StructuredRefusal(
                'Claude emitted no structured_output and answered in prose — this is a '
                'refusal, not malformed output', prose=value)
        raise ValueError('Claude result has no cards[] object')
    return value


#: Bounded tail kept from a failed paid envelope. A provider refusal is ~1 KB; 4 KB is
#: generous and still incapable of growing without limit. Mirrors the probe's
#: `PROBE_RAW_TAIL_BYTES` (H2326) rather than inventing a second number.
FAILED_ENVELOPE_TAIL_BYTES = 4096
#: Sits under the pilot's gitignored `output/`, exactly like the probe's raw-envelope dir, so
#: this commits nothing and leaks nothing.
FAILED_ENVELOPE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   'output', 'failed_envelopes')


def write_failed_envelope(label, classification, stdout, error):
    """Persist the tail of a PAID call's envelope that failed structured validation.

    H3157 repair (c), generalised from the probe's `_write_probe_raw` (H2326 — same lesson, one
    lane over): a call that bills in full and then fails validation must leave its own evidence
    behind. On 19-08-2026 a refusal cost 5 401 output + 94 752 subagent tokens and the harness
    stored nothing; the diagnosis existed only because the CLI kept an unrelated session JSONL,
    which no future session should have to rely on.

    Best-effort and append-only: a window must never fail because its diagnostic could not be
    written, and a later failure must never erase an earlier one.
    """
    text = stdout or ''
    raw = text.encode('utf-8')
    truncated = len(raw) > FAILED_ENVELOPE_TAIL_BYTES
    tail = (raw[-FAILED_ENVELOPE_TAIL_BYTES:].decode('utf-8', 'replace') if truncated else text)
    name = 'failed_envelope_%s.txt' % re.sub(r'[^A-Za-z0-9_.-]', '_', str(label or 'nolabel'))[:64]
    header = ('--- %s | label=%s | classification=%s | bytes=%d%s\n--- error: %s\n'
              % (time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), label or '-',
                 classification, len(raw),
                 ' | TRUNCATED to last %d B' % FAILED_ENVELOPE_TAIL_BYTES if truncated else '',
                 error))
    try:
        os.makedirs(FAILED_ENVELOPE_DIR, exist_ok=True)
        with open(os.path.join(FAILED_ENVELOPE_DIR, name), 'a',
                  encoding='utf-8', newline='\n') as fh:
            fh.write(header + tail + '\n')
    except OSError as exc:
        print('warning: failed-envelope capture failed: %s' % exc, file=sys.stderr)
        return None
    return os.path.join('output', 'failed_envelopes', name)


def extract_structured(stdout):
    """Compatibility helper returning ``(structured, wrapper)`` for existing callers/tests."""
    wrapper = parse_cli_wrapper(stdout)
    return structured_from_wrapper(wrapper), wrapper


def restore_text(text, placeholders, unmapped=None):
    """Unmask `{Tn}` against `placeholders`.

    C-42: an index outside the map still returns the token verbatim (changing that is a
    behaviour change this correction does not make), but it is now COUNTED into `unmapped`
    when a caller supplies a sink. The silent pass-through is how a raw `{T196}` reached the
    canonical store on a card that reported success: the article is masked WHOLE (235+
    placeholders) but restored per-subcard against a subcard-local map, so a high global
    index maps nothing. Counting is what lets `normalize_batch` gate on zero.
    """
    def repl(match):
        idx = int(match.group(1)) - 1
        if 0 <= idx < len(placeholders):
            return placeholders[idx]
        if unmapped is not None:
            unmapped.append(match.group(0))
        return match.group(0)
    return re.sub(r'\{T(\d+)\}', repl, text or '')


def restore_card(card, field, placeholders, unmapped=None):
    """Unmask every field the promote path reads -- the set is `card_fields`, not a local list.

    C-01: this used to restore three things (record.grammar, sense.german, sense.<field>)
    while `promote_final_cards.rows_for` read six, so card.iast / record.h / sense.tag /
    sense.differentia were promoted with their `{Tn}` intact -- 670 store rows, 223 of them
    a raw `{Tn}` in the HEADWORD. The lists are now one constant, pinned by
    `test_restore_covers_every_promoted_field`.

    Deliberate delta from the old loop: a field is restored only when it is a `str`. The old
    code tested key-presence and passed `text or ''`, silently rewriting a `None` grammar to
    `''`. Extending that to `h` would have laundered the 468 known `h is None` rows into
    empty strings -- destroying the very signal C-02 is diagnosed by. A non-str field is now
    left exactly as found.
    """
    return card_fields.restore_card_fields(
        card, field, lambda text: restore_text(text, placeholders, unmapped))


def stitch_records(senses, owners):
    """Rebuild `records[]` from healed senses, preserving each sense's `(h, grammar)` owner.

    C-02: the stitch used to emit a single `{'senses': senses}` record -- no `h`, no
    `grammar` -- which violates `schemas/pwg_ru_final_card.schema.json` (`record.required =
    {h, grammar, senses}`) and made the promote path write `h: null`. It also collapsed real
    homonyms: 79 sub-cards legitimately carry more than one distinct `h`, so one flat record
    cannot represent them.

    Consecutive senses sharing an owner stay in one record; a change of owner opens the next.
    Order is preserved exactly, so the whole-card `<ls>`/`{#` fidelity counts are unchanged.
    """
    records = []
    for sense, owner in zip(senses, owners):
        if not records or records[-1]['_owner'] != owner:
            rec_h, rec_grammar = owner
            records.append({'_owner': owner, 'h': rec_h, 'grammar': rec_grammar, 'senses': []})
        records[-1]['senses'].append(sense)
    for record in records:
        record.pop('_owner', None)
    return records


def stitched_card(key, iast, senses, owners):
    """B02 (H1339): construct a heal-stitched card schema-complete.

    `iast` and `notes` are CARD_REQUIRED (`validate_final_card_schema.CARD_REQUIRED`); a
    stitched card missing them was refused WHOLE by save_and_audit's schema gate (or per-key
    by the audit final-schema gate + promotion contract), losing every paid agent call in
    the healed window. `iast` falls back to the key when the portrait carries none. The JS
    twin is the `const stitched = { key1: k, iast: IASTS[k] || k, notes: '', ... }`
    construction in gen_opt_harness2.py, fed from the same window_common.portrait_key_iast."""
    return {'key1': key, 'iast': iast or key, 'notes': '',
            'records': stitch_records(senses, owners)}


def count_card(card, needle):
    """Count `needle` across the card's `german` senses.

    DELIBERATELY still `german`-only. The C-02 boundary asks to "make count_card/countOf see
    record-level fields", but that is wrong AT THIS SITE and its own fixture proves it: this
    count is compared against `inp['ls']`/`inp['sk']`, which are SOURCE-occurrence counts
    (`raw.count('<ls')`). One source token echoed into both `grammar` and `german` -- exactly
    what `headless_worker_selftest.success_runner` builds, `{T1}` in both -- then counts 2
    against a denominator of 1 and the card is rejected as a fidelity failure.

    Adding record-level text belongs with the token-MULTISET guards (C-17, Step 6), whose
    denominator really is the whole skeleton. Restoring `grammar` on the stitch lane (C-02)
    leaves this count unchanged, because stitched cards previously carried no `grammar` term
    at all -- so historical comparisons stay valid.
    """
    return sum((sense.get('german') or '').count(needle)
               for record in card.get('records') or []
               for sense in record.get('senses') or [])


def count_card_field(card, field, needle):
    """Count `needle` across the card's per-sense TARGET-language field (russian/english).

    H1152 parity (C1): count_card above proves only that the `german` SOURCE echo is faithful.
    A {#..#}/<ls> span can be dropped from the translation field alone (german 33/33, english
    32/33 -- the live H1070 r102 pattern) with zero effect on the german count, so a
    translation-only span drop reached the store on this lane. The JS batch accept() closed
    this with countOfField(TARGET_FIELD); the headless normalize_batch (now the production
    route) never did. Same source-occurrence denominator (inp['ls']/inp['sk']) as count_card.
    """
    return sum((sense.get(field) or '').count(needle)
               for record in card.get('records') or []
               for sense in record.get('senses') or [])


def normalize_batch(manifest, keys, structured):
    by_key = {}
    for card in structured['cards']:
        if isinstance(card, dict) and card.get('key1') not in by_key:
            by_key[card.get('key1')] = card
    nominal_map = manifest['meta'].get('nominal_keymap') or {}
    reverse = {}
    for key in keys:
        reverse.setdefault(nominal_map.get(key), []).append(key)
    rows = []
    for key in keys:
        card = by_key.get(key)
        echoed = nominal_map.get(key)
        if card is None and echoed and len(reverse.get(echoed, [])) == 1:
            card = by_key.get(echoed)
            if card:
                card['key1'] = key
        error = None
        if card is None:
            error = 'missing-or-mismatched-key'
        else:
            inp = manifest['inputs'][key]
            field = manifest['field']
            phs = manifest['placeholder_maps'].get(key, [])
            # H858 Part B: keep the PRE-restore card. The repair below works on `{Tn}`
            # tokens, which `restore_card` consumes -- after it the dropped span is
            # indistinguishable from prose and can no longer be anchored.
            masked = copy.deepcopy(card)
            unmapped = []
            card = restore_card(card, field, phs, unmapped)
            if count_card(card, '<ls') != inp['ls'] or count_card(card, '{#') != inp['sk']:
                # H858 Part B: the model dropped a masked span from its `german` echo. That is
                # the dominant retry-RESISTANT null class (6 of 7 residual nulls in no_pwg_w10,
                # H1283) -- a requeue reproduces it, because the drop is a property of the echo,
                # not of transport. Re-inject the dropped spans from the source skeleton, then
                # re-run THIS SAME count as the verifier: the repair is accepted only when it
                # makes the card exactly source-faithful, and refused cards fall through to the
                # identical reject as before. A card that passed the count above never enters
                # this branch, so clean cards are byte-untouched.
                ok, info = german_anchor.reanchor(masked, inp.get('skeleton') or '')
                candidate, cand_unmapped = None, []
                if ok:
                    candidate = restore_card(masked, field, phs, cand_unmapped)
                if (candidate is not None
                        and count_card(candidate, '<ls') == inp['ls']
                        and count_card(candidate, '{#') == inp['sk']):
                    card, unmapped = candidate, cand_unmapped
                    card['german_anchor'] = german_anchor.stamp(info)
                else:
                    error = 'fidelity-reject: german-anchor %s' % (
                        'verify-failed' if ok else info.get('reason', 'refused'))
                    card = None
            if card is not None:
                if (count_card_field(card, field, '<ls') != inp['ls']
                        or count_card_field(card, field, '{#') != inp['sk']):
                    # H1152 parity (C1): german echo is faithful, but the translation dropped a
                    # span -- requeue instead of promoting a lossy card.
                    error = 'translation-fidelity-reject'
                    card = None
                elif unmapped:
                    # C-42: an out-of-range {Tn} maps nothing and cannot be recovered downstream.
                    error = 'unmapped-token-reject'
                    card = None
        row = {'key': key, 'card': card, 'judge': None, 'judge_sonnet': None,
               'escalated': False}
        if error:
            row['error'] = error
        rows.append(row)
    return rows


def classify_process(proc):
    text = (proc.stdout or '') + '\n' + (proc.stderr or '')
    if AUTH_RE.search(text):
        return 'authentication', EXIT_AUTH
    if RATE_RE.search(text):
        return 'rate_limit', EXIT_RATE_LIMIT
    if CONN_RE.search(text):
        return 'connection', proc.returncode or 1
    return 'process', proc.returncode or 1


# H2077 / #947: reasons meaning "the CALL died", not "the card is defective". A fragment missing
# for one of these leaves an otherwise healthy card incomplete, so the audit must not file it as a
# content defect — that denylists the card AND discards the frag_prov fshas of the fragments that
# DID translate (paid-for TM, permanently). Deliberately a CLOSED list: anything unrecognised (a
# fidelity reject, a mismatched fragment key, malformed output) stays content, because
# over-exempting would let a genuinely defective card back into the cheap-re-run lane — the
# 'stubborn null' loop that the fidelity-reject rule exists to stop.
INFRA_FAILURE_REASONS = ('timeout', 'budget_exceeded', 'rate_limit', 'authentication', 'connection')


def is_infra_failure(reason):
    """True when a recorded failure reason means the call failed, not that the card is bad."""
    return bool(reason) and str(reason).startswith(INFRA_FAILURE_REASONS)


def timeout_output_text(exc):
    """Text drained from a killed child and attached to its ``TimeoutExpired`` by ``run_tree_kill``.

    Empty string when nothing was captured (an older runner, or a stub that raises a bare
    ``TimeoutExpired``), so every caller degrades to the historical 'timeout' classification."""
    out = getattr(exc, 'output', None) or ''
    err = getattr(exc, 'stderr', None) or ''
    if isinstance(out, bytes):
        out = out.decode('utf-8', 'replace')
    if isinstance(err, bytes):
        err = err.decode('utf-8', 'replace')
    return out + '\n' + err


def classify_timeout(exc):
    """Classify a KILLED call from the output ``run_tree_kill`` attached to its ``TimeoutExpired``.

    A rate-limited or unauthenticated Claude CLI does not exit with 429/401 — it retries internally
    until our wall ceiling kills it (Uprava FINDINGS §270), so the provider's own message reaches
    the pipeline only through the attached text. Without this, an account-level refusal is recorded
    as a local `timeout` and the run keeps spending against a locked account.

    Deliberately narrower than ``classify_process``: only ACCOUNT-level causes are promoted. A
    `connection`-looking string in a killed call's output stays 'timeout', because the call really
    did exceed the wall ceiling and 'connection' would claim more than the evidence supports."""
    text = timeout_output_text(exc)
    if AUTH_RE.search(text):
        return 'authentication', EXIT_AUTH
    if RATE_RE.search(text):
        return 'rate_limit', EXIT_RATE_LIMIT
    return 'timeout', EXIT_TIMEOUT


def card_by_key(cards):
    out = {}
    for card in cards or []:
        if isinstance(card, dict) and card.get('key1') not in out:
            out[card.get('key1')] = card
    return out


def token_multiset(value):
    if not isinstance(value, str):
        value = json.dumps(value, ensure_ascii=False)
    return collections.Counter(re.findall(r'\{T\d+\}', value))


def card_token_multiset(card):
    # C-17: collect {Tn} from EVERY source-mirror field (record.grammar + sense.german), driven
    # by the one `card_fields.TOKEN_FIDELITY_FIELDS` tuple the JS `cardTokens` also uses. The old
    # body read `sense.german` only, so a grammar-{Tn} card counted fewer tokens than its skeleton
    # and was falsely `fragment-fidelity-reject`ed on this lane while JS accepted it.
    record_fields = [n for lvl, n in card_fields.TOKEN_FIDELITY_FIELDS if lvl == 'record']
    sense_fields = [n for lvl, n in card_fields.TOKEN_FIDELITY_FIELDS if lvl == 'sense']
    tokens = []
    for record in card.get('records') or []:
        for name in record_fields:
            tokens.extend(re.findall(r'\{T\d+\}', record.get(name) or ''))
        for sense in record.get('senses') or []:
            for name in sense_fields:
                tokens.extend(re.findall(r'\{T\d+\}', sense.get(name) or ''))
    return collections.Counter(tokens)


# run_tree_kill / terminate_tree moved to proc_tree (shared D-J runner); imported above.


def _fragment_index(frag_key):
    """H2a sort key: the NUMERIC fragment index of a `<key>_f<index>` fragment key.

    Plain lexicographic order would put `_f10` before `_f2`, making the reported stop
    reason depend on how many fragments a card happens to have. Unparseable keys sort
    first and deterministically rather than raising.
    """
    try:
        return int(frag_key.rsplit('_f', 1)[1])
    except (IndexError, ValueError):
        return -1


class HeadlessEngine:
    def __init__(self, manifest, claude, timeout, runner, max_agents_override=None,
                 call_reservation=None, config_dir=None, active_claim=None):
        self.m = manifest
        self.claude = claude
        if not config_dir:
            raise ValueError('paid headless execution requires an explicit config directory')
        self.config_dir = os.path.abspath(config_dir)
        self.profile_fingerprint = config_dir_fingerprint(self.config_dir)
        self.active_claim = active_claim
        budgets = manifest.get('budgets') or {}
        # R4 (C-15): the effective bound is min(operator, budgets.timeout_ceil_ms, HARD).
        #
        # H2254: the two INPUTS to that min() are now refused above the hard maximum instead
        # of being clamped into it, and the refusal happens here -- in __init__, before a
        # single model subprocess is spawned, so a bad request costs nothing. The min() below
        # is unchanged and still selects the STRICTEST of the three; only the direction of
        # the >ceiling case moved, from "quietly becomes 300 s" to "raises".
        #
        # Both are checked, not just the operator's: a sealed manifest reaches this engine
        # through `--allow-historical-v1` and through validate_manifest, and defence in depth
        # here means the money guard does not depend on which validation path ran first.
        requested_ms = int(timeout) * 1000
        assert_timeout_within_ceiling(requested_ms, 'operator --timeout', HARD_TIMEOUT_MS)
        ceil_ms = budgets.get('timeout_ceil_ms')
        assert_timeout_within_ceiling(ceil_ms, 'manifest budgets.timeout_ceil_ms',
                                      HARD_TIMEOUT_MS)
        eff_ms = min(requested_ms, HARD_TIMEOUT_MS)
        if ceil_ms:
            eff_ms = min(eff_ms, int(ceil_ms))
        self.timeout = eff_ms / 1000.0
        self.cli_cwd = bare_cli_cwd()   # H2158: None => inherit, the historical behaviour
        # H2189: opt-in, and resolved ONCE here rather than per call, so a mid-run CLI
        # swap cannot make half a window's calls carry the flag and half not.
        self.safe_mode = resolve_safe_mode(manifest, claude)
        self.run = runner or run_tree_kill
        self.attempts = []
        self.failures = {}
        self.translate_calls = 0
        self.heal_calls = 0
        self.kill_timeouts = 0
        self.conn_errors = 0
        # R3 (C-12/C-13): the manifest agent budgets were write-only -- emitted, validated-adjacent,
        # never read by the executor. Enforce them here. None = unbounded (back-compat). The
        # `--max-agents` override caps the TOTAL across both lanes and binds even without budgets.
        self.max_translate_agents = budgets.get('max_translate_agents')
        self.max_heal_agents = budgets.get('max_heal_agents')
        self.max_total_agents = budgets.get('max_agents')
        if max_agents_override is not None:
            self.max_total_agents = (max_agents_override if self.max_total_agents is None
                                     else min(self.max_total_agents, max_agents_override))
        self.budget_stops = 0
        # R5 (C-25): the CLI wrapper's usage/cost were parsed then dropped at the call site, so
        # actual spend was unreconcilable and a priced run ended STOP_COST_UNEVALUABLE. Accumulate.
        self.usage = {'input_tokens': 0, 'output_tokens': 0, 'cache_read_tokens': 0,
                      'cache_creation_tokens': 0, 'subagent_tokens': 0,
                      'usage_evaluable': True,
                      'observed_cost_usd': 0.0, 'cost_evaluable': True, 'priced_calls': 0,
                      'missing_usage_calls': 0}
        self.call_reservation = call_reservation

    def note(self, key, error, preserve=False):
        # H1610 / H1618: mirror JS `if (!FAIL[k]) noteFail(...)` so a later terminal
        # soft stamp (selfheal-nothing-resolved, no-selfheal-fallback) cannot clobber
        # an earlier budget_exceeded / timeout / content note that is the real cause.
        if preserve and key in self.failures:
            return
        self.failures[key] = str(error)[:300]

    def _accumulate_usage(self, telemetry):
        """Fold one already-validated call finalization into the in-memory result summary."""
        self.usage['priced_calls'] += 1
        for name in ('input_tokens', 'output_tokens', 'cache_read_tokens',
                     'cache_creation_tokens'):
            self.usage[name] += telemetry[name]
        accounting = telemetry.get('accounting') or {}
        usage_evaluable = accounting.get(
            'usage_evaluable', telemetry.get('cost_evaluable', False)) is True
        if not usage_evaluable:
            self.usage['usage_evaluable'] = False
            self.usage['missing_usage_calls'] += 1
        if not telemetry['cost_evaluable']:
            self.usage['cost_evaluable'] = False
        self.usage['observed_cost_usd'] += telemetry['observed_cost_usd']
        self.usage['subagent_tokens'] = (
            self.usage['input_tokens'] + self.usage['output_tokens']
            + self.usage['cache_read_tokens'] + self.usage['cache_creation_tokens'])

    def _budget_ok(self, heal):
        """R3: True while another spawn on this lane stays within the manifest agent budgets.
        Checked BEFORE the counter increments and the subprocess spawns, so `translate_calls` /
        `heal_calls` can never exceed their ceilings. None = unbounded (back-compat)."""
        if (self.max_total_agents is not None and
                self.translate_calls + self.heal_calls >= self.max_total_agents):
            return False
        if heal:
            return self.max_heal_agents is None or self.heal_calls < self.max_heal_agents
        return self.max_translate_agents is None or self.translate_calls < self.max_translate_agents

    def call(self, prompt, label, keys, heal=False):
        if not self._budget_ok(heal):
            # R3: a refused call consumes NO spawn and returns a typed stop reason.
            self.budget_stops += 1
            return None, 'budget_exceeded:%s' % ('heal' if heal else 'translate')
        if self.call_reservation is None:
            raise RuntimeError(
                'paid headless spawn requires a durable call reservation ledger')
        if (not isinstance(self.active_claim, ActiveCallClaim)
                or not self.active_claim.is_live_canonical_for(
                    self.profile_fingerprint)):
            raise RuntimeError(
                'paid headless spawn requires the live canonical profile claim')
        argv = claude_argv_prefix(self.claude) + [
                '-p', '--output-format', 'json', '--json-schema',
                json.dumps(self.m['output_schema'], ensure_ascii=False, separators=(',', ':')),
                '--model', self.m['model'], '--permission-mode', 'plan']
        if self.safe_mode:                       # H2189: strips profile CLAUDE.md/skills/hooks
            argv.append(SAFE_MODE_FLAG)
        try:
            reservation = self.call_reservation.reserve(
                'headless:%s' % ('heal' if heal else 'translate'),
                profile=(self.m.get('execution') or {}).get('profile_slot'),
                detail=label)
        except CallLimitReached:
            self.budget_stops += 1
            return None, 'budget_exceeded:max_calls'
        started = time.monotonic()
        if heal:
            self.heal_calls += 1
        else:
            self.translate_calls += 1
        try:
            proc = self.run(argv, input=prompt, text=True, encoding='utf-8',
                            capture_output=True, timeout=self.timeout, cwd=self.cli_cwd)
        except subprocess.TimeoutExpired as exc:
            # A timeout happened after a real spawn. No trustworthy wrapper survived, so count the
            # call and fail closed on cost instead of leaving a paid timeout looking like $0.
            telemetry = unevaluable_telemetry()
            self.call_reservation.finalize(reservation, telemetry)
            self._accumulate_usage(telemetry)
            self.kill_timeouts += 1
            # H2056 / #944: a rate-limited CLI HANGS rather than reporting 429 (FINDINGS §270), so
            # this handler — not classify_process below — is where an account-level refusal actually
            # lands. run_tree_kill now attaches the killed child's drained output (#943), so the
            # cause is finally visible here. Route it into the SAME HardFailure path a non-hanging
            # 429 takes: that is what makes the worker exit 21 and lets the orchestrator's existing
            # is_rate_limited -> park + requeue_rate_limited fire. Without it the run continues
            # against a locked account, returns all-null cards, and is recorded done/success.
            classification, code = classify_timeout(exc)
            attempt = {'label': label, 'keys': keys, 'returncode': 124,
                       'elapsed_ms': int((time.monotonic() - started) * 1000),
                       'classification': classification}
            cleanup = getattr(exc, 'cleanup_trouble', None)
            if cleanup:                                # D-J: diagnostic only, about cleanup not cause
                attempt['cleanup_trouble'] = cleanup
            self.attempts.append(attempt)
            if classification != 'timeout':
                # Account-level: stop the run. Every remaining call would hit the same wall.
                raise HardFailure(classification, code, timeout_output_text(exc)[-2000:])
            return None, 'timeout'
        except BaseException:
            # Reservation authority is irreversible. A spawn/runner exception
            # cannot turn the attempt back into an apparent zero-cost call.
            telemetry = unevaluable_telemetry()
            self.call_reservation.finalize(reservation, telemetry)
            self._accumulate_usage(telemetry)
            raise
        elapsed = int((time.monotonic() - started) * 1000)
        try:
            wrapper = parse_cli_wrapper(proc.stdout)
        except ValueError:
            wrapper = None
        # Account for EVERY spawned process before classifying its result. This covers non-zero
        # provider exits and rc=0 wrappers whose structured_output is malformed. A missing envelope
        # increments missing_usage_calls and makes the whole run unevaluable.
        execution = self.m.get('execution') or {}
        telemetry = telemetry_from_cli_wrapper(
            wrapper, max_agent_sdk_credit=True,
            credit_claimed=execution.get('agent_sdk_credit_claimed') is True,
            credit_claim_evidence=execution.get('agent_sdk_credit_claim_evidence'))
        structured = None
        structured_error = None
        structured_raw_path = None
        if not proc.returncode:
            try:
                if wrapper is None:
                    raise ValueError('Claude output is not a JSON object envelope')
                structured = structured_from_wrapper(wrapper)
            except ValueError as exc:
                structured_error = exc
                # Malformed output is permanently unevaluable even if its outer wrapper claimed
                # a price: the paid/result association itself failed validation.
                telemetry = dict(telemetry, cost_evaluable=False)
                # H3157 repair (c): keep the envelope of any PAID call that failed validation.
                # The §498 diagnosis survived only because the CLI happened to keep its own
                # session JSONL; the harness saved nothing, so a refusal that billed 5 401
                # output tokens left no evidence of its own cause. Best-effort by construction.
                structured_raw_path = write_failed_envelope(
                    label, 'refusal' if isinstance(exc, StructuredRefusal) else 'malformed_output',
                    proc.stdout, exc)
        # Durable finalization occurs before any classification branch returns or raises.
        self.call_reservation.finalize(reservation, telemetry)
        self._accumulate_usage(telemetry)
        if proc.returncode:
            classification, code = classify_process(proc)
            if classification == 'connection':
                self.conn_errors += 1
            self.attempts.append({'label': label, 'keys': keys, 'returncode': proc.returncode,
                                  'elapsed_ms': elapsed, 'classification': classification})
            raise HardFailure(classification, code, (proc.stderr or proc.stdout or '')[-2000:])
        if structured_error is not None:
            # H3157 repair (b): a refusal and a malformed structured channel are different
            # faults with different fixes — the first is a prompt/mode problem, the second a
            # schema/parser one. Reporting both as `malformed_output` routed the operator to
            # the wrong half of the system for a full session (§498).
            refused = isinstance(structured_error, StructuredRefusal)
            classification = 'refusal' if refused else 'malformed_output'
            attempt = {'label': label, 'keys': keys, 'returncode': 0,
                       'elapsed_ms': elapsed, 'classification': classification}
            if structured_raw_path:
                attempt['raw_envelope_path'] = structured_raw_path
            if refused:
                # The model's own words are the diagnosis; carry a bounded excerpt inline so a
                # reader of the attempt log never has to go find the file to know what happened.
                attempt['refusal_excerpt'] = (structured_error.prose or '')[:400]
            self.attempts.append(attempt)
            return None, '%s:%s' % (classification, structured_error)
        self.attempts.append({'label': label, 'keys': keys, 'returncode': 0,
                              'elapsed_ms': elapsed, 'classification': 'success'})
        return structured, None

    def whole_prompt(self, keys):
        return build_prompt(self.m, keys)

    def resolve_group(self, keys, label):
        resolved = {}
        pending = list(keys)
        attempts = int(self.m.get('runtime', {}).get('whole_attempts', 2))
        timed_out = False
        for attempt in range(attempts):
            if not pending:
                break
            structured, error = self.call(self.whole_prompt(pending),
                                          '%s%s' % (label, '.retry%d' % attempt if attempt else ''),
                                          pending)
            if error:
                for key in pending:
                    self.note(key, error, preserve=error.startswith('budget_exceeded'))
                if error.startswith('budget_exceeded'):
                    break                    # R3: retrying/bisecting would only refuse again
                timed_out = error == 'timeout'
                if timed_out:
                    break
                continue
            for row in normalize_batch(self.m, pending, structured):
                if row['card']:
                    resolved[row['key']] = row['card']
                else:
                    self.note(row['key'], row.get('error', 'unresolved'))
            pending = [key for key in pending if key not in resolved]
        if (pending and len(pending) > 1 and
                self.m.get('runtime', {}).get('binary_split', True) and
                self._budget_ok(False)):
            mid = (len(pending) + 1) // 2
            for suffix, half in (('A', pending[:mid]), ('B', pending[mid:])):
                child, _child_pending = self.resolve_group(half, label + '/' + suffix)
                resolved.update(child)
            pending = [key for key in pending if key not in resolved]
        return resolved, pending

    def fragment_prompt(self, key, group, indices):
        # B01/H2191 implementation is shared with the batch compiler so cache
        # blocks cannot drift from the production CLI prompt.
        return build_fragment_prompt(self.m, key, group, indices)

    def heal_group(self, key, group, indices, label, budget):
        resolved = {}
        pending = list(indices)
        attempts = int(self.m.get('runtime', {}).get('fragment_attempts', 3))
        timed_out = False
        for attempt in range(attempts):
            if not pending or budget['spent'] >= budget['max']:
                break
            budget['spent'] += 1
            structured, error = self.call(self.fragment_prompt(key, group, pending),
                                          '%s%s' % (label, '.retry%d' % attempt if attempt else ''),
                                          ['%s_f%d' % (key, i) for i in pending], heal=True)
            if error:
                for index in pending:
                    self.note('%s_f%d' % (key, index), error)
                if error.startswith('budget_exceeded'):
                    break                    # R3: heal ceiling hit -- stop, do not bisect
                timed_out = error == 'timeout'
                if timed_out:
                    break
                continue
            by_key = card_by_key(structured['cards'])
            for index in pending:
                frag_key = '%s_f%d' % (key, index)
                card = by_key.get(frag_key)
                if not card:
                    self.note(frag_key, 'missing-or-mismatched-fragment-key')
                    continue
                if card_token_multiset(card) != token_multiset(group[index]['skeleton']):
                    self.note(frag_key, 'fragment-fidelity-reject')
                    continue
                resolved[index] = card
            pending = [index for index in pending if index not in resolved]
        no_bisect = timed_out and self.m.get('runtime', {}).get('kill_timeout_no_bisect', True)
        if (len(pending) > 1 and not no_bisect and budget['spent'] < budget['max']
                and self._budget_ok(True)):
            mid = (len(pending) + 1) // 2
            for suffix, half in (('A', pending[:mid]), ('B', pending[mid:])):
                child, _ = self.heal_group(key, group, half, label + '/' + suffix, budget)
                resolved.update(child)
            pending = [index for index in pending if index not in resolved]
        return resolved, pending

    def _fragment_keys(self, key):
        """H2a: the EXACT fragment-key set for `key`, derived from `fragment_groups`.

        Never a prefix match. Fragment keys are `<key>_f<index>` (see `fragment_prompt` /
        `heal_group`), so a `startswith('ab_f')` test also captures `ab_foo_f0` — a
        DIFFERENT card's fragment. Set membership built from this card's own groups
        cannot make that mistake.
        """
        groups = self.m.get('fragment_groups', {}).get(key) or []
        return {'%s_f%d' % (key, index)
                for group in groups for index in range(len(group))}

    def _partial_cause(self, key):
        """H2077 / #947: the typed reason this card came back PARTIAL, for the audit's
        transient-vs-defect split.

        Before this, a partial card recorded WHICH fragments were missing but never WHY, so the
        audit could only judge it by SHAPE — and a card left incomplete by a hung/budget-stopped
        heal call was filed as a content defect, permanently denylisting a healthy card and
        discarding the TM of the fragments that did translate.

        Same deterministic precedence as `_selfheal_stop_reason`: fragment keys in ascending
        NUMERIC index, first INFRASTRUCTURE reason wins, so several failed fragments cannot make
        the reported cause depend on set/dict iteration order. Falls back to the first recorded
        reason of any kind, so a content cause is still reported — and still classified as
        content by `is_infra_failure`. Returns None when nothing was recorded, which the audit
        treats exactly as it did before (unchanged behaviour)."""
        first = None
        for frag_key in sorted(self._fragment_keys(key), key=_fragment_index):
            error = self.failures.get(frag_key)
            if not error:
                continue
            if is_infra_failure(error):
                return error
            if first is None:
                first = error
        return first

    def _selfheal_stop_reason(self, key):
        """H2a: classify a zero-sense `self_heal` outcome as infrastructure vs content.

        A heal-lane budget refusal is a TRANSIENT INFRASTRUCTURE stop, not a content
        defect. `call()` returns the typed `budget_exceeded:*` reason and `heal_group`
        stamps it on the FRAGMENT keys, but the presplit base key was then stamped
        `selfheal-nothing-resolved` — routing a budget stop into the content-defect lane
        (the C-49 residual class). `note(..., preserve=True)` could not save it: preserve
        only protects an EARLIER note on the base key, and a presplit key has none,
        because it never ran a whole-card translate attempt. So propagate the typed
        reason to the base key instead.

        Precedence is deterministic and RANKED, in two passes over the fragment keys in
        ascending NUMERIC index (so `_f10` sorts after `_f2`, not before it):

        1. the first `budget_exceeded:*` — H2a's invariant, deliberately unchanged. A budget
           stop must stay observable and must NOT be masked by another reason on a lower
           index (pinned by `test_h2a_precedence_is_deterministic_and_budget_stays_observable`);
        2. failing that, the first OTHER typed infrastructure reason — H2091 (#948);
        3. failing that, the historical `selfheal-nothing-resolved`.

        H2091 (#948) added rank 2. H2a's argument was never budget-specific: a heal lane that
        died because the CALL died is a transient infrastructure stop whatever killed it, yet a
        `timeout` fell through to `selfheal-nothing-resolved` — a CONTENT verdict, and the ONLY
        per-key cause an operator or any downstream tool ever sees (`row['error']`,
        `summary['failures'][key]`, `report['failure_reasons'][key]`). The typed reason survived
        only on the discarded `<key>_f<i>` fragment keys. Widening had to be RANKED rather than
        flat, because a flat "first infra wins" lets a low-index `timeout` mask a budget stop and
        silently repeals H2a.

        A genuine content failure (fidelity reject, missing/mismatched key) still leaves
        `selfheal-nothing-resolved` exactly as it was — that string must keep meaning "the model
        answered and nothing usable came back".
        """
        ordered = sorted(self._fragment_keys(key), key=_fragment_index)
        errors = [self.failures.get(frag_key) for frag_key in ordered]
        for error in errors:                                   # rank 1: budget stop (H2a)
            if error and error.startswith('budget_exceeded'):
                return error
        for error in errors:                                   # rank 2: any other infra (#948)
            if is_infra_failure(error):
                return error
        return 'selfheal-nothing-resolved'                     # rank 3: genuine content

    def self_heal(self, key):
        groups = self.m.get('fragment_groups', {}).get(key) or []
        if not groups:
            self.note(key, 'no-selfheal-fallback', preserve=True)
            return None
        runtime = self.m.get('runtime', {})
        maximum = (int((len(groups) * float(runtime.get('per_card_heal_factor', 1.5))) + 0.9999) +
                   int(runtime.get('per_card_heal_headroom', 3)))
        if not runtime.get('per_card_heal_budget', True):
            maximum = 10 ** 9
        budget = {'spent': 0, 'max': maximum}
        cached_groups = self.m.get('fragment_tm', {}).get(key) or []
        ph_groups = self.m.get('fragment_placeholder_maps', {}).get(key) or []
        senses = []
        owners = []          # C-02: parallel to `senses` -- the (h, grammar) each came from
        unmapped = []        # C-42: {Tn} indices that map nothing, instead of a silent pass
        frag_prov = []
        missing = []
        sense_tags = {}
        for gi, group in enumerate(groups):
            cached = cached_groups[gi] if gi < len(cached_groups) else []
            phs = ph_groups[gi] if gi < len(ph_groups) else []
            uncached = [i for i in range(len(group)) if i >= len(cached) or not cached[i]]
            resolved, unresolved = self.heal_group(key, group, uncached,
                                                   'heal:%s#g%d' % (key, gi + 1), budget)
            missing.extend('g%d:f%d' % (gi + 1, i) for i in unresolved)
            for index, fragment in enumerate(group):
                # C-02: keep each sense's OWNING record. The old comprehension here flattened
                # `records -> senses` and dropped `record` itself, so the stitch below had no
                # `h`/`grammar` left in scope to emit and every promoted row read `h: null`
                # (468 rows / 20 sub-cards). `h` is free lexicographic text ("2. bhid",
                # "PW 3 (с anu, отсылка к entry 5)"), so a dropped one cannot be reconstructed
                # later -- it has to survive the flatten.
                frag_records = []
                if index < len(cached) and cached[index]:
                    # R6: a served frag-TM slot is v2 -- it carries the PER-SENSE owner harvested at
                    # the fresh-resolve run. v1 (ownerless) rows are a serve-time cache MISS (the
                    # gview build drops them), so a served slot restores each sense's real
                    # (h, grammar) instead of the C-02 residual null owner that regenerated null-`h`
                    # rows on every warm run.
                    slot = cached[index]
                    c_senses = slot.get('senses') or []
                    c_owners = slot.get('owners') or []
                    frag_records = [((c_owners[j] or [None, None])[0] if j < len(c_owners) else None,
                                     (c_owners[j] or [None, None])[1] if j < len(c_owners) else None,
                                     [c_senses[j]])
                                    for j in range(len(c_senses))]
                elif index in resolved:
                    card = restore_card(resolved[index], self.m['field'],
                                        phs[index] if index < len(phs) else [], unmapped)
                    frag_records = [(record.get('h'), record.get('grammar'),
                                     record.get('senses') or [])
                                    for record in card.get('records') or []]
                    frag_senses = [sense for _, _, group in frag_records for sense in group]
                    # R6: carry the PER-SENSE owner into frag_prov so a later warm-cache stitch of
                    # this fragment restores each sense's (h, grammar) instead of a null owner.
                    frag_owners = [[rh, rg] for rh, rg, group in frag_records for _ in group]
                    if fragment.get('fsha') and frag_senses:
                        frag_prov.append({'fsha': fragment['fsha'], 'senses': frag_senses,
                                          'owners': frag_owners})
                for rec_h, rec_grammar, group in frag_records:
                    for sense in group:
                        source_ord = fragment.get('si')
                        if source_ord is not None:
                            if source_ord in sense_tags:
                                sense['tag'] = sense_tags[source_ord]
                            else:
                                sense_tags[source_ord] = sense.get('tag')
                        senses.append(sense)
                        owners.append((rec_h, rec_grammar))
        if not senses:
            # H2a: a heal-budget stop recorded on this card's own fragments is the real
            # cause and must not be reported as a content defect.
            self.note(key, self._selfheal_stop_reason(key), preserve=True)
            return None
        card = stitched_card(
            key,
            portrait_key_iast((self.m['inputs'].get(key) or {}).get('portrait') or '', key),
            senses, owners)
        if frag_prov:
            card['frag_prov'] = frag_prov
        if missing:
            card.update({'partial': True, 'missing_fragments': missing,
                         'missing_groups': len({item.split(':')[0] for item in missing}),
                         'total_groups': len(groups)})
            # H2077 / #947: record WHY it is partial, not just which fragments are absent. The
            # audit's transient-vs-defect split consumes `partial_cause_infra`; without it the
            # split can only see shape, and an infrastructure gap reads as a content defect.
            cause = self._partial_cause(key)
            if cause:
                card['partial_cause'] = cause
                card['partial_cause_infra'] = is_infra_failure(cause)
        else:
            inp = self.m['inputs'][key]
            ls_count, sk_count = count_card(card, '<ls'), count_card(card, '{#')
            if ls_count != inp['ls'] or sk_count != inp['sk']:
                self.note(key, 'stitched-fidelity-reject: <ls> %d/%d, {# %d/%d' %
                          (ls_count, inp['ls'], sk_count, inp['sk']))
                return None
            # H1152 parity (C1): the german counts above are the SOURCE echo. Run the same count
            # over the TARGET field so a translation-only span drop on the headless heal lane is
            # rejected instead of stitched and promoted (twin of the JS selfHeal check).
            field = self.m['field']
            ls_t, sk_t = count_card_field(card, field, '<ls'), count_card_field(card, field, '{#')
            if ls_t != inp['ls'] or sk_t != inp['sk']:
                self.note(key, 'stitched-translation-fidelity-reject: %s <ls> %d/%d, {# %d/%d' %
                          (field, ls_t, inp['ls'], sk_t, inp['sk']))
                return None
        # C-42: a {Tn} whose index maps nothing used to be written through verbatim on a card
        # that reported success -- that is how `ban_d~~h0_11_ni` and `ban_d~~h0_21_upasam_0`
        # reached the canonical store carrying a raw {T196}/{T235}. The token is unrecoverable
        # by construction (the index addresses a whole-article map the sub-card never had), so
        # refuse the card instead of promoting a known-corrupt one.
        if unmapped:
            self.note(key, 'unmapped-token-reject: %d out-of-range placeholder(s): %s'
                      % (len(unmapped), ', '.join(sorted(set(unmapped))[:6])))
            return None
        return card

    def run_all(self):
        rows = []
        healed = 0
        presplit = set(self.m.get('presplit_keys') or [])
        for index, batch in enumerate(self.m.get('batches') or []):
            resolved, pending = self.resolve_group(batch, 'b%d' % index)
            for key in pending:
                card = self.self_heal(key)
                if card:
                    resolved[key] = card
                    healed += 1
            for key in batch:
                row = {'key': key, 'card': resolved.get(key), 'judge': None,
                       'judge_sonnet': None, 'escalated': key in pending and key in resolved}
                if not row['card']:
                    row['error'] = self.failures.get(key, 'unknown')
                rows.append(row)
        for key in self.m.get('presplit_keys') or []:
            card = self.self_heal(key)
            row = {'key': key, 'card': card, 'judge': None, 'judge_sonnet': None,
                   'escalated': bool(card), 'presplit': True}
            if not card:
                row['error'] = self.failures.get(key, 'unknown')
            else:
                healed += 1
            rows.append(row)
        return rows, healed, len(presplit)


def _validate_fragment_tm(manifest):
    """R6 execution-time gate: refuse a manifest whose fragment_tm carries any warm slot with
    invalid/null owners, BEFORE any paid call. The generator's gview already drops v1 (ownerless) and
    null-owner rows, but a DIRECT / hand-edited manifest bypasses the generator -- so validate here
    that every non-empty slot is a v2 shape {senses, owners} whose owners are len(senses) [h, grammar]
    pairs with BOTH members strings (no None). A bare/legacy (ownerless) slot or a null owner is
    refused rather than stitched under a null owner."""
    for key, groups in (manifest.get('fragment_tm') or {}).items():
        for group in groups or []:
            for slot in group or []:
                if not slot:
                    continue                     # None / empty slot = cache miss, fine
                senses = slot.get('senses') if isinstance(slot, dict) else None
                owners = slot.get('owners') if isinstance(slot, dict) else None
                if not (isinstance(senses, list) and isinstance(owners, list)
                        and len(owners) == len(senses)
                        and all(isinstance(p, (list, tuple)) and len(p) == 2
                                and all(isinstance(x, str) for x in p) for p in owners)):
                    raise ValueError(
                        'fragment_tm slot for %r has invalid/null owners (refused before any call): %r'
                        % (key, owners))


def refuse_starvation_max_agents(manifest, max_agents_override):
    """H1610 / H1618: `--max-agents N` is a TOTAL spawn ceiling (translate+heal), not width.

    Canary-only values (N=1) on multi-key windows produce only-b0 / all-nulls with
    `budget_stops ≫ 0` while failures are stamped `selfheal-nothing-resolved`. Refuse
    before any paid call when the override is strictly less than the selected key count.
    Single-key canaries (override >= 1 and keys == 1) still pass.
    """
    if max_agents_override is None:
        return
    keys = (manifest.get('meta') or {}).get('selected_keys') or []
    n = len(keys)
    if n > 1 and max_agents_override < n:
        raise ValueError(
            '--max-agents=%d starves a %d-key window (total spawn ceiling, not concurrency '
            'width). Omit --max-agents for multi-key/heal-capable windows so manifest '
            'budgets (max_translate_agents / max_heal_agents) apply; use --max-agents 1 '
            'only for true single-spawn canaries (1 key that must finish in one call). '
            'See LAUNCH_FUCKUPS id C2_M50_W1_MAX_AGENTS1_2026-07-24.'
            % (max_agents_override, n))


def execute(manifest, claude='claude', timeout=DEFAULT_TIMEOUT_S, runner=None,
            max_agents_override=None,
            call_reservation=None, config_dir=None):
    validate_manifest(manifest, require_v2=False)
    _validate_fragment_tm(manifest)      # R6: refuse a null-owner fragment_tm slot BEFORE any call
    refuse_starvation_max_agents(manifest, max_agents_override)
    config_dir = config_dir or os.environ.get('CLAUDE_CONFIG_DIR')
    if not config_dir:
        raise ValueError('CLAUDE_CONFIG_DIR is required for paid headless execution')
    config_dir = os.path.abspath(config_dir)
    if manifest.get('schema') == SCHEMA_V2:
        # Public execute() is itself a paid boundary. Do not rely on a CLI
        # caller having validated the manifest against the actual profile.
        validate_profile(manifest, config_dir)
    fingerprint = config_dir_fingerprint(config_dir)
    engine = None
    try:
        # One kernel-backed profile claim covers every translation/heal spawn
        # in this generation attempt. Public execute() therefore cannot bypass
        # the same lock that the CLI route uses.
        with ActiveCallClaim(fingerprint) as active_claim:
            engine = HeadlessEngine(
                manifest, claude, timeout, runner, max_agents_override,
                call_reservation=call_reservation, config_dir=config_dir,
                active_claim=active_claim)
            results, healed, presplit = engine.run_all()
    except HardFailure as exc:
        return None, {'classification': exc.classification, 'error': exc.detail,
                      'attempts': engine.attempts, 'usage': engine.usage}, exc.code
    for key, card in manifest.get('tm_resolved', {}).items():
        results.append({'key': key, 'card': card, 'judge': None, 'judge_sonnet': None,
                        'escalated': False, 'tm': True})
    for key, card in manifest.get('degenerate_resolved', {}).items():
        results.append({'key': key, 'card': card, 'judge': None, 'judge_sonnet': None,
                        'escalated': False, 'degenerate_passthrough': True})
    seen = {row['key'] for row in results}
    for key in manifest['meta']['selected_keys']:
        if key not in seen:
            results.append({'key': key, 'card': None, 'judge': None, 'judge_sonnet': None,
                            'escalated': False, 'error': 'unaccounted-key'})
    failures = {row['key']: row.get('error', 'unknown') for row in results if not row['card']}
    summary = {'root': manifest['meta']['root'], 'lang': manifest['meta']['lang'],
               'cards': len(results), 'ok': len(results) - len(failures), 'null': len(failures),
               'healed': healed, 'presplit': presplit,
               'tm': sum(bool(row.get('tm')) for row in results),
               'degenerate_passthrough': sum(bool(row.get('degenerate_passthrough')) for row in results),
               'null_keys': list(failures), 'partial_keys': [], 'failures': failures,
               # H858 Part B: how many cards were SAVED from an ls/sk fidelity-reject by
               # re-injecting a dropped source span, and which spans -- the measurement the
               # handoff's "is the {#-drop null class gone?" question is answered from. JS twin:
               # summary.german_anchor_repairs / german_anchor_detail.
               'german_anchor_repairs': sum(bool((row.get('card') or {}).get('german_anchor'))
                                            for row in results),
               'german_anchor_detail': [{'key': row['key'],
                                         'reinjected': row['card']['german_anchor']['reinjected']}
                                        for row in results
                                        if (row.get('card') or {}).get('german_anchor')],
               'translate_agents_spent': engine.translate_calls,
               'heal_agents_spent': engine.heal_calls,
               'budget_stops': engine.budget_stops,
               'usage': engine.usage,
               'kill_timeouts': engine.kill_timeouts, 'conn_errors': engine.conn_errors,
               'headless_attempts': engine.attempts}
    output_meta = dict(manifest['meta'])
    output_meta['execution_manifest_schema'] = manifest.get('schema')
    output_meta['execution'] = manifest.get('execution')
    output_meta['provenance_classes'] = manifest.get('key_provenance')
    payload = {'meta': output_meta, 'summary': summary, 'results': results}
    status = {'classification': 'completed_with_residuals' if failures else 'success',
              'attempts': engine.attempts, 'null_keys': list(failures),
              # H2251: what the spawn ACTUALLY did, which is not the same fact as
              # `meta.execution.cli_safe_mode` (what the manifest REQUESTED). They differ
              # exactly in the loud-downgrade case H2189 built the stderr warning for --
              # a CLI that cannot parse the flag. That warning is ephemeral; this is the
              # durable record, so a run whose savings were never actually taken can be
              # identified afterwards from its own artifacts instead of a lost console.
              'cli_safe_mode_effective': engine.safe_mode}
    return payload, status, 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('manifest')
    ap.add_argument('--output', required=True)
    ap.add_argument('--status-out', required=True)
    ap.add_argument('--claude-bin', default='claude')
    ap.add_argument('--only-profile', help='required profile-slot assertion for live v2 execution')
    ap.add_argument('--allow-historical-v1', action='store_true',
                    help='read-only/historical replay only; v1 is not a production contract')
    ap.add_argument('--timeout', type=int, default=DEFAULT_TIMEOUT_S,
                    help='per-call subprocess ceiling in SECONDS. Default and absolute '
                         'maximum %d s (H2254); a larger value is REFUSED before any paid '
                         'call, never clamped. Lower values bind normally.'
                         % DEFAULT_TIMEOUT_S)
    ap.add_argument('--max-agents', type=int, default=None,
                    help='R3: hard cap on TOTAL model spawns (translate+heal), not concurrency '
                         'width. Canary-only: refuse when N < selected key count (H1610). '
                         'Omit for multi-key windows so manifest budgets apply.')
    ap.add_argument('--call-reservation',
                    help='pwg.call_reservation.v1 ledger shared by probes and workers')
    ap.add_argument('--run-id', help='run key in --call-reservation')
    ap.add_argument('--max-calls', type=int, default=None,
                    help='durable total-call ceiling; must match the initialized ledger')
    ap.add_argument('--preflight', help='validated pwg.performance_preflight.v1/matrix.v1')
    ap.add_argument('--preflight-sha256', help='optional sealed preflight hash')
    ap.add_argument('--manifest-sha256',
                    help='required external seal for paid manifest v2 execution')
    import data_root
    data_root.add_arg(ap)
    args = ap.parse_args(argv)
    if args.data_root:
        # H2175 step 4: set the env seams before any path resolution so the worker and
        # every child it spawns resolve TM/input/output/telemetry under the data root.
        data_root.apply(args.data_root, ensure_dirs=True)
    # H1 (H1940): the manifest read/decode used to sit OUTSIDE this try, so an unreadable
    # file (OSError), undecodable bytes or invalid JSON escaped main() with NO status file
    # written at all -- the orchestrator saw a bare traceback instead of a deterministic
    # `configuration` verdict and burned its retries on a defect that can never succeed.
    # KeyError/TypeError from a structurally malformed manifest escaped the same way, from
    # inside the try, because they were absent from the except tuple.
    #
    # manifest_hash is bound to None FIRST so the unconditional status write below can
    # neither raise UnboundLocalError nor attest a hash for bytes that were never read.
    # null is the shape downstream already handles for an absent hash --
    # bounded_staged_run reads it as `headless.get('manifest_sha256')` and
    # max_account_orchestrator.emit_call_events falls back via `or 'call'`.
    manifest_hash = None
    try:
        with open(args.manifest, 'rb') as f:
            manifest_bytes = f.read()
        manifest_hash = hashlib.sha256(manifest_bytes).hexdigest()
        manifest = json.loads(manifest_bytes.decode('utf-8'))
        if manifest.get('schema') != SCHEMA_V1:
            if not args.manifest_sha256:
                raise ValueError('paid v2 execution requires --manifest-sha256')
            if manifest_hash != args.manifest_sha256:
                raise ValueError('manifest hash changed before paid execution')
        preflight_path = args.preflight or os.environ.get('PWG_PREFLIGHT_PATH')
        preflight_hash = args.preflight_sha256 or os.environ.get('PWG_PREFLIGHT_SHA256')
        if manifest.get('schema') != SCHEMA_V1:
            validate_preflight_artifact(
                preflight_path, manifest=manifest, expected_sha256=preflight_hash)
        reservation_path = args.call_reservation or os.environ.get('PWG_CALL_RESERVATION_PATH')
        reservation_run = args.run_id or os.environ.get('PWG_CALL_RESERVATION_RUN_ID')
        reservation_max = args.max_calls
        if reservation_max is None and 'PWG_CALL_RESERVATION_MAX_CALLS' in os.environ:
            raw_max = os.environ.get('PWG_CALL_RESERVATION_MAX_CALLS')
            reservation_max = None if raw_max == '' else int(raw_max)
        call_reservation = (CallReservationLedger(
            reservation_path, reservation_run, reservation_max) if reservation_path else None)
        if call_reservation is None:
            raise ValueError('paid execution requires --call-reservation and --run-id '
                             '(or PWG_CALL_RESERVATION_* environment)')
        if manifest.get('schema') == SCHEMA_V1:
            if not args.allow_historical_v1:
                raise ValueError('v1 manifest is historical-only; production requires %s' % SCHEMA_V2)
            payload, status, code = execute(manifest, args.claude_bin, args.timeout,
                                            max_agents_override=args.max_agents,
                                            call_reservation=call_reservation,
                                            config_dir=os.environ.get(
                                                'CLAUDE_CONFIG_DIR'))
        else:
            config_dir = os.environ.get('CLAUDE_CONFIG_DIR')
            if not config_dir:
                raise ValueError('CLAUDE_CONFIG_DIR is required for manifest v2')
            validate_profile(manifest, config_dir, args.only_profile)
            payload, status, code = execute(
                manifest, args.claude_bin, args.timeout,
                max_agents_override=args.max_agents,
                call_reservation=call_reservation, config_dir=config_dir)
    except (OSError, RuntimeError, ValueError, KeyError, TypeError) as exc:
        # KeyError/TypeError stringify to a bare quoted key or a bare internal message
        # ("'inputs'", "'int' object is not iterable") that names no cause, so those two
        # are qualified with their type. The pre-H1 types keep their exact wording.
        detail = (str(exc) if isinstance(exc, (OSError, RuntimeError, ValueError))
                  else '%s: %s' % (type(exc).__name__, exc))
        payload, status, code = None, {'classification': 'configuration', 'error': detail}, 2
    status['manifest_sha256'] = manifest_hash
    if payload is not None:
        payload.setdefault('meta', {})[
            'execution_manifest_sha256'] = manifest_hash
        atomic_json(args.output, payload)
        status['result_sha256'] = sha256_path(args.output)
    atomic_json(args.status_out, status)
    print(json.dumps(status, ensure_ascii=False))
    raise SystemExit(code)


if __name__ == '__main__':
    main()
