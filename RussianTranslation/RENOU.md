# Renou language-state tagging

_Created: 24-06-2026 · Last updated: 01-07-2026 (archive layer added 01-07-2026)_

Every dictionary headword/sense is classified into one of **Louis Renou's five
states of Sanskrit** (*Histoire de la langue sanskrite*, 1956 — the five chapters;
[source PDF](https://github.com/gasyoun/VisualDCS/blob/main/docs/Histoire_de_la_langue_sanskrite_Renou_Louis.pdf),
[verified table of contents](https://github.com/gasyoun/VisualDCS/blob/main/docs/Renou_1956_structure.md)),
from **four independent, provenance-tagged signals**. The state is *diachronic /
register* ("which Sanskrit is this attested in"), not semantic, and a word is
**multi-label** (attested across eras carries all applicable states).

## The five states

| | State | Covers |
|---|---|---|
| **I** | Vedic | Saṃhitā, Brāhmaṇa, Upaniṣad, Sūtra, Vedāṅga |
| **II** | Pāṇinian | the classical norm & grammarians' Sanskrit (Pāṇini, Patañjali) |
| **III** | Epic & prolongements | Mbh, Rām, Harivaṃśa, Gītā, Purāṇa, Smṛti, Tantra |
| **IV** | Classical | kāvya, drama, kathā, classical śāstra, kośa, later grammar |
| **V** | Buddhist / Jaina | Buddhist Hybrid & Jaina Sanskrit |

## The four signals (`renou_provenance`)

Each state on a card records *which signal(s)* support it, so trust is transparent.

| Source | What it means | Determinism | Trust |
|---|---|---|---|
| `ls` | the dictionary's own `<ls>` **citation** resolves to a text of that state | deterministic, no LLM | strongest (the lexicographer cited it) |
| `dcs` | the headword **lemma is attested** in a DCS corpus text of that state | deterministic (corpus scan) | strong (real attestation) |
| `bhs` | the headword is in **Edgerton's BHS** dictionary → attested in Buddhist Sanskrit | deterministic (set membership) | V only; register-attestation (a common word *used in* Buddhist texts also qualifies) |
| `wl` | **wisdomlib** groups the word under a Buddhism/Jainism tradition section | deterministic parse of fetched pages | tertiary corroboration (web-fetched, Cloudflare-gated) |

A state backed by several sources (e.g. `V: ["bhs","wl"]`) is strong; `bhs`-only V
is the weakest (register attestation, not a semantic Buddhist claim).

## Per-dictionary coverage

Canonical index `{code}.renou.jsonl`, keyed by `key1` (joins to the Russian cards).
**8 dictionaries · 770,292 entries** (`renou_pipeline.py --all`, 2026-06-24):

Counts are **after** the DCS min-support policy (see *Validation* below).

| Dict | Entries | I | II | III | IV | V | V sources (ls·dcs·bhs·wl) |
|---|--:|--:|--:|--:|--:|--:|---|
| PWG | 123,366 | 31,090 | 18,627 | 45,351 | 59,946 | 17,357 | 0·11,341·10,343·23 |
| MW | 286,560 | 76,328 | 28,705 | 111,203 | 137,232 | 56,434 | 4,503·38,200·33,949·50 |
| PW | 170,556 | 24,238 | 5,639 | 36,427 | 38,091 | 17,694 | 0·10,340·11,481·30 |
| AP | 90,654 | 9,203 | 3,873 | 20,856 | 22,802 | 7,138 | 0·4,774·3,650·5 |
| AP90 | 34,882 | 6,360 | 2,607 | 9,681 | 13,013 | 5,011 | 0·3,646·2,307·2 |
| BEN | 17,310 | 6,010 | 2,347 | 11,683 | 11,485 | 5,468 | 0·4,378·2,580·0 |
| SCH | 29,125 | 3,358 | 1,241 | 5,783 | 7,747 | 4,375 | 0·2,407·3,157·2 |
| BHS | 17,839 | 1,488 | 624 | 2,878 | 2,820 | 13,622 | 13,172·2,877·0·27 |

Notes: **V**'s sources are complementary — `<ls>` gives it only where a dict cites
Buddhist texts (MW, BHS); `dcs` + `bhs` carry it everywhere else; `wl` is the partial
(63-word) validated sample. PWG/PW/AP/AP90/BEN/SCH have no Buddhist source in their
`<ls>` canon, so their V is entirely corpus + register (`dcs`+`bhs`) — which is exactly
the gap the BHS transfer closed.

## Validation — inter-signal agreement audit

`renou_audit.py` validates the tags **automatically** (no human labels) by cross-
checking the four signals against each other, treating `<ls>` (the lexicographer's
own citation) as the trusted anchor. It targets the dominant accuracy risk: **`dcs`
over-tagging**. The DCS index is keyed by bare lemma string, so homographs collapse
to one entry carrying the *union* of all their eras (`akāra`, the name of the letter,
inherits I–V from 27 texts), and the downstream tagger keeps only the state *list* —
a state from one occurrence is indistinguishable from one in a hundred.

Findings (`renou_audit_report.md`, 2026-06-24):

- **`dcs` widening is the dominant disagreement.** Among entries carrying *both* `ls`
  and `dcs`, `dcs` adds eras beyond what `ls` cites (`dcs_adds`) far more often than it
  agrees exactly — MW 53 %, BEN 77 %, AP90 76 %, AP 62 %, SCH 57 %, PW 45 % (only
  PWG/PW reach ~46 % exact). `dcs_misses` (too narrow) is everywhere ≤10 %.
- **Most `dcs` states are uncorroborated.** Share of `dcs` (entry, state) assertions
  with no `ls` and no `bhs` backing: PWG 42 % · BEN 59 % · MW 64 % · AP 76 % · AP90 77 %
  · BHS 79 % · PW 86 % · SCH 90 %. (`ls`-rich PWG is the most self-corroborating.)
- **5-state inheritance.** 4.4 % (PW) – 11.4 % (BEN) of `dcs`-hit entries inherit a
  maximal I–V lemma — only 1.4 % of DCS lemmas are 5-state, but they are the most
  frequent ones, so they over-tag disproportionately.
- **Suspects are closed-class.** The top over-tag patterns (tight `ls` span → I–V on a
  250+-text lemma) are exactly the particles and pronouns: `ca`, `eva`, `as`, `na`,
  `iti`, `api`, `idam`, `tad`, `yad`.

Root cause = (1) homograph collapse in the lemma-keyed index and (2) discarded per-
state evidence depth. The audit itself is read-only — it changes no tags, only
measures them.

```sh
python renou_audit.py            # -> renou_audit_report.md (+ console summary)
```

### The min-support fix (applied)

`build_dcs_renou.py` now records, per lemma, **`state_support`** = `{state: {n_texts,
best_confidence}}` (lossless), and `renou.filter_dcs_states()` applies the policy at
*tagger* time (so the threshold is tunable without rescanning): **keep a `dcs` state
iff it is attested in ≥ `DCS_MIN_SUPPORT` (=2) corpus texts, OR at least one of those
texts is confidently typed** (authoritative DCS genre / curated Buddhist–grammar name
hint). This drops the thin, low-confidence tail — single date-fallback occurrences —
while leaving genuinely-attested and curated states intact. Tune with
`tag_dict_from_source.py CODE --dcs-min-support N`.

Effect (2026-06-24, default threshold): **9.9 % of `dcs` state-assignments pruned**
across 14.8 % of lemmas, almost all of it spurious **IV** (the `date ≥ 400` fallback
bucket: 9,736 dropped) and **I** (2,923); **0** state-II and state-V assignments
dropped, because those come only from confidently-typed Vyākaraṇa / Buddhist texts —
so the curated signal is untouched. Only 33 maximal lemmas fall below five states.

The residual `dcs_adds` breadth (MW 52 %, BEN 76 %) is **not** pruned, and that is
correct: it is dominated by genuinely era-neutral high-frequency words — `ca`, `idam`,
`akāra` carry well-attested high-confidence support in *every* era, so their I–V span
is corpus-accurate, merely uninformative. That is a *display* concern, not a tagging
error to delete: `renou_portrait.portrait()` now sets **`renou_low_info: True`** on an
all-era span (tunable via `LOW_INFO_MIN_STATES`) so a UI can de-emphasise the badge
rather than show a meaningless five-era label.

## Register axis (subsections) — corpus route live

The five states are Renou's five **chapters**. His **subsections** are distinct
registers a flat I–V tag cannot express — all twenty of them, e.g. `épigraphique`
(Ch. II, p. 94) or `bhāṣya` = commentary language (Ch. IV, p. 133, with its own grammar),
but equally the drama, the narrative, the Purāṇa, the grammarians' norm: each is a register,
not a period, and fits none of the five states as such. The verified book structure is in
[`../../VisualDCS/docs/Renou_1956_structure.md`](../../VisualDCS/docs/Renou_1956_structure.md);
the full design (orthogonal, multi-label, ~20-register lattice, combined detectors) is
in [`RENOU_SUBSECTIONS_PLAN.md`](RENOU_SUBSECTIONS_PLAN.md). The **full catalog of all 20
registers** (Renou subsection + page, coverage, detector route) is in
[`RENOU_REGISTERS.md`](RENOU_REGISTERS.md).

**Built — two routes (additive; the state axis is unchanged).** Every entry carries an
orthogonal **`renou_register`** + `renou_register_provenance`:

- **DCS corpus** — `build_dcs_renou.py` emits per-lemma `register` + lossless
  `register_support` (genre→register + name-stem detectors, esp. `bhāṣya` by
  `*bhāṣya/ṭīkā/vṛtti/…`); same min-support policy (`renou.filter_dcs_registers`).
- **`<ls>` citation** — `renou_register.py` maps each cited siglum's
  `ls_source_map*.json` record → register(s) (`renou.ls_registers_for_text`); the only
  route for **`jaina`** (MW `Jain`/`Kalpas` → 288 entries) and a second signal for
  **`bhāṣya`** (commentary sigla Sāy/Kāś/Pat → 4,109 MW entries).

Per-register provenance is `["dcs"]`/`["ls"]`/both. Coverage: ~38–41 % of entries carry
≥1 register; `bhasya` ~14 k (PWG) / 45 k (MW).

**Audit + display.** `renou_audit.py` has a register section (coverage + per-register
`ls`/`dcs`/`both` provenance + register-low-info), and `renou_portrait` emits a
`renou_register_label` (+ a `bhāṣya` editorial note, low-info flag at ≥10 registers).

**`épig` + inline dicts (done).** A dedicated detector (`renou_register.dedicated_registers`)
reads an inscription marker in the `<ls>` text (PWG `Inschr.`, MW/Apte `Inscr.`) → `epig`
(MW 687, AP 17, PWG 9, …; sparse by nature). The inline dicts get registers via
`renou_sigla.SIGLUM_REGISTER` (+ `bhs`→`bauddha` wholesale). Only `hors_inde` stays 0
(no source). Registers do **not** affect the state fields — the axis is complete.

**Attestation-level register (corpus provenance, done).** The two routes above are
**headword-level** (one register set per dictionary entry). [`renou_corpus_map.py`](src/renou_corpus_map.py)
adds a third, **attestation-level** route: it resolves each `corpus_lexicon.jsonl` pairing's
`genre` onto the same 20-register lattice (reusing `renou_register._genre_register`, plus a
work-slug override for RV-vs-AV Saṃhitā and Buddhist kāvya, plus a supplement for corpus-only
genres — Upaniṣad, commentary, darśana, tantra, kāma). Full coverage, no unmapped genres.
`corpus_provenance.py --renou <form>` tags each Russian rendering with its register(s) and a
per-query register profile; `renou_corpus_map.py` alone prints corpus-wide register counts
(epic 61.0 %, rgveda 14.4 %, atharva 5.6 %, kavya 3.9 %, smrti 3.6 %, upanisad 3.5 %, karika
2.6 %, katha 2.0 %, tantra 1.2 %, bhasya 1.2 %, bauddha 1.1 %, over all 1,091,528 aligned
pairs). This is the register axis grounded in actual parallel-corpus usage rather than a
dictionary's `<ls>` sigla — full write-up in [`CORPUS_PROVENANCE.md`](CORPUS_PROVENANCE.md#renou-register-layer-attestation-level).

## Archive layer — Renou applied to mailing-list discourse

**Location:** The INDOLOGY-L Archive Atlas lives in the `Indology/` subdirectory of [github.com/gasyoun/IndologyScholars](https://github.com/gasyoun/IndologyScholars)
([local: C:\Users\user\Documents\GitHub\IndologyScholars\Indology](file:///C:\Users\user\Documents\GitHub\IndologyScholars\Indology)).
It is a **downstream application** that reuses the Renou state/register vocabulary for a **single, defined corpus**:
40 years of public mailing-list discussion (INDOLOGY-L, 62k+ messages) with a different evidence type (keyword
matching on subject lines, not lexical/corpus attestation). **Note:** Renou tagging is NOT yet applied to the
Zograf or Roerich conference datasets also housed in IndologyScholars (in the `conferences/` directory);
those remain analyzed separately via the parent project's authority-control and topic taxonomy.

**Input.** Subject-line text from every message in the **INDOLOGY-L mailing list archive** (since ~1989).
A parallel project studying the Zograf and Roerich **conference proceedings** (in the parent IndologyScholars
repo's `conferences/` directory) is NOT yet tagged with Renou; it uses separate topic taxonomies. The archive
atlas is deliberately scoped to the one, most complete data source (INDOLOGY-L) to avoid fragmentation.

**Output.** Per-message and per-thread Renou tags (`state`, `register`, `confidence`):
- Exact keyword match → confidence `high`
- Fuzzy / substring match → confidence `medium`
- Absent → no tag (sparse by design)

**Evidence.** A rule table [`renou_subject_rules.csv`](https://gasyoun.github.io/IndologyScholars/IndologyArchive/data/curation/renou_subject_rules.csv)
maps keyword phrases (e.g., "Vedic", "Ṛgveda", "Buddhist", "commentary") → (state, register, confidence).
Rules are curated by keyword, not by LLM; the tagger is simple pattern-matching against subject lines.

**Use case.** **Finding discussions**, not dating words. A researcher asking "which INDOLOGY-L threads
discuss Purāṇic Sanskrit?" or "which conversations mention epigraphic evidence?" can now scan the
filtered message list and thread summaries. The Renou tagging provides **topical navigation** over
a 40-year archive that would otherwise require full-text search or manual browsing.

**Coverage.** Currently 6,217 / 62,112 messages (10.01 %) and 3,309 / 24,033 threads (13.77 %) are
tagged. Most subject lines don't signal a Sanskrit-linguistic category explicitly, so the sparse
coverage is expected. A blank tag = "not classified by this layer," not "not relevant."

**Relationship to dictionary layer.** The dictionary Renou system (SanskritLexicography, this repo)
is **canonical**: it defines the five states, twenty registers, and the four-signal evidence scheme
(LS/DCS/BHS/wisdomlib). The archive layer is a **downstream instantiation** that borrows these
definitions wholesale but with simpler evidence (keywords) applied to a new corpus (subject lines).
Both are read-only frontends; curation is rule-based, not LLM-based, so the archive remains fully
deterministic and auditable.

## Use cases

Both axes are per-sense, multi-label, and provenance-graded, so they answer queries a
flat headword list can't. Join any `{code}.renou.jsonl` to the Russian cards by `key1`.

**In the dictionary layer** (this repo, RussianTranslation/):


**Dictionary layer — per-word, per-sense, multi-signal:**

**State axis (I–V) — *when* is this Sanskrit?**
- **Diachronic filter / archaism hunt** — `renou_enriched == ["I"]` (Vedic-only) surfaces
  words that dropped out after the Saṃhitās; `"I" in … and "IV" in …` finds the long-lived
  core. Good for a learner's "Vedic vs Classical" layer.
- **Oldest-sense ordering** — `renou_portrait.order_senses_oldest_first` floats the
  earliest-attested meaning first (genetic, not alphabetical) — the PWG sense-order study's
  payload.
- **Date a headword's currency** — the I–V span + `renou_oldest` = "first attested Vedic,
  still live in kāvya."
- **Trust grading** — prefer `ls`-backed states (the lexicographer cited it) over
  `dcs`-only (corpus attestation) over `bhs`-only V (register, not a Buddhist-semantic
  claim); the `renou_low_info` flag hides era-neutral function words (`ca`, `idam`).

**Register axis — *what kind* of Sanskrit?**
- **Build a register glossary** — `renou_glossary.py REGISTER` filters `renou_register`
  to one code for a **kāvya** poetic lexicon, a **bauddha** Buddhist glossary, a **jaina**
  Jaina glossary, or the **bhāṣya** scholastic/meta-language vocabulary. Shipped examples
  in [`glossaries/`](glossaries/README.md): épigraphique (709 words, **68 % corpus-absent**),
  bhāṣya (14,498), jaina (286).
- **Epigraphic vocabulary** — `epig` isolates the donative/administrative/regional terms
  inscriptions use (`akṣayanīvī` "perpetual endowment", regional names) — a ready feed for
  epigraphists.
- **Cross-axis queries** — `state I + register bhasya` = Vedic words the commentarial
  tradition kept alive; `register kavya & not state I` = vocabulary born in classical poetry.
- **Translation register-matching** — a `kavya` word cues poetic Russian, a `bhāṣya` word
  technical/terse Russian, a `bauddha` word Buddhist terminology — drives the `pwg_ru`
  style choice per sense (the Apresjan register-judgment hook).
- **Headword genre profile** — the register set shows which text-types actually use a word
  (drama vs epic vs commentary), independent of its date.

**Attestation-level register — *which register is this specific rendering from?***
- **Per-sense register instead of per-headword** — `python src/corpus_provenance.py <form>
  --renou` answers "which register does *this* Russian meaning belong to?" grounded in the
  actual verse it was mined from, finer-grained than the headword-level `renou_register`
  (a headword can span several registers; a single attestation sits in exactly one text).
- **Corroborate or contest a dictionary's `<ls>` register** — compare a headword's
  `renou_register` (from citation sigla) against its attestations' corpus registers; agreement
  strengthens trust, disagreement flags a citation worth checking.
- **Register×period distribution studies** — `renou_corpus_map.py`'s corpus-wide counts
  (epic 61 %, ṛgveda 14.4 %, kāvya 3.9 %, bhāṣya 1.2 %, …) give a real-usage baseline to
  compare against headword-level register coverage — where do dictionaries over/under-cite
  a register relative to how often it's actually attested?
- **Ground a translation choice in a cited register** — when justifying a `pwg_ru` style
  pick, cite not just "this is a kāvya word" but the specific attested register of the
  Russian rendering used, traceable to `work:passage`.

**Archive layer — topical discovery in mailing-list discourse:**
- **Browse by Sanskrit tradition** — filter INDOLOGY-L threads tagged `state I` (Vedic) or `state V` (Buddhist)
  to find discussions of interest without scanning all 24k threads. The state classifier answers:
  "which conversations are about this era?"
- **Register-specific topic finding** — search for `register bhāṣya` (commentary language) to find
  technical/scholiast discussions, or `register epig` (inscriptions) to locate numismatic/paleographic threads.
- **Trend over time** — the [dashboard](https://gasyoun.github.io/IndologyScholars/IndologyArchive/dashboard/index.html)
  shows which Sanskrit traditions dominate discussion across decades (e.g., "Buddhist Sanskrit topics spiked in 2005").
- **Hybrid discovery** — combine state + register filters: "Vedic + commentary = threads where classical
  grammarians discuss Vedic usage" — a rare cross-disciplinary intersection.

**Archive-discourse layer — *where do Renou categories surface in scholarly discussion?***

Since 2026-06, Renou's five-state and twenty-register taxonomy has been extended beyond
dictionaries into a **second application domain**: the [INDOLOGY-L Archive Atlas](https://github.com/gasyoun/IndologyScholars)
(in [C:\Users\user\Documents\GitHub\IndologyScholars](file:///C:\Users\user\Documents\GitHub\IndologyScholars))
applies the same vocabulary to classify public mailing-list **subject lines**, not dictionary
headwords. This is a new proof of concept for Renou's **reusability as a discourse-indexing taxonomy**
across domains beyond lexicography.

**How it works.** The archive tagger runs an evidence matcher over 62,112 messages (24,033 threads)
from INDOLOGY-L (spanning ~40 years, 1989–2030), scoring subject-line keywords against the same
five-state + twenty-register coordinate system. A message tagged `III·purana` means "this discussion
explicitly signals Epic or Purāṇic Sanskrit, detectably via subject-line keywords." The goal is
**topical discovery**: answering "which threads on the Vedas / on commentarial language / on Buddhist
Sanskrit am I interested in?" rather than lexical attestation.

**Live outputs** in GitHub Pages ([`gasyoun.github.io/IndologyScholars/IndologyArchive`](https://gasyoun.github.io/IndologyScholars/IndologyArchive)):
- [`dashboard`](https://gasyoun.github.io/IndologyScholars/IndologyArchive/dashboard/index.html) — interactive chart of state + register coverage across decades
- [`renou_messages.csv`](https://gasyoun.github.io/IndologyScholars/IndologyArchive/data/processed/renou_messages.csv) — all 6,217 / 62,112 messages with matched state/register
- [`renou_message_matches.csv`](https://gasyoun.github.io/IndologyScholars/IndologyArchive/data/processed/renou_message_matches.csv) — per-message: matched keywords + source subject line + thread ID
- [`renou_thread_matches.csv`](https://gasyoun.github.io/IndologyScholars/IndologyArchive/data/processed/renou_thread_matches.csv) — aggregate: thread's dominant state/register + sample messages
- [`renou_coverage.csv`](https://gasyoun.github.io/IndologyScholars/IndologyArchive/data/processed/renou_coverage.csv) — coverage stats (state I: 418 threads, V: 224 threads, …)
- editable [`renou_subject_rules.csv`](https://gasyoun.github.io/IndologyScholars/IndologyArchive/data/curation/renou_subject_rules.csv) — the keyword matching rules (tunable, rule-based, not LLM)

**Sparse by design.** The atlas currently classifies 6,217 / 62,112 messages (10.01 %)
and 3,309 / 24,033 threads (13.77 %) by subject-line evidence. A blank Renou field means
"not classified by this layer," not "not relevant to Renou" — most discussion titles don't
signal a Sanskrit-linguistic register explicitly. This is the opposite of dictionary entries,
where most headwords carry some state/register by construction.

**Different unit of evidence.** Dictionary Renou tags are per-entry/per-sense and
provenance-graded from `<ls>` citation, DCS corpus, BHS dictionary, and wisdomlib scraped traditions.
The archive layer is a **discourse index**: its evidence is the **matched subject term** (keyword),
**confidence label** (exact keyword vs substring vs fuzzy), and the **archive URL + thread context**.
It should be used for **finding discussions to read**, not for lexical attestation — if you want to know
which threads discuss Vedic Sanskrit, this is your tool; if you want to know whether a word is Vedic,
use the dictionary layer instead.

**Relationship to SanskritLexicography.** The dictionary Renou system (this repo, RussianTranslation/)
is the **canonical** state/register definitions + four-signal annotation scheme (LS/DCS/BHS/wisdomlib).
The archive application (IndologyScholars) is a **downstream consumer** of that taxonomy: it borrows
the five states and twenty registers wholesale, instantiates them with a simpler (keyword-based) evidence
layer, and applies them to a new corpus (mailing-list subject lines). The tagger lives in IndologyScholars;
the definitions stay here. Both systems are read-only for end users (the dictionary layer, the archive layer);
curation happens via `renou_subject_rules.csv` (archive keywords) and `ls_source_map.json` + `build_dcs_renou.py`
(dictionary signals).

The two axes compose: `(state, register, provenance)` is an evidence-graded coordinate per
sense — e.g. *akṣobhya* = `III·V` / `purana·tantra·bauddha` / all-four-signals = "an Epic-
and-Buddhist word, used in Purāṇa/Tantra/Buddhist registers, maximally corroborated." Six
**cross-axis slices** (Vedic-in-commentary, born-in-kāvya, the grammatical meta-language, …)
are worked through with anatomy + examples in [`RENOU_CROSSAXIS.md`](RENOU_CROSSAXIS.md); the
per-register empirical findings (bhāṣya as Renou's cross-disciplinary syntactic register; BHS
as a second self-contained lexical world; doctrinal registers = perennial lexicon) are in
[`RENOU_FINDINGS.md`](RENOU_FINDINGS.md). Renou's **nominal-style** thesis (the finite verb
receding Vedic→Classical, bhāṣya more nominal than kāvya) is verified on the corpus in
[`RENOU_NOMINAL_STYLE.md`](RENOU_NOMINAL_STYLE.md).

## Reproduce

```sh
cd RussianTranslation/src
# prereqs (built once):
python build_ls_map.py            # ls_source_map.json      (PWG/PW/PWK/SCH Petersburg sigla)
python build_ls_map_mw.py         # ls_source_map_mw.json   (MW sigla)
python build_dcs_renou.py         # dcs_lemma_renou.json    (scans the DCS corpus; ~2–3 min; gitignored)

# one canonical index per dictionary (all four signals):
python renou_pipeline.py --all [--wl path/to/word_traditions.jsonl]
#   chains:  tag_dict_from_source (<ls>+DCS)  ->  enrich_renou_bhs (+V)  ->  enrich_renou_wisdomlib (+wl)
#   -> {code}.renou.jsonl  +  a states / V-by-source report
```

Individual stages are also runnable standalone (`tag_dict_from_source.py CODE`,
`enrich_renou_bhs.py IN --out OUT`, `enrich_renou_wisdomlib.py IN --wl … --out OUT`).

## Files

| Path | Committed? | What |
|---|---|---|
| [`renou.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou.py) | ✓ | state resolver + min-support policy (`filter_dcs_states`, `filter_dcs_registers`) |
| [`renou_sigla.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_sigla.py) | ✓ | Apte/Benfey/BHS siglum→state **and** `SIGLUM_REGISTER` (inline-dict register route) |
| [`renou_register.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_register.py) | ✓ | register axis: canonical `REGISTERS` lattice + `<ls>` register routes (`ls_registers`, dedicated `epig`) |
| [`build_ls_map.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_ls_map.py), [`build_ls_map_mw.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_ls_map_mw.py) | ✓ | build the `<ls>` source maps |
| [`ls_source_map.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_source_map.json), [`ls_source_map_mw.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_source_map_mw.json) | ✓ | curated source → state + genre/name (drives both axes) |
| [`build_dcs_renou.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_dcs_renou.py) | ✓ | scan DCS corpus → lemma index: per-state `state_support` **and** per-register `register_support` |
| [`tag_dict_from_source.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tag_dict_from_source.py), [`tag_mw_from_source.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/tag_mw_from_source.py) | ✓ | per-dict tagger — emits both `renou_*` (state) and `renou_register*` |
| [`enrich_renou_dcs.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/enrich_renou_dcs.py), [`enrich_renou_bhs.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/enrich_renou_bhs.py), [`enrich_renou_wisdomlib.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/enrich_renou_wisdomlib.py) | ✓ | the DCS / BHS / wisdomlib state enrichers (pass registers through) |
| [`annotate_renou.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/annotate_renou.py), [`add_corpus_renou.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/add_corpus_renou.py) | ✓ | per-sense card backfill; raw-text corpus augmenter |
| [`renou_pipeline.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_pipeline.py) | ✓ | the driver (this system's entry point) |
| [`renou_portrait.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_portrait.py) | ✓ | editor badge: state label + register sub-label + low-info flags + oldest-sense reorder |
| [`renou_audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_audit.py) | ✓ | inter-signal agreement audit — state over-tag suspects **and** register mode |
| [`renou_corpus_map.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/renou_corpus_map.py) | ✓ | attestation-level register: `corpus_lexicon.jsonl` genre → the 20-register lattice; corpus-wide register stats |
| `dcs_lemma_renou.json`, `{code}.renou.jsonl`, `*_renou*.jsonl`, `renou_audit_report.md` | gitignored | derived indices + audit report (regenerated, not on GitHub) |

The wisdomlib fetcher itself (`definitions.py`, producing `word_traditions.jsonl`)
lives in the **SamudraManthanam** repo (`web/corpus_builder/wisdomlib/`); it is
Cloudflare-gated per-IP, so the `wl` layer is partial (run gently from a residential
connection). See that repo's wisdomlib README.

## Provenance examples

Ten actual records, **simple → tough**, pulled live from `pwg.renou.jsonl` /
`mw.renou.jsonl` (2026-06-25 build). Each ends with a one-line conclusion — what
that record teaches about the tagging system, not just what it says.

**1. `aṃśakaraṇa` (PWG) — the floor case: one state, one signal, no register.**
```json
{"iast": "aṃśakaraṇa", "renou_enriched": ["IV"],
 "renou_provenance": {"IV": ["ls"]}, "renou_register": [], "renou_register_provenance": {}}
```
*Conclusion:* the minimum viable tag — a single `<ls>` citation (KAVIKALPADRUMA) puts it
in Classical, nothing else fires because nothing else is attested. No register because
no genre/citation signal maps to one. This is what most of the corpus looks like.

**2. `agnitā` (PWG) — two states, two independent single-source signals, one register.**
```json
{"iast": "agnitā", "renou_enriched": ["I","IV"],
 "renou_provenance": {"I": ["ls"], "IV": ["dcs"]},
 "renou_register": ["brahmana"], "renou_register_provenance": {"brahmana": ["ls"]}}
```
*Conclusion:* the `<ls>` citation (Śatapatha Brāhmaṇa) plants state I *and* the register
`brahmana` in one shot; `dcs` independently adds IV from later corpus attestation. Two
signals agreeing on *nothing* in common is normal — they cover different eras, not the
same claim twice.

**3. `akaca` (PWG) — a state resting on the single weakest signal, alone.**
```json
{"iast": "akaca", "renou_enriched": ["V"],
 "renou_provenance": {"V": ["bhs"]}, "renou_register": []}
```
*Conclusion:* `bhs`-only V is explicitly the weakest tier in the trust ladder (register
attestation, not a semantic Buddhist claim — Edgerton's BHS dictionary happens to include
this word). Trust grading means: don't read "V" here as "this is a Buddhist term," read
it as "a word also found in the Buddhist-Sanskrit lexicographic tradition."

**4. `akarā` (PWG) — one strong state next to one weak state, same entry.**
```json
{"iast": "akarā", "renou_enriched": ["IV","V"],
 "renou_provenance": {"IV": ["ls"], "V": ["bhs"]}, "renou_register": []}
```
*Conclusion:* a card is never uniformly trustworthy — IV here is lexicographer-cited
(strong), V is register-only (weak). A consumer has to grade *per state*, not per entry;
collapsing this to "III states, done" would hide that half the tag is much softer than
the other half.

**5. `akāra` "the letter a" (PWG) — the homograph-collapse case named in the audit.**
```json
{"iast": "akāra", "renou_enriched": ["I","II","III","IV","V"],
 "renou_provenance": {"I": ["dcs"], "II": ["dcs"], "III": ["ls","dcs"], "IV": ["dcs"], "V": ["dcs","bhs"]},
 "renou_register": ["brahmana","upanisad","sutra","vyakarana","epic","purana","tantra","smrti","karika","bhasya","bauddha"]}
```
*Conclusion:* the `<ls>` citation only supports III (Manu, Bhagavadgītā); `dcs` inflates
all five states because the DCS index is keyed by bare lemma, and *every* text that
happens to name the letter "a" — across all eras — collapses onto this one entry. This
is the exact mechanism `renou_audit.py` was built to catch (Validation, above) — a
maximal I–V span here is a red flag, not a rich attestation.

**6. `api` (PWG) — the named over-tag suspect, at full scale.**
```json
{"iast": "api", "renou_enriched": ["I","II","III","IV","V"],
 "renou_provenance": {"I": ["ls","dcs"], "II": ["ls","dcs"], "III": ["ls","dcs"], "IV": ["ls","dcs"], "V": ["dcs","bhs"]},
 "renou_register": ["rgveda","atharva","yajus","brahmana","upanisad","sutra","vyakarana","epic",
                     "purana","tantra","smrti","karika","bhasya","katha","natya","kavya","bauddha"]}
```
*Conclusion:* unlike `akāra`, this maximal span is *not* a collapse artifact — `api` is a
genuinely era-neutral particle with dense `ls` corroboration on four of five states (the
audit's own example list: `ca, eva, api, idam` …). `renou_portrait` flags this as
`renou_low_info: True` precisely so a UI de-emphasises a "this word spans I–V" badge that
is true but tells an editor nothing.

**7. `akheditva` (MW) — register with no corpus route at all: the dedicated Jaina path.**
```json
{"iast": "akheditva", "renou_enriched": ["V"],
 "renou_provenance": {"V": ["ls"]},
 "renou_register": ["jaina"], "renou_register_provenance": {"jaina": ["ls"]}}
```
*Conclusion:* `jaina` has exactly one route in the whole system — MW's own `Jain`/`Kalpas`
citation sigla — because `dcs`'s genre labels never distinguish Jaina texts. Where `dcs`
is silent, the register axis still works, but only as strong as the one signal behind it.

**8. `akratu` (MW) — the register axis citing a commentary, independent of the state axis.**
```json
{"iast": "akratu", "renou_enriched": ["I","IV"],
 "renou_provenance": {"I": ["ls","dcs"], "IV": ["ls","dcs"]},
 "renou_register": ["rgveda","atharva","upanisad","sutra","bhasya"],
 "renou_register_provenance": {"bhasya": ["ls"], "rgveda": ["ls","dcs"]}}
```
*Conclusion:* `bhasya` fires here because MW cites a commentary siglum (Sāyaṇa-class) for
this word, wholly separate from the `rgveda` register the same word also carries — one
headword, cited in both the Vedic hymn tradition *and* the scholiast tradition that glosses
it, exactly the kind of cross-register profile the axis was built to expose.

**9. `akṣayanīvī` (MW) — a register with *zero* state: the axes' independence at its limit.**
```json
{"iast": "akṣayanīvī", "renou_enriched": [], "renou_provenance": {},
 "renou_register": ["epig"], "renou_register_provenance": {"epig": ["ls"]}}
```
*Conclusion:* "perpetual endowment," an epigraphic donative term — the dedicated `epig`
detector (an `Inscr.` marker in the `<ls>` text) fires with **no Renou state at all**,
because inscriptions aren't one of the five chapters. This is the cleanest proof that
register is not derived from state: an entry can have a rich register and an empty state,
or vice versa.

**10. `gam` vs. `gamemahi` (MW headword vs. corpus attestation) — the toughest case: two
axes, two independent systems, disagreeing on purpose.**
```json
// headword-level (mw.renou.jsonl) — the root, maximally frequent, low-info by construction
{"iast": "gam", "renou_enriched": ["I","II","III","IV","V"],
 "renou_register": ["rgveda","atharva","yajus","brahmana","upanisad","sutra","vyakarana",
                     "epic","purana","tantra","smrti","karika","bhasya","katha","natya","kavya","bauddha"]}
// attestation-level (corpus_provenance.py gamemahi --renou) — one specific inflected form
gamemahi -> соединимся      (n=1)  register: atharva   source: 01_atharvaveda:1.4
gamemahi -> да соединимся   (n=1)  register: atharva   source: 07_atharvaveda:10.4
gamemahi -> повстречаться   (n=1)  register: rgveda    source: 07_rigveda:81.2
gamemahi -> хотим встретиться (n=1) register: rgveda   source: 06_rigveda:54.2
```
*Conclusion:* the headword `gam` carries all 17 registers — true, but useless (it is the
`renou_low_info` case at its most extreme, same mechanism as `api` above). The specific
form `gamemahi` narrows that to exactly two registers, each traceable to an exact verse
and a specific published Russian rendering. This is the whole point of the attestation-level
layer in [`CORPUS_PROVENANCE.md`](CORPUS_PROVENANCE.md#renou-register-layer-attestation-level):
per-*sense* register beats per-*headword* register, and it composes with the state axis the
same way — independent, provenance-graded, and only as informative as the evidence actually is.

_Dr. Mārcis Gasūns_
