# Runbook — frequency queue on the Max workflow harness

Goal: scale the PWG→Russian production run in DCS-frequency order, with giant
roots split into single-pass units and re-glued after translation. This is the
post-judge path: the 38-unit freq test is complete, 37/38 were publishable, and
the lone sev-3 belongs to the NWS owner-row slip class that the deterministic
audit gate catches.

**QA policy — BALANCED, token-optimized (2026-06-27, [`../../TOKEN_OPTIMIZATION_2026-06-27.md`](../../TOKEN_OPTIMIZATION_2026-06-27.md)):**
the bulk pass is **translate (Sonnet, single-turn inlined) + three FREE Python gates on 100 %
of cards**; the LLM judge is no longer per-card. The measured driver is `cache_read ≈ context ×
turns`, so the run is reshaped to "Python at max, LLM at minimum" — the A/B cut cache_read 3.2×
and eliminated the transient dropouts.

- **Free gates (0 tokens, every card):** `audit_translation.py` (markup fidelity), the NEW
  [`../audit_coverage.py`](../audit_coverage.py) (dropped/fabricated senses), and `nws_split.py`
  via `run_real_test.py audit` (NWS owner-map). Any flag → re-queue.
- **LLM judge (the only QA spend):** runs ONLY on Python-gate-flagged cards + a ~5–10 % random
  mistranslation sample. **Sonnet judges; Opus adjudicates ONLY its rejects** (`ok=false ||
  severity>=3`), Opus verdict final — see [`../../research/JUDGE_POLICY.md`](../../research/JUDGE_POLICY.md).
  Publishable cards spend no Opus tokens.

The earlier "Opus-judged-every-card" framing was the validation phase; "Sonnet-bulk/Opus-on-reject"
was the 2026-06-26 escalation policy; the per-card LLM judge itself is now dropped from the bulk path.

## Current preflight

Last local preflight: **2026-06-26**.

```powershell
cd RussianTranslation\src
python freq_route.py 8
python _pilot_gen_merged.py --manifest freq --root-split --limit 3
python verify_root_glue.py
```

Observed state:

- `scale_manifest.freq.json`: **43,968 / 106,082** PWG headwords are DCS-attested
  (**41%**).
- Frequency top 8: `sTA`, `BU`, `gam`, `yuj`, `as`, `i`, `vid`, `han`.
- Top 3 with `--root-split`: already generated locally (`0 to generate`), so the
  machine has the required rootmaps/sub-cards for `sTA`, `BU`, and `gam`.
- `verify_root_glue.py`: **ALL GATES PASS**; lossless round-trip, 0 secondary
  conjugation blocks still merged, 60 rootmaps with unique keyed subkeys.

The preflight writes only gitignored pilot artifacts except when code/docs are
changed intentionally.

## Prompt/gate nits — DONE, encoded in the harness (verify, don't re-apply)

These four were folded into the inlined prompt of
[`run_pilot_wf.js`](run_pilot_wf.js) and the audit loop; this is now a
**verification checklist**, not a to-do:

- ✅ keep German abbreviations such as `Bed.`/`Schol.` verbatim, never expand —
  `CONV` line + **HARD RULE 3**;
- ✅ render **every** PWG Nachträge patch — **HARD RULE 4** ("ALL RECORDS,
  INCLUDING NACHTRÄGE … dropping any single patch fails coverage"); inputs are
  assembled main+Nachträge by `_pilot_gen_merged.py`;
- ✅ treat `<is>...</is>` source italics as siglum text, never `{%...%}` gloss —
  `CONV` line + **HARD RULE 3**;
- ✅ `nws_split.py` owner-map gate — **HARD RULE 5** (authoritative pre-parsed
  owner map) + the deterministic auditor wired into `run_real_test.py audit`
  (quarantines misattribution → `*.merged.REJECTED.md`).

Also encoded (2026-06-26 literature-harvest port): Sanskrit-microstructure
rendering guidance (samāsa right-headedness, the *yad…tad* correlative map,
śāstric formulas, synonym-string cardinality, comma/semicolon sense-grouping,
manner/position forcing) as soft-judged guidance (judge check 7). Source tables:
[`../../glossaries/de_ru_translation_aids.md`](../../glossaries/de_ru_translation_aids.md).

## Window loop

Pick a small first window, e.g. **25–50 root/headword entries**, because the top
of the queue is giant-root-heavy. The manifest is ordered by production priority.

```powershell
cd RussianTranslation\src

# Refresh the frequency manifest if VisualDCS data changed.
python freq_route.py 20

# Ensure the next manifest slice has root-split inputs.
python _pilot_gen_merged.py --manifest freq --root-split --limit 50
```

Then set the Max workflow harness to the frequency manifest. **The committed
file ships as `SECTION = 'a'`** — you MUST edit these three lines before the run
(no guard catches a SECTION/manifest mismatch):

```js
const SECTION = 'freq'
const OFFSET = 0
const LIMIT = 50
```

Run the **optimized** harness `run_pilot_wf.opt.js` (dual-lane, translate-only — generated
per root from the committed `run_pilot_wf.js`, prompts byte-identical) in the interactive Max
workflow harness and save the JSON result as `wf_output.json`. The in-chat Workflow tool is not
sufficient because the harness reads local files with `node:fs`. Lanes:

- **sparse** card (≤30 `<ls>`): single-turn, inputs inlined, **no tools** — the cheap path for
  the ~43 k normal sub-cards.
- **dense** card (>30 `<ls>`, e.g. a lone over-budget head sense): multi-turn, reads its own
  files, no-abridge directive. Heads are pre-split into citation-light parts by `sense_chunks()`
  (`_pilot_gen_merged.py`, budget `HEAD_CIT_BUDGET=18`), so this lane is a rare fallback.
- 1 automatic retry per stage; `judge:null` (the free Python gates own bulk QA).
- The optimized translate agents explicitly run with `tools: []`; any `Read`
  use in a Max run means an outdated harness file is being used.

Audit the window — run **all three** free gates (zero tokens):

```powershell
# 1) NWS owner-map gate (quarantines misattribution → *.merged.REJECTED.md)
python src\pilot\run_real_test.py audit wf_output.json
# 2) Markup-fidelity gate (sigla ≥90% kept, Sanskrit ≥85% kept, Russian present where German gloss was)
python src\audit_translation.py
# 3) Sense-coverage gate (no silently dropped/fabricated senses)
python src\audit_coverage.py wf_output.json
```

Any NWS owner mismatch is quarantined as `*.merged.REJECTED.md`; a markup-fidelity failure
(lost sigla/Sanskrit or an empty card) or a coverage flag (COVERAGE-LOW/OVER) is likewise a
re-queue, not an accept. Only the re-queued (Python-flagged) cards plus a ~5–10 % sample go to
the LLM judge.

## Instrumentation

For each Max window, record:

- `OFFSET`, `LIMIT`, fresh units, rejected units, and successful merged cards;
- wall-clock minutes;
- Max-reported input/output/cache tokens if available;
- whether the weekly cap fired, and cumulative tokens at that moment.

Append the measurements to `PILOT_COST.md` §6. The point is to answer the
feasibility question: one Max seat over roughly two months vs a paid API bulk run.

## Done criterion

The frequency queue milestone is done when:

- every manifest entry in the target frequency window has a merged card or a
  glued nested article;
- zero `*.merged.REJECTED.md` files remain for that window;
- rootmap-backed giant roots have matching `*.NESTED.md` outputs;
- the cost/quota table has enough windows to estimate the run duration.
