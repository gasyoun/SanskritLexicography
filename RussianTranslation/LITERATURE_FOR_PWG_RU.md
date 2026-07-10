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

Plus exemplars: classical *Убежал [тот] осел, которого мы любили* (postposed →
который) vs. Sanskrit-type *Который осел убежал, того мы любили* (preposed →
correlative *кто…тот*, often with emphatic *и*).

### 1c. 19th-c. German → Russian term/spelling decoder
From **Delbrück** — the period German PWG is written in:

| German (period) | Modern | Russian | Note |
|---|---|---|---|
| Theil / getheilt | Teil | часть / разделенный | th→t |
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
- **Accusative under a deverbal noun = error** — *шитье шубы* (gen.), not *шубу*
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

## 6. Second pass — comparative lexicography, semantics, corpus methodology

Additions from the sources first judged off-topic. The big win is **§6 judge rules**:
the polysemy/distinctness tests give the QA stage a principled way to decide whether
two PWG German sub-senses should stay split or merge.

### Translator-prompt additions
- **Synonym-string cardinality.** Render a German synonym-string (*Glanz, Schimmer,
  Pracht*) as a Russian synonym-string of *equal cardinality* — never collapse to one
  word; each member is a distinct near-equivalent (Baalbaki, Arabic tradition).
- **Never abridge an entry.** A shorter Russian entry is a defect, not an improvement:
  Paul-the-Deacon's compression of Festus destroyed the very sense/form distinctions the
  source drew (Ferri, Latin). Preserve every sub-sense and source context.
- **Don't harmonize a multi-source entry** into one smooth Russian register — PWG entries
  are stratified accretions of glosses from different authorities; preserve the seams,
  smoothing is the error (Dickey, Greek scholia).
- **Function-word "use" definitions** (German *dient zum Ausdruck…*, *zur Bezeichnung
  von…*) → Russian function-paraphrase (*служит для выражения…*), never coerced into a
  noun-equivalent (Jackson's 4th definition type).
- **German `un-` forms:** follow the form actually used; don't auto-map *ungefährlich* to
  the lexical Russian antonym of *gefährlich* (the base is gradable, the *un-* form often
  absolute) (Riemer).
- **Preserve vagueness/underspecification** — a gloss that leaves gender/number/sub-type
  open is correctly vague; don't over-commit the Russian equivalent to one reading (Riemer).

### Judge-prompt additions
- **Sense-distinctness test battery (the headline addition).** To decide whether two PWG
  German sub-senses are genuinely distinct vs. should merge, apply three independent tests
  and weight by agreement: (a) **Quinean** truth test, (b) **zeugma/identity** test, (c)
  **definitional** test (distinct iff no single maximally-general-yet-minimally-specific
  gloss covers both). Calibrate by reading-distance — require a *strong* zeugma clash for
  metaphor/metonymy-linked senses before splitting (Riemer).
- **Autohyponymy is legitimate** — a general gloss + a narrowed technical/ritual gloss of
  the same word (very common in Sanskrit) is NOT redundant duplication; don't flag it as
  circular (Riemer).
- **Antonym-type-mismatch defect.** A German opposition must map to the same Russian
  sub-type — комплементарные (*dead/alive*) · градуальные (*long/short*, where *nicht lang*
  ≠ *короткий*) · реверсивы (*rise/fall*) · конверсивы (*buy/sell*). Don't render a converse
  as a gradable antonym (Riemer).
- **Synonym-string flattening** (n German near-synonyms → 1 Russian word) and
  **abridgement/context-loss** (dropping a distinction the German drew) are new defect
  classes (Baalbaki, Ferri).
- **Never "correct" a citation to match a suspect gloss.** The `<ls>` quote/siglum is an
  *independent* witness and is often textually sounder than the surrounding prose — if
  gloss and quote disagree, the quote usually wins (Dickey).
- **Respect source homonym numbering** — don't merge two superscript-numbered PWG
  headwords because their German glosses look close (splitting is etymology-driven, not
  sense-distance-driven), nor re-segment a single entry on sense-distance alone (Jackson).
- **`gewöhnlich`/`meist` is a hedge on a core sense, not a new sub-sense** — keep it
  attached, don't split on it (Jackson).

### Corpus-gate / strata additions
- **Quote-count as a confidence metric:** a sense backed by a single `<ls>` siglum carries
  lower grounding-confidence than a multiply-attested one — count distinct sigla
  (Baalbaki; sharpens the existing "weak grounding" kośa caveat).
- **Transmission-depth signal:** when a PWG gloss is visibly second-hand (copied from an
  earlier kośa/lexicon), lower confidence and don't present it as primary attestation
  (Ferri).
- **Association measures, not raw counts:** rank a candidate Russian sense by the
  association strength of its collocates (PMI / log-likelihood G² / Fisher exact), and do
  **not** read high raw frequency as association (Desagulier).
- **Dispersion test:** require a Russian sense to attest across *multiple* corpus texts
  (good dispersion), not just clear a token threshold — reject senses carried by one
  outlier text; compute normalized per-stratum rates, not pooled totals (Egbert & Biber).
- **Rater-agreement check** when a human verifies gate output (intra-/inter-rater
  reliability) (Egbert).

### Glossary additions
- **German register-cue → Apresjan tag crosswalk:** map German *abwertend/scherzh./iron.*
  cues to the §1d Russian register labels; connotation belongs in the label slot, not the
  gloss body (Jackson).
- **Sense-relation marker rows** (extend the §1c decoder): *auch genannt / ein anderes
  Wort für* → *также называется / другое название для*; negation *nicht…* → *не…* (keep
  polarity); *Teil von* → *часть…* (Jackson).
- **Opposite-type tagset:** комплементарные · градуальные · реверсивы · конверсивы (Riemer).
- **Controlled Russian metalanguage** for PWG's own apparatus terms (gloss vs. definition
  vs. citation vs. note) — the learned metavocabulary doesn't map 1:1 across traditions, so
  fix it once and enforce it (Dickey).

### Confirmed low/zero yield for pwg_ru
- **McEnery & Brezina** (philosophy of corpus science), **O'Keeffe & McCarthy Handbook**
  (spoken/multimodal alignment, not parallel-corpus), **Энциклопедический словарь юного
  филолога**, **Partridge** — nothing beyond what other sources state more usefully.
- **Not mined** (confirmed serving other repos, not DE→RU): the Sanskrit-syntax-theory set
  (Carnie, Gillon ×3, Ruppel, Kumar, Meenakshi, Speyer ×2, Lowe), the SLA/pedagogy set
  (Lu, Sinclair, Szudarski, Wong-Barcroft, Pérez-Paredes), and the DCS NLP/UD-eval set
  (Adapting-NLP, Evaluating-Syntactic-Annotation, Performance-POS, Patterns-of-Exchange).

---

## 7. Third pass — full-shelf completion (every remaining source)

Sweep of all files not yet touched. The high-value adds are the **compound-type Russian
names**, the **śāstric formula equivalents**, the **expanded correlative inventory**, and
the **lexicalized-participle keying** rule.

### Translator-prompt additions
- **Compound (samāsa) rendering, right-headed.** Build the Russian gloss off the *vigraha*
  (paraphrase), head = the **second** member: татпуруша *asi-kalaha* → «бой мечом» (head
  *бой*); never calque member-by-member off the first constituent. A literal member-by-member
  Russian calque should be flagged suspect (Gillon95/96, Apte).
- **Bahuvrīhi is exocentric** — denotes a possessor *outside* the compound; *hata-putra-* →
  «та, у кого убиты сыновья / чьи сыновья убиты», not the literal sum (Apte, Ruppel).
- **`-ādi`/`-prabhṛti` compounds** = open-ended category = the *hypernym* of members →
  «X и тому подобное / и прочее», never a closed dvandva list (Inglese & Geupel).
- **Split over-long compounds into clauses** rather than one Russian calque — Apte's own
  rule that stacked compounds become "unintelligible" (Apte §356).
- **Preserve the absolutive/participial character.** Sanskrit prefers gerunds, absolute
  locatives and noun-predicates over subordinate clauses; when a German gloss unpacks one
  into a finite/relative clause, keep the Russian деепричастный/participial where natural,
  don't over-subordinate (Speyer 1886).
- **Derived/compound headword may itself BE a relative clause** — gloss it as one
  («тот, кто…»), lifting an embedded Sanskrit head out and fronting it (Ruppel).

### Correlative-map additions (extend §1b)
- **Doubled relative** *yo yaḥ* = «кто бы ни / всякий, кто»; adverbial pairs
  *yatas…tatas* «откуда…оттуда», *yāvat…tāvat* «пока…до тех пор», *yadi…tarhi* «если…то»
  (Ruppel).
- **Multiple-head correlative** (two relative pronouns, one-to-one to two correlates) →
  distributive Russian «каждый… того, с кем…», not a single *который* pair (Lipták).
- **Default reading is maximalizing/universal/definite** → correlate defaults to «все, кто…»
  / «тот, кто…»; use «два/некоторые» only with an explicit partitive (Lipták).
- **`yad…tad` is a *weak* correlative** — one form covers restrictive, appositive,
  conditional («если…»), and indirect-question readings. **Judge/gate: widen the acceptable
  band** — flag a Russian rendering only when it contradicts the German, not merely for
  choosing conditional/appositive over restrictive (Davison LSA08; Historical Syntax:
  Vedic-flavored citations may be paratactic «…, и тот…», not subordinate).

### Glossary additions
- **Compound-type Russian names:** татпуруша (определительное/падежное) · кармадхарая
  (аппозитивное определительное) · бахуврихи (притяжательное/посессивное, «тот, у кого…»)
  · двандва (копулятивное/сочинительное) · авьяйибхава (наречное неизменяемое) · двигу
  (числительное определительное) (Apte).
- **Absolutive/case-construction names:** локативный абсолютив (абсолютный локатив) as the
  canonical rendering for абсолютные обороты (genitive absolute = the marked variant);
  dative subtypes «датив выгоды/заинтересованности» (*commodi*) vs «датив цели» (*finalis*)
  (Speyer 1886).
- **Śāstric analysis formulas → fixed dry Russian equivalents** (don't re-translate per
  occurrence): *iti arthaḥ* → «то есть; таков смысл»; *anena … vivakṣitam* → «этим он хочет
  сказать»; *X-bhāvaḥ* → «состояние/свойство X» (Tubb). Their presence also *marks* a gloss
  as scholastic-register → flat terminological Russian.

### Corpus-gate / strata additions
- **Lexicalized participle ≠ live participle — separate keys.** A `-ant/-vant/-ta` surface
  form (e.g. *sunvánt-* "Soma-presser") can attest either the verb's sense or a lexicalized
  nominal sense; don't collapse them onto one headword key, and flag `-ta/-na/-ant` forms as
  POS-ambiguous when keying (Lowe).
- **Sense-by-distinct-collocate-set:** two proposed Russian senses drawing on the *same*
  Sanskrit collocate set are likely one sense (merge); genuinely distinct senses show
  distinct collocates (Sinclair) — a concrete sense-split/merge cross-check.
- **Decision-list WSD with positional weighting:** weight disambiguating collocates by
  offset/distance (Smadja-style), not flat PMI, when picking the cue for which sense a usage
  supports (Ryan).
- **Range via `nunique()`** as a fast pre-filter (how many texts/strata a sense appears in)
  before the heavier dispersion test (Keller).

### QA / human-verify additions
- **Jaccard span-IoU agreement metric** for the human-verify step: measure agreement on
  *which Sanskrit token-span* a Russian sense attaches to (intersection-over-union of spans),
  since the unit boundaries themselves vary and label-kappa doesn't apply. Report
  `raw → cleaned → cleaned-sameSeg`; budget more review on prose strata (lower reliability
  than metrical) (Biagetti & Hellwig).
- **Grammatical-parallelism check:** when the German sets two glosses in analogous slots
  (paired/antithetical sense-lists, dvandva-style "X und Y"), the Russian should preserve
  the same case/number/POS parallelism across the pair, not vary the construction — judge
  symmetry, not just lexical accuracy (Jakobson).

### Display / learner-layer additions
- **Sense-ordering policy:** PWG is a 19th-c. *historical* dictionary, so its sense order is
  genealogical; a modern pwg_ru may legitimately re-sort senses by frequency/generality for
  the reader (Allan) — but keep this an explicit, flagged transform, not silent.
- **Coverage-tier profiling for the learner layer:** compute SLP1-lemma coverage over the
  aligned corpus to bucket headwords into core / mid-frequency / specialist tiers; the
  mid-frequency band is the learner layer's primary target (Szudarski). Attach paradigm +
  KWIC corpus-concordance links around the gloss (Allan mediostructure).

### Coverage ledger (every source, honest verdict)

| Status | Sources |
|---|---|
| **Mined — new material** | Peshkovsky · Testelets · Lomov · Синтаксис-2009 · Mitrenina · Zaliznyak-Paducheva · Apresjan · Hartmann · Bloomsbury · Klosa · Leitan · Delbrück · Renou · Gonda-Vogel · Baalbaki · Ferri · Dickey · Jackson · Riemer · Desagulier · Egbert · Apte-Composition · Tubb · Inglese-Geupel · Speyer-1886 · Gillon95 · Gillon96 · Ruppel · Correlatives-Cross-Ling · Lowe · Biagetti-Hellwig · Szudarski · Keller · Ryan · Sinclair · Allan · Jakobson · Davison-LSA08 |
| **Overlap only** (covered elsewhere) | Gillon-Shaer (in Gillon96) · "55"=Mitrenina-correlatives (in mitrenina_fdsl) · Kumar (nominalization typology) · Historical-Syntax (paratactic→hypotactic, 1 line) · Gerow (marginal learner note) |
| **Zero yield for pwg_ru** | McEnery · O'Keeffe · Partridge · Энциклопедический-словарь · Patterns-of-Exchange · StrategiesDoing · Pérez-Paredes · Lu · Wong-Barcroft · Applied-Ling ×2 · Carnie · Teaching-English-YL · Bowern · AEK (RU intro textbook) |
| **⚠ Blocked — needs OCR / re-extract** | Speyer-1895 (image PDF, 0 chars) · Meenakshi-1983 (no OCR body) · Rātānjanakar/Hints (Devanagari OCR noise) · Загадки_5 (Cyrillic mojibake) · Adapting-NLP & Performance-POS (mis-titled multi-paper bundles; the relevant single paper wasn't OCR'd) |

> **Actionable:** the five **⚠ blocked** sources can't be mined until re-OCR'd. Worth a
> `/cologne-preface-ocr`-style pass on Speyer-1895 (a genuinely relevant German source) and
> re-extracting the two NLP proceedings to isolate the Hellwig tagger paper.

---

*Mined 2026-06-26 from the full-text `literature/md/` extractions across three passes
(16 + 9 + ~37 sources = the whole shelf) via per-source close reading. Highest-value adds:
the §6 sense-distinctness test battery (judge), the §1b/§7 correlative map (translator),
and the §1c/§7 German→Russian + compound-type glossary tables.*
