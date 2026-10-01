#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""h5069_source_support_audit.py — H5069: bounded source-support audit of 30
already-published PWG-RU sense records.

The question is NOT "is the Russian good" (that is the R15/R3434 gate apparatus,
which estimates pool-wide fidelity/equivalence rates with LLM judges). The
question here is narrower and purposive: **does the German source span actually
support the meaning the Russian asserts?** Four verdicts, defined once:

  faithful        — every Russian assertion is licensed by the German span, and
                    every qualification the German attaches survives.
  addition        — the Russian asserts a meaning, referent or specificity the
                    German span does not license (the dangerous class: fluent
                    Russian concealing an unlicensed meaning).
  omission        — the German attaches a qualification (hedge, domain label,
                    restriction, "Gegens.", "bes.", "wohl") that the Russian
                    silently drops, so the Russian reads more certain or more
                    general than the source.
  conflation      — two German senses (or a sense and its sub-sense) are merged
                    into one Russian assertion, or a sense boundary is moved.

Substrate: release/pwg_tm_canonical/canonical.v1.jsonl — ALREADY COMMITTED in a
PUBLIC repo, so quoting it here adds no publication risk (this is why the H178
bake-off substrate, src/pwg_ru_translated.jsonl, is deliberately NOT used: that
store is gitignored and unpublished).

Selection is seedless and fully reproducible: strata are computed from the
record text, and within each stratum the 6 members are the 6 smallest
sha256(record_id) values. Re-running `freeze` on the same store byte-for-byte
reproduces the same 30 ids.

Usage:
  python src/h5069_source_support_audit.py census    # strata sizes, no writes
  python src/h5069_source_support_audit.py freeze    # manifest + frozen sample
  python src/h5069_source_support_audit.py controls  # blind packet + sealed key
  python src/h5069_source_support_audit.py verify    # re-prove the freeze
  python src/h5069_source_support_audit.py score <reviewer_verdicts.json>
  python src/h5069_source_support_audit.py selftest
"""
import argparse
import collections
import hashlib
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STORE = os.path.join(ROOT, "release", "pwg_tm_canonical", "canonical.v1.jsonl")
OUT = os.path.join(ROOT, "pwg_ru", "h5069")

MANIFEST = os.path.join(OUT, "manifest.json")
SAMPLE = os.path.join(OUT, "sample30.jsonl")
CONTROLS = os.path.join(OUT, "controls.jsonl")
CONTROLS_KEY = os.path.join(OUT, "controls_key.json")
PACKET = os.path.join(OUT, "review_packet.jsonl")

N_PER_STRATUM = 6
STRATA = ("short_gloss", "uncertainty", "polysemy", "compound", "citation_dense")
VERDICTS = ("faithful", "addition", "omission", "conflation")

GLOSS_RE = re.compile(r"\{%(.*?)%\}", re.S)
SA_RE = re.compile(r"\{#(.*?)#\}", re.S)
LS_RE = re.compile(r"<ls\b")
AB_RE = re.compile(r"<ab>(.*?)</ab>", re.S)
# 19th-c. lexicographic hedges and "if correct" markers. Deliberately literal:
# an over-clever regex here would silently change the stratum membership and so
# change the frozen sample.
UNCERTAIN_RE = re.compile(
    r"(?<![\w.])(wohl|viell\.|vielleicht|etwa|ungewiss|unsicher|fehlerhaft"
    r"|zweifelhaft|scheinbar|angeblich|verderbt)(?![\w])", re.I)


def _read_store(path=STORE):
    with io.open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def features(row):
    """Text-derived features. Pure function of the record — no randomness."""
    src = row.get("source_string") or ""
    tgt = row.get("target_string") or ""
    loc = row.get("source_locator") or {}
    sm = row.get("structural_markup") or {}
    iast = loc.get("iast") or ""
    hom = loc.get("homonym") or ""
    return {
        "n_gloss_de": len(GLOSS_RE.findall(src)),
        "n_gloss_ru": len(GLOSS_RE.findall(tgt)),
        "n_sa": len(SA_RE.findall(src)),
        "n_ls": len(LS_RE.findall(src)),
        "n_senses": sm.get("n_senses") or 1,
        "uncertain": bool(UNCERTAIN_RE.search(src)),
        "src_len": len(src),
        "identical": row.get("source_hash") == row.get("target_hash"),
        "empty_tgt": not tgt.strip(),
        # A preverb/compound head: PWG writes these as "vraj (upā)" / "upa+jan".
        "compound": bool(re.search(r"[(\-]", iast) or re.search(r"[+\-]", hom)),
    }


def eligible(feat):
    """Auditable at all: the Russian must actually assert a meaning."""
    return (feat["n_gloss_de"] >= 1
            and not feat["identical"]
            and not feat["empty_tgt"])


def stratum_of(feat):
    """Disjoint strata, fixed priority. Priority order is part of the frozen
    contract — changing it changes the sample, so it is declared in the
    manifest and pinned by selftest."""
    if not eligible(feat):
        return None
    if feat["src_len"] <= 200 and feat["n_senses"] == 1:
        return "short_gloss"
    if feat["uncertain"]:
        return "uncertainty"
    if feat["n_senses"] >= 5:
        return "polysemy"
    if feat["compound"]:
        return "compound"
    if feat["n_ls"] >= 10:
        return "citation_dense"
    return None


def rank_key(record_id):
    return hashlib.sha256(record_id.encode("utf-8")).hexdigest()


# Salt is committed, not secret: the point of an opaque packet id is that a
# reviewer cannot tell a control from a real record BY LOOKING, not that the
# mapping is unrecoverable afterwards. Reproducibility beats secrecy here.
PACKET_ID_SALT = "H5069/packet/2026-09-20"


def packet_id(record_id):
    h = hashlib.sha256((PACKET_ID_SALT + "|" + record_id).encode("utf-8"))
    return "H5069.item:" + h.hexdigest()[:32]


def select(rows, n_per=N_PER_STRATUM):
    """-> {stratum: [row, ...]} deterministically."""
    buckets = collections.defaultdict(list)
    for row in rows:
        st = stratum_of(features(row))
        if st:
            buckets[st].append(row)
    out = {}
    for st in STRATA:
        members = sorted(buckets.get(st, []), key=lambda r: rank_key(r["record_id"]))
        out[st] = members[:n_per]
    return out, {st: len(buckets.get(st, [])) for st in STRATA}


def gloss_pairs(row):
    """Index-aligned German/Russian meaning assertions. A length mismatch is
    itself evidence (an unpaired Russian gloss is a structural addition)."""
    de = GLOSS_RE.findall(row.get("source_string") or "")
    ru = GLOSS_RE.findall(row.get("target_string") or "")
    pairs = []
    for i in range(max(len(de), len(ru))):
        pairs.append({
            "i": i,
            "de": de[i].strip() if i < len(de) else None,
            "ru": ru[i].strip() if i < len(ru) else None,
        })
    return pairs


def slim(row, stratum=None):
    feat = features(row)
    rec = {
        "record_id": row["record_id"],
        "sense_id": row.get("sense_id"),
        "entry_id": row.get("entry_id"),
        "src_key": (row.get("source_locator") or {}).get("src_key"),
        "iast": (row.get("source_locator") or {}).get("iast"),
        "source_hash": row.get("source_hash"),
        "target_hash": row.get("target_hash"),
        "source_string": row.get("source_string"),
        "target_string": row.get("target_string"),
        "gloss_pairs": gloss_pairs(row),
        "features": {k: feat[k] for k in
                     ("n_gloss_de", "n_gloss_ru", "n_ls", "n_senses",
                      "uncertain", "src_len", "compound")},
    }
    if stratum:
        rec["stratum"] = stratum
    return rec


def _write_jsonl(path, records):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")


def _write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def cmd_census(args):
    rows = _read_store()
    picked, sizes = select(rows)
    print("store rows: %d" % len(rows))
    print("store sha256: %s" % file_sha256(STORE))
    elig = sum(1 for r in rows if eligible(features(r)))
    print("eligible (RU asserts a meaning, target != source): %d" % elig)
    for st in STRATA:
        print("  %-15s pool=%-5d picked=%d" % (st, sizes[st], len(picked[st])))
    short = [st for st in STRATA if len(picked[st]) < N_PER_STRATUM]
    if short:
        print("UNDERFILLED: %s" % ", ".join(short))
        return 1
    return 0


def cmd_freeze(args):
    rows = _read_store()
    picked, sizes = select(rows)
    frozen = []
    for st in STRATA:
        if len(picked[st]) < N_PER_STRATUM:
            print("REFUSE: stratum %s underfilled (%d < %d)"
                  % (st, len(picked[st]), N_PER_STRATUM), file=sys.stderr)
            return 1
        for row in picked[st]:
            frozen.append(slim(row, st))
    _write_jsonl(SAMPLE, frozen)
    manifest = {
        "handoff": "H5069",
        "generated": args.date,
        "store": {
            "path": "RussianTranslation/release/pwg_tm_canonical/canonical.v1.jsonl",
            "sha256": file_sha256(STORE),
            "bytes": os.path.getsize(STORE),
            "rows": len(rows),
        },
        "selection_rule": {
            "eligibility": "n_gloss_de >= 1 AND source_hash != target_hash AND target_string non-empty",
            "strata_priority": list(STRATA),
            "strata_predicates": {
                "short_gloss": "src_len <= 200 AND n_senses == 1",
                "uncertainty": "German hedge marker present (UNCERTAIN_RE)",
                "polysemy": "n_senses >= 5",
                "compound": "iast has '(' or '-', or homonym has '+' or '-'",
                "citation_dense": "n_ls >= 10",
            },
            "within_stratum": "ascending sha256(record_id), first %d" % N_PER_STRATUM,
            "seed": None,
            "note": "seedless: identical store bytes reproduce identical ids",
        },
        "strata_pool_sizes": sizes,
        "n_selected": len(frozen),
        "sample_sha256": file_sha256(SAMPLE),
        "records": [
            {"record_id": r["record_id"], "sense_id": r["sense_id"],
             "stratum": r["stratum"], "source_hash": r["source_hash"],
             "target_hash": r["target_hash"]}
            for r in frozen
        ],
    }
    _write_json(MANIFEST, manifest)
    print("froze %d records -> %s" % (len(frozen), SAMPLE))
    print("manifest -> %s" % MANIFEST)
    return 0


# --- controls -------------------------------------------------------------
# Both controls are SYNTHETIC records derived from real frozen rows. They never
# enter the store; they exist only in the review packet, so the independent
# reviewer's ability to catch a planted unsupported assertion is measurable.
# ids are prefixed H5069.control: so no downstream reader can mistake them for
# published translations.

def _load_frozen():
    return [json.loads(l) for l in io.open(SAMPLE, encoding="utf-8")]


def cmd_controls(args):
    frozen = _load_frozen()
    spec = json.load(io.open(os.path.join(HERE, "h5069_controls_spec.json"),
                             encoding="utf-8"))
    # TWIN GUARD (added 20-09-2026, second blinding defect). A control whose
    # base record ALSO ships unmutated puts the mutation right beside its own
    # twin, and a reviewer can then find it by diffing two near-identical items
    # instead of by asking what the German licenses. The first reviewer to pass
    # this gate did exactly that, and said so: it named the positive control
    # because a sibling item "renders the byte-identical source" plainly. A
    # gate passed that way measures near-duplicate detection, not source
    # support. Bases now come from eligible records OUTSIDE the frozen 30.
    frozen_ids = {r["record_id"] for r in frozen}
    twins = [c["id"] for c in spec["controls"]
             if c["base_record_id"] in frozen_ids]
    if twins:
        print("REFUSE: control base(s) also ship unmutated in the packet — %s. "
              "Draw the base from an eligible record outside the frozen 30."
              % ", ".join(twins), file=sys.stderr)
        return 1
    store_by_id = {r["record_id"]: r for r in _read_store()}
    blind, key = [], []
    for c in spec["controls"]:
        base = store_by_id.get(c["base_record_id"])
        if base is None:
            print("REFUSE: control %s — base record not in the store" % c["id"],
                  file=sys.stderr)
            return 1
        tgt = base["target_string"]
        if c["find"] not in tgt:
            print("REFUSE: control %s — find-string absent from base target"
                  % c["id"], file=sys.stderr)
            return 1
        mutated = tgt.replace(c["find"], c["replace"], 1)
        if mutated == tgt:
            print("REFUSE: control %s — mutation was a no-op" % c["id"],
                  file=sys.stderr)
            return 1
        rec = {
            "record_id": c["id"],
            "synthetic": True,
            "stratum": "control",
            "source_string": base["source_string"],
            "target_string": mutated,
            "gloss_pairs": gloss_pairs({"source_string": base["source_string"],
                                        "target_string": mutated}),
        }
        blind.append(rec)
        key.append({
            "id": c["id"],
            "packet_id": packet_id(c["id"]),
            "kind": c["kind"],
            "base_record_id": c["base_record_id"],
            "expected_verdict": c["expected_verdict"],
            "planted": c["replace"],
            "original": c["find"],
            "rationale": c["rationale"],
        })
    _write_jsonl(CONTROLS, blind)
    # BLINDING (fixed 20-09-2026 after the first packet failed it): every packet
    # item — real and synthetic alike — carries an OPAQUE id of one shape. The
    # first build shipped ids literally spelling "H5069.control:pos:001", and
    # the first reviewer to open the file named both controls from the id
    # strings before reading a single gloss. An id that announces the answer is
    # not a control. The id -> record map lives only in the sealed key.
    packet = [{"id": packet_id(r["record_id"]),
               "source_string": r["source_string"],
               "target_string": r["target_string"],
               "gloss_pairs": r["gloss_pairs"]}
              for r in frozen + blind]
    packet.sort(key=lambda r: r["id"])
    _write_jsonl(PACKET, packet)
    id_map = {packet_id(r["record_id"]): r["record_id"] for r in frozen + blind}
    if len(id_map) != len(frozen) + len(blind):
        print("REFUSE: packet id collision", file=sys.stderr)
        return 1
    _write_json(CONTROLS_KEY, {"handoff": "H5069", "generated": args.date,
                               "controls": key, "packet_id_map": id_map,
                               "sealed_until": "independent review recorded"})
    print("controls -> %s (%d)" % (CONTROLS, len(blind)))
    print("sealed key + id map -> %s" % CONTROLS_KEY)
    print("blind packet -> %s (%d items, opaque ids)" % (PACKET, len(packet)))
    return 0


def cmd_verify(args):
    """Re-prove the freeze against the live store: same store bytes, same ids,
    same per-record hashes, same sample file."""
    manifest = json.load(io.open(MANIFEST, encoding="utf-8"))
    fails = []
    live_store = file_sha256(STORE)
    if live_store != manifest["store"]["sha256"]:
        fails.append("store sha256 drifted: %s != %s"
                     % (live_store, manifest["store"]["sha256"]))
    rows = _read_store()
    by_id = {r["record_id"]: r for r in rows}
    for rec in manifest["records"]:
        live = by_id.get(rec["record_id"])
        if live is None:
            fails.append("record vanished: %s" % rec["record_id"])
            continue
        if live.get("source_hash") != rec["source_hash"]:
            fails.append("source_hash drift: %s" % rec["record_id"])
        if live.get("target_hash") != rec["target_hash"]:
            fails.append("target_hash drift: %s" % rec["record_id"])
    picked, _ = select(rows)
    reselected = [r["record_id"] for st in STRATA for r in picked[st]]
    if reselected != [r["record_id"] for r in manifest["records"]]:
        fails.append("re-selection does not reproduce the frozen id list")
    live_sample = file_sha256(SAMPLE)
    if live_sample != manifest["sample_sha256"]:
        fails.append("sample30.jsonl sha256 drifted")
    if fails:
        for f in fails:
            print("FAIL %s" % f)
        return 1
    print("VERIFY OK — store %s, %d records, re-selection reproduces the frozen list"
          % (live_store[:12], len(manifest["records"])))
    return 0


def cmd_poolcheck(args):
    """Store-wide CENSUS of the two mechanical defect classes the 30-record
    audit surfaced. This is a census over all 2392 records, not an inference
    from the purposive sample — every record is counted, nothing is estimated.

      gloss_wrapper_loss  — German has >=1 {%...%} span, Russian has fewer.
                            Downstream gloss extractors see the missing spans
                            as "no translation present".
      gloss_wrapper_total — Russian has ZERO spans against >=1 German span.
      ru_in_sanskrit_mask — Cyrillic prose emitted inside a {#...#} span, i.e.
                            Russian wearing Sanskrit markup.
    """
    rows = _read_store()
    cyr = re.compile(r"[А-Яа-яЁё]")
    guill = re.compile(r"«[^»]{1,120}»")
    partial = total = in_sa = guill_sub = 0
    ex = {"partial": [], "total": [], "in_sa": []}
    for r in rows:
        f = features(r)
        tgt = r.get("target_string") or ""
        if f["n_gloss_de"] >= 1 and f["n_gloss_ru"] < f["n_gloss_de"]:
            partial += 1
            if f["n_gloss_ru"] == 0:
                total += 1
                # Did the Russian substitute guillemets where the gloss
                # delimiters used to be? (The German side never has them.)
                if guill.search(tgt) and not guill.search(r["source_string"]):
                    guill_sub += 1
                if len(ex["total"]) < 3:
                    ex["total"].append(r["record_id"])
            elif len(ex["partial"]) < 3:
                ex["partial"].append(r["record_id"])
        if any(cyr.search(s) for s in SA_RE.findall(tgt)):
            in_sa += 1
            if len(ex["in_sa"]) < 3:
                ex["in_sa"].append(r["record_id"])
    n = len(rows)
    print("store rows: %d  (sha256 %s)" % (n, file_sha256(STORE)[:16]))
    print("gloss_wrapper_loss  (RU spans < DE spans): %d/%d = %.1f%%"
          % (partial, n, 100.0 * partial / n))
    print("  of which TOTAL loss (RU spans == 0)    : %d/%d = %.1f%%"
          % (total, n, 100.0 * total / n))
    print("ru_in_sanskrit_mask (Cyrillic in {#..#}) : %d/%d = %.1f%%"
          % (in_sa, n, 100.0 * in_sa / n))
    print("  of the TOTAL-loss rows, guillemets appear where the gloss\n"
          "  delimiters were, and nowhere in the German             : %d/%d"
          % (guill_sub, total))
    for k, v in ex.items():
        for rid in v:
            print("  e.g. %-10s %s" % (k, rid))
    return 0


def cmd_show(args):
    """Human-readable dump of frozen records: the gloss pairs are the audit
    unit — one German source span against one Russian assertion."""
    frozen = _load_frozen()
    if args.stratum:
        frozen = [r for r in frozen if r.get("stratum") == args.stratum]
    for i, r in enumerate(frozen, 1):
        print("=" * 78)
        print("[%02d] %s  |  %s  |  %s" % (i, r.get("stratum"), r["sense_id"],
                                           r.get("iast")))
        print("     n_senses=%s n_ls=%s gloss de/ru=%s/%s len=%s"
              % (r["features"]["n_senses"], r["features"]["n_ls"],
                 r["features"]["n_gloss_de"], r["features"]["n_gloss_ru"],
                 r["features"]["src_len"]))
        for p in r["gloss_pairs"]:
            print("  %2d DE: %s" % (p["i"], p["de"]))
            print("     RU: %s" % p["ru"])
        if args.full:
            print("  --- full source ---")
            print(r["source_string"])
            print("  --- full target ---")
            print(r["target_string"])
    return 0


def cmd_score(args):
    """Grade an independent reviewer's verdicts against the sealed control key.

    Reviewer file: {"reviewer": "...", "model_version": "...",
                    "verdicts": [{"id": ..., "verdict": ...}, ...]}"""
    key = json.load(io.open(CONTROLS_KEY, encoding="utf-8"))
    rev = json.load(io.open(args.path, encoding="utf-8"))
    got = {v["id"]: v.get("verdict") for v in rev["verdicts"]}
    rc = 0
    print("reviewer: %s (%s)" % (rev.get("reviewer"), rev.get("model_version")))
    for c in key["controls"]:
        actual = got.get(c.get("packet_id") or c["id"])
        if c["kind"] == "positive":
            ok = actual in ("addition", "omission", "conflation")
            verdict = "DETECTED" if ok else "MISSED"
        else:
            ok = actual == "faithful"
            verdict = "CLEAN" if ok else "FALSE POSITIVE"
        print("  %-24s %-9s expected=%-10s got=%-10s  %s"
              % (c["id"], c["kind"], c["expected_verdict"], actual, verdict))
        if not ok:
            rc = 1
    ctrl_ids = {c.get("packet_id") or c["id"] for c in key["controls"]}
    n_real = sum(1 for i in got if i not in ctrl_ids)
    print("real records graded by reviewer: %d" % n_real)
    print("CONTROL GATE: %s" % ("PASS" if rc == 0 else "FAIL"))
    return rc


def cmd_selftest(args):
    """Pin the pieces that, if they drift, silently change the frozen sample."""
    ok = True

    def check(name, cond):
        nonlocal ok
        print("%s %s" % ("ok  " if cond else "FAIL", name))
        ok = ok and cond

    check("strata priority order pinned",
          STRATA == ("short_gloss", "uncertainty", "polysemy", "compound",
                     "citation_dense"))
    check("n per stratum pinned", N_PER_STRATUM == 6)
    check("uncertainty regex matches 'wohl'", bool(UNCERTAIN_RE.search("{%wohl%}")))
    check("uncertainty regex matches 'viell.'", bool(UNCERTAIN_RE.search("viell. so")))
    check("uncertainty regex does not match 'sowohl'",
          not UNCERTAIN_RE.search("sowohl als auch"))
    check("uncertainty regex does not match 'Wohlstand'",
          not UNCERTAIN_RE.search("Wohlstand"))
    fake = {"source_string": "{%a%} {%b%}", "target_string": "{%а%} {%б%} {%в%}",
            "source_hash": "x", "target_hash": "y",
            "source_locator": {}, "structural_markup": {"n_senses": 1}}
    check("extra RU gloss surfaces as an unpaired pair",
          gloss_pairs(fake)[2]["de"] is None and gloss_pairs(fake)[2]["ru"] == "в")
    check("short record with one sense lands in short_gloss",
          stratum_of(features(fake)) == "short_gloss")
    same = dict(fake, target_hash="x")
    check("source==target is ineligible", stratum_of(features(same)) is None)
    check("rank_key is deterministic", rank_key("abc") == rank_key("abc"))
    # The blinding regression: a packet id must not reveal that an item is a
    # control. The first packet build shipped literal "H5069.control:pos:001"
    # ids and the first reviewer named both controls from the ids alone.
    pid_ctl = packet_id("H5069.control:pos:001")
    pid_real = packet_id("pwg.tm.v1:exact-card:ru:deadbeef")
    check("packet id hides 'control'", "control" not in pid_ctl)
    check("packet ids share one shape",
          pid_ctl.startswith("H5069.item:") and pid_real.startswith("H5069.item:")
          and len(pid_ctl) == len(pid_real))
    check("packet id is deterministic",
          pid_ctl == packet_id("H5069.control:pos:001"))
    check("packet ids differ per record", pid_ctl != pid_real)
    check("verdict vocabulary pinned",
          VERDICTS == ("faithful", "addition", "omission", "conflation"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--date", default="2026-09-20")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("census", "freeze", "controls", "verify", "selftest", "poolcheck"):
        sub.add_parser(name)
    sc = sub.add_parser("score")
    sc.add_argument("path")
    sh = sub.add_parser("show")
    sh.add_argument("--stratum", choices=STRATA)
    sh.add_argument("--full", action="store_true")
    args = ap.parse_args(argv)
    return {"census": cmd_census, "freeze": cmd_freeze, "controls": cmd_controls,
            "verify": cmd_verify, "score": cmd_score, "show": cmd_show,
            "poolcheck": cmd_poolcheck,
            "selftest": cmd_selftest}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
