# Handoff — Scope A: continue the PWG→Russian frequency (dhātu) queue

Date: 2026-06-29 · Audience: Claude Code (new chat) · Repo:
`SanskritLexicography/RussianTranslation` (a subdir of the `gasyoun/SanskritLexicography`
repo, branch `master`). Read `.ai_state.md` first for the full journal.

## Goal

Translate the remaining frequency-ranked **verb-root** PWG articles into Russian on the
validated **3-layer batched+masked harness**, one root at a time, auditing each before the next.

## Where things stand (2026-06-29)

- **Harness = `src/pilot/gen_opt_harness2.py`** (DEFAULT). It: masks each card (`pwg_mask`,
  citations→`{Tn}`), bin-packs N cards per agent (`--budget`, default 9000), injects the
  Whitney **grammar block once per root**, and restores `{Tn}` to source markup IN-JS so the
  output is already a canonical `wf_output.json`. Legacy per-card `gen_opt_harness.py` exists
  but is superseded. Full design: `TLONLY_PROTOTYPE.md`, `GRAMMAR_LAYER.md`.
- **Economics (measured):** ~**$0.050/card**, ~**5.1 s/card**, ~**$3.22/root**, ~5.5 min/root.
- **60 rootmaps prepared** in `src/pilot/input/*.rootmap.json` = **3,059 sub-cards** total.
- **Done: 8 roots.** BUT NOT UNIFORM — only `yuj`/`vid`/`han` had the **Whitney grammar layer**;
  `gam` + Stage A/B `sTA`/`BU`/`as`/`i` were translated BEFORE grammar was wired (2-layer only).

## Step 0 — one-time code fix (do FIRST, de-noises every root)

Fix **F-gate-nws-fp**: `has_text_signal()` in `src/pilot/prompt_rule_audit.py` ignores NWS
owner citations (MW/Graßmann/Geldner), so `suspicious_attested_without_text_signal` is a
~60–70% false positive on every `*_zz_pw*`/NWS card. Teach it to count an NWS owner citation
as a text signal. This removes the dominant false-positive requeue queue-wide (free, no
re-translation). Verify with `python src/pilot/window_selftest.py`.

## Step 1 — re-run the 5 non-uniform roots for grammar parity (~$30, ~30 min)

`sTA`, `BU`, `as`, `i`, `gam` lack the Whitney grammar layer. Re-translate each on
`gen_opt_harness2.py` so all roots are uniformly 3-layer. (Skip if the user decides 2-layer
is acceptable for these.) Same per-root loop as Step 2.

## Step 2 — the per-root loop (THIS chat = SLICE A, 26 roots ≈ $65, ~2.5 h)

**Parallelization:** the 52 remaining roots are split into two disjoint slices so a second
chat (`H030-Sonnet_RussianTranslation_scope_c_freq_queue_29.06.26.md`) can run concurrently. **This chat owns
SLICE A only** (don't touch Slice C):

```
dA,jYA,vac,car,diS,vA,hA,viS,muc,Sru,mA,vas,Ap,vah,laB,As,siD,ji,tap,dah,ram,Baj,kzip,aS,SaMs,tyaj
```

Use a per-chat **TAG = `sa`** for unique filenames so the two chats never clobber each other's
`run_pilot_wf.opt2.js` / `wf_output.json`. For each root R:

```powershell
python src\pilot\root_window_status.py R          # expect PASS, 0 stale; --prune-stale if needed
python src\pilot\gen_opt_harness2.py R             # writes run_pilot_wf.opt2.js (3-layer)
copy src\pilot\run_pilot_wf.opt2.js src\pilot\run_pilot_wf.sa.js   # unique per chat
# run src/pilot/run_pilot_wf.sa.js via the Workflow tool; save its result as wf_output.sa.json
python src\pilot\audit_window.py wf_output.sa.json --root R --write-requeue
```

**Read the audit's STDOUT** for the accept/requeue decision (clean/requeue counts are printed
inline) — do NOT rely on the shared `src/pilot/output/requeue.keys.txt` persisting (the other
chat overwrites it). **Defer actual requeue re-runs** (`requeue_from_audit.py`) to a single
coordinating pass after both slices finish — running it inline races on `requeue.keys.txt`.

Verify each `wf_output.json`: 0 null beyond the guard, 0 leftover `{Tn}`, markup-fidelity =
non-null count (the harness already guards this — nulled cards = requeue, never garbled).

**Decision rule (per root, same as gam):** `nws` + `sense_dupes` PASS and residual = the known
pattern (F-gate-nws-fp on `pw` cards + coverage on dense/homonym heads) → **accept with
documented residuals**. Real mechanical failures → `python src\pilot\requeue_from_audit.py R`
→ re-run Max → re-audit. Typical clean rate ~76–87%.

## Notes / guardrails

- **csl-orig is READ-ONLY** — never modify/commit/push it. Commit code+state to
  `SanskritLexicography` (`master`); `ai-wip:` prefix; end messages with the Co-Authored-By
  line. `wf_output.json` and `src/pilot/output/*` are gitignored local artifacts.
- The 3 layers in the prompt: **lexicon** (`corpus_lexicon.jsonl` candidates, in the portrait),
  **corpus/Renou** (strata + register), **Whitney grammar** (`whitney_grammar.py`, injected),
  plus the **Apresjan-led manual layer** (RENDERING GUIDANCE in the TR). Don't strip any — the
  lean-TR A/B (`AB_TEST_LEAN_TR.md`) proved trimming the TR saves nothing.
- **Cost lever** = agent count (the 30k subagent system prompt dominates). `--budget=20000`
  packs ~2.5× more cards/agent (−~23% $) but is slower + slightly more requeues; default 9000
  is the proven balance. See `TLONLY_PROTOTYPE.md` cost decomposition.
- After finishing, update `.ai_state.md` + `../../Uprava/GTD_NEXT_ACTIONS.md`.

## What to bring back

Per root: clean/total, requeue count, $ cost (`parse_workflow_cost.py <transcript_dir>`),
and the accept/requeue decision. Running totals for the queue.
