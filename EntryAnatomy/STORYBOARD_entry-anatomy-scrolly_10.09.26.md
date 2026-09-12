# Storyboard — EntryAnatomy scrollytelling tour «Как читать словарную статью»

_Created: 10-09-2026 · Last updated: 10-09-2026_

**Source of truth:** [EntryAnatomy/](https://github.com/gasyoun/SanskritLexicography/tree/master/EntryAnatomy) —
`build_entry_anatomy.py` emits self-contained HTML + print PDF from one callout set
([README](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/README.md)) ·
**Template:** [SCROLLYTELLING_STORYBOARD_TEMPLATE.md](https://github.com/gasyoun/Uprava/blob/main/docs/SCROLLYTELLING_STORYBOARD_TEMPLATE.md)
**Status:** awaiting MG read. Host decision (Docusaurus guide page vs standalone HTML) recorded in the build handoff.

## Goal

Turn the static specimen sheets into a guided scroll: reveal one annotation layer at a time (callout-by-callout)
so a learner reads a PWG/MW entry the way a lexicographer does. Digital record layer (`<L>…<LEND>`) bridges
the print and the CDSL text. One source (callout JSON) must drive HTML and PDF — never two hand-kept outputs.

## Constraints

1. Build only from committed callout JSON / `--markup` specs; the PDF stays the final frame of the same data.
2. Rights: Cologne scans display-permitted; the **Duden plate is internal-only** — never on a public page
   ([publish-safety-check](https://github.com/gasyoun/claude-config/blob/main/commands/publish-safety-check.md) before publish).
3. No new JS dependencies; scrolly is a progressive layer over the existing self-contained HTML engine
   (which already measures layout for `@page`).
4. Print contract unbroken: `chrome --headless --print-to-pdf` output unchanged after the scrolly layer.

## Beats

| # | Beat / claim | Scroll trigger | Visual | Feed (committed) | Text | Fallback | Reduced motion | Analytics goal | QA check | Rights / PII | Owner |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | «Статья — это не текст, а слои» | section enter | full PWG entry, unannotated | `pwg-entry-anatomy.html` data | 2 sentences | static entry | static | `scrolly_anatomy_1` | page renders no-JS | Cologne display-permitted | build agent |
| 2 | «Форма: хомографы и деванагари» | callouts 1–n highlight sequentially | callout labels + leader lines (headword/homograph layer) | callout JSON (PWG) | label text verbatim from JSON | all callouts pinned at once | static pinned | `scrolly_anatomy_2` | label↔target binding test | Cologne | build agent |
| 3 | «Смысл: глоссы и цитаты» | next callout group | sense/gloss/citation layers | callout JSON | verbatim | pinned | static | `scrolly_anatomy_3` | spot-check 3 callouts vs print | Cologne | build agent |
| 4 | «Цифровой слой: `<L>`-запись» | section enter | CDSL record vs rendering side-by-side | [`cdsl-record-anatomy.html`](https://github.com/gasyoun/SanskritLexicography/blob/master/EntryAnatomy/cdsl-record-anatomy.html) | key1/key2, `<ls n=…>` explanation | static columns | static | `scrolly_anatomy_4` | XML snippet diff vs csl-orig | Cologne | build agent |
| 5 | «Один и тот же материал: PWG ↔ MW» | toggle/steps | same lemma family (heman/gup) in both traditions | two committed specimens | 2 sentences | static side-by-side | static | `scrolly_anatomy_5` | both pages built from same pipeline | Cologne; Duden excluded | build agent |

## Mechanics

1. Extend `build_entry_anatomy.py` with a `--scrolly` emission path that wraps the existing sheet in
   step containers; callouts get `data-step` from the JSON order. No forked template.
2. Vanilla `IntersectionObserver`; CSS `sticky` for the specimen panel; no external libraries.
3. `prefers-reduced-motion` / no-JS → the already-correct static sheet (callouts all visible, navigation works).
4. Host decision + analytics: if standalone (GitHub Pages), use a lightweight counter or accept
   “unmeasured — accepted”; if Docusaurus (csl-guides), no tracker (scholar site) — state it.

## QA

1. Rebuild both outputs; PDF byte-comparable layout (page count unchanged).
2. Link/callout integrity test: every JSON callout resolves to a target.
3. Headless screenshots desktop + mobile; print-to-pdf smoke.
4. `publish-safety-check` verdict recorded before any public hosting.

## Gates

1. **MG storyboard read** — this file.
2. **Rights** — Duden never public; Cologne scans display-permitted only.
3. Host decision recorded (csl-guides vs standalone) with rationale in the build handoff.

## Out of scope

New specimens beyond the committed exemplars; Duden re-publication; PDF redesign.

_Dr. Mārcis Gasūns_
