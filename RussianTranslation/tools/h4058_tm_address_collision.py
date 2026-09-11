#!/usr/bin/env python
"""H4058 — does a TM address (ru:input_raw_sha256) identify ONE sense, or a whole entry?

Read-only. For every address shared by 2+ store rows, check whether the rows differ
in (subcard, sense_tag) and in `ru`. Then, for the ten H4056 cards, look each card up
in a hold-out TM (store minus the card row) and compare the returned Russian with
the card's own Russian: a hit that returns ANOTHER sense's translation is a sense
collision, not reuse.
"""
import collections
import json
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(RT, 'src', 'pilot'))
import translation_memory as tm  # noqa: E402

DATA = os.path.normpath(os.path.join(RT, '..', '..', 'pwg-ru-data'))
STORE = os.path.join(DATA, 'tm', 'pwg_ru_translated.jsonl')
MANIFEST = os.path.join(RT, 'reports', 'H4056_evidence_packet_manifest.json')
OUT = os.path.join(RT, 'reports', 'H4058_tm_address_collision.json')


def main():
    rows = [json.loads(l) for l in open(STORE, encoding='utf-8') if l.strip()]
    by_addr = collections.defaultdict(list)
    for r in rows:
        a = (r.get('provenance') or {}).get('input_raw_sha256')
        if a:
            by_addr[a].append(r)
    shared = {a: rs for a, rs in by_addr.items() if len(rs) > 1}
    diff_sense = sum(1 for rs in shared.values()
                     if len({(r.get('subcard'), r.get('sense_tag')) for r in rs}) > 1)
    diff_ru = sum(1 for rs in shared.values() if len({r.get('ru') for r in rs}) > 1)
    diff_key1 = sum(1 for rs in shared.values() if len({r.get('key1') for r in rs}) > 1)
    rows_under_shared = sum(len(rs) for rs in shared.values())
    rep = {'schema': 'h4058-tm-address-collision/v1', 'rows': len(rows),
           'distinct_addresses': len(by_addr), 'shared_addresses': len(shared),
           'rows_under_shared_addresses': rows_under_shared,
           'shared_addresses_with_differing_sense_identity': diff_sense,
           'shared_addresses_with_differing_ru': diff_ru,
           'shared_addresses_with_differing_key1': diff_key1,
           'max_rows_per_address': max(len(rs) for rs in by_addr.values())}

    man = json.load(open(MANIFEST, encoding='utf-8'))
    idx = {(r.get('subcard'), r.get('sense_tag')): r for r in rows}
    scratch = tempfile.mkdtemp(prefix='h4058_coll_')
    cards = []
    for c in man['cards']:
        r = idx[(c['subcard'], c['sense_tag'])]
        hold = os.path.join(scratch, 'hold.jsonl')
        with open(hold, 'w', encoding='utf-8') as f:
            for x in rows:
                if (x.get('subcard'), x.get('sense_tag')) != (r.get('subcard'), r.get('sense_tag')):
                    f.write(json.dumps(x, ensure_ascii=False) + '\n')
        tmp = os.path.join(scratch, 'hold.ru.json')
        tm.build(hold, 'ru', out=tmp)
        a = (r.get('provenance') or {}).get('input_raw_sha256')
        hit = tm.lookup('ru', a, tm=tmp)
        siblings = [(x.get('subcard'), x.get('sense_tag')) for x in by_addr.get(a, [])
                    if x is not r]
        hit_ru = None
        if hit:
            hit_ru = hit.get('ru') or hit.get('translation') or hit.get('text')
        cards.append({'key1': r.get('key1'), 'sense_tag': r.get('sense_tag'),
                      'address_rows': len(by_addr.get(a, [])),
                      'sibling_senses_same_address': siblings[:6],
                      'holdout': 'hit' if hit else 'miss',
                      'hit_keys': sorted(hit.keys()) if hit else None,
                      'hit_ru_equals_card_ru': (hit_ru == r.get('ru')) if hit else None,
                      'hit_ru_head': (hit_ru or '')[:120] if hit else None,
                      'card_ru_head': (r.get('ru') or '')[:120]})
    rep['h4056_cards_holdout'] = cards
    json.dump(rep, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    print('wrote', OUT)


if __name__ == '__main__':
    main()
