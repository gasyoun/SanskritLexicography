- H5706: **the two Tier-0 safety defects of the 2026-10 repair queue are closed — the EN
  citation-TM refuses the vālakhilya block, and `--merge` no longer writes without `--apply`.**
  **(1, FINDINGS §524 / h2361)** for RV mandala 8, sūkta ≥ 49 the Griffith EN column of
  `griffith_en_1896.json` is displaced against its own row key (eleven vālakhilya hymns keyed
  inline in the corpus, appended in the English source), so `lookup('ṚV.','8,60,1',lang='en')`
  returned `status=hit` with a fluent verse of the **wrong hymn** (19.8 % stanza agreement over
  8.49–8.103 vs 87–94 % elsewhere; 678 of 10 552 stanzas). The EN lane now returns the typed
  miss `en-numbering-unverified` — no canonical_id, no griffith_location, exactly the
  refuse-don't-guess shape `_rama_gorresio` already uses — until the asset is repaired upstream
  (h2361 recipe step 2). Pinned: 8,49/8,60/8,103 refused for both `ṚV.`/`RV.` prefixes; the
  8,48,1 pre-block control still hits; 1.1.1 / 10.90.1 unchanged; the RU lane untouched (corpus
  `#ru`/`#sa` agree throughout). **(2, FINDINGS §611.2 / the H3663 accident)** `--apply` used to
  gate only the `--ready-partial-report` path, so a plain `--merge` **promoted for real**.
  Since H5706 `--apply` is the ONE write switch for every single-mode lane: plain `--merge`
  refuses (`REFUSED: --merge is dry-run by default since H5706`); `--merge --apply` writes with
  the automatic `.premerge.*.bak`. Unchanged and selftest-pinned on the real `main()` over
  fixture stores: the H2089 default-store interplay (`--promotion-id` /
  `--allow-raw-default-merge` / `PWG_ALLOW_RAW_MERGE_DEFAULT_STORE`), the §611.1 defect guard
  (`requeue.defect.keys.txt` = the promotable verdict), and the refusal-gate order (duplicate
  identity → content mass → row shrink). H3654/H3663 recipes and the pilot RUN_LOG annotated to
  the corrected contract; the 2026-10 repair-queue plan landed under `docs/`. No pipeline
  version bump: the `script` component was already drifted on `master` before this change and
  no promoted row's content changes (write-gating only).
