"""Ad-hoc anomaly scan over the raw KEWA index (H3169 exploration)."""
from __future__ import annotations

import collections
import html
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

SRC = "C:/Users/user/Documents/GitHub/SamudraManthanam/Index/lib/x86_64-win64/Data/KEWA.txt"
CYRILLIC = re.compile(r"[\u0400-\u04FF]")
UPPER = re.compile(r"(?<![\s,(])[A-Z]|^[A-Z]")

lines = open(SRC, encoding="utf-8").read().splitlines()
print("total lines:", len(lines))

cyr = [(i + 1, l) for i, l in enumerate(lines) if CYRILLIC.search(l)]
print("lines with Cyrillic:", len(cyr))
for i, l in cyr[:10]:
    print("  ", i, l[:110])

# capital Latin inside the IAST heading zone (before the first slash group)
caps = collections.Counter()
capex = []
for i, l in enumerate(lines[1:], start=2):
    head = html.unescape(l.split("/")[0])
    for m in re.finditer(r"[A-Z]", head):
        caps[m.group(0)] += 1
        if len(capex) < 25:
            capex.append((i, m.group(0), head.strip()[:80]))
print("\ncapital Latin letters in heading zone:", dict(caps.most_common()))
for e in capex:
    print("  ", e)

# combining breve (U+0306) = the printed "i or ii" variant notation
brv = [i + 1 for i, l in enumerate(lines) if "\u0306" in l]
print("\nlines with combining breve (variant notation):", len(brv))

# other combining marks census
marks = collections.Counter()
for l in lines[1:]:
    for ch in html.unescape(l.split("<br>")[0]):
        if "\u0300" <= ch <= "\u036F":
            marks[f"U+{ord(ch):04X}"] += 1
print("combining marks in heading zone:", dict(marks.most_common()))
