# Protected slow-update field — DRAFT for approval (H388 @DECIDE)

_Created: 08-07-2026 · Last updated: 08-07-2026_

SkillOpt's optimizer **rewrites the translation skill document on its own**. The
rules below must never be auto-edited or deleted, so they sit inside the
`<!-- SLOW_UPDATE_START -->` / `<!-- SLOW_UPDATE_END -->` markers, which
[`Uprava/tools/skillopt/edits.py`](https://github.com/gasyoun/Uprava/blob/main/tools/skillopt/edits.py)
physically refuses to touch (`_touches_protected`). Only the epoch-wise
slow-update process (also validated by the gate) may write here.

**This is a DRAFT.** A human should decide whether the fenced set below is
complete — add anything missing, strike anything that should stay
optimizer-editable — before the first live H388 run.

## Proposed protected block (paste verbatim into the skill doc)

```markdown
<!-- SLOW_UPDATE_START -->
## Locked discipline — never edit or remove (MG-locked, per /pwg-drain)

- **opt2 harness is canonical** — `gen_opt_harness2.py`; do not substitute another
  generation harness.
- **`--output-budget=90`** on generation.
- **`--tm=auto` on the first pass**; `--no-tm` is mandatory on every
  requeue-for-audit-failure round (a plain requeue re-serves the exact flagged
  content — the "gam trap").
- **≤3-wide concurrency** — never more than 3 roots/agents concurrent (the Slice-D
  18× collapse = 117 transient nulls is the counter-example).
- **PWG sense order is preserved** — never reorder senses; lean-TR is rejected.
- **`csl-orig/v02/pwg/pwg.txt` is read-only** — always.
- **On a requeue regression, keep the better prior attempt** — never overwrite a
  complete card with a fresh partial ("latest requeue wins" is WRONG).
- **Provenance records the exact model version** — `claude-sonnet-5`, never a bare
  "sonnet".
<!-- SLOW_UPDATE_END -->
```

## Why each is fenced (for the review)

| Rule | If the optimizer edited it away… |
|---|---|
| opt2 canonical | a different harness silently changes output shape; gates misread |
| `--output-budget=90` | truncation/overrun the gates weren't calibrated for |
| `--no-tm` on requeue | the "gam trap" — re-serving flagged content as if fixed |
| ≤3-wide | the 18× concurrency collapse (117 transient nulls) returns |
| PWG sense order | citation IDs and scan anchors drift; lean-TR quality loss |
| csl-orig read-only | corrupts the canonical source |
| better-prior-attempt | a regression overwrites good cards with partials |
| exact model version | provenance becomes a defect (bare-tier) |

## What is intentionally LEFT optimizer-editable

Everything about *how to translate well* — fragment-splitting heuristics, RU
register choices, handling of commentary vs. verse, format-defect avoidance, the
failure-mode guardrails distilled in
[`best_skill.pwg.md`](https://github.com/gasyoun/Uprava/tree/main/tools/skillopt).
That is exactly what SkillOpt is meant to improve; fencing it would defeat the
loop. The fence is only around **run discipline**, not translation craft.

_Dr. Mārcis Gasūns_
