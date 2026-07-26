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
import time

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


def run_tree_kill(argv, input=None, timeout=None, text=True, encoding='utf-8',
                  capture_output=False, cwd=None, env=None, **_ignored):
    """Drop-in for ``subprocess.run`` (Popen + ``communicate(timeout=)``) that, on timeout,
    performs bounded best-effort termination of the ENTIRE process tree instead of just the
    immediate child — so a killed call is bounded and no orphaned native binary keeps holding the
    API call (H818 defect D-J). Terminates the tree while the parent is still alive, then drains
    the pipes and reaps the parent using the REMAINING kill budget to an absolute deadline (a small
    grace beyond the call budget, not an independent fixed window). Cleanup trouble is attached
    diagnostically to the raised ``subprocess.TimeoutExpired`` — the caller still records exactly
    one ``timeout`` event."""
    pipe = subprocess.PIPE if capture_output else None
    popen_kw = dict(stdin=subprocess.PIPE, stdout=pipe, stderr=pipe,
                    text=text, encoding=encoding, cwd=cwd, env=env)
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
    start = time.monotonic()
    try:
        out, err = proc.communicate(input=input, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        grace = min(10.0, (timeout or 0) * 0.1 + 2.0)  # small, proportional, capped cleanup grace
        deadline = start + (timeout or 0) + grace
        trouble = terminate_tree(proc, deadline)
        try:
            remaining = max(0.5, deadline - time.monotonic())
            out, err = proc.communicate(timeout=remaining)     # drain pipes + reap within budget
        except subprocess.TimeoutExpired:
            trouble = (trouble or '') + ';reap-timeout'
            try:
                proc.kill()
                proc.communicate(timeout=2)
            except (OSError, subprocess.TimeoutExpired):
                pass
        if trouble:
            exc.cleanup_trouble = trouble              # diagnostic only; classification stays 'timeout'
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
