# H5263 — the /pwg-live-gate step 2 canary on c1 (ONE paid call) + mechanical judge.
# Run on the Windows box after canary_manifest_build.py printed the sha below.
param([string]$Sha = '5385e180f015514a9d53673ce2f5bda24e8f545b30176e4e8b96d5a558dfe678')
cd C:\Users\user\Documents\GitHub\SanskritLexicography-h5263-88487\RussianTranslation
$env:CLAUDE_CONFIG_DIR = 'D:\ClaudeTools\profiles\claude1\.claude'
$d = 'C:\Users\user\.pwg_h5263\canary'
$run = 'h5263-canary-20260924'
python src\pilot\headless_worker.py "$d\execution_manifest.canary.json" --output "$d\out.canary.json" --status-out "$d\status.canary.json" --only-profile c1 --max-agents 1 --timeout 600 --max-calls 3 --manifest-sha256 $Sha --preflight "$d\preflight.canary.json" --call-reservation "$d\calls.canary.json" --run-id $run 2>&1 | Select-Object -Last 3
python src\pilot\canary_gate.py judge "$d\out.canary.json" --receipt "$d\canary_receipt.json" --manifest "$d\execution_manifest.canary.json" --status "$d\status.canary.json" --call-reservation "$d\calls.canary.json" --run-id $run 2>&1 | Select-Object -Last 12
