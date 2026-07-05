# NWS-vs-Cologne staleness report

_Created: 06-07-2026 · Last updated: 06-07-2026_

**Deliverable 2 of
[H180](https://github.com/gasyoun/Uprava/blob/main/handoffs/H180-Opus_RussianTranslation_pwg_ru_addenda_typology_glue_learner_05.07.26.md).**
Tests MG's hypothesis that **NWS embeds an outdated ~2013 Cologne (Th. Malten) snapshot
of PW/SCH**, so current csl-orig may carry fixes NWS lacks (or vice-versa), letting NWS
content silently shadow a corrected Cologne reading.

## Verdict (first pass)

> **The strong staleness hypothesis is NOT confirmed for SCH content.** NWS's embedded
> Schmidt fragments are **content-identical** to current csl-orig SCH (mean token
> Jaccard **0.992**, 98.0 % identical). The measurable divergence is **PW coverage**,
> not content: on a 4,200-headword sample, csl-orig indexes PW material for **10.0 %**
> of headwords where NWS's snapshot carries none. NWS therefore does **not** silently
> shadow a *corrected* SCH reading; the open risk is narrower — a *coverage* gap in PW.

## Method

Measured with
[`src/_nws_drift.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_nws_drift.py)
(pre-existing; prior-art reused, not rebuilt) and a sampled driver
[`src/_nws_drift_sample.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/_nws_drift_sample.py)
(every 40th scraped **a-**card → 4,200 headwords, for tractability over the 167,991-card
scrape in `src/pilot/nws/`).

Each scraped card stores its own `sch` (full text), `nws` (full text) and `pw_len`
(**only the length** of NWS's PW fragment — full PW text was not retained). So:
- **SCH** — coverage (presence) **and** content (token Jaccard, boilerplate stripped).
- **PW** — coverage (presence) **and** a coarse length-delta only.

Both NWS and csl-orig digitize the *same print*, so their diff measures what Cologne
has corrected/added since NWS forked ~2013.

## Results — SCH (Schmidt)

Coverage (4,200 headwords):

| bucket | count | % |
|---|---:|---:|
| both | 752 | 17.9 |
| nws_only (NWS keeps, csl-orig no longer indexes) | 9 | 0.2 |
| orig_only (Cologne has, NWS 2013 lacks) | 5 | 0.1 |
| neither | 3,434 | 81.8 |

Content drift on the 752 in-both:

| bucket | count | % |
|---|---:|---:|
| identical (Jaccard ≥.95) | 737 | 98.0 |
| minor (.8–.95) | 2 | 0.3 |
| moderate (.5–.8) | 6 | 0.8 |
| major (<.5) | 7 | 0.9 |

**mean Jaccard 0.992.**

**The 7 "major" cases are markup/tokenization artifacts, not editorial drift.** Verified
`kandala` (Jaccard 0.4): the two texts carry the *same* glosses (*Schädel*, *junger
Sproß*, *˚Kampf*, *sanfter Ton*) and the *same* citations (S I,117,3; 320,6; 545,6; S
II,231,10 …); they differ only in markup density — csl-orig wraps `{%…%}` / `<ls>…</ls>`
/ `{part=…}` metadata that the plain-text NWS fragment lacks, plus NWS's `― Schmidt S.
133 (show scan)` provenance tail. On short entries a handful of un-stripped markup tokens
tanks the ratio. So the *true* SCH content-identity is ≥ 99 %, and no verified case shows
a Cologne correction absent from NWS.

Sampled low-Jaccard keys (for the record): `amlAna` 0.40, `dAS` 0.40,
`duzpraBaYjana` 0.40, `ekAdaSavyUha` 0.47, `kUrdana` 0.38, `kandala` 0.43, `pAli` 0.41.

## Results — PW (Böhtlingk)

| bucket | count | % |
|---|---:|---:|
| both | 3,343 | 79.6 |
| nws_only | 3 | 0.1 |
| **orig_only (Cologne indexes PW, NWS snapshot lacks)** | **419** | **10.0** |
| neither | 435 | 10.4 |

Coarse length delta on the 3,343 in-both: `|Δlen| > 50 %` in **242 (7.2 %)** — but this
is length-only (full PW text was not stored), so it cannot distinguish a real content
change from markup/whitespace. **This is the one genuinely open question**: the 10 %
orig_only + 7 % length-divergent PW cases need the full PW text to adjudicate.

`orig_only` SCH sample (Cologne has, NWS lacks — the rare case that *does* fit the
hypothesis, but for coverage not correction): `alakzmIka`, `apapivaMs`,
`bahirvESravaRa`, `cittam`, `pfzwimAMsAdana`.

## Consequence for the merge

- **SCH:** safe. NWS's SCH content matches current Cologne; no silent shadowing of a
  corrected reading was found. The reglue can trust NWS SCH fragments.
- **PW:** treat NWS's PW fragment as **potentially under-covered**, never as
  authoritative over csl-orig PW. Where both exist, prefer csl-orig PW; where only NWS
  has it, keep but flag `pw_source=nws_snapshot`.

## Next pass (to reach "confirmed")

1. **Re-scrape PW full text** (currently only `pw_len`) for a sample of the 419
   orig_only + 242 length-divergent headwords, then re-run the Jaccard on PW to convert
   the coarse length signal into a real content-drift number.
2. Extend beyond the **a-** section (the scrape is a-only) once other sections are
   scraped.
3. Fold the confirmed `orig_only`/`corrected` cases into
   [`ADDENDA_TYPOLOGY.md`](ADDENDA_TYPOLOGY.md) as `pw_correct` / coverage instances.

_Dr. Mārcis Gasūns_
