# SanskritLibrary.org publications.html — census of 15 positions

_Created: 26-09-2026 · Last updated: 26-09-2026_

**Handoff:** [H5510](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5510-OxAlpha_SanskritLexicography_sanskritlibrary-publications-census_26.09.26.md) · **Executor:** OxAlpha (glm-5.3-flash) · **Source:** https://sanskritlibrary.org/publications.html (fetched 26-09-2026)

**MG rulings baked in (/grillme 26-09-2026, both waves):** all four goals (survey + literature mining + venue scouting + standards/pedagogy benchmark); 3-tier depth with Tier C = kill set (price/availability/talk-list only); 3 free PDFs landed with rights-pending note (dhp precedent, MG 30-07-2026); Vimarśinī added as **third venue option** into the OPEN P4 `@DECIDE` (the choice itself stays human); Rajpopat review = bibliographic pointer only; vimeo speakers NOT registered in IndologyScholars; pedagogy purchase stays `@DECIDE`.

**Method note (network path):** sanskritlibrary.org:443 is filtered from the win-box (TCP 443 timeout; port 80 serves only a 302; local DNS dead — resolved via DoH 1.1.1.1, IP 198.12.158.38). All Tier A/B/C content came through server-side fetch lanes: `webfetch` (raw HTML pages), `r.jina.ai` (PDF text extraction + Lulu JS-rendered spotlight), Wayback Machine (`web.archive.org`, snapshots 2025-06-21/2026-03-03/2026-05-11) for the PDF binaries. Vimeo is CDN-gated (human-check wall) — its talk list was taken from the parent publications.html markup, which carries it verbatim.

## The 15 positions — what-it-gives → consumer repo → action

| # | Position | Tier | What it gives | Consumer repo | Action taken this pass |
|---|---|---|---|---|---|
| 1 | *Vimarśinī: The Sanskrit Library Journal* (`vimarsini.html`) | B | Third venue option: peer-reviewed journal, scope = Vedic/Śikṣā/Chandas/Vyākaraṇa/Nirukta/Nyāya/Mīmāṁsā/Alaṅkāraśāstra + digital critical editing, DH, computational linguistics; Vol I exists (Lulu 25-04-2026); free online by registration + paid print | **SanskritLexicography** (roadmap P4 `@DECIDE`) | Added as third option in `ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md` P4 rows (below); desc/eds pages extracted |
| 2 | SL stylesheet (`slStyle.html`) | B | SL print-composition standards: SLP1-preferred encoding, r/s language tags, accent conventions, daṇḍa-as-period, biblatex author-date | **csl-standards** + `data/dhp` (divergence note) | Divergence note below (§ Standards divergence) |
| 3 | *Linguistic Issues in Encoding Sanskrit* (Scharf & Hyman; `Sanskrit/pub/lies_sl.pdf`) | A | 289-pp book (SL, Providence 2011; Cardona foreword): encoding theory — 3 axes (graphic–phonetic / synthetic–analytic / contrastive–non-contrastive), survey of 13 legacy encodings, SLP basic/segmental/featural appendices | **literature/** (this repo) | PDF landed + rights note; deep read = separate handoff [H5511 (Sonnet 5) — lies-2010-deep-read](https://github.com/gasyoun/Uprava/blob/main/handoffs/H5511-Sonnet_SanskritLexicography_lies-2010-deep-read_26.09.26.md) |
| 4 | *Sanskrit Syntax* 2015 (ed. Scharf, Hock bibliography) | B | 12 papers / 17 contributors; Hock survey + full Hock bibliography of Sanskrit syntax; Aṣṭādhyāyī sutra index | **SanskritGrammar/BibliothecaSanscritica** | [TOC + contributors extracted](https://github.com/gasyoun/SanskritGrammar/blob/main/BibliothecaSanscritica/SANSKRIT_SYNTAX_2015_TOC_CONTRIBUTORS.md) |
| 5 | WSC 2018 Vyākaraṇa section (`wsc2018.html`) | B | 6 papers (Aussant, Bonino, Ben-Dor, Blinderman, Wielińska-Soltwedel, Kawamura), eds Kulkarni & Scharf, UBC 2019 — all **open access** at UBC cIRcle with DOIs | **SanskritGrammar/BibliothecaSanscritica** | [Section TOC + links](https://github.com/gasyoun/SanskritGrammar/blob/main/BibliothecaSanscritica/WSC2018_VYAKARANA_SECTION_TOC.md) |
| 6 | *Śabdānugamaḥ* vol. I (2021) | B+C | Cardona felicitation vol 1 (Vyākaraṇa + śābdabodha): 18 studies / 19 scholars + Cardona bibliography appendix | **SanskritGrammar/BibliothecaSanscritica** | [TOC + contributors](https://github.com/gasyoun/SanskritGrammar/blob/main/BibliothecaSanscritica/SABDANUGAMAH_VOL1_TOC_CONTRIBUTORS.md); price in § Tier C |
| 7 | *Śabdānugamaḥ* vol. II (2022) | B+C | Vol 2 (historical linguistics, Vedic, etc.): 20 studies / 21 scholars (Parpola, Ringe, Hock, Dunkel…) | **SanskritGrammar/BibliothecaSanscritica** | [TOC + contributors](https://github.com/gasyoun/SanskritGrammar/blob/main/BibliothecaSanscritica/SABDANUGAMAH_VOL2_TOC_CONTRIBUTORS.md); price in § Tier C |
| 8 | Śabdānugamaḥ dedication video (vimeo 716920057, 03-06-2022) | C | Talk list only (kill set): honoree Cardona; speakers Ozono, Ajotikar, Ruiz-Falqués, Klebanov, Shukla | — (census record only) | Recorded here; **5 vimeo speakers NOT registered** in IndologyScholars (MG ruling) |
| 9 | *Śabdabrahman* (2022, 2 vols) | B+C | Pedagogy: linguistic intro to Sanskrit, no prior knowledge assumed; vol I text+exercises (20 lessons), vol II appendices + Pāṇinian terminology crosswalk | Census benchmark (§ Pedagogy) + purchase `@DECIDE` | Descriptive summary + prices; GTD `@DECIDE` purchase row minted |
| 10 | *Saṅkṣiptamahābhāratam* (2022) | B+C | Pedagogy reader: MBh 1.55 (43 verses) with graded prose paraphrases + glossary; 2nd-semester+ | Census benchmark + purchase `@DECIDE` | Same |
| 11 | *Rāmopākhyāna* Devanāgarī rev. ed. (2023, 2 vols) | B+C | Pedagogy reader: MBh Āraṇyakaparvan 257–276 (728 verses), per-verse apparatus (sandhi, inflection, glossary, derivation, prose, translation) | Census benchmark + purchase `@DECIDE` | Same |
| 12 | *Rāmopākhyāna* Roman rev. ed. (2023, 2 vols) | B+C | Same work, Roman-script version (sandhi analysis + appendices in Roman) | Census benchmark + purchase `@DECIDE` | Same |
| 13 | *Rāmopākhyāna* English prose translation (2023) | B+C | Close English prose translation + introduction; secondary-school/university audience | Census benchmark + purchase `@DECIDE` | Same |
| 14 | Scharf, *Review of Rajpopat, In Pāṇini we trust* (23-12-2022; `pub/scharf-ReviewOfRajpopat-InPaniniWeTrust.pdf`) | A | 83-pp review: critiques the universal "right-hand operation first" reading of A. 1.4.2 *vipratiṣedhe param kāryam* with counterexamples (*bhavya*, *bhavanti*); credits Rajpopat's affix-before-base observation | **SanskritGrammar/BibliothecaSanscritica** (pointer only) | [Bibliographic pointer](https://github.com/gasyoun/SanskritGrammar/blob/main/BibliothecaSanscritica/RAJPOPAT_REVIEW_POINTER.md); deep read = separate Sonnet handoff (residual minted) |
| 15 | *Sanskrit characters: 12 fonts conjunct coverage* (05-08-2023; `pub/chars.pdf`) | A | Authoritative comparison table: 12 fonts × full conjunct inventory (columns: SKT, SKT option, Chandas, Uttara, Siddhanta, San2003, San2020, Shobhika, ShobhikaB, SanTxt, Praja, Arial, DevMT, Mangal + SLP1/Roman reference) | **sanskrit-fonts** + literature/ | [Crossrow](https://github.com/sanskrit-lexicon/sanskrit-fonts/blob/gh-pages/README.md) in sanskrit-fonts README; PDF landed in literature/ |

## Venue profile — Vimarśinī (for the P4 `@DECIDE`)

From `vimarsini.html` + `pubdesc/vimarsinidesc.html` + `pubdesc/vimarsinieds.html` (fetched 26-09-2026):

- **Status:** peer-reviewed journal of The Sanskrit Library; Vol I published in print 25-04-2026 (Lulu, hardcover $39.60); **free online access by registration** (Google form `cNNDCynbGBqnpfyu5`); Indian-rupee orders via the shared SL India form.
- **Scope:** Sanskrit, Prakrit, Pāli in Vedic, Śikṣā, Chandas, Vyākaraṇa, Nirukta, Nyāya, Mīmāṁsā, Alaṅkāraśāstra **plus** digital critical editing, digital humanities, computational linguistics — P4 (indigenous microstructure of ŚKD/VCP, digital method) is squarely in scope.
- **Review process:** submissions to the editor-in-chief, following the SL stylesheet (`slStyle.html`); no public CFP or deadline calendar found on the fetched pages — a gap to note, not to guess.
- **Editorial board:** P. M. Scharf (editor-in-chief), Anuja P. Ajotikar, Tanuja P. Ajotikar, Sharon Ben-Dor, Timothy Cahill, Brendan Gillon, Masato Kobayashi, Aleix Ruiz-Falqués.
- **Registration act (human-only):** the P4 venue row now reads IJL / WSC 2027 / *Vimarśinī* — the choice is MG's `@DECIDE`, untouched.

## Standards divergence — slStyle vs estate surfaces

Point (8) of the mission, recorded as a note (no standards repo edits):

1. **slStyle.html is presentation-composition-oriented:** it governs how a *paper* is typeset for SL print — SLP1-preferred inline encoding (`{p}ARini`), `<r>`/`<s>` Roman-vs-Devanāgarī tags, udātta/svarita accent marks (acute/circumflex/grave), daṇḍa encoded as period, American/British quote-register rules, biblatex author-date with SLP1-tagged Sanskrit titles.
2. **`data/dhp` DTDs are data-model-oriented:** `ScharfMDhP/MadhaviyaDhP3.dtd` (Funderburk/Scharf pipeline, 2009 lineage) defines a custom XML document (`<MadhaviyaDhP3>`, elements `sUtra`/`entry`/`fullDAtu`/`lemma`/`sense`, attribute-coded accents `u/a/s` and pada `p/a` in `preds`) — the same SL intellectual family but encoding **structural dhātupāṭha data**, not print typography. Divergence axis: typographic conventions (slStyle) vs structural encoding (dhp DTD) — no conflict, different layers; the shared ground is the SLP1-family transliteration.
3. **csl-standards line:** the estate's own standards surface is [sanskrit-lexicon/csl-standards](https://github.com/sanskrit-lexicon/csl-standards) (TEI Lex-0 pilot incl. 47 SKD samples, roadmap G2). If SL conventions are ever adopted for submission (e.g. a Vimarśinī P4 submission), the mapping SLP1-tags ↔ estate transcoder chain and Lex-0 ↔ SL markup would be a small dedicated note — **not built here** (no consumer yet).

## Pedagogy benchmark (point 11, short form)

| SL print product | Estate counterpart | Positioning |
|---|---|---|
| *Śabdabrahman* (2 vols, $55+$46; ₹5,000 India) — linguistic intro from zero, 20 lessons + appendices, audio | [gasuns-sanskrit-manual](https://github.com/gasyoun) + Systema-Sanscriticum course (A0→ ladder, live platform) | SL = self-contained print course with Pāṇinian terminology crosswalk; estate = interactive platform with immediate evaluation (SL's own online courses mirror this) — benchmark for the manual's exercise-apparatus density, not a replacement |
| *Saṅkṣiptamahābhāratam* ($35 hc / $30 coil; ₹4,000) — 43-verse reader, graded paraphrases | Systema-Sanscriticum reading layer (learner's layer v1, csl-atlas) | SL's "several prose paraphrases per verse, simple→complete" is a directly transferable pedagogical device for the atlas learner layer (P6) |
| *Rāmopākhyāna* (4 hcs $21+$101 ×2 scripts + $25 English) — 728-verse reader, per-verse sandhi/inflection/glossary/derivation | estate epic-reading modules (DCS-based) | The per-verse apparatus is the print analogue of the lemma dossier; the 2-script parallel editions are a model for Devanāgarī/Roman dual delivery |

**Purchase stays MG `@DECIDE`** — GTD row minted this pass linking this census + the Lulu price table. Total set cost ≈ $460 print (all 13 Lulu items, see below) or the rupee route (SBI transfer, e.g. Śabdabrahman I ₹5,000; up to 5 weeks delivery, non-returnable).

## Tier C — Lulu price/availability table (kill-set depth; jina render of the spotlight, 26-09-2026)

| Product | Format | Published | Price |
|---|---|---|---|
| Vimarśinī: The SL Journal, Vol. 1 | hardcover | 25-04-2026 | $39.60 |
| Rāmopākhyāna — close English prose translation | paperback | 23-11-2023 | $25.00 |
| Rāmopākhyāna rev. Devanāgarī vol. 2 | hardcover | 27-10-2023 | $101.00 |
| Rāmopākhyāna rev. Roman vol. 2 | hardcover | 27-10-2023 | $101.00 |
| Rāmopākhyāna rev. Roman vol. 1 | hardcover | 27-10-2023 | $21.00 |
| Rāmopākhyāna rev. Devanāgarī vol. 1 | hardcover | 27-10-2023 | $21.00 |
| Saṅkṣiptamahābhāratam (coilbound) | paperback | 03-01-2023 | $30.00 |
| Saṅkṣiptamahābhāratam | hardcover | 03-01-2023 | $35.00 |
| Śabdabrahman vol. I (Text and exercises) | hardcover | 23-07-2022 | $55.00 |
| Śabdabrahman vol. II (Appendices) | hardcover | 23-07-2022 | $46.00 |
| Śabdānugamaḥ vol. II | hardcover | 16-02-2022 | $126.00 |
| Śabdānugamaḥ vol. I | hardcover | 04-02-2022 | $126.00 |
| Sanskrit Syntax (2015) | hardcover | 20-03-2015 | $100.00 |

Google order forms (Tier C): `forms.gle/2GmheR9jgTZh7XAm8` = **"The Sanskrit Library Publications India Order"** — email/name/address/pin/+91 phone, per-book rupee prices (e.g. Śabdabrahman I ₹5,000; nutshell ₹4,000), SBI account settlement (acct 37887607863, IFSC SBIN0021161), ≤5 weeks, non-returnable; `forms.gle/CB3dAbTMwY3T82eLA` = the Sanskrit-Syntax-specific variant of the same India-order form. Vimeo 716920057: CDN human-check wall; availability not probed deeper (kill set); talk list recorded from the parent page above.

## Landed artifacts (this pass)

- `literature/lies_sl.pdf` (2.6 MB), `literature/chars.pdf` (4.9 MB), `literature/scharf-ReviewOfRajpopat-InPaniniWeTrust.pdf` (92 KB) — from Wayback snapshot bytes (originals behind the site's filtered 443); SHA-256 in [docs/SANSKRITLIBRARY_PDFS_RIGHTS_NOTE_26-09-2026.md](docs/SANSKRITLIBRARY_PDFS_RIGHTS_NOTE_26-09-2026.md).
- [SanskritGrammar/BibliothecaSanscritica/](https://github.com/gasyoun/SanskritGrammar/tree/main/BibliothecaSanscritica): 4 volume TOC/contributor files + Rajpopat pointer.
- [sanskrit-fonts README](https://github.com/sanskrit-lexicon/sanskrit-fonts/blob/gh-pages/README.md): chars.pdf crossrow.
- [IndologyScholars curation/non_participant_indologists.csv](https://github.com/gasyoun/IndologyScholars/blob/main/curation/non_participant_indologists.csv): +2 rows — Scharf (`RIND_64c2044a`), Malhar Kulkarni (`RIND_67ecefda`); **only these two** (MG ruling; the 5 vimeo speakers deliberately excluded).
- `ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md`: P4 venue cell + Q1-2027 item now carry the third option.
- GTD: 2 rows — pedagogy purchase `@DECIDE`; Rajpopat deep-read handoff mint `@DO`.

---

_Gasūns_
