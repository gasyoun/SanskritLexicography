#!/usr/bin/env python3
"""UTF-8 validity gate — refuse a tracked text file that is not valid UTF-8.

Created 18-10-2026 (H6936 follow-up) after a CP1251 PowerShell console capture
sat in the repo as its only invalid-UTF-8 file: a defect a hand-run audit
found, not a check. See docs/ENCODING_BOM_AUDIT_HEADWORDLISTS_17-10-2026.md
§7.1.

Forbidden condition: a tracked text file whose bytes are not valid UTF-8.
Text-vs-binary is decided by content (a NUL byte in the first 8 KiB marks a
binary and is skipped), not by extension, so an unusually named text file
cannot slip past the gate. A UTF-16/UTF-32 BOM is a failure — the repo rule is
UTF-8 for text; a UTF-8 BOM is valid and intentionally preserved where it
exists (HeadwordLists/ then-2014).

Enforcement surfaces:
  - CI job "UTF-8 validity" in .github/workflows/ci.yml (required on master)
  - .githooks/pre-commit (staged files)
  - .pre-commit-config.yaml (local hook, for pre-commit users)

Usage:
    python tools/utf8_gate.py              # every tracked file (CI)
    python tools/utf8_gate.py --staged     # staged A/C/M/R files only
    python tools/utf8_gate.py --selftest   # positive and negative controls

Exit codes: 0 = all text decoded, 1 = at least one invalid file, 2 = operational
failure (git missing, unreadable path) — fail-closed by default.
"""
from __future__ import annotations

import codecs
import os
import subprocess
import sys
import tempfile
from pathlib import Path

CHUNK = 1 << 20  # 1 MiB streaming chunks; split sequences are legal
HEAD = 8192      # binary sniff window
BOMS = (b"\xff\xfe", b"\xfe\xff", b"\x00\x00\xfe\xff", b"\xff\xfe\x00\x00")


def _decode_reason(exc: UnicodeDecodeError) -> str:
    return f"{exc.reason} (byte 0x{exc.object[exc.start]:02x})"


def _looks_like_utf16_ascii(head: bytes) -> bool:
    """True for BOM-less UTF-16 whose high-byte plane is mostly NUL.

    A plain NUL sniff would call such a file binary and skip it, so a
    UTF-16-encoded text file would pass the gate unseen. Requiring one
    interleaved plane to be >=80 % NUL and the other >=90 % printable ASCII
    keeps this from matching ordinary binaries.
    """
    even, odd = head[0::2], head[1::2]
    if len(even) < 8:
        return False
    def printable(plane: bytes) -> int:
        return sum(1 for b in plane if 32 <= b < 127 or b in (9, 10, 13))

    for high, low in ((odd, even), (even, odd)):
        if high.count(0) / len(high) > 0.8 and printable(low) / len(low) > 0.9:
            return True
    return False


def check_file(path: Path) -> tuple[str, str, int]:
    """Return (status, reason, byte_offset); status is ok | binary | error."""
    try:
        with path.open("rb") as fh:
            head = fh.read(HEAD)
            if head.startswith(BOMS):
                return "error", "UTF-16/UTF-32 BOM — text must be UTF-8", 0
            if b"\x00" in head:
                if _looks_like_utf16_ascii(head):
                    return "error", "UTF-16 without BOM — text must be UTF-8", 0
                return "binary", "NUL byte in the first 8 KiB", 0
            fh.seek(0)
            decoder = codecs.getincrementaldecoder("utf-8")("strict")
            offset = 0
            while True:
                chunk = fh.read(CHUNK)
                if not chunk:
                    break
                try:
                    decoder.decode(chunk)
                except UnicodeDecodeError as exc:  # pragma: no cover - exercised by selftest
                    return "error", _decode_reason(exc), offset + exc.start
                offset += len(chunk)
            try:
                decoder.decode(b"", final=True)
            except UnicodeDecodeError as exc:
                return "error", f"truncated sequence at EOF: {_decode_reason(exc)}", offset + exc.start
    except OSError as exc:
        return "error", f"unreadable: {exc}", 0
    return "ok", "", 0


def _git(*args: str, cwd: Path) -> bytes:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True).stdout


def repo_root() -> Path:
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], check=True, capture_output=True
    ).stdout.decode("utf-8").strip()
    return Path(out)


def select_files(root: Path, staged: bool) -> list[Path]:
    if staged:
        raw = _git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z", cwd=root)
    else:
        raw = _git("ls-files", "-z", cwd=root)
    names = [p.decode("utf-8", "surrogateescape") for p in raw.split(b"\0") if p]
    files: list[Path] = []
    for name in names:
        path = root / name
        if path.is_symlink() or not path.is_file():
            continue
        files.append(path)
    return files


def run(paths: list[Path], root: Path) -> int:
    counts = {"ok": 0, "binary": 0, "error": 0}
    failures: list[tuple[Path, str, int]] = []
    for path in paths:
        status, reason, offset = check_file(path)
        counts[status] += 1
        if status == "error":
            failures.append((path, reason, offset))
    for path, reason, offset in failures:
        try:
            shown = path.relative_to(root)
        except ValueError:
            shown = path
        print(f"FAIL {shown}:{offset}: {reason}", file=sys.stderr)
    total = len(paths)
    if failures:
        print(
            f"utf8-gate: FAIL — {len(failures)} invalid of {counts['ok'] + counts['error']} text "
            f"files ({counts['binary']} binary skipped, {total} tracked)",
            file=sys.stderr,
        )
        return 1
    print(
        f"utf8-gate: OK — {counts['ok']} text files decode as UTF-8 "
        f"({counts['binary']} binary skipped, {total} tracked)"
    )
    return 0


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
    if failed:
        print(f"selftest: FAIL — {failed} of {len(cases)} controls wrong", file=sys.stderr)
        return 1
    print(f"selftest: OK ({len(cases)}/{len(cases)}) — positive controls pass, negatives refuse")
    return 0


def main(argv: list[str]) -> int:
    staged = "--staged" in argv
    if "--selftest" in argv:
        return selftest()
    try:
        root = repo_root()
        paths = select_files(root, staged)
    except (subprocess.CalledProcessError, OSError) as exc:
        print(f"utf8-gate: cannot enumerate files: {exc}", file=sys.stderr)
        return 2
    return run(paths, root)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
