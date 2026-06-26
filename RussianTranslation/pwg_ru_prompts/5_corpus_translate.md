# pwg_ru — stage 5: corpus-first per-sense translation (LOCKED)

The production translate prompt for the corpus-first pipeline (Sonnet 4.6 on Max).
Embedded in [src/pilot/run_pilot_wf.js](../src/pilot/run_pilot_wf.js); this file is
the canonical, reviewable version. Validated on the 15-card a-section pilot
(13/15 publishable, 15/15 sigla, strong discrimination) + the Nachträge guard;
hardened 2026-06-26 with the four judge-derived nits from the 38-unit freq test.

## Conventions (from Böhtlingk-Roth's own prefaces + project decisions)

- **Register:** scholarly-philological. Faithful to PWG's density and precision.
- Translate into Russian **only the German gloss prose**.
- **Keep verbatim** (never translate/transliterate): Sanskrit (IAST/Devanāgarī);
  literary-source sigla (ṚV., MBH., M., AK., H., …); German grammatical
  abbreviations (m., f., n., Pl., Du., adj., …); German lexicographic/meta
  abbreviations inside `<ab>…</ab>` (**Bed.** = Bedeutung, **Schol.**, s.v., u.s.w.)
  — keep the token, **never** expand it to its Russian meaning; and `<is>…</is>`
  italic source text — a source/siglum reference, kept verbatim, **never** treated
  as `{%…%}` German gloss to translate.
- **Two-source principle:** a sense backed by a TEXT citation = *attested*
  demonstrable usage; a sense from a kośa/grammarian only (AK, H, P, Med.) =
  Indian-lexicographic → `source_type=lexicographic`.
- **Vedic** senses are 19th-c. European philology, possibly superseded; render
  faithfully; keep the German's own hedges.

## Task

For each record (homonym) and each sense/sub-sense in the tree, write the Russian:
- Use the **corpus candidates as primary evidence** for word choice (attested,
  ~84% precision, translation-weighted). Where several near-synonyms fit,
  **discriminate à la Apresjan** — pick the right one(s) for *this* sense and state
  the differentia (semantic / combinatorial / stratum-connotational). Prefer the
  sense's **cited stratum** (a ṚV-cited sense → the Vedic corpus renderings).
- Mark `equivalence_type`: a 1–2 word equivalent vs an explanatory gloss (толкование).
- Side-by-side: keep the German sense beside the Russian.

## Hard rules (the judge fails the card otherwise)

1. **No fabrication** — never output a sense/sub-sense/tag absent from the raw
   German; tags must match the raw; do not invent/split/merge senses.
2. **Complete coverage** — render every numbered + lettered sense AND every
   etymology / cross-reference / "personif." note. Skip nothing.
3. **Sigla untouched** — no siglum or abbreviation translated, *including
   commentator sigla* (Sāy., Schol., Sch., Comm.) and German lexicographic/meta
   abbreviations inside `<ab>…</ab>` (**Bed.**, Schol., s.v.): keep the abbreviation
   token verbatim, **never expand it** (the judge caught `<ab>Bed.</ab>` → «значением»).
   `<is>…</is>` italic source text stays a verbatim siglum — **never** `{%…%}` gloss
   (the judge caught `<is>` rendered inside `{%…%}` on idam). No German/English word
   leaks into the Russian.
4. **All records, including Nachträge** — a headword is often a MAIN record plus
   ADDENDA/NACHTRÄGE that *patch* it ("to sense 3 add X"; "sense 10: read … instead
   of …"; an etymology tail; a new astrological/numeric sense). Render every record
   and every addendum **in full, including its tail**; addenda are first-class; key
   each to the main-entry sense number it patches. One addendum can itself carry
   **several** numbered patch-items (1a, 2a, 3a…) — render **every** one; dropping any
   fails coverage (the judge caught kārya dropping 2: 1a ṚV.PRĀT 14,16; 2a Spr. 3008).

## Stage 6 — Opus judge rubric

Fail/score the card on: (1) Russian correctness vs the German; (2) scholarly
register; (3) sigla + grammar abbrevs verbatim; (4) per-sense Apresjan
discrimination quality (real differentiae, not a flat list); (5) corpus evidence
used; (6) coverage — every sense + every Nachträge record. severity 1 =
publishable … 5 = broken; `ok` + sev ≤ 2 → publishable, else → the human queue.

## Audit gate (deterministic, post-translation)

`run_real_test.py audit wf_output.json` runs `nws_split.py check` on every card: a
card whose NWS owners disagree with the deterministic owner parse (the F12 slide,
e.g. idam swapping Geldner↔Graßmann) is **rejected** — its `.merged.md` is moved
aside to `.merged.REJECTED.md` and re-queued, and the audit exits non-zero. Keep
this gate in the scale loop (it is the deterministic backstop the lone sev-3 needs).
