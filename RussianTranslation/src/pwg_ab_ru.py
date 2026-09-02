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

RULING (MG, 02-09-2026, registry-contradictions vote sheet): "It's mixed. Some
remain Latin, none remain German, most German become Russian and do not become
Latin." That approves the two-bucket policy above and adds ONE constraint it never
asserted: *none remain German*. The 10-07 fallback-to-the-original-token behaviour
was therefore a defect for Bucket A -- roughly 5 % of <ab> occurrences rendered raw
German in the Russian column by design. H3959 closed it: BUCKET_B below is the
explicit stay-Latin set, RU_MAP now covers every Bucket-A token, and RESIDUE names
the handful with no defensible Russian form (no pwgab entry, or a pwgab entry that
is itself ambiguous/garbled). `census` proves the A-unmapped set is empty.

Direction matters: a Bucket-A German token goes to RUSSIAN, never to Latin. The
H2849 sweep's German->Latin direction (Akk->Acc., Lok->Loc.) is right for Bucket B
and forbidden for Bucket A.

Full methodology, the census table, and the store-residue verdict:
RussianTranslation/ABBREVIATIONS_RU.md.

  python pwg_ab_ru.py lookup <token>
  python pwg_ab_ru.py coverage           # how much of the ru-field <ab> volume this maps
  python pwg_ab_ru.py census             # the four-bucket census; A-unmapped must be 0
"""
import os, re, sys, json, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pwg_ab  # noqa: E402

# The store is git-ignored local data, so a worktree checkout does not carry it;
# PWG_RU_STORE lets census/coverage run from a worktree against the main clone.
STORE = os.environ.get('PWG_RU_STORE') or os.path.join(HERE, 'pwg_ru_translated.jsonl')
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

    # ------------------------------------------------------------------
    # H3959 (02-09-2026) — the "none remain German" closure. Every token
    # below was Bucket A and previously fell back to its raw German form in
    # the RU column. Russian only; not one of them is routed to Latin.
    # ------------------------------------------------------------------
    # deictic cross-reference: pwgab expands 'u.' as "unter" (not "und"), the
    # German preposition of the "see under <headword>" formula:
    'u.': 'под',
    # textual criticism: 'v. l.' is Latin, but it is EDITORIAL, not a
    # grammatical category, so "some remain Latin" (= Bucket B) does not cover
    # it; Russian textology has its own established siglum:
    'v. l.': 'разночт.',
    # register / diasystem label — same class as the buddh./astr./liturg.
    # domain labels above, which already translate:
    'ved.': 'вед.',
    # plain German adverb qualifying a construction ("dopp. Acc."), not a siglum:
    'dopp.': 'двойн.',
    # citation mechanics (joins Z./Ausg./Hdschr. above)
    'p.': 'с.', 'ed.': 'изд.', 'Aufl.': 'изд.', 'lith.': 'литогр.',
    'Rec.': 'редакция', 'Anm.': 'прим.', 'St.': 'место', 'd. St.': 'место',
    # case variants of entries already mapped above (insbes./Gramm.):
    'Insbes.': 'особ.', 'gramm.': 'грамм.',
    # plain German prose adverbs and pronouns leaking into a Russian sentence:
    'urspr.': 'первонач.', 'desgl.': 'так же', 'dgl.': 'так же',
    'Jmd.': 'кто-л.', 'vom.': 'от',
    # German-formed grammar PROPERTIES (not international Latin category
    # sigla, so Bucket B does not cover them — 'unregelmäßig' is a German
    # adjective, whereas 'Acc.'/'caus.' are the Latin termini technici):
    'unregelm.': 'неправ.', 'ungramm.': 'неграмм.', 'Ortsadv.': 'нареч. места',
    # usage / register labels, same class as Bein./N. pr. above:
    'euphem.': 'эвфем.', 'myst.': 'мист.', 'metr.': 'метр.',
    'etymol.': 'этимол.', 'Patron.': 'патроним.',
}

# Bucket B — grammatical-category sigla that STAY international Latin in the RU
# column (MG 10-07-2026, re-affirmed 02-09-2026 as "some remain Latin"). Listed
# explicitly, not inferred, so `census` can prove that nothing has silently
# fallen out of both buckets. Case/number/gender, tense/mood/voice/aspect,
# part-of-speech, compound and derivation types, and their Latin plurals.
BUCKET_B = frozenset([
    # case, number, gender (+ the Latin plurals PWG prints for lists of forms)
    'Acc.', 'acc.', 'Abl.', 'abl.', 'Dat.', 'dat.', 'Gen.', 'gen.',
    'Instr.', 'instr.', 'Loc.', 'loc.', 'Nom.', 'nom.', 'Nomin.', 'nomin.',
    'Voc.', 'voc.', 'locc.', 'datt.', 'nomm.', 'pronomm.',
    'Sg.', 'sg.', 'sing.', 'Pl.', 'pl.', 'Du.', 'du.', 'masc.', 'neutr.',
    # voice, causation, tense, mood, non-finite forms
    'Act.', 'act.', 'Med.', 'Pass.', 'pass.',
    'Caus.', 'caus.', 'Desid.', 'desid.', 'desider.', 'Intens.', 'intens.',
    'Aor.', 'aor.', 'Perf.', 'perf.', 'Imperf.', 'imperf.',
    'Praes.', 'praes.', 'Präs.', 'Praet.', 'praet.', 'Fut.', 'fut.',
    'Conj.', 'conj.', 'Imper.', 'imper.', 'Imperat.', 'imperat.',
    'Indic.', 'indic.', 'Opt.', 'Potent.', 'pot.', 'potent.',
    'Prec.', 'prec.', 'precat.', 'Absol.', 'absol.', 'absolut.',
    'Infin.', 'infin.', 'infinit.', 'Inf.', 'inf.',
    'Partic.', 'partic.', 'part.', 'gerund.', 'Augm.', 'Redupl.', 'Declin.',
    # part of speech, valency, syntactic role
    'Subst.', 'subst.', 'Verb.', 'Interj.', 'Praep.', 'praep.', 'praepp.',
    'indecl.', 'fin.', 'Obj.', 'obj.', 'subj.', 'praed.',
    'Trans.', 'trans.', 'transit.', 'tr.',
    'Intrans.', 'intrans.', 'intransit.', 'intr.',
    'instrans.',                                          # PWG's own typo for intransitiv
    'Impers.', 'impers.',
    # compound / derivation types and degrees
    'Comp.', 'comp.', 'Compp.', 'compp.', 'compon.', 'Simpl.', 'simpl.',
    'adj. Comp.', 'adj. comp.', 'adv. Comp.',
    'Nom. abstr.', 'nom. abstr.', 'Nom. ag.', 'nom. ag.', 'nom. act.',
    'Superl.', 'superl.', 'Compar.', 'compar.',
    'oxyt.', 'partit.', 'dem.', 'priv.', 'recipr.', 'denom.', 'defect.',
    'neg.', 'suff.',
])

# Declared residue — tokens with NO defensible Russian form. Two admissible
# reasons only, per H3959's ambiguity policy: the token has no entry in PWG's
# own pwgab table at all (source-side noise, local sigla, proper-name
# initials), or its pwgab entry is itself ambiguous or flagged garbled. A
# declared undecided token costs one row here; a guessed Russian gloss for a
# garbled token would put invented Russian into a dictionary.
RESIDUE = {
    'e.': 'no pwgab entry',
    'H.': 'no pwgab entry',
    'M.': 'no pwgab entry',
    'Fr.': 'no pwgab entry',
    'o.': 'no pwgab entry (probably "oben", but PWG never declares it)',
    'o. W.': 'no pwgab entry',
    'r. V.': 'no pwgab entry',
    'd. r. V.': 'no pwgab entry',
    'schl.': 'no pwgab entry',
    '3.': 'no pwgab entry — numeric markup artifact',
    'geder.': 'pwgab itself reads "gedeutet?" — garbled source',
    'd.': 'pwgab reads "der / die / das" — ambiguous definite article',
    'pers.': 'pwgab reads "Person / persisch" — grammatical vs domain, undecidable',
    'ind.': 'pwgab reads "indisch / Indikativ" — domain vs grammatical, undecidable',
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


def bucket(tok):
    """Which of the four H3959 buckets a token falls in.
    'A-mapped'   — editorial/domain/deictic, renders Russian from RU_MAP
    'B'          — grammatical category, deliberately stays international Latin
    'residue'    — declared undecided (see RESIDUE for the per-token reason)
    'A-unmapped' — the defect MG's 02-09-2026 ruling outlaws: renders raw German"""
    if tok in RU_MAP:
        return 'A-mapped'
    if tok in BUCKET_B:
        return 'B'
    if tok in RESIDUE:
        return 'residue'
    return 'A-unmapped'


def _ru_ab_freq():
    freq = collections.Counter()
    with open(STORE, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            for tok in _AB.findall(json.loads(line).get('ru') or ''):
                freq[re.sub(r'\s+', ' ', tok.strip())] += 1
    return freq


def cmd_census(_args):
    """The H3959 four-bucket census. Exit 1 if any A-unmapped token survives."""
    freq = _ru_ab_freq()
    total, distinct = sum(freq.values()), len(freq)
    by = collections.defaultdict(collections.Counter)
    for tok, c in freq.items():
        by[bucket(tok)][tok] = c
    print('<ab> reaching the RU column: %d occurrences, %d distinct tokens'
          % (total, distinct))
    print('%-12s %10s %8s %10s %8s' % ('bucket', 'occurr.', '%', 'distinct', '%'))
    for name in ('B', 'A-mapped', 'residue', 'A-unmapped'):
        occ, dis = sum(by[name].values()), len(by[name])
        print('%-12s %10d %7.1f%% %10d %7.1f%%'
              % (name, occ, 100.0 * occ / total, dis, 100.0 * dis / distinct))
    print('\ndeclared residue (no defensible Russian form):')
    for tok, c in by['residue'].most_common():
        print('  %-12r %3d  %s' % (tok, c, RESIDUE[tok]))
    # MG's direction constraint: a Bucket-A token becomes RUSSIAN, never Latin.
    latin = sorted(k for k, v in RU_MAP.items() if not re.search(r'[А-Яа-яЁё]', v))
    if latin:
        print('\nFAIL — %d Bucket-A token(s) map to a non-Cyrillic form: %s'
              % (len(latin), ', '.join(repr(k) for k in latin)))
        return 1
    print('\nall %d RU_MAP values are Cyrillic — no Bucket-A token routed to Latin.'
          % len(RU_MAP))

    bad = by['A-unmapped']
    if bad:
        print('\nFAIL — %d token(s) still render raw German in the RU column:' % len(bad))
        for tok, c in bad.most_common():
            r = pwg_ab.resolve(tok)
            print('  %-14r %5d  %s' % (tok, c, r and r['de']))
        return 1
    print('\nPASS — zero A-unmapped tokens: nothing renders untranslated German.')
    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 0
    return {'lookup': cmd_lookup, 'coverage': cmd_coverage, 'census': cmd_census}.get(
        sys.argv[1], lambda *_: print(__doc__))(sys.argv[2:]) or 0


if __name__ == '__main__':
    sys.exit(main())
