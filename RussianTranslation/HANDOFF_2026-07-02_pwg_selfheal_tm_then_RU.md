# Handoff — PWG selfheal hardening + translation memory DONE; RU is the priority next

_Created: 02-07-2026 · Last updated: 02-07-2026_

**To start this work:** Read
[`HANDOFF_2026-07-02_pwg_selfheal_tm_then_RU.md`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/HANDOFF_2026-07-02_pwg_selfheal_tm_then_RU.md)
and execute it.

**Branch:** `feat/pwg-en-fu1-phase0` (off `master`). **⚠️ A second (autonomous) account
cycles the local checkout across branches mid-session and leaves uncommitted work in it**
(this session found it on `feat/renou-hypotheses-spec` with `RENOU.md` modified). **Commit
ONLY via a git worktree off `origin/feat/pwg-en-fu1-phase0`** — never the main checkout:
```
git fetch origin feat/pwg-en-fu1-phase0
git worktree add --detach <tmp> origin/feat/pwg-en-fu1-phase0
# edit code in <tmp>; the gitignored DATA (wf_output stores, src/pilot/input/, tm/) lives
# ONLY in the main checkout — copy the per-key files you need INTO the worktree to run,
# then commit+push code from the worktree:
git -C <tmp> add ... && git -C <tmp> commit -m ...
git -C <tmp> fetch origin feat/pwg-en-fu1-phase0 -q && git -C <tmp> rebase origin/feat/pwg-en-fu1-phase0
git -C <tmp> push origin HEAD:feat/pwg-en-fu1-phase0
```
**Model:** generation = Sonnet 5 (`claude-sonnet-5`, pinned on the `--lang=en` path);
orchestration = Opus 4.8 (`claude-opus-4-8`).

## ⭐ PRIORITY: get back to RU. EN was a proof-of-concept, not a full deliverable.
MG (02-07-2026): *"after these small EN translations get back to RU, which is the most
important part. EN for now is just a proof of concept."* The EN FU1 track is now
**functionally complete as a PoC** (below). The next session's real job is the **RU**
translation, now armed with the two harness robustness fixes and the translation memory
built this session.

## What this session shipped (all pushed to `feat/pwg-en-fu1-phase0`)
- **EN coverage 98.9% → 99.9%** (2119/2121). ALL 6 giant heads healed to 100%: hi (205
  `<ls>`), brū (198), banD (162), ji (137), diS (125), car (124). Residual = **2 tiny
  cards** left as PoC-acceptable: `j_y_a~~h1_00_pwg00`, `yat~~h0_zz_pw`
  (both stochastic-fail after 3 tries; retry fresh if ever wanted). Giants are
  **stochastic** on the whole-card attempt — the earlier "always fails" was one unlucky
  run; retry 2–3× and they pass (brū: fail→pass; banD: 3rd try). Stores synced to main.
- **Two harness fixes** in [`src/pilot/gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/src/pilot/gen_opt_harness2.py):
  1. `fragGermanOk` **per-fragment `{Tn}`-fidelity gate + 4th retry** (commit `68d9ec1`):
     selfHeal only retried *null* fragments, so a fragment that returned a card but
     silently dropped a `{Tn}` was accepted and sank the whole-card stitch (the brū miss).
     Now each fragment is gated on its restored-German `<ls>/{#}` counts and the specific
     offender is re-billed. **Validated:** ji/car/vad/Bid/Ap healed via this path.
  2. **Never crash on the StructuredOutput cap** (commit `1c5cbfc`): `agent({schema})`
     THROWS when the retry cap is hit; that throw propagated out of `translateBatch` →
     the `parallel()` slot went null → the summary crashed the WHOLE workflow (killed
     sibling cards; seen on pA/Bid/banD). Both `agent()` sites are now `try/catch`→null,
     so a hard-fail card returns a clean null and the run reports `null_keys`. **Also use
     `--budget=1` for multi-key roots** so a dense card can't poison its light siblings.
- **AB-LOSS hard flags eliminated (4→0)** — [`src/pilot/audit_window_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/src/pilot/audit_window_en.py)
  gained a tight `TRANSLATABLE_AB` allowlist (commit `86a6fd4`): inline German content
  abbreviations correctly rendered to English (`best.`→"certain", `Bed.`→"sense") no
  longer count toward AB-LOSS (they aren't sigla). The two genuine drops were hand-patched
  in the stores (gam `caus-4` = restored `<ab>intens.</ab>`/`<ab>desid.</ab>`; laB
  `sec_1` = restored the whole `<ab>caus.</ab>…<ab>aor.</ab>` head + forms + citations).
  New `window_selftest.test_en_ab_loss_translatable` locks both directions.
- **Translation memory** (commit `173f0e4`) — the "reuse, don't reinvent" asset MG asked
  for: [`src/pilot/translation_memory.py`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/src/pilot/translation_memory.py)
  (content-addressed `sha256(lang|prompt_sha|source)` → translation; prompt_sha scoping =
  auto-invalidate on prompt change) + [`src/pilot/tm_build.py`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/src/pilot/tm_build.py)
  (harvests a sense-level TM from the stores: **EN = 11,377 entries, 3.5% exact-duplicate
  sources**). `tm/` is gitignored (regenerable). The reuse is **wired into the harness**
  (commit `9d46a20`, `--tm` gated OFF by default) + [`tm_harvest.py`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/src/pilot/tm_harvest.py)
  — see next-step 1. **Run `python src/pilot/tm_build.py ru` before the RU work** to seed
  the RU sense-TM from the ~10k existing RU cards.

## DO NEXT — in order

### 1. ✅ DONE — `--tm` fragment reuse is wired (commit `9d46a20`)
Shipped this session, gated behind `--tm` (**default OFF** → the autonomous RU runs and
every existing run are byte-for-byte unchanged; verified agent/tools-guard parity +
node-check on the default path). With `--tm`,
[`gen_opt_harness2.py`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/src/pilot/gen_opt_harness2.py)
builds `PRESOLVED[k#gi#i]` from the fragment TM (`tm.<lang>.frag.jsonl`) for any fragment
whose EXACT source is cached; `selfHeal` serves those without a model call and sends only
uncached fragments to the LLM. Each fresh fragment is harvested AT RESOLVE TIME (survives
a card-null → a retry reuses it — the brū-waste fix).
[`tm_harvest.py`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/src/pilot/tm_harvest.py)
ingests a run's `harvest` back into the TM (re-deriving each fragment source from the same
deterministic split; no source text travels through the payload). Keyed by the run's
`tm_prompt_sha`. Validated deterministically (seed 1 jYA fragment → "1 pre-resolved").
**Usage per --tm run:** generate with `--tm`, run the workflow, `save_and_audit … --merge`,
then `python src/pilot/tm_harvest.py <task_output_file>` to grow the cache.
- **Why not `resumeFromRunId`:** it REPLAYS a run verbatim (including the failure) — it
  does NOT re-attempt a stochastic failure. Fresh-run re-translates everything. The TM is
  the only real fragment reuse. (Do not repeat the resume mistake.)

### 2. RU translation run (the priority)
Resume the staged PWG→RU work on the hardened harness — now with `--selfheal --tm`,
`--budget=1` for multi-key, retry-fresh on stochastic nulls, ≤3-wide roots. **First seed
the RU TMs:** `python src/pilot/tm_build.py ru` (sense-level, from the ~10k RU cards); the
fragment TM fills as `--tm` runs harvest via `tm_harvest.py`.
Full RU run discipline: the `/pwg-slice` skill and
[`.ai_state.md`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/.ai_state.md).

### 3. SENSE-DUPE retag pass (7 EN roots — deferred, needs care)
Healing the giant heads to 100% added cross-part sense-number collisions (net 4→7 roots):
car(5), ji(3), hi/vac/su/laB(1 each), plus siD(5, partly exempted already). **These are
NOT faithful reuse — they are mis-tags:** the head part (`pwg00`) labels *continuation
citations* or the *homonym "N." label* as sense "N", colliding with the *real* sense "N"
in the sibling part (`pwg01`, which carries the proper `— N)` marker). Confirmed by
content spot-check (ji "3": pwg00=citations, pwg01="— 3) to drive out victoriously").
**Do NOT mask via `_dupe_exempt`.** Fix = a deterministic retag pass: in a head part, a
sense whose tag collides with a sibling AND whose German lacks a matching `— N)` marker
(it's citation overflow / a `N.` homonym label) gets relabelled to a non-colliding
continuation tag (e.g. `N-cont`). Gate to clear:
`python src/audit_sense_dupes.py wf_output.en.<root>.json` → PASS. This same mis-tag
exists in the RU pipeline (siD) — the retag pass benefits RU too.

### 4. THEN EN Phase 2 (validation) — only if EN is revived beyond PoC
Per [`FU1_PLAN.md`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/FU1_PLAN.md):
`promote_en.py` → `annotate_dcs_freq.py` → Opus 4.8 judge → human gold. Ground truth =
faithful to the PWG German (MW = cross-check only). `review_status` stays `ai_translated`.

### 5. Dashboard EN wiring (`:8765`) — still open, low priority
[`src/pilot/audit_window_en.py`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/src/pilot/audit_window_en.py)
is report-only; make it emit `dashboard_events.jsonl` + `window_status.json` so
[`dashboard_server.py`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/src/pilot/dashboard_server.py)
(`:8765`) reflects EN, not stale RU. (The gh-pages article dashboard already shows EN∪RU
coverage, so this is only for the live run-monitor.)

## Operational notes (learned this run)
- `src/pilot/input/` has **218k files** — never `du`/bulk-copy it; copy per-key
  (`<key>.raw.txt`, `<key>.portrait.json`, `<safe_root>.rootmap.json`) into the worktree.
- Per-root save loop used this session: `save_and_audit.py <root> <taskout> en --merge`
  then copy `wf_output.en.<root>.json` back to main. Never overwrite; `--merge` only fills.
- Windows console is cp1251 → every script does `sys.stdout.reconfigure(encoding='utf-8')`.

Journal: [`.ai_state.md`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/.ai_state.md).
Prior handoff: [`HANDOFF_2026-07-01_pwg_en_fu1_finalize.md`](https://github.com/gasyoun/SanskritLexicography/blob/feat/pwg-en-fu1-phase0/RussianTranslation/HANDOFF_2026-07-01_pwg_en_fu1_finalize.md).

_Dr. Mārcis Gasūns_
