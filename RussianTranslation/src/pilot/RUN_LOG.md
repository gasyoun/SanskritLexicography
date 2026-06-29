# PWG → Russian — Max run log

One block per Max run. **Record the model tier on every step** (Sonnet / Opus /
Haiku / none), not just runtime and tokens. Failures are logged, not hidden.
History of how the harness got here: [`EVOLUTION_TIMELINE.md`](EVOLUTION_TIMELINE.md).

---

## 2026-06-29 — Stage A: sTA

Operator: Claude Code Max. Handoff: [`../../HANDOFF_2026-06-29_claude_code_max.md`](../../HANDOFF_2026-06-29_claude_code_max.md).

### Round 1 — full window (123 cards)

| step | tool / model | result |
|---|---|---|
| pre-check | `root_window_status.py sTA` — **no LLM** | `stale_artifact`, 123/123 raw+portrait present, structurally ready (PASS) |
| translate | Workflow `run_pilot_wf.opt.js`, **123 × Sonnet** agents, 1 retry, tools:[] | 123/123 translated; no Opus spent |
| audit | `audit_window.py` — **no LLM** (deterministic gates) | **FAIL → needs_requeue** |

- Max wall-clock: **~22 min** (1,295,437 ms)
- Max total tokens: **4,170,022** · weekly cap fired: **no**
- Coverage: **119/123** (4 flagged: `ud`, `pratyupa`, `pari`, `vi`)
- Clean keys: **90** · Requeue: **33** · Judge sample: **42** (seed `c04c04593372f356`)
- Semantic risks: **571** across 51 keys; **61 high-confidence** (29 keys)
- Gate exits: coverage=1 (4), prompt_semantic=1 (29), nws=0, translation=1 (3), sense_dupes=0
- Dominant high-confidence risks: `untranslated_german_residue` /
  `untranslated_braced_german_gloss` (real defects — German left untranslated:
  `anu`, `sam`, `pwg11b03`); plus lower-confidence
  `suspicious_attested_without_text_signal` cluster on NWS cards `pw00–07`.

### Round 2 — requeue (33 cards)

| step | tool / model | result |
|---|---|---|
| requeue gen | `requeue_from_audit.py sTA` — **no LLM** | harness rescoped to 33 keys (CARDS=33, META.generated_at 2026-06-29) |
| translate | Workflow `run_pilot_wf.opt.js`, **33 × Sonnet** agents, 1 retry, tools:[] | 33/33 translated; no Opus spent |
| audit | `audit_window.py` — **no LLM** | **FAIL → needs_requeue** |

- Max wall-clock: **~9.8 min** (590,562 ms) · Max total tokens: **1,140,912** · cap fired: **no**
- Convergence: requeue **33 → 27** (only **6 cleared**); cumulative clean ≈ **96/123**
- Round-2 risk mix: 220 risks / 27 keys / 56 high-confidence

| rule | count | nature |
|---|---:|---|
| `suspicious_attested_without_text_signal` | 146 (66%) | **gate false positive on the NWS layer** (see finding below) |
| `untranslated_braced_german_gloss` | 17 | **real defect** — German left in braces: `{bleibe}`, `{eröffnen}`, `{sich halten an, streben nach}` |
| `untranslated_german_residue` | 37 | mixed — several fire on legitimately-kept `{#Sanskrit#}` quote spans |
| collapsed_synonym_string / likely_circular_gloss / other | ~20 | mixed, low volume |

### 🔴 Finding F-gate-nws-fp (2026-06-29) — the requeue loop chases a gate false positive

`suspicious_attested_without_text_signal` is the dominant flag (66% of round-2
risks; **80 on `pw01` alone**) and it **cannot be cleared by re-translation**.
Verified in source: [`prompt_rule_audit.py:321`](prompt_rule_audit.py) —
`has_text_signal()` returns true only for `TEXT_CITATION` (literary sigla: `<ls`,
ṚV, MBH, Manu, …) **or** a non-empty `stratum`. NWS **owner** citations
(`MW : 47`, `Graßmann 1873 (1996) : 70`, `Geldner 1907`) are NOT in `TEXT_CITATION`,
so any NWS sense the model (correctly) marks `source_type=attested` with only an
owner citation and no stratum fires this flag by construction. `pw01` scored
810→**1430** between runs — *worse* — purely from emit-noise, not regression.

**Consequence:** another identical Sonnet requeue pass would spend ~1M tokens to
clear, at best, a few real `untranslated_braced_german_gloss` cards while leaving
all 146 false positives untouched. The loop has hit diminishing returns.

**Real residual defects (fixable):** `untranslated_braced_german_gloss` on
citation-dense cards (`anu`, `sam`, `55_pra`, `zz_sch`, `15_ava`, `43_samud`).
These are a genuine **Sonnet ceiling** → candidates for the harness's
designed-but-unused **Opus** retranslate tier, or a targeted prompt fix — NOT a
repeat Sonnet pass.

**Decision surfaced to operator (do not auto-loop):**
1. Teach the gate to count NWS owner citations as a text signal (kills 146 FPs), **or**
2. Escalate only the ~6 real braced-gloss failers to an **Opus** retranslate, **or**
3. Accept current state (96/123 clean + documented FP) and proceed to Stage B `BU`.

No Opus has been spent on sTA in either round; the Opus LLM-judge of the judge
sample is still a separate, not-yet-run step.
