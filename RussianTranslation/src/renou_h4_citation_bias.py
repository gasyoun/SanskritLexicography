#!/usr/bin/env python
"""renou_h4_citation_bias.py — H4: dictionary citation bias (RENOU_HYPOTHESES.md).

Hypothesis: 19th-century dictionaries over-cite Vedic and kavya relative to
actual usage, and under-cite the epic. Two deterministic, non-gold-standard
routes are compared:

  citation side  per dict, per register: share of entries whose <ls>-route
                 register-provenance includes "ls" (renou_register_provenance
                 in {code}.renou.jsonl). Entry-level unit (the canonical index
                 does not retain per-entry resolved citation *instances* — see
                 Limitations in RENOU_H4_CITATION_BIAS.md).
  usage side     renou_corpus_map.py corpus-wide register shares over the
                 1,091,528 aligned Sa-Ru attestations (attestation-level unit).

bias(d, r) = log2( citation_share(d, r) / usage_share(r) )

Bootstrap (1,000 reps, resample entries with replacement) gives a 95% CI on
the citation side only (the usage-side baseline is treated as a fixed
population parameter per the spec — bootstrapping citation entries is what
answers "how much would this dict's profile move under resampling").

Scope guard: only registers reachable by BOTH routes (usage_share > 0 in the
corpus AND the register appears in at least one dict's ls-route) enter the
ratio table. One-route registers (jaina, epig -> ls-only; any corpus-only
genre) are reported separately. hors_inde is excluded (no source at all).

Read-only over {code}.renou.jsonl / corpus_lexicon.jsonl. Writes only to
RENOU_H4_CITATION_BIAS.md (by a separate write-up step) and
h4_citation_bias.json (this script's own gitignored intermediate — regenerate
with `python renou_h4_citation_bias.py`).

  python renou_h4_citation_bias.py [--reps 1000] [--seed 42] [--out h4_citation_bias.json]

Computed by Sonnet 5 (claude-sonnet-5).
"""
import json
import math
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from renou_register import REGISTERS       # noqa: E402
import renou_corpus_map as rcm             # noqa: E402

CANON = ('pwg', 'mw', 'pw', 'ap', 'ap90', 'ben', 'sch', 'bhs')


def load_entries(code):
    path = os.path.join(HERE, code + '.renou.jsonl')
    with open(path, encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def citation_register_sets(entries):
    """Per entry: the set of registers whose provenance includes 'ls'."""
    out = []
    for e in entries:
        rp = e.get('renou_register_provenance') or {}
        regs = frozenset(r for r, srcs in rp.items() if 'ls' in srcs)
        out.append(regs)
    return out


def shares_from_sets(reg_sets, registers):
    """Register -> share of entries citing it (an entry can cite >1 register,
    so shares need not sum to 1 — this is a per-register incidence rate, the
    correct comparand to a corpus-wide attestation share)."""
    n = len(reg_sets)
    if n == 0:
        return {r: 0.0 for r in registers}
    counts = {r: 0 for r in registers}
    for regs in reg_sets:
        for r in regs:
            if r in counts:
                counts[r] += 1
    return {r: counts[r] / n for r in registers}


def bootstrap_ci(reg_sets, registers, reps, seed, alpha=0.05):
    """Per-register 95% CI on the citation share via entry resampling
    (resample entries with replacement, 1,000 reps, per RENOU_HYPOTHESES.md H4
    method step 3).

    Exact-and-fast marginal shortcut: bootstrap-resampling n entries with
    replacement and asking "what fraction carries register r" has, MARGINALLY
    for each register r, exactly the distribution Binomial(n, p_hat_r) / n —
    the same distribution that resampling entire multi-label entry rows and
    recounting column r would produce, because each of the n resampled slots
    is an iid draw of one original entry's register-r membership regardless
    of what its other registers are. This holds for a *per-register*
    independent CI (what we report); it does NOT preserve the joint
    across-register resampling correlation, which H4 never needs (each
    register's CI is read independently in the table). Avoids materializing
    an (n_entries x n_registers) resampled matrix per rep — reps=1000 over
    MW's 286,560 entries runs in milliseconds instead of minutes."""
    n = len(reg_sets)
    if n == 0:
        return {r: (0.0, 0.0) for r in registers}
    reg_index = {r: i for i, r in enumerate(registers)}
    p_hat = np.zeros(len(registers))
    for regs in reg_sets:
        for r in regs:
            j = reg_index.get(r)
            if j is not None:
                p_hat[j] += 1
    p_hat /= n

    rng = np.random.default_rng(abs(hash(seed)) % (2**32))
    sums = rng.binomial(n, p_hat, size=(reps, len(registers)))
    shares = sums / n
    lo_idx = int(alpha / 2 * reps)
    hi_idx = min(reps - 1, int((1 - alpha / 2) * reps))
    shares_sorted = np.sort(shares, axis=0)
    out = {}
    for j, r in enumerate(registers):
        out[r] = (float(shares_sorted[lo_idx, j]), float(shares_sorted[hi_idx, j]))
    return out


def usage_shares():
    """Corpus-wide register shares (attestation-level), reusing
    renou_corpus_map.py's canonical genre/work -> register mapping."""
    lex_path = os.path.join(HERE, 'corpus_lexicon.jsonl')
    by = {}
    total = 0
    for line in open(lex_path, encoding='utf-8'):
        r = json.loads(line)
        reg = rcm.to_register(r.get('genre'), r.get('work'))
        by[reg] = by.get(reg, 0) + 1
        total += 1
    return {r: n / total for r, n in by.items()}, total, by


def log2_bias(cshare, ushare):
    if cshare <= 0 or ushare <= 0:
        return None
    return math.log2(cshare / ushare)


def main():
    args = sys.argv[1:]
    reps = 1000
    seed = 42
    out_path = os.path.join(HERE, 'h4_citation_bias.json')
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--reps':
            reps = int(args[i + 1]); i += 2
        elif a == '--seed':
            seed = int(args[i + 1]); i += 2
        elif a == '--out':
            out_path = args[i + 1]; i += 2
        else:
            raise SystemExit('unknown option: %s' % a)

    u_shares, u_total, u_counts = usage_shares()
    # registers reachable by the usage route at all (>0 attestations)
    usage_reachable = {r for r, s in u_shares.items() if s > 0}

    result = {
        'method': 'H4 dictionary citation bias — log2(citation_share / usage_share), '
                  'entry-level citation unit, attestation-level usage unit, '
                  '%d-rep bootstrap CI over entries' % reps,
        'seed': seed, 'reps': reps,
        'usage_side': {'total_attestations': u_total,
                        'shares': {r: u_shares.get(r, 0.0) for r in REGISTERS if r in usage_reachable}},
        'dicts': {},
    }

    for code in CANON:
        entries = load_entries(code)
        reg_sets = citation_register_sets(entries)
        n_entries = len(entries)
        n_with_ls_reg = sum(1 for s in reg_sets if s)
        c_shares = shares_from_sets(reg_sets, REGISTERS)
        cis = bootstrap_ci(reg_sets, REGISTERS, reps, seed='%d:%s' % (seed, code))

        both_route = {}
        one_route_ls_only = {}
        for r in REGISTERS:
            if r == 'hors_inde':
                continue
            cs = c_shares.get(r, 0.0)
            if cs <= 0 and r not in usage_reachable:
                continue
            if r in usage_reachable and cs > 0:
                us = u_shares[r]
                lo, hi = cis[r]
                both_route[r] = {
                    'citation_share': cs, 'citation_ci95': [lo, hi],
                    'usage_share': us,
                    'log2_bias': log2_bias(cs, us),
                    'log2_bias_ci95': [log2_bias(lo, us) if lo > 0 else None,
                                       log2_bias(hi, us) if hi > 0 else None],
                    'n_citing_entries': int(round(cs * n_entries)),
                }
            elif cs > 0 and r not in usage_reachable:
                one_route_ls_only[r] = {'citation_share': cs,
                                         'n_citing_entries': int(round(cs * n_entries))}

        result['dicts'][code] = {
            'n_entries': n_entries,
            'n_entries_with_ls_register': n_with_ls_reg,
            'both_route_registers': both_route,
            'ls_only_registers': one_route_ls_only,
        }

    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print('wrote %s' % out_path)

    # console summary: headline registers
    for code in CANON:
        d = result['dicts'][code]
        br = d['both_route_registers']
        line = []
        for r in ('epic', 'rgveda', 'kavya'):
            if r in br:
                b = br[r]
                line.append('%s log2=%.2f [%.2f,%.2f]' % (
                    r, b['log2_bias'],
                    b['log2_bias_ci95'][0] if b['log2_bias_ci95'][0] is not None else float('nan'),
                    b['log2_bias_ci95'][1] if b['log2_bias_ci95'][1] is not None else float('nan')))
        print('%-5s %s' % (code.upper(), ' · '.join(line)))


if __name__ == '__main__':
    main()
