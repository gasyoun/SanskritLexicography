# Runbook — translate the full a-section on the Max workflow harness

Goal: translate all **12,156** a-section cards (PWG+PW+SCH+PWKVN+NWS merged) to Russian
via the `run_pilot_wf.js` workflow on your **interactive Claude Max** session, with the
deterministic F12 gate quarantining any NWS-attribution slip. Decided 2026-06-23
("hand bulk to Max workflow"). The Agent-tool path validated the pipeline (5/6 clean,
`as` with 60 NWS owners CLEAN); this scales it.

## Why the Max harness (not the Workflow tool)
`run_pilot_wf.js` reads its inputs with `node:fs`. The in-chat Workflow tool runs
scripts with **no filesystem access**, so it can't run this script — but your
interactive Max workflow harness can. Free on Max; built for volume.

## Prerequisites (all DONE as of 2026-06-23)
- Inputs regenerated **with the owner map**: `python src/_pilot_gen_merged.py --manifest a`
  (each NWS card's `pilot/input/<safe>.raw.txt` now ends in a "PRE-PARSED OWNER MAP" section).
- `run_pilot_wf.js` consumes it — **HARD RULE 5** = "one row per owner-map entry, owner
  verbatim, no re-derivation" (kills F12 by construction). CONV carries Guard 7 (de/fr/en).
- `pilot/output/scale_manifest.a.json` = coverage-first order (12,156 keys).
- Card + judge schema: `schemas/pwg_ru_final_card.schema.json`.

## The per-window loop
Pick a window size `N` (suggest **50–100** — bigger = fewer manual runs; the workflow
pipelines internally at the concurrency cap). For each `OFFSET` = 0, N, 2N, … < 12156:

```sh
# 1) PREP — sets OFFSET/LIMIT inside run_pilot_wf.js + lists fresh vs protected
python src/pilot/run_real_test.py prep N OFFSET

# 2) TRANSLATE+JUDGE — run run_pilot_wf.js on your Max workflow harness;
#    save its JSON result to wf_output.json   (the script returns {results:[{key,card,judge}]})

# 3) AUDIT — render each card → pilot/output/<safe>.merged.md, run the F12 gate,
#    quarantine slides, print judge pass-rate + NWS-CLEAN count
python src/pilot/run_real_test.py audit wf_output.json
```

`prep` skips cards already rendered and never overwrites the protected hand-authored
cards (`aMSa`, `anna`, `ap`). `audit` is the gate: any fresh card whose NWS owners
disagree with the deterministic `nws_split` parse is moved to
`<safe>.merged.REJECTED.md` and the command exits non-zero — so the **next** `prep`
re-queues it automatically. Run one clean-up sweep at the end to re-translate the
rejects.

## Tracking progress
```sh
# rendered so far / 12,156  + quarantined count
python - <<'PY'
import os, json
from src.safe_filename import safe_name   # or run from src/ and `from safe_filename import safe_name`
man=[e['key1'] for e in json.load(open('src/pilot/output/scale_manifest.a.json',encoding='utf-8'))]
out=set(os.listdir('src/pilot/output'))
done=sum(1 for k in man if safe_name(k)+'.merged.md' in out or k+'.merged.md' in out)
rej=sum(1 for f in out if f.endswith('.merged.REJECTED.md'))
print('rendered %d/%d (%.1f%%) | quarantined %d'%(done,len(man),100*done/len(man),rej))
PY
```

## Done criterion
All 12,156 have a `<safe>.merged.md` and **zero** `*.merged.REJECTED.md` remain
(rejects cleared by the end-sweep). Then assemble the section
(`assemble.py`) and move to human review (`run_batch.py review_csv` /
`gold_review_csv.py`).

## Notes / gotchas
- **Don't hand-guess `safe_name`** — compute it (`safe_name('As')='_as'`, not `_a_s`).
- A few generic-gloss cards may show gate **abstentions** ("unlocated") — those are
  not failures (the owner is verbatim from the map); only "MISATTRIBUTION" quarantines.
- Window quota: on Max, large windows can hit the weekly cap — if so, drop `N` and
  resume; everything is resumable off the rendered `.merged.md` set.
