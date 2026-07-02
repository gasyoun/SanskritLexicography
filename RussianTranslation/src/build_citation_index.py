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
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ls_resolver as lsr  # noqa: E402

REPO = os.path.dirname(HERE)                       # RussianTranslation/
RU_STORE = os.path.join(HERE, 'pwg_ru_translated.jsonl')
OUT_MD = os.path.join(REPO, 'CITATION_SOURCES.md')
OUT_JSON = os.path.join(REPO, 'release', 'citation_sources.json')
OUT_UNCOVERED = os.path.join(REPO, 'UNCOVERED_SOURCES.md')
OUT_UNCOVERED_JSON = os.path.join(REPO, 'release', 'uncovered_sources.json')

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
    groups = defaultdict(lambda: {'total': 0, 'resolved': 0, 'scan': 0, 'html': 0,
                                   'sample_url': None, 'sample_ref': None,
                                   'repos': set(), 'templates': set()})
    total = resolved = 0
    counts = {'scan': 0, 'html': 0}
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
            t = lsr.link_type(url)
            g[t] = g.get(t, 0) + 1
            counts[t] = counts.get(t, 0) + 1
            repo, templ = host_repo(url)
            g['repos'].add(repo)
            g['templates'].add(templ)
            if g['sample_url'] is None:
                g['sample_url'] = url
                g['sample_ref'] = ((n_attr or '') + vis).strip()
    return groups, total, resolved, counts


def emit(groups, total, resolved, counts):
    rows = sorted(groups.items(), key=lambda kv: (-kv[1]['total'], kv[0]))
    scan_n, html_n = counts.get('scan', 0), counts.get('html', 0)
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    data = {
        'total_distinct_refs': total, 'resolved': resolved,
        'resolved_scan': scan_n, 'resolved_html': html_n,
        'coverage_pct': round(100 * resolved / total, 1) if total else 0,
        'distinct_abbreviations': len(groups),
        'abbreviations': [{
            'abbr': k, 'total': v['total'], 'resolved': v['resolved'],
            'scan': v['scan'], 'html': v['html'],
            'repos': sorted(v['repos']), 'sample_ref': v['sample_ref'],
            'sample_url': v['sample_url'],
        } for k, v in rows],
    }
    with open(OUT_JSON, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    def pct(n):
        return 100 * n / total if total else 0

    unresolved_rows = [(k, v) for k, v in rows if v['resolved'] < v['total']]
    L = []
    L.append('# PWG citation sources — abbreviation → source-link index')
    L.append('')
    L.append('_Auto-generated by build_citation_index.py — do not edit by hand._')
    L.append('')
    L.append('Every `<ls>` literary-source citation in the PWG article corpus '
             '(the roots published at '
             '[gasyoun.github.io/SanskritLexicography]'
             '(https://gasyoun.github.io/SanskritLexicography/)), grouped by '
             'source abbreviation, with the Cologne target each links to. A '
             'target is either a **scan** (photographed book pages, on '
             '`sanskrit-lexicon-scans.github.io` or the Cologne westergaard '
             'Dhātupāṭha viewer) or **HTML** (rendered digital text — the '
             '`rvlinks`/`avlinks` hymn pages and external `ashtadhyayi.com` '
             'Pāṇini sūtras). Links are generated by [`ls_resolver.py`]'
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
    L.append('| resolved to a source link | %d (%.1f%%) |' % (resolved, pct(resolved)))
    L.append('| &nbsp;&nbsp;• to a scan (page image) | %d (%.1f%%) |' % (scan_n, pct(scan_n)))
    L.append('| &nbsp;&nbsp;• to HTML (digital text) | %d (%.1f%%) |' % (html_n, pct(html_n)))
    L.append('| unresolved | %d |' % (total - resolved))
    L.append('| distinct abbreviations | %d |' % len(groups))
    L.append('')
    L.append('> **Coverage is target-limited, not resolver-limited.** The resolver '
             'implements essentially the full mapping set the Cologne app itself '
             'supports; most unresolved references cite works the Cologne project '
             'has **not digitized** (no scan repository exists — e.g. Suśruta, most '
             'Upaniṣads, the Śrauta/Gṛhya sūtras, several chrestomathies), so they '
             'cannot be linked from anywhere.')
    L.append('')
    L.append('> The most-cited uncovered works are ranked (by how often each is '
             'actually cited) in [`UNCOVERED_SOURCES.md`]'
             '(https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/UNCOVERED_SOURCES.md), '
             'regenerated on every build.')
    L.append('')
    L.append('## Abbreviation index')
    L.append('')
    L.append('| abbreviation | refs | resolved | scan | HTML | target | example |')
    L.append('|---|---:|---:|---:|---:|---|---|')
    for k, v in rows:
        repos = ', '.join(sorted(v['repos'])) or '—'
        if v['sample_url']:
            ex = '[%s](%s)' % (v['sample_ref'] or v['sample_url'], v['sample_url'])
        else:
            ex = '—'
        L.append('| %s | %d | %d | %d | %d | %s | %s |' %
                 (k.replace('|', '\\|'), v['total'], v['resolved'],
                  v['scan'], v['html'], repos, ex))
    L.append('')
    if unresolved_rows:
        L.append('## Unresolved abbreviations (no Cologne target yet)')
        L.append('')
        L.append('These citations render as plain (dim) text on the site because no '
                 'source mapping resolved them — either no scan/HTML exists in the '
                 'Cologne ecosystem, or they are grammatical authorities/cross-refs '
                 'that are not linkable. Candidates for the PWG `<ls>` link-target '
                 'program (Dictionary-to-Book) where a scan does exist.')
        L.append('')
        L.append('| abbreviation | unresolved refs |')
        L.append('|---|---:|')
        for k, v in sorted(unresolved_rows, key=lambda kv: -(kv[1]['total'] - kv[1]['resolved'])):
            L.append('| %s | %d |' % (k.replace('|', '\\|'), v['total'] - v['resolved']))
        L.append('')
    L.append('_Dr. Mārcis Gasūns_')
    with open(OUT_MD, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')


# ---------------------------------------------------------------------------
# Occurrence analysis (how OFTEN each source is cited, vs how many DISTINCT refs)
# ---------------------------------------------------------------------------
# The distinct-ref counts above measure the *reference set*. To measure how
# often a source is actually cited we count every <ls> as it appears in the
# displayed corpus. That corpus is the build_article_site union model (RU∪EN
# deduplicated per sense) — counting the raw stores instead would multiply by
# the DE/RU/EN fields and the store overlap. We read the raw DE source per
# displayed sense (de_raw), which keeps the <ls n="..."> attribute, so a bare
# continuation inherits its parent work and grouping uses the true prefix.


def occurrence_stats():
    """Count every <ls> as it appears on the displayed DE surface (occurrences).

    Returns (occ_scan, occ_html, per, total) where per[abbr] = {'res','unres'}
    occurrence counts. An abbreviation with res==0 is *truly uncovered* (no
    occurrence resolves anywhere → no Cologne target); res>0 with unres>0 is a
    resolution edge-case (the work is digitized, a few refs are malformed)."""
    sys.path.insert(0, os.path.join(HERE, 'pilot'))
    import build_article_site as bas
    model = bas.build_model()
    occ_scan = occ_html = total = labels = 0
    per = defaultdict(lambda: {'res': 0, 'unres': 0})
    for r in model:
        for sc in r['subcards']:
            for s in sc['senses']:
                for m in _LS.finditer(s.get('de_raw') or ''):
                    total += 1
                    nm = _N_ATTR.search(m.group(1) or '')
                    n_attr = nm.group(1) if nm else None
                    vis = (m.group(2) or '').strip()
                    try:
                        url = lsr.generate_href('pwg', n_attr, vis)
                    except Exception:
                        url = None
                    t = lsr.link_type(url)
                    if t == 'scan':
                        occ_scan += 1
                        per[abbr_of(n_attr, vis)]['res'] += 1
                    elif t == 'html':
                        occ_html += 1
                        per[abbr_of(n_attr, vis)]['res'] += 1
                    elif not re.search(r'[0-9]', (n_attr or '') + vis):
                        # <ls> with no coordinate = an edition/cross-ref LABEL
                        # ("ed. Bomb.", "ebend."), never a linkable reference.
                        labels += 1
                    else:
                        per[abbr_of(n_attr, vis)]['unres'] += 1
    return occ_scan, occ_html, per, total, labels


def emit_uncovered(per, occ_scan, occ_html, occ_total, labels):
    """Live list of the most-cited sources with NO link, most frequent first.

    `per[abbr] = {'res','unres'}`. Truly-uncovered = res==0 (no target exists);
    edge-cases (res>0, unres>0) are listed separately — the work is digitized,
    only some refs are malformed."""
    uncovered = {k: v['unres'] for k, v in per.items() if v['res'] == 0 and v['unres'] > 0}
    edge = {k: v['unres'] for k, v in per.items() if v['res'] > 0 and v['unres'] > 0}
    rows = sorted(uncovered.items(), key=lambda kv: (-kv[1], kv[0]))
    un_total = sum(uncovered.values())
    occ_resolved = occ_scan + occ_html
    data = {
        'occurrences_total': occ_total,
        'occurrences_linked': occ_resolved,
        'occurrences_scan': occ_scan, 'occurrences_html': occ_html,
        'occurrences_uncovered': un_total,
        'occurrences_noncoordinate_labels': labels,
        'distinct_uncovered_works': len(uncovered),
        'uncovered': [{'abbr': k, 'occurrences': n} for k, n in rows],
        'edge_case_misses': [{'abbr': k, 'unresolved': n}
                             for k, n in sorted(edge.items(), key=lambda kv: -kv[1])],
    }
    with open(OUT_UNCOVERED_JSON, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    L = []
    L.append('# PWG uncovered citation sources — most-cited works with no link')
    L.append('')
    L.append('_Auto-generated by build_citation_index.py — do not edit by hand._')
    L.append('')
    L.append('Works cited by `<ls>` in the PWG article corpus that **have no Cologne '
             'target at all** — *no* occurrence resolves, because no scan repo exists '
             'in the [`sanskrit-lexicon-scans`](https://github.com/orgs/sanskrit-lexicon-scans/repositories) '
             'org (or the abbreviation is a grammatical authority / cross-reference, '
             'not a citable text). Ranked by **how often the work is actually cited** '
             '(occurrences on the displayed DE surface), most-cited first — so the top '
             'rows are the highest-value targets should Cologne ever digitize them. '
             'Regenerated on every build by [`build_citation_index.py`]'
             '(https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_citation_index.py).')
    L.append('')
    L.append('Of **%s** citation occurrences on the site, **%s** link out '
             '(%s scan + %s HTML) and **%s (%.1f%%)** stay unlinked. The unlinked '
             'ones are **%d truly-uncovered works** below (%s occurrences), plus %d '
             'edge-case misses in otherwise-covered works (see end) and %s '
             'non-coordinate `<ls>` labels (edition/cross-ref notes like '
             '"ed. Bomb.", never linkable).'
             % (f'{occ_total:,}', f'{occ_resolved:,}', f'{occ_scan:,}', f'{occ_html:,}',
                f'{occ_total - occ_resolved:,}', 100 * (occ_total - occ_resolved) / occ_total if occ_total else 0,
                len(uncovered), f'{un_total:,}', sum(edge.values()), f'{labels:,}'))
    L.append('')
    L.append('| rank | source (abbreviation) | citations |')
    L.append('|---:|---|---:|')
    for i, (k, n) in enumerate(rows, 1):
        L.append('| %d | %s | %d |' % (i, k.replace('|', '\\|'), n))
    L.append('')
    if edge:
        L.append('## Edge-case misses (work IS digitized; some refs malformed)')
        L.append('')
        L.append('These abbreviations resolve for most citations — the counts below '
                 'are individual references with a malformed/unusual coordinate that '
                 'the resolver could not parse. Not "uncovered".')
        L.append('')
        L.append('| source | unresolved refs |')
        L.append('|---|---:|')
        for k, n in sorted(edge.items(), key=lambda kv: -kv[1]):
            L.append('| %s | %d |' % (k.replace('|', '\\|'), n))
        L.append('')
    L.append('_Dr. Mārcis Gasūns_')
    with open(OUT_UNCOVERED, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')


def main():
    groups, total, resolved, counts = build()
    emit(groups, total, resolved, counts)
    occ_scan, occ_html, per, occ_total, labels = occurrence_stats()
    emit_uncovered(per, occ_scan, occ_html, occ_total, labels)
    occ_resolved = occ_scan + occ_html
    print('citation index: %d distinct refs, %d resolved (%.1f%%), %d abbreviations'
          % (total, resolved, 100 * resolved / total if total else 0, len(groups)))
    print('  -> %s' % OUT_MD)
    print('  -> %s' % OUT_JSON)
    print('occurrences (displayed DE surface): %d total, %d linked '
          '(scan %d / HTML %d), %d unlinked'
          % (occ_total, occ_resolved, occ_scan, occ_html, occ_total - occ_resolved))
    if occ_resolved:
        print('  scan:HTML by occurrence = %.1f : 1  (by distinct ref = %.1f : 1)'
              % (occ_scan / occ_html if occ_html else 0,
                 counts['scan'] / counts['html'] if counts['html'] else 0))
    print('  -> %s' % OUT_UNCOVERED)


if __name__ == '__main__':
    main()
