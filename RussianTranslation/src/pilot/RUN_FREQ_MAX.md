# Runbook — frequency queue on the Max workflow harness

Goal: scale the PWG→Russian production run in DCS-frequency order, with giant
roots split into single-pass units and re-glued after translation. This is the
post-judge path: the 38-unit freq test is complete, 37/38 were publishable, and
the lone sev-3 belongs to the NWS owner-row slip class that the deterministic
audit gate catches.

**Judge policy (implemented 2026-06-26, [`../../research/JUDGE_POLICY.md`](../../research/JUDGE_POLICY.md)):**
translate = **Sonnet**; **Sonnet judges every card**; **Opus re-judges ONLY the
rejects** (`ok=false || severity>=3`) and its verdict is final. Publishable cards
(sev 1–2) spend no Opus tokens — the weekly-quota headroom that makes the run
feasible. Per batch also run the periodic ~5 % Opus audit of clean-passed cards
(`judge_disagreements.py`) until it is wired into the loop. The earlier
"Opus-judged" framing was the validation phase, not the bulk policy.

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

Run `run_pilot_wf.js` in the interactive Max workflow harness and save the JSON
result as `wf_output.json`. The in-chat Workflow tool is not sufficient because
the harness reads local files with `node:fs`.

Audit the window — run **both** gates:

```powershell
# 1) NWS owner-map gate (quarantines misattribution → *.merged.REJECTED.md)
python src\pilot\run_real_test.py audit wf_output.json
# 2) Fidelity gate (sigla ≥90% kept, Sanskrit ≥85% kept, Russian present where German gloss was)
python src\audit_translation.py
```

Any NWS owner mismatch is quarantined as `*.merged.REJECTED.md`; the next prep
cycle should re-queue rejects instead of accepting them. A fidelity-gate failure
(lost sigla/Sanskrit or an empty card) is likewise a re-queue, not an accept.

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

