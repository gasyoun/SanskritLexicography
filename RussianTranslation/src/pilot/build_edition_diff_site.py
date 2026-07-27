#!/usr/bin/env python
r"""Edition-diff reading surface: PWG skeleton vs PW/SCH/PWKVN/NWS (H1631 / N14).

Renders one static, self-contained HTML page listing headwords where the PWG
sense skeleton is shown with the other edition layers (PW/SCH/PWKVN/NWS)
attached at their classified insertion point -- each supplement badged with
its ``edition_rel`` subtype (base / restate / pw_correct / sch_star /
derived_sense / a2a / nws_at_sense / foreign_fragment). H1624 G4's
``edition_rel.classify_edition_rel`` is the ONLY typology used here; this
module invents no new classes. DE text is rendered for READING ONLY -- never
rewritten, never re-translated (scope: pwg_ru/REGLUE_SPEC.md).

Data source: the gitignored ``src/pwg_ru_translated.jsonl`` store (resolved
via ``store_path.canonical_store``, same convention as build_article_site.py
and the rest of pwg_ru tooling) when it exists locally; the FIXTURE_ROWS
below is a small SYNTHETIC multi-layer headword (fictitious gloss text, not
store content -- N9 rights clearance forbids publishing the real store) that
covers every non-``unknown`` edition_rel subtype, used for CI/selftest and
any environment without the local store.

  python src/pilot/build_edition_diff_site.py                # build from the local store, REGLUE_SPEC pilot keys
  python src/pilot/build_edition_diff_site.py --keys gA,Cid   # a subset of the store
  python src/pilot/build_edition_diff_site.py --fixture       # force the synthetic fixture
  python src/pilot/build_edition_diff_site.py --selftest
"""
import argparse
import html
import json
import os
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
REPO = os.path.dirname(SRC)
sys.path.insert(0, SRC)
from edition_rel import edition_rel_for_row, build_pwg_gender_index, SUBTYPES  # noqa: E402
from store_path import canonical_store  # noqa: E402

STORE = canonical_store(os.path.join(SRC, 'pwg_ru_translated.jsonl'))
OUT_DIR = os.path.join(REPO, 'article_site')

# The 5-layer REGLUE_SPEC pilot roots (pwg_ru/REGLUE_SPEC.md Sec.5) -- the demo default
# when no --keys is given and the local store is present.
DEFAULT_KEYS = ('gA', 'Cid', 'Sam', 'jIv', 'rakz', 'vraj', 'yat')

LAYER_LABEL = {'pwg': 'PWG', 'pw': 'PW', 'sch': 'SCH', 'pwkvn': 'PWKVN', 'nws': 'NWS'}

BADGE_COLOR = {
    'base': '#607d8b', 'restate': '#8d6e63', 'pw_correct': '#e65100',
    'sch_star': '#2e7d32', 'derived_sense': '#00838f', 'a2a': '#6a1b9a',
    'nws_at_sense': '#1565c0', 'foreign_fragment': '#ad1457', 'unknown': '#757575',
}


def _root_of(key1):
    return (key1 or '').split('~~')[0]


def _de_text(s):
    """Plain-text rendering of a stored DE field for this diff view -- unwrap the
    translatable-gloss braces, keep <lex> gender/grammar tags as a bracketed
    label, drop everything else. Read-only display transform; never mutates the
    source string and is not a substitute for build_article_site.py's full
    citation/abbreviation renderer."""
    t = s or ''
    t = re.sub(r'\[Page[^\]]*\]', '', t)
    t = t.replace('\xa6', '')  # lemma-terminator (Cologne drops it too)
    t = re.sub(r'\{%(.*?)%\}', r'\1', t, flags=re.S)
    t = re.sub(r'\{#(.*?)#\}', r'\1', t, flags=re.S)
    t = re.sub(r'<lex>(.*?)</lex>', r'[\1] ', t)
    t = re.sub(r'<[^>]+>', '', t)
    return re.sub(r'\s+', ' ', t).strip()


def load_store_rows(store, keys):
    rows = []
    with open(store, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if _root_of(r.get('key1') or r.get('subcard')) in keys:
                rows.append(r)
    return rows


# Synthetic fixture: one 5-layer headword exercising every non-'unknown' subtype,
# plus one 3-layer headword for variety. Fictitious gloss text throughout -- never
# real store content (N9).
FIXTURE_ROWS = [
    {'key1': 'kfz', 'subcard': 'kfz~~h0_00_pwg00', 'layer': 'pwg', 'sense_tag': '1',
     'de': '<lex>m.</lex> {%to pull, sense one%}'},
    {'key1': 'kfz', 'subcard': 'kfz~~h0_00_pwg00', 'layer': 'pwg', 'sense_tag': '2',
     'de': '<lex>m.</lex> {%to draw, sense two%}'},
    {'key1': 'kfz', 'subcard': 'kfz~~h0_zz_pw01', 'layer': 'pw', 'sense_tag': '1',
     'de': '<lex>m.</lex> {%to pull (abridged)%}'},
    {'key1': 'kfz', 'subcard': 'kfz~~h0_zz_pw02', 'layer': 'pw', 'sense_tag': '2',
     'de': '<lex>f.</lex> {%to draw (gender corrected)%}'},
    {'key1': 'kfz', 'subcard': 'kfz~~h0_zz_sch', 'layer': 'sch', 'sense_tag': '3',
     'de': '{%an additional SCH-only sense%}'},
    {'key1': 'kfz', 'subcard': 'kfz~~h0_zz_sch', 'layer': 'sch', 'sense_tag': 'pra_caus',
     'de': '{%causative derived form%}'},
    {'key1': 'kfz', 'subcard': 'kfz~~h0_zz_pwkvn', 'layer': 'pwkvn', 'sense_tag': '4',
     'de': '{%addendum to an addendum%}'},
    {'key1': 'kfz', 'subcard': 'kfz~~h0_zz_pwkvn', 'layer': 'pwkvn', 'sense_tag': 'ava_desid',
     'de': '{%desiderative derived form%}'},
    {'key1': 'kfz', 'subcard': 'kfz~~h0_zz_nws00', 'layer': 'nws', 'sense_tag': '2',
     'de': 'der Zusatz ist mit und die sich auf ein'},
    {'key1': 'kfz', 'subcard': 'kfz~~h0_zz_nws01', 'layer': 'nws', 'sense_tag': 'NWS-1',
     'de': 'the term is of and in with for from by as testword'},
    {'key1': 'vAh', 'subcard': 'vAh~~h0_00_pwg00', 'layer': 'pwg', 'sense_tag': '1',
     'de': '{%to carry%}'},
    {'key1': 'vAh', 'subcard': 'vAh~~h0_zz_pw01', 'layer': 'pw', 'sense_tag': '1',
     'de': '{%to carry (abridged)%}'},
    {'key1': 'vAh', 'subcard': 'vAh~~h0_zz_sch', 'layer': 'sch', 'sense_tag': 'ava_caus',
     'de': '{%causative carry, derived%}'},
]


def _sense_sort_key(tag):
    if tag.lower() in ('header', 'head'):
        return (0, 0, tag)
    m = re.match(r'\d+', tag)
    if m:
        return (1, int(m.group()), tag)
    return (2, 0, tag)


def build_model(rows):
    """rows -> ({key1: {'pwg': [...], 'attach': {target_sense: [supp,...]}, 'new': [supp,...]}}, counts).

    Every subtype/insertion-point decision comes from edition_rel_for_row --
    this function only groups and renders, it never re-derives classification."""
    by_key = {}
    for r in rows:
        by_key.setdefault(_root_of(r.get('key1') or r.get('subcard')), []).append(r)
    model = {}
    counts = Counter()
    for key1, key_rows in by_key.items():
        idx = build_pwg_gender_index(key_rows)
        pwg_senses, attach, new = [], {}, []
        for r in key_rows:
            rel = edition_rel_for_row(r, idx)
            counts[rel['subtype']] += 1
            layer = r.get('layer') or 'pwg'
            entry = {
                'layer': layer, 'label': LAYER_LABEL.get(layer, layer.upper()),
                'subtype': rel['subtype'], 'sense_tag': str(r.get('sense_tag') or ''),
                'de_text': _de_text(r.get('de')),
            }
            if layer == 'pwg':
                pwg_senses.append(entry)
                continue
            target = (rel.get('insertion_point') or {}).get('target_sense')
            if target and target not in ('*new', '*whole'):
                attach.setdefault(target, []).append(entry)
            else:
                new.append(entry)
        pwg_senses.sort(key=lambda e: _sense_sort_key(e['sense_tag']))
        model[key1] = {'pwg': pwg_senses, 'attach': attach, 'new': new}
    return model, counts


def _badge(entry):
    st = entry['subtype']
    return ('<span class="badge" data-subtype="%s" style="background:%s">%s &middot; %s</span>'
            % (st, BADGE_COLOR.get(st, BADGE_COLOR['unknown']), html.escape(entry['label']), st))


def render_key(key1, m):
    parts = ['<section class="kw" id="%s">' % html.escape(key1, quote=True),
             '<h2 class="iast">%s</h2>' % html.escape(key1)]
    used_targets = set()
    for s in m['pwg']:
        used_targets.add(s['sense_tag'])
        tag = '' if s['sense_tag'].lower() in ('header', 'head') else '<span class="tag">%s)</span> ' % html.escape(s['sense_tag'])
        parts.append('<div class="sense">')
        parts.append('<div class="pwg-line">%s%s %s</div>' % (tag, html.escape(s['de_text']), _badge(s)))
        for supp in m['attach'].get(s['sense_tag'], []):
            parts.append('<div class="suppl">%s %s</div>' % (_badge(supp), html.escape(supp['de_text'])))
        parts.append('</div>')
    leftover = [supp for tgt, supps in m['attach'].items() if tgt not in used_targets for supp in supps]
    extra = leftover + m['new']
    if extra:
        parts.append('<div class="new-block"><h4>Additional (not attached to a shown PWG sense)</h4>')
        for supp in extra:
            parts.append('<div class="suppl">%s %s</div>' % (_badge(supp), html.escape(supp['de_text'])))
        parts.append('</div>')
    parts.append('</section>')
    return '\n'.join(parts)


PAGE_TEMPLATE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PWG edition-diff -- PWG skeleton vs PW/SCH/PWKVN/NWS (H1631)</title>
<style>
:root{--bg:#fff;--fg:#1a1a1a;--mut:#6a6a6a;--line:#e4e4e4;--accent:#7a1f1f;--card:#fafafa}
@media(prefers-color-scheme:dark){:root{--bg:#161616;--fg:#e8e8e8;--mut:#9a9a9a;--line:#333;--accent:#e6928a;--card:#1e1e1e}}
*{box-sizing:border-box}body{margin:0;font:15px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;color:var(--fg);background:var(--bg)}
#wrap{display:flex;min-height:100vh}
#side{width:220px;border-right:1px solid var(--line);padding:10px;overflow-y:auto;height:100vh;position:sticky;top:0}
#side h1{font-size:14px;margin:4px 6px 10px}
#side a{display:block;padding:4px 8px;border-radius:6px;color:var(--fg);text-decoration:none;font-style:italic}
#side a:hover{background:var(--card)}
#main{flex:1;padding:20px 28px;max-width:900px}
.kw{margin-bottom:40px;padding-bottom:20px;border-bottom:1px solid var(--line)}
.kw h2{font-size:24px;margin:0 0 12px}
.sense{margin:10px 0;padding:10px 12px;background:var(--card);border-radius:8px}
.pwg-line{margin-bottom:2px}
.tag{font-weight:700;color:var(--accent);margin-right:4px}
.suppl{margin:4px 0 4px 18px;padding:4px 0 4px 10px;border-left:2px solid var(--line)}
.badge{display:inline-block;font-size:11px;color:#fff;border-radius:10px;padding:1px 8px;margin-right:6px;white-space:nowrap}
.new-block{margin-top:10px;padding:8px 12px;border:1px dashed var(--line);border-radius:8px}
.new-block h4{margin:0 0 6px;font-size:13px;color:var(--mut);font-weight:600}
.counts{font-size:12px;color:var(--mut);margin-bottom:20px}
.counts ul{margin:4px 0 0;padding-left:18px}
.note{font-size:12px;color:var(--mut);margin-bottom:14px}
</style></head><body><div id="wrap">
<nav id="side"><h1>PWG edition-diff</h1>%(nav)s</nav>
<main id="main">
<h1>PWG skeleton vs PW / SCH / PWKVN / NWS</h1>
<p class="note">Each supplement is badged with its edition_rel subtype (H1624 G4 classifier).
DE text shown here is read-only -- never re-translated, never rewritten.</p>
<div class="counts">Subtypes in this build:<ul>%(counts)s</ul></div>
%(body)s
</main></div></body></html>
"""


def render_page(model, counts):
    nav = ''.join('<a href="#%s">%s</a>' % (html.escape(k, quote=True), html.escape(k)) for k in sorted(model))
    body = '\n'.join(render_key(k, model[k]) for k in sorted(model))
    counts_html = ''.join('<li>%s: %d</li>' % (st, counts[st]) for st in SUBTYPES if counts.get(st))
    return PAGE_TEMPLATE % {'nav': nav, 'body': body, 'counts': counts_html}


def selftest():
    model, counts = build_model(FIXTURE_ROWS)
    assert set(model) == {'kfz', 'vAh'}, sorted(model)
    page = render_page(model, counts)
    expected = {'base', 'restate', 'pw_correct', 'sch_star', 'derived_sense',
                'a2a', 'nws_at_sense', 'foreign_fragment'}
    for st in expected:
        assert ('data-subtype="%s"' % st) in page, 'missing badge for subtype %r' % st
    # every subtype rendered is a KNOWN edition_rel subtype -- no new typology invented
    found = set(re.findall(r'data-subtype="([a-z0-9_]+)"', page))
    assert found <= set(SUBTYPES), 'unknown subtype(s) rendered: %r' % (found - set(SUBTYPES))
    assert found == expected, 'expected all 8 non-unknown subtypes, got %r' % found
    # DE not rewritten: the fixture's own gloss text passes through verbatim (unwrapped, not translated)
    for needle in ('to pull, sense one', 'to draw, sense two', 'gender corrected',
                   'addendum to an addendum', 'desiderative derived form', 'testword'):
        assert needle in page, 'DE text altered/missing: %r' % needle
    # gender-conflict classification actually fired (not just default restate)
    assert counts['pw_correct'] >= 1 and counts['restate'] >= 1, counts
    print('build_edition_diff_site --selftest: OK (%d headwords, %d rows, subtypes=%r)'
          % (len(model), sum(counts.values()), dict(counts)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--keys', help='comma-separated key1 roots (default: REGLUE_SPEC pilot set)')
    ap.add_argument('--fixture', action='store_true', help='force the built-in synthetic fixture')
    ap.add_argument('--out', default=os.path.join(OUT_DIR, 'edition_diff.html'))
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    keys = set(args.keys.split(',')) if args.keys else set(DEFAULT_KEYS)
    if args.fixture or not os.path.exists(STORE):
        rows = [r for r in FIXTURE_ROWS if not args.keys or _root_of(r['key1']) in keys]
    else:
        rows = load_store_rows(STORE, keys)
    if not rows:
        sys.exit('no rows found for keys=%r (store=%s)' % (sorted(keys), STORE))
    model, counts = build_model(rows)
    page = render_page(model, counts)
    os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)
    with open(args.out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(page)
    print('edition_diff: %d headword(s), %d row(s)' % (len(model), len(rows)))
    for st in SUBTYPES:
        if counts.get(st):
            print('  %-18s %d' % (st, counts[st]))
    print('  wrote -> %s' % args.out)


if __name__ == '__main__':
    main()
