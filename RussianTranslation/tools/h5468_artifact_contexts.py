"""H5468 scratch probe: show the real gloss context of H5262's six measurement artifacts.

Read-only over the census + the store. For each artifact lemma the spot-check named, print
its recorded surface forms and the gloss substrings the store actually carries, so the
precision filters of H5468 step 5 are written against real text, not a guess at it.
"""
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
sys.stdout.reconfigure(encoding="utf-8")

import h5262_ipm_audit as audit  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CENSUS = os.path.join(HERE, "..", "reports", "H5262_lemma_census.json")
ARTIFACTS = ["ламывать", "грызать", "сарасватить", "бодхисаттво",
             "десятикратное", "столько-то"]

census = json.load(io.open(CENSUS, encoding="utf-8"))
by_lemma = {r["lemma"]: r for r in census["lemmas"]}

wanted = {}
for lemma in ARTIFACTS:
    row = by_lemma.get(lemma)
    print("\n== %s == occurrences=%s forms=%s cards=%s"
          % (lemma, row and row["occurrences"], row and row["forms"],
             row and row["cards"][:3]))
    for form in (row or {}).get("forms", []):
        wanted[form] = lemma

store = audit.default_store()
pattern = re.compile("|".join(re.escape(f) for f in sorted(wanted, key=len, reverse=True)),
                     re.I)
seen = {}
for rec in audit.iter_store(store):
    text = audit.gloss_text(rec.get("ru"))
    if not text:
        continue
    for m in pattern.finditer(text):
        lemma = wanted.get(m.group(0).lower())
        bucket = seen.setdefault(lemma, [])
        if len(bucket) < 3:
            bucket.append(text[max(0, m.start() - 45):m.end() + 25].replace("\n", " | "))
    if all(len(v) >= 3 for v in seen.values()) and len(seen) == len(ARTIFACTS):
        break

for lemma in ARTIFACTS:
    print("\n-- %s --" % lemma)
    for snippet in seen.get(lemma, ["(no snippet found)"]):
        print("   ..." + snippet + "...")
