# Fifty Thousand Corrections: An Error-Origin Typology of Twelve Years of Collaborative Sanskrit Dictionary Maintenance

_Created: 17-07-2026 · Last updated: 17-07-2026_

> Draft manuscript for **Lexikos** (A31/P5 in the project's publication pipeline).
> Empirical basis: the released OBS-T correction-event corpus
> ([correction_events_release.csv](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/correction_events_release.csv),
> 52,498 events) plus the origin-axis census computed for this paper by
> [a31_origin_census.py](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/a31_origin_census.py)
> (outputs under
> [papers/a31/](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/a31)).
> Companion and boundary: the corpus, the location and edit-type axes, and the
> resource release are the subject of the OBS-T resource paper
> ([paper-obs-t-error-typology.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/paper-obs-t-error-typology.md),
> A12, LREC-COLING register); the maintenance *process* (who corrects, funnel,
> sustainability) is the subject of the GitHub-ecosystem paper
> ([A15_github_ecosystem.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/article/A15_github_ecosystem.md)).
> This paper adds a third, metalexicographic axis — the **origin** of each error
> in the dictionary production chain — and reads its consequences for
> lexicographic practice. It duplicates neither companion's analyses.

## Abstract

Retro-digitised dictionaries are corrected continuously after release, and every
correction quietly asserts a claim about *where the error came from*: the
nineteenth-century compositor, the twenty-first-century typist, or the
digitisation project's own markup tooling. We make that claim explicit. Building
on a released twelve-year corpus of 52,498 correction events to the Cologne
Digital Sanskrit Lexicon (CDSL, 43 dictionaries, 2014–2026), we define an
**error-origin typology** — *print-source*, *digitization*,
*conversion-markup*, *undetermined* — and attribute every event to it with
anchored, reproducible rules: the correctors' own per-event testimony where the
historical correction form recorded it, and one structural rule (the tag and
record-id layer does not exist in any printed book). Rules classify 58.4 % of
the corpus and abstain on the rest; on a stratified hand-checked sample,
per-class precision is 0.90–0.97 (micro-average 0.93). Three findings follow.
First, **evidence complementarity**: the 2014–2019 correction form preserves
origin testimony for 98.9 % of its events, while the 2019–2026 git history —
positionally richer in every other respect — supports origin attribution for
only 23.1 %. What a workflow asks its correctors determines what a project can
later know about its own errors. Second, attributed origins are dominated by
digitisation-era typing slips (41.5 % of all events), not by faults of the
nineteenth-century originals (3.8 %) — the books were better than their digital
copies before correction. Third, print-source shares vary by an order of
magnitude across dictionaries (0.5 %–46.9 % of classified events), but the high
shares are **single-collator campaign fingerprints**: in the dictionaries where
print errors dominate, one careful proofreader with the scan open contributed
94–100 % of the print-error reports. We close with concrete recommendations for
correction-workflow design in retro-digitisation projects, the first being:
ask the person with the scan open to record the origin, because nobody
downstream can reconstruct it.

**Keywords:** dictionary maintenance; error typology; error origin;
retro-digitisation; correction workflow; Sanskrit lexicography; Cologne Digital
Sanskrit Lexicon; quality assurance; crowdsourcing; metalexicography.

## 1. Introduction

A digitised historical dictionary has three authors: the lexicographer who
wrote it, the compositor who set it in type, and the project that keyed,
converted and marked it up a century later. When a user reports that an entry
is wrong, the repair fixes the text — but the *error* belonged to one of those
three hands, and the difference matters. An error inherited from the printed
book is a bibliographical fact about the 1866 edition; a keying slip is a
quality-assurance fact about the digitisation campaign; a broken tag is an
engineering fact about the conversion pipeline. The three call for different
tools, different budgets, and different expectations about how many more errors
of the same kind remain.

Correction streams are usually studied, when they are studied at all, by *what*
was changed. The Cologne Digital Sanskrit Lexicon (CDSL) — forty-three
dictionaries of Sanskrit, the largest digital resource of its kind — offers the
rare chance to ask the other question at scale. Its twelve-year correction
record (2014–2026) has been unified into a released, typed corpus of 52,498
correction events (the OBS-T resource; §3). The existing typology of that
corpus is deliberately two-axis: *where in the entry microstructure* an edit
landed, and *what kind of surface change* it made. Neither axis asks where the
error entered the production chain. This paper adds that third axis and asks
what twelve years of collaborative maintenance can teach working lexicographers
about the error genetics of retro-digitised dictionaries.

The answer turns out to hinge less on the dictionaries than on the correction
*workflow*. The CDSL collected corrections in two regimes: a public web form
(2014–2019) whose submitters wrote a short free-text justification for every
report, and a source git repository (2019–2026) whose commits batch hundreds of
edits under one message. The form's little comment box — `typo`,
`print error  n/n4`, `markup` — turns out to be the single most valuable piece
of origin evidence the project possesses, and the git era, for all its
positional precision, records almost none (§6.1). That asymmetry is the
methodological heart of this paper, and its most exportable lesson.

Our contributions: (i) a four-class **error-origin typology** for
retro-digitised dictionaries, with anchored classification rules that abstain
rather than guess (§4); (ii) a validated census of the full 52,498-event CDSL
correction corpus under that typology, with per-class precision measured on a
stratified hand-checked sample (§5); (iii) three empirical findings — evidence
complementarity between collection regimes, the dominance of digitisation-era
error mass, and the campaign structure of print-error discovery (§6); and (iv)
practical recommendations for correction-workflow design (§7).

## 2. The correction ecosystem

The CDSL's maintenance loop is described in detail in the project's workflow
documentation
([correction-workflow.md](https://github.com/sanskrit-lexicon/csl-corrections/blob/main/docs/correction-workflow.md))
and analysed as a contributor ecosystem in a companion paper (A15); here we
give only what the origin axis needs.

**The form era (2014–2019).** A public correction form invited any user to
report an error: dictionary, headword, the wrong text, the proposed fix, and a
free-text comment. 24,441 events survive from this era. Crucially, the
reporting user typically had the page scan open beside the digital text — the
CDSL interface links every entry to its scan — so the comment routinely records
a judgment nobody else could later make: whether the *print itself* was wrong
(`print error  virAma missing in print`) or the digital transcription had
strayed from a correct print (`typo`). A small number of maintainers then
applied the accepted reports to the source files.

**The git era (2019–2026).** Corrections moved to the source repository
itself: contributors (or maintainers acting on emailed and issue-tracker
reports) commit edits directly to the XML source, usually in batches — a
campaign of citation re-taggings, a sweep of English spelling fixes, an
alphabetisation audit. 28,057 events derive from this era's diffs. The commit
message names the campaign and its issue thread, but almost never states, per
edit, whether the flaw being repaired was the book's or the keyboarder's.

**The funnel.** Across both eras the contributor structure is a steep funnel —
about two hundred people reported, while a handful applied: the ecosystem
analysis counts 206 distinct submitters against 5 people who ever applied
corrections to the source, with the two most prolific maintainers accounting
for the large majority of applied events. For this paper the funnel matters in
one specific way: *testimony is authored at the wide end*. The person who saw
the scan wrote the comment; the person who applied the batch did not re-derive
it. A workflow that discards the wide end's free text discards the origin
record.

## 3. Data: the OBS-T corpus, and what this paper does not redo

All counts in this paper are computed from the released OBS-T corpus snapshot
([correction_events_release.csv](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/observatory/site/src/data/correction_events_release.csv),
CC-BY-4.0): 52,498 correction events, 2014-03-18 to 2026-05-30, 43
dictionaries, 208 named correctors after alias resolution; one row is one dated
old→new edit with IAST-normalised strings, a character-level edit-operation
trace, the corrector's verbatim comment where one exists, and two typology
axes — **location** in the entry microstructure (headword, sense, citation,
markup, …), derived by joining the edit to the XML-tagged source, and
**edit-type** (spelling, diacritic, spacing, …), read from the edit-op trace.
The corpus construction, the two-axis design and its empirical justification,
the encoding unification of the mixed Devanagari/Harvard-Kyoto form archive,
and the resource release with baselines are the subject of the OBS-T resource
paper (A12) and its design specification
([ERROR_TYPOLOGY_DESIGN.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/ERROR_TYPOLOGY_DESIGN.md));
we consume them and do not restate them.

Two properties of the corpus carry directly into our design. First, its
**evidence-label discipline**: every location label is marked `derived` (a
deterministic join succeeded) or `inferred` (join failed, label
`unattributed`), and no figure hides the distinction. We adopt the same
discipline for origin. Second, its **layer stamp**: every event records whether
it came from the correction form or the git history, which is what lets §6.1
measure the two regimes against each other.

One number should be fixed here because the project's own planning documents
have circulated a stale pair: earlier drafts and the P5 roadmap row cite
"50,953 corrections", the count of a superseded cut; the released snapshot is
52,498, and *no inter-annotator agreement figure exists yet* for any axis of
this corpus (the gold sample's second-annotator column is still empty — §8).
A κ value that appears in one roadmap table (0.42) describes tooling
demonstrated on other org datasets, not a measured property of this corpus,
and is not claimed anywhere in this paper.

## 4. The origin axis

### 4.1 Classes

The typology answers one question per event: **at which stage of the
production chain did the flaw being repaired enter the text?**

**Table 1.** The error-origin typology.

| Class | The flaw entered… | Typical evidence |
|---|---|---|
| `print-source` | in the printed book (author, compositor, press) | corrector testimony: "print error", "misprint", "print partially missing" |
| `digitization` | at transcription: keying, OCR, misread scan, encoding entry | corrector testimony: "typo", "OCR", "scan error", "coding" |
| `conversion-markup` | in the project's own tag/record layer | structural: the location join places the edit in markup or record-metadata — a layer no printed book has |
| `undetermined` | evidence insufficient | — (never guessed) |

Digitization subtypes (keying slip vs OCR vs scan misreading vs encoding) are
carried by the rule identifier on each classified row, not collapsed away; in
this corpus they are dominated overwhelmingly by the keying-slip anchor
(21,718 of 21,795 digitization events; OCR 48, scan 19, coding 10) — consistent
with the CDSL's history as a keyed, not OCR'd, digitisation.

An *editorial* class (enhancements and normalisations that repair no error) was
designed and then dropped: the only candidate anchor — 89 form events whose
comments note a variant reading — sits under the corrector's own "typo" type
token, so no anchored rule separates editorial intent from a transcription
slip. The class exists in the data (our validation sample surfaced
citation-format normalisations filed as "typos"; §5), but it cannot be
extracted mechanically at acceptable precision, and we prefer a missing class
to a fabricated one. It is future work under campaign-level attribution (§8).

### 4.2 Rules, and the abstention discipline

Classification uses two evidence sources and nothing else.

**Corrector testimony** (form layer only, 24,441 events, 99.97 % of which
carry a comment): word-anchored patterns over the comment — `print error` /
`misprint` / `print … missing` → `print-source`; a leading `typo`,
`capitali[sz]ation`, `coding`, or an `ocr` / `scan error` token →
`digitization`; a leading `markup` → `conversion-markup`. Print-source
patterns outrank the leading `typo` token, because the form's conventions put
the type word first and the substantive judgment after it (`typo  print error
i/i10`). Git-era commit messages are *not* used: they describe campaigns, not
events.

**One structural rule** (any layer): an event whose *derived* location is
`markup` or `meta` — the tag layer, the record ids, the page-column pointers —
is classified `conversion-markup`, because that layer is created by the
project; a printed dictionary has no `<ls>` tags to get wrong. The rule fires
only on join-backed (`derived`) locations, never on heuristic ones.

Everything else is `undetermined`. The abstention discipline is inherited from
a measured in-house failure: an earlier text classifier in this project used
unanchored patterns and silently misclassified at least 7.1 % of its targets;
the repair cost more than the anchored design would have. Every classified row
in the released census carries the identifier of the rule that fired
([a31_origin_rules.csv](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/a31/a31_origin_rules.csv)),
so any rule can be audited, re-weighted or ablated without re-running the
judgment.

## 5. Validation

A stratified sample of 120 events (30 per class, seeded reservoir sampling)
was drawn and independently judged against each event's full evidence — the
old/new strings, the corrector's comment, the OBS-T location and edit-type
([a31_origin_validation_sample.csv](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/a31/a31_origin_validation_sample.csv)).
The annotator of record for this pass is the drafting model (Fable 5,
`claude-fable-5`), a single annotator; a second, human annotation pass is the
standing gate shared with the corpus's location-axis gold sample, and until it
lands we report precision, not agreement (§8).

**Table 2.** Per-class precision on the hand-checked sample
([a31_origin_validation_metrics.csv](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/a31/a31_origin_validation_metrics.csv)).

| Class | n | correct | precision |
|---|---:|---:|---:|
| print-source | 30 | 29 | 0.967 |
| digitization | 30 | 28 | 0.933 |
| conversion-markup | 30 | 27 | 0.900 |
| **all classified (micro)** | **90** | **84** | **0.933** |
| undetermined (abstention correctness) | 30 | 21 | 0.700 |

The failure modes are instructive, not random. All five classified errors are
**editorial events wearing an error costume**: citation-format normalisations
filed under "typo" or even "print error  reformat for consistency", an
editorial supplement wrapped in a change tag, and one block of untranscribed
Greek — print content the keying pass skipped — whose repair the structural
rule read as tag-layer work. The abstention misses run the other way: 9 of the
30 `undetermined` rows *could* have been classified (all as
`conversion-markup`) by reading the git commit message, which names the
markup-enrichment campaign the edit belongs to. Rule-level abstention is thus
conservative in exactly the direction we want — its errors are recall lost,
not fabricated classes — and campaign-level attribution is the obvious next
increment (§8).

## 6. Results

### 6.1 Evidence complementarity: the workflow decides what you can know

**Table 3.** Origin census, overall and by collection regime
([a31_origin_census.csv](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/a31/a31_origin_census.csv)).

| Scope | print-source | digitization | conversion-markup | undetermined |
|---|---:|---:|---:|---:|
| all (n = 52,498) | 2,010 (3.8 %) | 21,795 (41.5 %) | 6,863 (13.1 %) | 21,830 (41.6 %) |
| form era (n = 24,441) | 2,010 (8.2 %) | 21,795 (89.2 %) | 368 (1.5 %) | 268 (1.1 %) |
| git era (n = 28,057) | 0 | 0 | 6,495 (23.1 %) | 21,562 (76.9 %) |

The split could hardly be sharper. The correction form yields origin evidence
for **98.9 %** of its events — because it asked a human, at the moment of
comparison with the scan, to say what they were looking at. The git era, whose
positional evidence is *better* in every other axis (its location joins are
100 % derived, against 28.8 % for the form era), supports origin attribution
for only **23.1 %** of its events, and all of it through the structural
markup/meta rule rather than through anyone's testimony. The two regimes are
evidence-complementary mirror images: the form knew *why*, the repository
knows *where*. Neither alone can support a full error genetics — and the
project's move from form to repository, rational on every engineering ground,
silently traded away the origin record.

### 6.2 The books were better than their digital copies

Among the 30,668 origin-classified events, digitisation-era typing slips
outnumber inherited print errors by more than ten to one (21,795 against
2,010). Even restricted to the form era — where both classes had an equal
chance of being reported, by the same people, in the same workflow — print
errors are 8.2 % of events against 89.2 % for transcription slips. The
nineteenth-century originals, whatever their reputations, arrive in the
corrected record as the *minor* error source: the dominant error mass of a
retro-digitised dictionary is manufactured at digitisation time. For
maintenance budgeting this inverts a common intuition. The scholarly instinct
is to distrust the old book; the evidence says to distrust the young keyboard,
and to spend QA effort accordingly — which is also the optimistic reading,
since transcription errors, unlike compositors' errors, are systematically
detectable against the scan and largely automatable away (spelling, diacritic
and case slips dominate the digitization class: 8,374 + 3,693 + 3,743 events).

### 6.3 Print-error discovery is a collation campaign, not a background hum

**Table 4.** Print-source share by dictionary (dictionaries with ≥ 30
classified events, ranked by share; full table in
[a31_origin_by_dict.csv](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/a31/a31_origin_by_dict.csv)).

| Dict | classified | print-source | share | top corrector's share of print-source rows |
|---|---:|---:|---:|---:|
| BEN (Benfey 1866) | 622 | 292 | 46.9 % | 97.9 % |
| PD | 1,375 | 511 | 37.2 % | 100 % |
| BUR (Burnouf 1866) | 739 | 241 | 32.6 % | 97.1 % |
| SKD (Śabdakalpadruma) | 323 | 90 | 27.9 % | 94.4 % |
| CAE (Cappeller 1891) | 1,298 | 216 | 16.6 % | 95.8 % |
| PUI | 739 | 99 | 13.4 % | 70.7 % |
| CCS | 2,226 | 92 | 4.1 % | 90.2 % |
| PWG (Böhtlingk-Roth) | 932 | 27 | 2.9 % | 63.0 % |
| MW (Monier-Williams) | 4,523 | 83 | 1.8 % | 34.9 % |
| PW (Böhtlingk) | 11,842 | 195 | 1.6 % | 33.3 % |
| WIL (Wilson) | 1,130 | 7 | 0.6 % | 57.1 % |

Read naïvely, Table 4 says Benfey's and Burnouf's 1866 printings were an order
of magnitude worse than the Petersburg Academy's. The last column forbids the
naïve reading: in every dictionary with a high print-source share, a *single
corrector* contributed 94–100 % of the print-error reports. These are
signatures of **systematic scan-against-text collation campaigns** — one
careful proofreader, one dictionary, the scan open — not population estimates
of press quality. What the table really measures is where such a collation was
carried out, and what it found when it was: *where someone systematically
collated, print errors were 13–47 % of what they caught*. In the
heavily-corrected big dictionaries (PW, MW), whose reports came from hundreds
of dispersed users reading entries for content, print errors are 1–2 % — not
because Roth's compositors were fifty times better, but because dispersed
lookup traffic surfaces transcription noise, while only deliberate collation
surfaces the print's own faults. Correction streams sample errors through the
behaviour of the people who report them; every share in this paper is a share
of curatorial attention (the caveat is the corpus's own, and it binds the
origin axis exactly as it binds the other two).

The edit-type skews corroborate the classes' construct validity: print-source
events concentrate in spelling, citation-digit and diacritic repairs (the
compositor's inventory of failure), conversion-markup events in spacing,
punctuation and whole-record (`source-raw`) operations (the pipeline's), and
digitization events in spelling, case and diacritic slips (the typist's)
([a31_origin_by_edit_type.csv](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/a31/a31_origin_by_edit_type.csv)).

## 7. Consequences for practice

Four recommendations follow directly from the evidence, in descending order of
generality.

**1. Ask for origin at report time.** The single highest-value field in twelve
years of CDSL correction data is a free-text box filled by a person with the
scan open. No downstream process — not the git diff, not the edit-op trace,
not this paper's rules — can reconstruct what that person could see in one
glance. A correction form (or issue template, or commit-message convention)
should ask: *was the print wrong too?* One radio button preserves what §6.1
shows the repository era lost.

**2. Budget QA against digitisation, not against the book.** The error mass is
transcription-era, surface-level, and machine-tractable (§6.2). For a
retro-digitisation project the cheapest large win is systematic
spelling/diacritic/case validation against per-language confusion profiles —
not semantic review of the original's content. The old book has earned more
trust than its digital copy.

**3. Treat print-error discovery as a campaign to be commissioned, not a
stream to be awaited.** Dispersed users will not find the print's faults; one
collator per dictionary will (§6.3). A project that wants a bibliographically
honest error record for a given dictionary should commission the collation —
the CDSL data suggests a single motivated proofreader per dictionary changes
the origin profile of the entire correction record.

**4. Preserve the audit trail in a form that survives workflow migrations.**
Each of the CDSL's collection regimes preserved evidence the other lost. When
maintenance workflows migrate — form to repository, repository to whatever
follows — an explicit evidence inventory (*what does the old workflow record
per event that the new one does not?*) would have cost one afternoon and saved
an axis.

## 8. Limitations

**Single-annotator validation, and no κ.** The precision figures in Table 2
are one annotator's judgments, and that annotator is the drafting model. No
inter-annotator agreement exists yet for this axis — nor, it must be said
plainly, for any axis of the underlying corpus: the corpus's own gold sample
([gold_sample.csv](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/validation/gold_sample.csv))
still awaits its second annotator. Both κ gates are the same recruiting
problem and are tracked as one action in the project's planning registry. A
published version of this paper should carry the measured κ or explicitly
mark the typology as single-adjudicated.

**Origin coverage is workflow-bounded.** 41.6 % of events are `undetermined`,
concentrated almost entirely in the git era (76.9 % of its events). This is a
property of the evidence, not of the taxonomy — but it means every
origin-share statement in §6 is conditional on the classified subset, and the
git era's classified subset is markup-only by construction. The form-era
numbers (98.9 % classified) are the load-bearing ones.

**Testimony is trusted, and testimony can be sloppy.** The rules inherit the
correctors' own judgments, including their errors: our validation surfaced
"print error" applied to a formatting normalisation. Measured precision
(0.93–0.97 on the testimony classes) bounds but does not eliminate this.

**Editorial events hide in the error classes.** The dropped editorial class
(§4.1) means some share of "digitization" events — our sample suggests a few
per cent — are normalisations, not error repairs. Campaign-level attribution
from git commit messages (which name enrichment campaigns explicitly, and
which our abstention analysis shows would reclassify roughly a third of a
sample's undetermined rows) is the designed next increment.

**Corrected ≠ wrong.** The corpus records repairs the community chose to make.
Dictionaries without a collation campaign do not have fewer print errors; they
have fewer *found* ones. No number in this paper is a latent error rate.

## 9. Conclusion

Asked *where its errors came from*, a retro-digitised dictionary's correction
record gives a clear answer wherever the workflow thought to keep the
evidence: mostly from the digitisation, not the book; from the project's own
markup layer in a substantial minority; from the nineteenth-century press in a
small share that balloons only where someone deliberately went looking for it.
The deeper finding is about the record itself. Origin evidence exists at
exactly one moment — when a person with the scan open decides what they are
seeing — and the CDSL's history demonstrates both outcomes: a humble web form
that captured that moment 24,000 times, and a technically superior successor
workflow that let it evaporate. Lexicographic error genetics, this corpus
suggests, is less a matter of forensic reconstruction than of asking one extra
question at the right time.

## References (draft — to be finalised for submission)

- Boros, E., M. Ehrmann, M. Romanello, S. Najem-Meyer and F. Kaplan. 2024.
  Post-Correction of Historical Text Transcripts with Large Language Models.
  *LaTeCH-CLfL 2024*. https://aclanthology.org/2024.latechclfl-1.14/
- Bryant, C., M. Felice and T. Briscoe. 2017. Automatic Annotation and
  Evaluation of Error Types for Grammatical Error Correction. *ACL 2017*.
- Gebru, T. et al. 2021. Datasheets for Datasets. *Communications of the ACM*
  64(12).
- Hartmann, R. R. K. and G. James. 1998. *Dictionary of Lexicography*.
  London: Routledge.
- Katre, S. M. 1941. *Introduction to Indian Textual Criticism*. Bombay:
  Karnatak Publishing House.
- Svensén, B. 2009. *A Handbook of Lexicography*. Cambridge: Cambridge
  University Press.
- Wiegand, H. E. 1998–. *Wörterbuchforschung*. Berlin: De Gruyter.
- Project resources: the OBS-T corpus and datasheet
  ([DATASHEET.md](https://github.com/sanskrit-lexicon/csl-observatory/blob/main/docs/DATASHEET.md));
  the OBS-T resource paper (A12, in draft); the CDSL maintenance-ecosystem
  paper (A15, in draft); the correction workflow documentation
  ([correction-workflow.md](https://github.com/sanskrit-lexicon/csl-corrections/blob/main/docs/correction-workflow.md)).
  [Lexikos house style and the final citation forms to be applied at
  submission; an Afrikaans *opsomming* is required by the venue and will be
  supplied.]

> Provenance: drafted 17-07-2026 by Fable 5 (`claude-fable-5`) under handoff
> [H1074](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1074-Fable_SanskritLexicography_a31-corrections-error-typology-draft_16.07.26.md);
> census and validation artifacts committed under
> [papers/a31/](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/a31).
> All tables computed by
> [a31_origin_census.py](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/a31_origin_census.py)
> and
> [a31/a31_apply_judgments.py](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/a31/a31_apply_judgments.py)
> from the released OBS-T snapshot; none are hand-edited.

_Dr. Mārcis Gasūns_
