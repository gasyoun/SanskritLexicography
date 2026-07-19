# What doesn't work in computational Sanskrit lexicography: negative results from a multi-repository research programme (A67)

_Created: 18-07-2026 · Last updated: 19-07-2026_

**Status:** draft 1, readiness 2/5 · registered as **A67** in
[Uprava/ARTICLES.md](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md) ·
handoff [H1268](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1268-Fable_SanskritLexicography_negative-results-dead-ends-methods-paper_18.07.26.md).
**Venue shortlist:** (1) *Insights from Negative Results in NLP* (ACL workshop — the field's
dedicated negative-results venue; short-paper format would take §§3–4 with the taxonomy);
(2) *Language Resources and Evaluation* (full-length; the resource-failure classes are squarely
in scope); (3) *Digital Scholarship in the Humanities* (the programme-level methods argument).
**Audit trail:** every adjudication behind this draft is in
[A67_negative_results_adjudication_table.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A67_negative_results_adjudication_table.md);
every claim below carries a link to the registry section or dataset that records its evidence.

## Abstract

Negative results are systematically under-published in digital humanities and computational
lexicography: methods that cannot work are re-attempted because nobody wrote down why they
failed. We report the recorded failures of a multi-repository research programme built around
the Cologne Digital Sanskrit Dictionaries (44 dictionaries), the Digital Corpus of Sanskrit
(DCS), and their derived crosswalks — a programme that maintains dedicated *epistemic
registries* (dead-end, contradiction, and refuted-hypothesis files) precisely so that failures
survive their sessions. From 46 recorded failure candidates we adjudicate each as **intrinsic**
(the approach cannot work on the stated inputs, with quantitative evidence), **incidental**
(an implementation or process accident), or **underpowered** (abandoned before evidence), and
find that fewer than half — 22 of 46 — survive as scientific negative results. The intrinsic results
organize into four recurring failure classes: **missing-signal** failures (the source never
carried the information: pitch accent, prefixed-verb forms, hidden headwords, compound-type
labels), **lossy-key** failures (a join or normalization key that silently merges or drops
data), **wrong-witness** failures (the evidence was sought in a different edition than the
claim is about), and **statistical-artifact** failures (confounds and invalid generalizations:
entry size, annotation density, school traits, single-exemplar scale-up). We also report one
recorded dead end whose blocking premise was refuted within a day of being generalized — the
case for writing every negative result with an explicit, falsifiable reopening condition.
The exclusion table — the 24 recorded failures that do *not* qualify — is published alongside,
because the commonest error in negative-results reporting is promoting an incidental failure
to a scientific one.

## 1. Introduction

A research programme that runs long enough accumulates a second, shadow literature: the
approaches that were tried and abandoned. In most projects this literature exists only as
reverted commits and stale branches, and its findings are re-purchased at full price by every
newcomer. Computational Sanskrit lexicography is unusually exposed to this waste because its
obvious-looking moves — join two dictionaries on a normalized headword, derive verb morphology
from the corpus, resolve a 19th-century citation against a modern critical edition — fail for
reasons that are structural rather than accidental, and the failure is typically *silent*: the
join returns rows, the classifier returns labels, the resolver returns loci. Nothing crashes;
the numbers are simply wrong.

The programme reported here — ~85 repositories around the Cologne Digital Sanskrit
Dictionaries ([CDSL](https://www.sanskrit-lexicon.uni-koeln.de/)), Hellwig's Digital Corpus of
Sanskrit, the [csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas) evidence-graded
review layer, and the [WhitneyRoots](https://github.com/gasyoun/WhitneyRoots) /
[SanskritGrammar](https://github.com/gasyoun/SanskritGrammar) grammar crosswalks — has since
mid-2026 maintained *epistemic registries* alongside its confirmed-findings files: a
[DEAD_ENDS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md)
graveyard for abandoned approaches (each row carrying `Failed because`, `Evidence`, and a
falsifiable `Don't retry unless` condition), a
[CONTRADICTIONS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/CONTRADICTIONS.md)
holding pen for unresolved source disagreements, and a refuted-hypothesis log. These
registries are the data of this paper. To our knowledge no comparable *published* negative-results
record exists for computational lexicography of any classical language; the nearest
neighbours are the NLP community's *Insights from Negative Results* workshop series and the
reproducibility literature, neither of which covers the dictionary-structure and
witness-selection failure classes that dominate here.

Two disclaimers govern everything below. First, **recall is unknown**: a failure appears in a
registry only if a session noticed it and wrote it down; we report the recorded record and do
not extrapolate to the true failure population. Second, **a programme reviewing its own
failures has a self-serving-framing risk**: the mitigations are that every quantitative claim
links to the committed dataset or registry section that records it, that no experiment was
re-run or re-scored for this paper, and that the full adjudication — including the 24
candidates we *excluded* and why — is published in the companion
[adjudication table](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A67_negative_results_adjudication_table.md).

## 2. Method: from recorded failure to publishable negative result

### 2.1 Harvest

We swept six sources in full on 18-07-2026: the Sanskrit-data dead-end registry
([SanskritLexicography/DEAD_ENDS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md)),
its infra twin ([Uprava/DEAD_ENDS.md](https://github.com/gasyoun/Uprava/blob/main/DEAD_ENDS.md)),
both CONTRADICTIONS registries, the 98-section measured-findings file
([FINDINGS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md);
numbered to §94 with a handful of duplicate keys), and
the retired-task rows of the programme's work registry. Yield: **46 candidate failures**.

### 2.2 Adjudication

Each candidate received exactly one ruling:

- **INTRINSIC** — the approach cannot work on the stated inputs; the mechanism of failure is
  understood; quantitative evidence is recorded. These are the paper's negative results.
- **INCIDENTAL** — an implementation, tooling, provenance, or process accident. The approach
  was never refuted; often it worked once the defect was fixed.
- **UNDERPOWERED** — abandoned or blocked before decisive evidence (n too small, never run,
  host outage, second annotator pending).
- **REVERSED** — a recorded dead end whose blocking premise was later refuted.
- **OUT-OF-SCOPE** — not a computational-lexicography method claim (dead external hosts,
  programme-management contradictions, adjudications of external critiques).

The verdict distribution — **21 intrinsic, 1 reversed, 12 incidental, 5 underpowered, 7
out-of-scope** — is itself the paper's first result: *fewer than half of the failures a
disciplined programme records are scientific negative results.* The distinction is
load-bearing in both directions. Publishing an incidental failure as intrinsic poisons the
field's memory (the approach worked; your regex didn't — §4 catalogues twelve rows of exactly
this shape). Publishing an underpowered abandonment as intrinsic converts "we didn't finish"
into "it can't be done."

### 2.3 Evidence tiers

Claims below inherit the evidence tier of their registry row. Most link to committed datasets
or validation reports. One deliberate exception is flagged inline: the body-text mining
precision figures (§3.1) survive only in a review-session record, because the measuring
extractor was deleted together with the rejected experiment — the registry entry exists
precisely so the number would not be lost, and we cite it as recorded, not re-derived.

## 3. Results: four classes of intrinsic failure

### 3.1 Missing-signal failures — the data never carried what the method needed

**No amount of cleverness recovers a signal the source does not encode.** Five methods failed
on exactly this.

**(a) Deriving present class from an unaccented corpus.** Sanskrit present classes I vs VI
(and IV vs passive) are distinguished by pitch accent (`cárati` vs `tudáti`); the DCS carries
none. A corpus-derived class pass wrote **117 spurious class additions into reviewed data —
all reverted** (120 unsound vs 19 kept)
([FINDINGS §8](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#8-unaccented-dcs-cannot-distinguish-present-class-i-from-vi)).
The general form of this limit: of the 38 root-homonym groups the DCS lumps under one lemma
id, only **5 are gaṇa-splittable** — the other 33 share a present class, so *no* morphological
tool, Pāṇinian generators included, can attribute their tokens
([FINDINGS §2](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#2-homonym-token-splitting-has-a-hard-morphological-ceiling)).
Escape hatch as recorded: an accent-bearing witness (accented Ṛg-Veda via VedaWeb) or
gloss-level adjudication — and where that witness exists, the same programme's accent work
*validated* (18/19 matrix cells GO,
[FINDINGS §54](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#54-whitney-accent-axis-validates-at-1719-matrix-cells-go-against-attested-rv-accents)),
which is the control showing the failure is in the corpus signal, not the method family.

**(b) Prefixed-verb attestation via sandhi-joined lookup.** Building a proper
`upasarga+root` sandhi join to find prefixed-verb evidence in a parallel corpus is a no-op:
the join produces the same surface strings as naive concatenation, and the corpus lemmatizes
prefixed verbs to the root or lacks them — of √man's 15 prefixed forms, **3** appear
([FINDINGS §5](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#5-the-parallel-corpus-rarely-attests-prefixed-verb-forms)).
Spelling was never the limiter; the forms are absent.

**(c) Mining "hidden" headwords from dictionary bodies.** The promise of +152k lemmas from
`<k2>` keys and entry bodies dissolved on inspection: `<k2>` is `<k1>` re-encoded (a
normalization artifact, ~0 genuinely new), the large forward dictionaries already split
compounds into their own records, and an extractor over the remaining candidates scored
**38.6% precision** by adversarial classification (per-dictionary 18–76%; the "new" tokens
dominated by inflected forms, glued phrases, and transcode artifacts)
([FINDINGS §30](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#30-body-text-headword-mining-is-a-dead-end-386-percent-precision);
evidence-tier caveat: the extractor was deleted with the rejected experiment, so these figures
survive in the review record only). The 376k-key broad headword index was already
near-ceiling; findability gains require different work (inflected-form→lemma indexing,
sandhi/compound splitting), which raises *findability*, not distinct-lemma count.

**(d) A compound-type (samāsa) frequency layer.** Two independent walls, both measured: no
corpus in the programme carries a samāsa-type label at all (DCS marks 841,052 tokens merely
as compound members; the 401k-row compound archive's "category" is stem *count*), and the
fallback — citing the grammarians' canonical examples' corpus frequencies — inverts the truth:
of 58 textbook examples, **8 are attested at all**, maximum frequency 147, and `saputra`
scores 0 while its type is ubiquitous
([FINDINGS §86](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#86-samāsa-type-frequency-does-not-exist-in-any-org-corpus--and-the-grammarians-canonical-examples-are-corpus-ghosts-858-attested-max-freq-147)).
The vyākaraṇa example inventory is a pedagogical artifact, not a corpus sample; an
example-frequency layer is a type-frequency claim in disguise and is *worse than no layer*.

**(e) Aorist-vs-perfect studies from UD tense features.** Universal Dependencies `Tense` has
no aorist or perfect value — DCS renders both as `Tense=Past` (102k tokens)
([FINDINGS §10](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#10-dcs-ud-tense-marking-conflates-aorist-and-perfect)).
The distinction is recoverable, but only from a different signal (the DCS-specific
`feat_formation` field within `Past`, or the legacy 2021 export's codes;
[FINDINGS §91](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#91-dcs-has-no-aorist-tense-value--feat_tensepast-lumps-aorist-with-the-perfect-feat_formation-is-what-actually-separates-them)):
the negative result is scoped to the UD tense layer, and it bit — an earlier fixed-form-set
workaround undercounted the aorist ~5×.

**(f) Spell-candidate promotion on corpus signal alone.** Promoting a spell-check candidate
on corpus frequency plus confusion statistics, without grounding in the entry body, was
refuted when the candidate pool surfaced real minimal pairs — *patra* "leaf" vs *pātra*
"vessel" — that no frequency or confusion signal can separate: lexical identity is simply not
in the signal ([Uprava DEAD_ENDS §6](https://github.com/gasyoun/Uprava/blob/main/DEAD_ENDS.md),
refuted hypothesis T2606-09; evidence tier: exemplar-grade refutation as recorded, not a
measured rate). Body-grounding is the witness that carries the missing information.

### 3.2 Lossy-key failures — a machine key that silently merges or drops data

**(a) NFD-decompose + strip-combining-marks as a Sanskrit join key.** The classic Unicode
fold destroys phonology: vowel length (`ā`→`a`), retroflexion (`ṣ`→`s`), and `ś` composed
with the pitch-accent mark all collapse — the key *manufactures* matches, silently, and
poisoned an entire family of source-siglum folds before it was replaced by a
length-preserving `form_key`
([FINDINGS §36](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#36-iast-unicode-collides-and-normalises-lossily),
[§45](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#45-siglum-prefix-families-routinely-bundle-several-distinct-works-the-diacritic-stripping-fold-has-poisoned-keys)).

**(b) Corpus-native ids as primary keys.** DCS CoNLL-U `OccId` is reused across a line's
sub-sentences and `sent_id` collides within a chapter: keying an import on either silently
dropped ~20 tokens and then **449 sentences** before synthetic surrogates replaced them
([FINDINGS §9](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#9-dcs-occid-and-sent_id-are-not-unique-keys)).
The failure is intrinsic to the ids (non-unique by the corpus's own construction), and its
cost was the silence: both losses were discovered by validation counts, not by errors.

**(c) Blind respelling from typo lists.** Applying a spell-checker's corrections as blind
headword respells founders on a structural property of the dictionaries: **~9% of "typos"
(11/122 verified) are collisions** — the "correct" spelling already exists as its own entry,
so the respell creates a duplicate or clobbers apparatus
([FINDINGS §24](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#24-about-9-percent-of-typo-corrections-are-collisions)).
The method as specified lacks the third editorial category (merge vs respell vs leave) the
data demands; without it, no confidence threshold rescues the pipeline.

**(d) Citation-spelling joins against homonym-numbered catalogs.** Three independent
incidents, one mechanism: Whitney's root catalog numbers its homonyms (`1 iṣ`, `2 iṣ`), and
any join keyed on the bare citation spelling smears one source entry across every homonym of
that spelling — a scrape merged homonyms' present classes
([FINDINGS §3](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#3-the-warnemyr-scrape-union-smears-homonym-classes));
an ingest of an author's own root classifications asserted 15 entries as 31 records, the rows
still reading `authorial`; and a homonym guard written as *non-contradiction* still bound
un-indexed spellings to multiple roots — the correct abstention rule is *unique-resolution*
([FINDINGS §90](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#90-a-spelling-keyed-join-onto-whitneys-roots-union-smears-homonyms--one-authorial-entry-lands-on-every-homonym-of-that-spelling-and-the-rows-still-read-authorial)).
The aggregate statistics were unaffected (10.5% exception rate before and after), which is
the trap: **a provenance-only defect is invisible to aggregate checks.**

### 3.3 Wrong-witness failures — the method interrogated the wrong text

**(a) Resolving 19th-century citations against a modern critical edition.** PWG and MW cite
the Harivaṃśa by *continuous śloka number in the Calcutta vulgate* (16,374 ślokas); the DCS
carries Vaidya's critical edition (≈⅓ the size, per-chapter numbering). Of 587 shared rare
citations, **1** resolved. The deeper result concerns the obvious repair: a vulgate↔critical
*concordance* cannot answer the question it would be built for, because a concordance maps an
address *on the assumption the address is correct* — which is the proposition under test. An
erroneous citation and a correct citation into vulgate-only material emit the same observable
(`ABSENT`), and with ⅔ of the vulgate absent from the critical text the `ABSENT` branch
swamps the signal
([DEAD_ENDS §8](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md)).
The plausible, buildable, scholarly-respectable intermediate artifact is structurally
incapable of the job. Before building a mapping, ask what it assumes; if it assumes the thing
you are testing, it cannot test it.

**(b) The shared-error proof of dictionary dependence: a powered null.** When the correct
witness *was* obtained — the Kinjawadekar vulgate, 93.8% coverage, a fitted per-chapter index
validated on held-out anchors at 68.4% vs a 2.1% shuffled null — the Lachmann-style
shared-*error* test still returned **zero**: 206 of 565 shared Petersburg/MW references
corroborate as *correct* at the exact cited śloka (recorded as 37.7% against a 0.5% null;
206/565 computes to 36.5% — an arithmetic wrinkle in the registry row itself, flagged in the
[adjudication table](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A67_negative_results_adjudication_table.md)
rather than silently repaired), and displaced
candidates fall *below* their shuffled-null expectation (79 vs 200), with no clustering
([DEAD_ENDS §8, executed](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md)).
Combined with the apparatus-inheritance evidence (MW ≈8× more predicted by PWG's
inclusion decisions than an independent compiler's, yet ~0% shared mechanical errors and
independently recomposed prose,
[FINDINGS §83](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#83-mw-and-the-petersburg-dictionaries-are-not-independent-witnesses-on-inventory-or-apparatus--do-not-count-their-agreement-as-corroboration-but-no-shared-error-has-ever-been-found)),
the negative result is precise: *the dictionaries share scholarship, not mistakes* — the
airtight stemmatic proof this field would love to import from textual criticism has no
material to bite on in the corpora tested. This is a null with a positive control (the 37.7%
corroboration), not an absence of evidence.

### 3.4 Statistical-artifact failures — the number measured something else

**(a) The entry-size confound (the "parametric core").** The hypothesis that per-entry
counted parameters (senses, glosses, cited phrases) identify a dictionary's structural core
was not confirmed on PWG: every counted parameter is first a measure of article length
(stable-core headwords average **14,876 characters vs 439** for the rest, 33.9×), raw entry
size alone recovers the core *better* (35.5%) than any parameter (8.5–33.5%), and at
size-matched comparison sense counts **reverse sign** (p = 0.038) while cited phrases stop
discriminating (p = 0.62)
([FINDINGS §67](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#67-in-pwg-article-size-dwarfs-every-parametric-statistic-you-can-extract-from-the-entry)).
Uncontrolled, the parameters measure the lexicographer's attention — itself a function of
corpus frequency (ρ = +0.497).

**(b) Sense counts as lexicographic progress.** Across 11 dictionaries and 135 years the
sense-count↔year correlation is **r = 0.036** — flat — while lexicographic-family means span
1.0–2.4 senses/entry
([FINDINGS §27](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#27-sense-granularity-is-a-family-trait-not-a-diachronic-trend)).
Granularity is a school trait; any per-sense-normalized cross-dictionary metric silently
encodes school bias.

**(c) Reading high p-values as change.** Aggregated over 9.94M stop/nasal varṇas, the
varga × epoch association is **Cramér's V = 0.037** — near-stable — and on such N "everything
is significant," so p-values carry no signal. The 2014 dissertation prose had labelled as
"gaining popularity" exactly the vargas whose pairwise-χ² p-values were *large* — the
statistically unchanged ones
([FINDINGS §62](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#62-varga-distribution-is-almost-epoch-stable-cramérs-v--0037--and-the-gasūns-2014-dissertation-prose-read-its-own-χ²-table-backwards)).
We include this self-correction deliberately: the programme's own earlier prose is the
subject, and the 2026 recompute sides with the 2014 table against the 2014 text.

**(d) Single-exemplar scale-up.** A hand-picked exemplar (*dharma*'s citation-fusion
behaviour in two indigenous dictionaries) *reversed direction* at corpus scale: SKD splits
53.3/46.7 while VCP skews toward fusion at 77.6% — the opposite of the exemplar's suggestion;
the driver is record type and genre, not dictionary convention
([FINDINGS §43](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#43-skdvcp-sensecitation-fusion-is-a-record-type-effect-not-a-dictionary-level-one)).
The corpus count was reported even though it contradicted the exemplar that motivated the
classifier — the discipline this paper exists to reward.

**(e) Annotation-density artifacts.** Metrics built on DCS verbal *features* track the
corpus's annotation coverage, not Sanskrit: tagged past participles fall Ṛg-Veda 1,874 →
Mahābhārata 465 → Daśakumāracarita **0** — in a 7th-century prose text saturated with
ta-participles — and a naive feats-based draft produced an *inverted* diachronic gradient
before the artifact was caught
([FINDINGS §86](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#86-dcs-verbal-feature-annotation-density-collapses-for-later-texts--feats-based-diachronic-metrics-measure-annotation-not-language)).
Kin results: raw `<ls>`-citation density misranks dictionaries whose citations live in a
different markup register entirely (28/44 dictionaries have no `<ls>` at all;
[FINDINGS §26](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#26-citation-density-is-register-bound-not-comparable-raw)),
and DCS homograph collapse gives high-frequency closed-class words the union of all their
homographs' eras — maximal, unusable period spans
([FINDINGS §14](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#14-renou-period-state-tagging-covers-770k-entries-in-8-dicts)).

**(f) Coverage claims from circular joins.** A morphological-attestation audit joining a
generation database against DCS attested forms looked like 94% coverage — but 93.30% of the
generated side was itself DCS-derived, making the join a 99.99% round-trip; the
attested-but-ungenerated set is degenerate (n = 2) and *cannot* measure engine gaps; the only
signal-bearing subtotal is the independent engine's 12.43%
([FINDINGS §94](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#94-koshas-generated-forms-is-93-dcs-derived-so-its-attested-form-join-is-a-round-trip--only-the-vidyut-engine-subtotal-124-attested-carries-signal-and-ag-cannot-measure-engine-gaps)).
Any A∩G coverage headline must split by generated-side provenance first.

**(g) A clean small null.** Injecting a derived per-word grammar token into dictionary
translation prompts did not help: in a blind A/B over 8 stratified headwords the judge
preferred grammar-OFF 5, tie 2, ON 1 — the token survives as structured data, not prompt
material ([FINDINGS §4](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md#4-pwg-nominal-grammar-compresses-into-335-paradigm-tokens)).
Small, honestly powered, and cheaper than the intuition it replaced.

## 4. What did not qualify — and why that matters

Twelve recorded failures were adjudicated **incidental** and are excluded from the negative
results above, with full reasons in the
[adjudication table](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A67_negative_results_adjudication_table.md):
among them a register classifier wrong on ≥7.1% of matches *because of unanchored Cyrillic
regexes* (the approach untested until the fix); a 28.6% undercount of MW's citation apparatus
from a literal-regex extractor (fixed; the apparatus was never smaller); a phantom
inter-annotator κ=0.42 that a roadmap cell invented and two paper drafts had to disclaim
(caught before submission — a planning document is not provenance); post-mortem
classifications overturned because the decisive counters had been hand-transcribed rather
than returned by the harness; and a spend guardrail that was declared and validated but
enforced nowhere on the live call path, with every offline gate green.

Five more candidate rows were **underpowered**: a grammatical contradiction unresolvable at
n = 2 attested lemmas; an embedding aligner tried once on a transliterated-Sanskrit sample;
a bundle of three optimization A/B experiments (one candidate row) retired before they ever
ran; a second-annotator agreement measurement whose gold column is still blank; and one row
included to pre-empt an over-read — a recorded 6.6% ungrounded-alignment figure that, cited
as "alignment fails", would itself be an underpowered claim: 93.4% ground, and the ungrounded
pairs correctly demote under grading.

The point of publishing the exclusion table is symmetrical to the point of the paper. A
negative-results genre that does not adjudicate provenance becomes a dumping ground for bugs;
the twelve incidental rows are exactly the ones that would have embarrassed this programme in
review had they shipped as science. Conversely the adjudication protects real negative
results from being dismissed as bugs: the intrinsic rows of §3 each name their mechanism, and
several carry positive controls.

## 5. The reversal: negative results need reopening conditions

On 11-07-2026 the programme recorded a structural dead end: the full-Mahābhārata citation
census was deferred because "no free bulk Nīlakaṇṭha-vulgate Sanskrit text exists" — every
bulk-downloadable MBH being the BORI critical recension, i.e. the wrong witness (§3.3's
class). The registry row carried its falsifiable escape hatch: *don't retry unless a
vulgate e-text with per-parvan continuous numbering is obtained.* **That premise was refuted
almost immediately**: a free 83,971-śloka Nīlakaṇṭha vulgate was located and harvested twice
independently, and the fitted-index method then passed its held-out gate on **all 18
parvans** (pooled 55.2% vs 1.4% shuffled null, ≈40×; the earlier single-book result
reproduced exactly across the two harvests)
([DEAD_ENDS §8b](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md);
[MBH census](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/MBH_CITATION_RESOLUTION_CENSUS.md)).
The historical record of the deferral is retained in the registry beneath the reversal.

Three lessons. A negative result is a claim about *inputs available now*, and must say so.
The `Don't retry unless` field is what made the reversal cheap — the reopening condition was
already written, and the new witness satisfied it verbatim. And a registry that can record
its own reversals without erasing the original entry earns the trust this genre needs:
the same file shows both that the programme closes doors and that it reopens them on
evidence.

## 6. Discussion

**The expensive part is the silence.** Nearly every intrinsic failure here *looked like
success*: 38.6% precision reads as thousands of plausible headwords; 117 spurious verb
classes sat in reviewed data; a lossy fold returns confident matches; a circular join
reports 94% coverage; a concordance would have returned loci for every query. The recurring
defence is not intelligence but instrumentation: held-out gates with shuffled nulls (§3.3),
size-matched controls (§3.4a), provenance splits (§3.4f), validation counts on every import
(§3.2b), and adversarial classification of extractor output (§3.1c).

**Ask what the intermediate artifact assumes.** The vulgate↔critical concordance is the
cleanest specimen of a general trap: a respectable, buildable artifact that presupposes the
correctness of the very thing under test. The programme now applies the question — *what
does this mapping assume?* — before building any bridge asset.

**Escape hatches keep dead ends honest.** Every registry row names the concrete condition
that would reopen it (an accent-bearing witness, a different corpus, a type-labelled
annotation layer, a vulgate e-text). §5 shows one firing. Negative results published without
reopening conditions age into folklore; with them, they are standing search queries.

**Where the classes bite hardest.** Missing-signal and wrong-witness failures dominate the
*philological* layer (they are properties of the sources); lossy-key failures dominate the
*engineering* layer (they are properties of joins and normalizations); statistical artifacts
dominate the *interpretive* layer. A newcomer to computational lexicography of any
under-resourced classical language can read the taxonomy as a checklist: what signal does my
source actually encode; what does my key collapse; which edition is my claim about; what does
my count confound.

## 7. Limitations

Recall is unknown and unknowable from the registries alone: failures that no session noticed,
or noticed and did not record, are absent, and early-programme (pre-registry) failures are
under-represented. All adjudications were made within the programme (single-adjudicator; the
protocol and per-row rationales are published for audit, but no independent second
adjudication exists yet). Evidence tiers vary and are flagged where weakest (§3.1c). The
programme is a single case; the taxonomy's transfer to other classical-language lexicography
programmes is argued, not demonstrated. And the paper reports *recorded* evidence only — no
failed experiment was re-run, so figures inherit their original runs' conditions.

## 8. Data availability

The Sanskrit-data registries this paper argues from — the dead-end and contradiction
registries and the measured-findings file — and the datasets behind the intrinsic results are
public in the [SanskritLexicography](https://github.com/gasyoun/SanskritLexicography),
[csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas),
[VisualDCS](https://github.com/gasyoun/VisualDCS),
[WhitneyRoots](https://github.com/gasyoun/WhitneyRoots),
[SanskritGrammar](https://github.com/gasyoun/SanskritGrammar),
[kosha](https://github.com/gasyoun/kosha),
[SanskritSpellCheck](https://github.com/drdhaval2785/SanskritSpellCheck),
[MWS](https://github.com/sanskrit-lexicon/MWS),
[csl-observatory](https://github.com/sanskrit-lexicon/csl-observatory) and
[IndologyScholars](https://github.com/gasyoun/IndologyScholars) repositories. Two harvest
sources are **private**: the programme-management hub (Uprava), which holds the infra twins
of the dead-end/contradiction registries, the refuted-hypothesis log, and the work registry —
their harvested rows are excerpted, with rulings, in the public companion
[adjudication table](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A67_negative_results_adjudication_table.md),
which carries all 46 per-candidate rulings. Links into the private hub are retained there for
programme-internal auditability and will not resolve for external readers; every intrinsic
result in §3 is additionally backed by a public source.

_Drafted by Fable 5 (`claude-fable-5`), 18-07-2026, under
[H1268](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1268-Fable_SanskritLexicography_negative-results-dead-ends-methods-paper_18.07.26.md);
fact-checked against every cited source by a read-only verification agent (Fable 5
`claude-fable-5` subagent), findings applied 19-07-2026.
Readiness 2/5 — pending: venue-format cut, related-work section beyond the venue sketch,
author voice pass, and the U1/U4 items maturing into results or staying excluded._

_Dr. Mārcis Gasūns_
