# Plan — Renou subsections as an orthogonal *register* axis

Extends the flat five-state model (`RENOU.md`) with Renou's **subsections** — the
linguistically-distinct registers inside each chapter. Ground truth: the verified
table des matières in
[`../../VisualDCS/docs/Renou_1956_structure.md`](../../VisualDCS/docs/Renou_1956_structure.md).
Motivating gap: **`épigraphique`** (Ch. II, p. 94) and **`bhāṣya`** = commentary
language (Ch. IV, p. 133–145, *with its own grammar*) are real registers a flat I–V
tag cannot express, and `bhāṣya` in particular "does not fit" any of the five states.

## Decisions (locked)

1. **Orthogonal axis.** Register is an **independent, multi-label tag parallel to the
   state**, not a child of it (`renou_register`, alongside `renou_enriched`). Rationale:
   a *bhāṣya* can comment on a Vedic, epic, or kāvya base text, and an inscription can
   be classical or epic in date — register cross-cuts period. Renou files each register
   under one chapter *at index level*, but its linguistics are not bound there. We record
   the **correlated state** for reference, not as a parent.
2. **Full lattice.** Code **every** Renou subsection across I–V, not only the two hard
   ones — so the axis is complete and the easy registers (kāvya, purāṇa, …) come almost
   free from the DCS genre map we already have.
3. **Combined detectors.** Each register is detected by the **union** of three signals,
   with per-register provenance: (a) **DCS genre/name** of the texts a lemma occurs in,
   (b) **`<ls>` siglum** → register, (c) a **dedicated detector** for registers the
   genre map can't see (commentary, epigraphic, Jaina, Sanskrit-abroad). Mirrors the
   state axis's `ls`/`dcs`/`bhs`/`wl` provenance discipline.

## Data model

Two new fields per `{code}.renou.jsonl` entry (additive; existing fields untouched):

```json
{ "renou_register": ["bhasya","kavya"],
  "renou_register_provenance": {"bhasya": ["lsname","dcsname"], "kavya": ["dcsgenre"]} }
```

- `renou_register` — sorted list of register codes (multi-label; may be empty).
- `renou_register_provenance` — `{code: [signal,…]}`, signals ⊆
  `{dcsgenre, dcsname, lssiglum, lsname, bhs, dedicated}`.
- Per-lemma evidence lives **lossless** in the DCS index as `register_support`
  `{code: {n_texts, best_confidence}}`, exactly like `state_support`; the min-support
  policy (`renou.filter_dcs_states`) generalises to registers.

## The register lattice

Correlated state in parentheses; a register can still attach across states. Detector
columns: **G** = DCS genre, **N** = DCS text-name hint, **L** = `<ls>` siglum/name,
**D** = dedicated set/rule.

| Code | Register (Renou subsection) | Renou loc. | ~State | Detectors |
|---|---|---|--:|---|
| `rgveda` | Ṛgveda / oldest mantra | I p. 10 | I | G `Vedic Saṃhitā` + N (`ṛgveda`) |
| `atharva` | Atharva & other mantras | I p. 32–38 | I | N (`atharva`,`gāthā`) |
| `brahmana` | prose brāhmaṇa | I p. 41 | I | G `Brāhmaṇa` |
| `upanisad` | Upaniṣad | I p. 50 | I | G `Upaniṣad` |
| `sutra` | Vedic/ritual sūtra | I p. 53 | I | G `Sūtra/Dharma`+`Ritual` (date<0) · N (`śrauta`,`gṛhya`,`kalpa`) |
| `vyakarana` | grammarians' norm | II p. 62–80 | II | G `Vyākaraṇa` · N (`aṣṭādhyāyī`,`mahābhāṣya`,`kāśikā`,…) |
| **`epig`** | **epigraphic / inscriptional** | II p. 94 | II | **L** inscription sigla (EI, CII, Ind.Ant.) · **D** inscription corpora *(low DCS coverage — see risks)* |
| `epic` | epic proper (MBh, Rām) | III p. 101 | III | G `Epic` |
| `purana` | Purāṇa (+ Bhāgavata) | III p. 115/120 | III | G `Purāṇa` |
| `tantra` | Tantra / Āgama | III p. 122 | III | G `Tantra/Āgama` |
| `smrti` | Smṛti / dharmaśāstra | III p. 124 | III | G `Sūtra/Dharma` (date≥0) · N (`smṛti`,`dharmaśāstra`) |
| `karika` | versified śāstra (kārikā) | III p. 125 | III | N (`kārikā`) · D |
| **`bhasya`** | **commentary language** | IV p. 133–145 | IV | **N**/`D` name ∈ {`bhāṣya`,`ṭīkā`,`vṛtti`,`vārttika`,`vivaraṇa`,`-comm`} · **L** commentary sigla *(cross-cuts all states)* |
| `katha` | narrative prose | IV p. 146 | IV | G `Narrative Prose` |
| `natya` | drama dialogue | IV p. 150 | IV | G `Nāṭya` |
| `kavya` | high poetry (kāvya) | IV p. 158 | IV | G `Kāvya` |
| `bauddha` | Buddhist (+ hybrid) | V p. 206 | V | G `Buddhist` · D BHS set (reuse `renou_bhs`) · N |
| `jaina` | Jaina Sanskrit | V p. 222 | V | N (`jaina`,`prakaraṇa`-jaina) · L Jaina sigla · D |
| `hors_inde` | Sanskrit abroad | V p. 229 | V | N/L (Khotan, Niya, SE-Asia epigraphy) · D *(low coverage)* |

`Kośa/Lexicon`, `Medical`, `Arthaśāstra`, `Philosophy` DCS genres have **no distinct
Renou register** — Philosophy base-texts are classical prose (state IV, no register)
unless the **name** marks them commentary (`bhasya`). They map to *no* register, which
is correct: not every text is a Renou register.

## Detector strategy (combine all three)

1. **DCS genre → register** — a `GENRE_REGISTER` map parallel to `build_dcs_renou.py`'s
   existing `GENRE_RENOU`. Same corpus scan already resolves each text's genre; emit a
   register alongside the state at **zero extra scan cost**.
2. **DCS text-name → register** — a `NAME_REGISTER` hint list parallel to the existing
   `NAME_HINTS`, for registers the genre lumps: split `Vedic Saṃhitā`→`rgveda`/`atharva`,
   `Sūtra/Dharma`→`sutra`/`smrti`, and above all detect **`bhasya`** by commentary
   name-stems (`*bhāṣya`, `*ṭīkā`, `*vṛtti`, `*vārttika`) — DCS has **no commentary
   genre**, so this is the only corpus route to it.
3. **`<ls>` siglum/name → register** — extend the `ls_source_map*.json` rows with a
   `register` field (the maps already carry `renou` state per siglum). This is the
   primary route for **`epig`** (inscription sigla) and a second route for `bhasya`
   (commentary sigla) and `jaina`.
4. **Dedicated sets** — reuse `renou_bhs` for `bauddha`; a curated inscription/Jaina/
   abroad list for the registers the corpus barely covers.

Provenance records which fired; a register backed only by a single low-confidence
signal is the weakest, exactly as with states.

## Reuse map (prior art — do **not** rebuild)

| Need | Reuse / extend | New |
|---|---|---|
| text → register, per-lemma support | extend `build_dcs_renou.py` (`GENRE_REGISTER`, `NAME_REGISTER`, emit `register_support`) | — |
| min-support filtering | reuse `renou.filter_dcs_states` (generalise to a `kind` arg) | — |
| `<ls>` siglum → register | extend `build_ls_map.py` / `build_ls_map_mw.py` + the JSON maps with a `register` column | — |
| tagger join | extend `tag_dict_from_source.py` to emit `renou_register*` | — |
| pipeline driver | extend `renou_pipeline.py` (register is just more fields per entry) | — |
| editor badge | extend `renou_portrait.py` (register sub-label under the state label) | — |
| validation | extend `renou_audit.py` (inter-signal agreement per register) | — |
| resolver | — | `renou_register.py` (genre/name/siglum → register, mirrors `renou.py`/`renou_sigla.py`) |

## Phasing

- **✅ Phase 0 — tables (done).** Register code list `REGISTERS` (20 codes) +
  `GENRE_REGISTER` + `NAME_REGISTER` + `registers_for_text` frozen in `build_dcs_renou.py`.
- **✅ Phase 1 — corpus side (done, 2026-06-25).** `build_dcs_renou.py` emits per-lemma
  `register` + lossless `register_support` `{n,conf}` in the same scan. Sane coverage:
  `bhasya` 13,102 lemmas (28 commentary texts: Nyāyabhāṣya, Kāśikāvṛtti, …), plus
  `epic`/`purana`/`sutra`/`katha`/`bauddha`/`kavya`/…; `atharva`/`epig`/`jaina`/
  `hors_inde` = 0 from corpus (await the `<ls>` route).
- **✅ Phase 4-dcs — wire + emit (done).** `renou.filter_dcs_registers` (min-support,
  shared with states) + the taggers emit `renou_register` + `renou_register_provenance`
  (`["dcs"]`); regenerated all 8. Coverage ~38–41 % of entries; survives the bhs/wl
  enrich chain. (Provenance gains `ls`/`bhs` sources in Phase 2–3.)
- **✅ Phase 2 — citation side (done, 2026-06-25).** `renou_register.py` maps each
  `ls_source_map*.json` record → register(s) (PWG structured `genre` + name rules; MW
  by name); `renou.ls_registers_for_text` + the taggers union it with the corpus route,
  provenance `["ls"]`/`["dcs"]`/both. Adds **jaina** (288 MW entries, corpus had 0) +
  **bhāṣya** ls-corroboration (4,109 MW; Sāy/Kāś/Pat) + an `ls` source on ~119 k (PWG) /
  ~155 k (MW) register-assignments. `REGISTERS` now canonical in `renou_register.py`
  (shared with the corpus builder). Minor known FP: Bālarāmāyaṇa → epic+natya.
- **Phase 3 — dedicated `epig` (+ `hors_inde`).** Still 0: neither CANON has inscription
  sigla (they're top-citation literary sources). Needs an inscription-siglum curation
  pass in `build_ls_map*.py` (e.g. add the dicts' `Inscr.`-class sigla). Lower value —
  inscriptional citations are sparse in these dictionaries.
- **Phase 5 — validate + display.** `renou_audit.py` register mode; `renou_portrait`
  register sub-label (+ reuse the low-info flag for all-register breadth). Human
  spot-check focused on **`bhasya`** precision (tighten the `dīpikā`-class name FPs,
  e.g. Haṭhayogapradīpikā) and **`epig`** recall.

## Risks / open issues

- **`epig` coverage is thin.** The DCS corpus has essentially no inscription texts, so
  `epig` rests almost entirely on `<ls>` inscription sigla — coverage will be low and
  patchy. Honest move: ship it, label it low-coverage in the audit (like `wl` for V),
  don't oversell recall.
- **`bhasya` cross-cutting state.** A commentary's *lemmas* are also attested in its
  base text's era, so `bhasya` words will (correctly) carry several states. The register
  tag is the value-add precisely because the state tag blurs it.
- **`Sūtra/Dharma` and `Vedic Saṃhitā` splits** need date/name rules (sūtra vs smṛti;
  ṛgveda vs atharva) — small ambiguity, default to the broader register when unsure.
- **Don't let registers leak into states.** The two axes stay separate fields; the
  state pipeline and its audited min-support behaviour are unchanged. Registers are
  purely additive.
