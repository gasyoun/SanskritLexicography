"""ACC x NCC P2 -- ingest /review-sheet votes, emit the confirmed crosswalk.

Per ROADMAP_ACC_NCC.md P2: reads crosswalk_candidates.jsonl.gz (P1 output,
read-only) plus a decisions.json exported by the review sheet
(review/build_p2_sheet.py) and produces:

  - works_crosswalk.tsv[.gz]  one row per confirmed ACC<->NCC link:
      Tier A/B rows are auto-accepted (P1 already partitions them as
      unambiguous); Tier C/D rows are included only if their id (acc_L +
      "__" + ncc_id) was voted "approve" in decisions.json.
  - P2_COUNTS.md              rows voted, accept/reject/defer counts per
      tier, and (only if the vote set is a documented sample, not this
      run's full-49,019-row pass) an extrapolated estimate for the
      un-sampled remainder.

Rejected rows are NOT deleted -- they are written to
works_crosswalk_rejected.tsv as confirmed non-matches (provenance, so a
future pass doesn't re-propose the same pair). Deferred and never-voted
rows are omitted from both outputs and remain pending a future P2 pass.

Usage:
    python HeadwordLists/works_catalogue/apply_p2_decisions.py <decisions.json>
"""
import sys
import os
import json
import gzip

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
CANDIDATES_PATH = os.path.join(HERE, "crosswalk_candidates.jsonl.gz")
OUT_TSV = os.path.join(HERE, "works_crosswalk.tsv")
OUT_REJECTED_TSV = os.path.join(HERE, "works_crosswalk_rejected.tsv")
COUNTS_PATH = os.path.join(HERE, "P2_COUNTS.md")

TSV_COLS = ["acc_L", "ncc_id", "match_tier", "score", "acc_match_key",
            "ncc_match_key", "provenance"]


def load_candidates():
    rows = []
    with gzip.open(CANDIDATES_PATH, 'rt', encoding='utf-8') as f:
        for line in f:
            rows.append(json.loads(line))
    return rows


def load_decisions(path):
    with open(path, encoding='utf-8') as f:
        payload = json.load(f)
    by_id = {}
    for item in payload.get("items", []):
        by_id[item["id"]] = item.get("decision")
    return by_id, payload


def tsv_row(r, tier, provenance):
    return "\t".join([
        r["acc_L"], r["ncc_id"], tier, str(r["score"]),
        r["acc_match_key"], r["ncc_match_key"], provenance,
    ])


def main():
    if len(sys.argv) != 2:
        print("Usage: python apply_p2_decisions.py <decisions.json>", file=sys.stderr)
        sys.exit(1)
    decisions_path = sys.argv[1]

    candidates = load_candidates()
    decisions, payload = load_decisions(decisions_path)

    accepted = []
    rejected = []
    tier_counts = {"A": 0, "B": 0, "C": {"approve": 0, "reject": 0, "defer": 0, "unvoted": 0},
                   "D": {"approve": 0, "reject": 0, "defer": 0, "unvoted": 0}}

    for r in candidates:
        tier = r["tier"]
        if tier in ("A", "B"):
            accepted.append(tsv_row(r, tier, "auto"))
            tier_counts[tier] += 1
            continue
        rid = f"{r['acc_L']}__{r['ncc_id']}"
        dec = decisions.get(rid)
        key = dec if dec in ("approve", "reject", "defer") else "unvoted"
        tier_counts[tier][key] += 1
        if dec == "approve":
            accepted.append(tsv_row(r, tier, "adjudicated"))
        elif dec == "reject":
            rejected.append(tsv_row(r, tier, "adjudicated"))

    with open(OUT_TSV, 'w', encoding='utf-8') as f:
        f.write("\t".join(TSV_COLS) + "\n")
        for row in accepted:
            f.write(row + "\n")

    with open(OUT_REJECTED_TSV, 'w', encoding='utf-8') as f:
        f.write("\t".join(TSV_COLS) + "\n")
        for row in rejected:
            f.write(row + "\n")

    c_total = sum(tier_counts["C"].values())
    d_total = sum(tier_counts["D"].values())
    lines = [
        "# ACC x NCC P2 -- adjudication counts",
        "",
        f"Sheet: `sanskritlexicography-acc_ncc_p2_c_d_review.html` · decisions file: `{os.path.basename(decisions_path)}`"
        f" · decided={payload.get('decided', 'n/a')} · exported={payload.get('generated', 'n/a')}",
        "",
        "| Tier | Rows | Approved | Rejected | Deferred | Unvoted |",
        "|---|---:|---:|---:|---:|---:|",
        f"| A (auto) | {tier_counts['A']} | {tier_counts['A']} | 0 | 0 | 0 |",
        f"| B (auto) | {tier_counts['B']} | {tier_counts['B']} | 0 | 0 | 0 |",
        f"| C | {c_total} | {tier_counts['C']['approve']} | {tier_counts['C']['reject']} | {tier_counts['C']['defer']} | {tier_counts['C']['unvoted']} |",
        f"| D | {d_total} | {tier_counts['D']['approve']} | {tier_counts['D']['reject']} | {tier_counts['D']['defer']} | {tier_counts['D']['unvoted']} |",
        "",
        f"**Confirmed crosswalk rows (works_crosswalk.tsv):** {len(accepted)} "
        f"({tier_counts['A']} Tier A + {tier_counts['B']} Tier B auto + "
        f"{tier_counts['C']['approve']} Tier C + {tier_counts['D']['approve']} Tier D adjudicated).",
        "",
        f"**Confirmed non-matches logged (works_crosswalk_rejected.tsv):** {len(rejected)}.",
        "",
        "No sampling was used for this P2 pass (MG ruling 09-07-2026): every Tier C/D row in "
        "crosswalk_candidates.jsonl.gz was included in the review sheet, so unvoted counts above "
        "reflect rows not yet reached in the voting pass, not an intentional sample -- a future "
        "P2 continuation pass can pick up where this decisions.json left off (unvoted rows carry "
        "`decision: null` and are still present in the sheet/candidate set).",
        "",
    ]
    with open(COUNTS_PATH, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))

    print(f"Wrote {OUT_TSV} ({len(accepted)} rows)")
    print(f"Wrote {OUT_REJECTED_TSV} ({len(rejected)} rows)")
    print(f"Wrote {COUNTS_PATH}")


if __name__ == "__main__":
    main()
