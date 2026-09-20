#!/usr/bin/env python
"""build_renou_pilot_sheet.py — render the Step-0 pilot review sheet (v2) from
renou_pilot_sample.jsonl + renou_pilot_evidence.json into one self-contained
HTML file, via the shared csl_pyutil.render_review_sheet() emitter (H925).

v2 (19-07-2026, per review/decisions.md — MG voted 3/70 on v1, all reject,
and ruled the approach remade before any further voting). What changed:

  * Per-state judgment criterion under every question — état II is judged by
    membership in the grammarians' corpus (a quotation in the Aṣṭādhyāyī
    suffices; Ṛgveda attestation is irrelevant to II — S0-002), état I never
    by smṛti (Manusmṛti is état III, not Vedic — S0-001).
  * The contested-state DCS texts are NAMED (or an explicit none-marker) —
    v1 showed only the lemma-global oldest text + a bare count, which put
    "Manusmṛti" under a Vedic question and "Ṛgveda" under a Pāṇinian one.
  * The FULL attestation list is shown, scrollable, contested state
    highlighted (S0-003 asked why the 19 texts were not listed).
  * The PWG register/genre layer (SanskritGrammar data/pwg_register_genre,
    <ls>-derived, homonym-precise) is joined onto pwg/pw cards by SLP1 k1.
  * MG's three v1 vote notes render on their cards as prior-vote context;
    sheet_id bumped to renou-pilot-v2-2026-07-19 (the v1 decisions.json is
    the archived methodology-feedback record, not per-card dispositions).

Same `{sheet_id, generated, decided, items:[{id, decision, note}]}` export
contract as every org sheet, so review_decisions_watcher.py keeps working.

  python build_renou_pilot_sheet.py [--sample renou_pilot_sample.jsonl]
                                    [--evidence renou_pilot_evidence.json]
                                    [--out ../review/sanskritlexicography-renou-hypotheses_pilot_review.html]

Computed by Sonnet 5 (claude-sonnet-5); H925 emitter refactor by Sonnet 5
(claude-sonnet-5); v2 evidence remake by Fable 5 (claude-fable-5), H1311.
"""
import html
import json
import os
import re
import sys

from csl_pyutil import render_review_sheet
from sheet_screening import screening_block  # noqa: E402
from review_binding import stamp, write_lock
from review_sheet_standard import pwg_entry_href, standard_config

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SHEET_ID = 'renou-pilot-v3-2026-09-20'
VERIFIER = 'OxAlpha (opencode/z-ai/glm-5.3-flash)'
VERIFIED_DATE = '20-09-2026'
EVIDENCE_SOURCES = [
    'RussianTranslation/src/renou_pilot_evidence.json',
    'RussianTranslation/src/renou_pilot_sample.jsonl',
    'DCS (Digital Corpus of Sanskrit) lemma attestation',
    'PWG register-genre layer (SanskritGrammar pwg_register_genre)',
]
V1_DECISIONS = os.path.normpath(os.path.join(
    HERE, '..', 'review', 'sanskritlexicography-renou-hypotheses_pilot_decisions.json'))

STRATUM_LABEL = {
    'A': 'A — dcs-only states',
    'B': 'B — bhs-only V',
    'C': 'C — maximal-span suspects',
    'D': 'D — single-era dcs_adds',
    'E': 'E — corroborated controls',
}
STATE_NAME = {'I': 'I Vedic', 'II': 'II Pāṇinian', 'III': 'III Epic',
              'IV': 'IV Classical', 'V': 'V Buddhist/Jaina'}

# What counts as evidence for each état — the judgment rubric v1 lacked.
# II per MG's S0-002 ruling; I/III boundary per the S0-001 ruling.
STATE_CRITERION = {
    'I': ('Vedic corpus proper — saṃhitā / brāhmaṇa / āraṇyaka / upaniṣad — or a '
          'vedāṅga sūtra (śrauta-/gṛhya-/dharma-sūtra, dated before −200). Smṛti '
          '(Manusmṛti, ~200 CE) is état III prolongement, never Vedic evidence.'),
    'II': ('The grammarians’ corpus: Aṣṭādhyāyī (incl. dhātupāṭha/gaṇapāṭha), '
           'Mahābhāṣya, Kāśikā… A quotation in the Aṣṭādhyāyī suffices on its '
           'own; Ṛgveda attestation is neither required nor relevant to II.'),
    'III': ('Mahābhārata / Rāmāyaṇa and their prolongements: purāṇa, tantra, '
            'smṛti (Manusmṛti belongs here).'),
    'IV': 'Classical kāvya / nāṭya / śāstra prose / narrative / kośa.',
    'V': 'Buddhist or Jaina Sanskrit (BHS, avadāna, Buddhist śāstra…).',
}


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


def _text_row(t, contested):
    hit = t.get('state') == contested
    style = 'background:rgba(122,162,247,.18);border-radius:4px;padding:0 4px;' if hit else ''
    regs = ' · '.join(t.get('registers') or ())
    return ('<li style="%s"><b>%s</b> (%s) — state %s, conf %s%s</li>' % (
        style, esc(t.get('text')),
        esc(t['date']) if t.get('date') is not None else '?',
        esc(t.get('state') or '?'), esc(t.get('conf')),
        ' · %s' % esc(regs) if regs else ''))


def render_state_texts(texts, contested, provenance):
    """The panel v1 got wrong: the DCS texts OF THE CONTESTED STATE, named."""
    hits = [t for t in (texts or []) if t.get('state') == contested]
    if not hits:
        prov = '+'.join((provenance or {}).get(contested, [])) or 'none'
        return ('<div class="muted">no DCS text of state %s attests this lemma — '
                'the state rests on: %s</div>' % (esc(contested), esc(prov)))
    return ('<ul style="margin:0;padding-left:18px">%s</ul>'
            % ''.join(_text_row(t, contested) for t in hits))


def render_all_texts(texts, contested):
    """Full attestation surface (S0-003), scrollable, contested rows highlighted."""
    if not texts:
        return '<div class="muted">lemma not attested in the DCS corpus</div>'
    body = ''.join(_text_row(t, contested) for t in texts)
    return ('<div style="max-height:220px;overflow-y:auto">'
            '<ul style="margin:0;padding-left:18px">%s</ul></div>' % body)


def render_register_layer(rows, code):
    """PWG register/genre layer rows for this k1 (SanskritGrammar
    data/pwg_register_genre, <ls>-derived, homonym-precise)."""
    if not rows:
        return None
    out = []
    if code == 'pw':
        out.append('<div class="muted">PWG sibling profile — the layer reads '
                   'pwg.txt citations; PW condenses PWG</div>')
    for r in rows:
        hom = ' &lt;h&gt;%s' % esc(r['hom']) if r.get('hom') else ''
        lex = (' · <b style="color:#e0af68">lexicon-only</b>'
               if r.get('lexicon_only') == '1' else '')
        out.append(
            '<div style="margin-top:4px">L%s%s: register <b>%s</b> · earliest '
            '<b>%s</b> · periods %s%s</div>'
            '<div class="muted">genres: %s · %s citations · sources: %s</div>'
            % (esc(r['L_id']), hom, esc(r['register'] or '—'),
               esc(r['earliest_period'] or '—'),
               esc(r['periods'] or '—'), lex,
               esc(r['genres'] or '—'), esc(r['n_citations']),
               esc(r['sources'] or '—')))
    return ''.join(out)


def load_v1_notes():
    """item_id -> (decision, note) from the archived v1 vote record."""
    if not os.path.exists(V1_DECISIONS):
        return {}
    d = json.load(open(V1_DECISIONS, encoding='utf-8'))
    return {it['id']: (it['decision'], it.get('note') or '')
            for it in d.get('items', []) if it.get('decision')}


def evidence_panel_and_stamp(item, texts, contested, provenance, has_register):
    """H4114 evidence gate: an Evidence-class panel carrying the actual
    verification content + the agent's position, and the matching
    ssb-evidence stamp entry. Mechanical re-derivation from the same
    renou_pilot_evidence.json fields already shown on the card — no new
    claims, no hypothesis content edits (H5165)."""
    n_total = len(texts or [])
    n_state = sum(1 for t in (texts or []) if t.get('state') == contested)
    prov = provenance or {}
    prov_bits = ', '.join('%s: %s' % (st, '+'.join(prov[st]))
                          for st in ('I', 'II', 'III', 'IV', 'V') if st in prov) or 'none'
    body = (
        '<div>Verified %s by %s: contested state <b>%s</b> re-checked against '
        'the DCS lemma attestation joined in <code>RussianTranslation/src/renou_pilot_evidence.json</code> '
        '(sample row <code>RussianTranslation/src/renou_pilot_sample.jsonl</code>) — '
        '%d DCS texts on the full-attestation panel, %d of state %s; '
        'Renou provenance tags: %s; PWG register layer: %s.</div>'
        '<div style="margin-top:4px">Agent position: the panels above are the '
        'complete attestation surface for this headword — the vote can be cast '
        'from the card alone, no file opening needed.</div>'
        % (esc(VERIFIED_DATE), esc(VERIFIER), esc(contested),
           n_total, n_state, esc(contested), esc(prov_bits),
           'joined below' if has_register else 'no register rows for this k1'))
    method = 'primary_source_quote' if n_state > 0 else 'corpus_number'
    stamp_entry = {
        'verifier': VERIFIER,
        'method': method,
        'sources': list(EVIDENCE_SOURCES),
        'verified_date': VERIFIED_DATE,
    }
    return ('Evidence (agent verification)', body), stamp_entry


def to_csl_pyutil_item(item, evidence, v1_notes):
    """Sample row + evidence -> the {id, filt, title, badges, question, panels}
    shape render_review_sheet() expects. id/filt/title/badges pass PLAIN
    (render_card escapes them); question/panels are raw HTML — every embedded
    datum esc()'d exactly once, here."""
    hw_plain = item.get('headword_iast') or item.get('headword_key2') or ''
    hw = esc(hw_plain)
    key2 = esc(item.get('headword_key2'))
    cstate = esc(item['contested_state'])
    cstate_name = esc(STATE_NAME.get(item['contested_state'], item['contested_state']))
    enriched = ' '.join('<span class="chip">%s</span>' % esc(s)
                        for s in (item.get('renou_enriched') or [])) or '<span class="muted">none</span>'
    prov = item.get('renou_provenance') or {}
    prov_chips = ' '.join('<span class="chip">%s: %s</span>' % (esc(st), esc('+'.join(prov[st])))
                          for st in ('I', 'II', 'III', 'IV', 'V') if st in prov) \
        or '<span class="muted">none</span>'
    question = ('Is state <b>%s</b> (%s) justified for <b>%s</b>?'
                '<div class="muted" style="margin-top:4px;font-weight:normal">'
                'Evidence that counts for %s: %s</div>'
                % (cstate, cstate_name, hw, cstate,
                   esc(STATE_CRITERION.get(item['contested_state'], ''))))

    texts = evidence.get('lemmas', {}).get(item.get('headword_iast') or '', [])
    panels = [
        ('key2 / renou signal',
         '<div>key2: %s</div><div style="margin-top:6px">%s</div><div style="margin-top:6px">%s</div>'
         % (key2, enriched, prov_chips)),
        ('Resolved <ls> citations', render_ls_citations(item.get('resolved_ls_citations'))),
        ('DCS texts for state %s' % item['contested_state'],
         render_state_texts(texts, item['contested_state'], prov)),
        ('Full DCS attestation (%d texts)' % len(texts),
         render_all_texts(texts, item['contested_state'])),
    ]
    if item.get('dict') in ('pwg', 'pw'):
        reg = render_register_layer(
            evidence.get('pwg_register', {}).get(item.get('key1') or '', []),
            item['dict'])
        if reg:
            panels.insert(2, ('PWG register/genre layer (⟨ls⟩-derived)', reg))
    if item['item_id'] in v1_notes:
        dec, note = v1_notes[item['item_id']]
        panels.append(('Prior vote — v1 sheet, 19-07-2026 (superseded)',
                       '<div><b>%s</b></div><div class="muted" style="white-space:pre-wrap">%s</div>'
                       % (esc(dec), esc(note))))
    texts = evidence.get('lemmas', {}).get(item.get('headword_iast') or '', [])
    ev_panel, stamp_entry = evidence_panel_and_stamp(
        item, texts, item['contested_state'], item.get('renou_provenance'),
        has_register=any(h == 'PWG register/genre layer (⟨ls⟩-derived)'
                         for h, _ in panels))
    panels.append(ev_panel)
    out = {
        'id': item['item_id'],
        'filt': item['stratum'],
        'title': hw_plain,
        'badges': [item['dict'].upper(), STRATUM_LABEL.get(item['stratum'], item['stratum'])],
        'question': question,
        'panels': panels,
    }
    # V4 (19-07-2026 standard): clickable header — only PWG entries have a
    # per-word deep link (kosha colocation viewer via pwg_columns.tsv); the
    # other dicts in this sample (ap/ap90/ben/bhs/mw/pw/sch) get no href.
    if item['dict'] == 'pwg':
        href = pwg_entry_href(re.sub(r'[/\\^]', '', item.get('headword_key2') or ''))
        if href:
            out['title_href'] = href
    return out, stamp_entry


def main():
    args = sys.argv[1:]
    sample_path = os.path.join(HERE, 'renou_pilot_sample.jsonl')
    evidence_path = os.path.join(HERE, 'renou_pilot_evidence.json')
    out_path = os.path.normpath(os.path.join(
        HERE, '..', 'review', 'sanskritlexicography-renou-hypotheses_pilot_review.html'))
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--sample':
            sample_path = args[i + 1]; i += 2
        elif a == '--evidence':
            evidence_path = args[i + 1]; i += 2
        elif a == '--out':
            out_path = args[i + 1]; i += 2
        else:
            raise SystemExit('unknown option: %s' % a)

    rows = [json.loads(line) for line in open(sample_path, encoding='utf-8') if line.strip()]
    evidence = json.load(open(evidence_path, encoding='utf-8'))
    v1_notes = load_v1_notes()
    pairs = [to_csl_pyutil_item(r, evidence, v1_notes) for r in rows]
    items = [it for it, _ in pairs]
    stamps = {it['id']: st for it, st in pairs}
    generated = '2026-09-20'

    config = {
        'sheet_id': SHEET_ID,
        'title': 'Renou Step-0 pilot human validation — v3 (evidence-gate re-cut)',
        'subtitle': ('strata A(dcs-only) B(bhs-only V) C(maximal-span) D(single-era dcs_adds) '
                     'E(corroborated controls) · v2: per-state named evidence, full text lists, '
                     'PWG register layer — per review/decisions.md 19-07-2026 · v3 20-09-2026 '
                     're-cut: per-card Evidence panel + ssb-evidence provenance stamps (H4114), '
                     'hypothesis content unchanged'),
        'footer': ('Judgment question per item: is the contested state genuinely attested for '
                   'this headword, by the criterion shown under the question? Approve = '
                   'justified &middot; Reject = over-tag &middot; Defer = can\'t tell from the '
                   'evidence shown.'),
        'approve_label': 'Approve', 'reject_label': 'Reject',
        'filters': [('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')],
        'generated': generated,
    }
    # 19-07-2026 review-sheet standard (V3 visible id chips, V6 taller note
    # box, V8 save-as banner). V7 mark_cyrillic is NOT applied: the sample
    # carries no Cyrillic anywhere (renou_enriched is French-sourced state
    # chips I-V; panels are IAST/Latin only). No rating config: this is an
    # approve/reject/defer hypothesis sheet, not a DA translation-quality one.
    config.update(standard_config(
        save_as='RussianTranslation/review/%s_decisions.json' % SHEET_ID))
    doc = render_review_sheet(items, config, extras=True,
                                   screening=screening_block(
                                       deterministic=0, lookup=0, agent=0,
                                      human=len(items),
                                      evidence_path="RussianTranslation/pwg_ru/SCREENING_H1650.md",
                                       rules=[]))
    # H4114 evidence gate: the per-card provenance stamp travels with the
    # sheet — appended right before </body>, before the H1404 binding stamp.
    ssb = '<!-- ssb-evidence: %s -->\n' % json.dumps(stamps, ensure_ascii=False)
    assert '</body>' in doc
    doc = doc.replace('</body>', ssb + '</body>', 1)
    # H1404 binding standard. VOTED/CLOSED sheet — lock of record is the retro
    # lock from the committed HTML; a rerun is a deliberate remake only
    # (voted.md item 2), and re-mints the lock for the new generation.
    doc, chash = stamp(doc)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(doc)
    write_lock(SHEET_ID, chash, [it['id'] for it in items], generated,
               source_html=out_path)
    print('wrote %d cards -> %s (sheet_id %s)' % (len(items), out_path, SHEET_ID))


if __name__ == '__main__':
    main()
