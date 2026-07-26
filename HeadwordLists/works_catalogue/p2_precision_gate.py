"""ACC x NCC P2 -- measure the adjudicator, then gate promotion per stratum.

H1657 deliverables 3-5. Two modes:

  FEASIBILITY (no votes yet)
      python p2_precision_gate.py
      Prints, per stratum, the Wilson 95% LOWER bound each possible sample
      outcome would produce and how many crosswalk rows ride on it -- the
      table a human needs to pick the promotion bar with its consequence
      stated in rows. Also emits an all-deferred decisions.json so nothing is
      promoted while every stratum is still unmeasured.

  GATE (votes returned)
      python p2_precision_gate.py <spotcheck_decisions.json> --bar 0.90
      Joins the human votes against p2_spotcheck_manifest.json, measures
      per-stratum agreement, publishes the Wilson lower bound, and emits a
      gated decisions.json: strata clearing the bar keep their agent verdict,
      strata below it are demoted to `defer` and stay agent-proposed.

The bar is NOT hardcoded and NOT defaulted into promotion: `--bar` must be
passed explicitly to gate, because how many of 49,019 rows enter a citable
dataset is a scholarly standard, not a statistic (H1657 deliverable 5, the
single human gate in the handoff).

Why a lower bound and not a point estimate: a stratum measured 3/3 = 1.000 has
a Wilson lower bound near 0.44 and has proved nothing. The bound is what makes
a small sample honest about its own thinness (the discipline H1470 ratified
for the handoff-lifecycle gate).

Usage:
    python HeadwordLists/works_catalogue/p2_precision_gate.py
    python HeadwordLists/works_catalogue/p2_precision_gate.py votes.json --bar 0.90
"""
import sys
import os
import json
import math
import gzip
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
VERDICTS = os.path.join(HERE, "p2_agent_verdicts.jsonl.gz")
MANIFEST = os.path.join(HERE, "p2_spotcheck_manifest.json")
OUT_DECISIONS = os.path.join(HERE, "p2_gated_decisions.json")
OUT_REPORT = os.path.join(HERE, "P2_PRECISION.md")

Z = 1.959963985  # two-sided 95%


def wilson_lower(k, n):
    """Wilson score interval, lower bound, 95%."""
    if n == 0:
        return 0.0
    p = k / n
    denom = 1 + Z * Z / n
    centre = (p + Z * Z / (2 * n)) / denom
    half = (Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))) / denom
    return max(0.0, centre - half)


def load_strata():
    pop = defaultdict(int)
    decision_of = {}
    rule_of = {}
    ids_by_stratum = defaultdict(list)
    with gzip.open(VERDICTS, 'rt', encoding='utf-8') as f:
        for line in f:
            v = json.loads(line)
            pop[v['stratum']] += 1
            decision_of[v['stratum']] = v['decision']
            rule_of[v['stratum']] = v['rule']
            ids_by_stratum[v['stratum']].append(v['id'])
    return pop, decision_of, rule_of, ids_by_stratum


def emit_decisions(ids_by_stratum, decision_of, passed, bar, measured):
    """One decisions.json for apply_p2_decisions.py.

    A stratum that cleared the bar keeps its agent verdict. Everything else is
    `defer` with an `agent-proposed:` note -- apply_p2_decisions.py routes those
    to works_crosswalk_agent_proposed.tsv instead of the citable crosswalk.
    """
    items = []
    for stratum, ids in ids_by_stratum.items():
        dec = decision_of[stratum]
        ok = passed.get(stratum, False)
        for rid in ids:
            if ok:
                items.append({'id': rid, 'decision': dec,
                              'note': f'agent-gated:{stratum}'})
            else:
                items.append({'id': rid, 'decision': 'defer',
                              'note': f'agent-proposed:{dec}:{stratum}'})
    payload = {
        'sheet_id': 'sanskritlexicography-acc_ncc_p2_c_d_review',
        'generated': f'H1657 gate (bar={bar if bar is not None else "unset"})',
        'decided': len(items),
        'adjudicator': 'adjudicate_p2.py (Opus 5 1M `claude-opus-5[1m]`)',
        'gated': True,
        'bar': bar,
        'measured': measured,
        'items': items,
    }
    with open(OUT_DECISIONS, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    return len(items)


def feasibility(pop, decision_of, rule_of, ids_by_stratum):
    with open(MANIFEST, encoding='utf-8') as f:
        plan = {p['stratum']: p for p in json.load(f)['plan']}

    lines = []
    lines.append("| stratum | verdict | rows | sample n | LB if n/n | LB if n-1 | LB if n-2 |")
    lines.append("|---|---|---:|---:|---:|---:|---:|")
    rows_at_stake = defaultdict(int)
    print(f"{'stratum':52s} {'verdict':8s} {'rows':>7s} {'n':>4s} "
          f"{'LB n/n':>7s} {'LB -1':>7s} {'LB -2':>7s}")
    for stratum in sorted(pop):
        n = plan.get(stratum, {}).get('n', 0)
        lb0 = wilson_lower(n, n)
        lb1 = wilson_lower(max(n - 1, 0), n)
        lb2 = wilson_lower(max(n - 2, 0), n)
        dec = decision_of[stratum]
        rows_at_stake[dec] += pop[stratum]
        print(f"{stratum:52s} {dec:8s} {pop[stratum]:7,} {n:4d} "
              f"{lb0:7.3f} {lb1:7.3f} {lb2:7.3f}")
        lines.append(f"| `{stratum}` | {dec} | {pop[stratum]:,} | {n} | "
                     f"{lb0:.3f} | {lb1:.3f} | {lb2:.3f} |")

    print("\nconsequence of each candidate bar, IF every stratum comes back perfect:")
    lines.append("")
    lines.append("**Consequence of each candidate bar, if every stratum votes perfect "
                 "(the best case any sample of this size can produce):**")
    lines.append("")
    lines.append("| bar | approve rows promoted | approve rows held | reject rows published |")
    lines.append("|---:|---:|---:|---:|")
    for bar in (0.80, 0.85, 0.90, 0.95, 0.98):
        promoted = held = rejected = 0
        for stratum in pop:
            n = plan.get(stratum, {}).get('n', 0)
            lb = wilson_lower(n, n)
            if decision_of[stratum] == 'approve':
                if lb >= bar:
                    promoted += pop[stratum]
                else:
                    held += pop[stratum]
            else:
                if lb >= bar:
                    rejected += pop[stratum]
        print(f"  bar {bar:.2f}: promote {promoted:6,} · hold {held:6,} · "
              f"publish-as-rejected {rejected:6,}")
        lines.append(f"| {bar:.2f} | {promoted:,} | {held:,} | {rejected:,} |")

    n_items = emit_decisions(ids_by_stratum, decision_of, {}, None, False)
    print(f"\nno stratum is measured yet -> all {n_items:,} rows emitted as "
          f"`defer` (agent-proposed) -> {OUT_DECISIONS}")
    return lines


def gate(votes_path, bar, pop, decision_of, rule_of, ids_by_stratum):
    with open(MANIFEST, encoding='utf-8') as f:
        manifest = json.load(f)
    agent = manifest['agent_verdicts']
    with open(votes_path, encoding='utf-8') as f:
        payload = json.load(f)
    human = {it['id']: it.get('decision') for it in payload.get('items', [])
             if it.get('decision')}

    agree = defaultdict(int)
    seen = defaultdict(int)
    unvoted = 0
    for rid, a in agent.items():
        h = human.get(rid)
        if h is None:
            unvoted += 1
            continue
        seen[a['stratum']] += 1
        # A human `defer` is not agreement -- it is the human declining to
        # confirm, which for a precision measurement counts against the agent.
        if h == a['decision']:
            agree[a['stratum']] += 1

    lines = []
    lines.append(f"Bar: **{bar:.2f}** Wilson 95% lower bound. "
                 f"{len(human):,} of {len(agent):,} sampled cards voted"
                 + (f"; {unvoted:,} unvoted (counted as no evidence, "
                    f"not as agreement)." if unvoted else "."))
    lines.append("")
    lines.append("| stratum | verdict | rows | n voted | agreed | precision | Wilson 95% LB | gate |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---|")
    passed = {}
    promoted = held = published_rej = held_rej = 0
    print(f"{'stratum':52s} {'rows':>7s} {'n':>4s} {'ok':>4s} {'LB':>7s}  gate")
    for stratum in sorted(pop):
        n, k = seen[stratum], agree[stratum]
        lb = wilson_lower(k, n)
        ok = n > 0 and lb >= bar
        passed[stratum] = ok
        dec = decision_of[stratum]
        if dec == 'approve':
            promoted += pop[stratum] if ok else 0
            held += 0 if ok else pop[stratum]
        else:
            published_rej += pop[stratum] if ok else 0
            held_rej += 0 if ok else pop[stratum]
        verdictmark = 'PASS' if ok else ('unmeasured' if n == 0 else 'HELD')
        print(f"{stratum:52s} {pop[stratum]:7,} {n:4d} {k:4d} {lb:7.3f}  {verdictmark}")
        prec = f"{k / n:.3f}" if n else "—"
        lines.append(f"| `{stratum}` | {dec} | {pop[stratum]:,} | {n} | {k} | "
                     f"{prec} | {lb:.3f} | {verdictmark} |")

    lines.append("")
    lines.append(f"**Promoted into `works_crosswalk.tsv`:** {promoted:,} rows. "
                 f"**Held as agent-proposed (not promoted):** {held:,} rows. "
                 f"**Published as confirmed non-matches:** {published_rej:,}. "
                 f"**Rejections held back:** {held_rej:,}.")
    print(f"\npromote {promoted:,} · hold {held:,} · publish-rejected "
          f"{published_rej:,} · hold-rejected {held_rej:,}")
    emit_decisions(ids_by_stratum, decision_of, passed, bar, True)
    print(f"gated decisions -> {OUT_DECISIONS}")
    return lines


def main():
    args = [a for a in sys.argv[1:]]
    bar = None
    if '--bar' in args:
        i = args.index('--bar')
        bar = float(args[i + 1])
        del args[i:i + 2]
    votes = args[0] if args else None

    pop, decision_of, rule_of, ids_by_stratum = load_strata()
    if votes:
        if bar is None:
            print("refusing to gate without an explicit --bar: the promotion "
                  "threshold is a human ruling, not a default (H1657 D5)",
                  file=sys.stderr)
            sys.exit(2)
        body = gate(votes, bar, pop, decision_of, rule_of, ids_by_stratum)
        head = "# ACC x NCC P2 -- measured adjudicator precision\n"
    else:
        body = feasibility(pop, decision_of, rule_of, ids_by_stratum)
        head = ("# ACC x NCC P2 -- adjudicator precision, bar feasibility\n\n"
                "No spot-check votes have been returned yet, so **no stratum is "
                "measured and nothing is promoted**. The table below is what the "
                "sample of 674 cards CAN prove: the Wilson 95% lower bound each "
                "stratum reaches if its draw comes back perfect, and the rows "
                "riding on it.\n")

    with open(OUT_REPORT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(head + "\n")
        f.write("_Created: 26-07-2026 · Last updated: 26-07-2026_\n\n")
        f.write("Generated by [`p2_precision_gate.py`](p2_precision_gate.py) "
                "(H1657, Opus 5 1M `claude-opus-5[1m]`).\n\n")
        f.write("\n".join(body) + "\n")
    print(f"\nreport -> {OUT_REPORT}")


if __name__ == '__main__':
    main()
