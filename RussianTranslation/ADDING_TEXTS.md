# Adding new corpus texts later

The corpus lexicon is incremental and resumable — new parallel texts can be added
any time without rebuilding. One command does it: [add_corpus_text.py](src/add_corpus_text.py).

## Quick path

```sh
# 1. Put the verse-aligned text here:
#    SamudraManthanam/web/corpus_builder/jsonl/<work>.jsonl
# 2. Align + stratify + audit it:
python src/add_corpus_text.py <work> [--genre "..."] [--date YEAR] [--workers 8]
```

That validates the source, stratifies it (genre + date), aligns **only** that
work with DeepSeek (skipping anything already done), appends to
`corpus_lexicon.jsonl`, and runs the integrity audit + coverage delta.

## Input format

One JSONL line per segment, in `SamudraManthanam/web/corpus_builder/jsonl/`:

```json
{"group": "<work>:<passage>", "seg": "sa",    "text": "<Sanskrit verse, IAST>",        "passage": "1.1"}
{"group": "<work>:<passage>", "seg": "ru",    "text": "<Russian translation, Cyrillic>", "lang": "ru"}
{"group": "<work>:<passage>", "seg": "comm1", "text": "<commentary note, Cyrillic>",    "lang": "ru"}
```

- `group` must be **globally unique** — prefix it with the work name (`mahabharata-19:1.1`).
- The Russian (`seg=ru`, `seg=comm*`) **must contain Cyrillic**. A `…` / `—`
  placeholder is treated as *untranslated* and skipped (this is the guard that
  prevents the fabrication failure — see [failures/FAILURE_GALLERY.md](failures/FAILURE_GALLERY.md) F1).
- `seg=sa` Sanskrit may be IAST; it is normalized to SLP1 (`form_key`) for keying.

## Stratification (genre + date)

Every text needs a stratum so its senses harvest period-correct Russian. Two ways:

1. **Preferred — add a rule** in [build_strata.py](src/build_strata.py) `RULES`
   (a filename regex → genre [Renou], Dharmamitra date + 95% CI). This keeps the
   classification reproducible and versioned. Periods are: `Vedic`,
   `Epic / early-Classical`, `Classical`, `Medieval` (Ṛgveda is part of Vedic).
2. **Ad-hoc** — pass `--genre "Kāvya — ..."` and `--date 600`; the script injects
   a one-off stratum (marked `source: manual`). Convert it to a rule later.

## If the text is also a PWG `<ls>` source

To make the new text *harvestable by citation* (a PWG sense citing it pulls its
stratum's Russian), add it to [src/build_ls_map.py](src/build_ls_map.py) `CANON`
(map the PWG `<ls>` abbreviation → a `corpus_prefix` matching the work name) and
re-run `python src/build_ls_map.py`. Otherwise it still contributes to the
SLP1-keyed lexicon, just not via citation matching.

## Re-running / safety

- **Idempotent**: re-running aligns only groups not yet in the lexicon.
- **Cost**: ~$/alignment is small; one mid-size text (~1–2k groups) is a few
  dollars. Run during DeepSeek off-peak to halve it.
- **Liveness**: a long alignment can be reaped by the environment — re-run to
  resume (nothing is lost). For a big batch, drive it with
  [src/_supervise.py](src/_supervise.py) (auto-restart) and watch with
  `python src/_watch.py <pct>`; verify it is *writing* via file mtime, not just
  row count (see FAILURE_GALLERY F7).
- After adding texts, regenerate dependent artefacts if needed: the post-build
  period re-stamp, and `build_ls_map.py` if `<ls>` coverage changed.
