"""Machine-state capture taken BESIDE every paid probe reading.

Why this exists (H2647, 13-08-2026). The h963 gate-0 series records latency, output
bytes and a classification -- everything about the *account and route* -- and nothing
about the box the CLI runs on. So a reading cannot distinguish its subject from its
environment. That is not hypothetical: a c1 probe on 13-08 at 22:54:58Z died in 7 754 ms
with ``output_bytes`` 0 and the envelope

    ASSERTION FAILED: MemoryExhaustion: Crash intentionally because memory is exhausted.
    /webkit/Source/JavaScriptCore/heap/LocalAllocator.cpp(150)

-- the JavaScriptCore heap failing to allocate in a fresh Node process. Measured on the
same box seconds later: 1.73 GB free of 15.85 GB, and commit charge **62.07 of 63.85 GB
(97 %)** with 90 python processes holding 29.51 GB of it. Nothing about that reading is
evidence about c1, but the series had no field in which to say so, and the earlier 0-byte
kill at 300 198 ms had already been read as account capacity with local starvation never
on the list of candidates.

Design rules, each paid for by something in this file's history:

1. **Never raise, never block.** Every entry point is wrapped; a capture failure returns
   ``None`` fields. Telemetry that can abort a paid call is worse than no telemetry.
2. **Never spawn, never spend time.** Both figures come from ctypes calls into kernel32
   (microseconds, no child process). This is not merely an optimisation: the first cut
   counted processes with ``tasklist``, and on a 99.4 %-commit box ``tasklist`` itself
   exits **82, "Out of memory"** -- the counter fails in the one condition worth counting.
3. **Prefix every field ``host_``.** A reader scanning a row must never mistake an
   environment fact for a subject fact -- that confusion is the whole defect.
4. **Report what was measured, not a verdict.** ``loaded_reason()`` returns a human
   string for a caller that wants to gate; this module never gates anything itself.
"""
import ctypes
import sys

# Provisional, from the single measured crash above: the CLI died at 97 % commit with
# 1.73 GB free. These are the thresholds a CALLER may choose to act on -- deliberately
# not enforced here (see rule 4). They are not a fitted model; one crash is one point.
COMMIT_PCT_WARN = 95.0
AVAIL_PHYS_MB_WARN = 1024


_TH32CS_SNAPPROCESS = 0x00000002
_INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
_MAX_PATH = 260


class _ProcessEntry32W(ctypes.Structure):
    _fields_ = [
        ('dwSize', ctypes.c_ulong),
        ('cntUsage', ctypes.c_ulong),
        ('th32ProcessID', ctypes.c_ulong),
        ('th32DefaultHeapID', ctypes.POINTER(ctypes.c_ulong)),
        ('th32ModuleID', ctypes.c_ulong),
        ('cntThreads', ctypes.c_ulong),
        ('th32ParentProcessID', ctypes.c_ulong),
        ('pcPriClassBase', ctypes.c_long),
        ('dwFlags', ctypes.c_ulong),
        ('szExeFile', ctypes.c_wchar * _MAX_PATH),
    ]


class _MemoryStatusEx(ctypes.Structure):
    _fields_ = [
        ('dwLength', ctypes.c_ulong),
        ('dwMemoryLoad', ctypes.c_ulong),
        ('ullTotalPhys', ctypes.c_ulonglong),
        ('ullAvailPhys', ctypes.c_ulonglong),
        ('ullTotalPageFile', ctypes.c_ulonglong),
        ('ullAvailPageFile', ctypes.c_ulonglong),
        ('ullTotalVirtual', ctypes.c_ulonglong),
        ('ullAvailVirtual', ctypes.c_ulonglong),
        ('ullAvailExtendedVirtual', ctypes.c_ulonglong),
    ]


def _mb(value):
    return int(value / (1024 * 1024))


def memory_state():
    """Physical + commit figures, or all-``None`` when they cannot be read.

    ``TotalPageFile``/``AvailPageFile`` are the **commit limit and its free remainder**,
    not a pagefile size -- that naming is a Win32 wart worth stating, because commit
    exhaustion (not low physical RAM) is what refuses a new JS heap.
    """
    blank = dict(host_total_phys_mb=None, host_avail_phys_mb=None,
                 host_commit_limit_mb=None, host_commit_used_mb=None,
                 host_commit_pct=None, host_memory_load_pct=None)
    if not sys.platform.startswith('win'):
        return blank
    try:
        stat = _MemoryStatusEx()
        stat.dwLength = ctypes.sizeof(_MemoryStatusEx)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
            return blank
        commit_limit = stat.ullTotalPageFile
        commit_used = commit_limit - stat.ullAvailPageFile
        pct = round(100.0 * commit_used / commit_limit, 2) if commit_limit else None
        return dict(
            host_total_phys_mb=_mb(stat.ullTotalPhys),
            host_avail_phys_mb=_mb(stat.ullAvailPhys),
            host_commit_limit_mb=_mb(commit_limit),
            host_commit_used_mb=_mb(commit_used),
            host_commit_pct=pct,
            host_memory_load_pct=int(stat.dwMemoryLoad),
        )
    except Exception:                      # noqa: BLE001 -- rule 1, never raise
        return blank


def process_counts():
    """Counts of the processes that actually compete for this box, or ``None``s.

    ``node`` is the CLI's own runtime and ``python`` is every pipeline worker; both were
    load-bearing in the 13-08 crash (18 node/claude, 90 python).

    **Deliberately does NOT shell out to ``tasklist``.** The first version did, and it was
    measured failing in exactly the condition this field exists to record: with commit at
    99.4 %, ``tasklist /FO CSV /NH`` exits **82, "Out of memory"** -- the box could not
    spawn the counter. A metric that goes blank precisely at the crisis it documents is
    worse than none, because its absence is indistinguishable from a healthy skip. So the
    count is taken **in-process** via a Toolhelp32 snapshot: no spawn, no allocation the
    OS can refuse, and it keeps working while the machine cannot start anything at all.
    """
    blank = dict(host_proc_node=None, host_proc_python=None)
    if not sys.platform.startswith('win'):
        return blank
    snapshot = None
    try:
        kernel32 = ctypes.windll.kernel32
        snapshot = kernel32.CreateToolhelp32Snapshot(_TH32CS_SNAPPROCESS, 0)
        if snapshot == _INVALID_HANDLE_VALUE:
            return blank
        entry = _ProcessEntry32W()
        entry.dwSize = ctypes.sizeof(_ProcessEntry32W)
        node = python = 0
        ok = kernel32.Process32FirstW(snapshot, ctypes.byref(entry))
        while ok:
            name = (entry.szExeFile or '').lower()
            if name in ('node.exe', 'claude.exe'):
                node += 1
            elif name in ('python.exe', 'pythonw.exe'):
                python += 1
            ok = kernel32.Process32NextW(snapshot, ctypes.byref(entry))
        return dict(host_proc_node=node, host_proc_python=python)
    except Exception:                      # noqa: BLE001 -- rule 1, never raise
        return blank
    finally:
        if snapshot is not None and snapshot != _INVALID_HANDLE_VALUE:
            try:
                ctypes.windll.kernel32.CloseHandle(snapshot)
            except Exception:              # noqa: BLE001
                pass


def capture(counts=True):
    """The full ``host_*`` field set for one telemetry row. Never raises."""
    state = memory_state()
    if counts:
        state.update(process_counts())
    else:
        state.update(host_proc_node=None, host_proc_python=None)
    return state


def loaded_reason(state=None,
                  commit_pct_warn=COMMIT_PCT_WARN,
                  avail_phys_mb_warn=AVAIL_PHYS_MB_WARN):
    """A human string when the box looks too loaded to trust a reading, else ``None``.

    Advisory by construction: returning a string is the whole effect. Whether that is
    worth refusing a paid attempt over is the caller's judgment, and differs between an
    operator watching a terminal and an unattended scheduled run.
    """
    state = capture() if state is None else state
    pct = state.get('host_commit_pct')
    avail = state.get('host_avail_phys_mb')
    reasons = []
    if pct is not None and pct >= commit_pct_warn:
        reasons.append('commit charge %.1f%% >= %.1f%%' % (pct, commit_pct_warn))
    if avail is not None and avail < avail_phys_mb_warn:
        reasons.append('%d MB physical free < %d MB' % (avail, avail_phys_mb_warn))
    if not reasons:
        return None
    return '; '.join(reasons)


def format_line(state=None):
    """One compact human line for probe stdout."""
    state = capture() if state is None else state
    if state.get('host_commit_pct') is None:
        return 'host state       : unavailable'
    return ('host state        : %d MB free of %d MB phys · commit %d/%d MB (%.1f%%) · '
            'node+claude %s · python %s'
            % (state.get('host_avail_phys_mb') or -1,
               state.get('host_total_phys_mb') or -1,
               state.get('host_commit_used_mb') or -1,
               state.get('host_commit_limit_mb') or -1,
               state.get('host_commit_pct'),
               state.get('host_proc_node'), state.get('host_proc_python')))


def selftest():
    """No live call, nothing spent."""
    checks = 0
    state = capture()
    expected = {'host_total_phys_mb', 'host_avail_phys_mb', 'host_commit_limit_mb',
                'host_commit_used_mb', 'host_commit_pct', 'host_memory_load_pct',
                'host_proc_node', 'host_proc_python'}
    assert set(state) == expected, sorted(set(state) ^ expected)
    checks += 1

    assert all(k.startswith('host_') for k in state), 'rule 3: every field is host_-prefixed'
    checks += 1

    if sys.platform.startswith('win'):
        assert state['host_total_phys_mb'] > 0, state
        assert 0 <= state['host_commit_pct'] <= 100, state
        assert state['host_commit_used_mb'] <= state['host_commit_limit_mb'], state
        checks += 1

    # counts=False must still return the full key set (append_event drops the Nones).
    lean = capture(counts=False)
    assert set(lean) == expected and lean['host_proc_node'] is None, lean
    checks += 1

    # A synthetic exhausted box trips the advisory; a healthy one does not.
    loaded = dict(host_commit_pct=97.0, host_avail_phys_mb=300)
    assert loaded_reason(loaded) and 'commit charge' in loaded_reason(loaded)
    assert loaded_reason(dict(host_commit_pct=40.0, host_avail_phys_mb=8000)) is None
    checks += 1

    # Unmeasurable state must NOT read as loaded -- fail-open, or a capture failure
    # silently becomes a refusal reason on every caller that gates on it.
    assert loaded_reason(dict(host_commit_pct=None, host_avail_phys_mb=None)) is None
    checks += 1

    assert isinstance(format_line(state), str) and format_line(state)
    checks += 1

    print('host_state selftest: %d/%d OK (no live call, nothing spent)' % (checks, checks))
    print('  ' + format_line(state))
    return 0


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    raise SystemExit(selftest())
