#!/usr/bin/env python
"""annotate_genres.py — tag final dictionary cards with per-sense citation genre(s).

Sibling of annotate_renou.py: same <ls>-citation walk, different output. For every
*sense* this derives the literal genre label(s) of its cited sources from
ls_source_map.json (45 curated works, ~70% of PWG's <ls> occurrences) and writes:

  sense['genre']          sorted list of curated genre labels cited by this sense
                          (e.g. ["Kāvya — Mahākāvya (Kālidāsa)", "Veda — Saṃhitā"]);
                          [] when the sense has no citation OR every cited siglum is
                          unmapped — genuinely UNKNOWN, never conflated with "attested
                          only in genre X".
  sense['genre_coarse']   sorted list of coarse rollups derived from genre's label
                          prefix (kavya/veda/sastra/purana/epic/kosha); [] when genre
                          is [].

This answers MG's "какие значения встречаются в kāvya?" at the citation-evidence
level: "PWG cites this sense from a kāvya work". It does NOT answer "the lemma is
corpus-frequent in kāvya" — that is the separate, frequency-weighted DCS register
lane (dcs_registers, annotate_dcs_freq.py) and the two are never merged (see W4 in
PIPELINE_CAPABILITY_AUDIT_2026-07-08.md). annotation_report.py folds both lanes'
queries into its single query CLI.

Siglum normalization reuses renou.keys_in_text verbatim, so genre and renou state
tagging always agree on which citations were recognised. Deterministic (no API),
idempotent, BOM-free, writes via temp file + atomic replace.

  python annotate_genres.py IN.jsonl [--out OUT.jsonl] [--dict pwg|mw]
  python annotate_genres.py IN.jsonl --report          # stats only, no write
  python annotate_genres.py --coverage [--top N]       # unmapped sigla by citation
                                                          mass, over raw pwg.txt
  python annotate_genres.py --selftest
"""
import collections
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import renou

HERE = os.path.dirname(os.path.abspath(__file__))
GH = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
PWG_TXT = os.path.join(GH, 'csl-orig', 'v02', 'pwg', 'pwg.txt')

# Coarse rollup: the curated genre label's prefix before " -- " (or the whole label
# for the one prefix-less entry, "Purana"). Every one of the 25 curated labels
# resolves to exactly one of these six buckets.
_COARSE = {
    'Epic': 'epic',
    'Kośa': 'kosha',
    'Kāvya': 'kavya',
    'Purāṇa': 'purana',
    'Veda': 'veda',
    'Śāstra': 'sastra',
}


def coarse_of(genre_label):
    # every curated label's bucket is its leading word, whether followed by an
    # " -- " qualifier ("Kāvya -- kathā") or a parenthetical ("Kośa (lexicon)")
    # or nothing at all ("Purāṇa").
    prefix = genre_label.split(None, 1)[0].strip() if genre_label else ''
    return _COARSE.get(prefix, '')


def genres_for_keys(source_keys, dict_name='pwg'):
    """Resolve already-extracted <ls> source keys -> curated genre label(s) +
    coarse rollup(s). Keys absent from ls_source_map are ignored (same policy as
    renou.states_for_keys), so an unmapped-only citation set comes back empty."""
    smap = renou.load_map(dict_name)
    genres, coarse = set(), set()
    for k in source_keys:
        rec = smap.get(k)
        if not rec:
            continue
        g = rec.get('genre')
        if not g:
            continue
        genres.add(g)
        c = coarse_of(g)
        if c:
            coarse.add(c)
    return sorted(genres), sorted(coarse)


def genres_for_text(text, dict_name='pwg'):
    return genres_for_keys(renou.keys_in_text(text, dict_name), dict_name)


def annotate_card(card, dict_name, stats):
    """Mutate one card's senses in place (structured records/senses schema);
    update stats counters. Mirrors annotate_renou.annotate_card."""
    for record in card.get('records', []):
        for sense in record.get('senses', []):
            text = ' '.join(v for v in sense.values() if isinstance(v, str))
            genres, coarse = genres_for_text(text, dict_name)
            sense['genre'] = genres
            sense['genre_coarse'] = coarse
            stats['units'] += 1
            if genres:
                stats['tagged'] += 1
                if len(genres) > 1:
                    stats['multi'] += 1
                for c in coarse:
                    stats['by_coarse'][c] += 1


def annotate_flat(obj, dict_name, stats):
    """Flat legacy/production store (pwg_ru_translated.jsonl): one sense per row,
    citation markup preserved verbatim in 'ru'. Mirrors annotate_renou.annotate_flat."""
    genres, coarse = genres_for_text(obj.get('ru') or '', dict_name)
    obj['genre'] = genres
    obj['genre_coarse'] = coarse
    stats['units'] += 1
    if genres:
        stats['tagged'] += 1
        if len(genres) > 1:
            stats['multi'] += 1
        for c in coarse:
            stats['by_coarse'][c] += 1


def card_of(obj):
    return obj.get('card', obj) if isinstance(obj, dict) else obj


def is_structured(obj):
    return isinstance(card_of(obj), dict) and 'records' in card_of(obj)


def run(path, out, dict_name, report_only):
    stats = {'cards': 0, 'units': 0, 'tagged': 0, 'multi': 0, 'structured': 0,
              'by_coarse': collections.Counter()}
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
    unit = 'senses' if s['structured'] else 'rows'
    print('dict=%s  cards=%d  %s=%d  (structured cards=%d)'
          % (dict_name, s['cards'], unit, s['units'], s['structured']))
    tagged = s['tagged']
    pct = (100.0 * tagged / s['units']) if s['units'] else 0.0
    print('  %s with >=1 recognised citation genre: %d (%.1f%%)' % (unit, tagged, pct))
    print('  multi-genre %s (>1 curated label): %d' % (unit, s['multi']))
    print('  coarse rollup distribution (%s carrying the bucket):' % unit)
    for c in ('veda', 'kavya', 'epic', 'sastra', 'purana', 'kosha'):
        print('    %-8s %d' % (c, s['by_coarse'].get(c, 0)))
    if out:
        print('→ %s' % out)


def cmd_coverage(top_n):
    """Top unmapped <ls> sigla by raw citation mass over pwg.txt (data-curation
    note, not a build item — extending ls_source_map.json is a separate pass)."""
    data = open(PWG_TXT, encoding='utf-8').read()
    # reuse renou.keys_in_text over the whole file so normalization matches the
    # per-sense path exactly (no separate parsing logic to drift).
    freq = collections.Counter(renou.keys_in_text(data, 'pwg'))
    total = sum(freq.values())
    smap = renou.load_map('pwg')
    mapped_cit = sum(c for k, c in freq.items() if k in smap)
    print('PWG <ls>: %d citations, %d distinct source keys' % (total, len(freq)))
    print('mapped by ls_source_map (45 works): %d/%d citations (%.1f%%)'
          % (mapped_cit, total, 100.0 * mapped_cit / total if total else 0.0))
    unmapped = [(k, c) for k, c in freq.most_common() if k not in smap]
    print('top %d UNMAPPED sigla by citation mass:' % top_n)
    for k, c in unmapped[:top_n]:
        print('  %-22s %6d' % (k, c))


def selftest():
    smap = {
        'RAGH': {'genre': 'Kāvya — Mahākāvya (Kālidāsa)'},
        'RV': {'genre': 'Veda — Saṃhitā'},
        'AK': {'genre': 'Kośa (lexicon)'},
    }
    renou._CACHE['pwg'] = smap
    g, c = genres_for_keys(['RAGH'])
    assert g == ['Kāvya — Mahākāvya (Kālidāsa)'] and c == ['kavya'], (g, c)
    g, c = genres_for_keys(['RAGH', 'RV'])
    assert g == ['Kāvya — Mahākāvya (Kālidāsa)', 'Veda — Saṃhitā']
    assert c == ['kavya', 'veda']
    g, c = genres_for_keys(['AK'])
    assert c == ['kosha'], c
    g, c = genres_for_keys(['ZZZUNMAPPED'])
    assert g == [] and c == []
    g, c = genres_for_keys([])
    assert g == [] and c == []
    del renou._CACHE['pwg']
    print('annotate_genres selftest OK')


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); return
    if args[0] == '--selftest':
        return selftest()
    if args[0] == '--coverage':
        top_n = 30
        if '--top' in args:
            top_n = int(args[args.index('--top') + 1])
        return cmd_coverage(top_n)
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
