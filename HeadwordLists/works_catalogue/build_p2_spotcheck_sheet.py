"""ACC x NCC P2 -- draw the stratified human spot-check sample (H1657).

The human is not re-deciding the 49,019 Tier C/D rows; the human is MEASURING
the agent that decided them (adjudicate_p2.py). So this script draws a
stratified sample, renders it through the existing sheet machinery, and keeps
the agent's own verdict OUT of the sheet.

## Why the sheet is blind

If a card showed "the agent said approve", the vote would measure agreement
with a visible answer, not independent judgement, and every precision figure
downstream would be an anchoring artefact. The agent verdicts live in
`p2_spotcheck_manifest.json`, which `p2_precision_gate.py` joins against the
returned votes. The human sees exactly what the full sheet shows.

## Sizing -- fixed here, BEFORE the draw

  * approve strata  n = 50   (promotion gates on these)
  * reject  strata  n = 40
  * any stratum smaller than its n is taken in full (census)

Rationale, in the terms the gate will use (Wilson 95% LOWER bound, the
discipline H1470 ratified -- a point estimate of 3/3 = 1.000 proves nothing,
its lower bound is 0.44):

    n = 50, 50/50 correct -> LB 0.929      n = 40, 40/40 -> LB 0.912
    n = 50, 49/50         -> LB 0.885      n = 40, 39/40 -> LB 0.869
    n = 50, 48/50         -> LB 0.850      n = 40, 38/40 -> LB 0.831

**The sample size caps the reachable bar, and that is a fact about the sample,
not about the adjudicator.** No stratum drawn at n = 50 can ever exceed a
0.929 lower bound, so a bar above ~0.92 promotes nothing however good the
agent is. Both n values are chosen so that a 0.90 bar is *attainable* on both
sides: at n = 25 (the first draft of this sample) the reject strata topped out
at 0.867 and a 0.90 bar would have silently made every rejection unpublishable
-- a structural defect in the sample, not a finding about the rules. Reaching
a 0.95 bar would need n ~= 80 per stratum, roughly 1,400 cards; that is a
larger ask and a separate decision.

Approve strata carry the tighter draw because they decide what enters a
citable dataset; a wrong *reject* costs recall in a file that already records
itself as provisional.

Usage:
    python HeadwordLists/works_catalogue/build_p2_spotcheck_sheet.py
"""
import sys
import os
import json
import gzip
import random
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import build_p2_sheet as sheet  # noqa: E402  (shared renderer)

VERDICTS = os.path.join(HERE, "p2_agent_verdicts.jsonl.gz")
CANDIDATES = os.path.join(HERE, "crosswalk_candidates.jsonl.gz")
OUT_HTML = os.path.join(REPO_ROOT, 'review',
                        'sanskritlexicography-acc_ncc_p2_spotcheck.html')
OUT_MANIFEST = os.path.join(HERE, "p2_spotcheck_manifest.json")
SHEET_ID = 'sanskritlexicography-acc_ncc_p2_spotcheck'

N_APPROVE = 50
N_REJECT = 40
SEED = 16572026  # H1657, fixed so the draw is reproducible


def main():
    by_stratum = defaultdict(list)
    verdict_of = {}
    with gzip.open(VERDICTS, 'rt', encoding='utf-8') as f:
        for line in f:
            v = json.loads(line)
            by_stratum[v['stratum']].append(v['id'])
            verdict_of[v['id']] = (v['stratum'], v['decision'], v['rule'])

    # --- the plan, printed BEFORE the draw ---------------------------------
    plan = []
    for stratum in sorted(by_stratum):
        ids = by_stratum[stratum]
        decision = verdict_of[ids[0]][1]
        target = N_APPROVE if decision == 'approve' else N_REJECT
        n = min(target, len(ids))
        plan.append({'stratum': stratum, 'decision': decision,
                     'population': len(ids), 'n': n,
                     'census': n == len(ids)})

    total_pop = sum(p['population'] for p in plan)
    total_n = sum(p['n'] for p in plan)
    print(f"sampling plan (fixed before the draw) -- {len(plan)} strata, "
          f"population {total_pop:,}, sample {total_n:,}\n")
    print(f"{'stratum':52s} {'verdict':8s} {'pop':>7s} {'n':>5s}  mode")
    for p in plan:
        print(f"{p['stratum']:52s} {p['decision']:8s} {p['population']:7,} "
              f"{p['n']:5d}  {'census' if p['census'] else 'random'}")
    print(f"\n{'TOTAL':52s} {'':8s} {total_pop:7,} {total_n:5d}")

    # --- the draw ----------------------------------------------------------
    rng = random.Random(SEED)
    sampled_ids = set()
    for p in plan:
        ids = sorted(by_stratum[p['stratum']])
        sampled_ids.update(ids if p['census'] else rng.sample(ids, p['n']))

    # --- render the cards from the ORIGINAL candidate rows ------------------
    # Deliberately re-read crosswalk_candidates.jsonl.gz rather than the
    # verdict file: the human must see exactly the card the full sheet would
    # have shown, with no agent-derived field anywhere in the DOM.
    cards = []
    with gzip.open(CANDIDATES, 'rt', encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            if r['tier'] not in ('C', 'D'):
                continue
            if f"{r['acc_L']}__{r['ncc_id']}" in sampled_ids:
                cards.append(sheet.card_for(r))
    # Shuffle so consecutive cards are not from one stratum -- a run of 50
    # near-identical approve cards would train the eye into a rhythm.
    rng.shuffle(cards)

    sheet.render(cards, SHEET_ID, OUT_HTML,
                 heading='ACC×NCC P2 — adjudicator spot-check (blind)')

    manifest = {
        'sheet_id': SHEET_ID,
        'handoff': 'H1657',
        'adjudicator': 'adjudicate_p2.py (Opus 5 1M `claude-opus-5[1m]`)',
        'seed': SEED,
        'n_approve_target': N_APPROVE,
        'n_reject_target': N_REJECT,
        'population_total': total_pop,
        'sample_total': len(cards),
        'blind': True,
        'plan': plan,
        'agent_verdicts': {rid: {'stratum': verdict_of[rid][0],
                                 'decision': verdict_of[rid][1],
                                 'rule': verdict_of[rid][2]}
                           for rid in sorted(sampled_ids)},
    }
    with open(OUT_MANIFEST, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print(f"\ndrew {len(cards):,} cards -> {OUT_HTML}")
    print(f"answer key (not in the sheet) -> {OUT_MANIFEST}")


if __name__ == '__main__':
    main()
