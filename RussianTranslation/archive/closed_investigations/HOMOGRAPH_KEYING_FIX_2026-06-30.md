# Homograph keying — FIXED (supersedes the handoff)

**Date:** 2026-06-30. The homograph multiplication in the bridge preview is **fixed**, verified
on `dA` and `vah`. This supersedes [`H032-Sonnet_RussianTranslation_homograph_keying_30.06.26.md`](H032-Sonnet_RussianTranslation_homograph_keying_30.06.26.md)
(no handoff needed) and corrects the "blocked, no discriminator" assessment in the bridge
follow-up note.

## The insight that unblocked it

The blocker was framed as "the **assembled** side has no homonym discriminator." True — and the
assembled same-`key1` entries are redundant (identical dict glosses) and segmented differently
from PWG homonyms, so they can't be matched. **But the homonym never needed to come from the
assembled side** — the **store** side has a clean homonym: each row's `subcard` key carries it
(`dA~~h3_..` → `h3`). So instead of attaching `translations[key1]` to every assembled entry
(the multiplication) and trying to fragile-match the assembled side, the fix attaches the
translations **once per `key1`** and labels each translation sense with its **store** homonym.

## What changed ([`src/export_interop.py`](src/export_interop.py))

1. `card_glosses(card, translations, emitted)` — translations are emitted **once per `key1`**
   (an `emitted` set, shared per export). `emitted=None` keeps the legacy behaviour.
2. Each translation sense is labelled by `store_homonym(row)` → `n="h3-review-2"`, so per-homonym
   attribution is preserved from the clean store side.
3. **Unique `xml:id`** per same-`key1` entry (`pwg-dA`, `pwg-dA-2`, …) — also fixes the prior
   invalid-TEI duplicate-ID collision (all homographs were `xml:id="pwg-dA"`).
4. Threaded through `export_tei` / `export_ontolex` / `export_reverse_index`.

## Verified on the 2 real cases

Preview export (`--review-status ai_translated`) over a `dA`+`vah` fixture:

| | before (multiplied) | after (fixed) |
|---|---|---|
| total `approved_translation` senses | ~1,785 (345×4 + 135×3) | **480** (345 + 135 = the actual store rows) |
| `xml:id`s | 4× `pwg-dA`, 3× `pwg-vah` (collide) | `pwg-dA`, `pwg-dA-2/3/4`, `pwg-vah`, `pwg-vah-2/3` (unique) |
| translation senses on `pwg-dA` / siblings | 345 on each of 4 | **345 on `pwg-dA`, 0 on siblings** |
| homonym labels | none | `h0..h9` (dA), `h0..h2` (vah) on each sense |

`window_selftest` 18/18 (new `test_export_translation_dedup`).

## Production safety + a remaining minor item

- **Unchanged in production:** the default export gate is still `{approved, human_reviewed}`
  (0 rows until G5 review), so this fix only affects *attribution* of preview/approved rows.
- **Separate, pre-existing:** the *structural* dict glosses still repeat across the redundant
  sibling entries (`pwg-dA-2/3/4` carry the same koch glosses). That is a different
  redundancy (the assembled cards overlap) and is out of scope here — this fix targets the
  translation multiplication + the duplicate IDs. Collapsing redundant sibling entries is an
  edition-modelling choice for the renderer stage.
