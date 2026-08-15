# agni gloss-review — decisions applied (15-08-2026)

_Created: 15-08-2026 · Last updated: 15-08-2026_

Audit record for the human vote on the agni gloss-review sheet. Applying session:
Opus 5 (claude-opus-5), 15-08-2026, handoff
[H2861](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2861-Opus_SanskritLexicography_agni-gloss-decisions-apply_15.08.26.md).

| | |
|:--|:--|
| Sheet id | `sanskritlexicography-article-comparison_agni` |
| Sheet (hub copy) | [gasyoun.github.io/vote/sheets/gloss_agni.html](https://gasyoun.github.io/vote/sheets/gloss_agni.html) |
| Decisions file | `Uprava/review/sanskritlexicography-article-comparison_agni_decisions.json` (private hub, gitignored artifact) |
| Voted | 11 / 11 — no unvoted rows, no unknown ids |
| Verdicts | **9 approve · 1 reject · 1 defer** |

## Applied (9 approve)

Column 3 («Русский») of
[article-comparison/agni.pd-min.ru.md](https://github.com/gasyoun/SanskritLexicography/blob/master/article-comparison/agni.pd-min.ru.md).

| id | Сенс | Было | Стало |
|:--|:--|:--|:--|
| `agni:A:2iii` | 2iii · āhavanīya | ахаванья (огонь для возлияний) | ахавания (огонь для возлияний) |
| `agni:A:3x` | 3x · as hotṛ | как хотар (жрец-возливатель) | как хотар (жрец-призыватель, рецитатор) |
| `agni:A:4vi` | 4vi · rite of preparing the fire-altar | обряд сооружения алтаря огня | обряд сооружения алтаря огня (агничаяна) |
| `agni:A:13` | 13 · a mental disposition | душевное состояние | склад ума, умонастроение |
| `agni:A:25xiv` | 25xiv · of the udātta | (божество) удатты (высокого тона) | (божество) удатты (повышенного тона, акута) |
| `agni:B:6vi` | 6vi · jāra | джара | джара (растение; PD listing — сверить источник) |
| `agni:B:25iv` | 25iv · of Vyāhṛtis | вьяхрити | (божество) Вьяхрити (сакральных возгласов bhūr bhuvaḥ svaḥ) |
| `agni:B:25vi` | 25vi · of a syllable of the mantra for Viṣṇu | слога мантры Вишну | (божество) слога мантры Вишну |
| `agni:B:26viii` | 26viii · a group of Bhavanavāsin gods | группа богов Бхаванавасин | группа богов Бхаванавасин (класс божеств-«обитателей дворцов», джайн./пуран.) |

### Carriers touched — the RU gloss lives in four places, not one

The sheet's own routing note names only `<w>.pd-min.ru.md` col. 3. That file alone is
**not** enough: the RU column is regenerated from a hardcoded `GLOSS` dict, so an edit
confined to the markdown silently reverts on the next build. All four carriers moved in
this pass:

| File | Role | Rows moved |
|:--|:--|:--|
| [article-comparison/agni.pd-min.ru.md](https://github.com/gasyoun/SanskritLexicography/blob/master/article-comparison/agni.pd-min.ru.md) | canonical bilingual skeleton, col. 3 | 9 |
| [article-comparison/agni.persense-ru.md](https://github.com/gasyoun/SanskritLexicography/blob/master/article-comparison/agni.persense-ru.md) | per-sense view (col. 3; corpus col. 4 untouched) | 9 |
| [RussianTranslation/src/_build_agni_ru.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_build_agni_ru.py) | `GLOSS` dict — regeneration source | 9 |
| [article-comparison/gloss_review_items.json](https://github.com/gasyoun/SanskritLexicography/blob/master/article-comparison/gloss_review_items.json) | sheet manifest — verdict stamped on all 11 | 11 |

## Rejected (1) — never re-surface unless the data changes

**`agni:A:4i`** — 4i · fire-altar. Cell stays **жертвенный алтарь (агничаяна)**.

Voter ruling: PD is an authoritative source; *fire-altar* maps one-to-one onto
«жертвенный алтарь», and the Cyrillic Sanskritism spoils nothing — it helps. The
proposed «жертвенный алтарь огня» is not idiomatic Russian (checkable against the
corpus and against ordinary usage).

This overrules the sheet's own H-severity rationale (that `agnicayana` is the rite,
not the altar, so the gloss belonged only at 4vi) and the Sonnet 5 (claude-sonnet-5)
source-check verdict recorded in the manifest as `spot_check: true`. Per
`/decisions-apply` this row is closed: it must not be re-presented in a future sheet
round unless the underlying PD text or the RU cell itself changes.

**Residual, stated rather than implied:** 4i and 4vi were minted as a *paired* edit —
move «агничаяна» from 4i to 4vi. The vote split the pair (4i reject, 4vi approve), so
«агничаяна» now stands in **both** cells. That is the voted outcome, not an application
error, and it is defensible (4i keeps the reader's anchor, 4vi names the rite the PD
gloss actually denotes). Flagged here so a later reader does not read it as a duplicate
to be cleaned up silently.

## Deferred (1) — returns to the queue

**`agni:A:14`** — 14 · a synonym of kleśa. Cell stays **синоним клеши (страдания)**;
the proposed «синоним клеши (аффекта/омрачения)» is held.

Voter note: take Paribok's wording from the transcripts of the first 16 Yoga-sūtra
classes into account before settling this. `deferred 15-08-2026` stamped in the
manifest so the next sheet round re-presents it.

> Source for the deferral: the Yoga-sūtra class transcripts under `Uprava/stenogrammy/`
> — personal-data-bearing, never exported. Whoever resolves this reads them in place.

## Open questions raised in voter notes (not blocking, not lost)

| id | Note | Status |
|:--|:--|:--|
| `agni:B:6vi` | «растение какое?» — which plant is *jāra*? | Applied gloss says «PD listing — сверить источник»; the species is still unidentified. Needs a PD verbatim check against the sense-6 plant list. |
| `agni:B:25iv` | «вьяхрити или Вьяхрити? В оригинал с заглавной буквой» | Resolved in application: PD prints *Vyāhṛtis* capitalised, so the applied cell reads **Вьяхрити**. |
| `agni:A:3x` | «Надо еще учесть данные книги Д. Н. Овсянико-Куликовского про огненный ритуал» | Approved edit applied as voted; Ovsyaniko-Kulikovsky's fire-ritual material is a follow-up enrichment, not a correction to the applied text. |

## Sheet disposal

The gitignored local copy
`SanskritLexicography/review/sanskritlexicography-article-comparison_agni_review.html`
is removed (MG ruling 16-07-2026 — a voted sheet next to live ones invites accidental
re-voting). The published hub copy at
[gasyoun.github.io/vote/sheets/gloss_agni.html](https://gasyoun.github.io/vote/sheets/gloss_agni.html)
is marked decided in the hub index rather than deleted. Either is reproducible:
`python article-comparison/_build_gloss_review_sheets.py`.

_Dr. Mārcis Gasūns_
