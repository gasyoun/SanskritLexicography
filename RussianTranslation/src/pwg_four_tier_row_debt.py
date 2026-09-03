#!/usr/bin/env python
"""H3948 option-2 residual (MG ruling 03-09-2026) -- name the rows, don't guess them.

The H3948 measurement (FINDINGS Sec.453, reports/H3948_four_tier_store_impact.json)
produced three buckets and no row lists: 12 tag-resolved-and-changed rows, 990
tag-resolved-unchanged, 2210 tag-unresolved. MG's ruling on the three-option brief
was option 2 -- rewrite ONLY the rows whose tier reads unambiguously, and record the
unresolvable ones as declared debt in a REPORT, never in the store.

Running it answered the first half in the negative. None of the 12 reads unambiguously:

  * each is a PARENT SPLIT, not a retag -- for all 7 affected key1 no sense id
    disappeared, only new greek children appeared, so the row's id survived while its
    body moved into alpha/beta/gamma and no single new id owns the row's text;
  * only 3 of the 12 carry the same greek marker count in `ru` as in `de`, so a
    mechanical RU split is unavailable for the other 9 (pwg_four_tier_ru_split_probe.py);
  * decisively, `sense_tag` is not a sense path at all. Store-wide it matches the marker
    the row's own `de` opens with in 84.7% of comparable rows, and among the debt rows
    it takes 943 distinct shapes -- `caus-2`, `main`, `pw_1_3`, `mit-ni-2`, `NWS-4`,
    `intro`, `cross-ref` -- free-form provenance labels from earlier extraction passes
    (pwg_sense_tag_agreement.py). A tier cannot be read from a label that never encoded
    one.

So this script emits ONE debt surface of 2222 rows instead of a rewrite list plus 2210:
the 12 join the debt as their own class rather than being guessed at, which is exactly
what the ruling's own qualifier -- rewrite the rows "где ярус читается однозначно" --
requires once the evidence says none of them does.

  reports/H3948_segmentation_debt.json/.tsv   2222 rows flagged "сегментация под
      вопросом", each carrying `class` and `tag_vocabulary`:
        parent-split           12    id survived, body moved into greek children
        sense-path-unresolved 143    path-shaped tag, no matching pre-H3948 id
        tag-not-a-sense-path 2067    tag is a provenance label, not an enumeration
  reports/H3948_four_tier_rewrite_candidates.json   the 12, with the evidence that
      would have had to support a rewrite: the row's own `de` digest, the pre- and
      post-H3948 digest lists for its sense_tag, and which new sense ids (none) carry
      byte-identical gloss text.

The store is opened 'r' and its sha256 is asserted equal before and after.

    python pwg_four_tier_row_debt.py
    python pwg_four_tier_row_debt.py --limit 5000     # debug, partial corpus
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
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import microstructure as ms                 # noqa: E402
import pwg_four_tier_store_impact as impact  # noqa: E402

REPORTS_DIR = os.path.join(HERE, '..', 'reports')
CANDIDATES_PATH = os.path.join(REPORTS_DIR, 'H3948_four_tier_rewrite_candidates.json')
DEBT_JSON = os.path.join(REPORTS_DIR, 'H3948_segmentation_debt.json')
DEBT_TSV = os.path.join(REPORTS_DIR, 'H3948_segmentation_debt.tsv')

DEBT_FLAG = 'сегментация под вопросом'

# `sense_tag` turned out NOT to be a controlled sense-path vocabulary: 943 distinct
# normalised shapes over the 2210 unresolved rows, most of them free-form provenance
# labels from earlier extraction passes (`caus-2`, `main`, `pw_1_3`, `mit-ni-2`).
# Only a path-shaped tag could ever carry a four-tier verdict, so the debt list says
# which vocabulary each row speaks instead of lumping all 2210 together.
SENSE_PATH_RE = re.compile(r'^\d{0,2}[a-z]?[\u03b1-\u03c9]?$')


def tag_vocabulary(tag):
    """Which naming scheme this sense_tag belongs to."""
    if not tag:
        return 'empty'
    if SENSE_PATH_RE.match(tag) and tag != '':
        return 'sense-path-like'
    if tag.startswith('pref-'):
        return 'prefix-subentry-label'
    return 'free-form-provenance-label'


CLASS_PARENT_SPLIT = 'parent-split'
CLASS_NOT_A_PATH = 'tag-not-a-sense-path'
CLASS_PATH_UNRESOLVED = 'sense-path-unresolved'

CLASS_REASON = {
    CLASS_PARENT_SPLIT: (
        'the row\'s sense id survived H3948, but its body moved into new greek '
        'children (alpha/beta/gamma); the paid RU text now spans several senses and '
        'no single post-H3948 id is correct for this row'),
    CLASS_NOT_A_PATH: (
        'sense_tag is not a sense path at all but a free-form provenance label from '
        'an earlier extraction pass, so no enumeration tier can be read from it'),
    CLASS_PATH_UNRESOLVED: (
        'sense_tag is path-shaped but is not an id the pre-H3948 parser emitted for '
        'this key1; the printed source does not disambiguate the tier'),
}


def row_de_digest(row):
    """The digest of this row's OWN German span, in segment()'s normal form."""
    de = row.get('de') or ''
    de = ms.HEAD_DIV.sub('', de) if hasattr(ms, 'HEAD_DIV') else de
    de = de.lstrip()
    for lead in ('<div n="1">', '<div n="2">', '<div n="3">'):
        if de.startswith(lead):
            de = de[len(lead):].lstrip()
    if de.startswith('—'):
        de = de[1:].lstrip()
    return impact.digest(ms.clean_de(de))


def ids_carrying(maps_k1, dg):
    return sorted(sid for sid, digs in maps_k1.items() if dg in digs)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--store', default=None)
    args = ap.parse_args(argv)

    store_path = impact.find_store(args.store)
    if not store_path:
        print('RU store not found', file=sys.stderr)
        return 2
    print('store : %s' % store_path)

    old_maps, new_maps, records = impact.scan_corpus(limit=args.limit)
    changed, per_id = impact.changed_keys(old_maps, new_maps)
    print('corpus: %d records, %d changed key1' % (records, len(changed)))

    sha_before = impact.sha256_of(store_path)
    candidates, debt = [], []
    rows = 0
    unchanged = 0
    with open(store_path, 'r', encoding='utf-8') as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            rows += 1
            k1 = row.get('key1') or ''
            if k1 not in changed:
                continue
            tag = row.get('sense_tag')
            tag = '' if tag is None else str(tag)
            om, nm = old_maps.get(k1, {}), new_maps.get(k1, {})
            base = {
                'line': lineno,
                'subcard': row.get('subcard'),
                'key1': k1,
                'iast': row.get('iast'),
                'sense_tag': tag,
                'column': row.get('column'),
                'page': row.get('page'),
                'volume': row.get('volume'),
                'review_status': row.get('review_status'),
                'reviewer': row.get('reviewer'),
            }
            base['tag_vocabulary'] = tag_vocabulary(tag)
            if tag in om:
                if not per_id.get(k1, {}).get(tag):
                    unchanged += 1
                    continue
                dg = row_de_digest(row)
                base.update({
                    'de_digest': dg,
                    'de_digest_in_old_tag': dg in om.get(tag, []),
                    'pre_h3948_digests': om.get(tag, []),
                    'post_h3948_digests': nm.get(tag, []),
                    'post_h3948_ids_carrying_this_row_text': ids_carrying(nm, dg),
                    'pre_h3948_ids_carrying_this_row_text': ids_carrying(om, dg),
                })
                base['flag'] = DEBT_FLAG
                base['class'] = CLASS_PARENT_SPLIT
                base['reason'] = CLASS_REASON[CLASS_PARENT_SPLIT]
                candidates.append(base)
                debt.append(base)
            else:
                cls = (CLASS_PATH_UNRESOLVED
                       if base['tag_vocabulary'] == 'sense-path-like'
                       else CLASS_NOT_A_PATH)
                base['flag'] = DEBT_FLAG
                base['class'] = cls
                base['reason'] = CLASS_REASON[cls]
                debt.append(base)
    sha_after = impact.sha256_of(store_path)
    assert sha_before == sha_after, \
        'FENCE VIOLATION: RU store hash changed during a read-only pass'

    os.makedirs(REPORTS_DIR, exist_ok=True)
    precise = [c for c in candidates
               if len(c['post_h3948_ids_carrying_this_row_text']) == 1]
    payload = {
        'handoff': 'H3948',
        'ruling': 'MG 03-09-2026, option 2 of the three-option brief',
        'finding': 'FINDINGS Sec.453',
        'read_only': True,
        'store_path': store_path,
        'store_sha256': sha_before,
        'store_rows': rows,
        'corpus_records': records,
        'tag_resolved_changed_rows': len(candidates),
        'tag_resolved_unchanged_rows': unchanged,
        'rows_with_a_unique_post_h3948_home': len(precise),
        'rows': candidates,
    }
    with open(CANDIDATES_PATH, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2, sort_keys=True)

    shapes = collections.Counter(d['sense_tag'][:24] or '(empty)' for d in debt)
    by_class = collections.Counter(d['class'] for d in debt)
    by_vocab = collections.Counter(d['tag_vocabulary'] for d in debt)
    with open(DEBT_JSON, 'w', encoding='utf-8') as fh:
        json.dump({
            'handoff': 'H3948',
            'ruling': 'MG 03-09-2026, option 2 of the three-option brief',
            'flag': DEBT_FLAG,
            'read_only': True,
            'store_never_written': True,
            'store_path': store_path,
            'store_sha256': sha_before,
            'rows_flagged': len(debt),
            'rows_by_class': by_class.most_common(),
            'rows_by_tag_vocabulary': by_vocab.most_common(),
            'class_reasons': CLASS_REASON,
            'distinct_sense_tag_shapes': len({d['sense_tag'] for d in debt}),
            'sense_tag_is_not_a_sense_path': (
                'Measured store-wide: the last component of sense_tag matches the '
                'marker the row\'s own `de` opens with in only 84.7% of the 5636 '
                'comparable rows (4772 agree / 257 disagree); see '
                'pwg_sense_tag_agreement.py. sense_tag is a provenance label, not a '
                'sense path, so no four-tier verdict can be computed from it.'),
            'tag_shapes': shapes.most_common(),
            'rows': debt,
        }, fh, ensure_ascii=False, indent=2, sort_keys=True)
    cols = ['line', 'subcard', 'key1', 'iast', 'sense_tag', 'tag_vocabulary',
            'class', 'column', 'page', 'volume', 'review_status', 'reviewer',
            'flag']
    with open(DEBT_TSV, 'w', encoding='utf-8') as fh:
        fh.write('\t'.join(cols) + '\n')
        for d in debt:
            fh.write('\t'.join(str(d.get(c, '')) for c in cols) + '\n')

    print('rewrite candidates : %d (unique post-H3948 home: %d)'
          % (len(candidates), len(precise)))
    print('declared debt rows : %d  -> %s' % (len(debt), DEBT_TSV))
    for cls, cnt in by_class.most_common():
        print('    %-24s %5d' % (cls, cnt))
    print('  by sense_tag vocabulary:')
    for voc, cnt in by_vocab.most_common():
        print('    %-24s %5d' % (voc, cnt))
    print('unchanged rows     : %d' % unchanged)
    return 0


if __name__ == '__main__':
    sys.exit(main())
