# H2878 — the no-output-progress watchdog (issue #1680)

_Created: 28-08-2026 · Last updated: 28-08-2026_

Executed by **Opus 5 (`claude-opus-5`)**, 28-08-2026, against
[H2878](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2878-Opus_RussianTranslation_pwg-c1-no-output-progress-watchdog_16.08.26.md).

## What was wrong

A **total-wall constant cannot separate a hung call from a slow one.** That is not a new
claim; it is written into the code this unit changes. The comment above
`PRODUCTION_HARD_TIMEOUT_MS` in
[`src/pilot/execution_contract.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/execution_contract.py)
says so in the H2313 owner ruling of 06-08-2026 and names the remedy as unbuilt:

> Separating "hung" from "very slow" for real needs a no-output-progress watchdog (kill on
> stalled output, not on total elapsed time), left as residual work.

The cost of the gap is on record. The 13-08 c1 reading — **300 198 ms, 0 output bytes** —
was written to the events series as a bare `timeout`, and nothing in that row could say
whether the route had died or whether the production lane, which kills at twice that
number, would still have been waiting on it. H2313 had already shown the failure from the
other side: 300 000 ms sat *below* p90 of the **completed** spawn distribution, so the
ceiling was manufacturing failures on the healthy tail. Raising it to 600 000 ms stopped
that and bought no ability to notice a spawn that died silently in second three.

## What shipped

A second bound, **orthogonal** to the ceiling: the longest stretch in which a spawn produced
no result bytes.

| Layer | File | Change |
|---|---|---|
| Contract | [`execution_contract.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/execution_contract.py) | `PRODUCTION_NO_OUTPUT_PROGRESS_MS = 90000`, the two `killed_reason` tokens, `progress_window_ms_for()`, `assert_progress_window_below_ceiling()` |
| Runner | [`proc_tree.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/proc_tree.py) | `run_tree_kill(..., progress_window_ms=, progress_out=)` — byte-granular progress observation and a stalled-output kill |
| Probe | [`max_account_orchestrator.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/max_account_orchestrator.py) | `_probe_call` watches its spawn; `_record_progress` parks the reading on the existing `detail_out` channel; `live_probe` emits it |
| Worker | [`headless_worker.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/headless_worker.py) | every generation call watched; killed attempts carry `killed_reason` / `bytes_seen` / `quiet_ms` |
| Telemetry | [`run_observability.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/run_observability.py) | `bytes_seen`, `quiet_ms`, `killed_reason` added to `ALLOWED` |

`killed_reason` is the field the whole unit exists to produce: `no_output_progress` is a
different event from `hard_timeout`, and after this they are never again the same row.

### The runner keeps its own guarantees

The watched path is a separate function (`_run_watched`) so the classic
`communicate(timeout=)` path is byte-for-byte what it was for any caller that asks for no
observation. The watched path performs the same bounded tree kill, drains the killed child's
output into `exc.output` / `exc.stderr` (H2056 #943 — the only copy of what a hung,
rate-limited CLI ever says), and attaches the new fields to the raised `TimeoutExpired`. That
placement is deliberate: **every existing `except subprocess.TimeoutExpired` keeps working
unchanged** and simply gains something to say.

Progress is read with `os.read` on binary pipes. A text-mode `read(n)` blocks until *n*
characters and `readline()` until a newline, so under either one a spawn dribbling bytes
without newlines is indistinguishable from a dead one.

Only **stdout** resets the quiet window. A CLI retrying internally against a locked account
chatters on stderr while producing no result at all (Uprava FINDINGS §270); counting that
chatter as liveness would blind the watchdog to the one hang it most needs to see. The
stderr byte count is recorded separately, so a reading can still say which pipe was alive.

## The finding that changed the wiring

**A 90 s stalled-output window must not be armed against a buffered `--output-format`, and
every paid lane in this tree uses one.**

`headless_worker`, `_probe_call` and `gen_opt_harness2` all spawn
`claude -p --output-format json`. That format buffers the entire CLI result envelope and
writes it in **one burst when the call finishes**. On that shape a healthy call's stdout is
legitimately 0 bytes for its whole duration — and the H2313 measurements put a healthy card
spawn at **49 404–511 908 ms, p50 189 327**. Arming a 90 000 ms window against it would kill
essentially every healthy call: the exact defect H2313 diagnosed in the 300 000 ms ceiling
("killing HEALTHY card spawns, not hung ones"), roughly six times more aggressive.

So the window is **derived from the spawn's output format**, never pinned by a literal at the
call site:

```python
STREAMING_OUTPUT_FORMATS = frozenset({'stream-json'})

def progress_window_ms_for(output_format, window_ms=PRODUCTION_NO_OUTPUT_PROGRESS_MS):
    return window_ms if output_format in STREAMING_OUTPUT_FORMATS else None
```

Today both paid lanes declare `json`, so both resolve to `None` — **observe only**. Nothing
new can be killed in production by this change. What every call now does is *record*
`bytes_seen` and `quiet_ms`, which is what turns the eventual arming decision into a reading
instead of a bet. A lane that switches to `stream-json` arms the watchdog by doing so, and no
lane can arm it against a buffered format by copying a constant. Both properties are pinned by
selftest (`test_h2878_window_is_derived_from_the_output_format_not_a_literal`).

This is the honest reading of the handoff's own fences — *"do not treat a slow-but-emitting
call as hung"*, *"on ambiguity: kill only on a 0-byte progress window; log"*. A buffered
healthy call is precisely a call that has not emitted **yet**.

`assert_progress_window_below_ceiling` refuses a window at or above the wall ceiling, taking
the same stance H2254 took for the ceiling itself: a request that could never fire is an
error, not something to accept and quietly ignore.

## Evidence

### 1. Selftest red → green

Red — the H2878 tests run against the **pre-patch** `proc_tree.py` (restored from
`origin/master`). The 0-byte child was held for the **full 30 s wall budget** and came back
with nothing to say:

```
subprocess.TimeoutExpired: Command '[..., '-c', 'import time; time.sleep(30)']'
    timed out after 30 seconds
  File ".../headless_worker_selftest.py", line 2210,
    in test_h2878_zero_byte_spawn_dies_on_the_progress_window
    assert exc.killed_reason == 'no_output_progress', exc.killed_reason
AttributeError: 'TimeoutExpired' object has no attribute 'killed_reason'
```

Green — the same tests against the shipped runner:

```
  H2878: a 0-byte spawn dies on the progress window at 505 ms (wall budget 30 000 ms, untouched)
  H2878: an emitting spawn survives 3074 ms against a 1 000 ms window (longest silence 199 ms)
  H2878: the total-wall backstop still fires and reports `hard_timeout`
  H2878: the window is derived from `--output-format` (json -> observe only, stream-json -> 90000 ms), never a copied literal
  H2878: PRODUCTION_HARD_TIMEOUT_MS unchanged at 600000 ms (no ceiling re-fit)
  H2878: a window at/above the ceiling (or non-positive) is refused, not ignored
  H2878: a killed attempt records killed_reason/bytes_seen/quiet_ms; an unwatched runner is byte-for-byte unchanged
  H2878: an emitting spawn survived 100150 ms against the production 90 000 ms window (longest silence 1000 ms)
headless_worker_selftest: PASS
```

The 0-byte spawn dies **at 505 ms on its silence**, nowhere near a wall budget sixty times
larger. That is the whole unit in one line.

The last row is the acceptance sentence taken literally — an emitting spawn survived
**100 150 ms against the real 90 000 ms window**, longest silence 1000 ms. It costs 100 s of
wall clock, so it is opt-in behind `H2878_LONG_SELFTEST=1`; the scaled test above it (3× its
window) runs on every pass.

### 2. The reading reaches the event row

`_test_h2878_probe_records_the_no_output_progress_reading` in
[`max_account_orchestrator_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/max_account_orchestrator_selftest.py)
drives `_probe_call` with a stubbed runner on both sides — one spawn that completes, one
killed on its silence — and asserts all the way through `append_event`, whose `ALLOWED` set
**refuses** unknown keys. A field the runner produces and the writer rejects is telemetry
that does not exist. A healthy row still omits `killed_reason` entirely rather than writing a
null, so the successful lane's row shape is unchanged.

### 3. The ceiling was not re-fit

H2299's standing ban holds. The only lines in the whole diff that mention a ceiling constant
are the new assertions **pinning** it:

```
$ git diff -U0 origin/master -- RussianTranslation/src/pilot/ \
    | grep -E "^[+-].*(PRODUCTION_HARD_TIMEOUT_MS|HARD_TIMEOUT_MS|KILL_CEIL_MS)\s*="
+    assert PRODUCTION_HARD_TIMEOUT_MS == 600000, PRODUCTION_HARD_TIMEOUT_MS
+    assert h.HARD_TIMEOUT_MS == PRODUCTION_HARD_TIMEOUT_MS
+    assert generator.KILL_CEIL_MS == PRODUCTION_HARD_TIMEOUT_MS
```

No definition changed. `PRODUCTION_HARD_TIMEOUT_MS` is still 600 000 ms, and
`HARD_TIMEOUT_MS` / `KILL_CEIL_MS` still import it.

### 4. No regressions

Nine suites, all exit 0: `execution_contract`, `run_observability`, `call_reservation`,
`headless_worker`, `max_account_orchestrator`, `gateway_route`, `gateway_external`,
`bounded_staged_run`, plus the long acceptance leg.

## What is NOT delivered: the one c1 probe

The handoff requires one live c1 probe **"from a session not on the `claude1` profile it
probes"**, and lists `probe from claude1` under *Fail =*.

**This session runs on the `claude1` profile** (`D:\ClaudeTools\profiles\claude1\.claude`),
which is the profile `c1` names. Firing the probe here is the one thing the handoff
explicitly forbids, so it was not fired. No paid call was made by this session.

It is a one-command run for a session on any other profile, from the canonical checkout
(the probe refuses a disposable-worktree evidence root):

```
cd C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation\src\pilot
python h963_c4_gate0_probe.py --account c1
```

That runs the repository's own D-K two-phase protocol — one warm-up plus one measured call,
which is **one probe** in this tree's vocabulary; running it twice is the "second paid probe"
the handoff stops on. Its events row will now carry `bytes_seen`, `quiet_ms` and
`killed_reason` alongside `elapsed_ms`.

**What that reading is for, and what it is not.** It is evidence, not a new ceiling. The
number worth reading off it is `quiet_ms` on a *successful* call: on the current buffered
`--output-format json` it should come back close to the call's full wall time, which is the
empirical confirmation that a stalled-output window cannot be armed against this format —
the finding above, measured rather than argued. It must not be turned into a constant.

## Residual

1. **The c1 probe above** — owed to a non-`claude1` session.
2. **Arming the window for real** needs a lane on `--output-format stream-json`. That is a
   change to the paid call's shape and to envelope parsing, out of this unit's scope, and it
   would invalidate the existing gate's comparability if done casually. The interlock is in
   place: such a lane arms itself.

_Dr. Mārcis Gasūns_
