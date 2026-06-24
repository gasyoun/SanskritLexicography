#!/usr/bin/env python
"""judge_ab_score.py — score an Opus-vs-Sonnet (or any two-model) QA-judge A/B.

Decides whether a cheaper judge model can replace the reference (Opus) for the scale-up.
Consumes two verdict sets — one per judge model — and reports the metrics that gate the
swap: OK/BAD agreement (+ Cohen's κ), severity deltas, and the decisive
**false-clear rate** (candidate passes a card the reference flagged BAD / sev≥3).

Verdict line schema (JSONL or JSON array), one per card:
  {"key1": str, "ok": bool, "severity": int 0-5, "issues": [str], "note": str}

  python judge_ab_score.py reference_opus.jsonl candidate_sonnet.jsonl
  python judge_ab_score.py --selftest          # the 2026-06-24 battleground (7 cards)

Decision rule (see research/JUDGE_AB.md): adopt the candidate for the bulk only if
κ ≥ 0.7 AND false-clear rate on reference-sev≥3 ≈ 0.
"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BAD_SEV = 3   # severity >= this (or ok=False) counts as a BAD verdict the judge must catch


def load(path):
    txt = open(path, encoding='utf-8').read().strip()
    if txt.startswith('['):
        rows = json.loads(txt)
    else:
        rows = [json.loads(l) for l in txt.splitlines() if l.strip()]
    return {r['key1']: r for r in rows}


def is_bad(v):
    return (not v.get('ok', True)) or int(v.get('severity', 0)) >= BAD_SEV


def kappa(ref, cand, keys):
    """Cohen's kappa on the binary BAD/not-BAD label."""
    n = len(keys)
    if not n:
        return 0.0
    rb = [is_bad(ref[k]) for k in keys]
    cb = [is_bad(cand[k]) for k in keys]
    po = sum(a == b for a, b in zip(rb, cb)) / n
    pr_ref, pr_cand = sum(rb) / n, sum(cb) / n
    pe = pr_ref * pr_cand + (1 - pr_ref) * (1 - pr_cand)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def score(ref, cand, ref_name='reference', cand_name='candidate'):
    keys = sorted(set(ref) & set(cand))
    n = len(keys)
    if not n:
        print('no shared keys between the two verdict sets'); return 1
    verdict_agree = sum(is_bad(ref[k]) == is_bad(cand[k]) for k in keys)
    sev_exact = sum(int(ref[k].get('severity', 0)) == int(cand[k].get('severity', 0)) for k in keys)
    sev_within1 = sum(abs(int(ref[k].get('severity', 0)) - int(cand[k].get('severity', 0))) <= 1 for k in keys)
    # false-clear: candidate says NOT bad where reference says BAD (the dangerous direction)
    ref_bad = [k for k in keys if is_bad(ref[k])]
    false_clears = [k for k in ref_bad if not is_bad(cand[k])]
    # over-flag: candidate says BAD where reference says not (wastes a repass; not dangerous)
    over_flags = [k for k in keys if is_bad(cand[k]) and not is_bad(ref[k])]
    k = kappa(ref, cand, keys)

    print('# judge A/B — %s (reference) vs %s (candidate), N=%d\n' % (ref_name, cand_name, n))
    print('  BAD/not-BAD agreement : %d/%d (%.0f%%)   Cohen κ = %.2f' % (verdict_agree, n, 100 * verdict_agree / n, k))
    print('  severity exact / ±1   : %d/%d / %d/%d' % (sev_exact, n, sev_within1, n))
    print('  reference-BAD cards   : %d' % len(ref_bad))
    print('  FALSE-CLEARS (candidate passed a reference-BAD card): %d %s'
          % (len(false_clears), false_clears or ''))
    print('  over-flags (candidate BAD, reference not)           : %d %s'
          % (len(over_flags), over_flags or ''))
    disagree = [k for k in keys if is_bad(ref[k]) != is_bad(cand[k])]
    if disagree:
        print('  disagreements:')
        for kk in disagree:
            print('    %-22s ref(ok=%s,sev=%s)  cand(ok=%s,sev=%s)'
                  % (kk, ref[kk].get('ok'), ref[kk].get('severity'),
                     cand[kk].get('ok'), cand[kk].get('severity')))
    adopt = k >= 0.7 and not false_clears
    print('\n  DECISION RULE (κ≥0.7 and 0 false-clears): %s'
          % ('candidate VIABLE for the bulk' if adopt else 'KEEP reference (candidate not yet validated)'))
    return 0


SELFTEST = ([  # reference = Opus judge, 2026-06-24 battleground
    {'key1': 'akz', 'ok': True, 'severity': 2}, {'key1': 'aMSu', 'ok': True, 'severity': 1},
    {'key1': 'akzan', 'ok': True, 'severity': 2}, {'key1': 'akzi', 'ok': True, 'severity': 1},
    {'key1': 'aMSa', 'ok': True, 'severity': 1},
    {'key1': 'aMSa_PLANT_gloss', 'ok': False, 'severity': 4},
    {'key1': 'aMSu_PLANT_coverage', 'ok': False, 'severity': 5},
], [          # candidate = Sonnet judge
    {'key1': 'akz', 'ok': True, 'severity': 1}, {'key1': 'aMSu', 'ok': True, 'severity': 2},
    {'key1': 'akzan', 'ok': True, 'severity': 2}, {'key1': 'akzi', 'ok': True, 'severity': 1},
    {'key1': 'aMSa', 'ok': True, 'severity': 1},
    {'key1': 'aMSa_PLANT_gloss', 'ok': False, 'severity': 5},
    {'key1': 'aMSu_PLANT_coverage', 'ok': False, 'severity': 5},
])


def main():
    if '--selftest' in sys.argv:
        ref = {r['key1']: r for r in SELFTEST[0]}
        cand = {r['key1']: r for r in SELFTEST[1]}
        return score(ref, cand, 'opus', 'sonnet')
    if len(sys.argv) < 3:
        print(__doc__); return 2
    return score(load(sys.argv[1]), load(sys.argv[2]), sys.argv[1], sys.argv[2])


if __name__ == '__main__':
    raise SystemExit(main())
