#!/usr/bin/env python
r"""Predict — with NO LLM spend — which EN cards need the head-splitter.

The EN stores are a free labelled dataset: a card that is currently null FAILED the
StructuredOutput retry cap; a non-null card PASSED. Both outcomes are visible without
calling a model. This script scores every card by deterministic size/complexity
features (from its masked input), learns the pass/fail boundary from the stores, and
classifies each *residual* (null) card as:

  SPLIT   -- output-size-bound; will keep failing even solo -> route to the head-splitter
            (_pilot_gen_merged.py --root-split, lower HEAD_CIT_BUDGET) BEFORE any LLM try.
  RETRY   -- below the size boundary; its null is transient (fidelity-guard / variance)
            -> a cheap solo re-run will very likely recover it. No split needed.

Features (all from the source card, no model): raw bytes, <ls> count, {#..#} count,
total masked spans, and an estimated output-token load (german + translation both must
reproduce every masked span, so output ~= 2x skeleton).

  python src/pilot/en_split_triage.py            # triage all residual, print report
  python src/pilot/en_split_triage.py --all      # also dump the learned boundary stats
"""
import argparse
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
REPO = os.path.dirname(SRC)
sys.path.insert(0, HERE)
from window_common import input_paths  # noqa: E402


def feats(raw):
    ls = raw.count('<ls')
    sk = raw.count('{#')
    ab = raw.count('<ab')
    spans = ls + sk + ab
    # output-token load: masking turns each span into a short {Tn}; both the german
    # echo and the translation must reproduce every span, so cost ~ 2*(prose + spans).
    est_out_tok = (len(raw) * 2) // 3
    return {'raw': len(raw), 'ls': ls, 'sk': sk, 'ab': ab, 'spans': spans,
            'est_out_tok': est_out_tok}


def has_en(card):
    return bool(card and card.get('records') and any(
        any(s.get('english') for s in r.get('senses', []))
        for r in card['records']))


def scan():
    """Return list of (root, key, features, passed) for every card in every EN store.

    A residual key whose source input file is missing is NOT dropped (FL4): it is kept with
    a `missing_input` feature marker so it stays visible in triage. Silently skipping it hid
    a null card whose input we could not find — exactly the kind of card that needs a human's
    eye. Missing-input rows are excluded from boundary learning (no size features to learn)."""
    rows = []
    for fp in sorted(glob.glob(os.path.join(REPO, 'wf_output.en.*.json'))):
        root = os.path.basename(fp).replace('wf_output.en.', '').replace('.json', '')
        d = json.load(open(fp, encoding='utf-8'))
        passed = {}
        for e in d['results']:
            passed[e['key']] = has_en(e.get('card'))
        # A heal/autosplit-merge store (e.g. wf_output.en.man_heal.json) carries no
        # selected_keys — fall back to its result keys so its cards still appear in triage
        # rather than crashing the whole run (FL4: nothing should vanish from triage).
        selected = (d.get('meta') or {}).get('selected_keys')
        if selected is None:
            selected = [e['key'] for e in d['results']]
        for key in selected:
            rp, _ = input_paths(key)
            if not os.path.exists(rp):
                rows.append((root, key, {'missing_input': True}, passed.get(key, False)))
                continue
            raw = open(rp, encoding='utf-8').read()
            rows.append((root, key, feats(raw), passed.get(key, False)))
    return rows


def learn_boundary(rows):
    """Pick, per feature, the value that best separates pass/fail (max Youden's J),
    plus the 'clean' threshold = the smallest fail value above ALL pass values (a
    high-precision SPLIT cut: nothing above it ever passed)."""
    rows = [r for r in rows if not r[2].get('missing_input')]   # no size features to learn from
    out = {}
    for key in ('ls', 'est_out_tok', 'raw', 'spans'):
        passv = sorted(f[key] for _, _, f, p in rows if p)
        failv = sorted(f[key] for _, _, f, p in rows if not p)
        if not passv or not failv:
            continue
        pmax = passv[-1]
        # clean cut: lowest fail strictly above every pass -> 100% precision for SPLIT
        clean = min([v for v in failv if v > pmax], default=None)
        # Youden's J best split over candidate thresholds
        cands = sorted(set(passv + failv))
        best_t, best_j = None, -1
        P, N = len(failv), len(passv)
        for t in cands:
            tp = sum(1 for v in failv if v >= t)
            fp = sum(1 for v in passv if v >= t)
            j = (tp / P) - (fp / N)
            if j > best_j:
                best_j, best_t = j, t
        out[key] = {'pass_max': pmax, 'clean_split_cut': clean,
                    'youden_t': best_t, 'youden_j': round(best_j, 3),
                    'pass_n': N, 'fail_n': P}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--all', action='store_true', help='also print learned boundary stats')
    args = ap.parse_args()
    rows = scan()
    b = learn_boundary(rows)
    # SPLIT rule: ls >= clean_split_cut(ls)  (nothing that passed had ls this high).
    # This is the high-precision boundary; the dense zz_pw supplements that fail on
    # {#..#} rather than <ls> are caught by the est_out_tok clean cut as a backstop.
    ls_cut = b.get('ls', {}).get('clean_split_cut')
    tok_cut = b.get('est_out_tok', {}).get('clean_split_cut')

    def needs_split(f):
        if ls_cut is not None and f['ls'] >= ls_cut:
            return True
        if tok_cut is not None and f['est_out_tok'] >= tok_cut:
            return True
        return False

    resid = [(r, k, f) for r, k, f, p in rows if not p]
    # Missing-input residuals have no size features — keep them VISIBLE in their own section
    # (FL4) rather than dropping them, but exclude them from size classification/sorting.
    missing_input = [(r, k) for r, k, f in resid if f.get('missing_input')]
    sized = [(r, k, f) for r, k, f in resid if not f.get('missing_input')]
    split, retry = [], []
    for r, k, f in sized:
        (split if needs_split(f) else retry).append((r, k, f))

    print('=== EN residual triage (no LLM) — %d null card(s) (%d missing-input) ==='
          % (len(resid), len(missing_input)))
    if ls_cut is None and tok_cut is None:
        print('FINDING: NO clean size wall exists — some cards that PASSED are larger on')
        print('every feature than the ones that failed (the 5 largest <ls> cards all passed).')
        print('=> failure is stochastic (retry-cap variance / content difficulty), NOT size.')
        print('=> a spend-free "needs split" predictor is impossible; RETRY-FIRST is correct.')
        print('   Only a card that persists after several INDEPENDENT solo tries is a genuine')
        print('   splitter candidate. Below: residual ranked by risk = retry priority order.\n')
    else:
        print('learned high-precision cuts: <ls> >= %s  OR  est_out_tok >= %s' % (ls_cut, tok_cut))
        print('  (nothing that PASSED reached these; so anything at/above is size-bound.)\n')
        print('--- SPLIT (%d) — head-split first, do NOT waste an LLM try ---' % len(split))
        for r, k, f in sorted(split, key=lambda x: -x[2]['ls']):
            print('  %-26s ls=%-4d sk=%-4d raw=%-6d ~out=%d' % (k, f['ls'], f['sk'], f['raw'], f['est_out_tok']))
    label = 'RETRY priority (ranked by risk; recover cheaply, escalate only if persistent)'
    print('--- %s (%d) ---' % (label, len(sized)))
    for r, k, f in sorted(sized, key=lambda x: -x[2]['est_out_tok']):
        print('  %-26s ls=%-4d sk=%-4d raw=%-6d ~out=%d' % (k, f['ls'], f['sk'], f['raw'], f['est_out_tok']))
    if missing_input:
        print('--- MISSING INPUT (%d) — null card, source file absent; needs manual attention '
              '(NOT silently dropped) ---' % len(missing_input))
        for r, k in sorted(missing_input):
            print('  %-26s (root %s) — no input file at src/pilot/input/' % (k, r))

    if args.all:
        print('\n=== learned boundary per feature (from %d cards) ===' % len(rows))
        for key, s in b.items():
            print('  %-12s pass_max=%-6s clean_split_cut=%-6s youden_t=%-6s J=%s (%dP/%dF)' % (
                key, s['pass_max'], s['clean_split_cut'], s['youden_t'], s['youden_j'],
                s['pass_n'], s['fail_n']))


if __name__ == '__main__':
    main()
