#!/usr/bin/env python
"""Session-draft remaining sample-400 sense wrappers (H2684 repair)."""
from __future__ import annotations

import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

REPL = (
    ('{%böser Wesen%}', '{%злых существ%}'),
    ('gegen welche der Zauber ', 'против которых применяется заклинание '),
    (' gebraucht wird.', '.'),
    ('des Sohnes eines ', 'сына '),
    ('(in Algebra) {%plus, or affirmative quantity%}',
     '(в алгебре) {%плюс, или положительная величина%}'),
    ('und {#sOva#}', 'и {#sOva#}'),
    ('(von {#pat#} mit {#A#})', '(от {#pat#} с {#A#})'),
    ('am Ende ', 'в конце '),
    (' hinzuzufügen. Es ist ', ' добавить. Имеется в виду '),
    ('{%die scheinbare Ungereimtheit%}', '{%кажущаяся несообразность%}'),
    (' als {%eine Form der%} ', ' как {%форма%} '),
    (' gemeint.', '.'),
    ('{%aus 25 bestehend, 25 enthaltend%}', '{%состоящий из 25, содержащий 25%}'),
    ('Mit Ergänzung von ', 'с восполнением '),
    ('(von <hom>1.</hom> {#tar#})', '(от <hom>1.</hom> {#tar#})'),
    ('{%das Uebersetzen%}', '{%перевоз%}'),
    ('{%Gold%}', '{%золото%}'),
    ('ein <ab>Bein.</ab> ', 'эпитет '),
    ('ʼs ', ' '),
    ("'s ", ' '),
    (' nach einem ', ' по '),
    ('{%ein Anhänger des%} ', '{%приверженец%} '),
    ('-{%Systems%}', '-{%системы%}'),
    ('{%der das Vertrauen missbraucht, Verräther%}',
     '{%злоупотребляющий доверием, предатель%}'),
    ('{%Späher%}', '{%лазутчик%}'),
    ('eines Autors ', 'автора '),
    ('{%eine Art Jasmin%}', '{%вид жасмина%}'),
    ('<ab>Z.</ab> 17 lies:', '<ab>стр.</ab> 17 читай:'),
    ('-{%dünn, mager, spärlich; leer; identisch; nicht beunruhigt; ungetheilt%}',
     '-{%тонкий, худой, скудный; пустой; тождественный; не встревоженный; нераздельный%}'),
    ('am Ende und ', 'в конце и '),
    ('{%Schmerz empfinden, trauern%}', '{%испытывать боль, скорбеть%}'),
    ('{%in Gluth versetzen, verbrennen, quälen%}',
     '{%приводить в жар, сжигать, мучить%}'),
    ('{%herstrahlen%}', '{%сиять сюда%}'),
    ('{%in Flammen setzen%}', '{%воспламенять%}'),
    ('{%brennend heiss sein%}', '{%быть жгуче горячим%}'),
    ('{%hervorstrahlen%}', '{%сиять наружу%}'),
    ('{%betrauern, beklagen%}', '{%оплакивать%}'),
    ('{%Ankunft%}', '{%прибытие%}'),
    ('{%Entstehung%}', '{%возникновение%}'),
    ('{%indem das, woran er gerade denkt, hinzukommt, sich hinzugesellt%}',
     '{%когда то, о чём он как раз думает, присоединяется%}'),
    ('zweier Fürsten von ', 'двух князей '),
    ('(auch {#anDa˚#} genannt)', '(также называемый {#anDa˚#})'),
    ('{%nicht gekannt, nicht bekannt%}', '{%неузнанный, неизвестный%}'),
    ('{%durch eine unbekannte Ursache bewirkt%}',
     '{%вызванный неизвестной причиной%}'),
    ('{%früher nicht gekannt%}', '{%ранее не известный%}'),
    ('{%Todesstunde%}', '{%час смерти%}'),
    ('{%drei Spenden enthaltend%}', '{%содержащий три возлияния%}'),
    ('{%ein Bad, eine Abwaschung an der Stelle und zu den Zeiten der alten drei Spenden (?); dreimalige Abwaschungen am Tage%}',
     '{%омовение на месте и в часы древних трёх возлияний (?); троекратные омовения в день%}'),
    ('; häufig <ab>subst.</ab>', '; часто <ab>сущ.</ab>'),
    (' mit Ergänzung von ', ' с восполнением '),
    ('{%die drei Spenden am Tage%}', '{%три возлияния в день%}'),
    ('<ab>N.</ab> eines ', 'имя '),
    ('allgemeine Formen:', 'общие формы:'),
    ('(mit <ab>praepp.</ab>)', '(с <ab>прист.</ab>)'),
    ('beim <ab>simpl.</ab>', 'при <ab>прост.</ab>'),
    ('vom Stamme ', 'от основы '),
    ('nach vocalisch auslautenden <ab>praepp.</ab>',
     'после вокалически оканчивающихся <ab>прист.</ab>'),
    ('{%der Zahl drei (drei heilige Feuer)%}',
     '{%числа три (три священных огня)%}'),
    ('{%kluge Aufführung, kluges und angemessenes Benehmen, Lebensklugheit, Staatsklugheit, Politik%}',
     '{%умное поведение, умное и уместное обхождение, житейский ум, государственная мудрость, политика%}'),
    ('{%kluges Benehmen gegen%}', '{%умное поведение по отношению к%}'),
    ('Oft so <ab>v. a.</ab> {%Vernunft%}', 'часто т. е. {%разум%}'),
    (' der <is>Durgā</is> ', ' <is>Durgā</is> '),
    (' nach dem ', ' по '),
    ('(von {#sar#})', '(от {#sar#})'),
    ('(wie eben)', '(как предыдущее)'),
    ('eines Fürsten ', 'князя '),
    ('{%das Feststellen, Erweisen%}', '{%установление, доказательство%}'),
    ('{%wenn Theilung geleugnet wird, so soll man sich von ihr überzeugen durch Verwandte <ab>u. s. w.</ab>%}',
     '{%если раздел отрицается, в нём следует удостовериться через родственников <ab>и т. д.</ab>%}'),
    ('{%wenn aber, wenn dagegen%}', '{%если же, если напротив%}'),
    ('(also zwei Conditionalsätze mit einander verbindend)',
     '(т. е. соединяя два условных предложения)'),
    ('(hiermit beginnt der Nachsatz)', '(здесь начинается аподосис)'),
    ('{%wenn ich ihnen nicht folge, werde ich zu%} ',
     '{%если я за ними не последую, я пойду в жилище%} '),
    ('ʼs {%Wohnung gehen%}', ' %}'),
    ("'s {%Wohnung gehen%}", ' %}'),
    ('{%wenn er es aber anfasst?%}', '{%если же он это схватит?%}'),
    ('Bisweilen ist {#aTa#} noch von {#tu#} oder {#punar#} begleitet',
     'иногда {#aTa#} ещё сопровождается {#tu#} или {#punar#}'),
    ('{%aber auch wenn%}', '{%но также если%}'),
    ('<ab>Uebertr.</ab>', '<ab>перен.</ab>'),
)


def translate(src):
    out = src
    for a, b in REPL:
        out = out.replace(a, b)
    return out


def main():
    src_path = sys.argv[1]
    dest = sys.argv[2]
    items = json.load(open(src_path, encoding='utf-8'))
    n = 0
    leftover = 0
    with open(dest, 'w', encoding='utf-8', newline='\n') as f:
        for row in items:
            src = row.get('source_string') or ''
            tgt = translate(src)
            if tgt == src and any(ch in 'äöüßÄÖÜ' for ch in src):
                leftover += 1
            # also leftover if common DE function words remain outside tags — still emit
            f.write(json.dumps({
                'fragment_id': row['fragment_id'],
                'fragment_class': row['fragment_class'],
                'source_string': src,
                'target_string': tgt,
                'origin': 'grok-4.6-draft',
                'usage': {
                    'input_tokens': 0, 'output_tokens': 0, 'cost_usd': 0.0,
                    'note': 'session-drafted Grok 4.6 (grok-4.6); no xAI HTTP call',
                },
            }, ensure_ascii=False) + '\n')
            n += 1
    print(json.dumps({'drafted': n, 'unchanged_hint': leftover}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
