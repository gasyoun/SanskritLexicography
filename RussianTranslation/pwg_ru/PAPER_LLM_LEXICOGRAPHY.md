# Paper A51 — LLM-assisted translation of a complete historical dictionary: the PWG→Russian pipeline and its evaluation (working title)

_Created: 07-07-2026 · Last updated: 07-07-2026_

Readiness: **2/5** (outline + verified related-work seed + committed data spine; results
pending the H178 B-1 human votes). Anchor framing per MG ruling (H178, 05-07-2026):
**LLM-assisted computational lexicography** primary; dictionary digitization (the MUDIDI
line, [csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas)) secondary bridge. Registered as
**A51** in [`Uprava/ARTICLES.md`](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md).
Sibling paper: A49 (addenda-typology algebra) shares the corpus, not the thesis.

## Thesis

A complete 19th-century bilingual scholarly dictionary (the Petersburg Wörterbuch
tradition, 5 merged layers, ~106k+ headwords) can be translated into a third modern
language (Russian) by an LLM pipeline whose quality control is **deterministic-first**
(structural gates on 100 % of cards, LLM judgment only on flagged residue), with
per-row model/pipeline provenance — and the right *human* evaluation protocol for such
output is an empirical question we answer with a four-rubric bake-off (MQM ·
adequacy/fluency · Direct Assessment · pairwise), scored on reliability,
discrimination, cost, and diagnostic value against a reference-free QE signal
(COMETKiwi).

**Novelty check (07-07-2026, verified):** no published work translates a *complete*
historical bilingual dictionary with LLMs. Nearest neighbor —
[Jürviste & Jakobson 2025, arXiv:2510.07931](https://arxiv.org/abs/2510.07931)
(vision-LLM digitization + modern-Estonian *enrichment* of 17th–18th-c. Estonian-German
dictionaries; no third-language translation, partial coverage). Must-cite and
differentiate.

## Data inventory (every claimed result → committed artifact or flagged gap)

| result | artifact | status |
|---|---|---|
| pipeline + gates | [`RUN_FREQ_MAX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/RUN_FREQ_MAX.md), [`audit_window.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pilot/audit_window.py) | ✅ committed |
| store scale + provenance | 11,261 rows / 50 roots, 100 % `model_version` + pipeline stamps — [`H178_REAUDIT_2026-07-06.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/H178_REAUDIT_2026-07-06.md) | ✅ committed (store local-only, rights) |
| error taxonomy | [`ERROR_ANALYSIS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/ERROR_ANALYSIS.md) | ✅ committed |
| data statement | [`DATA_STATEMENT.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/DATA_STATEMENT.md) | ✅ committed |
| reproducibility | [`REPRODUCIBILITY.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/REPRODUCIBILITY.md) | ✅ committed |
| eval protocol + machinery | [`EVALUATION_PROTOCOL.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/pwg_ru/EVALUATION_PROTOCOL.md), [`h178_eval_bakeoff.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/h178_eval_bakeoff.py) | ✅ committed |
| **bake-off table (κ/ρ/cost/diagnostic)** | `pwg_ru/eval/h178_bakeoff_report.json` | ⛔ GAP — pending MG votes on 4 sheets |
| **COMETKiwi scores + correlations** | `pwg_ru/eval/h178_cometkiwi_scores.jsonl` | ⛔ GAP — pending one-time HF license/token |
| human-approved subset | G5 gate flips `ai_translated → approved` | ⛔ GAP — G5 not started |

## Outline

1. Introduction — the Petersburg tradition; why translate a superseded 19th-c.
   dictionary (Russian Sanskrit-studies infrastructure); LLM-era lexicography context
   (de Schryver 2023; Lew 2023).
2. The 5-layer source and its markup (PWG+Nachträge+PW+SCH+PWKVN+NWS; SLP1 spans,
   `{%…%}` glosses, `<ls>` citations) — bridge to digitization (Jürviste & Jakobson
   2025; Khemakhem et al. 2017; TEI Lex-0).
3. Pipeline — harvest-first, Sonnet-5 generation, deterministic gates, TM reuse,
   autosplit/topup repair ladder, provenance stamps (REPRODUCIBILITY.md distilled).
4. Error analysis — taxonomy × frequencies × examples (ERROR_ANALYSIS.md distilled);
   linguistic vs infrastructural split.
5. The evaluation bake-off — design (EVALUATION_PROTOCOL.md), results table, the chosen
   standing protocol, COMETKiwi correlation + domain-validity caveat.
6. Data statement + limitations (single annotator; human×model agreement labeling;
   superseded Vedic philology).
7. Related work + conclusion.

## Related work (verified 07-07-2026, Fable 5 `claude-fable-5` research pass; all links live)

**LLM-assisted lexicography.**
- de Schryver (2023). Generative AI and Lexicography: The Current State of the Art Using ChatGPT. *IJL* 36(4). [academic.oup.com/ijl/article/36/4/355/7288213](https://academic.oup.com/ijl/article/36/4/355/7288213) — field-defining survey; frames human+machine verification protocols.
- Lew (2023). ChatGPT as a COBUILD lexicographer. *HSSC* 10. [nature.com/articles/s41599-023-02119-6](https://www.nature.com/articles/s41599-023-02119-6) — blinded expert evaluation of LLM entries; methodological template for our human channel.
- Jürviste & Jakobson (2025). Vision-Enabled LLMs in Historical Lexicography. [arXiv:2510.07931](https://arxiv.org/abs/2510.07931) — closest prior art; digitization+enrichment, not full translation.

**Human MT-evaluation protocols.**
- Freitag et al. (2021). Experts, Errors, and Context. *TACL* 9. [aclanthology.org/2021.tacl-1.87](https://aclanthology.org/2021.tacl-1.87/) — MQM canon.
- Graham et al. (2013). Continuous Measurement Scales in Human Evaluation of MT. *LAW 7*. [aclanthology.org/W13-2305](https://aclanthology.org/W13-2305/) — Direct Assessment origin.
- Callison-Burch et al. (2007). (Meta-) Evaluation of Machine Translation. *WMT*. [aclanthology.org/W07-0718](https://aclanthology.org/W07-0718/) — adequacy/fluency Likert + pairwise ranking canon.

**Reference-free QE.**
- Rei et al. (2022). CometKiwi: IST-Unbabel 2022 Submission. *WMT22*. [aclanthology.org/2022.wmt-1.60](https://aclanthology.org/2022.wmt-1.60/) — `wmt22-cometkiwi-da`.
- Rei et al. (2023). Scaling up CometKiwi. *WMT23*. [aclanthology.org/2023.wmt-1.73](https://aclanthology.org/2023.wmt-1.73/) — `wmt23-cometkiwi-da-xl/-xxl`.
- Zerva et al. (2022). Findings of the WMT 2022 QE Shared Task. *WMT22*. [aclanthology.org/2022.wmt-1.3](https://aclanthology.org/2022.wmt-1.3/).

**Sanskrit NLP / MT.**
- Aralikatte et al. (2021). Itihāsa: Sanskrit-English corpus. *WAT 8*. [aclanthology.org/2021.wat-1.22](https://aclanthology.org/2021.wat-1.22/).
- Nehrdich (2022). SansTib. *LREC*. [aclanthology.org/2022.lrec-1.724](https://aclanthology.org/2022.lrec-1.724/).
- Sandhan et al. (2022). TransLIST. *Findings of EMNLP*. [aclanthology.org/2022.findings-emnlp.513](https://aclanthology.org/2022.findings-emnlp.513/).
- Nehrdich, Hellwig & Keutzer (2024). ByT5-Sanskrit. *Findings of EMNLP*. [aclanthology.org/2024.findings-emnlp.805](https://aclanthology.org/2024.findings-emnlp.805/).

**Digitization + data statements.**
- Bender & Friedman (2018). Data Statements for NLP. *TACL* 6. [aclanthology.org/Q18-1041](https://aclanthology.org/Q18-1041/).
- Khemakhem, Foppiano & Romary (2017). Automatic Extraction of TEI Structures in Digitized Lexical Resources. *eLex 2017*. ⚠ verified via secondary sources only — re-check before camera-ready.
- Tasovac, Romary et al. (2018). TEI Lex-0. ⚠ same caveat.

## Candidate venues (liveness-checked 07-07-2026)

1. **International Journal of Lexicography** (OUP; rolling) — strongest fit; both anchor papers appeared there.
2. **EURALEX 2026** (Vienna, 29-09→03-10-2026, theme "Lexicography in the Age of AI") — main deadline likely passed; check late-breaking/poster.
3. **eLex 2027** — CFP not yet out.
4. **GWC 2027** / **LREC 2028** — resource-paper framing.
5. **WMT research track** — the evaluation-methodology angle alone.

Route the final venue choice through `/venue-scout A51` + `/decision-record` when
readiness reaches 3–4.

_Dr. Mārcis Gasūns_
