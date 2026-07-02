#!/usr/bin/env python
r"""Ingest a `--tm` run's freshly-translated fragments into the fragment translation memory.

The harness (gen_opt_harness2.py --tm) returns `harvest = { "k#gi#i": restored_senses }`
for every fragment it translated (including fragments of a card that ultimately nulled).
This re-derives each fragment's SOURCE text from the same deterministic split the harness
used — so no source text ever travels through the workflow payload — and writes
source -> senses into src/pilot/tm/tm.<lang>.frag.jsonl, keyed by the run's own
`tm_prompt_sha` (from meta). Next time the same fragment appears (a retry of the same
card, or a different card sharing that source), `--tm` serves it from cache instead of
re-calling the model.

  python src/pilot/tm_harvest.py <task_output_file>     # a --tm run's saved workflow output
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from window_common import input_paths, read_text
from gen_opt_harness2 import _group_by_budget
from autosplit_requeue import plan as split_plan
import pwg_mask
from translation_memory import TM


def fragment_sources(key, budget):
    """Reproduce the harness's fragment grouping for `key` -> {(gi, i): source_text}.
    Mirrors gen_opt_harness2.build's selfheal precompute exactly (same split, same lossy
    guard, same citation-weighted grouping) so positions line up with the harvest keys."""
    pl = split_plan(read_text(input_paths(key)[0]))
    if len(pl) < 2:
        return {}
    fl = []
    for _si, _pi, t in pl:
        fsk, fph, _ = pwg_mask.mask(t)
        if pwg_mask.restore(fsk, fph) != t:
            return {}                      # lossy -> the harness skipped this card's fallback
        fl.append({'ls': t.count('<ls'), 'src': t})
    groups = _group_by_budget(fl, lambda it: 1 + it['ls'], budget)
    out = {}
    for gi, g in enumerate(groups):
        for i, it in enumerate(g):
            out[(gi, i)] = it['src']
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit('usage: tm_harvest.py <task_output_file>')
    with open(sys.argv[1], encoding='utf-8') as f:
        wrapper = json.load(f)
    result = wrapper.get('result', wrapper)
    if isinstance(result, str):
        result = json.loads(result)

    meta = result.get('meta') or {}
    harvest = result.get('harvest') or {}
    if not meta.get('tm'):
        sys.exit('not a --tm run (meta.tm is false) — nothing to harvest')
    if not harvest:
        print('harvest empty — nothing to ingest')
        return
    lang = meta['lang']
    psha = meta.get('tm_prompt_sha') or ''
    budget = meta.get('selfheal_group_budget') or 12

    # group harvest keys by card, re-derive that card's fragment sources once
    by_key = {}
    for pk, senses in harvest.items():
        k, gi, i = pk.rsplit('#', 2)
        by_key.setdefault(k, {})[(int(gi), int(i))] = senses

    tm = TM(lang, psha, path=os.path.join(HERE, 'tm', 'tm.%s.frag.jsonl' % lang))
    before = len(tm)
    added = 0
    missing = 0
    for k, frags in by_key.items():
        src_map = fragment_sources(k, budget)
        for (gi, i), senses in frags.items():
            src = src_map.get((gi, i))
            if src is None:
                missing += 1
                continue
            if tm.put(src, senses):
                added += 1
    tm.save()
    print('lang=%s prompt_sha=%s' % (lang, psha))
    print('harvested fragments : %d  (new/changed %d, position-miss %d)'
          % (len(harvest), added, missing))
    print('fragment TM %s: %d -> %d entries' % (os.path.basename(tm.path), before, len(tm)))


if __name__ == '__main__':
    main()
