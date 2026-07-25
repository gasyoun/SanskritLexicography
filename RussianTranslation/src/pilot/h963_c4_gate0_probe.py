#!/usr/bin/env python3
"""H963 Gate-0: ONE fresh dated D-K health attempt for a Max profile (default c4).

Runs the repository's own D-K two-phase protocol (`max_account_orchestrator.live_probe`)
at >= v1.9.17 (natural, schema-carrying, load-representative prompt) against the exact
generation model.

    python src/pilot/h963_c4_gate0_probe.py                 # c4 (unchanged default)
    python src/pilot/h963_c4_gate0_probe.py --account c5
    python src/pilot/h963_c4_gate0_probe.py --account c5 --config-dir <path>

PROFILE SCOPE (25-07-2026)
--------------------------
The account was hardcoded to c4 because H1110 gates c4 only. /pwg-live-gate's own
"serial multi-profile assessment" section already specifies the shape for other
profiles -- one health+canary pair per profile, run SERIALLY, each with its own
distinct `config_dir_fingerprint`, never interleaved and never sharing a fingerprint --
so the account is now a parameter rather than a copy of this file per profile.

Each account keeps its OWN events log: a profile's health history is its own series,
and reading two profiles out of one file re-creates the #729 contamination class one
level up. c4 keeps the original filename (11 rows of history, cited by path in the
H1110/H1447/H858 gate reports); any other account gets
`h963_<account>_gate0_probe_events.jsonl`.

Evidence discipline: exactly ONE attempt. Both the warm-up and the measured
reading are emitted to the append-only events log BEFORE any fail-closed exit,
so a NO-GO leaves the same immutable trace as a PASS. No retry, no re-warm,
no reroll. The historical NO-GO (warm-up 29 743 ms / measured 52 815 ms,
15-07-2026) is NOT overwritten or reinterpreted -- this is a new dated reading.

Gate rule applied here is STRICTER than live_probe's own gate: live_probe
excludes the warm-up from the ceiling, but the H963 c4 resume brief requires
that EITHER reading at >= 30 000 ms is a NO-GO. Both are reported.

RUN SCOPE (issue #729, fixed 25-07-2026)
----------------------------------------
`RUN_ID` used to be a CONSTANT (`h963-c4-single-profile-gate0-2026-07-16`). Every
invocation appended to *and re-read* that one bucket, then kept the last row per
purpose -- so a run could pair its own warm-up with a **stale** `measured` from days
earlier. The 25-07-2026 gate run printed `measured latency 168352 ms >= 30000 ms` as a
NO-GO reason for a measured call it never made (that row was from 23-07).

There it only mis-stated a reason. The hazard is the INVERSE: a stale *passing* measured
row plus a passing warm-up leaves the fail list empty and prints `GATE-0 VERDICT: PASS`,
citing a measured call never made this session -- and that verdict is what
`/pwg-live-gate` Step 3 turns into `LIVE_GO`, which authorizes `/pwg-bounded-run` to
spend. A paid window opened off a two-day-old number, from inside the gate whose whole
purpose is "a stale GO never authorizes a window".

So the run id is now minted per invocation (`new_run_id()`), and the reader
(`readings_for`) matches it EXACTLY. The old constant survives as `CAMPAIGN`, a prefix
for historical grouping -- it is a label, never a scope. The verdict is derived by the
pure `derive_fails()`, exercised without any live call by `--selftest`.
"""
import argparse
import json
import os
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import max_account_orchestrator as mao  # noqa: E402
from headless_worker import claude_argv_prefix  # noqa: E402


def resolve_claude_bin():
    """D-R: the repo default ``--claude-bin 'claude'`` is a BARE name, so
    ``claude_argv_prefix`` resolves the shim dir via ``abspath('claude')`` -> the CWD,
    finds no ``node_modules`` there, and falls back to ``['claude']`` -- which Windows
    CreateProcess cannot launch (the real file is a ``.cmd`` shim). Resolve to the real
    shim path so the prefix reaches its intended ``[node, cli*.cjs]`` form."""
    if os.name != "nt":
        return "claude"
    for cand in (shutil.which("claude.cmd"), shutil.which("claude"),
                 os.path.join(os.environ.get("APPDATA", ""), "npm", "claude.cmd")):
        if cand and os.path.isfile(cand) and os.path.splitext(cand)[1].lower() == ".cmd":
            return cand
    return "claude"


CONFIG_DIR = r"D:\ClaudeTools\profiles\claude4\.claude"
ACCOUNT = "c4"
PROFILE_ROOT = r"D:\ClaudeTools\profiles"
# The historical campaign label. A GROUPING PREFIX, never a run scope -- see the module
# docstring. Reports that cite `run_id=h963-c4-single-profile-gate0-2026-07-16` (H1110
# 18-07, H1447 22-07) still match rows by this prefix.
CAMPAIGN = "h963-c4-single-profile-gate0-2026-07-16"
EVENTS = HERE / "output" / "h963_c4_gate0_probe_events.jsonl"
PAYLOAD_BYTES = 6491          # repo default; actual prompt 6828 B (H909 runbook, v1.9.19)
CEILING_MS = mao.PROBE_LATENCY_CEILING_MS   # 30 000
STRICT_CEILING_MS = 30_000    # resume brief: EITHER reading >= this is NO-GO
CONN_ERR_CLASSES = {"process", "timeout"}


def config_dir_for(account):
    """`cN` -> that profile's config dir, by the repo's own `claudeN` layout."""
    if not re.fullmatch(r"c\d+", account or ""):
        raise SystemExit("account %r is not of the form cN; pass --config-dir explicitly"
                         % account)
    return os.path.join(PROFILE_ROOT, "claude" + account[1:], ".claude")


def campaign_for(account):
    """The grouping label for `account`.

    c4 keeps the historical string verbatim -- the H1110/H1447/H858 gate reports cite it,
    and 11 rows carry it. Any other profile gets its own, because a c5 row whose run id
    reads `h963-c4-...` misleads exactly the reader this label exists to orient.
    """
    if account == ACCOUNT:
        return CAMPAIGN
    return "h963-%s-single-profile-gate0" % account


def events_for(account):
    """One events log PER ACCOUNT.

    Sharing one file across profiles would re-create the #729 contamination one level up:
    a c5 row answering for a c4 verdict. c4 keeps the original filename because 11 rows of
    history live there and the H1110/H1447/H858 gate reports cite it by path.
    """
    if account == ACCOUNT:
        return EVENTS
    return HERE / "output" / ("h963_%s_gate0_probe_events.jsonl" % account)


def preflight_profile(config_dir):
    """Cheap, FREE provisioning checks. Returns a reason string, or None when usable.

    Deliberately NOT `max_account_orchestrator.profile_status`: that helper fires its own
    paid `-p` call, and this gate exists to spend exactly one no-reroll attempt. A missing
    directory or absent credentials is a provisioning fact, readable off the disk — the same
    discipline as the D-R argv pre-flight below (never burn the attempt on a mis-provisioned
    profile, and never report a provisioning defect as a health signal).
    """
    if not os.path.isdir(config_dir):
        return "profile directory does not exist: %s" % config_dir
    if not os.path.isfile(os.path.join(config_dir, ".credentials.json")):
        return ("no .credentials.json in %s — the profile is not logged in "
                "(a login is a human action; this gate never performs one)" % config_dir)
    return None


def new_run_id(campaign=CAMPAIGN, now=None, pid=None):
    """A run id unique to THIS invocation, under the campaign prefix.

    The UTC second alone is not enough: two invocations can share it, and the whole point
    of this identifier is that no two runs can ever read each other's rows. The pid makes
    a collision impossible in practice while keeping the id greppable and human-readable.
    """
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))
    return "%s/%s-pid%d" % (campaign, stamp, os.getpid() if pid is None else pid)


def readings_for(events_path, run_id):
    """The `probe_call` rows THIS run wrote -- EXACT run_id match, in file order.

    Deliberately exact, never a prefix/campaign match: a prefix match is precisely the
    defect (#729), because it re-admits every historical row into the current verdict.
    """
    path = Path(events_path)
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("run_id") == run_id and row.get("event") == "probe_call":
            rows.append(row)
    return rows


def derive_fails(readings, strict_ceiling_ms=STRICT_CEILING_MS):
    """The gate policy as a pure function of THIS run's readings. Empty list == PASS.

    Both readings must be present, `success`, free of connection/process errors, and
    strictly below the ceiling. A missing reading is a FAIL, never a skip -- that is what
    makes a run whose measured phase never executed a NO-GO instead of silently
    inheriting someone else's measured row.
    """
    by_purpose = {r.get("purpose"): r for r in readings}
    fails = []
    for label, key in (("warm-up", "warmup"), ("measured", "measured")):
        r = by_purpose.get(key)
        if r is None:
            fails.append("%s reading absent (probe stopped before it ran)" % label)
            continue
        cls = r.get("classification")
        ms = r.get("elapsed_ms")
        if cls != "success":
            fails.append("%s classification=%s (not success)" % (label, cls))
        if cls in CONN_ERR_CLASSES:
            fails.append("%s connection/process error (%s)" % (label, cls))
        if isinstance(ms, int) and ms >= strict_ceiling_ms:
            fails.append("%s latency %d ms >= %d ms ceiling" % (label, ms, strict_ceiling_ms))
    return fails


def main(argv=None):
    ap = argparse.ArgumentParser(description="H963 Gate-0 single-profile D-K health attempt")
    ap.add_argument("--account", default=ACCOUNT,
                    help="profile slot to gate (default %s)" % ACCOUNT)
    ap.add_argument("--config-dir", default=None,
                    help="that profile's CLAUDE_CONFIG_DIR (default: derived from --account)")
    args = ap.parse_args(argv)
    account = args.account
    config_dir = args.config_dir or (CONFIG_DIR if account == ACCOUNT
                                     else config_dir_for(account))
    events = events_for(account)
    events.parent.mkdir(parents=True, exist_ok=True)

    # Belt-and-suspenders: pin the store to a scratch path so nothing can touch the
    # canonical 11,605-row store. (live_probe makes no store write by construction.)
    os.environ["PWG_RU_STORE"] = str(HERE / "output" / "h963_c4_gate0_scratch_store.jsonl")

    campaign = campaign_for(account)
    run_id = new_run_id(campaign)
    claude_bin = resolve_claude_bin()
    argv_prefix = claude_argv_prefix(claude_bin)

    prompt = mao._probe_prompt(PAYLOAD_BYTES)
    actual_prompt_bytes = len(prompt.encode("utf-8"))

    print("=" * 72)
    print("H963 Gate-0 — single-profile %s D-K health attempt" % account)
    print("=" * 72)
    print("date (UTC)        : %s" % time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    print("profile           : %s  (%s)" % (account, config_dir))
    print("exact model       : %s" % mao.EXACT_GEN_MODEL)
    print("payload_bytes arg : %d" % PAYLOAD_BYTES)
    print("actual prompt B   : %d  (floor %d B / 5 KiB=5120)"
          % (actual_prompt_bytes, mao.PROBE_MIN_PAYLOAD_BYTES))
    print("ceiling           : %d ms (strict: either reading >= %d ms => NO-GO)"
          % (CEILING_MS, STRICT_CEILING_MS))
    print("run_id            : %s   (unique to THIS run — #729)" % run_id)
    print("campaign          : %s   (grouping label only, never a read scope)" % campaign)
    print("events            : %s   (per-account series)" % events)
    print("claude bin        : %s" % claude_bin)
    print("resolved argv     : %s" % argv_prefix)
    print("-" * 72)

    if actual_prompt_bytes < 5120:
        print("RESULT: NO-GO — payload undersized (%d B < 5 KiB)" % actual_prompt_bytes)
        return 2

    # PRE-FLIGHT (no call made): a mis-provisioned profile is a PROVISIONING fact, not a
    # health reading, and must never consume the one no-reroll attempt or be logged as
    # latency. Free — reads the disk, spends nothing.
    reason = preflight_profile(config_dir)
    if reason:
        print("PRE-FLIGHT ABORT (no probe call made, no attempt consumed):")
        print("  %s" % reason)
        print("  This is a provisioning state, NOT a %s health signal." % account)
        return 4

    # PRE-FLIGHT (no call made): never spend the one no-reroll attempt on a mis-resolved
    # binary. A bare ['claude'] fallback is the D-R defect and is NOT a health reading.
    if os.name == "nt" and (len(argv_prefix) != 2 or not argv_prefix[0].lower().endswith("node.exe")):
        print("PRE-FLIGHT ABORT (no probe call made, no attempt consumed):")
        print("  claude_argv_prefix(%r) -> %s" % (claude_bin, argv_prefix))
        print("  expected [<node.exe>, <cli*.cjs>]; a bare fallback cannot be launched by")
        print("  CreateProcess. This is a tooling-resolution defect (D-R), NOT a %s health signal."
              % account)
        return 3

    verdict_exc = None
    t0 = time.monotonic()
    try:
        mao.live_probe(
            config_dir,
            claude=claude_bin,
            payload_bytes=PAYLOAD_BYTES,
            model=mao.EXACT_GEN_MODEL,
            latency_ceiling_ms=CEILING_MS,
            events_path=str(events),
            run_id=run_id,
            account=account,
        )
    except SystemExit as exc:
        verdict_exc = str(exc)
    wall_s = time.monotonic() - t0

    print("wall clock        : %.1f s" % wall_s)
    print("-" * 72)

    # Re-read the append-only events log: it holds BOTH readings even on a fail-closed
    # exit -- but ONLY the rows this run wrote (#729).
    readings = readings_for(events, run_id)

    print("RAW READINGS (append-only telemetry, THIS run only — run_id %s):" % run_id)
    if not readings:
        print("  (none — no probe call completed)")
    for r in readings:
        print("  purpose=%-8s elapsed_ms=%-7s classification=%-10s output_bytes=%s"
              % (r.get("purpose"), r.get("elapsed_ms"), r.get("classification"),
                 r.get("output_bytes")))

    print("-" * 72)
    if verdict_exc:
        print("live_probe fail-closed: %s" % verdict_exc)

    fails = derive_fails(readings)
    by_purpose = {r.get("purpose"): r for r in readings}

    print()
    if fails:
        print("GATE-0 VERDICT: NO-GO")
        for f in fails:
            print("  - %s" % f)
        print()
        print("STOP. No canary. No production window. No reroll.")
        return 1

    print("GATE-0 VERDICT: PASS")
    print("  warm-up  %d ms (success)" % by_purpose["warmup"]["elapsed_ms"])
    print("  measured %d ms (success), strictly below %d ms"
          % (by_purpose["measured"]["elapsed_ms"], STRICT_CEILING_MS))
    return 0


# ---------------------------------------------------------------------------
def _row(run_id, purpose, ms, cls="success"):
    return {"event": "probe_call", "run_id": run_id, "purpose": purpose,
            "elapsed_ms": ms, "classification": cls, "output_bytes": 1400}


def selftest():
    """Regression pin for #729. Pure — makes no live call, spends nothing.

    The load-bearing case is the LAST one: a log carrying a historical PASSING pair, and
    a fresh run whose measured phase never executed. Under the old constant-`RUN_ID`
    reader that combination printed `GATE-0 VERDICT: PASS`.
    """
    d = tempfile.mkdtemp()
    try:
        log = Path(d) / "events.jsonl"
        old, new = CAMPAIGN, new_run_id(now=0, pid=1)
        rows = [
            _row(old, "warmup", 17972),            # 22-07 historical pair -- both PASSING,
            _row(old, "measured", 16621),          # which is what makes this the hazard
            _row(new, "warmup", 17878, "rate_limit"),   # this run: fail-closed on warm-up
        ]
        log.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")

        # 1. the reader is scoped to the run, not to the campaign or the file
        mine = readings_for(log, new)
        assert len(mine) == 1 and mine[0]["purpose"] == "warmup", mine
        assert readings_for(log, old) == rows[:2], 'an unrelated run must still read its own rows'

        # 2. THE PIN: a run whose measured phase never ran is NO-GO, and says so about
        #    ITS OWN missing reading -- never a latency borrowed from another run.
        fails = derive_fails(mine)
        assert any("measured reading absent" in f for f in fails), fails
        assert any("warm-up classification=rate_limit" in f for f in fails), fails
        assert not any("168352" in f or "16621" in f for f in fails), \
            'a NO-GO reason must never cite a reading this run did not take'

        # 3. RED: the pre-#729 behaviour (campaign-wide read, last row per purpose) would
        #    have paired this run's warm-up with the 22-07 measured. Prove that pairing is
        #    a PASS, so the pin above is protecting against a real false-GO, not a typo.
        contaminated = [r for r in rows]                    # every row, as the old reader saw it
        by_purpose = {r["purpose"]: r for r in contaminated}
        assert by_purpose["measured"]["elapsed_ms"] == 16621
        assert derive_fails([by_purpose["measured"], _row(new, "warmup", 17878)]) == [], \
            'the contaminated pairing must be demonstrably PASS-shaped (that is the hazard)'

        # 4. a genuine clean pair still passes; a slow one still fails
        assert derive_fails([_row(new, "warmup", 17972), _row(new, "measured", 16621)]) == []
        slow = derive_fails([_row(new, "warmup", 17972), _row(new, "measured", 40003)])
        assert len(slow) == 1 and "40003 ms >= 30000 ms" in slow[0], slow

        # 5. run ids are unique per invocation even within the same UTC second
        assert new_run_id(now=0, pid=1) != new_run_id(now=0, pid=2)
        assert new_run_id(now=0, pid=1).startswith(CAMPAIGN + "/"), 'campaign stays a prefix'
        # the label is account-aware: a c5 row whose run id reads `h963-c4-...` misleads
        # exactly the reader the label exists to orient.
        assert campaign_for("c4") == CAMPAIGN, 'c4 keeps the string the gate reports cite'
        assert campaign_for("c5") == "h963-c5-single-profile-gate0", campaign_for("c5")
        assert campaign_for("c5") != campaign_for("c6")

        # 6. profile scope: c4's log keeps its historical path (reports cite it by name),
        #    and no two accounts share a file -- sharing one would re-create the #729
        #    contamination one level up, a c5 row answering for a c4 verdict.
        assert events_for("c4") == EVENTS, 'c4 must keep its historical events path'
        seen = {str(events_for(a)) for a in ("c4", "c5", "c6")}
        assert len(seen) == 3, seen
        assert config_dir_for("c5").endswith(os.path.join("claude5", ".claude")), config_dir_for("c5")
        for bad in ("", "cee", "claude5", "c5x"):
            try:
                config_dir_for(bad)
            except SystemExit:
                pass
            else:
                raise AssertionError('config_dir_for(%r) must refuse, not guess a path' % bad)

        # 7. a mis-provisioned profile is refused BEFORE any call, and is reported as a
        #    provisioning state -- never logged as a health reading.
        missing = Path(d) / "no-such-profile"
        assert "does not exist" in (preflight_profile(str(missing)) or ''), 'missing dir must refuse'
        logged_out = Path(d) / "logged-out" / ".claude"
        logged_out.mkdir(parents=True)
        assert "not logged in" in (preflight_profile(str(logged_out)) or ''), 'no creds must refuse'
        (logged_out / ".credentials.json").write_text("{}", encoding="utf-8")
        assert preflight_profile(str(logged_out)) is None, 'a provisioned profile must pass pre-flight'

        print("h963_c4_gate0_probe selftest: 7/7 OK (no live call, nothing spent)")
    finally:
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        selftest()
        raise SystemExit(0)
    raise SystemExit(main())
