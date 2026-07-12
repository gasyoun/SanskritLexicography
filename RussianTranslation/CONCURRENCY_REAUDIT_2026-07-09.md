# Concurrency + append-safety + artifact-lifecycle re-audit (adversarial)

_Created: 09-07-2026 · Last updated: 09-07-2026_

**Model:** Opus 4.8 (`claude-opus-4-8`). Handoff:
[H423](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H423-Opus_RussianTranslation_concurrency_append_artifact_reaudit_09.07.26.md).

## What this is

An adversarial **re-verification** of the W1 collision matrix in
[PIPELINE_CAPABILITY_AUDIT_2026-07-08.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/PIPELINE_CAPABILITY_AUDIT_2026-07-08.md)
(§W1), checked against **current `master`** (`78fd80c`, 09-07-2026) rather than trusting the
audit's own 08-07-2026 verdict column. The 08-07 audit classified every direct-production-path
writer as **safe / LWW / TORN / LOCKED**; between then and now the **H336** hardening pass
landed the H-1/H-2/H-3 fixes. The task was to falsify "fixed", not trust it — construct the
concrete two-session interleaving that still breaks each guard, and only open a fix PR for a
guard **proven** broken.

**Headline verdict: no guard is proven broken.** Every unrecoverable-loss (LWW) and
torn-append (TORN) hazard the 08-07 matrix flagged now has a landed, code-level fix on
`master`, each with a selftest. The two residuals are honest *opt-in / discipline* caveats
already subsumed by the worktree-per-account operating protocol — not correctness holes. Per
the handoff's fix-PR gate, **no fix PR is warranted**; this verdict table is the deliverable.

## Per-row verdict table

Verdict key: **FIXED-since** = the 08-07 hazard is closed by code that landed after the audit ·
**NOT-A-RISK** = re-confirmed regenerable/advisory, no unrecoverable loss · **RESIDUAL (opt-in)**
= a code backstop exists but is not the default; the operating protocol is the primary defense.

| Matrix row (writer) | 08-07 class | Re-audit verdict | Evidence on `master` (78fd80c) |
|---|---|---|---|
| `pwg_ru_translated.jsonl` — the store (`promote_final_cards.py --merge`) | **LWW (unrecoverable)** | **FIXED-since** | H336/H-1: [`promote_lock.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_lock.py) `PromoteClaim` = `O_EXCL` claim at `<store>.promote.lock`, TTL-only staleness (no PID check — meaningless across clones), `--steal-lock` escape hatch. [`promote_final_cards.py:337-398`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/promote_final_cards.py) wraps the **entire** merge-read→guard→backup→`os.replace` window in the claim, and the backup is now a **unique** `.premerge.<UTC>.bak` (line 386-389). Two concurrent `--merge` runs: the O_EXCL loser raises `ClaimBusy` and writes nothing; serialized re-run keeps its own timestamped backup. Interleaving falsified. |
| `translation_memory.<lang>.json` | LWW (regenerable) | **NOT-A-RISK** | Full rewrite from the whole store; regenerable, rebuilt once after merge per the single-promoter protocol. No unrecoverable loss. |
| `translation_memory.frag.<lang>.jsonl` | **TORN** | **FIXED-since** | Now appended via [`translation_memory.py:593-594`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/translation_memory.py) → `window_common.append_jsonl_line` (single `os.write` to an `O_APPEND` fd). |
| `translation_memory.denylist.jsonl` — writer **and** reader | **TORN + silent-drop (P0 correctness)** | **FIXED-since** | Writer: [`requeue_from_audit.py:92`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/requeue_from_audit.py) uses `append_jsonl_line`. Reader: [`load_denylist` (translation_memory.py:234-240)](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/translation_memory.py) now **raises `DenylistError`** on a torn line instead of silently skipping — a dropped denylist row can no longer silently re-enable TM reuse of gate-rejected content. This was the one flagged single-account correctness hole; it is closed and fail-loud. |
| `window_status.{json,md}`, `audit_window.report.{json,md}`, `judge_sample.keys.txt` | LWW (same-clone) | **RESIDUAL (opt-in)** | H336/H-2: [`audit_window.py --window-tag`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py) routes these to `output/<tag>/…` (tag defaults to `--root`). But the **default** (`--window-tag` omitted) still writes flat singletons ([audit_window.py:310](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py)), so two audits in **one shared clone** without the flag still clobber. Not a hole under the protocol (rule 1 = one worktree per account, never a shared clone). |
| `requeue.keys.txt` (+ `.transient`/`.defect`) — write→read TOCTOU | LWW + TOCTOU | **RESIDUAL (opt-in)** | Same H336/H-2 tag: [`requeue_from_audit.py --window-tag`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/requeue_from_audit.py) reads from the same `output/<tag>/` the audit wrote (closes the TOCTOU) **when the tag is passed**. Default reads the singleton. Worktree-per-account is the primary defense. |
| `window_ledger.jsonl` | **TORN** | **FIXED-since** | [`window_reports.py:148`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/window_reports.py) → `append_jsonl_line`. |
| `run_pilot_wf.opt2.js` (harness) | LWW | **NOT-A-RISK** | Regenerable; per-window `--out=…wNN.js` convention. No data loss. |
| `verb_batch_worklist.json` / `nominal_batch_worklist.json` | LWW (advisory) | **NOT-A-RISK** | Regenerable worklists. |
| `layer_version_log.jsonl`, `failures/auto_failures.jsonl` | **TORN** | **FIXED-since** | [`layer_versions.py:177`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/layer_versions.py) and [`failure_capture.py:88`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/failure_capture.py) → `append_jsonl_line`. |
| coordinator `state.json` / `dashboard.json` / `artifacts/<lease>/` | LOCKED (opt-in) | unchanged | `DirLock`, single-machine, opt-in; the direct production loop bypasses it (documented). |

## Scope 3 — artifact lifecycle (H234 / `synth_dispatch.py`)

**CONFIRMED-implemented.** [`synth_dispatch.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/synth_dispatch.py)
codifies all six H180-ArmB failure lessons with real guards, pinned by a 7-case `selftest`:

- **#1 false-stall kill** — liveness is judged **only** by output-file growth (`_alive_by_output`, line 258), never a 0-byte transcript.
- **#2 wide fan-out** — `max_concurrent` default 3, `HARD_CAP=4` raises `ValueError` (line 222), staggered starts.
- **#3 silent hang** — `--kill-after` (default 600 s) output-file kill-guard.
- **#4 watcher wipe** — `land_watcher_safe` (line 166): atomic `os.replace`, sha verify, sleep, **re-verify the file survived**, re-land up to 3×.
- **#5 zombie overwrite** — `_maybe_land` (line 281) lands only the current owner attempt; landed jobs are sealed (`state == "landed"` discards late output); re-dispatch happens only after `_kill_confirm_dead` (`proc.wait()` returns).
- **#6 large free-form** — inputs over `--assemble-over` (800 `<ls>`) route to deterministic verbatim fragment fusion (`assemble_entry`, multiset self-check), zero LLM.

**"Bare fan-outs are banned" — the honest verdict: documented + true-in-practice, NOT
code-enforced.** A grep of the pilot/src tree for every concurrency primitive
(`ThreadPoolExecutor`/`ProcessPoolExecutor`/`asyncio`/`multiprocessing`/`subprocess.Popen`/
`threading.Thread`) finds **no bare pwg_ru multi-agent fan-out** competing with
`synth_dispatch.py`. The other hits are unrelated: `audit_window.py:389` (a bounded
`max_workers=4` pool running an audit's own child gates), and `build_corpus_lexicon.py` /
`mine_running_text.py` / `nws_scrape.py` (DeepSeek/HTTP data-build scrapers, not the Claude
production path). Actual production Claude fan-out runs through the Max **Workflow** surface
(generated JS), not a Python fan-out at all — so nothing structurally competes with the
dispatcher today. The "ban" holds because only one dispatcher exists, but nothing in code
*prevents* a future bare fan-out; it remains an operating-discipline rule, not a mechanical gate.

**Minor, out-of-scope observation (not a W1 hazard, not a finding):**
`build_corpus_lexicon.py:307` and `mine_running_text.py:192` open their output in `'a'` mode
under a `ThreadPoolExecutor` (concurrent threads sharing one buffered append handle) — a
torn-line risk in principle. They are single-invocation data-build tools outside the
multi-account production path and outside the W1 matrix, so they are noted here for the record
only, not routed as a correctness finding.

## Conclusion

The FIX_PLAN's P0/P1 "complete" survives adversarial attack on the concurrency axis: H336
turned the four TORN appenders into single-`os.write` atomic appends, made the denylist reader
fail-loud, and put an `O_EXCL` claim + unique timestamped backup around the one
unrecoverable-loss promote race. The same-clone `window_status`/requeue clobber is the only
class left to *code discipline* (`--window-tag` is opt-in), and it is fully subsumed by the
mandatory worktree-per-account rule. **No proven-broken guard → no fix PR.**

_Dr. Mārcis Gasūns_
