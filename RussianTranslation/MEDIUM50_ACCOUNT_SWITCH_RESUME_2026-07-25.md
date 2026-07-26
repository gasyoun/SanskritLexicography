# Medium50 offline prep — ready for headless (NO --max-agents)

_Created: 25-07-2026 · Last updated: 25-07-2026_

## Gate status (this session)

- c4 gate-0: **NO-GO** (warmup classification=auth; prior measured latency also over ceiling)
- c2 gate-0: **NO-GO** (warmup auth)
- Direct claude -p on c1/c2/c4/c5/default: **HTTP 403 Request not allowed** for all models tried
- **No canary, no paid translation, no store write.**

## Offline prep completed

- Merged 5-layer inputs for **48** medium50 keys (excl. yuvan/ftvij)
- Bare-key aliases for gen_opt_harness2 input_paths (safe_name vs key stems)
- Harnesses + execution manifests for **5** windows

- h1447-m50-w1: 3 keys — nakzatra, sarvatra, sakft
- h1447-m50-w2: 12 keys — Srama, vAhana, zoqaSan, SudDi, prajYA, prAtar, retas, patnI, nUnam, samIpa, vfzwi, AcArya
- h1447-m50-w3: 11 keys — dIkzA, rAtra, rAzwra, Bezaja, vyavasTA, spfS, Ahuti, vicitra, maraRa, vinASa, Bakza
- h1447-m50-w4: 11 keys — jAtavedas, yajus, aDama, SvAsa, aDastAt, saKi, darBa, Akfti, prasU, idAnIm, SoDana
- h1447-m50-w5: 11 keys — vraRa, prada, vadana, sAhasra, martya, sadana, BrU, yOvana, loman, zoqaSa, divA

## Resume (when live-gate is LIVE_GO again)

1. Fresh /pwg-live-gate (health + canary). Canary may use --max-agents 1 (single synthetic key only).
2. For **each** production window, run headless **without** --max-agents:

```powershell
python src/pilot/headless_worker.py src/pilot/output/coordinator/artifacts/h1447-m50-w1/execution_manifest.h1447-m50-w1.json --output src/pilot/output/h1447-m50-w1.wf_output.json --status-out src/pilot/output/h1447-m50-w1.status.json --only-profile c4 --timeout 180
# keys (3): nakzatra, sarvatra, sakft

python src/pilot/headless_worker.py src/pilot/output/coordinator/artifacts/h1447-m50-w2/execution_manifest.h1447-m50-w2.json --output src/pilot/output/h1447-m50-w2.wf_output.json --status-out src/pilot/output/h1447-m50-w2.status.json --only-profile c4 --timeout 180
# keys (12): Srama, vAhana, zoqaSan, SudDi, prajYA, prAtar, retas, patnI, nUnam, samIpa, vfzwi, AcArya

python src/pilot/headless_worker.py src/pilot/output/coordinator/artifacts/h1447-m50-w3/execution_manifest.h1447-m50-w3.json --output src/pilot/output/h1447-m50-w3.wf_output.json --status-out src/pilot/output/h1447-m50-w3.status.json --only-profile c4 --timeout 180
# keys (11): dIkzA, rAtra, rAzwra, Bezaja, vyavasTA, spfS, Ahuti, vicitra, maraRa, vinASa, Bakza

python src/pilot/headless_worker.py src/pilot/output/coordinator/artifacts/h1447-m50-w4/execution_manifest.h1447-m50-w4.json --output src/pilot/output/h1447-m50-w4.wf_output.json --status-out src/pilot/output/h1447-m50-w4.status.json --only-profile c4 --timeout 180
# keys (11): jAtavedas, yajus, aDama, SvAsa, aDastAt, saKi, darBa, Akfti, prasU, idAnIm, SoDana

python src/pilot/headless_worker.py src/pilot/output/coordinator/artifacts/h1447-m50-w5/execution_manifest.h1447-m50-w5.json --output src/pilot/output/h1447-m50-w5.wf_output.json --status-out src/pilot/output/h1447-m50-w5.status.json --only-profile c4 --timeout 180
# keys (11): vraRa, prada, vadana, sAhasra, martya, sadana, BrU, yOvana, loman, zoqaSa, divA

```

Or one-shot plan after rebuild: python src/pilot/h1447/build_plan.py then
python src/pilot/bounded_staged_run.py --plan ... --max-windows 5 --stop-before-promote --execute
with **no** --max-agents on multi-key windows.

3. Audit each window; /pwg-window-close only after clean audit.

_Do not copy canary --max-agents 1 onto multi-key windows (H1610/H1618)._
