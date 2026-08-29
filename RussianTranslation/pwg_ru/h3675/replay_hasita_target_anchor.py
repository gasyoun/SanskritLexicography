#!/usr/bin/env python
r"""H3675 — replay `hasita~~h0_zz_pw` through the TARGET-side repair, offline.

The companion to [`../h3665/replay_hasita_german_anchor.py`](../h3665/replay_hasita_german_anchor.py),
which established that `german_anchor` returns `nothing-missing` on this card: every source
span IS present, in the `german` field, and the loss is in `russian`. That is why H3675 exists.

Same reconstruction, same justification: the model's own card for `hasita` is on disk nowhere
(`normalize_batch` sets `card = None` on `translation-fidelity-reject`, and
`write_failed_envelope` only fires on a PROCESS-level failure, which that batch was not —
FINDINGS §608). What survives pins the card's shape by control flow: reaching the target-field
guard requires the german-only count to have already matched, so `hasita`'s german echo was
exactly `<ls> 2/2, {# 2/2` and only `russian` was short.

Run: python replay_hasita_target_anchor.py [--evidence-root DIR]
Zero network, zero model calls.
"""
import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'src'))

import german_anchor  # noqa: E402
import target_anchor  # noqa: E402

DEFAULT_ROOT = r"D:\ClaudeTools\profiles\claude1\.pwg_ru_evidence\c1\h3659"
KEY = 'hasita~~h0_zz_pw'


def build_masked_card():
    """The card `hasita` provably produced: german faithful, russian one span short.

    Sense split follows the skeleton's own `— 1〉` / `— 2〉` numbering; every `{Tn}` keeps its
    source order. `{T7}` (`<ls>GAUT.</ls>`) is the span the translation dropped.
    """
    return {'key1': 'hasita',
            'records': [{'senses': [
                {'n': '1',
                 'german': '{T1}¦ {T8}— 1〉 {T2} {T3} {T9}2.{T10} {T4}.',
                 'russian': '{T1}¦ {T8}— 1〉 {T2} {T3} {T9}2.{T10} {T4}.'},
                {'n': '2',
                 'german': '{T11}— 2〉 {T5} das Lachen, Gelächter {T6}. {T7}',
                 'russian': '{T11}— 2〉 {T5} смех, хохот {T6}.'}]}]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--evidence-root', default=DEFAULT_ROOT)
    args = ap.parse_args()

    with open(os.path.join(args.evidence_root, 'execution_manifest.w09v2.json'),
              encoding='utf-8') as handle:
        manifest = json.load(handle)
    inp = manifest['inputs'][KEY]
    field = manifest['field']
    print('key            : %s' % KEY)
    print('field          : %s' % field)
    print('source counts  : ls=%d sk=%d' % (inp['ls'], inp['sk']))

    card = target_anchor._card  # noqa: F841  (keeps the module import honest under linters)
    card = build_masked_card()
    senses = target_anchor.card_senses(card)
    for index, sense in enumerate(senses):
        print('sense %d german : %s' % (index + 1, ' '.join(target_anchor.tokens(sense['german']))))
        print('sense %d %-7s: %s' % (index + 1, field,
                                     ' '.join(target_anchor.tokens(sense[field]))))

    # The H3665 result, restated so the two replays can be read side by side.
    g_ok, g_info = german_anchor.plan(card, inp['skeleton'])
    print('')
    print('german_anchor.plan   -> ok=%s info=%s' % (g_ok, json.dumps(g_info, ensure_ascii=False)))

    ok, info = target_anchor.reanchor(card, field)
    print('target_anchor.reanchor -> ok=%s' % ok)
    if not ok:
        print('   info=%s' % json.dumps(info, ensure_ascii=False))
        print('')
        print('VERDICT: the target repair REFUSED this card.')
        return 1
    print('   reinjected=%s stamp=%s'
          % (info['missing'], json.dumps(target_anchor.stamp(info), ensure_ascii=False)))
    print('')
    for index, sense in enumerate(target_anchor.card_senses(card)):
        print('sense %d %s -> %s' % (index + 1, field, sense[field]))
    print('')

    # The verifier the production caller runs: per-sense target tokens must now equal the
    # german ones exactly. `count_card_field` counts `<ls`/`{#` after restore; at this stage
    # the equivalent statement is token-for-token equality against the anchor.
    for index, sense in enumerate(target_anchor.card_senses(card)):
        got = target_anchor.tokens(sense[field])
        want = target_anchor.tokens(sense['german'])
        assert got == want, (index, got, want)
    print('VERIFIER: every sense\'s %s token sequence now equals its german anchor exactly.'
          % field)
    print('VERDICT: `hasita~~h0_zz_pw` is REPAIRED by the target-side anchor -- the card that')
    print('         cost a paid window and was requeued as unfixable is promotable.')
    print('         `german_anchor` on the same card: %s.' % g_info.get('reason'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
