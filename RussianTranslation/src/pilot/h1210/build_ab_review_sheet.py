#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_ab_review_sheet.py — H1210's BLIND A/B human-verdict sheet.

The handoff's deliverable 2: "выборка карточек обеих рук вперемешку, без пометки руки —
слепая практика второго аннотатора (как в A44). Человеческие вердикты = верхний слой
сравнения качества." So the sheet interleaves cards from both arms with NO arm label
anywhere in the HTML — not in the id, not in a badge, not in the DOM order — and the
arm mapping lives only in the committed lock file, which the reviewer does not open.

Blinding specifics (all deliberate):
* item ids are opaque running numbers (`h1210-ab-007`), not keys or arm names;
* items are ordered by a deterministic hash of (sheet_id, key1, arm), so arm-A and arm-B
  items interleave reproducibly without an RNG seed anyone has to remember;
* the same headword may appear from both arms — that is a feature (a within-item
  comparison the reviewer performs unknowingly), and the lock records both rows;
* the filter bar filters by STRATUM (the selection dimension), never by arm.

Content comes from the canonical audit's `restored_card` — i.e. what the card looks like
after {Tn} restoration, the same text a promote would write — so the human is rating the
real artifact, not masked skeleton text.

LEGIBILITY (H1646 csl-atlas -> H1808 here; do not regress it again): the sense bodies are
raw CDSL markup, so they go through `csl_pyutil.anatomy.highlight()` — a wall of escaped
`&lt;ls&gt;` / `{#...#}` is not something a human can rate — with `legend_html()` once per
sheet, and every `<ls>` citation rendered as a link to the scan via the repo's own ported
resolver (`src/ls_resolver.py`). Each new sheet generator has re-introduced this defect;
the fix is cheap and belongs in the generator, not in the reviewer's patience.

PUBLISH SAFETY: the sheet embeds unpublished RU/DE store-grade text → the HTML is
gitignored (`review/*_sheet.html`); only `review/locks/<sheet_id>.lock.json` is committed.

Usage:
  python src/pilot/h1210/build_ab_review_sheet.py \
      --arm-a-audit src/pilot/h1210/arm_a.canonical_audit.json \
      --arm-b-audit src/pilot/h1210/arm_b.canonical_audit.json \
      --worklist src/pilot/h1210/H1210_ab100_worklist.28.07.26.json \
      --per-arm 20 --generated 28-07-2026
"""
import argparse
import hashlib
import html
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(os.path.dirname(HERE))                 # .../src
RT = os.path.dirname(SRC)
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import review_sheet_standard as STD                          # noqa: E402
from csl_pyutil import anatomy, render_review_sheet          # noqa: E402
from ls_resolver import generate_href                        # noqa: E402
if HERE not in sys.path:
    sys.path.insert(0, HERE)
from ab_report import worklist_index                         # noqa: E402  (same card-id join)
from safe_filename import decode_safe_name                   # noqa: E402


def load(p):
    return json.load(open(p, encoding='utf-8'))


_N_ATTR = re.compile(r'\bn\s*=\s*"([^"]*)"')


def ls_payload(part, inner, attrs):
    """Render an `<ls>` citation as a link to the scan; everything else falls through.

    `ls_resolver.generate_href` is the repo's port of the Cologne resolver, so the sheet
    links exactly where csl-app links. An unresolvable citation stays plain text rather
    than becoming a dead link — the resolver returns None/'' for what it cannot place.
    """
    if part != 'citation':
        return None
    href = None
    try:
        href = generate_href('pwg', (_N_ATTR.search(attrs or '') or [None, ''])[1], inner)
    except Exception:                                        # a resolver miss is not fatal
        href = None
    body = html.escape(str(inner))
    if not href:
        return '<span style="color:#e06c75">%s</span>' % body
    return ('<a href="%s" target="_blank" rel="noopener" '
            'style="color:#e06c75;text-decoration:underline dotted">%s</a>'
            % (html.escape(href, quote=True), body))


def body_html(text):
    """One raw CDSL body -> colour-coded, citation-linked HTML (never escaped-only)."""
    return anatomy.highlight(str(text or ''), payload_hook=ls_payload)


def senses_html(card):
    out = []
    for rec in (card.get('records') or []):
        gram = html.escape(str(rec.get('grammar') or ''))
        if gram:
            out.append('<div style="color:#666;font-size:90%%">%s</div>' % gram)
        for s in (rec.get('senses') or []):
            out.append('<div style="margin:.45em 0">'
                       '<b>%s</b> %s</div>'
                       % (html.escape(str(s.get('tag') or '')),
                          body_html(s.get('russian'))))
    return '\n'.join(out) or '<i>(no senses)</i>'


def source_html(card):
    out = []
    for rec in (card.get('records') or []):
        for s in (rec.get('senses') or []):
            out.append('<div style="margin:.45em 0;color:#333">'
                       '<b>%s</b> %s</div>'
                       % (html.escape(str(s.get('tag') or '')),
                          body_html(s.get('german'))))
    return '\n'.join(out) or '<i>(no senses)</i>'


def sort_key(sheet_id, key1, arm):
    return hashlib.sha256(('%s|%s|%s' % (sheet_id, key1, arm)).encode('utf-8')).hexdigest()


def pick(audit, per_arm, sheet_id, arm):
    """Deterministic per-arm sample: promote-DRY PASS cards only (a human rating a card the
    machine already hard-rejected measures nothing the free gate did not), spread across
    the hash order so no stratum or size band dominates."""
    rows = [r for r in audit['reports'] if r.get('promote_dry') and r.get('restored_card')]
    rows.sort(key=lambda r: sort_key(sheet_id, r['key1'], arm))
    return rows[:per_arm]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--arm-a-audit', required=True)
    ap.add_argument('--arm-b-audit', required=True)
    ap.add_argument('--worklist', required=True)
    ap.add_argument('--per-arm', type=int, default=20)
    ap.add_argument('--generated', required=True, help='DD-MM-YYYY, passed explicitly')
    ap.add_argument('--sheet-id', default=None)
    a = ap.parse_args()

    # sheet_id carries the ISO date so it sorts next to the other locks in review/locks/.
    d, m, y = a.generated.split('-')
    sheet_id = a.sheet_id or 'h1210-ab-blind-%s-%s-%s' % (y, m, d)
    worklist = load(a.worklist)
    strata, _ids = worklist_index(worklist)

    chosen = ([(r, 'A') for r in pick(load(a.arm_a_audit), a.per_arm, sheet_id, 'A')]
              + [(r, 'B') for r in pick(load(a.arm_b_audit), a.per_arm, sheet_id, 'B')])
    chosen.sort(key=lambda t: sort_key(sheet_id, t[0]['key1'], t[1]))

    items, lock_rows = [], []
    for i, (rep, arm) in enumerate(chosen, 1):
        item_id = 'h1210-ab-%03d' % i
        key = rep['key1']
        card = rep['restored_card']
        stratum = strata.get(key, 'S?').split('_')[0]
        items.append({
            'id': item_id,
            'filt': stratum,
            # The audit keys on the safe-name stem; the reader needs the printed headword.
            'title': STD.slp1_iast(decode_safe_name(key.split('~~')[0])),
            'title_href': STD.pwg_entry_href(decode_safe_name(key.split('~~')[0])),
            'badges': [stratum],
            'question': 'Is this Russian rendering publishable as-is — faithful to the German, '
                        'complete, and in scholarly register?',
            'panels': [
                ('Русский (перевод)', senses_html(card)),
                ('Deutsch (источник)', source_html(card)),
            ],
            'note_placeholder': 'What is wrong, concretely (sense tag + what it should say)?',
        })
        lock_rows.append({'item_id': item_id, 'key1': key, 'arm': arm, 'stratum': stratum})

    cfg = dict(STD.standard_config(save_as='review/%s_decisions.json' % sheet_id))
    cfg.update({
        'sheet_id': sheet_id,
        'title': 'H1210 — blind quality vote, 100-card PWG A/B',
        # The anatomy legend goes here (the one place rendered once per sheet, above the
        # cards) — `subtitle` is interpolated as raw HTML by render_review_sheet.
        'subtitle': ('%d cards from two generation pipelines, interleaved and UNLABELLED. '
                     'Rate each card on its own merits; do not try to guess which system '
                     'produced it. (Approve = publishable as-is.)%s' % (
                         len(items),
                         anatomy.legend_html(['sanskrit', 'gloss', 'citation', 'grammar',
                                              'abbreviation', 'structure']))),
        'footer': 'H1210 · handoff deliverable 2 · verdicts are the top layer of the A/B '
                  'quality comparison',
        'approve_label': 'publishable',
        'reject_label': 'not publishable',
        'filters': sorted({(it['filt'], it['filt']) for it in items}),
        'generated': a.generated,
        'rating': STD.DA_RATING,
    })
    out_html = os.path.join(RT, 'review', '%s_sheet.html' % sheet_id)
    doc = render_review_sheet(items, cfg)
    os.makedirs(os.path.dirname(out_html), exist_ok=True)
    with open(out_html, 'w', encoding='utf-8', newline='\n') as f:
        f.write(doc)

    lock = {
        'schema': 'review-lock/v1',
        'sheet_id': sheet_id,
        'content_hash': 'sha256:' + hashlib.sha256(doc.encode('utf-8')).hexdigest(),
        'generated': a.generated,
        'gate': 'H1210-AB',
        'n_items': len(items),
        'blinding': 'arm labels appear ONLY in this lock file; the HTML carries none',
        'per_arm': a.per_arm,
        'items': lock_rows,
        'ids': [r['item_id'] for r in lock_rows],
    }
    out_lock = os.path.join(RT, 'review', 'locks', '%s.lock.json' % sheet_id)
    os.makedirs(os.path.dirname(out_lock), exist_ok=True)
    with open(out_lock, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(lock, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print('wrote %s (%d items, gitignored — embeds unpublished RU)' % (out_html, len(items)))
    print('wrote %s (committed: the unblinding key)' % out_lock)
    from collections import Counter
    print('arm split (lock only): %s' % dict(Counter(r['arm'] for r in lock_rows)))


if __name__ == '__main__':
    main()
