# Renou Step-0 pilot — evidence remake (v2) and the ACC/NCC source-markup answer

_Created: 19-07-2026 · Last updated: 19-07-2026_

Response to [review/decisions.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/decisions.md)
(MG, 19-07-2026): 3 of 70 pilot cards voted, all reject, with the ruling —
remake the approach before any further voting; count the new PWG
register/genre layer; answer how ACC/NCC data can serve `<ls>` source markup
for the PWG Russian and English translations. Executed as
[H1311](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1311-Fable_RussianTranslation_renou-pilot-evidence-remake_19.07.26.md).

## 1. The one systemic defect behind all three rejections

The v1 card's "DCS evidence" panel showed **lemma-global** facts — the oldest
attestation of the lemma *anywhere* and a bare text count — under a question
about **one specific state**. So a Vedic (I) question was headlined by
Manusmṛti (S0-001), a Pāṇinian (II) question by the Ṛgveda (S0-002), and a
19-text lemma named none of its texts (S0-003). The voter could not see which
texts actually back the contested state — the exact thing being voted.

The remake ships three artifacts (all in
[src/](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/src)):

- [renou_pilot_evidence.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_pilot_evidence.py)
  — one DCS pass collecting, per sampled lemma, the **full list of attesting
  texts** (name, date, Renou state, text-level confidence, register codes),
  reusing `build_dcs_renou`'s text→state resolution verbatim so evidence and
  index cannot drift. Output: `renou_pilot_evidence.json` (committed).
- [renou_pilot_sample.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_pilot_sample.py)
  — now also carries `key1` (SLP1) per item; deterministic regen verified
  (same 70 items, same stratum composition).
- [build_renou_pilot_sheet.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_renou_pilot_sheet.py)
  — v2 sheet: per-state judgment criterion under every question; the
  contested-state texts **named** (or an explicit "no DCS text of this state —
  the state rests on: [signals]" marker); the **full attestation list**,
  scrollable, contested rows highlighted; the PWG register/genre layer joined
  onto pwg/pw cards; MG's three v1 notes rendered on their cards as
  prior-vote context. `sheet_id` bumped to `renou-pilot-v2-2026-07-19`.

## 2. Answers to the three v1 vote notes

### S0-001 (śvapac, PW, state I) — "Manusmṛti is epic, not vedic"

Agreed, and the pipeline already agrees: Manusmṛti (DCS genre Sūtra/Dharma,
date 200 CE) resolves to **état III** (epic prolongement), not I — see
`GENRE_RENOU` + `state_by_date` in
[build_dcs_renou.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_dcs_renou.py).
Manusmṛti was **never the state-I evidence** for śvapac; it appeared on the
card only as the lemma-global "oldest attestation", which the v1 panel wrongly
put under a state-I question. The evidence run now names the actual state-I
supporter — and vindicates the rejection twice over: it is
**Vaikhānasagṛhyasūtra, dated 450 CE**, classified état I purely by the
`gṛhyasūtra` **name-hint, which carries no date guard** (`NAME_HINTS` in
`build_dcs_renou.py` maps any gṛhya/śrauta-sūtra name to I regardless of the
text's date — this one is a late-classical manual, not a vedāṅga). So the
"Vedic" tag for śvapac rests on a 450-CE text: a probable over-tag, exactly
the failure class stratum A samples — now visible on the card instead of
hidden behind a count. The name-hint date-guard fix is deliberately NOT
applied here: the pilot vote measures over-tagging before the tagger is
touched; the fix lands after the vote confirms the class. The card also now
carries the word's PWG register-layer profile (`Svapac`: register *sutra*,
genres *dharmaśāstra | lexicon | other*, sources AK · M · ŚKDR — a
koṣa-and-Manu word in PWG's own citations).

### S0-002 (sru, PW, state II) — "It's quoted in Aṣṭādhyāyī, that is enough. Right?"

Right — **adopted as the état-II criterion**: membership in the grammarians'
corpus (Aṣṭādhyāyī incl. dhātupāṭha/gaṇapāṭha, Mahābhāṣya, Kāśikā…) suffices
on its own; Ṛgveda attestation is neither required nor relevant to II. The v2
card states this criterion under the question and its state panel lists only
state-II texts. The Ṛgveda line the v1 card showed was, again, the
lemma-global oldest-attestation figure, not II evidence.

### S0-003 (bhoja, PWG, state III) — "why do you not show the full list?"

No reason — it was an information loss in the lemma index
(`dcs_lemma_renou.json` stores counts, not names, to stay compact over 100k+
lemmas). The evidence sidecar restores the names for the sampled 70: every v2
card has a "Full DCS attestation (N texts)" panel listing all N texts with
date, state and registers, contested state highlighted.

## 3. The PWG register/genre layer, counted

The layer ([SanskritGrammar
data/pwg_register_genre](https://github.com/gasyoun/SanskritGrammar/blob/main/data/pwg_register_genre/README.md),
merged 19-07-2026: 116,033 entries, homonym-precise, 90.6 % of `<ls>` citation
tokens mapped) is joined onto every pwg/pw card by SLP1 `k1`: register,
earliest period, full period set, lexicon-only flag, genre profile, matched
source tokens. For PW cards the panel is labeled as the PWG sibling profile
(the layer reads `pwg.txt` citations; PW condenses PWG).

This gives each card **two independent period systems**: the DCS route (dated
corpus texts the lemma occurs in) and the `<ls>` route (the sources the
dictionary itself cites). Where they disagree — e.g. a PWG-vedic word with no
Vedic DCS attestation — the disagreement is now visible on the card instead of
silently merged, which is precisely the over-tag class the pilot samples.

## 4. Как использовать ACC и NCC в разметке источников PWG (и его русского/английского переводов)

ACC (Aufrecht, *Catalogus Catalogorum*) и NCC (*New Catalogus Catalogorum*,
Мадрас) — каталоги **произведений и авторов**, не корпусы: они говорят, что
произведение существует (рукописи, издания, комментарии, варианты заглавий),
но не что слово в нём встречается. Поэтому их место — в **идентификации
источников**, а не в подтверждении словоупотреблений. У нас уже есть актив:
кроссволк ACC×NCC (H249, P1, слит; адъюдикация P2 Tier C/D ждёт голосования —
[H264](https://github.com/gasyoun/Uprava/blob/main/handoffs/H264-Sonnet_SanskritLexicography_acc_ncc_p2_adjudication_06.07.26.md));
дорожная карта — [ROADMAP_ACC_NCC.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ACC_NCC.md).

Четыре применения, в порядке отдачи:

1. **Сигла → каноническое произведение.** Каждый токен-источник PWG (`ṚV.`,
   `MBH.`, `KATHĀS.`, `Verz. d. Oxf. H.`…) получает ссылку на запись ACC/NCC —
   стабильный идентификатор произведения. Это даёт **один** реестр
   источников с колонками: сигла PWG → работа (ACC/NCC id) → каноническое
   русское название → каноническое английское название. Один реестр
   обслуживает и pwg_ru, и будущий английский перевод: немецкие сокращения
   Бётлингка перестают «переводиться» ad hoc в каждой статье (ровно жалоба из
   голосов H178: «немецкие сокращения не оставляем непереведёнными»).
   Технически это колонка `acc_ncc_id` в таблице источников
   [pwg_sources.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_sources.py)
   / кураторской карте register-слоя (~90 токенов = 89 % цитат — стартовый
   объём ручной привязки один вечер, не месяцы).
2. **Метаданные там, куда DCS не дотягивается.** У register-слоя 9.4 %
   токенов не размечены, у DCS — 270 текстов против тысяч произведений,
   цитируемых PWG. NCC даёт автора/датировку/традицию для этих «хвостовых»
   источников — второй маршрут к периодизации `<ls>`-цитат, независимый от
   DCS.
3. **Проверка lexicon-only (слова-призраки).** 32,690 заголовков PWG
   засвидетельствованы только в кошах. ACC/NCC идентифицируют сами коши
   (Amara, Medinī, Hemacandra…), их редакции и комментарии — и по NCC видно,
   всплывает ли слово хоть в одном не-лексикографическом произведении. Это
   готовый исследовательский срез поверх lexicon-only переписи register-слоя.
4. **Тултипы/ссылки в переводе.** В render-слое статьи (`<ls>`-тултипы,
   [build_article_site.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_article_site.py))
   каждая сигла может вести на карточку произведения (название RU/EN, автор,
   век, ACC/NCC-ссылка) — читатель перевода видит, *что* цитируется, без
   немецкого аппарата XIX века.

Ограничение, честно: ACC/NCC не заменяют ни DCS (аттестация), ни
register-слой (профиль цитат) — они третий, каталожный слой поверх тех же
сигл. Правильный порядок внедрения: сначала доголосовать P2-адъюдикацию
кроссволка (H264), затем колонка `acc_ncc_id` для топ-90 токенов, затем хвост.

## 5. Re-vote

The regenerated sheet (same 70 items, same IDs, evidence complete):
`RussianTranslation\review\sanskritlexicography-renou-hypotheses_pilot_review.html`
— sheet_id `renou-pilot-v2-2026-07-19`. Voting starts fresh; the three v1
notes are visible on their cards. The v1 3-vote export
([sanskritlexicography-renou-hypotheses_pilot_decisions.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/sanskritlexicography-renou-hypotheses_pilot_decisions.json))
is committed as the methodology-feedback record of the v1 sheet, not as
per-card dispositions.

Evidence remake computed by Fable 5 (`claude-fable-5`), H1311; underlying
pipeline by Sonnet 5 (`claude-sonnet-5`) and Opus 4.8 (`claude-opus-4-8`) per
the respective script docstrings.

_Dr. Mārcis Gasūns_
