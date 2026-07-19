_Created: 19-07-2026 · Last updated: 19-07-2026_

# PLAN — PWG data layers: card anatomy, formal schema, four extraction layers, German-side enrichment

**Repo:** [SanskritLexicography](https://github.com/gasyoun/SanskritLexicography) · **Subject:** PWG (Petersburger Wörterbuch / Böhtlingk–Roth) data layers · **Span:** 2026 H2 · **Handoff:** [H1350](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1350-Sonnet_SanskritLexicography_pwg-data-layers-anatomy-schema-extract_19.07.26.md)

This is the cover/index for a `/ask`-grade layered plan: a single unattended 5–8 h execution run that (1) reconciles the three existing PWG-card anatomy descriptions into one canonical reference, (2) authors the first-ever **formal** PWG grammar (RelaxNG over raw markup + JSON Schema over the parsed portrait) and runs it over all 123,366 records, (3) extends four extraction layers — citations, sense structure, cross-references, government — onto the existing OntoLex sidecar, and (4) turns the byproduct markup defects into staged csl-corrections change files (never a csl-orig PR).

The four layer docs this points at:

- **Roadmap** — [ROADMAP_SanskritLexicography_PWG_DATA_LAYERS_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/ROADMAP_SanskritLexicography_PWG_DATA_LAYERS_2026H2.md)
- **Architecture** — [ARCHITECTURE_SanskritLexicography_PWG_DATA_LAYERS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/ARCHITECTURE_SanskritLexicography_PWG_DATA_LAYERS.md)
- **Implementation** — [IMPLEMENTATION_SanskritLexicography_PWG_DATA_LAYERS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/IMPLEMENTATION_SanskritLexicography_PWG_DATA_LAYERS.md)
- **Verification** — [VERIFICATION_SanskritLexicography_PWG_DATA_LAYERS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/VERIFICATION_SanskritLexicography_PWG_DATA_LAYERS.md)

---

## 1. Goal (one paragraph)

Make the anatomy of a PWG card a **formally specified, machine-validated, queryable** object, and route the enrichment additively onto the German original — never into the German source text. Today the card's structure is described in three unreconciled places (a 24-element pedagogical list, a machine-measured tag census, and a working parser), enforced only by ad-hoc Python validators with no grammar. This wave produces one canonical anatomy reference, two real schemas that classify every record as pass-or-typed-failure, four extended extraction layers rolled into the existing OntoLex graph, and a staged (not shipped) set of upstream defect reports. The German markup in `csl-orig` is **read-only** throughout; "enrich the German" here means additive sidecar annotation on the shared `lemma/<key1>` spine (the PWG++ pattern, [H772](https://github.com/gasyoun/Uprava/blob/main/handoffs/README.md)), plus a formal grammar that describes the German markup without altering it.

## 2. Decisions taken (Phase-2 interview rulings)

Every fork a builder would hit was ruled up front. The execution agent trusts these without re-deriving them.

| # | Decision | Ruling | Rationale |
|---|----------|--------|-----------|
| D1 | What "enrich the German" means | **Sidecar overlay + formal PWG schema + anatomy synthesis doc.** No new text into csl-orig. | Additive annotation is zero-risk and already has infrastructure ([`export_lod.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/export_lod.py), H772). The formal schema *describes* the German markup; it does not modify it. |
| D2 | Extraction targets for this wave | **All four:** citations `<ls>`, sense structure + the `〉` fallout, cross-references (`s.`/`vgl.`), grammar/government (Rektion). | Each extends a partially-built asset rather than starting cold; together they cover the card's full apparatus. |
| D3 | What the RU pass feeds back | **Markup defects + sense-segmentation disagreements + OCR/text errors.** Not "keep the wall". | The translation pass reads every word; its byproduct defects are the highest-signal source-quality feed that exists. Bucket C has been 0 forever — this opens it. |
| D4 | Upstream delivery contract | **csl-corrections change files only.** No csl-orig PR; no auto-merge to any maintainer repo. MG runs [/cologne-batch-pr](https://github.com/gasyoun/claude-config/blob/main/commands/cologne-batch-pr.md) later. | csl-corrections takes agent commits (audit trail); csl-orig and maintainer-repo merges stay MG `@DECIDE`. Reconciles the "agent-gated" preference with the standing read-only rule. |
| D5 | Formal schema target | **Both** — RelaxNG over raw `<L>…<LEND>` markup **and** JSON Schema over the `microstructure.py` portrait. | RNG (source-facing) drives the upstream defect reports and matches the TEI header's `tei_all.rnc` lineage; JSON (internal) proves the parse is complete. |
| D6 | `〉` sense audit depth | **Full measure + quarantine, no requeue.** | Bounds the blast radius (how many RU-store rows were translated against merged segmentation) without spending scarce generation budget or colliding with the paused nominal lane / [H1209](https://github.com/gasyoun/Uprava/blob/main/handoffs/README.md) canary. |
| D7 | Sidecar overlay shape | **Extend the existing OntoLex graph** (`entry/<key1>/de` nodes on the `lemma/<key1>` spine). | One coherent, queryable graph; reuses `export_lod.py`; consistent with [LOD_GRAPH.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/LOD_GRAPH.md). |
| D8 | `<ls>` citation coverage method | **Extend `ls_source_map` + `pwgbib` resolver deterministically.** No LLM resolution of the tail. | Auditable, no synthesised sources (avoids the "repaired ≠ synthesised" trap, [FINDINGS §94/§95](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)). Realistic ceiling ~85–90%. |
| D9 | Wave-1 scope | **Everything in one long unattended run**, internally sub-ordered (anatomy doc → schemas → `〉` audit → extraction layers → defect staging). | The whole plan is deterministic-first, so it can run start-to-finish without a human. |
| D10 | Doc home | **`SanskritLexicography/docs/`** — co-located with `EntryAnatomy/`, `RussianTranslation/`, and FINDINGS. | Ownership clarity; the code these docs describe lives here. |
| D11 | Anatomy doc role | **Index + crosswalk; keep the three originals.** | Preserves each source's audience (teaching / machine / parser); adds a measured coverage matrix on top. |
| D12 | Generation budget | **Deterministic-first, with ONE bounded ≤50-card LLM sanity check** of the `〉` re-segmentation via DeepSeek (`--backend openai`, **no Anthropic key, ever**). | Keeps the run essentially offline; the single model step is gated and its network risk is isolated. |
| D13 | Schema pass-bar | **100% parse OR typed failure bucket; zero unclassified drops.** | The failure buckets *are* the upstream defect reports; a silent drop hides a complementary class ([FINDINGS §129/§130](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)). |

## 3. The autonomy contract (verbatim — governs the unattended run)

No human is reachable for 5–8 h. The execution agent is bound by the following:

**Ambiguity policy — default-and-log, never block.** On any unplanned ambiguity: pick the plan's marked default, or failing that the most conservative / read-only option; log the decision + rationale under `## 🧠 Dev Notes & Hypotheses` in [`.ai_state.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/.ai_state.md); press on. Never stall waiting for a human. Anything genuinely unresolvable is parked as a typed `@DECIDE` row — never acted on destructively.

**Stop conditions.** Halt (commit progress, write a resume note, stop) only on: (a) a git push rejection that `/branch-contention-recover` cannot resolve; (b) the single ≤50-card LLM sanity check failing to run (no backend / network) — skip that step, log it, continue with the rest; (c) any operation that would require writing to `csl-orig` or merging a maintainer-repo PR — park it, never do it. No other condition stops the run.

**Commit authority.** Per the handoff-scoped autonomy rule, H1350 authorizes commit → PR → merge **within SanskritLexicography** (author in a worktree off `origin/master`, push branch, open PR, auto-merge + delete branch). csl-corrections receives **change-file commits only** (its own PR/merge is a later human step). No exception.

**The fence — never touch (verbatim):**
1. **`csl-orig` is read-only.** Only `git log` / `git show`. Every source defect becomes a csl-corrections change file — never an edit, commit, or PR to csl-orig.
2. **No new csl-orig PR; no auto-merge to any maintainer repo** (csl-orig, csl-corrections, csl-devanagari). Those stay MG `@DECIDE`.
3. **Never mutate the RU store.** `pwg_ru_translated.jsonl` and its `.enriched`/`.quarantine` siblings are not rewritten. The `〉` audit quarantines by writing a **separate marker file**, never by rebuilding the store (supersede-mode rebuild once wiped overlays — [FINDINGS §9](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md)). *[Agent-applied conservative default, derived from the standing FINDINGS §9 rule — not an explicit interview ruling, but load-bearing.]*
4. **Do not launch the paused generation lanes** (nominal medium50, promote/requeue) and do not collide with the H1209 canary. This wave triggers no generation lane. *[Agent-applied conservative default, same basis.]*

## 4. Autonomy-readiness gate verdict

**PASS.** Every wave-1 deliverable has an architecture spec, ordered implementation steps, an acceptance criterion, and identified risks (see the four layer docs). Zero blocking forks remain — all 13 decisions above are ruled, and the two non-selected fence items are applied as conservative read-only defaults consistent with standing rules. Prior-art verdicts are recorded in the architecture doc (build-vs-reuse per piece); nothing scheduled rebuilds an existing asset. The autonomy contract covers the plausible ambiguities the audit surfaced (missing backend, malformed records, contention on the shared tree).

## 5. Starter line (paste into a fresh chat, then walk away)

```
Read C:\Users\user\Documents\GitHub\SanskritLexicography\docs\PLAN_SanskritLexicography_PWG_DATA_LAYERS_2026H2.md and execute it.
```

Run as Sonnet 5 (`claude-sonnet-5`) or higher; `cd C:\Users\user\Documents\GitHub` first. The handoff [H1350](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1350-Sonnet_SanskritLexicography_pwg-data-layers-anatomy-schema-extract_19.07.26.md) names the scope; this PLAN carries everything else.

_Dr. Mārcis Gasūns_
