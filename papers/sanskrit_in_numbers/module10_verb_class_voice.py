#!/usr/bin/env python3
"""Module 10 - verb classes + voice (Sanskrit-in-Numbers Wave 1, H813).

Duden's *Sprache in Zahlen* reports German verb-class shares (weak 76.7% /
strong 17.2%) and the haben/sein auxiliary split. Sanskrit's direct analogs:
the 10 gana (verb class) distribution, and the parasmaipada / atmanepada /
ubhayapada (P/A/U, "for others" / "for oneself" / both) voice split -- a
cleaner structural analog of haben/sein than German's own irregular-verb list.

Source (WhitneyRoots, a sibling repo -- reused per org convention, not
re-derived from raw PWG prose):
  - GANA: Whitney_roots_class-PP.txt -- 938 roots digitized from Whitney's
    "Roots, Verb-forms and Primary Derivatives" (1885), the standard
    philological reference (Whitney's own classification, cross-checked
    against the corpus elsewhere in that repo at 85.5% agreement -- cited,
    not re-measured, here).
  - PADA (voice): src/paradigms.json -- vidyut-prakriya-generated paradigms
    for 454/938 roots (the subset where a Pāṇinian-gaṇa-consistent, either
    corpus- or Dhātupātha-attested paradigm could be generated/corroborated).
    Multi-pada roots (attested with more than one pada across paradigm
    entries) are classified ubhayapada.

Honesty note: gana coverage is 938 roots (full Whitney inventory, ~14% with
no attested/classifiable class, shown as "unclassified"); voice coverage is
the smaller 454-root corroborated subset -- reported as its own denominator,
not silently extrapolated to all 938.
"""
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parents[2]
GITHUB_ROOT = REPO_ROOT.parent
WHITNEY_ROOT = GITHUB_ROOT / "WhitneyRoots"
CLASS_PP_PATH = WHITNEY_ROOT / "Whitney_roots_class-PP.txt"
PARADIGMS_PATH = WHITNEY_ROOT / "src" / "paradigms.json"

LINE_RE = re.compile(
    r"^\s*\d+\.\s+(?:\d\s+)?√?\s*(?P<root>\S+)\s+(?P<classes>\S+)\s+"
)


def parse_gana():
    """Return dict root -> set of gana roman numerals (or empty set if '-')."""
    roots = {}
    with open(CLASS_PP_PATH, encoding="utf-8") as f:
        for line in f:
            m = LINE_RE.match(line)
            if not m:
                continue
            root = m.group("root")
            classes_raw = m.group("classes")
            if classes_raw in ("—", "-", "—"):
                classes = set()
            else:
                classes = set(c for c in classes_raw.split("/") if c)
            # multiple homonyms of the same root spelling: keep the union of
            # classes under one key (root spelling is what Module 10 counts,
            # matching how the dictionary family cites class per root-spelling)
            roots.setdefault(root, set()).update(classes)
    return roots


def parse_pada():
    """Return dict root -> set of padas attested across generated paradigms."""
    with open(PARADIGMS_PATH, encoding="utf-8") as f:
        data = json.load(f)
    roots = defaultdict(set)
    meta = data["_meta"]
    for _key, entry in data["roots"].items():
        root = entry["root"]
        for p in entry.get("paradigms", []):
            pada = p.get("pada")
            if not pada:
                continue
            # vidyut labels ubhayapada roots with a single combined string
            # "parasmaipada+atmanepada" rather than two separate paradigm
            # entries -- split it so it lands in both/ubhayapada correctly.
            for part in pada.split("+"):
                if part:
                    roots[root].add(part)
    return dict(roots), meta


GANA_ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]


def main():
    gana_by_root = parse_gana()
    n_roots_total = len(gana_by_root)
    n_unclassified = sum(1 for v in gana_by_root.values() if not v)
    n_classified = n_roots_total - n_unclassified

    # gana distribution: a root with multiple classes contributes to each
    # (matching Duden's own practice of not double-counting whole-word tokens,
    # but here a multi-class root genuinely belongs to more than one gana --
    # report both a "primary gana" (first-listed) share and a "multi-class
    # membership" share, so neither reading is silently hidden)
    primary_gana = Counter()
    membership_gana = Counter()
    n_multi_class = 0
    for root, classes in gana_by_root.items():
        if not classes:
            continue
        ordered = [g for g in GANA_ROMAN if g in classes]
        if ordered:
            primary_gana[ordered[0]] += 1
        if len(classes) > 1:
            n_multi_class += 1
        for g in classes:
            membership_gana[g] += 1

    primary_gana_pct = {
        g: {"n": primary_gana.get(g, 0), "pct": round(100 * primary_gana.get(g, 0) / n_classified, 2)}
        for g in GANA_ROMAN
    }
    membership_gana_pct = {
        g: {"n": membership_gana.get(g, 0), "pct": round(100 * membership_gana.get(g, 0) / n_classified, 2)}
        for g in GANA_ROMAN
    }

    pada_by_root, paradigms_meta = parse_pada()
    n_pada_roots = len(pada_by_root)
    pada_class = Counter()
    for root, padas in pada_by_root.items():
        if len(padas) > 1:
            pada_class["ubhayapada"] += 1
        elif padas == {"parasmaipada"}:
            pada_class["parasmaipada"] += 1
        elif padas == {"atmanepada"}:
            pada_class["atmanepada"] += 1
        else:
            pada_class["other/" + ",".join(sorted(padas))] += 1

    pada_pct = {
        k: {"n": v, "pct": round(100 * v / n_pada_roots, 2)}
        for k, v in pada_class.items()
    }

    out = {
        "module": 10,
        "title": "verb classes (gana) + voice (parasmaipada/atmanepada/ubhayapada)",
        "trust_block": {
            "source": "WhitneyRoots Whitney_roots_class-PP.txt (938 roots, Whitney 1885 "
                       "digitized classification) for gana; WhitneyRoots src/paradigms.json "
                       "(vidyut-prakriya 0.4.0 generated, 454/938 roots corroborated) for pada",
            "n": {
                "roots_total_whitney": n_roots_total,
                "roots_gana_classified": n_classified,
                "roots_gana_unclassified": n_unclassified,
                "roots_multi_class": n_multi_class,
                "roots_pada_corroborated": n_pada_roots,
            },
            "date": str(date.today()),
            "model": "Sonnet 5 (claude-sonnet-5)",
        },
        "gana_primary_pct": primary_gana_pct,
        "gana_membership_pct": membership_gana_pct,
        "pada_pct": pada_pct,
        "note": "gana 'primary' = first-listed class per root (the dictionary/grammar's "
                "own citation order); 'membership' = every class a multi-class root "
                "belongs to, so membership percentages sum to >100%. Voice (pada) is "
                "reported only over the 454-root vidyut-corroborated subset, NOT "
                "extrapolated to all 938 -- the smaller, cleaner denominator is stated "
                "explicitly rather than silently assumed representative of the full "
                "root inventory. Cross-reference: WhitneyRoots' own corpus-vs-Whitney "
                "gana agreement measurement (857 DCS-attested roots, 85.5%) is cited, "
                "not re-run, here (see corpus_verdict_summary.txt in that repo).",
    }

    out_path = Path(__file__).parent / "module10_verb_class_voice.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"roots total: {n_roots_total}, classified: {n_classified}, unclassified: {n_unclassified}")
    print(f"primary gana pct: {primary_gana_pct}")
    print(f"pada roots: {n_pada_roots}, pada pct: {pada_pct}")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
