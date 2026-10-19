#!/usr/bin/env python3
"""H5263 A/B — pre-fetch the NKRYa evidence for the two A/B cards into committed JSON.

The paid half runs on the Windows box, which has no NKRYa token; this Mac does. So the
evidence is fetched here once (live, through the ONE shared cached client), committed as
`pwg_ru/h5263/evidence_<card>.json` plus the new `pwg_ru/nkrya_cache` entries, and the
Windows run injects it offline with `inject_file` below — 0 NKRYa calls there.

Card choice (both carry an MG-voted gold rendering, H5069 chat vote 22-09-2026):
  han~~h0_57_sam_0  C07 «{#meGAH#} {%zusammenhängend%}» — clouds collocation (gold: deferred,
                    MG: «тучи сгущаются»); heads/candidates = the C07 evidence card, cached.
  yat~~h0_01_sec_1  C02 «verbünden, vereinigen» -> store «союзить» (non-word; gold
                    «связывать союзом, объединять»). Head союз:S is the noun of German
                    «Bund»; candidates = the store word, the gold verb and two common
                    synonyms. Disclosed leak: the gold verb is among the candidates, as the
                    audit proposal would have put it there in production too.

  python tools/h5263_ab_evidence.py fetch            # Mac, live NKRYa (~14 calls)
  python tools/h5263_ab_evidence.py inject M.json OUT.json CARD   # anywhere, offline
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "src")
for path in (SRC, os.path.join(SRC, "pilot")):
    if path not in sys.path:
        sys.path.insert(0, path)

import nkrya_client as nk  # noqa: E402
import nkrya_evidence_card as card  # noqa: E402
import nkrya_prompt_evidence as npe  # noqa: E402

OUT_DIR = os.path.join(ROOT, "pwg_ru", "h5263")
CARDS = {
    "han~~h0_57_sam_0": ("туча:S,облако:S",
                         "связный:A,сплочённый:A,сплошной:A,"
                         "сгущающийся=сгущаться:V,сомкнутый=сомкнуть:V"),
    "yat~~h0_01_sec_1": ("союз:S",
                         "союзить:V,связывать:V,объединять:V,соединять:V"),
}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def _path(key):
    return os.path.join(OUT_DIR, "evidence_%s.json" % key.split("~~")[0])


def fetch():
    os.makedirs(OUT_DIR, exist_ok=True)
    cli = nk.NkryaClient()
    for key, (heads, cands) in CARDS.items():
        ev = npe.build_evidence(cli, card.parse_items(heads), card.parse_items(cands))
        ev["card"] = key
        with open(_path(key), "w", encoding="utf-8", newline="\n") as f:
            json.dump(ev, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print("%s: %d head(s), %d candidate(s) -> %s"
              % (key, len(ev["heads"]), len(ev["candidates"]), _path(key)))
        print(npe.render_block(ev))


def inject_file(manifest_path, out_path, key):
    with open(_path(key), encoding="utf-8") as f:
        ev = json.load(f)
    ev.pop("card", None)
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)
    npe.inject(manifest, key, ev)
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("injected %s -> %s" % (key, out_path))


if __name__ == "__main__":
    if sys.argv[1:2] == ["fetch"]:
        fetch()
    elif sys.argv[1:2] == ["inject"] and len(sys.argv) == 5:
        inject_file(*sys.argv[2:5])
    else:
        sys.exit(__doc__)
