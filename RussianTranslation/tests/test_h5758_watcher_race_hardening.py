"""H5758 — watcher-race hardening failure-injection tests.

Two production surfaces lost work to the repo-watcher tmp/staging-file race:

  * ``synth_dispatch.Dispatcher`` — the run() poll loop caught only
    RuntimeError, and the confirm-time re-land RE-READ the staging file from
    disk; a watcher wipe between confirmations let FileNotFoundError escape
    run(), crashing the dispatcher and orphaning every concurrently running
    worker (commit de665b179 24h-risk review, failure mode #4).
  * ``pilot/cloud_window.run_cloud_window`` — the wf_output tmp + os.replace
    land had no retry; the same watcher race lost a completed PAID window's
    in-memory-only results.

These tests inject exactly those wipes and pin the recovery: re-land from
MEMORY, OSError caught in the poll loop (redispatch, never a crash), bounded
retry around the replace, log-and-keep-going on persistent failure.
"""
import io
import json
import os
import subprocess
import sys
import threading
import time

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, 'src')
PILOT = os.path.join(SRC, 'pilot')
for p in (SRC, PILOT):
    if p not in sys.path:
        sys.path.insert(0, p)

import synth_dispatch
import cloud_window


# ---------------------------------------------------------------- helpers

def _registered_attempt(d, job, n=1, payload="memory payload <ls>R. 1, 2</ls>\n"):
    """An attempt whose worker already exited 0, registered as the job's single
    live owner — queue drained and the attempts counter reconciled so run()
    continues from this attempt instead of _start() displacing it."""
    att = synth_dispatch.Attempt(job, n, subprocess.Popen([sys.executable, "-c", "pass"]),
                                 os.path.join(d.staging_dir, f"{job.key}.attempt{n}.out"))
    att.proc.wait()
    d.running[job.key] = att
    job.state = "running"
    job.attempts = n
    d.queue.clear()
    io.open(att.staging, "w", encoding="utf-8").write(payload)
    return att


def _make_dispatcher(tmp, key="k1", **kw):
    job = synth_dispatch.Job(key, "-", os.path.join(tmp, f"{key}.final.txt"))
    kw.setdefault("poll_s", 0.05)
    kw.setdefault("stagger_s", 0)
    kw.setdefault("land_recheck_s", 0.05)
    d = synth_dispatch.Dispatcher([job], [sys.executable, "-c", "pass"],
                                  os.path.join(tmp, "staging"), **kw)
    return d, job


# ------------------------------------------------- synth_dispatch: memory re-land

def test_confirm_relands_from_memory_after_staging_wipe(tmp_path):
    """Staging AND final wiped between confirmations: the re-land must come
    from memory — the old code re-read the wiped staging file and let
    FileNotFoundError escape (crash + orphaned workers)."""
    d, job = _make_dispatcher(str(tmp_path))
    att = _registered_attempt(d, job)
    assert d._maybe_land(att) is None            # first land started
    assert att.land_text is not None             # text held from the FIRST read
    os.remove(att.staging)                       # the watcher wipe: staging AND
    os.remove(job.final_path)                    # final, between confirmations
    time.sleep(0.06)
    assert d._confirm_landing(att) is False      # re-landed (not yet confirmed)
    assert not os.path.exists(att.staging)       # proof: no staging re-read
    assert io.open(job.final_path, encoding="utf-8").read() == att.land_text
    time.sleep(0.06)
    assert d._confirm_landing(att) is True
    assert job.state == "landed"


def test_run_survives_watcher_wipe_between_confirmations(tmp_path):
    """Full run() with a live worker subprocess and a watcher thread that
    wipes staging+final once after the first land: run() must survive and
    land the job (old code raised FileNotFoundError out of run())."""
    tmp = str(tmp_path)
    worker = os.path.join(tmp, "worker.py")
    io.open(worker, "w", encoding="utf-8").write(synth_dispatch.FAKE_WORKER)
    job = synth_dispatch.Job("w1", "-", os.path.join(tmp, "w1.final.txt"))
    staging = os.path.join(tmp, "staging")
    d = synth_dispatch.Dispatcher(
        [job], [sys.executable, worker, "good", "{output}", "{attempt}"],
        staging, stagger_s=0, poll_s=0.05, kill_after_s=5, land_recheck_s=0.2)
    final, wiped = job.final_path, threading.Event()

    def watcher():
        while not os.path.exists(final):
            time.sleep(0.005)
        st = os.path.join(staging, "w1.attempt1.out")
        if os.path.exists(st):
            os.remove(st)
        os.remove(final)
        wiped.set()

    t = threading.Thread(target=watcher)
    t.start()
    try:
        states = d.run()                         # OLD code: FileNotFoundError here
    finally:
        t.join(timeout=5)
    assert wiped.is_set()
    assert states == {"w1": "landed"}
    assert any("landing attempts 2" in h for h in job.history)   # re-land fired
    assert io.open(final, encoding="utf-8").read().startswith("chunk 0")


def test_poll_loop_catches_oserror_and_redispatches(tmp_path, monkeypatch):
    """OSError surfacing at confirm-time re-land (e.g. the wiped outdir) is
    caught by the poll loop and redispatched — never a run() crash."""
    d, job = _make_dispatcher(str(tmp_path))
    att = _registered_attempt(d, job)
    real = synth_dispatch.land_atomic
    calls = {"n": 0}

    def flaky_land(text, final_path):
        calls["n"] += 1
        if calls["n"] == 2:                      # the confirm-time re-land
            raise FileNotFoundError("watcher wiped the landing tmp")
        return real(text, final_path)

    monkeypatch.setattr(synth_dispatch, "land_atomic", flaky_land)
    assert d._maybe_land(att) is None
    os.remove(job.final_path)                    # force the re-land path
    time.sleep(0.06)
    states = d.run()                             # OLD code: crash on OSError
    assert states == {"k1": "failed"}            # redispatched, then failed cleanly
    assert job.attempts == 2
    assert calls["n"] == 2
    assert any("watcher wiped the landing tmp" in h for h in job.history)


def test_maybe_land_wiped_staging_redispatches_via_run(tmp_path, monkeypatch):
    """Staging wiped between _maybe_land's exists-check and its first read:
    the OSError is converted to a redispatch, run() survives."""
    d, job = _make_dispatcher(str(tmp_path))
    att = synth_dispatch.Attempt(job, 1,
                                 subprocess.Popen([sys.executable, "-c", "pass"]),
                                 os.path.join(d.staging_dir, "k1.attempt1.out"))
    att.proc.wait()
    d.running[job.key] = att
    job.state = "running"
    io.open(att.staging, "w", encoding="utf-8").write("payload\n")
    d.running[job.key] = att
    job.state = "running"
    job.attempts = 1
    d.queue.clear()

    real_io_open = io.open

    def wiping_open(f, *a, **kw):
        if str(f) == att.staging:                # the TOCTOU read of staging
            if os.path.exists(att.staging):
                os.remove(att.staging)
            raise FileNotFoundError(str(f))
        return real_io_open(f, *a, **kw)

    monkeypatch.setattr(io, "open", wiping_open)  # synth_dispatch reads via io.open
    states = d.run()                             # OLD code: crash in _maybe_land
    assert states == {"k1": "failed"}            # redispatch ran, no output -> failed
    assert any("staging unreadable/vanished before first land" in h
               for h in job.history)


def test_run_survives_non_utf8_staging(tmp_path):
    """Verifier residual (H5758 follow-up): a worker that wrote non-UTF-8
    bytes makes _maybe_land's read raise UnicodeDecodeError (a ValueError,
    NOT an OSError) — run() must redispatch, not crash."""
    d, job = _make_dispatcher(str(tmp_path))
    att = synth_dispatch.Attempt(job, 1,
                                 subprocess.Popen([sys.executable, "-c", "pass"]),
                                 os.path.join(d.staging_dir, "k1.attempt1.out"))
    att.proc.wait()
    d.running[job.key] = att
    job.state = "running"
    job.attempts = 1
    d.queue.clear()
    with open(att.staging, "wb") as f:           # malformed worker output
        f.write(b"\xff\xfe halb\xfc GARBLE \x81\x82")
    states = d.run()                             # OLD code: crash on decode
    assert states == {"k1": "failed"}            # redispatch ran, then failed cleanly
    assert job.attempts == 2
    assert any("staging unreadable/vanished" in h and "codec can't decode" in h
               for h in job.history)


# ------------------------------------------------- cloud_window: land retry

def _fake_translate(item):
    card = {'iast': 'aṃśa', 'records': [
        {'h': item['key'], 'grammar': 'm',
         'senses': [{'tag': 's1', 'german': 'Teil', 'russian': 'часть'}]}]}
    usage = {'input_tokens': 10, 'output_tokens': 5,
             'cache_creation_input_tokens': 0, 'cache_read_input_tokens': 0,
             'observed_cost_usd': 0.001}
    return card, usage


def test_cloud_window_retries_tmp_removal(tmp_path, monkeypatch, capsys):
    """The watcher wipes the tmp between write and os.replace: the bounded
    retry re-writes and lands the paid window's output."""
    monkeypatch.setattr(cloud_window, "WF_LAND_SLEEP_S", 0.0)
    real_replace = os.replace
    calls = {"n": 0}

    def wiping_replace(src, dst):
        calls["n"] += 1
        if calls["n"] == 1:                      # the watcher wipe — once
            if os.path.exists(src):
                os.remove(src)
            raise FileNotFoundError(str(src))
        return real_replace(src, dst)

    monkeypatch.setattr(os, "replace", wiping_replace)
    wf, rows, parked = cloud_window.run_cloud_window(
        'cw_retry', [{'key': 'r~~x'}], _fake_translate, model_identifier='m',
        out_dir=str(tmp_path),
        parked_env={'PWG_PARKED_DIR': str(tmp_path / 'parked')})
    assert calls["n"] >= 2                       # the retry actually fired
    assert os.path.exists(wf['_wf_path'])        # landed on the second attempt
    with open(wf['_wf_path'], encoding='utf-8') as f:
        assert json.load(f)['results'][0]['key'] == 'r~~x'
    assert 'attempt 1/3' in capsys.readouterr().err


def test_cloud_window_persistent_land_failure_keeps_going(tmp_path, monkeypatch, capsys):
    """A persistent wipe exhausts the retry: the window's results are NOT
    lost (kept in memory), no lying _wf_path is set, the log says so, and
    the usage ledger still lands."""
    monkeypatch.setattr(cloud_window, "WF_LAND_SLEEP_S", 0.0)

    def failing_replace(src, dst):
        raise FileNotFoundError("watcher keeps wiping " + str(src))

    monkeypatch.setattr(os, "replace", failing_replace)
    wf, rows, parked = cloud_window.run_cloud_window(
        'cw_lost', [{'key': 'r~~y'}], _fake_translate, model_identifier='m',
        out_dir=str(tmp_path),
        parked_env={'PWG_PARKED_DIR': str(tmp_path / 'parked')})
    assert '_wf_path' not in wf                  # never landed — no lying pointer
    assert wf.get('_wf_land_error')              # honest in-memory-only marker
    assert wf['summary']['translated'] == 1      # results NOT lost
    assert wf['results'][0]['key'] == 'r~~y'
    err = capsys.readouterr().err
    assert 'attempt 3/3' in err and 'in-memory only' in err
    assert not os.path.exists(os.path.join(str(tmp_path), 'wf_output.cw_lost.json'))
    assert os.path.exists(wf['_usage_path'])     # ledger append unaffected
