# pwg_ru — changelog

How the Russian edition of the Petersburg Dictionary (PWG, Böhtlingk–Roth)
evolved. Newest first. This is the *project* changelog (method + pipeline); the
data stores are gitignored and versioned by their build provenance.

See also: [METHODOLOGY_REVIEW.md](METHODOLOGY_REVIEW.md) (where we want to go),
[failures/FAILURE_GALLERY.md](failures/FAILURE_GALLERY.md) (what went wrong and
how it got better), [APRESJAN.md](APRESJAN.md) (the theory we build on).

## 2026-06-24

### Root-entry segmenter suite (the giant-root fix) + external resources
- **The structural fix for "translation pass dies on bhū/vid":** a root mega-record is now
  split into per-prefix sub-cards and gluable back. Built one at a time in
  [research/](research/) (full write-up: [research/ROOT_ENTRY_ARCHITECTURE.md](research/ROOT_ENTRY_ARCHITECTURE.md) §BUILDS A–C):
  - `root_segment_proto.py` — lossless `<div n="p">` slicer; `root_glue.py` — SPLIT→NESTED
    glue (PWG + MW), cap-aware via the link table; `root_units.py` — segments a root record
    into per-prefix **translation units** in the `compile_translatable` manifest shape
    (`BU`→380 units).
  - `lex_noun_link.py` — PWG nominal→root chain table (34.8 % linked, dict-field-first);
    `mw_deriv.py` — MW derivation oracle + link table (133.7 k rows) from Funderburk's
    `MWderivations`; `root_merge.py` — PWG↔MW merged comparative article (bhū 33/41 aligned);
    `apte_parse.py` — Apte Sanskrit–Hindi → independent root oracle (1,654 dhātus, 793 not in
    verbs01) + `productivity` (affix-productivity from 38,757 `+`-etymologies: upasarga×root —
    `vi`>`sam`>`pra` — and kṛt/taddhita pratyaya×root — `kta`>`ṭāp`>`lyuṭ`>`ac` — cross-listed
    with MWderivations' `wsfx` surface-suffix counts `-tva`>`-tā`>`-vat`; → `apte_productivity.tsv`).
    `apte_parse.py crossmap` + curated `affix_map.tsv` **bridge the two lenses**
    (Pāṇinian pratyaya ↔ surface suffix ↔ MW wsfx, via anubandha-stripping): they OVERLAP on
    transparent taddhita but MW≫Apte there (`tva` 11 vs 1996 — Apte rarely cites the obvious
    suffix), while Apte alone covers the kṛt formation affixes (`kta`/`ghañ`/`lyuṭ`/`ṭāp`, MW
    wsfx=0 — lexicalised headwords). Complementary coverage, now quantified.
- **Wired into the pipeline (the unblocker):** `_pilot_gen_merged.py --root-split` (also
  `--manifest freq --root-split`) auto-detects a giant root (≥8 prefix divisions) and explodes
  it into one single-pass-sized sub-card per prefix — HEAD card keeps the simple verb + all
  supplements + NWS owner map; each prefix sub-card is its own `<div n="p">` block — plus a
  `<safe>.rootmap.json` for `root_glue` reassembly. `BU`→41 sub-cards (head 820 lines + 93-entry
  owner map; `anu` prefix card 87 lines vs the 1315-line whole record), `gam`→63. This lets the
  frequency-first queue (top = sthā/bhū/gam) run without the single-pass death.
- **Glue-after-translate (round-trip closed):** `root_glue_translated.py <root>` reads the
  `rootmap.json` + each sub-card's translated `<subkey>.merged.md` and stitches them back into
  one `<safe>.NESTED.md` Russian article (head → prefixes by seg order; missing → pending).
  Demoed on `BU`: 3 prefix sub-cards (anu/abhi/ud) translated → glued into the 41-sub-card
  nested article, each in its slot, Sanskrit/sigla preserved. SPLIT→translate→GLUE confirmed.
- **Scale-proven:** `scale_test.py` segments **all 1,163 PWG verb roots, 100 % LOSSLESS**;
  the slicer's 8,588 prefix-divisions vs verbs01's 8,361 vetted upasargas (+227 FP gap, 159
  roots) confirm the false-positive guard is needed at scale.
- **Reuse, not reinvention** (per *check-prior-art*): the segmenter sits on Jim Funderburk's
  [`PWG/verbs01/`](https://github.com/sanskrit-lexicon/PWG/tree/master/verbs01) (sandhi join +
  MW alignment already done) and [`MWderivations`](https://github.com/funderburkjim/MWderivations)
  (220 k MW headwords classified pfx/cpd/wsfx). Cross-check: `MWderivations/compounds.txt` is
  byte-identical to `WhitneyRoots/MW_compounds_12610.txt`. External data vendored gitignored
  under `research/external/`; `research/apte_roots.tsv` + `research/lex_noun_link_pwg.tsv` tracked.

## 2026-06-23

### Scaled + handed off (translation pipeline)
- **Owner-map feed — F12 eliminated by construction.** `_pilot_gen_merged.py` appends
  an AUTHORITATIVE "PRE-PARSED OWNER MAP" (deterministic `nws_split` triples) to each
  card's NWS layer; the translator emits one row per entry with the owner VERBATIM and
  never re-derives attribution. `run_pilot_wf.js` HARD RULE 5 + Guard 7 consume it.
- **Re-validated on fresh cards:** `ātman` CLEAN (13/13, incl. French TAK *le soi*→RU);
  `ās` went MISATTRIBUTION (3 owner-swaps, pre-fix) → **CLEAN** (0 mismatches) after the
  owner-map feed. First coverage-first batch of 6 (`as`/`A`/`anu`/`akṣa`/`arjuna` clean,
  `as` with 60 NWS owners CLEAN) = **5/6 first-pass clean**; `Ap` quarantined + re-queued.
- **Full a-section staged for the Max workflow:** regenerated **4,264 NWS a-cards** with
  owner maps (`--manifest a`); runbook [src/pilot/RUN_ASECTION_MAX.md](src/pilot/RUN_ASECTION_MAX.md)
  (per-window prep → run `run_pilot_wf.js` on Max → `run_real_test.py audit`; rejects
  auto-re-queue). Window 1 (`[0,50)`, 37 fresh) prepped.
- **Failure gallery:** F10 (Windows case-insensitive filename collision — would lose
  ~15 k headwords), F11 (editorial-intent fabrication), F12 (NWS cite-after-gloss
  off-by-one inherited by the judge). See [failures/FAILURE_GALLERY.md](failures/FAILURE_GALLERY.md).
- **Cost & feasibility re-grounded** — [PILOT_COST.md](PILOT_COST.md) §6: measured
  **0.78 tok/byte**; a-section ≈ **0.5–0.8 B** tokens, whole PWG dict ≈ **4–7 B**;
  throughput ~7 k cards/day at 24/7 (~15 days *continuous*) but **quota-bound to ~1–2
  months on one Max seat**. Documents the data gaps (Max weekly quota, typical-card
  cost, total size) and the one instrumented-window experiment that resolves them.

- **Frequency-first ordering (DCS) built + validated.** `freq_route.py` ranks PWG
  headwords by hybrid token×breadth×richness → `scale_manifest.freq.json` (41% DCS-attested;
  ~3.8k band-4+5 core). Top cards = verbal **roots** (sthā 379 senses, i 272, gam 213). Freq-
  first pipeline validated: `rūpa`/`rasa` CLEAN through the owner-map gate. **Finding:** roots
  (`vid` 74, `bhū` 131) fail single-pass translation ("connection closed mid-response") →
  root-entry sectioning is the open design question before scaling (pending manuals review).

- **Lexicography design studies — 3 handoff chats spawned.** The giant-root failure opened the
  microstructure question; decided the **two-mode root architecture** (SPLIT cards for translation +
  `root_key` linkage → glue to a NESTED root article on demand) and created 3 grounded research briefs
  in [research/](research/) — (A) root architecture, (B) sense ordering, (C) homonym/gloss/citation/
  run-on conventions — each spun off as its own cold handoff chat (`task_740ea467`/`task_2242dc13`/
  `task_9b9ce8db`) to read the OCRed prefaces + probe entries and fill a per-dict comparison table
  before scaling.

### Added
- **Renou language-state (I–V) tag on every cited sense.** Each dictionary
  *meaning* is now classified into one of Louis Renou's five states of Sanskrit
  (*Histoire de la langue sanskrite*, the five chapters): **I** Vedic, **II**
  Pāṇinian/grammarians', **III** Epic & prolongements, **IV** Classical, **V**
  Buddhist/Jaina. Derivation is **deterministic from the sense's `<ls>`
  citations** — no LLM — so it is fully auditable. A sense is **multi-label**
  (a meaning attested across eras carries all applicable states, e.g.
  `["I","III"]`), and its **oldest citation** is flagged separately
  (`renou_oldest`, plus `renou_oldest_sense` on the record) to answer "in which
  era was this meaning first attested".
  - [src/build_ls_map.py](src/build_ls_map.py): every curated PWG source in
    `CANON` carries a `renou` state; `ls_source_map.json` regenerated with it.
    PWG coverage — I 123 806 · II 25 291 · III 199 075 · IV 211 071 · V 0
    citations (PWG's curated canon has no Buddhist/Jaina source).
  - [src/build_ls_map_mw.py](src/build_ls_map_mw.py) (new): MW-side map
    (`ls_source_map_mw.json`), with an MW-specific siglum extractor (no `n=""`
    attribute; lowercase-roman volume refs stripped; `L.` kept as
    lexicographers). 77 sources, 84.1 % of MW `<ls>` citations; **state V
    populates here** (Buddh./Lalit./Divyāv./SaddhP./Jaina — 4 611 citations).
  - [src/renou.py](src/renou.py) (new): `states_for_text/keys` resolves
    citations → states, dict-aware (`pwg`/`mw`).
  - [src/annotate_renou.py](src/annotate_renou.py) (new): idempotent, BOM-free,
    temp-swap backfill of `renou` / `renou_oldest` onto final-card senses (and
    `renou_oldest_sense` per record); `--report` prints the I–V distribution,
    multi-label count and first-attestation breakdown.
  - [schemas/pwg_ru_final_card.schema.json](schemas/pwg_ru_final_card.schema.json):
    `renou` (array of I–V) and `renou_oldest` added to the sense as **optional**
    fields, and `renou_oldest_sense` to the record — existing MW/PWG cards stay
    valid.
  - Ran record-level on the legacy PWG store (`pwg_ru_translated.jsonl`, 217
    cards): **184 tagged (84.8 %)**, 45 multi-label · I 70 · II 21 · III 48 ·
    IV 106 · V 0.

- **DCS corpus enrichment of the Renou tag (second, provenance-tagged signal).**
  `<ls>` is authoritative but narrow (only cited sources); the Digital Corpus of
  Sanskrit (DCS, 2026 CoNLL-U, 270 texts / 5.46 M words) shows where a headword
  *lemma is actually attested*, recovering states the citations miss.
  - [src/build_dcs_renou.py](src/build_dcs_renou.py) (new): resolves each DCS text
    → Renou state (genre from VisualDCS `dcs_texts_clean.json`, name-hints for the
    Buddhist **V** / grammar **II** texts it misses, date fallback), then scans the
    corpus (lemma = CoNLL-U col 3) → `dcs_lemma_renou.json` (gitignored build
    artifact): **90 346 lemmas** → `{renou states, oldest text/date, n_texts}`.
  - [src/enrich_renou_dcs.py](src/enrich_renou_dcs.py) (new): joins the index to
    cards on `key1`→IAST, adding `renou_dcs`, `renou_dcs_oldest`, `renou_dcs_texts`,
    `renou_enriched` (ls ∪ dcs) and `renou_provenance` (`{state:["ls","dcs"]}`).
    DCS is per-lemma, so it merges at the card/record level and **never overwrites**
    the per-sense `<ls>` tag.
  - On the 217 PWG cards: 127 (58.5 %) DCS-hit, 83 gained ≥1 state; **state V
    went 0 → 37 cards** (Buddhist attestation `<ls>` never supplied). Enriched
    coverage I 93 · II 30 · III 90 · IV 136 · V 37.
  - **Scaled to the whole dictionary** — ran on `assembled_cards.jsonl`, all
    **120 173 PWG headwords** (key1→IAST join, no translations needed): **54 519
    (45.4 %) DCS-hit** → corpus-grounded Renou states. Coverage I 22 075 · II 4 926 ·
    III 31 187 · IV 35 544 · **V 10 171** (e.g. *akaniṣṭha, akṣayamati, akṣobhya* —
    Buddhist headwords `<ls>` never marks). DCS is itself built from GRETIL e-texts,
    so it already subsumes the raw-corpus layer; the 45.4 % ceiling is the
    exact-lemma-form join (rare/variant/compound headwords miss).
  - [src/add_corpus_renou.py](src/add_corpus_renou.py) (new): reusable augmenter
    that folds a raw IAST text (no lemmatiser) into the index at a given Renou
    state, word-FORM level — additive, idempotent (`__sources__` meta guards
    re-runs). Applied to GRETIL's **Skandapurāṇa Revākhaṇḍa** (state III): 25 075
    forms → 23 765 new form-keys + 184 existing lemmas gained III (index 90 346 →
    114 111). **Data-availability finding:** GRETIL serves only the Revākhaṇḍa for
    Skanda (the `sa_skandapurANa1-31` critical edition is listed but 404s in all
    formats); the Revākhaṇḍa is *already in DCS lemmatised*, so the fold is near-zero
    marginal on the 217-card sample (III unchanged). The full 81 k-verse vulgate is
    not available as clean Sanskrit e-text on GRETIL — the augmenter is ready for it
    when a source surfaces.
  - **Third tier — wisdomlib (built; reuses the existing Samudra crawler).** A word's
    wisdomlib **tradition** sections (Buddhism/Jainism/Ayurveda/Vyakarana/Vedic/…) give
    a tertiary, lower-confidence Renou hint (Buddhism/Jainism → **V**). New
    `SamudraManthanam/web/corpus_builder/wisdomlib/definitions.py` fetches `/definition/`
    pages **reusing `crawl.py`'s** polite fetch + `is_block_page`, parses tradition
    headings → `word_traditions.jsonl`. Consumer
    [src/enrich_renou_wisdomlib.py](src/enrich_renou_wisdomlib.py) (new) folds it into
    `renou_wl` + `renou_provenance` as source `"wl"` — never overriding `<ls>`/DCS; a
    state backed by `wl` alone is the weakest evidence. Join is on a diacritic-free key
    (wisdomlib ASCII slug `akshobhya` ↔ SLP1→IAST `akṣobhya`); consumer + parser
    self-test pass. **Blocked on live fetch:** wisdomlib is Cloudflare-gated per-IP (the
    crawler README's documented reality — `http=000` here), so `word_traditions.jsonl`
    must be produced gently from a residential connection, validating the parser with
    `definitions.py parse <page>` on the first real page.
  - **Parser validated on real pages (2026-06-24)** once the IP cooled: `akshobhya`/
    `bodhisattva` tradition extraction correct; fixed two bugs the run exposed — force
    HTTP/1.1 (wisdomlib drops HTTP/2 from this egress) and gloss count via
    `class="suffix source"` (Samudra PR #15). A real BHS batch (16,837 slugs) re-tripped
    the per-IP block, exposing + fixing two more: resumable (don't persist transient
    failures) and a timeout-aware circuit breaker.

- **BHS → PWG/MW/AP deterministic V transfer ([src/enrich_renou_bhs.py](src/enrich_renou_bhs.py), new).**
  Edgerton's Buddhist Hybrid Sanskrit dictionary *is* the state-**V** register, so any
  headword present in BHS but lacking V in a mainstream dict is a missed attestation —
  filled deterministically, no fetching (what the Cloudflare-blocked wisdomlib batch was
  approximating). Adds V with provenance source `"bhs"` (an attestation claim, so common
  words used in Buddhist texts — e.g. *viṣṇu* — correctly gain a V-register attestation,
  marked `bhs`-only and distinguishable from `ls`/`dcs`/`wl`). **New V tags: MW 15 239 ·
  PWG 5 734 · AP 2 364 (23 337 total), plus 23 911 corroborated.** Join on the
  diacritic-free key; outputs `{store}.bhs.jsonl` (gitignored).

- **Consolidated into one pipeline + [RENOU.md](RENOU.md).**
  [src/renou_pipeline.py](src/renou_pipeline.py) (new) chains the four signals —
  `<ls>`+DCS (`tag_dict_from_source`) → BHS V (`enrich_renou_bhs`) → wisdomlib
  (`enrich_renou_wisdomlib`) — into one canonical `{code}.renou.jsonl` per dictionary,
  keyed by `key1`, with a states / V-by-source report. `--all` ran the **8 LS-rich
  dicts = 770 292 entries** (PWG 123 366 · MW 286 560 · PW 170 556 · AP 90 654 · AP90
  34 882 · SCH 29 125 · BEN 17 310 · BHS 17 839). [RENOU.md](RENOU.md) documents the
  five states, the four provenance sources + their trust, the per-dict coverage, and
  how to reproduce. Canonical indices are gitignored (regenerated by the pipeline).

- **Editorial layer — [src/renou_portrait.py](src/renou_portrait.py) (new).** Turns the
  signals into editor-facing output: `portrait(entry)` renders a headword's Renou era
  label (Russian), its first attestation, and a confidence note — a V supported only by
  `bhs` is flagged *register-only* (e.g. *viṣṇu* "V: только регистр (BHS)" vs *akṣobhya*
  V from `dcs+bhs+wl`). `order_senses_oldest_first(card)` reorders a structured card's
  senses earliest-attested-first (uses `renou_oldest_sense`; ready for the per-sense
  store, no-op without it). Demoed on MW.

- **Renou tagging extended to Monier-Williams (both layers).** The MW *Russian*
  cards live in a separate working repo, but the Renou tag is language-independent
  (headword + `<ls>`), so [src/tag_mw_from_source.py](src/tag_mw_from_source.py)
  (new) derives it straight from the MW source `csl-orig/v02/mw/mw.txt` and keys it
  by `key1` (joins to the Russian cards later) → `mw_renou.jsonl` (gitignored).
  All **286 560 MW entries**: **59.1 % `<ls>`-tagged**, **47.6 % DCS-hit**. The two
  signals now cross-check — `<ls>` state **V** = 4 503 (citation-based:
  Buddh./Lalit./Divyāv./SaddhP./Jaina), DCS state **V** = 38 200 (attestation-based),
  enriched union **41 195**, of which **1 508 are corroborated by BOTH `<ls>` and
  DCS** (e.g. *aṭaṭa* — a Buddhist hell — `ls=[V] dcs=[V]`). Per-entry
  `renou_provenance` records which signal(s) back each state.

- **Renou tagging extended to the 6 remaining LS-rich dictionaries (8 total).**
  Ranked the whole csl-orig corpus by `<ls>` richness and tagged the leaders:
  **AP** (Apte), **AP90**, **PW**, **BEN** (Benfey), **SCH** (Schmidt), **BHS**
  (Edgerton). New [src/renou_sigla.py](src/renou_sigla.py) holds the curated
  Apte/Benfey siglum→state tables (Apte `R`=Raghuvaṃśa, `Mv`=Mahāvīracarita — *not*
  Rāmāyaṇa/Mahāvastu) and the BHS rule (**default-V** + a meta blocklist of
  editors/dictionaries); [src/tag_dict_from_source.py](src/tag_dict_from_source.py)
  generalises the MW tagger over any dict (Petersburg dicts PW/SCH **reuse the PWG
  map**; AP/AP90/BEN use the inline tables; BHS the default-V rule) and emits
  `{code}_renou.jsonl` (gitignored). **360 366 more entries tagged:**
  - **BHS** 17 839 — 73.8 % `<ls>`-tagged, **all V** (13 172; the pure Buddhist
    signal: *dharma/buddha/bodhisattva* `ls=[V]`, corroborated by DCS).
  - **BEN** 17 310 — 70.0 % `<ls>` (citations concentrate in ~30 sigla).
  - **AP** 90 654 / **AP90** 34 882 — 26–29 % `<ls>` (long Apte siglum tail), DCS V
    4 774 / 3 646.
  - **PW** 170 556 / **SCH** 29 125 — `<ls>` partial (10–13 %; their Petersburg sigla
    exceed the PWG canon), but DCS carries them (PW enriched V = 10 340).
  Together with PWG + MW, all eight LS-rich dictionaries now carry the two-layer,
  provenance-tagged Renou state, keyed by `key1`.

### Fixed
- `nws_split.py` OWNER citation now stops at `;` so the trailing-tag
  sub-entry variant (`gloss … <DIATAG> ; SOURCE:page`, e.g. `aYj`) keeps
  only the SOURCE as owner, not the diasystem tag.
- `nws_split.py check` locates card rows on word boundaries instead of raw
  substring, killing a false MISATTRIBUTION where the short Sanskrit
  locator `apāṃ` matched inside the compounds `apāṃpitta`/`apāṃnidhi`
  (the `ap` cross-reference `apāṃ napāt → s.v. napāt` has no card row).
- **Root cause of the `av` `+ upa` owner slide:** `compile_translatable`
  `mask_nws_gloss` now strips the leading owner *bleed*. A roman-numeral
  co-owner cite (`Rivelex (2) : XLV`) that `nws_split`'s digit-only OWNER
  can't tag rode onto the FRONT of the next gloss as `<tag> ; Source :
  page > …`, putting a competing source in the to-translate prose of
  glosses whose deterministic owner was already correct — which led the
  LLM assembly to attribute `+ upa` to Rivelex instead of Geldner. The
  strip fires only on real bleeds (5 `av` glosses) and leaves
  `nws_split.py` itself untouched (parsing the roman co-owner there
  destabilises lemma/gloss alignment).
- Hand-corrected the slid `av` `+ upa` block in the (gitignored) merged
  card to the reading-direction owners (Geldner → Graßmann → NṚV → NṚV →
  Rivelex); all other prefix blocks verified already-correct.

- `nws_split.py` OWNER trailing parenthetical now spans one level of
  nested parens and no longer requires the `s.v.` prefix, so cites like
  `BHSD : 154 (s.v. ekoti -(° tī -) bhūta)`,
  `Olivelle 2015 : 391 (s.v. ṣaḍvidha (- bala))` and bare headword
  variants `MW : 756 (bhā́s)` / `MW : 759 (bhujiṣyà)` resolve their owner
  instead of being dropped. Found by the b-section split-preview audit;
  `selftest` + all 10 a-section checks still CLEAN.
- `scale_route.py` accepts any single-letter section (e.g. `b`), not just
  `a`/`all`, emitting `scale_manifest.<letter>.json`.
- **`nws_split.nws_fragment` no longer swallows the appended owner map.**
  `_pilot_gen_merged.py` writes an authoritative `NWS — PRE-PARSED OWNER
  MAP` layer after the net-new NWS addendum, but `nws_fragment` captured
  `(.*)\Z` from the first `=== LAYER: NWS` marker to EOF, so on any
  owner-map input it re-parsed that map as source content — corrupting
  `split()`, the F12 gate (`check`) and `compile_translatable` (the
  d-section first showed 1,380 phantom empty-gloss + 33 phantom no-owner
  entries). It now captures only up to the next `=== LAYER:` marker and
  skips the `PRE-PARSED` header. Found while auditing the d-section (first
  section generated with the owner-map injection); `selftest` + all 10
  a-section checks still CLEAN, `compile_translatable('day')` → 7 clean
  units, 0 map artifacts.
- **`nws_owner_map` debleeds the injected owner map.** The roman co-owner
  bleed (e.g. `Hillebrandt 1885 : IV`) that `compile_translatable` already
  strips also contaminated the appended `PRE-PARSED OWNER MAP`: `split`'s
  `lemma_tag` scatters the bled segment into an entry's leading gloss, its
  tag (stray `; Name : page`) and a punctuation-only lemma (`{#,#}`). The
  owner stays correct, so this is cosmetic for what the translator reads.
  `nws_owner_map` now strips the leading-bleed from the gloss, removes a
  bled-in `Name : page` cite from the tag, and drops punct-only lemmas
  (mirrors `mask_nws_gloss`). The owner field is never touched; clean
  sections are no-ops. Found in the g-section (`gam`).

### Added
- `run_real_test.py audit` is now a true **NWS attribution gate**: a fresh
  (non-protected) card whose NWS owners disagree with the deterministic
  `nws_split` parse is rejected — its `<safe>.merged.md` is moved to
  `<safe>.merged.REJECTED.md` so the next `prep` re-queues it — and the
  command exits non-zero. Protected hand-authored cards are audited but
  never quarantined. Verified end-to-end (slid card → FAIL → quarantined →
  exit 1; clean card → PASS → exit 0). `selftest` + all 10 audited keys
  CLEAN.

### Audited
- **Full b-section deterministic split-preview** (all 4,613 b-keys → 971
  NWS-bearing, 2,655 entries): **0 roman-cite bleeds** — the `av`-class
  F12 owner slide does not occur anywhere in the b-section. After the
  trailer-paren fix above, only 11 entries are unowned: 4 benign
  empty-segments + 7 real losses confined to the two known-limitation
  sources below.
- **Full c-section deterministic split-preview** (all 2,366 c-keys → 719
  NWS-bearing, 1,828 entries): **0 roman-cite bleeds**. 17 unowned = 8
  benign empty-segments + 9 real losses, all in the known-limitation
  sources below (8 × Meister `(2.1)`, 1 × Böhtlingk `*NNN`).
- **Full d-section deterministic split-preview** (all 6,019 d-keys → 1,439
  NWS-bearing, 3,808 entries): **0 roman-cite bleeds**. First section
  generated with the owner-map injection, which surfaced the
  `nws_fragment` over-capture bug fixed above; after that fix only 4
  entries (0.10%) are real losses — one each Meister `(2.1)`, roman page,
  Böhtlingk `*NNN`, plus one page-less cross-reference
  (`duHzvapnya → s.v. duṣvápnya (Graßmann 1873 (1996))`, no `: page` to
  parse). The 14 remaining unowned are benign empty terminal segments.
- **Full e-section deterministic split-preview** (all 663 e-keys → 203
  NWS-bearing, 470 entries): **0 roman-cite bleeds**, cleanest section so
  far. 3 unowned = 2 benign empty + 1 page-less cross-reference
  (`eta → s.v. éta . Rivelex (2) (s.v. éta)`, no `: page` to parse); none
  of the Meister/roman/Böhtlingk classes appear. Cross-checked against the
  injected owner map: 470 map entries with exactly 3 `[NWS: ?]`, matching
  the split-preview one-for-one — confirming the `nws_fragment` fix and
  owner-map generation are consistent. The page-less cross-reference (no
  `Name : page` cite exists) is a recurring benign category, not a parser
  gap — it also appears once in d (`duHzvapnya`).
- **Full f-section deterministic split-preview** (all 339 f-keys [SLP1 `f`
  = ṛ] → 156 NWS-bearing, 502 entries): **0 roman-cite bleeds, 0 real
  losses** — the only unowned entry is a benign empty terminal segment, no
  Meister/roman/Böhtlingk/page-less cases. Owner-map cross-check: 502 map
  entries, exactly 1 `[NWS: ?]`, matching the split-preview one-for-one.
- **Full g-section deterministic split-preview** (all 3,354 g-keys → 974
  NWS-bearing, 2,866 entries): **2 roman-cite bleeds** (both `gam`,
  `Hillebrandt 1885 : IV`) — the first bleeds since the a-section; the
  owner stays correct (`Geldner 1907 : 52`), and the cosmetic owner-map
  contamination is fixed by the `nws_owner_map` debleed above. 9 unowned =
  8 benign empty + 1 Meister `(2.1)` (0.03% real loss). Owner-map
  cross-check: 2,866 entries, 9 `[NWS: ?]`, matching the split-preview.
- **Full h-section deterministic split-preview** (all 2,027 h-keys → 466
  NWS-bearing, 1,353 entries): **0 roman-cite bleeds**. 10 unowned = 8
  benign empty + 2 real (1 Meister `(2.1)`, 1 page-less cross-reference
  `hriRIy → s.v. hṛṇīy (TŚPC 3)`, no `: page`) = 0.15%. Owner-map
  cross-check: 1,353 entries, 10 `[NWS: ?]`, matching the split-preview,
  and **0 inputs with residual contamination** — confirming the
  `nws_owner_map` debleed produces clean maps on fresh generation.
- **Full i-section deterministic split-preview** (all 777 i-keys → 281
  NWS-bearing, 1,045 entries): **0 roman-cite bleeds**. 4 unowned = 3
  benign empty + 1 real (`in → … : XLVII (als Lemma in Rivelex 1, S. 561
  hinzuzufügen)`, a roman-page owner trailed by an editorial note — the
  roman-page known limitation) = 0.10%. Owner-map cross-check: 1,045
  entries, 4 `[NWS: ?]`, matching the split-preview, 0 residual
  contamination.
- **Full j-section deterministic split-preview** (all 2,089 j-keys → 506
  NWS-bearing, 1,207 entries): **0 roman-cite bleeds, 0 real losses** — the
  6 unowned entries are all benign empty terminal segments, with no
  Meister/roman/Böhtlingk/page-less cases (0.00% real loss). Owner-map
  cross-check: 1,207 entries, exactly 6 `[NWS: ?]`, matching the
  split-preview one-for-one, 0 residual contamination.
- **Full k-section deterministic split-preview** (all 8,637 k-keys → 2,590
  NWS-bearing, 6,530 entries — the largest section): **3 roman-cite
  bleeds** (all `kar`, `Hillebrandt 1885 : IV`, the same g-section pattern;
  owner stays correct and the cosmetic owner-map contamination is cleaned
  by the `nws_owner_map` debleed — **0 residual contamination**). 39 unowned
  = 28 benign empty + 11 real (0.17%): 6 × Meister `(2.1)`, 2 page-less
  x-ref, 1 roman page, 1 Böhtlingk `*NNN`, all known limitations, plus **1
  source-data typo** — `vṛtrakhādá → … NṚV 2B : 79 (s. (2. khād )` has an
  **unbalanced** trailing parenthetical (a stray extra `(`, a digitization
  error for `(s.v. 2. khād )`); its two sibling entries with the identical
  owner `NṚV 2B : 79` (`amitrakhādá`, `vikhādá`) parse correctly, so this is
  bad input, not a parser gap — admitting unbalanced parens is the kind of
  destabilising relaxation already reverted, so no code change. Owner-map
  cross-check: 6,530 entries, 39 `[NWS: ?]`, matching the split-preview
  one-for-one.
- **Full l-section deterministic split-preview** (all 1,464 l-keys → 286
  NWS-bearing, 735 entries): **0 roman-cite bleeds**. 11 unowned = 6 benign
  empty + 5 real (0.68%), all known limitations: 4 × Böhtlingk `*NNN` + 1
  page-less x-ref; no Meister/roman/OTHER cases. The 0.68% real-loss rate is
  the highest section so far only because the small 735-entry base magnifies
  one `*NNN` cluster — not a new gap. Owner-map cross-check: 735 entries, 11
  `[NWS: ?]`, matching the split-preview one-for-one, 0 residual
  contamination.
- **Full m-section deterministic split-preview** (all 6,350 m-keys → 1,425
  NWS-bearing, 3,495 entries): **0 roman-cite bleeds**. 28 unowned = 17 benign
  empty + 11 real (0.31%), all known limitations: 6 × Meister `(2.1)` + 4 ×
  roman page + 1 page-less x-ref; no Böhtlingk `*NNN`/OTHER cases. Owner-map
  cross-check: 3,495 entries, 28 `[NWS: ?]`, matching the split-preview
  one-for-one, 0 residual contamination.
- **Full n-section deterministic split-preview** (all 4,278 n-keys → 1,022
  NWS-bearing, 2,407 entries): **0 roman-cite bleeds**. 27 unowned = 24 benign
  empty + 3 real (0.12%), all known limitations: 2 × page-less x-ref + 1 ×
  roman page; no Meister `(2.1)`/Böhtlingk `*NNN`/OTHER cases. Owner-map
  cross-check: 2,407 entries, 27 `[NWS: ?]`, matching the split-preview
  one-for-one, 0 residual contamination.
- **Full o-section deterministic split-preview** (all 461 o-keys → 129
  NWS-bearing, 306 entries): **0 roman-cite bleeds**, **0 unowned** — the
  cleanest section so far (0.00% real loss; no benign empties, no known-
  limitation classes, no OTHER). Owner-map cross-check: 306 entries, 0
  `[NWS: ?]`, matching the split-preview one-for-one, 0 residual contamination.
- **Full p-section deterministic split-preview** (all 11,095 p-keys → 2,878
  NWS-bearing, 6,863 entries): **0 roman-cite bleeds**. 90 unowned = 73 benign
  empty + 17 real (0.25%): 8 × page-less x-ref + 6 × Meister `(2.1)` + 2 ×
  roman page + **1 new known-limitation class** — a multi-page citation
  (`TPSI 3 : 19, 22` on `prakaraRasama`). The fragment's terminal owner closes
  with a comma-joined page list, which OWNER's single-token page class
  (`\d+[A-Za-z]?`) cannot represent, so the owner does not close the gloss and
  is dropped — structurally the same digit-only-page cause as the roman/
  asterisk-page limitations (single TPSI multi-page cite in the section; not a
  typo, not a bug). Owner-map cross-check: 6,863 entries, 90 `[NWS: ?]`,
  matching the split-preview one-for-one, 0 residual contamination.
- **Full q-section deterministic split-preview** (all 105 q-keys [SLP1 `q` =
  retroflex ḍ] → 18 NWS-bearing, 42 entries): **0 roman-cite bleeds**. 2
  unowned = 1 benign empty + 1 real, a single Meister `(2.1)`; no OTHER. The
  2.38% real-loss rate is purely the 42-entry small base magnifying one
  Meister cite, not a new gap. Owner-map cross-check: 42 entries, 2
  `[NWS: ?]`, matching the split-preview one-for-one, 0 residual contamination.
- **Full r-section deterministic split-preview** (all 2,905 r-keys → 656
  NWS-bearing, 1,770 entries): **0 roman-cite bleeds**. 9 unowned = 8 benign
  empty + 1 real (0.06%), the multi-page-cite known limitation again
  (`Ensink 1964 : 156, viii` on `ratnasaMBava` — a comma-joined page list, the
  second token a lowercase roman; single page `Ensink 1964 : 156` parses, the
  `, viii` breaks the close). No Meister/Böhtlingk/roman/OTHER cases. Owner-map
  cross-check: 1,770 entries, 9 `[NWS: ?]`, matching the split-preview
  one-for-one, 0 residual contamination.
- **Full s-section deterministic split-preview** (all 18,140 s-keys → 4,297
  NWS-bearing, 10,588 entries — the largest section): **0 roman-cite bleeds**.
  88 unowned = 73 benign empty + 15 real (0.14%): 6 × Meister `(2.1)` + 3 ×
  multi-page cite (`TPSI 3 : 235, 238`, `213, 216`, `248, 249, 251`) + 3 ×
  page-less x-ref (incl. `śelu → Olivelle 2013 : śelu (s.v. śleṣmātaka )`, a
  word locator, no numeric page) + 2 × roman page + **1 new known-limitation
  class** — a lowercase parenthetical source name (`succhardís → s.v. suchardís
  Graßmann 1873 (1996). (pw) : 1531`). OWNER's name class is capital-initial, so
  `(pw)` is not matched (the canonical `PW : 1531` parses); it is a rare,
  well-formed citation style, not a typo. Owner-map cross-check: 10,588 entries,
  88 `[NWS: ?]`, matching the split-preview one-for-one, 0 residual
  contamination.
- **Full t-section deterministic split-preview** (all 3,477 t-keys → 821
  NWS-bearing, 1,968 entries): **0 roman-cite bleeds**. 15 unowned = 12 benign
  empty + 3 real (0.15%): 1 × Meister `(2.1)` + 1 × roman page + 1 × multi-page
  cite (`taTAgata → Ensink 1964 : 73, vii`, comma-joined page list, as in
  r/s). No new classes, no OTHER left after classification. Owner-map
  cross-check: 1,968 entries, 15 `[NWS: ?]`, matching the split-preview
  one-for-one, 0 residual contamination.
- **Full u-section deterministic split-preview** (all 2,903 u-keys → 1,126
  NWS-bearing, 2,656 entries): **0 roman-cite bleeds**. 39 unowned = 34 benign
  empty + 5 real (0.19%): 2 × page-less x-ref + 2 × Meister `(2.1)` + 1 ×
  roman page; no new classes, no OTHER. Owner-map cross-check: 2,656 entries,
  39 `[NWS: ?]`, matching the split-preview one-for-one, 0 residual
  contamination.
- **Full v-section deterministic split-preview** (all 9,658 v-keys → 2,418
  NWS-bearing, 6,526 entries): **0 roman-cite bleeds**. 79 unowned = 65 benign
  empty + 14 real (0.21%): 8 × Meister `(2.1)` + 2 × page-less x-ref + 2 ×
  roman page + 1 × multi-page cite (`vErocana → Ensink 1964 : 180, viii`) + 1 ×
  source-data typo (`vftraKAda` = vṛtrakhāda → `NṚV 2B : 79 (s. (2. khād )`).
  The typo is the **same upstream NWS defect** already in the errata (an
  unbalanced trailing paren); it surfaces here under the v-keyed headword and
  in the k-section under the khād-root fragment (`KAd`), so it costs an owner
  in both section-fragments — one source defect, two losses. No new classes,
  both OTHER classified. Owner-map cross-check: 6,526 entries, 79 `[NWS: ?]`,
  matching the split-preview one-for-one, 0 residual contamination.
- **Full w-section deterministic split-preview** (all 92 w-keys [SLP1 `w` =
  retroflex ṭ] → 19 NWS-bearing, 45 entries): **0 roman-cite bleeds**, **0
  real** (1 benign empty), 0 OTHER. Owner-map cross-check: 45 entries, 1
  `[NWS: ?]`, one-for-one, 0 residual contamination.
- **Full x-section deterministic split-preview** (all 3 x-keys [SLP1 `x` =
  vocalic ḷ] → 2 NWS-bearing, 9 entries): **0 roman-cite bleeds**, **0
  unowned**, 0 OTHER — the smallest section. Owner-map cross-check: 9 entries,
  0 `[NWS: ?]`, one-for-one, 0 residual contamination.
- **Full y-section deterministic split-preview** (all 1,810 y-keys → 420
  NWS-bearing, 1,286 entries): **0 roman-cite bleeds**. 3 unowned = 1 benign
  empty + 2 real (0.16%): 1 × roman page + 1 × Böhtlingk `*NNN`; no new
  classes, no OTHER. Owner-map cross-check: 1,286 entries, 3 `[NWS: ?]`,
  one-for-one, 0 residual contamination.
- **Full z-section deterministic split-preview** (all 302 z-keys [SLP1 `z` =
  ṣ] → 64 NWS-bearing, 112 entries): **0 roman-cite bleeds**. 2 unowned = 1
  benign empty + 1 real, a single Böhtlingk `*NNN`; no OTHER. The 0.89%
  real-loss rate is the 112-entry small base magnifying one cite, not a new
  gap. Owner-map cross-check: 112 entries, 2 `[NWS: ?]`, one-for-one, 0
  residual contamination. **This completes the full SLP1 key universe (a–z,
  with capital/long-vowel sections folded into their lowercase counterparts by
  the case-insensitive section router).**

### Known limitations
- **`Meister 1988 (2.1) : 397`** — a source name carrying a `.` *inside* a
  parenthetical volume number (`(2.1)`) is not recognized as an owner,
  because OWNER's name class excludes `.` on purpose (to stop names like
  `Hoernle 1893-1912 (II) 30.81` / `EI Vol. XV` from swallowing whole
  sentences — guarded by the `aMSa` selftest). Drops 4 b-section owners
  (`BadrapIWa`, `boDimaRqa`, `BadraraTa`, `BUmiKaRqa`).
- **`Walter 1893 : XXXII`** — a roman-numeral page is not matched, because
  OWNER's page is digit-only. Admitting roman pages globally is what
  destabilised the parser earlier (it turns co-owner segments into
  gloss-closers → lemma-stuffing) and was reverted, so it stays out.
  Drops 3 b-section owners (`brahmagranTi`, `brahmaranDra`, `brahmadvAra`).
- **`Böhtlingk 1887 : *163`** — an asterisk-prefixed page is not matched,
  because OWNER's page is digit-only. Extending it to `\*?\d+` was tried
  and reverted: like roman pages, admitting `*NNN` turns segments such as
  `Böhtlingk 1887 : *150 >` into gloss-closers and regressed `ap`/`av` to
  MISATTRIBUTION. Drops 1 c-section owner (`ci`).
- **`TPSI 3 : 19, 22`** — a multi-page citation (comma-joined page list) is
  not matched, because OWNER's page is a single token (`\d+[A-Za-z]?`) and the
  owner must close the gloss; the trailing `, 22` leaves residue after `: 19`,
  so the owner does not close and is dropped entirely. Same digit-only-page
  family as roman/asterisk pages: broadening the page class to swallow
  comma-joined lists would let trailing comma-separated gloss content be read
  as page numbers, destabilising segment/owner alignment, so it stays out by
  design. Drops `prakaraRasama` (p), `ratnasaMBava` (r,
  `Ensink 1964 : 156, viii`), 3 s-section owners (`savyaBicAra`,
  `saMSayasama`, `sADyasama`, all `TPSI 3 : …, …`), `taTAgata` (t,
  `Ensink 1964 : 73, vii`) and `vErocana` (v, `Ensink 1964 : 180, viii`).
- **`(pw) : 1531`** — a lowercase parenthetical source name is not matched,
  because OWNER's name class is capital-initial (the canonical `PW : 1531`
  parses); admitting lowercase parenthetical tokens would let parenthetical
  gloss asides be read as owners, so it stays out by the same name-class design
  as `Meister (2.1)`. Drops 1 s-section owner (`sucCardis → s.v. suchardís
  Graßmann 1873 (1996). (pw) : 1531`); a rare, well-formed citation style, not
  a typo.
- These are rare (b: 7 / 2,655 = 0.26%; c: 9 / 1,828 = 0.49%), terminal,
  and confined to a few works (Meister 1988, Walter 1893, Böhtlingk 1887);
  the safely-fixable nested/variant-paren gap is already fixed. Roman and
  asterisk pages share one cause — admitting them as page tokens
  destabilises segment/owner alignment — so both stay out by design.

## 2026-06-20

### Added
- `schemas/pwg_ru_final_card.schema.json` and
  `validate_final_card_schema.py` define the final translated-card + judge
  contract, including auditable Apresjan `differentia` evidence.
- `validate_assembled_export.py` checks deterministic assembled-card JSONL
  exports, with full count-match mode and bounded supervised-sample mode.
- `run_batch.py validate_review` and `run_batch.py apply_review` make the
  review store gate machine-checkable before any row can become print-ready.
- `gold_validate.py`, `gold_ingest.py`, and `gold_agreement.py` validate human
  gold labels, ingest release-bound JSONL, and compute Wilson precision plus
  double-review agreement metrics.
- `export_interop.py` and `validate_interop.py` generate and validate minimal
  TEI Lex-0, OntoLex, and Russian reverse-index artifacts.
- `make_edition_cut.py`, `validate_release.py`, `CITATION.cff`, and
  `DOI_PLAN.md` add the immutable edition-cut skeleton and manifest hash check.
- Nonhuman print-gate helper tooling now prepares reviewer work without filling
  human decisions: `run_batch.py review_report`, `gold_status.py`,
  `gold_packet.py`, `gold_double_review_queue.py`, and `release_readiness.py`.
- `gold/REVIEWER_HANDOFF.md` gives reviewers one place for allowed enum values,
  protected columns, validation commands, and the G5-G7 handoff flow.
- `gold_packet_verify.py`, `gold_double_review_verify.py`, and
  `preflight_remaining_gates.py` verify reviewer packets, second-review queues,
  and the compact "what's left?" status without inferring any human labels.
- `gold_ingest_double_review.py` bridges filled wide double-review queues into
  long-form reviewer JSONL that `gold_agreement.py` can score.
- Review-gate fixture coverage now exercises blank decisions, invalid approvals,
  explicit `apply_review`, and fail-closed interop export without touching the
  real local translation store.

### Changed
- `assemble.py build` now writes to temp files and installs outputs only after
  successful completion, protecting `assembled_cards.jsonl` from killed-run
  corruption.
- Failed atomic replacement now leaves the previous assembled export untouched
  and keeps the temp file for manual recovery instead of unlinking the old file.
- `assemble.py build` now precomputes corpus evidence once per build, uses
  `corpus_lexicon.jsonl` rows for export-time examples instead of per-card
  SQLite FTS, and supports grouped-card chunks via `--offset`, `--out`, and
  `--quarantine`.
- The top-level AI/release status now says the core release machinery is ready
  but print remains blocked by human review, human gold labels, double-review
  agreement, and a real immutable edition cut.
- `roadmap_check.py` now detects gate status drift between the aggregate
  scientific-hardening JSON and the JSONL gate ledger.
- Release manifest validation now rejects missing/null gate status maps and
  checks manifest gate statuses against the edition's copied gate ledger.
- The monorepo CI/local fixture checks now exercise final-card schemas,
  gold-label packets, double-review queues, interop fixture exports, and a
  fixture edition cut without requiring local gitignored production data.
- `run_batch.py` and `release_readiness.py` accept `PWG_RU_STORE`,
  `PWG_RU_REVIEW_Q`, `PWG_RU_REVIEW_CSV`, and `PWG_RU_REVIEW_REPORT` path
  overrides so review-gate tests can run against disposable fixture stores.
- Full interop export now validates: `release/tei_lex0.xml` and
  `release/ontolex.ttl` each cover 120,173 lexical entries, and
  `release/reverse_index.jsonl` has 209,319 Russian-to-Sanskrit rows.

## 2026-06-19

### Added
- Machine-readable scientific-hardening roadmap and print-blocking quality gates:
  `roadmap/scientific_hardening.json`, `roadmap/quality_gates.jsonl`, and
  `src/roadmap_check.py`.
- `src/pilot/run_real_test.py` audit preflight was exercised with a synthetic
  `ap` workflow output, proving the collect → protected-card preservation →
  `nws_split.py check` → report path before the June-22 Max run.
- `run_batch.py review_csv` exports `_review_queue.jsonl` to a spreadsheet-ready
  `_review_queue.csv` with blank human-review columns (`reviewer_id`, `decision`,
  `edit`, `notes`) while leaving review state unchanged.
- `gold/HUMAN_GOLD_PROTOCOL.md` defines the human gold-set labeling protocol,
  double-review/adjudication workflow, and acceptance criteria; `gold_review_csv.py`
  exports the existing 320-row balanced scaffold for reviewers.
- `schemas/pwg_ru_lexicographic_portrait.schema.json` and
  `validate_portrait_schema.py` define and check the v1 Apresjan portrait
  contract for live `microstructure.portrait()` output.

### Changed
- Modern Sanskrit-Russian sources with project approvals are now marked
  publishable with attribution/provenance, not evidence-only; see
  [RIGHTS_APPROVALS.md](RIGHTS_APPROVALS.md).
- Shared the case-collision-safe filename encoder across NWS scrape/split/audit,
  pilot generation, and merge lookup; forbidden Windows filename characters are
  escaped reversibly.
- `_pilot_collect.py` now writes audited `<safe>.merged.md` files directly using
  `safe_name()`; the real-test auditor no longer needs a brittle external
  `<key>.md` copy bridge and uses the same filename encoder as the rest of the
  pipeline.
- `run_real_test.py prep` was refreshed for the June-22 batch window
  (`OFFSET=0`, `LIMIT=10`): `as As Ap api amfta agni Atman anu arjuna arTa`,
  now correctly all fresh after exact-case output checks.
- `run_pilot_wf.js` now loads the canonical final-card schema instead of
  carrying a prompt-local schema copy.

### Fixed
- Corpus harvest no longer lemmatizes Sanskrit proper names such as `Агни` to
  unrelated Russian verbs such as `агнуть`.
- `scale_route.py` now routes by the protected microstructure sense parser.
- `assemble.py` quarantines lossy round-trip records instead of emitting them
  into the normal assembled card stream.
- `run_batch.py migrate_legacy` backfills old translation-store rows and marks
  unverifiable legacy cards `legacy_needs_review`.
- Protected hand-authored pilot cards (`aMSa`, `anna`, `ap`) are preserved during
  real-test collection/audit, while still being audited by `nws_split.py`.
- Legacy `.merged.md` compatibility checks now require exact filenames, avoiding
  Windows case-insensitive false positives such as `Ap` being treated as protected
  because `ap.merged.md` exists.
- Generated the missing writable a-section input for `arI|a` (`|` escaped as
  `~007c`); pilot inputs now cover 12,156/12,156 a-section manifest cards.
- Materialized the human review worklist with `run_batch.py review`: 217
  `legacy_needs_review` cards, severity-sorted, with no reviewer decisions
  advanced.

## 2026-06-16

### Added
- **Corpus harvest layer** ([HARVEST.md](HARVEST.md)): `build_ls_map.py` +
  `ls_source_map.json` (PWG `<ls>`→stratum, 45 sources = 72.4% of 772k
  citations, 29.8% corpus-harvestable) and `corpus_harvest.py` — SLP1 key →
  Russian renderings, lemma-grouped (pymorphy3), POS-filtered, stratified, with
  the `<ls>`-cited stratum first and a `--raw` escape for particle headwords.
- **Recurring deterministic integrity auditor** (`_audit.py`): flags
  placeholder leak / non-Cyrillic / `ru==sa` / `√`-keys / dups / stratum
  mismatch; run at each build milestone; exit-code verdict.
- **Live cost/ETA watcher** (`_watch.py`): progress bar, $ spent / needed, ETA,
  measured over a live window (not the append-only file's stale ctime).
- **Methodology review** ([METHODOLOGY_REVIEW.md](METHODOLOGY_REVIEW.md)):
  grounded 5-lens review (FAIR/DH, bilingual lexicography, corpus-NLP eval,
  standards/interop, editorial) → prioritized roadmap.
- **Priority-1 fixes**: per-card **provenance** (model ids, prompt hash,
  `pwg.txt` commit, run id, timestamp + persisted senses); **human-review state
  machine** + `run_batch.py review` editor worklist; **per-sense rights gate**
  (`corpus_gate.RIGHTS`/`publishable()`) + **CC BY-SA 4.0** data licence
  ([DATA_LICENSE.md](DATA_LICENSE.md)).
- **Coverage honesty check** (`corpus_harvest.py coverage`): per-stratum rows /
  groups-done flags EMPTY/thin strata.
- **Apresjan theoretical grounding** ([APRESJAN.md](APRESJAN.md)) and a
  **failure gallery** ([failures/FAILURE_GALLERY.md](failures/FAILURE_GALLERY.md)).

### Changed
- Corpus-lexicon build **batched** (~8 verse-units / DeepSeek call, 12 workers,
  biggest-first); quality verified equal to single-call, ~3–4× faster.
- `build_strata.count_groups()` now requires a Cyrillic translation, so sizes /
  ordering reflect genuinely-translated material (78,139 → 58,897 genuine groups).

### Fixed
- **Placeholder fabrication (build-stopping)**: untranslated `…` verses were fed
  to DeepSeek, which hallucinated 166k/204k rows (81%). Fixed with a Cyrillic
  guard; recovered to 26,277 genuine rows. See the gallery.
- Footnote-overwrites-translation; `√` leaking into keys; commentary
  cross-segment duplication; biggest-first cost mis-projection; frozen/dead-build
  liveness misreads. See [failures/FAILURE_GALLERY.md](failures/FAILURE_GALLERY.md).

## 2026-06-15

### Added
- **Source extraction** (`build_src.py`): 5 Sanskrit–Russian dictionaries
  (Кочергина, Кнауэр, Фриш, Смирнов, Коссович) pulled from SamudraManthanam →
  gitignored `src/*.jsonl` (~57,640 keyed entries).
- **Stage-4 corpus gate** (`corpus_gate.py`): SLP1 join over the 5 dicts + the
  parallel-corpus query; non-blocking 2-signal annotation (correctness vs
  independent dicts; reference-agreement vs KOW). Coverage measured honestly
  (correctness 16.4% / KOW 8.0% / corpus ~14–15%; dominant `no-check`).
- **Pipeline** (`pwg_mask.py` masker, `assemble.py` harvest, `run_batch.py`
  driver): mask German skeleton → harvest attested senses → translate (Sonnet
  4.6 on Max) → judge (Opus 4.8) → re-translate. Pilot: 6/6 then ~88–95%
  first-pass publishable.
- **Stratification** (`build_strata.py` + `corpus_strata.json`): 121 corpus
  texts by genre (Renou) + date (Dharmamitra Gibbs median + 95% CI) + period.

### Changed
- Strategy pivots: **harvest-first** (assemble Russian from existing material;
  harvested meanings become additional *attested senses*), then **corpus-first**
  (build the corpus word-alignment lexicon before bulk translation), then
  **quality-over-quantity** (it becomes a printed scholarly dictionary).

## 2026-06-14

### Added
- **pwg_ru kit scaffolded** (committed `384fedb`), mirroring the completed
  `mw_ru`: editor doc [pwg_ru.md](pwg_ru.md) + stage prompts
  ([pwg_ru_prompts/](pwg_ru_prompts/)) (translate → 2 QA judges → re-translate →
  corpus check). Headline format rule: PWG `{%…%}` wraps both German glosses
  (translate) and Latin (leave). Model unified to Opus 4.8.
