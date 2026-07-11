# Making dictionaries: a guide to lexicography and the Multi-Dictionary Formatter (MDF) — David F. Coward & Charles E. Grimes, SIL International, 2000

_Created: 11-07-2026 · Last updated: 11-07-2026_

**Source:** `SanskritLexicography/papers/MDF_2000.pdf` — 243 pp., SIL International,
Waxhaw NC, ISBN 1-55671-011-9, software version 1.0 (minor-corrections reprint of the
1995 edition; canonical archive entry: SIL Global Language & Culture Archives, *Making
dictionaries: a guide to lexicography and the Multi-Dictionary Formatter*, David F. Coward
and Charles E. Grimes, [sil.org/resources/archives/5741](https://www.sil.org/resources/archives/5741)).

**Rights verdict (checked 11-07-2026):** the PDF's own copyright page (p. ii) states
"©1995, 2000 by SIL International. ALL RIGHTS RESERVED," and explicitly grants only the
right to share copies of the accompanying MDF software diskette "for the purposes of
non-commercial research," not the text of the book. The SIL archive page itself could not
be fetched for a redistribution-terms cross-check (blocked with HTTP 403 from this
session), but nothing in the book's own front matter licenses redistribution of the text,
so the conservative reading governs. **This digest is therefore notes/summary and short
illustrative paraphrase, not full-text reproduction** — unlike the two other works in this
folder that are OCR/EPUB conversions of open-access or otherwise permissively licensed
originals. The source PDF is `.gitignore`d and kept only as a local working copy.

**Cross-reference:** a fuller correlation of this book against the CDSL standards/export
pipeline (field-by-field mapping to `\lf`, `\sd`, RANGE SETS, etc., plus the MG-ruled
program of follow-on work H721–H727) lives in
[`SIL_MDF_ECOSYSTEM_CORRELATION.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/SIL_MDF_ECOSYSTEM_CORRELATION.md).
This digest covers the book on its own terms — a general-purpose lexicography manual —
per [`SIL_MDF_ECOSYSTEM_CORRELATION.md` §5](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/SIL_MDF_ECOSYSTEM_CORRELATION.md).

---

## What the book is

Two books bound as one. Chapters 1–3 (not digested here — MDF-software-specific:
installing MDF, running it, menu options, WORD stylesheets) are tied to a discontinued
1990s DOS/WordPerfect/SHOEBOX toolchain and have no standalone interest. **Chapters
4–10 are a software-independent practical guide to lexicography** — decisions any
dictionary-maker must resolve regardless of tooling — grown out of decades of SIL
fieldwork on previously undescribed languages (chiefly Buru, an Austronesian language of
Maluku, Indonesia, which supplies the majority of worked examples, plus data from
Tetun, Selaru, Javanese, and others). Appendices A–E are reference material: the full MDF
field-marker inventory, field ordering, and starter lists for semantic domains, lexical
functions, and abbreviations.

---

## Ch. 4 — Basic strategies and perspectives

**Terminology (§4.1).** The book insists on distinguishing *lexicon* (the vocabulary of a
language, or its physical database), *dictionary* (a curated, audience-targeted extract from
the lexical database), *glossary* (headword + bare gloss, no examples or senses — "a
necessary minimum for archiving dying languages, but should not be the goal... of any
significant fieldwork"), *finderlist* (an index for locating a form, not a dictionary), and
*thesaurus* (organized by semantic domain rather than alphabet — not recommended as a
first publication, since a community's own domain categories rarely match a compiler's).

**Audience and purpose (§4.2).** A dictionary's design follows from who it targets:
scholar/compiler (default, least usable by others), academic, national government (a
weak motive, "rarely a service to anybody"), local government (glossary-level need only),
local audience (prestige, cultural archiving), general (too vague to drive decisions), or
mixed. **The book's recommendation:** aim the primary dictionary at the local-community
audience, then embellish entries with scholarly extras (scientific names, etymologies,
morphological parses) rather than compiling two separate dictionaries — few compilers
have the resources for both.

**Mono-/bi-/trilingual dictionaries (§4.3).** A bilingual dictionary is fundamentally a
*translation aid*: where two languages' semantic categories are not isomorphic (the normal
case for typologically distant languages), the compiler is forced into monolingual-style
analytic definitions rather than simple gloss substitution — quoting Andrew Pawley's
1993 lecture notes at length on this point. Trilingual (vernacular–English–national
language) formats are visually cluttered and generally discouraged for final publication,
though useful as an internal consistency-checking format.

**Text-based lexicography (§4.4).** Ranks word-finding strategies by reliability: pure
introspection and elicited wordlists rank low (native-speaker elicitation without native
control of the metalanguage is "full of inherent pitfalls"); a large corpus of natural texts,
mined systematically, is the most reliable primary source, supplemented by semantic-set
comparison (eliciting and contrasting near-synonyms with skilled native speakers — e.g.
comparing several words for "roof rafter" to isolate what distinguishes one from the
others). Caution: morpheme-level interlinearizing of texts tends to make compilers overlook
compounds and phrasal lexemes (`book-keep-ing`, `short-stop`) — a second, word-level pass
is recommended.

**Minimal vs. expanded entries (§4.5).** A minimal entry needs only headword + gloss;
fields can always be added later. The book recommends a generous field template from the
start (SHOEBOX's `DATABASE TEMPLATE` mechanism) — an empty field costs nothing at
print time but its *presence* prompts the compiler to fill it in, where its absence invites
skipping known information out of laziness.

**Root-oriented vs. lexeme-oriented databases (§4.6).** The book's most structurally
consequential decision. A *root-based* database subordinates derived/compound forms as
subentries under their root — convenient for morpheme-level interlinearizing, favored by
linguists, but frustrating for ordinary users who look up the surface form they actually
hear, not its underlying root (most heavily root-organized Austronesian dictionaries are
criticized on exactly this point, citing Zorc 1992). A *lexeme-based* database gives every
surface form, root or derived, its own alphabetized entry, cross-referenced via `\lf`/`\cf`
fields — easier for end users, but requires rigorous, error-prone cross-referencing
discipline to avoid orphaned entries. **Recommended compromise (§4.6.3):** enter both
roots/affixes *and* every lexeme as individual headwords, connected by consistent
cross-reference bundles — incorporating the advantages of each approach. Worked
5-entry Tetun example (`ai` "tree/wood," `ai balun` "casket," `ai kabelak` "board," `balu`
"part/side," `bela` "flat") shows the pattern in practice, alongside two alternative
strategies for citation-only bound roots (`\ps Rt` entries with `\mn` cross-reference, vs.
a single entry keyed by `\lc` citation form).

## Ch. 5 — Structuring the database

Argues for a structured database (SHOEBOX-style field records piped through a
formatter like MDF) over word-processor-native entry: sorting, reversal-index generation,
global format changes, semantic-domain extraction, and housekeeping-field suppression at
print time are all automated only if the underlying data is field-structured, not prose.

**Multiple-language information (§5.2)** is organized by a `v/e/n/r` prefix system
(vernacular/English/national-language/regional-language) applied consistently across
gloss, reversal, definition, example, usage, lexical-function, restriction, encyclopedic-info,
and variant field bundles — and the book recommends printing different target-language
sets in *separate* sections or separate publications rather than cluttering one entry with
three languages at once.

**Three categories of entry information (§5.3):** (1) information *about* the headword
itself (gloss, definition, part of speech, example, morphology); (2) information relating
the headword to *other* entries — its lexical network (homonym number, lexical
functions, synonym/antonym, cross-reference, semantic domain, variant forms); (3)
housekeeping (source, status, date last worked, bibliographic/text reference) — much of
which is never meant for publication, only for data management.

**Sort sequences (§5.4)** cover four separate problems: correct secondary ordering of
homonyms (`\hm 1`, `\hm 2`...), restoring a language-specific primary alphabet order that
differs from ASCII (digraphs like `ng`, `ch`; letters like `ñ`), choosing whether to sort by
headword or by citation form for languages needing one (`\lc`), and consistently placing
bound-root hyphens at the end of a sort run rather than scattering them.

## Ch. 6 — Structuring information in lexical entries

**What counts as a headword (§6.1).** Beyond simple monomorphemic words and
phonologically-fused compounds, the chapter adopts (with attribution) Andrew Pawley's
(1986) 23-point battery of tests for whether a multi-word string has achieved
*lexicalized*, socially-institutionalized status and therefore deserves its own entry — the
naming test, terminological-system membership, customary/legal status, speech-act
formulas, acronym formation, base-for-derivation, unacceptability of internal pause,
inseparability of constituents, conventionally reduced or truncated pronunciation,
metonymic headword omission, stress/intonation patterns, invariable grammatical frames,
definite-article-on-first-mention, orthographic conventions (capitals, quotes), semantic
opacity, arbitrary sense-selection, and ritual-parallelism membership. The point: many
"words" a grammarian would treat as regular phrasal combinations are, empirically,
conventionalized cultural units that belong in the dictionary as headwords in their own
right.

**Bound affixes and prefixing languages (§6.1.1–6.1.2)** get their own entries, tagged by
prefix/suffix/infix part-of-speech categories; for prefixing languages where the bare root
is not a possible utterance, a citation form (`\lc`) stands in as the alphabetized headword,
with the compiler choosing whether the printed dictionary sorts under the citation form or
the bare root.

**Choosing example sentences (§6.2)** draws on Bartholomew & Schoenhals (1983):
good examples delineate sense discrimination, exemplify correct/unusual grammar,
justify glosses, disambiguate multiple senses, and illustrate cultural norms — via twelve
"associational categories" (characteristic attribute, behavior, use, position, material,
subject/object/instrument, contrast, cause-effect, abstraction, part-whole, synonym/class,
comparison). Caution against sentences authored by non-native speakers, translated
material, or text extracted without checking that it still reads naturally out of its original
discourse context.

**Homonymy vs. polysemy (§6.3)** is decided empirically from a natural-text corpus, not
introspection, using a battery of tests: is there a native-speaker-acknowledged shared
meaning thread; does a part-of-speech split correlate with a syntax-driven rather than
lexicon-inherent category system (if so, treat as one polysemous lexeme, not two
homonyms); do the putative senses share a lexical-function network or diverge; do they
share collocational/grammatical frames; is cross-sense ambiguity attested (more likely
within polysemy than across true homonyms); is the relation metonymic
part-whole/generic-specific (again more typical of polysemy). Historically related forms
can nonetheless be *synchronically* distinct words to native speakers (Spanish `caballero`
"horseman" → "gentleman" → in places simply "men's [toilet]"); borrowed vocabulary is
flagged as the single most common source of true homonymy. The chapter closes with
Pawley's coined term **"false polysemy"** — the systematic over-splitting bilingual
dictionaries commit when they mistake *target-language translation-equivalent
boundaries* for *source-language sense boundaries* (worked example: a hypothetical
form `tal` covering "shank/thigh/chair-leg," which is one unified sense in the source
language despite needing three different target-language words).

**Semantic domains (§6.4)** (`\sd`, plus `\th` thesaurus and `\is` index-of-semantics
fields) support both extraction of topical subsets via SHOEBOX filters and, for some
word classes, act as a proxy for shared morphosyntactic behavior — e.g. tagging Buru
verbs as `Vcut` or `Vcarry` predicts shared argument-structure templates across the whole
class. A starter list is given in Appendix C.

**Dialect information (§6.5)** should always identify one dialect as primary (stated
explicitly in the dictionary's introduction, with a dialect map) and mark all others
explicitly via `\ue` (usage) or the `\lf SynD=` (dialectal synonym) / `\va` (variant-form)
field bundles — never silently pooling variants into one undifferentiated entry, which the
book calls a strategy that "belongs to nobody and represents nobody." Four distinct kinds
of dialect variation are distinguished: related (structural-variant) forms, unrelated
(different-lexeme) forms, same-form-different-meaning forms, and same-form-different-
distribution forms.

## Ch. 7 — Lexical functions (`\lf`)

The chapter most directly reusable outside SIL's toolchain. **Lexical functions**
(credited to Apresyan and Mel'čuk) formalize regular *meaning*-based associations
between a headword and other lexemes — independent of morphological derivation (e.g.
`drive : driver :: fly : pilot :: write : writer` are all Actor-of-verb relations despite no
shared derivational morphology). The chapter reports that eliciting lexical-function
networks with language consultants is unusually engaging fieldwork — both Grimes
co-authors independently report consultants spontaneously returning days or weeks
later with more entries in a network, a level of voluntary engagement they say they never
saw doing syntax elicitation.

A defined, MDF-implemented set of ~40 function labels (full list also in Appendix D)
covers: **Syn/SynD/SynL/SynR/SynT** (synonym, and its dialectal/loan/register/taboo
subtypes), **Gen/Spec/Sim** (generic/specific/near-synonym — the folk-taxonomy
backbone used again in ch. 8), **Nact/Nug/Nloc/Ninst/Nben/Ngoal/Ndev** (actor,
undergoer, locative, instrument, benefactee, goal, and deverbal nominalizations
associated with a verb), **Whole/Part/Mat** (part-whole and material relations),
**Vwhole** (verb-of-the-whole, the converse of Whole), **Serial/Compound/Sit/Prep**
(conventionalized combinations, situational associations, preparatory activities),
**Phase/Start/Stop** (life-cycle or process phases), **Max/Min/Degrad** (superlative,
diminished, degraded degree), **Ant/Cpart** (antonym, complementary counterpart),
**Head/Group/Unit** (leader-of, collective-of, singular-instance-of), **Res** (result state),
**ParS/ParD** (same-sense / opposite-sense ritual-poetry parallelism), **Feel/Sound**
(sensation, characteristic sound). Each is illustrated with a worked one- or two-field
Buru/Indonesian entry. The recommendation is to build these networks *before* choosing
example sentences, since a well-explored lexical network gives the compiler and
consultant a much richer sense of what an example sentence needs to illustrate.

## Ch. 8 — Special classes of entries

**Folk taxonomies (§8.1)** get an extended treatment: most languages encode at least a
generic/specific two-level system, and many encode three-plus levels (life forms —
broadest — down through intermediate taxa to terminal taxa, often glossed loosely as
"species"). Seven cautions are given for cross-linguistic taxonomy work: folk and
scientific taxonomies are rarely isomorphic (Selaru `masy` "fish" folk-covers dolphins,
whales, and some shellfish); intermediate taxa/life forms may be expressed as verbal
propositions rather than nominal categories; folk systems weight behavioral/use criteria
the scientific system doesn't; culturally salient flora/fauna (staple crops, ritually or
economically central animals) are systematically over-differentiated lexically; and
questions must be pitched at the *next* taxonomic level up (toe → foot → leg → body, not
toe → body directly), mirroring general part-whole reference patterns.

Detailed field checklists follow for **plants** (physical description, habitat/growth,
uses, social/ritual value, named varieties), **animals** (§8.1.2), **birds** (§8.1.3, feather
markings, calls, migratory/nesting behavior), **fish** (§8.1.4, habitat strata, fin structure,
spawning), **insects** (§8.1.5, life-cycle stages and whether the culture links larval and
adult forms terminologically), **body-part terms** (§8.1.6 — Buru's `kada-n` glossed
"leg" actually spans English leg+foot; caution that translation-equivalent glosses
systematically mislead here), **kin terms** (§8.1.7, extensive discussion of
reference-vs-address forms, reciprocal terms, and the point — quoting Pawley again —
that kinship glosses are dangerously misleading unless the cultural role obligations
bundled into the term are spelled out, not just the biological relation), **cultural
artifacts** (§8.1.8), and general **natural-environment terms** (§8.1.9).

**Syntactic classes (§8.2)** distinguishes activities/events (Actor-initiated, with typical
undergoer/instrument/location/preparatory-activity/result slots, all expressible via `\lf`
fields) from states/processes (single-argument Undergoer/experiencer predicates, which
may or may not have a lexical, morphological, or periphrastic causative counterpart —
`big`→`grow`, `wide`→`widen`, `thirsty`→`make thirsty`).

**Loans and etymology (§8.3)** distinguishes the `\bw` (borrowed-word) field from `\et`
(historical etymology, reserved for citing *attested published* reconstructions only —
private guesses go in `\nt`/`\ec` instead), and stresses that identifying loan vs. inherited
vocabulary matters even for languages sharing a common ancestor with their contact
languages (worked Buru/Malay pairs: inherited `fofo` "fish trap" < *bubu vs. borrowed
`bubun` "fish trap" < Malay `bubu`).

**Ritual speech and registers (§8.4)** surveys Javanese's three-level Ngoko/Madyo/Kromo
speech-register system and Buru's taboo forest-register ("Li Garan"), then gives a
compact treatment of formulaic ritual parallelism (paired lines that repeat or invert
meaning — illustrated with a Rotinese poem, a Buru hunting formula, and Psalm 139:7–10)
as a further, `\lf ParS=`/`\lf ParD=`-taggable, lexical-network phenomenon.

## Ch. 9 — Parts of speech (`\ps`)

Opens by naming the actual problem: dictionary-makers routinely (a) assign
part-of-speech tags from the *gloss language*'s grammar rather than the source
language's own morphosyntax; (b) never revisit early, provisional tags as understanding
of the grammar deepens; (c) wrongly assume every lexeme has one *inherent* part of
speech rather than potentially being defined by its syntactic slot; (d) force a "primary
class, secondary derivation" analysis onto genuinely flexible-category lexemes (the "flaw
of the excluded middle"); (e) assume universal categories like "adjective" must exist in
every language; (f) collapse verb subclassing to a bare transitive/intransitive binary even
where a language needs more; (g) borrow case-grammar terminology (ergative,
nominative) inappropriately for languages with fundamentally different alignment
systems.

Two recurring cross-category cases get worked through in detail: **adposition-or-
conjunction functors** that link constituents of varying syntactic scope (word, phrase,
clause, sentence, paragraph) — for which the book proposes the cover term *relater*
rather than forcing a single traditional label — and **noun-or-verb ambivalence**
(English `sail`/`photocopy`/`shower`, Malay `jalan`, Paiwan actor/undergoer/locative/
instrumental nominalizations of `kan` "eat"), where the recommendation is to record both
functions on one entry rather than splitting into homonyms absent independent surface
evidence for "zero derivation."

**Verbal subclasses (§9.3.2)** covers split-S (split-intransitive) systems, where a
language's single class of intransitive-subject arguments splits into two distinct
morphosyntactic treatments depending on whether the subject is semantically an Actor or
an Undergoer (Dixon 1979/1994's terminology; illustrated from Buru, Selaru, Dobel, and
Acehnese) — requiring a minimum three-way `vt`/`vi`/`vn` (active-transitive /
active-intransitive / non-active) split rather than the usual binary; *intradirective/
quasi-reflexive* verbs (motion/posture verbs like "go," "sit" that some languages mark as
morphologically transitive despite one semantic referent); and morphologically defined
sub-paradigms recorded via the `\pd` field (Buru's `em-`/`eb-`/`-t` non-active verb
classes; `-k`/`-h` transitive-object-marking classes).

**Adjectives (§9.3.3)**: many Austronesian languages, including Buru, have no
underived adjective class at all — attributive modifiers are uniformly derived from verb
roots, and where predicative/attributive forms differ morphologically, the attributive
(nominalized) form is always the *derived* one, never the reverse; labeling such forms
"adjective" misdescribes the grammar.

**Abbreviation strategy (§9.6)** contrasts informal (nearest-English-word) vs. formal
(fixed technical-term, all-caps, no-period) interlinear glossing conventions, following
Simons & Versaw (1987) and citing Lehmann (1982)'s ~170-term standard list as the
fullest available at the time; recommends short unambiguous pronoun-gloss codes
(`1s`/`2s`/`3s` + case suffix), all-caps functor glosses with no terminating period, periods
only for portmanteau-morpheme glosses, and a fixed convention for vague-referent glosses
(`s.t.`, `s.o.`, `k.o.`). **RANGE SETS (§9.7)** — SHOEBOX's mechanism for defining a
closed master list of legal values per field (parts of speech, semantic domains,
paradigm codes) and flagging anything that doesn't match — is presented as a basic
data-consistency safeguard.

## Ch. 10 — Completing the dictionary

**Recommends against** rushing out an unedited "preliminary/pocket dictionary" dump
to satisfy sponsor/government demands for visible progress; **recommends instead**
publishing a *series* of complete topical-subset volumes (kin terms, plants, birds...)
extracted via semantic-domain filters, which builds community engagement and
demonstrates real progress without compromising eventual full-dictionary quality.

**Writing the introduction (§10.2)** — drafted early (after the first ~1,000 entries) and
refined throughout — should independently orient a reader with no other access to a
grammar or ethnography of the language: audience/purpose and total entry counts;
sociolinguistic/demographic/geographic context; contact history relevant to interpreting
`\et`/`\bw` fields; language name and classification (with explicit caution against vague
relatedness claims — "some linguists will describe two unintelligible languages as
'close' that are less than 30% true cognate"); dialect and register map; phonology and
orthography guide (with a comparative table if competing orthographies exist); **a part-
of-speech-by-part-of-speech grammar sketch** (called out as the section most likely to
make or break a dictionary's usability); a brief ethnographic sketch; a labels/abbreviations
key; a "how to read an entry" walkthrough; and a guide to using the reversed finderlist.

**Acknowledgments (§10.3)**: be generous, name every contributing consultant,
institution, and funder, and ensure complimentary copies reach the local community and
relevant government bodies once published — framed explicitly as maintaining future
research access, not mere courtesy.

## Appendices A–E — reference material (structure only, not reproduced)

- **Appendix A** — an alphabetized inventory of essentially the full MDF field-marker set
  (nearly 100 codes: `\lx` headword, `\ps` part of speech, `\ge`/`\gn`/`\gr` glosses,
  `\de`/`\dn`/`\dr` definitions, `\xv`/`\xe`/`\xn` examples, `\lf`/`\le` lexical functions,
  `\cf`/`\ce` cross-references, `\et`/`\eg`/`\es`/`\ec` etymology bundle, `\sd`/`\th`/`\is`
  semantic-classification fields, `\va`/`\ve` variants, `\nt`/`\na`/`\nd`/`\ng`/`\np`/`\nq`/`\ns`
  note-type bundle, pronoun-inflection codes `\1s`…`\4p`, and more), each paired with its
  MDF-generated English and Indonesian print labels.
- **Appendix B** — the fixed relative print-order of those fields within an entry.
- **Appendix C** — a starter list of ~45 semantic-domain codes (`Nkin`, `Nplant`, `Vcut`,
  `Vcarry`, `ADJsize`, etc.), summarized above under §6.4.
- **Appendix D** — the alphabetized ~40-item lexical-function list, fully enumerated
  above under ch. 7 (this appendix is the authoritative short-form reference; the chapter
  text is the worked-example version of the same inventory).
- **Appendix E** — a starter list of standard glossing abbreviations, complementing §9.6.

Appendices F–I (MDF v0.9/0.95 version-history changelog, files/programs used by the
MDF program, WORD macro listings, and a problem-reporting address) are entirely
software-specific to the discontinued MDF/SHOEBOX toolchain and are not digested here.

---

## Why this book, for this project

Coward & Grimes distill roughly a decade of SIL fieldwork-lexicography practice into a
single, unusually concrete methodology text — most points come with a worked example
from a genuinely undescribed language rather than staying at the level of abstract
principle. For a project building a Sanskrit dictionary-standards layer, its main value is as
an **independent, non-Indological methodological baseline**: a field-linguistics
lexicographer working from oral fieldwork on a previously undocumented language faces
structurally similar decisions (root- vs. lexeme-orientation, homonymy/polysemy
adjudication, semantic-domain tagging, relation typing) to a philologist standardizing a
century-old print dictionary corpus, despite the completely different source material. See
[`SIL_MDF_ECOSYSTEM_CORRELATION.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/SIL_MDF_ECOSYSTEM_CORRELATION.md)
for the field-by-field crosswalk against MW/PWG/PW/csl-atlas and the resulting
H721–H727 work program.

_Dr. Mārcis Gasūns_
