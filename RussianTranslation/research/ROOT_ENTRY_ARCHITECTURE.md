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

---

## PRIOR ART (checked 2026-06-24) — the segmenter substantially already exists

Before building anything: per the "check prior art first" rule, swept the sibling repos.
The root-record prefix segmenter sketched in §"Implementation sketch" above is **already
built** by Jim Funderburk in [`PWG/verbs01/`](https://github.com/sanskrit-lexicon/PWG/tree/master/verbs01) (flagged in
[`SHARED_CODE.md`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/SHARED_CODE.md) §4 "verb/preverb morphology"). It does **more** than the sketch
asked for, on real data, and its outputs are committed.

### What `verbs01` already computes

| File / program | What it produces | Scale |
|---|---|---|
| [`preverb1.py`](https://github.com/sanskrit-lexicon/PWG/blob/master/verbs01/preverb1.py) | splits each PWG verb record at `<div n="p">— {#<upasarga>#}`, joins prefix+root via a full **sandhi map** (`sandhimap`, `join_prefix_verb`), and matches each surface prefixed-verb to its MW headword | 6819 upasargas in 711 PWG verb entries; 8370 total upasarga divisions |
| [`pwg_preverb1.txt`](https://github.com/sanskrit-lexicon/PWG/blob/master/verbs01/pwg_preverb1.txt) | the per-root parse table: every upasarga, its sandhi-joined PWG spelling, the matched MW spelling, and the **canonical Pāṇinian-order parse** (`prati+anu+BU`) | 6773 MW-matched ("yes") + 1588 unmatched ("no") |
| [`mwverbs1.txt`](https://github.com/sanskrit-lexicon/PWG/blob/master/verbs01/mwverbs1.txt) | MW verb inventory categorised verb-vs-preverb from MW's own `<info verb=…>` tags, with class/pada | 10 122 MW verb/preverb headwords |
| [`pwg_verb_filter_map.txt`](https://github.com/sanskrit-lexicon/PWG/blob/master/verbs01/pwg_verb_filter_map.txt) | PWG-root → MW-root correspondence map (the cross-dict `root_key` align) | 2444 PWG verb roots (21 with `mw=?`) |
| [`pwg_verb_exclude.txt`](https://github.com/sanskrit-lexicon/PWG/blob/master/verbs01/pwg_verb_exclude.txt) | empirical list of non-verb records that *carry* root patterns — the `<div n="p">` **false-positive** guard | 149 exclusions |

Worked example — the probe root `bhū`, straight from `pwg_preverb1.txt` (Case 1211,
`L=55166`): **38 upasargas, 32 MW-matched**, including stacked prefixes resolved to
Pāṇinian order: `anvABU → anu+A+BU`, `aByABU → aBi+A+BU`, `AvirBU → Avis+BU`. `gam` is
parsed **twice** (`L=21814` 61 upasargas; `L=72578` 27) — i.e. the multi-homonym root
case is already handled per `<L>` record.

### This answers the four planned analyses — mostly already done

1. **Quantify the mega-record problem** → 711 PWG verb records hold the 6819 nested
   prefix-divisions; `bhū`=38, `gam`=61+27, etc. The upasarga count *is* the sub-card
   count (the histogram is `pwg_preverb1.txt`'s per-Case `#upasargas`).
2. **Validate the `<div n="p">` cue** → the cue is **not** 1:1 with "prefixed verb":
   8370 total upasarga divisions vs 6819 inside verb entries → the surplus is in
   **non-verb** entries (`non_verb_upasargas()` + the 149-row `pwg_verb_exclude.txt`).
   So the FP guard is required and already characterised. (Caveat: PWG also uses
   `<div n="p">` for phrasal notes like `— Mit {#na#}`/`— Mit {#kva#}`; `preverb1` keys
   on the `{#<roman>#}` upasarga shape and excludes those.)
3. **Secondary-conjugation boundaries** → `preverb1.mark_entries_verb()` already detects
   `<ab>(Desid.|Intens.|Caus.)</ab>` as separate marks alongside the `<div n="m">` cue.
4. **Cross-dict root-key alignment** → `pwg_verb_filter_map.txt` (PWG↔MW root) +
   the per-prefix MW match in `pwg_preverb1.txt`. **And MW carries the parse natively**:
   prefixed-verb records have `<info verb="pre" … parse="anu+BU"/>` and simple roots
   `<info verb="genuineroot" cp="1P,1Ā"/>` ([mw.txt L25020 / L507286](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/mw/mw.txt)) — so MW's `root_key`+`upasarga` need **no** inference, just a tag read.

### The actual GAP (what to build — small, not a segmenter from scratch)

`verbs01` *analyses and aligns*; it does **not** emit translation-ready sub-cards. For
the SPLIT/NESTED pipeline the remaining work is:

- **Text-slicer**: cut the giant PWG record into the actual `<div n="p">…</div>` German
  text slices (gloss + `<ls>` apparatus) per `(root, upasarga)`, carrying `root_key`,
  `upasarga`, and `seg_index` = position in the parse string. Reuse `preverb1`'s
  `Entry`/`init_entries` record splitter and its parse output for the keys — don't
  re-derive sandhi.
- **Glue** (`root_glue.py`): order sub-cards by the `prati+anu+BU` parse (Pāṇinian
  upasarga order is already encoded in the parse string) and re-emit the nested article.
- **Lexicalised-noun link**: join the separate `<k1>aDiBU`-type headwords to their
  `root_key` (they are *not* in `verbs01`, which is verbs-only).

Net: the hard parts (cue, sandhi join, MW alignment, FP guard, Pāṇinian order) are
**done and committed**; the translation pipeline needs a thin text-slicing + glue layer
on top of `preverb1`'s record model, PWG-only to start.

### Prototype + test (built 2026-06-24)

[`root_segment_proto.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/root_segment_proto.py) implements the text-slicer + glue gap (the head card +
one sub-card per `<div n="p">` / `<div n="m">` boundary, each carrying `root_key` /
`upasarga`) and asserts a **lossless** SPLIT→glue round-trip. Self-test on the probes:

```
L=55166  k1=BU   lines=1315  sub-cards=41 (1 head + 40 prefix)  round-trip=LOSSLESS
L=21814  k1=gam  lines=1695  sub-cards=63 (1 head + 62 prefix)  round-trip=LOSSLESS
L=72578  k1=gam  lines=180   sub-cards=36 (1 head + 35 prefix)  round-trip=LOSSLESS
```

Two findings the test surfaced (both confirm the RESULTS analysis):

1. **Raw `<div n="p">` count ≥ true-upasarga count.** The slicer finds **40** prefix
   divisions for `bhū` vs `preverb1`'s **38** upasargas — the surplus is exactly the FP
   class (`preverb1`'s shape-filter + 149-row exclude list reconcile 40→38). Confirms
   analysis #2: the cue needs `verbs01`'s guard before the sub-cards are trusted as verbs.
2. **The secondary-conjugation cue is dict-specific** (0 `<div n="m">` matched in PWG):
   `<div n="m">` is the **PW** caus/desid cue ([pw.txt L331019](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pw/pw.txt)); **PWG** marks caus/desid
   inline as `— <ab>caus./desid./intens.</ab>` (often inside `<div n="v">`/`<div n="p">`),
   which is what `preverb1.mark_entries_verb()` keys on. The per-dict segmenter rules in
   RESULTS therefore need a per-dict secondary-conjugation cue, not a shared one.
