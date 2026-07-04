# Handoff — Scope A, SLICE C: parallel verb-root translation workstream

Date: 2026-06-29 · Audience: Claude Code (new chat, runs CONCURRENTLY with the Slice A chat) ·
Repo: `SanskritLexicography/RussianTranslation` (subdir of `gasyoun/SanskritLexicography`,
`master`). Read `.ai_state.md` and `H029-Sonnet_RussianTranslation_scope_a_freq_queue_29.06.26.md` first.

## Goal

Translate **SLICE C** of the remaining frequency-ranked verb roots into Russian on the 3-layer
batched+masked harness, in parallel with the Slice A chat. Same pipeline, disjoint roots.

## Division of labour (do NOT cross slices)

The 52 remaining roots are split into two disjoint slices. **This chat owns SLICE C only:**

```
DA,yA,nI,man,jan,banD,pat,su,vad,iz,mad,hi,Bid,Buj,paS,pA,Sam,yat,gA,Cid,brU,naS,vraj,jIv,yaj,rakz
```

(The Slice A chat owns `dA,jYA,vac,…,tyaj`; it also owns the shared setup — the
`has_text_signal()` fix and the 5 grammar-parity re-runs. You do NOT repeat those. The
`has_text_signal()` fix affects only AUDIT noise, not translation, so you can translate without
it; `git pull` it when convenient for cleaner audits.)

## Per-root loop — TAG = `sc` (unique filenames so chats never clobber each other)

For each root R in Slice C (≈ 26 roots / ~1,130 cards ≈ **$65, ~2.5 h**):

```powershell
python src\pilot\root_window_status.py R          # expect PASS, 0 stale; --prune-stale if needed
python src\pilot\gen_opt_harness2.py R             # writes run_pilot_wf.opt2.js (3-layer)
copy src\pilot\run_pilot_wf.opt2.js src\pilot\run_pilot_wf.sc.js   # UNIQUE per chat
# run src/pilot/run_pilot_wf.sc.js via the Workflow tool; save its result as wf_output.sc.json
python src\pilot\audit_window.py wf_output.sc.json --root R --write-requeue
```

Verify each: 0 null beyond the guard, 0 leftover `{Tn}`, markup-fidelity = non-null count.

**Concurrency safety (critical):**
- Always `copy` the generated harness to `run_pilot_wf.sc.js` and launch THAT — never the bare
  `run_pilot_wf.opt2.js` (the Slice A chat overwrites it).
- Save results to `wf_output.sc.json` (not the shared `wf_output.json`).
- **Read the audit STDOUT** for the accept/requeue decision (printed inline). Do NOT depend on
  the shared `src/pilot/output/requeue.keys.txt` (the other chat clobbers it).
- **Defer requeue re-runs** to the post-translation coordinating pass; don't run
  `requeue_from_audit.py` inline (it races on `requeue.keys.txt`).

## Decision rule, layers, guardrails

Identical to the Slice A handoff: accept-with-documented-residuals when `nws`+`sense_dupes` PASS
and residual = the known pattern (F-gate-nws-fp on `pw` cards + coverage on dense/homonym heads);
real failures → flag for the coordinating requeue pass. The 3 layers (lexicon + corpus/Renou +
Whitney grammar) + the Apresjan manual layer are all in the harness — don't strip them.
**csl-orig is READ-ONLY.** Commit code/state to `SanskritLexicography` (`master`, `ai-wip:`,
Co-Authored-By line); `wf_output.sc.json` is a gitignored local artifact.

## Coordination with the other chats

- **Commits:** you both touch `.ai_state.md` — keep edits to your own roots' lines and pull
  before pushing to avoid conflicts (append-only, merge-friendly).
- **Cleanup:** `run_pilot_wf.sc.js` and `wf_output.sc.json` are throwaway — delete when done.
- **What to bring back:** per root clean/total, requeue count, $ cost
  (`parse_workflow_cost.py <transcript_dir>`), accept/flag decision; Slice C running totals.
