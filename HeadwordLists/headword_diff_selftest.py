"""Selftest for headword_diff.py `now`-mode write contract (H6518).

Offline and fixture-based: builds a sandbox with fake then-2014 snapshots and
fake csl-orig sources, points headword_diff at them by attribute injection,
and asserts the three H6518 behaviors on real executions of write_now():

  1. FAIL-CLOSED — with no sources, `now` returns non-zero with a loud stderr
     message naming the CSL_ORIG_V02 override, and writes nothing; with no
     then-2014 inputs at all it returns non-zero too.
  2. STABLE / PINNED-ALIAS NAMES — a rerun with the same source writes the
     identical filenames; when the live count drifts off a pinned name, the
     NAME is kept (in-place write) and the drift is recorded in
     NOW_COUNT_DELTA.md — never a rename churn.
  3. BOM PRESERVATION — the regenerated file byte-begins with the then-2014
     sibling's BOM where that sibling has one (MW-unique-key1 shape) and
     gains NO BOM where the sibling has none (its key2 sibling shape).

Run: python3 HeadwordLists/headword_diff_selftest.py   (exit 0 = green)
"""
import importlib.util
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "headword_diff", os.path.join(HERE, "headword_diff.py"))
hd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hd)

_failures = []


def check(name, cond, detail=""):
    tag = "PASS" if cond else "FAIL"
    print(f"  [{tag}] {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        _failures.append(name)


def run_now(module=hd):
    """Invoke write_now() and return its exit code."""
    return module.write_now()


class Sandbox:
    """A temp tree: then-2014/ snapshots + a fake csl-orig v02/ source root."""

    def __init__(self, then_files=(), sources=()):
        self.root = tempfile.mkdtemp(prefix="h6518_selftest_")
        self.then_dir = os.path.join(self.root, "then-2014")
        self.now_dir = os.path.join(self.root, "now-2026")
        self.orig = os.path.join(self.root, "v02")
        os.makedirs(self.then_dir)
        for name, lines, bom in then_files:
            self.write_then(name, lines, bom)
        for code, k1s, k2s in sources:
            d = os.path.join(self.orig, code.lower())
            os.makedirs(d)
            with open(os.path.join(d, code.lower() + ".txt"), "w",
                      encoding="utf-8", newline="\n") as fh:
                fh.write("".join(f"<k1>{k}" for k in k1s))
                fh.write("".join(f"<k2>{k}¦x\n" for k in k2s))

    def write_then(self, name, lines, bom):
        with open(os.path.join(self.then_dir, name), "wb") as fh:
            if bom:
                fh.write(b"\xef\xbb\xbf")
            fh.write(("\n".join(lines) + "\n").encode("utf-8"))

    def rewrite_source(self, code, k1s, k2s=()):
        d = os.path.join(self.orig, code.lower())
        with open(os.path.join(d, code.lower() + ".txt"), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write("".join(f"<k1>{k}" for k in k1s))
            fh.write("".join(f"<k2>{k}¦x\n" for k in k2s))

    def now_files(self):
        return sorted(f for f in os.listdir(self.now_dir) if f.endswith(".txt"))

    def bind(self, module=hd):
        """Point the module at this sandbox, returning the saved real state."""
        saved = (module.THEN2014, module.NOW2026, module.ORIG, module.PD_SRC)
        module.THEN2014 = self.then_dir
        module.NOW2026 = self.now_dir
        module.ORIG = self.orig
        module.PD_SRC = os.path.join(self.root, "no-such-pd.txt")
        return saved

    @staticmethod
    def restore(saved, module=hd):
        module.THEN2014, module.NOW2026, module.ORIG, module.PD_SRC = saved

    def cleanup(self):
        shutil.rmtree(self.root, ignore_errors=True)


def with_sandbox(sb):
    """Decorator: run the test body with the module bound to the sandbox."""
    def deco(fn):
        def wrapped():
            saved = sb.bind()
            try:
                fn()
            finally:
                Sandbox.restore(saved)
                sb.cleanup()
        wrapped.__name__ = fn.__name__
        return wrapped
    return deco


# ----------------------------------------------------------------- fixtures
BOM_PAIR = (  # MW shape: key1 sibling HAS a BOM, key2 sibling does NOT
    ("MW-unique-key1-4.txt", ["a", "b", "c", "d"], True),
    ("MW-unique-key2-4.txt", ["azA", "vidyA", "deva", "agni"], False),
)
SOURCES = [("MW", ["a", "b", "c", "d"], ["azA", "vidyA", "deva", "agni"])]


# ------------------------------------------------------------------- tests
def test_fail_closed_zero_written():
    print("test 1 — fail-closed: 0 snapshots written => non-zero, loud, no writes")
    sb = Sandbox(then_files=BOM_PAIR, sources=())   # then files exist, NO sources
    @with_sandbox(sb)
    def body():
        rc = run_now()
        check("exit code non-zero on zero-written", rc == 1, f"rc={rc}")
        now_txt = sb.now_files()
        check("zero snapshots written", now_txt == [], f"on disk: {now_txt}")
        check("delta sidecar not written on failure",
              not os.path.exists(os.path.join(sb.now_dir, "NOW_COUNT_DELTA.md")))
        # CLI-level: the loud message must reach stderr with the override name
        import io, contextlib
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            run_now()
        msg = err.getvalue()
        check("loud stderr message", "0 now-2026/ snapshots written" in msg and "FAIL-CLOSED" in msg,
              f"stderr={msg[:200]!r}")
        check("message names the CSL_ORIG_V02 override", "CSL_ORIG_V02" in msg)
    body()


def test_fail_closed_no_inputs():
    print("test 2 — fail-closed: empty then-2014 => non-zero")
    sb = Sandbox()   # nothing at all
    @with_sandbox(sb)
    def body():
        rc = run_now()
        check("exit code 2 with no then-2014 inputs", rc == 2, f"rc={rc}")
    body()


def test_bom_preservation():
    print("test 3 — BOM: output byte-begins with the then-2014 sibling's BOM where present")
    sb = Sandbox(then_files=BOM_PAIR, sources=SOURCES)
    @with_sandbox(sb)
    def body():
        rc = run_now()
        check("positive run exits 0", rc == 0, f"rc={rc}")
        p1 = os.path.join(sb.now_dir, "MW-unique-key1-4.txt")
        p2 = os.path.join(sb.now_dir, "MW-unique-key2-4.txt")
        with open(p1, "rb") as fh:
            check("MW key1 regenerated WITH the then-2014 BOM (efbbbf)",
                  fh.read(3) == b"\xef\xbb\xbf")
        with open(p2, "rb") as fh:
            check("MW key2 regenerated with NO BOM (sibling has none)",
                  fh.read(3) != b"\xef\xbb\xbf")
    body()


def test_stable_names_and_pin_drift():
    print("test 4 — stable names: rerun identical; count drift keeps the pinned name")
    sb = Sandbox(then_files=BOM_PAIR, sources=SOURCES)
    @with_sandbox(sb)
    def body():
        rc1 = run_now()
        names1 = sb.now_files()
        check("first generation mints count-bearing names",
              names1 == ["MW-unique-key1-4.txt", "MW-unique-key2-4.txt"], str(names1))
        rc2 = run_now()
        names2 = sb.now_files()
        check("rerun with same source writes IDENTICAL filenames", names1 == names2)
        check("rerun exits 0", rc1 == 0 and rc2 == 0)
        # count drift: source grows 4 -> 5, pinned name must NOT change
        sb.rewrite_source("MW", ["a", "b", "c", "d", "e"])
        rc3 = run_now()
        names3 = sb.now_files()
        check("count drift keeps the pinned filename (no rename churn)",
              names3 == names1, f"now: {names3}")
        with open(os.path.join(sb.now_dir, "MW-unique-key1-4.txt"), encoding="utf-8-sig") as fh:
            n_lines = sum(1 for l in fh if l.strip())
        check("drifted content written in place (5 keys under the pinned name)",
              n_lines == 5, f"lines={n_lines}")
        delta = open(os.path.join(sb.now_dir, "NOW_COUNT_DELTA.md"), encoding="utf-8").read()
        check("drift recorded in NOW_COUNT_DELTA.md",
              "pinned" in delta and "| 5" in delta, delta[:200])
        check("drift run still exits 0", rc3 == 0, f"rc={rc3}")
    body()


def test_positive_control_and_stale_duplicate_cleanup():
    print("test 5 — positive control + stale duplicate cleanup")
    sb = Sandbox(then_files=BOM_PAIR, sources=SOURCES)
    @with_sandbox(sb)
    def body():
        # pre-seed a stale legacy duplicate for the MW key1 pair (highest N wins)
        os.makedirs(sb.now_dir, exist_ok=True)
        legacy = os.path.join(sb.now_dir, "MW-unique-key1-9.txt")
        with open(legacy, "w", encoding="utf-8") as fh:
            fh.write("stale\n")
        rc = run_now()
        names = sb.now_files()
        check("exit 0", rc == 0, f"rc={rc}")
        check("highest-N legacy file is the pin", "MW-unique-key1-9.txt" in names, str(names))
        check("pin content overwritten in place (not stale text; Sanskrit-collated)",
              open(os.path.join(sb.now_dir, "MW-unique-key1-9.txt"),
                   encoding="utf-8-sig").read().split() == ["a", "c", "d", "b"])
        check("no duplicate second file for the pair",
              sum(1 for n in names if n.startswith("MW-unique-key1-")) == 1, str(names))
        check("delta sidecar written",
              os.path.exists(os.path.join(sb.now_dir, "NOW_COUNT_DELTA.md")))
    body()


def main():
    print(f"H6518 selftest — headword_diff.py now-mode write contract (python {sys.version.split()[0]})")
    test_fail_closed_zero_written()
    test_fail_closed_no_inputs()
    test_bom_preservation()
    test_stable_names_and_pin_drift()
    test_positive_control_and_stale_duplicate_cleanup()
    print()
    if _failures:
        print(f"SELFTEST RED — {len(_failures)} failing check(s):")
        for f in _failures:
            print("  - " + f)
        return 1
    print("SELFTEST GREEN — all H6518 write-contract behaviors verified.")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
