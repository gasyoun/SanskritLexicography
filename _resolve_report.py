"""Resolve the two conflict hunks in the H3207 wave-1 report keeping the PR (HEAD) side."""
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = "docs/H3207_WAVE1_SPLIT_LAYOUT_REPORT_2026-08.md"
s = io.open(p, encoding="utf-8").read()
s2 = re.sub(r"<<<<<<< HEAD\n(.*?)=======\n.*?>>>>>>> origin/master\n", r"\1", s, flags=re.S)
assert "<<<<<<<" not in s2, "markers remain"
assert s2 != s, "nothing resolved"
io.open(p, "w", encoding="utf-8", newline="").write(s2)
print("report resolved, PR side kept,", len(s2), "bytes")
