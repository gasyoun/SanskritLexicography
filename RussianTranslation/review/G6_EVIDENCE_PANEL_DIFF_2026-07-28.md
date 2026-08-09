# G6 gold card — evidence panel: re-cut and diff (H1801)

_Created: 28-07-2026 · Last updated: 28-07-2026_

MG's ruling of 28-07-2026, after the first real G6 vote
([H1796](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1796-Opus_SanskritLexicography_g6-mqm-gold-starter-vote-apply_28.07.26.md)):
a gold card must carry the dictionary sense, the root and the corpus contexts
**before** the vote, not after it. «Это все надо давать ДО, а не ПОСЛЕ.»

Executed by Opus 5 1M (`claude-opus-5[1m]`) per
[H1801](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1801-Opus_SanskritLexicography_g6-gold-card-evidence-panel_28.07.26.md).

## What changed

| | before (`g6-mqm-gold-starter-2026-07-25`) | after (`g6-mqm-gold-starter-evidence-picker-2026-07-29`) |
|---|---|---|
| panels per card | 3 — Sanskrit, Russian, LLM label | 7 — + dictionary, root, contexts, ranked glossary |
| sheet size | 59 291 bytes | 139 797 bytes |
| cards / ids | 20 | 20, **identical ids** (same `pick()`, same `gold_set.jsonl`) |
| lock | untouched, votes stay validatable | new lock, new `sheet_id` |

The 20 ids are byte-identical between the two locks, so the diff isolates the
panel change: same rows, more evidence. The old sheet's votes are already
applied (H1796) and its lock is deliberately left in place.

**Merged with H1802.** The two H1796 follow-ups re-cut the same sheet within a
day of each other — [H1802](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1802-Sonnet_csl-pyutil_review-sheet-reject-label-picker_28.07.26.md)
added the required reject-label select control (so the note is rationale only,
never the carrier of the answer), H1801 the evidence panels. They are one
instrument, not two, so this generation carries **both**. H1802's picker-only id
`g6-mqm-gold-starter-reject-picker-2026-07-28` was never voted and is superseded
here; its lock stays on disk as a record.

Panels are built by
[`src/gold_evidence_panel.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/gold_evidence_panel.py)
and rendered between the Russian rendering and the LLM label — so the reviewer
reads the evidence before judging the label.

## Coverage over the 20 starter cards

| panel | cards with evidence |
|---|---|
| ranked Sa→Ru glossary (A2/A4) | **20 / 20** |
| period-routed dictionary sense | **16 / 20** |
| corpus contexts in the card's own work | **14 / 20** (+6 attested via glossary only) |
| root line | **8 / 20** |

Root coverage is the honest floor, not a defect to paper over: of the 12 cards
without one, `ikzvAkURAM` (Ikṣvāku) and `gARqIvam` (Gāṇḍīva) are proper names,
`te` and `na` are a pronoun and a particle — none has a dhātu. Chaining them to
a root anyway is exactly the fabrication [rule 4](#never-fake-completeness)
forbids; the panel prints what it searched instead.

## Per card

`root` names the source that produced it (DCS `lemma2root` · MW `mw_etymology` ·
PWG `pwg_etymology`), because the three disagree and the reviewer must see which
one is speaking. `contexts` gives the count and the match grade.

| id | form | period | work | dictionary | root | Whitney | contexts | Sa→Ru variants |
|---|---|---|---|---|---|---|---|---|
| 5 | `ikzvAkURAM` | Classical | raghuvamsha | MW `ikzvAku` | — | — | 1 (token) | 3 |
| 3 | `Kinna` | Classical | shatakatrayam-serebryakov | MW `Kinna` | √khid (DCS) | √khid "tear" | 1 (substring) | 11 |
| 6 | `puruza` | Epic/eC | bhagavadgita-erman | MW `puruza` | √pṝ (MW) | — | 3 (substring) | 171 |
| 9 | `gARqIvam` | Epic/eC | 05_mahabharata-udyogaparva | MW `gARqIva` | — | — | 2 (substring) | 12 |
| 4 | `saMsAra` | Medieval | gitarthasamgraha-abhinavagupta | MW `saMsAra` | √sṛ (MW) | √sṛ "flow" | 3 (substring) | 43 |
| 2 | `kftAYjali` | Medieval | gitarthasamgraha-abhinavagupta | MW `kftAYjali` | — | — | 2 (substring) | 52 |
| 0 | `yuvAnam` | Vedic | 01_rigveda | GRA `yuvan` | √yu (MW) | 1 √yu "unite" | 1 (token) | 5 |
| 1 | `grAmyAH` | Vedic | 03_atharvaveda | GRA `grAmya` | √grAma (PWG) | — | 2 (token) | 2 |
| 118 | `aruRAmSub` | Classical | raghuvamsha | — | — | — | glossary | 2 |
| 128 | `grAvan` | Classical | nyaya-bhashya | MW `grAvan` | — | — | glossary | 10 |
| 92 | `avAk-SAKaH` | Epic/eC | bhagavadgita-radha | MW `avAkSAKa` | — | — | glossary | 1 |
| 87 | `pramucyate` | Epic/eC | bhagavadgita-prabhupada | MW `pramuc` | √muc (DCS) | √muc "release" | 1 (token) | 19 |
| 105 | `kApAlike` | Medieval | hatha-yoga-pradipika | MW `kApAlika` | — | — | 1 (token) | 2 |
| 120 | `te` | Medieval | gitarthasamgraha-abhinavagupta | MW `tvad` | — | — | 3 (token) | 233 |
| 80 | `advaita` | Vedic | br-up | MW `advEta` | — | — | glossary | 5 |
| 122 | `na` | Vedic | 08_rigveda | GRA `na` | — | — | 3 (token) | 109 |
| 221 | `prAyaRa` | Classical | nyaya-bhashya | MW `prAyaRa` | √kṛ (MW) | 1 √kṛ "make" | 3 (substring) | 6 |
| 201 | `DvanisparSa` | Classical | nyaya-bhashya | — | — | — | glossary | 1 |
| 189 | `Danezin` | Epic/eC | manavadharmashastra | — | — | — | glossary | 1 |
| 224 | `titikz` | Epic/eC | bhagavadgita-burba | — | √titikz (DCS) | — | 1 (substring) | 11 |

## The five cards that motivated the ruling

**id 122 `na` → «словно», `08_rigveda`** — the label reversed at adjudication.
Vedic routing now serves Grassmann first, and Grassmann says it in the entry's
opening line: *«Verneinungswort, und zwar theils in strengem Sinne verneinend
„nicht", theils nur die eigentliche Bedeutung verneinend „wie, gleichwie,
gleichsam"»*. Under it sit three attested `08_rigveda` passages with their
published Russian, and the ranked glossary showing «как» 213× and «словно» 153×
against «не» 3543×. All four were withheld from the reviewer who was asked to
rule that «na это всегда нет, никогда не словно».

**id 3 `Kinna`** — «не говоришь от какого корня и что корень означает согласно
Whitney … не приводишь контексты». The card now carries MW *khinna mfn.
depressed, distressed, suffering pain*, the root √khid with Whitney's own gloss
"tear", and a `shatakatrayam-serebryakov` context.

**id 92 `avAk-SAKaH`** — «не видя контекста, а он у тебя есть, но отсутствует у
меня». The hyphenated scaffold key matched nothing until de-hyphenation; MW's
`avāk—śākha` *"having shoots turned downwards (as the Ficus Indica)"* is now the
first entry shown — the sense «с ветвями вниз» was being judged on.

**id 6 `puruza`** — «Недостаточно данных для однозначного ответа». 171 ranked
Russian renderings and three contexts now stand behind the card.

**id 1 `grAmyAH`** — «почему мы работаем не с основами, а формами падежей?». The
card still votes on the attested form, but the panel now shows the lemma
(`grAmya`), the dictionary entry under the stem, and the root line, so the form
is no longer the only thing on screen.

## Never fake completeness

Rule 4 of the handoff. Every panel returns the concrete list of what it looked
in, and a panel that found nothing prints `evidence not found: искали — …`. A
blank panel and an unsearched panel must not look alike; that
indistinguishability is what produced the low-information votes.

Three consequences, all visible on the sheet:

- **Context grades are shown, not flattened.** `token` (the form stands as a
  whole word) · `substring` (inside a sandhi/compound blob, only for forms ≥4
  characters, or `na` would match every second word) · `glossary` (the raw text
  search did not localize it, but the aligned corpus lexicon attests it in that
  work, with a count). Six cards sit at `glossary`, and say so.
- **Variant hits are labelled.** `advaita` is not a real SLP1 string — the
  scaffold's key never folded the `ai` digraph, and the MW headword is `advEta`.
  The lookup tries a small closed set of transcoding/segmentation variants and
  names the one that hit ("композит без дефиса", "+ ai/au → E/O"), so a variant
  hit can never read as an exact one.
- **Homographs are rejected out loud.** `na` resolves in DCS to six lemmas,
  among them the pronoun stem `mad` (the enclitic *nas* "us", 836×) beside the
  particle `na` (63 304×). Unfiltered, the panel served Grassmann's √mad
  *"wallen, sprudeln"* as a sense of `na` — a fabricated chain on the very card
  this work exists to fix. Candidates below 10 % of the top candidate's corpus
  count are dropped, and the rejects are still named in `searched`.

## Two defects found in the sources

1. **The gold scaffold's `slp1` field is not reliably SLP1.** It is the corpus
   aligner's token: `advaita` for `advEta` (the `ai`/`au` digraphs were never
   folded), `aruRAmSub` for a form whose anusvāra came through as `m`,
   `avAk-SAKaH` carrying a compound hyphen and a case ending. Four of the five
   dictionary misses traced to this, two are recovered by the variant layer, and
   `aruRAmSub` is not recoverable — it matches no headword in any of the three
   dictionaries and no token in `raghuvamsha`.
2. **The id in the H1796 provenance is wrong.** The commit message, the handoff
   and FINDINGS §499 all record the reversed card as "id 118 `na` →
   «словно», `08_rigveda`". Card **118** is `aruRAmSub` / `raghuvamsha` /
   Classical, ruled `defer` with `needs_adjudication=true`; the reversed card is
   **122**. Checked against
   [`gold/decisions_g6-mqm-gold-starter-2026-07-25.csv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/decisions_g6-mqm-gold-starter-2026-07-25.csv)
   rows 11 and 18. The ruling itself is untouched — only the id was misrecorded.

## Reproduce

```sh
cd RussianTranslation
python src/gold_evidence_panel.py --selftest
python src/build_g6_mqm_gold_sheet.py --coverage-json review/g6_v2_evidence_coverage.json
python src/build_g6_mqm_gold_sheet.py --no-evidence --out /tmp/g6_old.html --locks-dir /tmp/locks
```

The selftest runs on fixtures in a temp dir and needs none of the eight external
assets, so it is green in CI where none of them is checked out. It covers the
four cases H1801 names — Vedic routing → GRA, Classical routing → MW/PWG, a
headword with no root hit, a form with zero corpus contexts — plus the homograph
guard, the variant layer and the whole-compound-before-parts ordering.

## Non-goal

The n=400 store gold sheet is **not** cut here. That is
[H1665](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1665-Fable_SanskritLexicography_pwg-store-gold-cut-execute-r1-r5_26.07.26.md),
and it stays gated until
[H1802](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1802-Sonnet_csl-pyutil_review-sheet-reject-label-picker_28.07.26.md)
(the required-label control in `csl-pyutil`) lands too.

The per-card evidence JSON (`--coverage-json`) is **gitignored** for the same
reason the sheet HTML is: it embeds the published Russian translations of the
quoted passages verbatim. The committed artifacts are this report and the lock.

_Dr. Mārcis Gasūns_
