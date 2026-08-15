# Mining the ⚑ citation gap — the resolver is at its ceiling

_Created: 15-08-2026 · Last updated: 15-08-2026_

**[H2835](https://github.com/gasyoun/Uprava/blob/main/handoffs/H2835-Opus_SanskritLexicography_ls-citation-gap-mine_15.08.26.md)**,
following the residual left open by
[H2827](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H2827-Opus_SanskritLexicography_reglue-vote-v2-ls-links-typology_15.08.26.md)
and [FINDINGS §536](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md).

## The question

H2827 linked 83.6 % of the pwg_ru store's `<ls>` citations and split the rest
into ∅ (a bare abbreviation, nothing to point at) and ⚑ (a real locus with no
target). It called ⚑ "the mintable gap — the only bucket worth research" and
left it unmined. This is the mining.

## The answer, up front

**Of 5,257 ⚑ occurrences, 60 are reachable by writing code. The other 5,197 cite
books Cologne has never digitised.** The resolver is not under-built; it is at
the ceiling its source corpus allows.

| bucket | occurrences | share of ⚑ | what closes it |
|---|---:|---:|---|
| repairable by a pattern rule | **60** | 1.1 % | four named rules, below |
| reachable via a hosted-but-unrouted viewer | **0** | 0.0 % | — nothing to route |
| cites a work with no Cologne scan | **5,197** | 98.9 % | a digitisation, not a regex |

So the ceiling for any code-only effort is **83.6 % → ~84.7 %**. "Mint the
remaining 17 %" is not a project that exists.

## How the number was reached — and why the first attempt was wrong

The first cut classified each gap by regex: *the source resolves elsewhere, so
this must be a format problem*. It reported **262** cheap format gaps. That
number is wrong by more than 4×, and the counter-example is worth keeping:

> `TS. PRĀT. 3,10.` shares its first token with `TS.` — Taittirīya Saṃhitā, 391
> resolving citations. The heuristic scored it cheap. But the Taittirīya
> **Prātiśākhya** is a *different work*, with no Cologne scan. No regex reaches it.

A prefix is not a work. Every "the source resolves elsewhere" claim built on
first-token grouping silently absorbs the sub-works that share that prefix.

The fix was to stop classifying and start **measuring**: apply one small, named,
reversible normalization to the citation string, then ask the real resolver
again. A gap is cheap **iff some repair makes
[`ls_resolver`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py)
emit a real href** — an experiment with a falsifiable outcome, not an opinion.
Run by
[`ls_gap_repair.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_gap_repair.py);
its selftest asserts both directions, including that no repair ever rescues
`TS. PRĀT.`, `AV. PRĀT.`, `SUŚR.` or `DAŚAK.`

## The 60 that do pay

Every row was verified end-to-end: the failing citation, the repaired citation,
the resolver's href, and an HTTP check that the page actually serves.

| repair | occ | fails | resolves after repair | live |
|---|---:|---|---|---|
| `expand_pratis` | 36 | `ṚV. PRĀT. 13,13.` | [rvps/app1/?13,13](https://sanskrit-lexicon-scans.github.io/rvps/app1/?13,13) | 200 |
| `drop_alt_numbering` | 15 | `VARĀH. BṚH. S. 41 (40),5.` | [brihatsam/app1?41,5](https://sanskrit-lexicon-scans.github.io/brihatsam/app1?41,5) | 200 |
| `uppercase_prefix` | 7 | `MBh. 1,71,17.` | [mbhbomb/app1?1,71,17](https://sanskrit-lexicon-scans.github.io/mbhbomb/app1?1,71,17) | 200 |
| `drop_edition_tail` | 2 | `R. ed. Ser. 1,8,19` | [ramayanaschl/?1,8,19](https://sanskrit-lexicon-scans.github.io/ramayanaschl/?1,8,19) | 200 |

What each one means:

1. **`expand_pratis` (36).** PWG abbreviates the Ṛgveda-Prātiśākhya two ways.
   `ṚV. PRĀTIŚ.` routes to the `rvps` viewer; `ṚV. PRĀT.` matches nothing. One
   work, two spellings. **Only ṚV pays** — `TS.`/`AV.`/`VS. PRĀT(IŚ).` are
   distinct works with no scan, and the retest confirms the repair leaves them
   dark rather than mis-routing them.
2. **`drop_alt_numbering` (15).** PWG prints the other edition's chapter in
   parentheses: `41 (40),5`. The parenthetical is apparatus, not a coordinate.
   Dropping it recovers the printed locus; the alternate is never used as the
   link target, so no citation moves to a different chapter.
3. **`uppercase_prefix` (7).** The resolver's prefix map is case-sensitive, so
   the store's occasional `MBh.` / `Śāk.` / `Hariv.` miss where the uppercase
   form hits. A genuine one-line resolver bug, not a data problem.
4. **`drop_edition_tail` (2).** `ed. Ser.` sits between prefix and locus.

## Why the other 5,197 are not work

Two independent checks agree.

**Check 1 — the works are absent.** The 15 largest unrepairable sources are
Suśruta (280), Śāṅkhāyana (241), Chāndogya (198), Āśvalāyana (197),
Prabodhacandrodaya (170), Kauśika (157), Mṛcchakaṭikā (146), Kāmandakīya (128),
Lāṭyāyana (118), Vetālapañcaviṃśati (114), Āpastamba (113), Sarvadarśanasaṃgraha
(107), Śiśupālavadha (85), Pañcaviṃśa (85), Daśakumāracarita (83). None has a
scan in the [sanskrit-lexicon-scans](https://github.com/sanskrit-lexicon-scans)
org. The tail is long and flat: **309 distinct works**, mostly under 50
occurrences each.

**Check 2 — the resolver is not the bottleneck.** Cologne hosts 101 scan repos;
53 are citable text scans (the rest are the CDSL dictionaries themselves and
infrastructure). The resolver already routes to **49 of those 53**. The four it
misses — `abch`, `bhagp_bur`, `sahityadarpana_mw`, `vikramor_mw` — are alternate
editions of works already routed through their primary scan, and they would
unlock **zero** additional citations. Measured by
[`ls_gap_unrouted_viewers.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_gap_unrouted_viewers.py).

There is no hidden inventory. The resolver has consumed essentially everything
Cologne has scanned.

## What this changes

- **FINDINGS §536's residual is closed, and its framing corrected.** It implied
  ~7,000 mintable occurrences worth research. The true figure is 60. Amended
  in place as §537.
- **Do not open a "citation coverage" workstream.** The 60 are a half-hour of
  resolver patterns; beyond them the constraint is the world's supply of
  digitised Sanskrit editions, not this repo's code.
- **The four repairs are diagnostic, not wired in.** They live in
  `ls_gap_repair.py` and are deliberately *not* called from `ls_links.py`. Each
  one rewrites a citation before resolving it, and a wrong rewrite invents a
  reference to the wrong book — worse than leaving it dark. Promoting any of
  them into the resolver is a human's call, one rule at a time.
- **If citation coverage ever becomes a priority**, the lever is upstream: which
  editions get scanned next. The ranked want-list is
  [`ls_gap_unrepairable_by_source.tsv`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/reports/ls_gap_unrepairable_by_source.tsv)
  — Suśruta alone would light up 280 citations.

## Reproduce

```
python src/ls_gap_mine.py             # split ⚑ by source, with pwgbib expansions
python src/ls_gap_repair.py           # the measurement: 60 of 5,257
python src/ls_gap_unrouted_viewers.py # hosted scans the resolver never routes to
```

Selftests: `python src/ls_gap_mine.py --selftest` (11/11),
`python src/ls_gap_repair.py --selftest` (10/10, including four
must-not-rescue assertions).

Artifacts under [`reports/`](https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation/reports):
`ls_gap_by_source.tsv` · `ls_gap_examples.jsonl` · `ls_gap_repairable.tsv` ·
`ls_gap_unrepairable_by_source.tsv` · `cologne_scan_repos.txt`.

_Dr. Mārcis Gasūns_
