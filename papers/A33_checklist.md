# A33 — ARR Responsible NLP + reproducibility checklist (dry run)

_Created: 11-07-2026 · Last updated: 11-07-2026_

Filled per the checklist gate added to
[`/paper-submission-pack`](https://github.com/gasyoun/claude-config/blob/main/commands/paper-submission-pack.md)
Phase 3.5 and [`/paper-referee`](https://github.com/gasyoun/claude-config/blob/main/commands/paper-referee.md)
Phase 2 (H666, 11-07-2026). Checklist source:
[aclrollingreview.org/responsibleNLPresearch](http://aclrollingreview.org/responsibleNLPresearch/),
fetched 11-07-2026, page marked "Updated for ARR October 2024 cycle". Subject:
[A33_sense_ordering_note.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A33_sense_ordering_note.md)
("Genetic, not historical...", readiness 4/5, target Lexikos / IJL / eLex — none ARR-governed,
so this is a dry run/internal quality check, not a required submission artifact per the
venue-calibration rule below).

## A. General

| Item | Status | Pointer |
|---|---|---|
| A1. Limitations discussion | **no** | The note has no dedicated Limitations section. §5 states one methodological caveat (the fixed sense-delimiter regex bug) but doesn't discuss scope-of-claims limits (single-language-family sample, PWG/MW-only for the quantitative core, AP90 Vedic-siglum recall explicitly flagged as unverified in "To do before submission"). |
| A2. Risk discussion | n/a (partial) | No human/societal-harm surface — this is corpus philology, not deployed NLP. Dual-use / fairness / privacy are not applicable to 19th-century dictionary text. |

## B. Scientific artifacts

| Item | Status | Pointer |
|---|---|---|
| B1. Citation of creators | **yes** | §"References" cites PWG, PW, MW, GRA, AP90, Kochergina with full bibliographic detail; CDSL cited as primary digital source with URL. |
| B2. Licenses/terms | **no** | No license statement for the CDSL editions (`csl-orig`) or the citation-dating map (`ls_source_map.json`) used as inputs. Gap — should cite CDSL's stated terms of use. |
| B3. Intended-use compatibility | n/a | Research/scholarly use of public-domain 19th–20th-c. dictionary text; no derivative-license conflict apparent. |
| B4. Personal info / offensive content | n/a | No personal data or human-subject content — historical lexicographic text only. |
| B5. Artifact documentation | **partial** | Domain (Sanskrit lexicography) and source editions are named; no formal data-statement/datasheet exists for the citation-dating map itself. |
| B6. Dataset statistics | **yes** | §3.1/§3.3 report exact entry/citation counts (11,882 PWG entries, 13,822 MW entries, 113,012/99,716/19,163/29,177 cited senses per dictionary). |

## C. Computational experiments

| Item | Status | Pointer |
|---|---|---|
| C1. Model/infra details | n/a | No ML model — this is a corpus-statistics study (counting, Kendall τ), not a trained model. |
| C2. Experimental setup | **yes** | §2 Method fully specifies the extraction and computation procedure (sense segmentation per dictionary format, dated-citation extraction, the three measured statistics). |
| C3. Descriptive statistics | **partial** | Point estimates given throughout with explicit chance-floor/ceiling framing (§3.1); no confidence intervals or error bars are reported for the percentages/τ values — a reproducibility gap worth flagging for a full submission. |
| C4. Package/tool versions | n/a | No third-party NLP toolkits used (regex/counting scripts only); scripts are self-contained and linked. |

## D. Human annotators/participants

| Item | Status | Pointer |
|---|---|---|
| D1–D5 | **n/a** | No human annotation or participant study — all data is derived mechanically from digitized dictionary markup. |

## E. AI assistant usage

| Item | Status | Pointer |
|---|---|---|
| E1. Disclosure of AI assistants | **yes** (should be stated in-paper) | The note's own status line credits "Fable 5 (`claude-fable-5`)" for the hostile referee pass (03-07-2026); the analysis scripts and this note were produced with heavy AI-agent assistance throughout the `pwg_ru`/RussianTranslation pipeline. **Gap:** the manuscript itself has no explicit AI-assistant disclosure statement in a Methods/Acknowledgements section — currently only inferable from the repo's provenance conventions, not stated for a reader outside this org. Recommend adding one line before submission. |

## Verdict

Not blocking for the current non-ARR target venues (Lexikos / IJL / eLex — none require
the formal checklist artifact per the venue-calibration rule), but two items are worth
fixing before submission regardless: **A1** (add a real Limitations paragraph — scope of
claims, single-language-family/only-2-dictionaries-quantitative-core caveat, the flagged
AP90 recall gap) and **E1** (add an explicit AI-assistant disclosure line). B2/B5 are minor
polish (a one-line CDSL terms-of-use citation). This is a report only — fixes are not
applied here; see [A33_review_fable5.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A33_review_fable5.md)
for the existing hostile-review memo, which this checklist supplements rather than replaces.

_Sonnet 5 (`claude-sonnet-5`), 11-07-2026, H666 dry run._
