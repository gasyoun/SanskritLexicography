"""Declared Python interpreter floor for the Uprava tool fleet + stdlib newline= compat.

H3541. Two jobs, one cheap stdlib-only import:

1. **Declare and enforce ONE floor.** ``FLOOR`` below is the single machine-readable
   source of truth. Importing this module checks the running interpreter against it
   and, on a miss, exits with a named message (required / found / a command that
   works) instead of letting a raw ``TypeError`` or ``SyntaxError`` surface halfway
   through a registry rewrite.

2. **Provide the 3.13-only ``newline=`` kwarg on every supported interpreter.**
   ``Path.read_text``/``Path.write_text`` only grew ``newline=`` in Python 3.13.
   The registry files are Windows-authored CRLF, so the kwarg is load-bearing:
   dropping it re-enables universal-newline translation and rewrites every line
   ending in ``handoffs/README.md`` (FINDINGS s262 / s299 / s305). ``io.open`` has
   accepted ``newline=`` since forever, so the wrappers below are byte-for-byte
   equivalent to the 3.13 methods on any 3.x.

Call as ``pyfloor.read_text(p, ...)`` / ``pyfloor.write_text(p, ...)`` -- never
``p.read_text(..., newline=...)``. ``tools/audit_pyfloor.py`` fails the build on
any regression.

Deliberately written without f-strings or any post-3.5 syntax: this module must be
able to *parse* under a below-floor interpreter in order to print why it refuses.
"""

import io
import os
import sys

# --- the one declared floor -------------------------------------------------
FLOOR = (3, 9)
FLOOR_STR = "3.9"
# Why 3.9 and not higher: `/usr/bin/python3` on macOS is 3.9.6, and both
# .githooks/pre-commit and the CI workflows resolve their interpreter by bare
# PATH lookup. A floor above the system interpreter has to be re-satisfied at
# every invocation path forever; a floor at it is satisfied by default.
# Full rationale: docs/DECISION_PYTHON_INTERPRETER_FLOOR_2026.md

_ENV_SKIP = "UPRAVA_PYFLOOR_SKIP"
# Test seam. A box that already satisfies the floor cannot otherwise prove the
# guard fires -- there is no below-floor interpreter to run it under. Setting
# UPRAVA_PYFLOOR_MIN=3.99 raises the required version for one invocation, so
# the named refusal can be demonstrated (and a floor bump rehearsed) on any box.
# Never set it in normal operation; it only ever makes the floor stricter.
_ENV_MIN = "UPRAVA_PYFLOOR_MIN"


def _env_minimum():
    """`UPRAVA_PYFLOOR_MIN` as a version tuple, or None."""
    raw = os.environ.get(_ENV_MIN, "").strip()
    if not raw:
        return None
    try:
        parts = tuple(int(p) for p in raw.split(".")[:3])
    except ValueError:
        return None
    return parts if len(parts) >= 2 else None


def satisfied(version_info=None, minimum=None):
    """True when `version_info` (default: this interpreter) meets `minimum`."""
    minimum = minimum or _env_minimum()
    vi = version_info or sys.version_info
    lo = minimum or _env_minimum() or FLOOR
    return tuple(vi[:2]) >= tuple(lo[:2])


def _candidates(minimum):
    """Interpreters on PATH (plus the usual Homebrew/pyenv shelves) that satisfy `minimum`.

    Only called on the failure path, so its cost never touches a healthy run.
    """
    import glob
    import subprocess

    seen = []
    names = []
    for minor in range(minimum[1], minimum[1] + 12):
        names.append("python3." + str(minor))
    names.append("python3")
    dirs = []
    for d in os.environ.get("PATH", "").split(os.pathsep):
        if d and d not in dirs:
            dirs.append(d)
    for d in ("/opt/homebrew/bin", "/usr/local/bin", os.path.expanduser("~/.pyenv/shims")):
        if os.path.isdir(d) and d not in dirs:
            dirs.append(d)
    found = []
    for d in dirs:
        for n in names:
            p = os.path.join(d, n)
            if os.path.isfile(p) and os.access(p, os.X_OK) and p not in seen:
                seen.append(p)
                found.append(p)
    for pattern in ("/opt/homebrew/Cellar/python@3.*/*/bin/python3.*",):
        for p in sorted(glob.glob(pattern)):
            if p.endswith("-config") or p in seen:
                continue
            seen.append(p)
            found.append(p)
    good = []
    for p in found:
        try:
            out = subprocess.check_output(
                [p, "-c", "import sys;print('%d.%d.%d' % sys.version_info[:3])"],
                stderr=subprocess.STDOUT,
            )
        except Exception:
            continue
        try:
            txt = out.decode("utf-8", "replace").strip().splitlines()[-1]
            parts = tuple(int(x) for x in txt.split("."))
        except Exception:
            continue
        if satisfied(parts, minimum) and (p, txt) not in good:
            good.append((p, txt))
    return good


def explain(minimum=None, tool=None):
    """The named, actionable below-floor message. Returns a string; prints nothing."""
    lo = minimum or _env_minimum() or FLOOR
    running = "%d.%d.%d" % sys.version_info[:3]
    who = tool or os.path.basename(sys.argv[0] or "this tool")
    lines = []
    lines.append("")
    lines.append("PYTHON FLOOR NOT MET -- refusing to run " + who)
    lines.append("")
    lines.append("  required : Python >= %d.%d  (declared in tools/pyfloor.py, FLOOR)" % (lo[0], lo[1]))
    lines.append("  found    : Python " + running)
    lines.append("  from     : " + (sys.executable or "<unknown interpreter>"))
    lines.append("")
    good = _candidates(lo)
    if good:
        lines.append("  A command that works on this box:")
        lines.append("")
        invocation = " ".join(sys.argv) if sys.argv and sys.argv[0] else "tools/<tool>.py"
        lines.append("      " + good[0][0] + " " + invocation)
        lines.append("")
        if len(good) > 1:
            lines.append("  Other interpreters that satisfy the floor:")
            for p, v in good[1:6]:
                lines.append("      " + p + "   (" + v + ")")
            lines.append("")
    else:
        lines.append("  No interpreter >= %d.%d was found on PATH." % (lo[0], lo[1]))
        lines.append("  Install one, e.g.:   brew install python@%d.%d" % (lo[0], lo[1]))
        lines.append("")
    lines.append("  Why this guard exists: below the floor these tools fail mid-run")
    lines.append("  (registry half-rewritten) instead of failing at startup. H3541.")
    lines.append("")
    return "\n".join(lines)


def require(minimum=None, tool=None):
    """Exit 3 with the named message unless the running interpreter meets the floor."""
    if os.environ.get(_ENV_SKIP):
        return
    minimum = minimum or _env_minimum()
    if satisfied(None, minimum):
        return
    try:
        sys.stderr.write(explain(minimum, tool) + "\n")
        sys.stderr.flush()
    except Exception:
        pass
    raise SystemExit(3)


# --- newline=-preserving text IO, available on every supported interpreter ---

def read_text(path, encoding=None, errors=None, newline=None):
    """Exactly `Path(path).read_text(encoding, errors, newline)` from Python 3.13."""
    with io.open(path, "r", encoding=encoding, errors=errors, newline=newline) as fh:
        return fh.read()


def write_text(path, data, encoding=None, errors=None, newline=None):
    """Exactly `Path(path).write_text(data, encoding, errors, newline)` from Python 3.13."""
    if not isinstance(data, str):
        raise TypeError("data must be str, not " + type(data).__name__)
    with io.open(path, "w", encoding=encoding, errors=errors, newline=newline) as fh:
        return fh.write(data)


require()


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    argv = sys.argv[1:]
    if "--floor" in argv:
        print(FLOOR_STR)
        raise SystemExit(0)
    if "--candidates" in argv:
        for p, v in _candidates(FLOOR):
            print(v + "\t" + p)
        raise SystemExit(0)
    print("floor      : Python >= " + FLOOR_STR)
    print("running    : %d.%d.%d" % sys.version_info[:3])
    print("executable : " + (sys.executable or "?"))
    print("verdict    : OK (this interpreter satisfies the declared floor)")
    raise SystemExit(0)
