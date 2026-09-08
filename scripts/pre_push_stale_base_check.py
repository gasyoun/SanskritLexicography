"""Refuse a push that deletes lines another session added upstream moments ago —
the silent-revert class of Uprava#1516.

WHY THE OBVIOUS DESIGN DOES NOT WORK
------------------------------------
The guard proposed on #1516 was "refuse a push whose tree contains a path modified
upstream after the local HEAD's merge-base". Implemented and measured 04-08-2026, it
is **redundant with git itself**: ``merge-base != remote_tip`` is the definition of a
non-fast-forward push, which git already rejects; and a fast-forward push always has
``merge-base == remote_tip``, so the check is vacuous exactly when it is needed. Both
#1516 incidents were clean fast-forwards. A ref-level test cannot see them.

What both incidents *do* share is visible at the line level: the push **deletes lines
that an upstream commit added very recently**, because the author's file content was a
pre-image copy — a stale index (29-07) or a stale checkout (04-08). Nobody edits a line
that landed ninety seconds ago on purpose without knowing it; when it happens it is
almost always a copy written before that line existed.

THE CHECK
---------
For each path the push changes, take the lines it removes relative to the remote tip,
``git blame`` them at the remote tip, and flag any whose introducing commit is

* **recent** — within ``--recent-days`` (default 3), and
* **not part of this push** — so rewriting your own just-pushed line is fine.

That pair is the whole rule. Old lines are ordinary edits. Your own lines are yours.
Someone else's line from an hour ago, deleted by a commit that never mentions it, is
the defect.

BLOCKS BY DEFAULT — DEMOTED, THEN RE-PROMOTED
---------------------------------------------
**Current behaviour: this hook REFUSES the push.** Override per-push with
``ALLOW_STALE_BASE_PUSH=1``. ``STALE_BASE_PUSH_STRICT=1`` is now the default and is
accepted as a no-op.

Re-promoted 16-08-2026 on MG's ruling, reversing the demotion described below. The
history is kept because it is the argument against this decision, and a future session
weighing another flip should read it rather than rediscover it:

This started as a **blocking** hook, which is what #1516 asked for. It was demoted to a
warning on the day it shipped, on measured evidence: while landing its own handoff it
refused three pushes, all of them legitimate, all of them this repo's standard workflow —

1. resolving a ``CHANGELOG`` version collision by renumbering a concurrent session's
   section (their rows deleted at the old line numbers, re-added lower);
2. filling a ``mint_handoff.py`` stub that had been pushed to ``main`` seconds earlier;
3. ``handoff_close.py`` archiving a handoff, which repoints ``handoffs/X`` links to
   ``handoffs/archive/X`` **inside rows added minutes ago**.

**All three are now exempted below**, plus a fourth found by measurement afterwards.
(3) was the open cost of re-promoting this to a blocker and was closed the same day
(MG 16-08-2026) rather than left to bite: see ``archive_normalized``. It normalizes the
``handoffs/X.md`` → ``handoffs/archive/X.md`` repoint on the REMOVED line only, so an
archive pass reads as the move it is. A push that repoints a link *and* drops anything
else on the same line still blocks — the exemption is the rewrite, not the tool.

(4) **Registry bookkeeping**, exempted 17-08-2026 — see ``is_registry_bookkeeping``.
``registry_check.apply_fix`` regenerates four derived lines on every close, so two
closes inside the recency window always look like each other's revert; FINDINGS §435
measured that blocking BOTH sanctioned close paths under ordinary push traffic.

(5) **Surgical forward modification of a minutes-old line**, exempted 22-08-2026 after
the retier of five handoff rows hit it twice in one hour: rewriting someone's fresh row
IN PLACE (token swap inside an otherwise byte-identical line) is not a deletion — the
line's information survives. Detection is two-gated so the H1516 class cannot dress up
as this: (a) the replacement must be a NEAR match (``difflib`` ratio ≥ ``NEAR_RATIO``)
of the removed line among the pushed survivors, and (b) that exact replacement text
must NOT already exist in the file as of the blamed commit's parent. Gate (b) is the
load-bearing half: a stale pre-image reinstall also near-matches (it differs from the
fresh line by exactly the upstream edit), but its text demonstrably existed *before*
their commit — which is the definition of installing old work over new, and still
blocks. A forward edit produces content history has never seen; a revert replays
content it has. See ``best_near_match`` / ``pre_image_lines`` and test cases 14/14b.

(5) **Generated single-writer artifacts**, exempted 18-08-2026 — see
``is_generated_single_writer``. A ``--land`` caller replaces a whole file it is the
ONLY writer of (a dashboard snapshot, a stats JSON) every run, and some of those
files churn dozens of lines a day — every such push trips this guard by
construction, not by accident. Measured 18-08-2026 (H3073): four consecutive
``tools/refresh_dashboards_daily.py --land`` runs were refused this way and
misreported as "origin kept moving", when the scheduled task had in fact been
red for three days.

(7) **Same-session mint→close and claim→close**, exempted 24-08-2026 and
26-08-2026 respectively — see
``is_same_session_mint_close`` (FINDINGS §457). Closing a handoff minted in the
same session rewrites the very registry row / body lines the mint commit added
minutes earlier, so blame hits a fresh non-pushed commit and EVERY such close
refused — measured on H3060 (cleared with ``ALLOW_STALE_BASE_PUSH=1``, landed
as ``cb0acd668``). Three gates keep the H1516 stale-pre-image class out: the
blamer subject must BE a mint claim, the removed line must name that minted
H###, and this push must visibly work on the same H### elsewhere (path basename
or added line). A stale checkout reverting someone's just-minted stub deletes
the row without touching anything else named H#### and stays blocked.

(8) **The FINDINGS next-number marker, bumped forward**, exempted 03-09-2026 — see
``findings_marker_bump`` (FINDINGS §695). ``FINDINGS.md`` ends with the single line
``§N takes the next number.``; every append CONSUMES that number and rewrites the
line, so every append deletes a line another session added minutes ago and every
append refuses — the same "routine work needs the override" shape §659 measured on
release pushes, and an override reflex trained on routine work is what §641/§643
warn about. One-directional and readable from the pushed content alone (the §437
bar): exempt only when the same push LEAVES a marker whose number is strictly
greater. A stale checkout reinstalling a pre-image marker moves the number backwards
or leaves it equal and still blocks — exactly the H1516 shape. The match is anchored
and whole-line, so nothing else on that line, and no other line in the file, gains
anything. See test cases 23/23b. §659's changelog-fragment twin stays OPEN.
That last sentence is superseded the same day: the twin shipped as class (9)
below — kept verbatim rather than rewritten so this guard's own history is
readable, and so the line survives its own recency check.

(9) **changelog_queue fragments consumed by a release cut**, exempted 03-09-2026 —
see ``promoted_queue_lines`` (FINDINGS §659, tightened by H3886). A cut
copies each ``changelog_queue/*.md`` fragment's bullet into ``CHANGELOG.md`` and
DELETES the fragment in the same commit, so every fragment another session added in
the last ``--recent-days`` is deleted by construction: measured 03-09-2026 on the
``v0.195.419`` cut, 35 lines across 33 files, and the same on every cut before it.
The text is not lost, it MOVED across paths, so the fix is a credit, not an override.
Same-push gated exactly like ``REGISTRY_RELOCATION_PAIR``: only the lines THIS PUSH ADDS
to ``CHANGELOG.md`` count, so a stale checkout that merely drops someone's fresh fragment
is credited with nothing and still blocks.

The credit is an EQUALITY test, and it is deliberately kept OUT of ``survivors`` (H3886,
07-09-2026). ``changelog_queue_consume.flush_bullets`` copies each non-blank fragment
line ``ln.rstrip()`` BYTE-IDENTICALLY into the release section, so a real cut always
produces exact text and needs no slack. Routing the changelog additions through the
survivor set instead — the shape shipped on 03-09 — also fed them to class 5's
``best_near_match``, and a fresh fragment's own BIRTH commit is its blamer, so gate (b)
is satisfied by construction (``_creation_sha`` -> empty pre-image): a push that DELETED
a fresh fragment while adding a REWORDED bullet was silently exempted. That is the H1516
class wearing a release cut's clothes, in the file class that churns hardest at release
time — the last place to widen a near-match surface. The credit is therefore taken like
§450's relocation: before blame, never as a survivor. Test cases 24 (promoted -> allowed),
24b (dropped -> blocks), 24c (reworded -> blocks).

(10) **Same-lane close-prep lines of the SAME handoff file**, downgraded to a loud
WARNING (not a block) 07-09-2026 — see ``is_same_lane_close_prep`` (GTD 0x, the
H4265 close incident). A drain session claimed H4265 (``exec-claim: H4265 …``),
filled its acceptance checkboxes in commit 8b5fbda (subject: "handoffs: … fanout
fills — H4260 umbrella + H4261–H4265 S1–S5 …"), and was then refused EIGHT times
when its own close push rewrote those same checkbox lines: the §457 exemption's
gate 1 only recognises mint/claim SUBJECTS, and 8b5fbda is a fill commit, so
every close of a handoff filled minutes earlier by its own lane blocked and
needed a human ruling (MG 06-09-2026: «Флип разрешить», via
GUARD_ESCAPE_HUMAN_RULING at 03:35 — the exact override-reflex cost §641/§643
warn about). The class is deliberately NOT a silent exemption: lines whose
blaming commit's subject names the SAME H### as the changed ``handoffs/`` file
itself (marker provenance — mint, exec-claim, fill and close subjects all carry
their H###s), where THIS PUSH visibly works on that same H###, are reported as
``stale-base guard: WARNING — push ALLOWED`` naming every line, and the push
proceeds. Honest limit, accepted by the ruling: a stale checkout that reverts
ANOTHER session's work inside that one handoff file also warns instead of
blocking — the blast radius is bounded to the one file whose name carries the
H###, the warning stays in stderr for the human, and registry/README/GTD lines
(outside ``handoffs/H####-*.md`` basenames) keep blocking. A subject that names
NO handoff id still blocks outright (case 20b).

The list above was wrong when written, which is the durable lesson: it claimed three
classes with one outstanding, and (4) was already live. Enumerate a guard's false
positives by measurement before promoting it, not from its own docstring. The
``ours`` set still covers only commits inside the CURRENT push: rewriting your own
lines from an EARLIER push blocks everywhere except the one file-shape class (10)
downgraded to a warning. (A general self-lineage exemption — adder-is-ancestor —
was considered for §457 and REJECTED: the 04-08 incident's stale-checkout shape
contains the rival commit as an ancestor while reinstalling pre-image content, so
ancestry alone cannot separate the two; the mint-subject + same-H### +
this-push-names-it gates above are the narrower cut that can.)

The demotion argument was that three false-positive classes against two true incidents is
the wrong ratio for a blocker, since the standing response to a hook that refuses good
pushes is to switch it off, and then it protects nothing. The counter-argument, which won:
a silent revert of another session's work is not recoverable by the person it happens to —
they discover it days later, if ever — while a false positive costs one extra environment
variable at the moment of the push, by someone who can see exactly what is being reverted::

    ALLOW_STALE_BASE_PUSH=1  git push ...   # per-push override (the only one needed)
    STALE_BASE_PUSH_STRICT=1 git push ...   # accepted no-op; blocking is now the default

A deliberate revert of fresh upstream work is flagged too — correctly, and now it must be
declared with the override rather than merely noticed.

LIMITS (measured, not assumed)
--------------------------
* Blame is per-path and costs ONE blame per changed file (batched: a single
  ``git blame --line-porcelain`` per path feeds every removed line); on a push
  touching hundreds of files this is still not free, so ``--max-paths``
  (default 40) bounds it and the script says so rather than silently sampling.
* **Work bounds (FINDINGS §543, §605)** — a line-level guard with unbounded work
  does not refuse, it HANGS, and a push killed mid-guard by the caller's timeout
  reports as silence, not as a verdict. Measured twice: a derived-views regen
  (§543, >300 s with no output) and a wholesale derived-JSON rewrite
  (§605, −28 488/+8 843 lines, >420 s standalone, push dead by timeout). Two
  bounds now cap the work per path: ``--max-blame-lines`` (default 2000) on the
  removed-line count, and ``--max-near-pairs`` (default 300 000) on the
  near-match comparison budget (removed × survivors, consumed by class 5's
  difflib work). Past either bound the path is NOT silently skipped — it gets a
  greppable ``STALE_BASE_CIRCUIT_BREAK`` verdict naming the path and the bound,
  and the check degrades to ref-level verification: a clean fast-forward
  (``merge-base --is-ancestor``) is allowed with that loud note; the same bulk
  rewrite on a forced/non-fast-forward update is refused fail-closed, because a
  forced push is exactly where git's own ref-level protection is switched off.
  A guard that degrades into an infinite computation converts every push into a
  silent kill, which is strictly worse than a visible skip (§605: a false
  refusal is visible; a hang teaches authors to bypass).
* Pure additions are never flagged; only deletions and rewrites of recent upstream lines.
* Whitespace-only differences are ignored (``-w``), so a CRLF renormalisation sweep does
  not trip it — the §299/§305 class is a different problem with a different fix.
* A push that reverts a line older than the window is not caught. That is the accepted
  cost of keeping false positives near zero.

A RETRY LOOP CANNOT WIN AGAINST THIS REFUSAL (H3134, FINDINGS §493)
---------------------------------------------------------------------
This is a LOCAL pre-push hook refusal, not a moved remote tip: a `fetch → rebase →
push` loop rebases cleanly every time and this script refuses every time, because
nothing about the refusal depends on where ``origin/main`` sits — the rebase never
changes the deleted lines this diff would drop. `report()` therefore prints a
stable, greppable marker (``STALE_BASE_GUARD_REFUSAL``) and names the override on
its first line, not twenty lines into the banner, so a wrapper can stop on the
FIRST refusal instead of burning its whole retry budget on a fixed answer (§493
measured a hand-written loop give up after 15 identical attempts).

The cheap discriminator for a wrapper that cannot inspect stderr: ``git merge-base
--is-ancestor origin/main HEAD`` is **true** for this LOCAL refusal (the local
branch already contains the remote tip — nothing to rebase onto) and **false**
for a genuine non-fast-forward (the remote moved and the local branch does not
yet contain it). ``handoff_claims.commit_texts_to_origin`` (FINDINGS §449) takes
the more precise route and reads this hook's own ``PUSH BLOCKED`` banner from the
push's stderr instead — it deliberately keeps retrying even on a confirmed guard
block, because its transforms are re-applied to freshly fetched content each pass
and a concurrent commit can change which exemption below applies; that is a
different, already-correct design and this handoff does not touch it.

NON-FAST-FORWARD IS NOT THIS GUARD'S BUSINESS (H4342, 08-09-2026)
------------------------------------------------------------------
The paragraph above is kept verbatim because its central claim is WRONG, and the
wrongness is the whole of H4342. It reads the two states as mutually exclusive —
LOCAL refusal *or* non-fast-forward. They are not. ``commit_texts_to_origin``
pins a base, builds a ``commit-tree`` on it, and pushes that detached sha; when a
concurrent session lands in that window the push is a non-fast-forward AND this
guard sees every line the winner just added as a line the push deletes. It then
printed ``STALE_BASE_GUARD_REFUSAL`` — "Retrying cannot clear it" — for the one
case where retrying is precisely what clears it, and the sticky
``diag["guard_blocked"]`` made the caller close with "This is NOT origin/main
moving". It was.

Measured 08-09-2026: the same H4339 close commit refused with 25 phantom
deletions in 2 paths when its base was one commit stale, and passed clean when
rebuilt on the tip — same transforms, same content. Against 3222 stale-base
refusals logged in ``logs/guard_firings.jsonl`` over ten days (241 episodes; the
worst single episode 383 refusals across 2 h 09 m) and 290 ``ALLOW_STALE_BASE_PUSH``
escapes, this shape is the reason the override reflex §641/§643 warn about ever
had routine work to train on.

``main()`` therefore asks ``push_is_fast_forward()`` before judging: a
non-fast-forward push gets ``STALE_BASE_NON_FF_SKIP``, its phantom lines named
in stderr, and exit 0 — git refuses the push itself, and on main/master a FORCED
one is refused fail-closed by ``scripts/pre_push_main_line_gate.py`` check 2
(rewind/rewrite, escape ``ALLOW_MAIN_LINE_REWIND=1``). Detection power lost for
the #1516 class: none — it is fast-forward-shaped by definition, as the opening
of this docstring says. Cases 26/26b pin both halves.

TWO EXEMPTIONS CONSIDERED FOR THIS HANDOFF, BOTH NOW ADDED
-----------------------------------------------------------
Both were checked against the same bar: recognisable from the pushed content
alone, with no guess about intent (§437's lesson — a heuristic exemption papers
over one false-positive class and leaves the others louder).

* **GTD active-state migration (H2697) — added, see ``cross_file_survivors``.**
  ``gtd_active_state.compact_card`` truncates an over-cap card to a status line
  in ``GTD_NEXT_ACTIONS.md`` while writing its FULL original text verbatim into
  ``GTD_ARCHIVE.md``, in the same commit. That satisfies the structural bar
  exactly: the deleted content reappears verbatim in the archive half of the
  SAME push. Scoped to this one declared file pair — not "any file elsewhere in
  the push", which would let the survivors check quietly absorb an unrelated
  file's coincidental text match.
* **Registry row relocation (FINDINGS §450, §530) — added once the shape became
  verbatim-checkable; see ``cross_file_survivors`` + ``relocated_registry_rows``.**
  This block originally said NOT added, on purpose: a ``handoff_close.py
  --commit`` move rewrites the row's status/date/tier cells, so no whole-line
  survivor exists, and matching on the bare ``H###`` id alone would exempt ANY
  deletion of that row whether or not the archive gained a real one. §530 then
  measured the guard refusing an H3167 close IDENTICALLY across two independent
  fresh checkouts — and the interim difflib near-match escape (ratio ≥ 0.85,
  landed earlier on 24-08-2026) misses real closes anyway, because the archived
  row APPENDS a long close summary that blows past the length slack. The
  checkable shape was there all along, one level down: treat
  ``handoffs/README.md ↔ handoffs/REGISTRY_ARCHIVE.md`` as ONE logical document.
  A row deleted from README.md counts as surviving ONLY when the SAME push adds
  to REGISTRY_ARCHIVE.md a row naming the SAME H### id AND carrying a contiguous
  verbatim fragment (≥ ``VERBATIM_FRAGMENT_MIN`` chars) of the moved row —
  recognisable from the pushed content alone, no intent guessed, scoped strictly
  to this one declared pair. One-directional: removing rows FROM the archive
  over live ones is still the pre-image shape and still blocks.

Install once per clone::

    git config core.hooksPath .githooks
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from generated_artifact_paths import GENERATED_SINGLE_WRITER_PATHS  # noqa: E402

# S27 telemetry (29-08-2026): persist every verdict to the clone's central
# firing record — the "no central firing record exists anywhere" gap of the
# S2 census, which left guard-refusal counts permanently unknown. Optional by
# design: a missing/broken logger degrades to exactly the old behaviour.
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from guard_firing_log import log_firing  # noqa: E402
except Exception:  # noqa: SE3 -- telemetry is optional; the guard is not
    log_firing = None

# H3978 (FINDINGS 685, incident H3880): this guard's remediation line is written
# for a HUMAN operator. An agent that reads "if the revert IS deliberate: <VAR>=1"
# as self-issued permission is the shape that landed eb929197aa47 on origin/main
# after six consecutive refusals on the session's own claim row. The gate renders
# the escape paragraph for whoever is actually reading it and records a refusal
# receipt so a same-session self-override can be refused at the pre-push hook.
# Unlike log_firing above, this one is NOT meant to silently degrade: the
# H3880/H3978 self-override refusal is a live safety contract, not telemetry
# (H4327). The vendored copy in this same directory guarantees it -- a HOME
# without ~/.claude/hooks or a claude-config checkout (any CI runner, for one)
# used to fall through to the old, overridable text with no warning.
guard_escape_gate = None
for _gate_dir in (Path(__file__).resolve().parent,
                  Path.home() / ".claude" / "hooks",
                  Path.home() / "Documents" / "GitHub" / "claude-config" / "hooks"):
    _gate_file = _gate_dir / "guard_escape_gate.py"
    if _gate_file.exists():
        try:
            sys.path.insert(0, str(_gate_dir))
            import guard_escape_gate  # noqa: E402
        except Exception:  # noqa: SE3 -- advisory layer, never fatal
            guard_escape_gate = None
        break


def escape_first_line(human_line: str) -> str:
    """H3978: the H3134 first-line hint, rendered for its actual reader.

    H3134 put the override on the FIRST line so a retry loop stops after one
    attempt instead of re-asking a question the refusal never depended on the
    remote tip to answer. That reason survives here -- an agent still needs the
    "retrying cannot clear this" signal on line one -- but it gets the signal
    WITHOUT a runnable override, which is what it read as permission in H3880.
    """
    if guard_escape_gate is None or guard_escape_gate.agent_caller() is None:
        return human_line
    return ("%s -- LOCAL guard refusal, not a moved remote tip. Retrying cannot "
            "clear it, and the override is a HUMAN's to issue -- see the end of "
            "this banner." % REFUSAL_MARKER)


GATE_INERT_NOTE = (
    "  NOTE: guard_escape_gate did not load (%s), so NO refusal receipt was "
    "recorded and a same-session self-override CANNOT be refused -- the "
    "H3978/H3880 protection is inert for this push. The vendored copy beside "
    "this script should make that impossible; if you are reading this line, it "
    "is missing or unimportable."
)


def escape_paragraph(human_line: str) -> str:
    """H3978: the escape hatch, rendered for its actual reader.

    A person keeps the operator command. An agent gets a refusal naming the human
    act -- report, name the shape, ask -- and no runnable override, plus a receipt
    that lets the pre-push hook refuse a self-issued override minutes later.

    The two fallbacks below SAY when they fire. Vendoring the gate (H4327) makes
    an unloadable gate very unlikely, but "very unlikely" and "visible" are
    different guarantees: the reason those nine fixtures sat red for four days is
    that an inert gate rendered a banner identical to a working one. Same
    doctrine as the pre-push hook's own "fail-open, but never silently".
    """
    if guard_escape_gate is None:
        return "%s\n%s" % (human_line, GATE_INERT_NOTE % "import failed at startup")
    try:
        guard_escape_gate.record_refusal(ESCAPE_ENV, "Uprava", REFUSAL_MARKER)
        return guard_escape_gate.refusal_hint(ESCAPE_ENV, "Uprava", human_line=human_line)
    except Exception as exc:  # noqa: SE3
        return "%s\n%s" % (human_line, GATE_INERT_NOTE % ("raised %s" % type(exc).__name__))

ESCAPE_ENV = "ALLOW_STALE_BASE_PUSH"
STRICT_ENV = "STALE_BASE_PUSH_STRICT"
MAX_LISTED = 12
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+")

# Stable, greppable — a wrapper script can `grep` this in captured stderr and
# stop retrying on the FIRST hit instead of burning its whole budget re-asking
# a question this hook's own refusal never depends on the remote tip to answer
# (H3134, FINDINGS §493). Never rename without updating any caller that greps
# it (`handoff_claims.commit_texts_to_origin` currently keys off the banner
# text "PUSH BLOCKED" instead, for the more precise reason documented above).
REFUSAL_MARKER = "STALE_BASE_GUARD_REFUSAL"

# H4342 (08-09-2026): the NON-fast-forward verdict. Emitted instead of a refusal
# when the remote tip is not an ancestor of the pushed commit — see
# `push_is_fast_forward()` and the NON-FAST-FORWARD block in the module
# docstring. Contains neither `PUSH BLOCKED` nor `pre-push: BLOCKED` on purpose:
# `handoff_claims.commit_texts_to_origin` keys `diag["guard_blocked"]` off those
# two strings, and this verdict means the exact opposite of a guard block.
NON_FF_MARKER = "STALE_BASE_NON_FF_SKIP"

# FINDINGS §543/§605: per-path work bounds. A line-level guard with unbounded
# work does not refuse, it HANGS — and a push killed mid-guard by the caller's
# timeout reports as silence, not as a blocked guard, so the author retries into
# the same hang. Past a bound the path is skipped LOUDLY (never silently) and
# the verdict degrades to ref-level merge-base verification; see the LIMITS
# block in the module docstring and report_circuit_break().
CIRCUIT_MARKER = "STALE_BASE_CIRCUIT_BREAK"
DEFAULT_MAX_BLAME_LINES = 2000
DEFAULT_MAX_NEAR_PAIRS = 300_000
DEFAULT_BLAME_TIMEOUT_SECONDS = 30


class BlameTimeout(RuntimeError):
    """The line-level guard hit its wall-clock budget for one path."""

# --- H3069: CHANGELOG tag-drift check (FINDINGS §469) ------------------------
#
# The deletion-side scan above is structurally blind to §469's incident: a clean
# rebase that ADDS a bullet inside an already-tagged `## [x.y.z]` section deletes
# nothing, so `blame_recent` has nothing to flag and the corruption lands clean.
# This is a separate ADDITIVE check alongside `scan()` — it never touches
# `blame_recent`/`surviving_text`/any exemption — scoped to changelog paths,
# sections this push actually touches, and versions that have a pushed tag.
#
# Its override is deliberately NOT reused from ESCAPE_ENV: the two refusals guard
# different risk classes (a deletion-revert vs a mutation of published release
# notes), a wrapper grepping which hatch to raise should be able to tell them
# apart, and the existing banner's own wording ("deletes lines") would be wrong
# for an addition-side refusal.
TAG_DRIFT_ENV = "ALLOW_CHANGELOG_TAG_DRIFT"
TAG_DRIFT_MARKER = "CHANGELOG_TAG_DRIFT_REFUSAL"
CHANGELOG_BASENAMES = ("CHANGELOG.md", "Changelog.md", "changelog.md")
SECTION_HEADING_RE = re.compile(r"^## \[([^\]]+)\]")


def git(*args: str, check: bool = False) -> str:
    proc = subprocess.run(
        ("git",) + args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and proc.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args), proc.stderr.strip()))
    return proc.stdout


def git_ok(*args: str) -> bool:
    """Exit-code view of a git command that prints nothing (merge-base --is-ancestor)."""
    proc = subprocess.run(
        ("git",) + args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.returncode == 0


def push_is_fast_forward(remote_ref: str, local_ref: str) -> bool:
    """True when `remote_ref` is already contained in the pushed commit.

    H4342 (08-09-2026). The whole line-level check below is only meaningful for
    a FAST-FORWARD push, and the module docstring has said so since the first
    line of it was written: "a fast-forward push always has
    ``merge-base == remote_tip``", and "Both #1516 incidents were clean
    fast-forwards". When the remote tip is NOT an ancestor of the pushed commit,
    the diff `removed_line_numbers()` computes is against a tip that is not this
    commit's parent, so every line the rival branch added since the fork shows up
    as a deletion this push "makes". It does not: the push is a non-fast-forward
    that git will refuse on its own, and on main/master a forced one is refused
    fail-closed by `scripts/pre_push_main_line_gate.py` check 2 (rewind/rewrite,
    escape ALLOW_MAIN_LINE_REWIND=1). Nothing is lost by declining to judge it.

    MEASURED, not assumed (08-09-2026). `handoff_claims.commit_texts_to_origin`
    pins `base = origin/main`, builds a commit-tree on it, then pushes; on this
    org's two most-contended files another session lands in that window often.
    The same H4339 close commit built on a base that had gone one commit stale
    was refused with 25 phantom deletions across 2 paths, and built on the
    current tip passed clean — same transforms, same content, different base.

    That race is the retry loop's normal, self-healing case, and this guard was
    converting it into `STALE_BASE_GUARD_REFUSAL` ("Retrying cannot clear it")
    plus the H3880 agent-override banner. Worse, `commit_texts_to_origin` reads
    that banner into a sticky `diag["guard_blocked"]`, so a caller that finally
    exhausted its retries reported "This is NOT origin/main moving" — the exact
    inversion of the truth. The guard's own docstring asserted the two states
    were mutually exclusive ("``--is-ancestor origin/main HEAD`` is **true** for
    this LOCAL refusal and **false** for a genuine non-fast-forward"); that is
    true for a branch push of HEAD and false for the plumbing push above, where
    the pushed ref is a detached `commit-tree` sha.

    Cost of the fix in detection power: zero for the class this guard exists to
    catch, which is fast-forward-shaped by definition. What is no longer flagged
    is a deletion inside a push that cannot land as it stands.
    """
    return git_ok("merge-base", "--is-ancestor", remote_ref, local_ref)


def blob_lines(ref: str, path: str) -> list:
    """Lines of ``path`` at ``ref``, numbered exactly as git numbers them (§695).

    NEVER ``str.splitlines()`` for anything a git line number will index into:
    it also breaks on form feed (U+000C), VT, NEL, U+2028 and U+2029, which git
    counts as ordinary characters inside a line. One stray form feed inside
    FINDINGS.md §544 shifted every later line by one, so blame line N indexed
    the text of line N-1 and EVERY content-based exemption below (survivors,
    registry bookkeeping, expired claim rows, class-5 near match) silently
    failed for the two thousand lines after it.
    """
    return git("show", "%s:%s" % (ref, path)).split("\n")


def pushed_commits(remote_ref: str, local_ref: str) -> set[str]:
    out = git("rev-list", "%s..%s" % (remote_ref, local_ref))
    return {line.strip() for line in out.splitlines() if line.strip()}


def changed_paths(remote_ref: str, local_ref: str) -> list[str]:
    out = git("diff", "--name-only", "-w", remote_ref, local_ref)
    return [p for p in out.splitlines() if p.strip()]


def removed_line_numbers(remote_ref: str, local_ref: str, path: str) -> list[int]:
    """Line numbers AT THE REMOTE TIP that this push removes or rewrites."""
    out = git("diff", "-w", "-U0", remote_ref, local_ref, "--", path)
    numbers: list[int] = []
    old_line = 0
    for line in out.splitlines():
        m = HUNK_RE.match(line)
        if m:
            old_line = int(m.group(1))
            continue
        if line.startswith("---") or line.startswith("+++"):
            continue
        if line.startswith("-"):
            numbers.append(old_line)
            old_line += 1
    return numbers


def added_line_numbers(remote_ref: str, local_ref: str, path: str) -> list[int]:
    """Line numbers IN THE PUSHED FILE that this push adds or rewrites."""
    out = git("diff", "-w", "-U0", remote_ref, local_ref, "--", path)
    numbers: list[int] = []
    new_line = 0
    for line in out.splitlines():
        # The plus side of the hunk header carries the NEW start; HUNK_RE above
        # captures only the minus side, so this needs its own pattern.
        hm = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)", line)
        if hm:
            new_line = int(hm.group(1))
            continue
        if line.startswith("---") or line.startswith("+++"):
            continue
        if line.startswith("+"):
            numbers.append(new_line)
            new_line += 1
    return numbers


_HEX = set("0123456789abcdef")


def blame_map(remote_ref: str, path: str,
              timeout_seconds: int = DEFAULT_BLAME_TIMEOUT_SECONDS) -> dict[int, list]:
    """Introducing [sha, author, time] of EVERY line of `path` at the remote tip,
    from ONE git blame invocation.

    §543/§605: the original loop paid one `git blame -L n,n` subprocess per
    removed line — 28k subprocesses on a wholesale derived-JSON rewrite, each
    re-parsing a multi-megabyte file. One batched `--line-porcelain` blame per
    path returns the identical per-line answer (same `-w`, same tip) at
    O(file) total. Keyed by the FINAL line number at the remote tip; lines git
    did not report (binary, unreadable) are simply absent — callers skip them,
    exactly as the per-line form did on empty output.
    """
    try:
        proc = subprocess.run(
            ("git", "blame", "-w", "--line-porcelain", remote_ref, "--", path),
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        raise BlameTimeout(
            "%s exceeded %ss" % (path, timeout_seconds)
        ) from exc
    out = proc.stdout
    result: dict[int, list] = {}
    cur: list | None = None
    for line in out.splitlines():
        if not line or line.startswith("\t"):
            continue
        parts = line.split()
        # Porcelain header: "<40-hex sha> <orig_lineno> <final_lineno> [<group>]".
        if parts and len(parts[0]) == 40 and set(parts[0]) <= _HEX:
            sha = parts[0]
            try:
                lineno = int(parts[2])
            except (IndexError, ValueError):
                lineno = 0
            cur = result.setdefault(lineno, [sha, "", None])
            cur[0] = sha
            continue
        if cur is None:
            continue
        if line.startswith("author "):
            cur[1] = line[len("author "):].strip()
        elif line.startswith("author-time "):
            try:
                cur[2] = datetime.fromtimestamp(int(line.split()[1]),
                                                tz=timezone.utc)
            except (ValueError, IndexError):
                cur[2] = None
    return result


def changelog_sections(text: str) -> list[tuple[str, int, int]]:
    """[(version, body_start0, body_end0_exclusive)] for each `## [v]` heading.

    A section's body is everything from the line after its heading down to (not
    including) the next `## [` heading, or EOF. `[Unreleased]` parses like any
    other bracket token and is filtered later by the tag lookup.
    """
    lines = text.split("\n")
    heads: list[tuple[str, int]] = []
    for i, ln in enumerate(lines):
        m = SECTION_HEADING_RE.match(ln)
        if m:
            heads.append((m.group(1).strip(), i))
    sections: list[tuple[str, int, int]] = []
    for j, (ver, hidx) in enumerate(heads):
        end = heads[j + 1][1] if j + 1 < len(heads) else len(lines)
        sections.append((ver, hidx + 1, end))
    return sections


def posix_basename(path: str) -> str:
    """Basename across BOTH separators — §469 gate 1.

    The inline form this replaces read ``replace("\\\\", "/")`` — a
    TWO-character literal that never matches a real Windows path, so every
    backslash-separated CHANGELOG path silently skipped the whole tag-drift
    check (H3587 wave-2 delta review; found by reading, pinned here so the
    two-char spelling cannot creep back).
    """
    return path.replace("\\", "/").split("/")[-1]


def changelog_tag_drift(remote_ref: str, local_ref: str,
                        max_paths: int) -> list[dict]:
    """Sections this push mutates under a version that already has a pushed tag.

    Returns one dict per drifted section:
        {"path": ..., "tag": "vx.y.z", "version": ..., "heading": ...,
         "lines": [(pushed_line_no, kind), ...]}
    where kind is "added" or "changed" relative to `git show <tag>:<path>`.

    Fail-open on everything it cannot verify: no local tag object, a tag blob
    that lacks the file entirely, an unparseable diff — none of these block,
    because a guard that refuses pushes it cannot reason about gets switched
    off (the stale-base sibling's own demotion lesson). Only a verified,
    byte-level difference between the pushed section and the tagged section
    refuses.
    """
    findings: list[dict] = []
    for path in changed_paths(remote_ref, local_ref)[:max_paths]:
        if posix_basename(path) not in CHANGELOG_BASENAMES:
            continue
        added = added_line_numbers(remote_ref, local_ref, path)
        if not added:
            continue  # nothing inserted/rewritten by THIS push: deletion-side scan's job
        pushed_lines = blob_lines(local_ref, path)
        for ver, b0, b1 in changelog_sections("\n".join(pushed_lines)):
            touched = [n for n in added if b0 <= n <= b1]
            if not touched:
                continue  # untouched section: never diffed (170+ sections must not cost)
            tag = "v%s" % ver.split()[0].lstrip("v")
            if not git("rev-parse", "--verify", "--quiet",
                       "refs/tags/%s" % tag).strip():
                continue  # [Unreleased], untagged versions: allowed by design
            tag_blob = git("show", "%s:%s" % (tag, path))
            if not tag_blob.strip():
                continue  # file absent at the tag: unverifiable, fail open
            tag_sections = {v: (s0, s1) for v, s0, s1 in
                            changelog_sections(tag_blob)}
            tag_lines = tag_blob.split("\n")
            if ver in tag_sections:
                t0, t1 = tag_sections[ver]
                tag_body = tag_lines[t0:t1]
            else:
                tag_body = []  # section created after tagging: whole body is drift
            pushed_body = pushed_lines[b0:b1]
            sm = difflib.SequenceMatcher(a=tag_body, b=pushed_body, autojunk=False)
            drift: list[tuple[int, str]] = []
            for op, i0, i1, j0, j1 in sm.get_opcodes():
                if op == "equal":
                    continue
                kind = "changed" if op == "replace" else "added"
                for k in range(j0, j1):
                    drift.append((b0 + k + 1, kind))
            if drift:
                heading = pushed_lines[b0 - 1].strip() if b0 - 1 < len(pushed_lines) else ver
                findings.append({"path": path, "tag": tag, "version": ver,
                                 "heading": heading, "lines": drift})
    return findings


def report_tag_drift(findings: list[dict]) -> None:
    total = sum(len(f["lines"]) for f in findings)
    e = sys.stderr
    print("", file=e)
    print("%s — LOCAL guard refusal, not a moved remote tip." % TAG_DRIFT_MARKER,
          file=e)
    print("  Override:  %s=1 git push ..." % TAG_DRIFT_ENV, file=e)
    print("PUSH BLOCKED — this push adds or changes %d line(s) inside "
          "CHANGELOG.md section(s) already published under a pushed tag, in "
          "%d section(s)." % (total, len(findings)), file=e)
    print("FINDINGS §469: a silent ADDITION inside a tagged section deletes "
          "nothing, so the deletion-side check above cannot see it; a released "
          "section must stay byte-identical to its tag.", file=e)
    print("", file=e)
    shown = 0
    for f in findings:
        print("  %s" % f["path"], file=e)
        print("      %s  (tag %s)" % (f["heading"], f["tag"]), file=e)
        for ln, kind in f["lines"]:
            if shown >= MAX_LISTED:
                break
            print("          line %-6d %s vs %s:CHANGELOG.md"
                  % (ln, kind, f["tag"]), file=e)
            shown += 1
        if shown >= MAX_LISTED:
            print("          …", file=e)
            break
    print("", file=e)
    print("If the change IS deliberate (fixing the section's prose, never its "
          "meaning):  %s=1 git push ..." % TAG_DRIFT_ENV, file=e)
    print("", file=e)


STUB_MARKER = "STUB claimed by mint_handoff.py"


def changelog_structure_findings(text: str) -> list[dict]:
    """Structural collisions in a CHANGELOG body: duplicate headings + order.

    The #2335 release-rebase collision (29-08-2026) inserted `## [0.195.347]`
    ABOVE the then-[Unreleased] block, so later appends landed inside a tagged
    section AND a duplicate `## [0.195.347]` heading materialised further
    down. The tag-drift check above only fires when THIS push adds lines into
    a tagged section — it is silent on a layout that is ALREADY broken and on
    a heading duplicated by a bad merge. Both shapes are verified here from
    the pushed text alone, no tag lookup needed:

      - duplicate-heading: the same `## [v]` token appears twice — one of the
        two bodies is unreachable by any reader or tool (`changelog_sections`
        itself keeps only the LAST occurrence).
      - order-violation: version sections do not strictly descend
        (`[Unreleased]` first, then newest → oldest). The collision shipped
        …349, 347, 348… — a shape no correct history produces.

    Pure function; the caller scopes it to changed CHANGELOG paths.
    """
    findings: list[dict] = []
    lines = text.split("\n")
    heads: list[tuple[str, int]] = []
    for i, ln in enumerate(lines):
        m = SECTION_HEADING_RE.match(ln)
        if m:
            heads.append((m.group(1).strip(), i))
    seen: dict[str, int] = {}
    for ver, i in heads:
        if ver in seen:
            findings.append({"kind": "duplicate-heading", "version": ver,
                             "line": i + 1,
                             "first_line": seen[ver] + 1})
        else:
            seen[ver] = i

    def rank(ver: str):
        if ver == "Unreleased":
            return (0, [])
        nums = [int(x) for x in re.findall(r"\d+", ver)]
        return (1, [-n for n in nums])

    ranked = [(rank(ver), ver, i + 1) for ver, i in heads
              if ver != "Unreleased"]
    for a, b in zip(ranked, ranked[1:]):
        if not (a[0] < b[0]):
            findings.append({"kind": "order-violation",
                             "version": "%s then %s" % (a[1], b[1]),
                             "line": b[2], "first_line": a[2]})
    return findings


def rank_key_lt(a, b) -> bool:
    """Strictly-less for the (group, negated-nums) rank tuples."""
    return a < b


def changelog_structure_path_findings(remote_ref: str, local_ref: str,
                                      max_paths: int) -> list[tuple[str, list[dict]]]:
    """Structural findings per changed CHANGELOG path in THIS push.

    Same changed-path scoping as `changelog_tag_drift` (a push that never
    touches a changelog never pays for the check); runs the pure
    `changelog_structure_findings` on the pushed content. Returns
    [(path, findings)] for paths with at least one finding.
    """
    out: list[tuple[str, list[dict]]] = []
    for path in changed_paths(remote_ref, local_ref)[:max_paths]:
        if posix_basename(path) not in CHANGELOG_BASENAMES:
            continue
        pushed = git("show", "%s:%s" % (local_ref, path))
        if not pushed.strip():
            continue  # file deleted in this push: not this check's class
        f = changelog_structure_findings(pushed)
        if f:
            out.append((path, f))
    return out


def report_structure_drift(findings: list[dict], path: str) -> None:
    e = sys.stderr
    print("", file=e)
    print("%s — LOCAL guard refusal, not a moved remote tip." % TAG_DRIFT_MARKER,
          file=e)
    print("  Override:  %s=1 git push ..." % TAG_DRIFT_ENV, file=e)
    print("PUSH BLOCKED — %s is structurally broken in this push: "
          "%d finding(s)." % (path, len(findings)), file=e)
    print("FINDINGS (29-08-2026 #2335 collision): a duplicated `## [v]` "
          "heading or a non-descending section order means a release rebase "
          "or a bad merge lodged content inside a tagged section — the "
          "tag-drift check cannot see a layout that is already broken or a "
          "duplicate heading, so this shape-level check refuses.", file=e)
    print("", file=e)
    shown = 0
    for f in findings:
        if shown >= MAX_LISTED:
            print("          …", file=e)
            break
        print("      line %-6d %s: %s (first occurrence line %d)"
              % (f["line"], f["kind"], f["version"], f["first_line"]), file=e)
        shown += 1
    print("", file=e)
    print("If the change IS deliberate (repairing the leaked layout):  "
          "%s=1 git push ..." % TAG_DRIFT_ENV, file=e)
    print("", file=e)


def surviving_text(local_ref: str, path: str) -> set[str]:
    """Every non-blank stripped line of the path as this push would leave it.

    Used to separate a MOVE from a LOSS. Renumbering a changelog section, resolving a
    merge by relocating someone's rows, reordering a table — all delete lines at their
    old position and re-add them elsewhere. The remote keeps the content, so there is
    nothing to protect. Only a line whose text survives NOWHERE in the pushed file is a
    real deletion. (Found by dogfooding: the guard blocked its own landing commit for
    exactly this, which is the false-positive class that gets a blocking hook disabled.)
    """
    out = git("show", "%s:%s" % (local_ref, path))
    return {ln.strip() for ln in out.splitlines() if ln.strip()}


# H3134: a card evicted from GTD_NEXT_ACTIONS.md by `gtd_active_state.py
# --migrate` is written verbatim into GTD_ARCHIVE.md in the SAME commit — see
# the module docstring's exemptions section for why this qualifies (verbatim
# survivor). Scoped to declared pairs on purpose: widening to "any two files
# touched by the same push" would let the survivors check quietly absorb an
# unrelated file's coincidental text match.
CROSS_FILE_ARCHIVE_PAIRS = {
    "gtd_next_actions.md": "GTD_ARCHIVE.md",
}

# FINDINGS §450/§530 (H3253): the two halves of the handoff registry are ONE
# logical document — a close MOVES a row from the live half to the archive
# half. Unlike the GTD pair above, survivor credit is gated on the SAME push:
# only lines this push ADDS to REGISTRY_ARCHIVE.md count, so a stale checkout
# that merely drops someone's fresh row gains no credit from rows archived
# long ago. One-directional by construction — see relocated_registry_rows()
# for the rewritten-status-cell shape; un-archiving over live rows blocks.
# Keys are case-folded for dispatch; values are exact Git tree paths.
# Git pathspecs remain case-sensitive on Windows. Lowercasing the value made
# real archive moves invisible while the old lowercase-only fixtures passed.
REGISTRY_RELOCATION_PAIR = {"handoffs/readme.md": "handoffs/REGISTRY_ARCHIVE.md"}

# FINDINGS §659 (03-09-2026): a release cut CONSUMES changelog_queue/*.md — each
# fragment's bullet is copied into CHANGELOG.md and the fragment file is deleted in
# the SAME commit (cut_release.py, H3833). Every fragment another session queued in
# the last --recent-days is therefore deleted by construction, so EVERY release push
# refuses (measured on v0.195.419: 35 lines across 33 files), and the only way out
# was the human-addressed override — routine work behind an override is the reflex
# §641/§643 warn about. This is a MOVE, not a loss: the bullet is right there in the
# pushed CHANGELOG.md, which is exactly what surviving_text() exists to recognise,
# only across paths. A directory prefix rather than a dict key because the queue is
# a glob of many one-entry files, and one-directional: fragments feed the changelog,
# never the reverse.
CHANGELOG_QUEUE_PREFIX = "changelog_queue/"

# §530 bar: a shorter shared run is noise — ids, pipes, "| Sonnet | x |"
# boilerplate recur across unrelated rows — while 40+ contiguous chars are
# unique to the moved row. A line shorter than the bar can never claim the
# fragment exemption.
VERBATIM_FRAGMENT_MIN = 40


def has_verbatim_fragment(text: str, candidates) -> bool:
    """True when >= VERBATIM_FRAGMENT_MIN contiguous chars of `text` appear
    verbatim inside one of `candidates`.

    The §437 bar made mechanical: recognisable from the pushed content alone,
    no intent guessed. Survives the status-cell rewrite a close performs,
    because the title/link/repo cells move over untouched."""
    if len(text) < VERBATIM_FRAGMENT_MIN:
        return False
    n = VERBATIM_FRAGMENT_MIN
    for cand in candidates:
        for i in range(len(text) - n + 1):
            if text[i:i + n] in cand:
                return True
    return False


def cross_file_survivors(remote_ref: str, local_ref: str, path: str) -> set[str]:
    """Lines of `path`'s declared sibling archive that count as survivors.

    GTD pair: every non-blank stripped line of the sibling AS THIS PUSH WOULD
    LEAVE IT — the migration always rewrites the archive in the same commit,
    so the pushed tree IS the same-push evidence. Registry pair (§530): only
    the lines THIS PUSH ADDS to REGISTRY_ARCHIVE.md, so an archive untouched
    by the push credits nothing. The changelog queue (§659) is NOT here, on
    purpose: its credit is an equality test taken before blame, because this set
    also feeds class 5's near match — see `promoted_queue_lines`. Empty set if
    `path` has no declared sibling.
    """
    key = path.replace("\\", "/").lower()
    sibling = CROSS_FILE_ARCHIVE_PAIRS.get(key)
    if sibling:
        out = git("show", "%s:%s" % (local_ref, sibling))
        return {ln.strip() for ln in out.splitlines() if ln.strip()}
    if key in REGISTRY_RELOCATION_PAIR:
        return set(added_line_texts(remote_ref, local_ref,
                                    REGISTRY_RELOCATION_PAIR[key]))
    return set()


# handoffs/H123-foo.md -> handoffs/archive/H123-foo.md, in a path or a full blob URL.
# Negative lookahead so an already-archived link is left alone (the transform must be
# idempotent, or a second archive pass would stop matching).
ARCHIVE_REPOINT_RE = re.compile(r"(handoffs/)(?!archive/)(H\d+[^)\s\"'<>]*\.md)")


def archive_normalized(text: str) -> str:
    """Collapse the pre- and post-archive spelling of a handoff link to one form.

    Class 3 of the known false positives: `handoff_close.py` archiving a handoff
    repoints every `handoffs/X.md` reference to `handoffs/archive/X.md`, including
    inside registry rows another session added minutes ago. The row is NOT lost —
    only its link is repointed — but the raw text no longer matches, so the
    surviving-text check in `blame_recent` cannot see it as a move.

    Normalizing the REMOVED line makes that visible: it is exempt only when its
    text, once the repoint is applied, still exists verbatim in the pushed file. A
    push that repoints a link AND drops anything else on the line does not match,
    so this forgives exactly the archive rewrite and nothing more.

    ONE DIRECTION ONLY — do not also normalize the survivors. Un-archiving someone's
    link (pushing `handoffs/X.md` over their `handoffs/archive/X.md`) is the exact
    pre-image revert this guard exists to catch, and it is what the test's own case 1
    does. Normalizing both sides makes the two indistinguishable and silently forgives
    the real defect; the lookahead above is what keeps the transform one-way.
    """
    return ARCHIVE_REPOINT_RE.sub(r"\1archive/\2", text)


# The two halves of the handoff registry. Scoped deliberately: the "Last updated"
# shape below appears in EVERY authored .md in the org, and exempting it globally
# would let a session silently revert someone's date bump.
REGISTRY_PATHS = ("handoffs/readme.md", "handoffs/registry_archive.md")

# FINDINGS §695 (03-09-2026): every FINDINGS.md append necessarily rewrites the
# file's single trailing marker line `§N takes the next number.` — the number is
# consumed and bumped by the very act of appending. That line is therefore
# deleted-and-replaced on EVERY append, so every append trips this guard the same
# way §659 measured every release push tripping it, and a guard overridden on
# routine work trains the override reflex it exists to prevent (§641/§643 class).
#
# One-directional, and readable from the pushed content alone per the §437 bar:
# exempt ONLY when the same push leaves a marker whose number is STRICTLY
# GREATER. A stale checkout reinstalling a pre-image marker moves the number
# backwards (or leaves it equal) and still blocks — that is precisely the H1516
# shape. The match is anchored and whole-line, so a push that rewrites the marker
# into anything else gains no exemption, and every other line stays fully guarded.
FINDINGS_BASENAMES = ("findings.md",)
FINDINGS_MARKER_RE = re.compile(r"^§(\d+) takes the next number\.$")


def findings_marker_bump(path: str, text: str, survivors: set) -> bool:
    """The FINDINGS next-number marker, consumed by an append (§695).

    ``text`` is the removed line; ``survivors`` is every stripped line of the
    file as this push would leave it. True only when both are the marker and the
    surviving number is strictly greater — a bump forward, never a rollback.
    """
    norm = path.replace("\\", "/").lower()
    if not any(norm.endswith(b) for b in FINDINGS_BASENAMES):
        return False
    removed = FINDINGS_MARKER_RE.match(text.strip())
    if removed is None:
        return False
    old = int(removed.group(1))
    for line in survivors:
        kept = FINDINGS_MARKER_RE.match(line)
        if kept is not None and int(kept.group(1)) > old:
            return True
    return False


# Lines `registry_check.apply_fix` REGENERATES on every close: the dated header, the
# next-free-ID marker, the counts line, and each bucket header's `(N)`.
REGISTRY_BOOKKEEPING_RES = (
    re.compile(r"^_Created:.*Last updated:.*_$"),
    re.compile(r"^\*\*Next free ID:"),
    re.compile(r"^\*\*Counts:\*\*"),
    re.compile(r"^##\s+.*\(\d+\)\s*$"),
)


# The Active Claims ledger. Its rows are written by `claim_handoff.py`, aged out by
# wall-clock TTL, and removed by `sweep_expired_claims.py` — nobody authors one.
CLAIM_LEDGER_PATHS = ("next_task_queue.md",)

# `| H3001 | multi | exec · Opus 5 (claude-opus-5) · pid28180 | <claimed ISO> | <expires ISO> |`
# Anchored to the whole five-cell shape INCLUDING both timestamps, so no other line in
# that file (the denylist, prose, headers) can match it.
CLAIM_ROW_RE = re.compile(
    r"^\|\s*H\d+\s*\|[^|]*\|[^|]*\|\s*(?P<claimed>\d{4}-\d{2}-\d{2}T[\d:]+Z)\s*"
    r"\|\s*(?P<expires>\d{4}-\d{2}-\d{2}T[\d:]+Z)\s*\|\s*$"
)


def is_expired_claim_row(path: str, text: str, now: datetime | None = None) -> bool:
    """An Active-Claims ledger row whose TTL has ALREADY run out.

    Class (b) of the §437 family, measured 18-08-2026. A claim row expires on a
    6-hour TTL but this guard protects any line for 3 days, so for ~2.5 days a row
    is simultaneously **expired** (the ledger says it is free) and **protected**
    (this guard says deleting it is a silent revert). In that window
    ``sweep_expired_claims.py`` — the org's only sanctioned release path, which has
    no ``--force`` and sets no escape — cannot land, and releasing a dead claim
    requires ``ALLOW_STALE_BASE_PUSH=1`` on entirely routine hygiene. That is the
    exact false-positive shape that got this guard demoted to a warning once before.

    Exempt because the row is **derived, and already dead by its own timestamp**: it
    is a lease, its content is reconstructible by re-claiming, and losing one
    destroys no work.

    The expiry check is the load-bearing half and is not optional. An **unexpired**
    row still blocks, because deleting a live claim is how two sessions end up in one
    tree (H214) — the incident this ledger exists to prevent. Whoever widens this must
    keep that case red.
    """
    norm = path.replace("\\", "/").lower()
    if not any(norm.endswith(p) for p in CLAIM_LEDGER_PATHS):
        return False
    m = CLAIM_ROW_RE.match(text.strip())
    if not m:
        return False
    try:
        expires = datetime.strptime(m.group("expires"), "%Y-%m-%dT%H:%MZ")
    except ValueError:
        try:
            expires = datetime.strptime(m.group("expires"), "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            return False  # unparseable expiry -> never exempt, fail closed
    return expires.replace(tzinfo=timezone.utc) <= (now or datetime.now(timezone.utc))


def is_registry_bookkeeping(path: str, text: str) -> bool:
    """A generated bookkeeping line in the handoff registry — recomputed, never authored.

    Class (a) of FINDINGS §437, and the last false positive that forced
    ``ALLOW_STALE_BASE_PUSH=1`` on routine work. ``registry_check.apply_fix`` rewrites
    the dated header, the next-free-ID marker, the ``**Counts:**`` line and every
    bucket header's ``(N)`` on EVERY close. Two closes inside the 3-day window
    therefore always look like each other's revert, because both legitimately rewrite
    the same four lines — and §435 measured that blocking BOTH sanctioned close paths
    under ordinary push traffic.

    Exempt because these lines are **derived**, not authored: their content is a
    function of the rows around them, so a close that recomputes them destroys no
    work, and a close that gets them wrong is caught by ``registry_check`` rather
    than by this guard. Handoff ROWS are not covered — a row is real content, and
    losing one is exactly the §1516 defect.
    """
    norm = path.replace("\\", "/").lower()
    if not any(norm.endswith(p) for p in REGISTRY_PATHS):
        return False
    stripped = text.strip()
    return any(rx.match(stripped) for rx in REGISTRY_BOOKKEEPING_RES)


def is_generated_single_writer(path: str) -> bool:
    """A declared generated artifact with exactly one writer (H3073).

    Every path in `tools.generated_artifact_paths.GENERATED_SINGLE_WRITER_PATHS`
    is replaced WHOLESALE by its own `--land` caller via
    `handoff_claims.commit_texts_to_origin` — never hand-edited, never
    concurrently authored. A whole-file replacement therefore destroys no work
    regardless of how many lines it deletes, so the whole path is exempt
    rather than trying to pattern-match individual regenerated lines the way
    `is_registry_bookkeeping` does for the registry. Keyed on the DECLARATION
    in that shared module, never on "the pushing script looked automated" —
    widening this must add a path there, not loosen the check here.
    """
    norm = path.replace("\\", "/")
    return norm in GENERATED_SINGLE_WRITER_PATHS


def is_mint_stub(remote_ref: str, path: str) -> bool:
    """A freshly minted handoff skeleton being filled in the same pass.

    `mint_handoff.py` lands a placeholder body on origin/main, then the session that
    minted it replaces those placeholders with real content — a legitimate rewrite of
    lines that are, by construction, minutes old and authored outside the push.
    """
    if "/handoffs/" not in "/" + path.replace("\\", "/"):
        return False
    return STUB_MARKER in git("show", "%s:%s" % (remote_ref, path))


# FINDINGS §457: the live mint_handoff.py claim subjects (checked against
# origin/main history 24-08-2026) — single and batch range forms.
MINT_SUBJECT_RE = re.compile(r"^mint: claim\s+(?P<spec>H\d+(?:\.\.H\d+)?)\b")
# FINDINGS §557: the OTHER machine-generated writer of lines a close erases.
# `handoff.py claim` / `claim_handoff.py` write the queue's Active-Claims row,
# and `handoff_close.py` drops it again — a pair exactly as symmetric as
# mint→close, but with a different subject, so §457's gate 1 never matched it
# and every claim→close was routed through ALLOW_STALE_BASE_PUSH=1. Three live
# forms (handoff_claims.py:339/875, claim_handoff.py:311, all present in
# origin/main history 26-08-2026):
#     exec-claim: H#### (<repo>) claimed by <tier> (marker+ledger)
#     exec-claim: H#### CLAIMED by <tier> (marker only)
#     exec-claim: H#### (<repo>) executing (ledger mirror)
# Claims are always a SINGLE handoff — no batch-range form, deliberately, so a
# non-handoff claim subject (`exec-claim: /skill-drain slice …`) captures
# nothing and stays blocked.
CLAIM_SUBJECT_RE = re.compile(r"^exec-claim:\s+(?P<spec>H\d+)\b")
HID_RE = re.compile(r"H\d+")


def _expand_mint_spec(spec: str) -> set[str]:
    """`H3423` -> {H3423}; `H3428..H3431` -> every id in the inclusive range."""
    if ".." in spec:
        lo_s, hi_s = spec.split("..", 1)
        try:
            lo, hi = int(lo_s[1:]), int(hi_s[1:])
        except ValueError:
            return {spec}
        if hi < lo or hi - lo > 200:  # absurd range -> never trust it wholesale
            return set()
        return {"H%d" % n for n in range(lo, hi + 1)}
    return {spec}


_MINT_HIDS_CACHE: dict[str, frozenset[str]] = {}


def mint_subject_hids(sha: str) -> frozenset[str]:
    """H###s the commit MINTED or CLAIMED, from its subject alone.

    Empty set = neither a mint nor a claim commit. Cached: blame can hit the
    same sha for many lines of one push.

    Both writers count (FINDINGS §557). A guard that exempts a
    machine-generated write has to enumerate EVERY writer of that class: the
    untreated members are not safer, they are permanently routed through the
    manual override, which trains the override into a reflex and defeats the
    guard. Widen here by adding a subject regex, never by loosening gates 2/3
    in ``is_same_session_mint_close`` — those are what keep the H1516
    stale-pre-image class out.
    """
    if sha not in _MINT_HIDS_CACHE:
        subject = git("log", "-1", "--format=%s", sha).strip()
        m = MINT_SUBJECT_RE.match(subject) or CLAIM_SUBJECT_RE.match(subject)
        _MINT_HIDS_CACHE[sha] = frozenset(_expand_mint_spec(m.group("spec"))) \
            if m else frozenset()
    return _MINT_HIDS_CACHE[sha]


def is_same_session_mint_close(text: str, sha: str,
                               push_hids: frozenset[str],
                               path: str | None = None) -> bool:
    """The removed line is THIS handoff's own mint or claim — §457, §557.

    Measured 18-08-2026 closing H3060 minutes after minting it: the close
    rewrites the very registry row / body lines the mint commit added minutes
    earlier, so the blame hits a fresh, non-pushed commit and the guard refused
    EVERY same-session mint→close (cleared each time with ALLOW_STALE_BASE_PUSH=1;
    cb0acd668 was one). §455(b)'s mint exemption lives in the DUPLICATE-push
    guard and inspects commit SUBJECTS — two guards, two data sources, so it
    never covered this one.

    Measured again 26-08-2026 closing H3541 minutes after CLAIMING it: gates 2
    and 3 held verbatim, and only gate 1 failed, because the row erased was the
    Active-Claims row written by `handoff.py claim` (`exec-claim: H3541 …`)
    rather than by `mint_handoff.py`. Same shape, second writer — FINDINGS §557.

    Measured THIRD on 27-08-2026 closing H3587 (this file's own landing): the
    id never appears in the REMOVED LINES AT ALL, because a spec-filled-at-mint
    stub ships WITHOUT the "STUB claimed by" marker (so ``is_mint_stub`` sees a
    filled file) and its placeholder body lines carry no H### token (so gate 2's
    text scan found nothing). The fill of such a stub was therefore refused
    unless ``path`` linking below exists. ``path`` extends gate 2 narrowly:
    an id counts as named when it appears in THIS changed path's basename,
    which by construction means the file being rewritten IS the minted
    artifact — the abuse surface someone else's unrelated fresh file would
    need its name to carry a foreign minted id.

    Exempt only when ALL THREE hold, so the H1516 pre-image class cannot dress
    up as a close:
      1. the blamer commit's subject is a mint claim (`mint: claim H#### stub`,
          incl. the `H####..H####` batch form) or an exec-claim
         (`exec-claim: H#### …`, added 26-08-2026 — FINDINGS §557);
      2. the removed line — or, since the H3587 measurement, this changed
         path's basename — NAMES one of those minted H###s;
      3. THIS PUSH also names that H### somewhere (a changed path's basename or
          an added line) — i.e. we are visibly working ON that handoff, not
         reverting someone else's just-minted stub wholesale. A stale checkout
         that reinstalls pre-mint content deletes the row without touching
         anything else named H####, and stays blocked.
    """
    minted = mint_subject_hids(sha)
    if not minted:
        return False
    named = set(HID_RE.findall(text))
    if path:
        named |= set(HID_RE.findall(os.path.basename(path)))
    return bool(named & minted & push_hids)


# GTD 0x (H4265 close incident, 06-09-2026): the ONE provenance signal shared by
# every handoff-lane writer — mint, exec-claim, fanout-fill and close subjects
# all carry their H### ids. ``mint_subject_hids`` above only admits the two
# machine writers; this cache admits ANY subject naming a handoff id, and is
# consumed ONLY by ``is_same_lane_close_prep``, whose verdict downgrades the
# block to a loud warning instead of exempting silently.
_SUBJECT_HIDS_CACHE: dict[str, frozenset[str]] = {}


def subject_hids(sha: str) -> frozenset[str]:
    """Every H### named in the commit's subject — the lane marker, any writer."""
    if sha not in _SUBJECT_HIDS_CACHE:
        subject = git("log", "-1", "--format=%s", sha).strip()
        _SUBJECT_HIDS_CACHE[sha] = frozenset(HID_RE.findall(subject))
    return _SUBJECT_HIDS_CACHE[sha]


def is_same_lane_close_prep(path: str, sha: str,
                            push_hids: frozenset[str]) -> bool:
    """Class (10): the removed line is a handoff file's own close-prep work.

    All three gates are content-checkable (the §437 bar — no intent guessed):

      1. the changed path IS a handoff file whose BASENAME names an H###
         (``handoffs/H4265-*.md``, active or ``handoffs/archive/``). Registry,
         GTD, FINDINGS and every other path never satisfy this gate and keep
         the hard block;
      2. the blaming commit's subject names that SAME H### (8b5fbda named
         H4265 in "… H4261–H4265 S1–S5 …"; close commits name theirs in
         "docs: close H4265 — …"). A subject naming no handoff id fails here
         and the line stays a hard block (case 20b);
      3. THIS PUSH visibly works on that same H### (a changed path's basename
         or an added line names it) — the close/fill/re-open shape, not a
         drive-by edit of an unrelated file.

    NOT a silent exemption: the caller collects these into the warned bucket,
    prints every line under ``stale-base guard: WARNING`` and ALLOWS the push
    (MG 06-09-2026: «Флип разрешить»). A stale checkout reverting another
    session's lines inside the same handoff file also warns instead of
    blocking — that is the accepted cost, bounded to the one file whose name
    carries the id, and the reason the class is a warning, never a ``continue``
    toward silence.
    """
    norm = path.replace("\\", "/")
    if "/handoffs/" not in "/%s" % norm:
        return False
    m = HID_RE.search(posix_basename(norm))
    if not m:
        return False
    hid = m.group(0)
    return hid in subject_hids(sha) and hid in push_hids


def blame_recent(remote_ref: str, path: str, lines: list[int],
                 cutoff: datetime, ours: set[str],
                 survivors: set[str],
                 pre_cache: dict | None = None,
                 push_hids: frozenset[str] = frozenset(),
                 blame: dict[int, list] | None = None,
                 near_budget: list[int] | None = None,
                 lane_warns: list[dict] | None = None,
                 ) -> tuple[list[tuple[int, str, str]], list[dict], bool]:
    """(hits, modifications, overflow) for removed lines added recently by
    someone else.

    ``hits`` are true losses — block. ``modifications`` are class-5 forward edits
    (near-match replacement whose text never existed before the blamed commit) —
    exempt with a note. ``lane_warns``, when given, collects class-10 same-lane
    close-prep lines: they do NOT block; the caller reports them as a loud
    warning and allows the push (GTD 0x, MG «Флип разрешить» 06-09-2026).
    ``blame`` is the batched per-path map from ``blame_map``;
    ``near_budget`` is a one-element mutable counter shared across the path's
    class-5 comparisons. ``overflow`` is True when that budget ran out mid-path —
    the caller turns the path into an explicit uncheckable verdict (§543/§605)
    rather than silently skipping the rest or grinding on for hours.
    """
    hits: list[tuple[int, str, str]] = []
    mods: list[dict] = []
    overflow = False
    old_text = blob_lines(remote_ref, path)
    if pre_cache is None:
        pre_cache = {}
    if blame is None:
        blame = blame_map(remote_ref, path)
    if near_budget is None:
        near_budget = [DEFAULT_MAX_NEAR_PAIRS]
    for ln in lines:
        info = blame.get(ln)
        if info is None:
            continue
        sha, author, when = info[0], info[1], info[2]
        # Moved, not lost: the same text is still somewhere in the pushed file —
        # either verbatim, or with its handoff link repointed to archive/ (class 3).
        stripped = ""
        if 1 <= ln <= len(old_text):
            stripped = old_text[ln - 1].strip()
            # A removed BLANK line carries no authored content, so there is
            # nothing for the H1516 revert class to destroy. Everywhere below,
            # an empty ``stripped`` already disables every exemption AND the
            # class-5 near-match, so such a line fell straight through to the
            # recency test and blocked on its own — a pure false positive.
            # Measured (§659): after the queue exemption landed, the ONE line
            # still refusing the v0.195.419 cut was the blank between a
            # fragment's ``### Added`` header and its bullet.
            if not stripped:
                continue
            if stripped in survivors or archive_normalized(stripped) in survivors:
                continue
            # Derived registry bookkeeping (counts, marker, dated header, bucket
            # headers): regenerated by every close, so a rewrite destroys no work.
            if is_registry_bookkeeping(path, stripped):
                continue
            # The FINDINGS next-number marker, bumped forward by an append: it is
            # consumed by construction, and the number only ever moves up (§695).
            if findings_marker_bump(path, stripped, survivors):
                continue
            # An Active-Claims row that is ALREADY past its own TTL: a dead lease,
            # not authored content. An unexpired row is NOT exempt and still blocks.
            if is_expired_claim_row(path, stripped):
                continue
        if sha in ours:
            continue
        # FINDINGS §457: the line is the fresh footprint of THIS handoff's own
        # mint (same-session mint→close). Verified against the three gates in
        # is_same_session_mint_close — the H1516 stale-pre-image class does not
        # satisfy gate 3 and still blocks below.
        if stripped and is_same_session_mint_close(stripped, sha, push_hids,
                                                   path=path):
            continue
        # CLASS 10 (GTD 0x, H4265): the line belongs to the SAME handoff file's
        # own close-prep — the blaming commit's subject names the file's H###.
        # Downgraded to a LOUD warning, never a silent pass: collected into
        # ``lane_warns`` and reported by report() while the push is allowed.
        if stripped and lane_warns is not None \
                and is_same_lane_close_prep(path, sha, push_hids):
            lane_warns.append({"line": ln, "sha": sha[:9], "author": author})
            continue
        # CLASS 5: a near-match survivor whose text history has never seen before
        # this commit's parent is a forward edit on top of their line, not a loss.
        if stripped:
            tied: list[str] = []
            best, ovf = best_near_match(stripped, survivors, near_budget,
                                        ties_out=tied)
            if ovf:
                overflow = True
                break
            if best is not None:
                key = (sha, path)
                if key not in pre_cache:
                    if sha == _creation_sha(remote_ref, path):
                        # FINDINGS §458: the blamer is the file's own BIRTH
                        # commit. Gate (b)'s question — did the replacement text
                        # exist before their edit? — has a definite answer here:
                        # NOTHING existed before the file was born, so any
                        # near-match rewrite of birth lines is forward by
                        # definition. The old code took `pre_image_lines`'s None
                        # ("missing parent blob") as unknowable and blocked,
                        # which refused the FIRST legitimate edit every file
                        # younger than the window ever receives. A stale
                        # overwrite of a newborn still blocks: it produces no
                        # near-match survivor to pass gate (a) with.
                        pre_cache[key] = set()
                    else:
                        pre_cache[key] = pre_image_lines(sha, path)
                pre = pre_cache[key]
                # FINDINGS §697 addendum: ask gate (b) of EVERY candidate tied
                # at the winning ratio, not of whichever one set iteration
                # happened to yield. One equally-good replacement absent from
                # the pre-image is a forward edit; a stale twin that merely
                # ties with it must not veto that. Gates 2/3 are untouched —
                # a pre-image reinstall with no better-or-equal fresh twin
                # still blocks (case 14b), and NEAR_RATIO is unchanged.
                if pre is not None and any(c not in pre for c in (tied or [best[0]])):
                    mods.append({"line": ln, "sha": sha[:9],
                                 "similarity": round(best[1], 2)})
                    continue
                # pre unknown (missing parent/blob) or text existed pre-X:
                # conservative fall-through — still a hit.
        if when is not None and when >= cutoff:
            hits.append((ln, sha[:9], author))
    return hits, mods, overflow


NEAR_RATIO = 0.85


def _creation_sha(remote_ref: str, path: str) -> str | None:
    """The commit that added `path` (its birth), as of the remote tip."""
    out = git("log", "--format=%H", "--diff-filter=A", "-1",
              remote_ref, "--", path)
    return out.strip() or None


def best_near_match(text: str, survivors: set[str],
                    budget: list[int] | None = None,
                    ties_out: list[str] | None = None,
                    ) -> tuple[tuple[str, float] | None, bool]:
    """Closest pushed-survivor line to `text` above NEAR_RATIO, else None.

    Second return value is the §543/§605 overflow flag: True when the shared
    per-path comparison budget (`budget[0]`, one-element mutable counter) ran
    out before every candidate was examined — the caller must NOT treat that as
    "no near-match" and block, because an unfinished exemption search is an
    UNANSWERED question, not a negative one. quick_ratio prescreens are sound
    here: both are upper bounds on ratio(), so a true ≥ NEAR_RATIO match can
    never be screened away.

    `ties_out`, when given, is filled with EVERY candidate tied at the winning
    ratio, best first-seen order preserved. FINDINGS §697 addendum: `survivors`
    is a set, so which of several equally-good candidates `best` happens to be
    is iteration-order luck — and Class 5's gate (b) then asks its question of
    that arbitrary winner. Measured on FINDINGS.md, whose convention is a
    serially-numbered trailer line (`§NNN takes the next number.`) that the file
    also QUOTES in its own body: deleting `§695 takes the next number.` scores
    0.96296 against both the real successor `§697 takes the next number.` (a
    genuine forward edit, absent from the pre-image) and the long-dead quoted
    `§689 takes the next number.` (present in the pre-image). Whenever the
    stale twin won the tie, every future append to that file was refused. The
    caller resolves the tie on the pre-image instead of here, so the gate keeps
    asking "did ANY equally-good replacement text not exist before their edit?"
    — which is the question Class 5 was always meant to ask.
    """
    best: tuple[str, float] | None = None
    ties: list[str] = []
    overflow = False
    tlen = len(text)
    slack = max(8, int(0.35 * tlen))
    for cand in survivors:
        if budget is not None:
            if budget[0] <= 0:
                if ties_out is not None:
                    ties_out[:] = ties
                return best, True
            budget[0] -= 1
        if abs(len(cand) - tlen) > slack:
            continue
        sm = difflib.SequenceMatcher(None, text, cand)
        if sm.real_quick_ratio() < NEAR_RATIO or sm.quick_ratio() < NEAR_RATIO:
            continue
        r = sm.ratio()
        if r < NEAR_RATIO:
            continue
        if best is None or r > best[1]:
            best = (cand, r)
            ties = [cand]
        elif r == best[1]:
            ties.append(cand)
    if ties_out is not None:
        ties_out[:] = ties
    return best, overflow


def pre_image_lines(sha: str, path: str) -> set[str] | None:
    """Stripped non-blank lines of `path` as of the blamed commit's PARENT.

    None means unknowable here (no parent, no blob at that revision) — callers
    treat None as 'cannot prove this is a forward edit' and keep blocking."""
    out = git("show", "%s~1:%s" % (sha, path))
    if not out.strip():
        return None
    return {ln.strip() for ln in out.splitlines() if ln.strip()}


def added_line_texts(remote_ref: str, local_ref: str, path: str) -> list[str]:
    """Stripped non-empty ADDED (+) lines of this push for `path`."""
    out = git("diff", "-w", "-U0", remote_ref, local_ref, "--", path)
    texts: list[str] = []
    for line in out.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            t = line[1:].strip()
            if t:
                texts.append(t)
    return texts


def promoted_queue_lines(remote_ref: str, local_ref: str, path: str,
                         removed: list[int]) -> set[int]:
    """Removed `changelog_queue/*.md` lines this push PROMOTES into CHANGELOG.md.

    Class (9), §659, tightened to equality by H3886. `cut_release.py --apply`
    consumes the queue and stages each fragment's DELETION into the release
    commit, so every cut deletes lines another session queued minutes ago —
    measured on the v0.195.419 cut, 35 lines across 33 files. The bullet is not
    lost, it moved: `changelog_queue_consume.flush_bullets` copies each non-blank
    fragment line `ln.rstrip()` byte-identically into the release section.

    A removed fragment line is exempt ONLY when its exact stripped text is among
    the lines this SAME push ADDS to CHANGELOG.md. Not a near match, not a §530
    fragment prefix: a real cut is always byte-identical, so slack buys nothing
    here and costs the one thing this guard is for. Dropping someone's fresh
    fragment without promoting it blocks (case 24b); promoting a REWORDED bullet
    blocks (case 24c).

    Taken like §450's relocation — before blame, and deliberately never as a
    `survivors` entry, which also feeds class 5's difflib near match.
    """
    key = path.replace("\\", "/").lower()
    if not (key.startswith(CHANGELOG_QUEUE_PREFIX) and key.endswith(".md")):
        return set()
    promoted: set[str] = set()
    for base in CHANGELOG_BASENAMES:
        promoted.update(added_line_texts(remote_ref, local_ref, base))
    if not promoted:
        return set()
    old_text = blob_lines(remote_ref, path)
    ok: set[int] = set()
    for ln in removed:
        if not 1 <= ln <= len(old_text):
            continue
        stripped = old_text[ln - 1].strip()
        if stripped and stripped in promoted:
            ok.add(ln)
    return ok


def relocated_registry_rows(remote_ref: str, local_ref: str, path: str,
                            removed: list[int]) -> set[int]:
    """Removed README rows this push RELOCATES into REGISTRY_ARCHIVE.md.

    §450 measured six refused attempts on one close: relocating a row rewrites
    its status/date cells in the same operation, so no whole-line survivor
    exists and the surviving-text check cannot see the move. Predicate (the
    finding's own "checkable" bar): the removed line names an H###, AND the
    archive half GAINS, in this same push, a row naming the SAME H### that
    carries a contiguous verbatim fragment (>= VERBATIM_FRAGMENT_MIN) of the
    removed line — §530's fold-in (H3253), replacing the interim difflib
    near-match whose length slack missed real closes: the archived row appends
    a long close summary, so |cand| - |text| blows past max(8, 0.35*len) and
    the very relocation this predicate exists to allow was refused again,
    identically across two independent fresh checkouts on 24-08-2026 (H3167).
    A stale checkout that merely drops someone's fresh row adds nothing to the
    archive and stays blocked; an archive row naming the id without carrying
    the row's text also stays blocked — the bare-id false negative §437/§450
    warn against.
    """
    target = REGISTRY_RELOCATION_PAIR.get(
        path.replace("\\", "/").lower())
    if not target:
        return set()
    added_archive = added_line_texts(remote_ref, local_ref, target)
    if not added_archive:
        return set()
    old_text = blob_lines(remote_ref, path)
    ok: set[int] = set()
    for ln in removed:
        if not 1 <= ln <= len(old_text):
            continue
        stripped = old_text[ln - 1].strip()
        hids = set(HID_RE.findall(stripped))
        if not hids:
            continue
        same_id = [c for c in added_archive if hids & set(HID_RE.findall(c))]
        if same_id and has_verbatim_fragment(stripped, same_id):
            ok.add(ln)
    return ok


def scan(local_ref: str, remote_ref: str, recent_days: float,
         max_paths: int,
         max_blame_lines: int = DEFAULT_MAX_BLAME_LINES,
         max_near_pairs: int = DEFAULT_MAX_NEAR_PAIRS,
         ) -> tuple[dict[str, list], dict[str, list], bool, dict[str, dict],
                    dict[str, list]]:
    """(found, modified, truncated, uncheckable, warned).

    ``uncheckable`` maps path -> {"removed", "reason"} for every path whose
    line-level analysis exceeded the §543/§605 work bounds. Such paths get NO
    line-level verdict here — the caller degrades them to ref-level
    verification and prints the STALE_BASE_CIRCUIT_BREAK note, loudly, either
    way. ``warned`` maps path -> [line dicts] for class-10 same-lane close-prep
    lines (GTD 0x): they never block, but they are reported loudly so a human
    can verify them after the push lands.
    """
    ours = pushed_commits(remote_ref, local_ref)
    cutoff = datetime.now(timezone.utc) - timedelta(days=recent_days)
    paths = changed_paths(remote_ref, local_ref)
    truncated = len(paths) > max_paths
    # §457 gate 3: which H###s THIS PUSH visibly works on — ids in changed path
    # basenames anywhere in the diff, plus ids inside added lines per path.
    push_hids = frozenset(h for p in paths for h in HID_RE.findall(p))

    found: dict[str, list] = {}
    modified: dict[str, list] = {}
    uncheckable: dict[str, dict] = {}
    warned: dict[str, list] = {}
    pre_cache: dict = {}
    for path in paths[:max_paths]:
        removed = removed_line_numbers(remote_ref, local_ref, path)
        if not removed:
            continue
        if is_generated_single_writer(path):
            continue
        if is_mint_stub(remote_ref, path):
            continue
        # FINDINGS §450: rows this push relocates into REGISTRY_ARCHIVE.md are
        # moves, not losses — drop them from the flagged set before blaming.
        relocated = relocated_registry_rows(remote_ref, local_ref, path, removed)
        if relocated:
            removed = [ln for ln in removed if ln not in relocated]
            if not removed:
                continue
        # §659 (H3886): fragment lines whose exact text this push copies into
        # CHANGELOG.md are promoted by a release cut, not lost. Same pre-blame
        # position as §450 above, and the credit never reaches `survivors` —
        # that set also feeds class 5's near match, which forgave a reworded
        # bullet (case 24c).
        promoted = promoted_queue_lines(remote_ref, local_ref, path, removed)
        if promoted:
            removed = [ln for ln in removed if ln not in promoted]
            if not removed:
                continue
        survivors = surviving_text(local_ref, path) | \
            cross_file_survivors(remote_ref, local_ref, path)
        # §543/§605 work bounds. Fired BEFORE any blame: on a wholesale
        # derived-file rewrite the old loop paid one blame subprocess per
        # removed line and one difflib comparison per (removed, survivor)
        # pair — hours of unbounded work, with the push killed by the
        # caller's timeout before any verdict existed.
        if len(removed) > max_blame_lines:
            uncheckable[path] = {
                "removed": len(removed),
                "reason": "%d removed line(s) > --max-blame-lines %d"
                          % (len(removed), max_blame_lines)}
            continue
        if len(removed) * len(survivors) > max_near_pairs:
            uncheckable[path] = {
                "removed": len(removed),
                "reason": "near-match pairs ~%d (removed x survivors) > "
                          "--max-near-pairs %d"
                          % (len(removed) * len(survivors), max_near_pairs)}
            continue
        path_push_hids = frozenset(push_hids) | {
            h for t in added_line_texts(remote_ref, local_ref, path)
            for h in HID_RE.findall(t)}
        try:
            blame = blame_map(remote_ref, path)
        except BlameTimeout as exc:
            uncheckable[path] = {
                "removed": len(removed),
                "reason": "git blame timeout: %s" % exc,
            }
            continue
        budget = [max_near_pairs]
        lane_warns: list[dict] = []
        hits, mods, overflow = blame_recent(remote_ref, path, removed, cutoff,
                                            ours, survivors, pre_cache,
                                            path_push_hids, blame, budget,
                                            lane_warns)
        if overflow and not hits:
            # Budget ran out before any concrete loss was proven: an unfinished
            # exemption search is an unanswered question, so the path gets the
            # explicit uncheckable verdict instead of a speculative refusal
            # (§605: a false refusal is visible; a hang teaches authors to
            # bypass — and a speculative block on unaffordable analysis is the
            # false-refusal cousin of the same mistake).
            uncheckable[path] = {
                "removed": len(removed),
                "reason": "near-match budget exhausted mid-path (%d removed "
                          "line(s), bound %d)" % (len(removed), max_near_pairs)}
            continue
        if hits:
            found[path] = hits
        if mods:
            modified[path] = mods
        if lane_warns:
            warned[path] = lane_warns
    return found, modified, truncated, uncheckable, warned


LANE_WARN_MARKER = "STALE_BASE_SAME_LANE_WARNING"


def report_lane_warnings(warned: dict[str, list], e=None) -> None:
    """The loud class-10 verdict: lines named, push ALLOWED (GTD 0x).

    Never silent — the whole point of downgrading the H4265 refusal is that the
    same-lane rewrite still shows up in stderr for the human, with every line
    and its blaming commit, so a foreign session's stale revert of a handoff
    file cannot hide behind the class either.
    """
    e = e or sys.stderr
    n_warn = sum(len(v) for v in warned.values())
    print("%s — push ALLOWED — %d recently-added handoff line(s) were "
          "rewritten/deleted by a commit whose subject names the same H### as "
          "the file (same-lane close-prep, the H4265 shape; MG 06-09-2026 "
          "«Флип разрешить», GTD 0x):" % (LANE_WARN_MARKER, n_warn), file=e)
    for path, warns in warned.items():
        print("  %s" % path, file=e)
        for w in warns:
            print("      line %-6d added by %s (%s)" % (w["line"], w["sha"],
                                                        w["author"]), file=e)
    print("  If these lines could belong to ANOTHER session's work, verify by "
          "hand:  git blame --line-porcelain <remote> -- <path>", file=e)
    print("", file=e)


def report_non_ff(found: dict[str, list], remote_ref: str,
                  e=None) -> None:
    """A NON-fast-forward push: say so, name the phantom lines, block nothing.

    Deliberately worded to contain NEITHER banner string
    `handoff_claims.GUARD_BANNER_RE` matches (`PUSH BLOCKED` /
    `pre-push: BLOCKED`), because a caller that reads this run as a guard block
    draws the exact opposite conclusion from the truth: this IS origin/main
    moving, and refetch-and-retry is what clears it.
    """
    e = e or sys.stderr
    total = sum(len(v) for v in found.values())
    print("", file=e)
    print("%s — push NOT blocked by this guard. %s is not an ancestor of the "
          "pushed commit, so this push is a NON-fast-forward: git will refuse "
          "it on its own (and on main the line gate refuses a forced one). The "
          "%d 'deleted' line(s) below are an artefact of diffing against a tip "
          "that is not this commit's parent — refetch, rebuild on the current "
          "tip, and push again." % (NON_FF_MARKER, remote_ref, total), file=e)
    for path, hits in sorted(found.items()):
        print("  %s" % path, file=e)
        for line, sha, author in hits[:5]:
            print("      line %-6d added by %s (%s)" % (line, sha, author), file=e)
        if len(hits) > 5:
            print("      … %d more" % (len(hits) - 5), file=e)
    print("", file=e)


def report(found: dict[str, list], modified: dict[str, list],
           remote_ref: str, recent_days: float,
           truncated: bool, max_paths: int,
           warned: dict[str, list] | None = None) -> None:
    warned = warned or {}
    total = sum(len(v) for v in found.values())
    e = sys.stderr
    print("", file=e)
    if not found:
        # Class 5 pass-through: say WHY the rewrite was allowed so the note is
        # greppable from wrappers, mirroring the refusal banner's discipline.
        # A push with no recent-line interaction stays silent, as before.
        n_mod = sum(len(v) for v in modified.values())
        if n_mod:
            print("stale-base guard: ALLOWED - %d recently-added line(s) were "
                  "modified in place (forward edits on top of upstream work, none "
                  "deleted)." % n_mod, file=e)
            for path, mods in modified.items():
                for m in mods:
                    print("  %s:%d sim %.2f (%s)" % (path, m["line"],
                                                     m["similarity"], m["sha"]), file=e)
        if sum(len(v) for v in warned.values()):
            report_lane_warnings(warned, e)
        if n_mod or warned:
            if truncated:
                print("NOTE: only the first %d changed paths were scanned (--max-paths)."
                      % max_paths, file=e)
            print("", file=e)
        return
    # The banner must match what main() actually returns — the H2656 lesson, kept
    # after the 16-08-2026 re-promotion to a blocker. It once printed "PUSH BLOCKED"
    # on a path that warned and let the push through; a session read that as a
    # refusal twice and hand-verified origin both times before noticing. Now the
    # check blocks unconditionally, so the one banner is the true one.
    print("", file=e)
    # H3134 (FINDINGS §493): the override belongs on the FIRST line, not twenty
    # lines into the banner — a retry loop that only greps stderr for
    # REFUSAL_MARKER can stop after one attempt instead of burning its whole
    # budget re-asking a question this refusal never depends on the remote tip
    # to answer. This is always a LOCAL hook decision (a genuine non-fast-forward
    # never reaches this script — git itself rejects it first).
    print(escape_first_line("%s — LOCAL guard refusal, not a moved remote tip."
                            "  Override:  %s=1 git push ..."
                            % (REFUSAL_MARKER, ESCAPE_ENV)), file=e)
    print("PUSH BLOCKED — this push deletes %d line(s) that landed on %s"
          % (total, remote_ref), file=e)
    print("within the last %g day(s), in %d file(s), and your commits never "
          "reference them." % (recent_days, len(found)), file=e)
    print("", file=e)
    shown = 0
    for path, hits in found.items():
        print("  %s" % path, file=e)
        for ln, sha, author in hits:
            if shown >= MAX_LISTED:
                break
            print("      line %-6d added by %s (%s)" % (ln, sha, author), file=e)
            shown += 1
        if shown >= MAX_LISTED:
            print("      …", file=e)
            break
    print("", file=e)
    if sum(len(v) for v in warned.values()):
        print("Also warned (class 10 same-lane close-prep — listed, not blocked, "
              "but this push is refused for the OTHER lines above):", file=e)
        for path, warns in warned.items():
            print("  %s" % path, file=e)
            for w in warns:
                print("      line %-6d added by %s (%s)" % (w["line"], w["sha"],
                                                            w["author"]), file=e)
        print("", file=e)
    print("That is Uprava#1516. Twice now a clean fast-forward with green hooks has", file=e)
    print("installed a pre-image copy over another session's work: 6 files on 29-07", file=e)
    print("(stale index after `git reset --soft`), 19 link fixes on 04-08 (stale", file=e)
    print("checkout — the branch ref moved, the working tree did not).", file=e)
    print("", file=e)
    print("If you did NOT mean to touch those lines, your file content is stale:", file=e)
    print("    git fetch origin && git rebase %s" % remote_ref, file=e)
    print("and if `git status` lists files you never edited, do NOT `git add -A` and", file=e)
    print("do NOT lift a patch out of that tree (a patch encodes its base, FINDINGS", file=e)
    print("§308) — rebuild on a fresh worktree off %s and re-apply your edits." % remote_ref, file=e)
    print("", file=e)
    print(escape_paragraph("If the revert IS deliberate:  %s=1 git push ..."
                           % ESCAPE_ENV), file=e)
    if truncated:
        print("", file=e)
        print("NOTE: only the first %d changed paths were scanned (--max-paths)." % max_paths, file=e)
    print("", file=e)


def report_circuit_break(uncheckable: dict[str, dict], ref_ok: bool,
                         remote_ref: str) -> None:
    """The loud §543/§605 verdict for paths the work bound skipped.

    Printed on EVERY circuit-broken push, allowed or refused — the row's bar is
    an explicit «skipped, uncheckable» verdict instead of silent omission. The
    marker sits on the first line so wrappers can grep it.
    """
    e = sys.stderr
    print("", file=e)
    print("%s — %d path(s) SKIPPED by the work bound, UNCHECKED at line level "
          "(FINDINGS §543, §605)." % (CIRCUIT_MARKER, len(uncheckable)), file=e)
    for path, info in uncheckable.items():
        print("  %s: %s" % (path, info["reason"]), file=e)
    if ref_ok:
        print("  Degraded to ref-level verification: %s IS an ancestor of the "
              "pushed tip (clean fast-forward) — allowed, but these paths were "
              "NOT scanned for silent line-level reverts." % remote_ref, file=e)
    else:
        print("  PUSH BLOCKED — ref-level verification FAILED: %s is NOT an "
              "ancestor of the pushed tip (forced/non-fast-forward update), "
              "and a bulk rewrite of unscanned paths on such an update is "
              "refused fail-closed." % remote_ref, file=e)
        print("  " + escape_first_line("Override:  %s=1 git push ..." % ESCAPE_ENV),
              file=e)
    print("  If this push might revert ANOTHER SESSION's lines on those paths, "
          "verify by hand first:", file=e)
    print("    git blame --line-porcelain %s -- <path>" % remote_ref, file=e)
    print("", file=e)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("local_ref")
    ap.add_argument("remote_ref")
    ap.add_argument("--recent-days", type=float, default=3.0)
    ap.add_argument("--max-paths", type=int, default=40)
    ap.add_argument("--max-blame-lines", type=int,
                    default=DEFAULT_MAX_BLAME_LINES,
                    help="per-path removed-line bound past which the path is "
                         "skipped loudly (§543/§605)")
    ap.add_argument("--max-near-pairs", type=int,
                    default=DEFAULT_MAX_NEAR_PAIRS,
                    help="per-path near-match comparison budget (§543/§605)")
    ap.add_argument("--no-fetch", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if not args.no_fetch:
        git("fetch", args.remote_ref.split("/", 1)[0] or "origin", "--quiet")

    if not git("rev-parse", "--verify", "--quiet", args.remote_ref).strip():
        if args.json:
            print(json.dumps({"result": "skip", "reason": "remote ref not found"}))
        return 0

    found, modified, truncated, uncheckable, warned = scan(
        args.local_ref, args.remote_ref, args.recent_days, args.max_paths,
        args.max_blame_lines, args.max_near_pairs)

    # H4342: a NON-fast-forward push is not this guard's business, and every
    # line it flags on one is a phantom. See push_is_fast_forward().
    if found and not push_is_fast_forward(args.remote_ref, args.local_ref):
        if log_firing is not None:
            try:
                log_firing(git("rev-parse", "--show-toplevel").strip(),
                           "stale-base", "non-ff-skip",
                           "non-fast-forward push; %d phantom line(s) in %d "
                           "path(s) not scanned: %s"
                           % (sum(len(v) for v in found.values()), len(found),
                              ",".join(sorted(found))[:400]))
            except Exception:  # noqa: SE3 -- telemetry must never break the guard
                pass
        if args.json:
            print(json.dumps({
                "result": "non-ff-skip",
                "paths": sorted(found),
                "lines": sum(len(v) for v in found.values()),
            }))
            return 0
        report_non_ff(found, args.remote_ref)
        return 0

    # §543/§605: circuit-broken paths degrade to ref-level verification —
    # fast-forward passes (loudly), a forced/non-ff bulk rewrite fails closed.
    ref_ok = True
    if uncheckable:
        ref_ok = git_ok("merge-base", "--is-ancestor",
                        args.remote_ref, args.local_ref)

    # H3069: additive §469 check — silent ADDITIONS inside an already-tagged
    # CHANGELOG section. Runs only when its own hatch is not raised; the
    # deletion-side scan and every one of its exemptions are untouched.
    drift: list[dict] = []
    structural: list[tuple[str, list[dict]]] = []
    if not os.environ.get(TAG_DRIFT_ENV):
        drift = changelog_tag_drift(args.remote_ref, args.local_ref,
                                    args.max_paths)
        # Same refusal family, same hatch: layout-level collisions the
        # line-diff above cannot see (duplicate headings, non-descending
        # sections — the #2335 collision class, repaired 29-08-2026).
        structural = changelog_structure_path_findings(
            args.remote_ref, args.local_ref, args.max_paths)

    blocked = (bool(found) or bool(drift) or bool(structural)
               or (bool(uncheckable) and not ref_ok))

    # S27 telemetry: one JSONL line per run into the clone's central firing
    # log (logs/guard_firings.jsonl in the MAIN checkout — every worktree of
    # the clone shares it). "refuse" when the push is blocked (the detail
    # names which refusal classes fired), "circuit-break" when the §543/§605
    # degraded verdict allowed a push whose paths were NOT line-scanned.
    # Fail-open end to end: a telemetry failure must never alter the verdict
    # or reach the guard's stderr.
    if log_firing is not None:
        try:
            classes = []
            if found:
                # H4342: the paths, not just the counts. Ten days of
                # "stale-base lines=1 paths=1" records could establish that the
                # guard fired 3222 times and nothing at all about WHICH file or
                # which rival commit, so no recurrence could be diagnosed from
                # the record the log exists to be. Names only, capped — this
                # file is gitignored local evidence, same as the main-line
                # witness, and a path list is what a census can group by.
                classes.append("stale-base lines=%d paths=%d [%s]" % (
                    sum(len(v) for v in found.values()), len(found),
                    ",".join(sorted(found))[:400]))
            if warned:
                classes.append("same-lane-warn lines=%d paths=%d" % (
                    sum(len(v) for v in warned.values()), len(warned)))
            if drift:
                classes.append("changelog-tag-drift sections=%d" % len(drift))
            if structural:
                classes.append("changelog-structure paths=%d" % len(structural))
            if uncheckable:
                classes.append("circuit-break paths=%d ref=%s" % (
                    len(uncheckable),
                    "fast-forward" if ref_ok else "non-fast-forward"))
            toplevel = git("rev-parse", "--show-toplevel").strip()
            if blocked:
                log_firing(toplevel, "stale-base", "refuse",
                           "; ".join(classes) or "blocked")
            elif warned:
                log_firing(toplevel, "stale-base", "warn",
                           "allowed; " + "; ".join(classes))
            elif uncheckable:
                log_firing(toplevel, "stale-base", "circuit-break",
                           "allowed; " + "; ".join(classes))
        except Exception:  # noqa: SE3 -- telemetry must never break the guard
            pass

    if args.json:
        print(json.dumps({
            "result": "block" if blocked else "ok",
            "paths": sorted(found),
            "lines": sum(len(v) for v in found.values()),
            "modified": {p: len(v) for p, v in modified.items()},
            "lane_warnings": {p: len(v) for p, v in warned.items()},
            "truncated": truncated,
            "circuit_break": uncheckable,
            "circuit_ref_level": "fast-forward" if ref_ok else "non-fast-forward",
            "changelog_tag_drift": drift,
            "changelog_structure": [{"path": p, "findings": f}
                                    for p, f in structural],
        }))
        return 1 if blocked else 0

    if uncheckable:
        report_circuit_break(uncheckable, ref_ok, args.remote_ref)
    report(found, modified, args.remote_ref, args.recent_days, truncated,
           args.max_paths, warned)
    if drift:
        report_tag_drift(drift)
    for p, f in structural:
        report_structure_drift(f, p)
    if not blocked:
        return 0
    # BLOCKS by default (MG 16-08-2026, reversing the demotion below). The push is
    # refused; the escape hatch in the banner is the single way through. STRICT_ENV
    # is kept as an accepted no-op so older callers and docs do not break.
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
