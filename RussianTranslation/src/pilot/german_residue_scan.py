#!/usr/bin/env python
r"""german_residue_scan.py -- detect untranslated German PROSE residue in the RU field.

Defect class (H1302, H178 DA-vote rows N16/N19): a German prose function word or fixed
phrase surviving untranslated in the `ru` field OUTSIDE protected markup -- e.g. *zu* in
"<ab>Schol.</ab> zu <ls>ŚĀK. 14.</ls>" (should be «к»), or *mit Ergänzung von*. This is
DISTINCT from `<ab>`-tagged abbreviations (those are render-time, H1303 scope) and from the
Russian glosses inside `{%…%}` (translated content, protected). See the register:
RussianTranslation/pwg_ru/H178_DA_VOTE_ISSUE_REGISTER_2026-07-19.md.

Scope fence (guardrail): this sweep touches ONLY prose outside
`<ab>`/`<ls>`/`<is>`/`<lex>`/`{%…%}`/`{#…#}`/«…»/`<div…>`/`[Page…]`. Everything else is masked
before scanning.

Reuse (not reinvented):
  - protected-span mask: extends the PROTECTED regex idea from fix_german_connectives.py
    (adds <lex>, generic tags, and [Page…] markers).
  - candidate lexicon: seeded from GERMAN_RESIDUE + GERMAN_GLOSS_WORDS in prompt_rule_audit.py,
    plus the survivors those lists miss (zu, bei, nach, unter, statt, dessen, im, am, Ende, …).
  - false-positive guards: LATIN_WORDS / FRENCH_CONTEXT_WORDS / AMBIGUOUS_DE_FR_WORDS from
    foreign_literal_guards.py (deliberately-preserved Latin euphemisms / French glosses).

Per hit it emits: key (key1|subcard|sense_tag), matched token/phrase, ±40-char context, and a
suggested class slot: 'a' deterministic-fixable, 'b' needs-retranslation, 'c' false-positive.

  python src/pilot/german_residue_scan.py            # scan the canonical store, write report
  python src/pilot/german_residue_scan.py --json out.jsonl
  python src/pilot/german_residue_scan.py --selftest  # fixture assertions (used by window_selftest)
"""
import argparse
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
if SRC not in sys.path:
    sys.path.insert(0, SRC)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from store_path import canonical_store  # noqa: E402
from foreign_literal_guards import (  # noqa: E402
    LATIN_WORDS, FRENCH_CONTEXT_WORDS, AMBIGUOUS_DE_FR_WORDS)

# ---------------------------------------------------------------------------
# Protected spans -- masked to spaces (offsets preserved) before scanning.
# Paired tags first (so a closed <ab>…</ab> is consumed whole), then any residual
# single tag (unclosed <div n="1">, self-close), then braces / quotes / page markers.
# ---------------------------------------------------------------------------
PROTECTED = re.compile(
    r'\{%.*?%\}'                                              # Russian gloss (translated)
    r'|\{#.*?#\}'                                             # Sanskrit (HK/SLP1)
    r'|«[^»]*»'                                               # verbatim quote
    r'|<(?:ab|ls|is|lex)\b[^>]*>.*?</(?:ab|ls|is|lex)>'       # paired siglum/markup tag
    r'|<[^>]*>'                                               # residual single tag (div, self-close)
    r'|\[Page[^\]]*\]'                                        # page-break marker
    r'|\[NWS:[^\]]*\]',                                       # NWS source-attribution bracket (bib refs)
    re.S | re.I)

# Proper names that carry German orthography (ß / umlaut) but are AUTHORS, not prose residue --
# they must never be flagged (they appear in author-year citations like "Böhtlingk 1840 : 548").
PROPER_NAMES = frozenset({'böhtlingk', 'graßmann', 'grassmann', 'böhtl'})


def mask_protected(text):
    """Return `text` with every protected span overwritten by same-length spaces."""
    out = list(text)
    for m in PROTECTED.finditer(text):
        for i in range(m.start(), m.end()):
            out[i] = ' '
    return ''.join(out)


# ---------------------------------------------------------------------------
# German residue lexicon. Whole-word ASCII matches so they can never land inside a
# Cyrillic or Sanskrit token. Seeded from prompt_rule_audit.GERMAN_GLOSS_WORDS and
# extended with the exact survivors that list misses (register §6 item 1).
# ---------------------------------------------------------------------------
_GERMAN_WORDS = [
    # articles / pronouns / determiners
    'der', 'die', 'das', 'den', 'dem', 'des', 'dessen', 'dieses', 'diese', 'dieser',
    'eine', 'einer', 'eines', 'einem', 'einen', 'ein', 'kein', 'keine',
    # conjunctions / particles / adverbs
    'und', 'oder', 'aber', 'auch', 'wohl', 'vielleicht', 'nicht', 'noch', 'nur', 'so',
    'als', 'wie', 'woraus', 'wenn', 'dann', 'sowie', 'sondern',
    # prepositions
    'mit', 'ohne', 'von', 'für', 'bei', 'beim', 'nach', 'unter', 'statt', 'im', 'am',
    'zum', 'zur', 'aus', 'gegen', 'ueber',
    # verb particle / infinitive marker seen in "zu ziehen", "Schol. zu"
    'zu', 'ziehen',
    # jemand family (near-ubiquitous B&R abbreviation)
    'Jmd', 'jmdm', 'jmdn',
    # capitalised German nouns that leaked as glosses
    'Name', 'Art', 'Theil', 'Teil', 'Bedeutung', 'Ende', 'Anfang',
    'Schulter', 'Strahl', 'Sonne', 'Wasser', 'Gewässer', 'Gabe', 'Geschenk',
    'Glanz', 'Schimmer', 'Pracht', 'Feuer', 'Brand', 'Schein', 'Ort', 'Zeit',
    'Grund', 'Handeln', 'Zeug', 'Pflanze', 'Gefäss', 'Gefäß',
    'Ergänzung', 'Ergaenzung', 'Regel', 'Weise',
]
# Longest first so a multi-char token is preferred; \b on both sides.
_LEX_ALT = '|'.join(sorted((re.escape(w) for w in _GERMAN_WORDS), key=len, reverse=True))
GERMAN_TOKEN = re.compile(r'\b(?:' + _LEX_ALT + r')\b', re.I)

# de-only orthographic evidence: umlaut / eszett in unmasked text is German by
# construction (Cyrillic has none; IAST citations live inside {#…#}/<ls>, already masked).
DE_ORTHO = re.compile(r'[äöüßÄÖÜ]')

# ---- deterministic-fix patterns (class 'a'), applied by fix_german_connectives --store ----
# citation "zu": a lone `zu` sitting between a closing siglum tag and a following <ls> cite.
CITATION_ZU = re.compile(r'(?:(?<=</ab>)|(?<=</ls>)|(?<=</is>))(\s*)\bzu\b(\s*)(?=<ls)')
# preverb-section header "Mit {#prefix#}" / "Mit {%…%}" -> «С» (the PW "with preverb X" idiom).
# Case-SENSITIVE capital M so it never touches lowercase prose "mit dem <ab>acc.</ab>".
MIT_HEADER = re.compile(r'\bMit\b(?=\s*\{[#%])')
# fixed editorial phrases (deterministic, class 'a').
MIT_ERGAENZUNG = re.compile(r'\bmit\s+Erg(?:ä|ae)nzung\s+von\b', re.I)
FEHLERHAFT_FUER = re.compile(r'\bfehlerhaft\s+f(?:ü|ue)r\b', re.I)
# citation "bei": a lone `bei` sitting just before an author siglum tag -> «у».
CITATION_BEI = re.compile(r'\bbei\b(\s*)(?=<(?:ls|ab)\b)', re.I)
# lone connectives with an unambiguous single Russian equivalent (from fix_german_connectives).
LONE_DETERMINISTIC = {
    'und': 'и', 'oder': 'или', 'ohne': 'без', 'auch': 'также',
}

CONTEXT = 40


def classify(token, ctx, detector):
    """Suggest a class: 'a' deterministic-fixable, 'b' retranslate, 'c' false positive."""
    low = token.lower()
    # (c) false-positive guards -- proper-name authors + deliberately-preserved Latin/French.
    if low in PROPER_NAMES:
        return 'c'
    if LATIN_WORDS.search(ctx):
        return 'c'
    if low in AMBIGUOUS_DE_FR_WORDS and FRENCH_CONTEXT_WORDS.search(ctx):
        return 'c'
    # (a) deterministic closed set.
    if detector in ('citation_zu', 'mit_ergaenzung', 'fehlerhaft_fuer',
                    'citation_bei', 'mit_header'):
        return 'a'
    if detector == 'lex' and low in LONE_DETERMINISTIC:
        return 'a'
    # everything else (multi-word German grammatical prose, ambiguous connectives) -> retranslate.
    return 'b'


def scan_text(text):
    """Yield (token, context, suggested_class) for every German-residue hit in `text`.

    Overlapping detectors (specific phrase > lexicon token > umlaut orthography) are
    resolved by keeping the highest-priority hit per text span, so `mit Ergänzung von`
    counts once, not three times.
    """
    masked = mask_protected(text)
    cands = []   # (start, end, token, detector, priority)  -- lower priority wins

    def add(s, e, token, detector, prio):
        cands.append((s, e, token, detector, prio))

    # priority 0: specific multi-token / context phrases (detected on the ORIGINAL where tags matter)
    for m in CITATION_ZU.finditer(text):
        s = m.start() + len(m.group(1))
        add(s, s + 2, 'zu', 'citation_zu', 0)
    for m in MIT_ERGAENZUNG.finditer(masked):
        add(m.start(), m.end(), m.group(0), 'mit_ergaenzung', 0)
    for m in FEHLERHAFT_FUER.finditer(masked):
        add(m.start(), m.end(), m.group(0), 'fehlerhaft_fuer', 0)
    for m in CITATION_BEI.finditer(text):
        add(m.start(), m.start() + 3, 'bei', 'citation_bei', 0)
    for m in MIT_HEADER.finditer(text):
        add(m.start(), m.end(), m.group(0), 'mit_header', 0)

    # priority 1: lexicon tokens (masked text -- protected spans excluded)
    for m in GERMAN_TOKEN.finditer(masked):
        add(m.start(), m.end(), m.group(0), 'lex', 1)

    # priority 2: de-only orthography (umlaut / ß) widened to the whole word
    for m in DE_ORTHO.finditer(masked):
        a = m.start()
        while a > 0 and (masked[a - 1].isalpha() or masked[a - 1] in "äöüßÄÖÜ"):
            a -= 1
        b = m.end()
        while b < len(masked) and (masked[b].isalpha() or masked[b] in "äöüßÄÖÜ"):
            b += 1
        add(a, b, text[a:b], 'ortho', 2)

    # resolve overlaps: walk highest-priority-first, accept a hit only if it does not
    # overlap an already-accepted span; then re-emit in document order.
    spans = []
    out = []
    for s, e, token, detector, prio in sorted(cands, key=lambda c: (c[4], c[0])):
        if any(not (e <= as_ or s >= ae) for as_, ae in spans):
            continue
        spans.append((s, e))
        ctx = text[max(0, s - CONTEXT):e + CONTEXT].replace('\n', ' ')
        out.append((s, token, ctx, classify(token, ctx, detector)))
    for _, token, ctx, cls in sorted(out):
        yield (token, ctx, cls)


def iter_store(store):
    with open(store, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def run(store, json_out=None):
    hits = []
    n_rows = 0
    for r in iter_store(store):
        n_rows += 1
        ru = r.get('ru') or ''
        for token, ctx, cls in scan_text(ru):
            hits.append({
                'key': '%s|%s|%s' % (r.get('key1'), r.get('subcard'), r.get('sense_tag')),
                'key1': r.get('key1'), 'subcard': r.get('subcard'),
                'sense_tag': r.get('sense_tag'),
                'token': token, 'context': ctx, 'suggested_class': cls,
            })
    if json_out:
        with open(json_out, 'w', encoding='utf-8') as f:
            for h in hits:
                f.write(json.dumps(h, ensure_ascii=False) + '\n')
    return hits, n_rows


def summarize(hits, n_rows):
    from collections import Counter
    by_tok = Counter(h['token'].lower() for h in hits)
    by_cls = Counter(h['suggested_class'] for h in hits)
    print('rows scanned      : %d' % n_rows)
    print('total hits        : %d' % len(hits))
    print('rows with a hit   : %d' % len({h['key'] for h in hits}))
    print('by suggested class: ' + ', '.join('%s=%d' % (c, by_cls[c]) for c in sorted(by_cls)))
    print('top tokens:')
    for tok, c in by_tok.most_common(40):
        print('  %-24s %d' % (tok, c))


def selftest():
    # a) prose zu in a citation is flagged and classed 'a'
    t1 = '5) {%извлекать%}: {#tApasA#}\n<ab>Schol.</ab> zu <ls>ŚĀK. 14.</ls>'
    hits = list(scan_text(t1))
    assert any(tok == 'zu' and cls == 'a' for tok, _, cls in hits), hits
    # b) mit Ergänzung von flagged 'a'
    t2 = '{%примирить%} mit Ergänzung von {#saha grIveRa#})'
    hits2 = list(scan_text(t2))
    assert any('Erg' in tok and cls == 'a' for tok, _, cls in hits2), hits2
    # c) a protected German gloss / quote is NOT flagged
    t3 = '{%родственник, друг%} «nahe stehend» <ab>vgl.</ab> {#Api#}'
    assert list(scan_text(t3)) == [], list(scan_text(t3))
    # d) pure Russian free text is clean
    t4 = '3) {%отгонять, удалять%}: {#SatrUn#}\n<ls>BHAṬṬ. 16,30.</ls>'
    assert list(scan_text(t4)) == [], list(scan_text(t4))
    # e) grammatical German prose "mit dem" is flagged as retranslate 'b'
    t5 = '{%думать о%}; mit dem <ab>acc.</ab>: {#aBi#}'
    hits5 = list(scan_text(t5))
    assert any(cls == 'b' for _, _, cls in hits5), hits5
    print('german_residue_scan selftest: PASS')
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--store', help='path to the JSONL store (default: canonical_store)')
    ap.add_argument('--json', dest='json_out', help='write per-hit JSONL here')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return
    default_local = os.path.join(SRC, 'pwg_ru_translated.jsonl')
    store = a.store or canonical_store(default_local)
    if not os.path.exists(store):
        sys.exit('STORE ABSENT: %s' % store)
    hits, n_rows = run(store, a.json_out)
    summarize(hits, n_rows)
    if a.json_out:
        print('wrote', a.json_out)


if __name__ == '__main__':
    main()
