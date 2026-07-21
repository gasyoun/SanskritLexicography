#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""build_h1303_abbrev_sheet.py — regen the H1303 abbreviation-ratification sheet.

The committed regenerator for `review/h1303_abbrev_sheet.html` (sheet_id
`h1303_abbrev`, local-only/gitignored — embeds nothing from the store beyond
`<ab>` token frequencies, but stays local like every voting sheet). One card per
distinct `<ab>` token in the store's RU fields + 3 `<ls>`-border sigla + 1
render-time-vs-store meta-card. The frozen human-readable table of the same
proposals is `pwg_ru/ABBREV_UNIFIED_LIST_PROPOSAL_2026-07.md` (committed
21-07-2026; this script does NOT rewrite it — the table is the record of what
was proposed, the sheet is the voting surface).

Usage (from RussianTranslation/):
    python src/build_h1303_abbrev_sheet.py

Store access via store_path.canonical_store() (H805 rule); emitter:
csl_pyutil.review_sheet (>=0.3.0, the H1301 standard). Judgment overlay
(bucket + proposed RU + origin class per token) authored by Fable 5
(`claude-fable-5`) under H1303 Session 1, 21-07-2026 — sourced from the
19-07-2026 DA-vote constraints (rows N3a/N4/N5/N8).

Tokens that have appeared in the store SINCE the overlay was authored fall
into a loud `NEW-TOKEN` bucket (defer-proposal, note asks for re-triage)
instead of crashing — the ratified list covers the 269 known tokens; new ones
need their own proposal pass.
"""
import os
import sys
import re
import json
import collections
import argparse

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(HERE)                      # RussianTranslation/
sys.path.insert(0, HERE)
import store_path                               # noqa: E402
import pwg_ab                                   # noqa: E402
from pwg_ab_ru import RU_MAP                    # noqa: E402
from csl_pyutil.review_sheet import render_review_sheet, esc, mark_cyrillic  # noqa: E402

GENERATED = '2026-07-21'
_AB = re.compile(r'<ab\b[^>]*>(.*?)</ab>', re.S)


def inventory():
    """Distinct <ab> tokens in the store's RU fields with frequency + pwgab data."""
    store = store_path.canonical_store(os.path.join(HERE, 'pwg_ru_translated.jsonl'))
    freq = collections.Counter()
    rows = 0
    with open(store, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            rows += 1
            for tok in _AB.findall(r.get('ru') or ''):
                freq[tok.strip()] += 1
    out = []
    for tok, c in freq.most_common():
        r = pwg_ab.resolve(tok)
        out.append({'token': tok, 'freq': c,
                    'de': r['de'] if r else None, 'en': r['en'] if r else None,
                    'in_pwgab': bool(r), 'ru_map': RU_MAP.get(tok)})
    print('store: %s — %d rows, %d occurrences, %d distinct'
          % (store, rows, sum(freq.values()), len(freq)), file=sys.stderr)
    return out


# ---------------------------------------------------------------- overlay
# b: 'a' grammatical | 'b' editorial/cross-ref/deictic | 'c' source/citation
# cls: 'нем' German word | 'лат' Latin/international siglum | 'конт' contextual
#      German (n=-attribute carries the expansion) | 'OCR' noise/unclear
# ru: proposed Russian rendering (None => defer-proposal, see note)
O = {
 # --- cross-reference / deictic (RU_MAP ratifications + additions)
 's.':    dict(b='b', cls='нем', ru='см.'), 'S.': dict(b='b', cls='нем', ru='см.'),
 's. u.': dict(b='b', cls='нем', ru='см.'), 's. d.': dict(b='b', cls='нем', ru='см.'),
 's. v.': dict(b='b', cls='лат', ru='см.'), 's. u. d.': dict(b='b', cls='нем', ru='см.'),
 'u.':    dict(b='b', cls='нем', ru='под', note='«s. … u. X» = «см. под X»; ср. контексты «Vgl. также u. upa»'),
 'v. a.': dict(b='b', cls='нем', ru='преим.'),
 'Vgl.':  dict(b='b', cls='нем', ru='ср.'), 'vgl.': dict(b='b', cls='нем', ru='ср.'),
 'Vergl.': dict(b='b', cls='нем', ru='ср.'),
 'sc.':   dict(b='b', cls='лат', ru='а именно'),
 'd. i.': dict(b='b', cls='нем', ru='т.е.'), 'd. h.': dict(b='b', cls='нем', ru='т.е.'),
 'näml.': dict(b='b', cls='нем', ru='а именно'),
 'u. s. w.': dict(b='b', cls='нем', ru='и т.д.'), 'z. B.': dict(b='b', cls='нем', ru='напр.'),
 # --- meaning / designation / usage labels
 'Bed.':  dict(b='b', cls='нем', ru='знач.'), 'Bedd.': dict(b='b', cls='нем', ru='знач.'),
 'Bez.':  dict(b='b', cls='нем', ru='обозн.'),
 'übertr.': dict(b='b', cls='нем', ru='перен.'), 'bildl.': dict(b='b', cls='нем', ru='перен.'),
 'uneig.': dict(b='b', cls='нем', ru='неточно'), 'Uneig.': dict(b='b', cls='нем', ru='неточно'),
 'eig.':  dict(b='b', cls='нем', ru='букв.'),
 'euphem.': dict(b='b', cls='лат', ru='эвфем.'),
 'dass.': dict(b='b', cls='нем', ru='то же'), 'ders.': dict(b='b', cls='нем', ru='тот же'),
 'des.':  dict(b='b', cls='нем', ru='того же'), 'ebend.': dict(b='b', cls='нем', ru='там же',
      note='H1323: на hUNgarAI стоит дважды подряд — вопрос к источнику (Cologne), не к списку'),
 'D.':    dict(b='b', cls='нем', ru='там же'),
 'desgl.': dict(b='b', cls='нем', ru='то же', note='H1323 (ISvare)'),
 'dgl.':  dict(b='b', cls='нем', ru='то же'),
 'diess.': dict(b='b', cls='нем', ru='это'), 'Jmd.': dict(b='b', cls='нем', ru='кто-л.'),
 'viell.': dict(b='b', cls='нем', ru='возможно'), 'Viell.': dict(b='b', cls='нем', ru='возможно'),
 'best.': dict(b='b', cls='нем', ru='определ.'), 'bes.': dict(b='b', cls='нем', ru='особ.'),
 'insbes.': dict(b='b', cls='нем', ru='особ.'), 'Insbes.': dict(b='b', cls='нем', ru='особ.'),
 'nam.':  dict(b='b', cls='нем', ru='особ.'), 'überh.': dict(b='b', cls='нем', ru='вообще'),
 'Gegens.': dict(b='b', cls='нем', ru='противоп.'), 'gew.': dict(b='b', cls='нем', ru='обычно'),
 'vorangeh.': dict(b='b', cls='нем', ru='предш.'), 'vorang.': dict(b='b', cls='нем', ru='предш.'),
 'fgg.':  dict(b='b', cls='нем', ru='сл.'), 'fg.': dict(b='b', cls='нем', ru='сл.'),
 'folg.': dict(b='b', cls='нем', ru='сл.'),
 'st.':   dict(b='b', cls='нем', ru='вместо'),
 'mannigf.': dict(b='b', cls='нем', ru='разнообр.'), 'einf.': dict(b='b', cls='нем', ru='просто'),
 'urspr.': dict(b='b', cls='нем', ru='первонач.'),
 'vom.':  dict(b='b', cls='нем', ru='от', note='«desid. vom. caus.» = «дезид. от кауз.»'),
 'Erkl.': dict(b='b', cls='нем', ru='пояснение'), 'Erkll.': dict(b='b', cls='нем', ru='пояснения'),
 'Verbind.': dict(b='b', cls='нем', ru='связь'), 'Einschieb.': dict(b='b', cls='нем', ru='вставка'),
 'Bein.': dict(b='b', cls='нем', ru='эпит.'), 'Beiw.': dict(b='b', cls='нем', ru='эпит.'),
 'Beiww.': dict(b='b', cls='нем', ru='эпит.'),
 'N. pr.': dict(b='b', cls='лат', ru='имя собств.'), 'N.': dict(b='b', cls='нем', ru='имя'),
 'w.':    dict(b='b', cls='конт', ru='слово', note='при n=-атрибуте переводить по нему'),
 'W.':    dict(b='b', cls='конт', ru='слово',
      note='ОСТОРОЖНО: в store встречается n="Wange" (щека) — фиксированное «слово» неверно; переводить по n=-атрибуту'),
 'd. W.': dict(b='b', cls='нем', ru='слово'),
 'geder.': dict(b='b', cls='OCR', ru=None, note='gedeutet? — OCR-шум, вопрос к источнику'),
 # --- domain labels
 'buddh.': dict(b='b', cls='лат', ru='будд.'), 'astrol.': dict(b='b', cls='лат', ru='астрол.'),
 'Astrol.': dict(b='b', cls='лат', ru='астрол.'), 'astr.': dict(b='b', cls='лат', ru='астр.'),
 'Astr.': dict(b='b', cls='лат', ru='астр.'), 'liturg.': dict(b='b', cls='лат', ru='литург.'),
 'techn.': dict(b='b', cls='лат', ru='техн.'), 'philos.': dict(b='b', cls='лат', ru='филос.'),
 'Philos.': dict(b='b', cls='лат', ru='филос.'), 'Rhet.': dict(b='b', cls='лат', ru='рит.'),
 'med.':  dict(b='b', cls='лат', ru='мед.',
      note='строчное med. = Medizin (домен); НЕ путать с Med. = медий (залог), см. отдельную строку'),
 'medic.': dict(b='b', cls='лат', ru='мед.'),
 'metr.': dict(b='b', cls='лат', ru='метр.'),
 # --- contextual German word-abbreviations (n=-attribute class)
 'H.':    dict(b='b', cls='конт', ru=None, note='n="Herrschaft"/"Hand" — переводить по n=-атрибуту, фиксированного соответствия нет'),
 'M.':    dict(b='b', cls='конт', ru=None, note='n="Mann"'),
 'Fr.':   dict(b='b', cls='конт', ru=None, note='n="Fremde"'),
 'o. W.': dict(b='b', cls='конт', ru=None, note='n="ohne Wissen" = «без ведома»'),
 'o.':    dict(b='b', cls='конт', ru=None, note='n="ohne"'),
 'e.':    dict(b='b', cls='конт', ru=None, note='n="einander"/"eingesogen"'),
 'schl.': dict(b='b', cls='конт', ru=None, note='n="schliessen"'),
 'r. V.': dict(b='b', cls='конт', ru=None, note='n="richtige Vorstellung"'),
 'd. r. V.': dict(b='b', cls='конт', ru=None, note='n="der richtigen Verfassung"'),
 'd.':    dict(b='b', cls='конт', ru=None, note='der/die/das перед контекстным сокращением'),
 # --- grammatical: cases (uniform internationalism: 8 cases vs 6 русских)
 'Acc.': dict(b='a', cls='лат', ru='акк.'), 'acc.': dict(b='a', cls='лат', ru='акк.'),
 'Loc.': dict(b='a', cls='лат', ru='лок.'), 'loc.': dict(b='a', cls='лат', ru='лок.'),
 'locc.': dict(b='a', cls='лат', ru='лок.'),
 'Instr.': dict(b='a', cls='лат', ru='инстр.'), 'instr.': dict(b='a', cls='лат', ru='инстр.'),
 'Abl.': dict(b='a', cls='лат', ru='абл.'), 'abl.': dict(b='a', cls='лат', ru='абл.'),
 'Dat.': dict(b='a', cls='лат', ru='дат.'), 'dat.': dict(b='a', cls='лат', ru='дат.'),
 'datt.': dict(b='a', cls='лат', ru='дат.'),
 'Gen.': dict(b='a', cls='лат', ru='ген.'), 'gen.': dict(b='a', cls='лат', ru='ген.'),
 'Nom.': dict(b='a', cls='лат', ru='ном.'), 'nom.': dict(b='a', cls='лат', ru='ном.'),
 'Nomin.': dict(b='a', cls='лат', ru='ном.'), 'nomin.': dict(b='a', cls='лат', ru='ном.'),
 'Voc.': dict(b='a', cls='лат', ru='вок.'), 'voc.': dict(b='a', cls='лат', ru='вок.'),
 # --- grammatical: number / gender / person
 'sg.': dict(b='a', cls='лат', ru='ед.'), 'Sg.': dict(b='a', cls='лат', ru='ед.'),
 'sing.': dict(b='a', cls='лат', ru='ед.'),
 'pl.': dict(b='a', cls='лат', ru='мн.'), 'Pl.': dict(b='a', cls='лат', ru='мн.'),
 'du.': dict(b='a', cls='лат', ru='дв.'), 'Du.': dict(b='a', cls='лат', ru='дв.'),
 'masc.': dict(b='a', cls='лат', ru='м.'), 'neutr.': dict(b='a', cls='лат', ru='ср. р.',
      note='не «ср.» — коллизия со «ср.» = vgl.'),
 'pers.': dict(b='a', cls='лат', ru='л.', note='«2. pers.» = «2-е л.»'),
 '3.':   dict(b='a', cls='OCR', ru=None, note='«3. Sg. Med.» — разметочный артефакт (цифра лица в <ab>), вопрос к источнику'),
 # --- grammatical: voice / secondary stems
 'act.': dict(b='a', cls='лат', ru='акт.'), 'Act.': dict(b='a', cls='лат', ru='акт.'),
 'pass.': dict(b='a', cls='лат', ru='пасс.'), 'Pass.': dict(b='a', cls='лат', ru='пасс.'),
 'Med.': dict(b='a', cls='лат', ru='медий',
      note='медий (атманепада), НЕ «мед.» — коллизия с med. = Medizin; 283 употр., в pwgab отсутствует (регистрозависимая пара)'),
 'caus.': dict(b='a', cls='лат', ru='кауз.'), 'Caus.': dict(b='a', cls='лат', ru='кауз.',
      note='зафиксировано MG 19-07-2026 (N8)'),
 'desid.': dict(b='a', cls='лат', ru='дезид.'), 'Desid.': dict(b='a', cls='лат', ru='дезид.'),
 'desider.': dict(b='a', cls='лат', ru='дезид.'),
 'intens.': dict(b='a', cls='лат', ru='интенс.'), 'Intens.': dict(b='a', cls='лат', ru='интенс.'),
 'denom.': dict(b='a', cls='лат', ru='деном.'),
 'simpl.': dict(b='a', cls='лат', ru='симпл.'), 'Simpl.': dict(b='a', cls='лат', ru='симпл.'),
 'recipr.': dict(b='a', cls='лат', ru='взаимн.'),
 # --- grammatical: tense / mood
 'aor.': dict(b='a', cls='лат', ru='аор.', note='N5: «нельзя не переводить»'),
 'Aor.': dict(b='a', cls='лат', ru='аор.', note='N5: «нельзя не переводить»'),
 'perf.': dict(b='a', cls='лат', ru='перф.'), 'Perf.': dict(b='a', cls='лат', ru='перф.'),
 'imperf.': dict(b='a', cls='лат', ru='имперф.'), 'Imperf.': dict(b='a', cls='лат', ru='имперф.'),
 'praes.': dict(b='a', cls='лат', ru='през.'), 'Praes.': dict(b='a', cls='лат', ru='през.'),
 'Präs.': dict(b='a', cls='лат', ru='през.'),
 'praet.': dict(b='a', cls='лат', ru='прет.'),
 'fut.': dict(b='a', cls='лат', ru='фут.'), 'Fut.': dict(b='a', cls='лат', ru='фут.'),
 'imperat.': dict(b='a', cls='лат', ru='импер.'), 'imper.': dict(b='a', cls='лат', ru='импер.'),
 'Imper.': dict(b='a', cls='лат', ru='импер.'), 'Imperat.': dict(b='a', cls='лат', ru='импер.'),
 'Conj.': dict(b='a', cls='лат', ru='конъ.'), 'conj.': dict(b='a', cls='лат', ru='конъ.'),
 'potent.': dict(b='a', cls='лат', ru='потенц.'), 'pot.': dict(b='a', cls='лат', ru='потенц.'),
 'Potent.': dict(b='a', cls='лат', ru='потенц.'), 'Opt.': dict(b='a', cls='лат', ru='опт.'),
 'prec.': dict(b='a', cls='лат', ru='прекат.'), 'precat.': dict(b='a', cls='лат', ru='прекат.'),
 'Prec.': dict(b='a', cls='лат', ru='прекат.'),
 'indic.': dict(b='a', cls='лат', ru='индик.'), 'Indic.': dict(b='a', cls='лат', ru='индик.'),
 'ind.': dict(b='a', cls='лат', ru='индик.', note='pwgab: indisch/Indikativ — контекст «2. pers. ind.» = индикатив'),
 # --- grammatical: non-finite / POS / syntax
 'partic.': dict(b='a', cls='лат', ru='прич.'), 'Partic.': dict(b='a', cls='лат', ru='прич.'),
 'part.': dict(b='a', cls='лат', ru='прич.'),
 'infin.': dict(b='a', cls='лат', ru='инф.'), 'Infin.': dict(b='a', cls='лат', ru='инф.'),
 'inf.': dict(b='a', cls='лат', ru='инф.'), 'Inf.': dict(b='a', cls='лат', ru='инф.'),
 'infinit.': dict(b='a', cls='лат', ru='инф.'),
 'absol.': dict(b='a', cls='лат', ru='абс.'), 'Absol.': dict(b='a', cls='лат', ru='абс.'),
 'absolut.': dict(b='a', cls='лат', ru='абс.'),
 'gerund.': dict(b='a', cls='лат', ru='герунд.', note='у PWG = абсолютив на -tvā; ср. абс.'),
 'subst.': dict(b='a', cls='лат', ru='сущ.'), 'Subst.': dict(b='a', cls='лат', ru='сущ.'),
 'Interj.': dict(b='a', cls='лат', ru='межд.'),
 'Praep.': dict(b='a', cls='лат', ru='предл.'), 'praep.': dict(b='a', cls='лат', ru='предл.'),
 'praepp.': dict(b='a', cls='лат', ru='предл.'),
 'pronomm.': dict(b='a', cls='лат', ru='мест.'), 'nomm.': dict(b='a', cls='лат', ru='имена'),
 'dem.': dict(b='a', cls='лат', ru='указ.'),
 'indecl.': dict(b='a', cls='лат', ru='нескл.'),
 'Verb.': dict(b='a', cls='лат', ru='глаг.'),
 'fin.': dict(b='a', cls='лат', ru='финитн.'),
 'Ortsadv.': dict(b='a', cls='нем', ru='нареч. места'),
 'nom. act.': dict(b='a', cls='лат', ru='имя действия'),
 'nom. ag.': dict(b='a', cls='лат', ru='имя деятеля'), 'Nom. ag.': dict(b='a', cls='лат', ru='имя деятеля'),
 'Nom. abstr.': dict(b='a', cls='лат', ru='абстр. имя'), 'nom. abstr.': dict(b='a', cls='лат', ru='абстр. имя'),
 'obj.': dict(b='a', cls='лат', ru='объект'), 'Obj.': dict(b='a', cls='лат', ru='объект'),
 'subj.': dict(b='a', cls='лат', ru='субъект'),
 'praed.': dict(b='a', cls='лат', ru='предик.'),
 # --- grammatical: valency / diathesis-adjacent
 'intrans.': dict(b='a', cls='лат', ru='неперех.'), 'intr.': dict(b='a', cls='лат', ru='неперех.'),
 'intransit.': dict(b='a', cls='лат', ru='неперех.'), 'instrans.': dict(b='a', cls='лат', ru='неперех.',
      note='опечатка источника (intransitiv)'),
 'Intrans.': dict(b='a', cls='лат', ru='неперех.'),
 'trans.': dict(b='a', cls='лат', ru='перех.'), 'transit.': dict(b='a', cls='лат', ru='перех.'),
 'Trans.': dict(b='a', cls='лат', ru='перех.'), 'tr.': dict(b='a', cls='лат', ru='перех.'),
 'impers.': dict(b='a', cls='лат', ru='безл.'), 'Impers.': dict(b='a', cls='лат', ru='безл.'),
 'neg.': dict(b='a', cls='лат', ru='отриц.'),
 'dopp.': dict(b='a', cls='нем', ru='двойн.', note='«dopp. Acc.» = «двойн. акк.»'),
 # --- grammatical: word formation / morphology / degree
 'Comp.': dict(b='a', cls='лат', ru='комп.', note='композит (сложное слово)'),
 'comp.': dict(b='a', cls='лат', ru='комп.'), 'compp.': dict(b='a', cls='лат', ru='комп.'),
 'Compp.': dict(b='a', cls='лат', ru='комп.'),
 'adj. Comp.': dict(b='a', cls='лат', ru='адъект. комп.'), 'adj. comp.': dict(b='a', cls='лат', ru='адъект. комп.'),
 'adv. Comp.': dict(b='a', cls='лат', ru='адверб. комп.'),
 'compon.': dict(b='a', cls='лат', ru='компонент'),
 'suff.': dict(b='a', cls='лат', ru='суфф.'), 'Augm.': dict(b='a', cls='лат', ru='аугм.'),
 'Redupl.': dict(b='a', cls='лат', ru='редупл.'), 'Declin.': dict(b='a', cls='лат', ru='скл.'),
 'priv.': dict(b='a', cls='лат', ru='прив.'), 'partit.': dict(b='a', cls='лат', ru='партит.'),
 'Superl.': dict(b='a', cls='лат', ru='превосх.'), 'superl.': dict(b='a', cls='лат', ru='превосх.'),
 'Compar.': dict(b='a', cls='лат', ru='сравн.'), 'compar.': dict(b='a', cls='лат', ru='сравн.'),
 'oxyt.': dict(b='a', cls='лат', ru='оксит.'),
 'ungramm.': dict(b='a', cls='нем', ru='неграмм.'), 'unregelm.': dict(b='a', cls='нем', ru='неправ.'),
 'defect.': dict(b='a', cls='лат', ru='дефект.'),
 'ved.': dict(b='a', cls='лат', ru='вед.'),
 'Patron.': dict(b='a', cls='лат', ru='патрон.'),
 'Gramm.': dict(b='c', cls='нем', ru='грамм.'), 'gramm.': dict(b='c', cls='нем', ru='грамм.'),
 # --- source / citation mechanics
 'Sch.': dict(b='c', cls='лат', ru='схол.'), 'Schol.': dict(b='c', cls='лат', ru='схол.'),
 'Scholl.': dict(b='c', cls='лат', ru='схол.'), 'Comm.': dict(b='c', cls='лат', ru='коммент.'),
 'v. l.': dict(b='c', cls='лат', ru='разночт.', note='varia lectio; латинский текстологический термин — кандидат на «оставить по общему согласию» (N5)'),
 'Z.': dict(b='c', cls='нем', ru='стк.'),
 'v. u.': dict(b='c', cls='нем', ru='снизу',
      note='von unten (счет строк снизу); H1323 (pArAsapuli) читал как «см. ниже» — уточнить на карточке'),
 'a. a. O.': dict(b='c', cls='нем', ru='указ. соч.'),
 'Ausg.': dict(b='c', cls='нем', ru='изд.'), 'Ausgg.': dict(b='c', cls='нем', ru='изд.'),
 'Calc. Ausg.': dict(b='c', cls='нем', ru='калькутт. изд.'), 'Aufl.': dict(b='c', cls='нем', ru='изд.'),
 'ed.': dict(b='c', cls='лат', ru='изд.'), 'Rec.': dict(b='c', cls='лат', ru='ред.'),
 'Hdschr.': dict(b='c', cls='нем', ru='рукоп.'), 'Hdschrr.': dict(b='c', cls='нем', ru='рукоп.'),
 'Inschr.': dict(b='c', cls='нем', ru='надпись'),
 'Cit.': dict(b='c', cls='нем', ru='цит.'), 'gedr.': dict(b='c', cls='нем', ru='печ.'),
 'ungedr.': dict(b='c', cls='нем', ru='неизд.'), 'lith.': dict(b='c', cls='нем', ru='литогр.'),
 'Anf.': dict(b='c', cls='нем', ru='начало'), 'Einl.': dict(b='c', cls='нем', ru='введ.'),
 'Th.': dict(b='c', cls='нем', ru='ч.'), 'Aut.': dict(b='c', cls='нем', ru='авт.'),
 'St.': dict(b='c', cls='нем', ru='место'), 'Anm.': dict(b='c', cls='нем', ru='прим.'),
 'p.': dict(b='c', cls='лат', ru='стр.'),
 'Uebers.': dict(b='c', cls='нем', ru='пер.'), 'Wörterb.': dict(b='c', cls='нем', ru='словарь'),
 'Unterschr.': dict(b='c', cls='нем', ru='подпись'),
}


BUCKET_NAMES = {'a': 'Грамматические категории', 'b': 'Редакторские / отсылочные / дейктические',
                'c': 'Источниковедческие (издания, рукописи, цитирование)'}
CLS_NAMES = {'нем': 'немецкое', 'лат': 'латинское/международное', 'конт': 'контекстное (n=)', 'OCR': 'OCR/неясное'}

toks = inventory()
new_tokens = [t['token'] for t in toks if t['token'] not in O]
for tok in new_tokens:
    print('NEW-TOKEN (post-21-07-2026, needs a proposal pass): %r' % tok, file=sys.stderr)
    O[tok] = dict(b='b', cls='OCR', ru=None,
                  note='токен появился в store после инвентаризации 21-07-2026 — нужен новый проход предложений')

# ---------------------------------------------------------------- sheet
items = []
def card(t):
    o = O[t['token']]
    exp = ' — '.join(x for x in (t['de'], t['en']) if x) or 'нет в pwgab'
    cur = ('уже в RU_MAP: «%s»' % t['ru_map']) if t['ru_map'] else 'сейчас: латиница/оригинал + тултип'
    prop = o['ru'] if o['ru'] else '(без фиксированного соответствия — см. примечание)'
    q = ('<b>%s</b>&nbsp;→&nbsp;' % esc(t['token'])
         + mark_cyrillic('<b>%s</b>' % esc(prop))
         + '&nbsp;&nbsp;<span class="muted">(%s)</span>' % esc(CLS_NAMES[o['cls']]))
    panels = [('данные', '<pre>расшифровка: %s\nчастота в store: %d\n%s</pre>'
               % (esc(exp), t['freq'], esc(cur)))]
    note = o.get('note')
    if note:
        panels.append(('примечание', '<pre>%s</pre>' % esc(note)))
    return {'id': 'ab:%s' % t['token'], 'filt': o['b'], 'title': t['token'],
            'badges': ['%d×' % t['freq'], CLS_NAMES[o['cls']].split('/')[0]],
            'question': q,
            'panels': panels,
            'note_placeholder': 'своя формулировка / комментарий'}

for t in toks:
    items.append(card(t))
for sig, freqs, exp, prop, note in [
    ('ed. Bomb.', '221', 'Bombay edition', 'Бомбейская ред.', 'зафиксировано MG 19-07-2026 (N4); ls-территория, применение с H1307'),
    ('Verz. d. Oxf. H.', 'в ls-ссылках', 'Verzeichniss der Oxforder Handschriften (Aufrecht 1864)', 'Кат. оксф. рукоп.', 'N9: не оставлять по-немецки; ls-территория'),
    ('Spr. / Spr. (II)', 'десятки', 'Indische Sprüche (Böhtlingk)', 'оставить сиглой + тултип «Индийские изречения»', 'заглавие источника, как ṚV.; ls-территория')]:
    items.append({'id': 'ls:%s' % sig, 'filt': 'c', 'title': sig,
                  'badges': [freqs, 'ls-сигла'],
                  'question': '<b>%s</b>&nbsp;→&nbsp;%s' % (esc(sig), mark_cyrillic('<b>%s</b>' % esc(prop))),
                  'panels': [('данные', '<pre>расшифровка: %s</pre>' % esc(exp)),
                             ('примечание', '<pre>%s</pre>' % esc(note))],
                  'note_placeholder': 'своя формулировка / комментарий'})
items.append({'id': 'meta:architecture', 'filt': 'meta',
              'title': 'МЕТА: где применяется утвержденный список?',
              'badges': ['архитектура'],
              'question': mark_cyrillic(
                  '<b>Принять</b> = применять только на этапе рендеринга (архитектура 10-07-2026: '
                  'store хранит исходные теги, переводит генератор сайта — покрывает все будущие корни). '
                  '<b>Отклонить</b> = список должен также переписать сам store (отдельный шаг с '
                  'translation_memory/промоушен-механикой). <b>Отложить</b> = обсудить.'),
              'panels': [('контекст', '<pre>ABBREVIATIONS_RU.md § "Architecture decision: fix at RENDER TIME"\n'
                          'Решение 10-07 остается в силе, пока эта карточка не проголосована иначе.</pre>')],
              'note_placeholder': 'комментарий'})

config = {
    'sheet_id': 'h1303_abbrev',
    'title': 'H1303 — единый список сокращений pwg_ru: ратификация',
    'subtitle': ('269 ab-токенов store + 3 ls-пограничных + 1 мета-карточка. '
                 'Принять = утвердить русское соответствие; отклонить = оставить как есть '
                 '(латиница/оригинал + тултип); отложить = обсудить. Немецкие — переводятся все '
                 '(N3a/N4); латинские грамматические по умолчанию переводятся (N8), '
                 'оставить — только явным голосом (N5). Эмиттер: csl-pyutil 0.3.1.'),
    'footer': ('Экспорт сохранить как pwg_ru/eval/h1303_abbrev.decisions.json — затем Session 2 '
               'хендоффа H1303 применит утвержденный список.'),
    'approve_label': 'принять RU', 'reject_label': 'оставить как есть',
    'filters': [('a', 'грамматические'), ('b', 'редакторские'), ('c', 'источники'), ('meta', 'мета')],
    'generated': GENERATED,
    'show_ids': True,
    'save_as': 'pwg_ru/eval/h1303_abbrev.decisions.json',
    'note_min_height_px': 56,
}
html_doc = render_review_sheet(items, config)
out = os.path.join(RT, 'review', 'h1303_abbrev_sheet.html')
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'w', encoding='utf-8', newline='\n') as f:
    f.write(html_doc)
print('wrote %s (%d cards, %d bytes)' % (out, len(items), len(html_doc)))
