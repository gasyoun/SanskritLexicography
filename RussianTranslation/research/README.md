# research/ — lexicographic design studies (gate the scale-up)

Comparative studies of the core Sanskrit dictionaries (PWG, PW, MW, GRA, AP90, SCH, FRI)
whose findings decide `pwg_ru`'s microstructure **before** the full translation scale-up.
Triggered by the frequency-first pivot (2026-06-23): the top cards are giant verbal
**roots** that don't survive a single pass, forcing the root-entry question, which opens
the broader "which convention do we follow?" set.

| Doc | Question | Status |
|---|---|---|
| [ROOT_ENTRY_ARCHITECTURE.md](ROOT_ENTRY_ARCHITECTURE.md) | nest / niche / split / run-on roots? | **DECISION made** (two modes: SPLIT for translation + glue to NESTED on demand) + handoff A to compare the dicts |
| [HANDOFF_sense_ordering.md](HANDOFF_sense_ordering.md) | historical / logical-semantic / etymological / frequency sense order? | handoff — read prefaces + probe `artha`/`dharma` |
| [HANDOFF_microstructure_conventions.md](HANDOFF_microstructure_conventions.md) | homonym / gloss-type / citation / run-on conventions per dict? | handoff — read prefaces + probe entries |

**Sources (all local):** OCRed prefaces in each sibling repo's `prefaces/` (PWG, PW(K),
MW, GRA, SCH; AP90/FRI = print front-matter); entry files in `csl-orig/v02/<dict>/<dict>.txt`.

**Execution model:** each handoff is self-contained (question · dicts · exact sources ·
method · output table · preliminary priors), runnable in a fresh chat or by an agent —
the project's handoff idiom (cf. `src/NWS_AUDIT_HANDOFF.md`). Findings feed back into the
merged-translate prompt + the (to-build) root segmenter/glue before scaling.


## Spawned as handoff chats (2026-06-23)
Each brief was spun off as its own cold background-task chat (one click to start in a
fresh worktree):
- **A — root architecture** → `task_740ea467`
- **B — sense ordering** → `task_2242dc13`
- **C — microstructure conventions** → `task_9b9ce8db`

Each chat reads its brief, the OCRed prefaces, and probe entries from `csl-orig/v02/`,
appends a `## RESULTS` section to its doc, and commits. Findings then fold into the
merged-translate prompt + the root segmenter/glue **before** the translation scale-up.
