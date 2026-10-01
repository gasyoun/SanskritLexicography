"""H5468 scratch probe: list the artifact verdicts of H5262's 30-flag spot-check.

Read-only. Prints lemma + verdict class + note for every card the spot-check did not
confirm, so the precision filters of H5468 step 5 are written against the real cases.
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "..", "reports", "H5262_spotcheck.json")

doc = json.load(io.open(PATH, encoding="utf-8"))
print("keys:", sorted(doc))
for key in sorted(doc):
    value = doc[key]
    if isinstance(value, list):
        print("\n== %s (%d) ==" % (key, len(value)))
        for row in value:
            print(json.dumps(row, ensure_ascii=False)[:400])
    elif not isinstance(value, dict):
        print("%s = %s" % (key, value))
    else:
        print("%s = %s" % (key, json.dumps(value, ensure_ascii=False)[:400]))
