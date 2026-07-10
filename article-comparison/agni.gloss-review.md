# agni — review of the hand-authored RU sense-glosses (draft pass for sign-off)

**What this is.** An agent (Opus 4.8, 2026-06-25) editorial pass over the **130
hand-authored Russian sense-glosses** in [`agni.pd-min.ru.md`](agni.pd-min.ru.md),
checked against the English PD sense, the Sanskrit term, and Russian Indological
convention (Kochergina; Elizarenkova for Vedic terms). **No gloss was changed** —
this is a proposal list for a human editor (M.G.) to accept/reject. The skeleton
itself still says _«Переводная часть — черновая, требует сверки»_; this closes that
loop with concrete, reviewable edits.

**How to sign off.** For each row put a decision in the `✓/✗` column (accept / reject
/ alter). Accepted edits then get applied to `agni.pd-min.ru.md` col. 3 (and, where the
gloss feeds it, re-run `_build_skeletons_ru.py`). Severity: **H** = factual/category
error, **M** = norm/precision, **L** = optional polish, **FYI** = PD-source defect (no
RU action).

**Headline.** Of 130 glosses the draft is largely sound. **1 factual category error**
(sense 4i ↔ 4vi, the agnicayana mislabel), **3 transliteration/precision** fixes, and a
handful of optional add-glosses. The English-source OCR typos (ghoe, Semicarpu, akind…)
were already silently corrected by the Russian translator — noted as FYI, no RU change.

---

## A. Substantive proposals

| ✓/✗ | Sense | English (PD) | Current RU | Proposed RU | Sev | Why |
|:--:|:--|:--|:--|:--|:--:|:--|
|  | **4i** | fire-altar | жертвенный алтарь (агничаяна) | жертвенный алтарь огня (citi / agnikṣetra) | **H** | **Category error.** *agnicayana* is the **rite** of piling the altar, not the altar. The altar is *citi/agnikṣetra*. The "агничаяна" tag belongs on 4vi, not here. |
|  | **4vi** | rite of preparing the fire-altar | обряд сооружения алтаря огня | обряд сооружения алтаря огня (агничаяна) | **M** | This *is* agnicayana — move the term here from 4i. Pairs with the fix above. |
|  | **2iii** | āhavanīya | ахаванья (огонь для возлияний) | ахавания (огонь для возлияний) | **M** | Transliteration norm: *āhavanīya* → **ахавания** (Kochergina), not "ахаванья". The soft-sign form is non-standard. |
|  | **3x** | as hotṛ | как хотар (жрец-возливатель) | как хотар (жрец-призыватель, рецитатор) | **M** | *hotṛ* is the invoker who **recites** the ṛcas (Elizarenkova: хотар); the manual pouring is the *adhvaryu*'s role. "Возливатель" misassigns the function. |
|  | **14** | a synonym of kleśa | синоним клеши (страдания) | синоним клеши (аффекта/омрачения) | **L** | In the yoga/abhidharma register *kleśa* is an **affliction/affect** (аффект, омрачение), wider than "страдание". |
|  | **13** | a mental disposition | душевное состояние | склад ума, умонастроение | **L** | "Disposition" = settled cast of mind (склад/умонастроение); "душевное состояние" reads as a transient *state*. |
|  | **25xiv** | of the udātta | (божество) удатты (высокого тона) | (божество) удатты (повышенного тона, акута) | **L** | *udātta* is the **raised** accent (акут); "высокого тона" is loose. |

## B. Optional add-glosses (transliteration-only cells that could carry a hint)

| ✓/✗ | Sense | English (PD) | Current RU | Proposed addition | Sev |
|:--:|:--|:--|:--|:--|:--:|
|  | **6vi** | jāra | джара | джара (растение; PD listing — сверить источник) | **L** |
|  | **25iv** | of Vyāhṛtis | вьяхрити | (божество) вьяхрити (сакральных возгласов *bhūr bhuvaḥ svaḥ*) | **L** |
|  | **26viii** | a group of Bhavanavāsin gods | группа богов Бхаванавасин | …Бхаванавасин (класс божеств-«обитателей дворцов», джайн./пуран.) | **L** |
|  | **25vi** | of a syllable of the mantra for Viṣṇu | слога мантры Вишну | (божество) слога мантры Вишну | **L** (parallel to siblings 25ii–v that keep "(божество)") |

## C. FYI — English PD-source defects already corrected in the RU (no RU action)

These are OCR/typo artifacts in the **English** PD column; the Russian gloss is already
correct. Flag them upstream to the PD source if desired, but the RU needs nothing.

| Sense | English (PD), as printed | RU (already correct) |
|:--|:--|:--|
| 3iii | with **ghoe** as food etc | вкушающий гхи (топленое масло) |
| 6iv | **Semicarpu sanacardium** | Semecarpus anacardium |
| 24 | **akind** of earthquake | разновидность землетрясения |
| 25x | **de- ified** types of fires | обожествленные виды огней |
| 16ii / 19 | **Kuṇḍa- linī** / **Hiraṇya- garbha** (hyphen artifacts) | Кундалини / Хираньягарбха |
| 2iv | dakṣiṇāgni **v** sacrificial fire… (stray "v") | дакшинагни; жертвенный огонь… |

---

## Coverage note

- **130/130 glosses reviewed.** ~118 accepted as-is (clean), **7 substantive proposals**
  (1 H, 3 M, 3 L), **4 optional add-glosses**, **6 FYI source-typos**.
- The transliteration of theonyms/technical terms (Джатаведас, Вайшванара, Свиштакрит,
  Хираньягарбха, Криттика, саптарши, ратхантара, …) is consistent and standard — no
  changes proposed there.
- This artifact is the **agent-doable half** of the Track B gloss review. The remaining
  half — final scholarly **sign-off** on these proposals — is the human step.
