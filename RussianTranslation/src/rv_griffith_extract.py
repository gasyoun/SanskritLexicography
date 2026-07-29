#!/usr/bin/env python
"""rv_griffith_extract.py -- extract the Griffith 1896 English RV layer from rvlinks' HTML.

rvlinks/RV_sa-hn-ru-de-en_1.html is a flat sequence of per-stanza blocks: a
<p class="stamp"> locus (rv01.001.01 form) followed by <p class="sa">/<p class="hn">/
<p class="ru">/<p class="de">/<p class="en"> paragraphs. This is the only place the
Griffith English translation exists in aligned, machine-readable form -- extracting it
here (rather than re-scraping/re-typing it) is the whole point of C1 (H1843 step 1).

Emits pwg_ru/griffith_en_1896.json in the same envelope shape as the three VedaWeb
translation files (grassmann_de_1876_1877.json etc.): {meta, contents: [{createdAt,
archived, text, location}]}.

  python rv_griffith_extract.py
"""
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
from sibling_root import sibling_root  # noqa: E402
GITHUB_ROOT, _ = sibling_root()  # GitHub/ (H1902: worktree-safe root resolution)
RVLINKS_HTML = os.path.join(GITHUB_ROOT, 'rvlinks', 'RV_sa-hn-ru-de-en_1.html')
LEMMATIZATION = os.path.join(
    GITHUB_ROOT, 'VisualDCS', 'non-derived', 'vedaweb', 'lemmatization.json')
OUT_PATH = os.path.normpath(os.path.join(HERE, '..', 'pwg_ru', 'griffith_en_1896.json'))
RUN_LOG_DIR = os.path.normpath(os.path.join(HERE, '..', 'pwg_ru', 'h1843'))
RUN_LOG_PATH = os.path.join(RUN_LOG_DIR, 'griffith_extract_run_log.md')

STAMP_RE = re.compile(r'<p class="stamp">\s*(rv\d+\.\d+\.\d+)\s*</p>')
EN_RE = re.compile(r'<p class="en">(.*?)</p>', re.DOTALL)
TAG_RE = re.compile(r'<[^>]+>')


def normalize_locus(stamp):
    """rv01.001.01 -> 1.1.1 (strip 'rv', drop leading zeros per field)."""
    body = stamp[2:]
    mandala, hymn, verse = body.split('.')
    return '%d.%d.%d' % (int(mandala), int(hymn), int(verse))


def clean_en_text(raw_html):
    text = raw_html.replace('<BR>', '\n').replace('<br />', '\n')
    text = text.replace('<br/>', '\n').replace('<br>', '\n')
    text = TAG_RE.sub('', text)
    lines = [ln.strip() for ln in text.split('\n')]
    lines = [ln for ln in lines if ln]
    return '\n'.join(lines).strip()


def rvlinks_provenance():
    try:
        commit = subprocess.run(
            ['git', 'rev-parse', 'HEAD'], cwd=os.path.join(GITHUB_ROOT, 'rvlinks'),
            capture_output=True, text=True, encoding='utf-8', check=True,
        ).stdout.strip()
    except Exception:
        commit = 'unknown'
    return ('extracted by rv_griffith_extract.py (H1843) from '
            'rvlinks/RV_sa-hn-ru-de-en_1.html @ %s' % commit)


def load_canonical_locations():
    with open(LEMMATIZATION, encoding='utf-8') as f:
        d = json.load(f)
    return {rec['location'] for rec in d['contents']}


def extract(html):
    stamps = list(STAMP_RE.finditer(html))
    canonical = load_canonical_locations()

    records = []
    seen = set()
    duplicates = []
    no_en_block = []
    not_in_canonical = []

    for i, m in enumerate(stamps):
        stamp = m.group(1)
        loc = normalize_locus(stamp)
        block_start = m.end()
        block_end = stamps[i + 1].start() if i + 1 < len(stamps) else len(html)
        block = html[block_start:block_end]

        en_m = EN_RE.search(block)
        if en_m is None:
            no_en_block.append(loc)
            continue

        if loc in seen:
            duplicates.append(loc)
            continue

        if loc not in canonical:
            not_in_canonical.append(loc)
            continue

        seen.add(loc)
        text = clean_en_text(en_m.group(1))
        records.append({
            'createdAt': '0001-01-01 00:00:00+00:00',
            'archived': False,
            'text': text,
            'location': loc,
        })

    stats = {
        'stamps_found': len(stamps),
        'extracted': len(records),
        'duplicates_kept_first': duplicates,
        'no_en_block': no_en_block,
        'not_in_canonical_set': not_in_canonical,
        'unmatched_share_pct': round(
            100.0 * (len(not_in_canonical) + len(no_en_block)) / len(stamps), 3
        ) if stamps else 0.0,
    }
    return records, stats


def main():
    with open(RVLINKS_HTML, encoding='utf-8') as f:
        html = f.read()

    records, stats = extract(html)

    envelope = {
        'meta': {
            'author': 'Ralph T. H. Griffith',
            'year': '1896',
            'language': 'en',
            'provenance': rvlinks_provenance(),
        },
        'contents': records,
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(envelope, f, ensure_ascii=False, indent=2)
        f.write('\n')

    os.makedirs(RUN_LOG_DIR, exist_ok=True)
    with open(RUN_LOG_PATH, 'w', encoding='utf-8', newline='\n') as f:
        f.write('# Griffith extraction run log (H1843 step 1 / S1 spike)\n\n')
        f.write('_Created: 29-07-2026 · Last updated: 29-07-2026_\n\n')
        f.write('- stamps found in source HTML: %d\n' % stats['stamps_found'])
        f.write('- records extracted: %d\n' % stats['extracted'])
        f.write('- duplicate loci (kept first, logged): %d\n' % len(stats['duplicates_kept_first']))
        f.write('- stamps with no `<p class="en">` block: %d\n' % len(stats['no_en_block']))
        f.write('- loci not in the VedaWeb canonical set (skipped): %d\n' % len(stats['not_in_canonical_set']))
        f.write('- unmatched share (S1 spike, VERIFICATION K5, must be <= 2%%): **%.3f%%**\n\n'
                % stats['unmatched_share_pct'])
        if stats['duplicates_kept_first']:
            f.write('## Duplicate loci\n\n')
            for loc in stats['duplicates_kept_first']:
                f.write('- %s\n' % loc)
            f.write('\n')
        if stats['no_en_block']:
            f.write('## Stamps with no en block\n\n')
            for loc in stats['no_en_block']:
                f.write('- %s\n' % loc)
            f.write('\n')
        if stats['not_in_canonical_set']:
            f.write('## Loci not in VedaWeb canonical set\n\n')
            for loc in stats['not_in_canonical_set']:
                f.write('- %s\n' % loc)
            f.write('\n')
        f.write('_Dr. Mārcis Gasūns_\n')

    print('stamps_found=%d extracted=%d unmatched_share_pct=%.3f'
          % (stats['stamps_found'], stats['extracted'], stats['unmatched_share_pct']))
    if stats['unmatched_share_pct'] > 2.0:
        print('WARNING: S1 spike threshold exceeded (K5) -- see run log', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
