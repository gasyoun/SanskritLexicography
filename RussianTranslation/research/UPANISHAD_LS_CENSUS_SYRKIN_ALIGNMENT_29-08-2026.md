# Upaniṣad `<ls>` citations in the pwg_ru store, and where Syrkin actually stands

_Created: 29-08-2026 · Last updated: 29-08-2026_

Measured by Opus 5 (`claude-opus-5`) against the live store at 11 519 rows, prompted by the
question "if `U.` is for Upanishads, have we aligned Syrkin's Russian translation to see what it
has?" — asked off the `jar_ayu` card produced by
[H3663](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H3663-Opus_SanskritLexicography_h3658-residual-lane-a-16key-c1-window_29.08.26.md).

## 1. The abbreviation in that card is not an Upaniṣad

`jar_ayu` carries `<ls>Uṇ. 1,4</ls>` directly after `(von 1. {#jar#})` — a derivation note. In
PWG that is the **Uṇādisūtras**, a grammatical text, not an Upaniṣad. The Upaniṣad references are
spelled `UP.` (`<ls>CHĀND. UP. 3,19,2</ls>`, also present in the same card). Three separate
abbreviations are in play and only one is an Upaniṣad:

| token | reads as | occurrences in the store |
|---|---|---:|
| `UP.` | Upaniṣad (always prefixed by the work) | **820** |
| `Uṇ.` | Uṇādisūtra | **4** |
| `U.` | *does not occur as a standalone `<ls>` source* | 0 |

Neither token resolves through repo data: `pwg_ab.py` covers `<ab>` abbreviations, not `<ls>`
sources, and [`ls_source_map.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_source_map.json)
holds only 45 entries with **no Upaniṣad among them**. The `Uṇ.` reading above is inferred from
the citation's position and shape, not verified against a source table — that table does not
exist yet, and building one is the prerequisite for any automated Upaniṣad routing.

## 2. The citation surface is small but concentrated

**820 `UP.` references across 314 store rows**, out of **82 957** `<ls>` references in total —
about **1 %** of the citation surface, touching ~2.7 % of rows.

| work | refs |
|---|---:|
| Chāndogya | 312 |
| Muṇḍaka | 70 |
| Bṛhadāraṇyaka (`BṚH. ĀR. UP.` + `… S.` + `… p.`) | 108 |
| Śvetāśvatara | 66 |
| Kauṣītaki | 56 |
| Taittirīya | 44 |
| Aitareya | 18 |
| Nṛsiṃhatāpanīya | 18 |
| Weber, Rāmatāpanīya | 14 |

The concentration matters more than the total: Chāndogya alone is 38 % of it, and the principal
Upaniṣads — exactly Syrkin's corpus — account for the large majority.

## 3. Syrkin is MINED, not ALIGNED

Both facts are already in the repo and they answer the question in opposite directions:

* **Mined.** `syrkin_tom_1_utf` is a source in the running-text mining pipeline
  ([`pwg_ru/RUNNING_TEXT_MINING.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/RUNNING_TEXT_MINING.md)),
  classified "running scholarly prose, terms scattered — lower, noisier" yield: **41 term-bearing
  rows, 35–36 useful**. That harvests Russian *equivalents for terms*; it does not tell you what
  Syrkin says at a given passage.
* **Not aligned.** [`REUSE_MAP.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/REUSE_MAP.md)
  records **Track A BLOCKED** — "none of MG's ~12 parallel texts exist in verse-aligned jsonl".
  Passage-level lookup (`CHĀND. UP. 3,19,2` → Syrkin's Russian) is precisely Track A, and it has
  never been built.

So: **no, we have not aligned it.** What exists is a low-yield prose mine over one volume. The
thing the question is really after — opening a card's Upaniṣad citation and reading the canonical
published Russian rendering beside the AI one — does not exist.

One caveat already recorded in [FINDINGS](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md):
the «Syrkin» file set is not purely Syrkin — a non-Syrkin `jabala-up` (2025) was found inside it,
and two edition years were retired. Any alignment must census the file set before trusting its
label.

## 4. Why this is worth more than 1 % suggests

An Upaniṣad citation is one of the few places in PWG where a **canonical, published, citable
Russian translation already exists** for the exact passage. Everywhere else the RU column is the
only Russian there is. For those 314 rows a reviewer could compare against Syrkin instead of
adjudicating from the German alone — which is the cheapest quality signal available anywhere in
the store, and it lands on G5 review, not on generation.

The blocker is not the dictionary side. It is that Syrkin exists here as prose, not as
verse-addressed text, and `ls_source_map.json` cannot resolve `UP.` to a work in the first place.
Two concrete prerequisites, in order:

1. Extend `ls_source_map.json` to cover the nine Upaniṣads above, so `CHĀND. UP. 3,19,2` parses
   into (work, chapter, section, verse).
2. Convert the Syrkin volume(s) to verse-addressed jsonl — the Track A work that is currently
   blocked for all ~12 parallel texts, not just this one.

Neither needs a paid model window; both are deterministic text engineering.

_Dr. Mārcis Gasūns_
