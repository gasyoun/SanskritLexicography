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

---

## RESULTS (executed 2026-06-24)

Method as briefed: read each preface for explicit arrangement statements, then pulled
the actual `bhū` (SLP1 `BU`) root record from each `csl-orig/v02/<dict>/<dict>.txt`
entry file and classified the **realized** structure (the marked-up text the segmenter
will actually see), spot-checking `kṛ`/`gam` and the prefixed-form headwords
(`aDiBU`, `anuBU`, `pariBU`, `praBU`, `aBiBU`, `samBU`).

### Headline finding — the priors are *half right*, and the nuance matters for the segmenter

Every Petersburg-family dictionary does **two things at once**, and conflating them is
what made our cards giant:

1. **Verbal prefix-forms are NESTED run-on inside the root `<L>` record** — `anu-bhū`,
   `abhi-bhū`, `sam-bhū` (and stacked `anu-sam-`, `abhi-sam-`) live *inside* the `bhū`
   record as `<div>`-delimited sub-paragraphs. This is the bulk that overflows a single
   translation pass.
2. **Lexicalised nominal prefix-forms are ALSO split out as their own `<k1>` headwords** —
   e.g. PWG [`aDiBU`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pwg/pwg.txt) m. "Herrscher, Gebieter", glossed `(von {#BU#} mit {#aDi#})`. So a grep for
   `<k1>anuBU<k2>` hits in *every* dict — that does **not** mean the dict is "split"; the
   verbal force usually still nests under the root. Only **MW** splits the *verb itself*.

So the segmenter must split on the **in-record `<div>` prefix boundary**, not on the
presence of a separate headword.

### Comparison table

| Dict | Prefixed **verbs** | Nominal derivatives | Prefix-boundary cue (the thing the segmenter keys on) | Evidence |
|---|---|---|---|---|
| **PWG** | **NESTED** run-on in root record | mostly run-on; lexicalised ones SPLIT to own `<k1>` | `<div n="p">— {#<upasarga>#}` (prefix in `{#…#}`, may stack: `{#anusam#}`, `{#aBisam#}`); 2ary conj `<div n="m">` / `— <ab>caus./desid.</ab>`; senses `<div n="1"> N)` | `BU` rec. [pwg.txt L535553–536869](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pwg/pwg.txt): `<div n="p">— {#aBisam#}`, `— {#parisam#}`, `— {#pratisam#}`; split `aDiBU` m. |
| **PW** (kürzere) | **NESTED** run-on | run-on; lexicalised ones SPLIT | `<div n="p">— Mit {#<prefix>#}`; 2ary conj `<div n="m">— <ab>Caus./Desid.</ab>`; senses `<div n="1">— N〉`, subsenses `<div n="2">— a〉` | `BU` rec. [pw.txt L331003–](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pw/pw.txt): `<div n="p">— Mit {#na#}`, `<div n="m">— <ab>Caus.</ab>` |
| **MW** | **SPLIT** — each `prefix-√root` is its **own `<L>` headword** | **NICHED** run-on under the root/leading word (subordinate line) | headword `<k1>anuBU<k2>anu-BU` + body `<s>anu-√ BU</s>` (the `-√` is the cue); senses `<div n="to"/>`, 2ary conj `<div n="vp"/>` | `anu-BU` [mw.txt L25014](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/mw/mw.txt); preface §"under every root the continuous series of derivative words" |
| **GRA** | **NESTED** run-on in root record | run-on; a few lexicalised SPLIT | `<div n="Pf">{@<prefix>@}` (Pf = *Präfix*; prefix in `{@…@}`, stacks: `{@ánu prá@}`, `{@abhí sám@}`); morphology blocks `<div n="H">`/`<div n="TS">` | `BU` rec. [gra.txt L42470–](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/gra/gra.txt): `<div n="Pf">{@ánu@}`, `{@abhí@}`, `{@pári@}`, `{@sám@}` |
| **AP90** | **RUN-ON** in a prose "Note" paragraph | run-on; lexicalised ones SPLIT | *text-level only, no `<div>`*: `;`-separated inline `{#<prefix>BU#}` glosses inside the Note; 2ary conj inline `{%--<ab>Caus.</ab>%}` | `BU` rec. [ap90.txt L190844–190948](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/ap90/ap90.txt): `{#punarBU#} to marry again; {#AvirBU#} to appear; {#tiroBU#} to disappear …` |
| **SCH** | **NESTED** run-on (additive supplement) | — | `— Mit {%<prefix>%}` (note: italic `{%…%}`, not `{#…#}`); stacks `{%samabhi%}`, `{%˚saṃpari%}` | `BU` rec. [sch.txt L63863](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/sch/sch.txt): `mit {%samabhi%} … — Mit {%abhyā%} … — Mit {%ud%}` |
| **FRI** | **none** (reader glossary) | — | no prefix forms; senses are trilingual `<div n="1"/> <lang n="…">` blocks | `BU` rec. [fri.txt L28267](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/fri/fri.txt): simple `√bhū` only, cz/ru/en glosses |

### Preface evidence (quoted)

- **MW** — explicitly abandons full root-arrangement but niches derivatives under roots:
  > "I also felt constrained to abandon the theoretically perfect ideal of a wholly
  > root-arranged Dictionary in favour of a more practical performance" — and the
  > subordinate line is used "for exhibiting clearly to the eye in regular sequence
  > **under every root the continuous series of derivative words which grow out of each
  > root**" ([`mwpref_all.en.md`](https://github.com/sanskrit-lexicon/MWS/blob/master/prefaces/mwpref_all.en.md), §"Explanation of the Plan and Arrangement"). MW *niches nominals, splits the prefixed verb.*
- **PWG/PW/GRA** — the prefaces give layout/transliteration policy (e.g. PWG banishes
  `ऋ ॠ ऌ` from verbal-root spellings, gives no class number since the 3 sg. pres. shows
  it — [`pwgpref_all.de.md`](https://github.com/sanskrit-lexicon/PWG/blob/master/prefaces/pwgpref_all.de.md) §187–189) but make **no** explicit statement that overrides the
  realized structure; the entry markup above is the decisive evidence (all three nest).

### One-line segmenter rule per dict

- **PWG** → split the root `<L>` record at every `<div n="p">` (prefixed-verb) and
  `<div n="m">` (caus/desid/intens) boundary; `upasarga` = the `{#…#}` token immediately
  after `— ` (split on internal `+`/concatenation for stacked `anusam`); additionally
  ingest already-split lexical forms by their own `<k1>` headword, linking via `root_key=BU`.
- **PW** → identical to PWG, but the prefix token follows the literal `Mit ` inside
  `<div n="p">`; secondary conjugation under `<div n="m">`.
- **MW** → **no in-record split needed** — prefixed verbs are already separate `<L>`
  records; group by `root_key` = the root after `-√` in the body (`<s>anu-√ BU</s>`),
  `upasarga` = the `k2` segment before the first hyphen (`anu-BU` → `anu`).
- **GRA** → split the root record at every `<div n="Pf">` boundary; `upasarga` = the
  `{@…@}` token (keep multi-word values verbatim for stacked prefixes, e.g. `ánu prá`).
- **AP90** → *no structural cue*: segment the run-on "Note" paragraph on `;`-delimited
  `{#<x>BU#}` tokens (lowest-fidelity; the prefix is fused to `BU` with no boundary
  marker), and otherwise rely on the separate `<k1>` headwords for lexicalised forms.
- **SCH** → split on `— Mit {%<prefix>%}` (italic `{%…%}`, supplement-only deltas).
- **FRI** → no segmentation (carries no prefixed forms).

### Net correction to the priors

| Prior | Verdict |
|---|---|
| PWG/PW/GRA **nest** prefixed verbs → giant cards | **CONFIRMED** — and the boundary is a real `<div>` cue (`p` / `Pf`), so segmentation is mechanical, not heuristic. |
| MW splits prefixed verbs as `√`-headwords, run-ons nominals | **CONFIRMED** — cue is the `-√` in the body + the hyphen in `k2`. |
| AP "compact nesting" | **CONFIRMED, sharpened to RUN-ON** — prose `;`-list with **no** markup boundary; this is the *hardest* dict to segment and should fall back to its split `<k1>` headwords. |
| (new) all dicts also emit separate `<k1>` headwords for lexicalised prefix-nouns | **the trap**: presence of `<k1>anuBU` ≠ "split verb"; only MW splits the verb. Segment on the `<div>` cue, not on headword presence. |
