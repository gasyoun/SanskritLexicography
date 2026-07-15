# Four-account Max orchestration runbook

<!-- markdownlint-disable MD013 MD036 -->

_Created: 12-07-2026 · Last updated: 15-07-2026_

This dispatcher runs ordinary commands under four isolated profiles. It does not translate by itself or bypass coordinator/audit/promotion gates.

## Provision

The owner authenticates; agents never handle credentials.

```sh
sudo install -d -o pwg-factory -g pwg-factory /opt/factory/acc{1,2,3,4} /var/lib/pwg-ru /var/log/pwg-ru
CLAUDE_CONFIG_DIR=/opt/factory/acc1 claude /login
# repeat through acc4
```

`init` checks both `claude auth status` and a minimal live exact-model call without exposing account metadata. Then confirm every profile with the repository's ≥5 KB latency probe before translation; the minimal call proves credentials, while the larger probe gates usable performance.

```sh
python3 src/pilot/max_account_orchestrator.py --db /var/lib/pwg-ru/max.sqlite init \
  --account acc1=/opt/factory/acc1 --account acc2=/opt/factory/acc2 \
  --account acc3=/opt/factory/acc3 --account acc4=/opt/factory/acc4
```

Prepare coordinator leases normally. Preparation now writes both the legacy Workflow JS and a canonical headless execution manifest. Import only prepared leases; the importer rejects overlapping keys and non-RU jobs.

```sh
python3 src/pilot/coordinator.py prepare LEASE_ID
python3 src/pilot/max_account_orchestrator.py --db /var/lib/pwg-ru/max.sqlite import-coordinator \
  --coord-dir src/pilot/output/coordinator \
  --cwd /opt/factory/SanskritLexicography/RussianTranslation \
  --lease-id LEASE_ID
python3 src/pilot/max_account_orchestrator.py --db /var/lib/pwg-ru/max.sqlite run-once
python3 src/pilot/max_account_orchestrator.py --db /var/lib/pwg-ru/max.sqlite record-done \
  --coordinator src/pilot/coordinator.py \
  --cwd /opt/factory/SanskritLexicography/RussianTranslation
python3 src/pilot/max_account_orchestrator.py --db /var/lib/pwg-ru/max.sqlite status
```

Install `deploy/pwg-ru-max-orchestrator.{service,timer}` for recurring dispatch. Startup refuses missing or unauthenticated profiles. A rate limit returns the job to pending and parks the account until the parsed epoch, or five hours if no reset is machine-readable. Every attempt gets immutable runner/status logs plus manifest/result hashes. `recover` returns crash-stranded jobs to pending. Promotion remains serialized through `coordinator.py promote-ready --gen-model-version claude-sonnet-5`.

## Acceptance

1. Four profile probes succeed.
2. One RU `no_pwg` card passes the headless worker, audit, and promotion with a store delta. Headless v2 implements Workflow-parity batch retry/split plus presplit fragment heal/stitch semantics.
3. Four disjoint jobs run concurrently.
4. Kill a dispatch pass, recover, and verify no duplicate promotion.
5. Record logs, reset behavior, exact model, clean rate, and store delta in the H818 audit.

## Windows 100-headword gate

The owner first creates and logs in a dedicated Max profile (the agent never
handles the login URL, code, cookie, or token):

```powershell
$env:CLAUDE_CONFIG_DIR = 'C:\pwg-factory\max1'
claude /login
python src/pilot/max_account_orchestrator.py --db C:\pwg-factory\max.sqlite init `
  --account max1=C:\pwg-factory\max1
```

Prepare the deterministic next 100 headwords without calling Claude:

```powershell
python src/pilot/no_pwg_scale_plan.py --headwords 100 --window-size 20 `
  --limit-windows 5 --dry-run --prefix h818_win100_w --start-index 1 `
  --manifest src/pilot/output/h818_windows100_plan.json
```

After the owner logs one or more Max accounts into dedicated profiles, repeat
with `--headless --coordinator-dir <dir>`, initialize each of those profiles, and
run. `staged-run` now fans across **N validated profiles** (one or more) instead
of hard-capping at a single account: it probes every validated profile and
dispatches disjoint jobs across the whole healthy fleet. `--max-accounts N` caps
the fleet size; `--drop-unhealthy` is the explicit opt-in described below.
Initializing exactly one profile (N=1) reproduces the original single-profile
Windows-100 path byte-for-byte.

```powershell
python src/pilot/max_account_orchestrator.py --db <db> staged-run `
  --coord-dir <dir> --cwd <RussianTranslation> `
  --coordinator src/pilot/coordinator.py --plan <prepared-plan.json> --stop-after 2 `
  --report src/pilot/output/windows100_readiness.json `
  --events src/pilot/output/run_events.jsonl `
  --census src/pilot/output/bug_census.json --run-id h818-win100
# restart boundary: rerun the same command with --resume and without --stop-after
```

The command refuses unauthenticated profiles and runs a ≥5 KB exact-model probe
on **each** validated profile (the D-K two-phase warm-up + measured split per
account, so the acceptance census carries exactly one measured latency sample per
profile, never an inflated count). The default policy is **STOP-on-any-NO-GO**:
the first profile whose probe fails or exceeds the health ceiling aborts the whole
run (an honest fleet NO-GO), matching acceptance criterion #1. `--drop-unhealthy`
is the explicit opt-in to instead drop the failing profile, park it, and proceed
on the healthy subset (still requiring at least one healthy profile). `report`'s
`probe_latency_ms` becomes a per-profile `name → measured_ms` map. The run then
records/audits each window, promotes only its audit-clean subset under the global
promotion lock, and emits a GO only when the exact headword/subcard census is
accounted, every window has a positive canonical-store delta, no hard failure or
duplicate exists, ≥80% of cards are audit-clean, and fidelity rejects stay <5%.
`run_events.jsonl` is the credential-safe append-only join across probe, model
attempts, audit and promotion; `bug_census.json` is regenerated from it.

The deterministic 100-word slice currently contains no presplit card. Before the
100-word run, build a manifest for a known heavy fixture and exercise fragment
recovery without promotion:

```powershell
python src/pilot/max_account_orchestrator.py --db <db> presplit-canary `
  --manifest <heavy-presplit-manifest.json> --output <canary-output.json> `
  --status <canary-status.json> --events src/pilot/output/run_events.jsonl `
  --run-id h818-presplit-canary
```

The command refuses a manifest without `presplit_keys`, requires exactly one
validated Max profile and a successful ≥5 KB probe, and returns GO only when the
presplit route completes with no residual. Canary output is never imported or
promoted.

_Dr. Mārcis Gasūns_
