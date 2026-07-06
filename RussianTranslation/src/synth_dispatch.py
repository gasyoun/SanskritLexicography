#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""synth_dispatch.py — dispatch-and-monitor wrapper for the pwg_ru sub-agent
fan-out (H234), codifying the six failure lessons of the 06-07-2026 H180 Arm-B
run (see PIPELINE_HISTORY.md "H234" entry):

  #1 false-stall kill   -> liveness is judged by OUTPUT-FILE growth only; a
                           transcript reading 0 bytes means nothing (they buffer).
  #2 mid-stream stalls  -> concurrency is capped at 3 (hard cap 4) with a
                           stagger between starts; never a 10-wide fan-out.
  #3 34-min silent hang -> every attempt has a wall-clock kill-guard: if its
                           output file has not grown in --kill-after seconds
                           (default 600), the worker is killed.
  #4 watcher wipe       -> workers author in a STAGING dir outside the repo;
                           the wrapper lands the finished text atomically and
                           re-verifies the landed sha after a delay (the
                           /watcher-safe-commit pattern) — never a bare
                           gitignored file the watcher can wipe mid-build.
  #5 zombie overwrite   -> each attempt owns its own staging file and only the
                           CURRENT owner of a job may land; a re-dispatch only
                           happens after the old process is confirmed dead
                           (wait() returned), and a landed job is sealed — any
                           late output for it is discarded, never landed.
  #6 large free-form    -> inputs above --assemble-over <ls> citations
                           (default 800) route to deterministic programmatic
                           assembly (verbatim fragment fusion), not free-form
                           LLM generation.

The wrapper is a deterministic Python driver: it spawns worker SUBPROCESSES
(one per job attempt) from a --worker-cmd template, so every worker is
observable (output file), killable (terminate/kill) and confirmable-dead
(returncode). It never calls a model itself; `assemble` mode is zero-LLM.

Usage:
  python synth_dispatch.py selftest
  python synth_dispatch.py plan     <key1> [...] [--store F] [--assemble-over N]
  python synth_dispatch.py assemble <key1> [...] [--store F] [--outdir D]
  python synth_dispatch.py run      <key1> [...] --worker-cmd "python worker.py {input} {output}"
                                    [--store F] [--indir D] [--outdir D]
                                    [--max-concurrent 3] [--kill-after 600]
                                    [--poll 10] [--stagger 15] [--staging D]

Worker-cmd placeholders: {key} {input} {output} {attempt}. The worker MUST
write its result to {output} (its private staging path) and exit 0 on success.

No model call in this file. All I/O UTF-8 without BOM.
"""
import sys, os, io, json, re, time, shutil, hashlib, tempfile, argparse, shlex
import subprocess, collections

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEF_STORE = os.path.join(HERE, "pwg_ru_translated.jsonl")
DEF_INDIR = os.path.join(ROOT, "pwg_ru", "reglue", "synth_inputs")
DEF_OUTDIR = os.path.join(ROOT, "pwg_ru", "reglue", "synth_outputs")

MAX_CONCURRENT_DEFAULT = 3
HARD_CAP = 4                    # failure #2: never a wide fan-out
KILL_AFTER_S = 600              # failure #3: 10-min output-file kill-guard
POLL_S = 10
STAGGER_S = 15                  # failure #2: staggered starts
MAX_REDISPATCH = 1              # one fresh replacement per job, no thundering herd
ASSEMBLE_OVER_LS = 800          # failure #6: programmatic assembly threshold
LAND_RECHECK_S = 5.0            # failure #4: re-verify landed file vs the watcher
LAND_RETRIES = 3

LS_RE = re.compile(r"<ls\b[^>]*>(.*?)</ls>", re.S)
WS_RE = re.compile(r"\s+")
LAYER_ORDER = ["pwg", "pw", "sch", "pwkvn", "nws"]


def norm_ls(cit):
    return WS_RE.sub(" ", cit).strip().strip(".,;: ")


def ls_multiset(text):
    return collections.Counter(norm_ls(c) for c in LS_RE.findall(text) if norm_ls(c))


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


# ---------------------------------------------------------------- store I/O

def load_store(store_path, keys):
    """key1 -> list of sub-card records (only the requested keys)."""
    want = set(keys)
    by_key = collections.defaultdict(list)
    with io.open(store_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                d = json.loads(line)
                if d.get("key1") in want:
                    by_key[d["key1"]].append(d)
    return by_key


def homonym_of(subcard):
    m = re.search(r"~~(h\d+)", subcard or "")
    return m.group(1) if m else "h0"


def store_ls_count(recs):
    de = " ".join(d.get("de", "") for d in recs)
    return sum(ls_multiset(de).values())


# ------------------------------------------------- failure #6: assembly

def assemble_entry(key1, recs):
    """Deterministic programmatic assembly: fuse ALL layers' German fragments
    verbatim into ONE entry — PWG skeleton first per homonym, supplements in
    layer order after it. Every fragment (hence every <ls> citation) is kept
    byte-for-byte, so fidelity vs the store is 1.0 and hallucination 0 by
    construction. Zero model call."""
    if not recs:
        raise ValueError(f"no store records for {key1}")
    layer_names = {"pwg": "PWG (Gerüst)", "pw": "PW (Ergänzung)",
                   "sch": "SCH (Ergänzung)", "pwkvn": "PWKVN (Ergänzung)",
                   "nws": "NWS (Ergänzung)"}
    by_hom = collections.defaultdict(list)
    for d in recs:
        by_hom[homonym_of(d.get("subcard"))].append(d)
    out = [f"{{#{key1}#}} — fusionierter deutscher Eintrag "
           f"(programmatische Assemblierung H234: alle Schichten, alle Belege verbatim)"]
    for hom in sorted(by_hom):
        if len(by_hom) > 1:
            out.append(f"\n==== {hom} ====")
        frags = by_hom[hom]
        for L in LAYER_ORDER:
            lf = [d for d in frags if d.get("layer") == L]
            if not lf:
                continue
            out.append(f"\n--- {layer_names.get(L, L.upper())} ---")
            for d in sorted(lf, key=lambda x: (str(x.get("subcard")), str(x.get("sense_tag")))):
                out.append(f"[{d.get('sense_tag')}] {d.get('de', '')}")
        # layers outside the known order, if any — never drop a fragment
        other = [d for d in frags if d.get("layer") not in LAYER_ORDER]
        if other:
            out.append("\n--- SONSTIGE ---")
            for d in sorted(other, key=lambda x: (str(x.get("subcard")), str(x.get("sense_tag")))):
                out.append(f"[{d.get('sense_tag')}] {d.get('de', '')}")
    text = "\n".join(out) + "\n"
    # self-check: the fused entry must carry the store's exact <ls> multiset
    src_ms = ls_multiset(" ".join(d.get("de", "") for d in recs))
    if ls_multiset(text) != src_ms:
        raise AssertionError(f"{key1}: assembled <ls> multiset != store multiset")
    return text


# ------------------------------------------------- failure #4: watcher-safe land

def land_watcher_safe(text, final_path, recheck_s=LAND_RECHECK_S,
                      retries=LAND_RETRIES, _post_land_hook=None):
    """Land `text` at final_path the watcher-safe way: atomic replace, sha
    verify, wait, re-verify the file survived (the repo watcher wipes
    untracked files mid-build — failure #4). Returns the number of landing
    attempts used; raises RuntimeError if the file will not stay put."""
    os.makedirs(os.path.dirname(final_path) or ".", exist_ok=True)
    data = text.encode("utf-8")
    want = hashlib.sha256(data).hexdigest()
    for attempt in range(1, retries + 1):
        tmp = final_path + ".landing.tmp"
        with open(tmp, "wb") as fh:
            fh.write(data)
        os.replace(tmp, final_path)
        if sha256_file(final_path) != want:
            continue
        if _post_land_hook:            # selftest hook: simulate a watcher wipe
            _post_land_hook()
            _post_land_hook = None
        time.sleep(recheck_s)
        if os.path.exists(final_path) and sha256_file(final_path) == want:
            return attempt
        log(f"WATCHER wiped/changed {os.path.basename(final_path)} after landing "
            f"(attempt {attempt}/{retries}) — re-landing")
    raise RuntimeError(f"could not keep {final_path} in place after {retries} landings")


# ------------------------------------------------- the dispatcher

class Attempt:
    def __init__(self, job, n, proc, staging):
        self.job, self.n, self.proc, self.staging = job, n, proc, staging
        self.started = time.monotonic()
        self.last_growth = self.started
        self.size = -1

    @property
    def id(self):
        return f"{self.job.key}#a{self.n}"


class Job:
    def __init__(self, key, input_file, final_path):
        self.key, self.input_file, self.final_path = key, input_file, final_path
        self.attempts = 0
        self.state = "pending"      # pending|running|landed|failed
        self.history = []


class Dispatcher:
    """Run jobs as worker subprocesses under the H234 guards."""

    def __init__(self, jobs, worker_cmd, staging_dir,
                 max_concurrent=MAX_CONCURRENT_DEFAULT, kill_after_s=KILL_AFTER_S,
                 poll_s=POLL_S, stagger_s=STAGGER_S, max_redispatch=MAX_REDISPATCH,
                 land_recheck_s=LAND_RECHECK_S):
        if max_concurrent > HARD_CAP:
            raise ValueError(f"max_concurrent {max_concurrent} exceeds the hard cap "
                             f"{HARD_CAP} (H234 failure #2 — never a wide fan-out)")
        self.jobs = {j.key: j for j in jobs}
        self.queue = [j.key for j in jobs]
        self.worker_cmd = worker_cmd
        self.staging_dir = staging_dir
        self.max_concurrent = max_concurrent
        self.kill_after_s = kill_after_s
        self.poll_s = poll_s
        self.stagger_s = stagger_s
        self.max_redispatch = max_redispatch
        self.land_recheck_s = land_recheck_s
        self.running = {}           # key -> Attempt (the single OWNER attempt)
        self.last_start = 0.0
        os.makedirs(staging_dir, exist_ok=True)

    # -- dispatch one attempt (the job's new single owner)
    def _start(self, key):
        job = self.jobs[key]
        job.attempts += 1
        staging = os.path.join(self.staging_dir, f"{key}.attempt{job.attempts}.out")
        if os.path.exists(staging):
            os.remove(staging)
        cmd = [a.format(key=key, input=job.input_file, output=staging,
                        attempt=job.attempts) for a in self.worker_cmd]
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        att = Attempt(job, job.attempts, proc, staging)
        self.running[key] = att
        job.state = "running"
        self.last_start = time.monotonic()
        log(f"START {att.id} pid={proc.pid} -> {os.path.basename(staging)}")
        return att

    # -- failure #1: liveness == output-file growth, nothing else
    def _alive_by_output(self, att):
        try:
            size = os.path.getsize(att.staging)
        except OSError:
            size = -1
        if size > att.size:
            att.size = size
            att.last_growth = time.monotonic()
        return (time.monotonic() - att.last_growth) <= self.kill_after_s

    # -- failure #3/#5: kill and CONFIRM dead (wait() must return)
    def _kill_confirm_dead(self, att):
        proc = att.proc
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()         # blocks until the OS reaps it — confirmed dead
        log(f"KILLED {att.id} (confirmed dead, rc={proc.returncode})")

    # -- failure #5: only the current owner may land; landed jobs are sealed
    def _maybe_land(self, att):
        job = att.job
        owner = self.running.get(job.key)
        if job.state == "landed" or owner is None or owner.id != att.id:
            log(f"ZOMBIE {att.id} discarded — job "
                f"{'already landed' if job.state == 'landed' else 'owned by ' + (owner.id if owner else '?')}")
            return False
        if not (os.path.exists(att.staging) and os.path.getsize(att.staging) > 0):
            return False
        text = io.open(att.staging, encoding="utf-8").read()
        n = land_watcher_safe(text, job.final_path, recheck_s=self.land_recheck_s)
        job.state = "landed"
        job.history.append(f"landed by {att.id} (landing attempts {n})")
        log(f"LANDED {att.id} -> {os.path.basename(job.final_path)} "
            f"({os.path.getsize(job.final_path)} B)")
        return True

    def _fail_or_redispatch(self, att, why):
        job = att.job
        job.history.append(f"{att.id}: {why}")
        del self.running[job.key]
        if job.attempts <= self.max_redispatch:
            log(f"REDISPATCH {job.key} (attempt {job.attempts + 1}) after: {why}")
            self.queue.insert(0, job.key)
            job.state = "pending"
        else:
            job.state = "failed"
            log(f"FAILED {job.key} after {job.attempts} attempts: {why}")

    def run(self):
        while self.queue or self.running:
            # start new attempts under the cap, staggered
            while (self.queue and len(self.running) < self.max_concurrent
                   and (time.monotonic() - self.last_start) >= (self.stagger_s
                        if self.running else 0)):
                self._start(self.queue.pop(0))
            for key in list(self.running):
                att = self.running[key]
                rc = att.proc.poll()
                if rc is not None:                      # worker exited by itself
                    if rc == 0 and self._maybe_land(att):
                        del self.running[key]
                    else:
                        self._fail_or_redispatch(
                            att, f"exit rc={rc}"
                            + ("" if rc else " with empty/unlandable output"))
                elif not self._alive_by_output(att):    # failure #1/#3 kill-guard
                    self._kill_confirm_dead(att)        # confirmed dead BEFORE re-dispatch
                    self._fail_or_redispatch(
                        att, f"output-file stale > {self.kill_after_s}s (kill-guard)")
            if self.queue or self.running:
                time.sleep(self.poll_s)
        return {k: j.state for k, j in self.jobs.items()}


# ------------------------------------------------- CLI commands

def cmd_plan(args):
    by_key = load_store(args.store, args.keys)
    print(f"{'key1':8s} {'subcards':>8s} {'raw_ls':>7s}  route")
    for k in args.keys:
        recs = by_key.get(k, [])
        n = store_ls_count(recs)
        route = ("ASSEMBLE (programmatic, zero-LLM)" if n > args.assemble_over
                 else "agent (worker subprocess)")
        print(f"{k:8s} {len(recs):8d} {n:7d}  {route}")


def cmd_assemble(args):
    by_key = load_store(args.store, args.keys)
    for k in args.keys:
        recs = by_key.get(k)
        if not recs:
            print(f"{k}: NOT IN STORE — skipped"); continue
        text = assemble_entry(k, recs)
        final = os.path.join(args.outdir, f"{k}.de_synth.txt")
        n = land_watcher_safe(text, final)
        ms = ls_multiset(text)
        print(f"{k}: landed {final} ({len(text.encode('utf-8'))} B, "
              f"raw_ls={sum(ms.values())}, unique={len(ms)}, landing attempts {n})")


def cmd_run(args):
    by_key = load_store(args.store, args.keys)
    staging = args.staging or tempfile.mkdtemp(prefix="synth_dispatch_")
    jobs, worker_keys = [], []
    for k in args.keys:
        recs = by_key.get(k, [])
        n = store_ls_count(recs)
        if n > args.assemble_over and not args.force_agent:
            log(f"{k}: {n} <ls> > {args.assemble_over} -> programmatic assembly (failure #6)")
            text = assemble_entry(k, recs)
            land_watcher_safe(text, os.path.join(args.outdir, f"{k}.de_synth.txt"))
        else:
            jobs.append(Job(k, os.path.join(args.indir, f"{k}.de.txt"),
                            os.path.join(args.outdir, f"{k}.de_synth.txt")))
            worker_keys.append(k)
    if jobs:
        if not args.worker_cmd:
            sys.exit("--worker-cmd is required for agent-routed keys: "
                     + ", ".join(worker_keys))
        d = Dispatcher(jobs, shlex.split(args.worker_cmd), staging,
                       max_concurrent=args.max_concurrent,
                       kill_after_s=args.kill_after, poll_s=args.poll,
                       stagger_s=args.stagger)
        states = d.run()
        print(json.dumps(states, indent=1))
        if any(v != "landed" for v in states.values()):
            sys.exit(1)


# ------------------------------------------------- selftest

FAKE_WORKER = r'''
import sys, os, time
mode, out, attempt = sys.argv[1], sys.argv[2], int(sys.argv[3])
if mode == "good":
    with open(out, "w", encoding="utf-8") as fh:
        for i in range(3):
            fh.write(f"chunk {i} <ls>Quelle {i}</ls>\n"); fh.flush(); time.sleep(0.1)
elif mode == "hang":
    time.sleep(600)                          # writes NOTHING — must be kill-guarded
elif mode == "hang_then_good":
    if attempt == 1:
        time.sleep(600)
    else:
        with open(out, "w", encoding="utf-8") as fh:
            fh.write("replacement output <ls>MBh. 1, 1</ls>\n")
elif mode == "overlap":
    log = os.environ["OVERLAP_LOG"]
    with open(log, "a", encoding="utf-8") as fh:
        fh.write(f"start {time.monotonic()}\n")
    time.sleep(0.5)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("ok\n")
    with open(log, "a", encoding="utf-8") as fh:
        fh.write(f"stop {time.monotonic()}\n")
'''


def cmd_selftest(_args):
    ok = 0
    tmp = tempfile.mkdtemp(prefix="synth_dispatch_selftest_")
    worker = os.path.join(tmp, "fake_worker.py")
    io.open(worker, "w", encoding="utf-8").write(FAKE_WORKER)
    py = sys.executable

    def mk(mode, keys, **kw):
        jobs = [Job(k, "-", os.path.join(tmp, f"{k}.final.txt")) for k in keys]
        d = Dispatcher(jobs, [py, worker, mode, "{output}", "{attempt}"],
                       os.path.join(tmp, "staging"), stagger_s=0, poll_s=0.1,
                       kill_after_s=1.5, land_recheck_s=0.05, **kw)
        return d, {j.key: j for j in jobs}

    # 1. good worker lands
    d, jobs = mk("good", ["w1"])
    assert d.run() == {"w1": "landed"} and os.path.getsize(jobs["w1"].final_path) > 0
    ok += 1; print("PASS 1: good worker lands watcher-safe")

    # 2. hung worker killed by the output-file guard, replacement lands
    d, jobs = mk("hang_then_good", ["w2"])
    assert d.run() == {"w2": "landed"} and jobs["w2"].attempts == 2
    assert any("kill-guard" in h for h in jobs["w2"].history)
    ok += 1; print("PASS 2: kill-guard fires on stale output file; one re-dispatch lands")

    # 3. permanently hung worker -> failed after 1+MAX_REDISPATCH confirmed-dead attempts
    d, jobs = mk("hang", ["w3"])
    assert d.run() == {"w3": "failed"} and jobs["w3"].attempts == 2
    ok += 1; print("PASS 3: permanent hang fails cleanly after capped re-dispatch")

    # 4. zombie cannot overwrite a landed result (single-owner seal)
    d, jobs = mk("good", ["w4"])
    d.run()
    good_sha = sha256_file(jobs["w4"].final_path)
    zombie_staging = os.path.join(tmp, "staging", "w4.attempt99.out")
    io.open(zombie_staging, "w", encoding="utf-8").write("ZOMBIE junk\n")
    zombie = Attempt(jobs["w4"], 99, subprocess.Popen(
        [py, "-c", "pass"]), zombie_staging)
    zombie.proc.wait()
    assert d._maybe_land(zombie) is False
    assert sha256_file(jobs["w4"].final_path) == good_sha
    ok += 1; print("PASS 4: zombie attempt discarded; landed file untouched")

    # 5. concurrency cap respected (6 jobs, cap 2 -> max overlap 2) + hard cap raises
    overlap_log = os.path.join(tmp, "overlap.log")
    os.environ["OVERLAP_LOG"] = overlap_log
    d, _ = mk("overlap", [f"c{i}" for i in range(6)], max_concurrent=2)
    assert set(d.run().values()) == {"landed"}
    depth = mx = 0
    events = sorted((float(l.split()[1]), l.split()[0])
                    for l in io.open(overlap_log, encoding="utf-8"))
    for _, ev in events:
        depth += 1 if ev == "start" else -1
        mx = max(mx, depth)
    assert mx <= 2, f"overlap {mx} > cap 2"
    try:
        Dispatcher([], [], tmp, max_concurrent=10)
        raise AssertionError("hard cap not enforced")
    except ValueError:
        pass
    ok += 1; print(f"PASS 5: concurrency cap held (max overlap {mx} <= 2); 10-wide refused")

    # 6. programmatic assembly is verbatim-complete (multiset self-check inside)
    recs = [
        {"key1": "t", "subcard": "t~~h0_00_pwg01", "layer": "pwg", "sense_tag": "1",
         "de": "gehen <ls>MBh. 1, 1</ls> <ls>R. 2, 2</ls>"},
        {"key1": "t", "subcard": "t~~h0_zz_pw", "layer": "pw", "sense_tag": "1",
         "de": "auch: laufen <ls>MBh. 1, 1</ls>"},
        {"key1": "t", "subcard": "t~~h1_00_pwg01", "layer": "pwg", "sense_tag": None,
         "de": "zweites Homonym <ls>AV. 3, 3</ls>"},
    ]
    text = assemble_entry("t", recs)
    assert ls_multiset(text) == ls_multiset(" ".join(r["de"] for r in recs))
    assert "gehen" in text and "laufen" in text and "zweites Homonym" in text
    ok += 1; print("PASS 6: programmatic assembly keeps every fragment + <ls> verbatim")

    # 7. watcher-wipe simulation: land re-lands after a post-land wipe
    target = os.path.join(tmp, "wipe.txt")
    n = land_watcher_safe("survives\n", target, recheck_s=0.05,
                          _post_land_hook=lambda: os.remove(target))
    assert n == 2 and io.open(target, encoding="utf-8").read() == "survives\n"
    ok += 1; print("PASS 7: watcher wipe detected on re-verify; re-landed")

    shutil.rmtree(tmp, ignore_errors=True)
    print(f"\nselftest: {ok}/7 PASS")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p, keys=True):
        if keys:
            p.add_argument("keys", nargs="+")
        p.add_argument("--store", default=DEF_STORE)
        p.add_argument("--assemble-over", type=int, default=ASSEMBLE_OVER_LS)

    p = sub.add_parser("plan"); common(p)
    p = sub.add_parser("assemble"); common(p)
    p.add_argument("--outdir", default=DEF_OUTDIR)
    p = sub.add_parser("run"); common(p)
    p.add_argument("--indir", default=DEF_INDIR)
    p.add_argument("--outdir", default=DEF_OUTDIR)
    p.add_argument("--worker-cmd", default=None)
    p.add_argument("--staging", default=None,
                   help="staging dir OUTSIDE the repo (default: fresh temp dir)")
    p.add_argument("--max-concurrent", type=int, default=MAX_CONCURRENT_DEFAULT)
    p.add_argument("--kill-after", type=float, default=KILL_AFTER_S)
    p.add_argument("--poll", type=float, default=POLL_S)
    p.add_argument("--stagger", type=float, default=STAGGER_S)
    p.add_argument("--force-agent", action="store_true",
                   help="route large inputs to a worker anyway (NOT recommended)")
    sub.add_parser("selftest")

    args = ap.parse_args()
    {"plan": cmd_plan, "assemble": cmd_assemble, "run": cmd_run,
     "selftest": cmd_selftest}[args.cmd](args)


if __name__ == "__main__":
    main()
