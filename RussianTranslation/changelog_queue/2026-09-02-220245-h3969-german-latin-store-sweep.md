- H3969: German markers **outside** `<ab>` in the store's `ru` field swept German→Latin —
  **141 substitutions over 75 rows** in `src/pwg_ru_translated.jsonl`, resolved through
  `store_path.canonical_store()` (the main checkout, never the worktree copy).
  By token: `Akk`→`Acc.` ×110 · `Instr`→`Ins.` ×22 · `Lok`→`Loc.` ×8 · `Präs`→`Praes.` ×1.
  By layer: `nws` 58 rows · `sch` 15 · `pwg` 2. Store row count unchanged (11,519 before
  and after); the `de` German source column and every `<ab>`, `<ls>` and `{#…#}` span
  untouched. Pre-sweep class check 142 hits / 76 rows → post-sweep 1 hit / 1 row.
  Declared residue: `Ausgabe` ×1 (`key1=nI`, layer `pwg`) — a German prose clause, not a
  grammatical marker, so it has no Bucket B Latin form and a routing to `Ed.` would be an
  editorial call, not a marker substitution. Sweep is reproducible via
  `src/h3969_german_latin_sweep.py` (census · `--apply` · `--selftest`, 13 cases).
  H3959's scoped 120/65 grew to 142/76 because that census listed only
  `Akk`/`Lok`/`Ausgabe`/`Präs`; `Instr` is the same German-only class with the same H2849
  target and was swept with them. Releases the H3947 TM-mirror-refresh gate.
