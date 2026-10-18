# H5069 — source support in 30 published PWG-RU sense records

_Created: 20-09-2026 · Last updated: 20-09-2026_

Executed by Claude Code Opus 5 (`claude-opus-5`). Handoff minted by Codex Astra
(`gpt-6-astra`), 16-09-2026; filename tier `Opus`, intended executor Claude
Opus 5 — tier matches, no provenance divergence. Class `data`, so the closing
`## Verifier` PASS is owed to a session that is not this one; see
[§10](#10-independent-review--pending-not-pass).

## 1. The question, and the question this is not

This audit asks one thing of each record: **does the German source span
license the meaning the Russian asserts?** It does not ask whether the Russian
is good Russian, and it does not estimate a pool-wide error rate — that is
what the R15 / R3434 gate apparatus already does with LLM judges over seeded
n=400 samples
([WAVE3_GATE_VERDICT.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/pwg_tm_canonical/wave3_receipt/WAVE3_GATE_VERDICT.md)).
The sample here is **purposive, not random**, and nothing in this document may
be read as a rate over the corpus. Where a corpus-wide number does appear
([§7](#7-store-wide-census--counted-not-estimated)) it is a **census** — every
one of the 2392 records counted by a deterministic predicate, nothing
estimated from the 30.

Four verdicts, fixed before the first record was opened:

1. `faithful` — every Russian assertion is licensed, every German
   qualification survives.
2. `addition` — the Russian asserts a meaning, referent, manner or specificity
   the German does not license.
3. `omission` — a German qualification is silently dropped, so the Russian
   reads more certain or more general than its source.
4. `conflation` — two German spans or senses merge into one Russian assertion,
   or a sense boundary moves.

## 2. Substrate and freeze

| item | value |
|---|---|
| store | [`release/pwg_tm_canonical/canonical.v1.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/pwg_tm_canonical/canonical.v1.jsonl) |
| sha256 | `b9ad8e9ff99d561de72029e9af40664e9cf7bfabe1575faf7858d88b757bbe82` |
| bytes / rows | 23 796 159 / 2392 |
| repo revision at freeze | `c1ccf220a38c3476c899b3445022f8389443c2a3` |
| eligible records | 2096 (Russian asserts a meaning; target ≠ source) |
| selected | 30 (6 per stratum) |

The store was chosen because it is **already committed in a public repo**, so
quoting it adds no publication risk. That is why the H178 bake-off substrate
`src/pwg_ru_translated.jsonl` was deliberately not used: that store is
gitignored and unpublished, and the H178 generator says so in its own header.

Selection is **seedless**. Strata are computed from the record text; within a
stratum the six members are the six smallest `sha256(record_id)`. Identical
store bytes reproduce the identical thirty ids, on any machine, with no seed
to record or lose. Re-prove it:

```bash
python src/h5069_source_support_audit.py verify
```

which re-hashes the store, re-hashes every frozen record, and re-runs the
selection, failing on any drift.

## 3. Strata

Disjoint, fixed priority order (the priority is part of the frozen contract —
changing it changes the sample, so it is declared in the manifest and pinned
by selftest).

| stratum | predicate | pool | drawn |
|---|---|---|---|
| `short_gloss` | `src_len ≤ 200` and `n_senses == 1` | 644 | 6 |
| `uncertainty` | German hedge present (`wohl`, `viell.`, `etwa`, `fehlerhaft`, …) | 233 | 6 |
| `polysemy` | `n_senses ≥ 5` | 279 | 6 |
| `compound` | preverb/compound head (`vraj (pari)`, `upa+jan`) | 328 | 6 |
| `citation_dense` | `n_ls ≥ 10` | 241 | 6 |

## 4. Verdict distribution

| verdict | n | records |
|---|---|---|
| `faithful` | 21 | R01–R06, R08, R09, R11, R14, R15, R19, R21–R29 |
| `addition` | 4 | R12, R16, R20, R30 |
| `conflation` | 3 | R10, R13, R17 |
| `omission` | 2 | R07, R18 |

Row-by-row evidence, with the deciding German and Russian words, a confidence
and a **refutation criterion for every substantive criticism**, is in
[`verdicts.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h5069/verdicts.tsv).

## 5. The findings that matter

### 5.1 `adhi-vid` asserts a spatial relation where PWG asserts an instrumental one

The headline defect, R20, stratum `compound`, record
`pwg.sense:vid:adhi + vid:1:1`.

German: `die erste Frau (acc.) durch eine zweite Frau (instr.) hintansetzen` —
to set the first wife aside **by means of** a second.

Russian: `ставить первую жену (acc.) позади второй жены (instr.)` — to place
the first wife **behind** the second.

The `(instr.)` grammar label is retained immediately after a Russian phrase
that expresses a locative relation. The record therefore now asserts that the
Sanskrit instrumental here carries a spatial meaning. A Russian-reading
Sanskritist takes the wrong construction semantics from a gloss that reads
fluently and confidently — precisely the failure mode this audit was
commissioned to look for.

Compounding it, this record also carries the §5.6 alignment defect in its worst
form. The German has seven gloss spans, the Russian six, and from index 2
onward **every Russian span renders the German span after it**:

| i | German | Russian |
|---|---|---|
| 0 | `überheirathen) die erste Frau` | `жениться поверх) ставить первую жену` |
| 1 | `durch eine zweite Frau` | `позади второй жены` |
| 2 | `hintansetzen` | `ставить позади первую (прежнюю) жену (жён)` ← renders DE 3 |
| 3 | `die erste (früheren) Frau (Frauen) hintansetzen` | `выступать соперницей` ← renders DE 4 |
| 4 | `als Nebenbuhlerin auftreten von` | `жена, отставленная соперницей` ← renders DE 5 |
| 5 | `eine durch eine Nebenbuhlerin hintangesetzte Frau` | `быть отставленной второй женой` ← renders DE 6 |
| 6 | `durch eine zweite Frau hintanzusetzen` | — |

Any consumer that pairs German span *n* with Russian span *n* — which is what
the wrappers exist for — reads the wrong gloss for five of the seven.

The table also settles the verdict from the record's own evidence. Rows 4 and 5
render exactly the same German relation with the Russian **instrumental**
(«отставленная соперницей», «отставленной второй женой») — agent, not location.
The headline gloss is the one place the record puts the second wife in a
locative relation, and it is the gloss a reader meets first.

What makes it a confirmed error rather than a judgment call: **the same record
renders `hintansetzen` correctly twice further down**, as «отставленная» and
«быть отставленной». The defective rendering is the headline gloss — the one a
reader meets first.

**Refutation criterion:** show a German or Sanskrit basis for reading this
instrumental spatially. None was found.

### 5.2 `союзить` is not a Russian word

R16, stratum `polysemy`, record `pwg.sense:unresolved:yat:0`. German
`verbünden, vereinigen` → Russian «союзить, объединять». The only attested
«союзить» is an obscure shoemaking term (to fit a vamp, from «союзка»); in the
sense "to ally" it is not in Ozhegov, Ushakov, BAS or Efremova. A non-word
cannot be licensed by any source span. **Refutation criterion:** produce it
from a standard dictionary in this meaning.

### 5.3 An unresolved translator alternative shipped to readers

R18, stratum `polysemy`, record `pwg.sense:unresolved:vah:0`. German
`ziehend folgen` → Russian «следовать, влекомый/тянущийся вослед». The slash
is not a Russian coordination; it is two candidate participles the translator
did not choose between, and the accept gate passed it.

### 5.4 Russian prose wearing Sanskrit markup

R03, stratum `short_gloss`. German `{%zum Weibe nehmen%}` → Russian
`{#брать в жёны#}`. The meaning is right; the Russian sits inside the
**Sanskrit** mask instead of the gloss mask. Every renderer and span counter
keyed on `{#…#}` now mis-types Russian prose as Sanskrit.

### 5.5 Untranslated German inside Russian glosses, and a lost scope

R07, stratum `uncertainty`, record `pwg.sense:unresolved:han:0`:

1. `fest —, consistent werden` → «сгущаться, становиться плотным —, плотным
   (consistent)» — the German word `consistent` survives untranslated in
   parentheses, and `fest` and `consistent` collapse onto one Russian word.
   Eighteen spans later the same German pair is rendered «твёрдым —, плотным
   (consistent)»: one record, two incompatible renderings, residue in both.
2. `einer <ab>best.</ab> Truppenaufstellung` → «построения <ab>best.</ab>
   войск». In German `best.` (= *bestimmten*) modifies the **formation**; in
   the Russian word order it reads as modifying the **troops**. The
   restriction "a *particular* formation" is gone.

### 5.6 Span merges that move a grammar label's anchor

R10, R13, R17. The recurring shape: German brackets a grammar label between
two gloss spans — `{%Kunde von Etwas%} (acc.) {%erhalten%}` — and the Russian
merges them into one span with the label trailing:
`{%получить весть, известие о чём-л.%} (acc.)`. Meaning survives for a human
reader; the label's anchor moves, and every later span in the record
misaligns, so any consumer that zips German span *n* to Russian span *n* pairs
the wrong two from that point on. R17 (`gam`, 83 senses, 8368 chars) carries
four such merges.

## 6. Where the rubric was deliberately not stretched

Several defects were found that are **not** source-support defects and are
recorded as such rather than inflating the verdict counts: the literalism
«не отходил от моего бока» for the idiom *von meiner Seite weichen* (R12), the
register elevation «санкционировать» for *billigen* (R10), and the predicate
demotion in «вести нищенскую жизнь бездомного скитальца» for *umherwandern*
(R19). A rubric that absorbs every infelicity measures nothing.

## 7. Store-wide census — counted, not estimated

Deterministic predicates over all 2392 records. This is a census; no number
here is an extrapolation from the 30.

```bash
python src/h5069_source_support_audit.py poolcheck
```

| class | count | share |
|---|---|---|
| Russian has fewer `{%…%}` spans than the German | 898 / 2392 | 37.5% |
| …of which the Russian has **none at all** | 718 / 2392 | 30.0% |
| …of those, guillemets «…» stand where the delimiters were, and appear nowhere in the German | 133 / 718 | 18.5% |
| Cyrillic prose inside a `{#…#}` Sanskrit mask | 25 / 2392 | 1.0% |

The datasheet for this release family states that markup `<ls>`, `{#…#}`,
`{%…%}` is **preserved**
([release/pwg_tm/DATASHEET.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/pwg_tm/DATASHEET.md)),
and the wave gate verdicts quote expected Russian targets *with* their
wrappers (`{%an%}` → `{%переселяться%}`). So this is a violation of a
documented invariant, not an undocumented convention — and it is inconsistent,
since 1494 records keep their wrappers.

**Where the defect lives.** Both published stores — `canonical.v1.jsonl` and
the sibling
[`release/translation_memory/translation_memory.ru.publication.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/translation_memory/translation_memory.ru.publication.jsonl)
— lose the wrapper on the Russian side of all 718 records while both keep it
on the German side. The loss is therefore **upstream of both exports**, in the
generated Russian itself, faithfully carried by the release layer rather than
introduced by it. The guillemet sub-shape is the tell: the model read `{%…%}`
as "italics" and re-rendered it in a Russian typographic convention.

## 8. Two of this audit's own hypotheses were falsified

Recorded because unfalsified findings from a session that never falsified
anything are worth less.

1. **"The canonical export drops the wrappers."** The first probe compared the
   canonical target against the sibling TM record and reported that the TM
   kept its wrappers in all 718 cases. The probe searched the whole payload
   JSON, which contains the **German** field. Re-run against the Russian field
   only: 0 of 718 keep it. The conclusion inverted — the export is innocent.
2. **"The 115-span `gam` record drops whole sub-senses."** German sub-senses
   `a〉 gekommen, angelangt` and `b〉 erfüllt —, voll von` appeared to have no
   Russian counterpart. They do; the Russian is 185 bytes shorter, so equal
   byte offsets show different material. Re-probing at corrected offsets found
   both present. The real defect is four span merges (§5.6), a much smaller
   claim.

Both misses share a shape: a negative about the data assembled from one probe
that was never asked whether it had measured what it claimed to measure.

## 9. Controls, and the blinding defect the controls exposed

Two synthetic items, built by mutating frozen real records, sit in the review
packet alongside the thirty. They never enter any store.

| control | base (outside the 30) | mutation | expected |
|---|---|---|---|
| positive | `apavā`, `ṚV. 10,130,1` | `{%распускать ткань%}` → `{%распускать шёлковую ткань%}` against German `{%ein Gewebe auflösen%}` | `addition` |
| negative | `samanuyā`, `MBH. 2,1608` | `{%следовать%}` → `{%идти следом%}` against German `{%folgen%}` | `faithful` |

The positive control plants a fibre the German never names — `Gewebe` is a
woven fabric of no stated material, and the record's only other content is a
bare locus, so nothing recovers the silk. The negative control replaces a gloss
with a paraphrase rather than a synonym, which is the sharper probe: a synonym
offers nothing to over-trigger on, while a structurally different but fully
licensed rendering does.

**Two blinding defects were found here, both by reviewers, both in this
apparatus rather than in the data.**

*First: ids that announced the answer.* The control ids were written literally
as `H5069.control:pos:001` and `H5069.control:neg:001`, and the first reviewer
named both controls from the id strings before reading a single gloss. Fixed:
every packet item, real and synthetic, carries an opaque `H5069.item:<hash>` id
of one shape; the id→record map lives only in the sealed key; four assertions
pin it. That packet's results were discarded, not reported.

*Second: each mutation shipped beside its own unmutated twin.* Both controls
were originally built from records **inside** the frozen thirty, so the packet
carried the mutated and the original text of the same record. The reviewer that
passed the gate said how it did so in its own words — it identified the
positive control because a sibling item "renders the byte-identical source"
with the plain wording. That is detection by near-duplicate comparison, not by
source-support reasoning: the gate it passed measured the wrong thing. Fixed
on two levels — control bases are now drawn from eligible records **outside**
the sample (so no twin exists), and `cmd_controls` **refuses** any packet in
which a base also ships unmutated, with the refusal pinned by a data-level
test. The v1 packet, its key and its verdicts are kept as
`*.v1-twin-defect.*` so the weakened result stays auditable rather than
disappearing.

Reviewer blinding is also enforced physically: during a review run the
directory contains only the brief and the packet — manifest, sample, controls,
sealed key and this session's verdicts are moved out of the tree.

One hygiene lapse is recorded rather than smoothed over: this report's first
draft was written straight into the packet directory while a review run was in
progress, and sat there for roughly two minutes before being moved out. The
brief forbids reading `*AUDIT*.md` by name, so the exposure is bounded by an
instruction rather than by physics — and "the instructions said not to" is a
weaker guarantee than "the file was not there", which is the guarantee the rest
of this section relies on. Nothing in the reviewer's output quotes or references
this report, but that is weak evidence, not proof.

## 9a. What the supplementary reviewer found

One blind pass by GLM 5.3 Flash (`zai-coding-plan/glm-5.3-flash`) over the
32-item v1 packet. It carries **no gate authority** — it is not the mandated
review (§10) — and its control result is weakened by the twin defect above.
It is reported anyway because it did three useful things.

**It passed the control gate.** Positive: `expected=addition, got=addition`.
Negative: `expected=faithful, got=faithful`. So the planted assertion is
detectable and the licensed re-wording does not provoke a false conviction —
though see the twin caveat for how it found the positive one.

**It agreed on 21 of 30 and disagreed on 9 — every disagreement in the
direction of `faithful`.** A reviewer that convicts less than the auditor is
the useful kind of disagreement: it tests whether the auditor over-triggered.
Three of them touch findings this report leads with, so each is adjudicated
here rather than averaged away.

1. **R20 `adhi-vid` (the headline).** The reviewer wrote: *"instrument 'durch'
   recast spatially ('позади'), same displacement sense, case labels kept"* —
   and graded it `faithful` at **medium** confidence. It agrees on the fact and
   differs on the rule: it treats a recast relation as tolerable because the
   overall displacement sense survives. **The verdict stands.** What the
   reviewer's reasoning does not weigh is the `(instr.)` label sitting on
   «второй жены»: without it this would be a translation infelicity, and with
   it the record makes a claim about what the Sanskrit instrumental *means*. A
   grammatical label attached to a relation the Russian does not express is not
   a stylistic matter. This is a genuine rubric disagreement between a human-
   readable "same idea" test and a "what does the record assert" test, and it
   is exactly the kind the mandated Astra review should adjudicate.
2. **R16 `yat` («союзить»).** The reviewer graded `faithful` at high
   confidence, evidencing *"All 15 pairs map 1:1; sense-3 case labels (gen./acc.)
   kept."* That is a **structural** check; it never addresses whether «союзить»
   is a Russian word in this meaning, which is the entire claim. **The verdict
   stands**, its refutation criterion unmet and untouched.
3. **R18 `vah` (the «влекомый/тянущийся» slash).** The reviewer graded
   `faithful`, quoting two *other* spans of the record (the `Pass.` gloss and
   `heimführen`). It never reaches the unresolved alternative. **The verdict
   stands**, again unaddressed rather than refuted.

The same shape holds for the remaining six (R07, R10, R12, R13, R17, R30): the
reviewer's evidence quotes spans other than the ones under criticism, or checks
index alignment instead of assertion content. That is a real limitation of a
one-pass flash review over 32 long records, and a reason the mandated review is
not a formality.

**It named the apparatus's second blinding defect** — the twin — which is the
most valuable thing it produced, and the reason §9 now carries a guard.

The full verdicts are in `reviewer_verdicts_supplementary.json`; re-grade with
`score`. Its own stated limitations are worth keeping: no access to printed PWG
or scans, so the German in the packet is its only ground truth, and it could
not verify Sanskrit quotations, loci or page references.

## 10. Independent review — PENDING, not PASS

The mint names the verifier precisely: *an independent Codex Astra
(`gpt-6-astra`) logic critic*, with DeepSeek V4 Pro forbidden. That lane was
live at the start of this session (probed: `codex-cli 0.153.4`, `model =
"gpt-6-astra"`, ChatGPT auth) and **hit its usage limit mid-run**:

```
ERROR: You've hit your usage limit. … try again at Sep 21st, 2026 10:02 PM.
```

Re-probed at the end of the session (20-09-2026 19:28 UTC) with a one-token
prompt: the same limit, the same reset time. The block is the account's quota,
not this session's invocation.

Per the mint, *missing review is PENDING, never PASS*. No substitute family
was promoted into the mandated verifier slot. The supplementary GLM 5.3 Flash
pass in §9a is **not** that review and does not satisfy it.

The Astra run should use the **rebuilt** packet, not the archived v1 one: the
controls now come from outside the sample, so the twin shortcut is gone and the
gate measures source-support reasoning rather than near-duplicate spotting.
Three verdicts it should adjudicate first are R20, R16 and R18, where this
session and the supplementary reviewer disagree on the record (§9a).

To complete the review after the reset, from the repository root:

```bash
cd RussianTranslation/pwg_ru/h5069 && codex exec --skip-git-repo-check -c model_reasoning_effort='"high"' --sandbox workspace-write "Read REVIEWER_BRIEF.md and carry out exactly what it asks over every item in review_packet.jsonl. Write reviewer_verdicts.json here."
```

then grade it against the sealed key:

```bash
python src/h5069_source_support_audit.py score pwg_ru/h5069/reviewer_verdicts.json
```

The control gate passes only if the reviewer convicts the positive control and
clears the negative one.

## 11. Corrections — staged, not applied

Five confirmed, mechanically checkable errors are staged in
[`corrections_proposed.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/h5069/corrections_proposed.tsv).
**Nothing was applied.** The existing editorial path for touching promoted
records runs through a human-voted review sheet and `/decisions-apply`
(see
[review/decisions_applied_2026-07-28_g6-mqm-gold-starter.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/decisions_applied_2026-07-28_g6-mqm-gold-starter.md)),
and the mint's edit scope forbids promotion of unreviewed records. Editing a
content-addressed release artifact by hand would also invalidate its
`target_hash`. So the corrections are staged for that path, and a human
decides.

## 12. Limitations

1. **Purposive sample.** No corpus-wide error rate may be inferred from the
   thirty. The §7 numbers are a census by deterministic predicate and are the
   only corpus-wide claims here.
2. **One auditor on the meaning verdicts, and a reviewer who disagrees with
   nine of them.** The verdicts in `verdicts.tsv` are this session's; the
   mandated independent check is pending (§10), and the supplementary reviewer
   graded nine `faithful` that this report does not (§9a). This report argues
   those nine are unaddressed rather than refuted, but that is the auditor
   marking its own homework — a reader who wants one number should treat the
   30 rows as **21 undisputed and 9 contested** until Astra rules. Six rows
   carry medium confidence for the ordinary reason (R06, R12, R19, R25, R29,
   R30).
3. **The citations were not checked against their sources.** R30's verdict
   («напал на них» for *kam über sie*) is stated with its refutation criterion
   — read the cited passage — precisely because that check was not run.
4. **German-side correctness is assumed.** Whether PWG's own German gloss is
   right about the Sanskrit is a different question and outside this mint.
5. **The five strata are not the only interesting ones.** Records whose
   Russian is byte-identical to the German (151 of 2392) are excluded by the
   eligibility rule, since a record asserting nothing in Russian cannot be
   audited for source support. They may deserve their own pass.

## 13. Reproduce everything

```bash
python src/h5069_source_support_audit.py selftest
```

```bash
python src/h5069_source_support_audit.py census
```

```bash
python src/h5069_source_support_audit.py verify
```

```bash
python src/h5069_source_support_audit.py poolcheck
```

```bash
python src/h5069_source_support_audit.py show --stratum compound
```

Tool:
[`src/h5069_source_support_audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/h5069_source_support_audit.py)
· control spec:
[`src/h5069_controls_spec.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/h5069_controls_spec.json)
· regression test:
[`tests/test_h5069_source_support_audit.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/tests/test_h5069_source_support_audit.py).

_Гасунс_
