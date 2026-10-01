"""Quick structural profile of the parsed KEWA index (H3169 exploration)."""
from __future__ import annotations

import collections
import sys

from kewa_parse import iter_rows

sys.stdout.reconfigure(encoding="utf-8")

SRC = sys.argv[1] if len(sys.argv) > 1 else (
    "C:/Users/user/Documents/GitHub/SamudraManthanam/Index/lib/x86_64-win64/Data/KEWA.txt"
)

rows = list(iter_rows(SRC))
print(f"rows parsed: {len(rows)}")

noise = collections.Counter()
for r in rows:
    for n in r.noise:
        noise[n] += 1
print("noise classes:", dict(noise))

nhead = collections.Counter(len(r.iast_plain) for r in rows)
print("headings per row:", dict(sorted(nhead.items())))

ratio = collections.Counter()
for r in rows:
    n = len(r.iast_plain)
    f = len(r.file_forms)
    if n == 0:
        ratio["n=0"] += 1
    elif f == n:
        ratio["forms==headings (iast only)"] += 1
    elif f == 2 * n:
        ratio["forms==2x headings (iast+slp1)"] += 1
    else:
        ratio[f"other n={n} f={f}"] += 1
print("machine-key ratio:", dict(ratio.most_common(12)))

print("\n-- rows whose ratio is neither n nor 2n --")
shown = 0
for r in rows:
    n, f = len(r.iast_plain), len(r.file_forms)
    if n and f not in (n, 2 * n):
        print(r.seq, r.vol, r.page, r.deva, r.iast_accented, r.file_forms)
        shown += 1
        if shown >= 15:
            break

print("\n-- rows with any noise flag --")
shown = 0
for r in rows:
    if r.noise:
        print(r.seq, r.noise, r.deva[:2], r.iast_accented[:2], r.file_forms[:3])
        shown += 1
        if shown >= 20:
            break
