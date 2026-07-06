#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_reglue.py — Deliverable 3 of H180 (REGLUE_SPEC.md), Arm A.

Content-aware re-glue: interleave the ALREADY-TRANSLATED sub-cards so each
supplement (SCH / NWS / PW / PWKVN) sits at its relevant PWG sense — proving the
re-glue is FREE (zero re-translation). PWG stays the skeleton; everything hangs
off it (MG). This is the canonical after-translation derived presentation; the
layered store remains canonical.

Consumes ONLY:
  * src/pwg_ru_translated.jsonl        (the `ru` bodies — copied verbatim)
  * src/pwg_ru_relationships.jsonl     (insertion points from build_relationships.py)
It NEVER calls the translate workflow. Every `ru` emitted is asserted
byte-identical to the store (success criterion (a) — proof of zero re-translation).

Outputs per pilot headword:
  * pwg_ru/reglue/<key1>.json          (structured, REGLUE_SPEC §4 schema)
  * pwg_ru/reglue/<key1>.md            (rendered print-oriented card for eyeballing)
  * pwg_ru/reglue/PILOT_SUMMARY.tsv    (per-headword success-criteria table)

Run: python src/build_reglue.py
"""
import sys, os, io, json, re, collections

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STORE = os.path.join(HERE, "pwg_ru_translated.jsonl")
REL = os.path.join(HERE, "pwg_ru_relationships.jsonl")
OUTDIR = os.path.join(ROOT, "pwg_ru", "reglue")

# Pilot set (REGLUE_SPEC §5) — 5/4/3-layer roots.
PILOT = ["gA", "Cid", "Sam", "jIv", "rakz", "vraj", "yat",          # 5-layer
         "DA", "Ap", "Bid", "Buj", "banD", "Sru",                    # 4-layer
         "viS", "siD"]                                               # 3-layer

LAYER_BADGE = {"pw": "PW", "sch": "SCH", "pwkvn": "PWKVN", "nws": "NWS"}


def lead_int(st):
    m = re.match(r"\s*(\d+)", str(st))
    return m.group(1) if m else None


def homonym_of(subcard):
    m = re.search(r"~~(h\d+)", subcard or "")
    return m.group(1) if m else "h0"


def load():
    store = collections.defaultdict(list)          # key1 -> [record]
    with io.open(STORE, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                d = json.loads(line)
                store[d["key1"]].append(d)
    rel = {}                                        # (subcard, sense_tag) -> relationship
    with io.open(REL, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                r = json.loads(line)
                rel[(r["subcard"], r["sense_tag"])] = r["relationship"]
    return store, rel


def reglue_one(key1, records, rel):
    """Return (json_obj, stats). Never re-translates: `ru` copied verbatim."""
    byte_ok = True
    supplements_placed = 0
    supplements_new = 0
    cancels = 0

    # homonym -> ordered PWG skeleton senses
    homs = collections.OrderedDict()

    def hom_slot(h):
        if h not in homs:
            homs[h] = {"h": h, "senses": collections.OrderedDict(), "new_senses": []}
        return homs[h]

    # 1. skeleton — PWG rows, numeric senses first
    pwg_rows = [d for d in records if d.get("layer") == "pwg"]

    def sort_key(d):
        si = lead_int(d.get("sense_tag"))
        return (0, int(si)) if si else (1, str(d.get("sense_tag")))

    for d in sorted(pwg_rows, key=sort_key):
        h = hom_slot(homonym_of(d["subcard"]))
        st = str(d.get("sense_tag"))
        h["senses"][st] = {"sense": st, "pwg_ru": d.get("ru", ""), "supplements": []}

    # 2/3/4. attach non-pwg supplements at their insertion point
    for d in records:
        layer = d.get("layer")
        if layer == "pwg":
            continue
        st = str(d.get("sense_tag"))
        r = rel.get((d["subcard"], st))
        if not r:
            continue
        ip = r["insertion_point"]
        h = hom_slot(ip.get("homonym", homonym_of(d["subcard"])))
        supp = {
            "layer": layer, "badge": LAYER_BADGE.get(layer, layer.upper()),
            "subtype": r["subtype"], "op": r["op"], "ru": d.get("ru", ""),
            "sense_tag": st, "confidence": r.get("confidence", "llm"),
        }
        if r["subtype"] == "foreign_fragment":
            supp["lang"] = r.get("source_lang", "??")
        if r["op"] in ("correct", "delete"):
            supp["cancels"] = True
            cancels += 1

        tgt = str(ip.get("target_sense"))
        if tgt in h["senses"]:
            h["senses"][tgt]["supplements"].append(supp)
            supplements_placed += 1
        else:
            supp["added_by"] = layer
            h["new_senses"].append(supp)
            supplements_new += 1

    obj = {
        "key1": key1,
        "homonyms": [
            {"h": hv["h"],
             "senses": [
                 {"sense": s["sense"], "pwg_ru": s["pwg_ru"],
                  "supplements": s["supplements"]}
                 for s in hv["senses"].values()],
             "new_senses": hv["new_senses"]}
            for hv in homs.values()
        ],
    }
    stats = {
        "key1": key1, "homonyms": len(homs),
        "pwg_senses": sum(len(hv["senses"]) for hv in homs.values()),
        "supplements_placed": supplements_placed,
        "supplements_new": supplements_new,
        "cancels": cancels, "byte_ok": byte_ok,
    }
    return obj, stats


def render_md(obj):
    lines = [f"# Re-glue — {obj['key1']}", ""]
    for hom in obj["homonyms"]:
        lines.append(f"## {hom['h']}")
        lines.append("")
        for s in hom["senses"]:
            lines.append(f"**{s['sense']})** {s['pwg_ru']}")
            for sup in s["supplements"]:
                tag = f"[{sup['badge']}·{sup['subtype']}]"
                strike = " ~~(cancels PWG)~~" if sup.get("cancels") else ""
                lang = f" ‹{sup['lang']}›" if sup.get("lang") else ""
                lines.append(f"  — {tag}{lang}{strike} {sup['ru']}")
            lines.append("")
        for sup in hom["new_senses"]:
            tag = f"[{sup['badge']}·{sup['subtype']} → *new]"
            lang = f" ‹{sup['lang']}›" if sup.get("lang") else ""
            lines.append(f"**+)** {tag}{lang} {sup['ru']}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    store, rel = load()

    summary = []
    for key1 in PILOT:
        recs = store.get(key1)
        if not recs:
            print(f"  [skip] {key1}: not in translated store")
            summary.append((key1, "ABSENT", 0, 0, 0, 0, "-"))
            continue
        obj, stats = reglue_one(key1, recs, rel)

        # hard byte-identity check (success criterion a): every emitted ru body —
        # skeleton AND supplement — must appear verbatim in this headword's store.
        store_ru = {r.get("ru", "") for r in recs}
        bad = 0
        for hom in obj["homonyms"]:
            for s in hom["senses"]:
                if s["pwg_ru"] not in store_ru:
                    bad += 1
                for sup in s["supplements"]:
                    if sup["ru"] not in store_ru:
                        bad += 1
            for sup in hom["new_senses"]:
                if sup["ru"] not in store_ru:
                    bad += 1
        byte_ok = (bad == 0)

        with io.open(os.path.join(OUTDIR, key1 + ".json"), "w", encoding="utf-8") as fh:
            json.dump(obj, fh, ensure_ascii=False, indent=1)
        with io.open(os.path.join(OUTDIR, key1 + ".md"), "w", encoding="utf-8") as fh:
            fh.write(render_md(obj))

        summary.append((key1, "OK" if byte_ok else "BYTE_FAIL",
                        stats["homonyms"], stats["pwg_senses"],
                        stats["supplements_placed"], stats["supplements_new"],
                        stats["cancels"]))
        print(f"  {key1:6s} senses={stats['pwg_senses']:3d} "
              f"placed={stats['supplements_placed']:3d} "
              f"new={stats['supplements_new']:2d} cancels={stats['cancels']} "
              f"byte_ok={byte_ok}")

    with io.open(os.path.join(OUTDIR, "PILOT_SUMMARY.tsv"), "w", encoding="utf-8") as fh:
        fh.write("key1\tstatus\thomonyms\tpwg_senses\tsupp_placed\tsupp_new\tcancels\n")
        for row in summary:
            fh.write("\t".join(str(x) for x in row) + "\n")

    built = sum(1 for r in summary if r[1] == "OK")
    print(f"\nreglue pilot: {built}/{len(PILOT)} headwords built (zero re-translation)")
    print(f"wrote {OUTDIR}\\*.json, *.md, PILOT_SUMMARY.tsv")


if __name__ == "__main__":
    main()
