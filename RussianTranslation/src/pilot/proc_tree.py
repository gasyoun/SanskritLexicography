#!/usr/bin/env python
"""Shared bounded-best-effort process-tree runner (H818 D-J).

Both the headless worker's generation calls and the orchestrator's probe/worker subprocess
calls spawn the SAME Windows claude launcher — ``node cli-wrapper.cjs``, which ``spawnSync``'s
the native claude binary as a CHILD. The stdlib timeout kill (``TerminateProcess`` on the
immediate node process) leaves that binary ORPHANED, still holding the API call — the observed
multi-minute 'hang' as kill-timeouts accumulate orphans. This module is the single home for the
tree-kill runner so every claude-spawning kill point (worker calls, the outer worker subprocess,
``live_probe``, ``profile_status``, the presplit-canary worker) shares one implementation.
"""
import os
import subprocess
import sys
import threading
import time

from execution_contract import (KILLED_REASON_HARD_TIMEOUT,          # noqa: E402
                                KILLED_REASON_NO_OUTPUT_PROGRESS)

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

_CREATE_SUSPENDED = 0x00000004


def _join_trouble(*parts):
    """Join non-empty cleanup diagnostics without producing leading separators."""
    return ';'.join(part for part in parts if part)


if os.name == 'nt':
    import ctypes
    from ctypes import wintypes

    _JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
    _JOB_OBJECT_EXTENDED_LIMIT_INFORMATION_CLASS = 9

    class _JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ('PerProcessUserTimeLimit', ctypes.c_longlong),
            ('PerJobUserTimeLimit', ctypes.c_longlong),
            ('LimitFlags', wintypes.DWORD),
            ('MinimumWorkingSetSize', ctypes.c_size_t),
            ('MaximumWorkingSetSize', ctypes.c_size_t),
            ('ActiveProcessLimit', wintypes.DWORD),
            ('Affinity', ctypes.c_size_t),
            ('PriorityClass', wintypes.DWORD),
            ('SchedulingClass', wintypes.DWORD),
        ]

    class _IO_COUNTERS(ctypes.Structure):
        _fields_ = [
            ('ReadOperationCount', ctypes.c_ulonglong),
            ('WriteOperationCount', ctypes.c_ulonglong),
            ('OtherOperationCount', ctypes.c_ulonglong),
            ('ReadTransferCount', ctypes.c_ulonglong),
            ('WriteTransferCount', ctypes.c_ulonglong),
            ('OtherTransferCount', ctypes.c_ulonglong),
        ]

    class _JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ('BasicLimitInformation', _JOBOBJECT_BASIC_LIMIT_INFORMATION),
            ('IoInfo', _IO_COUNTERS),
            ('ProcessMemoryLimit', ctypes.c_size_t),
            ('JobMemoryLimit', ctypes.c_size_t),
            ('PeakProcessMemoryUsed', ctypes.c_size_t),
            ('PeakJobMemoryUsed', ctypes.c_size_t),
        ]

    _kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    _kernel32.CreateJobObjectW.argtypes = (ctypes.c_void_p, wintypes.LPCWSTR)
    _kernel32.CreateJobObjectW.restype = wintypes.HANDLE
    _kernel32.SetInformationJobObject.argtypes = (
        wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD)
    _kernel32.SetInformationJobObject.restype = wintypes.BOOL
    _kernel32.AssignProcessToJobObject.argtypes = (wintypes.HANDLE, wintypes.HANDLE)
    _kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
    _kernel32.TerminateJobObject.argtypes = (wintypes.HANDLE, wintypes.UINT)
    _kernel32.TerminateJobObject.restype = wintypes.BOOL
    _kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
    _kernel32.CloseHandle.restype = wintypes.BOOL

    _ntdll = ctypes.WinDLL('ntdll')
    _ntdll.NtResumeProcess.argtypes = (wintypes.HANDLE,)
    _ntdll.NtResumeProcess.restype = ctypes.c_long


class _WindowsKillJob:
    """A Windows Job Object that contains the child before its first instruction runs."""

    def __init__(self):
        self.handle = None

    def create(self):
        handle = _kernel32.CreateJobObjectW(None, None)
        if not handle:
            raise ctypes.WinError(ctypes.get_last_error())
        self.handle = handle
        info = _JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        info.BasicLimitInformation.LimitFlags = _JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not _kernel32.SetInformationJobObject(
                handle, _JOB_OBJECT_EXTENDED_LIMIT_INFORMATION_CLASS,
                ctypes.byref(info), ctypes.sizeof(info)):
            error = ctypes.WinError(ctypes.get_last_error())
            self.close()
            raise error

    def assign(self, proc):
        """Assign a CREATE_SUSPENDED Popen process before it can create descendants."""
        process_handle = int(proc._handle)  # CPython's owned process HANDLE on Windows
        if not _kernel32.AssignProcessToJobObject(self.handle, process_handle):
            raise ctypes.WinError(ctypes.get_last_error())

    @staticmethod
    def resume(proc):
        """Resume all threads in the newly assigned, initially suspended process."""
        process_handle = int(proc._handle)
        status = _ntdll.NtResumeProcess(process_handle)
        if status < 0:
            raise OSError('NtResumeProcess failed with NTSTATUS 0x%08x'
                          % (status & 0xffffffff))

    def terminate(self):
        """Terminate every current job member and close the kill-on-close handle."""
        trouble = None
        if self.handle:
            if not _kernel32.TerminateJobObject(self.handle, 1):
                trouble = 'TerminateJobObject:winerror%d' % ctypes.get_last_error()
        close_trouble = self.close()
        return _join_trouble(trouble, close_trouble)

    def close(self):
        trouble = None
        if self.handle:
            if not _kernel32.CloseHandle(self.handle):
                trouble = 'CloseHandle(job):winerror%d' % ctypes.get_last_error()
            self.handle = None
        return trouble


def windows_hidden_flags():
    """subprocess creationflags that suppress the transient console window ``taskkill``/``tasklist``
    would otherwise flash on Windows (``CREATE_NO_WINDOW``). Returns 0 (no-op) on POSIX so the same
    call is safe everywhere. Shared by proc_tree's taskkill and the selftests' tasklist so all three
    sites behave consistently."""
    if os.name == 'nt':
        return getattr(subprocess, 'CREATE_NO_WINDOW', 0)
    return 0


def terminate_tree(proc, deadline):
    """Bounded process-tree termination.

    Windows normally uses the race-free Job Object attached by :func:`run_tree_kill`; ``taskkill``
    is only a bounded fallback when job setup failed. POSIX kills the child's private process
    group. Always falls back to ``proc.kill()`` if the immediate child remains alive. Returns a
    short diagnostic string on cleanup trouble, else None — callers keep the primary ``timeout``
    classification regardless.
    """
    if proc.poll() is not None:
        job = getattr(proc, '_tree_job', None)
        if job is not None:
            return job.close()
        return None
    trouble = getattr(proc, '_tree_setup_trouble', None)
    if os.name == 'nt':
        job = getattr(proc, '_tree_job', None)
        if job is not None:
            trouble = _join_trouble(trouble, job.terminate())
        else:
            budget = max(1.0, deadline - time.monotonic())
            try:
                result = subprocess.run(
                    ['taskkill', '/PID', str(proc.pid), '/T', '/F'],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=budget,
                    creationflags=windows_hidden_flags())   # no console-window flicker
                if result.returncode:
                    trouble = _join_trouble(trouble, 'taskkill:exit%d' % result.returncode)
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as exc:
                trouble = _join_trouble(trouble, 'taskkill:%s' % type(exc).__name__)
    else:
        import signal as _signal
        try:
            os.killpg(os.getpgid(proc.pid), _signal.SIGKILL)
        except (ProcessLookupError, PermissionError, OSError) as exc:
            trouble = _join_trouble(trouble, 'killpg:%s' % type(exc).__name__)
    if proc.poll() is None:                            # always fall back if the parent still lives
        try:
            proc.kill()
        except OSError as exc:
            trouble = _join_trouble(trouble, 'proc.kill:%s' % type(exc).__name__)
    return trouble


# H2878 (issue #1680, FINDINGS §378) -- the no-output-progress watchdog.
#
# The stdlib path below (`proc.communicate(timeout=)`) can only answer ONE question: has the
# call exceeded its total wall budget? That is the question `PRODUCTION_HARD_TIMEOUT_MS`
# already answers, and H2313 established it cannot separate a hung route from a slow one --
# 300 000 ms sat below p90 of the COMPLETED spawn distribution, so it was manufacturing
# failures on the healthy tail. Raising it to 600 000 ms stopped that, and bought no ability
# to detect a hang at all: a spawn that dies silently at second 3 is now held for ten minutes.
#
# These helpers answer the other question: how long has this spawn produced NOTHING? That is
# a liveness signal, it is orthogonal to total elapsed time, and it is what makes a kill
# readable after the fact (`killed_reason=no_output_progress` vs `hard_timeout`).
#
# WHY BINARY PIPES. Progress has to be observed at BYTE granularity. A text-mode
# `TextIOWrapper.read(n)` blocks until n characters or EOF and `readline()` blocks until a
# newline, so under either one a spawn dribbling bytes without newlines is indistinguishable
# from a dead one. `os.read` on the raw fd returns as soon as ANY bytes are available, so the
# progress path opens the pipes in binary and decodes once at the end, with the caller's own
# `encoding`. The classic path is untouched and still used whenever no progress observation
# was asked for.

_PROGRESS_POLL_SECONDS = 0.05


def _drain_pipe(stream, chunks, state, lock, is_result):
    """Read one pipe to EOF, recording byte arrivals as progress.

    Only RESULT bytes (stdout) reset the quiet window. Stderr is counted separately and
    deliberately does NOT count as progress: a CLI retrying internally against a locked
    account chatters on stderr while producing no result at all (FINDINGS §270), and treating
    that chatter as liveness would make the watchdog blind to the one hang it most needs to
    see. The stderr count is still recorded, so a reading can say which pipe was alive.
    """
    fd = stream.fileno()
    try:
        while True:
            block = os.read(fd, 65536)
            if not block:
                break
            with lock:
                chunks.append(block)
                if is_result:
                    state['bytes_seen'] += len(block)
                    state['last_progress'] = time.monotonic()
                else:
                    state['stderr_bytes_seen'] += len(block)
    except (OSError, ValueError):
        # The pipe is closed under us when the tree is killed. That is the normal end of
        # this thread, not a fault: whatever was drained before the kill is kept.
        pass


def _feed_stdin(proc, payload):
    """Write the prompt and close stdin, in a thread, so a full pipe cannot deadlock the poll
    loop. A child killed mid-write breaks the pipe; that is expected, never fatal here."""
    try:
        if payload:
            proc.stdin.write(payload)
        proc.stdin.close()
    except (OSError, ValueError):
        pass


def _communicate_with_progress(proc, payload, timeout, window_s, state):
    """`communicate` with a stalled-output watchdog. Returns (stdout_bytes, stderr_bytes).

    Raises ``subprocess.TimeoutExpired`` carrying ``killed_reason`` / ``bytes_seen`` /
    ``quiet_ms`` when either bound fires. The caller performs the tree kill -- this function
    only decides, and never leaves the decision implicit.
    """
    lock = threading.Lock()
    out_chunks, err_chunks = [], []
    threads = []
    if proc.stdin is not None:
        threads.append(threading.Thread(target=_feed_stdin, args=(proc, payload), daemon=True))
    if proc.stdout is not None:
        threads.append(threading.Thread(
            target=_drain_pipe, args=(proc.stdout, out_chunks, state, lock, True), daemon=True))
    if proc.stderr is not None:
        threads.append(threading.Thread(
            target=_drain_pipe, args=(proc.stderr, err_chunks, state, lock, False), daemon=True))
    for thread in threads:
        thread.start()
    state['threads'] = threads
    state['out_chunks'] = out_chunks
    state['err_chunks'] = err_chunks
    state['lock'] = lock

    def _snapshot():
        now = time.monotonic()
        with lock:
            quiet = now - state['last_progress']
            if quiet > state['quiet_s']:
                state['quiet_s'] = quiet          # LONGEST silence, not the trailing one
            return now, quiet, state['bytes_seen']

    while True:
        returncode = proc.poll()
        now, quiet, _seen = _snapshot()
        if returncode is not None:
            break
        if timeout is not None and now - state['start'] >= timeout:
            state['killed_reason'] = KILLED_REASON_HARD_TIMEOUT
            raise subprocess.TimeoutExpired(proc.args, timeout)
        if window_s is not None and quiet >= window_s:
            # The whole point of the unit: this is a kill on STALLED OUTPUT, and the
            # exception carries the window that fired -- not the total-wall ceiling, which
            # this spawn never reached and which would misreport the cause.
            state['killed_reason'] = KILLED_REASON_NO_OUTPUT_PROGRESS
            raise subprocess.TimeoutExpired(proc.args, window_s)
        time.sleep(_PROGRESS_POLL_SECONDS)

    # Exited on its own. Join the readers so nothing the child wrote just before exit is lost.
    for thread in threads:
        thread.join(timeout=10.0)
    _snapshot()
    with lock:
        return b''.join(out_chunks), b''.join(err_chunks)


def _progress_state():
    start = time.monotonic()
    return {'start': start, 'last_progress': start, 'bytes_seen': 0,
            'stderr_bytes_seen': 0, 'quiet_s': 0.0, 'killed_reason': None}


def _publish_progress(state, progress_out):
    """Copy the bounded reading into the caller's dict. Five scalars, no payload."""
    if progress_out is None:
        return
    progress_out['bytes_seen'] = state['bytes_seen']
    progress_out['stderr_bytes_seen'] = state['stderr_bytes_seen']
    progress_out['quiet_ms'] = int(state['quiet_s'] * 1000)
    progress_out['killed_reason'] = state['killed_reason']
    progress_out['elapsed_ms'] = int((time.monotonic() - state['start']) * 1000)


def run_tree_kill(argv, input=None, timeout=None, text=True, encoding='utf-8',
                  capture_output=False, cwd=None, env=None, progress_window_ms=None,
                  progress_out=None, **_ignored):
    """Drop-in for ``subprocess.run`` (Popen + ``communicate(timeout=)``) that, on timeout,
    performs bounded best-effort termination of the ENTIRE process tree instead of just the
    immediate child — so a killed call is bounded and no orphaned native binary keeps holding the
    API call (H818 defect D-J). Terminates the tree while the parent is still alive, then drains
    the pipes and reaps the parent using the REMAINING kill budget to an absolute deadline (a small
    grace beyond the call budget, not an independent fixed window). Cleanup trouble is attached
    diagnostically to the raised ``subprocess.TimeoutExpired`` — the caller still records exactly
    one ``timeout`` event.

    H2878: ``progress_window_ms`` and ``progress_out`` select the no-output-progress path.

    * ``progress_out`` (a dict) alone is OBSERVE ONLY -- the spawn is bounded exactly as
      before, and the dict comes back holding ``bytes_seen`` / ``stderr_bytes_seen`` /
      ``quiet_ms`` (the LONGEST stretch with no result bytes) / ``elapsed_ms`` /
      ``killed_reason``. This is how a lane learns whether a window would be safe to arm
      before arming one, which is the difference between a reading and a guess.
    * ``progress_window_ms`` additionally ARMS the watchdog: a spawn silent for that long is
      killed with ``killed_reason=no_output_progress``, distinct from the total-wall
      ``hard_timeout``. Both are attached to the raised ``TimeoutExpired`` alongside
      ``bytes_seen`` and ``quiet_ms``, so every caller's existing ``except TimeoutExpired``
      still fires and simply has more to say.

    Both require ``capture_output`` -- there are no pipes to watch otherwise, so the request
    degrades to the classic path rather than pretending to observe something.
    """
    pipe = subprocess.PIPE if capture_output else None
    # H2878: the watchdog needs byte-granular arrivals, which only raw binary pipes give
    # (see the helpers above). Without capture_output there is nothing to watch, so the
    # request degrades to the classic path instead of silently observing nothing.
    watching = capture_output and (progress_window_ms is not None or progress_out is not None)
    popen_kw = dict(stdin=subprocess.PIPE, stdout=pipe, stderr=pipe,
                    text=(False if watching else text),
                    encoding=(None if watching else encoding), cwd=cwd, env=env)
    job = None
    setup_trouble = None
    if os.name == 'nt':
        creationflags = getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0)
        job = _WindowsKillJob()
        try:
            job.create()
            creationflags |= _CREATE_SUSPENDED
        except OSError as exc:
            setup_trouble = 'job-create:%s' % type(exc).__name__
            job = None
        popen_kw['creationflags'] = creationflags
    else:
        popen_kw['start_new_session'] = True          # own process group -> killpg reaches children
    try:
        proc = subprocess.Popen(argv, **popen_kw)
    except BaseException:
        if job is not None:
            job.close()
        raise
    proc._tree_job = job
    proc._tree_setup_trouble = setup_trouble
    if job is not None:
        try:
            job.assign(proc)
        except OSError as exc:
            # Resume even if assignment failed, otherwise the fallback would target a suspended
            # process forever. With no assigned process the job is empty and safe to close.
            setup_trouble = 'job-assign:%s' % type(exc).__name__
            try:
                job.resume(proc)
            except OSError as resume_exc:
                setup_trouble += ':resume-%s' % type(resume_exc).__name__
                setup_trouble = _join_trouble(setup_trouble, job.terminate())
                try:
                    proc.kill()
                    proc.wait(timeout=2)
                except (OSError, subprocess.TimeoutExpired):
                    pass
                raise OSError('Windows Job Object setup failed: %s' % setup_trouble) from exc
            setup_trouble = _join_trouble(setup_trouble, job.close())
            proc._tree_job = None
            proc._tree_setup_trouble = setup_trouble
        else:
            try:
                job.resume(proc)
            except OSError as exc:
                setup_trouble = _join_trouble(
                    'job-resume:%s' % type(exc).__name__, job.terminate())
                try:
                    proc.kill()
                    proc.wait(timeout=2)
                except (OSError, subprocess.TimeoutExpired):
                    pass
                raise OSError('Windows Job Object setup failed: %s' % setup_trouble) from exc
    if watching:
        return _run_watched(proc, argv, input, timeout, encoding, text,
                            progress_window_ms, progress_out)
    start = time.monotonic()
    try:
        out, err = proc.communicate(input=input, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        grace = min(10.0, (timeout or 0) * 0.1 + 2.0)  # small, proportional, capped cleanup grace
        deadline = start + (timeout or 0) + grace
        trouble = terminate_tree(proc, deadline)
        out = err = None
        try:
            remaining = max(0.5, deadline - time.monotonic())
            out, err = proc.communicate(timeout=remaining)     # drain pipes + reap within budget
        except subprocess.TimeoutExpired:
            trouble = (trouble or '') + ';reap-timeout'
            try:
                proc.kill()
                out, err = proc.communicate(timeout=2)
            except (OSError, subprocess.TimeoutExpired):
                pass
        if trouble:
            exc.cleanup_trouble = trouble              # diagnostic only; cleanup, not classification
        # H2056 / #943: the text drained above is the ONLY copy of what the killed child said that
        # ever reaches this process — and a rate-limited Claude CLI does not exit with a 429, it
        # retries internally until our wall ceiling kills it (Uprava FINDINGS §270). Dropping `out`
        # and `err` here is what forced every caller to hardcode 'timeout': they had nothing left to
        # classify. Attach them so the CAUSE survives the kill. `.output`/`.stdout` are the same
        # slot on TimeoutExpired (`.stdout` is a property alias), and coordinator.py already reads
        # both. This is diagnostic payload only — it does not itself change any classification.
        if out is not None:
            exc.output = out
        if err is not None:
            exc.stderr = err
        raise
    except BaseException as exc:
        # communicate() can also fail while the child is live (decode error, pipe/OSError,
        # injected test exception, cancellation). Never abandon that process tree merely because
        # the primary failure was not TimeoutExpired.
        deadline = time.monotonic() + 10.0
        trouble = terminate_tree(proc, deadline)
        try:
            proc.communicate(timeout=max(0.5, deadline - time.monotonic()))
        except BaseException as reap_exc:
            trouble = _join_trouble(
                trouble, 'exception-reap:%s' % type(reap_exc).__name__)
            try:
                proc.kill()
                proc.wait(timeout=2)
            except (OSError, subprocess.TimeoutExpired):
                pass
        if trouble:
            exc.cleanup_trouble = trouble
        raise
    finally:
        if proc.poll() is not None and getattr(proc, '_tree_job', None) is not None:
            proc._tree_job.close()
    return subprocess.CompletedProcess(argv, proc.returncode, out, err)


def _run_watched(proc, argv, payload, timeout, encoding, text, progress_window_ms, progress_out):
    """The H2878 progress-watched half of ``run_tree_kill``, split out so the classic path
    above stays byte-for-byte what it was. Same contract, same tree-kill, same bounded drain;
    the only additions are the stalled-output bound and the reading it produces."""
    codec = encoding or 'utf-8'
    if payload is not None and isinstance(payload, str):
        payload = payload.encode(codec)
    window_s = None if progress_window_ms is None else progress_window_ms / 1000.0
    state = _progress_state()
    try:
        try:
            out, err = _communicate_with_progress(proc, payload, timeout, window_s, state)
        except subprocess.TimeoutExpired as exc:
            # Identical bounded-cleanup shape to the classic path: terminate the TREE while the
            # parent still lives, then reap within a small proportional grace. The budget is
            # taken from the bound that actually fired, so a 90 s progress kill is not given a
            # ten-minute cleanup window derived from a ceiling it never reached.
            fired_s = exc.timeout or 0
            grace = min(10.0, fired_s * 0.1 + 2.0)
            deadline = time.monotonic() + grace
            trouble = terminate_tree(proc, deadline)
            for thread in state.get('threads') or []:
                thread.join(timeout=max(0.5, deadline - time.monotonic()))
            try:
                proc.wait(timeout=max(0.5, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                trouble = (trouble or '') + ';reap-timeout'
                try:
                    proc.kill()
                    proc.wait(timeout=2)
                except (OSError, subprocess.TimeoutExpired):
                    pass
            lock = state.get('lock')
            with lock:
                out = b''.join(state.get('out_chunks') or [])
                err = b''.join(state.get('err_chunks') or [])
            if trouble:
                exc.cleanup_trouble = trouble
            # H2056 / #943: the drained text is the ONLY copy of what the killed child said,
            # and a rate-limited CLI says it there rather than exiting 429. Same slots as the
            # classic path, so `timeout_output_text` / `classify_timeout` read a progress kill
            # exactly as they read a wall kill.
            exc.output = out.decode(codec, 'replace')
            exc.stderr = err.decode(codec, 'replace')
            # The three fields the unit exists to produce. `killed_reason` is what separates a
            # hung route from a call the production lane would still have been waiting on.
            exc.killed_reason = state['killed_reason']
            exc.bytes_seen = state['bytes_seen']
            exc.stderr_bytes_seen = state['stderr_bytes_seen']
            exc.quiet_ms = int(state['quiet_s'] * 1000)
            _publish_progress(state, progress_out)
            raise
        except BaseException as exc:
            deadline = time.monotonic() + 10.0
            trouble = terminate_tree(proc, deadline)
            for thread in state.get('threads') or []:
                thread.join(timeout=max(0.5, deadline - time.monotonic()))
            try:
                proc.wait(timeout=max(0.5, deadline - time.monotonic()))
            except BaseException as reap_exc:
                trouble = _join_trouble(trouble, 'exception-reap:%s' % type(reap_exc).__name__)
                try:
                    proc.kill()
                    proc.wait(timeout=2)
                except (OSError, subprocess.TimeoutExpired):
                    pass
            if trouble:
                exc.cleanup_trouble = trouble
            _publish_progress(state, progress_out)
            raise
    finally:
        if proc.poll() is not None and getattr(proc, '_tree_job', None) is not None:
            proc._tree_job.close()
    _publish_progress(state, progress_out)
    if text:
        out = out.decode(codec)
        err = err.decode(codec)
    return subprocess.CompletedProcess(argv, proc.returncode, out, err)
