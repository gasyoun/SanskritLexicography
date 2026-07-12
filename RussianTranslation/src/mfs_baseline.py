#!/usr/bin/env python
r"""Most-frequent-sense (MFS) baseline per lemma — roadmap card 5 (evaluation spine).

Card 5's claim: "A simple MFS baseline is necessary to keep WSD and learner-ranking
claims honest." This emitter is that honesty floor. It reads the translated store
(read-only), groups sense rows by ``key1``, and emits one deterministic MFS
candidate per lemma, plus an explicit ``unknown`` outcome when the lemma has no
DCS frequency evidence (acceptance: "every lemma with >= 2 senses and DCS
frequency evidence gets a deterministic MFS candidate plus an unknown outcome
when evidence is absent").

WHY "first-listed sense" and not a corpus MFS: a true corpus MFS needs
sense-annotated token counts. The DCS frequency signal (``annotate_dcs_freq.py``)
is per-LEMMA, not per-sense — every sense of a lemma shares one count — so it
cannot rank senses. The honest deterministic baseline is therefore the WordNet-
style *first-sense* heuristic: the dictionary's own primary (lowest-numbered)
sense. DCS attestation is used only as the applicability gate — an MFS baseline
is meaningful only for a lemma that actually occurs in the corpus; a lemma absent
from DCS yields ``unknown`` (there is no token whose sense we would be predicting).

The score this baseline is measured against needs a frozen, sense-labelled gold
slice, which does not exist yet — see GOLD_SLICE_NEEDS_CAPABILITY_ROADMAP.md. This
script emits the baseline and its coverage; the accuracy number is gold-gated.

Read-only over the store. Output ``src/pwg_mfs_baseline.jsonl`` is gitignored
(derived from the local-only store, like pwg_sense_stratum.jsonl). No LLM, no network.

  python src/mfs_baseline.py                  # emit sidecar + coverage report
  python src/mfs_baseline.py --dry-run         # coverage report only, no write
  python src/mfs_baseline.py --selftest
"""
import argparse
import json
import os
import re
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
STORE = os.path.join(HERE, "pwg_ru_translated.jsonl")
FREQ = os.path.join(HERE, "dcs_freq.json")
OUT = os.path.join(HERE, "pwg_mfs_baseline.jsonl")

_LEAD_INT = re.compile(r"\s*(\d+)")
_ANY_INT = re.compile(r"(\d+)")


def sense_sort_key(row, idx):
    """Deterministic dictionary-order key for one sense row.

    Plain numbered senses ("1", "2", ...) sort first, by their number — the
    lowest is the lexicographer's primary sense. Labelled/derived senses
    ("Kaus. 2)", "Intens.", "Desid.") sort after every plain-numbered sense.
    ``subcard`` then original file index break ties, so the ordering is total
    and stable regardless of store row order.
    """
    tag = (row.get("sense_tag") or "").strip()
    m = _LEAD_INT.match(tag)
    if m:
        return (0, int(m.group(1)), row.get("subcard", ""), idx)
    m2 = _ANY_INT.search(tag)
    return (1, int(m2.group(1)) if m2 else 0, row.get("subcard", ""), idx)


def mfs_for_lemma(rows, freq_fn):
    """Build the MFS record for one key1 group (list of sense rows, file order).

    ``freq_fn(iast) -> dict`` returns a DCS frequency block with at least
    ``attested``/``band``/``count``/``matched`` (production: annotate_dcs_freq.freq_block;
    selftest: a stub). Returns the emit dict for this lemma.
    """
    ordered = sorted((r for r in rows), key=lambda r: sense_sort_key(r, rows.index(r)))
    first = ordered[0]
    homonyms = sorted({(r.get("h") or "") for r in rows})
    freq = freq_fn(first.get("iast"))
    rec = {
        "key1": first.get("key1"),
        "iast": first.get("iast"),
        "homonyms": homonyms,
        "n_homonyms": len(homonyms),
        "n_senses": len(rows),
        "dcs": {
            "attested": bool(freq.get("attested")),
            "band": freq.get("band", 0),
            "count": freq.get("count", 0),
            "matched": freq.get("matched", "none"),
        },
    }
    if not freq.get("attested"):
        rec["mfs"] = None
        rec["mfs_status"] = "unknown"
        rec["reason"] = "no-dcs-attestation"
        return rec
    basis = "single-sense" if len(rows) == 1 else "first-listed-sense"
    rec["mfs"] = {
        "sense_tag": first.get("sense_tag"),
        "subcard": first.get("subcard"),
        "basis": basis,
    }
    rec["mfs_status"] = "candidate"
    return rec


def build(rows, freq_fn):
    """Group rows by key1 (roadmap card 5) and emit one MFS record per lemma."""
    groups = defaultdict(list)
    for r in rows:
        groups[r.get("key1")].append(r)
    out = [mfs_for_lemma(g, freq_fn) for _, g in sorted(groups.items(), key=lambda kv: (kv[0] or ""))]
    return out


def summarize(records):
    n = len(records)
    poly = [r for r in records if r["n_senses"] >= 2]
    cand = [r for r in records if r["mfs_status"] == "candidate"]
    unknown = [r for r in records if r["mfs_status"] == "unknown"]
    poly_cand = [r for r in poly if r["mfs_status"] == "candidate"]
    bands = {b: 0 for b in range(6)}
    for r in records:
        bands[r["dcs"]["band"]] = bands.get(r["dcs"]["band"], 0) + 1
    return {
        "lemmas": n,
        "polysemous(>=2 senses)": len(poly),
        "mfs candidates": len(cand),
        "  of which polysemous": len(poly_cand),
        "unknown (no DCS)": len(unknown),
        "band distribution": bands,
    }


def print_report(records):
    s = summarize(records)
    print("=== MFS BASELINE (card 5) ===")
    print("lemmas (key1 groups)      : %d" % s["lemmas"])
    print("polysemous (>=2 senses)   : %d" % s["polysemous(>=2 senses)"])
    print("MFS candidates emitted    : %d" % s["mfs candidates"])
    print("  of which polysemous     : %d" % s["  of which polysemous"])
    print("unknown (no DCS evidence) : %d" % s["unknown (no DCS)"])
    print("band distribution         : " + ", ".join(
        "%d:%d" % (b, s["band distribution"][b]) for b in range(5, -1, -1)))


def selftest():
    # Three lemmas: a polysemous DCS-attested lemma, a single-sense attested lemma,
    # and a polysemous lemma absent from DCS (-> unknown).
    rows = [
        {"key1": "Ap", "iast": "āp", "h": "{T1}", "sense_tag": "6", "subcard": "_ap~~h0_06"},
        {"key1": "Ap", "iast": "āp", "h": "{T1}", "sense_tag": "1", "subcard": "_ap~~h0_01"},
        {"key1": "Ap", "iast": "āp", "h": "{T1}", "sense_tag": "Kaus. 2)", "subcard": "_ap~~h0_k2"},
        {"key1": "gam", "iast": "gam", "h": "{T2}", "sense_tag": "1", "subcard": "_gam~~h0_01"},
        {"key1": "zzq", "iast": "zzq", "h": "", "sense_tag": "1", "subcard": "_zzq_01"},
        {"key1": "zzq", "iast": "zzq", "h": "", "sense_tag": "2", "subcard": "_zzq_02"},
    ]
    by = {"āp": {"attested": True, "band": 4, "count": 120, "matched": "compound"},
          "gam": {"attested": True, "band": 5, "count": 5000, "matched": "compound"}}

    def stub_freq(iast):
        return by.get(iast, {"attested": False, "band": 0, "count": 0, "matched": "none"})

    recs = {r["key1"]: r for r in build(rows, stub_freq)}
    # sense ordering: primary sense "1" wins over "6" and labelled "Kaus. 2)"
    assert recs["Ap"]["mfs"]["sense_tag"] == "1", recs["Ap"]
    assert recs["Ap"]["mfs"]["basis"] == "first-listed-sense", recs["Ap"]
    assert recs["Ap"]["n_senses"] == 3, recs["Ap"]
    # single-sense attested lemma -> trivial candidate, labelled as such
    assert recs["gam"]["mfs"]["basis"] == "single-sense", recs["gam"]
    # polysemous but absent from DCS -> unknown, no candidate
    assert recs["zzq"]["mfs"] is None and recs["zzq"]["mfs_status"] == "unknown", recs["zzq"]
    assert recs["zzq"]["reason"] == "no-dcs-attestation", recs["zzq"]
    # summary sanity
    s = summarize(list(recs.values()))
    assert s["lemmas"] == 3 and s["mfs candidates"] == 2 and s["unknown (no DCS)"] == 1, s
    # labelled-sense sort: "Kaus. 2)" must sort after plain numbered senses
    assert sense_sort_key({"sense_tag": "Kaus. 2)", "subcard": "x"}, 0)[0] == 1
    assert sense_sort_key({"sense_tag": "1", "subcard": "x"}, 0)[0] == 0
    print("mfs_baseline selftest OK")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--store", default=STORE)
    ap.add_argument("--freq", default=FREQ)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    # Lazy import so --selftest stays hermetic (no dcs_freq.json / build_dcs_freq needed).
    from annotate_dcs_freq import freq_block
    by_lemma = json.load(open(args.freq, encoding="utf-8"))["by_lemma"]

    def freq_fn(iast):
        return freq_block(iast, by_lemma)

    rows = [json.loads(l) for l in open(args.store, encoding="utf-8") if l.strip()]
    records = build(rows, freq_fn)
    print_report(records)
    if args.dry_run:
        print("\n(dry run — sidecar not written)")
        return
    with open(args.out + ".tmp", "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(args.out + ".tmp", args.out)
    print("\nwrote MFS baseline -> %s (%d lemmas)" % (args.out, len(records)))


if __name__ == "__main__":
    main()
