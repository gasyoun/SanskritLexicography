#!/usr/bin/env python3
"""Classify each Monier-Williams headword as text-attested vs lexicographer-listed.

The H1363 union corroboration re-audit
([WITNESS_INDEPENDENCE_REAUDIT_UNION15_2026.md](WITNESS_INDEPENDENCE_REAUDIT_UNION15_2026.md))
works on headword *membership* only — it sees that MW attests a word, not *how*.
FINDINGS §97 v2 established that MW's own ``<ls>L.</ls>`` ("lexicographers")
marker flags koṣa-sourced senses with **no text citation** — MW merely listing
the word. So "MW attests H" overstates independent text-attestation.

This script reads csl-orig ``mw.txt`` and classifies each MW headword (SLP1
``<k1>``, homograph-collapsed to match the union key) as:
  * **text-attested** — the headword's record(s) carry >=1 ``<ls>`` that is NOT
    ``L.`` (a citation to an actual text or authority, e.g. MBh., RV., W.).
  * **not-text-attested** — every ``<ls>`` is ``L.``, or there is no ``<ls>`` at
    all: MW lists the word without citing a text. This is §97's "L.-only" set.

The union is homograph-collapsed, so a headword counts as text-attested if ANY
of its homograph records has a non-``L.`` ``<ls>``.

Validation anchor: §97 v2 measured **59,697 of 194,084** MW headwords (30.8%)
as L.-only; this script's not-text-attested count should land near that.

Output (beside this script): ``mw_non_textattested_slp1.txt`` — one SLP1 key per
line, the headwords MW does NOT text-attest. Committed so the re-audit is
reproducible WITHOUT the (large, external, CC-BY-SA) csl-orig checkout: the flag
per headword is a derived fact, no source prose is carried.

Usage:
    python mw_ls_textattest.py [--mw PATH]

H1389 (follow-up to H1363). Run 20-07-2026 by Opus 4.8 (claude-opus-4-8).
"""

import argparse
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

K1_RE = re.compile(r"<k1>([^<]*)")
LS_RE = re.compile(r"<ls>([^<]*)</ls>")
# MW's lexicographer marker. Treat "L." (and the bare "L") as non-text.
L_ONLY = {"L.", "L"}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--mw",
        default=str(
            Path(__file__).resolve().parents[2] / "csl-orig" / "v02" / "mw" / "mw.txt"
        ),
        help="path to csl-orig/v02/mw/mw.txt (external repo; not in CI)",
    )
    args = ap.parse_args()

    mw_path = Path(args.mw)
    if not mw_path.exists():
        sys.exit(
            f"MW source not found: {mw_path}\n"
            "This step needs the csl-orig checkout (sibling repo). The committed\n"
            "mw_non_textattested_slp1.txt already carries the result for the re-audit."
        )

    # per headword: has it EVER shown a non-L. <ls>?
    has_text = {}      # k1 -> bool
    seen = set()       # every k1 seen (so no-<ls> headwords are counted too)
    records = 0
    cur_k1 = None
    cur_has_text = False

    def flush():
        if cur_k1 is None:
            return
        seen.add(cur_k1)
        if cur_has_text:
            has_text[cur_k1] = True
        else:
            has_text.setdefault(cur_k1, False)

    with open(mw_path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("<L>"):
                flush()
                records += 1
                m = K1_RE.search(line)
                cur_k1 = m.group(1) if m else None
                cur_has_text = False
                continue
            if cur_k1 is None:
                continue
            for ls in LS_RE.findall(line):
                if ls.strip() not in L_ONLY:
                    cur_has_text = True
        flush()

    total = len(seen)
    text_attested = sum(1 for v in has_text.values() if v)
    not_text = total - text_attested

    print(f"MW records (<L> lines): {records}")
    print(f"MW distinct headwords (k1, homograph-collapsed): {total}")
    print(f"  text-attested (>=1 non-L. <ls>): {text_attested} ({text_attested/total:.1%})")
    print(f"  NOT text-attested (L.-only or no <ls>): {not_text} ({not_text/total:.1%})")
    print(f"  §97 v2 anchor: 59,697 L.-only of 194,084 (30.8%) — compare above")

    here = Path(__file__).resolve().parent
    out = here / "mw_non_textattested_slp1.txt"
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        for k1 in sorted(k for k, v in has_text.items() if not v):
            fh.write(k1 + "\n")
    print(f"\nwrote {out} ({not_text} headwords MW does not text-attest)")


if __name__ == "__main__":
    main()
