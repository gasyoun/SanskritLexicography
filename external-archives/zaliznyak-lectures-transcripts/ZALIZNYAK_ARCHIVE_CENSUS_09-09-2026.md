# А.А.Зализняк archive — text-layer census, classification, index (09-09-2026)

_Created: 09-09-2026 · Last updated: 13-09-2026_

**Verifier pass, 13-09-2026 (independent session, OxAlpha
`zai-coding-plan/glm-5.3-flash` — the H4358 `{class: data}` gate):**

1. **Format census re-derived from the frozen listing** — every count in the
   table below reproduces exactly (txt 266 / srt 200 / json 192 / ans 179 /
   html 178 / mp4 130 / docx 64 / mkv 41 / webm 29 / vtt 13 / tsv 13 / pdf 4 /
   mp3 261; 1,570 objects, 461 media). Topic tally from the committed index
   reproduces exactly: 108 / 66 / 62 / 33 / 2 / 1 = 272 groups.
2. **Rebuild reproducibility FIXED** — `build_census.py`'s `csv.writer`
   emitted CRLF, so the documented rebuild did not byte-match the committed
   LF index (content was identical). Now `lineterminator="\n"`; rebuild is
   **byte-identical** to [transcript_index.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/external-archives/zaliznyak-lectures-transcripts/transcript_index.tsv).
3. **Sample filenames de-personalised** — `osankina-` prefix dropped from all
   five samples (mission rule: uploader names stay in the index, not in the
   published sample; sample *contents* were already name-free — grep-verified).
4. **Count correction** — total text-layer objects is **1,109**
   (1,570 − 461), not the 1,192 first printed.

**Update 10-09-2026:** the kosha manifest row proposed below (§ "Proposed
kosha manifest row") is now landed — [kosha PR #551](https://github.com/gasyoun/kosha/pull/551)
(merged), registering `zaliznyak-lectures-transcripts` in kosha's own
`data/manifest/datasets.json`.

Handoff [H4473](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4473-OxAlpha_SanskritLexicography_zaliznyak-transcripts_09.09.26.md).
Source: private Yandex.Disk remote `yadisk:ААЗализняк-архив` (rclone WebDAV
remote already configured on this machine, credentials at
`~/.secrets/yadisk.env`) — **not** vendored into any git repo; this document
and [`transcript_index.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/external-archives/zaliznyak-lectures-transcripts/transcript_index.tsv)
are the derived, committable layer.

## What the archive is

101.3 GiB / 1,570 objects across recordings and transcripts of the late
academician А.А.Зализняк (Andrei Zaliznyak) — public lectures on Russian
historical linguistics, Novgorod birch-bark documents, **and Sanskrit/Vedic
grammar** (he also lectured on Sanskrit syntax and the Ṛgveda at MSU), split
across two independent uploader channels (**Алексей Головастиков**,
**Анна Осанкина** — both public YouTube-channel operators, not private
individuals; names appear only as folder labels, per the mission's privacy
note). No personal data beyond these two public attributions was found in
any sampled file.

## Format census (whole archive, all folders)

| ext | count | what it is |
|---|---|---|
| `txt` | 266 | plain transcript text — either a whisper.cpp flat dump (one paragraph) or, in `таймкоды-*` folders, a **speech-timecode list only** (no text, see below) |
| `mp3` | 261 | audio (media, out of scope for this census) |
| `srt` | 200 | SubRip subtitle transcript (timestamped, whisper.cpp output) |
| `json` | 192 | whisper.cpp structured output — full model/run metadata (`ggml-medium`, `language: ru`) + per-segment `{timestamps, offsets, text}` array |
| `ans` | 179 | **whisper.cpp plain-text-with-timestamps dump** (`[hh:mm:ss.mmm --> hh:mm:ss.mmm]  text`) — the mission's speculation ("srt=json+ans suggests quiz/answer data") is **refuted**: `.ans` is an ASR artifact, not quiz-answer data; see `samples/rv1034-27nov2010.ans` |
| `html` | 178 | `ansi2html`-rendered terminal capture of the whisper.cpp CLI run (same text as `.txt`/`.srt`, wrapped in a dark-terminal HTML skin) |
| `mp4` | 130 | video (media, out of scope) |
| `docx` | 64 | **manuscript pages of a print book** ("Популярные лекции для юношества" vol. II) at various proofreading stages (`после_первой_читки` / `после_третьей_читки` / `после_предвёрстки` = "after first/third proof read" / "after pre-layout") — not ASR output |
| `mkv` | 41 | video (media) |
| `webm` | 29 | video (media) |
| `vtt` | 13 | WebVTT subtitle transcript — present only for 13 items in Головастиков's folder that carry **Sanskrit/Vedic** lecture titles (`Строй-ведийского-языка`, `Грамматический-строй-санскрита`, …) — professionally captioned (credits a subtitle editor), distinct from the whisper.cpp auto-transcripts |
| `tsv` | 13 | same 13 Sanskrit/Vedic items — a `start\tend\ttext` flat table, same content as the `.vtt` |
| `pdf` | 4 | scans, in `прочее/` (miscellaneous), not further classified here |

**Total text-layer objects: 1,109** (1,570 objects − 461 media = 1,109; the
1,192 first printed on 09-09 was an addition slip, corrected in the verifier
pass 13-09-2026).

## Folder → channel → format map

| Folder | Objects | Content |
|---|---|---|
| `текст-канал-Алексей-Головастиков` | 614 | per-lecture `.ans/.html/.json/.srt/.txt` (129 lectures × ~5 files); 13 of these lectures **also** carry `.tsv`+`.vtt` (the Sanskrit/Vedic subset, professionally captioned) |
| `текст-канал-Анна-Осанкина` | 357 | same 5-format pattern, 69 lectures — heavily Sanskrit/Vedic/Ṛgveda-titled (`Разбор-RV-1034`, `Строй-ведийского-языка`, `Грамматический-строй-санскрита`) |
| `таймкоды-речи-канал-Анна-Осанкина` | 69 | **timecode-only** `.txt` — a bare list of `hh:mm:ss - hh:mm:ss` speech-segment boundaries, no transcript text at all (see `samples/timecodes-sanskrit-root-jR.txt`) — looks like a pre-ASR diarization/pause-detection pass, one per lecture matching the same 69 basenames as `текст-канал-Анна-Осанкина` |
| `обработанные-тексты` | 56 | book-manuscript `.docx`, proofreading-stage naming |
| `II том Популярных лекций для юношества` | 8 | same manuscript, later duplicate/working copies |
| `текст`, `прочее`, `аудио*`, `видео*` | ≤4 each | stragglers — one loose `.srt`, misc `.pdf`, and the media folders (out of scope) |

## Topic classification (272 text-bearing (folder, basename) groups)

Filename-keyword classifier ([`build_census.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/external-archives/zaliznyak-lectures-transcripts/build_census.py)), tags not mutually exclusive in principle but came out disjoint on this corpus:

| Tag | Count | Trigger |
|---|---|---|
| `russian_diachrony` | 108 | "история языка/ударения", "контуры истории" |
| `sanskrit_vedic` | 66 | "санскрит", "ведийск", "RV", "панини", "веда" |
| `other_unclassified` | 62 | no keyword hit — mixed: Slovo o polku Igoreve readings, ACADEMIA "Русский устный" series, personal-occasion recordings (Падучева's anniversary, Melchuk's birthday greeting), book presentations |
| `birchbark_novgorod` | 33 | "берест", "новгород" |
| `velesova_book` | 2 | "велесов" (Zaliznyak's refutation of the Book of Veles forgery) |
| `interview_conversation` | 1 | "беседует"/"отвечает на вопросы" (dialogue with V. A. Uspensky) |

**The Sanskrit/Vedic slice (66 groups) is the one directly relevant to this
repo** — it includes the Ṛgveda close-reading series (`Разбор-RV-1034`,
`Разбор-RV-10135`) and multi-lecture "Строй ведийского языка" /
"Грамматический строй санскрита" courses, none of which overlap with the
existing kosha `zaliznyak-grammar-index` / `zaliznyak-drills` datasets (those
are PWG declension-class data, not lecture transcripts) or with
`stenogrammy-teaching-glossary` (a different, private, teaching-corpus
source).

## Index

[`transcript_index.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/external-archives/zaliznyak-lectures-transcripts/transcript_index.tsv) — 272 rows,
`folder · basename · text_formats · media_formats · topic_tags · text_bytes_total`.
Rebuild: `python3 build_census.py listing_09-09-2026.tsv transcript_index.tsv`
(the listing itself, [`listing_09-09-2026.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/external-archives/zaliznyak-lectures-transcripts/listing_09-09-2026.tsv), is
the frozen `rclone lsf -R --files-only --format tsp` snapshot this index was
built from — re-list the remote and rerun for a fresh census).

## Sample set (bounded, `samples/`)

Five files, all from the Sanskrit/Vedic slice, chosen for small size and to
cover every text-layer format family found:

- [`rv1034-27nov2010.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/external-archives/zaliznyak-lectures-transcripts/samples/rv1034-27nov2010.txt) — flat ASR text
- [`rv1034-27nov2010.srt`](https://github.com/gasyoun/SanskritLexicography/blob/master/external-archives/zaliznyak-lectures-transcripts/samples/rv1034-27nov2010.srt) — SubRip
- [`rv1034-27nov2010.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/external-archives/zaliznyak-lectures-transcripts/samples/rv1034-27nov2010.json) — whisper.cpp structured output
- [`rv1034-27nov2010.ans`](https://github.com/gasyoun/SanskritLexicography/blob/master/external-archives/zaliznyak-lectures-transcripts/samples/rv1034-27nov2010.ans) — whisper.cpp bracketed-timestamp dump
- [`timecodes-sanskrit-root-jR.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/external-archives/zaliznyak-lectures-transcripts/samples/timecodes-sanskrit-root-jR.txt) — timecode-only format (`таймкоды-*` folder)

No `.html`/`.vtt`/`.tsv`/`.docx` sample is included — `.html` is a
byte-identical rewrap of `.txt`/`.srt` (terminal-capture skin, no new
information), and `.vtt`/`.tsv`/`.docx` samples were skipped to keep the
sample set small; their format is fully described above and one representative
of each was inspected live during this census (not re-vendored).

## Prior-art cross-check

- kosha `zaliznyak-grammar-index` / `zaliznyak-drills` (declension-class data
  derived from PWG headwords) — **no overlap**, different source and content
  entirely.
- kosha `stenogrammy-teaching-glossary` — different private corpus (Uprava
  teaching stenograms), unrelated uploader/channel.
- No existing kosha dataset covers Zaliznyak **lecture transcripts**.

**LANDED 10-09-2026** via [kosha PR #551](https://github.com/gasyoun/kosha/pull/551)
(merged) — the row below is now live in kosha's own
`data/manifest/datasets.json`, filed as a follow-up worktree + PR against
that separate guarded main-tree checkout.

## Proposed kosha manifest row (prepared, NOT yet landed)

kosha is a separate, guarded main-tree checkout on this machine
(`data/manifest/datasets.json`) — landing this needs its own worktree + PR,
which this ~45-minute unit's time budget did not cover. The row below follows
the existing `stenogrammy-teaching-glossary` entry's shape and is ready for a
follow-up session to paste in:

```json
{
  "id": "zaliznyak-lectures-transcripts",
  "title": "А.А.Зализняк public-lecture transcript census (Sanskrit/Vedic + Slavic linguistics)",
  "tier": "public",
  "in_release": "not-applicable",
  "format": "tsv (index only — full transcripts NOT vendored, source is a private Yandex.Disk remote)",
  "rows": 272,
  "size_bytes": null,
  "keying": "folder, basename, text_formats (csv of txt/srt/json/ans/html/tsv/vtt present), media_formats, topic_tags (sanskrit_vedic/russian_diachrony/birchbark_novgorod/velesova_book/interview_conversation/other_unclassified), text_bytes_total",
  "source_repo": "https://github.com/gasyoun/SanskritLexicography",
  "source_path": "external-archives/zaliznyak-lectures-transcripts/transcript_index.tsv",
  "builder": "https://github.com/gasyoun/SanskritLexicography/blob/master/external-archives/zaliznyak-lectures-transcripts/build_census.py, reading an rclone listing of yadisk:ААЗализняк-архив",
  "consumers": [],
  "notes": "Index only, not a vendored corpus — 101.3 GiB source stays on the private Yandex.Disk remote (rclone remote 'yadisk', not this repo). 66 of 272 groups are Sanskrit/Vedic-tagged (Rṭgveda close-reading + grammar courses); the rest are Slavic-linguistics/Novgorod-birchbark/miscellaneous. Uploader channel names (Головастиков, Осанкина) are public YouTube operators, kept in the index by design (mission note); no other personal data found in sampled content.",
  "sha256": {},
  "provenance_verified": "2026-09-09 (H4473, OxAlpha z-ai/glm-5.3-flash claim; executed by Claude Code Sonnet 5)",
  "rebuild": "rclone lsf yadisk:ААЗализняк-архив -R --files-only --format tsp > listing.tsv && python3 build_census.py listing.tsv transcript_index.tsv",
  "regen_checked": null,
  "consumer_candidates": []
}
```

## Provenance

Built 09-09-2026 by Sonnet 5 (`claude-sonnet-5`), executing OxAlpha
(opencode/z-ai/glm-5.3-flash)-claimed handoff
[H4473](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4473-OxAlpha_SanskritLexicography_zaliznyak-transcripts_09.09.26.md)
per [H3688](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) (any
executor may run any tier's handoff). Full-archive listing captured live via
`rclone lsf`/`rclone cat` against the `yadisk` WebDAV remote; every count in
this document is derived from that listing, not estimated.

_Dr. Mārcis Gasūns_
