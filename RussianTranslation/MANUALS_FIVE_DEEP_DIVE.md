# The five load-bearing manuals — theoretical input for the Sanskrit–Russian dictionary

A deep-dive companion to [`MANUALS_FOR_PWG_RU.md`](MANUALS_FOR_PWG_RU.md) (the
37-manual audit) and [`LITERATURE_FOR_PWG_RU.md`](LITERATURE_FOR_PWG_RU.md) (the
by-insertion-point harvest). This file takes the **five manuals that most change the
run** and documents, in detail and grounded in each book's actual text, what theory
each contributes to the Sanskrit work — specifically the making of a **Sanskrit–Russian
dictionary** by translating the Petersburg Sanskrit–German Dictionary (PWG /
Böhtlingk–Roth, 1855–1875) into Russian (`pwg_ru`).

Each manual was deep-read in its full-text extraction under
[`../literature/md/Lexicography-Manuals/`](../literature/md/INDEX.md) (these are **not**
one-line stubs — Apresjan ≈ 980 KB, Riemer ≈ 2.5 MB, Hartmann ≈ 583 KB, Gonda–Vogel ≈
312 KB, Klosa ≈ 807 KB of OCR'd text). Quotations and page/chapter anchors below are
from those extractions.

**Why these five.** They are the four corners plus the roof of a bilingual historical
dictionary: **Apresjan** fixes the *target-language* discipline (how Russian must be
written); **Riemer** fixes *sense individuation* (when one Sanskrit word is two);
**Hartmann & James** fix *equivalence* (how a German sense becomes a Russian one);
**Gonda–Vogel** fix *source-evidence weighting* (how much a kośa citation is worth);
**Klosa** fixes *delivery* (how the finished entry lives as queryable data on the web).
Together they touch all five pipeline insertion points — glossary, translator prompt,
QA-judge prompt, corpus gate, web display.

---

## Apresjan — Systematic Lexicography (2008)

Jurij Apresjan's *Systematic Lexicography* (tr. Kevin Windle, Oxford 2008) is the
programmatic statement of the Moscow Semantic School's approach to dictionary-making.
Its thesis is that a lexicon is not a list of independent entries but a structured
object whose every word is the intersection of (a) classes it shares with others and
(b) properties unique to it. Four "keynotes" organize the book: the language picture of
the world, **lexicographic types**, **lexicographic portraits**, and the **integrated
description** of language.

**1. Core theory.** A *lexicographic type* is "a group of lexemes with a shared property
or properties, not necessarily semantic, which are sensitive to the same linguistic
rules and which should therefore be uniformly described in the dictionary" (Introduction
§2; cf. ch. 11.1). Apresjan's worked example is factive vs. putative mental predicates
(*know* vs. *think*), which differ systematically in government, prosody, and
rheme/theme behaviour. A *lexicographic portrait*, by contrast, is "an exhaustive
account of all the linguistically relevant properties of a lexeme, with particular
emphasis on the semantic motivation of its formal properties" (Intro §3; ch. 9.1.1).
The two are complementary: types handle "unification," portraits handle
"individuation" — "one should give equal attention to the shared properties of lexemes
… and to what distinguishes them." The **principle of integrated/uniform description**
demands that grammar and dictionary be "mutually adjusted," using the same categories
and formal devices, so a property posited for a type is recorded identically in every
member. Underpinning all of this is a **unified semantic metalanguage** (ch. 10.1): "a
sub-language" whose basis "is semantic primitives," reduced and disambiguated (one
stylistically neutral word chosen per synonym row), in which all senses across the whole
dictionary are explicated by the same controlled vocabulary, moving "closer to the
metalanguage of Anna Wierzbicka."
→ *Sa–Ru application:* the metalanguage maps to a **closed glossary of fixed Russian
terms** — one canonical gloss per recurring Sanskrit concept (kāraka roles, grammatical
categories, deictics) — so PWG's German is rendered uniformly, not ad hoc per card.
Lexicographic types become **judge rubrics**: all Sanskrit causatives, all denominatives,
all "verbs of motion" get one prescribed treatment the QA judge checks against.

**2. Lexical functions / Moscow School framing.** The book sits inside the
Meaning⇔Text apparatus, where collocational and paradigmatic relations are captured by
*lexical functions* and where each entry is built from explication + government pattern +
lexical-function zone. For microstructure this means an entry is not just gloss +
examples but a fixed set of zones (semantics, syntax/valency, co-occurrence, prosody).
→ *Sa–Ru application:* fix the **entry microstructure** as named zones (sense → Russian
gloss → government/valency → collocations → register), so every PWG card is parsed into
the same slots and the **web display** can render them consistently.

**3. Register/stylistic marking and connotations.** Apresjan gives the verbatim
traditional tagset (ch. 4.1.2): literary style — *vysok.* (высок., high), *knizhn.*
(книжн., bookish), *ofic.* (офиц., official), *poet.* (поэт.); spoken — *razg.* (разг.,
colloquial), *prost.* (прост., substandard); sub-literary — *grub.*, *zharg.*, *bran.*;
attitudinal — *lask.*, *neodobr.*, *iron.*, *prezr.*, *prenebr.*; plus domain, temporal
(*ustar.*, *arkh.*), and spatial labels. He adds innovations *neobikhodn.* (formal,
between bookish and neutral) and *narrat.* (narrative). Crucially, **connotations are a
separate descriptive layer** from denotation: *lakej* carries "subservience, servility"
vs. *sluga* "loyalty"; *osël* "stupidity and stubbornness" vs. *išak* "uncomplaining
diligence" — same referent, different connotational charge (ch. 4.1.4).
→ *Sa–Ru application:* the **translator prompt** must carry a register flag forward (a
hymnic/Vedic word should not be glossed with разг. Russian); the **glossary** stores
connotation as its own field so synonymous Sanskrit pairs do not collapse to one neutral
Russian word; the **judge** flags register mismatch as an error class. (This is the §1d
register tagset already adopted project-wide.)

**4. Manner of motion / position.** Apresjan's signature contrast (Intro §1): Russian
*grammatically forces* a manner verb where French/German use a neutral verb. "The dog
left its kennel" must become *Sobaka vybezhala* (ran out) / *Zmeja vypolzla* (crawled
out) — neutral *pokinula* "sound[s] unmotivatedly elevated." For position, Russian
"forces its speakers … to specify the way they are positioned (e.g. whether they
*stand, lie, or hang*)": *stoial / viseli / lezhali*, where neutral *nakhodit'sia*
"would be odd." German leaves manner open.
→ *Sa–Ru application:* PWG's German *liegen/stehen* neutrality cannot pass through
untouched — a default like «лежать» for an object that hangs is **grammatical but
false**. The translator prompt must require manner/position resolution from context; the
**corpus gate** supplies the disambiguating context; the judge rejects a default-neutral
verb where Russian forces a choice.

**5. Synonym discrimination and the dominant.** Each synonym series begins with a
*dominant* — "a lexeme which has the most general meaning … the broadest application and
co-occurrence, and is most neutral from the point of view of style, pragmatics …
grammar, and prosody" (ch. 4.1.1). Other members are differentiated by added components
and by register (e.g. *zhalovat'sia* neutral vs. *setovat'* formal vs. *roptat'* bookish
vs. *skulit'/khnykat'* low-colloquial).
→ *Sa–Ru application:* where one Sanskrit headword has several Russian candidates, the
glossary names the **dominant as the default gloss** and ranks alternates by register;
the judge checks that a marked synonym was chosen only when the source warrants it.

**6. Anti-circularity / cryptographic-gloss prohibition.** Explications must be
"non-circular, … necessary and sufficient, … hierarchically structured, … explicit"
(ch. 10.1.2): a word may not be defined by itself, and the definiens must decompose into
*simpler* blocks down to primitives. Apresjan attacks "cryptographic metaphors" that "do
not clarify complex meanings, but encipher simple ones" (ch. 4 fn.) — a gloss more
obscure than the headword.
→ *Sa–Ru application:* a hard QA rule — reject a Russian gloss that reuses a
transliterated Sanskrit term, is itself rarer than the headword, or is circular. The
judge enforces "definiens simpler than definiendum"; the glossary forbids defining a
Sanskrit term by another untranslated Sanskrit term.

---

## Riemer — The Routledge Handbook of Semantics (2015)

### 1. Polysemy and why a dictionary cannot stay neutral
The central methodological problem is set out in Dirk Geeraerts' chapter 13
("Polysemy"): given that *clown* applies to a circus jester, a "comic entertainer in
general", and a metaphorical buffoon, "what arguments exactly do we have to say that
these are different meanings of the word?" Geeraerts documents a shift "from a static
conception of polysemy, in which senses are well-defined linguistic units" to a
"flexible and dynamic view of meaning" — Cruse's "seamless fabric of meaning-potential"
(1982). A dictionary, however, *must* take a stance: every numbered subsense is an
editorial commitment that two readings are distinct. PWG already encodes such
commitments in German; pwg_ru re-litigates each one in Russian. The handbook supplies
the test battery for that decision.
→ **Sa–Ru application.** Treat each PWG sense number as a *hypothesis to be tested*, not
an inherited fact. Tag every sense node with a `split-confidence` field (high /
borderline / lumped-from-German) so the QA-judge can flag low-confidence splits for
review rather than mechanically mirroring the German numbering.

### 2. The sense-distinctness test battery
Geeraerts (§2.1) distinguishes **three** criteria, explicitly noting they "are in mutual
conflict … in the sense that they need not lead to the same conclusion."

(a) **Quinean truth-theoretical test** (Quine 1960: 129): "a lexical item is polysemous
if it can simultaneously be clearly true and clearly false of the same referent" —
*Sandeman is a port but not a port*. Are the two readings "intuitively sufficiently
dissimilar"?

(b) **Zeugma / identity ("crossed readings") test** (Zwicky & Sadock 1975; Lakoff's
*and so* construction): identity-of-sense anaphora. *At midnight the ship passed the
port, and so did the bartender* is awkward on a crossed reading, signalling two senses;
*Vintage Noval is a port, and so is blended Sandeman* coordinates freely, signalling
vagueness, not polysemy.

(c) **Definitional (Aristotelian) test**: an item has more than one meaning "if there is
no minimally specific definition covering the extension … as a whole," and "no more
lexical meanings than there are maximally general definitions." Definitions must be
*maximally general* (blended + vintage port collapse under "sweet fortified wine from
Portugal") yet *minimally specific* (not "thing, entity").

The tests **disagree**, and Cruse's coordination chain shows that "readings that are
close together can be coordinated without oddity, but if they are sufficiently far apart,
they are incompatible" — a **reading-distance** continuum, not a dichotomy.
→ **Sa–Ru application.** Encode a three-vote rule in the QA-judge prompt: split a Russian
sense only when ≥2 of {Quinean clash, zeugma clash, definitional non-coverage} agree.
For metaphor/metonymy-linked pairs (e.g. *aṅga* "limb" → "subsidiary member of a
ritual/treatise"), require a **strong** zeugma clash before splitting, since near
readings coordinate freely.

### 3. Ambiguity vs vagueness vs generality
Geeraerts separates *conceptual underspecification* (*neighbour* is genuinely unspecified
for gender — no one asks "which sense, male or female?") from *ambiguity* (*she is a
plain girl* — "ugly" or "unsophisticated?"). Tuggy (1993) frames it as entrenchment:
ambiguity = two entrenched senses with no close subsuming schema; vagueness = unentrenched
readings under a close schema. Lexicographic rule: **do not over-commit the equivalent**
where the source is deliberately general.
→ **Sa–Ru application.** Translator rule: when PWG gives a broad German gloss, prefer an
equally broad Russian word over a narrowing one. E.g. *jana* "person/people/creature" —
render «человек/люди» generically, not the contextually narrower «подданный», unless the
entry attests that sub-sense.

### 4. Autohyponymy
Geeraerts' key disagreement case: *dog* = "Canis familiaris" *and* "male Canis
familiaris". The definitional test sees no ambiguity (the narrow reading is a proper
subset), yet *Lady is a dog but not a dog* "cannot be ruled out as ungrammatical" (Quinean
test fires). This general+narrowed pairing is **legitimate, not circular duplication**.
→ **Sa–Ru application.** Sanskrit is saturated with ritual/technical narrowings of common
words: *havis* "(any) oblation" vs the specific clarified-butter offering; *karman*
"action" vs "ritual act"; *mantra* "counsel/formula" vs "Vedic verse". Tag such senses
`autohyponym:technical` and license keeping both the general Russian gloss and the ritual
one — the QA-judge must *not* merge them as redundant.

### 5. Antonymy sub-types
Chapter 14 (Storjohann, "Sense relations") gives the four-way split: **complementary**
(*dead/alive* — binary); **gradable** (*long/short* — "*X is not long* does not entail *X
is short*"); **reversive** (*fall/rise* — opposite paths); **converse** (*buy/sell*,
*parent/child* — "different perspectives of one event"). Mapping a converse onto a
gradable scale is a category error.
→ **Sa–Ru application.** Tag opposition senses with `antonym-type`. The QA-judge rejects
a Russian gloss that turns a converse into a gradable — *pati/patnī* (husband/wife,
converse roles) must not be glossed as scalar. And "not-long" ≠ "short": for *dīrgha*
"long", do not let *adīrgha* collapse to «короткий».

### 6. Morphological negation
Storjohann's German finding: *gefährlich/ungefährlich* — the base is gradable, but the
*un-* form "does not indicate a degree … but an absolute state," behaving as a
complementary. **Follow the attested form**, not the assumed symmetry.
→ **Sa–Ru application.** Directly relevant to Sanskrit privative *a-/an-*. *amṛta*
("non-dying" → absolute "immortal") is not a mere gradable negation of *mṛta*. Rule:
gloss each *a-* form on its own attested behaviour; the privative often denotes an
absolute state where the base is scalar.

---

## Hartmann & James — Dictionary of Lexicography (2002)

This terminological dictionary of the field supplies the precise vocabulary in which the
equivalence problem at the heart of a Sanskrit→Russian dictionary can be stated. Its
entries are short and definitional; the relevant ones cluster around **anisomorphism**,
**equivalence/equivalent**, **equivalence discrimination**, **sense discrimination**,
**diasystematic labelling**, and **structural indicator / punctuation**.

**1. Anisomorphism.** The headword *anisomorphism* is defined as "A mismatch between a
pair of languages due to their semantic, grammatical and cultural differences. This leads
to a relative absence of direct, one-to-one translation EQUIVALENTS." Because Sanskrit
and Russian carve up meaning, grammar and culture differently, a PWG headword will rarely
map onto a single clean Russian word. The *equivalence* entry draws the consequence:
"Because of the problem of ANISOMORPHISM, equivalence is 'partial' or 'relative' rather
than 'full' or 'exact' for most contexts."
→ **Sa–Ru application:** the translator prompt must treat one-to-one Russian glosses as
the exception, not the default; the QA-judge should never penalise a *set* of Russian
equivalents as "over-translation" when the Sanskrit sense is genuinely diffuse.

**2. Typology of equivalents.** The *equivalent* entry: "A word or phrase in one language
which corresponds in MEANING to a word or phrase in another language… translation
equivalents are typically partial, approximative, non-literal and asymmetrical… recourse
must be had to surrogate EXPLANATORY EQUIVALENTS." The plain **translation equivalent**
is a target-language word/phrase (Zgusta's "cognitive" insertable equivalent). The
**explanatory equivalent** — "In the translation of CULTURE-SPECIFIC VOCABULARY, the
explanation of a word or phrase by means of a surrogate PARAPHRASE in the target language
rather than a one-to-one EQUIVALENT" — is the discursive fallback. *Lexical gap* and
*culture-specific vocabulary* mark the zero-equivalence case.
→ **Sa–Ru application:** culture-bound Sanskrit terms (*dharma*, *brāhmaṇa*, *yajña*,
ritual/philosophical realia) take a **paraphrastic explanatory equivalent** in Russian,
optionally with a transliterated loan; ordinary nouns/verbs take a direct translation
equivalent. QA-defect class: a bare one-word Russian gloss given where the source is a
lexical gap (false full-equivalence).

**3. Equivalent / meaning discrimination.** *equivalence discrimination* = "SENSE
DISCRIMINATION in the bilingual dictionary. Words with multiple meaning
('polyequivalence') need to have translation EQUIVALENTS specified for each of these
meanings." *meaning discrimination* and *sense distinction* both cross-refer to *sense
discrimination*, "The division inside a dictionary entry of distinct SENSES of a word or
phrase." The defect this guards against is under-differentiation: collapsing two source
sub-senses into one undifferentiated Russian blob.
→ **Sa–Ru application:** each numbered German sub-sense in PWG must yield its **own
distinct Russian equivalent block**; the QA-judge flags *polyequivalence
under-differentiation* whenever two PWG senses receive identical or overlapping Russian
wording, or when sense-2 silently inherits sense-1's gloss.

**4. Microstructure & punctuation semantics.** *punctuation*: "Dictionaries use
conventional punctuation marks in a variety of ways, e.g. as STRUCTURAL INDICATORS."
*structural indicator*: "A device which signals links and divisions within the text of a
reference work… punctuation marks (e.g. colons, semicolons, brackets)… inside entries."
In the standard convention these entries presuppose, a **comma** separates
near-synonymous, interchangeable equivalents within one sense, while a **semicolon**
separates distinct, non-interchangeable senses/equivalent groups. PWG already encodes its
sense architecture partly through exactly this comma/semicolon contrast.
→ **Sa–Ru application:** punctuation is load-bearing, not cosmetic — the translator must
**preserve PWG's comma vs semicolon** in the Russian output (comma → list of synonymous
Russian glosses; semicolon → boundary between senses). QA-defect class: a semicolon
flattened to a comma (or vice versa) silently destroys a sense boundary and must fail.

**5. Diasystematic / register labels.** *label*: "A special symbol or abbreviated term…
to mark a word or phrase as being associated with a particular USAGE or LANGUAGE
VARIETY." *diasystematic labelling*: "A unified way of specifying the restrictions on the
USAGE of the word or phrase being explained, through a range of interrelated USAGE
LABELS." The label is a **microstructural slot separate from the equivalent itself** —
diaphasic (formal/informal), diamedial (written/spoken), diastratic (high/demotic).
→ **Sa–Ru application:** PWG's usage/domain markers (poetic, grammatical, ritual, *im
Drama*) must survive as a labelled Russian slot, not be folded into the gloss. A
**dropped label is a defect even when the Russian equivalent is lexically correct** — its
own QA-judge defect class, scored independently of equivalent accuracy. (Dovetails with
Apresjan §1d, which supplies the actual Russian label inventory.)

**6. Macrostructure & sense ordering; polysemy vs homonymy.** *sense ordering*:
arrangement may be historical, logical or by frequency, and "in practice these different
principles are not always made explicit." *sense number* is "An ORDERING DEVICE used to
divide dictionary entries into sections." *polysemy*: "Polysemous items are assigned
distinct (and often numbered) senses within an entry, while homonyms are treated in
different entries, but sometimes the boundary… is not clearly drawn."
→ **Sa–Ru application:** the Russian dictionary inherits, does not re-derive, PWG's
macrostructure — **keep the source's homonym splitting and its sense numbering/ordering
verbatim**. The translator must not re-sequence senses or merge numbered sub-senses; the
QA-judge flags any change to sense count, numbering, or homonym entry-split as a
structural-fidelity defect. (This is the project's "Renou = badge, never re-sort" rule,
here given its general-lexicographic justification.)

---

## Gonda & Vogel — Indian Lexicography (History of Indian Literature, Vol. 5)

Claus Vogel's fascicle on *Indian Lexicography* (in Jan Gonda's *A History of Indian
Literature*, Vol. 5) describes the indigenous **kośa** tradition — short for
*abhidhānakośa*, "treasury of words" (p. 303). These are the very works PWG so often
cites in lieu of a quoted text passage, so Vogel's structural account directly governs
how much evidential weight such a citation carries.

**1. The two great classes.** Vogel's central division: "Indian dictionaries may be
synonymic or homonymic" (p. 305). The **synonymic** kośas are "systematic catalogues of
words with one and the same meaning (*ekārtha*, *samānārtha*)… commonly grouped
subjectwise"; the **homonymic** kośas "register words with more than one meaning
(*anekārtha*, *nānārtha*)." The classic synonymic work is Amarasiṃha's *Amarakośa*, whose
third section nonetheless appends a *Nānārthavarga* (III 3) of homonyms — for "many
synonymic lexica include a homonymic section." This matters because the *kind* of kośa
determines what a citation asserts: a synonymic source says "this word is one of several
names for X"; a homonymic source says "this word can, among other senses, mean X."
Misreading one as the other inverts the claim.
→ *Sa–Ru application:* tag each kośa source by class. A synonymic-kośa citation supports a
*synonym set* (low risk the headword means X in isolation); a homonymic-kośa citation
isolates *one polyseme* and should map to exactly one PWG sense, not be spread across the
synonym chain.

**2. Metrical form and filler.** Kośas were "intended, not for reference, but for
learning by heart" (p. 305), so "the dictionary-makers wrote in verse — usually Ślokas
but also Āryās — to facilitate the labour of memorizing" (p. 304). An entry and a stanza
were once "strictly coextensive, with the surplus space filled by expletive words and
phrases." Separator particles — *atha* and *tu* "serving as punctuation aids" in the
*Amarakośa* (p. 311), or *punar, tu, atha* in Yādavaprakāśa's *Vaijayantī* — are metrical
scaffolding, not semantic content.
→ *Sa–Ru application:* strip *ca, tu, atha, vā, api, hi* and similar expletives before
glossing; never let a filler particle become a Russian lexeme. Word order inside a kośa
line is metre-driven, so a QA rule should forbid inferring meaning from sequence within a
quoted ślokapāda.

**3. Gender marking and the dual/plural sense-count trap.** Kośas mark gender by
terminations or labels (*nṛ/puṃs* masc., *strī* fem., *napuṃsaka* neut., *tri* "all
three"; p. 311). But Vogel flags "a curious feature of homonymic lexica": "words of two
meanings may stand in the nominative dual and words of three or more meanings in the
nominative plural" — grammatically *ekaśeṣas* — "with the meanings themselves added
either as copulative compounds… or separately" (p. 306). Śāśvata's *Anekārthasamuccaya*
makes this explicit (p. 319). The dual/plural here counts *senses*, not real number.
→ *Sa–Ru application:* a dual or plural form in a homonymic-kośa entry must NOT be
rendered as a Russian dual/plural noun. Detect *ekaśeṣa* sense-count duals and treat them
as "this word has 2/3+ meanings" — a high-confidence *signal to sense-split*, not
morphology to translate.

**4. Topic-based order is not frequency.** A synonymic kośa is "grouped subjectwise"; the
*Amarakośa*'s three *kāṇḍas* run heaven → earth → general, by subject domain (pp.
311–312). Articles are even "ranged in an ascending or descending scale of length," i.e.
by synonym count, "nowhere does a European type of organization occur" (p. 305). Order
reflects subject and metre, never usage weight.
→ *Sa–Ru application:* corpus-gate rule — sense #1 in a kośa-derived PWG entry is NOT
"most common." Do not let kośa order set sense ranking; derive frequency only from
attested corpus tokens.

**5. Evidential weight — the lexical-only word.** Vogel's decisive observation: "the
classical lexica hardly show any traces of literary influence" (p. 304). Unlike the Vedic
*nighaṇṭus*, which "are based on one or several individual texts," the kośas "were meant
primarily to help poets in composition" — productive word-hoards, where a word or sense
can live in the lexical tradition without ever surfacing in a living text. Vogel
repeatedly notes vocables attested by one kośa that "do not occur" elsewhere (pp. 318,
326).
→ *Sa–Ru application:* a sense whose only PWG source is a kośa (no quoted *literary*
passage) gets a **lower confidence tier** — a lexicographers'/ghost-word flag. The corpus
gate down-weights kośa-only senses relative to text-quoted ones, and surfaces them with a
hedge ("attested only lexically") rather than as established usage.

**6. Long synonym chains and the dvandva problem.** A favoured terseness device was "to
combine synonyms, meanings, and even homonyms into copulative compounds (dvandvas), the
resolution of which gave rise to many a mistake in modern dictionaries" (p. 306). Authors
strove "to give as many synonyms in a row as possible," and within such strings
near-synonyms and even cognates are "often separated from one another" (p. 319).
→ *Sa–Ru application:* resolve every kośa *dvandva* into its members before glossing; do
not carry a compound across as one token. A long synonym chain is a candidate for
**sense-splitting** — members may carry distinct nuances and must be checked individually
rather than collapsed into a single Russian gloss.

---

## Klosa-Kückelhaus — Internet Lexicography (2024)

Annette Klosa-Kückelhaus's English re-working of the IDS *Internetlexikografie* owns the
**display and access layer** of the pipeline. Its central claim — argued in Chapter 4
("Data Modelling") and Chapter 5 ("Linking and Access Structures") — is that an online
dictionary is *not a page but a database*, and that "data modelling and presentation" are
two separate levels, captured in the "maps vs road signs" analogy: the data model defines
"which elements can be linked at all," while individual rendered cross-references are "the
individually placed signposts."

**1. From page to structured data model.** Chapter 4 builds an entry as a hierarchically
nested tree — `entry → form/grammar → senses → sense → definition`, plus typed
`cross-reference` blocks carrying an `id`/`refid` attribute — encoded both as XML (with a
per-dictionary *schema*) and as relational tables (`ENTRYTABLE`, `SENSETABLE`,
`REFERENCETABLE`). The decisive point: an XSL transformation lets "the same XML document …
generate … an overview presentation … as well as a complete, detailed view," and the
data can be "(re)organised according to any criteria at all for presentational purposes."
→ **Sa–Ru application:** encode each PWG→Russian entry as addressable fields — `lemma`
(SLP1 key + Devanagari + IAST display) → `sense[@n]` → `equivalent` (Russian gloss) →
`attestation` (`<ls>` siglum) — not as a flat translated paragraph. One canonical
XML/SQLite record feeds CDSL's full and compact views; the Russian gloss must be its *own*
field, never inlined into prose, so it can be queried and re-rendered independently.

**2. Access structure & the cross-reference as data.** The manual splits the link into
**link relation** (data-level connection, invisible in UI), **link marker** (the
clickable element), and **link target**. It distinguishes **structural links** = the
*internal access structure* (sense navigator, "synonyms"/"examples" jumps within an
entry) from **content links** = pointers "motivated by properties of the dictionary
object" (synonyms, translations, outward references). In print these were the
*mediostructure*; online "in the best case, we only have to click once."
→ **Sa–Ru application:** model every PWG pointer — German `s.`, `vgl.`, bare
sense-pointers — as a *typed relation* with `refid` resolving to a target entry ID,
exactly the `REFERENCETABLE(Source, Target, Position)` m:n design (note the warning:
relational rows have "no intrinsic ordering," so display order must be an explicit
`Position` column). Build **structural** in-entry sense links *and* **content** links
outward to Monier-Williams and sibling Cologne dicts (PW, PWK), each a one-click
hyperlink.

**3. Search as the real external access structure.** Chapter 5.3.1 catalogues
semasiological (form→meaning) headword search and the affordances we must implement:
**type-ahead/incremental** completion against the lemma list; a
**case-sensitive/insensitive** toggle; **fuzzy / spelling-tolerant** search showing
"lemmas … similar phonetically or graphemically"; **placeholder (wildcard)** search "for
individual letters or for a chain of letters"; and **search by inflected form**, where an
inflected input is "led back to the root form by automatic lemmatisation."
→ **Sa–Ru application:** the headword index needs transliteration tolerance across
IAST/SLP1/Devanagari (one normalized key, three input forms), wildcards for morphological
cohorts (all `-tva` abstracts, all forms of `√gam`), and inflected-form lookup via
lemmatisation against vidyut/DCS so a corpus token resolves to a lemma. The manual flags
(Ch. 7) that bad lemmatisation silently mis-routes — "errors … not always apparent to
users."

**4. The onomasiological reverse index — free, if glosses are disciplined.** The manual's
most load-bearing point for us. A **full-text search** is "conceived in its core function
as a semasiological search but when used skilfully and **verbalised consistently in the
entry texts** it can also be employed as an onomasiological search" — returning "the
entries in which the search term appears in the entry text or its meaning."
→ **Sa–Ru application:** full-text search over the Russian gloss field *automatically*
turns the bilingual dictionary into a Russian-concept → Sanskrit-word index — but only if
equivalents are verbalised consistently. This is a direct, citable justification for the
**controlled glossary**: inconsistent Russian wording (synonyms, varying word order)
degrades the reverse index, so the glossary must standardise equivalent forms expressly
to make onomasiological access work. (The single tightest coupling between the *display*
layer and the *glossary* layer — Klosa pays Apresjan's metalanguage back at query time.)

**5. Faceted filtering on structured fields.** Chapter 5.3.1 describes **filter-based**
and **faceted** search — checkboxes/drop-downs that progressively narrow results ("one
filter after the other while the search output is continuously reduced"), filtering
lemmas by "formal, semantic, etymological" properties.
→ **Sa–Ru application:** because §1 made fields addressable, expose facets directly: POS
(`<gram>`), source siglum (`<ls>`), sense-count, root. These cost nothing extra once the
data model is right — the payoff of structured encoding.

**6. QA at scale & continuous updatability.** The "Outlook" (5.4) advocates analysing
"the entire digital database … using statistical methods" and representing the link
network as a **graph**; Chapter 3 stresses an extension dictionary is "oriented towards
continuous addition and revision," published with per-entry **revision history**, never a
"frozen" edition, with referential integrity enforced by the DBMS (it "prevents a dataset
… from being deleted … if there is still a reference to the ID").
→ **Sa–Ru application:** dump all `refid` relations as a graph to detect **dangling
links** (target ID absent) and **orphan entries** (no edges) as a CI gate before each
CDSL push; treat the Sa–Ru dictionary as a continuously-updatable, versioned resource,
not a one-shot edition.

---

## How the five compose — the dictionary as one machine

The five are not a reading list; they slot into one production line, each owning a
different failure mode and several handing off to the next:

| Stage | Manual | What it guarantees | Hands off to |
|---|---|---|---|
| **Source-evidence weighting** | Gonda–Vogel | a koša-only sense is flagged weaker than a text-quoted one; *ekaśeṣa* duals read as sense-counts; topic order ≠ frequency | feeds the **corpus gate** a confidence tier per sense |
| **Sense individuation** | Riemer | two German sub-senses split into two Russian senses only on a ≥2-of-3 test verdict; autohyponymy and antonym-type preserved | sets the **sense count** Hartmann then equips |
| **Equivalence** | Hartmann & James | each distinct sense gets a *distinct* Russian equivalent (no under-differentiation); culture-bound terms get explanatory equivalents; comma/semicolon preserved | sets the **slots** Apresjan then fills |
| **Target-language discipline** | Apresjan | the Russian itself is right: canonical register label, dominant-by-default synonym, forced manner/position, no circular gloss | produces the **gloss text** Klosa indexes |
| **Delivery** | Klosa | the finished entry is addressable data — typed cross-refs, transliteration-tolerant + faceted search, onomasiological reverse index, dangling-link CI | closes the loop back to the glossary (consistent glosses ⇒ working reverse index) |

The two tightest couplings worth stating explicitly:

1. **Riemer → Hartmann → Apresjan is a single decision chain per sense.** Riemer decides
   *how many* Russian senses there are; Hartmann decides *what kind* of equivalent each
   gets (word vs paraphrase) and that they must differ; Apresjan decides *how the Russian
   is actually worded* (register, dominant, manner, non-circularity). A defect at any link
   is invisible to the others, so the QA-judge needs one checklist spanning all three.

2. **Apresjan ⇄ Klosa is a loop, not a line.** Apresjan's controlled metalanguage is
   what makes Klosa's full-text gloss search behave as a free Sanskrit↔Russian
   onomasiological index; conversely, the *promise* of that reverse index is the strongest
   practical argument for paying the cost of a controlled glossary up front. Consistency
   is not housekeeping — it is a queryable feature.

And Gonda–Vogel sits *upstream of all of them*: it is the only one of the five about the
**Sanskrit source tradition** rather than general lexicographic or computational method.
It is what stops the pipeline from laundering a 12th-century poets' word-hoard into the
same confident Russian gloss as a Ṛgvedic attestation — the one guard the Western manuals
cannot supply.

---

## Where each finding now lives in the pipeline (status as of the bulk-run preflight)

The run-relevant findings are **ported into the production Max harness**
([`src/pilot/run_pilot_wf.js`](src/pilot/run_pilot_wf.js), 2026-06-26) — that file inlines
its own translator + judge prompt, so this is where a finding has to be to affect the run
(the `pwg_ru_prompts/*.txt` files and `glossaries/de_ru_translation_aids.md` are the
human-facing source-of-record; they do **not** drive the Max harness). Status:

| Finding | Insertion point | Status in the live harness |
|---|---|---|
| Apresjan — near-synonym discrimination (differentia per sense) | translator | ✅ live (`TR`, "DISCRIMINATE … à la Apresjan") |
| Apresjan — manner/position forcing | translator | ✅ ported (rendering guidance) |
| Apresjan — register faithfulness (scholarly-philological) | translator + judge | ✅ live (`CONV` + judge check 2); §1d colloquial tagset is N/A for a uniform scholarly register |
| Apresjan — circular/cryptographic-gloss ban | judge | ⚠️ **not yet an explicit judge check** — candidate add |
| Hartmann — equivalent type (1–2 word vs толкование) | translator | ✅ live (`equivalence_type`) |
| Hartmann — comma/semicolon sense-grouping | translator | ✅ ported (rendering guidance) |
| Hartmann — polyequivalence / coverage (every sense a distinct RU) | translator + judge | ✅ live (HARD RULE 2 + judge check 6) |
| Gonda–Vogel — kośa two-source / `source_type=lexicographic` | translator | ✅ live (`CONV` two-source principle) |
| Gonda–Vogel — *ekaśeṣa* dual = sense-count; kośa order ≠ frequency | corpus gate / input gen | ✅ handled upstream (portrait/strata), not a prompt rule |
| Baalbaki/Apresjan — synonym-string cardinality | translator | ✅ ported (rendering guidance) |
| Apte/Inglese-Geupel — samāsa right-headedness, `-ādi` = hypernym | translator | ✅ ported (rendering guidance + judge check 7) |
| Tubb — śāstric formula equivalents | translator | ✅ ported (rendering guidance) |
| Mitrenina/Ruppel — *yad…tad* correlative map | translator | ✅ ported (rendering guidance) |
| Riemer — ≥2-of-3 sense-distinctness battery; autohyponymy; antonym-type | (judge) | ⏸️ **deliberately out of scope for the bulk run** — PWG's printed sense division is authoritative ("Renou = badge, never re-sort/merge/split", HARD RULE 1). The battery informs the `article-comparison` study + human review, not bulk re-individuation. |
| Klosa — display/data-model, search, cross-ref graph | web frontend | ⏸️ post-translation (CDSL frontend); not a translation-run concern |

**Net:** every finding that can change a *rendering* is live in the harness as of the
preflight; two are open candidates (Apresjan circularity judge check), and two
(Riemer's battery, Klosa's display layer) are intentionally not part of the bulk
translation step. This document is the theoretical justification behind each row; the
source tables are [`glossaries/de_ru_translation_aids.md`](glossaries/de_ru_translation_aids.md)
and [`LITERATURE_FOR_PWG_RU.md`](LITERATURE_FOR_PWG_RU.md).

---

*Compiled 2026-06-26 from full-text deep-reads of the five extractions under
[`../literature/md/Lexicography-Manuals/`](../literature/md/INDEX.md), one parallel reader
per manual. Companion to [`MANUALS_FOR_PWG_RU.md`](MANUALS_FOR_PWG_RU.md) (37-manual
audit) and [`LITERATURE_FOR_PWG_RU.md`](LITERATURE_FOR_PWG_RU.md) (by-insertion-point
harvest).*
</content>
