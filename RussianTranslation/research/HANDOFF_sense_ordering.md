# Handoff research — sense ordering across the core dictionaries (2026-06-23)

**Question.** In what order does each core Sanskrit dictionary arrange the senses
*within* an entry — **historical** (oldest/Vedic attestation first → later), **logical /
semantic** (grouped by meaning, common-first, pedagogical), **etymological** (derivation
order), or **frequency** (none known to exist in print)? This decides how `pwg_ru`
orders each card's senses — and we already carry the **Renou I–V** tag + `renou_oldest`
per sense, so *historical* ordering is essentially free if that's the target.

**Why it matters.** The sense order is an editorial stance, not a mechanical fact. A
printed Russian PWG should order senses the way scholarly users expect; if the source
dictionaries disagree, `pwg_ru` must choose deliberately and state it.

## Working hypothesis (user, to verify)
- **The 19th-c. European dictionaries are HISTORICAL.** PWG, PW, MW, GRA arrange senses
  by period of attestation (Vedic → Brāhmaṇa → epic → classical), the comparative-
  philology paradigm of their era. *Likely true — verify in each preface.*
- **No printed FREQUENCY dictionary of Sanskrit exists yet** (so frequency-order is a
  `pwg_ru` innovation if we want it — and DCS now makes it possible).
- **AP (Apte) is NON-historical** — but is its order best described as *logical/semantic
  grouping* (common/practical senses first, grouped by meaning, student-facing)?
  **Open — continue research.**

## Sources (read the PREFACES first — most are OCRed)
| Dict | Preface (OCR) — read for the explicit ordering statement | Entry file (verify against real entries) |
|---|---|---|
| PWG | [`PWG/prefaces/pwgpref_all.de.md`](https://github.com/sanskrit-lexicon/PWG/blob/master/prefaces/pwgpref_all.de.md) | `csl-orig/v02/pwg/pwg.txt` |
| PW | [`PWK/prefaces/pwpref_all.de.md`](https://github.com/sanskrit-lexicon/PWK/blob/master/prefaces/pwpref_all.de.md) | `csl-orig/v02/pw/pw.txt` |
| MW | [`MWS/prefaces/mwpref_all.en.md`](https://github.com/sanskrit-lexicon/MWS/blob/master/prefaces/mwpref_all.en.md) | `csl-orig/v02/mw/mw.txt` |
| GRA | [`GRA/prefaces/grapref_all.en.md`](https://github.com/sanskrit-lexicon/GRA/blob/master/prefaces/grapref_all.en.md) (also `.de`, `.ru`) | `csl-orig/v02/gra/gra.txt` |
| AP90 | *(no OCR preface — read the Apte 1890 print front-matter / "Scheme of the work")* | `csl-orig/v02/ap90/ap90.txt` |
| SCH | [`SCH/prefaces/schpref_all.de.md`](https://github.com/sanskrit-lexicon/SCH/blob/master/prefaces/schpref_all.de.md) | `csl-orig/v02/sch/sch.txt` |

**Method.** (1) In each preface, find the passage on *Anordnung der Bedeutungen* /
"arrangement of meanings" / "scheme of the work"; quote it. (2) Cross-check against a
shared polysemous probe word translated across all of them — e.g. `artha` (अर्थ: aim →
wealth → meaning → lawsuit) or `dharma` — does sense 1 in each correspond to the oldest
attested meaning, the commonest, or the etymological core? (3) Classify each dict +
quote the evidence.

**Output:** a table `dict × {historical / logical-semantic / etymological} × evidence
quote`, plus a recommendation for `pwg_ru`'s sense order (likely **historical via the
Renou tag**, since we already compute `renou_oldest` per sense — but confirm it matches
PWG's own order so we don't fight the source).

**Note for executor.** Distinguish *macro*structure (headword order = alphabetical for
all) from *micro*structure (sense order within an entry) — this handoff is only the
latter. Watch for dictionaries that mix axes (e.g. etymological *grouping* of homonyms
but historical order *within* a homonym).

---

## RESULTS (executed 2026-06-24)

**Headline.** The hypothesis is **broadly confirmed, with one important refinement**:
the four 19th-c. European dictionaries (PWG, PW, MW, GRA) are **NOT historical in the
strict "oldest-sense-first" sense** the brief proposed. They are **etymological-genetic**:
the *lead* sense is the reconstructed **Grundbedeutung** (root core), and the *historical*
axis governs (a) the **chronological ordering of citations *within* each sense** (Veda →
Brāhmaṇa/Sūtra → epic → classical) and (b) explicit **attestation/gender notes**. Apte
(AP90) is **logical-semantic / pedagogical** — it leads with the practically salient gloss
for an English-medium student, relegates etymology to a head-bracket, and carries **no
historical citation apparatus**. So the two camps mix axes exactly as the brief warned:
*genetic sense-heads + chronological citation-threading* (European) vs. *salience-ranked
sense-heads, no chronology* (Apte).

No printed **frequency** dictionary of Sanskrit was found or implied by any preface — the
frequency axis remains a `pwg_ru` innovation (DCS-powered), as hypothesised.

### Preface evidence (microstructure statements)

| Dict | Preface says about *sense* order | Verbatim |
|---|---|---|
| **PWG** | **Silent** on an explicit sense-sequencing rule, but states a *genetic method of meaning-recovery* anchored in the oldest (Vedic) layer. | "…wo im spätern Sprachgebrauch die **Grundanschauung** eines Wortes verwischt … ist, da darf man zurückgreifen in den Schatz des Veda um noch … die Angabe des **ursprünglichen Werthes** zu finden." ([pwgpref_all.de.md L106](https://github.com/sanskrit-lexicon/PWG/blob/master/prefaces/pwgpref_all.de.md)) — *recover the original value from the Veda*. The lone "Anordnung" (L191) refers to arranging the whole *material*, not senses. |
| **PW** (kürzere Fassung) | **Silent.** Defers wholesale to the big PWG ("die Hauptquelle"); the only sense-level remark is about citation placement. | "Ein früher angeführtes Citat wird man … nur dann wiederholt finden, wenn es **zu einer anderen Bedeutung des Wortes gestellt** … worden ist." ([pwpref_all.de.md L60](https://github.com/sanskrit-lexicon/PWK/blob/master/prefaces/pwpref_all.de.md)) |
| **MW** | **Silent on sense sequence**; preface is exhaustive on the *macrostructure* (etymological root-nesting). Only sense-level rule is punctuation (comma = amplification, semicolon = distinct shade → grouping by affinity). | "…the ruling aim of the whole arrangement is to exhibit … the **evolution of words from roots** …" ([mwpref_all.en.md L355](https://github.com/sanskrit-lexicon/MWS/blob/master/prefaces/mwpref_all.en.md)); "mere amplifications of preceding meanings are separated by a comma, whereas those which do not clearly run into each other are divided by semicolons." (L378) |
| **GRA** | **EXPLICIT — the only preface that states the rule.** Senses derived from a reconstructable **basic meaning**, then numbered for usefulness. | "I have **derived the meaning … from reconstructable basic meaning**, but then simply by consecutive numbers … put in **sequence** … so that it becomes apparent which meaning … I attribute to the word in each referenced passage." ([grapref_all.en.md L74–85](https://github.com/sanskrit-lexicon/GRA/blob/master/prefaces/grapref_all.en.md)) |
| **SCH** | **Silent / N/A.** A *Nachträge* (supplement) of new words & citations keyed to PWK; entries are mostly single-sense additions. Inherits the PWK convention. | (no statement; cf. [schpref_all.de.md](https://github.com/sanskrit-lexicon/SCH/blob/master/prefaces/schpref_all.de.md)) |
| **AP90** | No OCR preface in-repo. Inferred from entries (below). Apte's known "Scheme of the Work" is practical/student-facing; entries bear it out. | — |

### Probe-word evidence (microstructure, from the entry files)

**`artha` (अर्थ, SLP1 `arTa`)** — first senses, in source order:

| Dict | Sense 1 | Sense 2 | Sense 3 | …where "wealth" / "meaning" land | Citation order in sense 1 |
|---|---|---|---|---|---|
| **PWG** | *Ziel, Zweck* (goal/aim) | *Grund, Veranlassung* (cause) | *Vortheil, Nutzen* (advantage) | wealth = **#5**, meaning = **#8** | **ṚV → VS → Kāty.Śr. → Manu → classical** (chronological) |
| **PW** | *Geschäft, Arbeit* (work — the RV idiom *arTam i/gam*) | *Ziel, Zweck* (goal) | *Grund* (cause) | wealth = **#7**, meaning = **#15** | leads with the Vedic *arTam i/gam* idiom |
| **MW** | *aim, purpose* | *advantage, use, utility* | *thing, object* (ŚBr. xiv) | wealth = **#5**, meaning = **#8 (last)** | **explicit gender history**: "in RV i-ix only n.; in RV x … n. and m.; in later Sanskṛt only m." |
| **GRA** | *Ziel* (goal) | *Geschäft, Arbeit* (work) | *(idiom)* an die Arbeit gehen | (Rig-Veda only; wealth/meaning n/a) | states inline: *"Grundbegriff ist „das Erstrebte" (von ar „streben"). **Daher** 1〉 Ziel; 2〉 …"* |
| **AP90** | *Object, purpose, end and aim* | *Cause, motive, reason* | **Meaning, sense, signification** | wealth = **#6**, **meaning = #3 (elevated)** | classical only (Mu./Dk./Ku./R./Bg.); **no Vedic, non-chronological** |

**`dharma` (धर्म, SLP1 `Darma`)** — the discriminator is sharper here:

| Dict | Sense 1 | Tell-tale |
|---|---|---|
| **PWG** | *Satzung, Ordnung* (statute, order) → a) Sitte, Recht, Pflicht; b) Gesetz, Brauch | etymological core *√dhṛ "hold firm" → that which is fixed* first; *Religion/virtue* folded into sub-senses |
| **PW** | *Satzung, Ordnung, Gesetz, Brauch, Sitte…* | identical core-first lead |
| **MW** | *"that which is established or firm, steadfast decree, statute, ordinance, law"* | **explicit historical note**: "(the **older form of the RV is `Darman`**, q.v.)" — derives from the Vedic *-man* stem |
| **AP90** | **Religion** → 2) Law/ordinance/statute → 3) virtue → … → 8) Nature → 9) essential quality | leads with the **pedagogically salient gloss**; the etymon *Driyate loko'nena … Df-man* sits in a head-bracket but does **not** drive the order; the philosophical core ("essential property") is demoted to #8–9 |

**Reading.** PWG/PW/MW lead with the **root core** and thread citations **oldest-first**;
MW even date-stamps the gender shift (RV i-ix → RV x → later) and flags the older Vedic
stem *dharman*. Apte leads with the gloss a learner needs first ("Religion"; "Meaning"
promoted to artha #3), gives the etymology as an aside, and shows **no chronological
discipline** in its citations. `artha` sense-1 alone under-discriminates (its etymological
core *and* a common sense both = "aim/purpose"), so `dharma` and the **citation-ordering +
attestation-apparatus** are the decisive signals.

### Classification

| Dict | Sense-ordering principle (microstructure) | Confidence | Decisive evidence |
|---|---|---|---|
| **PWG** | **Etymological-genetic** (Grundbedeutung-first) + **chronological citation-threading** | High | `dharma` #1 = "fixed/established"; `artha` #1 = "goal"; ṚV-first citations; L106 *ursprünglicher Werth* |
| **PW** | Same as PWG (explicitly derivative) | High | `dharma`/`artha` lead with archaic core, not classical salience |
| **MW** | **Etymological-genetic**, historically annotated; macrostructure = etymological root-nesting | High | RV i-ix gender note; "older RV form `Darman`"; root-evolution preface |
| **GRA** | **Etymological-logical** — *stated*: basic concept → numbered derived senses (single Vedic corpus, so chronology is moot) | Very high (explicit) | preface L74–85 + inline *"Grundbegriff … Daher 1〉…"* |
| **SCH** | N/A (supplement; inherits PWK) | n/a | single-sense additions |
| **AP90** | **Logical-semantic / pedagogical** (salience-first, grouped) | High | `dharma` #1 = "Religion", core demoted; `artha` "meaning" promoted to #3; no Vedic/chronological apparatus |

> **Refinement of the brief's wording.** Call the European group **"etymological-genetic
> with historical citation-threading,"** not plain "historical." Strict *oldest-sense-first*
> would re-sort the tail differently from what Böhtlingk-Roth actually printed; their
> **lead** sense is the root core (which *happens* to be the oldest-attested, so the two
> axes coincide at sense 1 but can diverge lower down).

### Recommendation for `pwg_ru` sense order

1. **Preserve PWG's own `<div n>` sense order verbatim — do NOT re-sort by `renou_oldest`.**
   `pwg_ru` is a translation *of* PWG; PWG's order is already etymological-genetic and
   authoritative. A strict `renou_oldest` re-sort would reproduce sense 1 (root core =
   oldest) but **fight the source** in the middle and tail, discarding Böhtlingk-Roth's
   editorial judgement. Faithfulness to the source wins.
2. **Use the Renou I–V tag + `renou_oldest` as per-sense *display metadata*, not a sort
   key.** Render a small period badge on each sense (Vedic / Brāhmaṇa / epic / classical).
   This surfaces exactly the historical signal the user wants — *for free, since we already
   compute it* — while keeping the printed order = PWG's order. It matches what PWG/MW were
   already doing implicitly (RV-first citations, attestation notes), made explicit.
3. **Optional secondary view: "sort senses by oldest attestation."** A toggle powered by
   `renou_oldest` gives the strict-historical reading for users who want it, without
   mutating the canonical PWG order. This is also where a future **DCS frequency** sort
   (the unbuilt fourth axis) would slot in as an alternative lens.
4. **Do not import Apte's order.** AP90's pedagogical salience-ranking is a *different
   editorial stance* for a *different audience*; mixing it into a PWG translation would be
   incoherent. If a learner-facing layer is ever wanted (cf. the lexicography roadmap),
   build it as a separate, explicitly-labelled view.

**One-line answer:** PWG/PW/MW/GRA order senses **etymologically-genetically (root core
first) with Vedic-first citation chronology**; Apte orders them **by pedagogical salience**.
For `pwg_ru`, **keep PWG's printed sense order** and attach the Renou period tag as a
per-sense badge rather than re-sorting.
