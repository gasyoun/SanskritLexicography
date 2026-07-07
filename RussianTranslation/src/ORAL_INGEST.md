# Oral-corpus ingest — the spoken register of the Sa→Ru TM (H215 Slice 4)

_Created: 07-07-2026 · Last updated: 07-07-2026_

This is the design + shared-schema doc for
[`src/ingest_oral.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ingest_oral.py),
the oral half of the publication-grade translation memory built by
[H215](https://github.com/gasyoun/Uprava/blob/main/handoffs/H215-Opus_RussianTranslation_pwg_ru_publication_grade_tm_tmx_and_oral_06.07.26.md).
Slices 1–3 turned **written** verse-aligned scholarly translations into a graded
[TMX](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/BUILD_TMX.md);
Slice 4 adds the **oral** register (recorded/spoken Sanskrit with a Russian
rendering) through the *same* L0 → grade → TMX pipeline, not a forked one.

## Coordination with H174 — one schema, two owners

The spoken material itself is owned by
[H174 · spoken-sanskrit-corpus](https://github.com/gasyoun/Uprava/blob/main/handoffs/H174-Opus_spoken-sanskrit-corpus_spoken_sanskrit_corpus_scaffold_04.07.26.md):
sourcing the recordings/subtitles and **ASR-transcript cleaning** (Data-Juicer:
disfluency/filler removal, garbled-segment filtering, near-dup collapse). H174 is
still 🟡 (repo not built yet), so this doc **defines the contract** it will produce
against. The division of labour:

| Stage | Owner | Output |
|---|---|---|
| Source recordings, subtitles, `.doc`/`.pdf` companions | **H174** | raw transcripts |
| ASR-noise cleaning (disfluency, garble, dedup) | **H174** (Data-Juicer) | *cleaned* timecoded transcript (VTT/SRT) |
| Cleaned transcript → graded Sa↔Ru parallel unit | **H215 Slice 4** (`ingest_oral.py`) | `corpus_builder/<work>.jsonl` → L0 → TMX |

`ingest_oral.py` does **no ASR** (per H174's interview the material is *existing*
machine-transcripts, not raw audio needing fresh recognition) and does **no
cleaning** (that is H174's Data-Juicer stage upstream). It parses a *cleaned*
subtitle track, pairs Sanskrit with Russian, applies the never-invent guards, and
emits the corpus schema below.

## The pipeline

```
cleaned VTT/SRT (sa) + (ru)                     [H174 delivers these]
        │  ingest_oral.py convert
        ▼
SamudraManthanam/web/corpus_builder/jsonl/<work>.jsonl   (modality:oral + anchors)
        │  build_l0.py build --sm <dir>
        ▼
release/corpus_tm/corpus_l0.jsonl               (L0 verse units, modality carried)
        │  tm_grade.py grade   (oral units: lowered base grade)
        │  build_tmx.py build --l0 …
        ▼
release/corpus_tm/corpus_tm.sa-ru.tmx           (TMX 1.4b, modality/t_start/t_end props)
```

Everything downstream of the source jsonl is the **existing written pipeline** —
oral flows through it unchanged except for the modality mark and the grade policy.

## Source schema — the extension to `corpus_builder/<work>.jsonl`

The written ingest format ([`ADDING_TEXTS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/ADDING_TEXTS.md))
is one JSONL line per segment: `{group, seg, text, passage, lang}`. Oral adds four
**optional** provenance fields on the segment records — absent on written sources,
so the written path is byte-for-byte unchanged:

```json
{"group": "gita-lecture-01:1", "seg": "sa", "passage": "1",
 "text": "yogaḥ karmasu kauśalam", "slp1": "yogaH karmasu kauSalam",
 "modality": "oral", "t_start": 1.0, "t_end": 5.0, "source_media": "gita01.mp3"}
{"group": "gita-lecture-01:1", "seg": "ru", "passage": "1", "lang": "ru",
 "text": "йога есть искусность в действиях",
 "modality": "oral", "t_start": 1.0, "t_end": 5.0, "source_media": "gita01.mp3"}
```

| Field | Meaning |
|---|---|
| `modality` | `oral` \| `written` (default `written` when absent) |
| `t_start` / `t_end` | float **seconds** into `source_media` — the time anchor |
| `source_media` | the audio/video filename the segment was spoken in (provenance) |
| `asr_conf` | optional 0–1 recognition confidence, if the cleaned transcript kept it |

`slp1` is filled by the **canonical** transcoder (`build_src.iast_to_slp1`, the same
one the written corpus uses) so oral units carry a real SLP1 key, not just the IAST
surface. `group` must stay globally unique — prefix it with the work name.

These fields flow through unchanged: `build_l0.py` copies `modality`/`t_start`/
`t_end`/`source_media`/`asr_conf` onto each L0 unit, and `build_tmx.py` emits them
as TMX `<prop>`s on the `<tu>`.

## Grade policy — the "lowered base grade" for oral

MG's spec: *"Oral units get a lower base grade by default"* (live interpretation is
noisier — translationese, paraphrase, hesitation). Implemented in **one place**
(`build_tmx.oral_cap`, applied by both the L0 exporter and the L1 grader) plus a
composite penalty in the grader:

1. **Composite penalty** — `tm_grade.ORAL_PENALTY = 0.15` is subtracted from an oral
   unit's composite score before thresholding, representing the higher noise floor.
2. **A-gate lock** — `oral_cap()` forbids grade **A** for an oral unit on the
   automatic signals alone: a unit that would score A when written is capped at **B**
   when oral. **Only human adjudication** (`/gold-adjudicate`, the `adjudicated` flag)
   lifts an oral unit to A. B and C pass through unchanged.

So an oral unit's ceiling is B unless a human confirms it — matching A's definition
("publication / hard gloss") which oral live-interpretation cannot claim unreviewed.

## Pairing rule — parallel tracks must share segmentation

`convert --sa X.vtt --ru Y.vtt` pairs cues **by index**: cue *i* of the Sanskrit
track ↔ cue *i* of the Russian track. This is correct only when both tracks segment
the **same** recording identically. A cue-count mismatch is a **hard error**, never a
silent `zip()` truncation — mis-segmented tracks would fabricate wrong Sa↔Ru pairs
(the F1 hallucination lesson,
[FAILURE_GALLERY](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/failures/FAILURE_GALLERY.md)).
When tracks are independently segmented, align them upstream and pass `--pairs` with
explicit `{sa, ru, t_start, t_end}` rows instead. The never-invent guards still apply
at emit: a Sanskrit surface must be present and the Russian must carry Cyrillic, or
the pair is dropped (reported, never fabricated).

## Formats accepted

- **WebVTT** (`.vtt`) and **SRT** (`.srt`) — the yt-dlp / Whisper subtitle outputs.
  Inline VTT tags (`<c>`, `<00:00:01.000>`) are stripped; `WEBVTT`/`NOTE`/`STYLE`
  headers are skipped; hours in the timestamp are optional.
- **JSON/JSONL** cue lists (`[{t_start, t_end, text, asr_conf?}]`) — a pre-parsed
  transcript.
- **`--pairs` JSONL** (`{sa, ru, t_start, t_end, asr_conf?, passage?}`) — already
  paired, bypassing the index-pairing step.

## Pilot results (07-07-2026, fixture)

No oral recordings are in a tracked repo yet (H174 unbuilt), so Slice 4 ships with a
**fixture pilot** proving the schema end-to-end and quantifying the grade policy.

**End-to-end chain** — a 3-cue parallel VTT pair (Bhagavad-Gītā lines) runs
`ingest_oral convert` → `build_l0 build --sm` → `build_tmx build --l0` and produces a
well-formed TMX 1.4b whose oral `<tu>`s each carry `modality=oral`, `t_start`/`t_end`,
and `source_media` props (validated by `build_tmx validate`). `slp1` is populated by
the canonical transcoder (`yogaḥ karmasu kauśalam` → `yogaH karmasu kauSalam`).

**Grade shift (lowered base)** — the *same* 6 clean, corroborated (≥2 works agreeing)
verse units, graded written vs oral, deterministic proxy QE:

| modality | A | B | C | mean composite |
|---|---:|---:|---:|---:|
| written | 6 | 0 | 0 | 0.892 |
| oral | 0 | 6 | 0 | 0.743 |

The −0.149 mean-score drop is `ORAL_PENALTY` (0.15); the A→B collapse is `oral_cap`'s
A-gate lock. Units that only reach B/C when written are unaffected by the cap (only
the penalty moves them). Reproduce: `python tm_grade.py selftest` (asserts the
written-A / oral-B / adjudicated-oral-A gates) and `python ingest_oral.py selftest`.

_Model provenance: deterministic — no LLM. Pilot generated under Opus 4.8
(`claude-opus-4-8`), H215 Slice 4._

## Follow-ups (not this slice)

- **Handout `.doc`/`.pdf` companions** (Slice 4 pipeline #5): a lecture's written
  handout of the same passage → the `docx-to-md` skill → `.mdx`, ingested as a
  **second reference** of the same verse (spoken vs handout → multi-reference
  consensus). Requires real handout assets (MG-gated).
- **Real audio → ASR** (pipeline #3): Whisper→WhisperX/MFA forced alignment for
  material that arrives as raw audio rather than cleaned subtitles — H174's ASR stage.
- **Scale ingest** is asset-gated: no oral recordings are in a tracked repo yet
  (H174 not built). This slice ships the schema + tooling + an end-to-end fixture
  pilot; scale runs when H174 delivers cleaned transcripts.

## Rights

Recorded third-party speech is consent/rights-gated **more** than written sources
(H174 guardrail). No public release before
[`/publish-safety-check`](https://github.com/gasyoun/Uprava) + per-source clearance
(H215 Slice 5). Emitted jsonl/TMX stay under the gitignored `release/corpus_tm/`
tree, exactly like the written corpus.

_Dr. Mārcis Gasūns_
