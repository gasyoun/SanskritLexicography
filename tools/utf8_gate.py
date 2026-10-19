#!/usr/bin/env python3
"""UTF-8 validity gate — refuse a tracked text file that is not valid UTF-8.

Created 18-10-2026 (H6936 follow-up) after a CP1251 PowerShell console capture
sat in the repo as its only invalid-UTF-8 file: a defect a hand-run audit
found, not a check. See docs/ENCODING_BOM_AUDIT_HEADWORDLISTS_17-10-2026.md
§7.1.

Forbidden condition: a tracked text file whose bytes are not valid UTF-8.
Text-vs-binary is decided by content, not by extension, so an unusually named
text file cannot slip past the gate. A UTF-16/UTF-32 BOM is a failure — the
repo rule is UTF-8 for text; a UTF-8 BOM is valid and intentionally preserved
where it exists (HeadwordLists/ then-2014).

Fixed 19-10-2026 (BUGHUNT-FINDINGS-SanskritLexicography-19.10.2026.md §2, §5):

* ``--staged`` decodes the **staged blob** from the index (``git cat-file blob
  :<path>``), not the working-tree file. Until then the pre-commit hook
  validated whatever was on disk, so an invalid blob could be committed by
  staging it and then fixing the file without re-staging (and the mirror case
  was a false refusal).
* BOM-less UTF-16 is recognised **structurally**, not by ASCII density. The old
  ``_looks_like_utf16_ascii`` needed a NUL-heavy high-byte plane, which Latin
  text has and Cyrillic (0x04xx) / Devanagari (0x09xx) never do — so exactly
  the Windows-PowerShell-capture class the gate was built for was skipped as
  "binary". Text is now recognised by decoding the head as UTF-16LE/BE and
  requiring ≥95 % printable characters; a file that decodes as UTF-8 but is
  dense in control characters (≥2 % — the densest tracked text file in this
  repo is 0.41 %) is probed the same way and, if it is not UTF-16, counted as
  binary rather than passed as text.

Enforcement surfaces:
  - CI job "UTF-8 validity" in .github/workflows/ci.yml (required on master)
  - .githooks/pre-commit (staged files, from the index)
  - .pre-commit-config.yaml (local hook, for pre-commit users)

Usage:
    python tools/utf8_gate.py              # every tracked file (CI, worktree)
    python tools/utf8_gate.py --staged     # staged A/C/M/R blobs, from the index
    python tools/utf8_gate.py --selftest   # positive and negative controls

Exit codes: 0 = all text decoded, 1 = at least one invalid file, 2 = operational
failure (git missing, unreadable path) — fail-closed by default.
"""
from __future__ import annotations

import codecs
import io
import subprocess
import sys
import tempfile
from pathlib import Path

CHUNK = 1 << 20  # 1 MiB streaming chunks; split sequences are legal
HEAD = 8192      # binary/UTF-16 sniff window
BOMS = (b"\xff\xfe", b"\xfe\xff", b"\x00\x00\xfe\xff", b"\xff\xfe\x00\x00")
UTF16_ENCODINGS = ("utf-16-le", "utf-16-be")
# Share of C0 control characters at which decoded text stops looking like text.
# Measured 19-10-2026 over the 5,352 valid-UTF-8 tracked files: the densest is
# 0.405 % (literature/md/SanskritLibrary/Scharf_SanskritCharacters12Fonts_2023.md),
# none reaches 1 %. 2 % is therefore a 5x margin, not a tuned guess.
TEXT_CONTROL_MAX = 0.02


def _decode_reason(exc: UnicodeDecodeError) -> str:
    return f"{exc.reason} (byte 0x{exc.object[exc.start]:02x})"


def _printable_ratio(text: str) -> float:
    if not text:
        return 1.0
    good = sum(1 for ch in text if ch.isprintable() or ch in "\t\n\r")
    return good / len(text)


def _control_ratio(text: str) -> float:
    if not text:
        return 0.0
    ctrl = sum(1 for ch in text if ord(ch) < 32 and ch not in "\t\n\r")
    return ctrl / len(text)


def _utf16_text_encoding(head: bytes) -> str | None:
    """Name the UTF-16 variant if the head decodes to plausible text.

    Structural, not ASCII-density based: a BOM-less UTF-16 file of Russian or
    Devanagari has no NUL-heavy plane, so the old printable-ASCII test called
    it binary and skipped it unseen (BUGHUNT §5). Requiring 95 % printable
    characters keeps compressed data (whose code points are largely
    unassigned/control) out.
    """
    if len(head) < 8:
        return None
    body = head[: (len(head) // 2) * 2]
    for enc in UTF16_ENCODINGS:
        try:
            text = body.decode(enc)
        except UnicodeDecodeError:
            continue
        if len(text) < 4:
            continue
        if _printable_ratio(text) >= 0.95:
            return enc
    return None


def _check_stream(fh) -> tuple[str, str, int]:
    """Return (status, reason, byte_offset); status is ok | binary | error."""
    head = fh.read(HEAD)
    if head.startswith(BOMS):
        return "error", "UTF-16/UTF-32 BOM — text must be UTF-8", 0
    if b"\x00" in head:
        enc = _utf16_text_encoding(head)
        if enc:
            return "error", f"UTF-16 without BOM ({enc}) — text must be UTF-8", 0
        return "binary", "NUL byte in the first 8 KiB", 0
    fh.seek(0)
    decoder = codecs.getincrementaldecoder("utf-8")("strict")
    offset = 0
    decoded: list[str] = []
    while True:
        chunk = fh.read(CHUNK)
        if not chunk:
            break
        try:
            decoded.append(decoder.decode(chunk))
        except UnicodeDecodeError as exc:
            return "error", _decode_reason(exc), offset + exc.start
        offset += len(chunk)
    try:
        decoded.append(decoder.decode(b"", final=True))
    except UnicodeDecodeError as exc:
        return "error", f"truncated sequence at EOF: {_decode_reason(exc)}", offset + exc.start
    text = "".join(decoded)
    if _control_ratio(text) >= TEXT_CONTROL_MAX:
        enc = _utf16_text_encoding(head)
        if enc:
            return "error", f"UTF-16 without BOM ({enc}) — text must be UTF-8", 0
        return "binary", "control-character density ≥ 2 % (not text)", 0
    return "ok", "", 0


def check_file(path: Path) -> tuple[str, str, int]:
    """Classify a worktree file (see :func:`_check_stream`)."""
    try:
        with path.open("rb") as fh:
            return _check_stream(fh)
    except OSError as exc:
        return "error", f"unreadable: {exc}", 0


def check_bytes(payload: bytes) -> tuple[str, str, int]:
    """Classify an in-memory payload — the staged blob, not the worktree."""
    return _check_stream(io.BytesIO(payload))


def _git(*args: str, cwd: Path) -> bytes:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True).stdout


def repo_root() -> Path:
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], check=True, capture_output=True
    ).stdout.decode("utf-8").strip()
    return Path(out)


def worktree_files(root: Path) -> list[Path]:
    """Every tracked file that exists in the worktree (symlinks skipped)."""
    raw = _git("ls-files", "-z", cwd=root)
    names = [p.decode("utf-8", "surrogateescape") for p in raw.split(b"\0") if p]
    files: list[Path] = []
    for name in names:
        path = root / name
        if path.is_symlink() or not path.is_file():
            continue
        files.append(path)
    return files


def staged_blobs(root: Path) -> list[tuple[str, bytes]]:
    """(path, bytes) for every staged A/C/M/R entry, read from the INDEX.

    The index mode is consulted so a staged symlink is skipped, exactly as
    :func:`worktree_files` skips one on disk.
    """
    raw = _git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z", cwd=root)
    names = [p.decode("utf-8", "surrogateescape") for p in raw.split(b"\0") if p]
    if not names:
        return []
    modes: dict[str, bytes] = {}
    for rec in _git("ls-files", "-s", "-z", cwd=root).split(b"\0"):
        if not rec:
            continue
        meta, _, path = rec.partition(b"\t")
        modes[path.decode("utf-8", "surrogateescape")] = meta.split(b" ")[0]
    out: list[tuple[str, bytes]] = []
    for name in names:
        if modes.get(name) == b"120000":
            continue
        proc = subprocess.run(
            ["git", "cat-file", "blob", ":" + name], cwd=root, capture_output=True
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"cannot read staged blob for {name}: "
                + proc.stderr.decode("utf-8", "replace").strip()
            )
        out.append((name, proc.stdout))
    return out


def _report(failures: list[tuple[str, str, int]], counts: dict[str, int], total: int,
            mode: str) -> int:
    for shown, reason, offset in failures:
        print(f"FAIL {shown}:{offset}: {reason}", file=sys.stderr)
    if failures:
        text_files = counts["ok"] + counts["error"]
        print(
            f"utf8-gate: FAIL — {len(failures)} invalid of {text_files} text "
            f"files ({counts['binary']} binary skipped, {total} {mode})",
            file=sys.stderr,
        )
        return 1
    print(
        f"utf8-gate: OK — {counts['ok']} text files decode as UTF-8 "
        f"({counts['binary']} binary skipped, {total} {mode})"
    )
    return 0


def run_worktree(paths: list[Path], root: Path) -> int:
    counts = {"ok": 0, "binary": 0, "error": 0}
    failures: list[tuple[str, str, int]] = []
    for path in paths:
        status, reason, offset = check_file(path)
        counts[status] += 1
        if status == "error":
            try:
                shown = str(path.relative_to(root))
            except ValueError:
                shown = str(path)
            failures.append((shown, reason, offset))
    return _report(failures, counts, len(paths), "tracked")


def run_staged(entries: list[tuple[str, bytes]], root: Path) -> int:
    counts = {"ok": 0, "binary": 0, "error": 0}
    failures: list[tuple[str, str, int]] = []
    for name, payload in entries:
        status, reason, offset = check_bytes(payload)
        counts[status] += 1
        if status == "error":
            failures.append((name, reason, offset))
    return _report(failures, counts, len(entries), "staged")


def selftest() -> int:
    cases: list[tuple[str, bytes, str]] = [
        ("ok-utf8.txt", "Привет, мир — →\n".encode("utf-8"), "ok"),
        ("ok-utf8-bom.txt", b"\xef\xbb\xbfhi\n", "ok"),
        ("empty.txt", b"", "ok"),
        ("bad-ff.txt", b"ok\xffbad\n", "error"),
        ("truncated.txt", b"abc\xc3", "error"),
        ("binary.bin", b"\x00\x01\x02\x03", "binary"),
        ("utf16le.txt", b"\xff\xfeh\x00i\x00", "error"),
        ("utf16le-nobom.txt", "hello world\n".encode("utf-16-le"), "error"),
        # BUGHUNT §5: the non-Latin cases the ASCII-density sniff used to skip.
        ("utf16le-ru-nobom.txt", "Привет, мир. Словарь.\n".encode("utf-16-le"), "error"),
        ("utf16be-ru-nobom.txt", "Привет, мир.\n".encode("utf-16-be"), "error"),
        ("utf16le-deva-nobom.txt", "नमस्ते देवनागरी\n".encode("utf-16-le"), "error"),
        # Devanagari has no U+00xx code point at all, so UTF-16LE of it carries
        # no NUL byte: the NUL branch never fires and the bytes are valid UTF-8
        # as control-character soup. The density probe must still refuse it.
        ("utf16le-deva-nonul.txt", "नमस्ते\n".encode("utf-16-le"), "error"),
        ("png-like.bin", b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10", "binary"),
        (
            "boundary.txt",
            b"a" * (CHUNK - 1) + "é".encode("utf-8") + b"z",
            "ok",
        ),
    ]
    failed = 0
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        for name, payload, expected in cases:
            path = base / name
            path.write_bytes(payload)
            status, reason, offset = check_file(path)
            good = status == expected
            failed += 0 if good else 1
            print(f"selftest {'PASS' if good else 'FAIL'} {name}: {status} (expected {expected})"
                  + (f" — {reason} at {offset}" if status == "error" else ""))
        failed += _selftest_staged(base / "staged")
    if failed:
        print(f"selftest: FAIL — {failed} of {len(cases) + 2} controls wrong", file=sys.stderr)
        return 1
    print(f"selftest: OK ({len(cases) + 2}/{len(cases) + 2}) — positive controls pass, "
          f"negatives refuse, staged mode reads the index")
    return 0


def _selftest_staged(base: Path) -> int:
    """Staged mode must judge the INDEX blob, not the worktree file.

    Both directions are controlled: invalid index + valid worktree must fail
    (the §2 defect), valid index + invalid worktree must pass (the mirror false
    refusal). The old selftest never touched --staged, which is why the defect
    survived.
    """
    import contextlib

    base.mkdir(parents=True, exist_ok=True)
    for args in (["init", "-q"], ["config", "user.email", "selftest@example.invalid"],
                 ["config", "user.name", "selftest"]):
        subprocess.run(["git", *args], cwd=base, check=True, capture_output=True)
    (base / "a.txt").write_bytes(b"seed\n")
    subprocess.run(["git", "add", "a.txt"], cwd=base, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-qm", "seed"], cwd=base, check=True, capture_output=True)

    failed = 0
    # 1. invalid blob staged, then the file fixed without re-staging
    (base / "a.txt").write_bytes(b"ok \xff bad\n")
    subprocess.run(["git", "add", "a.txt"], cwd=base, check=True, capture_output=True)
    (base / "a.txt").write_bytes(b"now valid utf8\n")
    err = io.StringIO()
    with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
        rc = run_staged(staged_blobs(base), base)
    good = rc == 1 and "a.txt" in err.getvalue()
    failed += 0 if good else 1
    print(f"selftest {'PASS' if good else 'FAIL'} staged-invalid-worktree-valid: "
          f"rc={rc} (expected 1, FAIL names a.txt)")

    # 2. valid blob staged, worktree still invalid (must NOT be refused)
    (base / "a.txt").write_bytes(b"valid staged\n")
    subprocess.run(["git", "add", "a.txt"], cwd=base, check=True, capture_output=True)
    (base / "a.txt").write_bytes(b"worktree \xff junk\n")
    with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
        rc = run_staged(staged_blobs(base), base)
    good = rc == 0
    failed += 0 if good else 1
    print(f"selftest {'PASS' if good else 'FAIL'} staged-valid-worktree-invalid: "
          f"rc={rc} (expected 0)")
    return failed


def main(argv: list[str]) -> int:
    staged = "--staged" in argv
    if "--selftest" in argv:
        return selftest()
    try:
        root = repo_root()
        if staged:
            return run_staged(staged_blobs(root), root)
        return run_worktree(worktree_files(root), root)
    except (subprocess.CalledProcessError, OSError, RuntimeError) as exc:
        print(f"utf8-gate: cannot enumerate files: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
