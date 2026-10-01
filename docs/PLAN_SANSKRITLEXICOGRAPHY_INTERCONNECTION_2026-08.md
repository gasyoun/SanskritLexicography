# Plan — SanskritLexicography interconnection, 2026-08

_Created: 26-08-2026 · Last updated: 26-08-2026_

SanskritLexicography's slice of the spine-interconnection programme. Programme index:
[PLAN_SPINE_INTERCONNECTION_2026H2.md](https://github.com/gasyoun/Uprava/blob/main/docs/PLAN_SPINE_INTERCONNECTION_2026H2.md).

Architecture and verification are **not** restated here (ruling F13) — they are identical for
all fourteen repos and live once in Uprava:

- [ARCHITECTURE_SPINE_INTERCONNECTION.md](https://github.com/gasyoun/Uprava/blob/main/docs/ARCHITECTURE_SPINE_INTERCONNECTION.md) — the five attachment points and the rules governing them
- [IMPLEMENTATION_SPINE_INTERCONNECTION_W1.md](https://github.com/gasyoun/Uprava/blob/main/docs/IMPLEMENTATION_SPINE_INTERCONNECTION_W1.md) — execution order, per-handoff steps, isolation, risks
- [VERIFICATION_SPINE_INTERCONNECTION.md](https://github.com/gasyoun/Uprava/blob/main/docs/VERIFICATION_SPINE_INTERCONNECTION.md) — the five gates and what "done" means

**Nothing here has executed.** The handoff below is 🟡 queued and runs only when a human
launches it.

## Why SanskritLexicography is in scope

One of the two knowledge hubs, already at 100 with all eight registries and 88 README hub links. Its fork count in this pass was **zero** — it needs no wiring. The single change is outward-facing.

## Measured baseline and target

| | Value |
|---|---|
| Wiring score, 26-08-2026 | **100** / 100 |
| Target after this plan | **100** / 100 |
| How the target is reached | Hold at 100. Any drop is a regression, not a trade-off. |

Measured by [`tools/interconnection_audit.py`](https://github.com/gasyoun/Uprava/blob/main/tools/interconnection_audit.py); full row in
[data/interconnection_audit_2026-08-26.json](https://github.com/gasyoun/Uprava/blob/main/data/interconnection_audit_2026-08-26.json);
report [AUDIT_REPO_INTERCONNECTION_2026-08-26.md](https://github.com/gasyoun/Uprava/blob/main/docs/AUDIT_REPO_INTERCONNECTION_2026-08-26.md).

The score counts artefacts, not whether they are true. It is **report-only** by ruling F2 and no
handoff closes on it — verification Gates 2 to 4 are what actually decide, and Gate 4 is read by
a human.

## Rulings that apply here

| Fork | Ruling |
|---|---|
| F6 | pwg-ru-data gets a minimal kit — one `CLAUDE.md` carrying the rights fence and code-home pointer. |

Full rulings table with every fork:
[ASK_BATCH_STAGING_REPO_INTERCONNECTION_2026-08.md](https://github.com/gasyoun/Uprava/blob/main/ASK_BATCH_STAGING_REPO_INTERCONNECTION_2026-08.md) Phase 2.

## What this plan does

1. Make RussianTranslation's role as the **code home** for the private pwg-ru-data store explicit, so a session landing in that data repo is pointed back here (F6).
2. Do not add registry files, do not restructure hub rows, and do not touch the 14 uncommitted tracked files on `master` — that is separate orphaned WIP (H1238) needing its own recovery.

## Handoff

- [H3564 (Sonnet 5) — interconnect sanskritlex hold codehome pointer](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3564-Sonnet_SanskritLexicography_interconnect-sanskritlex-hold-codehome-pointer_26.08.26.md) · trivial · 🟡 queued

## Autonomy contract

The launching agent may create the files named above, add hub rows, open and merge its PR,
remove its worktree and close its handoff row — without asking.

It must stop and ask if a local `FINDINGS.md` cannot be given two genuine findings (the
documented fallback is to drop the file and take the pointer line, recorded not silent), if a
corpus row would carry an unmasked snapshot or quote a sample, or if a second speculative edge
becomes necessary. It must never turn the wiring score into a failing gate, commit to
`csl-orig`, or add the seven non-FINDINGS registries.

## Open @DECIDE

None. Every fork touching SanskritLexicography was ruled in sitting 1 on 26-08-2026, so the autonomy gate
passes and nothing in the wave-1 path stalls on a human.

_Dr. Mārcis Gasūns_
