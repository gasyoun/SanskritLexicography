# H3170 — Ceiling C8: DharmaMitra license-gated ingest memo

_Created: 23-08-2026 · Last updated: 23-08-2026_

Executed under [H3170 (OxAlpha) — Ceiling C8: DharmaMitra license-gated probe + outreach draft](https://github.com/gasyoun/Uprava/blob/main/handoffs/H3170-OxAlpha_SanskritLexicography_ceiling-c8-dharmamitra-probe-outreach_19.08.26.md),
programme [PLAN_SanskritLexicography_PWG_RU_CEILING_RESIDUAL_2026H2.md](https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PLAN_SanskritLexicography_PWG_RU_CEILING_RESIDUAL_2026H2.md)
(item R3 / roadmap item [C8](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/research/ROADMAP_CEILING_2026.md)).
Companion outreach draft (parked, NOT sent): [OUTREACH_2026-08-24_dharmamitra_mitra-parallel-license-api.md](https://github.com/gasyoun/Uprava/blob/main/handoffs/OUTREACH_2026-08-24_dharmamitra_mitra-parallel-license-api.md).

**Status: derived measurements only. Nothing composed, nothing vendored, nothing sent.**
Composition/redistribution is parked as `@DECIDE` (filed in [GTD_NEXT_ACTIONS.md](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md)) and must be ruled before any corpus composition or republication. PWG stays a closed historical corpus — any future use is federation, never extension of PWG entries.

## 1. What lexicon.dharmamitra.org is

[lexicon.dharmamitra.org](https://lexicon.dharmamitra.org) is the **MITRA Translation Lexicon (beta)** — a search UI over term/phrase pairs *automatically extracted* from aligned sentence pairs in the
[mitra-parallel](https://github.com/dharmamitra/mitra-parallel) dataset. Its own disclaimer (verbatim, retrieved 23-08-2026):

> Please note: this is not a manually curated lexicon. The term and phrase pairs were automatically extracted from aligned sentence pairs using machine-learning methods, so they are not always precise; individual matches can be wrong, partial, or mis-aligned. Always read the actual context of the sentence-pair examples rather than relying on an extracted pair on its own.

Footer (verbatim): "Part of the Dharmamitra Project · based on the mitra-parallel dataset".

**No documented public API.** Probed politely on 23-08-2026: `GET /openapi.json` → 404, `GET /api` → 404. The UI is the only interface; formal API access is exactly the ask of the parked outreach draft.

### Site access signals (robots.txt, verbatim, retrieved 23-08-2026)

From https://lexicon.dharmamitra.org/robots.txt:

> User-agent: *
> Content-Signal: search=yes,ai-train=no,use=reference
> Allow: /

with AI crawlers (GPTBot, ClaudeBot, CCBot, Google-Extended, Bytespider, …) individually `Disallow:`ed, and the notice "ANY RESTRICTIONS EXPRESSED VIA CONTENT SIGNALS ARE EXPRESS RESERVATIONS OF RIGHTS UNDER ARTICLE 4 OF THE EUROPEAN UNION DIRECTIVE 2019/790". **Consequence for us:** measure from the *released dataset files* below, never by scraping or model-training over the served UI. This also matches the handoff fence: no bulk scraping.

## 2. License — quoted verbatim (not paraphrased)

### 2.1 Where the license is *declared*

| Surface | Declaration (verbatim quote) | Retrieved |
|---|---|---|
| [dharmamitra-stardict-dictionaries README §License](https://github.com/dharmamitra/dharmamitra-stardict-dictionaries#license) | "These dictionaries are released under the Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)." | 23-08-2026 |
| [Dharmamitra guides → MITRA Dictionaries](https://dharmamitra.github.io/dharmamitra-guides/mitra_dictionaries/) | "**License:** CC BY‑SA 4.0" | 23-08-2026 |
| [Dharmamitra guides → Datasets (MITRA-parallel)](https://dharmamitra.github.io/dharmamitra-guides/datasets/) | "**License**: CC BY-SA 4.0" | 23-08-2026 |
| [Dharmamitra guides → Datasets (SansTib)](https://dharmamitra.github.io/dharmamitra-guides/datasets/) | "**License**: CC BY-SA 4.0" | 23-08-2026 |
| [sebastian-nehrdich/sanstib](https://github.com/sebastian-nehrdich/sanstib) repo metadata | LICENSE file present; GitHub SPDX detection: `CC-BY-SA-4.0` | 23-08-2026 |

### 2.2 ⚠️ Rights-ambiguity finding: mitra-parallel itself carries no LICENSE file

GitHub repo metadata reports `license: null` for [dharmamitra/mitra-parallel](https://github.com/dharmamitra/mitra-parallel) (checked 23-08-2026): **no LICENSE file exists in the repository**, and the root
[README.md](https://github.com/dharmamitra/mitra-parallel/blob/main/README.md) (full text verified 996 chars, 23-08-2026) contains **no License and no Citation section** — even though
[v2/README.md](https://github.com/dharmamitra/mitra-parallel/blob/main/v2/README.md) closes with the dangling pointer (verbatim):

> Pāli is not part of this release. License and citation follow the repository root README.

So the only license statement for the dataset behind the lexicon is the *guides page* declaration quoted above, not an in-repo license file. This is a genuine gap, it is one of the concrete asks in the parked outreach draft, and until it is resolved the `@DECIDE` below should be ruled conservatively (derived measurements fine; redistribution/composition waits).

### 2.3 The license text itself — CC BY-SA 4.0 legal code, verbatim excerpts

Source: <https://creativecommons.org/licenses/by-sa/4.0/legalcode.txt> · retrieval date: **23-08-2026** · full text archived in this session; the load-bearing clauses follow word-for-word.

Section 1 — Definitions (verbatim):

> **a. Adapted Material** means material subject to Copyright and Similar Rights that is derived from or based upon the Licensed Material and in which the Licensed Material is translated, altered, arranged, transformed, or otherwise modified in a manner requiring permission under the Copyright and Similar Rights held by the Licensor. […]
>
> **h. Licensed Material** means the artistic or literary work, database, or other material to which the Licensor applied this Public License.
>
> **k. Share** means to provide material to the public by any means or process that requires permission under the Licensed Rights, such as reproduction, public display, public performance, distribution, dissemination, communication, or importation, and to make material available to the public including in ways that members of the public may access the material from a place and at a time individually chosen by them.

Section 2 — Scope. License grant (verbatim):

> Subject to the terms and conditions of this Public License, the Licensor hereby grants You a worldwide, royalty-free, non-sublicensable, non-exclusive, irrevocable license to exercise the Licensed Rights in the Licensed Material to:
>
> a. reproduce and Share the Licensed Material, in whole or in part; and
>
> b. produce, reproduce, and Share Adapted Material.

Section 3 — License Conditions (verbatim):

> **a. Attribution.**
>
> 1. If You Share the Licensed Material (including in modified form), You must:
>
>    a. retain the following if it is supplied by the Licensor with the Licensed Material:
>
>       i. identification of the creator(s) of the Licensed Material and any others designated to receive attribution, in any reasonable manner requested by the Licensor (including by pseudonym if designated);
>
>       ii. a copyright notice;
>
>       iii. a notice that refers to this Public License;
>
>       iv. a notice that refers to the disclaimer of warranties;
>
>       v. a URI or hyperlink to the Licensed Material to the extent reasonably practicable;
>
>    b. indicate if You modified the Licensed Material and retain an indication of any previous modifications; and
>
>    c. indicate the Licensed Material is licensed under this Public License, and include the text of, or the URI or hyperlink to, this Public License.
>
> […]
>
> **b. ShareAlike.**
>
> In addition to the conditions in Section 3(a), if You Share Adapted Material You produce, the following conditions also apply.
>
> 1. The Adapter's License You apply must be a Creative Commons license with the same License Elements, this version or later, or a BY-SA Compatible License.
>
> […]

Section 4 — Sui Generis Database Rights (verbatim):

> a. for the avoidance of doubt, Section 2(a)(1) grants You the right to extract, reuse, reproduce, and Share all or a substantial portion of the contents of the database;

**Reading for our two candidate uses:**

- *Derived measurements* (scores, counts, join statistics, probe results reported as numbers): not a Share of Licensed Material or Adapted Material — permitted now. This is what this probe did.
- *Composition* (building a Tib/Ch cross-lingual lookup corpus joined into ours, publishing extracts or full copies): that is Share of Adapted Material ⇒ attribution + share-alice obligations apply (Adapter's License must be CC BY-SA 4.0-or-later/BY-SA-compatible), plus the §2.2 ambiguity above. Parked as `@DECIDE`.

## 3. Fetchable inventory (liveness-checked 23-08-2026)

All probes were single polite requests (HEAD or single download); nothing bulk-fetched.

| # | Artifact | What it is | Size / scale | Fetchable? (evidence, 23-08-2026) | License statement |
|---|---|---|---|---|---|
| 1 | [lexicon.dharmamitra.org](https://lexicon.dharmamitra.org) | MITRA Translation Lexicon beta — search UI over extracted Skt↔Tib↔Ch term pairs | UI over mitra-parallel | ✅ live (fetched); ❌ no public API (`/openapi.json`, `/api` → 404); robots `ai-train=no` | none stated on-site; underlying dataset per row 2 |
| 2 | [mitra-parallel v2](https://github.com/dharmamitra/mitra-parallel/tree/main/v2) | Trilingual parallel corpus sa-bo / bo-zh / sa-zh (+mirrors): 1,693,730 records, 2,338,400 segment pairs | six `.ndjson.gz` files, 31–80 MB gz each (exact bytes in table below) | ✅ live (`bo-zh_matches.ndjson.gz` downloaded once, 80,459,833 B byte-exact) | ⚠️ no LICENSE file in repo; CC BY-SA 4.0 declared on guides Datasets page only |
| 3 | [v2/build_stats.json](https://github.com/dharmamitra/mitra-parallel/blob/main/v2/build_stats.json) | build statistics (kept/decontaminated/deduped counts) | 566 B | ✅ live, fetched; numbers cross-check v2 README exactly | (same repo) |
| 4 | [mitra-parallel v1 + eval](https://github.com/dharmamitra/mitra-parallel/tree/main/v1) | previous 1.74M-pair release + retrieval benchmarks | repo total ≈ 473 GB git size (LFS-scale data dirs) | listed, not probed further | (same repo) |
| 5 | [mitra-dictionary-skt-tib.zip](https://dharmamitra.org/pub/dictionaries/mitra-dictionary-skt-tib.zip) | MITRA sa-bo StarDict dictionary (~4M entries from parallel pairs) | 344,825,421 B | ✅ HEAD 200, `application/zip` | "released under the […] (CC BY-SA 4.0)" (README §License) |
| 6 | [mitra-dictionary-tib-skt.zip](https://dharmamitra.org/pub/dictionaries/mitra-dictionary-tib-skt.zip) | MITRA bo-sa StarDict dictionary | 351,577,632 B | ✅ HEAD 200, `application/zip` | same |
| 7 | Sanskrit↔Chinese StarDict | announced companion dictionary | — | ❌ "currently under preparation and will be coming soon" (guides, verbatim) | n/a yet |
| 8 | [sebastian-nehrdich/sanstib](https://github.com/sebastian-nehrdich/sanstib) | SansTib Skt–Tib parallel corpus (~317k pairs) + embedding model refs | repo present | ✅ live; LICENSE detected `CC-BY-SA-4.0` | in-repo LICENSE ✅ |
| 9 | [MITRA Qwen3.5 collection](https://huggingface.co/collections/buddhist-nlp/mitra-qwen35-2026) | fine-tuned translation/embedding models | HF collection | listed on root README 23-08-2026; not probed | model cards govern (out of this memo's scope) |

Per-direction file sizes for row 2 (GitHub contents API, 23-08-2026):

| file | bytes |
|---|---|
| `sa-bo_matches.ndjson.gz` | 57,721,382 |
| `bo-sa_matches.ndjson.gz` | 57,658,815 |
| `bo-zh_matches.ndjson.gz` | 80,459,833 |
| `zh-bo_matches.ndjson.gz` | 80,305,347 |
| `sa-zh_matches.ndjson.gz` | 31,269,904 |
| `zh-sa_matches.ndjson.gz` | 31,202,646 |

Docs inconsistency noted honestly: the guides/README say "~10 GB per direction after unzip" for the StarDict zips while the zips themselves are ~350 MB compressed (plausible for StarDict with large index files, unverified — we did not unzip); the same pages variously say the dictionaries are "based on 600,000 parallel Sanskrit-Tibetan sentence pairs" and "more than 1.7m sentence pairs combined" — the latter matches v1's 1.74M release. Worth asking the team in the outreach draft which figure is current.

## 4. Hand-checked sample — what a bo-zh cross-lingual record actually contains

One-time download of [`v2/bo-zh_matches.ndjson.gz`](https://github.com/dharmamitra/mitra-parallel/blob/main/v2/bo-zh_matches.ndjson.gz) (80,459,833 B, sha-checked against GitHub's reported size); first records decompressed locally in session temp (never committed). Record 1, fields verbatim:

```json
{
  "id": "BO_K08_D0056-2:186a-1_ZH_T11_0310_053:0312b19_5",
  "score": 0.858,
  "root_segnr": "BO_K08_D0056-2:186a-1",
  "par_segnr": "ZH_T11_0310_053:0312b19_5 ZH_T11_0316_037:0879a09_9 ZH_T32_1660_002:0524c27_1",
  "root_segtext": "dad pa'i stobs dang / brtson 'grus kyi stobs dang / dran pa'i stobs dang / ting nge 'dzin gyi stobs dang / shes rab kyi stobs so/ /",
  "par_segtext": "舍利子！一者信力，二者精進力，三者念力，四者三摩地力，五者勝慧力。彼神足力高出自在，過魔煩惱、入佛境界覺諸眾生，聚集宿世善根資糧，魔及魔身天等不能障礙。",
  ...
}
```

Full field list observed on real lines (18 keys): `id, score, par_length, root_length, inquiry_pos_beg, inquiry_pos_end, target_pos_beg, target_pos_beg, target_pos_end, root_segnr, par_segnr, root_segtext, par_segtext, root_string, par_string, root_offset_beg, root_offset_end, par_offset_beg, par_offset_end, src_lang, tgt_lang, filename, co_occ, gemini_score`.

Two honest observations beyond the marketing page:

1. **The schema is richer than documented.** [v2/README.md](https://github.com/dharmamitra/mitra-parallel/blob/main/v2/README.md) documents `id, score, root_segnr/par_segnr, root_segtext/par_segtext, root_string/par_string, position fields, lengths` — the files additionally carry `src_lang`, `tgt_lang`, `filename`, `co_occ` and `gemini_score` (an LLM-scored alignment-quality field; provenance of `gemini_score` is undocumented in-repo — another outreach question).
2. **The alignment hand-check passes.** Record 1 aligns the Tibetan five-powers passage (Kangyur segment `BO_K08_D0056-2:186a-1`) with the Chinese 五力 list: 信力=dad pa'i stobs (faith), 精進力=brtson 'grus kyi stobs (effort), 念力=dran pa'i stobs (mindfulness), 三摩地力=ting nge 'dzin gyi stobs (samādhi), 勝慧力=shes rab kyi stobs (wisdom) — five-for-five term-for-term correct, `score=0.858`. Segment IDs are DharmaNexus numbering; `par_segnr` carries multiple Chinese witnesses (T11_0310, T11_0316, T32_1660), i.e. records are many-target-capable, matching the README's "each direction unions target segments per source segment independently".

This is the real structure the composition `@DECIDE` should rule on: per-record JSON with Wylie-transliterated Tibetan + traditional-character Chinese + DharmaNexus segment coordinates + alignment scores.

## 5. Composition `@DECIDE` (parked — do not act until ruled)

Filed in [GTD_NEXT_ACTIONS.md](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md) (23-08-2026). The fork:

- **Option A — measurements-only standing policy.** We keep consuming mitra-parallel for derived statistics (probe scores, coverage counts, BLI/WSD evals) and never redistribute or compose. No share-alike exposure, no dependence on resolving §2.2.
- **Option B — federated composed layer, CC BY-SA 4.0 out.** Compose a Tib/Ch cross-lingual lookup layer (or publish extracts), released under CC BY-SA 4.0 with full attribution + URI per §3(a), gated on the team clarifying the missing in-repo LICENSE (§2.2) — ideally in writing via the parked outreach draft.
- **Option C — wait-and-see.** Defer everything until the outreach reply lands; keep only Option A activities meanwhile.

Recommendation recorded in the GTD row: **A now, B only after written license clarification arrives**, i.e. effectively A-until-reply. Ruling is MG's alone.

## 6. Fence compliance

- Nothing entered any PWG entry; no composed corpus was built; no dataset was vendored into any repo (the sample above lives in temp only; its content quoted here falls under quotation-for-measurement).
- No outreach email was sent — draft parked at [OUTREACH_2026-08-24_dharmamitra_mitra-parallel-license-api.md](https://github.com/gasyoun/Uprava/blob/main/handoffs/OUTREACH_2026-08-24_dharmamitra_mitra-parallel-license-api.md).
- Live-service etiquette: every HTTP touch on dharmamitra.org/lexicon/GitHub was a single fetch or HEAD; one full download of the smallest-needed bo-zh artifact for the hand check; zero scraping of the UI; robots content-signals respected.
- SERVER_OUTAGES.md: no entry needed — every probed endpoint answered normally on 23-08-2026.

_Dr. Mārcis Gasūns_
