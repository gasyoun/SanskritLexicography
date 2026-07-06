# PWG addenda / operation typology

_Created: 06-07-2026 · Last updated: 06-07-2026_

> **Implemented 06-07-2026** — [`src/build_relationships.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_relationships.py)
> classifies all **5,603** non-`pwg` sub-card senses into the sidecar
> [`src/pwg_ru_relationships.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ru_relationships.jsonl)
> (non-destructive — the canonical store stays byte-identical) + the rollup
> [`pwg_ru/relationships_rollup.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/relationships_rollup.tsv).
> Counts are in §5 below.

A **typed operation algebra** for every cross-layer change in the five-layer PWG→RU
merge (PWG · PW · SCH · PWKVN · NWS), plus the abridging descendants (MW · AP). It is
the metadata contract that lets [`REGLUE_SPEC.md`](REGLUE_SPEC.md) place each supplement
at its correct PWG sense with **zero re-translation**, and the empirical spine of the
research paper (Deliverable 5 of
[H180](https://github.com/gasyoun/Uprava/blob/main/handoffs/H180-Opus_RussianTranslation_pwg_ru_addenda_typology_glue_learner_05.07.26.md)).

Status: **first-pass design, LLM-proposed.** Relationship instances are to be emitted
with `confidence: llm`; the human gold standard is a separate, later deliverable
(do not conflate).

## 0. What the data already gives us (measured 06-07-2026)

The per-sense translated store
[`src/pwg_ru_translated.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ru_translated.jsonl)
(10,857 sub-cards) already carries the fields this typology attaches to — the
[H179](https://github.com/gasyoun/Uprava/blob/main/handoffs/H179-Opus_RussianTranslation_pwg_ru_nominal_core_queue_reorder_05.07.26.md)
Step-1 `layer` field landed:

| `layer` | sub-cards | role |
|---|---:|---|
| `pwg`   | 5,276 | skeleton (the only translated *base*) |
| `pw`    | 5,048 | Böhtlingk shorter — abridging **and** correcting |
| `sch`   | 146   | Schmidt *Nachträge* — additive |
| `pwkvn` | 129   | PW *Nachträge* (v.7) + von Negelein — additive |
| `nws`   | 258   | Neues Wörterbuch scrape — additive, often foreign-language |

Each sub-card also has `subcard` (e.g. `_ap~~h0_00_pwg01`, `_cid~~h0_zz_nws00`),
`sense_tag` (e.g. `6`, `NWS-1`, `anu_desid`, `ava_caus`), and an empty
`provenance.relationship` slot — **this typology fills that slot.**

Multi-layer richness (distinct layers per headword, in the translated set):

| # layers | headwords | examples |
|---:|---:|---|
| 5 | 7  | `yat`, `vraj`, `rakz`, `jIv`, `gA`, `Sam`, `Cid` |
| 4 | 25 | `yaj`, `yA`, `vas`, `vah`, `vA`, `pat`, `pA`, `nI` |
| 3 | 11 | … |

These 5-layer roots are the natural pilot set for
[`REGLUE_SPEC.md`](REGLUE_SPEC.md).

## 1. The three axes

Every cross-layer change is `(operation, target, direction)` plus an **insertion point**.

### Axis A — Operation

| op | meaning | typical layer |
|---|---|---|
| `add` | a sense / source / form absent from PWG | sch, pwkvn, nws |
| `delete` / `cancel` | PWG material a later layer withdraws | pw |
| `correct` | same referent, changed value (gender, form, reading) | pw |
| `restate` | same content, reworded / re-sourced | pw, sch |
| `relocate` | material moved to a different headword/sense (incl. a supplement *to a supplement*) | pwkvn (Nachträge) |
| `merge` | two PWG senses collapsed | pw |
| `split` | one PWG sense divided | pw, sch |

### Axis B — Target

`headword` · `sense/meaning` · `source/citation (<ls>)` · `grammar/gender (<lex>)` ·
`orthography` · `cross-reference (<ab>vgl.</ab>)`.

### Axis C — Direction

- **Additive** `{pwg_nachtr, sch, pwkvn, nws}` — *grow* the entry (skeleton + supplements).
- **Abridging** `{pw, mw, ap}` — *shrink* it (a simplification of PWG).

MG's framing, honoured: **addenda and abridgement are the same algebra in two
directions.** An `add` read backwards is a `delete`; a `split` backwards is a `merge`.
The typology is therefore *signed*: an instance records `direction` and the same seven
ops cover both.

## 2. Insertion point (the field REGLUE consumes)

Every non-skeleton instance must resolve **where on the PWG skeleton it attaches**:

```
insertion_point:
  key1:          "Ap"          # PWG headword
  homonym:       "h0"          # PWG homonym slot (from subcard ...~~h0...)
  target_sense:  "6"           # PWG sense number, or "*whole" / "*new"
  anchor:        "sense"       # headword | sense | citation | grammar | xref
```

`target_sense` is the crux of MG's "NWS adds to a *specific* PWG sense (e.g. sense 2),
not at the end." When a layer supplies a genuinely new sense with no PWG parent,
`target_sense = "*new"` and the reglue appends it, flagged as an addition.

## 3. First-class special cases (MG-named), with real instances

Each is a `(op, target, direction)` triple with a dedicated `subtype` tag so the reglue
and the paper can count them.

### 3.1 `pw_cancels` — PW withdraws a PWG word / sense / source / gender
`op=delete`, `direction=abridging`, `subtype=pw_cancel`. The canonical case is a
**gender correction** ("PWG n. vs PW m.") — modelled as `delete` of the PWG `<lex>`
value plus a paired `correct`. Detected by comparing the PWG `<lex>` token against the
PW sub-card's for the same `key1`+sense.

### 3.2 `sch_star` — SCH adds a new meaning marked `*`
`op=add`, `target=sense`, `direction=additive`, `subtype=sch_star`.
**Real instance** — `Ap`, sub-card `_ap~~h0_zz_sch`, `sense_tag=anu_desid`: Schmidt
adds the preverb+desiderative sense *"einstimmen / соглашаться"* (VP. 4,2,11) absent
from the PWG skeleton. `target_sense="*new"`.

### 3.3 `nws_at_sense` — NWS adds to a *specific* PWG sense
`op=add`, `target=sense`, `direction=additive`, `subtype=nws_at_sense`.
**Real instance** — `Cid`, sub-card `_cid~~h0_zz_nws00`, `sense_tag=NWS-1`: NWS adds a
mathematical sense *"(in math.) to divide"* (Sūryasiddhānta iv,26). Here `target_sense`
is a new technical sense → `*new`; when the NWS card names an existing PWG sense the
`sense_tag` carries it.

### 3.4 `foreign_fragment` — NWS entry partly in FR / LA / **EN**
`op=add`, `subtype=foreign_fragment`, plus a `needs_ru_from_{fr,la,en}` flag.
**Correction to the handoff:** the handoff named French/Latin; the scrape shows **English
too** — the `Cid` NWS card above is authored in English ("(in math.) to divide"). The
flag must therefore cover `en` as well as `fr`/`la`. These already receive a Russian
rendering in the translated store, so the flag is provenance, not a translation gap.

### 3.5 `a2a` — Addenda-to-Addenda (nested supplement)
`op=relocate`, `subtype=a2a`. PWG's *Nachträge* (vol. 7) and PW's *Nachträge* are
supplements-to-a-supplement. Measured presence in csl-orig and folding rules are in
[`ADDENDA_TO_ADDENDA_PROBE.md`](ADDENDA_TO_ADDENDA_PROBE.md); the `pwkvn` layer (129
sub-cards) is exactly this material already pulled into the merge.

### 3.6 `pwkvn_caus` etc. — grammar-derived sub-senses
`op=add`, `target=grammar`, `subtype=derived_sense`. **Real instance** — `Ap`,
`_ap~~h0_zz_pwkvn`, `sense_tag=ava_caus`: adds the causative-with-*ava* sense
("заставлять достигать", NAIṢ. 8,89). The `sense_tag` (`<preverb>_<derivation>`) is
already a machine-readable attachment key.

## 4. The `provenance.relationship` sidecar schema

Written per non-`pwg` sub-card (the `pwg` skeleton needs none):

```json
"relationship": {
  "op": "add",
  "target": "sense",
  "direction": "additive",
  "subtype": "sch_star",
  "insertion_point": {"key1":"Ap","homonym":"h0","target_sense":"*new","anchor":"sense"},
  "confidence": "llm",
  "evidence": "sense_tag=anu_desid; SCH-only preverb+desiderative not in PWG skeleton"
}
```

- One row per sub-card; the rollup table in §5 aggregates by `(subtype, layer)`.
- `confidence`: `llm` (proposed) → `human` (gold, later). Never overwrite an `llm` value
  in place — append a `human` verdict alongside so κ can be computed.
- Emitting script (to build): `src/build_relationships.py`, reading
  `pwg_ru_translated.jsonl` + PWG skeleton, writing the sidecar back per sub-card and a
  `pwg_ru/relationships_rollup.tsv`. **No workflow / translate call** — pure metadata.

## 5. Rollup table (populated 06-07-2026 by `build_relationships.py`)

| subtype | op | direction | layer(s) | count | notes |
|---|---|---|---|---:|---|
| `restate` | restate | abridging | pw | 5,054 | PW abridging restatement (default when no gender conflict) |
| `nws_at_sense` | add | additive | nws | 211 | attach to PWG sense N |
| `a2a` | relocate | additive | pwkvn | 89 | Nachträge-to-Nachträge |
| `sch_star` | add | additive | sch | 88 | new `*` senses |
| `foreign_fragment` | add | additive | nws | 62 | all detected `en` (English) — the handoff named FR/LA; the scrape is English-heavy |
| `derived_sense` | add | additive | sch | 58 | preverb/caus/desid |
| `derived_sense` | add | additive | pwkvn | 40 | preverb/caus/desid |
| `pw_correct` | correct | abridging | pw | 1 | gender change, same referent |

**Findings from the first run:**
- **`pw_correct` is rare (1) and `pw_cancel` (0) by the deterministic gender test** — a
  `pw_cancel`/`pw_correct` fires only when PWG *and* PW both carry a `<lex>` gender token
  at the *same numeric sense*, which is uncommon in the verb-root-first store (most PW
  gender info sits on nominal cards not yet translated). This is a **coverage** limit, not
  a typology gap; the abridging-direction ops will populate as nominal PWG lands.
- **Foreign fragments are 100% English** in the scrape — the `needs_ru_from_en` flag (the
  handoff correction §3.4) is the only one that fires; FR/LA remain first-class categories
  for when they appear.
- **`restate` dominates** because PW is overwhelmingly an abridging *re-statement* of PWG,
  not a canceller — consistent with MG's "abridgement = entry depth, not withdrawal".

## 6. Validation plan (first pass)

- **Labelled sample:** hand-label `relationship` on the 7 five-layer roots' non-`pwg`
  sub-cards (~a few dozen) + a random 30 sub-cards, as an interactive HTML voting sheet
  (never markdown checkboxes — [[feedback_interactive_review_not_checkboxes]]), and
  compute κ vs the LLM proposal where a second signal exists (the `sense_tag` gives a
  weak automatic second label for `derived_sense`/`nws_at_sense`).
- **`pw_cancel` gender check:** deterministic — join PWG vs PW `<lex>` per sense; every
  disagreement is a candidate `pw_cancel`/`pw_correct`. This needs no LLM and calibrates
  precision of the abridging-direction ops.

## 7. Guardrails carried from H180

- Never blocks or delays the H179 translation run; consumes its sidecar, does not gate it.
- No re-translation — operates on already-translated sub-cards.
- Reuse before deriving: `union_headwords`, `corpus_lexicon`, existing MW/AP crosswalks
  (check [`SHARED_CODE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/SHARED_CODE.md)
  / [`PROJECT_INTERLINKS.md`](https://github.com/gasyoun/Uprava/blob/main/PROJECT_INTERLINKS.md)).

_Dr. Mārcis Gasūns_
