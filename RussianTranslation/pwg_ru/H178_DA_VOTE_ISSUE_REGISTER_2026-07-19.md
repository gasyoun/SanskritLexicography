# H178 DA-sheet vote — processing register and work-stream fan-out (H1300)

_Created: 19-07-2026 · Last updated: 19-07-2026_

MG voted the first of the four H178 B-1 bake-off sheets — `h178_da_sheet.html`
(Direct Assessment, 30 promoted pwg_ru glosses) — on 19-07-2026 and left, besides
the 30 decisions, a meta-feedback note (`voted.md`) with 8 rulings on the voting-sheet
system itself plus ~20 substantive translation-policy issues inside the per-card notes.
This register is the durable record of that vote and the single source for the
work-stream fan-out minted the same pass (H1301–H1308). Processed by Fable 5
(`claude-fable-5`) under
[H1300](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1300-Fable_RussianTranslation_h178-da-vote-processing_19.07.26.md).

Related: bake-off generator
[`src/h178_eval_bakeoff.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/h178_eval_bakeoff.py)
· compute consumer
[H274](https://github.com/gasyoun/Uprava/blob/main/handoffs/H274-Fable_DO_RussianTranslation_pwg_ru_bakeoff_compute_07.07.26.md)
· sheet registry
[REVIEW_SHEETS_INDEX.md](https://github.com/gasyoun/Uprava/blob/main/REVIEW_SHEETS_INDEX.md)
· operator guide
[HUMAN_VOTE_GUIDE.md](https://github.com/gasyoun/Uprava/blob/main/HUMAN_VOTE_GUIDE.md).

## 1. Vote record and file provenance

- **Sheet:** `h178_da_sheet.html` (`sheet_id h178_da`), 30 items, generated 07-07-2026.
- **Decisions: 27 approve / 3 reject** (`decided: 30`).
- **Filing (local-only, gitignored per the H178 publish-safety rule):** the raw browser
  export was saved to the H274 contract path
  `RussianTranslation\pwg_ru\eval\h178_da.decisions.json`, and the meta-feedback note to
  `RussianTranslation\pwg_ru\eval\h178_da_voted_notes.md`. Loss-protection copies of both
  originals: `D:\ClaudeTools\evidence\h178_da_vote_19-07-2026\`.
- **DA numeric channel is PARTIAL: 15/30 items** carry an `H178:{"da":NN}` value
  (100 ×1, 80 ×2, 71 ×1, 70 ×11; mean ≈ 71.4). The other 15 have none — a mix of
  slider friction (see ruling V5 below) and the known H937 residual (rubric-widget
  values can be silently dropped from the export on a second vote click). H274's
  compute must treat missing `da` as absent, not zero.
- **The 10-card suspected-weak oversample vs 20 random:** of the 3 rejects, none is in
  the flagged oversample — early signal that the A-1(a) "suspected weak" flags and MG's
  actual quality verdicts do not coincide; H274 computes this properly.

### The 3 rejected cards

| Card | Reject reason | Class |
|---|---|---|
| `nI\|n_i~~h0_13_apa\|5)` | `Schol.` **zu** `ŚĀK. 14.` — German prose word *zu* (= рус. «к») survived untranslated in the RU field | German prose residue → H1302 |
| `gam\|gam~~h0_42_prod\|1` | DE one word `{%hervorragen%}` rendered as RU doublet `{%выступать, возвышаться над окружающим%}`; KATHĀS. 26,9 has a published RU translation — check it and keep the attested single equivalent | Doublet policy + citation reuse → H1302 (repair) · H1306 (policy) · H1304 (citation check) |
| `DA\|_d_a~~h0_81_a_bisam\|8` | *mit Ergänzung von* left untranslated | German prose residue → H1302 |

## 2. Sheet-system rulings (voted.md V1–V8)

All eight go to **H1301** unless noted. Verbatim source: `h178_da_voted_notes.md`.

| # | Ruling (MG, 19-07-2026) | Disposition |
|---|---|---|
| V1 | Direct Assessment widget goes **below** the card, not above; not a slider but **clickable 1–5** (5 = good, **3 = approval threshold**) | H1301 — this is a mid-bake-off DA-rubric change; see §5 |
| V2 | **Regenerate all remaining voting sheets** in `RussianTranslation/review/` only **after** the first sheet's votes are worked through — voting the other sheets before that is pointless | H1301 final step, gated — see §6 |
| V3 | Every vote card carries a **visible unique ID** MG can cite back | H1301 |
| V4 | Card header must state the headword **in IAST** and make it a **clickable link to the full dictionary entry** (`si_d~~h1_00_pwg02 · derivative-T68-T72` is opaque to a human) | H1301 |
| V5 | Clicking **Publishable** auto-raises DA to at least **4**; manual lowering to 3 / raising to 5 stays possible | H1301 |
| V6 | Comment box **2 rows taller** | H1301 |
| V7 | **Russian words highlighted in color** inside the translation so the eye lands on what is being judged | H1301 |
| V8 | **Where is the voting-sheet standard?** How do human AND agent know a given `decisions.json` belongs to `h178_da_sheet.html`? | H1301 — surface `sheet_id` + target save-path inside the sheet UI; the standard docs are [/review-sheet](https://github.com/gasyoun/claude-config/blob/main/commands/review-sheet.md) + [REVIEW_SHEETS_INDEX.md](https://github.com/gasyoun/Uprava/blob/main/REVIEW_SHEETS_INDEX.md) + [HUMAN_VOTE_GUIDE.md](https://github.com/gasyoun/Uprava/blob/main/HUMAN_VOTE_GUIDE.md); the binding is the `sheet_id` field inside the JSON + the `<sheet_id>_decisions.json` download name (the h178 sheets predate the v0.1.1 emitter fix — MG's export came down as bare `decisions.json`, which is exactly the defect) |

## 3. Content issues from the per-card notes (N1–N20)

| # | Card(s) | Issue | Stream |
|---|---|---|---|
| N1 | `muc~~h0_20_pra\|8` | R. 2,91,26 + MBH. 5,7331 already have RU translations in SamudraManthanam (incl. the earlier Nīlakaṇṭha-vs-Critical-edition comparison) — that data must be reused **here and in every place, for every covered text**, not only R./MBH. | H1304 |
| N2 | `vas~~h0_zz_pw00\|samava` | Is government marked up structurally (`<ab>Instr.</ab>`)? MG wants **one click → all cards with Instr. government** | H1308 |
| N3 | `vas~~h13_00_pwg00\|5` | (a) German `<ab>` abbreviations must not stay untranslated: `vgl.` = ср., also `v. a.` and all others; (b) `<ls>Spr. (II)</ls>` — is the reference wired to the recognized full text of *Indische Sprüche*? | (a) H1303 · (b) H1307 |
| N4 | `vid~~h0_10_ni\|3` | «вместо» → «вм.»; `ed. Bomb.` = Бомбейская ред.; `fg.` and all German abbreviations translate — "Russians don't read German" | H1305 (terseness) · H1303 (abbrevs) |
| N5 | `vas~~h0_zz_pw03\|2-vi` | Abbreviations like `Aor.` cannot stay untranslated; **only Latin ones stay, by common agreement, via a ratified unified list** | H1303 |
| N6 | `jan~~h0_11__a\|1` · `na_s~~h0_07_nis\|nis-naś-2` | RV citations: translated from scratch or 1:1 Elizarenkova? **Must take Elizarenkova**; where the German rendering differs, mark the divergence separately | H1304 |
| N7 | `ji~~h0_zz_sch\|6` | «отвоёвывать» — **no ё anywhere** except все/всё disambiguation | H1305 |
| N8 | `vi_s~~h0_zz_pw01\|259` · `car~~h0_zz_pw02\|pw-T9` | `Caus.` = `кауз.` (каузатив) | H1303 |
| N9 | `ban_d~~h0_11_ni\|2` | KATHĀS. 34,203 — Ocean-of-Stories Sa↔Ru comparison exists: translate quotes via it wherever possible, and not only KATHĀS.; `Verz. d. Oxf. H.` must not stay German; **build the census of all works with existing RU translations** — e.g. `SamudraManthanam/archive_ignatiev_2026` is definitely not fully ingested | H1304 (+H1303) |
| N10 | `man~~h0_zz_pw01\|upa_5` | *im Comp., vorangehend* → «в Comp. в препозиции» is clunky Russian; the pattern recurs tens of thousands of times — a lightweight standard formula is needed (meaning: first member of a compound) | H1306 |
| N11 | `vid~~h0_01_sec_1\|1` | GṚHY. not yet in the corpus but an RU translation exists — mark for ingestion; R. GORR. 2,16,46 — is there a concordance from the Gorresio edition onto Leonov's southern-recension translation? | H1304 |
| N12 | `n_i~~h0_zz_pw01\|PW-prefix-T4` | «в значении» → «в знач.» | H1305 |
| N13 | `_buj~~h0_zz_pw\|PW3-3` | Research the Russian textological convention for Latin `v. l.` — «разночтение»? | H1306 |
| N14 | `vraj~~h0_00_pwg00\|1` | Do all Pāṇini references link to the matching page of [ashtadhyayi.com](https://ashtadhyayi.com) as on the Cologne site? Plus sūtra lists by book/chapter | H1307 |
| N15 | `vas~~h4_01_sec_1\|2` | DHĀTUP. references should cite the Palsule list | H1307 |
| N16 | `n_i~~h0_13_apa\|5)` **reject** | German prose *zu* untranslated ("How could a German word survive at all?") | H1302 |
| N17 | `gam~~h0_42_prod\|1` **reject** | One DE word → two RU words unjustified; KATHĀS. 26,9 RU translation is the arbiter | H1306 · H1302 · H1304 |
| N18 | `gam~~h0_20_ava\|2` | Same doublet question; translate Sanskrit citations into RU — **first checking whether a translation already exists** (TS. 2,3,1,4 has none, but partial TMs may help) | H1306 · H1304 |
| N19 | `_d_a~~h0_81_a_bisam\|8` **reject** | *mit Ergänzung von* untranslated | H1302 |
| N20 | `pa_s~~h0_zz_pw00\|mit_T56` | Doublet-vs-single policy: nearly everywhere one DE word becomes two RU words, unverifiable without citations — **what does Apresyan say?** | H1306 |

## 4. Work streams — the minted batch

All nine claimed atomically 19-07-2026 (`mint_handoff.py --batch`, IDs H1300–H1308).
Model lock is in each filename; prior-art anchors were verified this pass — none of
these starts from scratch.

| Handoff | Scope | Prior art to consume |
|---|---|---|
| [H1300](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1300-Fable_RussianTranslation_h178-da-vote-processing_19.07.26.md) (Fable, this pass) | Vote filing, this register, the fan-out, index/registry sync | — |
| [H1301](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1301-Opus_RussianTranslation_pwg-ru-review-sheet-ux-standard-regen_19.07.26.md) (Opus) | V1–V8: DA 1–5 buttons below card, visible IDs, IAST headword + entry link, Publishable→DA≥4, taller comment box, RU-token highlight, in-sheet `sheet_id`/save-path banner; generic parts land in the shared emitter (`csl_pyutil.render_review_sheet`, v0.3.0), h178-specific parts in the bake-off script; **final step (gated, §6): regenerate all pending sheets in `review/`** | Emitter v0.2.0 ([csl-pyutil](https://github.com/sanskrit-lexicon/csl-pyutil), [SHARED_CODE.md](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md) row 9); the existing `<ab>`/`<ls>` render-time tooltip layer in [`build_article_site.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/build_article_site.py) `_render()` — wire it into sheet rendering instead of showing raw store markup |
| [H1302](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1302-Opus_RussianTranslation_pwg-ru-german-residue-sweep-reject-repair_19.07.26.md) (Opus) | Store-wide sweep for **German prose residue** in RU fields (*zu*, *mit Ergänzung von*, and kin — distinct from `<ab>`-tagged abbreviations, which are H1303's); classify, fix/requeue; repair + re-promote the 3 rejected cards | [`ABBREVIATIONS_RU.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md) (scopes what is `<ab>`-tagged vs prose); requeue mechanics in [`PIPELINE_HISTORY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_HISTORY.md) |
| [H1303](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1303-Fable_RussianTranslation_pwg-ru-abbrev-unified-list-ratification_19.07.26.md) (Fable) | Full `<ab>` inventory (791-entry `pwg_ab.py` + 265 in-store tokens) → per-token proposal: translate-to-RU vs stay-Latin → **ratification review sheet for MG** → apply the ratified list; resolves the logged contradiction (§7) | The 10-07 render-time architecture + bucket split in [`ABBREVIATIONS_RU.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md); [`pwg_ab.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ab.py) |
| [H1304](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1304-Fable_RussianTranslation_pwg-ru-covered-texts-citation-tm-registry_19.07.26.md) (Fable) | Census of every text with an existing RU translation (SamudraManthanam MBH/R. incl. `archive_ignatiev_2026` full ingest, KATHĀS./Ocean of Stories, Elizarenkova RV — 1:1 reuse policy with divergence marking, Leonov Rāmāyaṇa + R.-GORR. concordance question, GṚHY., TS. partials) → citation-translation lookup wired into the pipeline + retro-application plan | 1.09M-pair verse-aligned [`corpus_lexicon.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_corpus_lexicon.py) (116 aligned works, [`pwg_ru/aligned_works.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/aligned_works.txt)); the `mined` TM tier ([`RUNNING_TEXT_MINING.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/RUNNING_TEXT_MINING.md), H186); [`REUSE_MAP.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/REUSE_MAP.md); H215 TM/TMX |
| [H1305](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1305-Sonnet_RussianTranslation_pwg-ru-style-mechanical-yo-terseness-sweep_19.07.26.md) (Sonnet) | Mechanical RU style: **no ё** (except все/всё), «вм.», «в знач.», `ed. Bomb.` → «Бомбейская ред.» and similar terseness subs; store sweep + prompt rules + selftest gates (SHARED per [LANG_PARITY.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LANG_PARITY.md)) | Existing gate wiring in `audit_window.py` / `window_selftest` |
| [H1306](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1306-Fable_RussianTranslation_pwg-ru-style-research-doublets-apresyan_19.07.26.md) (Fable) | Research-grade style rulings: doublet-vs-single gloss policy grounded in Apresyan (systematic lexicography), the RU textological rendering of `v. l.`, the standard formula for *im Comp. vorangehend*; each ends in a proposal sheet for MG, then prompt + store application | Rejected-card evidence here (N17/N18/N20); citation arbiter mechanism from H1304 |
| [H1307](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1307-Opus_RussianTranslation_pwg-ru-ls-link-enrichment-panini-spr-dhatup_19.07.26.md) (Opus) | `<ls>` enrichment: Pāṇini refs → [ashtadhyayi.com](https://ashtadhyayi.com) deep links (+ sūtra browse lists by book/chapter), `Spr. (II)` → *Indische Sprüche* full-text link, DHĀTUP. → Palsule list | 2,681-entry PWG bibliography [`pwg_sources.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_sources.py) + the `<ls>` tooltip layer |
| [H1308](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1308-Opus_RussianTranslation_pwg-ru-valency-government-index_19.07.26.md) (Opus) | Audit whether government/valency (`<ab>Instr.</ab>` + «с + case» patterns) is structurally recoverable; build the index + one-click search surface (dashboard/site page) | `<ab>` corpus-wide dashboard ask already recorded in [`ABBREVIATIONS_RU.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md) §Why |

## 5. Protocol change — DA rubric 0–100 slider → 1–5 buttons

V1 changes the Direct Assessment arm mid-bake-off: the 19-07 votes were cast on the
0–100 slider (15 numeric values recorded); all future DA voting happens on 1–5 buttons
(3 = approval threshold). For H274's cross-rubric comparison the two generations must
be normalized (0–100 values map onto the 1–5 grid as `round(1 + 4·(da/100))` or simply
divided into the five 20-point bands); the report must state per-item which scale the
value was cast on. This also makes DA and Likert near-identical as instruments — a
fact H274 should surface when the data picks the standing protocol.

## 6. Ordering and gates

1. **Now runnable in parallel:** H1301 (UX + standard, everything except the regen
   step) · H1302 (German-residue sweep + reject repair) · H1305 (mechanical style
   sweep) · H1308 (valency audit) · H1307 (link enrichment).
2. **Ratification loops (produce a sheet, then wait on MG):** H1303 (abbrev list) ·
   H1306 (style research). Their *store application* follows the vote.
3. **Big infrastructure:** H1304 (citation-TM registry + reuse) — start any time;
   N17-class citation checks in H1302/H1306 may consume its first outputs.
4. **Regen gate (V2):** H1301's final regeneration of the remaining sheets
   (`h178_{mqm,likert,pairwise}`, the two h180 sets, kochergina, renou) fires only
   after H1302 + H1305 have landed in the store (minimum honest bar for "голоса
   отработаны"); regenerating earlier reproduces the very defects MG just flagged.
5. **Then:** MG votes the three remaining h178 sheets →
   [H274](https://github.com/gasyoun/Uprava/blob/main/handoffs/H274-Fable_DO_RussianTranslation_pwg_ru_bakeoff_compute_07.07.26.md)
   bake-off compute → standing evaluation protocol chosen.

## 7. Contradiction logged (abbreviations)

The 10-07-2026 ruling in
[`ABBREVIATIONS_RU.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ABBREVIATIONS_RU.md)
("grammatical-category abbreviations stay Latin, tooltip only") collides with the
19-07-2026 vote notes (`Caus.` = `кауз.`, `Aor.` "нельзя не переводить", "only
Latin by ratified unified list"). Logged as a 🔴 row in
[`CONTRADICTIONS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)
(§ B — sources disagree across time); H1303's ratified list is the designated
resolution path, after which the row graduates to a `D##` decision record.

_Dr. Mārcis Gasūns_
