#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""h1682_abbrev_collapse.py — shared classification core for H1682.

H1664 (VOTING_SHEET_SCREENING_AUDIT_26-07-2026.md §11) ruled the 273-card
`h1303_abbrev` sheet HYBRID: "a ~6-rule policy asked 273 times" — the O
overlay in build_h1303_abbrev_sheet.py already carries a full per-token
classification (bucket a/b/c, cls нем/лат/конт/OCR, proposed ru, citation
notes); the 273-card shape is a card-DESIGN defect, not a missing-data
problem. This module re-derives the rule-level structure from that SAME O
overlay + its own `# --- ...` section-comment headers (authored by Fable 5
`claude-fable-5`, H1303 Session 1, 21-07-2026) — no token is reclassified,
only re-grouped — and classifies each token as RULE-BULK (covered by its
section's policy, no individual vote needed) or RESIDUE (a classifier-
flagged ambiguity: no fixed `ru`, a genuine collision/caution note, or an
OCR/context-dependent token) per H1682 step 1's 100%-classification mandate.

Residue heuristic (`_AMBIG_RE`): a token is residue iff `ru is None`
(no fixed proposal — includes the pure `конт` n=-attribute-governed set,
whose true translation varies per occurrence and cannot be fixed at the
token level), or its `note` contains a collision/caution/no-fixed-value/
OCR/source-doubt signal. A settled explanatory footnote (e.g. "N8, MG
19-07-2026" pinning `Caus.` -> `кауз.`) does NOT make a token residue —
the footnote is preserved in the tsv but the token stays in its rule's
bulk. This is a re-grouping of already-made decisions, not a new policy
call — VOTING_SHEET_SCREENING_AUDIT_26-07-2026.md §11 mandate; the actual
RU/precedent for every token is unchanged from build_h1303_abbrev_sheet.py.
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

_SRC_PATH = os.path.join(HERE, 'build_h1303_abbrev_sheet.py')
_SHEET_MARKER = '\n# ---------------------------------------------------------------- sheet\n'

_AMBIG_RE = re.compile(
    r'коллиз|осторожно|неверно|нет фикс|фиксированного соответствия нет|'
    r'вопрос к источнику|OCR|шум|артефакт|кандидат на')

_HEADER_RE = re.compile(r'^\s*#\s*---\s*(.+)$', re.M)
_TOKEN_RE = re.compile(r"'((?:[^'\\]|\\.)*)':\s*dict\(")

# One-line precedent citation per H1303 section header (H1682 step 1: every
# token's classification must carry a cited precedent -- these are the
# RULE-level citations; residue tokens additionally carry their own O[tok]
# note verbatim in the tsv/sheet).
SECTION_CITATION = {
    'cross-reference / deictic (RU_MAP ratifications + additions)':
        'RU_MAP (pwg_ab_ru.py) + MG 10-07-2026 AskUserQuestion ruling '
        '(ABBREVIATIONS_RU.md Bucket A) + DA-vote N3(a)/N4 "все немецкие '
        'сокращения переводятся" (H178_DA_VOTE_ISSUE_REGISTER, 19-07-2026)',
    'meaning / designation / usage labels':
        'RU_MAP + DA-vote N3(a)/N4; MG\'s own worked examples Bein./N. pr. '
        '(ABBREVIATIONS_RU.md "MG flagged... Bein. Vṛṣaṇaśva\'s")',
    'domain labels':
        'ABBREVIATIONS_RU.md "subject-domain labels (semantic-field tags, '
        'not grammar) translate like any encyclopedic register label" + RU_MAP',
    'contextual German word-abbreviations (n=-attribute class)':
        'Mechanism note, not a per-token RU_MAP entry: these tokens\' visible '
        'German expansion lives in the source\'s own `n=` attribute, which '
        'varies per occurrence -- no context-independent fixed correspondence '
        'is possible at the token level (O dict notes, H1303 Session 1)',
    'grammatical: cases (uniform internationalism: 8 cases vs 6 русских)':
        'MG 31-07-2026 LOCK: cases stay Latin visible (Acc./Loc./Instr./Dat./'
        'Abl./Gen./Nom./Voc.); tooltip/legend = full Latin + Russian case name '
        '(Kochergina model: A. - accusativus - винительный падеж). LES forms '
        '(акк., вин. п.) metalanguage only, never visible replacement. N5 does '
        'NOT mean "translate Acc." — cases are Latin-stay by MG 31-07 (overrules '
        'prior LES-sanctioned акк. for visible tokens; H2047)',
    'grammatical: number / gender / person':
        'DA-vote N3/N5/N8 (19-07-2026), same grammatical-translate policy as cases',
    'grammatical: voice / secondary stems':
        'DA-vote N3/N5/N8 (19-07-2026); N8 specifically pins Caus. -> кауз.',
    'grammatical: tense / mood':
        'DA-vote N5 (19-07-2026): "Abbreviations like Aor. cannot stay '
        'untranslated; only Latin ones stay, by common agreement, via a '
        'ratified unified list"',
    'grammatical: non-finite / POS / syntax':
        'DA-vote N3/N5/N8 (19-07-2026), same grammatical-translate policy',
    'grammatical: valency / diathesis-adjacent':
        'DA-vote N3/N5/N8 (19-07-2026), same grammatical-translate policy',
    'grammatical: word formation / morphology / degree':
        'DA-vote N3/N5/N8 (19-07-2026), same grammatical-translate policy',
    'source / citation mechanics':
        'DA-vote N4 (ed. Bomb. = Бомбейская ред.) + N9 (Verz. d. Oxf. H.); '
        'Sch./Schol./Comm. translated as native Russian classical-philology '
        'forms (схол./коммент.), same rationale as the "see/cf." family',
}


def _parse_sections():
    """Return (order, subgroup_of) — the 12 `# --- ...` section headers in
    build_h1303_abbrev_sheet.py's O dict, in source order, and a
    token -> header-label map, parsed straight from the source text (no
    hand-copied token lists -- avoids re-typing 269 tokens by hand)."""
    src = io.open(_SRC_PATH, encoding='utf-8').read()
    start = src.index('O = {')
    end = src.index('\n\n\nBUCKET_NAMES')
    block = src[start:end]
    headers = [(m.start(), m.group(1).strip()) for m in _HEADER_RE.finditer(block)]
    headers.append((len(block), None))
    order = []
    subgroup_of = {}
    for i in range(len(headers) - 1):
        pos, label = headers[i]
        nxt = headers[i + 1][0]
        segment = block[pos:nxt]
        order.append(label)
        for tm in _TOKEN_RE.finditer(segment):
            subgroup_of[tm.group(1)] = label
    return order, subgroup_of


def _load_overlay_module():
    """Exec build_h1303_abbrev_sheet.py up to (not including) its sheet-
    writing tail, in an isolated namespace -- gives us the real O dict +
    the real store-backed `toks` inventory (freq/de/en/in_pwgab/ru_map)
    without regenerating/overwriting the old h1303_abbrev_sheet.html."""
    src = io.open(_SRC_PATH, encoding='utf-8').read()
    prefix = src[:src.index(_SHEET_MARKER)]
    ns = {'__name__': 'h1303_abbrev_overlay', '__file__': _SRC_PATH}
    exec(compile(prefix, _SRC_PATH, 'exec'), ns)
    return ns


def classify():
    """Return a dict:
      order         -- 12 section labels, source order
      citation      -- {label: one-line precedent citation}
      by_token      -- {token: {..., 'section': label, 'residue': bool,
                                 'rule_bulk': bool}} for every real (in-store)
                        token, 269 entries as of 26-07-2026
      toks_meta     -- the underlying inventory() rows (freq/de/en/ru_map)
      sections      -- {label: {'bulk': [tok...], 'residue': [tok...]}}
    """
    order, subgroup_of = _parse_sections()
    ns = _load_overlay_module()
    O, toks = ns['O'], ns['toks']
    inv_by_tok = {t['token']: t for t in toks}

    by_token = {}
    sections = {label: {'bulk': [], 'residue': []} for label in order}
    for tok, meta in inv_by_tok.items():
        o = O.get(tok)
        if o is None:
            continue  # would be a NEW-TOKEN; none as of 26-07-2026 (verified: toks == O keys)
        label = subgroup_of.get(tok, 'unclassified (BUG: no section header matched)')
        note = o.get('note', '')
        residue = (o['ru'] is None) or bool(_AMBIG_RE.search(note))
        row = {
            'token': tok, 'freq': meta['freq'], 'de': meta['de'], 'en': meta['en'],
            'ru_map_current': meta['ru_map'], 'bucket': o['b'], 'cls': o['cls'],
            'ru_proposed': o['ru'], 'note': note, 'section': label, 'residue': residue,
        }
        by_token[tok] = row
        sections[label]['residue' if residue else 'bulk'].append(tok)

    return {
        'order': order,
        'citation': SECTION_CITATION,
        'by_token': by_token,
        'toks_meta': toks,
        'sections': sections,
    }


def selftest():
    result = classify()
    n = len(result['by_token'])
    assert n == 269, 'expected 269 real ab-tokens (H1303 21-07-2026 inventory), got %d' % n
    n_bulk = sum(1 for r in result['by_token'].values() if not r['residue'])
    n_residue = sum(1 for r in result['by_token'].values() if r['residue'])
    assert n_bulk + n_residue == n
    assert set(result['citation']) == set(result['order']), 'every section must carry a citation'
    for label in result['order']:
        sec = result['sections'][label]
        assert len(sec['bulk']) + len(sec['residue']) == sum(
            1 for r in result['by_token'].values() if r['section'] == label)
    print('h1682_abbrev_collapse selftest: PASS (%d tokens: %d bulk / %d residue across %d sections)'
          % (n, n_bulk, n_residue, len(result['order'])))
    return True


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    if '--selftest' in sys.argv:
        selftest()
    else:
        r = classify()
        for label in r['order']:
            sec = r['sections'][label]
            print('%-70s bulk=%3d residue=%3d' % (label, len(sec['bulk']), len(sec['residue'])))
        print('TOTAL bulk=%d residue=%d'
              % (sum(len(s['bulk']) for s in r['sections'].values()),
                 sum(len(s['residue']) for s in r['sections'].values())))
