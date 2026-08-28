# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Layout

**Single-context repo.** Domain terms and architecture decisions live at the repo root:

```
/
├── CONTEXT.md
├── docs/adr/
│   ├── 0001-<decision>.md
│   └── 0002-<decision>.md
└── ...
```

Neither `CONTEXT.md` nor `docs/adr/` exists yet; they are created lazily (see below). In the meantime, the de-facto domain orientation docs are [`CLAUDE.md`](../CLAUDE.md) (repo conventions, encodings, key semantics, hazard notes), [`docs/manuals/`](../docs/manuals), and [`ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md`](../ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md) (research framing).

## Before exploring, read these

- **`CONTEXT.md`** at the repo root (when it exists).
- **`docs/adr/`**: read ADRs that touch the area you're about to work in.

If any of these files don't exist, **proceed silently**. Don't flag their absence; don't suggest creating them upfront. The `/domain-modeling` skill (reached via `/grill-with-docs` and `/improve-codebase-architecture`) creates them lazily when terms or decisions actually get resolved.

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in `CONTEXT.md`. Don't drift to synonyms the glossary explicitly avoids.

Until a glossary exists, keep to the vocabulary already fixed in [`CLAUDE.md`](../CLAUDE.md) — e.g. **key1** (normalized computational key) vs **key2** (printed-source-faithful key), **pwg_ru** (the PWG→RU pipeline), **card** (one translated dictionary entry), **L0/TMX** (translation-memory lanes).

If the concept you need isn't in the glossary yet, that's a signal: either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/domain-modeling`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0007 (event-sourced orders), but worth reopening because…_
