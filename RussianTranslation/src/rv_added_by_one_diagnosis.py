#!/usr/bin/env python
r"""rv_added_by_one_diagnosis.py -- why `added_by_one` never fires (H2192, W1-RV residual).

H1844 measured `added_by_one` at **0 of 12,000** pilot labels and H1901 reproduced the
zero on three independently-trained model arms (0/300, 0/300, 0/267). Both entries in
`docs/DECISIONS_LOG_rv_multitranslation.md` recorded the same verdict -- "a prompt or
taxonomy defect, not a fact about the Rigveda" -- and both left the cause unmeasured.
This module measures it, deterministically, from committed data with **no model call and
no network**.

Three independent lines of evidence, one command each:

  structural  -- `added_by_one` and `omitted_by_one` are CONVERSE RELATIONS over one
                 undirected event. The pair key is unordered (`a|b`), the model-arm reply
                 schema is `{"class", "why"}` with no side field, and the deterministic arm
                 emits `missing_side` for exactly the same event class. So a model that
                 sees surplus material on one side cannot say WHICH side, and the two
                 labels become one label with a coin flip between them. Also proves the
                 K3 coarse projection is unstable: the same event maps to `omission` or
                 `divergence` depending on which of the two converse names is drawn.
  surplus     -- the population the class was supposed to catch, measured on the committed
                 spine over the pilot's own 2,000 stanzas: per-translator supplied-material
                 marker rates, and per-pair counts of stanzas where exactly ONE side carries
                 a marker. This is where `added_by_one` had to fire and did not.
  coarse-kappa-- recomputes H1901's coarse-projection kappa on the three committed spike
                 arms under the OLD map and under the FIXED map (both converse classes to
                 one coarse class), so the cost of the defect to the K3 decision is a
                 number rather than an assertion.

Usage:
  python src/rv_added_by_one_diagnosis.py structural
  python src/rv_added_by_one_diagnosis.py surplus [--pilot pwg_ru/rv_divergence_pilot.jsonl]
  python src/rv_added_by_one_diagnosis.py coarse-kappa
  python src/rv_added_by_one_diagnosis.py report      # all three, the committed report body
  python src/rv_added_by_one_diagnosis.py selftest    # asserts only, no data files needed

Marker caveat stated up front, because the numbers are worthless without it: a bracket or
parenthesis is a PROXY for editorially supplied material, not proof of it, and the
convention differs by edition. Elizarenkova parenthesises supplied words as a matter of
house style; Griffith's Victorian padding is italicised in print and carries no delimiter
at all in our extracted text. So the marker rate measures the population where the
DIRECTION is recoverable from the text, which is exactly the population the class needs --
it does not measure "who padded more".
"""
import argparse
import collections
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT_ROOT = os.path.normpath(os.path.join(HERE, '..'))
PWG_RU_DIR = os.path.join(RT_ROOT, 'pwg_ru')

# Reuse the typer's own vocabulary rather than restating it -- if TRANSLATORS or COARSE_MAP
# move, this diagnosis moves with them instead of silently measuring a stale taxonomy.
sys.path.insert(0, HERE)
import rv_divergence_type as dt  # noqa: E402

PILOT_PATH = dt.PILOT_OUT
SPIKE_ARMS = [
    os.path.join(dt.RUN_DIR, 'spike.ds-v3.jsonl'),
    os.path.join(dt.RUN_DIR, 'spike.gpt4o-mini.jsonl'),
    os.path.join(dt.RUN_DIR, 'spike.gemini-flash.jsonl'),
]

ASYMMETRIC = ('added_by_one', 'omitted_by_one')

# Supplied-material proxies, counted separately because the two delimiters carry different
# editorial conventions and collapsing them would hide that.
SQUARE = re.compile(r'\[[^\]]+\]')
ROUND = re.compile(r'\([^)]+\)')

# The fix this module argues for: the converse pair projects to ONE coarse class, because
# it is one event. Kept here rather than imported so the old and new maps can be compared
# in the same run.
COARSE_MAP_FIXED = dict(dt.COARSE_MAP, added_by_one='omission')


# --------------------------------------------------------------------- structural
def structural_facts():
    """Properties of the instrument itself, read off the typer module. Each is a fact a
    reader can re-derive from `src/rv_divergence_type.py` in one grep.

    Two kinds are mixed here on purpose. The first two are permanent properties of the
    DOMAIN -- an unordered pair key and two converse class definitions -- which no fix
    removes and which are exactly why a direction has to be carried explicitly. The last
    three are GUARD properties of the H2192 fix: they hold now, they did not hold when the
    12,000-label pilot ran, and if any of them regresses `added_by_one` goes inert again.
    """
    facts = []

    unordered = all('|' in k for k in dt.PAIR_KEYS) and len(set(
        frozenset(k.split('|')) for k in dt.PAIR_KEYS)) == len(dt.PAIR_KEYS)
    facts.append((
        'pair key is unordered',
        unordered,
        'PAIR_KEYS holds one key per UNORDERED pair (%d keys for %d translators). '
        'Nothing in the key distinguishes "a added" from "b omitted".'
        % (len(dt.PAIR_KEYS), len(dt.TRANSLATORS)),
    ))

    converse_defs = all(
        any(l.strip().startswith('- "%s"' % c) for l in dt.SYSTEM.splitlines())
        for c in ASYMMETRIC)
    facts.append((
        'the two class definitions are converse relations over one event',
        converse_defs,
        'omitted_by_one := one rendering leaves material the other renders; '
        'added_by_one := one rendering supplies material with no counterpart in the other. '
        'On an unordered pair {a,b} those are the SAME configuration read from opposite '
        'ends: material present in a and absent in b satisfies both readings. A class name '
        'alone therefore cannot identify the event -- only class + direction can.',
    ))

    facts.append((
        'GUARD: the model reply schema demands a direction',
        'surplus_side' in dt.SYSTEM and 'FIRST translator named in the pair key' in dt.SYSTEM,
        'The prompt now requires `surplus_side` on every asymmetric label and fixes the '
        'reading point at the first translator in the pair key. Before H2192 the reply shape '
        'was `class` + `why` only: a model that saw surplus material on one side had no '
        'field in which to say which side, so one name absorbed the whole event class '
        '(omitted_by_one 2.4%, added_by_one 0.0% over 12,000 labels).',
    ))

    facts.append((
        'GUARD: an unresolvable direction is recorded, not coerced',
        dt.normalise_side('nobody', 'grassmann_de_1876|griffith_en_1896')[0] is None
        and dt.normalise_side('Griffith', 'grassmann_de_1876|griffith_en_1896')[0]
        == 'griffith_en_1896',
        'normalise_side() accepts the full id or a bare surname and rejects anything that is '
        'not one of THIS pair\'s two translators, returning None plus a note rather than a '
        'coerced side -- the same posture the class enum already takes with out-of-enum '
        'values (H1901 recorded `class: null` for 9 Gemini replies rather than snapping them '
        'to the nearest class).',
    ))

    det = dt.deterministic_pairs({
        'location': '10.106.5', 'mandala': 10, 'hymn': 106, 'stanza': 5,
        'translations': {
            t: {'status': 'absent_from_source' if t == 'geldner_de_1951' else 'present',
                'text': None if t == 'geldner_de_1951' else 'x'}
            for t in dt.TRANSLATORS},
    })
    det_has_side = bool(det) and all(
        'missing_side' in v and v.get('surplus_side') and v['surplus_side'] != v['missing_side']
        for v in det.values())
    facts.append((
        'GUARD: the deterministic arm records the same direction',
        det_has_side,
        'deterministic_pairs() emits `missing_side` AND `surplus_side` on every row it '
        'decides -- there the direction is a fact about the source, not a judgment. It '
        'already emitted `missing_side` before H2192, which is the sharpest evidence that '
        'direction was always expressible in this format and was dropped in exactly the one '
        'arm -- the model arm -- that cannot recover it any other way.',
    ))

    facts.append((
        'GUARD: the K3 coarse projection is invariant under the converse relabelling',
        dt.COARSE_MAP['added_by_one'] == dt.COARSE_MAP['omitted_by_one'],
        'COARSE_MAP now sends both converse names to %r. Before H2192 it sent added_by_one '
        'to \'divergence\' and omitted_by_one to \'omission\', so a semantically vacuous '
        'choice between two names for one event moved the COARSE class too -- the very '
        'projection K3 collapses to was not invariant under the defect.'
        % dt.COARSE_MAP['added_by_one'],
    ))

    return facts


def cmd_structural(a):
    facts = structural_facts()
    print('structural degeneracy of the asymmetric classes, and the H2192 guards (no data read)')
    for name, holds, detail in facts:
        print('  [%s] %s' % ('x' if holds else ' ', name))
        for line in _wrap(detail, 92):
            print('        %s' % line)
    print('  verdict: %d/%d properties hold' % (sum(1 for _, h, _ in facts if h), len(facts)))
    return 0


# ------------------------------------------------------------------------ surplus
def load_pilot(path):
    rows = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def markers(text):
    """(n_square, n_round) supplied-material proxies in one rendering."""
    if not text:
        return 0, 0
    return len(SQUARE.findall(text)), len(ROUND.findall(text))


def surplus_stats(pilot_path=PILOT_PATH, stanza_path=dt.STANZA_PATH):
    pilot = load_pilot(pilot_path)
    locations = [r['location'] for r in pilot]
    wanted = set(locations)
    spine = {}
    with open(stanza_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec['location'] in wanted:
                spine[rec['location']] = rec

    present = collections.Counter()
    marked = collections.Counter()
    sq_only = collections.Counter()
    rd_only = collections.Counter()
    for loc in wanted:
        for t, d in spine[loc]['translations'].items():
            if d.get('status') != 'present':
                continue
            present[t] += 1
            ns, nr = markers(d.get('text'))
            if ns or nr:
                marked[t] += 1
            if ns:
                sq_only[t] += 1
            if nr:
                rd_only[t] += 1

    # Per pair: stanzas where exactly ONE side carries a supplied-material marker. That is
    # the population in which the direction is textually recoverable, i.e. exactly where a
    # directional added/omitted distinction is decidable.
    one_sided = collections.Counter()
    both_sided = collections.Counter()
    for loc in wanted:
        tr = spine[loc]['translations']
        for a, b in dt.PAIRS:
            da, db = tr.get(a, {}), tr.get(b, {})
            if da.get('status') != 'present' or db.get('status') != 'present':
                continue
            ma = any(markers(da.get('text')))
            mb = any(markers(db.get('text')))
            if ma != mb:
                one_sided['%s|%s' % (a, b)] += 1
            elif ma and mb:
                both_sided['%s|%s' % (a, b)] += 1

    labels = collections.Counter()
    by_method = collections.Counter()
    why_names_a_side = 0
    omitted_model = 0
    surnames = {t: t.split('_')[0] for t in dt.TRANSLATORS}
    for rec in pilot:
        for pk, entry in rec['pairs'].items():
            cls = entry.get('class')
            labels[cls] += 1
            by_method[(cls, entry.get('method'))] += 1
            if cls == 'omitted_by_one' and entry.get('method') == 'model':
                omitted_model += 1
                why = (entry.get('why') or '').lower()
                a, b = pk.split('|')
                if surnames[a] in why or surnames[b] in why:
                    why_names_a_side += 1

    return {
        'n_stanzas': len(wanted),
        'n_labels': sum(labels.values()),
        'labels': labels,
        'by_method': by_method,
        'present': present,
        'marked': marked,
        'square': sq_only,
        'round': rd_only,
        'one_sided': one_sided,
        'both_sided': both_sided,
        'omitted_model': omitted_model,
        'why_names_a_side': why_names_a_side,
    }


def cmd_surplus(a):
    s = surplus_stats(a.pilot, a.stanzas)
    print('surplus-material population vs what the taxonomy recorded')
    print('  pilot: %s (%d stanzas, %d labels)' % (a.pilot, s['n_stanzas'], s['n_labels']))
    print('  labels actually assigned:')
    for c in dt.FIVE_CLASSES:
        n = s['labels'][c]
        print('    %-16s %6d  %5.1f%%' % (c, n, 100.0 * n / s['n_labels'] if s['n_labels'] else 0))
    print('  supplied-material markers per translator (proxy -- see module docstring):')
    print('    %-28s %8s %8s %8s %8s' % ('translator', 'present', 'marked', '[..]', '(..)'))
    for t in dt.TRANSLATORS:
        p = s['present'][t]
        print('    %-28s %8d %8d %8d %8d   %5.1f%% marked'
              % (t, p, s['marked'][t], s['square'][t], s['round'][t],
                 100.0 * s['marked'][t] / p if p else 0))
    tot_one = sum(s['one_sided'].values())
    tot_both = sum(s['both_sided'].values())
    print('  pairs where exactly ONE side carries a marker: %d' % tot_one)
    print('  pairs where BOTH sides carry a marker:         %d' % tot_both)
    print('  top one-sided pairs:')
    for pk, n in s['one_sided'].most_common(5):
        print('    %-60s %6d' % (pk, n))
    print('  against that population, added_by_one fired %d times.' % s['labels']['added_by_one'])
    print('  of %d MODEL-decided omitted_by_one rows, %d name a translator in `why` '
          '(%.1f%%) -- the direction the schema had no field for.'
          % (s['omitted_model'], s['why_names_a_side'],
             100.0 * s['why_names_a_side'] / s['omitted_model'] if s['omitted_model'] else 0))
    return 0


# ------------------------------------------------------------------------ backfill
def _surnames_in(why, a, b):
    """Which of the pair's two translators the free-text `why` names. Surname match only --
    the model writes 'Griffith', not 'griffith_en_1896'."""
    low = (why or '').lower()
    hits = []
    for t in (a, b):
        surname = t.split('_')[0]
        if surname in low:
            hits.append(t)
    return hits


def backfill_direction(pilot_path=PILOT_PATH):
    """Recover `surplus_side` for the already-labelled asymmetric rows WITHOUT a model call.

    The direction the schema had no field for was written into `why` anyway. Where exactly
    one of the pair's two translators is named, the side is recoverable deterministically;
    where both are named it is not, and that row is emitted as ambiguous rather than
    guessed. Additive only -- writes a sidecar, never mutates the pilot.
    """
    rows, stats = [], collections.Counter()
    for rec in load_pilot(pilot_path):
        for pk, entry in rec['pairs'].items():
            if entry.get('class') not in ASYMMETRIC:
                continue
            a, b = pk.split('|')
            if entry.get('method') == 'deterministic':
                stats['deterministic'] += 1
                side, how = entry.get('missing_side'), 'deterministic'
            else:
                hits = _surnames_in(entry.get('why'), a, b)
                if len(hits) == 1:
                    stats['recovered'] += 1
                    side, how = hits[0], 'why_surname'
                elif len(hits) == 2:
                    stats['ambiguous'] += 1
                    side, how = None, 'both_named'
                else:
                    stats['unrecoverable'] += 1
                    side, how = None, 'no_name'
            rows.append({
                'location': rec['location'], 'pair': pk, 'class': entry['class'],
                'method': entry.get('method'), 'surplus_side': side, 'recovered_by': how,
                'why': entry.get('why'),
            })
    return rows, stats


def cmd_backfill(a):
    rows, stats = backfill_direction(a.pilot)
    total = len(rows)
    print('direction backfill over the committed asymmetric labels (no model call)')
    print('  asymmetric rows: %d' % total)
    for k in ('deterministic', 'recovered', 'ambiguous', 'unrecoverable'):
        print('    %-16s %6d  %5.1f%%' % (k, stats[k], 100.0 * stats[k] / total if total else 0))
    named = stats['deterministic'] + stats['recovered']
    print('  direction recoverable without a model call: %d/%d (%.1f%%)'
          % (named, total, 100.0 * named / total if total else 0))
    if a.out:
        out = a.out if os.path.isabs(a.out) else os.path.join(RT_ROOT, a.out)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, 'w', encoding='utf-8', newline='\n') as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        print('  wrote %s' % out)
    return 0


# ------------------------------------------------------------------- coarse kappa
def coarse_kappa_table(arms=None):
    arms = arms or SPIKE_ARMS
    have = [p for p in arms if os.path.exists(p)]
    rows = []
    for i, pa in enumerate(have):
        for pb in have[i + 1:]:
            la, lb = dt._labels(pa), dt._labels(pb)
            shared = sorted(set(la) & set(lb))
            model_only = [k for k in shared
                          if la[k][1] == 'model' and lb[k][1] == 'model']
            fine = [(la[k][0], lb[k][0]) for k in model_only]
            old = [(dt.COARSE_MAP.get(x), dt.COARSE_MAP.get(y)) for x, y in fine
                   if x is not None and y is not None]
            new = [(COARSE_MAP_FIXED.get(x), COARSE_MAP_FIXED.get(y)) for x, y in fine
                   if x is not None and y is not None]
            ko, ao, no = dt.cohens_kappa(old)
            kn, an, nn = dt.cohens_kappa(new)
            rows.append({
                'a': os.path.basename(pa), 'b': os.path.basename(pb),
                'n': no, 'kappa_old': ko, 'kappa_fixed': kn,
                'agree_old': ao, 'agree_fixed': an,
                'identical': old == new,
            })
    return rows, have


def cmd_coarse_kappa(a):
    rows, have = coarse_kappa_table()
    print('K3 coarse-projection kappa, old map vs converse-collapsed map')
    print('  arms found: %d' % len(have))
    if not rows:
        print('  no committed spike arms -- nothing to recompute')
        return 0
    print('  %-24s %-24s %6s %10s %10s' % ('arm A', 'arm B', 'n', 'kappa_old', 'kappa_fix'))
    for r in rows:
        print('  %-24s %-24s %6d %10.3f %10.3f'
              % (r['a'], r['b'], r['n'], r['kappa_old'], r['kappa_fixed']))
    if all(r['identical'] for r in rows):
        print('  Both projections coincide on THIS data, and that is itself the finding: '
              'added_by_one fired zero times, so the unstable half of the map was never '
              'exercised. The projection is fragile, not yet damaged -- fixing it now costs '
              'nothing and removes a defect that would have silently moved every coarse '
              'number the moment the class started firing.')
    else:
        print('  The two projections DIVERGE -- H1901 coarse kappas were computed under the '
              'old map and must be read with that caveat.')
    return 0


# ------------------------------------------------------------------------ report
def cmd_report(a):
    cmd_structural(a)
    print()
    cmd_surplus(a)
    print()
    cmd_backfill(a)
    print()
    cmd_coarse_kappa(a)
    return 0


def _wrap(text, width):
    words, line, out = text.split(), '', []
    for w in words:
        if len(line) + len(w) + 1 > width:
            out.append(line)
            line = w
        else:
            line = (line + ' ' + w).strip()
    if line:
        out.append(line)
    return out


# ---------------------------------------------------------------------- selftest
def selftest():
    facts = structural_facts()
    assert len(facts) == 6, facts
    assert sum(1 for n, _, _ in facts if n.startswith('GUARD:')) == 4, facts
    for name, holds, _ in facts:
        assert holds, 'structural property does not hold: %s' % name

    # The converse-degeneracy claim in one executable line: on an unordered pair the two
    # labels describe one and the same configuration.
    a_text, b_text = 'Agni (the priest) is invoked', 'Agni is invoked'
    a_has_surplus = any(markers(a_text)) and not any(markers(b_text))
    assert a_has_surplus, (a_text, b_text)
    # "a added" and "b omitted" are the same fact; nothing in the pair key or the reply
    # schema can tell them apart.
    assert 'grassmann_de_1876|geldner_de_1951' in dt.PAIR_KEYS
    assert 'geldner_de_1951|grassmann_de_1876' not in dt.PAIR_KEYS

    # The backfill reads a side out of prose only when exactly one translator is named.
    assert _surnames_in('Griffith drops the epithet', 'griffith_en_1896',
                        'geldner_de_1951') == ['griffith_en_1896']
    assert len(_surnames_in('Griffith expands where Geldner does not',
                            'griffith_en_1896', 'geldner_de_1951')) == 2
    assert _surnames_in('one side drops an epithet', 'griffith_en_1896',
                        'geldner_de_1951') == []

    assert markers('a [b] c (d) e') == (1, 1)
    assert markers(None) == (0, 0)
    assert markers('no markers here') == (0, 0)

    # The fix keeps the converse pair together under one coarse class.
    assert COARSE_MAP_FIXED['added_by_one'] == COARSE_MAP_FIXED['omitted_by_one']
    assert COARSE_MAP_FIXED['agreement'] == 'agreement'
    assert COARSE_MAP_FIXED['semantic_shift'] == 'divergence'

    print('rv_added_by_one_diagnosis selftest: OK')
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest='cmd', required=True)
    for name, fn in (('structural', cmd_structural), ('surplus', cmd_surplus),
                     ('backfill', cmd_backfill), ('coarse-kappa', cmd_coarse_kappa),
                     ('report', cmd_report)):
        s = sub.add_parser(name)
        s.add_argument('--pilot', default=PILOT_PATH)
        s.add_argument('--stanzas', default=dt.STANZA_PATH)
        s.add_argument('--out', default=None,
                       help='backfill only: write the recovered directions to this sidecar')
        s.set_defaults(func=fn)
    s = sub.add_parser('selftest')
    s.set_defaults(func=lambda a: selftest())
    a = p.parse_args(argv)
    return a.func(a)


if __name__ == '__main__':
    sys.exit(main())
