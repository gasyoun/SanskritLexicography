# Learner-simplified edition — apparatus spec

_Created: 06-07-2026 · Last updated: 06-07-2026_

**Deliverable 4 of
[H180](https://github.com/gasyoun/Uprava/blob/main/handoffs/H180-Opus_RussianTranslation_pwg_ru_addenda_typology_glue_learner_05.07.26.md).**
Design for a *lighter PWG for Russian students*: PWG stays the only translated
skeleton, and the descendant dictionaries **vote** on which senses a learner needs.
Honours MG's two corrections (05-07-2026): the learner signal is the **Russian student
tier**, not PW/MW/AP; and edition deltas are tracked at **headword level**.

## 1. The three-tier descendant ladder

All headword counts measured 06-07-2026 (`<L>` entry markers in csl-orig, or line count
in the extracted jsonl). "Present" = confirmed on disk this session.

### BIG — scholarly abridgements (a *separate* scholarly axis, **NOT** the learner signal)

| code | dict | entries | join | note |
|---|---|---:|---|---|
| PW | Böhtlingk kürzere Fassung | 170,556 | csl-orig `pw` | abridging **and** correcting PWG |
| MW | Monier-Williams | 286,525 | csl-orig `mw` | **larger** than PWG — "abridgement" = entry *depth*, not fewer headwords |
| AP | Apte (full) | 90,843 | csl-orig `ap` | |

### MEDIUM — scholarly, single-language

| code | dict | entries | lang | note |
|---|---|---:|---|---|
| CAE | Cappeller | 40,069 | Sa→En | "based upon the St. Petersburg Lexicons" |
| **CCS** | Cappeller | 30,010 | Sa→**German** | a same-language abridgement of PW/PWG — unusually useful |
| MD | Macdonell | 20,749 | Sa→En | |

### SMALL — the **Russian student dictionaries = THE learner signal**

The edition is *for Russian students*, so what these keep is what a learner needs.
**All already extracted — CONSUME, don't rebuild** ([[reference_corpus_lexicon]]); each is
a flat `{source, slp1, iast, gloss}` jsonl folded into `corpus_lexicon.jsonl`:

| weight | code | dict | jsonl | entries |
|---:|---|---|---|---:|
| **1.00** | KCH | Kochergina 1987 (the modern Sa→Ru anchor, "above all") | `src/koch.jsonl` | 29,177 |
| 0.70 | KOW | Kossovich 1854 | `src/kow.jsonl` | 13,488 |
| 0.70 | KNA | Knauer 1908 | `src/kna.jsonl` | (present) |
| 0.60 | SMI | Smirnov (SamudraManthanam) | `src/smirnov.jsonl` | (present) |
| 0.50 | FRI | Frisch | `src/fri.jsonl` | (present) |

LAN (Lanman, 4,944, Sa→En) is a secondary English glossary, not weighted in the Russian
learner core.

## 2. Learner-core score

For each PWG **headword** `k` (SLP1 `key1`):

```
learner_score(k) = Σ_i  w_i · present_i(k)          # SMALL Russian tier, weighted
support_score(k) = mean over MEDIUM tier of present(k)   # CAE/CCS/MD backing
scholarly_score(k) = mean over BIG tier of present(k)    # PW/MW/AP — reported, not gating
```

- `present_i(k)` joins on normalized SLP1 (see §4 caveat). A headword kept by Kochergina
  alone already clears a low threshold; kept by ≥2 Russian dicts → solidly learner-core.
- **Threshold** on `learner_score` (backed by `support_score`) selects the learner
  edition's headword set. Calibrate the cut on a small human-labelled sample
  (interactive HTML sheet, not checkboxes — [[feedback_interactive_review_not_checkboxes]]).
- `scholarly_score` is the **second, independent axis** (MG: PW/MW/AP are
  abridged-but-scholarly, never for students) — reported alongside, never used to admit a
  sense into the learner set.

### Sense-level refinement (later)

The student jsonls are **headword→gloss (flat)**, so first-pass retention is
headword-level. Per-*sense* retention requires aligning each student `gloss` (Russian)
against the PWG sense glosses — a gloss-to-sense alignment reusing
`corpus_lexicon.jsonl`, deferred to a second pass. Until then the learner edition keeps
the full PWG sense set for admitted headwords and only *prunes headwords*.

## 3. Edition deltas at headword level (measured 06-07-2026)

The later editions had access to more PWG entries **and** the completed PW, so
add/keep/drop vs the earlier edition is itself a learner-relevance signal (what a mature
editor thought worth adding). Computed by set-diff on `<k1>` SLP1 keys.

### Raw

| pair | old uniq | new uniq | kept | added | dropped |
|---|---:|---:|---:|---:|---:|
| AP90 → AP | 34,277 | 88,869 | 26,056 | 62,813 | 8,221 |
| MW72 → MW | 51,159 | 194,084 | 45,856 | 148,228 | 5,303 |

### ⚠️ Normalization caveat (measured, not assumed)

The raw "dropped" sets are **inflated by orthographic drift between editions**, chiefly
**final anusvara `-M` vs `-m`** (e.g. AP90 `ABAsanaM` "dropped" ↔ AP `ABAsanam` "added" —
the *same* word). Collapsing final `M→m` before the diff:

| pair | kept | added | dropped |
|---|---:|---:|---:|
| AP90 → AP | 30,240 | 58,628 | **4,030** (was 8,221) |
| MW72 → MW | 45,856 | 148,209 | **5,301** |

Final-`M` normalization alone **halves** AP90's apparent drops. Residual dropped keys
still show *internal* anusvara variants (`AByaMtara`, `AKaMqalaH`) → a full delta needs
proper SLP1 normalization (all anusvara, sandhi-final, homonym-number stripping), not
just the final-char fix. **Design rule:** the edition-delta and every student-dict join
in §2 must run through a shared `slp1_norm()` (anusvara + final-sandhi + homonym strip)
before set operations, or the learner signal inherits this OCR/citation-form noise.

## 4. Secondary aids (not primary sources)

- **English→Sanskrit for disambiguation/essentiality:** MWE (MW reverse, 32,378) + BOR
  (Borooah, 24,609, En→Sa) — reverse-lookup a candidate sense to narrow the Sanskrit; a
  word present in the small En→Sa BOR is likely learner-core. Secondary weight only.
- **PD (Deccan College *Encyclopedic Dictionary of Sanskrit on Historical Principles*,
  Poona):** **not yet in Cologne** — confirmed absent this session. An OED-scale future
  comparand; when it lands, compare whether PD exceeds PWG for the **a-** range (ref
  counts: PWG a- 12,167 · MW 21,742 · AP 6,338 · CAE 3,946). No near-term work.
- **Etymological layer — KEWA / EWA (Mayrhofer):** an *etymology* signal orthogonal to
  gloss. `KEWA.txt` (SamudraManthanam) is a word index where **dhātus appear as finite
  verb forms** (e.g. `bhavati` for root `bhū`) — a normalization gotcha to resolve before
  joining on roots. Add EWA later; document the crosswalk.

## 5. Build plan (first pass, no re-translation)

1. `src/slp1_norm.py` — the shared normalizer (§3 caveat). Reuse existing transcoder
   from [`SHARED_CODE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/SHARED_CODE.md)
   §1 rather than writing anusvara handling from scratch.
2. `src/build_learner_scores.py` — join PWG `key1` against the five student jsonls +
   three MEDIUM + three BIG dicts (all on disk), emit
   `pwg_ru/learner_scores.tsv` (`key1, learner_score, support_score, scholarly_score,
   dicts_present`). **No workflow / translate call.**
3. Calibrate the threshold on a human-labelled sample (HTML sheet).
4. Doubles as evidence for the Deliverable-5 paper ("how the Petersburg tradition
   abridged itself").

## 6. Guardrails (H180)

- Never blocks the H179 run; operates on already-translated sub-cards.
- Reuse before deriving — every dict above is already extracted; do not re-parse.
- Small human annotation now is OK to calibrate; full gold is a separate later task
  ([[feedback_second_annotator_deferred]] — do **not** open a recruit-annotator GTD item).

_Dr. Mārcis Gasūns_
