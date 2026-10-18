# User study protocol — learner's reading layer vs plain Cologne lookup (gap G7)

_Created: 24-09-2026 · Last updated: 24-09-2026_

Handoff [H5336](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5336-Opus_SanskritLexicography_learner-layer-user-study-protocol-g7_23.09.26.md) (Opus, 🟡2 medium), epic [E014](https://github.com/gasyoun/Uprava/blob/main/handoffs/epics/E014-atlas-fairpubs-wave-1.md). Closes gap **G7** of [ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md) ("no user-facing evaluation … Pedagogical-lexicography venues will ask"); feeds paper **P6** (*A frequency-graded reading layer for Sanskrit learners*, Lexikos / eLex 2027).

## 0. Status and scope — what this document is, and what it is not

**It is** the full study design, fixed in writing **before any data exists**: tasks, materials, measures, sample size with its reasoning, the analysis plan, and the personal-data regime. The analysis plan is additionally fixed **in code** — [`data/h5336_learner_study_power.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/h5336_learner_study_power.py) — so that "we decided the test after seeing the numbers" is not available to us later.

**It is not** recruitment. No participant is approached, no consent is collected, no student list is read, and no session is scheduled by this document or by the handoff that produced it. Running the study needs three things this protocol does not have: an MW sense index for the answer options (§11.2), a gold sense key (§4.4), and a human-approved Russian consent text (§9.3).

## 1. Research questions and hypotheses

The claim the roadmap makes and this study tests: **the learner's reading layer helps a learner arrive at the right dictionary sense of a word in a passage faster, and not less accurately, than the same learner using plain Cologne lookup.**

| # | Hypothesis | Direction | Primary outcome |
|---|---|---|---|
| H1 | Time-to-correct-sense is lower with the learner layer | directional, one fixed sign | log time per item |
| H2 | Sense-selection accuracy is not lower with the learner layer | non-inferiority, margin fixed in §8.3 | correct / incorrect per item |
| H3 | Self-reported ease is higher with the learner layer | directional | 5-point ease rating per item |

H1 is the confirmatory hypothesis; H2 is a guard against the obvious failure mode (a layer that is fast because it pushes a wrong, prominent sense); H3 is secondary. Everything else in §6 is exploratory and is reported as such — a nominal p-value on an exploratory measure is a description, not a test.

**What would refute the roadmap's claim:** a confidence interval on the time ratio that includes 1 with n at target (the layer does not help), or an accuracy loss beyond the §8.3 margin (the layer helps by making people wrong faster). Either outcome is publishable and is written up as such in P6 — that is why the outcome is pre-declared here.

## 2. Design

Within-subject (each participant works in both conditions), two conditions:

1. **Condition A — control.** Plain Cologne lookup: the Cologne Digital Sanskrit Dictionaries simple search, <https://www.sanskrit-lexicon.uni-koeln.de/simple/>, and the MW web interface <https://www.sanskrit-lexicon.uni-koeln.de/scans/MWScan/2020/web/webtc/indexcaller.php>. Both live-probed HTTP 200 on 24-09-2026; the pilot re-probes and pins the exact build, because an upstream interface change between pilot and main run is a confound, not a detail.
2. **Condition B — treatment.** The learner's reading layer as shipped in csl-atlas: the page [`src/tools/learner-reading-layer.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/tools/learner-reading-layer.md) over [`src/data/learner/learner-index.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/learner/learner-index.json) — probed 24-09-2026: **52,934 lemma records**, generated 2026-06-13, CC-BY-SA-4.0, each record carrying the DCS frequency band, attestation flag, cross-dictionary coverage over 7 dictionaries, a grammar-reliability count and a link out to csl-orig.

**What condition B does and does not contain, stated precisely, because the hypothesis depends on it.** The shipped record fields are `l, fb, at, c, gr, d, g, src` — a band and a routing decision. **There is no per-sense ranking in the shipped layer**; the survival-ranked senses the roadmap describes are the pending v2 piece ([H5317](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5317-Opus_csl-atlas_learner-layer-v1-card-and-join-spec_23.09.26.md) spec, [H5318](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5318-OxAlpha_csl-atlas_learner-layer-v1-dataset-build_23.09.26.md) build, [H5319](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5319-OxAlpha_csl-atlas_learner-layer-v1-public-page_23.09.26.md) page). So the study as specified here measures the **routing** benefit: does knowing the band and which of seven dictionaries to open get a learner to the right sense faster? If sense ranking ships before the run, it is a *different* condition B and this protocol's §1 wording changes with it — either way, **the exact commit sha of the layer under test is pinned in the results file and frozen for the whole run**, because a layer that improves mid-study is an uninterpretable study.

**Item counterbalancing is mandatory, by a 2-group Latin square.** Two matched item sets (§4.3); group 1 sees set 1 under A and set 2 under B, group 2 the reverse. Condition order is additionally counterbalanced within each group (A-first / B-first), giving four cells; assignment is by the participant code's position in a seeded random permutation, not by arrival order.

**Why the Latin square is a requirement and not a nicety — measured, not asserted.** The naive design (each condition gets its own items) was simulated under a true null: with 24 participants × 10 items, the by-participant test rejects a non-existent effect **45.8%** of the time, because the offset between two independently drawn item sets is common to every participant and is indistinguishable from a condition effect. Under the counterbalanced design the same test sits at **3.1%** against a nominal 5%. The selftest in the power tool asserts both numbers, so a future session cannot quietly drop the counterbalance:

```bash
python data/h5336_learner_study_power.py selftest
```

## 3. Participants

- **Source:** the review-pool students — the same cohort doing double-keyed review work ([H5307](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5307-Opus_csl-atlas_review-pool-v1-double-keying-design_23.09.26.md), [H5310](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5310-Fable_csl-atlas_review-pool-student-guide-ru_23.09.26.md)). The roadmap's own G7 mitigation names this cohort; using it is a design constraint, not a convenience.
- **Eligibility:** has completed at least one term of Sanskrit; can read Devanāgarī and IAST; has not worked on building the learner layer itself.
- **Exclusion, declared in advance:** anyone who saw the item list before the session; anyone who authored or adjudicated the gold key (§4.4).
- **A participant is never a subject of assessment.** Results are never fed back to teaching staff at the individual level and never affect a grade, a payment, or standing in the pool. This is stated in the consent text and is the reason §9 keeps the identity key out of the research data entirely.
- **Attrition:** a participant who stops mid-session contributes their completed items to the item-level models and is dropped from the by-participant fallback test; both numbers are reported.

## 4. Materials

### 4.1 Item frame — counted on our own data, not estimated

The sampling frame is the intersection of three live assets, printed by the tool (`frame` subcommand, run 24-09-2026):

| Fact | Value | Source |
|---|---|---|
| DCS lemma summary | 83,239 lemmas, `DCS-2021`, CC BY | [`VisualDCS/dcs_lemma_summary.json`](https://github.com/gasyoun/VisualDCS/blob/main/dcs_lemma_summary.json) |
| Band rule | 1 hapax(1) · 2 rare(2–9) · 3 uncommon(10–99) · 4 common(100–999) · 5 very-common(1000+) | same file, `bandingRule` |
| Band sizes | 35,693 / 29,453 / 13,276 / 4,112 / 705 | same file |
| H5330 typology pool | 2,100 rows, 2,081 distinct `k1` over 7 dictionaries | [`data/definition_typology_pool_300x7_manifest.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/definition_typology_pool_300x7_manifest.tsv) |
| Pool ∩ DCS-attested | 853 keys (bands 1–5: 180 / 268 / 240 / 132 / 33) | computed |
| Band-eligible (bands 3–5) | 405 | computed |
| Learner layer coverage | 52,934 lemma records, generated 2026-06-13 | [`csl-atlas/src/data/learner/learner-index.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/learner/learner-index.json) |
| **Eligible items (band-eligible ∧ has a learner card)** | **360** | computed |

Two exclusions, both by rule and both applied before any selection. Bands 1–2 go because a lemma the corpus attests once or twice has no reading context to disambiguate in, so a "find the right sense" task over it measures guessing. Then 45 of the remaining 405 go because they have **no record in the learner index** — condition B would show an empty card, which is not a comparison of two interfaces but a comparison of one interface with nothing. The 360 that survive, against a need of 20 items (§5), is a comfortable margin, which matters because §4.4 will discard more.

### 4.2 Item selection rule (fixed before selection)

From the 405 eligible keys, keep only lemmas that are **genuinely polysemous in MW** (≥ 3 distinct numbered senses) — an item with two senses is a coin flip and wastes a participant's time. Then draw a stratified sample, seeded (`5336`) and reproducible: bands 3 / 4 / 5 in proportion **10 / 8 / 2** per 20 items. The weights follow availability, not a preference for rarity — band 5 holds only 705 lemmas corpus-wide and 33 in the pool, so it cannot carry a quarter of the items without the same few words appearing in every session, while band 3 ("uncommon", 10–99 occurrences) is both the largest eligible stratum and the band where a learner plausibly needs help at all: a band-5 word is one they already know. Draw two matched sets of 10 (set 1, set 2) balanced on band and on MW sense count. The draw script is written once the polysemy counts exist (it depends on an MW sense index the learner layer build produces); its output is a committed manifest of **item ids only, never dictionary text** — the never-commit-csl-orig fence applies here exactly as it does to the H5330 sheets.

### 4.3 Reading contexts

Each item is a **short passage plus a highlighted token**, not a bare headword: the task is sense selection in context, which is what a learner does and what plain lookup is bad at. Passages come from [`VisualDCS/passage_library.json`](https://github.com/gasyoun/VisualDCS/blob/main/passage_library.json) — 40 curated passages carrying `genre`, a difficulty rating `diff` and a vocabulary-difficulty score `vd` (probed 24-09-2026) — with DCS itself as the fallback source when no library passage contains the item's lemma. Passage difficulty is balanced across the two item sets and reported; it is not a covariate of interest.

### 4.4 Gold sense key — double-keyed, adjudicated, and allowed to discard items

The correct sense for each item-in-context is assigned **independently by two annotators** (the pool's existing double-keying discipline, [H5307](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5307-Opus_csl-atlas_review-pool-v1-double-keying-design_23.09.26.md)), never by the layer's own ranking — otherwise the study would be scoring the layer against itself. Agreement is reported as Cohen's κ using the pool's existing κ tool ([H5309](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5309-OxAlpha_csl-atlas_review-pool-kappa-report-tool_23.09.26.md)). Disagreements go to one adjudicator; **an item that survives adjudication only as "either sense is defensible" is dropped from the study**, before any participant sees anything. If fewer than 20 items survive, the frame is re-drawn — not the threshold lowered.

## 5. Task and procedure

One session, ~45 minutes, remote, screen-shared or instrumented in the browser:

1. **Consent** (§9), then the participant code is read out to them; no name is typed into anything used by the study.
2. **Instructions + 2 practice items per condition**, not analysed, present only so that the first real item is not a tutorial.
3. **Block 1 (10 items)** in the participant's first condition, then a 2-minute break, then **block 2 (10 items)** in the other condition. Item order within a block is randomised per participant.
4. **Per item:** the passage and the highlighted token appear; the timer starts on first display; the participant uses only the condition's resource; they select one sense from the item's numbered MW sense list; they rate ease 1–5; the timer stops on submission. **Timeout 180 s**, recorded as a timeout with the response given (or none) — timeouts are not silently dropped (§8.4).
5. **Post-block question** (one sentence, free text, optional): what was hardest. Free text is screened per §9.4 before it goes anywhere.
6. **Debrief**, including which condition was which, and the withdrawal reminder.

The facilitator runs a fixed script and does not help with the task. Sessions are **not recorded** — no audio, no video, no screen capture; see §9.2 for why that is a design decision rather than a convenience.

## 6. Measures

**Primary.** Time-to-correct-sense per item, in milliseconds, analysed on the log scale (task times are right-skewed; the log makes the condition effect a ratio, which is also the quantity a paper can state plainly: "median 22% faster").

**Secondary.** (1) Sense-selection accuracy against the §4.4 gold key, per item. (2) Ease rating 1–5, per item. (3) Number of lookups/clicks made before answering, where the instrumentation can count them without recording content.

**Exploratory.** Time by frequency band; accuracy by MW sense count; order effects (block 1 vs block 2); passage difficulty interaction; first-item-of-block cost.

**Not collected, deliberately:** free-text search queries typed into Cologne, keystroke streams, screen or audio recording, IP addresses, browser fingerprints, anything about a participant's coursework or grades. Each of these would either be personal data under §9 or would create a re-identification path in a sample of ~24 people from a known cohort.

## 7. Sample size and its reasoning

Computed, not asserted — `python data/h5336_learner_study_power.py power` (α = 0.05 two-sided, power 0.80, run 24-09-2026):

**Analytic, by-participant paired t:** d = 0.4 → 52 participants · d = 0.5 → 34 · **d = 0.6 → 24** · d = 0.8 → 15.

**Monte-Carlo, crossed participants × items** (2,000 sims, seed 5336, variance components sd_participant 0.35 / sd_item 0.30 / sd_residual 0.45 / sd_slope 0.15, analysed with the conservative by-participant test — so these are floors for the mixed model):

| n | items/condition | β (log) | time ratio | power |
|---|---|---|---|---|
| 16 | 10 | −0.18 | 0.84 | 0.68 |
| 16 | 10 | −0.25 | 0.78 | 0.93 |
| 20 | 10 | −0.18 | 0.84 | 0.80 |
| 24 | 10 | −0.18 | 0.84 | 0.86 |
| 24 | 10 | −0.25 | 0.78 | 0.99 |
| 30 | 10 | −0.18 | 0.84 | 0.94 |

**Target: n = 24 (12 per Latin-square group), 10 items per condition, 480 item observations.** The reasoning, stated so a referee can disagree with it: a 16% time reduction (ratio 0.84) is the smallest effect worth claiming for a reading aid — below that, a learner will not notice it and no venue should care — and n = 24 buys 0.86 power against it under the conservative analysis. n = 24 is also inside what the review pool can plausibly supply, which is the real constraint; if the pool yields fewer than 16, the study is reported as a **pilot with descriptive statistics and no confirmatory test**, not as an underpowered test (§8.6).

**Pilot first: 6 participants**, whose data re-estimate the variance components and are **not** pooled into the main analysis. If the pilot's residual SD exceeds 0.60 on the log scale, n is recomputed from the pilot's own numbers before the main run, and the recomputation is recorded in this file with its date.

## 8. Analysis plan — written before the data exists

### 8.1 Primary
Mixed-effects model on log time: `log_time ~ condition + block + (1 + condition | participant) + (1 | item)`, restricted to **correct** responses (H1 is about time to the *right* sense). Condition effect reported as a ratio with a 95% CI. If the maximal random-effects structure fails to converge, the pre-declared fallback ladder is: drop the correlation term, then the random slope, then — only then — the by-participant paired t used in the power simulation. The ladder is fixed here so that "the model that converged" cannot become "the model that was significant".

### 8.2 Secondary
Accuracy: mixed logistic `correct ~ condition + block + (1 | participant) + (1 | item)`. Ease: ordinal mixed model, or by-participant means with a paired test if it fails to converge.

### 8.3 Non-inferiority margin for accuracy
H2 is declared non-inferior if the lower bound of the 95% CI on the accuracy difference (layer − control) is **above −0.07** (7 percentage points). The margin is a judgment, and it is written down before the data so it cannot be adjusted afterwards: a reading aid that costs more than 7 points of sense accuracy is not worth a speed gain.

**H2 is under-powered at n = 24 and is reported as a bound, not as a demonstration of equivalence.** The sample size in §7 is chosen for H1; a non-inferiority test on a proportion at this margin would need substantially more participants, and inflating n for it is not worth the pool's time. So the write-up states the accuracy difference with its CI and says plainly what the interval does and does not exclude. What H2 can still do at this n — and the reason it is kept — is catch a *large* accuracy loss, which is the failure mode that would matter.

### 8.4 Exclusions and missing data
Fixed in advance: (a) practice items excluded; (b) timeouts kept, and analysed as incorrect for accuracy, censored at 180 s for time — plus one sensitivity analysis with timeouts dropped, reported whatever it shows; (c) items dropped at adjudication (§4.4) never enter; (d) no per-observation outlier deletion by eye — the log scale plus the mixed model handles skew, and any trimming rule, if introduced at all, is applied identically to both conditions and named in the write-up.

### 8.5 Multiplicity
One confirmatory test (H1). H2 and H3 are secondary and reported with Holm correction across the two. Exploratory measures carry no inferential claim.

### 8.6 Stopping and interpretation
Data collection stops at n = 24 or when the pool is exhausted, whichever comes first — **never when the p-value looks good**; no interim inferential peek is taken. A null result is reported as a null result, with the CI, and P6 states what the study can and cannot rule out.

### 8.7 Reproduction
Analysis code and the de-identified item-level data (§9.5) are published with P6 so the numbers can be recomputed. The pre-data version of this protocol is its git history in this repo — the commit that introduced this file is the timestamp.

## 9. Personal data — 152-ФЗ regime

The controlling constraint: **no participant name, e-mail, phone, handle, or any other identifier reaches any repository, ever** — public or private, committed or gitignored. The design below makes that structurally true rather than a rule someone must remember.

### 9.1 What is processed, and where
- **Research data** (what lands in a repo): participant **code** (`P01`…`P24`), condition, block, item id, time in ms, selected sense, correctness, ease rating, coarse experience band. Contains no identifier.
- **Identity data** (what never lands in a repo): the name/contact of a person who agreed to take part, and the consent record itself. These live only in MG's own contact store outside `GitHub/`, exactly as the [stenogrammy hard deny](https://github.com/gasyoun/claude-config/blob/main/rules/tgrep-fast-search.md) treats the student corpus — no agent indexes, greps, or serves them.
- **The code↔person mapping** is generated once, held with the identity data, and is **not** needed to analyse the study. It exists only so a participant can exercise withdrawal (§9.6). Codes are assigned from a shuffled list, so `P01` carries no information about who enrolled first.

### 9.2 Why there are no recordings
A screen or audio recording of a session is personal data (a voice is an identifier), it would need separate consent and a storage regime, and it would create exactly the artifact that must never be committed. Everything the study needs — times, choices, ratings — is captured as structured fields. This is the same reasoning that keeps the oral corpus out of every index in this estate.

### 9.3 Consent
Written (electronic) informed consent in **Russian**, obtained before the session, naming: the operator (MG, as the person responsible for the processing), the purpose (evaluating a dictionary interface for a research publication), the exhaustive list of data processed, that participation is voluntary and refusal costs nothing, that results are published **only in aggregate**, the retention period (§9.5), and how to withdraw (§9.6). **A human must review and approve the consent text before the first participant is approached** — an agent drafts it, an agent does not approve it; that is the §13 decision, and it is a genuine blocker on running the study, not on this protocol.

### 9.4 Free text
The one optional free-text field (§5.6) is screened before storage: any name, contact, or identifying detail a participant happens to write is removed at intake, and the screened text is stored under the code. If a response cannot be screened without destroying its meaning, it is discarded.

### 9.5 Retention and publication
- Identity data and the mapping: deleted **within 30 days of the last session**, or immediately after the withdrawal window closes, whichever is later. After deletion the research data is irreversibly pseudonymous.
- Research data: retained and published de-identified alongside P6, because a reproducible study is the point.
- **Aggregate-only reporting, with a floor:** no cell of any published table may describe fewer than 5 participants. In a sample of ~24 drawn from a known cohort, a table like "students in year 3, female, n = 2" re-identifies people; coarse bands (experience: <1 year / 1–3 years / >3 years) are used, and no demographic beyond that band is collected at all.
- Before anything from this study is published, it goes through [`/publish-safety-check`](https://github.com/gasyoun/claude-config/blob/main/commands/publish-safety-check.md) with `personal_data` treated as a hard NO-GO, per the [HTML-links personal-data carve-out](https://github.com/gasyoun/claude-config/blob/main/rules/html-links-github-io.md).

### 9.6 Withdrawal
A participant may withdraw at any point up to **14 days after their session**, by contacting MG; their rows are deleted from the research data and their code is retired (never reused). Withdrawal after the mapping is deleted is impossible by construction — the consent text says so plainly, because a promise that cannot be kept is worse than a clear limit.

## 10. Ethics and fairness

No deception: participants are told that two interfaces are being compared, and which is which at debrief. Compensation, if any, is fixed in advance and paid regardless of performance or of withdrawal. Participation is not a course requirement and produces no individual feedback to anyone. The study evaluates an interface, not a person — and the instrument is built so that it *cannot* be repurposed into an assessment of a person, because the identity key is gone within 30 days.

## 11. Prerequisites — what must exist before the first session

1. **The version of the layer under test, frozen and pinned.** Probed 24-09-2026: the layer **already ships** (page + 52,934-record index, §2), so condition B exists today — this is not a blocker, it is a freeze obligation. Pin the csl-atlas commit sha in the results file before the first session and do not rebuild the index during the run. If [H5317](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5317-Opus_csl-atlas_learner-layer-v1-card-and-join-spec_23.09.26.md)/[H5318](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5318-OxAlpha_csl-atlas_learner-layer-v1-dataset-build_23.09.26.md)/[H5319](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5319-OxAlpha_csl-atlas_learner-layer-v1-public-page_23.09.26.md) add sense ranking first, run against that and say so — but pick one version and stay on it.
2. **An MW sense index** giving per-lemma numbered senses — needed for item polysemy filtering (§4.2) and for the answer options themselves. This is the one genuinely missing artifact: the shipped learner index carries no senses (§2), so the answer options for every item have to come from MW directly.
3. **The gold key** (§4.4), double-keyed and adjudicated.
4. **The Russian consent text, human-approved** (§9.3).
5. **The timing instrument**, with the measurement points of §5.4 and no content capture (§9.2).

## 12. Reproducing the numbers in this document

```bash
python data/h5336_learner_study_power.py selftest
python data/h5336_learner_study_power.py power
python data/h5336_learner_study_power.py frame
```

Run 24-09-2026: selftest PASS (`n(d=0.5)=34 n(d=0.6)=24 n(d=0.8)=15`, type-I 0.031 counterbalanced vs 0.458 uncounterbalanced); `frame` printed the 360 eligible items of §4.1. The `frame` command fails closed when any of its three inputs is absent — it never substitutes a remembered number.

## 13. For a human to decide

1. **Approve or rewrite the Russian consent text** once it is drafted (§9.3). *If you approve it:* recruitment can start as soon as the MW sense index and the gold key exist (§11.2–3) — the layer itself is already up — and P6 gets a real evaluation section. *If you do not:* the study cannot run at all — no consent, no session — and P6 ships with the G7 gap open, which is the thing Lexikos reviewers were expected to ask about.
2. **Confirm n = 24 as the target, or name a different one** (§7). *If you confirm:* the pool needs 24 volunteers plus 6 for the pilot. *If the pool cannot supply that:* say the realistic number now and the study is pre-declared a descriptive pilot, which is honest and still publishable — deciding this after the fact is what would not be.

_Гасунс_
