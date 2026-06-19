#!/usr/bin/env python
"""Collect the pilot workflow output → judge summary + side-by-side DE→RU review.

  python _pilot_collect.py <workflow-output.json>
"""
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from safe_filename import safe_name

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'pilot', 'output')
PROTECTED = {k for k in os.environ.get('PILOT_COLLECT_PROTECTED', '').split(',') if k}


def find_results(o):
    if isinstance(o, dict):
        if isinstance(o.get('results'), list):
            return o['results']
        for v in o.values():
            r = find_results(v)
            if r is not None:
                return r
    if isinstance(o, list):
        for v in o:
            r = find_results(v)
            if r is not None:
                return r
    return None


def render(res):
    lines = []
    c = res.get('card') or {}
    lines.append('# %s (%s)\n' % (c.get('key1', res.get('key')), c.get('iast', '')))
    for rec in c.get('records', []):
        lines.append('## homonym %s — %s\n' % (rec.get('h') or '–', rec.get('grammar', '')))
        lines.append('| # | German (PWG) | Russian | type | src | stratum |')
        lines.append('|---|---|---|---|---|---|')
        for s in rec.get('senses', []):
            lines.append('| %s) | %s | %s | %s | %s | %s |' % (
                s.get('tag', ''), (s.get('german', '') or '').replace('|', '/'),
                (s.get('russian', '') or '').replace('|', '/'),
                s.get('equivalence_type', ''), s.get('source_type', ''), s.get('stratum', '') or '–'))
            if s.get('differentia'):
                lines.append('| | **διφ:** %s | | | | |' % s['differentia'].replace('|', '/')[:400])
        lines.append('')
    if c.get('notes'):
        lines.append('> %s\n' % c['notes'])
    return '\n'.join(lines)


def main():
    wf = sys.argv[1]
    results = find_results(json.loads(open(wf, encoding='utf-8').read())) or []
    os.makedirs(OUT, exist_ok=True)
    print('=== PILOT JUDGE SUMMARY (%d cards) ===' % len(results))
    print('%-12s %-4s %-4s %-7s %-6s %-6s %-13s %s' %
          ('card', 'ok', 'sev', 'regist', 'sigla', 'cover', 'discrimin', 'issues'))
    npass = 0
    combined = []
    for res in results:
        k = res.get('key')
        j = res.get('judge') or {}
        ok = j.get('ok')
        npass += 1 if (ok and (j.get('severity') or 5) <= 2) else 0
        nsense = sum(len(r.get('senses', [])) for r in (res.get('card') or {}).get('records', []))
        print('%-12s %-4s %-4s %-7s %-6s %-6s %-13s %s' % (
            k, 'Y' if ok else 'n', j.get('severity', '?'),
            'Y' if j.get('register_ok') else 'n', 'Y' if j.get('sigla_kept') else 'n',
            'Y' if j.get('coverage_ok') else 'n', j.get('discrimination_quality', '?'),
            '; '.join('s%s:%s' % (i.get('severity'), i.get('detail', '')[:50]) for i in j.get('issues', [])[:2])))
        md = render(res)
        out_md = os.path.join(OUT, safe_name(k) + '.merged.md')
        if k in PROTECTED and os.path.exists(out_md):
            print('  %s protected — kept existing %s' % (k, os.path.basename(out_md)))
        else:
            open(out_md, 'w', encoding='utf-8').write(md)
        combined.append(md)
        combined.append('\n---\n')
    open(os.path.join(OUT, 'pilot_review.md'), 'w', encoding='utf-8').write('\n'.join(combined))
    print('\npublishable (ok & sev<=2): %d/%d' % (npass, len(results)))
    print('side-by-side review → %s' % os.path.join(OUT, 'pilot_review.md'))


if __name__ == '__main__':
    main()
