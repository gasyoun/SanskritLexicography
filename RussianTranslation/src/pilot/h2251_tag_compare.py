#!/usr/bin/env python
"""H2251 -- rule the H2189 §4.2 `tag`-vocabulary divergence IN or OUT, mechanically.

H2189 ran one real card through two spawn arms and saw different free-text `tag`
vocabularies come back:

    paid  ->  tail · name · xref · sch-name · pwkvn-name
    safe  ->  cross-ref · addendum-1 · addendum-crossref · SCH-Nachtrag · PWKVN-crossref

Both validate (the schema types `tag` as a bare non-empty string) and every gate the
project actually checks was identical across arms. But it was **n=1 per arm**, so the
observation had two live explanations and no way to choose:

  (A) `--safe-mode` changes the tag vocabulary  -- a real behaviour change, and a reason
      not to flip the default;
  (B) tag vocabulary is simply not stable between two independent generations of the same
      card -- sampling variation, in which case the divergence says nothing about the flag.

THE DISCRIMINATING DESIGN -- why repeats, not more cards
--------------------------------------------------------
Adding more *cards* to a one-call-per-arm design cannot separate (A) from (B): every extra
card still contributes exactly one paid draw and one safe draw, so every difference stays
attributable to either cause. What separates them is **repeats within an arm**. Run the
same card twice on the SAME arm and the flag is held constant by construction, so any tag
difference that appears there is (B) and nothing else.

So the statistic is a comparison of two distances, not a diff:

    within-arm  distance  = d(paid#1, paid#2), d(safe#1, safe#2), ...   flag held CONSTANT
    between-arm distance  = d(paid#i, safe#j)                          flag VARIED

  * within ~= 0 and between >> 0  -> the flag tracks the vocabulary: (A), refuse the flip.
  * within comparable to between  -> the vocabulary is not stable run to run: (B), the
    divergence is sampling noise and is closed.

`d` is Jaccard distance over the set of tag strings in a card (0.0 identical, 1.0 disjoint).
Sets, not sequences: the question is which vocabulary the model reached for, and a
positional diff would score two identical vocabularies as different merely for ordering.

Reads the raw envelopes `h2189_profile_ab.py` commits (`h2189_card_<arm>_<key>_<n>.json`),
so it re-analyses an existing run for free and never issues a call of its own.

    python src/pilot/h2251_tag_compare.py --raw pwg_ru/h2251/raw
    python src/pilot/h2251_tag_compare.py --selftest        # offline, spends nothing

Model: authored by Opus 5 (`claude-opus-5`) for handoff H2251.
"""
import argparse
import glob
import itertools
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# h2189_profile_ab.py writes `h2189_<phase>_<arm>_<key>_<n>.json`. Arm names contain no
# underscore-free guarantee (`safe_clean`, `clean_cwd`), so anchor on the KNOWN arm names
# rather than splitting on '_' and mis-attributing `safe_clean` rows to `safe`.
ENVELOPE_RE = re.compile(
    r'^h2189_card_(?P<arm>safe_clean|clean_cwd|minimal|paid|safe)_(?P<key>.+)_(?P<n>\d+)\.json$')

# A verdict needs BOTH distances to exist. With one draw per arm there is no within-arm
# distance at all, which is exactly the H2189 position this handoff was minted to leave.
MIN_REPEATS_PER_ARM = 2


def load_cards(path):
    """Return the `cards` list from a CLI envelope, or [] when the call produced none."""
    with open(path, encoding='utf-8') as fh:
        wrapper = json.load(fh)
    result = wrapper.get('result', wrapper)
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except ValueError:
            return []
    if not isinstance(result, dict):
        return []
    cards = result.get('cards')
    return cards if isinstance(cards, list) else []


def tags_of(cards):
    """Every non-empty `tag` string in a card payload, as a set.

    Empty and whitespace-only tags are dropped rather than counted as a shared member: an
    absent annotation is not a vocabulary choice, and keeping it would inflate the measured
    similarity of every pair equally.
    """
    tags = set()
    for card in cards or []:
        for record in (card.get('records') or []):
            for sense in (record.get('senses') or []):
                tag = (sense.get('tag') or '').strip()
                if tag:
                    tags.add(tag)
    return tags


def jaccard_distance(a, b):
    """0.0 = identical vocabulary, 1.0 = disjoint. Two empty sets count as identical."""
    if not a and not b:
        return 0.0
    return 1.0 - len(a & b) / float(len(a | b))


# A bare sense NUMBER (`0`, `1`, `2`, `3`, and the `1)`/`2.` shapes) is structural: it
# mirrors PWG's own sense numbering, so every arm and every draw reproduces it. The
# H2189 §4.2 observation was about the FREE-TEXT labels alongside those (`tail`, `xref`,
# `SCH-Nachtrag`, …), which is where the vocabulary is actually chosen.
NUMERIC_TAG_RE = re.compile(r'^\d+[).\-]?$')


def free_text(tags):
    """The free-text subset -- the tags §4.2 was actually about."""
    return {t for t in tags if not NUMERIC_TAG_RE.match(t)}


def collect(raw_dir):
    """Map (arm, key, n) -> tag set for every card envelope in a raw dir."""
    draws = {}
    for path in sorted(glob.glob(os.path.join(raw_dir, 'h2189_card_*.json'))):
        m = ENVELOPE_RE.match(os.path.basename(path))
        if not m:
            continue                      # rollups (h2189_card_rows.json) and other files
        cards = load_cards(path)
        draws[(m.group('arm'), m.group('key'), int(m.group('n')))] = {
            'tags': tags_of(cards), 'cards': len(cards), 'path': path}
    return draws


def pair_distances(draws, key):
    """Within-arm and between-arm Jaccard distances for one card."""
    by_arm = {}
    for (arm, k, n), draw in draws.items():
        if k == key:
            by_arm.setdefault(arm, []).append((n, draw))
    within, between = [], []
    for arm, items in sorted(by_arm.items()):
        for (n1, d1), (n2, d2) in itertools.combinations(sorted(items), 2):
            within.append({'arm': arm, 'a': '%s#%d' % (arm, n1), 'b': '%s#%d' % (arm, n2),
                           'distance': jaccard_distance(d1['tags'], d2['tags']),
                           'free_text_distance': jaccard_distance(free_text(d1['tags']),
                                                                  free_text(d2['tags']))})
    for arm1, arm2 in itertools.combinations(sorted(by_arm), 2):
        for n1, d1 in sorted(by_arm[arm1]):
            for n2, d2 in sorted(by_arm[arm2]):
                between.append({'arms': '%s|%s' % (arm1, arm2),
                                'a': '%s#%d' % (arm1, n1), 'b': '%s#%d' % (arm2, n2),
                                'distance': jaccard_distance(d1['tags'], d2['tags']),
                                'free_text_distance': jaccard_distance(
                                    free_text(d1['tags']), free_text(d2['tags']))})
    return by_arm, within, between


def mean(values):
    return sum(values) / float(len(values)) if values else None


def verdict(within, between):
    """Rule the divergence from the two distance families. Refuses on insufficient design.

    The rule is deliberately conservative in one direction: `flag` (refuse the flip) is
    returned whenever the within-arm family is tight AND the between-arm family is not, so
    an ambiguous middle never reads as a licence to flip.
    """
    if not within:
        return ('insufficient', 'no within-arm repeats: the flag was never held constant, '
                                'so no observed difference can be attributed. This is the '
                                'n=1 design H2189 already ran.')
    if not between:
        return ('insufficient', 'only one arm present: nothing to compare it against.')
    w, b = mean([p['distance'] for p in within]), mean([p['distance'] for p in between])
    if w == 0.0 and b == 0.0:
        return ('stable', 'tag vocabulary was IDENTICAL everywhere -- within arm and '
                          'across arms. The H2189 divergence did not reproduce at all.')
    if w == 0.0 and b > 0.0:
        return ('flag', 'tag vocabulary is REPRODUCIBLE within each arm (mean within-arm '
                        'distance 0.0) but differs across arms (mean %.3f): the vocabulary '
                        'tracks --safe-mode, not the draw.' % b)
    if w >= b:
        return ('draw', 'tag vocabulary varies run-to-run on the SAME arm at least as much '
                        'as it does across arms (within %.3f >= between %.3f): the H2189 '
                        'divergence is sampling variation, not a --safe-mode effect.' % (w, b))
    return ('mixed', 'tag vocabulary is unstable within an arm (mean %.3f) AND differs more '
                     'across arms (mean %.3f). Neither cause is excluded; do not read this '
                     'as a licence to flip.' % (w, b))


def report(raw_dir, out_json=None):
    draws = collect(raw_dir)
    if not draws:
        print('no card envelopes under %s' % raw_dir, file=sys.stderr)
        return 2
    keys = sorted({k for (_a, k, _n) in draws})
    per_key, all_within, all_between = [], [], []
    for key in keys:
        by_arm, within, between = pair_distances(draws, key)
        all_within.extend(within)
        all_between.extend(between)
        per_key.append({'key': key,
                        'arms': {arm: {'draws': len(items),
                                       'tags': sorted(set().union(
                                           *[d['tags'] for _n, d in items]) or set())}
                                 for arm, items in sorted(by_arm.items())},
                        'within': within, 'between': between})

    print('raw dir : %s' % raw_dir)
    print('draws   : %d envelope(s) over %d card(s)' % (len(draws), len(keys)))
    for entry in per_key:
        print('\n== %s ==' % entry['key'])
        for arm, info in entry['arms'].items():
            short = min(info['draws'], MIN_REPEATS_PER_ARM) < MIN_REPEATS_PER_ARM
            print('  %-11s %d draw(s)%s  tags: %s'
                  % (arm, info['draws'], '  <- no within-arm pair' if short else '',
                     ' · '.join(info['tags']) or '(none)'))
        for pair in entry['within']:
            print('  within  %-22s all %.3f   free-text %.3f'
                  % ('%s vs %s' % (pair['a'], pair['b']),
                     pair['distance'], pair['free_text_distance']))
        for pair in entry['between']:
            print('  between %-22s all %.3f   free-text %.3f'
                  % ('%s vs %s' % (pair['a'], pair['b']),
                     pair['distance'], pair['free_text_distance']))

    w, b = (mean([p['distance'] for p in all_within]),
            mean([p['distance'] for p in all_between]))
    wf, bf = (mean([p['free_text_distance'] for p in all_within]),
              mean([p['free_text_distance'] for p in all_between]))
    ruling, why = verdict(all_within, all_between)
    print('\n== ruling ==')
    print('mean within-arm  distance: %s (n=%d)'
          % ('n/a' if w is None else '%.3f' % w, len(all_within)))
    print('mean between-arm distance: %s (n=%d)'
          % ('n/a' if b is None else '%.3f' % b, len(all_between)))
    print('H2189 §4.2 tag divergence: %s' % ruling.upper())
    print('  %s' % why)
    # Reported, never ruled on. The verdict stays on the full tag set -- the metric this
    # tool was written with, BEFORE any of these numbers existed. The free-text split is
    # the sharper view of the same question (§4.2 was about the free-text labels; the bare
    # sense numbers are structural and reproduce everywhere, so including them makes every
    # distance CONSERVATIVELY small), but choosing a metric after seeing the data is how a
    # measurement talks itself into a conclusion. It corroborates; it does not decide.
    print('\nfree-text tags only (reported, NOT the basis of the ruling):')
    print('  mean within-arm  %s   mean between-arm %s'
          % ('n/a' if wf is None else '%.3f' % wf,
             'n/a' if bf is None else '%.3f' % bf))

    payload = {'raw_dir': raw_dir, 'keys': keys, 'per_key': per_key,
               'mean_within_arm_distance': w, 'mean_between_arm_distance': b,
               'mean_within_arm_free_text_distance': wf,
               'mean_between_arm_free_text_distance': bf,
               'within_pairs': len(all_within), 'between_pairs': len(all_between),
               'ruling': ruling, 'why': why}
    if out_json:
        with open(out_json, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
            fh.write('\n')
        print('\nwrote %s' % out_json)
    return 0


def _draw(arm, key, n, tags):
    return (arm, key, n), {'tags': set(tags), 'cards': 1, 'path': '<fixture>'}


def selftest():
    """Offline. Pins the two rulings that carry a decision, and the refusal in between."""
    assert jaccard_distance(set('ab'), set('ab')) == 0.0
    assert jaccard_distance(set('ab'), set('cd')) == 1.0
    assert jaccard_distance(set(), set()) == 0.0, 'two empty tag sets are not a difference'

    # The H2189 shape itself: one draw per arm. It must NOT produce a ruling -- that design
    # is precisely what could not attribute the divergence.
    n1 = dict([_draw('paid', 'k', 1, ['tail', 'name']),
               _draw('safe', 'k', 1, ['cross-ref', 'addendum-1'])])
    _by, within, between = pair_distances(n1, 'k')
    assert verdict(within, between)[0] == 'insufficient', \
        'n=1 per arm must refuse to rule; that is the H2189 position this handoff exists to leave'

    # (B) noise: the same arm disagrees with itself as much as the arms disagree.
    noisy = dict([_draw('paid', 'k', 1, ['tail', 'name']),
                  _draw('paid', 'k', 2, ['cross-ref', 'addendum-1']),
                  _draw('safe', 'k', 1, ['tail', 'name']),
                  _draw('safe', 'k', 2, ['cross-ref', 'addendum-1'])])
    _by, within, between = pair_distances(noisy, 'k')
    assert verdict(within, between)[0] == 'draw'

    # (A) real effect: each arm reproduces itself exactly, and the arms differ.
    real = dict([_draw('paid', 'k', 1, ['tail', 'name']),
                 _draw('paid', 'k', 2, ['tail', 'name']),
                 _draw('safe', 'k', 1, ['cross-ref', 'addendum-1']),
                 _draw('safe', 'k', 2, ['cross-ref', 'addendum-1'])])
    _by, within, between = pair_distances(real, 'k')
    assert verdict(within, between)[0] == 'flag'

    # Ambiguity is never silently rounded down to a licence to flip.
    mixed = dict([_draw('paid', 'k', 1, ['tail', 'name']),
                  _draw('paid', 'k', 2, ['tail', 'xref']),
                  _draw('safe', 'k', 1, ['cross-ref', 'addendum-1']),
                  _draw('safe', 'k', 2, ['SCH-Nachtrag', 'PWKVN-crossref'])])
    _by, within, between = pair_distances(mixed, 'k')
    assert verdict(within, between)[0] == 'mixed'

    # `safe_clean` must not be parsed as arm `safe` -- it is a different spawn shape, and
    # folding it in would put a stacked-lever draw inside safe's within-arm family.
    m = ENVELOPE_RE.match('h2189_card_safe_clean_nakzatra_2.json')
    assert m and m.group('arm') == 'safe_clean' and m.group('key') == 'nakzatra', m
    m = ENVELOPE_RE.match('h2189_card_safe_nakzatra_1.json')
    assert m and m.group('arm') == 'safe' and m.group('n') == '1', m

    print('h2251_tag_compare selftest: PASS')
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--raw', help='dir of committed h2189_card_*.json envelopes')
    ap.add_argument('--json-out', help='write the full comparison payload here')
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
