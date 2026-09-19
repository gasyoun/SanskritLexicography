# H4058 — PWG post-GLM linguistic and corpus-evidence review (first, independent verdict)

_Created: 05-09-2026 · Last updated: 05-09-2026_

Reviewer: Fable 5.1 (`claude-fable-5-1`), unattended drain worker, worktree
`SanskritLexicography-h4058-drain` off `origin/master` `182f5c339`. Handoff:
[H4058](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4058-Fable_SanskritLexicography_pwg-post-glm-linguistic-evidence-review_04.09.26.md).
**Independence:** the peer review H4059 (Codex, pipeline reproducibility) was not read;
no H4059 PR existed at review time (`gh pr list --search H4059` → empty). This file is
the sealed first verdict. Elapsed for the review pass: ~40 min wall-clock, 0 provider
calls, 0 canonical writes.

## 1. Verdicts

| axis | verdict | one-line reason |
|---|---|---|
| Implementation correctness of the six deliveries | **PASS (offline scope only)** | All six merged, receipts present, store hash reproduced; every delivery is expressly offline and none claims live quality. |
| Corpus / alignment / TM evidence | **FAIL** | The evidence panel shown per card is a lemma-level roll-up copied onto every sense; the 1.09M-row Sa↔Ru parallel corpus is never compared with the Russian; teaching corpora are not wired; English is absent from the store; the packet's TM "10/10 hit" is self-identity. |
| Readiness to request human review | **NOT READY** | The user's prerequisite (show how well Sanskrit aligns with Russian/English/German and how TM and corpora are actually used) is unproved; the ten cards' visible "supports" lines overstate what was checked. |

NOT READY is the overall conclusion. Nothing here approves voting.

## 2. Frozen inputs

| item | identity |
|---|---|
| Reviewed repo revision | SanskritLexicography `origin/master` `182f5c339` (merge of PR #2077) |
| Runtime store | `pwg-ru-data/tm/pwg_ru_translated.jsonl` · sha256 `79d72dbcb4b33fc88d9e907dec9ecaa0e56ebfb72495a5115ce951a623f8ca65` · 11,519 rows (matches H4052/H4055/H4056 receipts) |
| pwg-ru-data revision | `eaeb870` (2026-09-02, H3947 mirror refresh) |
| TM identity | no persisted TM file; TM is rebuilt from the store by `pilot/translation_memory.build` (addresses = `ru:<provenance.input_raw_sha256>`); denylist `tm/translation_memory.denylist.jsonl` 107 lines → 113 addresses |
| H4056 packet | `h4056-evidence-packet-2026-09-05`, content sha256 `234772d2…`, 10 cards ([manifest](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H4056_evidence_packet_manifest.json)) |
| H4053 packet | [frozen 30-card sample](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H4053_quarantine_sample30_frozen.json) — quality unmeasured by design |
| Corpus assets (pwg-ru-data/corpus) | koch 29,177 · kna 3,271 · fri 8,151 · smirnov 3,547 · kow 13,488 · grin12 457 · grin3 206 · apte_hi 111,235 · kosha_syn 88,839 · vedic_rituals_hi 6,166 · meulenbeld_plants 453 · corpus_lexicon 1,093,391 rows (290.5 MB, verse-aligned Sa↔Ru, keys `sa/slp1/ru/work/passage/…`) |
| Mined running-text tier | `corpus_lexicon.mined.jsonl` **absent** in pwg-ru-data and in this worktree (main checkout carries only a 1 KB `.mined.done.jsonl`) |
| English store | **none** (no `en` column in any store row; no `*en*.jsonl` under `pwg-ru-data/tm`) |

### Upstream completion checklist

| handoff | registry | PR | receipt read | scope note |
|---|---|---|---|---|
| H4052 delivery metrics | ✅ Done 05-09 | #2073 merged | `reports/PWG_DELIVERY_REPORT_04-09-2026.json` | 11,519 rows, sha 79d72dbc reproduced |
| H4053 quarantine sample-30 | ✅ Done 05-09 | #2077 merged | `reports/H4053_quarantine_sample30_frozen.json` | report-only, never promotes, quality unmeasured |
| H4054 one-card contract | ✅ Done 05-09 | #2074 merged | `pwg_ru/h4054/H4054_ONE_CARD_DEFAULT_EVIDENCE_05-09-2026.md` | call shape only |
| H4055 store lineage | ✅ Done 05-09 | #2072 merged | `reports/H4055_store_mirror_box_matrix.json` | Mac store MISSING, no divergence |
| H4056 first packet | ✅ Done 05-09 | #2075 merged | `reports/H4056_evidence_packet_report.md` | 10 cards, TM 10/10, replay 8/8 |
| H4057 GLM route | ✅ Done 05-09 | #2076 merged | `reports/H4057_glm_route_qualification.json` | QUALIFIED_OFFLINE, 0 provider calls |

Gate satisfied. None of the six is a live quality result, and none claims to be.

## 3. Own-data evidence (reproducible)

Commands (read-only over the store; scratch TM under the system temp dir):

```text
python RussianTranslation/tools/h4058_evidence_probe.py
python RussianTranslation/tools/h4058_tm_address_collision.py
```

Outputs: [H4058_evidence_probe.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H4058_evidence_probe.json),
[H4058_tm_address_collision.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/H4058_tm_address_collision.json).

### 3a. Evidence census over all 11,519 store rows

| measure | rows | of store |
|---|---:|---:|
| rows with an `evidence_summary` | 10,805 | 93.8 % |
| rows with a **sense-level** `evidence` array (the only per-sense RU check) | 2,218 | **19.3 %** |
| rows whose lemma roll-up names ≥1 RU dictionary in `supports_senses` | 10,802 | 93.8 % |
| rows where the parallel corpus is `present` (lemma has examples) | 8,852 | 76.8 % |
| rows where the parallel corpus **supports a sense** | **0** | 0 % |
| rows with `contradicts` non-empty | 1,057 | 9.2 % |
| rows with a human decision | 5 | 0.04 % |
| rows with any English | 0 | 0 % |

Reading `annotate_evidence.py` (lines 222–258): `supports_senses` is computed once per
**lemma** as the union of dictionaries whose glosses overlap *any* sense row's Russian,
then the identical summary is copied onto every sense row of that lemma. The per-sense
truth is the `evidence` array, and 80.7 % of rows have none. The parallel corpus
(`corpus`) sits in `NONRU_LANES`: only `present`/`silent` is recorded (does the lemma
have examples), its Russian side is never compared with the card's Russian.
`evidence_match_kind` is `lemma` for all 3,591 evidence items — there is no sense- or
passage-level match anywhere in the store.

### 3b. Source-family counts: available → used

| family | available (rows) | indexed | used for RU sense support | provenance class |
|---|---:|---|---|---|
| Kochergina 1987 (koch) | 29,177 | yes | lemma roll-up 10,802 rows; per-sense items ⊂ 3,591 | independent dictionary |
| Knauer 1908 textbook glossary (kna) | 3,271 | yes | lemma roll-up 10,585 rows | textbook-derived glossary (the only "teaching" source) |
| Frisch 1956 (fri) | 8,151 | yes | roll-up 1,791 | independent dictionary |
| Smirnov (smirnov) | 3,547 | yes | roll-up 8,808 | independent dictionary |
| Kossovich 1854 (kow, WIL-seeded) | 13,488 | yes | roll-up 4,916 | dictionary-derived (REF) |
| Grintser Rāmāyaṇa glossaries (grin12/grin3) | 663 | yes | silent on 10,805 rows (0 hits) | specialist, evidence-only |
| Verse-aligned Sa↔Ru parallel corpus | 1,093,391 | yes | **0** (presence only) | independent attestation (Rāmāyaṇa, MBh, Manu, AV …) |
| Mined running-text tier | 0 on disk | no | 0 | mined (H186 pilot 421 pairs, not present) |
| Lecture transcripts (samskrtam.ru `/l/…`) | not wired | no | 0 | teacher-explanatory; backlog item 7 in RESEARCH_LAYERS_UNCAPTURED_BACKLOG_2026 |
| English (any) | none | no | 0 | — |
| German source (`de`) | 11,516 rows | n/a | it is the source text | PWG |

Teaching-corpus scope, provisionally per the open /ask interview: textbook material =
the Knauer glossary only (a glossary lookup, not exercises); lesson/lecture transcripts =
none available to the pipeline. Both are flagged unavailable at corpus level; no final
human ruling is asserted here.

### 3c. Sanskrit preservation and apparatus (DE vs RU, whole store)

| check | rows |
|---|---:|
| rows whose German carries `{#…#}` Sanskrit | 8,254 |
| RU drops a Sanskrit token present in DE | 60 (0.7 % of those) |
| RU adds a Sanskrit token absent in DE | 68 |
| `<ls>` citation count differs DE vs RU | 118 (1.0 %) |

Small but non-zero apparatus drift; the ten packet cards show none of it (10/10 exact
token and citation parity).

### 3d. The ten H4056 cards, traced independently

| key1 | sense | type | lemma roll-up shows | per-sense `evidence` | parallel corpus | grammatical vs lexical |
|---|---|---|---|---:|---|---|
| Ap | note | explanatory | kna koch kow smirnov | **0** | present, unused | grammatical apparatus (caus., gerund) |
| Bid | 1 | equivalent | kna koch kow smirnov | 1 (Kochergina «раскалывать») | silent | lexical gloss ✔ |
| Buj | ava | equivalent | kna koch kow smirnov | **0** | present, unused | preverb sense |
| Cid | 5 | equivalent | kna koch smirnov | **0** | silent | lexical gloss |
| DA | caus. | explanatory | kna koch smirnov | **0** | present, unused | grammatical apparatus (RU = DE byte-identical apart from nothing to translate) |
| Sam | NWS-1 | explanatory | kna koch | **0** | present, unused | NWS supplementary layer |
| Sru | 2 | equivalent | kna koch | **0** | silent | metrical note + citations |
| brU | 1 | equivalent | kna koch kow smirnov | 4 (Kochergina «говорить») | silent | lexical gloss ✔ |
| car | header | explanatory | kna koch smirnov | **0** | silent | grammatical apparatus (finite forms) |
| dA | A. Präsensformen | explanatory | kna koch smirnov | **0** | present, unused | grammatical apparatus |

Eight of ten cards have **no sense-level Russian evidence**, yet the rendered verdict
panel prints "supports: kna/koch/kow/smirnov" for every one of them — the lemma roll-up
read as if it were sense support. Six of ten are grammatical apparatus or headers where
the Russian is a near-copy of the German scaffolding, so they test formatting fidelity,
not lexical translation. Only Bid-1 and brU-1 are genuine lexical glosses with a
dictionary witness (both Kochergina, lemma match).

Worked positive case — `bhid` 1: DE «spalten, einbrechen, ein Loch in Etwas schlagen,
zerschlagen, zersprengen, aufreissen, schlitzen» → RU «раскалывать, проламывать,
пробивать отверстие в чем-либо, разбивать, разносить, разрывать, разрезать»; Kochergina
«1) раскалывать, разбивать» supports sense 1; `{#puraH#}`, `{#adrim#}` and ṚV. 1,53,8 /
2,14,6 / AIT. BR. 1,25 preserved. Exact lexical equivalence, seven-for-seven synonyms.

Worked negative case — `dhā` caus.: DE «— caus. {#DApayati#} P. 7,3,36; s. u. {#antar,
api …#}» → RU identical string. Nothing lexical was translated; the card is pure
apparatus, `s. u.` left as Latin abbreviation, and it still shows four "supporting"
dictionaries. Presenting it as alignment evidence is misleading.

Worked contradiction class — 1,057 rows carry a `contradicts` source (a dictionary has
Russian for the lemma that shares no content token with any sense's Russian). H4056
excluded them upstream (1,768-row quarantine); the packet therefore shows the cleanest
decile, and nothing in it speaks for the 15 % that contradict.

### 3e. TM reuse, traced

| measure | value |
|---|---:|
| store rows carrying a TM address | 11,510 |
| distinct addresses | **2,445** |
| addresses shared by ≥2 rows | 1,263 (covering 10,328 rows) |
| shared addresses whose rows differ in sense identity | 1,247 |
| shared addresses whose rows differ in Russian | 1,262 |
| max rows under one address | 100 |
| H4056 cards: hit in TM built from the full store | 10/10 |
| H4056 cards: hit in TM built with the card row held out | 8/10 |

The TM unit is the whole PWG entry (raw masked source), not the sense: one address maps
to up to 100 sense rows, and a `lookup` returns an entry-level object (`card`,
`n_senses`, `trust_level`, `reuse_policy`) rather than a sense's Russian. That is a
defensible design, but it means the packet's per-card "TM hit" is an entry-level
statement, and "10/10" was measured against a TM built from the very store that holds
the cards — self-identity by construction (`build_h4056_evidence_packet.py` lines
174–183). The 8/10 hold-out hits come from sibling senses of the same entry, i.e. the
same self-identity one row removed; Buj-ava and DA-caus. (single-row entries) miss.
No hit/miss/defer log from a production run was available to audit, so **actual TM use
in production is UNVERIFIED**; what is demonstrated is the mechanism, and the real reuse
ceiling is 2,445 distinct inputs.

### 3f. Breadth

The ten cards are ten verb roots (round-robin over sorted roots): no nominal, no
compound, no homonym pair (`h` = 0 throughout), no long polysemous entry, and one NWS
supplementary row. Vedic/Epic/Classical spread is incidental (ṚV., MBH., KAUŚ., VYUTP.
citations appear). A population estimate from these ten is not supported; the store-wide
census in 3a–3c is the only breadth measurement here.

## 4. Prioritized defects (repair residuals — the reviewed baseline is untouched)

1. **P0 — lemma roll-up rendered as sense support.** `annotate_evidence.py` copies one
   lemma summary onto every sense row; the H4056 panel and any future sheet must show the
   per-sense `evidence` array (present on 19.3 % of rows) and label the roll-up as
   lemma-level. Owner: agent.
2. **P0 — parallel corpus unused for alignment.** 1.09 M verse-aligned Sa↔Ru rows are
   consulted for presence only. Wire the corpus Russian into `best_relation` (or a
   passage-level lane) so it can support or contradict a sense; report matched / missed /
   ambiguous with denominators. Owner: agent.
3. **P1 — TM evidence must be non-circular.** Report TM as hit/miss/defer from a real run
   log or a hold-out replay, state the entry-level unit, and stop counting self-hits.
   Owner: agent.
4. **P1 — teaching corpora absent.** Mined tier not on disk; lecture transcripts not
   wired (Track A never built). Inventory both classes, distinguish textbook/exercise
   from transcript, and flag what is unavailable — pending the /ask scope ruling.
   Owner: agent; scope: a human should decide.
5. **P2 — English direction unrepresented.** No EN store exists; cross-language
   equivalence RU/EN cannot be judged. Owner: agent (EN lane status report).
6. **P2 — apparatus drift.** 60 dropped / 68 added Sanskrit tokens, 118 `<ls>` count
   mismatches; add these as store-wide mechanical gates. Owner: agent.
7. **P3 — packet breadth.** Next packet must stratify by nominal / compound / homonym /
   long entry and include contradicting rows as negative examples.

Repair residual minted this pass: see § 6.

## 5. What this review does not claim

Not a judgement of live translation quality (no paid calls were made); not a reading of
the peer review; not a rewrite of any reviewed file; not a human vote. Rights and
licence facts unchanged. The scratch TM files live under the system temp dir only.

## 6. Landing

Report, two probe scripts and two JSON receipts land by PR on SanskritLexicography.
Repair residual: one bounded agent handoff for defects 1–3 (evidence-panel truthfulness
+ parallel-corpus sense lane + non-circular TM receipt), minted via `mint_handoff.py`
in the same pass and referenced from the PR body; defects 4–7 are recorded here for
the GTD sweep.

_Dr. Mārcis Gasūns_
