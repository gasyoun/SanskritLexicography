# Manuals — SanskritLexicography

_Created: 10-07-2026 · Last updated: 11-07-2026_

The audience-specific manual set for this repository — **this directory is the
canonical set** (H604 ruling): depth lives here; the two root `MANUAL_*` sheets
below are thin index/hard-rules views that defer to it. **Pick the one that
matches why you're here** — each is a standalone deep reference; you don't need
to read the others.

| If you are… | Read | Language |
|---|---|---|
| **Operating or extending** the repo (maintainer / next agent) — conventions, the pipelines, the epistemic registries, "how not to break things" | [MAINTAINER_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/MAINTAINER_MANUAL.md) | English |
| A **lexicographer / DH researcher / historian of dictionaries** — the evidence-graded thesis, the paper pipeline, what's citable | [RESEARCHER_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/RESEARCHER_MANUAL.md) | English |
| A **Sanskrit student / learner** — the teaching material and what's usable today | [STUDENT_MANUAL_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/STUDENT_MANUAL_RU.md) | Русский |
| A **programmer / data engineer / NLP researcher** reusing the data — formats, encodings, traps, rights | [DATA_REUSE_MANUAL.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/DATA_REUSE_MANUAL.md) | English |
| An **agent session** (Claude/Codex) entering this shared tree — entry protocol, hard rules, canonical-doc index | [MANUAL_LEXICON_WORKSPACE_AGENTS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/MANUAL_LEXICON_WORKSPACE_AGENTS.md) (root, thin) | English |
| **The human owner** — repo map, monthly delta, human gates, account protocol | [MANUAL_LEXICON_WORKSPACE_HUMAN_RU.md](https://github.com/gasyoun/SanskritLexicography/blob/master/MANUAL_LEXICON_WORKSPACE_HUMAN_RU.md) (root, thin) | Русский |

Regeneration/refresh of this set is encoded in the
[/workspace-manual](https://github.com/gasyoun/claude-config/blob/main/commands/workspace-manual.md)
skill; the per-repo overlay it reads is
[PROFILE.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/PROFILE.md)
(subsystem deep-manual queue, language overrides, traps that must survive every
refresh). Set provenance + improvement backlog:
[README.meta.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/manuals/README.meta.md).

## What this repository is, in one paragraph

A **personal research-and-data workspace** for Sanskrit digital lexicography
(`gasyoun/SanskritLexicography`, branch `master` — *not* part of the
`sanskrit-lexicon` org). It has grown into ~12 subprojects — headword-list
analytics, two large LLM dictionary-translation pipelines (`mw_ru`, `pwg_ru`), a
Brill book draft, a paper pipeline, Russian syntax lectures, a reverse
dictionary, and a governance layer of nine append-only epistemic registries —
unified by one thesis: **evidence-graded lexicography** (a dictionary as a
layered evidence graph). Fuller orientation:
[README.md](https://github.com/gasyoun/SanskritLexicography/blob/master/README.md) ·
[ROADMAP_2026_2027.md](https://github.com/gasyoun/SanskritLexicography/blob/master/ROADMAP_2026_2027.md).

## Language convention

Manuals follow the repo rule — **language matches the audience**: the student
manual is in Russian (its readership); the maintainer, researcher, and
data-reuse manuals are in English (their readership). See the
[HANDOFF.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HANDOFF.md)
documentation conventions.

_Dr. Mārcis Gasūns_
