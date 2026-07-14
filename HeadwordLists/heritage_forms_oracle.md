# Heritage ↔ kosha inflected-forms oracle

_Created: 03-07-2026 · Last updated: 03-07-2026_

A **third independent witness** for Sanskrit inflected-form data, diffed against
kosha's existing DCS + vidyut forms layer. This is a **comparison / oracle** — it
never merges or overwrites either side. Phase 4 of
[HERITAGE_INRIA_ROADMAP.md](https://github.com/gasyoun/SanskritLexicography/blob/master/HERITAGE_INRIA_ROADMAP.md);
handoff [H105](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H105-Opus_SanskritLexicography_heritage_phase4_morphology_forms_03.07.26.md).

## The two witnesses

| | Heritage (this study) | kosha baseline |
|---|---|---|
| Source | [Sanskrit Heritage](https://sanskrit.inria.fr/) morphology databank `SL_morph.xml`, dict **v3.81** (2026-06-21) | [kosha](https://github.com/gasyoun/kosha) `data/db/kosha.db` → `forms` |
| Method | Gérard Huet's **rule-based declension/conjugation engine** (generates the full paradigm of each lexicon stem) | **DCS corpus-attested** + **vidyut-generated**, imported from [SanskritRussian](https://github.com/gasyoun/SanskritRussian)'s `dcs_form2lemma.tsv` + `vidyut_form2lemma.tsv` |
| Size | **1,286,615** `<f>` entries → **1,022,526** distinct SLP1 forms / 32,837 stems | **426,410** form→lemma pairs → **409,978** distinct SLP1 forms |
| Lemma key | stem with `#N` homonym index (`aMSaka#2`) — same convention as [mw_heritage_crosswalk.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/mw_heritage_crosswalk.tsv) | bare lemma, no `#N` |

**Join:** on the SLP1 form string (both sides are already SLP1). Heritage's `#N`
is stripped before lemma-set comparison. A form is scored **agree** if the two
sides share ≥1 lemma, **disagree** if their lemma sets are disjoint.

## Headline numbers

| Metric | Value |
|---|---|
| Forms in **both** (raw string join) | **94,264** |
| — agree (share ≥1 lemma) | **73,768 · 78.3%** |
| — disagree (disjoint lemma sets) | **20,496 · 21.7%** |
| Forms **only in Heritage** | **928,262** |
| Forms **only in kosha** | **315,714** |
| Heritage covers of kosha's forms | 23.0% (raw) → **25.4%** nasal-normalised |
| kosha covers of Heritage's forms | 9.2% |

The raw overlap looks small — but most of the gap is **model difference and
transcription convention, not a real coverage gap.** That is the main result.

## Why the overlap is only ~94k — and why that is expected

- **Heritage generates the whole paradigm; DCS records what a corpus attests.**
  Heritage's engine emits every declined/conjugated form of each stem, including
  ~half a million compound-initial (`iic`/`iiv`) forms a corpus never lists as
  standalone tokens. So **928,262 Heritage-only forms** is engine richness, not
  DCS error — it is exactly the "third witness" surplus worth harvesting.
- **The anusvara / homorganic-nasal convention split.** DCS writes word-final and
  pre-consonant nasalisation as anusvara `M` (`AvAsaM`, `oMkAra`, `BayaMkara`);
  Heritage writes the phonetic nasal (`AvAsam`, `oNkAra`, `BayaNkara`).
  **18,636** of the 315,714 kosha-only forms (5.9%) recover a Heritage match once
  this is normalised — a pure transcription artifact, not a missing form.
- **DCS sandhi-context avagraha artifacts.** **8,264** kosha-only forms carry a
  leading avagraha `'` (e.g. `''jYAya` for elided initial ā) — corpus-context
  forms that by construction never appear in a citation-form declension table.
- **Heritage's declared scope gaps.** Precative/benedictive, subjunctive,
  injunctive and conditional are out of Heritage's scope, so those DCS/vidyut
  verb forms are systematically kosha-only by design.

## Anatomy of the 20,496 disagreements

Disjoint lemma sets do **not** mean "one side is wrong" — they are dominated by a
documented **lemmatization-policy** difference:

| Split | Count | What it is |
|---|---|---|
| **Verbal-derived** (Heritage tags participle / finite-verb / verbal-indecl) | **13,530 · 66.0%** | Heritage lemmatizes a participle to its **participle-stem** (`garhita`, `kfRvat`) and a finite verb to its **root** (`kf`, `sic`); DCS/vidyut give the **root** for the participle and the **causative/denominative stem** (`kampay`, `secay`) for the verb. Both are internally consistent — a policy difference, not a contradiction. |
| **Nominal / indeclinable only** | **6,966 · 34.0%** | The genuine-divergence pool: real both-valid ambiguities plus the (minority) one-sided errors. |

Auto-classification of the disagreements (heuristic — see caveat below):

| Class | Count | Meaning |
|---|---|---|
| `genuine-or-ambiguous` | 12,905 | residue — **upper bound** (see below) |
| `stem-granularity` | 7,132 | one lemma is a literal prefix of the other (`Sabda`⊂`Sabdayat`) |
| `nasal-variant` | 459 | lemma strings differ only by anusvara/nasal (`saNgrAma`/`saMgrAma`) |

**Caveat:** the `genuine-or-ambiguous` bucket is a large **over**count. The
prefix test cannot see root↔stem pairs that are suppletive (`vah`→`UQa`,
`aYj`→`akta`), guṇa/vṛddhi-obscured (`kf`→`kAray`, `sic`→`secay`), or where the
root is < 3 characters (`Df`⊂`Dfta`, `kf`⊂`kfRvat`). Hand-verification (below)
shows roughly half of the sampled `genuine-or-ambiguous` rows are in fact
lemmatization-granularity.

## Hand-verification — 40 rows adjudicated

Sampled across all three classes (6 nasal-variant, 8 stem-granularity, 26
genuine-or-ambiguous) and adjudicated by morphology against both sources:

| Form (SLP1) | Heritage stem(s) | kosha lemma(s) | Verdict |
|---|---|---|---|
| `saNgrAmeRa` | saNgrAma | saMgrAma | **convention** — saṅgrāma, ṅ vs anusvara |
| `kiYcid` | kiYcid | kiMcid | **convention** — kiñcid |
| `arindamAn` | arindama | ariMdama | **convention** — arindama |
| `puraYjanasya` | puraYjana | puraMjana | **convention** — Purañjana |
| `sanDIn` | sanDi | saMDi | **convention** — sandhi |
| `BUmiYjaya` | BUmiYjaya | BUmiMjaya | **convention** — bhūmiñjaya |
| `glAnasya` | glAna (ppp) | glA (root) | **policy** — participle-stem vs root |
| `kampayatu` | kamp (root) | kampay (caus) | **policy** — root vs causative-stem |
| `sevanIyena` | sevanIya (gerundive) | sev (root) | **policy** — gerundive vs root |
| `mantrya` | mantr (root) | mantray (denom) | **policy** — root vs denominative |
| `Sabdayati` | Sabda \| Sabdayat | Sabday | **policy** — noun/ppr vs denom-stem |
| `buButsate` | buButsat \| buD | buButsa | **policy** — desiderative ppr/root vs stem |
| `UQam` | UQa (ppp) | vah (root) | **policy** — suppletive ūḍha ↔ vah |
| `aktena` | akta (ppp) | aYj (root) | **policy** — suppletive akta ↔ añj |
| `kfRvantam` | kfRvat (ppr) | kf (root) | **policy** — root < 3 chars, missed by prefix test |
| `DftAt` | Dfta (ppp) | Df (root) | **policy** — root < 3 chars |
| `kArayasva` | kf (root) | kAray (caus) | **policy** — guṇa-obscured root↔caus |
| `secayet` | sic (root) | secay (caus) | **policy** — guṇa-obscured |
| `tyaktO` | tyakta (ppp) | tyaj (root) | **policy** — suppletive |
| `pAryante` | pF \| pf | pAray (caus) | **policy** — root vs causative |
| `ABAByAm` | ABA (fem ā) | ABa (a-stem) | **ambiguous** — ābhābhyām from ābhā *or* ābha, both valid |
| `pawI` | pawa (m.) | pawI (f.) | **ambiguous** — paṭa's fem *or* paṭī, both valid |
| `nAgarI` | nAgara (adj) | nAgarI (f. noun) | **ambiguous** — both valid |
| `vfdDikA` | vfdDaka (m.) | vfdDikA (f.) | **ambiguous** — both valid |
| `vESvadevezu` | vESvadeva | **AparAhRika** | **divergence — DCS wrong**: vaiśvadeveṣu mis-lemmatized to *aparāhṇika* |
| `jAnAt` | jAna (noun) | jYA (root) | **divergence** — jānāt is abl. of *jāna*; DCS's jñā is a stretch |
| `sAyakAs` | sAyaka (arrow) | sAyi | **divergence** — vidyut lemma `sAyi` unmotivated |
| `pulomAyAm` | puloman (m.) | pulomA (f.) | **divergence — Heritage odd**: loc. is fem *Pulomā*, kosha right |
| `gozWIm` | gozWa (m./n.) | gozWI (f.) | **divergence — Heritage odd**: acc. fem is *goṣṭhī*, kosha right |
| `ABAsate` | ABAsatA | ABAs (root) | **divergence — Heritage odd**: 3sg. ātm. of root ā-bhās; kosha right |

**Tally of the 40:** 6 pure convention · ~20 lemmatization-policy (both defensible)
· 4 both-valid ambiguity · ~10 genuine one-sided divergences. The genuine
divergences occur on **both sides** — DCS corpus mis-tags (`vaiśvadeveṣu` →
`aparāhṇika`) and Heritage stem-choice oddities (`goṣṭhīm` → `goṣṭha`).

## What this means

- **Real agreement is far above the raw 78.3%.** Fold in the 66% verbal
  lemmatization-policy rows and the nasal convention and the two engines *contradict*
  each other on only a low-single-digit percentage of the shared forms.
- **Genuine one-sided divergences are on the order of a few thousand** (they
  concentrate in the 6,966 nominal-only disagreements; hand-sampling suggests
  roughly half of those are both-valid ambiguities rather than errors). This is a
  **tractable, high-value review pool** — most valuable where a DCS corpus tag is
  demonstrably wrong.
- **928k Heritage-only forms** are a candidate third-witness expansion for
  [kosha](https://github.com/gasyoun/kosha) and
  [SanskritSpellCheck](https://github.com/sanskrit-lexicon/SanskritSpellCheck) —
  **but not merged here** (see the GTD `@DECIDE`).

## Outputs (this directory)

| File | Contents |
|---|---|
| [heritage_forms_oracle.tsv.gz](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_forms_oracle.tsv.gz) | full 94,264-row intersection: `form · flag · heritage_stems · kosha_lemmas · heritage_category · kosha_sources · disagreement_class` |
| [heritage_forms_oracle_disagreements.tsv](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_forms_oracle_disagreements.tsv) | the 20,496 disagreement rows only (browsable) |
| [heritage_forms_oracle_stats.json](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_forms_oracle_stats.json) | machine-readable summary |
| [heritage_forms_oracle.py](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/heritage_forms_oracle.py) | reproducible parser + differ |

**Reproduce:** `python HeadwordLists/heritage_forms_oracle.py` (needs the
gitignored `heritage_mirror/manual/SL_morph.xml.gz` and a sibling `kosha`
checkout with `data/db/kosha.db` built). The **nominal-only disagreement review
pool** (6,966 rows) is `awk -F'\t' 'NR>1 && $5!~/verb/ && $5!~/participle/'
heritage_forms_oracle_disagreements.tsv`.

## Provenance & licence

Heritage morphology © Gérard Huet 1994–2026, **LGPLLR**; composition with kosha's
CC BY-SA data approved by Huet **03-07-2026** (see
[HERITAGE_INRIA_ROADMAP.md §2](https://github.com/gasyoun/SanskritLexicography/blob/master/HERITAGE_INRIA_ROADMAP.md)
and
[H121-Opus_SanskritLexicography_OUTREACH_2026-07-03_gerard_huet_heritage_03.07.26.md](https://github.com/gasyoun/Uprava/blob/main/handoffs/H121-Opus_SanskritLexicography_OUTREACH_2026-07-03_gerard_huet_heritage_03.07.26.md)).
The raw decompressed XML stays local / gitignored; only this derived diff is
committed. Cite Huet + LGPLLR in any downstream reuse.

_Dr. Mārcis Gasūns_
