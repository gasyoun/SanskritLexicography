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

| Dict | Entries | I | II | III | IV | V | V sources (ls·dcs·bhs·wl) |
|---|--:|--:|--:|--:|--:|--:|---|
| PWG | 123,366 | 32,327 | 18,627 | 45,929 | 61,866 | 17,357 | 0·11,341·10,343·23 |
| MW | 286,560 | 79,543 | 28,705 | 112,992 | 142,244 | 56,434 | 4,503·38,200·33,949·50 |
| PW | 170,556 | 26,188 | 5,639 | 37,271 | 42,292 | 17,694 | 0·10,340·11,481·30 |
| AP | 90,654 | 9,773 | 3,873 | 21,756 | 23,993 | 7,138 | 0·4,774·3,650·5 |
| AP90 | 34,882 | 6,779 | 2,607 | 10,097 | 13,503 | 5,011 | 0·3,646·2,307·2 |
| BEN | 17,310 | 6,434 | 2,347 | 11,774 | 11,840 | 5,468 | 0·4,378·2,580·0 |
| SCH | 29,125 | 3,661 | 1,241 | 5,920 | 8,410 | 4,375 | 0·2,407·3,157·2 |
| BHS | 17,839 | 1,612 | 624 | 3,139 | 3,108 | 13,629 | 13,172·2,877·0·27 |

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
state evidence depth. The indicated fix (not yet applied): record per-state `n_texts`
in `build_dcs_renou.py` and prune `dcs` states below a min-support threshold (and/or
exclude closed-class lemmas from `dcs` widening). The audit is read-only — it changes
no tags, only measures them.

```sh
python renou_audit.py            # -> renou_audit_report.md (+ console summary)
```

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
| `build_dcs_renou.py` | ✓ | scan DCS corpus → lemma→state index |
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
