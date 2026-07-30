"""ACC x NCC P2 -- draw the stratified human spot-check sample (H1657 / H1951).

The human is not re-deciding the Tier C/D rows; the human is MEASURING
the agent that decided them (adjudicate_p2.py). So this script draws a
stratified sample, renders it through the existing sheet machinery, and keeps
the agent's own verdict OUT of the sheet.

## Why the sheet is blind

If a card showed "the agent said approve", the vote would measure agreement
with a visible answer, not independent judgement, and every precision figure
downstream would be an anchoring artefact. The agent verdicts live in
`p2_spotcheck_manifest.json`, which `p2_precision_gate.py` joins against the
returned votes. The human sees exactly what the full sheet shows.

## Sizing -- derived BEFORE the draw (H1951 re-cut)

MG's 30-07-2026 ruling (in-Grok vote 4c, H1948): **re-draw a larger sample
first** before locking the Wilson promotion bar, so a 0.95 bar is attainable.

Wilson 95% lower bound at perfect agreement simplifies to n/(n+z^2), z=1.96:
    n = 72 -> LB 0.9493  (fails 0.95)
    n = 73 -> LB 0.9500  (clears 0.95)
    n = 50 -> LB 0.929   (old H1657 draw; 0.95 unreachable by construction)

  * approve strata  n = 73   (promotion gates on these)
  * reject  strata  n = 73   (same floor: a 0.95 bar must be reachable both sides)
  * any stratum smaller than its n is taken in full (census)

Sensitivity (same n, imperfect agreement):
    n = 73, 73/73 -> LB 0.950   n = 73, 72/73 -> LB 0.926
    n = 73, 71/73 -> LB 0.906   n = 120, 119/120 -> LB 0.954 (1-err still clears)

Strata with population < 73 are censused and still cannot clear a 0.95 Wilson
LB even when perfect (e.g. C-same_author_prefix-c pop=62 -> max LB ~0.942).
That is a fact about the stratum size, reported in P2_PRECISION.md; the bar
vote after the human sample must reckon with it.

The previous H1671 re-draw (seed 16572026, n=50/40, 698 cards) is superseded
and was unvoted — re-drawing discards no human work.

Usage:
    python HeadwordLists/works_catalogue/build_p2_spotcheck_sheet.py
"""
import sys
import os
import json
import gzip
import random
import hashlib
import datetime
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import build_p2_sheet as sheet  # noqa: E402  (shared renderer)

# H1404 binding (stamp/write_lock) lives under RussianTranslation; import path.
sys.path.insert(0, os.path.join(REPO_ROOT, 'RussianTranslation', 'src'))
from review_binding import write_lock  # noqa: E402

VERDICTS = os.path.join(HERE, "p2_agent_verdicts.jsonl.gz")
CANDIDATES = os.path.join(HERE, "crosswalk_candidates.jsonl.gz")
OUT_HTML = os.path.join(REPO_ROOT, 'review',
                        'sanskritlexicography-acc_ncc_p2_spotcheck.html')
OUT_MANIFEST = os.path.join(HERE, "p2_spotcheck_manifest.json")
# Root /review/ is gitignored (local HTML only). Lock + manifest are committed
# under this directory so the sample frame survives without the HTML.
LOCKS_DIR = HERE
SHEET_ID = 'sanskritlexicography-acc_ncc_p2_spotcheck'

# Minimum n with wilson_lower(n, n) >= 0.95 (H1951).
N_APPROVE = 73
N_REJECT = 73
SEED = 19512026  # H1951, fixed so the draw is reproducible
GENERATED = '30-07-2026'
HANDOFF = 'H1951'


def _content_hash(html_text):
    norm = html_text.replace('\r\n', '\n').replace('\r', '\n')
    return 'sha256:' + hashlib.sha256(norm.encode('utf-8')).hexdigest()


def _stamp_p2_sheet(html_text, card_ids):
    """Stamp the custom virtualized P2 sheet (not csl_pyutil emitter layout).

    The shared renderer uses ``const SHEET_ID`` and an inline payload object,
    so review_binding.stamp() anchors do not match. Binding contract is the
    same: hash pre-stamp HTML, embed CONTENT_HASH, echo it on export, write
    a metadata-only lock.
    """
    if 'var CONTENT_HASH' in html_text or 'const CONTENT_HASH' in html_text:
        raise ValueError('sheet already stamped — regenerate instead of re-stamping')
    chash = _content_hash(html_text)
    # Declare CONTENT_HASH next to SHEET_ID.
    if 'const SHEET_ID =' not in html_text:
        raise ValueError('expected const SHEET_ID declaration in P2 sheet')
    stamped = html_text.replace(
        'const SHEET_ID = "%s";' % SHEET_ID,
        'const SHEET_ID = "%s";\nconst CONTENT_HASH = %s;\nconst IDS = %s;' % (
            SHEET_ID, json.dumps(chash), json.dumps(list(card_ids))),
        1,
    )
    # Export payload carries the hash so validate_decisions can join.
    old_payload = (
        'const payload = { sheet_id: SHEET_ID, generated: new Date().toISOString(), '
        'decided: Object.keys(decisions).length, items };'
    )
    new_payload = (
        'const payload = { sheet_id: SHEET_ID, content_hash: CONTENT_HASH, '
        'generated: new Date().toISOString(), decided: Object.keys(decisions).length, '
        'items };'
    )
    if old_payload not in stamped:
        raise ValueError('export payload anchor not found — renderer layout changed')
    stamped = stamped.replace(old_payload, new_payload, 1)
    # Visible chip in the header title area (best-effort).
    chip = (
        ' &middot; bound <code class="bindchip" title="content_hash — binds this '
        'sheet\'s decisions.json export to exactly this HTML">%s…</code>'
        % chash[:19]
    )
    # Insert after the heading text if present.
    marker = 'adjudicator spot-check (blind)'
    if marker in stamped:
        stamped = stamped.replace(marker, marker + chip, 1)
    return stamped, chash


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
                     'census': n == len(ids),
                     'max_wilson_lb_if_perfect': None})  # filled after import of gate fn

    # Compute max attainable LB without importing the whole gate module.
    import math
    Z = 1.959963985

    def wilson_lower(k, n):
        if n == 0:
            return 0.0
        p = k / n
        denom = 1 + Z * Z / n
        centre = (p + Z * Z / (2 * n)) / denom
        half = (Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))) / denom
        return max(0.0, centre - half)

    for p in plan:
        p['max_wilson_lb_if_perfect'] = round(wilson_lower(p['n'], p['n']), 4)
        p['clears_0_95_if_perfect'] = p['max_wilson_lb_if_perfect'] >= 0.95

    total_pop = sum(p['population'] for p in plan)
    total_n = sum(p['n'] for p in plan)
    print(f"sampling plan (fixed before the draw) -- {len(plan)} strata, "
          f"population {total_pop:,}, sample {total_n:,}\n")
    print(f"{'stratum':52s} {'verdict':8s} {'pop':>7s} {'n':>5s}  "
          f"{'LB n/n':>7s}  mode / 0.95?")
    for p in plan:
        mode = 'census' if p['census'] else 'random'
        ok = 'YES' if p['clears_0_95_if_perfect'] else 'no'
        print(f"{p['stratum']:52s} {p['decision']:8s} {p['population']:7,} "
              f"{p['n']:5d}  {p['max_wilson_lb_if_perfect']:7.3f}  {mode} / {ok}")
    print(f"\n{'TOTAL':52s} {'':8s} {total_pop:7,} {total_n:5d}")
    n_clear = sum(1 for p in plan if p['clears_0_95_if_perfect'])
    print(f"\nstrata that can clear 0.95 on a perfect vote: {n_clear}/{len(plan)}")

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
    # Shuffle so consecutive cards are not from one stratum -- a run of 73
    # near-identical approve cards would train the eye into a rhythm.
    rng.shuffle(cards)

    html = sheet.render(
        cards, SHEET_ID, OUT_HTML,
        heading='ACC×NCC P2 — adjudicator spot-check (blind)')

    # H1681/H1404 binding: stamp + write_lock. Force=True is intentional re-cut
    # (H1951); the prior 698-card generation was unvoted.
    stamped, chash = _stamp_p2_sheet(html, [c['id'] for c in cards])
    with open(OUT_HTML, 'w', encoding='utf-8', newline='\n') as f:
        f.write(stamped)
    lock_path = write_lock(
        SHEET_ID, chash, [c['id'] for c in cards], GENERATED,
        locks_dir=LOCKS_DIR, gate='ACC-NCC-P2',
        source_html=OUT_HTML, mode='stamped', force=True,
    )

    manifest = {
        'sheet_id': SHEET_ID,
        'handoff': HANDOFF,
        'supersedes': {
            'handoff': 'H1657/H1671',
            'seed': 16572026,
            'n_approve_target': 50,
            'n_reject_target': 40,
            'sample_total': 698,
            'note': 'unvoted; re-drawn so a 0.95 Wilson bar is attainable (MG vote 4c, 30-07-2026)',
        },
        'adjudicator': 'adjudicate_p2.py (Opus 5 1M `claude-opus-5[1m]`)',
        'seed': SEED,
        'n_approve_target': N_APPROVE,
        'n_reject_target': N_REJECT,
        'wilson_bar_design_target': 0.95,
        'min_n_for_bar': 73,
        'population_total': total_pop,
        'sample_total': len(cards),
        'blind': True,
        'content_hash': chash,
        'generated': GENERATED,
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
    print(f"content_hash {chash}")
    print(f"lock -> {lock_path}")


if __name__ == '__main__':
    main()
