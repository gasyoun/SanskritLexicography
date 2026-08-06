#!/usr/bin/env python
"""H2251 -- is the CARD equivalent across spawn arms? The question the `tag` ruling leaves.

`h2251_tag_compare.py` answers whether the free-text `tag` vocabulary tracks `--safe-mode`.
It came back MIXED: the vocabulary is only partly reproducible within an arm, yet every
between-arm pair is completely disjoint. So the H2189 §4.2 divergence is REAL and
arm-linked -- it is not sampling noise that will wash out.

That makes this the decisive question, and it is a different one: a difference in a
free-text label no gate consumes is only acceptable if the CARD ITSELF -- the translated
content the store actually keeps -- is equivalent across arms. H2189 §4.1 checked exactly
this and found it equivalent, but at n=1 per arm. Here it runs over every committed draw.

The measures are the project's own, not private heuristics:

  * records / senses / senses carrying non-empty target-language text -- a dropped sense is
    the SAN-LOSS class the canary exists to catch;
  * the `{Tn}` masked-span token SET, via `promote_final_cards.TN_RE` -- the same
    single-sourced regex the promote C-01 guard uses. A masked span dropped or invented is
    a real defect regardless of how the sense is labelled;
  * literal `SAN-LOSS` / `UNMAPPED` markers, via `canary_gate.LITERAL_MARKERS`;
  * target-language and German character volume, as a coarse "did the card shrink" read.

A tag-style difference over an equivalent card is cosmetic. A tag-style difference over a
card that lost a sense or a masked span is not, and would refuse the flip on its own.

    python src/pilot/h2251_content_equivalence.py --raw pwg_ru/h2251/raw
    python src/pilot/h2251_content_equivalence.py --selftest      # offline

Model: authored by Opus 5 (`claude-opus-5`) for handoff H2251.
"""
import argparse
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)                     # promote_final_cards lives one level up
for _p in (HERE, SRC):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Import-only, for the ONE canonical regex. Nothing here calls a promote/supersede path --
# this script never writes to the store (Uprava FINDINGS §9 overlay-wipe class).
from promote_final_cards import TN_RE                       # noqa: E402  C-01 single source
from canary_gate import LITERAL_MARKERS                     # noqa: E402  same marker list
from h2251_tag_compare import ENVELOPE_RE, load_cards       # noqa: E402  one envelope reader

FIELD = 'russian'


def profile_card(cards):
    """Structural profile of one draw. Language-agnostic except for the target field name."""
    records = senses = filled = 0
    tn, markers, target_chars, german_chars = set(), set(), 0, 0
    for card in cards or []:
        for record in (card.get('records') or []):
            records += 1
            for sense in (record.get('senses') or []):
                senses += 1
                target = (sense.get(FIELD) or '')
                german = (sense.get('german') or '')
                if target.strip():
                    filled += 1
                target_chars += len(target)
                german_chars += len(german)
                tn.update(TN_RE.findall(target))
                tn.update(TN_RE.findall(german))
                for marker in LITERAL_MARKERS:
                    if marker in target or marker in german:
                        markers.add(marker)
    return {'records': records, 'senses': senses, 'senses_with_target': filled,
            'tn_tokens': tn, 'markers': sorted(markers),
            'target_chars': target_chars, 'german_chars': german_chars}


def collect(raw_dir):
    out = {}
    for path in sorted(glob.glob(os.path.join(raw_dir, 'h2189_card_*.json'))):
        m = ENVELOPE_RE.match(os.path.basename(path))
        if not m:
            continue
        out[(m.group('key'), m.group('arm'), int(m.group('n')))] = profile_card(
            load_cards(path))
    return out


def jaccard(a, b):
    if not a and not b:
        return 0.0
    return 1.0 - len(a & b) / float(len(a | b))


def compare(profiles, key):
    """Per-card content comparison, decomposed WITHIN arm vs BETWEEN arms.

    The decomposition is the whole point, and getting it wrong is easy: a first cut of this
    script asked only "do all draws agree?", which lumps the two together and reports
    DIFFER for a card whose `paid` arm merely disagreed with ITSELF. That is precisely the
    conflation the `tag` analysis was designed to avoid, re-introduced on the measure that
    matters more. A difference is evidence about `--safe-mode` ONLY if the same arm
    reproduces itself; otherwise it is evidence about the pipeline's own nondeterminism.
    """
    arms = {}
    for (k, arm, n), prof in sorted(profiles.items()):
        if k == key:
            arms.setdefault(arm, []).append((n, prof))
    rows, problems = [], []
    for arm, draws in sorted(arms.items()):
        for n, prof in draws:
            rows.append((arm, n, prof))
            # These two are DEFECTS at any n: they are not "variation", they are loss.
            if prof['markers']:
                problems.append('%s#%d: literal %s in card content'
                                % (arm, n, '/'.join(prof['markers'])))
            if prof['senses_with_target'] != prof['senses']:
                problems.append('%s#%d: %d/%d senses carry %s (sense loss)'
                                % (arm, n, prof['senses_with_target'], prof['senses'], FIELD))

    def spread(values):
        return max(values) - min(values) if values else 0

    within = {}
    for arm, draws in sorted(arms.items()):
        senses = [p['senses'] for _n, p in draws]
        records = [p['records'] for _n, p in draws]
        tn = [p['tn_tokens'] for _n, p in draws]
        within[arm] = {
            'senses': senses, 'sense_spread': spread(senses),
            'records': records, 'record_spread': spread(records),
            'tn_distance': (jaccard(tn[0], tn[1]) if len(tn) == 2 else None),
            'tn_identical': (tn[0] == tn[1]) if len(tn) == 2 else None,
        }

    between = None
    if len(arms) == 2:
        (a1, d1), (a2, d2) = sorted(arms.items())
        s1 = [p['senses'] for _n, p in d1]
        s2 = [p['senses'] for _n, p in d2]
        pairs = [jaccard(p1['tn_tokens'], p2['tn_tokens'])
                 for _n1, p1 in d1 for _n2, p2 in d2]
        between = {
            'arms': '%s|%s' % (a1, a2),
            'sense_range': {a1: [min(s1), max(s1)], a2: [min(s2), max(s2)]},
            # Do the two arms' sense counts even separate? If their ranges overlap, the
            # arm cannot be read off the count -- the flag is not what moved it.
            'sense_ranges_overlap': not (max(s1) < min(s2) or max(s2) < min(s1)),
            'mean_tn_distance': sum(pairs) / float(len(pairs)) if pairs else None,
        }
    return rows, problems, {'within': within, 'between': between}


def report(raw_dir, out_json=None):
    profiles = collect(raw_dir)
    if not profiles:
        print('no card envelopes under %s' % raw_dir, file=sys.stderr)
        return 2
    keys = sorted({k for (k, _a, _n) in profiles})
    payload, all_problems, all_agree = [], [], []
    print('%-10s %-6s %2s %8s %7s %8s %7s %9s %9s'
          % ('key', 'arm', '#', 'records', 'senses', 'w/target', '{Tn}', 'ru_chars', 'de_chars'))
    for key in keys:
        rows, problems, agreement = compare(profiles, key)
        for arm, n, prof in rows:
            print('%-10s %-6s %2d %8d %7d %8d %7d %9d %9d'
                  % (key, arm, n, prof['records'], prof['senses'],
                     prof['senses_with_target'], len(prof['tn_tokens']),
                     prof['target_chars'], prof['german_chars']))
        all_problems.extend('%s: %s' % (key, p) for p in problems)
        all_agree.append((key, agreement))
        payload.append({'key': key, 'agreement': agreement, 'problems': problems,
                        'draws': [{'arm': a, 'n': n,
                                   'records': p['records'], 'senses': p['senses'],
                                   'senses_with_target': p['senses_with_target'],
                                   'tn_tokens': sorted(p['tn_tokens']),
                                   'markers': p['markers'],
                                   'target_chars': p['target_chars'],
                                   'german_chars': p['german_chars']}
                                  for a, n, p in rows]})

    print('\n== within-arm reproducibility (the flag held CONSTANT) ==')
    for key, agreement in all_agree:
        for arm, info in sorted(agreement['within'].items()):
            print('  %-10s %-6s senses %-9s spread %d   records %-7s   {Tn} d=%s'
                  % (key, arm, info['senses'], info['sense_spread'], info['records'],
                     'n/a' if info['tn_distance'] is None else '%.3f' % info['tn_distance']))

    print('\n== between-arm (the flag VARIED) ==')
    for key, agreement in all_agree:
        b = agreement['between']
        if not b:
            continue
        print('  %-10s sense ranges %s   ranges overlap: %s   mean {Tn} d=%s'
              % (key, json.dumps(b['sense_range']),
                 'YES' if b['sense_ranges_overlap'] else 'NO',
                 'n/a' if b['mean_tn_distance'] is None else '%.3f' % b['mean_tn_distance']))

    # The decision rule, stated before reading the numbers:
    #   * a DEFECT (sense with no content, literal SAN-LOSS/UNMAPPED) refuses on its own,
    #     at any n -- that is loss, not variation;
    #   * otherwise the flag is implicated only if each arm REPRODUCES ITSELF and the arms
    #     nonetheless differ. An arm that does not reproduce itself cannot be the cause of
    #     a difference from the other arm.
    reproducible = all(info['sense_spread'] == 0 and info['tn_identical'] is not False
                       for _k, a in all_agree for info in a['within'].values())
    separable = all(a['between'] and not a['between']['sense_ranges_overlap']
                    for _k, a in all_agree)
    print('\n== content verdict ==')
    for problem in all_problems:
        print('  DEFECT %s' % problem)
    if all_problems:
        verdict = ('REFUSE — a card lost content (above). That is loss, not variation, and '
                   'it refuses the flip on its own regardless of the arm comparison.')
    elif reproducible and separable:
        verdict = ('FLAG-LINKED — each arm reproduces itself AND the arms separate. The '
                   'card content tracks --safe-mode; do not flip.')
    elif not reproducible:
        verdict = ('NOT REPRODUCIBLE ON EITHER ARM — sense segmentation and/or the {Tn} set '
                   'move between two draws of the SAME card on the SAME arm. Card content is '
                   'therefore not a function of the spawn shape, and a paid-vs-safe '
                   'difference of the same magnitude is not attributable to --safe-mode. '
                   'Zero content LOSS in any draw (every sense carries text, no SAN-LOSS/'
                   'UNMAPPED marker anywhere), which is the property the gates actually check.')
    else:
        verdict = ('INCONCLUSIVE — arms reproduce but do not separate, or vice versa. '
                   'Do not read this as a licence to flip.')
    print('  %s' % verdict)
    clean = not all_problems

    if out_json:
        with open(out_json, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump({'raw_dir': raw_dir, 'per_key': payload, 'no_content_loss': clean, 'verdict': verdict,
                       'problems': all_problems}, fh, ensure_ascii=False, indent=2)
            fh.write('\n')
        print('\nwrote %s' % out_json)
    return 0 if clean else 1


def selftest():
    """Offline. A dropped sense and a dropped {Tn} must each break equivalence."""
    def cards(senses):
        return [{'records': [{'senses': senses}]}]

    good = [{'russian': '{T1} огонь', 'german': '{T1} Feuer'},
            {'russian': '{T2} свет', 'german': '{T2} Licht'}]
    prof = profile_card(cards(good))
    assert prof['senses'] == 2 and prof['senses_with_target'] == 2
    assert prof['tn_tokens'] == {'{T1}', '{T2}'}, prof['tn_tokens']

    empty_target = [{'russian': '  ', 'german': '{T1} Feuer'}]
    assert profile_card(cards(empty_target))['senses_with_target'] == 0, \
        'a sense with no target text must not count as filled -- that is the SAN-LOSS class'

    marked = [{'russian': 'SAN-LOSS', 'german': 'x'}]
    assert profile_card(cards(marked))['markers'] == ['SAN-LOSS']

    # Two arms that differ ONLY in tag text stay equivalent; a dropped {Tn} does not.
    # Two arms, two draws each, identical content: each arm reproduces itself (spread 0,
    # {Tn} identical) and the arms do not separate.
    same = {('k', arm, n): profile_card(cards(good))
            for arm in ('paid', 'safe') for n in (1, 2)}
    _rows, problems, agreement = compare(same, 'k')
    assert not problems
    assert all(i['sense_spread'] == 0 and i['tn_identical']
               for i in agreement['within'].values()), agreement['within']
    assert agreement['between']['sense_ranges_overlap'], \
        'identical arms were reported as separating'

    # The case that must implicate the FLAG: each arm reproduces itself, arms differ.
    short = [{'russian': '{T1} огонь', 'german': '{T1} Feuer'}]
    flagged = {('k', 'paid', 1): profile_card(cards(good)),
               ('k', 'paid', 2): profile_card(cards(good)),
               ('k', 'safe', 1): profile_card(cards(short)),
               ('k', 'safe', 2): profile_card(cards(short))}
    _rows, _problems, agreement = compare(flagged, 'k')
    assert all(i['sense_spread'] == 0 for i in agreement['within'].values())
    assert not agreement['between']['sense_ranges_overlap'], \
        'two arms that never overlap in sense count were reported as overlapping'

    # An arm that disagrees with ITSELF must NOT be read as a flag effect.
    noisy = {('k', 'paid', 1): profile_card(cards(good)),
             ('k', 'paid', 2): profile_card(cards(short)),
             ('k', 'safe', 1): profile_card(cards(good)),
             ('k', 'safe', 2): profile_card(cards(short))}
    _rows, _problems, agreement = compare(noisy, 'k')
    assert agreement['within']['paid']['sense_spread'] == 1, \
        'within-arm sense variation was not measured'
    assert agreement['between']['sense_ranges_overlap'], \
        'arms with identical ranges were reported as separating -- that would blame the ' \
        'flag for the pipeline\'s own nondeterminism'

    print('h2251_content_equivalence selftest: PASS')
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--raw')
    ap.add_argument('--json-out')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        selftest()
        return 0
    if not args.raw:
        ap.error('--raw is required (or --selftest)')
    return report(args.raw, args.json_out)


if __name__ == '__main__':
    sys.exit(main())
