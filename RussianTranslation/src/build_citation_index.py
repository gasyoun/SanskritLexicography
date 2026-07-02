#!/usr/bin/env python
r"""Document every <ls> literary-source citation in the PWG article corpus and
report how many resolve to a Cologne scan page.

Reads the same stores the article site is built from
(`pwg_ru_translated.jsonl` DE/RU fields + `wf_output.en.<root>.json` german/
english), extracts each `<ls n="PREFIX">VISIBLE</ls>` citation, resolves it via
`ls_resolver` (PWG paths), and writes:

  * RussianTranslation/CITATION_SOURCES.md  -- human-readable index:
      abbreviation -> scan repo + example URL, occurrences, resolved %
      + a coverage summary and the top unresolved abbreviations.
  * RussianTranslation/release/citation_sources.json -- the same data, machine-readable.

  python src/build_citation_index.py
"""
import glob
import json
import os
import re
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ls_resolver as lsr  # noqa: E402

REPO = os.path.dirname(HERE)                       # RussianTranslation/
RU_STORE = os.path.join(HERE, 'pwg_ru_translated.jsonl')
OUT_MD = os.path.join(REPO, 'CITATION_SOURCES.md')
OUT_JSON = os.path.join(REPO, 'release', 'citation_sources.json')

_LS = re.compile(r'<ls\b([^>]*)>(.*?)</ls>', re.S)
_N_ATTR = re.compile(r'\bn\s*=\s*"([^"]*)"')
# Abbreviation = leading run up to the first digit / the n= prefix, trimmed.
_ABBR = re.compile(r'^\s*([^0-9]*?)\s*[0-9]')


def abbr_of(n_attr, visible):
    """Human-meaningful grouping label: the source abbreviation. Prefer the n=
    prefix (carries the inherited work for bare-number continuation refs); fall
    back to the visible text."""
    for s in (n_attr, visible):
        if not s:
            continue
        m = _ABBR.match(s)
        if m and m.group(1).strip():
            return m.group(1).strip()
        if s.strip():
            return s.strip()
    return '?'


def iter_ls():
    """Yield (attrs, visible) for every <ls> in every DE/RU/EN source field."""
    if os.path.exists(RU_STORE):
        with open(RU_STORE, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                for fld in ('de', 'ru'):
                    for m in _LS.finditer(r.get(fld) or ''):
                        yield m.group(1), m.group(2)
    for fp in glob.glob(os.path.join(REPO, 'wf_output.en.*.json')):
        try:
            d = json.load(open(fp, encoding='utf-8'))
        except Exception:
            continue
        for e in d.get('results') or []:
            c = e.get('card')
            if not c:
                continue
            for rec in c.get('records') or []:
                for s in rec.get('senses') or []:
                    for fld in ('german', 'english'):
                        for m in _LS.finditer(s.get(fld) or ''):
                            yield m.group(1), m.group(2)


def host_repo(url):
    """Extract the scan-repo slug + a normalized template from a resolved URL."""
    m = re.match(r'https?://([^/]+)/([^?#]*)', url)
    if not m:
        return url, url
    host, path = m.group(1), m.group(2)
    repo = path.split('/')[0] if 'scans.github.io' in host or 'lexicon.github.io' in host else host
    templ = re.sub(r'[0-9]+', 'N', url)
    return repo, templ


def build():
    groups = defaultdict(lambda: {'total': 0, 'resolved': 0, 'sample_url': None,
                                   'sample_ref': None, 'repos': set(), 'templates': set()})
    total = resolved = 0
    seen = set()
    for attrs, visible in iter_ls():
        m = _N_ATTR.search(attrs or '')
        n_attr = m.group(1) if m else None
        vis = (visible or '').strip()
        key = (n_attr, vis)
        # de/ru/en repeat the same citations across senses; count DISTINCT refs
        # so the index measures the reference set, not sense multiplicity.
        if key in seen:
            continue
        seen.add(key)
        label = abbr_of(n_attr, vis)
        g = groups[label]
        g['total'] += 1
        total += 1
        try:
            url = lsr.generate_href('pwg', n_attr, vis)
        except Exception:
            url = None
        if url:
            g['resolved'] += 1
            resolved += 1
            repo, templ = host_repo(url)
            g['repos'].add(repo)
            g['templates'].add(templ)
            if g['sample_url'] is None:
                g['sample_url'] = url
                g['sample_ref'] = ((n_attr or '') + vis).strip()
    return groups, total, resolved


def emit(groups, total, resolved):
    rows = sorted(groups.items(), key=lambda kv: (-kv[1]['total'], kv[0]))
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    data = {
        'total_distinct_refs': total, 'resolved': resolved,
        'coverage_pct': round(100 * resolved / total, 1) if total else 0,
        'distinct_abbreviations': len(groups),
        'abbreviations': [{
            'abbr': k, 'total': v['total'], 'resolved': v['resolved'],
            'repos': sorted(v['repos']), 'sample_ref': v['sample_ref'],
            'sample_url': v['sample_url'],
        } for k, v in rows],
    }
    with open(OUT_JSON, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    unresolved_rows = [(k, v) for k, v in rows if v['resolved'] < v['total']]
    L = []
    L.append('# PWG citation sources — abbreviation → scan-page index')
    L.append('')
    L.append('<p align="right"><sub>Created: 02-07-2026 · Last updated: 02-07-2026</sub></p>')
    L.append('')
    L.append('Every `<ls>` literary-source citation in the PWG article corpus '
             '(the roots published at '
             '[gasyoun.github.io/SanskritLexicography]'
             '(https://gasyoun.github.io/SanskritLexicography/)), grouped by '
             'source abbreviation, with the Cologne scan repository each links '
             'to. Links are generated by [`ls_resolver.py`]'
             '(https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py) '
             '— a Python port of the canonical resolver in '
             '[`csl-app/lib/core/ls_service.dart`]'
             '(https://github.com/sanskrit-lexicon/csl-app/blob/main/lib/core/ls_service.dart).')
    L.append('')
    L.append('## Coverage')
    L.append('')
    L.append('| metric | value |')
    L.append('|---|---:|')
    L.append('| distinct citation references | %d |' % total)
    L.append('| resolved to a scan page | %d (%.1f%%) |' %
             (resolved, 100 * resolved / total if total else 0))
    L.append('| unresolved | %d |' % (total - resolved))
    L.append('| distinct abbreviations | %d |' % len(groups))
    L.append('')
    L.append('## Abbreviation index')
    L.append('')
    L.append('| abbreviation | refs | resolved | scan repo | example |')
    L.append('|---|---:|---:|---|---|')
    for k, v in rows:
        repos = ', '.join(sorted(v['repos'])) or '—'
        if v['sample_url']:
            ex = '[%s](%s)' % (v['sample_ref'] or v['sample_url'], v['sample_url'])
        else:
            ex = '—'
        L.append('| %s | %d | %d | %s | %s |' %
                 (k.replace('|', '\\|'), v['total'], v['resolved'], repos, ex))
    L.append('')
    if unresolved_rows:
        L.append('## Unresolved abbreviations (link target still missing)')
        L.append('')
        L.append('These citations render as plain (dim) text on the site because no '
                 'scan mapping resolved them — candidates for the PWG `<ls>` '
                 'link-target program (Dictionary-to-Book).')
        L.append('')
        L.append('| abbreviation | unresolved refs |')
        L.append('|---|---:|')
        for k, v in sorted(unresolved_rows, key=lambda kv: -(kv[1]['total'] - kv[1]['resolved'])):
            L.append('| %s | %d |' % (k.replace('|', '\\|'), v['total'] - v['resolved']))
        L.append('')
    L.append('<p align="right"><sub>Dr. Mārcis Gasūns</sub></p>')
    with open(OUT_MD, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')


def main():
    groups, total, resolved = build()
    emit(groups, total, resolved)
    print('citation index: %d distinct refs, %d resolved (%.1f%%), %d abbreviations'
          % (total, resolved, 100 * resolved / total if total else 0, len(groups)))
    print('  -> %s' % OUT_MD)
    print('  -> %s' % OUT_JSON)


if __name__ == '__main__':
    main()
