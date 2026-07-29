#!/usr/bin/env python
r"""H1210 — a one-card probe for what the fidelity gate cannot see: gloss ARITY drift.

The deterministic gate and the canonical audit both check the `{Tn}` mask as a MULTISET —
every German token present, none invented. That catches sense loss and token invention, and
it is blind to a card where the token mask is perfect but each German gloss has quietly
become two or three Russian ones ('erblickend' -> 'узревающий, взирающий'). Inflation of that
kind reads as fluent Russian and is not a fidelity reject, so nothing in the A/B's numbers
would ever surface it.

This is a PROBE, not a measurement: it was run on a single card (`kAS`, arm B) during the
H1210 close-out. Its output is a list of candidate arity drifts to look at by eye, not a
rate. Treat a hit as a question for the reviewer, not a defect count.

Usage:
  python src/pilot/h1210/qc_gloss_arity.py <senses.json>

Input is a JSON list of `{tag, german, russian}` objects — the shape `slice_result`'s
per-sense rows already carry.
"""
import argparse
import json
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

TOK = re.compile(r"\{T\d+\}")
GLOSS = re.compile(r"\{%(.*?)%\}", re.S)


def n_glosses(text):
    return len([x for x in re.split(r'[,;]', text) if x.strip()])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('senses', help='JSON list of {tag, german, russian}')
    a = ap.parse_args()
    senses = json.load(open(a.senses, encoding='utf-8'))

    all_de_tokens = Counter()
    hits = 0
    for s in senses:
        de, ru = Counter(TOK.findall(s['german'])), Counter(TOK.findall(s['russian']))
        all_de_tokens.update(de)
        if de != ru:
            print('[TOKEN MISMATCH] tag=%s missing_in_ru=%s extra_in_ru=%s'
                  % (s['tag'], dict(de - ru), dict(ru - de)))
            hits += 1
        gd, gr = GLOSS.findall(s['german']), GLOSS.findall(s['russian'])
        if len(gd) != len(gr):
            print('[GLOSS COUNT] tag=%s de=%d ru=%d' % (s['tag'], len(gd), len(gr)))
            hits += 1
            continue
        for de_g, ru_g in zip(gd, gr):
            na, nb = n_glosses(de_g), n_glosses(ru_g)
            if na != nb:
                print("[GLOSS ARITY] tag=%s de(%d)='%s' -> ru(%d)='%s'"
                      % (s['tag'], na, de_g, nb, ru_g))
                hits += 1

    nums = sorted(int(t[2:-1]) for t in all_de_tokens)
    print('\nduplicate german tokens: %s' % {k: v for k, v in all_de_tokens.items() if v > 1})
    if nums:
        print('token range: %d-%d (count %d), gaps: %s'
              % (nums[0], nums[-1], len(nums),
                 [n for n in range(nums[0], nums[-1] + 1) if n not in set(nums)]))
    print('candidate arity drifts: %d' % hits)


if __name__ == '__main__':
    main()
