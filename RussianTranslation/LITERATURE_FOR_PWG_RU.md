# Literature harvest for `pwg_ru` (German → Russian)

What the `literature/` reference shelf gives the **German→Russian** translation of
the Petersburger Wörterbuch (Böhtlingk–Roth, 1855–1875). Mined one source at a
time against the five insertion points of the pipeline: **glossary**,
**translator prompt** ([pwg_ru_prompts/1_perevod.txt](pwg_ru_prompts/1_perevod.txt)),
**judge prompt** ([pwg_ru_prompts/2_qa_sudya_opus.txt](pwg_ru_prompts/2_qa_sudya_opus.txt)),
**corpus gate / strata** ([HARVEST.md](HARVEST.md), `src/build_strata.py`), and
**display/web** (CDSL frontend).

> **Note on the shelf.** The files under
> [`../literature/md/`](../literature/md/INDEX.md) are *stubs* — one-line pointers.
> The actual content is the PDFs under [`../literature/`](../literature/). The
> mapping of which source serves which repo is
> [`../literature/md/INDEX.md`](../literature/md/INDEX.md) (Renou and Apresjan now
> carry the **RuTrans** tag).

## Sources mined vs. skipped

| Mined (bears on DE→RU) | Skipped (serves DCS / csl-atlas / SaLex, not pwg_ru) |
|---|---|
| Peshkovsky · Testelets · Lomov · Синтаксис-2009 · Zaliznyak-Paducheva · Mitrenina | Corpus-stats books (Desagulier, McEnery, Programming-for-CL, Doing-Linguistics) |
| Apresjan *Systematic Lexicography* · Hartmann & James · Bloomsbury Companion · Partridge | SLA / corpus-pedagogy (Lu, Sinclair, Szudarski, Wong-Barcroft) |
| internet lexicography (Klosa) | Sanskrit-compound / POS-tagger / UD-eval (Gillon, Rātānjanakar, Inglese-Geupel) |
| Delbrück *Altindische Syntax* (German source decoder) · Renou · Gonda/Vogel | Syntax-theory handbooks (Carnie, Lowe, Ruppel) — only marginal |
| Leitan handout · Entsiklopedicheskiy (low yield, noted) | |

Skip rationale: the corpus-statistics and SLA books inform the *corpus* and *teaching*
layers, not the act of rendering 19th-c. German into Russian. They remain tagged to
**DCS**/**RuTrans-methodology** in the INDEX.

---

## 1. Glossary drop-ins (highest reuse)

These are lookup tables to seed `glossaries/` so every card uses the same Russian.

### 1a. Canonical modern-Russian grammatical term set
From **Peshkovsky / Testelets / Lomov** — use these forms, never Latin (*accusativus*)
or German (*Genitiv*) labels, and never a dated/rare synonym:

- **Cases:** винительный · родительный · дательный · творительный · предложный (падеж).
- **Semantic roles (Testelets, authoritative):** агенс · пациенс · бенефактив(=реципиент) · экспериенцер · стимул · инструмент · адресат · источник · цель. Avoid the unstable periphery (*средство, маршрут, результат*).
- **Voice/diathesis:** действительный/активный залог · страдательный/пассивный залог · возвратный (-ся) · взаимный; valency ops: каузатив · аппликатив · декаузатив.
- **Government:** сильное / слабое управление; беспредложное (непосредственное) vs предложное (опосредствованное) управление — render German "regiert den Akk." / "mit Präp." with these exact labels.
- **Lomov rulings (prefer canonical over rare):** агенс (not *агент/агентив*) · косвенное дополнение (not *непрямой объект*) · наречное (not *адвербиальное*) словосочетание.

### 1b. Correlative / relative map (Sanskrit *yad…tad* → Russian)
From **Mitrenina** (verbatim table) + **Zaliznyak-Paducheva**:

| Relative (XPrel) | Anaphor (XPana) |
|---|---|
| кто | тот |
| что | то |
| какой | такой / тот |
| чей | того / тот |
| где | там |
| куда / откуда | туда / оттуда |
| когда | тогда |
| как | так |
| сколько | столько |
| чем | тем |
| каков | таков *(archaic, copular only)* |

Plus exemplars: classical *Убежал [тот] осёл, которого мы любили* (postposed →
который) vs. Sanskrit-type *Который осёл убежал, того мы любили* (preposed →
correlative *кто…тот*, often with emphatic *и*).

### 1c. 19th-c. German → Russian term/spelling decoder
From **Delbrück** — the period German PWG is written in:

| German (period) | Modern | Russian | Note |
|---|---|---|---|
| Theil / getheilt | Teil | часть / разделённый | th→t |
| thun, That | tun, Tat | делать, деяние | th→t |
| citirt, anführen | zitiert | цитируется, приводить | source ref |
| Uebersetzung | Übersetzung | перевод | Ue→Ü |
| Sprachgebrauch | — | словоупотребление, узус | key gloss term |
| Stelle | — | место, пассаж | text locus |
| Wendung | — | оборот (речи) | |
| bezeichnet | — | обозначает | definition verb |
| Localis / Instrumentalis | Lokativ | локатив·местный / творительный | case |
| Genera Verbi | — | залоги глагола | grammar |
| erstarrt (Form) | — | застывшая, окаменевшая форма | |
| Congruenz | Kongruenz | согласование | |
| specifisch | spezifisch | специфический | c→z |
| Dativus commodi / Nomina actionis | — | *(keep Latin)* датив выгоды / имена действия | Latin tag stays |

### 1d. Russian register tagset (Apresjan, verbatim)
высок./книжн./офиц./поэт. · разг./прост. · груб./жарг./бран. ·
ласк./неодобр./ирон./презр. · устар./арх./ист./нов. · обл./диал. — adopt as the
project's register labels; the judge flags a gloss whose register drifts from the
German marking.

### 1e. Gloss-expansion idiom (Leitan)
Use **«т. е.»** as the canonical Russian connector when expanding a sense
(*īpsitam, т. е. желаемое*); fixes Russian names for derivational categories
(дезидератив, интенсив, каузатив, деноминатив, композит) for when German prose
*spells them out* (never the abbreviations themselves).

---

## 2. Translator-prompt rules

- **Decode period spelling first.** Add an instruction that `That/thun/Theil/citirt`
  are 19th-c. forms, not unknown tokens (Delbrück §1c).
- **Gloss-verb aspect default = imperfective infinitive** (*бить*, not *ударить*)
  for the lemma sense; German tenseless infinitives under-specify aspect (Peshkovsky).
- **Force manner of motion/position** Russian requires (идти/ползти/лететь;
  стоять/лежать/висеть) from context — German leaves it open and a wrong default is
  grammatical-but-false (Apresjan).
- **Pick the synonym by register, default to the dominant.** Absent a German register
  cue, use the neutral Russian dominant; reserve marked synonyms (*покидать, зреть*)
  for elevated/archaic German — prevents "unmotivatedly elevated" Russian (Apresjan).
- **Prefer accurate paraphrase over a snappy-but-skewed word.** For culture-bound
  Sanskrit headwords give a discursive Russian explanation rather than force a wrong
  single equivalent (Adamska-Sałaciak; Hartmann's explanatory-equivalent).
- **Zero copula.** German *"ist ein…"* → bare Russian nominative; do not insert
  *есть/является* (Peshkovsky).
- **Preserve correlative shape & assertion direction.** Render *yad…tad* as a preposed
  Russian correlative (*кто…тот*, with idiomatic *и*) when the German keeps the
  correlative order; keep both pairs of a double-*ya-* construction; don't flip which
  clause is asserted (Mitrenina, Zaliznyak-Paducheva).
- **Punctuation carries sense-grouping:** comma = interchangeable equivalents, semicolon
  = non-interchangeable; preserve PWG's punctuation semantics in the Russian
  (Adamska-Sałaciak).
- **Preserve hedges** (*vielleicht, wohl, unklar, etwa* → *возможно, по-видимому,
  неясно*); do not resolve an editor's deliberate uncertainty into a confident gloss
  (Delbrück).
- **Keep PWG's sense order and numbering**; reordering/merging German sub-senses is out
  of scope (Hartmann; and note sense #1 ≠ "most common" — kośa ordering is topic-based,
  Vogel).

---

## 3. QA-judge rubric additions

Concrete, checkable defect classes for the judge stage (OK/BAD + severity):

- **Agreement is a hard gate**, aspect is soft: лицо/число/род/время/наклонение must
  agree; aspect choice is stylistic (Peshkovsky).
- **Accusative under a deverbal noun = error** — *шитьё шубы* (gen.), not *шубу*
  (Peshkovsky).
- **Perfective verb + `-ся` passive = construction error**; agent of a Russian passive
  is bare instrumental, not *от*+gen. (Testelets, Lomov).
- **Relative `что` only in Nom/Acc;** `который`'s case comes from inside its own clause
  (never case-attraction from the antecedent); required correlates
  (*тот/то/настолько/тем*) must not be dropped (Zaliznyak-Paducheva, Синтаксис-2009).
- **Russian theme-rheme word order**, not calqued German/source order (Синтаксис-2009).
- **Circularity / cryptographic gloss:** BAD if the Russian gloss is more obscure than
  the headword, metaphorical where the German was literal, or defines a word by itself
  (Apresjan).
- **Equivalent-type mismatch:** flag a single Russian word forced onto a culture-bound
  term needing a paraphrase, and needless paraphrase where a clean word exists
  (Hartmann).
- **Polyequivalence / under-differentiation:** every numbered German sub-sense must
  surface a *distinct* Russian equivalent; identical Russian across two numbered senses
  is a discrimination failure (Hartmann).
- **Register label is a separate defect from a wrong gloss** — score a correct
  equivalent with a dropped German label as still flaggable (Hartmann).
- **Latin tag check:** the Latin grammatical term is retained AND its German host clause
  was rendered, not dropped (Delbrück).
- **Don't penalize legitimate encyclopedic content** in a gloss (historical dictionaries
  blend definition + realia — Considine).
- **Spurious `является/есть`** in a present-tense nominal gloss is unidiomatic
  (Peshkovsky).

---

## 4. Corpus gate / strata

- **Renou five-period spine** to drive the strata tagger: I Vedic (Ṛgveda→AV→
  brāhmaṇa-prose→Sūtra) · II Classical/Pāṇinian · III Epic (MBh, Purāṇa, Smṛti,
  kārikā) · IV Classical kāvya/kathā/commentary · V Buddhist/Jaina hybrid. These are
  **register tiers, not just dates**, and overlap — **tag per sense, not per headword**.
- **Register → Russian register:** brāhmaṇa/Sūtra = dry terminological Russian; kāvya =
  elevated literary; kathā/drama = neutral narrative (Renou).
- **Flag hybrid/Buddhist/Jaina citations** so the annotator doesn't penalize genuine
  non-standard forms as "wrong Classical" (Renou).
- **Vedic poetic vs Brāhmaṇa-prose is a real split** — a PWG "ved." vs "Brāhm." ref are
  different strata; Pāṇini's rules diverge from attested Brāhmaṇa usage (Delbrück).
- **kośa-source caveats (Vogel):** a sense sourced to a synonymic *kośa* has *weaker*
  textual grounding than a cited passage (confidence signal for the gate); kośa
  sense-order is topic-grouping, not frequency; dual/plural in a homonymic kośa entry is
  a **sense-count artifact** (dual = 2 senses), not real morphology — don't render
  literally; exclude metrical filler particles from the translatable span; long German
  synonym chains may be an unresolved *dvandva* — flag for sense-splitting.
- **Strong (governed) vs weak (circumstantial) participants:** keep a governed argument's
  fixed case in the gloss; circumstantials are freely phrasable (Peshkovsky, Testelets).

---

## 5. Display / web (CDSL frontend)

- **Model cross-references as data, render as one-click links.** Turn every German
  `s.`/`vgl.`/sense pointer into a resolved hyperlink (link relation vs marker vs target,
  Klosa §5). Build both **structural** in-entry links (sense navigator, attestations) and
  **content** links (outward to MW and sibling Cologne dicts).
- **Semasiological search toolkit** on the headword field: type-ahead, case-insensitive,
  **fuzzy/transliteration-tolerant**, wildcard (all `-tva` / `√gam`), and inflected-form
  search via lemmatisation (Klosa).
- **Full-text search over the Russian gloss** gives a free **onomasiological** (Russian
  concept → Sanskrit word) reverse index — worth verbalising glosses consistently so it
  works (Klosa).
- **Faceted filters** on POS, `<ls>` source, sense count, root — model these as
  filterable fields (Klosa).
- **Toggle, don't replace:** ship PWG front-matter/abbreviations with Russian equivalents
  as a *switchable* original-German vs Russian view, not a destructive overwrite
  (Adamska-Sałaciak).
- **Post-translation QA tool:** dump all cross-refs as a graph to find dangling/unresolved
  links and orphan entries (Klosa, Wiktionary-atlas method).
- **Preserve the historical apparatus verbatim** — modernise only the German *prose*;
  lemma → senses → dated attestations is the entry's evidential backbone, `<ls>` refs are
  load-bearing and never translated (Considine).

---

*Mined 2026-06-26 from 16 PDFs under [`../literature/`](../literature/) via per-source
close reading. Lower-yield note: the Soviet *Энциклопедический словарь юного филолога*
and Partridge's *Gentle Art* added little beyond what Синтаксис-2009 and Apresjan state
more authoritatively.*
