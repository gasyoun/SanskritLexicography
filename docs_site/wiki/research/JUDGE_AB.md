# Judge A/B — Opus vs Sonnet as the QA judge model (battleground, 2026-06-24)

**Question.** The scale-up's main path uses an **Opus** QA judge (per the pilot). A **Sonnet**
judge would roughly halve the API-reference cost of the top-500 batch ($277 → $143, since the
judges are ~$167 of the $277 — see [`PILOT_COST.md` §7](RussianTranslation/PILOT_COST.md)). But cheaper is only
acceptable if a Sonnet judge **agrees with Opus on real cards** and, critically, **catches the
defects Opus catches**. This is that empirical test, run before committing the longer run.

## Method (real battleground)

- **Cards:** 5 already-translated real PWG cards spanning the prior pipeline's severities
  (`akz` 4, `aMSu` 3, `akzan` 2, `akzi` 1, `aMSa` 1) + **2 planted-defect** variants to test
  detection power (the 5 clean cards alone can't show whether a judge *catches* errors):
  - `aMSa_PLANT_gloss` — 3 Russian glosses reverted to untranslated German
    (`{%Theil, Abschnitt%}`, `{%Erbschaftsantheil%}`, `{%Nenner eines Bruchs%}`).
  - `aMSu_PLANT_coverage` — back ~50 % of the translation truncated (senses 3–7 dropped).
- **Arms:** each card judged by an **Opus** agent and a **Sonnet** agent given the *identical*
  `(body_de, body_ru)` pair and the same PWG rubric (German gloss → Russian, Latin/English kept
  verbatim, sigla/markup as anchors, coverage, register). One-line JSON verdict per run.
- **Apples-to-apples:** both models see the same input, so the *relative* comparison is valid
  even though this ad-hoc rubric is simpler than the production judge (see caveats).

## Results

| card | prior sev | Opus-judge | Sonnet-judge | verdict agree | sev Δ |
|---|---|---|---|---|---|
| `akz` | 4 | ok, 2 | ok, 1 | ✓ | 1 |
| `aMSu` | 3 | ok, 1 | ok, 2 | ✓ | 1 |
| `akzan` | 2 | ok, 2 | ok, 2 | ✓ | 0 |
| `akzi` | 1 | ok, 1 | ok, 1 | ✓ | 0 |
| `aMSa` | 1 | ok, 1 | ok, 1 | ✓ | 0 |
| `aMSa_PLANT_gloss` | — | **BAD, 4** (named all 3 glosses) | **BAD, 5** (named all 3) | ✓ | 1 |
| `aMSu_PLANT_coverage` | — | **BAD, 5** (senses 3–7 dropped) | **BAD, 5** (senses 3–7 dropped) | ✓ | 0 |

**Metrics:** OK/BAD verdict agreement **7/7 (100 %)** · severity exact 4/7, **within ±1 on 7/7** ·
**Sonnet false-clears = 0** (Sonnet never passed a card Opus flagged BAD) · **both planted
defects caught by both models**, each naming the exact errors. On the clean cards both flagged
the same minor issue (stray German connectives `und`/`oder`/`u.s.w.`).

## Reading

On this battleground a **Sonnet judge matched an Opus judge on every card** — same verdict,
severity within one point, identical defect identification including the untranslated-gloss and
the dropped-senses traps. No evidence here that Sonnet misses what Opus catches. So the
~$134 (48 %) saving on the top-500 looks **achievable** — *pending a larger, production-faithful
validation* (below). This evidence does **not** by itself flip the default: per the editorial
call, **Opus judges remain the main path**; Sonnet is a validated-promising **alternative**.

## Caveats (why this is a probe, not the verdict)

1. **Small N (7).** Seven cards, two of them synthetic. A handful of agreements is encouraging,
   not conclusive.
2. **Ad-hoc rubric ≠ production judge.** This used a condensed single-judge rubric on *unmasked*
   input; production runs the locked [`2_qa_sudya_opus.txt`](../pwg_ru_prompts/2_qa_sudya_opus.txt)
   on `{Tn}`-masked pairs, as a **two-judge** panel (Opus + YandexGPT). The real question is
   whether the *production* Sonnet judge holds up.
3. **Infra flakiness.** Two Opus agent runs failed to read the `/tmp` data file (sandbox path
   resolution); re-running inline worked. Orchestrating the larger run should pass data inline or
   via a repo-relative path, not `/tmp`.

## Recommendation / next step before the longer run

- **Keep Opus judges as the main path** (default `--judge-model opus`).
- **Validate Sonnet at larger N through the real pipeline** before trusting it for the bulk:
  ≥30 cards, ~30 % carrying real or planted defects, judged by `judge=opus` vs `judge=sonnet`
  through the production harness. **Adopt Sonnet for the bulk only if** verdict-agreement κ ≥ 0.7
  **and** Sonnet false-clear rate on Opus-sev≥3 ≈ 0.
- **Hedge regardless:** even if Sonnet judges the bulk, keep **Opus for the repass of rejects**
  and for a judged **sample** — cheap insurance, small cost.
- Score any such run mechanically with [`src/judge_ab_score.py`](../src/judge_ab_score.py)
  (verdict agreement, severity Δ, Sonnet false-clears).

*This run's verdicts are recorded inline above rather than as data files (the agent runs were
one-offs); reproduce via the protocol in “Method”.*

---

## RUN 2 — POS-stratified scale-up (26 cards, 2026-06-24)

Addresses run 1's small-N. 26 already-translated cards stratified across **parts of speech**
(translations exist only for the **a-section**, so POS — not dictionary section — is the
diversity axis): **5 adjectives, 5 m-nouns, 4 f-nouns, 4 n-nouns, 3 indeclinables, 3 verb
roots, 2 unmarked**. Each judged by an Opus and a Sonnet agent on identical inputs (batch
of ~6 per agent, reading the pairs file by absolute repo path — no `/tmp`). Verdicts:
[`judge_ab_run2_opus.jsonl`](judge_ab_run2_opus.jsonl) ·
[`judge_ab_run2_sonnet.jsonl`](judge_ab_run2_sonnet.jsonl), scored by
[`../src/judge_ab_score.py`](../src/judge_ab_score.py).

**Metrics:** BAD/not-BAD agreement **26/26, Cohen κ = 1.00** · severity exact 11/26, **within
±1 on 25/26** (lone Δ2 = `akzan`, both still OK) · **Sonnet false-clears = 0** · over-flags = 0.

**Natural defects found (not planted) — and both models caught them.** 2 of 26 cards came back
severity-5 `wrong_entry` from **both** judges: `aMSa` (the Russian body is the *shoulder*
homonym, but body_de is `a/MSa` "part/share") and `aMh` (Russian is homonym #2 "speak/shine",
body_de is #1 "go"). This is a real **homonym-pairing bug in the legacy `pwg_ru_translated`
set** (~8 % of this sample) — surfaced as a by-product, worth a separate fix pass. For the A/B
it matters that the Sonnet judge flagged both at sev 5, identical to Opus.

**Combined (run 1 + run 2 = 33 cards, 7 POS classes):** Opus and Sonnet agree on **every**
BAD/not-BAD call (κ = 1.0), **zero** Sonnet false-clears, and **every defect caught** (2 planted
+ 2 natural). Disagreement is confined to ±1 severity granularity on clean cards.

**Recommendation (updated).** Default unchanged — **Opus is the main path**. The Sonnet judge
now has materially stronger support (33 cards, POS-diverse, no false-clears), so the
~$134/top-500 (Max-quota) saving looks robust. The *only* remaining gate before adopting Sonnet
for the bulk is **production fidelity**: re-run through the real masked, two-judge pipeline (and,
once non-a-section translations exist, across more of the alphabet), scored by the same rule
(κ ≥ 0.7, 0 false-clears). The ad-hoc-rubric / unmasked-input caveat from run 1 still applies.

---

## RUN 3 — full a-section audit, 201 cards (2026-06-24, workflow `judge-ab-201`)

Ran the **entire** translated a-section through both judges as a background workflow (21
chunks × Opus + Sonnet = 42 batch-judge agents, deterministic scoring). Verdicts:
[`judge_ab_run3_opus.jsonl`](judge_ab_run3_opus.jsonl) ·
[`judge_ab_run3_sonnet.jsonl`](judge_ab_run3_sonnet.jsonl). One Opus chunk (10 cards
`akanizWa`…`akartana`) died on an API 500, so **191/201 cards have both verdicts**.

### A/B result (the valid conclusion) — holds decisively at scale

| metric | value |
|---|---|
| BAD/not-BAD agreement | **191/191 — Cohen κ = 1.00** |
| severity exact / within ±1 | 114/191 / **190/191** (lone Δ2 = `aMhasaspati`, both still OK) |
| **Sonnet false-clears** | **0** |
| over-flags / verdict disagreements | **0 / 0** |

Across **224 cards total** (runs 1–3, 7 POS classes) Opus and Sonnet have **never disagreed on
a single accept/reject call** and Sonnet has **never once false-cleared** a card Opus flagged.
The model choice is settled on this evidence; only production-pipeline fidelity remains to test.

### Audit result — and an honest correction to my own harness

The raw run flagged **14/191 cards (7%)** as severity-5, **13 of them `wrong_entry`** (Russian
body describes a *different homonym* than the German). That looked like a systemic translation
bug — **but it is mostly an artifact of MY pairing harness, not the data.** `pwg_ru_translated.jsonl`
has **14 keys with multiple homonym rows**; my extractor joined each `key1`'s *first* PWG German
record to the *last* homonym's Russian (dedup by bare `key1`), guaranteeing a cross-homonym
mismatch. **13 of the 14 flagged cards are exactly those 14 multi-homonym keys** — so the judges
correctly detected a mismatch *I* created.

Corrected reading:
- Of the **178 correctly-paired (single-homonym) cards, exactly one** was flagged — `akzamA`,
  for a **single stray untranslated connective** "im" (→ "в"); Opus sev 2, Sonnet sev 3, and run 2
  had judged the same card clean. A borderline minor, not a substantive defect.
- So the **legacy a-section translations are clean** at the substantive level (≈0 real defects in
  178 correctly-paired cards); there is **no 7% defect rate**.

### Two real findings (beyond the A/B)

1. **The judge is a reliable homonym-mismatch detector.** Both models flagged all 13 crossed-
   homonym pairs at sev 5 with the exact diagnosis — a useful standing QA guardrail.
2. **Pipeline lesson: pair `de`↔`ru` by homonym, never by bare `key1`.** Joining on `key1` alone
   silently crosses homonyms (the bug my harness hit). Any merge/QA step must key on
   `key2`/`hom`/`ord`. This is the actionable takeaway for the scale-up wiring.

*Caveat: run-3 verdicts are valid as judge-**agreement** data but NOT as a translation-defect
inventory — 13 of the BAD calls reflect harness mis-pairing, flagged via `mispaired_homonym:true`
in the verdict files. A clean defect audit needs homonym-correct pairing (done below).*

### RUN 3b — homonym-CORRECT re-pairing of the 14 flagged keys (resolves the artifact)

Re-paired every Russian row of the 14 multi-homonym keys to its **own** German homonym (matched
by `key2`; 30 rows, 0 unmatched) and re-judged with the main-path **Opus** judge. Verdicts:
[`judge_ab_homonym_opus.jsonl`](judge_ab_homonym_opus.jsonl).

**Result: 28/29 rows clean** (the 30th, `akzarapaNkti~h2`, wasn't returned — agent slip, not a
defect). When each homonym's Russian is matched to its own German, the previously "catastrophic"
cards are fine — e.g. `aMSa~h1` (Theil↔часть) and `aMSa~h2` (Schulter↔плечо) both clean;
likewise `aMh~h1`/`~h2`, `aMhati~h1`/`~h2`, `aMsa~h1`/`~h2`, etc.

The **only** residual flag is `a~h3` — the headword `a`, whose every homonym shares `key2="a"`,
so key2-matching can't disambiguate and the order-fallback mispaired it. That is a pairing
edge-case of the most-polysemous headword, **not** a confirmed translation defect (it would need
manual homonym mapping for `a`).

---

## RUN 4 — ground-truth POWER test: does Opus catch subtle defects Sonnet misses? (2026-06-25)

Runs 1–3 mostly judged *clean* cards, so agreement was partly "both agree it's fine." To test
**discriminating power** I built a **250-item battery with known ground truth** (workflow
`judge-ab-battery`): from the 178 clean single-homonym cards I planted exactly one *subtle*
defect per card and kept controls —

| ground truth | category | n |
|---|---|---|
| **BAD** | anchor-drop (one `{#…#}` removed) | 90 |
| **BAD** | sigla-alter (one `<ls>` source falsified, e.g. RV→AV) | 40 |
| **BAD** | drop-sense (one `<div>` sub-sense removed) | 36 |
| **BAD** | latin-translated (a binomial wrongly Russified) | 6 |
| **BAD** | numeral-drift (a number inside a gloss changed) | 2 |
| **OK** | clean control (unmutated) | 70 |
| **OK** | latin-kept decoy (binomial correctly verbatim — false-positive trap) | 6 |

Both judges scored the **blinded** battery (no ground-truth fields visible). The API was
unstable (two passes + a resume; transient connection-closed/403 errors), so **Opus judged 239,
Sonnet 209**. Verdicts: [`judge_ab_battery_opus.jsonl`](judge_ab_battery_opus.jsonl) ·
[`judge_ab_battery_sonnet.jsonl`](judge_ab_battery_sonnet.jsonl).

### Result — a statistical tie

| | Opus | Sonnet |
|---|---|---|
| defect **recall** | **163/164 = 99 %** | **143/144 = 99 %** |
| false-positives on the 76 OK items | **0 %** | **0 %** |
| accuracy, head-to-head (209 shared) | **208/209** | **208/209** |

Per category both scored ~100 % recall (anchor-drop, sigla-alter, drop-sense, latin-translated,
numeral-drift). **Each missed exactly one — different — card** (Opus missed `anchordrop~akava`;
Sonnet missed `dropsense~aga`). The "Opus edge" and "Sonnet edge" are **1 card apiece**. Neither
model false-flagged a single clean card or Latin-kept decoy.

### Answer to "is Sonnet enough, or does Opus have power Sonnet lacks?"

**For the QA-judge job, Sonnet = Opus.** On 200+ subtle defects with ground truth, the cheaper
model matched the reference at 99 % recall / 0 % false-positives, with a 1-vs-1 wash on the only
misses. There is **no detectable Opus power advantage** for the mechanical core of judging
(gloss translated? anchors intact? citations faithful? coverage complete? Latin kept?).

**Honest scope.** These defects are *structural/mechanical* (anchors, citations, coverage,
Latin, numbers) — clean ground truth, but they test **vigilance**, not deep **semantic**
discrimination. The one category I could not auto-generate with reliable ground truth is the
**plausible-but-wrong gloss** (a correct-looking but semantically wrong Russian rendering) — the
likeliest place a weaker judge could slip. That remains the single open question; testing it
needs an LLM-generated defect set with verified ground truth. Subject to that caveat, the
evidence now strongly supports **Sonnet as the bulk judge** (the ~$134/top-500 Max-quota saving),
with Opus kept for the repass and a periodic audited sample.

---

## Conclusion of the full audit

**The legacy a-section translations are clean**: across 178
single-homonym cards (run 3) only one borderline minor (`akzamA`'s stray "im"), and across the 30
re-paired homonym rows 28/29 clean with the lone `a~h3` flag being a pairing edge-case. **There is
no systemic translation defect; the "7 % wrong_entry" was 100 % a harness pairing artifact.** The
two durable findings stand: the judge reliably catches homonym mismatches, and the pipeline must
pair `de`↔`ru` by homonym (`key2`/`hom`) — and for the all-`key2`-identical headword `a`, by an
explicit homonym index, since `key2` alone is insufficient there.

---

## Run 5 — the semantic question, and why we stopped synthesizing defects (2026-06-25)

Runs 1–4 settled **vigilance** (mechanical/structural defects): Sonnet = Opus. The open
question was deep **semantic** judgment — a *plausible-but-wrong gloss*. I attempted a synthetic
battery (Opus generates one wrong-but-related / antonym / register-drift gloss per card, editor
verifies ground truth). **Abandoned on the editor's objection, which is correct:**

> A one-word gloss pair (`Theil` → часть vs доля, `Strahl` → луч vs свет) is **undecidable in
> isolation.** Both the German and the Russian word are polysemous; deciding which is right needs
> the **whole entry plus the Sanskrit sense in that passage**. The cases decidable by eye are the
> *rude* ones — which Sonnet already catches (run 4). So a planted "subtle defect" has a
> contestable ground truth and tests nothing real.

**The honest gate instead: mine real Opus-vs-Sonnet disagreements in production.** Both judges
score every card; the editor adjudicates **only** the cards where they disagree, each shown with
the complete German + Russian entry (real context, the editor is ground truth). Tooled by
[`../src/judge_disagreements.py`](../src/judge_disagreements.py).

**Already near-conclusive on the data we have:** `judge_disagreements.py` finds **0 conflicts in
run 3 (191 real a-section cards)** and **2 in run 4 (209)** — a ~0.5 % rate. The adjudication
queue is essentially empty; the two models almost never disagree, so there is barely anything
left for a human to decide. No hidden Opus advantage surfaces as a backlog of disagreements.

**Final decision** (see [`JUDGE_POLICY.md`](JUDGE_POLICY.md)): **Sonnet for the bulk judge, Opus
for the reject-repass + a ~5 % audited sample.** The semantic gate is a *standing production
check*, not a blocker — let `judge_disagreements.py` surface the rare conflicts each batch, and
revisit only if that rate climbs. **Methodological lesson worth keeping: do not build a synthetic
test whose ground truth you cannot defend; for translation correctness the only honest ground
truth is the entry in full context, adjudicated by the editor on genuine disagreements.**
