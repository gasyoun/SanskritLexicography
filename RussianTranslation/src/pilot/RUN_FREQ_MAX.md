# Runbook — frequency queue on the Max workflow harness

Goal: scale the PWG→Russian production run in DCS-frequency order, with giant
roots split into single-pass units and re-glued after translation. This is the
post-judge path: the 38-unit freq test is complete, 37/38 were publishable, and
the lone sev-3 belongs to the NWS owner-row slip class that the deterministic
audit gate catches.

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

## One-time prompt/gate nits before the first Max window

Apply these in the Max harness prompt / review checklist before translating the
first production window:

- keep German abbreviations such as `Bed.` and `Schol.` verbatim; do not expand
  them into Russian prose;
- render **every** PWG Nachträge patch, even when it looks like a small addendum;
- treat `<is>...</is>` source italics as source/siglum text, not as `{%...%}`
  German gloss text;
- keep the `nws_split.py` check in the audit loop so idam-class owner-row swaps
  are rejected and re-queued.

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

Then set the Max workflow harness to the frequency manifest:

```js
const SECTION = 'freq'
const OFFSET = 0
const LIMIT = 50
```

Run `run_pilot_wf.js` in the interactive Max workflow harness and save the JSON
result as `wf_output.json`. The in-chat Workflow tool is not sufficient because
the harness reads local files with `node:fs`.

Audit the window:

```powershell
python src\pilot\run_real_test.py audit wf_output.json
```

Any NWS owner mismatch is quarantined as `*.merged.REJECTED.md`; the next prep
cycle should re-queue rejects instead of accepting them.

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

