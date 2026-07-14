#!/usr/bin/env python
"""build_renou_pilot_sheet.py — render the Step-0 pilot review sheet from
renou_pilot_sample.jsonl into a single self-contained HTML file.

Calls the shared csl_pyutil.render_review_sheet() emitter (H925) instead of
hand-writing HTML/JS — one deterministic, tested emitter shared with every
other review-sheet builder in the org, instead of this file's own now-retired
copy of the TEMPLATE/render_card pattern. Same `sheet_id` and exported
`{sheet_id, generated, decided, items:[{id, decision, note}]}` decisions.json
contract as before, so in-progress local votes and
Uprava/tools/review_decisions_watcher.py both keep working unchanged.

  python build_renou_pilot_sheet.py [--sample renou_pilot_sample.jsonl]
                                     [--out ../review/renou_pilot_sheet.html]

Computed by Sonnet 5 (claude-sonnet-5); refactored for H925 by Sonnet 5 (claude-sonnet-5).
"""
import html
import json
import os
import sys

from csl_pyutil import render_review_sheet

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SHEET_ID = 'renou-pilot-2026-07-02'

STRATUM_LABEL = {
    'A': 'A — dcs-only states',
    'B': 'B — bhs-only V',
    'C': 'C — maximal-span suspects',
    'D': 'D — single-era dcs_adds',
    'E': 'E — corroborated controls',
}
STATE_NAME = {'I': 'I Vedic', 'II': 'II Pāṇinian', 'III': 'III Epic',
              'IV': 'IV Classical', 'V': 'V Buddhist/Jaina'}


def esc(s):
    return html.escape(str(s) if s is not None else '')


def render_ls_citations(cites):
    if not cites:
        return '<div class="muted">no resolved &lt;ls&gt; citations recovered</div>'
    rows = []
    for c in cites:
        rows.append('<li><b>%s</b> — %s (state %s%s)</li>' % (
            esc(c.get('siglum')), esc(c.get('name')), esc(c.get('state')),
            ', date %s' % c['date'] if c.get('date') is not None else ''))
    return '<ul class="cites" style="margin:0;padding-left:18px">%s</ul>' % ''.join(rows)


def render_dcs_evidence(ev):
    if not ev:
        return '<div class="muted">lemma absent from dcs_lemma_renou.json</div>'
    supp = ev.get('state_support')
    supp_line = ('no support entry for this state (below min-support / filtered)'
                 if not supp else
                 'confidence <b>%s</b>, n=<b>%s</b> texts' % (esc(supp.get('conf')), esc(supp.get('n'))))
    return ('<div>lemma total: <b>%s</b> DCS texts &middot; oldest attestation: '
            '<b>%s</b> (%s) </div><div>this state: %s</div>') % (
        esc(ev.get('n_texts_lemma_total')), esc(ev.get('oldest_text')),
        esc(ev.get('oldest_date')), supp_line)


def render_provenance(prov):
    rows = []
    for st in ('I', 'II', 'III', 'IV', 'V'):
        if st in (prov or {}):
            rows.append('<span class="chip">%s: %s</span>' % (st, '+'.join(prov[st])))
    return ' '.join(rows) or '<span class="muted">none</span>'


def to_csl_pyutil_item(item):
    """renou_pilot_sample.jsonl row -> the {id, filt, title, badges, question,
    panels} shape render_review_sheet() expects.

    render_card() (csl_pyutil) already calls esc() on id/filt/title/badges —
    those must be passed PLAIN here, not pre-escaped, or they double-escape
    (verified against a real browser render: a pre-escaped "&lt;ls&gt;" panel
    heading rendered as the literal text "&LT;LS&GT;"). question/panels are
    raw-HTML fields (render_card inserts them unescaped, matching the donor's
    own convention) — every piece of item data embedded into them must be
    esc()'d exactly once, here.
    """
    hw_plain = item.get('headword_iast') or item.get('headword_key2') or ''
    hw = esc(hw_plain)
    key2 = esc(item.get('headword_key2'))
    dic_plain = item['dict'].upper()
    cstate = esc(item['contested_state'])
    cstate_name = esc(STATE_NAME.get(item['contested_state'], item['contested_state']))
    enriched = ' '.join('<span class="chip">%s</span>' % esc(s)
                         for s in (item.get('renou_enriched') or [])) or '<span class="muted">none</span>'
    question = ('Is state <b>%s</b> (%s) justified for <b>%s</b> — is the word genuinely '
                'attested in that Sanskrit?' % (cstate, cstate_name, hw))
    return {
        'id': item['item_id'],
        'filt': item['stratum'],
        'title': hw_plain,
        'badges': [dic_plain, STRATUM_LABEL.get(item['stratum'], item['stratum'])],
        'question': question,
        'panels': [
            ('key2 / renou signal',
             '<div>key2: %s</div><div style="margin-top:6px">%s</div><div style="margin-top:6px">%s</div>'
             % (key2, enriched, render_provenance(item.get('renou_provenance')))),
            ('Resolved <ls> citations', render_ls_citations(item.get('resolved_ls_citations'))),
            ('DCS evidence for state %s' % item['contested_state'], render_dcs_evidence(item.get('dcs_evidence'))),
        ],
    }


def main():
    args = sys.argv[1:]
    sample_path = os.path.join(HERE, 'renou_pilot_sample.jsonl')
    out_path = os.path.normpath(os.path.join(HERE, '..', 'review', 'renou_pilot_sheet.html'))
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--sample':
            sample_path = args[i + 1]; i += 2
        elif a == '--out':
            out_path = args[i + 1]; i += 2
        else:
            raise SystemExit('unknown option: %s' % a)

    rows = [json.loads(line) for line in open(sample_path, encoding='utf-8') if line.strip()]
    items = [to_csl_pyutil_item(r) for r in rows]
    generated = '2026-07-14'

    config = {
        'sheet_id': SHEET_ID,
        'title': 'Renou Step-0 pilot human validation',
        'subtitle': ('strata A(dcs-only) B(bhs-only V) C(maximal-span) D(single-era dcs_adds) '
                     'E(corroborated controls)'),
        'footer': ('Judgment question per item: is the contested state genuinely attested for '
                   'this headword in that era of Sanskrit? Approve = justified &middot; '
                   'Reject = over-tag &middot; Defer = can\'t tell from the evidence shown.'),
        'approve_label': 'Approve', 'reject_label': 'Reject',
        'filters': [('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')],
        'generated': generated,
    }
    doc = render_review_sheet(items, config)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(doc)
    print('wrote %d cards -> %s' % (len(items), out_path))


if __name__ == '__main__':
    main()
