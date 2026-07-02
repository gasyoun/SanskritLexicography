# A36 — referee-style review (pre-submission)

_Created: 02-07-2026 · Last updated: 02-07-2026_

Substantive pre-submission review of
[A36_latin_obscena_note.md](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A36_latin_obscena_note.md)
by Fable 5 (`claude-fable-5`), 02-07-2026, within the Fable trial window (session S9). Target
venue: **Beiträge zur Geschichte der Sprachwissenschaft** (Nodus; historians of linguistics,
not computational linguists). All internal numbers were re-verified against the three CSVs and
against `csl-orig` source (every §3/§3a/§3b figure checks out exactly; the PWG line count
593,596 is real); the external claims (Loeb/Goold, OED/Murray, LSJ) were verified on the web.
Findings are ranked; **all of Major 1–7 and Minor 8–14 were applied in the same pass** — each
item below records its resolution.

**Overall verdict: the paper is sound, the data is honest, and the core finding (a datable,
audience-sensitive Latin screen with a within-author tightening) will genuinely interest BGS.
The two real referee risks were (a) a method-first framing at a historiography venue and (b) a
missing comparandum — Liddell–Scott's Latin glosses for obscene Greek — that any historian of
classical scholarship will know and that made the novelty claim look naive. Both fixed. After
this pass I judge the paper ready to send, with the Nodus stylesheet conformance deferred to
acceptance (the cover letter already offers it).**

## Major (all applied)

1. **The nearest prior was missing: Liddell–Scott screens obscene Greek in Latin *inside a
   dictionary*.** LSJ glossed βινέω as "*inire, coire*", λαικάζω as "to wench" — the identical
   device, in the era's most famous dictionary, removed only by the Cambridge Greek Lexicon
   (Diggle et al. 2021), which made international headlines for doing so
   ([Guardian/Irish Times coverage](https://www.irishtimes.com/culture/books/first-english-dictionary-of-ancient-greek-since-victorian-era-spares-no-blushes-1.4576743);
   [Wikipedia: A Greek–English Lexicon](https://en.wikipedia.org/wiki/A_Greek%E2%80%93English_Lexicon)).
   A BGS referee reads "has never previously been documented" against that and stops trusting
   the author. **Fix applied:** new §0 paragraph on Greek lexicography; novelty claim re-scoped
   to what is actually novel — first documentation for *Sanskrit* lexicography, first
   *quantification* for any tradition, and the metalanguage-relative confound fix. Cover
   letters re-hedged identically. Diggle et al. 2021 added to references. The LSJ case
   *strengthens* the paper: it shows the screen was pan-philological, which is the paper's own
   thesis (§1 already says the school "took it over from Greek and Roman textual scholarship").
2. **History must lead — the venue is a historiography journal.** Title and abstract led with
   the method; the cover letter promises historiography first. **Fix applied:** retitled to
   *"The Latin discretion-screen in nineteenth-century Sanskrit lexicography: a history, and a
   metalanguage-relative method for measuring it"*; abstract rebuilt with the historical
   finding as ¶1 and the method as ¶2; both cover letters updated (incl. the German rendering
   of the title). ⚠️ **M.G.: the retitle is the one edit you may want to veto** — the old title
   survives in git history if so.
3. **Internal contradiction on Bopp, caught against source: BOP has no √*yabh* entry at all.**
   §3b said "Bopp does not even reach for *futuere* on the sex act" (correct — zero *futu-*
   hits other than *futurum* "future") while the §5b table claimed BOP glosses the sex act
   *futuere* (wrong). Verified in `csl-orig/v02/bop/bop.txt`: no `<k1>yaB` headword; the sex
   act appears under other lemmas glossed with clinical Latin (*maithuna* → *coitus*; under
   √*gam*: "adire virum, feminam, i.e. *coire, concumbere*"). **Fix applied** to the §3b
   bullet and the §5b table row.
4. **MW72's lone obscene-core hit is not a screen — and removing it sharpens the diachrony.**
   The single *cunnus* in the 1872 Monier-Williams (line 215431) sits inside a comparative
   etymology (Lithuanian *pís-ti* glossed in Latin), not a headword gloss; and MW72's own
   √*yabh* gloss is plain English ("to know carnally, have sexual intercourse with, lie
   with"). So the first edition screens **zero** headwords and the 1872→1899 tightening is
   starker than claimed — plus the etymology-in-Latin exactly echoes the §5a finding (the
   comparative reach hides behind Latin). **Fix applied:** §3c row and narrative corrected,
   the 1872 gloss quoted.
5. **§3c table was malformed Markdown** — two stacked header rows (a 4-column header followed
   by a 5-column one), rendering broken; and §3c's counts silently come from the raw corpus
   sweep that is only explained (and disclaimed) in §3d, so its MW figure (6) disagrees with
   the curated §3a figure (*futuere* ×4 + *mingere* ×1). **Fix applied:** single header,
   explicit "counts are the raw §3d sweep tallies" clause.
6. **Adams misattribution risk: *stercus*, *cacare*, *mingere* are not Adams "basic
   obscenities".** In Adams 1982 *stercus* is the ordinary word (usable in agricultural
   prose; *merda* is the obscenity) and *mingere* the acceptable term. A classicist referee
   scores an easy point against "words obscene *in Latin itself*… *stercus*". The paper's own
   metalanguage-relative logic supplies the honest fix: what matters is markedness in the
   *dictionary's* language, not in Rome. **Fix applied:** the marker set is now defined as
   Adams' basic obscenities proper (*futuere, cunnus, mentula, paedicare*) **plus** the blunt
   scatological/urinary set, with an explicit sentence that the latter are included not for
   their Latin-internal register but because no 19th-century vernacular author prints them
   except as a screen (abstract, §2, §3b wording aligned).
7. **43 vs 44.** [`A36_corpus_screen.csv`](https://github.com/gasyoun/SanskritLexicography/blob/master/papers/A36_corpus_screen.csv)
   has 44 rows and 30 English entries; the paper says 43 dictionaries and ~29 English. The
   arithmetic only works because MW's two editions are two rows but one dictionary — nowhere
   stated. **Fix applied:** counting convention made explicit in §3d and §7.

## Minor (all applied)

8. **"OCS *jębati*" is phonologically wrong** (nasal *ę* would give Russian *я*-vocalism; the
   attested Russian is *ебать* with *e*). Standard reconstruction is Common Slavic *jebati* —
   and the word is not attested in the OCS canon anyway. Fixed to "the Slavic root *jebati*".
9. **"Only seven comparative-grammar references in all of PWG"** hedged to the scope of the
   sigla scan actually run (§5a and abstract) — "exactly seven" invited a counterexample hunt.
10. **"High-Victorian" for a Russian-imperial German product** — one clause added
    acknowledging the anglocentric shorthand; the print-decency regime it names was European.
11. **LAN (Lanman) appeared in §3c/§3d but not in the references** — added (Reader 1st ed.
    1884; the CDSL edition is dated 1906).
12. **§1's PWG quotation was in raw SLP1 markup** (`{#yaB#}`) — now rendered in IAST for the
    journal's readers, with the csl-orig link kept as the source.
13. **Cover-letter word count** ("6,000–7,000") updated to "roughly 7,000" (the draft runs
    ~7,500 gross including tables and apparatus); EN letter's German-terminology teaser
    synced to the DE letter's fixed terms (*Diskretionsschirm, Schirmsprache,
    metasprachenrelativ, verschleiert*).
14. **Status block** updated (draft date, this pass recorded, readiness 5/5).

## Left for M.G. (flagged, not applied)

- **The retitle veto** (Major 2 above).
- **Wilson 1819.** §3c anchors "absent before" on Wilson **1832**, which is the *second*
  edition; the 1819 first edition would push the pre-screen baseline earlier still. Optional
  one-line footnote if you can check the 1819 printing of √*yabh*'s region — do not claim it
  unseen.
- **Nodus stylesheet** — the one remaining formal step, only obtainable from the editors; the
  paper keeps its clean author-date form and the cover letter offers conformance. This is a
  post-acceptance task, not a submission blocker: **send it**.
- **Suggested reviewers** in the cover letter are still the placeholder categories — name real
  people or delete the section before sending.

## What is genuinely strong — keep and foreground

The within-author tightening (MW 1872 plain English → 1899 *futuere* ×4) is the quotable
datum — it is now stronger still (see Major 4) and stays in the abstract. The Bopp positive
control (§5b: the screen maps exactly onto the gaps in printable German — *Hure* and
*schänden* exist, so *meretrix* and *stuprum* never appear) is the most elegant argument in
the paper and would survive any referee. The 401-entry blunt-German counter-inventory with
its zero in the sex column is the single most persuasive table. The metalanguage-relative
point (§3b) is a real methodological contribution beyond this corpus — the LSJ addition now
gives it a second famous instance to generalise over.

_Review: Claude Fable 5 (`claude-fable-5`) · paper: Dr. Mārcis Gasūns_
