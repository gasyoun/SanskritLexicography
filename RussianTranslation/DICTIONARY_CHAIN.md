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

## SCH preface — what Schmidt's own front matter gives us (2026-06-17)

Source: [`SCH/prefaces/schpref_all.de.md`](https://github.com/sanskrit-lexicon/SCH/blob/master/prefaces/schpref_all.de.md)
(foreword **Münster, 26 Sept 1924**; published **Leipzig 1928**, Harrassowitz). The
preface is Schmidt's **spec for reading his entries** — and almost all of it is
verifiable as live structure in `csl-orig/v02/sch/sch.txt`.

**1. Marker semantics (the decoder ring).** Schmidt's two relational marks are not
decoration — the digitization already lifted them into a structured `type=` field in
each record's trailing `{…}`:

| Mark | Meaning (per preface) | In data |
|---|---|---|
| `°` | word / sense / gender **wholly absent from pw** (net-new) | **9,254×**, `type=˚` |
| `*` | item **not yet attested** in pw (first attestation) | **5,327×**, `type=*` |
| *(no mark)* | a vocable Böhtlingk added in his Generalindex, carried over | — |

→ We get a **free machine flag for net-new-ness** per SCH headword (`type=˚`/`type=*`),
exactly the "what does this layer add over pw" signal the merge needs.

**2. Contributor / provenance tags (preserve verbatim, like sigla).**
`(Ko.)` = 2,295× — finds from Śrutadevasūri's commentary on the Yaśastilaka;
`[Z.]` = 344× — Zachariae's new attestations; `[B.]` = 137× — E. Baer's ~100+ Kashmir-
Śaivism vocables. These are authorship attributions inside the entry; the translator
must leave them untouched (the existing "sigla untouched" guard already covers them).

**3. Citation conventions.** Cited by **Band, Seite, Zeile**; `v.u.` = *von unten*
(line counted from the bottom, annotation lines excluded); strophes keyed `a,b` /
`a,b,c,d`; location lists deliberately partial (`etc`). Needed to render SCH `<ls>`
refs correctly.

**4. Source-sigla are already resolved — do not rebuild.** [`ls/front1a.txt`](https://github.com/sanskrit-lexicon/SCH/blob/master/ls/front1a.txt)
maps every SCH siglum → full title+edition, **tagged `(PW)`/`(SCH)`/`(CSL)`/`[unknown]`**
(the preface's Pages 03–04 list, extracted *and* merged with the inherited pw
bibliography); [`ls/freq_ls1.txt`](https://github.com/sanskrit-lexicon/SCH/blob/master/ls/freq_ls1.txt)
gives frequencies (Kauś. 236, Daśak. 212, Daśar. 169, Praty.Hṛd. 133, Govardh. 138…).
This is the SCH analogue of `pwgbib.txt` — wire `front1a.txt` into a `sch_sources`
resolver, don't re-extract from the preface.

**5. Two caveats that lower SCH citation confidence vs PWG.**
- Schmidt **took over Böhtlingk's Nachträge citations unverified** ("ich habe alles
  einfach übernommen") — so SCH's Böhtlingk-derived refs are 1889-vintage, unchecked.
- The print **has known typos** ("eine ganze Anzahl von Druckfehlern"); Schmidt even
  flags them inline (e.g. `aṃśumatphala … (Ko.; aśu˚ gedruckt)` = "printed as aśu°").
- Authorship rule when `°`/`*` don't settle it: "the citation or its form decides"
  Böhtlingk-vs-Schmidt.

**6. Scale + dominant source** (corroborates our merge count of ~28,455 SCH entries):
~**14,450** Böhtlingk-Nachträge articles + ~**12,000** Schmidt-original. The new
material is led by the **Yaśastilakacampū** (Somadeva + comm.), the *bhāṇa* plays,
Kashmir-Śaiva texts, and the Kāvyamālā erotic-science editions — a **Classical/late,
kāvya-and-śāstra** stratum (useful for our genre tagging: SCH skews post-classical,
*not* Vedic).

**7. The chain's rationale, in Schmidt's words.** He closes wishing for a full new pw
edition incorporating everything since 1889, needing "alle Indologen der Welt" — which
is precisely the brief **NWS** (Halle, 2013–16) later took up. SCH is the ideological
bridge PWG→PW→**SCH**→NWS.

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

**Scrape status — COMPLETE (2026-06-18): all 167,990 headwords, audit CLEAN.**
The whole dictionary is scraped (`nws_scrape.py section all`), not just the a-section:
`_nws_audit.py all` = 167,990/167,990 present, 0 missing / 0 case-collisions / 0 dups /
0 refusals. Net-new (`has_nws_extra`) = **34,101 (20 %)**; has-NWS-fragment 20 %, has-
Schmidt 17 %, has-pw 81 %, fully-empty 6 %.

**Drift severity — MEASURED across ALL sections (2026-06-18, `_nws_drift.py all`): LOW.**
Comparing the `sch` fragment NWS returns against current `csl-orig/v02/sch` over all
167,990 headwords (extends the a-section finding to the whole dictionary):
- **SCH coverage drift ≈ 0.1 %** — of 28,372 shared Schmidt entries, only 211 are
  NWS-only and 83 csl-orig-only. The Schmidt headword set is essentially unchanged
  since NWS's 2013 snapshot.
- **SCH content 96.7 % identical** (mean token-Jaccard **0.987** after stripping
  boilerplate; only 0.8 % "major" <.5, and those are huge polysemous heads — `a`,
  `agnihotra` — where low overlap = restructuring/granularity, not corrections).
- **PW coverage:** 135,848 in-both (80.9 %); NWS-only just 170 (0.1 %). The 15,501
  (9.2 %) csl-orig-only is **Cologne growth since 2013** (added/re-indexed pw entries),
  not NWS being wrong. (Only `pw_len` was stored, so the pw diff stays coarse — 7.2 %
  show |Δlen|>50 %, inflated by markup; not worth a re-scrape given SCH is near-frozen.)

**Conclusion:** NWS's 2013 Cologne base is **not dangerously stale** — we trust its
pw/Schmidt content as-is. Crucially, the merge sources pw/Schmidt from **current**
`csl-orig` and uses NWS **only for its net-new `has_nws_extra` fragment**, so even the
9.2 % pw coverage NWS lacks never propagates staleness downstream. No reconciliation
needed before using it. ⚠️ *Methodology note (F9 lesson):* an early pass reported scary
43 % "major" SCH / 19.9 % PW drift; both were verification artifacts (formatting
boilerplate; index granularity). Always eyeball a flagged case before trusting an aggregate.

**Fold status — DONE (2026-06-18):** NWS is wired into the merge spine as the 5th layer.
`dict_merge.merged()` appends the NWS fragment last, **only when net-new**, looked up
per-key on demand (kept *out* of `LAYERS` since it adds no new headwords — its keys
derive from the csl layers, and `nws_scrape` enumerates `LAYERS` for the key universe).
The scaled merged-input generator (`_pilot_gen_merged.py --manifest <sec> --limit N`,
driven by `scale_route.py`'s coverage-first manifest) shows NWS-extra reaching **95 %**
on the dense coverage-first core vs 20 % dict-wide — the addendum lands on the high-value
heads that translate first.

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
