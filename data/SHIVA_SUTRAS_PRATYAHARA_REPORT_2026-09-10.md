# ShivaSutras.xlsx / .docx — schema inspection, prior-art check, derived dataset (H4471)

_Created: 10-09-2026 · Last updated: 10-09-2026_

Source: [`yadisk:Panini/ShivaSutras.xlsx`](https://webdav.yandex.ru) +
`ShivaSutras.docx` (Yandex Disk, fetched via the `yadisk:` rclone remote —
see [Uprava memory 2026-09-07-yadisk-rclone-selfserve-palsule-rights-cleared.md](https://github.com/gasyoun/Uprava/blob/main/.claude/projects/Uprava/memory/2026-09-07-yadisk-rclone-selfserve-palsule-rights-cleared.md)).
Both files are **not** committed (rights not checked — unlike the Palsule
XLS, no MG clearance is on record for this source); only the derived
extraction below is.

## What the source actually is

The handoff mission asked to check for "list, sūtra text, numbering" — but
**the source is not a list of the 14 Māheśvara/Śiva Sūtras with text and
numbering at all.** `ShivaSutras.docx` is a Russian-language essay
explaining pratyāhāra notation (why the sūtras reorder the alphabet and
insert anubandha markers); `ShivaSutras.xlsx` is a **pratyāhāra range
table** — the 42 two/three-letter abbreviations (`aK`, `aC`, `iK`, `yaṆ`,
`haL`, ...) that the sūtras are used to construct, each expanded to its
ordered phoneme span. There is no sūtra-by-sūtra text or numbering (P.1–14)
anywhere in either file.

## Schema — `ShivaSutras.xlsx`

| Sheet | Dimensions | Content |
|---|---|---|
| `Ranges` | A1:BG52 | **The actual dataset.** Col 1 = an unexplained numeric tag (not a phoneme count — checked against the sheet's own worked example for `aK`); col 2 = pratyāhāra name; cols 3–59 repeat the same 57-symbol alphabet sequence (letters + anubandha markers) for every row. **Membership in a pratyāhāra's range is encoded by solid cell fill (`cell.fill.patternType == "solid"`), not by cell content** — every row has identical text in columns 3+, only the highlighting differs. 42 named pratyāhāra rows. |
| `Pictures` | A1:CT81 | Visual grid re-rendering the same alphabet table for the essay's diagrams (voiced/unvoiced/place-of-articulation layout). No new structured data over `Ranges`; not extracted. |
| `SandhiExamples` | B1:AX775 | Same alphabet grid repeated ~20× in IAST for worked sandhi-rule illustrations (708 non-empty rows), rule membership again via cell fill/color, not text. Not extracted — out of scope for a "trivial" pass; a future handoff could mine specific rule examples (e.g. `iko yaṇ aci`) if a use case needs them. |

## Prior-art check (done first, per mission)

| Candidate | Checked | Verdict |
|---|---|---|
| kosha `paninian-sutra-coverage-map` | [docs/data-statements/paninian-sutra-coverage-map.meta.md](https://github.com/gasyoun/kosha/blob/main/docs/data-statements/paninian-sutra-coverage-map.meta.md) | **No overlap.** Covers the 3,983 *Aṣṭādhyāyī* sūtras (P.1.1.1–8.4.68) via vidyut 0.4.0 `Data.load_sutras()` `Source.Ashtadhyayi`. Confirmed live: `vidyut.prakriya.Source` enum has no Śivasūtra/Māheśvara member (`Ashtadhyayi, Dhatupatha, Kashika, Kaumudi, Linganushasana, Phit, Unadipatha, Varttika` only) — the 14 Śiva Sūtras / pratyāhāras are not in vidyut's named enumeration at all. |
| VisualDCS | grepped for pratyāhāra/śivasūtra/māheśvara | No hits beyond incidental substring matches (`aK`, `aC` inside unrelated compound tokens). No pratyāhāra dataset present. |
| Sangram `grammar-lab-g1` | [Uprava REUSE_INDEX.md](https://github.com/gasyoun/Uprava/blob/main/REUSE_INDEX.md) row (repo not cloned locally) | "Grammar Lab Wave-1 topic graph (Whitney + Zalizniak root alternation / verbal morphology)" — verb morphology, not pratyāhāras. No overlap by description. |
| vidyut | `pip show vidyut` (0.4.0, installed) + `Source` enum introspection | No Śivasūtra/pratyāhāra data structure (see above). |
| kosha REUSE_INDEX.md / SanskritLexicography | grepped for pratyahara/sandhi/śivasūtra | Only unrelated sandhi-frequency and corpus datasets (`corpus-sandhi`, `gita-sandhi`, `sandhi-curriculum`) — none encode pratyāhāra ranges. |

**Verdict: genuine gap.** No existing dataset in kosha, VisualDCS, Sangram,
or vidyut encodes the pratyāhāra → phoneme-range mapping. The derived
extraction below is new.

## Derived dataset

- [`shiva_sutras_pratyahara_ranges.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/shiva_sutras_pratyahara_ranges.tsv) / [`.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/shiva_sutras_pratyahara_ranges.json) — 42 rows, one per pratyāhāra: `pratyahara`, `source_tag` (opaque, carried through unexplained), `span_length`, `phonemes_devanagari` (ordered, includes anubandha markers as printed, duplicates preserved e.g. the two `ण्` instances).
- Builder: [`build_shiva_sutras_pratyahara_ranges.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/data/build_shiva_sutras_pratyahara_ranges.py) — re-run after `rclone copy yadisk:Panini/ShivaSutras.xlsx data/_raw_local/`.
- Deliberately **not** attempted: stripping anubandha markers to get the "real" phoneme list per pratyāhāra (e.g. `aK` → 5 letters, not 7). That requires knowing which of the 57 symbols are markers vs. letters, which is domain judgment beyond a faithful transcription of what the spreadsheet encodes — left as a documented follow-up, not guessed.

## kosha registration — explicit skip verdict

The acceptance criterion allows "kosha manifest row **or explicit skip
verdict**." Skipping, for now:

1. kosha's dataset registration is a versioned, multi-file contract
   (`data/manifest/datasets.json` + per-dataset `MANIFEST.json` with
   sha256/rights/consumers + a `docs/data-statements/*.meta.md` + typically
   a `data-vX.Y.Z` release tag) — a different unit of work than this
   handoff's derived-file-in-SanskritLexicography scope, and not
   "trivial" effort.
2. kosha's main-tree checkout had 3 uncommitted tracked files (orphaned WIP
   from another session, flagged by the SessionStart hook) at the time of
   this run — landing a registration there needs its own clean worktree,
   not a same-pass addition from here.
3. Rights on `ShivaSutras.xlsx`/`.docx` are unconfirmed (unlike the
   Palsule XLS, no MG clearance is on record) — a kosha manifest row
   normally cites a rights class, which is undetermined here.

**Recommendation:** mint a follow-up kosha-scoped handoff
(`id: shiva-sutras-machine`) once rights are confirmed, pointing at this
report's derived TSV/JSON as the source-of-record.

_Dr. Mārcis Gasūns_
