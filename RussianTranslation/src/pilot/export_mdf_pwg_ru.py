#!/usr/bin/env python
r"""export_mdf_pwg_ru.py — promoted pwg_ru cards -> MDF (SIL Multi-Dictionary Formatter) SFM.

READ-ONLY consumer of the promoted store (src/pwg_ru_translated.jsonl). Never
writes to the store, the TMs, the queues, or any harness artifact — it turns
already-promoted de+ru(+en) sense rows into standard-format MDF records
(Toolbox/FLEx lineage) so the RU translation has an exchange format consumable
by the language-documentation toolchain (Lexique Pro, Webonary, Dictionary App
Builder). Design note: RussianTranslation/docs/MDF_EXPORT_PWG_RU.md. Profile
alignment: csl-standards data/schema/mdf-export-profile.json (marker inventory
and Coward & Grimes 2000 App. B field order; checked by --selftest when the
sibling csl-standards clone is present).

Language lanes (the book's national-vs-English contrast, C&G 2000 §2.3):
  \de  Russian   — the national/target-language definition (the primary lane;
                   same ruling as csl-standards gives SKD/VCP their Sanskrit \de)
  \ge  English   — the secondary gloss lane, emitted only when promote_en.py has
                   attached an `en` field to the row (absent rows stay \de-only;
                   never fabricated)
The German source text is deliberately NOT exported: it is PWG's own material,
recoverable from the store / csl-orig via the meta pointer, and this dataset is
the *translation*, not a PWG re-edition.

RANGE-SET gate (C&G 2000 §9.7): <ab> abbreviation tokens and \ps values are
checked against closed vocabularies (PWG's own pwgab table for <ab>; PS_RANGE
below for \ps). Violations are counted and reported; --strict makes them fatal.

  python src/pilot/export_mdf_pwg_ru.py --selftest
  python src/pilot/export_mdf_pwg_ru.py --keys Ap --out out.mdf      # sample
  python src/pilot/export_mdf_pwg_ru.py --out full.mdf --strict      # everything
"""
import argparse
import json
import os
import re
import sys
from collections import OrderedDict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
for p in (HERE, SRC):
    if p not in sys.path:
        sys.path.insert(0, p)

import pwg_ab                     # noqa: E402  authoritative <ab> table (791 entries)
import pwg_ab_ru                  # noqa: E402  RU display policy (Bucket A -> Russian)
from build_article_site import slp1_iast  # noqa: E402  shared SLP1->IAST, no transcoder #63

PROFILE_VERSION = 'mdf-export-pwg-ru-v0.1'
NATIONAL_LANGUAGE = 'ru'

DEFAULT_STORE = os.path.join(SRC, 'pwg_ru_translated.jsonl')

# Marker subset used by this exporter — must stay inside the csl-standards
# mdf-export-profile-v0.1 inventory (selftest cross-checks when the sibling
# clone is present).
MARKERS = ('lx', 'hm', 'ps', 'sn', 'ge', 'de', 'bb', 'nt')

# Canonical relative field order, C&G 2000 App. B, as fixed by the csl-standards
# profile schema. \sn/\ge/\de repeat as one sense block per sense (bilingual
# deviation from the MW profile, where \de never repeats — documented in the
# design note).
FIELD_ORDER = ('lx', 'hm', 'lc', 'se', 'ps', 'sn', 'ge', 're', 'de', 'xv', 'xn',
               'lf', 'le', 'cf', 'va', 'et', 'es', 'sd', 'bb', 'nt')
SENSE_BLOCK = frozenset(('sn', 'ge', 'de'))

# RANGE-SET (§9.7) closed vocabulary for \ps: every <lex> value observed in the
# promoted store as of 11-07-2026 plus the standard PWG gender/POS inventory.
# A value outside the set is a range violation, not a silent passthrough.
PS_RANGE = frozenset((
    'm.', 'f.', 'n.', 'mfn.', 'adj.', 'Adj.', 'adv.', 'Adv.', 'ind.',
    'Indecl.', 'indecl.', 'interj.', 'Interj.', 'Pronomm.', 'pron.',
    'm. f.', 'f. m.', 'm. n.', 'n. m.', 'f. n.', 'n. f.',
))

_LS = re.compile(r'<ls(?:\s+n="([^"]*)")?\s*>(.*?)</ls>', re.S)
_AB = re.compile(r'<ab>(.*?)</ab>', re.S)
_LEX = re.compile(r'<lex>(.*?)</lex>', re.S)
_IS = re.compile(r'<is\b[^>]*>(.*?)</is>', re.S)
_SK = re.compile(r'\{#(.*?)#\}', re.S)
_GL = re.compile(r'\{%(.*?)%\}', re.S)
_TAG = re.compile(r'<[^>]+>')
_PAGE = re.compile(r'\[Page[^\]]*\]')
_HM = re.compile(r'~~h(\d+)_')
_WS = re.compile(r'\s+')


def one_line(s):
    return _WS.sub(' ', s or '').strip()


def ab_tokens(text):
    return [one_line(m.group(1)) for m in _AB.finditer(text or '')]


def check_ab_range(tokens, violations):
    """RANGE-SET gate: every <ab> token must resolve in PWG's own pwgab table.
    The table is lowercase-keyed, so sentence-initial capitals (Pass., Act.)
    are folded before being declared out-of-range."""
    for tok in tokens:
        if pwg_ab.resolve(tok) is None and pwg_ab.resolve(tok.lower()) is None:
            violations.append(('ab', tok))


def bb_citations(text):
    """Distinct <ls> citations, in order. <ls n="M.">8,64.</ls> continuation
    form is expanded to 'M. 8,64.' so every \\bb is self-contained."""
    seen = OrderedDict()
    for n, inner in _LS.findall(text or ''):
        inner = one_line(inner)
        value = one_line('%s %s' % (n, inner)) if n else inner
        if value:
            seen.setdefault(value, None)
    return list(seen)


def clean_prose(text, lang):
    """One MDF field line from a store prose field.

    <ls> kept inline as plain sigla (the citation is part of the printed
    definition; \\bb additionally lists it for machines), <ab> rendered per the
    tooltip policy (RU: pwg_ab_ru Bucket-A translation, Bucket-B Latin
    fallback; EN: original token), {#..#} SLP1 -> IAST, {%..%} unwrapped,
    <is> proper names kept IAST (site-level Cyrillicization is not yet
    corpus-validated — ABBREVIATIONS_RU.md open item), leftover tags stripped.
    """
    t = text or ''
    t = _LS.sub(lambda m: one_line('%s %s' % (m.group(1) or '', one_line(m.group(2)))), t)
    if lang == 'ru':
        t = _AB.sub(lambda m: pwg_ab_ru.display(one_line(m.group(1)))[0], t)
    else:
        t = _AB.sub(lambda m: one_line(m.group(1)), t)
    t = _IS.sub(lambda m: one_line(m.group(1)), t)
    t = _SK.sub(lambda m: slp1_iast(one_line(m.group(1))), t)
    t = _GL.sub(lambda m: m.group(1), t)
    t = _TAG.sub(' ', t)
    t = _PAGE.sub(' ', t)          # print-page markers are layout, not prose
    t = t.replace('¦', ' ')   # PWG's headword¦body separator
    return one_line(t)


def card_ps(rows, violations):
    """First <lex> across the card's RU (then DE) fields -> \\ps, range-checked."""
    for field in ('ru', 'de'):
        for row in rows:
            m = _LEX.search(row.get(field) or '')
            if m:
                value = one_line(_TAG.sub(' ', m.group(1)))
                if value not in PS_RANGE:
                    violations.append(('ps', value))
                return value
    return None


def card_hm(subcard):
    m = _HM.search(subcard or '')
    return m.group(1) if m and m.group(1) != '0' else None


def observed_sense_numbers(rows):
    """PWG prints real sense numbers (unlike MW's prose senses). When every row
    carries a distinct purely-numeric sense_tag, that printed numbering is used
    as-is; otherwise numbering is inferred 1..n and flagged with the same
    \\nt convention csl-standards uses."""
    tags = [str(r.get('sense_tag') or '') for r in rows]
    if all(re.fullmatch(r'\d+', t) for t in tags) and len(set(tags)) == len(tags):
        return tags, True
    return [str(i + 1) for i in range(len(rows))], False


def mdf_record(key1, subcard, rows, violations):
    lines = []
    notes = []

    lines.append('\\lx %s' % (one_line(rows[0].get('iast')) or slp1_iast(key1)))

    hm = card_hm(subcard)
    if hm:
        lines.append('\\hm %s' % hm)

    ps = card_ps(rows, violations)
    if ps:
        lines.append('\\ps %s' % ps)

    for row in rows:
        check_ab_range(ab_tokens(row.get('ru')), violations)

    bb = OrderedDict()
    numbers, observed = observed_sense_numbers(rows)
    multi = len(rows) > 1
    for number, row in zip(numbers, rows):
        if multi:
            lines.append('\\sn %s' % number)
        en = row.get('en')
        if en:
            lines.append('\\ge %s' % clean_prose(en, 'en'))
        lines.append('\\de %s' % clean_prose(row.get('ru'), 'ru'))
        for cite in bb_citations(row.get('ru')):
            bb.setdefault(cite, None)
    for cite in bb:
        lines.append('\\bb %s' % cite)

    if multi and not observed:
        notes.append('\\nt sense-numbering: inferred from row order, not observed in source')

    prov = rows[0].get('provenance') or {}
    meta = ('\\nt meta: profile=%s; national=%s; slp1=%s; subcard=%s; '
            'src=PWG pc=%s page=%s; review=%s; model=%s' % (
                PROFILE_VERSION, NATIONAL_LANGUAGE, key1, subcard,
                rows[0].get('column') or '-', rows[0].get('page') or '-',
                rows[0].get('review_status') or '-',
                prov.get('model_version') or '-'))

    return '\n'.join(lines + notes + [meta]) + '\n'


def load_cards(store_path, keys=None, limit=None):
    """Group store rows into cards by (key1, subcard), preserving store order
    within a card. Yields (key1, subcard, rows) sorted by IAST headword."""
    cards = OrderedDict()
    with open(store_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if keys and row.get('key1') not in keys:
                continue
            cards.setdefault((row.get('key1'), row.get('subcard')), []).append(row)
    items = sorted(cards.items(), key=lambda kv: (slp1_iast(kv[0][0] or '').lower(), kv[0][1] or ''))
    if limit:
        items = items[:limit]
    return items


def export(store_path, out_path, keys=None, limit=None):
    violations = []
    records = []
    for (key1, subcard), rows in load_cards(store_path, keys, limit):
        records.append(mdf_record(key1, subcard, rows, violations))
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(records))
    return len(records), violations


# ---------------------------------------------------------------- validation

def parse_fields(text):
    fields = []
    for line in text.split('\n'):
        if not line.strip():
            continue
        m = re.match(r'^\\(\w+)(?:\s+(.*))?$', line)
        fields.append({'marker': m.group(1) if m else None,
                       'value': (m.group(2) or '').strip() if m else line})
    return fields


def order_violations(markers):
    """Field-order check mirroring csl-standards validate-mdf-profile.mjs,
    with \\sn/\\ge/\\de sharing one sense-block key (the bilingual deviation)."""
    sense_key = min(FIELD_ORDER.index(m) for m in SENSE_BLOCK)
    bad = []
    max_seen = -1
    for marker in markers:
        key = sense_key if marker in SENSE_BLOCK else (
            FIELD_ORDER.index(marker) if marker in FIELD_ORDER else None)
        if key is None:
            continue
        if key < max_seen:
            bad.append(marker)
        else:
            max_seen = max(max_seen, key)
    return bad


def validate_records(text):
    """Structural marker-profile validation of an exported .mdf text."""
    problems = []
    for i, block in enumerate(t for t in text.split('\n\n') if t.strip()):
        where = 'record %d' % (i + 1)
        fields = parse_fields(block)
        markers = [f['marker'] for f in fields]
        if markers[:1] != ['lx']:
            problems.append('%s: must begin with \\lx' % where)
        if any(m is None for m in markers):
            problems.append('%s: non-marker line' % where)
        unknown = sorted({m for m in markers if m and m not in MARKERS})
        if unknown:
            problems.append('%s: markers outside profile: %s' % (where, ', '.join(unknown)))
        bad = order_violations([m for m in markers if m])
        if bad:
            problems.append('%s: field order violated at: %s' % (where, ', '.join(sorted(set(bad)))))
        if not any(f['marker'] == 'nt' and f['value'].startswith('meta:') for f in fields):
            problems.append('%s: missing meta note' % where)
        if not any(f['marker'] == 'de' for f in fields):
            problems.append('%s: no \\de definition' % where)
    return problems


def profile_schema_path():
    return os.path.join(os.path.dirname(os.path.dirname(SRC)), '..',
                        'csl-standards', 'data', 'schema', 'mdf-export-profile.json')


# ------------------------------------------------------------------ selftest

FIXTURE_ROWS = [
    {'key1': 'Ap', 'subcard': '_ap~~h0_00_pwg01', 'iast': 'āp', 'sense_tag': '6',
     'ru': '6) {%близкий, родственный%}; <lex>m.</lex> {%родственник%} '
           '(<ab>vgl.</ab> {#Api#}) <ls>M. 2,109.</ls> <ls n="M.">8,64.</ls>',
     'de': 'x', 'review_status': 'ai_translated',
     'provenance': {'model_version': 'claude-sonnet-5'},
     'column': '1-0649', 'page': '1-p0325'},
    {'key1': 'Ap', 'subcard': '_ap~~h0_00_pwg01', 'iast': 'āp', 'sense_tag': '7',
     'ru': '7) {%достигать%} {#Apnoti#} <ls>YĀJÑ. 1,28.</ls>', 'de': 'x',
     'en': '7) {%to reach%} {#Apnoti#}',
     'review_status': 'ai_translated', 'provenance': {'model_version': 'claude-sonnet-5'},
     'column': '1-0649', 'page': '1-p0325'},
]


def selftest():
    ok = True

    def check(cond, name):
        nonlocal ok
        print('%s %s' % ('PASS' if cond else 'FAIL', name))
        ok = ok and cond

    violations = []
    rec = mdf_record('Ap', '_ap~~h0_00_pwg01', FIXTURE_ROWS, violations)
    fields = parse_fields(rec)
    markers = [f['marker'] for f in fields]

    check(markers[0] == 'lx' and fields[0]['value'] == 'āp', 'lx is IAST headword')
    check('hm' not in markers, 'h0 homonym suppressed')
    check(fields[markers.index('ps')]['value'] == 'm.', 'ps from <lex>')
    check(markers.count('sn') == 2 and markers.count('de') == 2, 'per-sense sn+de')
    check(markers.count('ge') == 1, 'ge only where en exists — never fabricated')
    sn_vals = [f['value'] for f in fields if f['marker'] == 'sn']
    check(sn_vals == ['6', '7'], 'observed PWG sense numbers kept')
    de1 = [f['value'] for f in fields if f['marker'] == 'de'][0]
    check('ср.' in de1 and 'vgl' not in de1, 'Bucket-A <ab> translated to RU (vgl.->ср.)')
    check('āpi' in de1.lower(), 'SLP1 {#..#} -> IAST in prose')
    bb_vals = [f['value'] for f in fields if f['marker'] == 'bb']
    check(bb_vals == ['M. 2,109.', 'M. 8,64.', 'YĀJÑ. 1,28.'],
          'bb citations incl. n= continuation expansion')
    check(not violations, 'no range violations on clean fixture')
    check(not validate_records(rec), 'record passes structural profile validation')

    poisoned = [dict(FIXTURE_ROWS[0], ru='{%x%} <ab>zzz9.</ab> <lex>weird.</lex>')]
    bad = []
    mdf_record('Ap', '_ap~~h0_00_pwg01', poisoned, bad)
    check(('ab', 'zzz9.') in bad, 'RANGE-SET gate trips on unknown <ab>')
    check(('ps', 'weird.') in bad, 'RANGE-SET gate trips on out-of-range \\ps')

    check(order_violations(['lx', 'ps', 'sn', 'ge', 'de', 'sn', 'de', 'bb', 'nt']) == [],
          'sense block repeats legally')
    check(order_violations(['lx', 'bb', 'ps']) == ['ps'], 'order check catches regression')

    schema = profile_schema_path()
    if os.path.exists(schema):
        with open(schema, encoding='utf-8') as f:
            prof = json.load(f)
        inventory = {m.lstrip('\\') for m in prof['markers']}
        check(set(MARKERS) <= inventory, 'marker subset within csl-standards inventory')
        check(tuple(m.lstrip('\\') for m in prof['fieldOrder']) == FIELD_ORDER,
              'field order matches csl-standards profile schema')
    else:
        print('SKIP csl-standards profile schema not present (%s)' % schema)

    print('selftest %s' % ('PASS' if ok else 'FAIL'))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--store', default=DEFAULT_STORE)
    ap.add_argument('--out', default=os.path.join(HERE, 'output', 'pwg_ru_full.mdf'))
    ap.add_argument('--keys', help='comma-separated key1 filter (sample export)')
    ap.add_argument('--limit', type=int, help='max cards')
    ap.add_argument('--strict', action='store_true', help='range violations are fatal')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()

    if args.selftest:
        sys.exit(selftest())

    if not os.path.exists(args.store):
        sys.exit('store not found: %s (local-only file; pass --store)' % args.store)

    keys = set(args.keys.split(',')) if args.keys else None
    count, violations = export(args.store, args.out, keys, args.limit)
    with open(args.out, encoding='utf-8') as f:
        problems = validate_records(f.read())
    print('exported %d records -> %s' % (count, args.out))
    if violations:
        summary = {}
        for kind, value in violations:
            summary.setdefault(kind, set()).add(value)
        for kind, values in sorted(summary.items()):
            print('RANGE-SET violations (%s): %d distinct: %s' % (
                kind, len(values), ', '.join(sorted(values)[:20])))
    if problems:
        print('structural validation problems:')
        for p in problems[:20]:
            print('- %s' % p)
    if (violations and args.strict) or problems:
        sys.exit(1)


if __name__ == '__main__':
    main()
