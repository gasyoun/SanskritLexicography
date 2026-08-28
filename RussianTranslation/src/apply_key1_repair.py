#!/usr/bin/env python
r"""H2996 — apply the key1/wrong-entry repair proposals to the pwg_ru store.

Input is the WHOLE of ``pwg_ru/key1_repair_proposals.jsonl`` (56 proposals,
161 store rows), produced by ``key1_repair_proposals.py`` and ruled
machine-resolvable by MG on 17-08-2026: the vote sheet
``key1_repair_vote_2026-08-17.html`` was WITHDRAWN because the printed
head of each card decides the case and "leave as is" is not a coherent
option. The authority here is therefore the printed source, not a
``decisions.json`` (FINDINGS §562).

What the defect is: the ingest went after an intended lemma (preserved in
the subcard prefix — ``aDvan``, ``vAsA``, ``BAra``…) but fetched the
FLATTENED look-alike entry (``advan``, ``vasa``, ``bara``…) and stored that
entry's content under the intended lemma's subcard. Where one flattened key
covered several intended lemmas, the same wrong card was stored verbatim
once per lemma — so the real PWG articles of ~60 lemmas are MISSING from
the store.

Two actions, one per class:

  quarantine + re-ingest   ``wrong_entry`` / ``wrong_entry_xref`` /
                           ``wrong_entry_dup`` — the stored content belongs
                           to a DIFFERENT article. Its rows leave the store
                           into a quarantine JSONL (evidence retained, never
                           deleted) and the intended lemma is parked in a
                           re-ingest worklist. This script never writes a
                           translation: re-ingest runs through the standard
                           pipeline, and a paid window needs a live-gate GO.

  key fix                  ``junk_key1`` — ``key1`` carries whole subcard
                           machinery (``durg_a~~h0_zz_sch``) while the card's
                           printed head IS the intended lemma, i.e. the
                           content is CORRECT and only the key is malformed.
                           Quarantining it would destroy a sound translation
                           and queue a re-ingest that cannot succeed: the
                           card is ``sch`` layer (Schmidt Nachträge) and has
                           no PWG record to re-ingest from. So this class is
                           repaired in place, exactly as the proposal's own
                           ``action`` field prescribes.

Every card must clear a printed-source gate before it is touched; a card
that fails is DEFERRED with a one-line reason and left untouched (handoff
step 4 — never batch an ambiguity into a vote):

  * quarantine classes need the stored head to print the FETCHED lemma and
    NOT the intended one — that is the whole evidence of wrong-entry ingest;
  * the key-fix class needs the head to print the INTENDED lemma;
  * a card whose live row count disagrees with the proposal's
    ``rows_affected`` is stale against the store;
  * a human-touched row (``promote_final_cards.human_touched``) is never
    removed — reverting machine output must not delete a human ruling
    (H2146 / FINDINGS §513).

Outputs (all committed; the store itself stays gitignored):

  reports/pwg_ru_wrong_entry_quarantine.jsonl        the quarantined rows
  reports/H2996_key1_repair_apply_ledger.jsonl       one event per proposal
  pwg_ru/H2996_WRONG_ENTRY_REINGEST_WORKLIST_<date>.jsonl   re-ingest units
  pwg_ru/H2996_WRONG_ENTRY_REINGEST_ROOTS_<date>.txt        unique lemmas

Dry-run by default; ``--write`` mutates the store through
``store_write.locked_store_rewrite`` (the one sanctioned path for a
non-promote mutator: PromoteClaim held across the window, unique fsynced
backup, atomic replace).

  python src/apply_key1_repair.py --selftest
  python src/apply_key1_repair.py                 # dry-run report
  python src/apply_key1_repair.py --write
"""
import argparse
import json
import os
import sys
from collections import OrderedDict, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from store_path import canonical_store                          # noqa: E402
import store_write                                              # noqa: E402
from key1_repair_proposals import decode_subcard, de_head_lemma  # noqa: E402
from promote_final_cards import human_touched                   # noqa: E402

DATE = '2026-08-28'
PROPOSALS = os.path.join(REPO, 'pwg_ru', 'key1_repair_proposals.jsonl')
QUARANTINE = os.path.join(REPO, 'reports', 'pwg_ru_wrong_entry_quarantine.jsonl')
LEDGER = os.path.join(REPO, 'reports', 'H2996_key1_repair_apply_ledger.jsonl')
WORKLIST = os.path.join(REPO, 'pwg_ru',
                        'H2996_WRONG_ENTRY_REINGEST_WORKLIST_%s.jsonl' % DATE)
ROOTS = os.path.join(REPO, 'pwg_ru',
                     'H2996_WRONG_ENTRY_REINGEST_ROOTS_%s.txt' % DATE)

QUARANTINE_CLASSES = ('wrong_entry', 'wrong_entry_xref', 'wrong_entry_dup')
KEY_FIX_CLASSES = ('junk_key1',)
WORKLIST_SCHEMA = 'pwg_ru.wrong_entry_reingest_worklist.v1'
LEDGER_SCHEMA = 'pwg_ru.key1_repair_apply.v1'
STORE_TAG = 'h2996_key1_repair'

# The consumer contract for the worklist. The historical defect was a
# case-flattened lookup, so the worklist carries the exact SLP1 key and says
# so: a consumer must match the PWG <k1> field exactly and must never
# lowercase or otherwise fold the key on the way in.
WORKLIST_NOTE = ('re-ingest the PWG article of this exact SLP1 lemma; match '
                 '<k1> EXACTLY (never case-folded — the flattened lookup is '
                 'the H2996/FINDINGS-562 defect). Translation runs through '
                 'the standard pipeline; a paid window needs a live-gate GO.')


def load_jsonl(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def card_rows(rows_by_key1, proposal):
    """The live store rows this proposal speaks for.

    A proposal names one fetched ``key1`` plus the intended lemmas whose
    subcards carry the wrongly-ingested content, so the rows are those of
    that key1 whose decoded subcard prefix is one of the intended lemmas.
    """
    intended = set(proposal['intended_lemmas'])
    return [r for r in rows_by_key1.get(proposal['key1'], [])
            if decode_subcard(r.get('subcard') or '') in intended]


def heads_of(rows):
    out = []
    for r in rows:
        out.extend(de_head_lemma(r.get('de') or '', r.get('layer')))
    return out


def judge(proposal, rows):
    """Printed-source gate -> (action, reason).

    action is 'quarantine', 'key_fix' or 'defer'; reason is a single line
    naming the evidence either way.
    """
    cls = proposal['class']
    if cls not in QUARANTINE_CLASSES + KEY_FIX_CLASSES:
        return 'defer', 'class %r is not in this pass (proposals-only class)' % cls
    if not rows:
        return 'defer', 'no live store rows carry this proposal any more'
    if len(rows) != proposal.get('rows_affected'):
        return 'defer', ('stale against the store: proposal claims %s rows, %d live'
                         % (proposal.get('rows_affected'), len(rows)))
    touched = [r.get('subcard') for r in rows if human_touched(r)]
    if touched:
        return 'defer', ('a human has ruled on %d of these rows (%s) — machine '
                         'repair never removes a human ruling'
                         % (len(touched), ', '.join(sorted(set(touched))[:3])))

    heads = set(heads_of(rows))
    intended = set(proposal['intended_lemmas'])
    if not heads:
        return 'defer', 'the stored cards print no head — no printed-source authority'

    if cls in KEY_FIX_CLASSES:
        if heads & intended:
            return 'key_fix', ('printed head %s IS the intended lemma: content is '
                               'sound, only key1 is malformed'
                               % sorted(heads & intended))
        return 'defer', ('printed head %s is not the intended lemma %s — a key fix '
                         'would mislabel sound content'
                         % (sorted(heads), sorted(intended)))

    if heads & intended:
        return 'defer', ('the stored card already prints the intended lemma %s — '
                         'quarantining it would destroy the right article'
                         % sorted(heads & intended))
    if proposal['key1'] not in heads:
        return 'defer', ('printed head %s matches neither the fetched key1 %r nor '
                         'the intended lemma — witnesses disagree'
                         % (sorted(heads), proposal['key1']))
    return 'quarantine', ('printed head %s is the FETCHED lemma, not the intended '
                          '%s: wrong-entry ingest'
                          % (sorted(heads), sorted(intended)))


def plan(proposals, rows):
    """Pure planner: returns (events, drop_indices, key_fixes, worklist).

    ``drop_indices`` are store row indices to quarantine; ``key_fixes`` maps a
    row index to its corrected key1; ``worklist`` is the ordered re-ingest
    unit list. Nothing is written here — the same plan drives dry-run and
    ``--write``.
    """
    rows_by_key1 = defaultdict(list)
    index_of = {}
    for i, r in enumerate(rows):
        rows_by_key1[r.get('key1')].append(r)
        index_of[id(r)] = i

    events, drop, fixes = [], {}, {}
    worklist = OrderedDict()
    for p in proposals:
        mine = card_rows(rows_by_key1, p)
        action, reason = judge(p, mine)
        idxs = sorted(index_of[id(r)] for r in mine)
        ev = {
            'schema': LEDGER_SCHEMA, 'handoff': 'H2996', 'date': DATE,
            'id': p['id'], 'class': p['class'], 'key1': p['key1'],
            'intended_lemmas': p['intended_lemmas'],
            'printed_head': p.get('printed_head'),
            'rows_claimed': p.get('rows_affected'), 'rows_live': len(mine),
            'action': action, 'reason': reason,
            'subcards': sorted({r.get('subcard') for r in mine}),
        }
        if action == 'quarantine':
            for i in idxs:
                drop[i] = p
            for lem in p['intended_lemmas']:
                unit = worklist.setdefault(lem, {
                    'schema': WORKLIST_SCHEMA, 'handoff': 'H2996',
                    'worklist_note': WORKLIST_NOTE,
                    'key1': lem, 'layers': p.get('layers') or ['pwg'],
                    'displaced_by': [], 'quarantined_subcards': [],
                    'evidence': 'FINDINGS §562; issue #1767',
                })
                if p['key1'] not in unit['displaced_by']:
                    unit['displaced_by'].append(p['key1'])
                for r in mine:
                    sub = r.get('subcard')
                    if decode_subcard(sub or '') == lem and \
                            sub not in unit['quarantined_subcards']:
                        unit['quarantined_subcards'].append(sub)
        elif action == 'key_fix':
            for i in idxs:
                fixes[i] = p['intended_lemmas'][0]
            ev['key1_after'] = p['intended_lemmas'][0]
        events.append(ev)
    return events, drop, fixes, worklist


def write_jsonl(path, records):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    os.replace(tmp, path)


def run(args):
    store = args.store or canonical_store(os.path.join(HERE, 'pwg_ru_translated.jsonl'))
    if not os.path.exists(store):
        sys.exit('STORE ABSENT: %s' % store)
    rows = load_jsonl(store)
    proposals = load_jsonl(args.proposals)
    events, drop, fixes, worklist = plan(proposals, rows)

    by_action = defaultdict(int)
    for ev in events:
        by_action[ev['action']] += 1
    print('proposals read      : %d' % len(proposals))
    print('store rows before   : %d' % len(rows))
    print('quarantine cards    : %d  (%d rows)' % (by_action['quarantine'], len(drop)))
    print('key-fix cards       : %d  (%d rows)' % (by_action['key_fix'], len(fixes)))
    print('deferred cards      : %d' % by_action['defer'])
    print('re-ingest lemmas    : %d' % len(worklist))
    for ev in events:
        if ev['action'] == 'defer':
            print('  DEFER %s %-16s %s' % (ev['id'], ev['key1'], ev['reason']))

    kept, quarantined = [], []
    for i, r in enumerate(rows):
        if i in drop:
            p = drop[i]
            rec = dict(r)
            rec['_quarantine'] = {
                'handoff': 'H2996', 'date': DATE, 'proposal_id': p['id'],
                'class': p['class'], 'fetched_key1': p['key1'],
                'intended_lemma': decode_subcard(r.get('subcard') or ''),
                'printed_head': p.get('printed_head'),
                'reason': 'wrong-entry ingest: this card is the article of %r, '
                          'stored under the subcard of %r (FINDINGS §562)'
                          % (p['key1'], decode_subcard(r.get('subcard') or '')),
                'disposition': 'evidence retained; the intended lemma is parked '
                               'in the H2996 re-ingest worklist',
            }
            quarantined.append(rec)
            continue
        if i in fixes:
            r = dict(r)
            r['key1'] = fixes[i]
        kept.append(r)

    print('store rows after    : %d  (delta %+d)' % (len(kept), len(kept) - len(rows)))
    if not args.write:
        print('\nDRY-RUN — nothing written. Pass --write to apply.')
        return 0

    write_jsonl(QUARANTINE, quarantined)
    write_jsonl(LEDGER, events)
    write_jsonl(WORKLIST, list(worklist.values()))
    os.makedirs(os.path.dirname(ROOTS), exist_ok=True)
    with open(ROOTS, 'w', encoding='utf-8', newline='\n') as f:
        for lem in worklist:
            f.write(lem + '\n')
    bak = store_write.locked_store_rewrite(store, kept, STORE_TAG)
    print('\nstore rewritten     : %s' % store)
    print('backup              : %s' % bak)
    print('quarantine          : %s (%d rows)' % (QUARANTINE, len(quarantined)))
    print('ledger              : %s (%d events)' % (LEDGER, len(events)))
    print('worklist            : %s (%d lemmas)' % (WORKLIST, len(worklist)))
    print('roots               : %s' % ROOTS)
    return 0


def selftest():
    fails = []

    def check(name, cond):
        if not cond:
            fails.append(name)

    mk = lambda key1, sub, de, **kw: dict(
        {'key1': key1, 'subcard': sub, 'de': de, 'layer': 'pwg',
         'sense_tag': '1', 'review_status': 'ai_translated', 'reviewer': None},
        **kw)

    # 1. a clean wrong_entry: head prints the FETCHED lemma -> quarantine
    rows = [mk('advan', 'a_dvan~~h0_01', '{#advan#}¦ <lex>adj.</lex> essend')]
    p = {'id': 'k1r-001', 'class': 'wrong_entry', 'key1': 'advan',
         'intended_lemmas': ['aDvan'], 'printed_head': ['advan'],
         'rows_affected': 1}
    ev, drop, fix, wl = plan([p], rows)
    check('wrong_entry quarantines', ev[0]['action'] == 'quarantine' and drop == {0: p})
    check('wrong_entry worklist', list(wl) == ['aDvan'])
    check('worklist carries exact key', wl['aDvan']['key1'] == 'aDvan')
    check('no key fix', fix == {})

    # 2. the card already prints the INTENDED lemma -> never quarantine it
    rows = [mk('advan', 'a_dvan~~h0_01', '{#aDvan#}¦ <lex>m.</lex> Weg')]
    ev, drop, fix, wl = plan([p], rows)
    check('right article is spared', ev[0]['action'] == 'defer' and not drop)

    # 3. junk_key1 whose head IS the intended lemma -> in-place key fix, no drop
    rows = [mk('durg_a~~h0_zz_sch', 'durg_a~~h0_zz_sch',
               '{%durgā%}¦ ˚ = {%bilva%}', layer='sch')]
    pj = {'id': 'k1r-011', 'class': 'junk_key1', 'key1': 'durg_a~~h0_zz_sch',
          'intended_lemmas': ['durgA'], 'printed_head': ['durgA'],
          'rows_affected': 1}
    ev, drop, fix, wl = plan([pj], rows)
    check('junk_key1 fixes the key', ev[0]['action'] == 'key_fix' and fix == {0: 'durgA'})
    check('junk_key1 never quarantines', not drop)
    check('junk_key1 never re-ingests', not wl)

    # 4. a human ruling protects the row even when the printed head convicts it
    rows = [mk('advan', 'a_dvan~~h0_01', '{#advan#}¦ adj. essend',
               reviewer='MG', review_status='approved')]
    ev, drop, fix, wl = plan([p], rows)
    check('human ruling protects', ev[0]['action'] == 'defer' and not drop)
    check('human reason names it', 'human has ruled' in ev[0]['reason'])

    # 5. a proposal stale against the store is deferred, not guessed at
    rows = [mk('advan', 'a_dvan~~h0_01', '{#advan#}¦ adj.'),
            mk('advan', 'a_dvan~~h0_02', '{#advan#}¦ adj.')]
    ev, drop, fix, wl = plan([p], rows)      # p claims 1 row, 2 are live
    check('stale proposal deferred', ev[0]['action'] == 'defer' and not drop)

    # 6. a card printing no head has no printed-source authority
    rows = [mk('advan', 'a_dvan~~h0_01', 'kein Kopf hier')]
    ev, drop, fix, wl = plan([p], rows)
    check('headless card deferred', ev[0]['action'] == 'defer' and not drop)

    # 7. wrong_entry_dup: one fetched key, several intended lemmas, all queued
    stub = '{#vasa#}¦ <ab>nom. act.</ab>'
    rows = [mk('vasa', 'v_as_a~~h0_01', stub), mk('vasa', 'va_s_a~~h0_01', stub)]
    pd = {'id': 'k1r-048', 'class': 'wrong_entry_dup', 'key1': 'vasa',
          'intended_lemmas': ['vAsA', 'vaSA'], 'printed_head': ['vasa'],
          'rows_affected': 2}
    ev, drop, fix, wl = plan([pd], rows)
    check('dup quarantines both', ev[0]['action'] == 'quarantine' and len(drop) == 2)
    check('dup queues both lemmas', sorted(wl) == ['vAsA', 'vaSA'])

    # 8. rows outside the proposal's intended lemmas are never touched
    rows = [mk('advan', 'a_dvan~~h0_01', '{#advan#}¦ adj. essend'),
            mk('advan', 'advan~~h0_01', '{#advan#}¦ adj. essend')]
    p1 = dict(p, rows_affected=1)
    ev, drop, fix, wl = plan([p1], rows)
    check('unrelated sibling row survives', drop == {0: p1})

    if fails:
        print('apply_key1_repair selftest: FAIL -> %s' % ', '.join(fails))
        return 1
    print('apply_key1_repair selftest: PASS (8 checks — printed-head gate both '
          'ways, human-ruling fence, stale/headless deferral, dup fan-out, '
          'key-fix never quarantines, sibling rows untouched)')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--store', default=None, help='override the canonical store path')
    ap.add_argument('--proposals', default=PROPOSALS)
    ap.add_argument('--write', action='store_true',
                    help='apply (default: dry-run report only)')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    return run(args)


if __name__ == '__main__':
    sys.exit(main())
