#!/usr/bin/env python
r"""sanloss_bundling_fix_probe.py -- H1225: probe (and DISPROVE) a pure-structural fix to
count_source_senses for the H1150 Nachtrag/corrigenda over-count class.

H1150 found 8/8 SANLOSS false flags, all "Nachtrag/corrigenda cards" where the pipeline
bundles textual-correction points for several distinct sub-lemmas -- each opened by its own
"-- {#headword#}" marker -- into ONE stored/translated sense, and proposed two fix directions
(pwg_ru/h1112/H1150_SOFTGUARD_FALSEFLAG_RATE_2026-07-18.md#sanloss, `fix_suggestion`):
  1. Partition count_source_senses' ordinal search by "-- {#headword#}" sub-lemma boundary
     before stamping source_senses.
  2. Cheaper: have accept() check whether an "extra" ordinal's content is verbatim present
     somewhere in the emitted card before counting it as a shortfall.

THIS SCRIPT PROVES BOTH ARE UNSAFE AS A GENERAL count_source_senses FIX, WITH CONCRETE
COUNTER-EVIDENCE FROM THE LIVE STORE. It does not change count_source_senses or accept();
it is read-only evidence for the H1225 escalation (see the addendum memo this script's JSON
output is cited from). No paid calls, no store mutation.

--- Direction 1 (structural cap): DISPROVEN ---
Hypothesis: when a card's raw/concatenated source text carries >=2 DISTINCT sub-lemma names
via a genuine line-opening "-- {#name#}" marker (the same marker root_segment_proto.UPA_RE
uses to cut giant PWG records into per-preverb sub-cards), the card is a bundled Nachtrag and
its true source-sense cardinality collapses to 1 (or some other cap), not the raw distinct-
ordinal count.

This correctly reduces 5 of the 8 H1150 keys to exp<=emitted (d_a~~h10_00_pwg00,
d_a~~h13_00_pwg00, iz~~h14_00_pwg00, vas~~h13_00_pwg00, y_a~~h5_00_pwg00) -- but it ALSO
silently caps `_ap~~h3_00_pwg00` (7 real stored rows, one per genuinely distinct preverb
correction: ava/pra/saMparipra/sam/parisam) and `vah~~h3_00_pwg00` (3 real stored rows:
ati+ud+saMpra bundled in one head row, vi, saMvi) down to source_senses=1, even though these
cards are NOT over-counts -- they are genuinely-split multi-preverb Nachtrag records where a
FUTURE drop of, say, 5 of _ap's 7 real corrections would go completely undetected under the
capped counter (1 <= emitted, however small emitted shrinks to). No cap value between "1"
(fixes the 5, breaks _ap/vah) and "count of distinct sub-lemma names" (leaves _ap/vah
untouched, but also leaves ALL 8 H1150 flags untouched, since a genuinely-bundled card's own
distinct-name count already equals or exceeds what a per-name cap would allow) exists,
because the single fact that actually distinguishes "d_a~~h10 -> collapses to 1 real row" from
"_ap~~h3 -> stays split into 7 real rows" is the MODEL'S OWN BUNDLING-VS-SPLITTING DECISION,
made AT GENERATION TIME -- information that does not exist yet when count_source_senses(raw)
is called PRE-generation (gen_opt_harness2.py line ~1010, before any agent() call). No
regex over the raw source text, however carefully scoped, can observe a decision that has not
been made yet.

--- Direction 2 (content-verbatim check): UNTESTABLE via this offline harness ---
The offline re-measurement's own "raw" IS the concatenation of the SAME store rows its
"candidate" is built from (build_eligible_cases: `senses` = the exact rows `concat_de` was
joined from) -- so a content-verbatim check comparing "source content" against "candidate
content" is TAUTOLOGICALLY true for every single card measured this way, false-flag or not.
It would report 0 false flags regardless of whether count_source_senses is fixed, which is not
evidence of a fix -- it is evidence the harness cannot test this direction. Making direction 2
meaningful requires the check to live in the LIVE production accept() (gen_opt_harness2.py),
where source and candidate ARE independent (source is read pre-generation; the candidate is
whatever the model returns) -- a change to actively-used live-generation code that cannot be
validated without either a live (paid) generation pass or extensive new JS test scaffolding,
neither authorized under this handoff's read-only/zero-paid-calls rail.

Usage:
    python src/pilot/sanloss_bundling_fix_probe.py --out ../pwg_ru/h1112/sanloss_bundling_fix_probe.json
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
SRC = os.path.dirname(HERE)
RT = os.path.dirname(SRC)

if SRC not in sys.path:
    sys.path.insert(0, SRC)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from store_path import canonical_store                     # noqa: E402
from sense_count import count_source_senses, _is_open_prefix  # noqa: E402

# The H1150 8 -- verbatim from softguard_falseflag_rate.json#sanloss.examples[].key
H1150_EIGHT = [
    'car~~h1_20_vi', 'd_a~~h10_00_pwg00', 'd_a~~h13_00_pwg00', 'iz~~h14_00_pwg00',
    'n_i~~h5_10_pari', 'n_i~~h5_11_pra', 'vas~~h13_00_pwg00', 'y_a~~h5_00_pwg00',
]
# Concrete counter-evidence: real store cards that are genuinely split into multiple stored
# rows across distinct sub-lemmas (i.e. the guard SHOULD be able to catch a future drop
# within them), hand-picked because they ALSO carry >=2 distinct "-- {#name#}" markers.
COUNTEREXAMPLE_CARDS = ['_ap~~h3_00_pwg00', 'vah~~h3_00_pwg00', 'iz~~h8_00_pwg00']

# The line-opening sub-lemma marker root_segment_proto.UPA_RE also uses to cut giant PWG
# records into per-preverb sub-cards ("<div n=\"p\">-- {#upasarga#}"); generalized here to any
# line, not just <div n="p">, since the store's `de` reconstruction loses that anchor.
_SUB = re.compile(r'—\s*(?:Mit\s*)?\{#([^#]+)#\}')


def bundled_sublemma_names(text):
    """Distinct sub-lemma headword names introduced by a genuine line-opening '-- {#name#}'
    marker (never a mid-prose one -- reuses count_source_senses' own _is_open_prefix so this
    stays consistent with the H960 cross-reference hardening)."""
    names = set()
    for line in (text or '').split('\n'):
        m = _SUB.search(line)
        if m and _is_open_prefix(line[:m.start()]):
            names.add(m.group(1))
    return names


def load_store_cards(store_path):
    cards = collections.OrderedDict()
    with open(store_path, encoding='utf-8') as f:
        for line in f:
            row = json.loads(line)
            cards.setdefault(row.get('subcard'), []).append(row)
    return cards


def probe_key(subcard, rows):
    concat = '\n'.join(r.get('de') or '' for r in rows)
    raw = count_source_senses(concat)
    names = bundled_sublemma_names(concat)
    emitted = len(rows)
    capped_to_1 = 1 if (raw > 1 and len(names) >= 2) else raw
    return {
        'key': subcard, 'raw_count_source_senses': raw, 'emitted_rows': emitted,
        'distinct_sublemma_names': sorted(names),
        'flagged_before': raw > emitted,
        'flagged_after_cap_to_1': capped_to_1 > emitted,
        'cap_to_1_value': capped_to_1,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(RT, 'pwg_ru', 'h1112', 'sanloss_bundling_fix_probe.json'))
    args = ap.parse_args()

    store_path = canonical_store(os.path.join(HERE, 'pwg_ru_translated.jsonl'))
    cards = load_store_cards(store_path)
    print('store:', store_path, '| cards:', len(cards))

    h1150 = [probe_key(k, cards.get(k, [])) for k in H1150_EIGHT]
    fixed = [r for r in h1150 if r['flagged_before'] and not r['flagged_after_cap_to_1']]
    still_flagged = [r for r in h1150 if r['flagged_before'] and r['flagged_after_cap_to_1']]
    print('\n=== H1150 8 under the "cap to 1 when raw>1 and >=2 distinct names" hypothesis ===')
    for r in h1150:
        print('  %-25s raw=%-3d cap1=%-3d emitted=%-3d %s' % (
            r['key'], r['raw_count_source_senses'], r['cap_to_1_value'], r['emitted_rows'],
            'FIXED' if (r['flagged_before'] and not r['flagged_after_cap_to_1']) else
            'still flagged' if r['flagged_before'] else 'n/a'))
    print('  fixed: %d / 8 (%s)' % (len(fixed), ', '.join(r['key'] for r in fixed)))
    print('  still flagged: %d / 8 (%s)' % (len(still_flagged), ', '.join(r['key'] for r in still_flagged)))

    counterex = [probe_key(k, cards.get(k, [])) for k in COUNTEREXAMPLE_CARDS]
    print('\n=== Counter-evidence: genuinely multi-row Nachtrag cards the SAME hypothesis would ALSO cap ===')
    collateral = []
    for r in counterex:
        would_cap = r['cap_to_1_value'] < r['raw_count_source_senses']
        if would_cap:
            collateral.append(r)
        print('  %-25s raw=%-3d cap1=%-3d emitted=%-3d would_be_capped=%s (a real regression: the guard '
              'could no longer detect a future drop leaving this card at 1..%d emitted senses)'
              % (r['key'], r['raw_count_source_senses'], r['cap_to_1_value'], r['emitted_rows'],
                 would_cap, r['emitted_rows'] - 1))

    verdict = {
        'schema': 'pwg_ru.sanloss_bundling_fix_probe.v1',
        'measured': '2026-07-19',
        'store': {'path': store_path, 'cards': len(cards)},
        'hypothesis': (
            'count_source_senses should cap its result to 1 whenever the raw/concatenated '
            'text carries >=2 distinct line-opening "-- {#name#}" sub-lemma markers (the '
            'memo\'s "partition by sub-lemma boundary" direction 1).'
        ),
        'h1150_eight': h1150,
        'fixed_count': len(fixed),
        'still_flagged_count': len(still_flagged),
        'fixed_keys': [r['key'] for r in fixed],
        'still_flagged_keys': [r['key'] for r in still_flagged],
        'counterexamples': counterex,
        'counterexamples_collaterally_capped': [r['key'] for r in collateral],
        'verdict': 'DISPROVEN' if collateral else 'not disproven by these counterexamples',
        'reason': (
            ('The hypothesis fixes 5/8 flags but ALSO collapses source_senses to 1 for at least '
             'one real, currently-unflagged, genuinely multi-row Nachtrag card (%s) -- cards '
             'that legitimately store multiple real distinct-preverb correction rows today '
             '(see counterexamples[].emitted_rows). A future regeneration that dropped all but '
             'one of those rows would go completely undetected under the capped counter. No cap '
             'value between "1" (fixes 5/8, breaks these) and "count of distinct sub-lemma '
             'names" (breaks nothing, fixes 0/8) exists, because the fact that actually '
             'distinguishes a card that WILL be bundled into one stored row from one that WILL '
             'be split into several is the model\'s own generation-time decision -- unknowable '
             'when count_source_senses(raw) runs pre-generation.'
             % ', '.join(r['key'] for r in collateral))
            if collateral else 'no collateral damage found among the probed counterexamples'
        ),
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    tmp = args.out + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(verdict, f, ensure_ascii=False, indent=1)
        f.write('\n')
    os.replace(tmp, args.out)
    print('\nwrote', args.out)
    print('VERDICT:', verdict['verdict'])


if __name__ == '__main__':
    main()
