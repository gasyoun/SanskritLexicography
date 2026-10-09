# Prior-art dosie: Padamitra (arXiv 2608.25038) — sandhi/samasa bottleneck cross-check (H6244)

_Created: 09-10-2026 · Last updated: 09-10-2026 · H6244 (OxAlpha, `zai-coding-plan/glm-5.3-flash`)_

_Provenance: full text read from the arXiv PDF (v2, 1 Sep 2026, 11 pp, [arxiv.org/pdf/2608.25038](https://arxiv.org/pdf/2608.25038)), fetched 09-10-2026 — the HTML route ([arxiv.org/html/2608.25038v1](https://arxiv.org/html/2608.25038v1)) returned abstract-only, PDF on route 2. Every number below carries a §/table anchor from that text; none from memory. Anchor snapshot: [Uprava report §2](https://github.com/gasyoun/Uprava/blob/main/reports/arxiv-mcp-sanskrit-exploration_2026-10-08.md)._

## TL;DR

| Axis | Verdict |
|---|---|
| **ADOPT / IGNORE** | **ADOPT (limited)** — adopt as (a) related-work citation in the B3/sandhi orbit, (b) an eval-method contrast for our junction-recovery bench; **IGNORE** their IFT pipeline as estate sandhi tooling. One-line: their own numbers prove explicit segmentation supervision is the lever (§7.1: gold segments raise Meaning Faithfulness 0.787 → 0.872) — which is exactly what `sandhi-bench` already measures and `sandhi-split`/`sandhi-council` already operationalize. |
| Citation realistic? | **Yes.** Their related work is the same lineage B3 already cites (Hellwig & Nehrdich 2018, Nehrdich et al. 2024 ByT5-Sanskrit — their §2 and §5.2); citing them back is one line, EMNLP 2026 Findings venue. |
| Data contribution realistic? | **Partial.** Their gold keys are samasa-**intact** glossary phrases (§3.1 example keeps पुरुष-परिचर्यया unsplit in the reference), not junction gold — our `sandhi-bench` is complementary, not a drop-in eval set. A contribution would be an upstream eval add-on (their data/code are public: HF collection `sanganaka/padamitra-glossary-generation`, GitHub `sanganaka-iitkgp/Padamitra-Glossary-Generation`, abstract fn. 1–2) — realistic, but a contact-driven follow-up, not this pass. |
| Estate gold sharpens their eval? | **Yes, at one precise point.** Their own Limitations §: "Neither [metric] recognizes morphological equivalence between valid sandhi resolutions, so orthographically distinct but correct segmentations are penalized." Our DCS-derived junction gold with rule/category metadata ([`sandhi-bench/data/test.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/sandhi-bench/data/test.jsonl)) and the kosha `mw-sense-dcs-join` sense inventory are the instruments that fix exactly this. |

## 1. The paper in five numbers (all §-anchored)

- **Task:** grounded glossary generation — from a śloka + translation, recover sandhi- and samasa-resolved phrases and ground each meaning in the translation; benchmark of **31,316** śloka-translation-glossary triples from Vālmīki Rāmāyaṇa + Śrīmad Bhāgavatam (abstract; §3.1: train 25,050 / val 3,133 / test 3,133). Formalizes the traditional *pāṭha* commentary practice (§1).
- **Dominant failure mode:** over-segmentation — **Table 2** (error analysis over 174 low-scoring samples, bottom 5 % by Meaning Faithfulness, §6.2): Over-Segmentation **122/174 (70 %)**, General Segmentation Issues 22, Both Over+Under 12, Under-Segmentation 9, Semantic & Translation Errors 4, No Issues 5. Flagship example: *trasareṇuḥ* (त्रसरेणुः) wrongly split into *tra* + *sareṇuḥ* (§6.2, §A.5).
- **Bottleneck claim:** "morphology-aware constraints and improved compound boundary modeling remain critical" (§6.2); conclusion §8: "morphology and compound boundary detection as the primary bottlenecks."
- **Segmentation ablation:** predicted intermediate segmentation adds ~nothing (phi-4 Jaccard .716→.708), but **gold** segmentation raises Meaning Faithfulness **0.787 → 0.872** (§7.1, Table 4) — segmentation quality, not task scaffolding, is the lever.
- **Metrics & a metric-level confession:** Jaccard on keys + Meaning Faithfulness = normalized-Levenshtein KeySim (threshold 0.7) × bge-base-en-v1.5 cosine ValSim (§4.2). Limitations §: the metrics "recognize neither" valid-but-different sandhi resolutions; error analysis covers only the bottom 5 %, "where most errors occur, may differ" (Limitations §).

## 2. Cross-check against named estate instruments

### 2.1 `sandhi-bench/` v2 (this repo, H6063) — junction-recovery gold

[`sandhi-bench/README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/sandhi-bench/README.md), data [`sandhi-bench/data/`](https://github.com/gasyoun/SanskritLexicography/blob/master/sandhi-bench/data/) (7,979 DCS-derived gold items, text-disjoint splits 5,561/478/1,940), baselines [`sandhi-bench/baselines/mfs_baseline.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/sandhi-bench/baselines/mfs_baseline.py) / [`llm_baseline.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/sandhi-bench/baselines/llm_baseline.py), results [`sandhi-bench/results/mfs_results_test.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/sandhi-bench/results/mfs_results_test.json).

- **Their failure modes live in our bench:** the over-split flagship *trasareṇuḥ → tra + sareṇuḥ* is an inter-word junction gone wrong; our items are precisely junction-level gold (LEFT+RIGHT, with induced rule + category). Their §A.4 metric intuition — "splits a single word into three fragments" → KeySim 0 — describes the failure our exact-match grader scores as 0 with no embedding generosity.
- **Where their models would land on us:** our MFS baseline is only **57.32 %** exact on test (`mfs_results_test.json`; vowel coalescence 44.01 %, visarga 55.74 %), local-LLM qwen2.5:7b 5-shot **3.0 %** (`llm_qwen2.5_7b-instruct_results_test.json`, n=100). Even the best Padamitra system (phi-4 IFT, Jaccard .716) is a *phrase-recovery* system, not a junction recoverer — their §6.3 seen/unseen near-parity (12,194 seen vs 8,956 unseen keys) shows generalizable segmentation behavior, but nothing in their setup is graded at single-junction exact match. Headroom on our bench is untouched by their paper.
- **What we adopt:** nothing mechanical — a citation contrast: their Table 2 (70 % over-seg) is the *task-level* symptom; our 57.3 % MFS ceiling is the *junction-level* cause, measured independently.

### 2.2 kosha `mw-sense-dcs-join` — the MW sense inventory

Registry row `mw-sense-dcs-join` ("MW senses × DCS citations — full-volume join") in [kosha `data/manifest/datasets.json`](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json); report [kosha `data/concordance/MW_SENSE_DCS_JOIN_REPORT.md`](https://github.com/gasyoun/kosha/blob/main/data/concordance/MW_SENSE_DCS_JOIN_REPORT.md).

- Their Meaning Faithfulness scores values by embedding cosine — sense-blind. Our MW-sense×DCS join is the estate instrument that would rescue the case their Limitations § confesses to: two *correct* resolutions that are orthographically distinct (e.g. a visarga junction resolved as `-ḥ` vs `-r` before a voiced consonant — our gold rule `ḥ b → r b`, item sb-000171) are penalized by their KeySim, while the sense inventory shows the recovered units map to the same MW sense.
- Their one non-segmentation error class is semantic (*ambaṣṭha* glossed "driver" instead of "elephant-keeper", §A.5) — 4/174 samples. Sense-level ground truth is where a richer eval would catch it; our join already provides per-sense attestation to diff against.

### 2.3 `sandhi-split` / `sandhi-council` skills (house sandhi tooling)

Skill files `~/.agents/skills/sandhi-split/SKILL.md` (runtime splitter: paste a sandhied string, get words + induced rule per junction; DharmaMitra neural method needs `--allow-network`) and `~/.agents/skills/sandhi-council/SKILL.md` (multi-agent adjudication for genuinely ambiguous junctions).

- Their **Ablation 1 prompt** (§A.8) hard-codes exactly the boundary our skills treat as *the* decision point: "Perform Padaccheda (**resolve sandhi, keep samasa compound words intact**)". The 70 % over-seg failure rate is what happens when that policy is enforced by prompt rather than by a junction-rule inducer + council. Their §6.2 "inconsistent boundary detection in longer Sanskrit strings" is the no-council condition; `sandhi-council` exists precisely to adjudicate the over/under splits their 12 "Both Over and Under Segmentation" samples exhibit.

### 2.4 H5949 dosie + B3 (ISCLS-9) hook — gold-data context

[Uprava `papers/A61_wsc/ARXIV_TOKENIZATION_SWEEP_2026-10-04.md`](https://github.com/gasyoun/Uprava/blob/main/papers/A61_wsc/ARXIV_TOKENIZATION_SWEEP_2026-10-04.md) (H5949): three 2026 tokenization reads bound the B3 LLM arm; [iscls.tex:342](https://github.com/gasyoun/Uprava/blob/main/papers/B3_iscls9/iscls.tex): "Context sentences are given in sandhied IAST as DCS stores them; unsandhied variants … unmeasured here."

- Padamitra's gold-segment oracle (+0.085 MF, §7.1) is **direct upstream evidence for the B3 caveat**: sandhied input measurably caps downstream semantic quality in a published EMNLP 2026 system. It strengthens the H5949 B3-paragraph claim ("segmentation moves results in its own right") with a third, independent 2026 data point — and their related-work set (Hellwig & Nehrdich 2018; Nehrdich 2024) is the same lineage B3 cites, so the citation costs nothing.
- Adjacent from H5949: kumaresan2026bharati's **87 %** rule-based sandhi-splitter accuracy remains our external reference point for the sandhi circuit — Padamitra reports no junction-accuracy number at all, so it does not displace it.

## 3. Our real examples, marked against their failure modes

Each row: a real gold item from our estate data, then "would their pipeline stumble on it" with the justification quoted from their text.

| # | Our example (source) | Surface → gold | Their failure mode hit? | Justification from their text |
|---|---|---|---|---|
| 1 | [`sandhi-bench/data/test.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/sandhi-bench/data/test.jsonl) sb-000011 (amarakośa, a+a→a) | `eṇasyaiṇam` → `eṇasya+aiṇam` | **Yes — over-segmentation (their 70 % class).** The a+a coalescence erases the boundary; nothing on the surface marks where the split falls. A prompt-driven glosser recovering "semantically meaningful phrases" is exactly the model that fragments such strings; their §6.2: "compounds formed through Sandhi and Samasa were fragmented into smaller units, leading to loss of contextual meaning" — and §A.5 "inconsistent boundary detection in longer Sanskrit strings." |
| 2 | same file, sb-000172 (visarga ḥ+b→r+b) | `stanayitnurbalāhakaḥ` → `stanayitnuḥ+balāhakaḥ` | **Yes — but at their *metric* level, not the model.** A correct split with the intermediate resolution `stanayitnur-` (-r before voiced b) is *valid sandhi*; their Limitations §: metrics "neither recognizes morphological equivalence between valid sandhi resolutions, so orthographically distinct but correct segmentations are penalized" — KeySim < 1 on a correct answer. Our grader (NFC+casefold exact, per the SSB W3.2 review locked in the bench README) has the same brittleness in the opposite direction — the reason a resolution-variant key set is the adoptable fix. |
| 3 | same file, sb-000014 (a+a→ā, function-word junction) | `cāmṛtāya` → `ca+amṛtāya` | **Yes — over-segmentation of clitic junctions.** *ca* + vowel is the most frequent junction type in our gold (vowel coalescence, 584/1,940 test items). Their §A.4: severe over-segmentation "may cause the similarity score to fall below the threshold, setting KeySim to 0"; clitic-sized fragments are the likeliest victims. Our own MFS is weakest here (44.01 % on vowel coalescence) — the failure concentrates in the same class for both systems. |
| 4 | B3 hook, [iscls.tex:342](https://github.com/gasyoun/Uprava/blob/main/papers/B3_iscls9/iscls.tex) via [H5949 dosie](https://github.com/gasyoun/Uprava/blob/main/papers/A61_wsc/ARXIV_TOKENIZATION_SWEEP_2026-10-04.md) | DCS stores contexts sandhied; unsandhied unmeasured | **Yes — upstream-side.** Their gold-segment oracle (0.787→0.872, §7.1 Table 4) shows unresolved-sandhi input drags semantic faithfulness even for a fine-tuned model — quantified support for B3's unmeasured-unsandhied caveat, from a different text pair and task. |

(Their own under-seg example — पुरुष-परिचर्यया "remained unsplit", §A.5 — is samasa-internal, which our junction bench deliberately does *not* cover; samasa type recovery is SanskritGrammar's P4/A64 lane, not `sandhi-bench`. Noted so nobody reads the bench as claiming compound-internal coverage.)

## 4. Roadmap impact (the mission's three questions, answered)

1. **Can estate gold data sharpen their eval?** Yes — concretely at the two places their Limitations § admits weakness: resolution-variant keys (sandhi-bench rule/category metadata; a variant-tolerant grader is a small extension) and sense-blind ValSim (kosha `mw-sense-dcs-join`). Their bottom-5 %-only error analysis (Limitations §) is another gap a gold-anchored mid-range audit would fill.
2. **Does it reshape our sandhi roadmap?** No new lanes. It *confirms* the existing shape: junction supervision is the lever (their §7.1 oracle), our bench already measures it, the skills already operationalize the resolve-sandhi/keep-samasa policy their prompt hard-codes. One durable note: their Table 2 (70 % over-seg on phrase recovery) is the citable task-level symptom of the junction problem we measure.
3. **Citation or data contribution realistic?** Citation: yes, near-free (§2.4). Data contribution: partial — complementary not drop-in (their keys keep samasa intact); a contact-driven upstream eval add-on via their public HF/GitHub artifacts is realistic but out of scope for this pass. No GTD row opened: nothing here blocks or gates current work; if MG wants the contact, that is a human decision on an external channel.

## Evidence (DoD checklist)

- [x] Dosie committed to main SanskritLexicography: `docs/PRIOR_ART_PADAMITRA_SANDHI_BOTTLENECK_2026-10.md` — blob URL after merge: https://github.com/gasyoun/SanskritLexicography/blob/master/docs/PRIOR_ART_PADAMITRA_SANDHI_BOTTLENECK_2026-10.md
- [x] Cross-check vs 2+ named estate instruments (file names above): `sandhi-bench/{README.md,data/test.jsonl,baselines/mfs_baseline.py,results/mfs_results_test.json}` (§2.1), kosha `data/manifest/datasets.json` row `mw-sense-dcs-join` + `data/concordance/MW_SENSE_DCS_JOIN_REPORT.md` (§2.2), `~/.agents/skills/sandhi-split/SKILL.md` + `~/.agents/skills/sandhi-council/SKILL.md` (§2.3), Uprava H5949 dosie + B3 `iscls.tex:342` (§2.4).
- [x] 4 real estate examples marked against their failure modes (§3) + **verdict line: ADOPT (limited)** — citation + eval-method contrast; ignore the IFT pipeline for estate sandhi tooling.

## Verifier

Full text: arXiv PDF v2 fetched 09-10-2026 (HTML route abstract-only — noted in provenance). Spot-checks: Table 2 counts (122/174 = 70 %), §7.1 oracle 0.787→0.872, §3.1 split 25,050/3,133/3,133 — all in the fetched text; MFS 0.5732 / visarga 0.5574 / coalescence 0.4401 from `sandhi-bench/results/mfs_results_test.json`; LLM 0.03 from `llm_qwen2.5_7b-instruct_results_test.json`; sb-000011/000014/000172 quoted verbatim from `sandhi-bench/data/test.jsonl`. No iscls.tex edit (H5949 fail-condition respected); no Uprava file touched.
