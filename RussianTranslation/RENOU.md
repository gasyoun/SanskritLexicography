# Renou language-state tagging

Every dictionary headword/sense is classified into one of **Louis Renou's five
states of Sanskrit** (*Histoire de la langue sanskrite*, 1956 — the five chapters),
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
registers a flat I–V tag cannot express — notably **`épigraphique`** (inside Ch. II,
p. 94) and **`bhāṣya`** = commentary language (the lead of Ch. IV, p. 133, with its
own grammar), which fits none of the five. The verified book structure is in
[`../../VisualDCS/docs/Renou_1956_structure.md`](../../VisualDCS/docs/Renou_1956_structure.md);
the full design (orthogonal, multi-label, ~20-register lattice, combined detectors) is
in [`RENOU_SUBSECTIONS_PLAN.md`](RENOU_SUBSECTIONS_PLAN.md).

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

**Pending:** **`épig`** (no inscription sigla in either CANON yet — needs a curation
pass, Phase 3) and the inline dicts' (`ap`/`ben`/`bhs`) `<ls>` register route (they use
`renou_sigla`, so their registers are corpus-only today). Registers do **not** affect
the state fields.

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
| `renou.py`, `renou_sigla.py` | ✓ | siglum→state resolvers (PWG/MW + Apte/Benfey/BHS) |
| `build_ls_map.py`, `build_ls_map_mw.py` | ✓ | build the `<ls>` source maps |
| `ls_source_map.json`, `ls_source_map_mw.json` | ✓ | curated source → state (small, auditable) |
| `build_dcs_renou.py` | ✓ | scan DCS corpus → lemma→state index, with per-state `state_support` (n_texts + confidence) |
| `tag_dict_from_source.py`, `tag_mw_from_source.py` | ✓ | per-dict `<ls>`+DCS tagger |
| `enrich_renou_dcs.py`, `enrich_renou_bhs.py`, `enrich_renou_wisdomlib.py` | ✓ | the DCS / BHS / wisdomlib enrichers |
| `annotate_renou.py`, `add_corpus_renou.py` | ✓ | per-sense card backfill; raw-text corpus augmenter |
| `renou_pipeline.py` | ✓ | the driver (this system's entry point) |
| `renou_portrait.py` | ✓ | editor-facing label (`portrait`) + oldest-sense reorder, on a `{code}.renou.jsonl` |
| `renou_audit.py` | ✓ | inter-signal agreement audit (the validation tool above) |
| `dcs_lemma_renou.json`, `{code}.renou.jsonl`, `*_renou*.jsonl`, `renou_audit_report.md` | gitignored | derived indices + audit report (regenerated) |

The wisdomlib fetcher itself (`definitions.py`, producing `word_traditions.jsonl`)
lives in the **SamudraManthanam** repo (`web/corpus_builder/wisdomlib/`); it is
Cloudflare-gated per-IP, so the `wl` layer is partial (run gently from a residential
connection). See that repo's wisdomlib README.

## Provenance example

```json
{"iast": "akṣobhya", "renou_enriched": ["III","V"],
 "renou_provenance": {"III": ["dcs"], "V": ["ls","dcs","bhs","wl"]}}
```
`akṣobhya` is Epic (III) by corpus attestation, and Buddhist (V) confirmed by all
four signals — its citation, corpus, the BHS register, and wisdomlib's tradition tag.
