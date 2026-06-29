# PWG → Russian pilot — evolution timeline (failure-driven)

Purpose: a faithful, no-gloss record of how the PWG→Russian translation harness
got to its current shape — **including every fuckup**, what it cost, and the fix
that hardened against it. New operators should read this before assuming any gate
is "obviously" right: every gate exists because something broke without it.

Convention added 2026-06-29 (M.G.): **state the model tier at every step.** The
bulk translate runs on **Sonnet**; the deterministic audit gates use **no LLM**
(free Python); the LLM judge of a ~10% sample uses **Sonnet** (every sampled card)
with **Opus** re-judging only rejects. The harness `meta.description` saying
"Sonnet bulk-judged, Opus adjudicates" describes the *judge* design, NOT the
translate-only `run_pilot_wf.opt.js` body — that body is **Sonnet-only**.

---

## Failure ledger (the "F-series" and process fuckups)

| id | failure | symptom | root cause | fix (commit / date) |
|---|---|---|---|---|
| F-fabrication | model invented senses/sub-senses not in the German | extra "epic"/"vedic" senses, split/merged senses | LLM filling gaps from memory | HARD RULE 1 + anti-fabrication guard (`545d9dc`, 2026-06-17) |
| F-coverage | senses silently dropped | not every 1)/2)/a)/b) rendered | long cards truncated | HARD RULE 2 coverage gate; `coverage` audit gate |
| F-sigla | sigla / abbrevs translated | ṚV./MBH./m./f./Bed. rendered into Russian | model "helpfully" translating tokens | HARD RULE 3 + sigla guard (`545d9dc`) |
| F-nachträge | addenda/Nachträge dropped or summarised | patch-records (`+ citation`, `read X instead`) missing | treated as repeats of main entry | Nachträge guard + HARD RULE 4 (`1bb1ec1`, 2026-06-17) |
| **F10** | input filename case-collision | `a` vs `A`, `as` vs `As` overwrote each other on Windows' case-insensitive FS | naïve `safeName` mapping | case-collision-safe filenames (`38a8905`, 2026-06-19); head sense-tag drift re-fix (`56e5025`, 2026-06-27) |
| **F12** | NWS owner mis-attribution ("Kleines Zitat" off-by-one) | owner citation slid onto the *next* gloss → wrong dictionary credited | reading direction: owner comes AFTER gloss, code read it before | Guard 6 + owner-map feed that kills F12 *by construction* (`4ace354`→`7a9d0f3`, 2026-06-18/23) |
| F-guard7 | multilingual NWS glosses relayed through German | de/fr/en gloss all funneled as German | CONV assumed German-only NWS layer | Guard 7: translate each gloss from its own language (`5ca74d2`, 2026-06-23) |
| F-evidence-blind | "evidence-blind giants" | huge root cards translated with no corpus evidence | root entry treated as one card | root-split sub-cards + Apresjan corpus evidence per sub-card (`611bdc6`, 2026-06-24) |
| F-caus-kind | secondary (caus/desid) sub-cards lost their kind/label | derivational stems mislabeled | root-split dropped sub-card kind | preserve caus/desid kind+label (`96112bd`, 2026-06-24) |
| F-fidelity | markup-stripping fidelity fail | `{#…#}` Sanskrit + `<ls>` citations stripped/transliterated | model "cleaned" markup | verbatim `{#}`/`<ls>` retention gate; reject if >15% `{#}` or >10% `<ls>` lost (`c69ac30`, 2026-06-27) |
| F-stale-doc | planning/runbook docs described an old pipeline | operators followed dead instructions | docs not updated with code | stale-doc cleanups (`60b6ca3` 2026-06-26, `398a999` 2026-06-28) |
| F-stale-output | stale `wf_output.json` used as evidence | "done" claimed from a previous run's JSON | reused artifact across runs | handoff non-negotiable: never use stale `wf_output.json`; root-scoped output only (2026-06-28/29) |
| F-token-blowup | ~10M tokens for ONE root | quota burned in 3–4 days | per-card Opus judging + full multi-turn | BALANCED translate-only harness (Sonnet, single-turn, inlined inputs, 1 retry); free Python gates replace per-card LLM judge (`ce7a1dd`, 2026-06-27) |
| F-nonascii-root | `gen_opt_harness` rootmap lookup failed for non-ASCII roots | harness couldn't generate for some roots | ASCII-only key assumption | rootmap lookup fix (`f450d10`, 2026-06-27) |
| **F-harness-size-limit** | 204-card root harness too big to launch | `i` harness = 567 KB > Workflow 512 KB `scriptPath` cap | inlined raw+portrait inputs scale with card count | split root into 2 sub-windows via `gen_opt_harness.py i body --keys=...`, run each (~280–316 KB), reassemble into one root-scoped `wf_output.json` for a single `i` audit (2026-06-29) |
| **F-gate-nws-fp** | requeue loop chases a gate false positive | `suspicious_attested_without_text_signal` = 66% of risks, never clears, NWS `pw01` got *worse* on rerun (810→1430) | `has_text_signal()` counts only literary sigla (`<ls`/ṚV/MBH) + stratum, NOT NWS owner citations (MW/Graßmann/Geldner) | OPEN (2026-06-29) — see [`RUN_LOG.md`](RUN_LOG.md); fix gate or escalate real failers to Opus, don't re-loop Sonnet |

---

## Chronology

**2026-06-17 — pilot is born.** a-section harness: corpus-first translate +
Apresjan discrimination + judge (`490ade8`). Same day, the first three guards
(anti-fabrication / coverage / sigla) + first cost analysis (`545d9dc`), then the
Nachträge guard + locked prompt + density router (`1bb1ec1`). Model: translate +
judge both **Opus** at this stage.

**2026-06-18–19 — the filename/attribution bugs.** F12 (NWS off-by-one) first
patched (`4ace354`); F10 (case-collision filenames) fixed and full a-section
generated (`38a8905`); manifest-driven batches; NWS row-format encoded as HARD
RULE 5; **v0.0.3** deterministic preflight released.

**2026-06-20–23 — kill F12 by construction.** Release hardening gates; batch
gated on NWS attribution to reject F12 slides (`af9c333`); Guard 7 (multilingual
glosses); finally the **owner-map feed** that makes F12 impossible by construction
— `ās` went MISATTRIBUTION→CLEAN (`7a9d0f3`). Bulk handoff to Max workflow.

**2026-06-24 — root-split.** The "evidence-blind giants" fix: root entries split
into sub-cards, each carrying its own Apresjan corpus evidence (`611bdc6`);
caus/desid sub-card kind preserved (`96112bd`); freq 38-unit run translated/glued/
audited with the fidelity gate (`0fd1b87`).

**2026-06-26 — judge economics.** Opus judge pass: 37/38 publishable (`b9e27fb`).
Judge escalation policy adopted — **Sonnet judges every card, Opus re-judges ONLY
rejects** (sev≥3 / ok=false), A/B-validated κ=1.0 over 474 cards (`fde8c88`). The 4
judge-derived prompt nits baked into the locked translate prompt.

**2026-06-27 — token optimization (the big lever).** M.G.: "10M tokens for one
root is too much even in Sonnet mode." Response: the **BALANCED translate-only
optimized harness** — single-turn, inlined inputs, 1 retry, **Sonnet translate**,
and the per-card LLM judge replaced by **free Python deterministic gates**
(`audit_window.py`), with the LLM judge reserved for a ~10% sample. Tool-lock
(no file reads in-agent), head-lane lock (sense-split, anti-roaming, caus tagging,
dup guard), non-ASCII rootmap fix, F10 head sense-tag drift re-fixed.

**2026-06-28 — audit hardening + handoff discipline.** Workflow ops cleaned;
audit guardrails hardened; the non-negotiable rules written (no 10-root pushes,
no stale `wf_output.json`, root-scoped output, requeue keys stay root-scoped).

**2026-06-29 — first staged Max run under the new rules (this session).** See
[`RUN_LOG.md`](RUN_LOG.md). Stage A `sTA`, 123 cards, **Sonnet-only translate**.

---

## Standing lessons

1. **The description lies; grep the code.** `meta.description` advertises an
   Opus judge that the translate-only body never calls. Always confirm the actual
   `model:` per `agent()` call and report it.
2. **Every gate is a tombstone.** coverage←F-coverage, sigla←F-sigla,
   owner-map←F12, fidelity←F-fidelity, sense-dupes←head-roaming. Don't disable a
   gate without re-reading why it exists.
3. **Stale artifacts are the quiet killer.** Both stale docs and stale
   `wf_output.json` produced confident-but-wrong "done" claims. Date everything;
   scope output per root; re-derive, never reuse.
4. **Cost is a correctness constraint here.** The 10M-tokens/root blowup forced
   the translate-only + free-gates architecture. Tier matters: Sonnet for bulk,
   Opus only on the hard residue.
