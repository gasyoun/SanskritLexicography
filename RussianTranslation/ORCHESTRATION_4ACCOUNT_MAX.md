# Four-account Max orchestration runbook

_Created: 12-07-2026 · Last updated: 12-07-2026_

This dispatcher runs ordinary commands under four isolated profiles. It does not translate by itself or bypass coordinator/audit/promotion gates.

## Provision

The owner authenticates; agents never handle credentials.

```sh
sudo install -d -o pwg-factory -g pwg-factory /opt/factory/acc{1,2,3,4} /var/lib/pwg-ru /var/log/pwg-ru
CLAUDE_CONFIG_DIR=/opt/factory/acc1 claude /login
# repeat through acc4
```

Confirm every profile with the repository's ≥5 KB probe before translation.

```sh
python3 src/pilot/max_account_orchestrator.py --db /var/lib/pwg-ru/max.sqlite init \
  --account acc1=/opt/factory/acc1 --account acc2=/opt/factory/acc2 \
  --account acc3=/opt/factory/acc3 --account acc4=/opt/factory/acc4
```

Each job is an argv JSON array. Enqueue only a proven adapter whose output feeds `coordinator.py record-output`; a Workflow JS file is not itself a `claude -p` prompt.

```sh
python3 src/pilot/max_account_orchestrator.py --db /var/lib/pwg-ru/max.sqlite enqueue \
  --external-id LEASE_ID --cwd /opt/factory/SanskritLexicography/RussianTranslation \
  --output /var/lib/pwg-ru/LEASE_ID.runner.json \
  --argv-json '["python3","src/pilot/PROVEN_ADAPTER.py","LEASE_ID"]'
python3 src/pilot/max_account_orchestrator.py --db /var/lib/pwg-ru/max.sqlite run-once
python3 src/pilot/max_account_orchestrator.py --db /var/lib/pwg-ru/max.sqlite status
```

Install `deploy/pwg-ru-max-orchestrator.{service,timer}` for recurring dispatch. A rate limit returns the job to pending and parks the account until the parsed epoch, or five hours if no reset is machine-readable. `recover` returns crash-stranded jobs to pending. Promotion remains serialized through `coordinator.py promote-ready --gen-model-version <exact-model>`.

## Acceptance

1. Four profile probes succeed.
2. One RU `no_pwg` card passes the adapter, audit, and promotion with a store delta.
3. Four disjoint jobs run concurrently.
4. Kill a dispatch pass, recover, and verify no duplicate promotion.
5. Record logs, reset behavior, exact model, clean rate, and store delta in the H818 audit.

_Dr. Mārcis Gasūns_
