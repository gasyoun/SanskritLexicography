# Token lever: portrait-slim is a non-lever; the real lever is batch budget

**Date:** 2026-06-30 · **Context:** PROCESS_AUDIT rec 4 proposed "portrait-slim": strip
`citations_resolved`/`citations`/`strata`/`examples_sa` from the inlined portrait for a
"~30–35 % lossless cut on the larger half of inlined card content." MG confirmed the
translator *needs* citations, gating the design. On inspection, the premise is **false**.

## Finding (verified corpus-wide, 3,538 sub-card portraits)

The harness ([`gen_opt_harness2.py`](RussianTranslation/src/pilot/gen_opt_harness2.py):278) inlines the
**per-sub-card** portrait (`*~~*.portrait.json`), and:

- the portrait is the **smaller** part of inlined content: **32 %** (skeleton 68 %),
  portrait/skeleton ratio **0.47** — *not* "1.7–2× the skeleton";
- every populated portrait contains exactly four fields: **`key1`, `iast`, `evidence_scope`,
  `corpus_synonyms`** (the corpus lexical-layer signal). `corpus_synonyms` is small
  (median 323 B, max 449 B);
- **none** of the audit's claimed strippable fields (`citations_resolved` / `citations` /
  `strata` / `examples_sa`) exist in any sub-card portrait.

The audit's token agent measured the per-**headword** aggregate (`vart.portrait.json`, ~447 KB),
which is **not** what the harness inlines. Decision #11 ("does the translator need
`citations_resolved`?") was therefore moot — that field isn't present; the real citations the
translator sees are the `{Tn}`-masked `<ls>` references inside the **skeleton** (essential, the
card itself). There is nothing in the portrait that is both sizeable and unneeded
(`corpus_synonyms` is the corpus layer; stripping it would remove a designed signal).

**Conclusion: portrait-slim is not implemented — it would strip non-existent fields or the
corpus signal.**

## The real lever: batch budget (rec 11)

The dominant cost is the **fixed per-agent framework overhead (~30 k tokens, paid once per
agent call)**, not the inlined card. So the lever is **fewer agent calls** = a higher
`--budget` (bytes packed per agent call). Measured batch counts (= agent calls = cost driver):

| root | b9000 (old) | b12000 | b16000 | b20000 |
|---|---:|---:|---:|---:|
| dA | 12 | — | 7 | 6 |
| car | 12 | — | 6 | 5 |
| viS | 13 | — | 7 | 6 |
| vas | 10 | — | 6 | 4 |
| hA | 8 | — | 4 | 4 |

**Default bumped 9000 → 12000** (a conservative ~−20–25 % agent calls while keeping batches
within the already-tested 13–14-card range). This is safe: a larger batch that degrades is
caught by the harness's post-restore `<ls>`/`{#..#}` **fidelity guard**, which nulls the
mismatched card → requeue — it cannot silently corrupt. Bigger budgets (16–18 k, ~−45 % agent
calls) are available via `--budget=` but should be **retry-rate-validated on a Max run** before
becoming the default (a larger batch can raise schema-validation retries).

## Net

The harness was already lean on the dimension the audit targeted. The remaining token savings
are: (a) this budget bump (shipped), (b) further budget tuning pending a retry-rate measurement,
(c) the lean-TR trim (already tested twice and **rejected** for quality loss). There is no free
portrait cut.
