#!/usr/bin/env python
r"""PWG <ab> abbreviation -> RUSSIAN display text, for the article-site RU rendering.

pwg_ab.py resolves every <ab> token to its authoritative German/English expansion
(from PWG's own pwgab table) but the *article site* (build_article_site.py) was
showing that raw German/Latin token verbatim in ALL three language columns (DE/RU/EN)
-- so the Russian column read things like "mena см. s. u. menā." (German "s. u."
left inside a Russian sentence) or "Bein. Vṛṣaṇaśvaа" (German "Bein." = Beiname).
MG flagged this 10-07-2026: German abbreviations must not survive into the RU text;
some Latin ones are "justified" and may stay.

DECISION (MG, 10-07-2026, via AskUserQuestion): grammatical-CATEGORY abbreviations
(case/mood/voice/tense/aspect/part-of-speech: Acc., Loc., caus., pass., aor., sg.,
masc., partic., subst. ...) are KEPT as international Latin siglum in the RU column
too -- this matches both Cologne's own site and worldwide Indological convention.
Only a hover tooltip (wired in build_article_site.py, not here) is added for those.

This module covers the OTHER bucket: purely editorial / cross-reference / deictic /
domain-label abbreviations, which have no comparable international-scholarly-Latin
status and read as plain leaked German (or German-flavoured Latin function words)
in a Russian sentence -- "s. u." is simply the German word "siehe" abbreviated, not
a term of art. These get a Russian equivalent as their VISIBLE text in the RU
column; the tooltip still shows the original German/English so the reader can spot
the source form. Anything NOT in RU_MAP silently falls back to the original DE
token (tooltip-only improvement) -- so an unclassified/rare token never gets WORSE,
it just doesn't (yet) get translated.

**This is a curated first pass, not an exhaustive audit.** It covers the ~50
highest-frequency editorial tokens (measured over pwg_ru_translated.jsonl,
2026-07-10: 265 distinct <ab> tokens / 12,152 occurrences total). A few entries are
judgment calls flagged inline; see RussianTranslation/ABBREVIATIONS_RU.md for the
full methodology, the complete frequency table, and the residual/open items.

  python pwg_ab_ru.py lookup <token>
  python pwg_ab_ru.py coverage           # how much of the ru-field <ab> volume this maps
"""
import os, re, sys, json, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pwg_ab  # noqa: E402

STORE = os.path.join(HERE, 'pwg_ru_translated.jsonl')
_AB = re.compile(r'<ab\b[^>]*>(.*?)</ab>', re.S)

# DE/Latin editorial token -> Russian display text. Keys are matched after
# whitespace-normalization + rstrip('.') is NOT applied (periods are kept, they
# are part of the printed abbreviation), so keys must match the token verbatim
# as it appears inside <ab>...</ab> (see pwg_ab.norm — collapses internal runs
# of whitespace only).
RU_MAP = {
    # cross-reference / deictic ("see" / "cf." family) -- collapse German+Latin
    # variants to the single Russian convention, since these are function words,
    # not termini technici (the strongest case for translating regardless of
    # whether the source token happens to be German "siehe" or Latin "sub verbo"):
    's.': 'см.', 'S.': 'см.', 's. u.': 'см.', 's. d.': 'см.', 's. v.': 'см.',
    's. u. d.': 'см.',
    # highest-frequency token overall (989 occurrences) — "vor allem" is a plain
    # emphasis adverb, not a grammatical siglum:
    'v. a.': 'преим.',
    'Vgl.': 'ср.', 'vgl.': 'ср.', 'Vergl.': 'ср.',
    'sc.': 'а именно', 'd. i.': 'т.е.', 'd. h.': 'т.е.',

    # etc. / e.g. / examples
    'u. s. w.': 'и т.д.', 'z. B.': 'напр.',

    # meaning / designation
    'Bed.': 'знач.', 'Bedd.': 'знач.', 'Bez.': 'обозн.',
    'übertr.': 'перен.', 'uneig.': 'неточно', 'Uneig.': 'неточно', 'eig.': 'букв.',

    # "the same" / "ibid." family
    'dass.': 'то же', 'ders.': 'тот же', 'des.': 'того же', 'ebend.': 'там же',
    'D.': 'там же',

    # citation mechanics (line/page/edition/manuscript pointers)
    'Z.': 'стк.', 'v. u.': 'снизу', 'a. a. O.': 'указ. соч.',
    'Ausg.': 'изд.', 'Ausgg.': 'изд.', 'Calc. Ausg.': 'калькутт. изд.',
    'Hdschr.': 'рукоп.', 'Hdschrr.': 'рукоп.', 'Inschr.': 'надпись',
    'Cit.': 'цит.', 'gedr.': 'печ.', 'ungedr.': 'неизд.',
    'Anf.': 'начало', 'Einl.': 'введ.', 'Erkl.': 'пояснение', 'Erkll.': 'пояснения',
    'Th.': 'ч.', 'Aut.': 'авт.', 'Gramm.': 'грамм.',
    # 'Sch.'/'Schol.'/'Scholl.' (Scholion/Scholiast) -- a Greco-Latin loanword
    # that Russian classical philology already renders natively (схолия/схолиаст),
    # unlike a plain German word, so this is translated for the same reason as
    # the "see"/"cf." family: it has a native, equally short, Russian form.
    'Sch.': 'схол.', 'Schol.': 'схол.', 'Scholl.': 'схол.', 'Comm.': 'коммент.',

    # sequence / degree
    'fgg.': 'сл.', 'fg.': 'сл.', 'folg.': 'сл.',
    'st.': 'вместо', 'best.': 'определ.', 'bes.': 'особ.', 'insbes.': 'особ.',
    'überh.': 'вообще', 'viell.': 'возможно', 'Viell.': 'возможно',
    'Gegens.': 'противоп.', 'gew.': 'обычно',
    'vorangeh.': 'предш.', 'vorang.': 'предш.', 'näml.': 'а именно',

    # usage/type labels (MG's own examples: Bein./N. pr.) -- lexicographic
    # classification, not inflectional grammar, so they translate like any
    # other prose label rather than staying an international Latin siglum:
    'Bein.': 'эпит.', 'Beiw.': 'эпит.', 'Beiww.': 'эпит.',
    'N. pr.': 'имя собств.', 'N.': 'имя',

    # word/text-level pointers (careful: kept distinct from fgg./fg. "сл." to
    # avoid a Russian-side collision; spelled out since low-frequency)
    'w.': 'слово', 'W.': 'слово', 'd. W.': 'слово',

    # subject-domain labels (semantic-field tags, not grammar -- translate like
    # any encyclopedic register label):
    'buddh.': 'будд.', 'astrol.': 'астрол.', 'Astrol.': 'астрол.',
    'astr.': 'астр.', 'Astr.': 'астр.', 'liturg.': 'литург.',
    'techn.': 'техн.', 'philos.': 'филос.', 'Philos.': 'филос.', 'Rhet.': 'рит.',
    # 'med.'/'medic.' resolve in pwgab as "Medizin/medicine" (domain label), NOT
    # the grammatical "medium voice" -- translated on that basis; flagged as a
    # residual risk in ABBREVIATIONS_RU.md if a genuine medium-voice usage of
    # the bare token 'med.' turns out to share the same string.
    'med.': 'мед.', 'medic.': 'мед.',

    'Wörterb.': 'словарь', 'Unterschr.': 'подпись', 'Verbind.': 'связь',
    'Einschieb.': 'вставка', 'Uebers.': 'пер.', 'bildl.': 'перен.',
    'diess.': 'это', 'mannigf.': 'разнообр.', 'nam.': 'особ.', 'einf.': 'просто',
}


def display(token):
    """(visible, title) for one <ab> token when rendering the RU column.
    visible = RU_MAP hit, else the original token unchanged.
    title   = the authoritative DE/EN expansion (pwg_ab), for the hover tooltip."""
    tok = token.strip()
    r = pwg_ab.resolve(tok)
    title = ('%s — %s' % (r['de'], r['en'])) if r else None
    return RU_MAP.get(tok, tok), title


def cmd_lookup(args):
    vis, title = display(args[0])
    print('%s -> %r  (title: %s)' % (args[0], vis, title))


def cmd_coverage(_args):
    freq = collections.Counter()
    with open(STORE, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            for tok in _AB.findall(r.get('ru') or ''):
                freq[tok.strip()] += 1
    total = sum(freq.values())
    mapped = sum(c for k, c in freq.items() if k in RU_MAP)
    print('RU_MAP entries: %d' % len(RU_MAP))
    print('<ab> in ru field: %d occurrences, %d distinct' % (total, len(freq)))
    print('translated to Russian: %d/%d occurrences (%.1f%%), %d/%d distinct (%.1f%%)'
          % (mapped, total, 100.0 * mapped / total,
             sum(1 for k in freq if k in RU_MAP), len(freq),
             100.0 * sum(1 for k in freq if k in RU_MAP) / len(freq)))
    print('kept as Latin/untranslated (still get a tooltip), top 20 by freq:')
    for k, c in [(k, c) for k, c in freq.most_common() if k not in RU_MAP][:20]:
        r = pwg_ab.resolve(k)
        print('  %-14r %5d  %s' % (k, c, r and r['en']))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    {'lookup': cmd_lookup, 'coverage': cmd_coverage}.get(
        sys.argv[1], lambda *_: print(__doc__))(sys.argv[2:])


if __name__ == '__main__':
    main()
