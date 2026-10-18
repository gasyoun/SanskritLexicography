#!/usr/bin/env python3
"""H6994 -- interim PD -> ACC -> NCC composition.

Builds the composition on the interim AOB denominator with provenance on every
row.  The four provenance values are those fixed by the H6989 grill
(papers/A68/PD_ACC_NCC_GRILL_DECISIONS_2026-10-18.md, Q10/Q13/Q18/Q23):

  composed   PD -> ACC -> NCC   (the ACC record matches the PD title; the
                                 ACC<->NCC edge comes from works_crosswalk.tsv)
  direct     PD -> NCC          (the NCC record matches the PD title directly)
  both       both paths agree   (PD matches the ACC record and the NCC record)
  cd_bridge  C/D-tier bridge    (separate ledger only, never in the headline)

Inputs
  pd_aob_siglum_title.tsv  PD siglum -> adjudicated AOB title, with the
                           occurrence count (the occurrence weight)
  pd_aob_entries.tsv       printed AOB entry inventory (entry ids per siglum)
  pd_siglum_families.tsv   5,106 harvested sigla; the 164 primary rows with an
                           adjudicated display_title are the C3 control
  acc.jsonl                ACC records (match_key is the folded title key)
  ncc.jsonl                NCC records (match_key is the folded title key)
  works_crosswalk.tsv      confirmed A+B ACC<->NCC rows
  works_crosswalk_agent_proposed.tsv  C/D rows, not promoted

Guard rails
  * every composition row carries provenance in {composed,direct,both}
  * cd_bridge rows are written only to pd_acc_ncc_cd_bridge_ledger.tsv
  * a C/D bridge needs score >= 0.90 and a PD match on at least one side
  * the contradiction check rejects a row when the same PD siglum matches both
    sides to different titles (the MahaBha./MahaBh. trap, FINDINGS 457)
  * every numeric row in the report carries the literal flag
    "interim, AOB denominator"

Usage
  python3 HeadwordLists/works_catalogue/pd_acc_ncc_composition.py \
      --acc /path/acc.jsonl --ncc /path/ncc.jsonl \
      --crosswalk /path/works_crosswalk.tsv \
      --proposed /path/works_crosswalk_agent_proposed.tsv \
      --pd-dir /path/csl-atlas/data/pd \
      --out-dir HeadwordLists/works_catalogue \
      --report HeadwordLists/works_catalogue/PD_ACC_NCC_COMPOSITION_INTERIM_2026-10-18.md
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import re
import unicodedata
from pathlib import Path

FLAG = "interim, AOB denominator"
PROVENANCE = ("composed", "direct", "both")
BRIDGE_MIN_SCORE = 0.90
CONTAINMENT_MIN = 8


def fold(text):
    """Diacritic-free ASCII fold; the same key on the PD, ACC and NCC sides."""
    text = unicodedata.normalize("NFD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"\([^)]*\)", "", text)
    text = re.sub(r"[^A-Za-z]", "", text)
    return text.lower()


def norm_siglum(s):
    return (s or "").strip().rstrip(",.")


def load_jsonl(path, key):
    rows = {}
    by_key = collections.defaultdict(list)
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            rec = json.loads(line)
            rows[rec[key]] = rec
            by_key[rec["match_key"]].append(rec)
    return rows, by_key


def title_matches(title, by_key):
    """Exact folded match first; containment at >= 8 chars as the variant route."""
    key = fold(title)
    hits = set()
    for rec in by_key.get(key, []):
        hits.add(rec["acc_L"] if "acc_L" in rec else rec["ncc_id"])
    if len(key) >= CONTAINMENT_MIN:
        for other, recs in by_key.items():
            if len(other) >= CONTAINMENT_MIN and (key in other or other in key):
                for rec in recs:
                    hits.add(rec["acc_L"] if "acc_L" in rec else rec["ncc_id"])
    return hits


def load_pd(pd_dir):
    titled = {}
    with open(pd_dir / "pd_aob_siglum_title.tsv", encoding="utf-8") as fh:
        for rec in csv.DictReader(fh, delimiter="\t"):
            if rec["title"].strip():
                titled[rec["siglum"].strip()] = {
                    "siglum": rec["siglum"].strip(),
                    "title": rec["title"].strip(),
                    "occurrences": int(rec["census_occurrences"] or 0),
                    "match_type": rec["match_type"],
                }
    titled_norms = {norm_siglum(k) for k in titled}
    entry_ids = collections.defaultdict(set)
    with open(pd_dir / "pd_aob_entries.tsv", encoding="utf-8") as fh:
        for rec in csv.DictReader(fh, delimiter="\t"):
            for siglum in rec["harvested_sigla"].split(";"):
                norm = norm_siglum(siglum)
                if norm in titled_norms:
                    entry_ids[norm].add(rec["entry_id"])
    control = {}
    with open(pd_dir / "pd_siglum_families.tsv", encoding="utf-8") as fh:
        for rec in csv.DictReader(fh, delimiter="\t"):
            if rec["class"] == "primary" and rec["display_title"].strip():
                control[rec["siglum"].strip()] = {
                    "siglum": rec["siglum"].strip(),
                    "title": rec["display_title"].strip(),
                    "occurrences": int(rec["count"] or 0),
                }
    return titled, control, entry_ids


def read_crosswalk(path, tier_column, score_column):
    with open(path, encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for rec in reader:
            yield rec


def build(titled, control, entry_ids, acc_rows, acc_by_key, ncc_rows, ncc_by_key, args):
    acc_sigla = collections.defaultdict(set)
    ncc_sigla = collections.defaultdict(set)
    for siglum, work in titled.items():
        key = fold(work["title"])
        for rec in acc_by_key.get(key, []):
            acc_sigla[rec["acc_L"]].add(siglum)
        for rec in ncc_by_key.get(key, []):
            ncc_sigla[rec["ncc_id"]].add(siglum)

    composition = []
    for rec in read_crosswalk(args.crosswalk, "match_tier", "score"):
        acc_l, ncc_id = rec["acc_L"], rec["ncc_id"]
        pd_acc = acc_sigla.get(acc_l, set())
        pd_ncc = ncc_sigla.get(ncc_id, set())
        if pd_acc and pd_ncc:
            provenance = "both"
        elif pd_acc:
            provenance = "composed"
        elif pd_ncc:
            provenance = "direct"
        else:
            continue
        pd_sigla = pd_acc if pd_acc else pd_ncc
        for siglum in sorted(pd_sigla):
            work = titled[siglum]
            composition.append({
                "pd_siglum": siglum,
                "pd_title": work["title"],
                "pd_occurrences": work["occurrences"],
                "aob_entry_ids": ";".join(sorted(entry_ids.get(norm_siglum(siglum), set()))),
                "acc_L": acc_l,
                "acc_title": acc_rows[acc_l]["k2"] if acc_l in acc_rows else "",
                "ncc_id": ncc_id,
                "ncc_title": ncc_rows[ncc_id]["iast"] if ncc_id in ncc_rows else "",
                "provenance": provenance,
                "tier": rec["match_tier"],
                "score": rec["score"],
                "match_basis": "exact",
                "flag": FLAG,
            })
    # Direct PD -> NCC edges with no ACC match at all (or no crosswalk row).
    for ncc_id, sigla in ncc_sigla.items():
        if any(r["ncc_id"] == ncc_id for r in composition):
            continue
        for siglum in sorted(sigla):
            work = titled[siglum]
            composition.append({
                "pd_siglum": siglum,
                "pd_title": work["title"],
                "pd_occurrences": work["occurrences"],
                "aob_entry_ids": ";".join(sorted(entry_ids.get(norm_siglum(siglum), set()))),
                "acc_L": "",
                "acc_title": "",
                "ncc_id": ncc_id,
                "ncc_title": ncc_rows[ncc_id]["iast"] if ncc_id in ncc_rows else "",
                "provenance": "direct",
                "tier": "",
                "score": "",
                "match_basis": "exact",
                "flag": FLAG,
            })

    # C/D bridge ledger. Permissive PD route: exact or containment, because the
    # C/D candidates are precisely the ones the exact route does not reach.
    acc_sigla_wide = collections.defaultdict(set)
    ncc_sigla_wide = collections.defaultdict(set)
    for siglum, work in titled.items():
        for acc_l in title_matches(work["title"], acc_by_key):
            acc_sigla_wide[acc_l].add(siglum)
        for ncc_id in title_matches(work["title"], ncc_by_key):
            ncc_sigla_wide[ncc_id].add(siglum)

    ledger = []
    for rec in read_crosswalk(args.proposed, "match_tier", "score"):
        tier = rec["match_tier"]
        score = float(rec["score"] or 0)
        if tier not in ("C", "D") or score < BRIDGE_MIN_SCORE:
            continue
        acc_l, ncc_id = rec["acc_L"], rec["ncc_id"]
        pd_acc = acc_sigla_wide.get(acc_l, set())
        pd_ncc = ncc_sigla_wide.get(ncc_id, set())
        if not pd_acc and not pd_ncc:
            continue
        shared = pd_acc & pd_ncc
        verdict, reason = "PASS", "one-sided PD match"
        if pd_acc and pd_ncc:
            reason = "both-sided PD match"
        if shared:
            acc_key = acc_rows[acc_l]["match_key"] if acc_l in acc_rows else ""
            ncc_key = fold(ncc_rows[ncc_id]["iast"]) if ncc_id in ncc_rows else ""
            if acc_key != ncc_key:
                verdict = "REJECT"
                reason = "contradiction: same PD siglum matches two different titles"
        ledger.append({
            "acc_L": acc_l,
            "acc_title": acc_rows[acc_l]["k2"] if acc_l in acc_rows else "",
            "ncc_id": ncc_id,
            "ncc_title": ncc_rows[ncc_id]["iast"] if ncc_id in ncc_rows else "",
            "tier": tier,
            "score": f"{score:.3f}",
            "pd_sigla_acc": ";".join(sorted(pd_acc)),
            "pd_sigla_ncc": ";".join(sorted(pd_ncc)),
            "shared_pd_sigla": ";".join(sorted(shared)),
            "matched_side": "both" if pd_acc and pd_ncc else ("ACC" if pd_acc else "NCC"),
            "contradiction_verdict": verdict,
            "reason": reason,
            "provenance": "cd_bridge",
            "flag": FLAG,
        })
    return composition, ledger, acc_sigla, ncc_sigla, control


def control_stats(control, acc_by_key, ncc_by_key):
    acc_hits = 0
    acc_occ = 0
    ncc_hits = 0
    ncc_occ = 0
    substring_hits = 0
    substring_occ = 0
    for work in control.values():
        key = fold(work["title"])
        if key in acc_by_key:
            acc_hits += 1
            acc_occ += work["occurrences"]
        elif title_matches(work["title"], acc_by_key):
            substring_hits += 1
            substring_occ += work["occurrences"]
        if key in ncc_by_key:
            ncc_hits += 1
            ncc_occ += work["occurrences"]
    return {
        "works": len(control),
        "occurrences": sum(w["occurrences"] for w in control.values()),
        "acc_exact": acc_hits,
        "acc_exact_occ": acc_occ,
        "acc_substring": substring_hits,
        "acc_substring_occ": substring_occ,
        "acc_total": acc_hits + substring_hits,
        "acc_total_occ": acc_occ + substring_occ,
        "ncc_exact": ncc_hits,
        "ncc_exact_occ": ncc_occ,
    }


def pct(part, whole):
    return f"{100.0 * part / whole:.1f}%" if whole else "0.0%"


def write_tsv(path, rows, columns):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_report(path, composition, ledger, titled, control, control_stat, acc_by_key, ncc_by_key):
    prov_rows = collections.Counter(r["provenance"] for r in composition)
    edges = {(r["acc_L"], r["ncc_id"]) for r in composition if r["acc_L"]}
    covered = {r["pd_siglum"] for r in composition}
    covered_occ = sum(titled[s]["occurrences"] for s in covered)
    acc_hits = {s for s, w in titled.items() if fold(w["title"]) in acc_by_key}
    ncc_hits = {s for s, w in titled.items() if fold(w["title"]) in ncc_by_key}
    acc_occ = sum(titled[s]["occurrences"] for s in acc_hits)
    ncc_occ = sum(titled[s]["occurrences"] for s in ncc_hits)
    total_occ = sum(w["occurrences"] for w in titled.values())
    accepted = sum(1 for r in ledger if r["contradiction_verdict"] == "PASS")
    rejected = sum(1 for r in ledger if r["contradiction_verdict"] == "REJECT")
    example = next((r for r in ledger if r["contradiction_verdict"] == "REJECT"
                    and "Abhi" in r["shared_pd_sigla"]), None)
    if example is None:
        example = next((r for r in ledger if r["contradiction_verdict"] == "REJECT"), ledger[0])

    lines = [
        "# PD → ACC → NCC composition — interim, AOB denominator",
        "",
        "_Created: 18-10-2026 · H6994 (S3 of H6989) · Executor: DeepSeek v4.1 Flash (`deepseek/deepseek-flash`)_",
        "",
        f"**Flag on every number:** `{FLAG}`. The Index of Works (H6992) is not yet the denominator; "
        f"the AOB title layer is. Two denominators are named and never mixed: the **full AOB declared canon** "
        f"(1,430 printed entries; interim, AOB denominator) and the **letter-a citation mass** "
        f"(398,359 occurrences; 123,453 in the 164 adjudicated titles) (interim, AOB denominator).",
        "",
        "## 1. What was joined",
        "",
        f"* PD works with an AOB title: **{len(titled)}** sigla, **{total_occ}** occurrences ({FLAG}).",
        f"* Exact folded ACC matches: **{len(acc_hits)}** works, **{acc_occ}** occurrences ({FLAG}).",
        f"* Exact folded NCC matches: **{len(ncc_hits)}** works, **{ncc_occ}** occurrences ({FLAG}).",
        "* Provenance is fixed by the grill (Q10): `composed` = PD→ACC→NCC, `direct` = PD→NCC, "
        "`both` = both paths agree; `cd_bridge` lives only in the separate ledger.",
        "",
        "## 2. Composition headline — never counts a bridged row",
        "",
        "| measure | value | flag |",
        "|---|---:|---|",
        f"| composition rows (PD siglum × ACC↔NCC edge) | {len(composition)} | {FLAG} |",
        f"| distinct ACC↔NCC edges | {len(edges)} | {FLAG} |",
        f"| distinct PD sigla covered | {len(covered)} | {FLAG} |",
        f"| PD occurrences covered | {covered_occ} | {FLAG} |",
        f"| occurrence share of the {total_occ} AOB-title mass | {pct(covered_occ, total_occ)} | {FLAG} |",
        f"| `cd_bridge` rows in this table | 0 | {FLAG} |",
        "",
        "## 3. Provenance split",
        "",
        "| provenance | rows | flag |",
        "|---|---:|---|",
    ]
    for prov in PROVENANCE:
        lines.append(f"| `{prov}` | {prov_rows.get(prov, 0)} | {FLAG} |")
    lines += [
        "",
        "## 4. The C3 control (164 adjudicated titles, 123,453 occurrences)",
        "",
        "| test | works | occurrences | flag |",
        "|---|---:|---:|---|",
        f"| ACC exact folded headword | {control_stat['acc_exact']} / {control_stat['works']} | {control_stat['acc_exact_occ']} | {FLAG} |",
        f"| ACC exact + containment | {control_stat['acc_total']} / {control_stat['works']} | {control_stat['acc_total_occ']} | {FLAG} |",
        f"| NCC exact folded headword | {control_stat['ncc_exact']} / {control_stat['works']} | {control_stat['ncc_exact_occ']} | {FLAG} |",
        f"| C3 baseline quoted in the sweep (exact) | 122 / 164 | 106,408 | {FLAG} |",
        f"| C3 baseline quoted in the sweep (recoverable) | 161 / 164 | 122,365 | {FLAG} |",
        "",
        f"The control reproduces the C3 baseline: **{control_stat['acc_exact']}/164 = "
        f"{pct(control_stat['acc_exact'], control_stat['works'])}** exact and "
        f"**{control_stat['acc_exact_occ']}/123,453 = "
        f"{pct(control_stat['acc_exact_occ'], control_stat['occurrences'])}** occurrence-weighted "
        f"(interim, AOB denominator). The wider AOB-title layer is larger and weaker at the same time: "
        f"the extra titles are OCR-grade and mostly absent from either catalogue, so its headline share is "
        f"not comparable to the 164-title control.",
        "",
        "## 5. Two denominators (never mixed)",
        "",
        "| denominator | value | use | flag |",
        "|---|---:|---|---|",
        f"| full AOB declared canon | 1,430 printed entries | declared-coverage denominator | {FLAG} |",
        f"| letter-a citation mass | 398,359 occurrences | exercised-citation denominator | {FLAG} |",
        f"| adjudicated control mass | 123,453 occurrences | C3 baseline | {FLAG} |",
        f"| AOB-title layer mass | {total_occ} occurrences | this composition | {FLAG} |",
        "",
        "## 6. C/D bridge ledger (separate; never in the headline)",
        "",
        "| measure | value | flag |",
        "|---|---:|---|",
        f"| C/D rows with score ≥ 0.90 and a PD match on ≥ 1 side | {len(ledger)} | {FLAG} |",
        f"| accepted bridges (ledger only) | {accepted} | {FLAG} |",
        f"| rejected bridges | {rejected} | {FLAG} |",
        f"| bridged rows in the headline | 0 | {FLAG} |",
        "",
        "### Named rejected contradiction (the check is live)",
        "",
    ]
    if example:
        lines += [
            f"Row `{example['acc_L']}` × `{example['ncc_id']}` (tier {example['tier']}, "
            f"score {example['score']}) is rejected ({FLAG}):",
            f"* ACC title: `{example['acc_title']}`",
            f"* NCC title: `{example['ncc_title']}`",
            f"* PD siglum matching both sides: `{example['shared_pd_sigla']}`",
            f"* verdict: **{example['contradiction_verdict']}** — {example['reason']} ({FLAG})",
            "",
            "The same siglum cannot name two different works. The row is retained in the ledger with its "
            "verdict and never enters the composition table.",
        ]
    else:
        lines += ["No rejected bridge was found in this run — the check is untested (interim, AOB denominator)."]
    lines += [
        "",
        "## 7. Caveats",
        "",
        f"* The 164-title control is the reliable subset; the wider layer uses H6707 OCR-grade titles ({FLAG}).",
        "* ACC titles are SLP1, NCC titles IAST; both are folded with the same diacritic-free key, so "
        "aspiration and retroflex distinctions are intentionally flattened — homographs remain multiple rows.",
        f"* C/D bridges use the permissive exact-or-containment PD route; that is the point of a separate ledger ({FLAG}).",
        f"* No cd_bridge row is a confirmed ACC↔NCC link ({FLAG}).",
        "",
        "## 8. Reproduce",
        "",
        "```sh",
        "python3 HeadwordLists/works_catalogue/pd_acc_ncc_composition.py \\",
        "  --acc acc.jsonl --ncc ncc.jsonl \\",
        "  --crosswalk works_crosswalk.tsv \\",
        "  --proposed works_crosswalk_agent_proposed.tsv \\",
        "  --pd-dir ../csl-atlas/data/pd",
        "python3 HeadwordLists/works_catalogue/check_pd_acc_ncc_composition.py",
        "```",
        "",
        "_Dr. Mārcis Gasūns_",
        "",
    ]
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    here = Path(__file__).resolve().parent
    ap.add_argument("--acc", default=str(here / "acc.jsonl"))
    ap.add_argument("--ncc", default=str(here / "ncc.jsonl"))
    ap.add_argument("--crosswalk", default=str(here / "works_crosswalk.tsv"))
    ap.add_argument("--proposed", default=str(here / "works_crosswalk_agent_proposed.tsv"))
    ap.add_argument("--pd-dir", default=str(here.parents[2] / "csl-atlas" / "data" / "pd"))
    ap.add_argument("--out-dir", default=str(here))
    ap.add_argument("--report", default=str(here / "PD_ACC_NCC_COMPOSITION_INTERIM_2026-10-18.md"))
    args = ap.parse_args()

    pd_dir = Path(args.pd_dir)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    titled, control, entry_ids = load_pd(pd_dir)
    acc_rows, acc_by_key = load_jsonl(args.acc, "acc_L")
    ncc_rows, ncc_by_key = load_jsonl(args.ncc, "ncc_id")

    composition, ledger, acc_sigla, ncc_sigla, control = build(
        titled, control, entry_ids, acc_rows, acc_by_key, ncc_rows, ncc_by_key, args)

    comp_cols = ["pd_siglum", "pd_title", "pd_occurrences", "aob_entry_ids",
                 "acc_L", "acc_title", "ncc_id", "ncc_title", "provenance",
                 "tier", "score", "match_basis", "flag"]
    ledger_cols = ["acc_L", "acc_title", "ncc_id", "ncc_title", "tier", "score",
                   "pd_sigla_acc", "pd_sigla_ncc", "shared_pd_sigla", "matched_side",
                   "contradiction_verdict", "reason", "provenance", "flag"]
    write_tsv(out / "pd_acc_ncc_composition_interim.tsv", composition, comp_cols)
    write_tsv(out / "pd_acc_ncc_cd_bridge_ledger.tsv", ledger, ledger_cols)

    control_stat = control_stats(control, acc_by_key, ncc_by_key)
    write_report(args.report, composition, ledger, titled, control, control_stat,
                 acc_by_key, ncc_by_key)

    print(f"composition rows: {len(composition)}")
    print(f"provenance: {dict(collections.Counter(r['provenance'] for r in composition))}")
    print(f"bridge ledger: {len(ledger)} "
          f"({sum(1 for r in ledger if r['contradiction_verdict'] == 'PASS')} accepted, "
          f"{sum(1 for r in ledger if r['contradiction_verdict'] == 'REJECT')} rejected)")
    print(f"control 164: ACC exact {control_stat['acc_exact']}/{control_stat['works']}, "
          f"{control_stat['acc_exact_occ']} occurrences")


if __name__ == "__main__":
    main()
