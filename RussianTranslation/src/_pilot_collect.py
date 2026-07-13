#!/usr/bin/env python
"""Collect the pilot workflow output → judge summary + side-by-side DE→RU review.

  python _pilot_collect.py <workflow-output.json>
"""
import json, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from safe_filename import safe_name
import pipeline_version

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


def find_meta(o):
    """First dict value carried under a 'meta' key anywhere in the wf wrapper —
    for the model id + generated_at that go into the .md footer."""
    if isinstance(o, dict):
        if isinstance(o.get('meta'), dict):
            return o['meta']
        for v in o.values():
            m = find_meta(v)
            if m is not None:
                return m
    if isinstance(o, list):
        for v in o:
            m = find_meta(v)
            if m is not None:
                return m
    return None


# The `notes` field is free-text model commentary; it sometimes *mentions* a
# masking placeholder ("Masked span {T1} is a citation reference…"). Rendered
# verbatim into the `.merged.md` blockquote, that mention makes stage2_pregate's
# stranded-anchor scan misfire STRANDED-ANCHOR on an otherwise-clean card (H858:
# 7/15 no_pwg_w09 "defects" were this false positive). A {Tn} in prose notes is
# always a masking artifact, never deliverable content — strip it.
_MASK_TOKEN_RE = re.compile(r'\{T(?:\d+|n)\}')


def strip_mask_tokens(text):
    """Remove {T<n>}/{Tn} masking-artifact tokens from free-text (notes), tidying
    the whitespace/punctuation the removal leaves behind. Deliverable fields
    (german/russian) are never passed here — their {Tn} are real, restorable spans."""
    if not text:
        return text
    out = _MASK_TOKEN_RE.sub('', text)
    out = re.sub(r'  +', ' ', out)          # collapse the gap a removed token left
    out = re.sub(r'\s+([.,;:])', r'\1', out)  # "span  is" / "span ." tidy
    return out.strip()


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
        note = strip_mask_tokens(c['notes'])
        if note:
            lines.append('> %s\n' % note)
    return '\n'.join(lines)


def main():
    wf = sys.argv[1]
    parsed = json.loads(open(wf, encoding='utf-8').read())
    results = find_results(parsed) or []
    meta = find_meta(parsed) or {}
    # pipeline footer: stamp from the CURRENT tooling (same source as run_batch/promote),
    # model + date from the wf meta. Warn on drift, like run_batch.py collect.
    model = meta.get('translate_model') or meta.get('model')
    pipeline = pipeline_version.stamp(model_version=model)
    footer = pipeline_version.md_footer(pipeline, model, meta.get('generated_at'))
    for d in pipeline_version.check():
        print('  WARNING pipeline drift: %s files changed but version still v%s '
              '(recorded %s → now %s) — bump pipeline_versions.json + freeze'
              % (d['component'], d['version'], d['recorded_sha'], d['current_sha']))
    os.makedirs(OUT, exist_ok=True)
    print('=== PILOT JUDGE SUMMARY (%d cards) ===' % len(results))
    print('%-12s %-4s %-4s %-7s %-6s %-6s %-13s %s' %
          ('card', 'ok', 'sev', 'regist', 'sigla', 'cover', 'discrimin', 'issues'))
    npass = 0
    combined = []
    for res in results:
        k = res.get('key')
        card = res.get('card')
        j = res.get('judge') or {}
        ok = j.get('ok')
        npass += 1 if (ok and (j.get('severity') or 5) <= 2) else 0
        nsense = sum(len(r.get('senses', [])) for r in (card or {}).get('records', []))
        print('%-12s %-4s %-4s %-7s %-6s %-6s %-13s %s' % (
            k, 'Y' if ok else 'n', j.get('severity', '?'),
            'Y' if j.get('register_ok') else 'n', 'Y' if j.get('sigla_kept') else 'n',
            'Y' if j.get('coverage_ok') else 'n', j.get('discrimination_quality', '?'),
            '; '.join('s%s:%s' % (i.get('severity'), i.get('detail', '')[:50]) for i in j.get('issues', [])[:2])))
        if not card:
            md = '# %s\n\nUNCOLLECTED: workflow returned no card; queued for re-run.\n' % k
            print('  %s null card — no merged file written' % k)
            combined.append(md)
            combined.append('\n---\n')
            continue
        # root-split sub-card keys (e.g. man~~h0_00_pwg00) are ALREADY safe stems — keep them
        # verbatim so root_glue_translated finds <subkey>.merged.md; only headword keys get safe_name.
        # The footer goes ONLY on whole cards; a sub-card's footer would scatter through the
        # glued .NESTED.md (root_glue_translated.body_of keeps everything after the title), so
        # the glue step stamps the assembled card once instead.
        is_subcard = '~~' in (k or '')
        md = render(res).rstrip('\n') + ('' if is_subcard else '\n\n' + footer) + '\n'
        stem = k if is_subcard else safe_name(k)
        out_md = os.path.join(OUT, stem + '.merged.md')
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
