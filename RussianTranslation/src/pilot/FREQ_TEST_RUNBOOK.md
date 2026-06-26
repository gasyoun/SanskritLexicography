# Freq-queue 10-article test — runbook (Max)

A bounded end-to-end test of the frequency-first pipeline: **8 single-card nouns + the
giant root `man` (30 sub-cards)** = **38 translation units**. Exercises the common path
(fast, ≈43k of 44k headwords look like this) AND one full giant `split → translate → glue`,
and yields per-card timing to extrapolate the full run.

> **Why this set, not the literal top-10.** The top-10 freq articles are all giant verb
> roots = **992** translation calls (i alone = 204). This mix is ~38 calls and proves the
> same pipeline. Full-queue estimate: ≈43k single-card + ~1,163 giants × ~85 ≈ **~140k
> calls** — the giants are the cost and they're front-loaded by frequency.

## Committed (in git)
- **Sub-card plumbing wired**: `run_pilot_wf.js` (`fileOf`) and `_pilot_collect.py` now keep
  a `~~`-containing sub-card stem verbatim instead of re-`safe_name`-ing it, so
  `<subkey>.raw.txt` → `<subkey>.merged.md` flows straight into `root_glue_translated.py`.

> **Inputs and the manifest are gitignored (per-machine) — regenerate them on the run
> machine first (Step 0).** They do NOT travel via git.

## Step 0 — generate inputs + manifest (on the run machine, from `src/`)

```sh
# 8 single-card nouns + the giant 'man' (auto-split into 30 single-pass sub-cards)
python _pilot_gen_merged.py --root-split man nara jana idam kArya vIra na iti loka

# build the 38-unit test manifest (8 noun safe-name stems + man's 30 sub-card subkeys)
python - <<'PY'
import json, sys; sys.path.insert(0, '.')
from safe_filename import safe_name
nouns = ['nara','jana','idam','kArya','vIra','na','iti','loka']
subs = [s['subkey'] for s in json.load(open('pilot/input/man.rootmap.json', encoding='utf-8'))['sub_cards']]
m = [{'key1': safe_name(n)} for n in nouns] + [{'key1': sk} for sk in subs]
json.dump(m, open('pilot/output/scale_manifest.freqtest.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote scale_manifest.freqtest.json:', len(m), 'units')
PY
```
This yields `pilot/input/` (8 noun whole-cards + `man~~h0_*` 30 sub-cards; max sub-card 131
lines, nouns 126–266) and `pilot/output/scale_manifest.freqtest.json` (38 entries, each
`key1` = the input stem the workflow iterates: noun `safe_name`, or a `man` sub-card subkey
verbatim, incl. 3 `man~~h0_0N_sec_N` secondary-conjugation stems).

The 8 nouns: `nara jana idam kArya vIra na iti loka` (all comfortably single-pass; the
bigger high-freq nouns `kAla`/`ka` were left out — at ~520 lines they risk overflowing a
single pass, which is a separate "extend the head-splitter to large non-giant entries"
follow-up, not part of this test).

## Run it (on Max)

**1. Point the workflow at the test manifest.** In [`run_pilot_wf.js`](run_pilot_wf.js) set:
```js
const SECTION = 'freqtest'   // was 'a'
const OFFSET  = 0
const LIMIT   = 38           // all 38 units
```
(Revert to `'a'` / `50` afterwards to resume the a-section.)

**2. Translate + judge** through your harness; save the JSON result to `wf_output.json`.
Translate = Sonnet (per-sense Russian + Apresjan discrimination); Judge = Sonnet bulk,
Opus on rejects only (per [`../../research/JUDGE_POLICY.md`](../../research/JUDGE_POLICY.md)).
**Record wall-clock + token totals** — that's the scaling number we're after.

**3. Render to `.merged.md`:**
```sh
python run_real_test.py audit wf_output.json
```
Writes one `<stem>.merged.md` per unit into `pilot/output/` (sub-card stems kept verbatim).

**4. Glue the giant into a NESTED article:**
```sh
python root_glue_translated.py man      # -> pilot/output/man.NESTED.md
```
The 8 nouns need no glue — each `<noun>.merged.md` is already its final article.

## What to check
- **Coverage**: 8 noun cards present; `man.NESTED.md` assembles all 30 sub-cards in order —
  homonym dividers (`# Омоним N`), simple-verb head parts, then secondary (caus/desid) stems, then prefixed verbs, supplements
  (PW/SCH/PWKVN) last. Pending slots only if a sub-card failed.
- **No overflow**: every unit ≤ ~270 lines, so each should translate in one pass (the old
  slow run was the now-deleted 820-line monolithic `_b_u~~00.raw.txt`).
- **Quality**: judge severity ≤ 2; sigla/IAST kept verbatim; NWS owner-map rows one-per-entry.
- **Timing**: per-unit wall-clock × the queue profile → full-run cost.

## Apresjan evidence on sub-cards (interim solution — now wired)
Split sub-cards **no longer translate evidence-blind**. `gen_root_split` writes a real
`corpus_synonyms` per sub-card via `subcard_portrait`:
- **head / secondary** (the simple verb + its caus/desid) → the **root's** corpus renderings
  (e.g. `man` → считать, думать, мыслить). Exactly right — they *are* the simple verb.
- **prefix** → keyed on the prefixed **surface form** (`upasarga+root`), because the corpus
  distinguishes them: `anu+man` → одобрять, `ava+man` → смотреть свысока, `abhi+man` →
  охватить мыслью — *different* from the bare root. The portrait's `evidence_scope` =
  `prefixed-form` when the corpus has the form, else `root-fallback …` (the bare-root
  candidates as a **weak hint** — the translate prompt is told to defer to the German gloss
  for these, so a shifted prefix meaning isn't overwritten by a root synonym).

On `man`: **3 of 18** prefixes get prefix-specific corpus evidence; the other 15 fall back
to the labelled root hint. **Residual gap (the proper fix):** sandhi-changed and stacked
prefixes (`sam+man`→saṃman, `abhi+sam+man`) miss the naïve `upasarga+root` concat and fall
back — matching them needs the **sandhi-joined surface form** already computed in
[`PWG/verbs01/pwg_preverb1.txt`](https://github.com/sanskrit-lexicon/PWG/blob/master/verbs01/pwg_preverb1.txt)
(`join_prefix_verb`). Wiring that lookup raises prefix-specific coverage; the interim hint is
safe in the meantime.

> **UPDATE 2026-06-26 — this sandhi-join wiring was DROPPED as futile.** Only 3/15 of `man`'s
> prefixed surface forms are corpus-attested, so the `pwg_preverb1.txt` join buys almost
> nothing; the labelled root-fallback hint is the accepted final behaviour. Do not revive it.

## Run log — executed 2026-06-24 (translate-only; no Opus judge)

Ran via the Workflow tool (38 general-purpose Sonnet agents, ~14-way concurrency), then
`root_glue_translated.py man`.

| Metric | Value |
|---|---|
| Translated | **38/38** units; all `<stem>.merged.md` written |
| Glued | `man` → **30/30 sub-cards, 0 pending** → `man.NESTED.md` (797 lines, structure correct) |
| Wall-clock | **10.5 min** (38 units at ~14 concurrency) |
| Tokens | **1.61 M** (avg 42.5k/unit — inflated by the 8 big nouns; `man` sub-cards median **9** output lines) |

**Apresjan worked as designed.** The `ava` agent *used* the corpus hint «смотреть свысока»
but **rejected** it as too colloquial, choosing the scholarly «презирать / относиться с
пренебрежением» (avamāna = contempt); the `pari` agent saw `evidence_scope='root-fallback'`
and deferred to the German gloss — exactly the weak-hint behaviour.

### Audit (this run)
- **Deterministic fidelity gate** [`src/audit_translation.py`](../audit_translation.py):
  **38/38 clean** — `<ls>` citations preserved ≥90 % (several units even expanded `n="…"`
  abbreviations to full), `{#…#}` Sanskrit preserved ≥85 %, Russian present in every unit.
- **Semantic spot-check** (3 `fact-check-against-source` agents on the hardest units):
  `anu` **PASS**, `nara` **PASS** (NWS owner-map 12/12 verbatim, EN glosses translated from
  EN), `ava` substantively **PASS**. Two trivial nits found:
  1. `ava`: `ein <ab>Schol.</ab>` → «один Schol.» — the gloss-prose article "ein" (= "one
     scholiast reads…") was translated; borderline-correct, not a siglum leak.
  2. `nara`: a Hoernle multi-citation NWS row was compressed (3 cites merged, one "physician"
     sub-sense dropped) — relates to NWS guard 4 ("render EVERY sub-sense"); owner verbatim.

### Opus judge pass — executed 2026-06-24 (38 Opus agents, 2.4 min, 2.06 M tok)
**Severity: {1: 24, 2: 13, 3: 1} → 37/38 publishable (sev ≤ 2).** Discrimination "good" on every
polysemous unit. The judge caught what the fidelity gate + spot-check did not:
- **`idam` — sev 3** (the only one): the translator **swapped NWS owner rows** Geldner↔Graßmann
  (Graßmann's distinct gloss lost) — the F12 the owner-map feed targets. The authoritative map is
  **correct** (row 1 = Graßmann:207, row 3 = Geldner:28), so this is a translator slip on a hard
  double-Geldner case, **caught in production by `nws_split.py check`** (my test ran translate-only
  without that gate). Also a broken `{%pāda{%}` brace and `<is>` italics rendered inside `{%..%}`.
- **`k_arya` — sev 2, coverage**: dropped 2 PWG Nachträge patches (1a ṚV.PRĀT 14,16; 2a Spr. 3008).
- **`jana` — sev 2, sigla**: merged two Sanskrit tokens `{#paTi#}`+`{#ka˚#}` → `{#paTika˚#}`.
- **`man~~h0_zz_pw00` — sev 2, sigla**: German abbrev `<ab>Bed.</ab>` expanded to «значением».

**Prompt-tuning findings for the scale run** (not blocking): (a) keep German abbrevs Bed./Schol.
verbatim, never expand; (b) render EVERY Nachträge patch (kārya drop); (c) `<is>` source-italics →
keep as transliterated siglum, not `{%..%}`; (d) the owner-map F12 is real on hard multi-cite rows —
keep the deterministic `nws_split.py check` gate in the scale loop (it catches idam).

**Verdict:** split → translate → glue runs end-to-end; **37/38 publishable**, no overflow, format
invariants hold; the 1 sev-3 is a known F12 class the production owner-gate catches. Pipeline is
scale-ready pending the prompt nits above + the `nws_split` gate wired into the run loop.

> **STATUS 2026-06-26 — all four prompt nits (a)–(d) and the `nws_split.py` owner-map gate are
> now encoded** in [`run_pilot_wf.js`](run_pilot_wf.js) (HARD RULES 3/4/5) and the audit loop
> (`run_real_test.py audit`); they are no longer pending. The findings above stay as the record
> of *why*. The judge is now Sonnet-bulk + Opus-on-reject (see step 2).
