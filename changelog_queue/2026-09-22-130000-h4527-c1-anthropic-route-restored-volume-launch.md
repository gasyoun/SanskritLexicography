_Created: 22-09-2026 · Last updated: 22-09-2026_

- H4527: **`c1` is back on the Anthropic route, and its first five-card volume launch promoted four
  cards.** On a human ruling («restore Anthropic») the six keys the 20-09 z.ai switch had added were
  removed from the `c1` profile's `settings.json` on MSI (original kept beside it as a `.bak`). Canary
  `h4527-canary-220922` went GO. Run `h4527-vol-220922` (`--cohort-path --cohort-width 1`,
  `--max-calls 7`) accepted and promoted `gl_ana`, `hasita`, `jaw_ayus` and `ku_rqal_i` (store
  11 524 → 11 534, 10 sense rows). `kast_ur_i` failed the audit (`untranslated_braced_german_gloss` ×2)
  and waits as a requeue. Every call of the run carries Anthropic response ids (`msg_011C…`/`req_011C…`),
  while the 20-09 transcript carries z.ai's (`msg_202609…`, no request id), which proves the 20-09
  acceptance card `darv_i` is GLM 5.3 output under a Sonnet label. Exit 1 follows the H5209 contract
  (requeue backlog non-empty), not FINDINGS §642. Packet:
  `pwg_ru/h4527/H4527_C1_ANTHROPIC_ROUTE_RESTORED_VOLUME_LAUNCH_22-09-2026.md`; the ledger entry
  `H4527_C1_ZAI_QUOTA_429_CANARY_2026-09-21` is now `fixed`. 8 paid calls (1 canary, 2 probe legs,
  5 cards).
