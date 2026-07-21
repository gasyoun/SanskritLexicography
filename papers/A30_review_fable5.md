# A30 — referee-style review (pre-submission, hostile)

_Created: 21-07-2026 · Last updated: 21-07-2026_

Hostile pre-submission review of
[papers/A30_skd_vcp_microstructure_note.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A30_skd_vcp_microstructure_note.md)
("When Zero Means Nothing: Recovering the Indigenous Microstructure of the Śabdakalpadruma
and the Vācaspatya", → IJL / WSC 2027) by **Fable 5 (`claude-fable-5`)**, 21-07-2026, under
handoff [H1382](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1382-Fable_SanskritLexicography_a30-hostile-referee-pass-skd-vcp_20.07.26.md).

**Fresh-session constraint (recorded per the handoff header).** The A30 draft was authored by
the same model tier (Fable 5, H1073). This pass was run as a fresh session with no memory of
the authoring choices: the committed draft was read as a stranger's manuscript, and every
figure was re-verified against the committed csl-atlas artifacts at `origin/main`
(commit `a56444f`, 21-07-2026) rather than taken on trust. Structured by the C1–C7
error-class checklist of
[PORTFOLIO_STATISTICAL_REDTEAM_2026H2.md](https://github.com/gasyoun/Uprava/blob/main/docs/PORTFOLIO_STATISTICAL_REDTEAM_2026H2.md)
§1/§5. Companion deliverables from the same pass:
[papers/A30_SKD_ITI_ADJUDICATION_MODEL_PASS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A30_SKD_ITI_ADJUDICATION_MODEL_PASS.md)
(the ~100-unit sample, model-labelled) and the edition-facts check (§Edition-facts below).

**Overall verdict: major revision; the 4/5 gate is NOT cleared as drafted.** Sections 1–5 and
the §9 doctrine are excellent and fully artifact-backed — every number in them re-verified
exact (table below). But the paper's quantitative centrepiece, the 53.3 % / 77.6 % fusion
contrast of §6 and the register reading built on it in §7, rests on a classifier whose
committed sample exposes **three distinct instrument artifacts** (severed citations, a
16-name recall ceiling, and formula false-positives), and the "short SKD entry vs. long VCP
commentary" causal story is contradicted by the corpus's own committed length statistics —
SKD records are *longer* than VCP's on both mean and median, and VCP has *more* records, not
"fewer". A referee who opens
[`r2_kosa_fusion_sample.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_kosa_fusion_sample.json)
(the paper's own validation sample) will see rows like `SUkaraH . ityamaraH` classed
"separable" and bare severed `medinI ..` tails filling that class in minutes. The honest
version — fusion classes reported as instrument-relative, with the artifacts disclosed — is
still a good paper, because the thesis ("a zero measures the instrument") survives; indeed
the classifier's own failure modes are a *fourth demonstration* of the thesis. As drafted,
however, §6–§7 commit the exact sin the paper warns against: reading an instrument's output
as the object's property.

The handoff's central question — **does disclosure discharge the objection, or merely name
it?** — gets a split answer below: limitation 5 (VCP underread) names a real issue and is
partially discharged; limitations 1–2 name their issues but do **not** discharge them,
because the abstract and §6 still state the numbers as findings and §7 still ranks on them.

---

## Major findings

### M1. The "separable" class is substantially an orthographic sandhi artifact — CONFIRMED

The unit splitter
([`splitIndigenous()`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-source-anchors.mjs))
cuts after every **standalone** `iti`; SKD authority detection
([`build-r2-kosa-fusion.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-kosa-fusion.mjs))
keys on the **sandhi-fused** `ity<word>` pattern plus a curated name list. Consequence: a
citation written fused (*ityamaraḥ* — obligatory sandhi before a vowel-initial name) stays in
its content unit and can be classed fused; a citation written unfused (*iti medinī*, *iti
hemacandraḥ* — no sandhi before consonant-initial names) is **severed at the split**, its
content unit drifting to `other-no-authority` and its name-tail landing in `separable` at
offset ≈ 0. The script's own comment concedes the mechanism ("still surface as a leading
token of the tail unit once split on iti").

The committed sample proves it is not marginal: of the 34 `separable` rows in
[`r2_kosa_fusion_sample.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_kosa_fusion_sample.json),
**about 24 are bare leading-name tails** — `medinI .`/`medinI ..` ×13, `hemacandraH ..` ×11
— i.e. the tail halves of citations that are philologically *fused* ("…haridrā **iti
medinī**" is a definition run closing in its citation, exactly like "…**ityamaraḥ**").
Whether an SKD citation counts fused or separable therefore depends substantially on
**whether the authority's name begins with a vowel**. Failure scenario: a referee samples the
separable class, finds it dominated by Medinī/Hemacandra name-tails, and concludes the
53.3 %/46.7 % split measures sandhi orthography, not lexicographic structure. Not disclosed
in §8; limitation 1's "iti also serves grammatical quotation" is a different defect.

### M2. The authority detector's recall ceiling biases the fusion denominator — CONFIRMED

SKD authority detection = a **16-name curated list** plus the `ity<word>` regex. The sampled
`other-no-authority` class (98,604 of 122,691 SKD units — 80 %) visibly contains severed real
authority citations the list misses: *halāyudhaḥ* (L1501), *rājanirghaṇṭaḥ* (L16657, L17951,
L29776), *trikāṇḍaśeṣaḥ* (L19244), *mugdhabodhaṭīkāyāṃ durgādāsaḥ* (L22951),
*tadbhāṣye sāyaṇaḥ* (L33424), *medinīkarahemacandrau* (L4313), *saṃkṣiptasāroṇādivṛttiḥ*
(L26380), *śrīmāgavate* (L8159 — the Bhāgavata, defeated by an M/B typo), *skandapurāṇe*
(L9421) — 13 of that class's 34 sampled rows are plainly citational. A08's independent count
([`citation_registers.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/obs/citation_registers.json))
finds **80,164** *iti*-citations in SKD, yet the fusion build's authority-marked denominator
is only **24,087** — the fusion statistic is computed over a ~30 % subsample skewed toward 16
names and vowel-initial sandhi forms. Failure scenario: a referee divides 24,087 by 80,164,
asks what happened to the other 56,000 citations, and the answer is "the fusion
classifier cannot see them." The 53.3 % is a property of that biased subsample; nothing
commits it to hold on the full citation register.

### M3. Fusion is quasi-deterministic in unit length, and the two "unit" populations are different objects — CONFIRMED (C1 + C2 + C4 jointly)

The fusion rule is: authority-marked unit + **≥ 20 non-whitespace chars before the earliest
authority match** ⇒ `authority-terminal`, else `separable`
(`FUSION_MIN_CONTENT_CHARS = 20`). The classifier never checks that the citation actually
*closes* the unit — "authority-terminal" is a misnomer for "authority not near the unit
start". Three consequences, all visible in committed data:

- **Denominator asymmetry (C1).** SKD units are standalone-*iti*-delimited micro-segments
  (122,691 units, 2.88/record); VCP has few standalone *iti* (inline-*iti* share 10.08 %),
  so its 65,675 "units" are mostly **whole-record lumps** (1.31/record; the splitter's own
  `lumped-proxy` confidence class). And "authority-marked" uses **different detectors** per
  dictionary (curated names + `ity`-regex for SKD; the `<name>0` siglum regex for VCP). The
  §6 table therefore compares percentages over two different kinds of object counted by two
  different instruments, while presenting them as one contrast. Limitation 5 discloses only
  the VCP *undercount* direction — not the object mismatch.
- **Length mechanism (C2).** For a long whole-record VCP unit, ≥ 20 chars before the first
  inline siglum is nearly automatic — VCP's 77.6 % "fusion" is close to a tautology of unit
  length, not evidence that "its authority citations more often close their discursive unit"
  (§6 asserts closure; the instrument never measures it).
- **One-sided default (C4).** Below-threshold authority units default to `separable`, so both
  misclassification streams — M1's severed name-tails *and* genuinely fused short runs —
  land on the same side, deflating SKD. Sampled proof of the second stream:
  `SUkaraH . ityamaraH` (L11871), `vrahmA . ityekAkzarakozaH` (L5630), `baRik .
  ityamarawIkAyAM BarataH` (L34212) — definition-closing-in-citation units, classed
  separable purely by the 20-char rule. The fraction of units within a few characters of the
  threshold is reported nowhere.

Failure scenario: a referee asks for the §6 table with (a) one shared unit definition and
(b) any length control, and neither exists in any committed artifact.

### M4. The register story's empirical premise is contradicted by the corpus's own statistics — CONFIRMED

The abstract states the fusion difference "tracks record type (short encyclopaedic entry vs.
long discursive commentary), not dictionary identity"; §7 characterizes VCP as "fewer,
longer, argumentative entries". Against
[`data/dictionary-coverage.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/dictionary-coverage.json)
(the artifact §7 itself cites): SKD meanChars **531** vs VCP **493**; medians **221** vs
**162**; records SKD **42,531** vs VCP **50,135**. So VCP entries are *more numerous* (not
"fewer") and *shorter on average* (not "longer") — the discursive VCP register is a tail
phenomenon (maxChars 312,261 vs 143,469), not the typical record (median 162 chars is a
stub). "Fewer" is contradicted by the paper's **own §1/§6 tables** on the same page. And no
committed artifact stratifies fusion by record length or record type: A02's re-scoping
([`paper_sense_inheritance.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_sense_inheritance.md)
§7) is a qualitative reading of the same aggregate rates, not a test. A30's "A02 … tested
whether fusion is a dictionary-level trait" overstates what the companion committed. Failure
scenario: a referee reads "fewer, longer", checks the paper's own Table in §1, and the
paper's credibility on everything quantitative is spent at that moment.

### M5. Formula false-positives contaminate the authority signal — CONFIRMED

`\bity[a-zA-Z]{3,}\b` matches the ubiquitous non-citational formulas *ityarthaḥ* ("that is
the meaning"), *ityādi* ("etc."), and grammatical fragments. In the committed sample:
L8904 *kaidāraḥ* is authority-marked **via `ityarTaH`** (the unit happens to also contain a
real Bhāvaprakāśa quote); L3336 *āḍhyaḥ* matches `ityAdiH` (an example-list closer); L37137
*saṃyat* matches `ityamya` (inside a Pāṇinian vārttika gloss). The build script's own header
lists `ityetyAdi` as a covered pattern — the false-positive class is designed in, not
accidental. Limitation 1's "upper-bound proxy" hedge names the neighbourhood but the §6
table still reports 24,087/42,980 "authority-marked units" as counts. This is the C3
exposure the portfolio red-team calls dominant, and it is real here: **the headline is an
instrument output awaiting validation, and the validation has not happened** — the ~100-unit
sample is drawn but unadjudicated (a model pass, clearly labelled as such, now exists:
[A30_SKD_ITI_ADJUDICATION_MODEL_PASS.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A30_SKD_ITI_ADJUDICATION_MODEL_PASS.md);
the human gate remains open).

### M6. The threshold sensitivity run is still un-run — CONFIRMED (disclosed, not discharged)

Limitation 2 concedes `FUSION_MIN_CONTENT_CHARS = 20` is "documented, not calibrated"; the
artifact's own limitations block says a re-run "may shift the fused/separable split modestly"
— an unquantified reassurance. Given M3's mechanism, the threshold is not a nuisance
parameter but the *definition* of the headline statistic; no committed table reports even one
alternative threshold. The paper's to-do already calls this "cheap insurance". A referee
reads an uncosted, un-run cheap check next to a headline built on it as unwillingness to
look. Disclosure names the objection; only the run discharges it.

### M7. The planned validation instrument validates the wrong axis — CONFIRMED

The adjudication sheet
([`REVIEW_SKD_ITI_ADJUDICATION.html`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/REVIEW_SKD_ITI_ADJUDICATION.html))
asks *citational vs grammatical* — the contamination axis (M5). Even fully human-adjudicated,
it cannot validate the *fused vs separable* boundary (M1–M3), because its rows are the same
severed units: 15 of the 34 `other-no-authority` rows end at "… iti" with the deciding
authority name sitting in the (invisible) next unit — undecidable out of context by design.
§8's limitation 1 implies the sample's adjudication would let the fusion figures "sharpen";
it would not — it tests a different property of a corrupted segmentation. The sheet needs a
following-context column and a post-stratification weighting note before the human pass (both
detailed in the model-pass companion). Failure scenario: the human adjudication is completed,
the paper claims the figures validated, and a referee points out the validated axis is not
the claimed one.

---

## C1–C7 verdicts (vs the red-team row `⚠️ | ⚠️ᵈ | ⚠️ᵈ | ⚠️ | ⚠️ᵈ | ⚠️ | ✅`)

| Class | Verdict here | Red-team | Where it differs and why |
|---|---|---|---|
| C1 denominator | **CONFIRMED** (M3) | ⚠️ | Escalated: units are different objects (micro-segments vs whole-record lumps) counted by different detectors — verified in the splitter code and unit-per-record ratios, not just suspected. |
| C2 length confound | **CONFIRMED** (M3, M4) | ⚠️ᵈ | Escalated: disclosure does not discharge — the ≥20-char rule makes fusion quasi-monotone in unit length, and the committed length stats *invert* the paper's short-SKD/long-VCP premise. |
| C3 classifier defect | **CONFIRMED** (M1, M2, M5, M7) | ⚠️ᵈ | Escalated: three concrete defect classes visible in the classifier's own committed sample; hedge covers only one of them, and the abstract still states the numbers as findings. |
| C4 fallback bucket | **CONFIRMED** (M3) | ⚠️ | Escalated: below-threshold + severed-tail misclassifications both default into `separable`, one-sidedly deflating SKD; near-threshold mass unreported. |
| C5 coverage overstatement | **CLEAN** (with note) | ⚠️ᵈ | **Downgraded** (per the red-team's own §4.7 precedent): the "of 44" rank claims verify exactly against the 44-file [`citation_registers.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/obs/citation_registers.json) (SKD `itiDensityRank` = 2; `<ls>` tied-last), the §3 snapshot convention is applied consistently at both rank statements, and §9's portability is framed as proposal ("will contain"), not result. Residual note: §7 itself warns "the indigenous tradition is not one convention" — keep that sentence when revising. |
| C6 single-run fragility | **CONFIRMED** (M6) | ⚠️ | Disclosed, undischarged; the threshold is the statistic's definition, not a detail. |
| C7 cross-paper drift | **CLEAN** (re-derived, 2 footnotes) | ✅ | Re-derived, not trusted: every imported figure traced (table below). Footnotes: (a) A08's 80,164/15,619 (44-file artifact) vs the regenerated 43-file [`dictionary-coverage.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/dictionary-coverage.json) now reading 80,173/15,627 — +9/+8 cross-artifact drift, immaterial but both live at `origin/main`; (b) the artifact label "Sabdakalpadruma 1822" carries the same one-year edition-date caveat as the paper (§Edition-facts). |

## Figure verification (all against csl-atlas `origin/main`, commit `a56444f`)

| A30 claim | Committed source | Verdict |
|---|---|---|
| SKD 42,531 / VCP 50,135 records | [`r2_kosa_fusion.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_kosa_fusion.json), [`dictionary-coverage.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/dictionary-coverage.json) | ✅ exact |
| §1 zero table (0/0/0/0; MW 182,097 · 15,312 · 350,610; PWG 185,563 · 113,613; MW 286,560 · PWG 123,366) | [`MICROSTRUCTURE_ZERO_MEANING.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_ZERO_MEANING.md) | ✅ exact |
| Measurement-doctrine quote | same doc | ✅ verbatim (ellipsis marked) |
| §4 *īr* worked example | same doc | ✅ verbatim |
| 2,544 / 2,230 template root records | [`indigenous_by_dict.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/indigenous_by_dict.json) | ✅ exact |
| 122,691 / 65,675 units; 2.88 / 1.31 per record; "roughly 188,000" | [`r2_kosa_fusion.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/r2_kosa_fusion.json) | ✅ exact (188,366) |
| §6 table: 18,418 (43.3 %) / 38,459 (76.7 %); 24,087 / 42,980; 12,831 (53.3 %) / 33,352 (77.6 %); 11,256 (46.7 %) / 9,628 (22.4 %) | same | ✅ exact |
| ≥20 non-whitespace-char fusion threshold | [`build-r2-kosa-fusion.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-r2-kosa-fusion.mjs) (`FUSION_MIN_CONTENT_CHARS`) | ✅ (but see M3/M6) |
| 46 anubandha letters; Palsule 43 | [`MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md) | ✅ exact |
| 1,117→1,737 (55 %) gaṇa; 1,167→1,498 (28 %) pada; ~1,925 of 2,544 (76 %) | same | ✅ exact (55.5 % / 28.4 % / 75.7 %) |
| śūnya rule (*bindu-yuktam athavā śūnyam*) | same doc | ✅ present |
| 85.5 % five-lexicon verb-class compatibility (cited as A04's) | [`MICROSTRUCTURE_ROOT_AGREEMENT.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/MICROSTRUCTURE_ROOT_AGREEMENT.md) (1,305/1,526) | ✅ exact; note the chance-corrected companion ([`root_agreement_kappa.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/root_agreement_kappa.json), gaṇa κ ≈ 0.81) exists and could be cited alongside |
| A08 figures: 80,164 / 15,619 / 1.88 per record; rank 2nd of 44 by *iti*-density; `<ls>` tied-last | [`paper_citation_registers.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_citation_registers.md) Table 2 + [`citation_registers.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/obs/citation_registers.json) | ✅ exact (see C7 footnote a) |
| §7 register shares (2.49 / 6.98 / 73.27 / 80.11; 0 / 0 / 79.13 / 94.30; 88.78 / 10.08 / 0.06 / 0.67) | [`dictionary-coverage.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/dictionary-coverage.json) `blockPct` | ✅ exact |

No figure in A30 fails verification against its cited artifact. The findings above concern
what the artifacts' numbers *mean*, not their transcription — which is itself a lesson in the
paper's own doctrine: exact citation of an instrument's output does not validate the
instrument.

## Minor findings

1. **A08-vs-coverage drift footnote** (C7-a above): if §6 keeps the A08 totals, add one
   sentence pinning them to the 44-file artifact, since the sibling 43-file coverage build
   now carries 80,173/15,627.
2. **Wiegand cite-to-survey** (§5): already on the paper's own to-do; a lexicography referee
   will demand the precise essay. Also verify the 1989 volume/essay pairing when substituting.
3. **§6.2's "80,164 … 1.88 per record" phrasing**: these are *iti*-token counts (A08's
   upper-bound register indicator); when M1/M2/M5 fixes land, keep the token-vs-citation
   distinction explicit at every mention, not only in limitation 1.
4. **"second of 44, behind only the Kṛdantarūpamālā"**: robust — rank 2 in both the 43-file
   and 44-file builds, and the gap to rank 3 (VCP, 0.31/record) is 6×. Keep; this is the
   paper's strongest single statistic.
5. **§5 "agreement figures cited in §5"**: the 85.5 % figure could carry its κ companion
   (minor strengthening, artifact already committed).

## Edition-facts check (limitation 6 / to-do item 1)

Each fact stated by the paper, verdict per the handoff's confirmed/corrected/unverifiable
rule:

| Fact as stated | Verdict | Evidence |
|---|---|---|
| SKD "published in parts from 1822"; References "Deva, Rādhākānta (1822–1858)" | **CORRECTED → 1821/22–1858** | The Bengali-script original ran to 8 parts with per-volume dates 1821, 1827, 1832, 1838, 1844, 1848, 1851, 1857, plus the supplement volume 1858 — per the Bavarian State Library's digitized set as reported on the [INDOLOGY list](https://www.mail-archive.com/indology@list.indology.info/msg05710.html) and the [wisdomlib kośa survey](https://www.wisdomlib.org/hinduism/essay/the-backdrop-of-the-srikanthacarita-and-the-mankhakosa/d/doc370629.html); [Banglapedia](https://en.banglapedia.org/index.php/Shabdakalpadruma) gives 1819 for a first volume (outlier, likely a compilation milestone). Because SKD title pages carry Śaka dates that straddle CE years, the defensible form is "8 parts, Calcutta 1821/22–1857, supplement 1858". A Devanāgarī re-edition followed 1886. |
| VCP "1873–1884"; References "Tarkavācaspati, Tārānātha (1873–1884)" | **CONFIRMED** | Vol 1 of the original is catalogued at 1873 ([Internet Archive, "1873 - Vachaspatya … Vol 1 of 6"](https://archive.org/details/wg1032)); the original serial issue was titled "A Comprehensive Sanscrit Dictionary. In Twenty Parts", with Part IX dated Calcutta 1875 and Part XVIII dated 1882 (scan title pages), consistent with completion 1884. A stray "1870–1884" appears only in a commercial catalogue listing and can be dismissed. |
| SKD compiled by "Rādhākānta Deva's team" | **CONFIRMED** | Compiled over ~40 years by paṇḍits working under Rādhākānta Deva, editorial credit to Karunasindhu Vidyanidhi ([Banglapedia](https://en.banglapedia.org/index.php/Shabdakalpadruma)); the 1859 "Rapid Sketch" is credited to "the editors of the Raja's Sabdakalpadruma" — a team, as the paper says. |
| VCP compiled by Tārānātha Tarkavācaspati (single compiler implied) | **CONFIRMED** | Title pages name only Tārānātha Tarkavācaspati (1812–1885). |
| Volume structure | **Nothing to verify in-text** | The paper wisely states no volume counts. For the to-do's completion: SKD original = 8 parts (Bengali script; modern reprints 5 vols); VCP original = 20 parts (modern reprints 6 vols). The exact Śaka date on SKD part 1's title page remains **unverifiable from this session** — recommend one direct look at the Bavarian State Library scan before submission. |
| The csl-atlas artifact label "Sabdakalpadruma 1822" | **Same caveat** | Inherits the 1821/22 correction; a one-character label fix in csl-atlas when next regenerated. |

## What is solid (keep and foreground)

- **§§1–5 are artifact-exact end to end** — the zero inventory, the doctrine quote, the *īr*
  template, the anubandha key layer (46 letters, the 55 %/28 % decode gains, the 76 % slot
  coverage), and the printed śūnya rule, which remains the paper's best exhibit and the
  title's justification.
- **The rank-inversion statistic** (tied-last by `<ls>`, 2nd of 44 by *iti*-density) is
  robust across both committed corpus builds and survives every finding above — it depends
  on raw *iti* token counts, not on the fusion classifier.
- **The §9 doctrine and its portability framing** — correctly stated as proposal, and
  strengthened, not weakened, by M1–M5: the fusion classifier's failure modes are themselves
  a demonstration that instruments built on one convention family misread another.
- **§8's candour** is real (7 numbered limitations); the problem is not honesty but that
  §6–§7's claims outrun what the hedges license.

## Disposition

| # | Where the fix lands | Effort |
|---|---|---|
| M1, M2, M5 | csl-atlas segmenter/detector (name-aware splitting, expanded authority list, formula exclusion) — **out of A30's no-new-computation scope**; the paper-side fix is to re-scope §6 as instrument-relative and disclose the three artifact classes | medium (paper-side: minor) |
| M3 | §6 prose + table caption: one shared unit definition, the object asymmetry stated; drop or heavily hedge the cross-dictionary 53.3-vs-77.6 *contrast* (per-dictionary within-instrument figures can stay) | minor |
| M4 | §7 "fewer, longer" corrected against the committed length stats; abstract's "short … vs. long …" causal clause removed or re-stated as hypothesis pending a stratified run | minor |
| M6 | the threshold-sensitivity table (to-do item 5) — run in csl-atlas, cite here | minor, mechanical |
| M7 | regenerate the adjudication sheet with a following-context column + weighting note, then the human pass (to-do item 2; model pass committed as companion) | minor + human |
| Edition facts | References + §2: "1822" → "1821/22" with the 8-part note | trivial |
| m1–m5 | §5/§6 text | trivial |

**Readiness proposal (a human decides):** hold at **3/5** until the M3/M4 paper-side
re-scope lands; with that revision committed (an afternoon of edits — no new computation
required), 4/5 is warranted, since §§1–5 + §9 already clear the bar and the referee gate
will then have been run. Venue note as input only: the M1–M7 profile argues for **WSC 2027**
over IJL for the *first* submission — a methods-aware Sanskritist audience will read the
instrument-relative re-scope as a strength; an IJL referee is likelier to bounce §6 outright.

The human gates recorded in the handoff remain open and are restated here: the 3/5→4/5 flip,
the venue `@DECIDE`, the A35↔A04↔A30 lead-paper `@DECIDE`, and the human adjudication of the
~100-unit sample (the committed model pass does **not** close that gate).

_Dr. Mārcis Gasūns_
