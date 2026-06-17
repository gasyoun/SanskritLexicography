# The Petersburg dictionary chain — research + architecture for a complete pwg_ru

To make the Russian translation **as complete as possible**, it must draw on the
whole Böhtlingk-Roth → Böhtlingk → Schmidt → NWS supplement tradition, not PWG
alone. Each layer "goes one step further": a later dictionary corrects and adds to
the earlier ones.

## The layers

| # | Code | Dictionary | Dates | Role | Where |
|---|---|---|---|---|---|
| 1 | **PWG** | *Sanskrit-Wörterbuch* (Böhtlingk & **Roth**), "groß" | 1855–1875, 7 vols | **The foundation** — large, full citations, Vedic-deep | `csl-orig/v02/pwg` (1.13M lines) |
| 2 | **PW / PWK** | *Sanskrit-Wörterbuch in kürzerer Fassung* (**Böhtlingk** alone) | 1879–1889, 7 vols | **Revised condensation** of PWG — corrects it, trims citations, adds new material | `csl-orig/v02/pw` (643k lines); repo [PWK](https://github.com/sanskrit-lexicon/PWK) |
| 2a | **PWKVN** | PWK *variant / Nachträge* | — | Supplement to PWK; entries **keyed to PW sense numbers** (`8〉 Nenner eines Bruchs`) | `csl-orig/v02/pwkvn` |
| 3 | **SCH** | R. Schmidt, *Nachträge zum Sanskrit-Wörterbuch in kürzerer Fassung* | 1928 | **Pure addenda** to PW — words/citations not in PW | `csl-orig/v02/sch` (28,455 entries); repo [SCH](https://github.com/sanskrit-lexicon/SCH) |
| 4 | **NWS** | *[Nachtragswörterbuch des Sanskrit](https://nws.uzi.uni-halle.de/description?lang=en)* (Halle, DFG) | modern | **Cumulative addenda** — shows *only what is not in PW or Schmidt*; the furthest layer | **external** (Halle), not in Cologne repos |

**Within** each of PWG/PW, the volumes also carry their own Addenda/Nachträge
(handled by the pwg_ru Nachträge guard — see below).

### The two relationships (they are not all the same kind)
- **PWG ↔ PW are two *editions*** of the same dictionary (large vs revised-short).
  PW is *not* a pure overlay on PWG — it has its own, sometimes differing, entries.
- **SCH, NWS, PWKVN are *supplements*** — pure addenda keyed to the Petersburg
  tradition (NWS explicitly excludes what PW/Schmidt already have).

## NWS and the "old Cologne snapshot" — verified from the live site (2026-06-17)

Confirmed from [`nws.uzi.uni-halle.de`](https://nws.uzi.uni-halle.de/?lang=de) (German project page, authoritative):

- **What it is.** *Kumulatives Nachtragswörterbuch des Sanskrit* — a cumulative
  supplement built **on** ("aufbauend auf") the Petersburg *kürzere Fassung* (**pw**,
  Böhtlingk 1879–89) **+ Schmidt's Nachträge (1928)**. It records *only what those do
  not already have*.
- **When.** DFG project, **1 December 2013 – 31 December 2016**. Indology: Hanneder +
  Demoto-Hahn (Marburg), Slaje + Einicke + Siegfried + Wilke (Halle). Informatics:
  Molitor + Ritter + Heße (Halle). → The pw/Schmidt **base it rests on is a
  ~2013-era Cologne snapshot** (Th. Malten's digitization), *not* the late-1990s I had
  guessed.
- **How its entries are shaped — important for us.** NWS does **not** reproduce the
  evaluated glossary articles in full. Each is condensed to a *„Kleines Zitat"* —
  noting only **new** information on *lemma / meaning / grammar* plus a **literature
  reference**. So NWS gives us a **completeness index + pointers**, not bulk
  translatable prose. Architecturally NWS contributes: (a) **new lemmas** absent from
  pw/Schmidt, (b) **new senses/grammar flags** on existing lemmas, (c) **citations to
  follow up** — high value for *coverage* and *recency*, low volume for translation.

**Drift severity — measurable, not speculative.** The scraper captures, per headword,
the `pw` and `sch` fragments NWS itself returns. Diffing those against current
`csl-orig/v02/pw` + `/sch` quantifies how far the ~2013 snapshot has drifted from
today's Cologne text (PWK timeline since: bibliography crefs 2016, IAST 2018, verbs
2020, abbrev 2022–24, MBH/Rām link-splitting 2025). This diff runs once the a-section
has accumulated — no separate access request needed for the measurement.

**Access caveat.** NWS states no licence and is a small/slow server; the scrape is
rate-limited, identified, gitignored, and provisional. For the *full* dataset a formal
Halle data request remains the clean path (deferred per your call — scrape-only for now).

## Proposed architecture — layered per-headword aggregation

The goal is **one Russian entry per headword that is the union of all layers**, with
provenance per fact. For each SLP1 headword key:

```
base   = PWG entry          (the fullest treatment, our current pipeline)
        + PW entry          (revision/condensation — note where PW corrects PWG)
        + SCH addenda       (append: new senses/citations, keyed to PW)
        + NWS addenda       (append: cumulative supplement, keyed to PW/Schmidt)
        + PWKVN addenda     (append: keyed to PW sense numbers)
→ a merged Russian portrait, each fact tagged with its source dictionary + provenance
```

- **Translate once, reuse across layers** — SCH/NWS/PWKVN are short addenda; many
  share vocabulary already translated for PWG/PW (the corpus lexicon + a
  translation-memory of done glosses cut re-work).
- **Conflict handling** — where PW revises PWG (different gender, sense dropped),
  surface both with their dates ("PWG: n.; PW: m.") rather than silently picking one.
- **Same microstructure pipeline** — PW/SCH/PWKVN use the same `<L>/<hom>/<lex>/
  {%..%}/{#..#}/<ls>` markup as PWG, so `pwg_mask` + `microstructure` extend to them
  with small format tweaks (`<hom>` vs `<h>`; `〉` sense markers in PWKVN).

## Crowdsourcing the human review (your students)

The `review_status` state machine + severity-sorted worklist already exist; scale
them to many reviewers:

```
machine → flags ~15-25% of cards → review queue
        → router by difficulty + reviewer skill:
            easy/medium cards → student reviewers (Sanskrit students)
            hard / Vedic / conflicted cards → you (lead editor)
        → each card: approve / edit / reject, with reviewer_id + decision
        → double-key a stratified sample to 2+ reviewers → Cohen/Fleiss κ (reliability)
        → you adjudicate disagreements + final sign-off (human_reviewed → approved)
```

**Platform options** (a key decision — see questions): a custom lightweight web app;
**Lexonomy** (the free ELEXIS dictionary-editing platform, purpose-built for exactly
this); a GitHub-issues-per-card flow (free, auditable, students already on GitHub);
or a structured spreadsheet. All consume the same gitignored review-queue JSONL and
write back `reviewer_id`/`decision`/`edit`.

## Nachträge handling — status (implemented + verified)
**Implemented.** `pwg_mask` reads all records (incl. the 635 float-id Nachträge);
`_pilot_gen` labels each record MAIN vs NACHTRÄGE; the locked translate prompt
(guard 4) renders every addendum keyed to the main-entry sense it patches.
**Verified** on the a-section: `antarikṣa`/`anta`/`akṣara` (the addenda-coverage
failures) now pass. *Corrected based on:* B&R's own structure — each Nachträge
record back-references the main entry's sense numbers; we render the patch under
`[к знач. N]` and new senses as `[новое знач. N]`, preserving the corrigenda
("read X instead of Y") verbatim.

## Open questions
See this turn's message.
