# RU_STYLE_MECHANICAL.md — mechanical Russian-output style rules (no-ё, terse metalanguage)

_Created: 19-07-2026 · Last updated: 19-07-2026_

Handoff: [H1305](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1305-Sonnet_RussianTranslation_pwg-ru-style-mechanical-yo-terseness-sweep_19.07.26.md)
· Model: Sonnet 5 (`claude-sonnet-5`) · Register:
[H178_DA_VOTE_ISSUE_REGISTER_2026-07-19.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H178_DA_VOTE_ISSUE_REGISTER_2026-07-19.md)
(rows N7, N12 + the terseness half of N4; §3, §4, §6). Fan-out of
[H1300](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1300-Fable_RussianTranslation_h178-da-vote-processing_19.07.26.md).
Sibling streams NOT in scope here: `<ab>` abbreviation ratification is
[H1303](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1303-Fable_RussianTranslation_pwg-ru-abbrev-unified-list-ratification_19.07.26.md),
German prose residue is
[H1302](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1302-Opus_RussianTranslation_pwg-ru-german-residue-sweep-reject-repair_19.07.26.md),
research-grade style rulings (doublets, Apresyan) are
[H1306](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1306-Fable_RussianTranslation_pwg-ru-style-research-doublets-apresyan_19.07.26.md).

## What this is

This is the *mechanical, rule-clear* Russian style stream: four deterministic, ratified
rules applied to the `ru` field of the canonical pwg_ru store, wired as a prompt HARD RULE
for future generation, and enforced by a new `ru_style` audit gate. Implementation:
[`src/ru_style_sweep.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ru_style_sweep.py)
(the sweep + the shared violation detector).

## Voted evidence

Verbatim from the 19-07-2026 DA-sheet vote (`h178_da.decisions.json` per-card notes,
local-only), as recorded in register §3:

- **N7** — card `ji|ji~~h0_zz_sch|6`:
  > отвоёвывать - никаких ё - нигде, кроме как для разграничения все и всё
- **N4** (terseness half; the `fg.`/abbreviation half is H1303) — card `vid|vid~~h0_10_ni|3`:
  > вместо слово длинное, достаточно вм.
  > `<ls>ed. Bomb.</ls>` = Бомбейская ред.
- **N12** — card `nI|n_i~~h0_zz_pw01|PW-prefix-T4`:
  > в значении, достаточно в знач.

## The rules

| id | rule | scope |
|---|---|---|
| **R1** | no letter ё anywhere in RU output — write е everywhere | whole `ru` field, whitelist below |
| **R2** | «вместо» → «вм.» | editorial metalanguage (measured unrestricted, see below) |
| **R3** | «в значении» → «в знач.» | editorial metalanguage (measured unrestricted, see below) |
| **R4** | `ed. Bomb.` → «Бомбейская ред.» | free prose ONLY, outside any `<ls>…</ls>` span |

**R1 — no-ё whitelist.** Exactly the standalone token «всё»/«Всё» (regex `\bвсё\b`
conceptually, implemented as `(?<![а-яёА-ЯЁ\-])[Вв]сё(?![а-яёА-ЯЁ\-])` so it never leaks
into a longer word or a hyphenated compound), per MG's ruling: «никаких ё — нигде, кроме
как для разграничения все и всё». **Edge case «всё-таки» etc.: defaults to е** («все-таки»)
per the ruling — the whitelist regex explicitly excludes anything immediately followed or
preceded by a hyphen, so a hyphenated compound is never mistaken for the standalone word.
**Measured**: 0 «всё-таки»-shaped occurrences exist in the current store (the edge case is
real per the ruling but had zero live instances to sweep); the regex still guards it
defensively for future content.

## False-positive measurement (BEFORE apply — the judgment call)

Extracted every occurrence of «вместо», «в значении», and `ed. Bomb.` from the RU field of
the canonical store (11,603 rows) and hand-classified metalanguage vs. quoted/translated
prose, per the handoff's ≥50-sample / ≤2%-threshold instruction.

| pattern | total occurrences | sample checked | prose (false-positive) | verdict |
|---|---:|---:|---:|---|
| «вместо» | 291 | 60 (random, seed 1305) | **0/60 (0%)** | unrestricted sweep (R2) |
| «в значении» | 24 | 24 (100%, small population) | **0/24 (0%)** | unrestricted sweep (R3) |
| `ed. Bomb.` | 283 | 283 (100%, markup-classified) | see split below | prose-only sweep (R4) |

**«вместо» (291 occurrences).** Every sampled hit is editorial apparatus — overwhelmingly
the fixed pattern «ошибочно/неточно/вероятно вместо X» ("read X instead of Y is an error";
42/60 carry an explicit error marker), plus other apparatus uses (case-government notes
like «Вместо <ab>Dat.</ab> также <ab>Instr.</ab>», corrigenda «читать n. вместо m.»,
variant-reading notes «<ab>v. l.</ab> вместо {#X#}») — **never** ordinary narrative prose
describing real-world meaning. 0% measured false-positive rate is well under the handoff's
~2% restriction threshold, so R2 applies to every occurrence unrestricted (no `{%…%}`
context gating needed).

**«в значении» (24 occurrences, full population checked).** Every occurrence is the
editorial sense-specification idiom («X в значении Y», "X in the sense of Y" / "X used to
mean Y") — the exact pattern N12's vote targeted. 0% false positives; R3 applies unrestricted.

**`ed. Bomb.` (283 occurrences) — markup split, not a prose-vs-metalanguage split.**
Every occurrence sits either standalone or embedded inside an `<ls>…</ls>` citation span,
except one:

| population | count | disposition |
|---|---:|---|
| standalone `<ls>ed. Bomb.</ls>` | 221 | **left verbatim** — see placement check below |
| embedded in a longer citation, e.g. `<ls>R. ed. Bomb. 3,69,4</ls>` | 61 | **left verbatim** — see placement check below |
| free prose outside any `<ls>…</ls>` (e.g. `<ls>Mālatīm.</ls> (ed. Bomb.) 304,1.`) | 1 | **swept** (R4 applied) |

## `ed. Bomb.` placement check (handoff step 5)

[`src/pwg_sources.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_sources.py)
resolves every `<ls>` citation against PWG's own bibliography
(`pwgauth/pwgbib.txt`) by extracting the citation's leading Latin token(s)
(`source_key()`, up to 4 words, stopping at the first digit) and looking that key up
(`resolve()`) — the bibliography is keyed entirely in Latin/German, no Cyrillic entries
exist. Rewriting `<ls>ed. Bomb.</ls>` → `<ls>Бомбейская ред.</ls>` (standalone) or
`<ls>R. ed. Bomb. 3,69,4</ls>` → `<ls>R. Бомбейская ред. 3,69,4</ls>` (embedded) would
change the exact key `source_key()` extracts and **break source resolution outright** —
confirmed by inspection of `pwg_sources.resolve()`, not merely suspected. Per the handoff's
decision rule, the store-level substitution therefore applies **only to the 1 free-prose
occurrence**; the 282 in-`<ls>` occurrences (221 standalone + 61 embedded) stay verbatim
Latin at the store level. Their eventual Russian *display* (e.g. rendering `<ls>ed.
Bomb.</ls>` as «Бомбейская ред.» at render time while keeping the underlying citation text
resolvable) is a render-time display-layer concern, not a store-sweep — handed off as a
PROPOSED follow-up (see below); it is NOT part of
[H1307](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1307-Opus_RussianTranslation_pwg-ru-ls-link-enrichment-panini-spr-dhatup_19.07.26.md)'s
shipped scope (that handoff covers Panini/Spr./DHATUP link enrichment specifically, not
`ed. Bomb.` display) — a future handoff should pick this up explicitly.

## Sweep results (applied)

Ran [`src/ru_style_sweep.py --apply`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ru_style_sweep.py)
against the canonical store (backup verified row-count-match before apply, per the
handoff's prerequisite 2):

| rule | substitutions | rows touched |
|---|---:|---:|
| R1 no-ё | 1,713 | (of 1,485 total touched rows) |
| R2 «вместо»→«вм.» | 291 | |
| R3 «в значении»→«в знач.» | 24 | |
| R4 `ed. Bomb.` (prose only) | 1 | |
| **total substitutions** | **2,029** | **1,485 distinct rows** |

**Store row count: 11,603 → 11,603 (unchanged, as required — content-only edit).**
Re-running the auditor (`python src/ru_style_sweep.py`, dry-run) after `--apply` reports
**0 residual violations** across all four rules — the sweep is idempotent (each
substitution's output contains none of its own trigger pattern: «вм.» contains no
«вместо», е-forms contain no ё, «Бомбейская ред.» sits outside `<ls>`, «в знач.» contains
no «в значении»).

## PROPOSED candidates (routed to H1306 / MG, NOT applied here)

Per the handoff's scope fence, mining
[`src/pwg_ab_ru.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ab_ru.py)'s
editorial bucket (`RU_MAP`) and
[ABBREVIATIONS_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md)
for further terse-form precedent surfaced no additional store-wide long-metalanguage
candidates beyond R1–R4 that meet the same "ratified + unambiguous" bar — R2/R3/R4 were
already the full set of terseness items the DA vote (N4/N12) ratified. The applied set
stays exactly R1–R4. Two items are explicitly OUT of this session's scope and are
listed here for the sibling streams that own them:

- **In-`<ls>` `ed. Bomb.` display substitution** (282 occurrences) — a render-time
  display-layer concern, not mined/ratified here; needs its own handoff (see placement
  check above).
- **Doublet / v.l. / Comp.-formula terseness** — research-grade (not mechanical), explicitly
  routed to [H1306](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1306-Fable_RussianTranslation_pwg-ru-style-research-doublets-apresyan_19.07.26.md)
  per the register.

## Future-generation compliance

- **Prompt HARD RULE 9** added to the `CONV`/`TR` template in
  [`src/pilot/run_pilot_wf.js`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/run_pilot_wf.js)
  states R1–R4 for the model. `gen_opt_harness2.py` extracts `TR` directly from this file
  by regex (`extract_conv_tr()`), so every future-generated optimized harness inherits the
  rule automatically — no separate derivative to keep in sync (verified by direct
  extraction, `'NO LETTER Ё' in tr` / `'«вм.»' in tr` / `'«в знач.»' in tr` /
  `'Бомбейская ред.' in tr`, all true).
- **Pinned** in
  [`src/pilot/prompt_rule_audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/prompt_rule_audit.py)'s
  `RULES` list as `ru_style_no_yo` / `ru_style_terse_metalanguage` / `ru_style_ed_bomb_siglum`
  — a future template edit that drops HARD RULE 9 fails `--fail-on-missing`.
- **`ru_style` audit gate** added to
  [`src/pilot/audit_window.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py)'s
  RU gate commands (alongside `translation`/`stage2_mechanical`/`coverage`/`sense_dupes`),
  reading the same `.merged.md` rendered output; reuses
  `ru_style_sweep.scan_violations()` verbatim (the sweep detector and the gate detector can
  never drift — one function, two callers). Tests in
  [`src/pilot/window_selftest.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_selftest.py)
  (`test_h1305_ru_style_mechanical`) cover: ё-word flagged, «всё»/«Всё» passes clean,
  «всё-таки» edge case correctly flagged (not whitelisted), metalanguage «вместо»/«в
  значении» flagged, in-`<ls>` `ed. Bomb.` (standalone and embedded) never flagged, a
  genuine free-prose `ed. Bomb.` flagged.
- **RU-only, never wired into `audit_window_en.py`** — see the
  [LANG_PARITY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md)
  `ru_style_mechanical_yo_terseness` INTENTIONAL-DIVERGENCE entry.

## Verification (this session)

- `python src/ru_style_sweep.py --selftest` — PASS (fixture rows: «отвоёвывать»→
  «отвоевывать», «всё» preserved, «всё-таки» edge case defaults to е, metalanguage
  «вместо»/«в значении» tersed, standalone AND embedded `<ls>ed. Bomb.</ls>` left verbatim,
  free-prose `ed. Bomb.` translated, idempotence).
- `python src/ru_style_sweep.py` (dry-run, post-apply) — **0 residual violations**.
- `python src/pilot/window_selftest.py` — **150/150 passed, 0 failed** (green, including
  the new `test_h1305_ru_style_mechanical`).
- `python src/pilot/prompt_rule_audit.py --fail-on-missing` — **PASS**.
- `python src/pilot/lang_parity_check.py` — **59 entries, all verdicts complete, no
  drift** (the new `ru_style_mechanical_yo_terseness` entry, plus 38 pre-existing entries
  re-affirmed after this session's additive edits to `window_selftest.py` /
  `audit_window.py` / `prompt_rule_audit.py` drifted their tracked sha256 — every
  re-affirmed entry's described behavior was unmodified by these edits, so each was
  re-snapshotted per the ledger's Case-C policy, not re-verdicted).

_Dr. Mārcis Gasūns_
