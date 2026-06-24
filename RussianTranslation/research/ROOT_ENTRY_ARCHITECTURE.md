# Root-entry architecture — decision + handoff research (2026-06-23)

## The problem
Frequency-first ordering front-loads the verbal **roots** (`sthā` 379 senses, `i` 272,
`gam` 213, `bhū` 131, `vid` 74). In PWG a root article *nests* every prefixed verb
(`adhi-`, `anu-`, `pari-`…) and the simple verb in one giant record, so a single
translation pass dies ("connection closed mid-response" on `vid`/`bhū`). The fix is
structural, not a bigger model.

## DECISION (user, 2026-06-23) — TWO MODES, both documented

**It is fine to translate sopasarga (prefixed) dhātus as SEPARATE entries** — this is
how **MW** already presents them, and splitting fixes the single-pass size problem.
**But the parser must REMEMBER the root linkage** so that, on demand, the separate
prefixed-verb cards can be **glued back into one nested root article** after translation.

So the data model and pipeline support **two modes**:

| Mode | What it is | When used |
|---|---|---|
| **SPLIT** (default for translation) | the simple root and each `prefix+root` are their own card; each carries a `root_key` + `upasarga` link back to the head root | the **translation unit** — keeps every card single-pass-sized; gated/judged independently |
| **NESTED** (assembled view) | a "glue" step re-collects all cards sharing a `root_key`, ordering simple-verb first then prefixed forms (Pāṇinian upasarga order), into one root article | the **reading / print view** and any "show me the whole root" query |

### Implementation sketch (no code yet — for the build after the manuals review)
- **Segment** the PWG root record at its prefix boundaries (PWG marks them — "mit
  {#adhi#}", "mit {#anu#}", the `<div>`/prefix cues) → one sub-card per `(root, upasarga)`,
  each with `root_key` (the SLP1 root), `upasarga` (the prefix, '' for the simple verb),
  and `seg_index`.
- **Translate** each sub-card separately (single-pass-sized) through the existing
  owner-map gated loop. Provenance + F12 gate unchanged.
- **Glue** (`root_glue.py`, to build): given a `root_key`, collect its sub-cards, order
  them (simple verb, then upasargas in a canonical order), emit the nested root article.
  Reversible: SPLIT ⇄ NESTED is a pure re-grouping, lossless.
- The **manifest** already keys by headword; roots get an extra pre-pass that explodes
  the giant record into its `(root, upasarga)` sub-cards before `_pilot_gen_merged`.

This also helps non-root mega-entries (any record over a size threshold can be
segmented on its top-level sense boundaries and glued back).

---

## HANDOFF A — which core dictionary uses which root approach *now*?

**Question.** For each core dictionary, are prefixed verbs and derivatives **nested**
under the root, **niched** (sub-headwords indented under the root but not run-on),
**split** (separate independent lemmas), or **run-on** (derivatives packed into a
paragraph)? This sets what SPLIT/NESTED must reproduce per source.

**Dictionaries + sources (all present locally):**
| Dict | Preface (OCR) | Entry file | Probe lemma (the root `bhū`/`kṛ`/`gam`) |
|---|---|---|---|
| PWG | [`PWG/prefaces/pwgpref_all.de.md`](https://github.com/sanskrit-lexicon/PWG/blob/master/prefaces/pwgpref_all.de.md) | `csl-orig/v02/pwg/pwg.txt` | `BU`, `kf`, `gam` |
| PW (kürzere) | [`PWK/prefaces/pwpref_all.de.md`](https://github.com/sanskrit-lexicon/PWK/blob/master/prefaces/pwpref_all.de.md) | `csl-orig/v02/pw/pw.txt` | same |
| MW | [`MWS/prefaces/mwpref_all.en.md`](https://github.com/sanskrit-lexicon/MWS/blob/master/prefaces/mwpref_all.en.md) | `csl-orig/v02/mw/mw.txt` | same |
| GRA (Grassmann RV) | [`GRA/prefaces/grapref_all.en.md`](https://github.com/sanskrit-lexicon/GRA/blob/master/prefaces/grapref_all.en.md) | `csl-orig/v02/gra/gra.txt` | `BU`, `kf` |
| AP90 (Apte) | *(no OCR preface — read the print front-matter scan)* | `csl-orig/v02/ap90/ap90.txt` | same |
| SCH / FRI | supplements — note only if they diverge | `…/sch.txt`, `…/fri.txt` | — |

**Method.** (1) Read each preface for explicit statements on root/derivative
arrangement. (2) Pull the actual `bhū`/`kṛ`/`gam` records from each entry file and
classify the realized structure. (3) Fill the table; note the markup cue each uses for
a prefix boundary (PWG "mit {#…#}", MW `√` + prefix, etc.) — that cue is what the
SPLIT segmenter keys on.

**Output:** a comparison table (dict × {nested / niched / split / run-on} + prefix-cue +
sense-vs-form nesting) + a one-line rule per dict for the segmenter.

**Preliminary priors (to verify, NOT to trust):** PWG/PW/GRA **nest** prefixed verbs
inside the root article (why our cards are giant); **MW** lists prefixed verbs as
separate `√`-headwords and **run-on**s nominal derivatives; **AP** tends to compact
nesting. Confirm via prefaces + the real records.
