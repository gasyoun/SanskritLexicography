#!/usr/bin/env python
r"""H3665 step 2 — replay `hasita~~h0_zz_pw` through `german_anchor` OFFLINE.

Why a RECONSTRUCTED card and not the model's own output: the model's card for `hasita` is
not on disk anywhere. `normalize_batch` sets `card = None` the moment it raises
`translation-fidelity-reject` (headless_worker.py:906-907) and `write_failed_envelope` only
fires on a PROCESS-level failure, which this batch was not (`b2` returned 0). So the H3659
evidence root carries the verdict and never the artefact.

What survives is stronger than a guess, though: the error string itself pins the card's
shape by control flow. Reaching line 902 requires line 879's condition to be FALSE, i.e.

    count_card(card, '<ls') == inp['ls'] == 2   and   count_card(card, '{#') == inp['sk'] == 2

-- `count_card` being german-only by design. So `hasita`'s german echo was EXACTLY faithful,
and only the `russian` field was short. This script rebuilds that proven state from the
manifest skeleton and asks `german_anchor` what it would have done.

Run: python replay_hasita_german_anchor.py [--evidence-root DIR]
Zero network, zero model calls.
"""
import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'src'))

import german_anchor  # noqa: E402

DEFAULT_ROOT = r"D:\ClaudeTools\profiles\claude1\.pwg_ru_evidence\c1\h3659"
KEY = 'hasita~~h0_zz_pw'


def build_masked_card(skeleton):
    """The card `hasita` provably produced: german faithful, russian one span short.

    Sense split follows the skeleton's own `— 1〉` / `— 2〉` numbering; every `{Tn}` keeps its
    source order, which is what `german_anchor.plan` checks.
    """
    return {'key1': 'hasita',
            'records': [{'senses': [
                {'n': '1',
                 'german': '{T1}¦ {T8}— 1〉 {T2} {T3} {T9}2.{T10} {T4}.',
                 'russian': '{T1}¦ {T8}— 1〉 {T2} {T3} {T9}2.{T10} {T4}.'},
                {'n': '2',
                 'german': '{T11}— 2〉 {T5} смех, хохот {T6}. {T7}',
                 # the drop: `{T7}` (<ls>GAUT.</ls>) never made it into the translation
                 'russian': '{T11}— 2〉 {T5} смех, хохот {T6}.'}]}]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--evidence-root', default=DEFAULT_ROOT)
    args = ap.parse_args()

    manifest_path = os.path.join(args.evidence_root, 'execution_manifest.w09v2.json')
    with open(manifest_path, encoding='utf-8') as handle:
        manifest = json.load(handle)
    inp = manifest['inputs'][KEY]
    skeleton = inp['skeleton']
    print('key            : %s' % KEY)
    print('field          : %s' % manifest['field'])
    print('source counts  : ls=%d sk=%d' % (inp['ls'], inp['sk']))
    print('skeleton tokens: %s' % ' '.join(german_anchor.tokens(skeleton)))

    card = build_masked_card(skeleton)
    german_tokens = [t for sense in german_anchor.card_senses(card)
                     for t in german_anchor.tokens(sense.get('german'))]
    russian_tokens = [t for sense in german_anchor.card_senses(card)
                      for t in german_anchor.tokens(sense.get('russian'))]
    print('german echo    : %s  (%d)' % (' '.join(german_tokens), len(german_tokens)))
    print('russian echo   : %s  (%d)' % (' '.join(russian_tokens), len(russian_tokens)))

    ok, info = german_anchor.plan(card, skeleton)
    print('')
    print('german_anchor.plan -> ok=%s info=%s' % (ok, json.dumps(info, ensure_ascii=False)))
    ok2, info2 = german_anchor.reanchor(card, skeleton)
    print('german_anchor.reanchor -> ok=%s info=%s' % (ok2, json.dumps(info2, ensure_ascii=False)))
    print('')
    if not ok:
        print('VERDICT: the repair CANNOT touch this card. Refusal reason %r -- every source'
              % info.get('reason'))
        print('         span is present in `german`; the drop is in `russian`, a field')
        print('         `german_anchor` neither reads nor writes (module docstring,')
        print('         DELIBERATE SCOPE LIMITS). Two independent defects, not one:')
        print('         (a) wiring -- the repair is gated on the german-only count at')
        print('             headless_worker.py:879 and a translation-only drop never enters it;')
        print('         (b) coverage -- even if invoked, `plan` returns nothing-missing.')
        return 0
    print('VERDICT: the repair WOULD have fixed this card -- pure wiring defect.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
