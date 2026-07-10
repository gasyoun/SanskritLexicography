#!/usr/bin/env python
r"""IAST -> practical Russian Cyrillic transliteration, for proper names embedded
in RU-column running prose (the <is>...</is> spans in pwg_ru — e.g. "Vṛṣaṇaśva",
"Himavant" left untransliterated inside translated Russian sentences: MG flagged
10-07-2026 that a name should read "записать кириллицей", not stay in IAST, when
it appears inline in a Russian sentence with a Russian case-ending glued onto it).

This is DELIBERATELY SCOPED to <is> proper-name spans only — the {#...#} SLP1
lexical-form spans (headwords, cited word-forms) stay italic-IAST in ALL THREE
languages by existing project convention (mirrors the mw_ru rule: Sanskrit forms
are deliberately left untouched, see the org CLAUDE.md) and this module must NOT
be applied there.

No prior-art hit: SHARED_CODE.md's translit family (sanskrit-util `iast_to_devanagari`,
`slug.py` Cyrillic->Latin BGN/PCGN) has nothing in the IAST->Cyrillic direction —
`iast_to_devanagari` is IAST->Devanagari and is itself flagged broken (see
[[reference_iast_normalization_pitfalls]] / SHARED_CODE.md ⚠️). This is a new,
narrow, best-effort utility, not a port of anything existing.

Scheme = the practical/scientific transliteration used in Russian Indology
(Elizarenkova/Kochergina tradition): vowel length + Vedic accents dropped (same
simplification the project already applies for {#...#} -> IAST, see
build_article_site.slp1_iast), ś/ṣ -> ш, c -> ч, j -> дж, y -> й, v -> в,
anusvara -> м, visarga -> х. This is a FIRST PASS, not a validated authoritative
scheme — known weak spots (documented, not silently hidden):
  * y/v + vowel semivowel-glide coalescence (e.g. word-initial "Ya-" vs "-ya-")
    is not modeled; both render via the plain consonant map.
  * visarga word-finally is often dropped in idiomatic Russian transliteration
    of proper names (Śiva -> Шива, not Шивах्); this module keeps it as "х" and
    the *caller* (build_article_site.py) strips a trailing "х" produced from a
    final visarga before a Russian case-ending is glued on — see _cyr_name().
  * capitalization: only the first letter of the whole (multi-word) name is
    capitalized; internal words are not re-capitalized.
See RussianTranslation/ABBREVIATIONS_RU.md for the residual QA/spot-check plan.

  python iast_to_cyrillic.py <IAST name>
"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Longest-match-first digraphs/trigraphs (aspirated stops, common clusters).
_MULTI = [
    ('kṣ', 'кш'), ('jñ', 'джн'),
    ('kh', 'кх'), ('gh', 'гх'), ('ch', 'чх'), ('jh', 'джх'),
    ('ṭh', 'тх'), ('ḍh', 'дх'), ('th', 'тх'), ('dh', 'дх'), ('ph', 'пх'), ('bh', 'бх'),
    ('ai', 'ай'), ('au', 'ау'),
]

_SINGLE = {
    'ā': 'а', 'ī': 'и', 'ū': 'у',
    'ṛ': 'ри', 'ṝ': 'ри', 'ḷ': 'ли', 'ḹ': 'ли',
    'a': 'а', 'i': 'и', 'u': 'у', 'e': 'е', 'o': 'о',
    'ṃ': 'м', 'ṁ': 'м', 'ḥ': 'х',
    'k': 'к', 'g': 'г', 'ṅ': 'н',
    'c': 'ч', 'j': 'дж', 'ñ': 'нь',
    'ṭ': 'т', 'ḍ': 'д', 'ṇ': 'н',
    't': 'т', 'd': 'д', 'n': 'н',
    'p': 'п', 'b': 'б', 'm': 'м',
    'y': 'й', 'r': 'р', 'l': 'л', 'v': 'в',
    'ś': 'ш', 'ṣ': 'ш', 's': 'с', 'h': 'х',
    "'": '',  # avagraha
}

_TOKEN_RE = re.compile(r'[A-Za-zĀĪŪṚṜḶḸṄÑṬḌṆŚṢḤṂṀāīūṛṝḷḹṅñṭḍṇśṣḥṃṁ\'-]+')


def transliterate(iast):
    """IAST word/phrase -> best-effort Cyrillic. Non-Sanskrit chars pass through
    unchanged (punctuation, spaces, digits)."""
    def _word(w):
        low = w.lower()
        out, i = [], 0
        while i < len(low):
            for pat, rep in _MULTI:
                if low.startswith(pat, i):
                    out.append(rep)
                    i += len(pat)
                    break
            else:
                out.append(_SINGLE.get(low[i], low[i]))
                i += 1
        cyr = ''.join(out)
        return cyr[:1].upper() + cyr[1:] if w[:1].isupper() and cyr else cyr

    return _TOKEN_RE.sub(lambda m: _word(m.group(0)), iast)


def name_for_ru_prose(iast):
    """Transliterate a proper name for inline use in a Russian sentence where a
    Russian case-ending typically follows immediately (as pwg_ru's translated
    `ru` field already does, e.g. "<is>Vṛṣaṇaśva</is>а" = stem + genitive "-а").
    Strips a bare final "х" (from a word-final visarga) so it doesn't collide
    with the appended Russian ending — matches idiomatic Russian transliteration
    practice (Śivaḥ -> Шива-, not Шивах-, before inflection)."""
    cyr = transliterate(iast)
    if cyr.endswith('х') and not cyr.endswith('кх') and not cyr.endswith('гх'):
        cyr = cyr[:-1]
    return cyr


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    name = ' '.join(sys.argv[1:])
    print('%s -> %s  (prose form: %s)' % (name, transliterate(name), name_for_ru_prose(name)))


if __name__ == '__main__':
    main()
