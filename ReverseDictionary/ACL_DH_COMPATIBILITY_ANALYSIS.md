# ACL Anthology compatibility + DH data-publication standards — Reverse Sanskrit Dictionary

_Created: 07-07-2026 · Last updated: 07-07-2026_

**What this is.** The deep analysis commissioned by
[H265](https://github.com/gasyoun/Uprava/blob/main/handoffs/H265-Fable_SanskritLexicography_acl-anthology-dh-standards-reverse-dict_07.07.26.md):
what "make the reverse dictionary ACL-Anthology compatible" actually means, which real venues
would take a paper about this resource, what those venues require, and which digital-humanities
data-publication standards the resource currently misses. Analysis only — no data was changed.
Subject: the ~266,820-headword reverse Sanskrit dictionary documented in
[`README.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/README.md)
(merged in [PR #203](https://github.com/gasyoun/SanskritLexicography/pull/203)).

**Provenance.** Researched and written 07-07-2026 by Fable 5 (`claude-fable-5`); venue liveness,
CFP, and standards facts verified the same day against primary web sources by four parallel
Explore subagents (also Fable 5 `claude-fable-5`, inherited), each claim carrying its source URL
below. Venue landscapes rot — re-verify any deadline before acting on it in 2027+.

---

## 0. Headline findings

1. **"ACL Anthology compatible" = publish a resource paper at an Anthology-indexed venue.**
   The [ACL Anthology](https://aclanthology.org) is a paper archive, not a data repository —
   nothing is "uploaded" to it directly. The dictionary gets into the Anthology by a paper about
   it appearing at an indexed venue. Good news: the Sanskrit-computational world is now firmly
   inside the Anthology — ISCLS, WILDRE, and (since 2025) even the World Sanskrit Conference's
   computational section are all indexed (§1).
2. **Timing: every 2026 edition has already happened.** As of 07-07-2026, LREC 2026 (May),
   ISCLS 2026 (March), WILDRE-8 (May), LaTeCH-CLfL 2026 (March), and NLP4DH 2026 (July 6) are
   all past. The nearest realistic submission targets are **LaTeCH-CLfL 2027** (CFP expected
   ~Nov–Dec 2026) and the **20th World Sanskrit Conference, December 2027, IIT Bombay** —
   with ISCLS/WILDRE/LREC following in 2028 on their biennial cycles.
3. **Licensing is the blocking gap, and it is a human's ruling, not a research conclusion.**
   The word list merges ~30 source dictionaries of wildly mixed copyright status (18 safely
   public domain, ~10 still in copyright somewhere, several unclear — full table in §3.1).
   Whether a merged *headword list* (no definitions) can be published openly is a genuine legal
   judgment call flagged as `@DECIDE` — this report supplies the per-source facts so the ruling
   can be made without re-deriving them. Everything else in the gap table (§3) is agent-doable
   and most of it does **not** wait on that ruling.
4. **A paper does not require releasing the data.** A descriptive resource paper (methodology,
   scale comparison vs. Schwarz 1974 / Stiehl 2004, word-formation use cases) is publishable at
   the §1 venues even while the raw list stays restricted-tier — the org already runs this
   two-tier pattern in
   [`kosha/data/manifest/datasets.json`](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json).
   An open-data release makes the paper stronger, but the licensing `@DECIDE` gates only the
   data tier, not the paper itself.

---

## 1. Venue landscape (liveness verified 07-07-2026)

| # | Venue | Anthology-indexed | Liveness evidence | Next edition / deadline | Fit |
|---|---|---|---|---|---|
| 1 | **World Sanskrit Conference — §23 "Computational Sanskrit & Digital Humanities"** | ✅ since 2025 ([2025.wsc-csdh](https://aclanthology.org/2025.wsc-csdh.0/), eds. Kulkarni & Hellwig, 13 papers) | 19th WSC held Kathmandu, June 2025 ([event page](https://aclanthology.org/events/wsc-2025/)) | **20th WSC, 10–14 Dec 2027, IIT Bombay** ([official site](https://www.hss.iitb.ac.in/wsc2027/)); computational track unconfirmed for 2027 but historically present | **Best fit.** The exact audience (Indologists + computational Sanskritists); a lexicographic resource paper is squarely in scope; Anthology indexing achieved. |
| 2 | **ISCLS — International Sanskrit Computational Linguistics Symposium** | ✅ ([2026.iscls-1](https://aclanthology.org/2026.iscls-1.0/)) | 8th ISCLS held 9–11 Mar 2026, IIT Roorkee ([site](https://iscls.github.io/)) | 9th expected **~2028** (biennial), unannounced | **Strong fit**, but a ~20-month wait. Scope explicitly includes Sanskrit lexical resources. |
| 3 | **LaTeCH-CLfL** (SIGHUM workshop on cultural-heritage/humanities NLP) | ✅ ([venue page](https://aclanthology.org/venues/latechclfl/), 2026 ed. = 33 papers) | 10th ed. held 28–29 Mar 2026 at EACL, Rabat ([sighum.wordpress.com](https://sighum.wordpress.com/events/sighum-latech-clfl-2026/)) | Annual — **2027 CFP expected ~Nov–Dec 2026** (2026 deadline was 5 Jan 2026) | **Nearest actionable deadline.** Accepts long (8pp) + short (4pp) papers in [ACL style](https://github.com/acl-org/acl-style-files); historical-language resources are core scope. |
| 4 | **NLP4DH** (NLP for Digital Humanities) | ✅ ([venue page](https://aclanthology.org/venues/nlp4dh/)) | 6th ed. held 6 Jul 2026 at ACL, San Diego ([nlp4dh.com](https://www.nlp4dh.com/nlp4dh-2026)) | Annual — 2027 expected (2026 deadline was 13 Mar 2026); submits via OpenReview, direct or ARR | Good fit; slightly more tool/method-oriented than pure resources. |
| 5 | **WILDRE** (Indian Language Data: Resources and Evaluation, at LREC) | ✅ ([venue page](https://aclanthology.org/venues/wildre/)) | WILDRE-8 held 12 May 2026 at LREC, Palma ([site](https://sanskrit.jnu.ac.in/conf/wildre8/)) | **~2028** with LREC (biennial) | Strong fit — Indic-resource-specific, run from JNU's Sanskrit school. |
| 6 | **LREC main conference** | ✅ ([venue page](https://aclanthology.org/venues/lrec/)) | LREC 2026 held 11–16 May 2026, Palma de Mallorca ([lrec2026.info](https://lrec2026.info/)); biennial, now standalone (not joint with COLING) | **LREC 2028** (2026 deadline was 17 Oct 2025) | The flagship language-resource venue — highest prestige for a resource paper, longest wait. |

Checked and set aside: **ICON** (Anthology-indexed [through 2024](https://aclanthology.org/venues/icon/)
only — 2025/2026 proceedings absent as of today; liveness unverified, don't plan on it),
**ML4AL** (one edition, [2024](https://aclanthology.org/venues/ml4al/); 2026 status unverified),
**ALP** (last confirmed [2025](https://aclanthology.org/venues/alp/); possibly biennial → watch
for a 2027 CFP — would be a reasonable backup), DravidianLangTech / LT-EDI (out of scope for
Sanskrit).

**Non-ACL alternative worth naming:** for a pure *data paper* (dataset description, no
research claims), the [Journal of Open Humanities Data](https://openhumanitiesdata.metajnl.com/)
is the standard DH outlet — but it presupposes an openly deposited dataset with a DOI, i.e. it
sits **behind** the licensing `@DECIDE` (§3.1), whereas the ACL-venue paper does not.

**Recommendation:** target **LaTeCH-CLfL 2027** as the near-term shot (deadline ~Dec 2026–Jan
2027, ACL-style long paper) and treat **WSC 2027** as the flagship venue where the fullest
version belongs; the two are not mutually exclusive (workshop paper ≠ conference paper if
content is appropriately differentiated). Venue *choice* is a human's call — route via
`/decision-record` or the GTD `@DECIDE` row when a paper is actually scaffolded.

---

## 2. What the target venues actually require

Verified against the current (2026) rules; re-check when the 2027 CFPs appear.

**ACL-family workshops (LaTeCH-CLfL, NLP4DH) and ARR:**

- **Template:** the official [ACL style files](https://github.com/acl-org/acl-style-files)
  (LaTeX/Overleaf or Word). Non-conforming submissions are rejected without review
  ([ACLPUB formatting](https://acl-org.github.io/ACLPUB/formatting.html)).
- **Page limits:** long papers 8 pages content, short papers 4, references/appendices unlimited,
  +1 page at camera-ready ([ARR CFP](https://aclrollingreview.org/cfp)).
- **Mandatory "Limitations" section** (unnumbered, before references, outside the page limit) —
  missing it is desk rejection ([ARR CFP](https://aclrollingreview.org/cfp)). Still in force in 2026.
- **[Responsible NLP Research checklist](https://aclrollingreview.org/responsibleNLPresearch/):**
  §B (scientific artifacts) is the one that bites this resource — it requires **citation,
  license/terms documentation, provenance, and use-restriction disclosure for every artifact
  used or released**. I.e. the §3.1 licensing table below is not optional apparatus; a version
  of it must exist for the paper itself to pass the checklist honestly.
- **Anonymized review** (double-blind) for ARR and most workshops.
- Workshops submit **directly** (SoftConf/OpenReview per workshop), not through ARR — though
  NLP4DH also accepts ARR-reviewed papers ([nlp4dh.com](https://www.nlp4dh.com/nlp4dh-2026)).
  ARR itself now runs ~5 ten-week cycles/year ([dates](https://aclrollingreview.org/dates)) and
  is the sole route into ACL/EMNLP/NAACL/EACL main conferences.

**LREC (for the 2028 horizon):** its own stylesheet (not ACL's — `lrec2026.sty` equivalent will
be reissued), 4–8 pages excluding references/limitations, direct SoftConf submission, and —
a change from LREC tradition — **anonymized submissions** are now required, though with no
preprint embargo ([LREC 2026 FAQ](https://lrec2026.info/faq/),
[author's kit](https://lrec2026.info/authors-kit/)). LREC explicitly invites "all aspects of
language resource development" ([2nd CFP](https://lrec2026.info/calls/second-call-for-papers/)) —
a reverse-dictionary compilation paper is a textbook LREC resource paper.

**WSC / ISCLS / WILDRE:** each issues its own CFP with per-edition formatting; ISCLS 2026 and
WSC-CSDH 2025 proceedings are Anthology-formatted, so expect ACL-style templates there too.
No 2027/2028 CFPs exist yet to verify against — a follow-up check belongs to whichever session
scaffolds the paper.

---

## 3. DH data-standard gap analysis

Current state read from the working tree on 07-07-2026 (master list
[`266820-reverse-Gasuns.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/.doc.pdf/266820-reverse-Gasuns.txt):
266,819 data lines, tab-separated `SOURCE_LETTER<TAB>IAST-word`, **UTF-8 with BOM** `EF BB BF` —
checked directly, not assumed).

| Dimension | Current state | Standard practice | Gap / action |
|---|---|---|---|
| **Licensing / rights** | No license declared anywhere in `ReverseDictionary/`; ~30 sources of mixed status (§3.1) | [FAIR R1.1](https://www.go-fair.org/fair-principles/): clear, machine-readable license; ARR checklist §B: per-artifact license documentation | **`@DECIDE` — human ruling required** (§3.1). Blocks open data release only, not the paper. |
| **Canonical version** | Three drafts (250,026 / 255,882 / 266,820) with no written note on why the list grew; older `.doc` drafts not marked superseded | Versioned releases with changelog (org pattern: [`/cut-release`](https://github.com/gasyoun/github-spine/blob/main/CLAUDE.md), [kosha manifest](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json)) | Declare 266,820 canonical in a dated changelog entry; mark 250k/255k drafts superseded. Agent-doable now. |
| **Format & schema** | Flat TSV, single-letter source codes (A–Z, Ā, Ö, Ś, Ü, ß) resolvable only via [`Словари-источники.mdx`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/%D0%A1%D0%BB%D0%BE%D0%B2%D0%B0%D1%80%D0%B8-%D0%B8%D1%81%D1%82%D0%BE%D1%87%D0%BD%D0%B8%D0%BA%D0%B8.mdx) (Russian) | [TEI Lex-0](https://lex-0.org/) (v0.9.5, DARIAH-maintained) is the DH lexicographic standard — **but it is designed for full entries** (form/sense/gramGrp). For a bare headword+source list, a **documented TSV/JSONL schema** is honest and sufficient; TEI Lex-0 `<entry>/<form>` wrapping is a later, optional interoperability layer toward the Cologne TEI ecosystem | Write a `SCHEMA.md` (column semantics, source-code→bibliography key table mapping the letter codes to the CDSL-style codes `apt/mwe/pwk/...` already present in the bibliography); do **not** force a TEI conversion before there's a consumer for it. Agent-doable now. |
| **Encoding** | UTF-8 **with BOM** (verified); IAST; NFC/NFD consistency across the 30 merged sources unaudited | Declared normalization form; org's own [IAST pitfalls finding](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md) shows why this matters (vowel-length/retroflex loss under naive normalization) | One-pass audit: BOM policy (repo rule: preserve existing state, never silently change), NFC check, duplicate-under-normalization check. Agent-doable now. |
| **Metadata & citation** | No `CITATION.cff`, no DOI, no datasheet; not yet in [`FEATURES_INDEX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md) or the [kosha manifest](https://github.com/gasyoun/kosha/blob/main/data/manifest/datasets.json) | [CITATION.cff v1.2.0](https://citation-file-format.github.io/); a **data statement** per [Bender & Friedman 2018](https://aclanthology.org/Q18-1041/), current [schema v3 (2024)](https://techpolicylab.uw.edu/data-statements/) (17 elements incl. Distribution/Maintenance); alternatively/additionally [Datasheets for Datasets](https://dl.acm.org/doi/10.1145/3458723); DOI via Zenodo once (if) released | Draft the data statement + CITATION.cff now (they document restrictions honestly even for a restricted dataset); DOI + FEATURES_INDEX/kosha registration follow the licensing ruling — kosha's `tier: restricted` exists precisely for the interim. |
| **Reproducibility** | Sort algorithm ([`reverse15.php`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/reverse15.php)) and editorial rulebook ([`Состав и строй словаря.mdx`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/%D0%A1%D0%BE%D1%81%D1%82%D0%B0%D0%B2%20%D0%B8%20%D1%81%D1%82%D1%80%D0%BE%D0%B9%20%D1%81%D0%BB%D0%BE%D0%B2%D0%B0%D1%80%D1%8F.mdx)) exist; the **merge itself** (30 sources → one list, ~20,000 inflected forms manually removed, case-by-case sandhi rulings) is not reproducible by an outsider — most sources can't be redistributed and many rulings were editorial, not algorithmic | Full pipeline reproducibility is the NLP-venue ideal, but ACL's checklist accepts documented *provenance* where re-derivation is impossible (standard for legacy/manual resources) | Document the merge provenance (which source snapshot, which era of Cologne digitization, what was manual) rather than pretending to scriptability. The unapplied errata ([`Опечатки которые не успели.mdx`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/%D0%9E%D0%BF%D0%B5%D1%87%D0%B0%D1%82%D0%BA%D0%B8%20%D0%BA%D0%BE%D1%82%D0%BE%D1%80%D1%8B%D0%B5%20%D0%BD%D0%B5%20%D1%83%D1%81%D0%BF%D0%B5%D0%BB%D0%B8.mdx)) should be applied *before* any versioned release, so v1.0 isn't born with known errors. |

### 3.1 Licensing — the `@DECIDE`, with the facts assembled

**The question a human must rule on:** may the merged headword list (words + single-letter
source attributions, **no definitions**) be published openly, given that ~a third of its 30
sources are still in copyright somewhere?

Two honest readings exist:

- **Permissive reading:** individual headwords are facts; copyright protects expression
  (definitions, glosses, arrangement), and the reverse dictionary copies none of a source's
  expression — only which words exist. Under US doctrine (*Feist*), word lists have at most
  thin selection/arrangement protection, and this compilation's selection and arrangement are
  the compiler's own. Stiehl's 2004 reverse list (from Cologne's MW) and Cologne's own headword
  indexes circulate publicly on exactly this logic.
- **Cautious reading:** a dictionary's *headword selection* is itself curatorial work; EU
  database sui-generis rights and the substantial-extraction doctrine could reach a wholesale
  extraction of every headword from an in-copyright dictionary (Kochergina 1978, Turner
  1962–85, Mylius 1975, Pujol 2005 are the clearest cases). Jurisdiction matters: RF (author's
  life + 70), India (life + 60), EU (life + 70 + database right), US (*Feist* + publication-era
  rules).

Per-source status (dates from
[`Словари-источники.mdx`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/%D0%A1%D0%BB%D0%BE%D0%B2%D0%B0%D1%80%D0%B8-%D0%B8%D1%81%D1%82%D0%BE%D1%87%D0%BD%D0%B8%D0%BA%D0%B8.mdx);
death-year-based assessments are stated as reasoning, not legal advice):

| Status | Sources |
|---|---|
| **Public domain — safe** (18) | Wilson 1832 · Yates 1846 · Goldstücker 1856 · Burnouf 1866 · Bopp *Glossarium* · PWG 1855–1875 · PWK 1879–1889 · Cappeller 1887 · MW 1899 · Grassmann · Sørensen *Index* 1904–1914 · Shabda-Sagara · Śabdakalpadruma (orig. 1828–1858; the 1967 Chowkhamba printing is a reprint) · Vāchaspatyam (orig. 1873–1884; 1969–70 reprint) · Aufrecht *Catalogus* (orig. 1891–1903; 1962 reprint) · Macdonell 1929 (d. 1930) · *Vedic Index* 1912 (Keith d. 1944) · Schmidt *Nachträge* 1928 (d. 1939) |
| **Likely PD, verify** (2) | *Purana Index* 1951–55 (Dīkshitar d. 1953 → India life+60 expired 2014) · Apte 1957–59 revised ed. (the 1890 Apte base is PD; the Prasad Prakashan **revision** is the question — widely digitized/redistributed incl. by Cologne, but formal status murky) |
| **In copyright — clear risk** (7) | Edgerton *BHS Dictionary* 1953 (d. 1963) · Stchoupak–Nitti–Renou 1932 (Renou d. 1966 → France ~2036) · Turner *CDIAL* 1962–66 + suppl. to 1985 (d. 1983 → UK ~2053) · Mylius 1975 (d. 2023) · Kochergina 1978 (d. 2018 → RF ~2088) · Vettam Mani *Purāṇic Encyclopaedia* 1979 (Eng.) · Pujol *Diccionari sànscrit-català* 2005 (living author) |
| **Own license / special** (1) | Huet *Héritage du sanscrit* 1996– (living; the Sanskrit Heritage lexicon is distributed under its own open license — check current terms; likely the *easiest* in-copyright source to clear properly) |
| **Unclear edition/status** (2) | *Sanskrit Names of Plants* · *Mahabharata Cultural Index* |

**Decision options to rule between** (any of these unblocks the data tier):

- **(a) Publish the full list openly**, on the permissive facts-not-expression reading, with the
  per-source table above as the documented risk assessment.
- **(b) Publish a PD-only subset** (drop or mask the ~10 risky sources' *unique* contributions —
  words attested only there; words also in a PD source stay). Requires a one-off count of how
  many of the 266,820 words are unique to risky sources — likely small, since PWK is the
  default source, but unmeasured.
- **(c) Keep the data restricted-tier** (kosha `tier: restricted` pattern) and publish only the
  paper + statistics. Zero legal risk, weakest FAIR score.

→ Mirrored to
[`Uprava/GTD_NEXT_ACTIONS.md`](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md)
as an `@DECIDE`. Nothing in this report pre-empts the ruling.

---

## 4. Recommendation — sequenced next steps

**Agent-doable now (no human ruling needed):**

1. **Declare the canonical list** — dated changelog entry establishing
   `266820-reverse-Gasuns.txt` as canonical; mark the 250,026/255,882 drafts superseded
   (README already calls for exactly this).
2. **Apply the outstanding errata** from
   [`Опечатки которые не успели.mdx`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/%D0%9E%D0%BF%D0%B5%D1%87%D0%B0%D1%82%D0%BA%D0%B8%20%D0%BA%D0%BE%D1%82%D0%BE%D1%80%D1%8B%D0%B5%20%D0%BD%D0%B5%20%D1%83%D1%81%D0%BF%D0%B5%D0%BB%D0%B8.mdx)
   so the declared version isn't born with known errors.
3. **Write `SCHEMA.md`** — TSV column semantics + the letter-code→bibliography-key table;
   run the encoding audit (BOM policy, NFC consistency, duplicates-under-normalization).
4. **Draft the data statement** (Bender & Friedman
   [schema v3](https://techpolicylab.uw.edu/data-statements/)) **+ `CITATION.cff`** — both are
   honest about restrictions even while the data stays private, and §2's Responsible-NLP
   checklist needs their content anyway.
5. **Measure option (b)'s cost** — count headwords unique to in-copyright sources, so the
   licensing ruling is made with numbers, not guesses.

**Human ruling (`@DECIDE`):**

6. **License/publication ruling** on §3.1 options (a)/(b)/(c) — the only step that gates the
   open-data tier, the DOI, and a JOHD-style data paper.

**After the ruling:**

7. Register the dataset (kosha manifest row at the ruled tier +
   [`FEATURES_INDEX.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FEATURES_INDEX.md));
   if open: `/data-release` (Zenodo DOI, provenance README, versioned release).
8. **Scaffold the paper** via `/paper-scaffold` (stable Axx ID in
   [`Uprava/ARTICLES.md`](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md)) targeting
   **LaTeCH-CLfL 2027** (nearest deadline, ~Dec 2026–Jan 2027, watch
   [sighum.wordpress.com](https://sighum.wordpress.com/)) with **WSC 2027** (Dec 2027, IIT
   Bombay) as the flagship target; final venue pick via `/decision-record` when the CFPs are out.

---

## 5. Option (b)'s cost — measured 07-07-2026 ([H270](https://github.com/gasyoun/Uprava/blob/main/handoffs/H270-Sonnet_SanskritLexicography_reverse-dict-publication-prep_07.07.26.md))

**Method used, and why the originally-named source changed.** The plan was to cross
`187992 headwords.txt` (described as "multi-source attestation tags") against the
master list. On inspection, that file is **not** a per-word attestation dataset — it is
a 30-line category-count *legend* (e.g. "74009 headwords coded as cpd1: simple compound
of 2 parts...") with only 3 illustrative example lines, not the full tagged list its
name implies. It cannot answer "which headwords are attested only in in-copyright
sources." Recorded here rather than silently substituted, per this handoff's standing
rule to investigate rather than guess.

**What was used instead:** the master list's own single-letter source-code column
(documented in [`SCHEMA.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/ReverseDictionary/SCHEMA.md)).
Since PWK (public domain) is the implicit default and every other source is marked
*only when the word is not already coverable from PWK or a higher-priority source*, a
headword's marked code is a genuine (if imperfect — see caveat below) proxy for "this
word's presence in the merged list depends on this specific source."

**Result.** Of the 12 source codes actually used in the 266,820-line file, exactly two
belong to the `ACL_DH_COMPATIBILITY_ANALYSIS.md` §3.1 "in copyright — clear risk" tier:

| Code | Source | Headwords |
|---|---|--:|
| `H` | Edgerton, *Buddhist Hybrid Sanskrit Dictionary* (1953) | 12,552 |
| `P` | Vettam Mani, *Puranic Encyclopaedia* (1979) | 1,919 |
| **Total** | | **14,471** |

**14,471 / 266,820 = 5.4%** of the full list is tagged to a genuinely in-copyright
source under this reading — i.e. option (b) (drop/mask risky-source-unique headwords)
would cost roughly **1 in 18 headwords**, concentrated almost entirely in two sources.

**Important caveat, stated honestly:** the other five "clear risk" sources named in
§3.1 — Stchoupak–Nitti–Renou, Turner *CDIAL*, Mylius, Kochergina, Pujol — **never
appear as a marked source-code in the file at all** (see `SCHEMA.md`'s note on the 18
declared-but-unused codes). This does not prove they contributed zero headwords; it
means the single-letter-per-line scheme cannot isolate their *unique* contribution from
whatever higher-priority source a shared headword got tagged under instead. **14,471 is
therefore a lower bound**, not a final figure — the true cost of option (b) could be
higher if, e.g., a Kochergina-only headword happens to coincide in form with a PWK
headword and was silently absorbed as unmarked. Establishing a tighter bound would need
per-source headword lists for the five silent sources (not available in this folder) to
diff against the canonical list — out of scope for this pass.

→ This count (14,471 confirmed + caveat) is mirrored to the `@DECIDE` row in
[`Uprava/GTD_NEXT_ACTIONS.md`](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md)
so the licensing ruling can weigh it — the ruling itself remains unresolved by this pass.

_Dr. Mārcis Gasūns_
