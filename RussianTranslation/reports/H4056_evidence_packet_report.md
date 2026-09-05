# H4056 — PWG evidence-demonstration packet: build + scratch vote-to-store replay

_Created: 05-09-2026 · Last updated: 05-09-2026_
Executor: OxAlpha (opencode / `z-ai/glm-5.3-flash`) · Handoff: H4056 · **Voting is NOT requested.**

## What this is

The 04-09-2026 ruling: before any human vote is requested, demonstrate
Sanskrit ↔ Russian/German alignment, actual TM use, and effective use of the
Sanskrit–Russian and teaching corpora — as evidence, in scratch copies. This
packet is that demonstration. It is **not** a voting instrument, carries no
approval request, and has **no production apply route**.

## Packet identity

| field | value |
|---|---|
| sheet_id | `h4056-evidence-packet-2026-09-05` |
| content_hash | `sha256:234772d2b800b3be00989f86248f3192c258157f81f6506fc51d84f1e8c11a4c` |
| lock | [review/locks/h4056-evidence-packet-2026-09-05.lock.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/review/locks/h4056-evidence-packet-2026-09-05.lock.json) (gate `H4056-DEMO`, metadata-only) |
| viewable artifact (local, gitignored) | `RussianTranslation/review/h4056_evidence_packet_sheet.html` |
| manifest | [reports/H4056_evidence_packet_manifest.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H4056_evidence_packet_manifest.json) |
| replay receipt | [reports/H4056_scratch_replay_receipt.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H4056_scratch_replay_receipt.json) |
| store (read-only) | `pwg-ru-data/tm/pwg_ru_translated.jsonl`, sha256 `79d72dbcb4b3…`, 11 519 rows |
| provider calls | **0** |
| canonical store writes | **0** (sha256 identical before/after replay) |

## Eligibility funnel (real gates, none weakened)

Measured over the live store with `review_residue_gate` + the H3948
segmentation quarantine recomputed read-only
(`pwg_four_tier_store_impact.scan_corpus/changed_keys`; 123 366 corpus records
→ **331 changed key1**, matching the committed H3948 report exactly):

| stage | rows |
|---|---:|
| store rows | 11 519 |
| not `ai_translated` (already decided) | 5 |
| no stable subcard/sense_tag identity | 0 |
| corpus-evidence quarantine (no evidence_summary / contradicts / no supports) | 1 768 |
| German source missing | 3 |
| German residue or machine flags D1/D3/D4 | 1 644 |
| H3948 segmentation quarantine | 2 515 |
| **machine-eligible** | **5 584** |

Ten cards were drawn round-robin across sorted roots
(`build_g5_review_sheet.pick`, deterministic, no RNG) — identities in the
manifest (review_id = positional `row:` id + stable `subcard:#sense_tag` tail;
printed homonym `h` travels beside the key per H3751; content digest16 per
card). No unresolved-segmentation or semantic-quarantine card is presented.

## Per-card evidence rendered

Print-facing Russian (abbreviation render-translation per batch1v2) beside the
German source, citation apparatus (`<ls>` Cologne links, printed page refs),
KEWA etymology advisory, NWS tag legend, and a machine-verdict panel:
mechanical gate results, corpus evidence (supports: kna/koch/kow/smirnov —
Sanskrit–Russian corpora; silent: teaching corpora; contradicts: none —
quarantined rows were excluded upstream), generation provenance
(model_version/generator/input hashes), and a TM-lookup result.

## Actual TM use (offline, zero provider calls)

The card TM was **built from the store** with
`pilot/translation_memory.build` into a scratch file, then every packet card
was resolved through the real content-addressed `lookup`
(`ru:input_raw_sha256`, canonical denylist applied read-only, 7 addresses):
**10/10 HIT** — each card's masked source re-arriving today would reuse the
stored translation with zero provider calls, trust/reuse policy intact.

## Vote-to-store replay (scratch only — 8/8 checks pass)

In a temp scratch dir holding copies of the lock, the review CSV, and the
store (`reviewer` = `H4056-scratch-replay (agent, not human)`):

1. **Default route PARKS** — an export bound to the `H4056-DEMO` lock reaches
   `apply_decisions`, which refuses to route it (rc=2): the packet has no
   production apply path by construction.
2. **Explicit G5 route applies in scratch** (rc=0; `run_batch validate_review`
   green: 3 print-ready decisions).
3. **Stable-key routing** — every review_id carries exactly its
   approve→approved / reject→reject / defer→needs_review decision + reviewer.
4. **Stale-hash negative control** — an export with a tampered
   `content_hash` is refused (`content_hash mismatch`) and leaves the CSV
   byte-identical.
5. **No accidental production writes** — canonical store sha256 unchanged;
   replay entirely under the system temp dir.

Prior sheets and locks were not touched; no existing vote is invalidated (new
sheet_id, no lock collision; the committed locks directory gained exactly one
new metadata-only file).

## Not claimed

Not a human approval, not publication-as-approval, not evidence of live
translation quality, no gold labels fabricated, Wave-1 dump untouched, no
hosted version (the HTML embeds unpublished store RU/DE and stays gitignored;
if it is ever hosted it must keep the visible «голосование не запрашивается»
banner and disabled controls it already carries).

## Agent-owned readiness action

Recorded as an active GTD row in
[Uprava GTD_NEXT_ACTIONS.md](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md):
an agent lane is to assess this packet's alignment/corpus/TM evidence and
report readiness (or defects) — the decision to request human votes stays with
the human.

_Dr. Mārcis Gasūns_
