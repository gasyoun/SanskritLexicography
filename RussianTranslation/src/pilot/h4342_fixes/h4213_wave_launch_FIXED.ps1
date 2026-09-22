$ErrorActionPreference = 'Continue'
$Log = 'C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation\src\pilot\output\h4213_wave_launch.log'
function L($m) { Add-Content -Path $Log -Value ('[' + (Get-Date -Format 'HH:mm:ss') + '] ' + $m) }
Set-Location C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation\src\pilot
$env:AUTOSPLIT_LS_BUDGET = '6'
$PY = 'C:\Python314\python.exe'
# H4342 (d): a fixed 'h4213can' prefix regenerates the SAME window id (h4213can02)
# on every attempt once next_free_index() sees no leftover files for that prefix --
# so a prior attempt's surviving artifact (partial cleanup, in-flight lock, an
# auto-restarted retry) makes the retry FAIL: headless window id already exists,
# not a transient error. A timestamp-unique prefix makes every attempt land on a
# window id no earlier attempt could have used, independent of cleanup succeeding.
$CanaryStamp = Get-Date -Format 'MMddHHmmss'
$CanaryPrefix = 'h4213can' + $CanaryStamp
L '=== h4213 wave launch start ==='
L ('canary prefix this attempt: ' + $CanaryPrefix)
# Best-effort tidy of any earlier attempts' canary artifacts (harmless if none exist;
# no longer load-bearing for correctness now that the id itself cannot collide).
Get-ChildItem -Path output\coordinator\artifacts -Directory -Filter 'h4213can*' -ErrorAction SilentlyContinue |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
# Step 1: probe c1
$out = & $PY max_account_orchestrator.py --db max_orchestrator.sqlite init --account 'c1=D:\ClaudeTools\profiles\claude1\.claude' --call-reservation output\h4213_call_ledger.json --run-id ('h4213-probe-' + (Get-Date -Format 'HHmmss')) 2>&1 | Out-String
L ('probe: ' + (($out.Trim() -replace "`n", ' | ')))
if ($out -match 'validation failed') { L 'STOP: c1 probe failed (still limited/logout). No spend.'; exit 2 }
L 'probe GO - c1 validated'
# Step 2: drop stale prepared leases so keys free up (legacy static id, harmless no-op
# once the id is timestamp-unique, kept for leases left over from before this fix)
& $PY -c "import json; p=r'C:\Users\user\Documents\GitHub\SanskritLexicography\RussianTranslation\src\pilot\output\coordinator\state.json'; s=json.load(open(p, encoding='utf-8')); s['leases']=[x for x in s.get('leases',[]) if (x.get('id') not in ('no_pwg_w10','h4213can02','no_pwg_w11')) and not x.get('id','').startswith('h4213can')]; json.dump(s, open(p,'w',encoding='utf-8'), ensure_ascii=False, indent=1)"
L 'stale leases dropped'
# Step 2b: remove orphaned artifacts dirs for dropped leases (window-id existence guard)
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue output\coordinator\artifacts\h4213can02, output\coordinator\artifacts\no_pwg_w10, output\coordinator\artifacts\no_pwg_w11
L 'orphan artifacts removed'
# Step 3: re-prep canary (1 card: _atmavat) -- unique prefix per attempt (H4342 fix)
Set-Content -Path output\no_pwg_w1.still_null.txt -Encoding utf8 -Value '_atmavat~~h0_zz_pw'
$o = & $PY no_pwg_scale_plan.py --headless --headwords 1 --window-size 1 --limit-windows 1 --prefix $CanaryPrefix --manifest output\h4213_canary_plan.json --profile-slot c1 --config-dir 'D:\ClaudeTools\profiles\claude1\.claude' 2>&1 | Out-String
L ('canary prep: ' + (($o.Trim() -replace "`n", ' | ')))
if ($LASTEXITCODE -ne 0) { L 'STOP: canary prep failed'; exit 3 }
# Step 4: canary run via mao staged-run
$o = & $PY max_account_orchestrator.py --db max_orchestrator.sqlite staged-run --plan output\h4213_canary_plan.json --coord-dir output\coordinator --coordinator coordinator.py --cwd C:\Users\user\Documents\GitHub\SanskritLexicography --call-reservation output\h4213_call_ledger.json --run-id ('h4213-canary-' + (Get-Date -Format 'HHmmss')) --max-calls 4 --stop-after 1 --report output\h4213_canary_report.json --events output\h4213_canary_events.jsonl --census output\h4213_canary_census.json 2>&1 | Out-String
L ('canary run: ' + (($o.Trim() -replace "`n", ' | ')))
$canaryPlan = Get-Content output\h4213_canary_plan.json -Raw | ConvertFrom-Json
$wf = $canaryPlan.windows[0].workflow_output
if (-not $wf -or -not (Test-Path $wf)) { L ('STOP: no canary wf_output at ' + $wf); exit 4 }
L ('canary wf_output: ' + $wf)
# Step 5: judge receipt
$o = & $PY canary_gate.py judge $wf --receipt output\h4213_canary_receipt.json 2>&1 | Out-String
L ('judge: ' + (($o.Trim() -replace "`n", ' | ')))
if ($o -notmatch 'GO') { L 'STOP: canary NO-GO'; exit 5 }
# Step 6: re-prep bulk wave (6 keys)
$keys = "apr_apta~~h0_zz_pw`nas_a_dya~~h0_zz_pw`nasa_mskfta~~h0_zz_pw`navy_ahata~~h0_zz_pw`navyagra~~h0_zz_pw`nb_ahlika~~h0_zz_pw"
Set-Content -Path output\no_pwg_w1.still_null.txt -Encoding utf8 -Value $keys
$o = & $PY no_pwg_scale_plan.py --headless --include-residuals --headwords 6 --window-size 6 --limit-windows 1 --prefix no_pwg_w --manifest output\h4213_wave_plan.json --profile-slot c1 --config-dir 'D:\ClaudeTools\profiles\claude1\.claude' 2>&1 | Out-String
L ('wave prep: ' + (($o.Trim() -replace "`n", ' | ')))
if ($LASTEXITCODE -ne 0) { L 'STOP: wave prep failed'; exit 6 }
# Step 7: restore original still_null
Move-Item -Force output\no_pwg_w1.still_null.txt.h4213bak output\no_pwg_w1.still_null.txt
L 'still_null restored'
# Step 8: bulk run (stop before promote)
$o = & $PY bounded_staged_run.py --plan output\h4213_wave_plan.json --coord-dir output\coordinator --coordinator coordinator.py --cwd C:\Users\user\Documents\GitHub\SanskritLexicography --db max_orchestrator.sqlite --events output\h4213_wave_events.jsonl --max-calls 12 --cost-ceiling 6 --execute --stop-before-promote --max-windows 1 --canary-receipt output\h4213_canary_receipt.json 2>&1 | Out-String
Add-Content -Path $Log -Value $o
L '=== launch script end (bulk result above; promotion intentionally NOT run - stop-before-promote) ==='
