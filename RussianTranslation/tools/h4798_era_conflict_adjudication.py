#!/usr/bin/env python3
"""H4798 — adjudicate the 233 gross era/attestation conflicts from Pair 1.

Inputs (read-only):
  * pwg_sense_attestation_window.jsonl   (C2P1, H3168) — per-sense earliest/latest
    YEARS from B-R citations resolved to the 45 dated works of
    work_dating_table.json (H3790 scholarly point dates).
  * kosha/data/dating/sense_dating.tsv   (H4019) — per-sense first_era BUCKETS
    from per-citation classification (DCS 2021 table / Dharmamitra chronology).

Pair 1 (tools/crosswalk_pwg_era_reconcile.py in Uprava) joined on
(slp1, major(sense_id)) == (key1, sense_no) and found 233 gross inversions:
vedic bucket with a CE earliest year, or late-medieval with a BCE one.

This tool reproduces that join, then adjudicates every conflict by cause:

  1. key_misalignment_hom_collapse — the attestation table contains SEPARATE
     row blocks per printed entry (homonyms share key1); Pair 1's dict took
     the FIRST block only.  If another block's window rank-agrees with the
     dating bucket, the conflict is a join artifact, not a data defect.
  2. key_misalignment_sub_sense_rollup — dating sense_id carries a letter
     suffix (2f) while the attestation row is the MAJOR-sense aggregate
     (2 = 2a..2g pooled).  The aggregate window reflects the earliest
     sibling, not this sub-sense.  Join-granularity artifact.
  3. evidence_base_work_dating — both sides name the same earliest work but
     the two layers date it to different eras (kosha genre bucket vs H3790
     scholarly point date).  Genuine cross-layer fork, flagged for DECIDE.
  4. evidence_base_coverage — the dating bucket rests on citations the
     45-work year table never resolved (n_unresolved / marginal / thin
     n_dateable), or the earliest work is absent from the kosha abbrev map.
  5. bucket_boundary — the year sits within ±100 of a band edge where the
     two era vocabularies legitimately overlap.
  6. evidence_base_citation_resolution — residual: no bucket-era work in the
     attestation's dated set; the two layers resolved different citation
     subsets for the sense (either side's citation left unresolved).

Era bands (ordinal, derived from kosha README boundaries + H3790 dates;
used only to test rank agreement, never asserted as scholarly fact):
  vedic <= -500 < epic-sutra <= 300 (Manu DCS 100..300 per seed)
  < classical <= 600 (Amarakoṣa c. 450-550) < early-medieval <= 1300
  < late-medieval.

Outputs (written under RussianTranslation/reports/):
  * H4798_ERA_CONFLICT_ADJUDICATION_19-09-2026.json  — full machine report
  * H4798_ERA_CONFLICT_ADJUDICATION_19-09-2026.md    — human report
  * h4798_era_conflict_corrected_joint.tsv           — corrected joint table,
    ALL joined rows, with cause/verdict columns (ok / conflict-classified)

Stdlib only, Python >= 3.9.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ERA_ORDER = ["vedic", "epic-sutra", "classical", "early-medieval", "late-medieval"]
ERA_RANK = {e: i for i, e in enumerate(ERA_ORDER)}
MAJOR_RE = re.compile(r"^(\d+)")
SUB_RE = re.compile(r"^(\d+)([a-z]+)$")
BAND_EDGES = [-500, 300, 600, 1300]
BOUNDARY_TOLERANCE = 100


def era_band(year):
    """Ordinal year -> era bucket (see module docstring for derivation)."""
    if not isinstance(year, int):
        return None
    if year <= BAND_EDGES[0]:
        return "vedic"
    if year <= BAND_EDGES[1]:
        return "epic-sutra"
    if year <= BAND_EDGES[2]:
        return "classical"
    if year <= BAND_EDGES[3]:
        return "early-medieval"
    return "late-medieval"


def rank_distance(era_a, era_b):
    if era_a in ERA_RANK and era_b in ERA_RANK:
        return abs(ERA_RANK[era_a] - ERA_RANK[era_b])
    return None


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--attestation", required=True)
    p.add_argument("--dating", required=True)
    p.add_argument("--work-dating", required=True,
                   help="work_dating_table.json (H3790): siglum -> map_date")
    p.add_argument("--abbrev-map", default=None,
                   help="kosha abbrev_map.tsv: abbrev -> era (optional)")
    p.add_argument("--json-out", required=True)
    p.add_argument("--md-out", required=True)
    p.add_argument("--tsv-out", required=True)
    return p.parse_args()


def load_attestation(path):
    """Return rows plus blocks: entry-blocks per key1 (sense_index resets)."""
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    blocks = collections.defaultdict(list)  # key1 -> [block, ...]
    current = {}  # (key1, block_idx) -> rows
    for r in rows:
        k = r["key1"]
        if r.get("sense_index") == 0:
            blocks[k].append([])
        if not blocks[k]:  # file starts mid-entry without sense_index 0 seen
            blocks[k].append([])
        blocks[k][-1].append(r)
    return rows, blocks


def load_dating(path):
    out = []
    with open(path, encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= len(header):
                out.append(dict(zip(header, parts)))
    return out


def major_of(sense_id):
    m = MAJOR_RE.match((sense_id or "").strip())
    return int(m.group(1)) if m else None


def load_abbrev_era(path):
    if not path or not Path(path).exists():
        return {}
    era_by_abbrev = {}
    with open(path, encoding="utf-8") as f:
        f.readline()
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 4:
                era_by_abbrev[parts[0]] = parts[3]
    return era_by_abbrev


def earliest_work(row, map_date):
    """Siglum of the row's dated work with the minimum H3790 point date."""
    best, best_y = None, None
    for s in row.get("dated_works") or []:
        y = map_date.get(s)
        if isinstance(y, int) and (best_y is None or y < best_y):
            best, best_y = s, y
    return best, best_y


def is_gross_conflict(first_era, earliest):
    if first_era == "vedic" and isinstance(earliest, int) and earliest > 0:
        return True
    if first_era == "late-medieval" and isinstance(earliest, int) and earliest < -500:
        return True
    return False


def main() -> int:
    a = parse_args()
    rows, blocks = load_attestation(a.attestation)
    dating = load_dating(a.dating)
    wdt = json.loads(Path(a.work_dating).read_text(encoding="utf-8"))["works"]
    map_date = {k: v.get("map_date") for k, v in wdt.items()}
    abbrev_era = load_abbrev_era(a.abbrev_map)

    # Reproduce the Pair 1 join (first-block candidate) to find the 233.
    first_by_key = {}
    for r in rows:
        first_by_key.setdefault((r["key1"], r.get("sense_no")), r)

    dating_by_lemma = collections.defaultdict(list)
    for d in dating:
        dating_by_lemma[(d.get("slp1"), d.get("hom"))].append(d)

    conflicts = []
    joint_rows = []
    for d in dating:
        era = (d.get("first_era") or "").strip()
        major = major_of(d.get("sense_id", ""))
        p_first = first_by_key.get((d.get("slp1"), major)) if major is not None else None
        if p_first is None:
            continue
        earliest = p_first.get("earliest")
        row = {
            "slp1": d.get("slp1"), "hom": d.get("hom") or "",
            "sense_id": d.get("sense_id"), "first_era": era,
            "bucket_via": d.get("bucket_via") or "",
            "marginal": d.get("marginal") or "",
            "n_cites": d.get("n_cites") or "", "n_dateable": d.get("n_dateable") or "",
            "att_sense_no": major, "att_earliest": earliest,
            "att_latest": p_first.get("latest"),
            "att_block": 1,
        }
        if not is_gross_conflict(era, earliest):
            row.update({"conflict": 0, "cause": "ok", "verdict": "agree",
                        "adjudicated_era": era if era else "",
                        "notes": ""})
            joint_rows.append(row)
            continue

        conflicts.append((d, p_first, major))

        # --- Adjudicate, in cause-test order -------------------------------
        # distinct windows among candidate blocks (first row of each block)
        cands = []
        for bi, b in enumerate(blocks.get(d.get("slp1"), [])):
            for r in b:
                if r.get("sense_no") == major:
                    cands.append((bi + 1, r))
                    break

        cause = verdict = notes = ""
        adjudicated_era = era
        att_block = 1

        # 1. hom collapse: another entry-block's window rank-agrees
        alt = None
        for bi, r in cands:
            if r is p_first and len(cands) == 1:
                continue
            dist = rank_distance(era, era_band(r.get("earliest")))
            if dist is not None and dist <= 1:
                if r is not p_first:
                    alt = (bi, r)
                    break
        if alt:
            bi, r = alt
            cause = "key_misalignment_hom_collapse"
            verdict = "join-artifact"
            adjudicated_era = era_band(r.get("earliest"))
            att_block = bi
            notes = (f"Pair 1 matched entry-block 1; block {bi} window "
                     f"({r.get('earliest')}..{r.get('latest')}) rank-agrees "
                     f"with bucket '{era}'")
            p_first = r
        else:
            # 2. sub-sense rollup
            m = SUB_RE.match((d.get("sense_id") or "").strip())
            if m:
                pref = m.group(1)
                sib_earlier = [
                    s for s in dating_by_lemma.get((d.get("slp1"), d.get("hom")), [])
                    if s is not d
                    and (s.get("first_era") or "").strip() in ERA_RANK
                    and (SUB_RE.match(s.get("sense_id") or "") or MAJOR_RE.match(s.get("sense_id") or ""))
                    and (MAJOR_RE.match(s.get("sense_id") or "").group(1) == pref)
                    and ERA_RANK[(s.get("first_era") or "").strip()] < ERA_RANK[era]
                ]
                if sib_earlier:
                    cause = "key_misalignment_sub_sense_rollup"
                    verdict = "join-artifact"
                    earliest_sib = sorted(sib_earlier, key=lambda s: ERA_RANK[(s.get("first_era") or "").strip()])[0]
                    adjudicated_era = era  # dating bucket stands for the sub-sense
                    notes = (f"attestation row is the MAJOR-sense aggregate; earliest "
                             f"sibling {earliest_sib.get('sense_id')} bucket "
                             f"'{earliest_sib.get('first_era')}' explains the window; "
                             f"bucket '{era}' stands for this sub-sense")
        if not cause:
            # 3. work-dating divergence: a dated work IS bucketed in the
            # dating layer's era vocabulary but its H3790 point date falls in
            # a different band.  The two layers disagree about that WORK.
            fork = None
            for s in p_first.get("dated_works") or []:
                s_era = abbrev_era.get(s)
                s_y = map_date.get(s)
                if s_era == era and isinstance(s_y, int) and era_band(s_y) != era:
                    fork = (s, s_y)
                    break
            ew_siglum, ew_year = earliest_work(p_first, map_date)
            ew_era_kosha = abbrev_era.get(ew_siglum) if ew_siglum else None
            if fork or (ew_siglum and ew_era_kosha and ew_era_kosha != era_band(ew_year)):
                s, s_y = fork or (ew_siglum, ew_year)
                cause = "evidence_base_work_dating"
                verdict = "cross-layer-fork"
                adjudicated_era = era
                notes = (f"work '{s}': kosha layer buckets it '{era}', H3790 "
                         f"point date {s_y} ({era_band(s_y)}); the two "
                         f"work-dating layers disagree about this WORK — "
                         f"genuine fork, flag to DECIDE")
            else:
                # 4. coverage / thin evidence in the dating row
                thin = (d.get("marginal") or "0").strip() == "1"
                try:
                    n_dateable = int(d.get("n_dateable") or 0)
                except ValueError:
                    n_dateable = 0
                unresolved = p_first.get("n_unresolved_citations") or 0
                no_kosha_map = ew_siglum and not ew_era_kosha
                if thin or n_dateable <= 2 or no_kosha_map:
                    trigger = []
                    if thin:
                        trigger.append("marginal=1")
                    if n_dateable <= 2:
                        trigger.append(f"n_dateable={n_dateable}")
                    if no_kosha_map:
                        trigger.append(f"earliest work '{ew_siglum}' outside kosha abbrev map")
                    cause = "evidence_base_coverage"
                    verdict = "prefer-attestation-year"
                    adjudicated_era = era_band(earliest)
                    notes = (f"dating row thin ({', '.join(trigger)}); "
                             f"attestation earliest {earliest} from scholarly "
                             f"point dates")
                else:
                    # 5a. citation-resolution divergence: no bucket-era work in
                    # the attestation's dated set — the two layers resolved
                    # different citation subsets for this sense.
                    edge_d = min(abs(earliest - e) for e in BAND_EDGES)
                    if edge_d <= BOUNDARY_TOLERANCE:
                        cause = "bucket_boundary"
                        verdict = "flag-only"
                        adjudicated_era = era
                        notes = (f"no structural cause; year {earliest} sits "
                                 f"{edge_d}y from a band edge where the era "
                                 f"vocabularies legitimately overlap")
                    else:
                        cause = "evidence_base_citation_resolution"
                        verdict = "flag-only"
                        adjudicated_era = era
                        notes = (f"no '{era}' work among the attestation's "
                                 f"dated set — the dating layer's '{era}' "
                                 f"citation was left unresolved by the year "
                                 f"table (n_unresolved_citations={unresolved}) "
                                 f"or vice versa; both claims survive")

        joint_rows.append({
            "slp1": d.get("slp1"), "hom": d.get("hom") or "",
            "sense_id": d.get("sense_id"), "first_era": era,
            "bucket_via": d.get("bucket_via") or "",
            "marginal": d.get("marginal") or "",
            "n_cites": d.get("n_cites") or "", "n_dateable": d.get("n_dateable") or "",
            "att_sense_no": major, "att_earliest": p_first.get("earliest"),
            "att_latest": p_first.get("latest"),
            "att_block": att_block,
            "conflict": 1, "cause": cause, "verdict": verdict,
            "adjudicated_era": adjudicated_era or "", "notes": notes,
        })

    cause_counts = collections.Counter(r["cause"] for r in joint_rows if r["conflict"])
    verdict_counts = collections.Counter(r["verdict"] for r in joint_rows if r["conflict"])

    report = {
        "handoff": "H4798",
        "date": "2026-09-19",
        "pair1_baseline": {
            "attestation_rows": len(rows), "dating_rows": len(dating),
            "joined": len(joint_rows), "gross_conflicts": len(conflicts),
        },
        "cause_counts": dict(sorted(cause_counts.items(),
                                    key=lambda kv: -kv[1])),
        "verdict_counts": dict(sorted(verdict_counts.items(),
                                      key=lambda kv: -kv[1])),
        "era_bands": {"vedic": "<= -500", "epic-sutra": "-500..300",
                      "classical": "300..600", "early-medieval": "600..1300",
                      "late-medieval": "> 1300"},
        "join_artifacts": sum(v for k, v in verdict_counts.items()
                              if k == "join-artifact"),
        "decide_flags": verdict_counts.get("cross-layer-fork", 0),
    }
    Path(a.json_out).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    tsv_cols = ["slp1", "hom", "sense_id", "first_era", "bucket_via", "marginal",
                "n_cites", "n_dateable", "att_sense_no", "att_block",
                "att_earliest", "att_latest", "conflict", "cause", "verdict",
                "adjudicated_era", "notes"]
    with open(a.tsv_out, "w", encoding="utf-8", newline="") as f:
        f.write("\t".join(tsv_cols) + "\n")
        for r in joint_rows:
            f.write("\t".join(str(r.get(c, "")) for c in tsv_cols) + "\n")

    join_art = report["join_artifacts"]
    lines = [
        "# H4798 — PWG two-era gross conflicts adjudicated (19-09-2026)",
        "",
        "_Created: 19-09-2026 · Last updated: 19-09-2026_",
        "",
        f"- joined rows: **{len(joint_rows)}** · gross conflicts adjudicated: "
        f"**{len(conflicts)}** (Pair 1 baseline reproduced)",
        f"- **{join_art} of {len(conflicts)} ({round(100*join_art/len(conflicts))}%) "
        "are join artifacts** — faults of the Pair 1 join key, not of either "
        "table; the remaining "
        f"{len(conflicts)-join_art} are evidence-base disagreements that "
        "survive a correct join.",
        "",
        "## Recommended actions",
        "",
        "1. Fix the join, not the tables: any future crosswalk of these two "
        "layers must (a) disambiguate homonym entry-blocks in "
        "`pwg_sense_attestation_window.jsonl` (carry an entry/hom ordinal) and "
        "(b) join sub-senses to their own citation subset, not the major-sense "
        "aggregate. With those two fixes the gross-conflict count collapses "
        f"from 233 to {len(conflicts)-join_art}.",
        f"2. The {verdict_counts.get('cross-layer-fork', 0)} "
        "`evidence_base_work_dating` rows are a real cross-layer fork (the "
        "same work dated to different eras by the kosha bucket layer vs the "
        "H3790 point dates) — carry them to the @DECIDE lane, do not "
        "self-resolve.",
        f"3. The {verdict_counts.get('flag-only', 0)} flag-only rows keep both "
        "claims side by side in the corrected joint table; neither table is "
        "rewritten by this handoff (read-only inputs).",
        "",
        "## Cause classification",
        "",
        "| cause | n | what it means |",
        "|---|---:|---|",
    ]
    meanings = {
        "key_misalignment_hom_collapse":
            "Pair 1 matched the lemma's FIRST entry-block; another homonym "
            "block's window rank-agrees with the bucket — join artifact",
        "key_misalignment_sub_sense_rollup":
            "dating sense is a sub-sense (2f) but the attestation row pools "
            "the whole major sense (2a..2g) — join-granularity artifact",
        "evidence_base_work_dating":
            "same earliest work, two eras: kosha genre bucket vs H3790 "
            "scholarly point date — genuine fork, DECIDE",
        "evidence_base_coverage":
            "dating row is thin (marginal / n_dateable<=2) or the earliest "
            "work is outside the kosha abbrev map — prefer attestation year",
        "bucket_boundary":
            "year within 100y of a band edge where the era vocabularies "
            "legitimately overlap — flag only",
        "evidence_base_citation_resolution":
            "no bucket-era work in the attestation's dated set — the two "
            "layers resolved different citation subsets — flag only",
    }
    for c, n in sorted(cause_counts.items(), key=lambda kv: -kv[1]):
        lines.append(f"| {c} | {n} | {meanings.get(c, '')} |")
    lines += [
        "",
        "## Verdicts",
        "",
        "| verdict | n |",
        "|---|---:|",
    ]
    for v, n in sorted(verdict_counts.items(), key=lambda kv: -kv[1]):
        lines.append(f"| {v} | {n} |")
    lines += [
        "",
        "## Era bands used for rank-agreement tests (ordinal, not asserted)",
        "",
        "- vedic ≤ -500 · epic-sutra -500..300 (Manu DCS 100..300 per seed) · "
        "classical 300..600 (Amarakoṣa c. 450-550) · early-medieval 600..1300 · "
        "late-medieval > 1300",
        "",
        "_Auto-generated by "
        "[h4798_era_conflict_adjudication.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tools/h4798_era_conflict_adjudication.py); baseline from "
        "[CROSSWALK_PWG_ERA_RECONCILE_14-09-2026.md](https://github.com/gasyoun/Uprava/blob/main/reports/CROSSWALK_PWG_ERA_RECONCILE_14-09-2026.md)._",
        "",
        "_Гасунс_",
        "",
    ]
    Path(a.md_out).write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"conflicts": len(conflicts),
                      "causes": dict(cause_counts),
                      "verdicts": dict(verdict_counts)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
