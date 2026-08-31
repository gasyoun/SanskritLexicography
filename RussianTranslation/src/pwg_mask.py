#!/usr/bin/env python
"""pwg_ru stage-0 — PWG card extractor + placeholder masker (De→Ru, no API).

Walks csl-orig/v02/pwg/pwg.txt, splits it into <L>…<LEND> records, and masks
each record so a translator model sees ONLY translatable German. Everything
untranslatable — Sanskrit {#…#}, source refs <ls>, abbreviations <ab>, italic
Sanskrit <is>, grammar <lex>, foreign <lang>, structural tags — becomes a
{Tn} placeholder, restorable left-to-right after translation.

The hard case is `{%…%}`: in PWG it is overwhelmingly a GERMAN gloss (translate,
kept inline). Non-German braces are the exceptions — Latin cognates (after
"lat."/"griech."), botanical binomials, Wilson/English literals — and must be
masked as placeholders so they never enter the translate prompt. Durable
per-span metadata is emitted by ``gloss_lang_spans`` (H1624 G1); the DE string
itself is never rewritten.

Modes:
  python pwg_mask.py stats  [N]        scan N records (default all) → counts
  python pwg_mask.py sample [N]        show N masked records (raw → skeleton + map)
  python pwg_mask.py card   <key1>     mask one record by key1
  python pwg_mask.py gloss-langs <key1>  emit gloss_lang span list for one card
  python pwg_mask.py --selftest        classifier + round-trip fixtures
"""
import os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
from sibling_root import sibling_root  # noqa: E402
GITHUB = sibling_root(HERE)
PWG = os.path.normpath(os.path.join(GITHUB, 'csl-orig', 'v02', 'pwg', 'pwg.txt'))

# untranslatable PAIRED spans (tag + content both go) — order matters.
# Opening tags use \b[^>]*> so ATTRIBUTED tags (<ls n="ṚV.">…</ls>) are masked
# whole; a bare-<ls> pattern would mask only the tags and leak the citation text.
PAIRED = [r'<ls\b[^>]*>.*?</ls>', r'<ab\b[^>]*>.*?</ab>', r'<is\b[^>]*>.*?</is>',
          r'<lex\b[^>]*>.*?</lex>', r'<lang\b[^>]*>.*?</lang>', r'\{#.*?#\}']
PAIRED_RE = re.compile('|'.join(PAIRED), re.S)
TAG_RE = re.compile(r'<[^>]+>')          # remaining structural/standalone tags
PCT_RE = re.compile(r'\{%(.*?)%\}', re.S)
HEADER_RE = re.compile(r'^<L>([\d.]+)<pc>(.*?)<k1>(.*?)<k2>(.*?)(?:<h>(\d+))?\s*$')   # L-id may be float (Cologne supplements, 635 records)
DE_CHARS = re.compile(r'[äöüßÄÖÜ]')
LATIN_CUE = re.compile(r'(lat\.|latein|griech|gr\.)\W{0,4}$', re.I)
LATIN_PHRASE = re.compile(r'^(De|Ab|Ex|In|Sub|Pro)\s+[a-z]', )  # Latin citation phrase
# C8: In/Ab/Ex/Sub/Pro are German-capitalized homographs of Latin prepositions, so a German gloss
# like "In der Regel" / "In den Schlusssatz einfallen" matched LATIN_PHRASE and was masked-and-
# dropped (never translated). "De" is not a German word, so a "De ..." phrase stays an unguarded
# Latin opener; a homograph opener stays Latin only if NO German function word follows.
HOMOGRAPH_LATIN_OPENER = re.compile(r'^(Ab|Ex|In|Sub|Pro)\b')
DE_FUNCTION = re.compile(r'\b(der|die|das|den|dem|des|ein|eine|einer|einem|einen|und|oder|mit|von'
                         r'|im|zur|zum|auf|für|nicht|auch|nur|wird|ist|sind|dass|wenn|bei|nach)\b',
                         re.I)
HOMOGRAPH = {'in', 'an', 'un', 'et', 'ut', 'a', 'i'}  # de/lat ambiguous short tokens

# --- H1624 G1: durable gloss_lang on {%…%} ---------------------------------
# Stable rule_id values (document in pwg_ru.md §4 / §8.0). Do not rename lightly;
# residue gates and selftests pin these ids.
RULE_LATIN_CUE = 'latin_cue'                 # das lat. / <ab>lat.</ab> / griech.
RULE_LATIN_PHRASE = 'latin_phrase'           # De accentu… / In usum Delphini
RULE_BOTANY_BINOMIAL = 'botany_binomial'     # Trapa bispinosa / Galedupa arborea
RULE_WILSON_EN = 'wilson_en'                 # Wils./WILSON + English content
RULE_ENGL_CUE = 'engl_cue'                   # engl. / englisch near the span
RULE_ENGLISH_CONTENT = 'english_content'     # clear English prose, no DE markers
RULE_HOMOGRAPH_AMBIG = 'homograph_ambig'     # in / an / et … short tokens
RULE_DEFAULT_DE = 'default_de'

# Wilson often sits in <ls>WILS.</ls>; after tag-strip the cue is bare WILS./WILSON.
# Do NOT put \b after the trailing period of WILS. — '.' and the following space are
# both non-word, so \b never fires there and the cue silently missed every "WILS. …".
WILSON_CUE = re.compile(r'(?<![A-Za-z])(?:Wils\.|WILS\.|Wilson|WILSON)(?![A-Za-z])', re.I)
ENGL_CUE = re.compile(r'(?<![A-Za-z])(?:engl\.|englisch)(?![A-Za-z])', re.I)
# Title-case Genus + lowercase epithet(s); German capitalizes every noun, so this
# alone is not enough — GERMAN_GLOSS_GUARD rejects ordinary DE noun phrases.
BINOMIAL = re.compile(r'^[A-Z][a-z]+(?:\s+[a-z][a-z.-]+){1,2}$')
# Shared with prompt_rule_audit.GERMAN_GLOSS_WORDS intent (subset for mask stage-0).
GERMAN_GLOSS_GUARD = re.compile(
    r'\b(?:der|die|das|den|dem|des|und|oder|mit|ohne|von|für|nicht|eine|einer|'
    r'eines|einem|einen|auch|wohl|Name|Art|Theil|Teil|Bedeutung|Schulter|'
    r'Strahl|Sonne|Wasser|Gewässer|Gabe|Geschenk|Glanz|Schimmer|Pracht|Feuer|'
    r'Brand|Schein|Ort|Zeit|Grund|Handeln|Pflanze|Jmd|jmdm|jmdn|du|wie|'
    r'Etwas|Jemand|Eines|Ende|Frau|Gang|Zweig|Liede|Eisen|Litanei|'
    r'Verehrung|Abwesenheit|Gegner|Tochter|Herr|Gespann|Gattin|Feind|'
    r'Vernichter|Lehrer|Sohn|Tempel|Nachkomme|Besieger|Genosse|Gedanke|'
    r'Beginn|Vater|Collyrium|Honig|Weber|Grube|Hure|Zinn|Krystall|'
    r'Sonnenscheibe|Testikeln|Trinkglas|Seidenraupe|Urinblase)\b',
    re.I)
# Clear English prose markers — split strong vs weak (H offline gloss_lang FP fix).
# FINDINGS §464 / DE export memo: english_content was ~77% FP on non-DE labels because
# weak tokens (a/an/of/and/or/with/as/war) match German or bare Latin too easily when
# used as a *sole* signal. Strong markers (the/who/leaving/…/Wilson lemmata) stay
# single-hit; weak markers need ≥2 distinct hits, or a near WILS/engl cue path.
ENGLISH_STRONG = re.compile(
    r'\b(?:the|who|only|used|leaving|abandoning|'
    r'water|fire|sun|moon|king|sacrifice|rice|wind|knowledge|law|right|wrong|'
    r'place|time|body|mind|widower|absent|lover|husband|shell|coin|Cowri|'
    r'thinks|enjoyment|informer|quantity|bubbles|specks|inauspicious|period|'
    r'evil|aspect|planets|vessel|marrow|spread|cowdung|array|variegated|'
    r'girdle|sleepy|lazy|fellow|terrestrial|latitude|mimic|conflict|'
    r'rind|fruit|boundary|passion|soft|down|homes|persons|hogweed)\b',
    re.I)
# Shared/ambiguous short words — never alone sufficient for english_content.
# Note: German "war" (was) and "an" (preposition) are deliberate exclusions from
# any single-hit path; "a"/"of"/"and"/"or"/"with"/"as"/"one" need a second weak
# or any strong hit.
ENGLISH_WEAK = re.compile(
    r'\b(?:a|an|of|or|and|with|as|one|war)\b',
    re.I)
# Back-compat alias (tests / callers that imported ENGLISH_MARKERS).
ENGLISH_MARKERS = re.compile(
    r'\b(?:the|who|only|used|leaving|abandoning|'
    r'water|fire|sun|moon|king|sacrifice|rice|wind|knowledge|law|right|wrong|'
    r'place|time|body|mind|widower|absent|lover|husband|shell|coin|Cowri|'
    r'thinks|enjoyment|informer|quantity|bubbles|specks|inauspicious|period|'
    r'evil|aspect|planets|vessel|marrow|spread|cowdung|array|variegated|'
    r'girdle|sleepy|lazy|fellow|terrestrial|latitude|mimic|conflict|'
    r'rind|fruit|boundary|passion|soft|down|homes|persons|hogweed|'
    r'a|an|of|or|and|with|as|one|war)\b',
    re.I)

# Kinds that leave the translate path (mask as {Tn}).
NON_TRANSLATE_LANGS = frozenset({'la', 'en'})


def records(limit=None):
    # utf-8-sig on READ only: strips a leading BOM if the source ever carries one
    # (a plain utf-8 read leaves '﻿<L>' unmatched and silently DROPS the
    # first record — FL6/CODE_REVIEW 2026-07-04). No-op on BOM-less files.
    buf, n = [], 0
    with open(PWG, encoding='utf-8-sig') as f:
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('<L>'):
                buf = [line]
            elif line.startswith('<LEND>'):
                if buf:
                    yield buf
                    n += 1
                    if limit and n >= limit:
                        return
                buf = []
            elif buf:
                buf.append(line)
    if buf:
        # a record opened with <L> but never closed by <LEND> (truncated source);
        # never yield it downstream, but never lose it silently either
        print('pwg_mask: WARNING — truncated final record dropped (no <LEND>): %r'
              % buf[0][:80], file=sys.stderr)


def parse(buf):
    m = HEADER_RE.match(buf[0])
    key1 = m.group(3) if m else ''
    key2 = m.group(4) if m else ''
    body = '\n'.join(buf[1:])
    return key1, key2, body


def plain_context(text):
    """Strip markup tags so lat./WILS. cues inside <ab>/<ls> are visible."""
    return TAG_RE.sub('', text or '')


def _has_german_markers(content):
    return bool(DE_CHARS.search(content) or DE_FUNCTION.search(content)
                or GERMAN_GLOSS_GUARD.search(content))


def looks_botany_binomial(content):
    """Genus species (optional third epithet); reject ordinary German noun phrases."""
    value = (content or '').strip()
    if not BINOMIAL.match(value) or _has_german_markers(value):
        return False
    return True


def looks_english_content(content):
    """High-confidence English braced gloss (Wilson EN / engl. literals).

    Strong English markers (or dual -ing forms) are enough alone. Weak markers
    (a/an/of/and/or/with/as/one/war) need ≥2 distinct hits so German/Latin
    residue does not take the english_content → translate:False path (§464).
    """
    value = (content or '').strip()
    if not value or _has_german_markers(value):
        return False
    if ENGLISH_STRONG.search(value):
        return True
    weak = {m.group(0).lower() for m in ENGLISH_WEAK.finditer(value)}
    if len(weak) >= 2:
        return True
    # Two distinct -ing tokens ("leaving, abandoning") without a listed lemma.
    ings = re.findall(r'\b[A-Za-z]{3,}ing\b', value)
    if len({t.lower() for t in ings}) >= 2:
        return True
    return False


def classify_pct_detail(content, preceding, following=''):
    """Classify one `{%…%}` span.

    Returns dict:
      gloss_lang: 'de' | 'la' | 'en' | 'ambig'
      rule_id:    stable rule id (see RULE_* constants)
      translate:  True → keep inline for the model; False → mask as {Tn}

    Preceding/following should already be plain (tags stripped / placeholders
    expanded) when called from ``mask``; ``gloss_lang_spans`` strips tags itself.
    """
    content = (content or '').strip()
    prec = (preceding or '').strip()
    foll = (following or '').strip()

    if LATIN_CUE.search(prec):
        return {'gloss_lang': 'la', 'rule_id': RULE_LATIN_CUE, 'translate': False}

    if LATIN_PHRASE.match(content) and not DE_CHARS.search(content):
        # C8: homograph opener + German function word → German prose, not Latin.
        if not (HOMOGRAPH_LATIN_OPENER.match(content) and DE_FUNCTION.search(content)):
            return {'gloss_lang': 'la', 'rule_id': RULE_LATIN_PHRASE, 'translate': False}

    if looks_botany_binomial(content):
        return {'gloss_lang': 'la', 'rule_id': RULE_BOTANY_BINOMIAL, 'translate': False}

    wilson_near = bool(WILSON_CUE.search(prec) or WILSON_CUE.search(foll[:80]))
    engl_near = bool(ENGL_CUE.search(prec) or ENGL_CUE.search(foll[:40]))
    if looks_english_content(content):
        if wilson_near:
            return {'gloss_lang': 'en', 'rule_id': RULE_WILSON_EN, 'translate': False}
        if engl_near:
            return {'gloss_lang': 'en', 'rule_id': RULE_ENGL_CUE, 'translate': False}
        # Clear English without a near cue still must not enter the DE translate path
        # (Wilson often attaches AFTER the span: `{%terrestrial latitude%}, <ls>WILS.</ls>`
        # is covered by following; remaining pure-English braces use english_content).
        return {'gloss_lang': 'en', 'rule_id': RULE_ENGLISH_CONTENT, 'translate': False}

    toks = [t.strip('.,;') for t in content.lower().split()]
    if toks and all(t in HOMOGRAPH for t in toks) and not DE_CHARS.search(content):
        return {'gloss_lang': 'ambig', 'rule_id': RULE_HOMOGRAPH_AMBIG, 'translate': True}

    return {'gloss_lang': 'de', 'rule_id': RULE_DEFAULT_DE, 'translate': True}


def classify_pct(content, preceding, following=''):
    """Return gloss_lang only: 'de' | 'la' | 'en' | 'ambig'.

    Backward-compatible with pre-G1 callers that only inspected de/la/ambig;
    'en' is new (Wilson/English) and is masked like 'la'.
    """
    return classify_pct_detail(content, preceding, following)['gloss_lang']


def gloss_lang_spans(body, context_window=100):
    """Durable per-span metadata for every `{%…%}` in a DE body (no rewrite).

    Each item::
      {
        "span": <inner text>,
        "gloss_lang": "de"|"la"|"en"|"ambig",
        "rule_id": <RULE_*>,
        "translate": bool,
        "start": int,   # offset of '{' in body
        "end": int,     # offset after closing '%}'
      }

    Safe to attach to a portrait/sidecar; never mutates the DE string.
    """
    body = body or ''
    out = []
    for m in PCT_RE.finditer(body):
        start, end = m.start(), m.end()
        prec = plain_context(body[max(0, start - context_window):start])
        foll = plain_context(body[end:end + context_window])
        detail = classify_pct_detail(m.group(1), prec, foll)
        out.append({
            'span': m.group(1).strip(),
            'gloss_lang': detail['gloss_lang'],
            'rule_id': detail['rule_id'],
            'translate': detail['translate'],
            'start': start,
            'end': end,
        })
    return out


def mask(body):
    ph = []
    stats = {
        'sanskrit_ls_ab': 0, 'tags': 0,
        'pct_de': 0, 'pct_la': 0, 'pct_en': 0, 'pct_ambig': 0,
    }

    def take(m):
        ph.append(m.group(0))
        return '{T%d}' % len(ph)

    # 1) paired untranslatable spans (Sanskrit / refs / abbrev / italic / foreign)
    def paired(m):
        stats['sanskrit_ls_ab'] += 1
        return take(m)
    body = PAIRED_RE.sub(paired, body)

    # 2) {%…%}: German kept inline; Latin + English masked; ambiguous flagged-but-kept.
    # The Latin cue ("<ab>lat.</ab>", "griech.") and Wilson cue ("<ls>WILS.</ls>") are
    # overwhelmingly inside tags that step 1 has ALREADY masked to {Tn} — so the raw
    # window would show "{T5}", not "lat."/"WILS.". Expand placeholders back to source
    # and drop tags before classifying.
    def _cue_context(text):
        def _back(mm):
            idx = int(mm.group(1)) - 1
            return ph[idx] if 0 <= idx < len(ph) else mm.group(0)
        return TAG_RE.sub('', re.sub(r'\{T(\d+)\}', _back, text))

    out, last = [], 0
    for m in PCT_RE.finditer(body):
        out.append(body[last:m.start()])
        prec = _cue_context(body[max(0, m.start() - 100):m.start()])
        foll = _cue_context(body[m.end():m.end() + 80])
        detail = classify_pct_detail(m.group(1).strip(), prec, foll)
        kind = detail['gloss_lang']
        if kind in NON_TRANSLATE_LANGS:
            stats['pct_la' if kind == 'la' else 'pct_en'] += 1
            ph.append(m.group(0))
            out.append('{T%d}' % len(ph))
        else:
            stats['pct_de' if kind == 'de' else 'pct_ambig'] += 1
            out.append(m.group(0))          # keep inline for translation
        last = m.end()
    out.append(body[last:])
    body = ''.join(out)

    # 3) any remaining standalone tags (<div>, <H>, <F>, strays)
    def tag(m):
        stats['tags'] += 1
        return take(m)
    body = TAG_RE.sub(tag, body)
    return body, ph, stats


def restore(skeleton, ph):
    def back(m):
        return ph[int(m.group(1)) - 1]
    return re.sub(r'\{T(\d+)\}', back, skeleton)


# ---- CLI -----------------------------------------------------------------
def cmd_stats(args):
    n = int(args[0]) if args else None
    tot = 0
    agg = {
        'sanskrit_ls_ab': 0, 'tags': 0,
        'pct_de': 0, 'pct_la': 0, 'pct_en': 0, 'pct_ambig': 0,
    }
    roundtrip_ok = 0
    for buf in records(n):
        tot += 1
        key1, key2, body = parse(buf)
        sk, ph, st = mask(body)
        for k in agg:
            agg[k] += st[k]
        if restore(sk, ph) == body:
            roundtrip_ok += 1
    print('records scanned: %d' % tot)
    print('round-trip lossless (restore==original): %d/%d (%.2f%%)'
          % (roundtrip_ok, tot, 100.0 * roundtrip_ok / max(tot, 1)))
    print('placeholders by class:')
    for k, v in agg.items():
        print('  %-16s %d' % (k, v))
    pct = agg['pct_de'] + agg['pct_la'] + agg['pct_en'] + agg['pct_ambig']
    if pct:
        print('{%%..%%} DE(translate) %d (%.1f%%) | LA(leave) %d (%.1f%%) | '
              'EN(leave) %d (%.1f%%) | ambig %d (%.1f%%)'
              % (agg['pct_de'], 100.0 * agg['pct_de'] / pct,
                 agg['pct_la'], 100.0 * agg['pct_la'] / pct,
                 agg['pct_en'], 100.0 * agg['pct_en'] / pct,
                 agg['pct_ambig'], 100.0 * agg['pct_ambig'] / pct))


def cmd_sample(args):
    n = int(args[0]) if args else 5
    shown = 0
    for buf in records(2000):
        key1, key2, body = parse(buf)
        if '{%' not in body and '{#' not in body:
            continue
        sk, ph, st = mask(body)
        print('=' * 72)
        print('key1=%s key2=%s' % (key1, key2))
        print('--- raw ---\n%s' % body[:500])
        print('--- skeleton (model sees only this German) ---\n%s' % sk[:500])
        print('--- %d placeholders, e.g. ---' % len(ph))
        for i, p in enumerate(ph[:6], 1):
            print('  {T%d} = %s' % (i, p[:60]))
        shown += 1
        if shown >= n:
            break


def cmd_card(args):
    target = args[0]
    for buf in records():
        key1, key2, body = parse(buf)
        if key1 == target:
            sk, ph, st = mask(body)
            print('key1=%s key2=%s\n--- raw ---\n%s\n--- skeleton ---\n%s\n--- map ---' % (key1, key2, body, sk))
            for i, p in enumerate(ph, 1):
                print('  {T%d} = %s' % (i, p))
            print('round-trip OK:', restore(sk, ph) == body)
            print('--- gloss_lang_spans ---')
            for rec in gloss_lang_spans(body):
                print('  [%s/%s] translate=%s  {%s}' % (
                    rec['gloss_lang'], rec['rule_id'], rec['translate'], rec['span'][:60]))
            return
    print('not found:', target)


def cmd_gloss_langs(args):
    """Emit JSON list of gloss_lang spans for one key1 (durable metadata API)."""
    import json
    if not args:
        print('usage: pwg_mask.py gloss-langs <key1>', file=sys.stderr)
        sys.exit(2)
    target = args[0]
    for buf in records():
        key1, key2, body = parse(buf)
        if key1 == target:
            payload = {
                'key1': key1,
                'key2': key2,
                'gloss_lang_spans': gloss_lang_spans(body),
            }
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return
    print('not found:', target, file=sys.stderr)
    sys.exit(1)


def _selftest():
    """Fixture selftest for G1 gloss_lang (also pinned in window_selftest)."""
    fails = []

    def check(cond, msg):
        if not cond:
            fails.append(msg)

    # DE
    d = classify_pct_detail('das Nichthandeln', '')
    check(d['gloss_lang'] == 'de' and d['translate'], 'DE default: %r' % d)
    d = classify_pct_detail('Gabe, Geschenk', '')
    check(d['gloss_lang'] == 'de', 'DE synonyms: %r' % d)
    d = classify_pct_detail('In der Regel', '')
    check(d['gloss_lang'] == 'de', 'C8 German homograph: %r' % d)

    # LA — cue / phrase / binomial
    d = classify_pct_detail('ignis', 'das lat. ')
    check(d['gloss_lang'] == 'la' and d['rule_id'] == RULE_LATIN_CUE, 'LA cue: %r' % d)
    d = classify_pct_detail('De accentu comp.', '')
    check(d['gloss_lang'] == 'la' and d['rule_id'] == RULE_LATIN_PHRASE, 'LA phrase: %r' % d)
    d = classify_pct_detail('Trapa bispinosa', '')
    check(d['gloss_lang'] == 'la' and d['rule_id'] == RULE_BOTANY_BINOMIAL,
          'LA binomial: %r' % d)
    # German Capitalized+lowercase must NOT be binomial
    d = classify_pct_detail('Name eines Baumes', '')
    check(d['gloss_lang'] == 'de', 'false binomial: %r' % d)

    # EN — Wilson / content
    d = classify_pct_detail(
        'leaving, abandoning',
        'WILS. übersetzt tyAga durch ')
    check(d['gloss_lang'] == 'en' and d['rule_id'] == RULE_WILSON_EN, 'EN Wilson: %r' % d)
    d = classify_pct_detail('terrestrial latitude', '', ', WILS.')
    check(d['gloss_lang'] == 'en', 'EN following WILS: %r' % d)
    # Wilson + German content stays DE (WILS übersetzt … durch {%Honig%})
    d = classify_pct_detail('Honig', 'WILS. übersetzt durch ')
    check(d['gloss_lang'] == 'de', 'Wilson+German stays DE: %r' % d)
    # §464 FP class: lone weak markers / German "war" must not take english_content
    d = classify_pct_detail('war', '')
    check(d['gloss_lang'] == 'de' and d['translate'], 'German war not EN: %r' % d)
    d = classify_pct_detail('and', '')
    check(d['gloss_lang'] == 'de' and d['translate'], 'lone weak and not EN: %r' % d)
    d = classify_pct_detail('an', '')
    check(d['rule_id'] != RULE_ENGLISH_CONTENT,
          'bare an not english_content: %r' % d)
    # true English without cue still works via strong markers
    d = classify_pct_detail('terrestrial latitude', '')
    check(d['gloss_lang'] == 'en' and d['rule_id'] == RULE_ENGLISH_CONTENT,
          'uncued strong EN: %r' % d)

    # gloss_lang_spans offsets + raw-body cues inside tags
    body = ('Feuer <ab>lat.</ab> {%ignis%} und {%Trapa bispinosa%} '
            '(<ls>WILS.</ls> übersetzt durch {%leaving, abandoning%}) '
            'sowie {%Gabe, Geschenk%}.')
    spans = gloss_lang_spans(body)
    by_span = {s['span']: s for s in spans}
    check(by_span['ignis']['gloss_lang'] == 'la', 'spans ignis: %r' % by_span.get('ignis'))
    check(by_span['Trapa bispinosa']['gloss_lang'] == 'la',
          'spans binomial: %r' % by_span.get('Trapa bispinosa'))
    check(by_span['leaving, abandoning']['gloss_lang'] == 'en',
          'spans EN: %r' % by_span.get('leaving, abandoning'))
    check(by_span['Gabe, Geschenk']['gloss_lang'] == 'de',
          'spans DE: %r' % by_span.get('Gabe, Geschenk'))
    for s in spans:
        chunk = body[s['start']:s['end']]
        check(chunk.startswith('{%') and chunk.endswith('%}')
              and s['span'] in chunk,
              'offset mismatch for %r got %r' % (s['span'], chunk))

    # mask: LA + EN placeholder; DE inline; round-trip lossless
    sk, ph, st = mask(body)
    check(st.get('pct_la', 0) >= 2, 'mask pct_la: %r' % st)
    check(st.get('pct_en', 0) >= 1, 'mask pct_en: %r' % st)
    check(st.get('pct_de', 0) >= 1, 'mask pct_de: %r' % st)
    check('{%ignis%}' not in sk, 'ignis leaked: %r' % sk)
    check('{%leaving, abandoning%}' not in sk, 'EN leaked: %r' % sk)
    check('{%Gabe, Geschenk%}' in sk, 'DE not inline: %r' % sk)
    check(restore(sk, ph) == body, 'round-trip failed')

    if fails:
        for f in fails:
            print('FAIL:', f, file=sys.stderr)
        sys.exit(1)
    print('pwg_mask --selftest: %d checks OK' % 20)


def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    if sys.argv[1] in ('--selftest', 'selftest'):
        _selftest()
        return
    {
        'stats': cmd_stats,
        'sample': cmd_sample,
        'card': cmd_card,
        'gloss-langs': cmd_gloss_langs,
    }.get(sys.argv[1], lambda *_: print(__doc__))(sys.argv[2:])


if __name__ == '__main__':
    main()
