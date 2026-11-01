#!/usr/bin/env python3
"""FINDINGS.md supersession DAG (H7594).

Parses the registry's supersession relations into machine-readable form and
builds per-topic chains with the CURRENT leaf verdict:

* explicit relations - "SUPERSEDED/extended/refuted/closed by Sec-N|H####"
  (targets may be a markdown link), and "extends Sec-N"
* header blurbs - the "Sec-N - ..." / "prior: Sec-N - ..." changelog trail on
  the dated header line attributes the relation to the Sec-N named before it
* in-place annotations - "**SUPERSEDED IN PART (H####, date):**" and
  "**Warning Update date (H####) -" notes inside a finding's own body
* builds-on citations - a later finding's narrow reference to an earlier
  verdict it extends ("Sec-N refuted ...", "the Sec-N verdict survives",
  "code path Sec-N built") - this links 458->650 and 447->453.

Stale-pointer flag (the 103->451 index-row defect class found 01-11): an
index row citing a Sec that no longer exists (renumber ghost), an index
anchor drifted beyond slugger dialect from its heading, or a supersession
edge naming a nonexistent Sec. --check exits 1 on any of these; --selftest
pins the four known chains on the real FINDINGS.md.

Usage:  python tools/findings_supersession.py            write data/findings_supersession.json
        python tools/findings_supersession.py --check    exit 1 on any stale pointer
        python tools/findings_supersession.py --selftest known-chain selftest, exit 1 on fail
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
FINDINGS_PATH = REPO / 'FINDINGS.md'
OUT_PATH = REPO / 'data' / 'findings_supersession.json'

HEADING_RE = re.compile(r'^### §(\d+)\. (.*)$', re.M)
INDEX_ROW_RE = re.compile(
    r'^\s*-\s*(🔴|🟠|🟡|🟢)\s*\[§(\d+)\. (.*?)\]\(#([^)]*)\)', re.M)
RELATION_RE = re.compile(
    r'\b(SUPERSEDED(?:\s+IN PART)?|superseded(?:\s+in part)?|EXTENDED|extended'
    r'|REFUTED|refuted|CLOSED|closed)\b'
    r'[^.\n]{0,80}?by\s+(?:\[\s*)?(?:§(\d+)|(H\d+))', re.S)
EXTENDS_RE = re.compile(r'\bextends\s+(?:\[\s*)?§(\d+)', re.I)
IN_PLACE_RE = re.compile(
    r'\*\*\s*(?:⚠️\s*)?(?:SUPERSEDED(?:\s+IN PART)?|Update\s+(\d{2}-\d{2}-\d{4}))\s*'
    r'\(?\s*(H\d{4})?')
ANNOTATED_IN_PLACE_RE = re.compile(r'annotated in-place by\s+(H\d{4})')
HEADER_SUBJECT_RE = re.compile(
    r'prior:\s*§(\d+)\b'
    r'|§(\d+)\s*(?:—|–|-(?=\s))'
    r'|§(\d+)\s+(?:SUPERSEDED|superseded|EXTENDED|extended'
    r'|REFUTED|refuted|CLOSED|closed)\b')
BUILDS_ON_RE = re.compile(
    r'§(\d+)\s+(?:refuted|refines|established)\b'
    r'|(?:the|The)\s+§(\d+)\s+verdict'
    r'|code path\s+§(\d+)\s+built')


def slugify(text):
    """Same slug rule as build_findings_data.py - anchor-drift comparison base."""
    s = text.lower()
    s = re.sub(r'[^\w\s-]', '', s)
    return s.replace(' ', '-')


def parse_findings(md_text):
    """{n: {'title', 'anchor'}} in file order, from ### Sec-N. headings."""
    out = {}
    for m in HEADING_RE.finditer(md_text):
        n, title = int(m.group(1)), m.group(2).strip()
        out[n] = {'title': title, 'anchor': slugify(f'{n}. {title}')}
    return out


def parse_index_rows(md_text):
    """Index bullets: [{'n', 'dot', 'title', 'anchor'}] - the 103-ghost-row surface."""
    rows = []
    for m in INDEX_ROW_RE.finditer(md_text):
        rows.append({'n': int(m.group(2)), 'dot': m.group(1),
                     'title': m.group(3).strip(), 'anchor': m.group(4)})
    return rows


def _findings_spans(md_text):
    """[(n, start, end)] body spans - end at the next ###/## heading."""
    heads = [(int(m.group(1)), m.start(), m.end()) for m in HEADING_RE.finditer(md_text)]
    spans = []
    for i, (n, s, e) in enumerate(heads):
        nxt = heads[i + 1][1] if i + 1 < len(heads) else len(md_text)
        tail = md_text[e:nxt]
        m2 = re.search(r'^##(?!#)\s', tail, re.M)
        span_end = e + (m2.start() if m2 else len(tail))
        spans.append((n, e, span_end))
    return spans


def _index_spans(md_text, findings):
    """[(n, start, end)] index-row spans covering the WHOLE row line."""
    spans = []
    for m in INDEX_ROW_RE.finditer(md_text):
        n = int(m.group(2))
        if n in findings:
            eol = md_text.find('\n', m.start())
            spans.append((n, m.start(), len(md_text) if eol == -1 else eol))
    return spans


def _subject_at(md_text, pos, spans, index_spans, findings):
    """Subject Sec of an annotation: index row, then body span, then header scan."""
    for n, s, e in index_spans:
        if s <= pos < e:
            return n, 'index'
    for n, s, e in spans:
        if s <= pos < e:
            return n, 'body'
    head = md_text[:pos]
    best = None
    for m in HEADER_SUBJECT_RE.finditer(head):
        n = next(int(g) for g in m.groups() if g)
        if n in findings:
            best = n
    return best, 'header'


def parse_supersession(md_text):
    """Extract edges, in-place annotations, chains and flags from FINDINGS.md."""
    findings = parse_findings(md_text)
    if not findings:
        raise SystemExit('REFUSED: 0 findings (no ### Sec headings) - malformed registry')
    spans = _findings_spans(md_text)
    index_spans = _index_spans(md_text, findings)
    edges, in_place, prose_superseded = [], [], []

    def add_edge(subject, rel, target, pos, quote):
        if subject is None:
            return
        edges.append({
            'from': subject, 'to': target, 'relation': rel,
            'line': md_text.count(chr(10), 0, pos) + 1, 'quote': quote[:140]})

    for m in RELATION_RE.finditer(md_text):
        subject, zone = _subject_at(md_text, m.start(), spans, index_spans, findings)
        kw = re.sub(r'\s+', ' ', m.group(1)).lower()
        rel = ('superseded_by' if 'supersed' in kw
               else 'refuted_by' if 'refut' in kw
               else 'extended_by' if 'extend' in kw else 'closed_by')
        target = f'§{m.group(2)}' if m.group(2) else (m.group(3) or None)
        if target:
            add_edge(subject, rel, target, m.start(), m.group(0))
        else:
            prose_superseded.append({'n': subject,
                                     'line': md_text.count(chr(10), 0, m.start()) + 1,
                                     'quote': m.group(0)[:140]})

    for m in EXTENDS_RE.finditer(md_text):
        subject, _ = _subject_at(md_text, m.start(), spans, index_spans, findings)
        add_edge(subject, 'extends', f'§{m.group(1)}', m.start(), m.group(0))

    for m in BUILDS_ON_RE.finditer(md_text):
        subject, _ = _subject_at(md_text, m.start(), spans, index_spans, findings)
        target_n = int(next(g for g in m.groups() if g))
        if subject is not None and subject != target_n:
            add_edge(subject, 'builds_on', f'§{target_n}', m.start(), m.group(0))

    for m in IN_PLACE_RE.finditer(md_text):
        subject, zone = _subject_at(md_text, m.start(), spans, index_spans, findings)
        if zone != 'body' or subject is None:
            continue
        kind = 'update_note' if m.group(1) else 'superseded_in_place'
        in_place.append({'n': subject, 'handoff': m.group(2), 'kind': kind,
                         'line': md_text.count(chr(10), 0, m.start()) + 1,
                         'quote': m.group(0)[:140]})

    for m in ANNOTATED_IN_PLACE_RE.finditer(md_text):
        subject, _ = _subject_at(md_text, m.start(), spans, index_spans, findings)
        if subject is None:
            continue
        in_place.append({'n': subject, 'handoff': m.group(1), 'kind': 'annotated_in_place',
                         'line': md_text.count(chr(10), 0, m.start()) + 1,
                         'quote': m.group(0)[:140]})

    index_rows = parse_index_rows(md_text)
    flags = check_flags(findings, index_rows, edges)

    return {
        'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'findings_count': len(findings),
        'edges': edges, 'in_place': in_place,
        'prose_superseded': prose_superseded,
        'chains': build_chains(findings, edges), 'flags': flags,
    }


def build_chains(findings, edges):
    """Walk edges into chains stale -> current. Passive relations
    (superseded_by/refuted_by/extended_by/closed_by) name the STALE subject;
    active ones (extends/builds_on) name the SUCCESSOR as subject. H-targets
    never join a chain."""
    succ, rels = {}, {}
    for e in edges:
        if not (isinstance(e['to'], str) and e['to'].startswith('§')):
            continue
        to_n = int(e['to'][1:])
        if e['relation'] in ('extends', 'builds_on'):
            pred, succ_n = to_n, e['from']
        else:
            pred, succ_n = e['from'], to_n
        succ.setdefault(pred, set()).add(succ_n)
        rels[(pred, succ_n)] = e['relation']
    chains, seen = [], set()
    for root in sorted(succ):
        if root in seen or any(root in s for s in succ.values()):
            continue
        chain, cur, fork = [root], root, False
        while cur in succ:
            nxts = sorted(succ[cur])
            if len(nxts) > 1:
                fork = True
            cur = nxts[0]
            if cur in chain:  # cycle guard
                fork = True
                break
            chain.append(cur)
        seen.update(chain)
        chains.append({'chain': chain, 'leaf': cur, 'fork': fork,
                       'relations': [rels.get((chain[i], chain[i + 1]), '?')
                                     for i in range(len(chain) - 1)]})
    return chains


def _norm_anchor(anchor):
    """Slugger-dialect-insensitive anchor compare: index slugs came from a
    different slugger than headings (dropped underscores, collapsed dashes);
    compare modulo dialect so only real title drift flags."""
    a = anchor.replace('_', '')
    return re.sub(r'-+', '-', a)


def check_flags(findings, index_rows, edges):
    """Stale-pointer flag: ghost index rows (103->451 class), stale index
    titles (anchor drift beyond slugger dialect), dangling Sec-targets."""
    ghost_rows = [r for r in index_rows if r['n'] not in findings]
    anchor_drift = [
        {'n': r['n'], 'index_anchor': r['anchor'], 'heading_anchor': findings[r['n']]['anchor']}
        for r in index_rows
        if r['n'] in findings
        and _norm_anchor(r['anchor']) != _norm_anchor(findings[r['n']]['anchor'])]
    dangling = sorted({e['to'] for e in edges
                       if isinstance(e['to'], str) and e['to'].startswith('§')
                       and int(e['to'][1:]) not in findings})
    return {'ghost_index_rows': [{'n': r['n'], 'title': r['title']} for r in ghost_rows],
            'anchor_drift': anchor_drift,
            'dangling_edge_targets': dangling}


def chain_panels(sup, findings):
    """Dashboard payload: chains with leaf metadata + in-place + handoff edges."""
    in_place_by_n = {}
    for a in sup['in_place']:
        in_place_by_n.setdefault(a['n'], []).append(
            {'handoff': a['handoff'], 'kind': a['kind']})
    panels = []
    for c in sup['chains']:
        leaf = c['leaf']
        meta = findings.get(leaf, {})
        panels.append({
            'chain': c['chain'], 'leaf': leaf, 'fork': c['fork'],
            'leaf_title': meta.get('title', ''), 'leaf_anchor': meta.get('anchor', ''),
            'relations': c['relations'],
            'in_place': [{'n': n, **a} for n in c['chain'] for a in in_place_by_n.get(n, [])],
        })
    chain_nodes = {x for c in sup['chains'] for x in c['chain']}
    lone = sorted({a['n'] for a in sup['in_place'] if a['n'] not in chain_nodes})
    handoff_edges = [
        {'n': e['from'], 'handoff': e['to'], 'relation': e['relation']}
        for e in sup['edges']
        if isinstance(e['to'], str) and e['to'].startswith('H')]
    return {'chains': panels,
            'lone_in_place': [{'n': n, **a} for n in lone for a in in_place_by_n[n]],
            'handoff_edges': handoff_edges,
            'flags': sup['flags']}


def selftest(sup):
    """Known-chain selftest (H7594): the four textual anchors on real data."""
    checks = []

    def ok(name, cond):
        checks.append((name, bool(cond)))

    in_place = {(a['n'], a['handoff']) for a in sup['in_place'] if a['handoff']}

    def chain_containing(n):
        return next((c for c in sup['chains'] if n in c['chain']), None)

    c40 = chain_containing(40)
    ok('Sec 40: in-place annotation by H7497 present', (40, 'H7497') in in_place)
    c458 = chain_containing(458)
    ok('458->650 edge present', c458 is not None and 650 in c458['chain'])
    ok('458-chain leaf = 650 (CURRENT)', c458 is not None and c458['leaf'] == 650)
    c447 = chain_containing(447)
    ok('447->453 edge present', c447 is not None and 453 in c447['chain'])
    ok('447-chain leaf = 453 (CURRENT)', c447 is not None and c447['leaf'] == 453)
    c508 = chain_containing(508)
    ok('508->651 edge present', c508 is not None and 651 in c508['chain'])
    ok('508-chain leaf = 651 (CURRENT)', c508 is not None and c508['leaf'] == 651)
    ok('Sec 465: in-place update note by H1670 present', (465, 'H1670') in in_place)
    ok('stale-pointer flag clean', not any(
        sup['flags'][k] for k in ('ghost_index_rows', 'anchor_drift', 'dangling_edge_targets')))

    for name, cond in checks:
        print(f'  {"PASS" if cond else "FAIL"}  {name}')
    failed = [n for n, c in checks if not c]
    print(f'SELFTEST {"FAIL: " + str(len(failed)) + " of " + str(len(checks)) + " failed" if failed else "PASS: " + str(len(checks)) + "/" + str(len(checks)) + " checks"}')
    return 1 if failed else 0


def write_json(sup, findings):
    """data/findings_supersession.json - sole writer; called standalone and by
    findings_dashboard/build_findings_data.py (the monthly refresh's build step)."""
    out = dict(sup)
    out['panels'] = chain_panels(sup, findings)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'{OUT_PATH.relative_to(REPO)}: {out["findings_count"]} findings, '
          f'{len(out["edges"])} edges, {len(out["chains"])} chains, '
          f'{len(out["in_place"])} in-place annotations, '
          f'{sum(len(v) for v in out["flags"].values())} flags')


def main(argv):
    md_path = Path(argv[argv.index('--md') + 1]) if '--md' in argv else FINDINGS_PATH
    md = md_path.read_text(encoding='utf-8')
    sup = parse_supersession(md)
    findings = parse_findings(md)
    if '--selftest' in argv:
        return selftest(sup)
    if '--check' in argv:
        f = sup['flags']
        for row in f['ghost_index_rows']:
            print(f"FLAG ghost index row: Sec-{row['n']} '{row['title'][:60]}'"
                  ' - no such finding (renumber ghost, 103->451 class)')
        for row in f['anchor_drift']:
            print(f"FLAG anchor drift: Sec-{row['n']} index anchor differs from heading")
        for t in f['dangling_edge_targets']:
            print(f'FLAG dangling edge target: {t} - no such finding')
        if any(f[k] for k in ('ghost_index_rows', 'anchor_drift', 'dangling_edge_targets')):
            return 1
        print(f'CHECK PASS: {len(findings)} findings, {len(sup["edges"])} edges, '
              f'{len(sup["chains"])} chains, {len(sup["in_place"])} in-place annotations'
              ' - zero stale pointers')
        return 0
    write_json(sup, findings)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
