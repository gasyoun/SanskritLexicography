#!/usr/bin/env python3
"""Build the FINDINGS dashboard data files.

Parses FINDINGS.md into findings_dashboard/data.json (per-finding metadata:
number, title, section, importance dot, evidence date, staleness, anchor) and
appends a monthly metrics snapshot to findings_dashboard/timeseries.json.

Metric collectors read the local sibling repo when present (this machine) and
fall back to raw.githubusercontent.com (GitHub Actions). Every collector is
optional: a parse/network failure records null and never aborts the build.

Run from anywhere:  python findings_dashboard/build_findings_data.py
"""

import json
import re
import sys
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SIBLINGS = REPO.parent  # C:\Users\user\Documents\GitHub on the local machine

IMPORTANCE = {'🔴': 3, '🟠': 2, '🟡': 1}
FINDINGS_URL = 'https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md'
STALE_DAYS = 180


def slugify(text):
    s = text.lower()
    s = re.sub(r'[^\w\s-]', '', s)
    return s.replace(' ', '-')


def parse_index_importance(md_text):
    """{finding number -> importance int} read from the `## Index` bullets, which
    are the canonical importance source (34 findings carry their dot ONLY here, not
    in the body). H1361: the Index is kept complete, so this classifies every finding."""
    m = re.search(r'^##\s+Index\s*$', md_text, re.M)
    if not m:
        return {}
    rest = md_text[m.end():]
    nxt = re.search(r'^##\s+(?!Index)', rest, re.M)
    idx = rest[:nxt.start()] if nxt else rest
    out = {}
    for line in idx.split('\n'):
        em = re.match(r'^\s*-\s*(🔴|🟠|🟡)\s*\[§(\d+)\.', line)
        if em:
            out[int(em.group(2))] = IMPORTANCE[em.group(1)]
    return out


def parse_findings(md_text):
    lines = md_text.split('\n')
    index_imp = parse_index_importance(md_text)
    findings, section = [], None
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('## ') and line != '## Index':
            section = line[3:].strip()
        m = re.match(r'^### §(\d+)\. (.*)$', line)
        if m:
            n, title = int(m.group(1)), m.group(2).strip()
            # claim line = first non-blank line after the heading
            j = i + 1
            while j < len(lines) and lines[j].strip() == '':
                j += 1
            # scan the block for the Source blockquote date tag
            block_end = j
            while block_end < len(lines) and not lines[block_end].startswith(('### ', '## ')):
                block_end += 1
            # importance: Index dot (canonical) first, then first dot anywhere in the body
            imp = index_imp.get(n)
            if imp is None:
                for bl in lines[j:block_end]:
                    c = next((ch for ch in bl if ch in IMPORTANCE), None)
                    if c:
                        imp = IMPORTANCE[c]
                        break
            dates = re.findall(r'·\s*(\d{4}-\d{2}(?:-\d{2})?)',
                               '\n'.join(l for l in lines[j:block_end] if l.startswith('> ')))
            evid = dates[-1] if dates else None
            age = None
            if evid:
                d = evid if len(evid) == 10 else evid + '-15'
                try:
                    age = (date.today() - datetime.strptime(d, '%Y-%m-%d').date()).days
                except ValueError:
                    pass
            anchor = slugify(f'{n}. {title}')
            findings.append({
                'n': n, 'title': title, 'section': section, 'importance': imp,
                'evidence_date': evid, 'age_days': age,
                'url': f'{FINDINGS_URL}#{anchor}',
            })
            i = block_end - 1
        i += 1
    return findings


def read_source(local_rel, raw_url):
    """Local sibling file first, raw.githubusercontent.com fallback."""
    p = SIBLINGS / local_rel
    try:
        if p.exists():
            return p.read_text(encoding='utf-8')
    except OSError:
        pass
    try:
        with urllib.request.urlopen(raw_url, timeout=20) as r:
            return r.read().decode('utf-8')
    except Exception as e:
        print(f'  collector miss: {raw_url} ({e.__class__.__name__})')
        return None


def rx(pattern, text):
    if text is None:
        return None
    m = re.search(pattern, text)
    return float(m.group(1)) if m else None


def collect_metrics():
    m = {}
    m['dcs_cdsl_linkage_pct'] = rx(
        r'\(([\d.]+)%\) linked to wf0',
        read_source('csl-apidev/simple-search/dcs_xref/readme.md',
                    'https://raw.githubusercontent.com/sanskrit-lexicon/csl-apidev/master/simple-search/dcs_xref/readme.md'))
    m['glossary_vidyut_coverage_pct'] = rx(
        r'\+ Vidyut fallback[^|]*\|[^|]*\|\s*([\d.]+)\s*%',
        read_source('SanskritLexicography/RussianTranslation/glossary/README.md',
                    'https://raw.githubusercontent.com/gasyoun/SanskritLexicography/master/RussianTranslation/glossary/README.md'))
    m['pwg_citation_coverage_pct'] = rx(
        r'\*\*covered\*\*[^|]*\|[^|]*\|\s*([\d.]+)%',
        read_source('PWG/pwg_ls/pwg_ru_coverage/COVERAGE_COMPARISON.md',
                    'https://raw.githubusercontent.com/sanskrit-lexicon/PWG/main/pwg_ls/pwg_ru_coverage/COVERAGE_COMPARISON.md'))
    tsv = read_source('SanskritSpellCheck/corrections_draft/file_first_verified.tsv',
                      'https://raw.githubusercontent.com/drdhaval2785/SanskritSpellCheck/master/corrections_draft/file_first_verified.tsv')
    if tsv:
        rows = [l.split('\t') for l in tsv.split('\n')
                if l.strip() and not l.startswith('#')]
        if rows and rows[0][:1] == ['dict']:
            hdr, data = rows[0], rows[1:]
            vi, di = hdr.index('verdict'), hdr.index('dict')
            verdicts, per_dict_pass = {}, {}
            for r in data:
                if len(r) <= max(vi, di):
                    continue
                v = r[vi].strip()
                verdicts[v] = verdicts.get(v, 0) + 1
                if v == 'PASS':
                    per_dict_pass[r[di]] = per_dict_pass.get(r[di], 0) + 1
            m['queue_verdicts'] = verdicts
            m['queue_pass_by_dict'] = per_dict_pass
            drop = verdicts.get('DROP', 0)
            total = sum(verdicts.values())
            m['queue_decay_pct'] = round(100 * drop / total, 2) if total else None
    return m


def main():
    md = (REPO / 'FINDINGS.md').read_text(encoding='utf-8')
    findings = parse_findings(md)
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    by_imp = {}
    for f in findings:
        k = str(f['importance'])
        by_imp[k] = by_imp.get(k, 0) + 1
    stale = [f['n'] for f in findings if (f['age_days'] or 0) > STALE_DAYS]

    data = {'generated_at': now, 'stale_days_threshold': STALE_DAYS,
            'counts': {'total': len(findings), 'by_importance': by_imp,
                       'stale': len(stale)},
            'findings': findings}
    (HERE / 'data.json').write_text(
        json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'data.json: {len(findings)} findings, {len(stale)} stale (> {STALE_DAYS}d)')

    print('collecting metrics …')
    metrics = collect_metrics()
    snap = {'date': date.today().isoformat(), 'source': 'build',
            'metrics': metrics,
            'registry': {'total': len(findings), 'by_importance': by_imp,
                         'stale': len(stale)}}
    ts_path = HERE / 'timeseries.json'
    ts = {'snapshots': []}
    if ts_path.exists():
        ts = json.loads(ts_path.read_text(encoding='utf-8'))
    month = snap['date'][:7]
    ts['snapshots'] = [s for s in ts['snapshots']
                       if not (s['source'] == 'build' and s['date'][:7] == month)]
    ts['snapshots'].append(snap)
    ts['snapshots'].sort(key=lambda s: s['date'])
    ts_path.write_text(json.dumps(ts, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'timeseries.json: {len(ts["snapshots"])} snapshots; this month: '
          + json.dumps({k: v for k, v in metrics.items() if not isinstance(v, dict)}))


if __name__ == '__main__':
    main()
