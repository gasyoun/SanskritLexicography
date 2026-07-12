# Four-account Max orchestration runbook

<!-- markdownlint-disable MD013 MD036 -->

_Created: 12-07-2026 · Last updated: 12-07-2026_

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
2. One RU `no_pwg` card with no presplit requirement passes the headless worker, audit, and promotion with a store delta. Headless v1 refuses presplit cards instead of bypassing Workflow self-heal.
3. Four disjoint jobs run concurrently.
4. Kill a dispatch pass, recover, and verify no duplicate promotion.
5. Record logs, reset behavior, exact model, clean rate, and store delta in the H818 audit.

_Dr. Mārcis Gasūns_
