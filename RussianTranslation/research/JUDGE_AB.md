# Judge A/B — Opus vs Sonnet as the QA judge model (battleground, 2026-06-24)

**Question.** The scale-up's main path uses an **Opus** QA judge (per the pilot). A **Sonnet**
judge would roughly halve the API-reference cost of the top-500 batch ($277 → $143, since the
judges are ~$167 of the $277 — see [`PILOT_COST.md` §7](../PILOT_COST.md)). But cheaper is only
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
