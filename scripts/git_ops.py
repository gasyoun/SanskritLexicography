#!/usr/bin/env python3
"""GitOperations — one exec seam for every subprocess-git call in tools/ (H3441).

Lesson mapped 1:1 (Vercel Academy, "Shell Execution with Safety"): callers ask
"run these args in that repo, give me stdout+exit", a backend answers. Before
this module, ~30 tools carried a private `def git()` wrapper each, with its own
error shape, timeout default, encoding, and env handling. That variance already
produced two realized incidents (see DANGER_FACTS.md): unfiltered `GIT_*` env
leaking into a fixture git call corrupted the canonical repo's `.git/config`
(FINDINGS s365 / H2629), and a background job that cd'd into a pruned worktree
let later git calls fall through to the enclosing repo and push the WRONG repo.

Builds on `tools/_common.py` (H3283) rather than re-wrapping subprocess: `run()`/
`git()` there already give every caller a mandatory timeout and utf-8 text I/O.
This module adds the two things `_common.git()` still leaves to each call site:
a uniform result shape regardless of success (`Result`, never raises on non-zero
unless asked), and a CALL-scope `GIT_*` env default. FINDINGS s365 fixed the
PROCESS-scope hole (`tools/testrunner.py._disinherit_git_env`, stripped once at
import for test suites run under testrunner); this seam is the complementary
per-call default for tools invoked OUTSIDE testrunner. `GIT_TERMINAL_PROMPT` is
kept (suppresses interactive auth prompts, names no repository) and forced to
"0" when strip_git_env is on.

Guard vocabulary (which commands may run at all) lives in H3439's deny-pattern
table, not here — this module owns HOW an allowed command is executed.

    from git_ops import GitOperations, MockGitOperations, Result

    ops = GitOperations()
    r = ops.exec(repo_path, ["status", "--porcelain"])
    if not r.ok:
        ...

    mock = MockGitOperations()
    mock.stub(("status", "--porcelain"), Result(" M f.py\n", "", 0))
    consume(mock)  # spawns nothing
"""
from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple

# --- pyfloor bootstrap (H3541): declared interpreter floor + newline= compat ---
import os as _os, sys as _sys
if _os.path.dirname(_os.path.abspath(__file__)) not in _sys.path:
    _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import pyfloor  # noqa: E402
# --- end pyfloor bootstrap ---

import _common  # noqa: E402

DEFAULT_TIMEOUT_S = 60


class GitTimeout(Exception):
    """A git invocation exceeded its bounded timeout — a named failure, never a
    silent hang or an empty result indistinguishable from 'nothing to report'."""


class GitCheckFailed(Exception):
    """`check=True` and the invocation exited non-zero."""


@dataclass(frozen=True)
class Result:
    """The uniform shape every backend returns, success or failure alike."""
    stdout: str
    stderr: str
    exit_code: int

    @property
    def ok(self) -> bool:
        return self.exit_code == 0


def filtered_git_env(base: dict | None = None) -> dict:
    """`base` (default: the current process env) with every `GIT_*` var dropped
    except `GIT_TERMINAL_PROMPT`, which is kept and forced to "0".

    This is the CALL-scope twin of `testrunner._disinherit_git_env` (FINDINGS
    s365): that guard strips once at import, process-wide, for suites launched
    through testrunner.py. A tool invoked directly (not via testrunner) never
    passes through that import, so a fixture `git init`/`add`/`commit` in such a
    tool can still inherit a caller's `GIT_DIR`/`GIT_INDEX_FILE` and silently
    operate on the wrong repository. Exported so a caller that wants to see
    exactly what env a call ran under can build it independently of `.exec`.
    """
    src = os.environ if base is None else base
    env = {k: v for k, v in src.items()
           if not (k.startswith("GIT_") and k != "GIT_TERMINAL_PROMPT")}
    env["GIT_TERMINAL_PROMPT"] = "0"
    return env


class GitOperations:
    """Real backend: spawns `git -C <repo> <args>` via `_common.git()`."""

    def exec(self, repo_path, args, *, timeout_s: float = DEFAULT_TIMEOUT_S,
              strip_git_env: bool = True, check: bool = False,
              text: bool = True, input_bytes: bytes | None = None) -> Result:
        """Run `git -C <repo_path> <args>`.

        `repo_path` is always passed explicitly as `-C <repo_path>` — never a
        bare `cwd`-relative call — so a caller can never fall through to
        whatever repo the process happens to be sitting in (the pruned-worktree
        incident this module's docstring names). Never raises on a non-zero
        exit unless `check=True`; a bounded timeout raises `GitTimeout` rather
        than hanging or returning an empty, unaudited-looking result.

        `text=False` returns raw, undecoded `bytes` in `Result.stdout` (stderr
        is still decoded, for messages) — the deliberate exception a blob-content
        caller (e.g. an EOL/CR-byte census) needs: `errors="replace"` on binary
        blob content silently corrupts the very bytes such a caller is counting,
        so it must opt out of decoding rather than have this seam force it.
        """
        repo_path = str(repo_path)
        env = filtered_git_env() if strip_git_env else None
        if text:
            try:
                proc = _common.git(repo_path, *args, check=False,
                                    timeout=timeout_s, env=env)
            except subprocess.TimeoutExpired as exc:
                raise GitTimeout(
                    f"git {' '.join(args)} in {repo_path} exceeded {timeout_s}s"
                ) from exc
            stdout, stderr = proc.stdout, proc.stderr
        else:
            cmd = ["git", "-C", repo_path, *args]
            try:
                proc = subprocess.run(
                    cmd, input=input_bytes, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, timeout=timeout_s,
                    env=(env if env is not None else None),
                )
            except subprocess.TimeoutExpired as exc:
                raise GitTimeout(
                    f"git {' '.join(args)} in {repo_path} exceeded {timeout_s}s"
                ) from exc
            stdout = proc.stdout
            stderr = proc.stderr.decode("utf-8", "replace")
        result = Result(stdout=stdout, stderr=stderr, exit_code=proc.returncode)
        if check and not result.ok:
            raise GitCheckFailed(
                f"git {' '.join(args)} in {repo_path} exited {result.exit_code}: "
                f"{(result.stderr or '').strip()}"
            )
        return result


class MockCall(NamedTuple):
    """One recorded `MockGitOperations.exec()` invocation, full call shape."""
    repo_path: str
    args: tuple
    timeout_s: float
    strip_git_env: bool
    text: bool
    input_bytes: bytes | None


@dataclass
class MockGitOperations:
    """Dry backend (the lesson's `mockOps`): returns canned `Result`s, never
    spawns a subprocess. `calls` records every invocation for assertions; an
    unstubbed `(repo, args)` pair returns a canned-empty success by default so
    a demo consumer can run end-to-end without pre-stubbing every call."""

    calls: list = field(default_factory=list)
    _canned: dict = field(default_factory=dict)
    default_result: Result = field(
        default_factory=lambda: Result(stdout="", stderr="", exit_code=0))

    def stub(self, args, result: Result, *, repo_path=None) -> None:
        """Canned `Result` for a given `args` tuple, optionally scoped to one repo."""
        key = (str(repo_path) if repo_path is not None else None, tuple(args))
        self._canned[key] = result

    def exec(self, repo_path, args, *, timeout_s: float = DEFAULT_TIMEOUT_S,
              strip_git_env: bool = True, check: bool = False,
              text: bool = True, input_bytes: bytes | None = None) -> Result:
        repo_path = str(repo_path)
        args = tuple(args)
        # Recorded alongside repo/args (not just accepted-and-dropped) so a
        # consumer's test can assert what a caller actually requested, e.g. that
        # a fixture op ran with strip_git_env=True.
        self.calls.append(MockCall(repo_path, args, timeout_s, strip_git_env,
                                    text, input_bytes))
        result = self._canned.get((repo_path, args))
        if result is None:
            result = self._canned.get((None, args), self.default_result)
        if check and not result.ok:
            raise GitCheckFailed(
                f"git {' '.join(args)} in {repo_path} exited {result.exit_code}: "
                f"{(result.stderr or '').strip()} (mocked)"
            )
        return result


__all__ = [
    "Result",
    "GitOperations",
    "MockGitOperations",
    "MockCall",
    "GitTimeout",
    "GitCheckFailed",
    "filtered_git_env",
    "DEFAULT_TIMEOUT_S",
]
