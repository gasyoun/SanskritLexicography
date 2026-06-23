#!/usr/bin/env python
"""annotate_renou.py — tag final dictionary cards with Renou language-states.

Streams a final-card JSONL (PWG or MW). For every *sense* it derives the Renou
state(s) of Sanskrit (I–V) from the <ls> citations carried in that sense's text
and writes, per sense:

  sense['renou']         multi-label list, ordered I→V (empty when uncited)
  sense['renou_oldest']  state of the sense's earliest dated <ls> citation ('' if none)

and per record:

  record['renou_oldest_sense']  index of the sense whose oldest citation is the
                                earliest in that record — i.e. the meaning first
                                attested (omitted when no sense has a dated cite).

The state→source mapping is ls_source_map.json (--dict pwg) or ls_source_map_mw.json
(--dict mw). Derivation is deterministic (no API), idempotent (re-run overwrites the
same fields), BOM-free, and writes via a temp file then atomic replace.

  python annotate_renou.py IN.jsonl [--out OUT.jsonl] [--dict pwg|mw]
  python annotate_renou.py IN.jsonl --report          # stats only, no write
"""
import json, os, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import renou

STATES = renou.STATES


def sense_text(sense):
    """All source text in a sense that could carry <ls> sigla. Joins the sense's
    string values so it works across dictionaries regardless of field naming
    (PWG keeps sigla in 'german'; MW in its English wrapper)."""
    return ' '.join(v for v in sense.values() if isinstance(v, str))


def annotate_card(card, dict_name, stats):
    """Mutate one card's senses/records in place; update stats counters."""
    for record in card.get('records', []):
        senses = record.get('senses', [])
        oldest_idx, oldest_date = None, None
        for i, sense in enumerate(senses):
            res = renou.states_for_keys(
                renou.keys_in_text(sense_text(sense), dict_name), dict_name)
            sense['renou'] = res['renou']
            sense['renou_oldest'] = res['renou_oldest']

            stats['units'] += 1
            if res['renou']:
                stats['cited'] += 1
                if len(res['renou']) > 1:
                    stats['multi'] += 1
                for st in res['renou']:
                    stats['by_state'][st] += 1
                if res['renou_oldest']:
                    stats['oldest_state'][res['renou_oldest']] += 1
            d = res['oldest_date']
            if d is not None and (oldest_date is None or d < oldest_date):
                oldest_date, oldest_idx = d, i
        if oldest_idx is not None:
            record['renou_oldest_sense'] = oldest_idx
        elif 'renou_oldest_sense' in record:
            del record['renou_oldest_sense']   # idempotent: clear a stale value


def annotate_flat(obj, dict_name, stats):
    """Legacy v0 store (pwg_ru_translated.jsonl): one homonym entry per line with
    the translated text in 'ru' and <ls> sigla restored inline — not segmented
    into senses[]. Tag at the record level (states union over the entry's
    citations + oldest). Per-sense tagging activates on the structured
    records/senses store."""
    res = renou.states_for_text(obj.get('ru') or '', dict_name)
    obj['renou'] = res['renou']
    obj['renou_oldest'] = res['renou_oldest']
    obj['renou_oldest_source'] = res['oldest_source']
    stats['units'] += 1
    if res['renou']:
        stats['cited'] += 1
        if len(res['renou']) > 1:
            stats['multi'] += 1
        for st in res['renou']:
            stats['by_state'][st] += 1
        if res['renou_oldest']:
            stats['oldest_state'][res['renou_oldest']] += 1


def card_of(obj):
    """A line may be the full {card, judge} envelope or a bare card."""
    return obj.get('card', obj) if isinstance(obj, dict) else obj


def is_structured(obj):
    """True when the line carries the records/senses schema (per-sense tagging);
    False for the flat legacy 'ru' store (record-level tagging)."""
    return isinstance(card_of(obj), dict) and 'records' in card_of(obj)


def run(path, out, dict_name, report_only):
    stats = {'cards': 0, 'units': 0, 'cited': 0, 'multi': 0, 'structured': 0,
             'by_state': collections.Counter(), 'oldest_state': collections.Counter()}
    tmp = (out + '.tmp') if not report_only else None
    sink = open(tmp, 'w', encoding='utf-8', newline='') if tmp else None
    try:
        with open(path, encoding='utf-8') as fin:
            for line in fin:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                if is_structured(obj):
                    annotate_card(card_of(obj), dict_name, stats)
                    stats['structured'] += 1
                else:
                    annotate_flat(obj, dict_name, stats)
                stats['cards'] += 1
                if sink:
                    sink.write(json.dumps(obj, ensure_ascii=False) + '\n')
    finally:
        if sink:
            sink.close()
    if tmp:
        os.replace(tmp, out)
    report(stats, dict_name, out if tmp else None)


def report(s, dict_name, out):
    # 'unit' = a sense in the structured store, a record (homonym entry) in the
    # flat legacy store.
    unit = 'senses' if s['structured'] else 'records'
    print('dict=%s  cards=%d  %s=%d  (structured cards=%d)'
          % (dict_name, s['cards'], unit, s['units'], s['structured']))
    cited = s['cited']
    pct = (100.0 * cited / s['units']) if s['units'] else 0.0
    print('  %s with a recognised citation (tagged): %d (%.1f%%)' % (unit, cited, pct))
    print('  multi-label %s (>1 state): %d' % (unit, s['multi']))
    print('  Renou state distribution (%s carrying the state):' % unit)
    for st in STATES:
        print('    %-3s %-15s %d' % (st, renou.RENOU_NAME[st], s['by_state'].get(st, 0)))
    print('  oldest-citation state (first attestation per tagged %s):' % unit[:-1])
    for st in STATES:
        print('    %-3s %-15s %d' % (st, renou.RENOU_NAME[st], s['oldest_state'].get(st, 0)))
    if out:
        print('→ %s' % out)


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); return
    path = args[0]
    out, dict_name, report_only = None, 'pwg', False
    i = 1
    while i < len(args):
        a = args[i]
        if a == '--out':
            out = args[i + 1]; i += 2
        elif a == '--dict':
            dict_name = args[i + 1]; i += 2
        elif a == '--report':
            report_only = True; i += 1
        else:
            raise SystemExit('unknown option: %s' % a)
    if not report_only and out is None:
        out = path   # in-place backfill
    run(path, out, dict_name, report_only)


if __name__ == '__main__':
    main()
