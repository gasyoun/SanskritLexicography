# REUSE_MAP.md — metadoc

_Created: 11-11-2026 · Last updated: 11-11-2026_

Companion record for [RussianTranslation/REUSE_MAP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/REUSE_MAP.md).

## Purpose & audience

Canonical inventory of every Russian Sa→Ru reuse asset available to the `pwg_ru`
pipeline and how to consume each — read before re-investigating what already
exists (the map's own 05-07-2026 scout premise), and now also the
availability/restore record of record: §7 carries the verified Git-LFS restore
recipe, size/SHA-256 receipts, consumer demonstrations and honest per-host
availability for the restricted corpus and the seven authority/specialist
glossaries.

## Provenance

Authored 05-07-2026 (H184 reuse-source wiring); extended 26-07-2026; §3
consume-only correction + §7 availability/restore receipts added 11-11-2026
under [H8040](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H8040-OxAlpha_SanskritLexicography_reuse-corpus-availability-recovery_11.11.26.md)
(PR [#2504](https://github.com/gasyoun/SanskritLexicography/pull/2504)),
replacing `build_tmx.py`'s withdrawn "build it first" advice for the
NOT-rebuildable `corpus_lexicon.jsonl`.

## Verification

```
LAST_VERIFIED: 11-11-2026
VERIFIED_BY: MiMo V2.6 Flash (mimo-v2.6-flash), H8040
COMMANDS_SPOT_RUN: 7
```

H8040 (11-11-2026): corpus restored from `gasyoun/pwg-ru-data` Git-LFS →
290,543,363 bytes, SHA-256 `9f3d852f1f1424c275af2cc1823dab1b561e649320e597d3cab013068ccc4072`
(byte-identical to the Uprava `shadow_assets.jsonl` row `corpus_lexicon`);
seven authority/specialist mirrors restored and `corpus_gate` reports
`evidence_status=ok`; `build_tmx --sample 500` validates (500 `<tu>`, exit 0);
independent acceptance verifier re-ran all 12 checks PASS.

## Known limitations

- Rights: the corpus and specialist glossaries are restricted/evidence-only —
  this map documents restore and consumption, never redistribution.
- Per-host availability rows are dated observations; re-probe before trusting
  them on a new host (the §7 `D:`/`guhya` lines were themselves corrected by
  live probes on 11-11-2026).
