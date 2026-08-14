#!/usr/bin/env python
"""Session drafts for the H2684 n=400 unfilled definition_gloss rows."""
from __future__ import annotations

import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

GLOSS = {
    '{%ganz unerfahren%}': '{%совершенно неопытный%}',
    '{%matt werden, hinsterben%}': '{%слабеть, умирать%}',
    '{%durchbrechen%}': '{%пробивать, прорывать%}',
    '{%Opferkuchen beim Thieropfer%}': '{%жертвенная лепёшка при жертвоприношении животного%}',
    '{%wie viele Unkosten fallen auf?%}': '{%какие издержки приходятся?%}',
    '{%Jahr%}': '{%год%}',
    '{%ein Leder, welches der Bogenschütz am linken Arm trägt, um diesen vor der abprallenden Sehne zu schützen%}':
        '{%кожа, которую лучник носит на левой руке, чтобы защитить её от отскакивающей тетивы%}',
    '{%strahlen, glänzen, prangen%}': '{%сиять, блестеть, красоваться%}',
    '{%verschaffend%}': '{%доставляющий%}',
    '{%weiterhin, dazu%}': '{%далее, к тому же%}',
    '{%Fasern%}': '{%волокна%}',
    '{%hinweisen, auf Etwas hindeuten, andeuten%}':
        '{%указывать, намекать на что-л., подразумевать%}',
    '{%es erreiche uns nicht%}': '{%да не постигнет нас%}',
    '{%das Ablegen der Kränze%}': '{%снятие венков%}',
    '{%schöne Hüften habend%}': '{%с прекрасными бёдрами%}',
    '{%Laut, Wort%}': '{%звук, слово%}',
    '{%verfügen über; vermögen, mächtig sein; Herr sein einer Sache%}':
        '{%располагать; мочь, быть в силах; быть господином чего-л.%}',
    '{%ehrwürdig%}': '{%досточтимый%}',
    '{%Wolken%}': '{%облака%}',
    '{%das Steigen der Macht%}': '{%возрастание могущества%}',
    '{%Wind%}': '{%ветер%}',
    '{%von hinten bedecken%}': '{%покрывать сзади%}',
    '{%gut geartet, wohlgebildet; ächt%}':
        '{%благонравный, хорошо сложённый; подлинный%}',
    '{%bekanntgeworden%}': '{%ставший известным%}',
    '{%einem Scheermesser ähnlich%}': '{%подобный бритве%}',
    '{%von selbst%}': '{%сам собой%}',
    '{%Zeichen im Thierkreise%}': '{%знак зодиака%}',
    '{%wohlunterrichtet, des Richtigen kundig%}':
        '{%хорошо сведущий, знающий должное%}',
    '{%eine Art Coitus%}': '{%вид соития%}',
    '{%erschrocken%}': '{%испуганный%}',
    '{%kennt, hersagt%}': '{%знает, читает наизусть%}',
    '{%einverstanden sein%}': '{%быть согласным%}',
    '{%das Zusammentreffen, Eintreffen%}': '{%встреча, наступление%}',
    '{%auf dass, damit%}': '{%дабы, чтобы%}',
    '{%Nass der Lippen%}': '{%влага губ%}',
    '{%zerpflückend%}': '{%раздёргивающий%}',
    '{%mache Platz%}': '{%посторонись%}',
    '{%Handlung%}': '{%действие%}',
    '{%noch nicht so bald reif werdend%}': '{%не так скоро созревающий%}',
    '{%wohlriechend gemacht%}': '{%сделанный благовонным%}',
    '{%verreinigt hinkommen; aufsuchen%}': '{%приходить вместе; разыскивать%}',
    '{%das Aeussere eines Menschen%}': '{%внешность человека%}',
    '{%das Studium der heiligen Schriften%}': '{%изучение священных писаний%}',
    '{%zugleich mit Etwas erscheinen%}': '{%являться вместе с чем-л.%}',
    '{%mit dem Dreizack bewaffnet%}': '{%вооружённый трезубцем%}',
    '{%Geistesgegenwart%}': '{%присутствие духа%}',
    '{%Gelbwurz%}': '{%куркума%}',
    '{%der Zerstreuer sein, wenn nicht <ab>u. s. w.</ab>%}':
        '{%быть рассеивателем, если не <ab>и т. д.</ab>%}',
}


def main():
    src = sys.argv[1]
    dest = sys.argv[2]
    n = 0
    missing = []
    with open(src, encoding='utf-8') as f_in, open(
            dest, 'w', encoding='utf-8', newline='\n') as f_out:
        for line in f_in:
            row = json.loads(line)
            if row.get('fragment_class') != 'definition_gloss':
                continue
            src_s = row.get('source_string') or ''
            tgt = GLOSS.get(src_s)
            if not tgt:
                missing.append(src_s)
                continue
            out = {
                'fragment_id': row['fragment_id'],
                'fragment_class': 'definition_gloss',
                'source_string': src_s,
                'target_string': tgt,
                'origin': 'grok-4.6-draft',
                'usage': {
                    'input_tokens': 0, 'output_tokens': 0, 'cost_usd': 0.0,
                    'note': 'session-drafted Grok 4.6 (grok-4.6); no xAI HTTP call',
                },
            }
            f_out.write(json.dumps(out, ensure_ascii=False) + '\n')
            n += 1
    print(json.dumps({'drafted': n, 'missing': missing}, ensure_ascii=False))
    return 1 if missing else 0


if __name__ == '__main__':
    sys.exit(main())
