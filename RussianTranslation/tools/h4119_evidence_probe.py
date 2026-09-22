#!/usr/bin/env python
"""h4119_evidence_probe.py — read-only receipt for the three H4058 evidence defects.

Repairs measured, never asserted. The probe touches the canonical pwg_ru store
READ-ONLY, makes no provider call and promotes nothing; every number it prints
carries its denominator.

P0 — sense-level vs lemma-level.
  `annotate_evidence` writes TWO fields: `row['evidence']` (per SENSE) and
  `row['evidence_summary']` (per LEMMA, attached identically to every row sharing
  a `key1`, D1 ruling 08-07-2026). Consumers read `evidence_summary.supports_senses`
  and render it as this sense's support, which credits a sense with a sibling
  sense's evidence. This section counts the inflation exactly: rows whose lemma
  roll-up is non-empty while the sense's own evidence array is empty.

P1 — the corpus lane.
  `corpus` is a presence-only NONRU lane, so the verse-aligned Sa-Ru corpus
  supports 0 senses. `corpus_lexicon_lane` turns the same resource into a
  token-comparable sense-support lane; this section reports matched / missed /
  ambiguous / no_lane with denominators, plus how many rows it NEWLY supports.

P2 — non-circular TM.
  A TM built FROM the store and then queried WITH that store's own addresses hits
  100 % by construction — a self-hit, not evidence of reuse. This section states
  the address unit (entry-level `provenance.input_raw_sha256`, one address per
  sub-card, many rows per address), then runs a HOLD-OUT replay: rebuild the TM
  from a store copy with the held-out addresses removed and look them up. A hit
  there means a DIFFERENT card carries byte-identical masked source — genuine
  reuse. Misses are honest re-translation cost; defers are rows that cannot be
  content-addressed at all.

  python tools/h4119_evidence_probe.py            # full receipt, canonical store
  python tools/h4119_evidence_probe.py --json reports/H4119_evidence_probe.json
  python tools/h4119_evidence_probe.py --selftest # fixtures only, no store needed
"""
import argparse
import json
import os
import sys
import tempfile
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(HERE)
SRC = os.path.join(RT, 'src')
for p in (SRC, os.path.join(SRC, 'pilot')):
    if p not in sys.path:
        sys.path.insert(0, p)

import store_path                                                  # noqa: E402
import corpus_lexicon_lane as lane_mod                             # noqa: E402

LOCAL_STORE = os.path.join(SRC, 'pwg_ru_translated.jsonl')
HOLDOUT_DEFAULT = 60


# ------------------------------------------------------------------ store IO
def resolve_store(explicit=None):
    return explicit or store_path.canonical_store(LOCAL_STORE)


def load_rows(path):
    rows = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def address_of(row, lang='ru'):
    """The entry-level TM address of a row, or None when it cannot be addressed."""
    raw = (row.get('provenance') or {}).get('input_raw_sha256')
    return ('%s:%s' % (lang, raw)) if raw else None


# ------------------------------------------------------------------ P0
def probe_sense_level(rows):
    """Per-sense evidence vs the lemma-level roll-up."""
    out = Counter()
    lemmas = set()
    for r in rows:
        out['rows'] += 1
        lemmas.add(r.get('key1') or '')
        ev = r.get('evidence') or []
        es = r.get('evidence_summary') or {}
        supports = es.get('supports_senses') or []
        if ev:
            out['rows_with_sense_evidence'] += 1
        if supports:
            out['rows_with_lemma_rollup'] += 1
        if supports and not ev:
            out['rows_credited_by_rollup_only'] += 1     # the P0 over-count
        if ev and not supports:
            out['rows_sense_evidence_without_rollup'] += 1
    res = dict(out)
    res['lemmas'] = len(lemmas)
    denom = max(1, res['rows'])
    res['pct_rows_with_sense_evidence'] = round(100.0 * res.get('rows_with_sense_evidence', 0) / denom, 2)
    res['pct_rows_with_lemma_rollup'] = round(100.0 * res.get('rows_with_lemma_rollup', 0) / denom, 2)
    res['inflation_factor'] = round(
        res.get('rows_with_lemma_rollup', 0) / max(1, res.get('rows_with_sense_evidence', 0)), 3)
    return res


# ------------------------------------------------------------------ P1
def probe_corpus_lane(rows, lexicon=None, max_glosses=lane_mod.MAX_GLOSSES_PER_KEY):
    keys = {r.get('key1') for r in rows if r.get('key1')}
    lane, stats = lane_mod.load_lane(lexicon, keys=keys, max_glosses=max_glosses)
    cls_count = Counter()
    newly = 0
    for r in rows:
        glosses = lane.get(r.get('key1') or '') or []
        cls, _rel, _ref = lane_mod.classify(r.get('ru') or '', glosses)
        cls_count[cls] += 1
        if cls == 'matched' and not (r.get('evidence') or []):
            newly += 1
    denom = max(1, len(rows))
    return {
        'lexicon': stats,
        'store_key1_distinct': len(keys),
        'key1_covered_by_lane': stats['keys_kept'],
        'key1_coverage_pct': round(100.0 * stats['keys_kept'] / max(1, len(keys)), 2),
        'rows': len(rows),
        'matched': cls_count['matched'],
        'missed': cls_count['missed'],
        'ambiguous': cls_count['ambiguous'],
        'no_lane': cls_count['no_lane'],
        'matched_pct_of_rows': round(100.0 * cls_count['matched'] / denom, 2),
        'matched_pct_of_judgeable': round(
            100.0 * cls_count['matched'] / max(1, cls_count['matched'] + cls_count['missed']), 2),
        'rows_newly_supported': newly,
        'baseline_senses_supported_by_corpus_lane': 0,   # presence-only lane, by construction
    }


# ------------------------------------------------------------------ P2
def probe_tm(rows, store_p, holdout_n=HOLDOUT_DEFAULT, lang='ru'):
    """Address census + a hold-out replay that cannot self-hit."""
    by_addr = defaultdict(list)
    unaddressed = 0
    for r in rows:
        a = address_of(r, lang)
        if a is None:
            unaddressed += 1
        else:
            by_addr[a].append(r)
    addresses = sorted(by_addr)
    census = {
        'address_unit': 'entry-level: %s:<provenance.input_raw_sha256>, one address '
                        'per sub-card, many sense rows per address' % lang,
        'rows': len(rows),
        'rows_addressable': len(rows) - unaddressed,
        'rows_unaddressable_defer': unaddressed,
        'distinct_addresses': len(addresses),
        'rows_per_address_mean': round(
            (len(rows) - unaddressed) / max(1, len(addresses)), 2),
        'circular_selfhit_rate_pct': 100.0 if addresses else 0.0,
        'circular_note': 'a TM built from this store answers HIT for every one of its own '
                         'addresses by construction — that number is excluded from the verdict',
    }
    if not addresses:
        census['holdout'] = {'status': 'no_addressable_rows'}
        return census

    import translation_memory as tm                                # noqa: E402
    step = max(1, len(addresses) // max(1, holdout_n))
    holdout = addresses[::step][:holdout_n]
    hold_set = set(holdout)

    tmpdir = tempfile.mkdtemp(prefix='h4119_tm_')
    try:
        filtered = os.path.join(tmpdir, 'store.holdout.jsonl')
        kept = dropped = 0
        with open(store_p, encoding='utf-8') as fin, \
                open(filtered, 'w', encoding='utf-8', newline='\n') as fout:
            for line in fin:
                s = line.strip()
                if not s:
                    continue
                try:
                    r = json.loads(s)
                except json.JSONDecodeError:
                    continue
                if address_of(r, lang) in hold_set:
                    dropped += 1
                    continue
                fout.write(s + '\n')
                kept += 1
        tm_out = os.path.join(tmpdir, 'translation_memory.holdout.%s.json' % lang)
        tm.build(filtered, lang, out=tm_out)
        try:
            deny = set(tm.load_denylist()['addresses'])
        except Exception:
            deny = set()
        verdict = Counter()
        for a in holdout:
            if a in deny:
                verdict['defer_denylisted'] += 1
                continue
            verdict['hit' if tm.lookup(lang, a.split(':', 1)[1], tm=tm_out) else 'miss'] += 1
        census['holdout'] = {
            'holdout_addresses': len(holdout),
            'store_rows_kept': kept,
            'store_rows_withheld': dropped,
            'hit': verdict['hit'],
            'miss': verdict['miss'],
            'defer_denylisted': verdict['defer_denylisted'],
            'hit_rate_pct': round(100.0 * verdict['hit'] / max(1, len(holdout)), 2),
            'interpretation': 'hit == another sub-card in the store carries byte-identical '
                              'masked source (genuine cross-card reuse); miss == real '
                              're-translation cost; defer == denylisted address',
        }
    finally:
        try:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)
        except Exception:
            pass
    return census


# ------------------------------------------------------------------ report
def render(receipt):
    p0, p1, p2 = receipt['p0_sense_level'], receipt['p1_corpus_lane'], receipt['p2_tm']
    L = ['=== H4119 EVIDENCE PROBE (read-only) ===',
         'store: %s' % receipt['store'],
         '',
         '--- P0 per-sense evidence vs lemma-level roll-up ---',
         'store rows                          : %d (over %d distinct key1)' % (p0['rows'], p0['lemmas']),
         'rows with own per-sense evidence    : %d (%.2f%%)' % (
             p0.get('rows_with_sense_evidence', 0), p0['pct_rows_with_sense_evidence']),
         'rows with non-empty lemma roll-up   : %d (%.2f%%)' % (
             p0.get('rows_with_lemma_rollup', 0), p0['pct_rows_with_lemma_rollup']),
         'rows credited by the roll-up ALONE  : %d  <- the P0 over-count' % p0.get(
             'rows_credited_by_rollup_only', 0),
         'roll-up / per-sense inflation       : x%.3f' % p0['inflation_factor'],
         '',
         '--- P1 corpus_lexicon as a sense-support lane ---']
    lx = p1['lexicon']
    if not lx['lexicon_present']:
        L.append('lexicon ABSENT at %s — lane not measurable (NOT the same as 0 support)' % lx['lexicon_path'])
    else:
        L += ['lexicon rows read / usable(ru)      : %d / %d' % (lx['rows_read'], lx['rows_usable']),
              'store key1 covered by the lane      : %d / %d (%.2f%%)' % (
                  p1['key1_covered_by_lane'], p1['store_key1_distinct'], p1['key1_coverage_pct']),
              'baseline senses supported (before)  : %d (presence-only NONRU lane)' % p1[
                  'baseline_senses_supported_by_corpus_lane'],
              'matched / missed / ambiguous / none : %d / %d / %d / %d  (denominator %d rows)' % (
                  p1['matched'], p1['missed'], p1['ambiguous'], p1['no_lane'], p1['rows']),
              'matched share of judgeable rows     : %.2f%%' % p1['matched_pct_of_judgeable'],
              'rows NEWLY supported by this lane   : %d' % p1['rows_newly_supported']]
    L += ['', '--- P2 TM, non-circular ---',
          'address unit                        : %s' % p2['address_unit'],
          'distinct addresses / rows           : %d over %d addressable rows (mean %.2f rows/address)' % (
              p2['distinct_addresses'], p2['rows_addressable'], p2['rows_per_address_mean']),
          'rows that cannot be addressed       : %d (defer)' % p2['rows_unaddressable_defer'],
          'circular self-hit rate (EXCLUDED)   : %.1f%%' % p2['circular_selfhit_rate_pct']]
    h = p2.get('holdout') or {}
    if 'hit' in h:
        L += ['hold-out replay                     : %d addresses withheld (%d store rows removed)' % (
                  h['holdout_addresses'], h['store_rows_withheld']),
              'hold-out hit / miss / defer         : %d / %d / %d  (hit rate %.2f%%)' % (
                  h['hit'], h['miss'], h['defer_denylisted'], h['hit_rate_pct'])]
    else:
        L.append('hold-out replay                     : %s' % h.get('status', 'not run'))
    return '\n'.join(L)


def run(args):
    store_p = resolve_store(args.store)
    if not os.path.exists(store_p):
        raise SystemExit('store not found: %s' % store_p)
    rows = load_rows(store_p)
    receipt = {
        'handoff': 'H4119',
        'store': store_p,
        'read_only': True,
        'provider_calls': 0,
        'p0_sense_level': probe_sense_level(rows),
        'p1_corpus_lane': probe_corpus_lane(rows, args.lexicon),
        'p2_tm': probe_tm(rows, store_p, args.holdout),
    }
    print(render(receipt))
    if args.json:
        os.makedirs(os.path.dirname(os.path.abspath(args.json)), exist_ok=True)
        with open(args.json, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(receipt, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write('\n')
        print('\nreceipt: %s' % args.json)
    return 0


# ------------------------------------------------------------------ selftest
def selftest():
    rows = [
        # lemma agni: sense 0 has its own evidence, sense 1 has none but inherits the roll-up
        {'key1': 'agni', 'ru': 'огонь', 'evidence': [{'source': 'koch', 'relation': 'provides'}],
         'evidence_summary': {'supports_senses': ['koch'], 'silent': [], 'contradicts': []},
         'provenance': {'input_raw_sha256': 'a' * 8}},
        {'key1': 'agni', 'ru': 'бог огня', 'evidence': [],
         'evidence_summary': {'supports_senses': ['koch'], 'silent': [], 'contradicts': []},
         'provenance': {'input_raw_sha256': 'a' * 8}},
        # lemma karman: no evidence anywhere; unaddressable (no provenance hash)
        {'key1': 'karman', 'ru': 'действие', 'evidence': [],
         'evidence_summary': {'supports_senses': [], 'silent': ['koch'], 'contradicts': []},
         'provenance': {}},
    ]
    p0 = probe_sense_level(rows)
    assert p0['rows'] == 3 and p0['lemmas'] == 2, p0
    assert p0['rows_with_sense_evidence'] == 1, p0
    assert p0['rows_with_lemma_rollup'] == 2, p0
    assert p0['rows_credited_by_rollup_only'] == 1, p0      # the defect, counted
    assert p0['inflation_factor'] == 2.0, p0

    p1 = probe_corpus_lane(rows, lexicon=lane_mod.FIXTURE)
    assert p1['rows'] == 3, p1
    assert p1['baseline_senses_supported_by_corpus_lane'] == 0, p1
    # `karman` -> 'действие' is in the fixture lane and that row had NO evidence before
    assert p1['matched'] >= 1 and p1['rows_newly_supported'] >= 1, p1
    assert p1['matched'] + p1['missed'] + p1['ambiguous'] + p1['no_lane'] == p1['rows'], p1

    # address census: two rows share one address, one row cannot be addressed
    by = probe_tm(rows, store_p=os.devnull, holdout_n=0)
    assert by['distinct_addresses'] == 1, by
    assert by['rows_unaddressable_defer'] == 1, by
    assert by['rows_addressable'] == 2, by
    assert by['circular_selfhit_rate_pct'] == 100.0, by

    assert 'P0' in render({'store': 's', 'p0_sense_level': p0, 'p1_corpus_lane': p1, 'p2_tm': by})
    print('h4119_evidence_probe selftest OK')
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--store')
    ap.add_argument('--lexicon')
    ap.add_argument('--json')
    ap.add_argument('--holdout', type=int, default=HOLDOUT_DEFAULT)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    return selftest() if a.selftest else run(a)


if __name__ == '__main__':
    sys.exit(main())
