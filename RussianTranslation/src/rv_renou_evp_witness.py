#!/usr/bin/env python
r"""rv_renou_evp_witness.py -- Renou (EVP) as a locus-keyed WITNESS on the RV spine (H1910).

Louis Renou, *Etudes vediques et paninieennes* (EVP), 17 vols, 1955-1969, sits
chronologically between Geldner 1951-57 and Elizarenkova 1989-99, and Elizarenkova argues
with it constantly -- exactly the "a later translator departs knowingly" pattern the H1908
chronology band exists to expose.

**Renou is NOT a fifth translation column, and this script exists to keep him out of one.**
EVP is a selective commentary covering chosen hymn groups, not all 1,028 hymns. Forcing it
into `translations` would produce a mostly-`absent_from_source` layer and would corrupt the
`omitted_by_one` class, whose whole meaning rests on absence being *meaningful*
(ARCHITECTURE Sec.3.1). Absence of a Renou remark at a locus means "Elizarenkova did not
cite him there", never "Renou did not render it" -- and those are not the same claim.
So this emits a witness file alongside the spine, joined by `location`, never inside it.

Input is the committed H1843 index, `pwg_ru/rv_renou_citation_index.jsonl`: 2,213 mentions
of "Рену" mined from Elizarenkova's own commentary, of which some carry a directly quoted
French fragment. Note the number: MG said "300+", the H1843 spec claimed 368 quoted, and
H1843 measured a different figure under the spec's own literal reading and logged the
discrepancy rather than tuning to match (docs/DECISIONS_LOG_rv_multitranslation.md). This
script re-measures from the committed index and prints what it finds -- it does not
reconcile to any published number.

  python rv_renou_evp_witness.py            # build pwg_ru/rv_renou_evp_witness.jsonl
  python rv_renou_evp_witness.py --report   # measure only, write nothing
  python rv_renou_evp_witness.py selftest   # deterministic asserts, no files, no network
"""
import argparse
import collections
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT_ROOT = os.path.normpath(os.path.join(HERE, '..'))
PWG_RU_DIR = os.path.join(RT_ROOT, 'pwg_ru')

INDEX_PATH = os.path.join(PWG_RU_DIR, 'rv_renou_citation_index.jsonl')
STANZA_PATH = os.path.join(PWG_RU_DIR, 'rv_stanza_translations.jsonl')
OUT_PATH = os.path.join(PWG_RU_DIR, 'rv_renou_evp_witness.jsonl')
RUN_LOG_DIR = os.path.join(PWG_RU_DIR, 'h1910')
RUN_LOG_PATH = os.path.join(RUN_LOG_DIR, 'renou_evp_witness_run_log.md')

# Renou's place in the chronology. A WITNESS row, deliberately not in TRANSLATORS -- see
# the module docstring and build_rv_divergence_gate_sheet.WITNESS_CHRONO.
RENOU_KEY = 'renou_fr_1955'
RENOU_YEARS = (1955, '1955–69', 'Рену')

# How many quoted fragments and contexts a witness record carries. The witness is a
# reviewer aid on a gate card, not an edition of EVP: an uncapped dump of 30 mentions at a
# popular locus would push the two renderings being judged off the card.
MAX_QUOTES = 3
MAX_CONTEXTS = 2
CONTEXT_CHARS = 300


def read_jsonl(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def build_witness(mentions, canonical_locations=None):
    """-> (records, stats). One record per locus that has at least one Renou mention."""
    by_loc = collections.OrderedDict()
    unresolved = 0
    off_spine = []
    for rec in mentions:
        loc = rec.get('location')
        if rec.get('locus_unresolved') or not loc:
            unresolved += 1
            continue
        if canonical_locations is not None and loc not in canonical_locations:
            off_spine.append(loc)
            continue
        by_loc.setdefault(loc, []).append(rec)

    records = []
    for loc, group in by_loc.items():
        mandala, hymn, stanza = (int(x) for x in loc.split('.'))
        quotes, contexts = [], []
        for rec in group:
            q = rec.get('quote_fr')
            if q and q not in quotes:
                quotes.append(q)
            c = (rec.get('context_ru') or '').strip()
            if c and c not in contexts:
                contexts.append(c[:CONTEXT_CHARS])
        quoted_n = sum(1 for r in group if r.get('mention_kind') == 'quoted_fr')
        records.append({
            'location': loc,
            'mandala': mandala, 'hymn': hymn, 'stanza': stanza,
            'witness': RENOU_KEY,
            'witness_year': RENOU_YEARS[0],
            'mention_count': len(group),
            'quoted_count': quoted_n,
            # A quoted French fragment is the strong form of the witness: Elizarenkova is
            # reproducing Renou's wording, so a reviewer can see what she is arguing with.
            'has_quote': bool(quotes),
            'quotes_fr': quotes[:MAX_QUOTES],
            'quotes_truncated': len(quotes) > MAX_QUOTES,
            'contexts_ru': contexts[:MAX_CONTEXTS],
            'contexts_truncated': len(contexts) > MAX_CONTEXTS,
            'source': 'elizarenkova_commentary',
        })
    records.sort(key=lambda r: (r['mandala'], r['hymn'], r['stanza']))
    stats = {
        'mentions_total': len(mentions),
        'mentions_unresolved': unresolved,
        'mentions_off_spine': off_spine,
        'loci_covered': len(records),
        'loci_with_quote': sum(1 for r in records if r['has_quote']),
        'mentions_resolved': sum(r['mention_count'] for r in records),
        'quoted_resolved': sum(r['quoted_count'] for r in records),
    }
    return records, stats


def selftest():
    mentions = [
        {'location': '1.1.1', 'mandala': 1, 'hymn': 1, 'stanza': 1,
         'mention_kind': 'quoted_fr', 'context_ru': 'ctx A', 'quote_fr': 'le dieu',
         'locus_unresolved': False},
        {'location': '1.1.1', 'mandala': 1, 'hymn': 1, 'stanza': 1,
         'mention_kind': 'paraphrase_ru', 'context_ru': 'ctx B', 'quote_fr': None,
         'locus_unresolved': False},
        {'location': None, 'mandala': 1, 'hymn': None, 'stanza': None,
         'mention_kind': 'paraphrase_ru', 'context_ru': 'front matter', 'quote_fr': None,
         'locus_unresolved': True},
        {'location': '9.9.9', 'mandala': 9, 'hymn': 9, 'stanza': 9,
         'mention_kind': 'paraphrase_ru', 'context_ru': 'ctx C', 'quote_fr': None,
         'locus_unresolved': False},
    ]
    recs, stats = build_witness(mentions, canonical_locations={'1.1.1', '9.9.9'})
    assert len(recs) == 2, recs
    a = recs[0]
    assert a['location'] == '1.1.1' and a['mention_count'] == 2
    assert a['quoted_count'] == 1 and a['has_quote'] is True
    assert a['quotes_fr'] == ['le dieu']
    assert a['witness'] == RENOU_KEY
    # the unresolved mention is counted, never given a locus
    assert stats['mentions_unresolved'] == 1
    assert stats['mentions_resolved'] == 3
    # a mention pointing off the canonical spine is dropped and reported, not invented
    recs2, stats2 = build_witness(mentions, canonical_locations={'1.1.1'})
    assert len(recs2) == 1 and stats2['mentions_off_spine'] == ['9.9.9']
    # the witness must never look like a translation column
    assert 'translations' not in a and 'text' not in a and 'status' not in a
    print('rv_renou_evp_witness selftest OK -- locus grouping, quote/paraphrase split, '
          'unresolved and off-spine mentions reported not invented, no translation shape')
    return 0


def main():
    ap = argparse.ArgumentParser(description='Renou EVP locus witness (H1910)')
    ap.add_argument('cmd', nargs='?', default='build', choices=['build', 'selftest'])
    ap.add_argument('--report', action='store_true', help='measure only, write nothing')
    a = ap.parse_args()
    if a.cmd == 'selftest':
        return selftest()

    mentions = read_jsonl(INDEX_PATH)
    canonical = None
    if os.path.exists(STANZA_PATH):
        canonical = {r['location'] for r in read_jsonl(STANZA_PATH)}
    records, stats = build_witness(mentions, canonical)

    print('Renou mentions in the committed index: %d' % stats['mentions_total'])
    print('  locus_unresolved (front matter / hymn-group intro): %d' % stats['mentions_unresolved'])
    print('  pointing off the canonical spine (dropped, reported): %d'
          % len(stats['mentions_off_spine']))
    print('  resolved onto a locus: %d' % stats['mentions_resolved'])
    print('  of those, quoted_fr: %d' % stats['quoted_resolved'])
    print('loci carrying a Renou witness: %d of %s canonical'
          % (stats['loci_covered'], len(canonical) if canonical else '?'))
    print('  with at least one quoted French fragment: %d' % stats['loci_with_quote'])
    per_mandala = collections.Counter(r['mandala'] for r in records)
    print('  per mandala: %s' % dict(sorted(per_mandala.items())))

    if a.report:
        return 0

    with open(OUT_PATH, 'w', encoding='utf-8', newline='\n') as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    print('wrote %s: %d witness records' % (OUT_PATH, len(records)))

    os.makedirs(RUN_LOG_DIR, exist_ok=True)
    with open(RUN_LOG_PATH, 'w', encoding='utf-8', newline='\n') as f:
        f.write('# Renou EVP witness join run log (H1910)\n\n')
        f.write('_Created: 30-07-2026 · Last updated: 30-07-2026_\n\n')
        f.write('Renou enters the layer as a **locus-keyed witness**, not as a fifth '
                'translation column: EVP is a selective commentary over chosen hymn '
                'groups, so a `translations` column for it would be mostly '
                '`absent_from_source` and would corrupt the `omitted_by_one` class, '
                'whose meaning depends on absence being meaningful.\n\n')
        f.write('| measure | value |\n|---|--:|\n')
        f.write('| Renou mentions in the committed H1843 index | %d |\n' % stats['mentions_total'])
        f.write('| locus_unresolved (front matter / group intro) | %d |\n'
                % stats['mentions_unresolved'])
        f.write('| pointing off the canonical spine (dropped) | %d |\n'
                % len(stats['mentions_off_spine']))
        f.write('| resolved onto a locus | %d |\n' % stats['mentions_resolved'])
        f.write('| of those, carrying a quoted French fragment | %d |\n'
                % stats['quoted_resolved'])
        f.write('| **loci carrying a Renou witness** | **%d** |\n' % stats['loci_covered'])
        f.write('| loci with at least one quoted fragment | %d |\n' % stats['loci_with_quote'])
        f.write('\n## Per mandala\n\n| Mandala | loci with a witness |\n|---|--:|\n')
        for m in range(1, 11):
            f.write('| %d | %d |\n' % (m, per_mandala.get(m, 0)))
        f.write('\n_Dr. Mārcis Gasūns_\n')
    print('wrote %s' % RUN_LOG_PATH)
    return 0


if __name__ == '__main__':
    sys.exit(main())
