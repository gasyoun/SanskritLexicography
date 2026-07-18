# MAINTAINER_MANUAL.md — metadoc

_Created: 18-07-2026 · Last updated: 18-07-2026_

Companion record for [docs/manuals/MAINTAINER_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/MAINTAINER_MANUAL.md).

## Purpose & audience

Operator/extender orientation for the whole hybrid workspace: subproject map, the epistemic-registry layer and its upkeep, pipelines + rerun safety, CI / pre-commit / release discipline. Audience: the next maintainer or agent session operating the repo (not merely consuming its data).

## Provenance

Authored 10-07-2026 (H479/H535 quartet), consolidated 11-07-2026 (H604). Refreshed 18-07-2026 under [H1245](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1245-Fable_multi_big-manuals-estate-refresh-umbrella_18.07.26.md) against a 221-commit drift window: 9 fact-check findings fixed (release stance, CI job list incl. the docs-site pytest job + the weekly link-check move, FINDINGS §N-stability breach warning, book 12/14 chapters, papers A30–A58, 714 tracked RT files, dashboard build outputs, three-generators count, same-pass worktree removal).

## Verification

```
LAST_VERIFIED: 18-07-2026
VERIFIED_BY: Fable 5 (claude-fable-5), H1245
COMMANDS_SPOT_RUN: 0
```

No quoted command was executed this pass — the dashboard/build commands all regenerate tracked outputs (fenced out of a docs-only run); each was verified read-only against its script's argparse and the CI YAML instead.

## Improvement backlog

| # | Item | Status |
|---|---|---|
| 1 | FINDINGS duplicate-§N repair (§80/§86/§87 pairs, observed 18-07-2026) — rerun the H616 renumber, then soften the §3 breach warning | open (queued via GTD, H1245) |
| 2 | When the dashboards gain a third registry renderer or the release cadence changes, §3/§7 need a same-PR update | open (standing) |

## Known limitations

- Counts (tracked files, chapters, papers range) are as-of-stamped 18-07-2026 and decay; the registries and [.ai_state.md](https://github.com/gasyoun/SanskritLexicography/blob/master/.ai_state.md) are the live truth.

## Intended use / known misuse

**For:** session-start orientation before operating/extending the repo. **Misuse:** treating it as the data-consumer guide (that is [DATA_REUSE_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/DATA_REUSE_MANUAL.md)) or as live state (that is `.ai_state.md`).

## Maintenance & sunset plan

Refreshed by [/workspace-manual](https://github.com/gasyoun/claude-config/blob/main/commands/workspace-manual.md) passes (PROFILE-bound); no automated staleness check yet — H1246's detector will consume the Verification block above. Retired only if the manual set itself is restructured.

## Deprecation status

`active`

## Revision history

| Date | Change | By |
|---|---|---|
| 10-07-2026 | Subject manual authored (H479/H535); consolidated H604 11-07-2026 | Fable 5 (`claude-fable-5`) / Opus 4.8 (`claude-opus-4-8`) |
| 18-07-2026 | Metadoc created (H1245 estate refresh); subject manual fact-checked by a dedicated agent, all 9 findings fixed same pass | Fable 5 (`claude-fable-5`) |

_Dr. Mārcis Gasūns_
