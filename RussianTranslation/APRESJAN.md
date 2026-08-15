# Apresjan and pwg_ru — the theoretical backbone

_Created: 06-08-2026 · Last updated: 15-08-2026_

The earlier [methodology review](METHODOLOGY_REVIEW.md) leaned on the
Anglo-American tradition (Atkins & Rundell, Zgusta). For a dictionary whose
*target* language is Russian, the native and more demanding tradition is the
**Moscow Semantic School** of **Ю. Д. Апресян (Yuri Apresjan)**. His
*Лексическая семантика. Синонимические средства языка* (Lexical Semantics:
Synonymic Means of Language; 1st ed. 1974, 2nd ed. 1995) is the foundational
text.

Source: [Apresjan-1995, Избранные труды, т. 1](https://ruslang.ru/sites/default/files/doc/apresjan/Apresjan-1995-izbr_trudy_1_lexsem.pdf)
(480 pp.). Section/page references below are to that edition.

## The three pillars (preface to the 2nd ed., с. 2)

Apresjan states his program in three principles — quoted, then applied to pwg_ru:

1. **Принцип интегральности описания языка** — *integral description of
   language*: a lexeme is given **all** properties relevant to the rules
   (including grammatical), and the rules account for all lexeme behaviour.
   → For pwg_ru: a headword entry is not a gloss list but is coordinated with
   Sanskrit **grammar** — `<gram>`/`<lex>`, the paradigm/root data from the
   sibling WhitneyRoots work, government (rekcija). *Grounds review rec 6
   (microstructure) and the integral dictionary↔grammar link.*

2. **Принцип лексикографического портретирования** — *lexicographic
   portraying*: each lexeme is "an autonomous and uniquely distinctive world,
   which one would want to describe in all its richness."
   → For pwg_ru: the target unit is a **lexicographic portrait** of each
   Sanskrit headword — senses (a tree, not a bag), government pattern, regular
   sense-extensions, Russian (near-)synonym set with discrimination, stylistic
   and diachronic labels, and culture-specific connotations. PWG already gives a
   rich portrait in German; the Russian edition should match that depth, not
   flatten it to equivalents.

3. **Лексикографические типы** — *lexicographic types*: groups of lexemes with
   partially shared properties that "react identically to definite linguistic
   rules"; portraits are combined with types.
   → For pwg_ru: cluster Sanskrit headwords into types (nomina actionis in
   *-ana*; agent nouns; the regular-polysemy classes below) and describe each
   type **uniformly** — same Russian equivalence strategy, same label scheme.
   *This is the theoretical basis for the cross-card terminology-consistency
   auditor (review rec 7): consistency is required precisely within a type.*

Plus the fourth, programmatic stance (preface, с. 2):
**Реконструкция «наивной картины мира»** — reconstructing the *naive picture of
the world* encoded in the lexis. → For pwg_ru: record the culture-specific
connotations of words like *dharma*, *karman*, *tapas* as part of the entry (the
"naive" Indian worldview), not as a single translation equivalent — the
treatment of culture-specific items, given a theoretical home.

## The toolkit from *Лексическая семантика*

- **Семантический язык / толкование** (semantic metalanguage / *explication*),
  гл. 2 (с. 56). Word meanings are explicated by reduction to a small inventory
  of **семантические примитивы** (semantic primitives; *словарь семантического
  языка*, с. 70), with explicit **требования к толкованиям** (requirements for
  explications, с. 95): an explication must be **non-circular**, in **simpler**
  terms than the definiendum, **necessary and sufficient**, and **substitutable**.
  → For pwg_ru: where a one-word equivalent is anisomorphic or absent, give a
  proper Russian *толкование* meeting these requirements — the difference between
  a word-list and a real semantic dictionary.

- **Регулярная многозначность** (regular polysemy / semantic derivation), гл. 3
  (с. 175; nouns с. 193, verbs с. 203). Sense extensions follow systematic
  patterns: ‘каузация → извлечение → ликвидация → удаление → обработка →
  деформация’, ‘действие → каузация действия’, ‘action → result → instrument →
  agent → place’.
  → For pwg_ru: Sanskrit polysemy is highly regular. Model the sense tree as a
  derivation network, **predict** the expected Russian renderings of each
  extension, and **detect** when the corpus harvest is missing a regular sense
  (a coverage signal, not just a list).

- **Семантические валентности / модель управления** (semantic valencies /
  government pattern), с. 119/133. Each predicate word carries its argument
  frame.
  → For pwg_ru: record the **rekcija** of verbal/relational headwords (cases,
  prepositions, the Russian construction) — the integral link to grammar.

- **Синонимия: точные и неточные синонимы** (exact vs near synonyms), the
  *Синонимические средства языка* programme (later → the *Новый объяснительный
  словарь синонимов*). Near-synonyms are separated by precise **semantic**,
  **combinatorial**, and **connotational** differences.
  → **The single highest-leverage application.** The harvest reader already
  surfaces multiple Russian renderings per Sanskrit word — e.g. *rājan* →
  царь / государь / владыка, *dharma* → дхарма / закон / добродетель / долг.
  Apresjan's method says these are a **near-synonym set to be discriminated**,
  not a flat list: царь (neutral) vs государь (honorific, address) vs владыка
  (power/lord connotation); dharma as закон (legal śāstra) vs добродетель/долг
  (epic ethics) vs дхарма (technical term). The stratified counts the harvest
  already produces are exactly the evidence for this discrimination.

- **Конверсивы и антонимы** (conversives, antonyms), гл. 5–6 (с. 263, 284):
  systematic lexical relations.
  → For pwg_ru: a relations layer (SKOS-style) linking senses — feeds the
  OntoLex export (review rec 8) and a future Russian→Sanskrit reverse index.

## How this reshapes the roadmap

Apresjan grounds, in the native tradition, several methodology-review items and
adds three concrete proposals:

| Apresjan principle | pwg_ru action | review rec |
|---|---|---|
| Lexicographic portrait | sense tree + government + labels + connotations per headword | 6 |
| Lexicographic types | uniform equivalence within a type → terminology-consistency auditor | 7 |
| Integral description | couple the entry with `<gram>` + WhitneyRoots paradigm/rekcija | 6 |
| Требования к толкованиям | quality bar for Russian *толкования* where no equivalent exists | 4 |
| Near-synonym discrimination | turn multi-rendering harvests into discriminated synonym sets | 6 (new) |
| Regular polysemy | predict + audit sense extensions; structured sense tree | 6 (new) |
| Naive picture of the world | record culture-specific connotations (dharma, karman…) | 6 (new) |

### Three new concrete proposals

1. **A "lexicographic portrait" card schema** (Apresjan pillar 2): formalize the
   per-sense structure — `sense_tree`, `government`, `equivalence_type`
   (translational-equivalent vs *толкование*), `synonyms` (discriminated),
   `labels` (diasystem), `connotations`. Supersedes the flat sense-bag.

2. **A synonym-discrimination step** (the highest-leverage one): when
   `corpus_harvest` returns ≥2 renderings for a key, attach Apresjan-style
   differentiae (semantic / combinatorial / stratum-connotational), using the
   stratified counts as evidence. This is the *Новый объяснительный словарь
   синонимов* method applied to the Sanskrit→Russian direction.

3. **A regular-polysemy layer**: encode the common Sanskrit sense-derivation
   patterns as types; predict and verify each sense's Russian rendering against
   the corpus — a structured alternative to an unordered sense list.

> Working note: pwg_ru should cite Apresjan as its lexicographic-theory backbone
> in the front matter, alongside Zgusta (general bilingual theory) and the
> Cologne CDSL apparatus. The native Russian tradition is not optional polish —
> for a Russian-target scholarly dictionary it is the correct standard.

## Диахрония взглядов Апресяна на синонимию (H2805, 15-08-2026)

Написано для закрытия §5.3 стилевого свода
([PWG_RU_STYLE_GUIDE_OF_RECORD_2026-07.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/PWG_RU_STYLE_GUIDE_OF_RECORD_2026-07.md)):
голос MG 15-08-2026 отложил карточки A2/A3 листа `h1306_style` с возражением «Апресян
требует различения, а не удаления квазисинонимов — и его позиция менялась по годам».
Ниже — эта диахрония по опубликованному, с честной границей того, что публикации не
решают. Составлено Fable 5 (`claude-fable-5`); страничные ссылки даны только там, где
они уже дословно сверены в этом репозитории
([STYLE_RESEARCH_DOUBLETS_VL_COMP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/STYLE_RESEARCH_DOUBLETS_VL_COMP.md) §2).

| Период | Работа (издание, год) | Что такое синоним | Что делать с квазисинонимами |
|---|---|---|---|
| 1957 | «Проблема синонима» (Вопросы языкознания, 1957, № 6) | ранний, операциональный период: синонимия ищется через критерии взаимозаменимости и дистрибуции; объект — пара слов и тест над ней | различия констатируются, аппарата их описания ещё нет |
| 1969 | «Синонимия и синонимы» (Вопросы языкознания, 1969, № 4) | переходный: критерий становится семантическим — совпадение толкований; появляется различение полной и неполной синонимии | неполные синонимы — законный объект словаря, но описание различий ещё программа, не метод |
| 1974 | «Лексическая семантика. Синонимические средства языка» (М.: Наука, 1974; 2-е изд. — Избранные труды, т. I, 1995) | зрелая теория: **точные** синонимы (толкования совпадают полностью) vs **неточные** = квазисинонимы (большая общая часть толкований), с. 218 2-го изд.; толкование обязано быть необходимым-и-достаточным (с. 95) | «требует чёткого различения тех и других при их фиксации в словаре» — различение становится обязанностью словаря |
| 1979 | «Англо-русский синонимический словарь» (Апресян и др., М.: Русский язык, 1979) | первая большая лексикографическая практика метода в двуязычной постановке | словарная статья = синонимический ряд + эксплицитные различия; ряд без различий статьёй не считается |
| 1986–1995 | «Интегральное описание языка и системная лексикография» (статьи 1986–1994; Избранные труды, т. II, 1995) | синонимический ряд встраивается в **лексикографический портрет** лексемы; портреты объединяются в типы | различия описываются по всем зонам портрета (семантика, сочетаемость, коннотации), не только по толкованию |
| 1997–2004 | НОСС: «Новый объяснительный словарь синонимов русского языка», вып. 1 (1997), вып. 2 (2000), вып. 3 (2003); 2-е изд., испр. и доп., одним томом (2004) | итоговая доктрина: «объяснительный» словарь — **содержанием статьи являются сами различия** ряда, по девяти осям сходств и различий | ряд никогда не редуцируется к одному члену; каждый член получает свою зону употребления |
| 2014–2017 | «Активный словарь русского языка», т. 1–2 (2014), т. 3 (2017), под ред. Ю. Д. Апресяна | активный словарь: синонимы и аналоги приводятся посзначно как средство **производства** текста | богатство ряда сохраняется ради говорящего; различение — через посзначную структуру |

**Инвариант всех периодов:** квазисинонимы надо **различать и описывать** — ни в одном
периоде нет санкции на их **удаление**. Менялись критерий (операциональный → через
толкования → интегральный), единица (пара → ряд → портрет) и глубина описания различий,
но не это требование. Возражение MG к A2/A3 подтверждается публикациями: жёсткое «ровно
один эквивалент» (A2) противоречит Апресяну **каждого** периода после 1969; политика A1 с
ним совместима ровно в той мере, в какой дискриминированные пары **сохраняются** и их
различие фиксируется (поле `differentia`) — что §5.2 свода и оговаривает.

**Чего опубликованное НЕ решает (вопросы Сергею Крылову):**

1. Санкционировал бы Апресян дефолт «один основной эквивалент» для **пассивного**
   двуязычного словаря мёртвого языка? Его двуязычная практика (АРСС 1979) — словарь
   активного типа; о редукции рядов в переводных словарях пассивного типа
   систематического высказывания в перечисленных работах нет.
2. Есть ли поздние (после НОСС) устные или малотиражные уточнения его позиции о
   квазисинонимии именно в переводной части двуязычного словаря — то, что не выяснимо
   по большим публикациям.

_Dr. Mārcis Gasūns_
