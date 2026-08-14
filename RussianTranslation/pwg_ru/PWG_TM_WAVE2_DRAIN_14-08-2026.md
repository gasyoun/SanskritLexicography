# PWG TM — Wave-2 5,000-key drain (H2727)

_Created: 14-08-2026 · Last updated: 14-08-2026_

Grok 4.6 (`grok-4.6`). Drain of the H2721 frozen queue under `pwg.tm.wave2.defaults.v1`. Wave 1 dumps were not written.

## Status: WAVE ACCOUNTED

| Check | Result |
|---|---|
| Queue / processed / missing source | **5000 / 5000 / 0** |
| Extracted fragments | **197916** |
| Accounted (promoted + quarantine) | **197916** |
| Silent drops | **0** |
| Promoted | **162107** |
| Quarantine | **35809** |
| Manifest pin | `f9fdb4ff6155f2e945d4f26d5fdb07a7f96b36ad48537b5a0be43988b0335ff8` |

Fill: deterministic 158807 · source reuse 3138 · sense-merge 420 · drafted 0 · unfilled 35551.

One refill against the new Wave-2 lexicon: **0** moved (leftovers are new unique glosses/senses, not denylist-eligible reuse). No second LLM repair.

Cost: 0 billed tokens. Cost is **not evaluable**, not zero. `XAI_API_KEY` unused; `--live` not passed.

Independent n=400 was **not** run (would need a non-Grok-4.6 judge).

Resume after a `MemoryError` on window 146 (append of large JSONL) used `--resume` + cheaper `fragment_id` scan. Remaining 328 keys finished.

Dumps stay gitignored under `release/pwg_tm_canonical/wave2_b/`. Compact recon: [`wave2_b_receipt/reconciliation.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/release/pwg_tm_canonical/wave2_b_receipt/reconciliation.json).

## Proof

```text
python src/pwg_tm_generate.py --verify
python src/pwg_tm_generate.py drain --route grok-4.6 --manifest release/pwg_tm_canonical/priority_5000_w2.manifest.json --queue release/pwg_tm_canonical/priority_5000_w2.jsonl --out-dir release/pwg_tm_canonical/wave2_b --window-size 32
python src/pwg_tm_generate.py drain --route grok-4.6 --resume --out-dir release/pwg_tm_canonical/wave2_b --manifest ... --queue ...
python src/pwg_tm_generate.py refill --route grok-4.6 --out-dir release/pwg_tm_canonical/wave2_b
```

_Dr. Mārcis Gasūns_
