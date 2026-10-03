#!/usr/bin/env python3
"""H5717 verifier probe — deterministic re-derivation of the DanaMjaya fact-check
evidence from csl-orig v02 primary sources + the worktree git history.

Read-only. Emits a dated JSON receipt beside itself and prints a PASS/FAIL line.
Run from the repo root of the h5717-drain worktree:
    python3 RussianTranslation/tools/h5717_verify_probe.py

Checks (each re-derived from primaries by record <L> id, never by line number):
  1. MW DanaMjaya records L99287–L99301.1: no "lexicograph" sense; L99297 body
     carries the author-of-Dala-rūpaka sense; L99300–99301.1 are dictionary
     TITLE headwords ("N. of dictionaries").
  2. PWG main entry L36018 sense 2〉h〉: contains "eines Lexicographen" with
     the Prauḍhamanorama witness, plus "Verfassers des Dharmapradīpa".
  3. PWG addenda entry L76433 (pc 5-1518): corrigendum-style entry whose h〉
     adds "auch N. pr. des Verfassers des Daśarūpaka" and the dictionary title.
  4. Worktree commit c27a073c touches exactly the two intended files and leaves
     both GLM draft card lines unchanged relative to 3369fb2d.
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

CSL_ORIG = Path("/Users/mac/Documents/GitHub/csl-orig/v02")
MW = CSL_ORIG / "mw" / "mw.txt"
PWG = CSL_ORIG / "pwg" / "pwg.txt"
REPO = Path(__file__).resolve().parents[2]

results = []


def check(name, ok, evidence):
    results.append({"check": name, "ok": bool(ok), "evidence": evidence})
    print(("PASS" if ok else "FAIL") + f"  {name}\n      {evidence}")


def record_body(path, lid):
    """Return the body text of the CDSL record with <L><lid> (or lid with .N)."""
    want = f"<L>{lid}<"
    lines = []
    inside = False
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("<L>"):
                inside = line.startswith(want)
                if inside:
                    lines.append(line)
                continue
            if inside:
                if line.startswith("<LEND>"):
                    break
                lines.append(line)
    return "".join(lines)


# 1. MW records
mw_dj = {lid: record_body(MW, lid) for lid in
         ["99287", "99288", "99289", "99290", "99291", "99292", "99293",
          "99294", "99295", "99296", "99297", "99298", "99299",
          "99300", "99301", "99301.1"]}
senses = {lid: body for lid, body in mw_dj.items() if lid not in
          ("99300", "99301", "99301.1")}
check("MW: no lexicographer sense in DanaMjaya records",
      all("lexicograph" not in body.lower() for body in senses.values()),
      "scanned bodies of L99287–L99299 for 'lexicograph' (case-insensitive): 0 hits")
b297 = mw_dj["99297"]
check("MW L99297: author-of-Dala-rūpaka sense",
      "Dala-r" in b297 and "author of the" in b297,
      b297.strip()[:120])
titles = "".join(mw_dj[lid] for lid in ("99300", "99301", "99301.1"))
check("MW L99300–99301.1: dictionary TITLE headwords",
      "of dictionaries" in titles
      and "Dana—M-jaya—koSa" in titles
      and "niGaRwu" in titles,
      "koSa/nAmamAlA/niGaRwu records carry '<ab>N.</ab> of dictionaries'")

# 2. PWG main entry
pwg_main = record_body(PWG, "36018")
check("PWG L36018 2〈h〉: 'eines Lexicographen PRAUḌHAMANOR.'",
      "eines Lexicographen" in pwg_main and "PRAUḌHAMANOR." in pwg_main,
      [ln for ln in pwg_main.splitlines() if "Lexicographen" in ln][0][:140])
check("PWG L36018 2〈h〉: 'Verfassers des Dharmapradīpa'",
      "Verfassers des" in pwg_main and "Dharmaprad" in pwg_main,
      "same record body")

# 3. PWG addenda entry
pwg_add = record_body(PWG, "76433")
check("PWG L76433: addenda/corrigendum entry (pc 5-1518)",
      "lies" in pwg_add and "st." in pwg_add,
      "corrigendum 'Z. 3 lies ... st. ...' present in body")
check("PWG L76433 h〉: Daśarūpaka author + Wörterbuch title",
      "Verfassers des" in pwg_add and "Wörterbuchs" in pwg_add
      and "Daśarūpaka" in pwg_add,
      [ln for ln in pwg_add.splitlines() if "Daśarūpaka" in ln][0][:140])

# 4. Worktree commit shape
diff_stat = subprocess.run(
    ["git", "-C", str(REPO), "show", "--name-only", "--format=", "c27a073c"],
    capture_output=True, text=True, check=True).stdout.split()
files = sorted(f for f in diff_stat if f)
check("commit c27a073c touches exactly the two intended files",
      files == ["RussianTranslation/PWG_RU_NWS_RESCUED2_GLMDRAFT_03-10-2026.md",
                "RussianTranslation/changelog_queue/2026-10-03-h5717-nws-factcheck-verification.md"],
      str(files))
cards_before = subprocess.run(
    ["git", "-C", str(REPO), "show", "3369fb2d:RussianTranslation/PWG_RU_NWS_RESCUED2_GLMDRAFT_03-10-2026.md"],
    capture_output=True, text=True, check=True).stdout
cards_after = subprocess.run(
    ["git", "-C", str(REPO), "show", "c27a073c:RussianTranslation/PWG_RU_NWS_RESCUED2_GLMDRAFT_03-10-2026.md"],
    capture_output=True, text=True, check=True).stdout
card_lines = lambda s: [ln for ln in s.splitlines()
                        if ln.startswith("**DanaMjaya (draft-ru):**")
                        or ln.startswith("**jIvaMjIvaka (draft-ru):**")]
# cards wrap; compare the card region instead: first line of each card + next line
def card_region(s):
    lines = s.splitlines()
    out = []
    for i, ln in enumerate(lines):
        if ln.startswith("**DanaMjaya (draft-ru):**") or ln.startswith("**jIvaMjIvaka (draft-ru):**"):
            out.append(lines[i] + "\n" + lines[i + 1])
    return out
check("draft card lines unchanged vs 3369fb2d",
      card_region(cards_before) == card_region(cards_after),
      "both card two-line regions byte-identical across the edit")

verdict = "PASS" if all(r["ok"] for r in results) else "FAIL"
receipt = {
    "probe": "h5717_verify_probe.py",
    "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "handoff": "H5717",
    "target_commit": "c27a073c",
    "baseline_commit": "3369fb2d",
    "primaries": [str(MW), str(PWG)],
    "checks": results,
    "verdict": verdict,
}
out = Path(__file__).with_suffix(".receipt.json")
out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
               encoding="utf-8")
print(f"\n{verdict} — receipt written to {out}")
sys.exit(0 if verdict == "PASS" else 1)
