#!/usr/bin/env python
r"""repair_h178_da_cards.py -- repair + re-promote the 3 cards the H178 DA sheet REJECTED.

Register: RussianTranslation/pwg_ru/H178_DA_VOTE_ISSUE_REGISTER_2026-07-19.md, rows N16/N17/N19.
This edits the CANONICAL store in place (never the 26 MB file by hand), keeping the repaired
text in the exact `key1|subcard` slot the DA sheet was generated from so the V2 regen picks it
up (register §6 item 4). review_status stays at the promoted-store value ('ai_translated') --
repairing in place IS the "re-promote" the register's contract requires.

Each of the 3 rows is:
  N16  nI |n_i~~h0_13_apa    |5)  -- prose *zu* in "Schol. zu ŚĀK. 14." -> «к»
  N19  DA |_d_a~~h0_81_a_bisam|8   -- *mit Ergänzung von* -> «с восполнением»
  N17  gam|gam~~h0_42_prod   |1   -- DE 1 word {%hervorragen%} rendered as a RU doublet;
                                     shrink to the single attested equivalent «возвышаться»
                                     (KATHĀS. 26,9 not in any local TM -> citation check
                                     DEFERRED to H1304; see the report).

Idempotent: a text fix is applied only if the German residue is still present (so it is a
no-op after fix_german_connectives.py --store has already run for N16/N19); the provenance
repair note is added once per (row, handoff).

  python src/pilot/repair_h178_da_cards.py [--dry-run]
"""
import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
for p in (SRC, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)
from store_path import canonical_store  # noqa: E402

HANDOFF = 'H1302'
DATE = '2026-07-19'
REASON = 'h178_da reject'

# (key1, subcard, sense_tag): list of (old_substring, new_substring) text repairs + a note.
REPAIRS = {
    ('nI', 'n_i~~h0_13_apa', '5)'): {
        'subs': [('<ab>Schol.</ab> zu <ls>ŚĀK. 14.</ls>', '<ab>Schol.</ab> к <ls>ŚĀK. 14.</ls>')],
        'note': 'German prose "zu" ("Schol. zu ŚĀK. 14.") -> «к» (register N16).',
    },
    ('DA', '_d_a~~h0_81_a_bisam', '8'): {
        'subs': [('mit Ergänzung von', 'с восполнением')],
        'note': 'German prose "mit Ergänzung von" -> «с восполнением» (register N19).',
    },
    ('gam', 'gam~~h0_42_prod', '1'): {
        'subs': [('{%выступать, возвышаться над окружающим%}', '{%возвышаться%}')],
        'note': ('DE 1 word {%hervorragen%} was rendered as a RU doublet; shrunk to the single '
                 'attested equivalent «возвышаться» (register N17). KATHĀS. 26,9 is absent from '
                 'every local TM (corpus_lexicon.jsonl not on disk; aligned_works.txt lists no '
                 'Kathāsaritsāgara) -> citation-translation check DEFERRED to H1304.'),
    },
}


def repair_row(r):
    key = (r.get('key1'), r.get('subcard'), r.get('sense_tag'))
    spec = REPAIRS.get(key)
    if not spec:
        return 0
    changed = 0
    ru = r.get('ru', '') or ''
    for old, new in spec['subs']:
        if old in ru:
            ru = ru.replace(old, new)
            changed += 1
        elif new not in ru:
            print('  WARN %s|%s|%s: neither old nor new text present -- verify manually'
                  % key, file=sys.stderr)
    r['ru'] = ru
    prov = r.setdefault('provenance', {})
    repairs = prov.setdefault('repairs', [])
    if not any(x.get('handoff') == HANDOFF and x.get('note') == spec['note'] for x in repairs):
        repairs.append({'handoff': HANDOFF, 'date': DATE, 'reason': REASON, 'note': spec['note']})
        changed += 1
    return changed


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    store = canonical_store(os.path.join(SRC, 'pwg_ru_translated.jsonl'))
    if not os.path.exists(store):
        sys.exit('STORE ABSENT: %s' % store)
    rows = []
    with open(store, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if line:
                rows.append(json.loads(line))
    found, total_changes = set(), 0
    for r in rows:
        key = (r.get('key1'), r.get('subcard'), r.get('sense_tag'))
        if key in REPAIRS:
            found.add(key)
            c = repair_row(r)
            total_changes += c
            print('repaired %s|%s|%s (%d edits) -- ru now: %s'
                  % (key[0], key[1], key[2], c, (r['ru'][:120] + '…') if len(r['ru']) > 120 else r['ru']))
    missing = set(REPAIRS) - found
    if missing:
        for m in missing:
            print('  MISSING ROW: %s' % (m,), file=sys.stderr)
        sys.exit('ERROR: %d target row(s) not found in store' % len(missing))
    print('cards repaired : %d | edits : %d%s' % (len(found), total_changes,
                                                  ' (DRY RUN)' if a.dry_run else ''))
    if not a.dry_run and total_changes:
        bak = store + '.h1302.bak'
        if not os.path.exists(bak):
            import shutil
            shutil.copyfile(store, bak)
            print('backup : %s' % bak)
        tmp = store + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        os.replace(tmp, store)
        print('wrote  : %s' % store)


if __name__ == '__main__':
    main()
