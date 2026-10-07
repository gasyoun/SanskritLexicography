#!/usr/bin/env python3
"""Render sandhi-bench leaderboard.html from results/*.json (H6063).

Derived-don't-store: the page is regenerated from the committed result
JSONs; hand-editing the HTML is overwritten on rebuild.

Usage:
    python sandhi-bench/build_leaderboard.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RES = HERE / "results"

GOLD_CEILING = {
    "system": "Gold ceiling (DCS Unsandhied lineage)",
    "type": "ceiling",
    "test_acc": 1.0, "dev_acc": None, "macro_test": None,
    "n_test": "—", "notes": "by construction — the bench answers ARE the "
                            "induced DCS gold splits (96.3% Gītā-gold "
                            "inducer coverage)",
    "date": "2026-10-06",
}


def load_rows() -> list[dict]:
    rows = [GOLD_CEILING]

    def acc(path: Path, key: str = "exact_acc"):
        return json.loads(path.read_text(encoding="utf-8"))[key]

    mfs_t = RES / "mfs_results_test.json"
    mfs_d = RES / "mfs_results_dev.json"
    if mfs_t.is_file():
        mfs = json.loads(mfs_t.read_text(encoding="utf-8"))
        rows.append({
            "system": "MFS (most-frequent split per surface, train-only)",
            "type": "baseline — deterministic",
            "test_acc": mfs["exact_acc"], "dev_acc": acc(mfs_d) if mfs_d.is_file() else None,
            "macro_test": mfs["macro_acc_by_category"],
            "n_test": mfs["n"],
            "notes": (f"surface-OOV rate on test {mfs['surface_oov_rate'] * 100:.1f}% "
                      "(identity fallback); the floor to beat"),
            "date": "2026-10-06",
        })
    for p in sorted(RES.glob("llm_*_results_test.json")):
        r = json.loads(p.read_text(encoding="utf-8"))
        rows.append({
            "system": r["system"], "type": "baseline — local LLM",
            "test_acc": r["exact_acc"],
            "dev_acc": None, "macro_test": r["macro_acc_by_category"],
            "n_test": f"{r['protocol']['sample']}-item seeded subsample",
            "notes": "seeded subsample (seed "
                     f"{r['protocol']['sample_seed']}), 5-shot from train, "
                     "temp 0 — reproducible reference, not a frontier entry",
            "date": "2026-10-06",
        })
    return rows


def fmt(v):
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v*100:.1f}"
    return str(v)


HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>sandhi-bench v2 — leaderboard</title>
<style>
  :root {{
    --bg: #faf9f6; --fg: #1f2328; --muted: #6e7781; --card: #ffffff;
    --accent: #7c3aed; --border: #e5e2da; --tag: #f3f0e8;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #14161a; --fg: #e6e4dd; --muted: #9aa0a6; --card: #1c1f24;
      --accent: #a78bfa; --border: #2c3037; --tag: #262a31;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font: 16px/1.6 -apple-system, "Segoe UI", Roboto,
         "Helvetica Neue", sans-serif; background: var(--bg);
         color: var(--fg); }}
  main {{ max-width: 980px; margin: 0 auto; padding: 40px 20px 64px; }}
  h1 {{ font-size: 1.7rem; margin: 0 0 4px; }}
  h1 .v {{ color: var(--accent); }}
  .sub {{ color: var(--muted); margin: 0 0 28px; font-size: .95rem; }}
  table {{ width: 100%; border-collapse: collapse; background: var(--card);
          border: 1px solid var(--border); border-radius: 10px;
          overflow: hidden; font-size: .93rem; }}
  th, td {{ text-align: left; padding: 10px 12px;
           border-bottom: 1px solid var(--border); vertical-align: top; }}
  th {{ background: var(--tag); font-weight: 600; white-space: nowrap; }}
  tr:last-child td {{ border-bottom: 0; }}
  td.num {{ font-variant-numeric: tabular-nums; white-space: nowrap; }}
  .type {{ color: var(--muted); font-size: .82rem; }}
  .notes {{ color: var(--muted); font-size: .85rem; }}
  .how {{ margin-top: 28px; padding: 16px 18px; background: var(--card);
         border: 1px solid var(--border); border-radius: 10px;
         font-size: .92rem; }}
  .how code {{ background: var(--tag); padding: 1px 5px; border-radius: 4px;
              font-size: .85em; }}
  a {{ color: var(--accent); }}
</style>
</head>
<body>
<main>
  <h1>sandhi-bench <span class="v">v2</span> — leaderboard</h1>
  <p class="sub">Public junction-recovery benchmark from DCS gold-splits
  (kosha sandhi programme lineage) · exact-match LEFT+RIGHT · text-disjoint
  splits · {n_items} items · built 2026-10-06 · H6063, ruling B4</p>
  <table>
    <thead><tr>
      <th>#</th><th>System</th><th>Type</th>
      <th>test exact acc %</th><th>test macro %</th><th>dev %</th>
      <th>n (test)</th><th>Notes</th><th>Date</th>
    </tr></thead>
    <tbody>
{rows}
    </tbody>
  </table>
  <div class="how">
    <strong>Scoring.</strong> A submission is a JSONL file of
    <code>{{"id": "sb-…", "pred": "LEFT+RIGHT"}}</code> over
    <code>sandhi-bench/data/test.jsonl</code> ({n_items:,} items), graded by
    <code>python sandhi-bench/evaluate.py --pred your.jsonl --split test</code>
    (NFC → casefold → whitespace-collapse; unanswered = wrong). Metrics:
    exact accuracy + macro accuracy over rule categories.
    <br><br>
    <strong>Submitting.</strong> Open a PR against
    <a href="https://github.com/gasyoun/SanskritLexicography">gasyoun/SanskritLexicography</a>
    adding <code>sandhi-bench/results/&lt;system&gt;_results_test.json</code> +
    the predictions file, then run
    <code>python sandhi-bench/build_leaderboard.py</code>. No test answers in
    prompts; dev is for model selection only. The corpus-level splitter
    bake-off numbers (vidyut-cheda F1 0.282 · DharmaMitra neural F1 0.795,
    kosha SANDHI_PROGRAMME.md) are NOT comparable rows — different metric —
    and are kept in the README as external context.
  </div>
</main>
</body>
</html>
"""


def main() -> int:
    rows = sorted(load_rows(), key=lambda r: -(r["test_acc"] or 0))
    trs = []
    for i, r in enumerate(rows, 1):
        trs.append(
            f'      <tr><td class="num">{i}</td>'
            f'<td>{r["system"]}</td>'
            f'<td class="type">{r["type"]}</td>'
            f'<td class="num"><strong>{fmt(r["test_acc"])}</strong></td>'
            f'<td class="num">{fmt(r["macro_test"])}</td>'
            f'<td class="num">{fmt(r["dev_acc"])}</td>'
            f'<td class="num">{fmt(r["n_test"])}</td>'
            f'<td class="notes">{r["notes"]}</td>'
            f'<td class="num">{r["date"]}</td></tr>')
    n_items = json.loads((HERE / "data" / "manifest.json").read_text(
        encoding="utf-8"))["splits"]["n_items"]
    html = HTML.format(rows="\n".join(trs), n_items=n_items["test"])
    out = HERE / "leaderboard.html"
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out} with {len(rows)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
