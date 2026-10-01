_Created: 07-09-2026 · Last updated: 07-09-2026_

# What else can be reused for `DHĀTUP. x,y`, now that Palsule is exhausted

H1333 wired PWG's `DHĀTUP. gaṇa,serial` citations to G.B. Palsule's artha index and
stopped at **1,226 / 1,751 distinct coordinates (70.0%)** with **139/232 exact
(59.9%)** agreement against Böhtlingk's own parenthesized artha. MG's ruling
07-09-2026: **no better Palsule exists**. This survey answers the follow-up — which
*other* datasets in or near the estate can lift either number — and it reports what
was measured, not what sounds plausible.

Every figure below was derived this session against the live artifacts
(probe scripts were scratch, not committed; each is one grep or one join over files
named here, re-derivable in minutes).

## The two axes, kept apart

A dataset is useful here for exactly one of two jobs, and conflating them is how the
original acquisition spec went wrong:

1. **Disambiguation** — resolving a coordinate to a *root*. H1333 dropped 525
   coordinates because PWG itself gives two claimants (Böhtlingk's double spellings)
   or none. A second dictionary that cites the same coordinates independently is the
   only honest fix.
2. **Artha (meaning)** — what the dhātupāṭha says the root *means*. Palsule supplies
   this today; PWG's inline parentheses are the independent witness that measured it.
   Another artha list is a second witness, not more coverage.

## Ranked findings

### 1. Monier-Williams — the one large second witness, already in the estate ★

[`csl-orig/v02/mw/mw.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/mw/mw.txt)
cites the dhātupāṭha in Böhtlingk's own coordinates, written in Roman gaṇa numerals:
`Dhātup. xxiv, 68`. Measured:

| Quantity | Value |
|---|---|
| Distinct coordinates MW cites | **1,309** |
| Overlap with the 1,751 PWG cites | **1,255** |
| Of the **525** H1333 could not resolve, MW covers | **396 (75.4%)** |
| …of those, with exactly **one** MW headword (immediately usable) | **250** |
| Coordinates MW cites and PWG never does | 54 |
| Cross-check where both resolve to a single root | **749 agree / 53 disagree (93.4%)** |

Two results, both load-bearing. **First**, the 250 unambiguous MW claimants are a
direct +14 pp on coordinate coverage (1,226 → ~1,476 of 1,751, ≈84%) without
inventing anything: the coordinate is read off MW's article exactly the way H1333
reads it off PWG's. **Second**, the 93.4% agreement is the independent confirmation
the H1333 map never had — and the 53 disagreements are not noise, they are the
interesting cases:

```
11,11  PWG=tup    MW=tump      13,2   PWG=ran    MW=rar
15,32  PWG=kvel   MW=kzvel     15,55  PWG=pIv    MW=piva
15,82  PWG=hinv   MW=hi        17,55  PWG=parz   MW=pfz
```

Nasal infixes, ablaut and citation-form variation — the H328 class exactly, now with
a second authority to adjudicate against instead of a guess. MW's glosses are
English, so MW helps the *disambiguation* axis and not the *artha* axis.

**Cost:** zero acquisition. The file is already a pipeline input; the parse is one
regex plus a Roman-numeral conversion.

### 2. vidyut `dhatupatha.tsv` — the artha witness, but on a different numbering

2,259 dhātus in SLP1 with the artha attached (`01.0001 BU sattAyAm`), a superset of
five traditional dhātupāṭhas. Recorded in
[H246](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H246-Fable_GasunsDhatu_2026_printed_book_prep_06.07.26.md)
and [H1023](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1023-Opus_SanskritGrammar_m03-ch5-dhatupatha-panini_16.07.26.md).

**Probed, not assumed:** the path those handoffs name
(`WhitneyRoots/scratch/vidyut_data/prakriya/dhatupatha.tsv`) **does not exist on this
Mac** — the whole `scratch/vidyut_data/` tree is gone. Re-acquisition from the
upstream vidyut/ambuda data release is a prerequisite, not a lookup.

The catch is structural: vidyut's `code` is `gaṇa.sūtra` in the **Pāṇinian ten-gaṇa**
numbering, while `DHĀTUP. x,y` runs to gaṇa 35 in Westergaard's/Böhtlingk's sections.
The two cannot be joined on the coordinate. What vidyut can do is supply a second
artha per **root** — and now that H1333 has a coordinate→root map read off PWG, that
join is (root, artha) against a known root, not the fragile normalized-dhātu join the
original spec feared. Use it to raise the *accuracy* number's denominator above the
232 coordinates where PWG happens to print its own artha.

### 3. Usha Sanka's Mādhavīya dhātupāṭha — Sanskrit artha, but a shadow asset

[`DATA_LAYERS_CENSUS.md`](https://github.com/gasyoun/Uprava/blob/main/DATA_LAYERS_CENSUS.md)
line 127 records `SanskritGrammar/Concordance/UshaSanka_Ph.D_2014/` (361 MB) holding
`dhatu_chart.csv`, `mAdhavIya-dhAtupATha.xlsx` and `dhatu-index.xlsx`. **Probed: not
present on this Mac** — `SanskritGrammar/Concordance/` is 20 MB and holds four
unrelated entries. The Mādhavīya dhātuvṛtti carries the Sanskrit artha per root and
would be the best non-Palsule artha witness available, but it is an acquisition, and
its numbering is Pāṇinian, so it joins like vidyut does: on the root, never on `x,y`.

### 4. DCS dhātu export — English gloss plus the only candidate for a real href

`RussianTranslation/pwg_ru/eval/DCS-6427-dhatus_kjc-fs-cluster.xlsx` (local,
gitignored, landed alongside the Palsule XLS) — **6,427 rows**: `##`, `WORD` (IAST),
`A.P.U.` (pada), `Minning` (English senses, `|`-separated), `URL`. Naive IAST
intersection with the 976 distinct roots in
[`src/data/dhatup_palsule.json`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/data/dhatup_palsule.json)
is **330** — most DCS rows are prefixed verbs (`ākram`, `niṣev`), so the bare-root
overlap is inherently limited.

Its distinctive offer is a **URL**, which this tooltip has never had: H1333 ships
text only because Palsule has no online edition. **Verify before using.** Probed
07-09-2026: the `kjc-fs-cluster.kjc.uni-heidelberg.de` host in the sheet resolves to
`240.0.0.92` from this box (sandbox DNS interception — not evidence the host is
down); the canonical DCS host `www.sanskrit-linguistics.org/dcs/` answers **HTTP
200**, but the `?contents=einzelwort&IDWord=…` deep link returned a 5.5 KB generic
page with no lemma in it. So the DCS deep link is **unverified as an href today** —
and [`SERVER_OUTAGES.md`](https://github.com/gasyoun/Uprava/blob/main/SERVER_OUTAGES.md)
line 59 already records DCS as HTTPS-broken, plain-HTTP only. Wiring a link that
404s would be the fabricated-href failure H1333 explicitly refused, one step removed.

### 5. `pw` (Böhtlingk's abridged dictionary) — 44 citations, free tiebreaker

[`csl-orig/v02/pw/pw.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pw/pw.txt)
uses the identical `DHĀTUP. x,y` notation (same author, same numbering) but only ~44
coordinate-bearing citations against PWG's 2,768 lines. Too small to move coverage;
worth reading in the disambiguation pass precisely because Böhtlingk is his own
authority on which spelling he meant.

### 6. Everything else measured and rejected

- **`csl-westergaard`** — the ideal source, since Westergaard's *Radices* **is** the
  numbering. Probed the repo tree: **405 page scans (`jpg/Westergaard_0001…0405.jpg`)
  plus `wgfiles.txt` and a readme. No digitized text at all.** This is an OCR
  project, not a reuse. It is also why the current gaṇa-level link is a scan viewer.
- **Other Cologne dictionaries** — swept every `csl-orig/v02/*/*.txt` for
  dhātupāṭha citations: `bhs` 30 lines, `ap90` 4, `mw72` 1. Noise.
- **Sanskrit-Sanskrit dictionaries** (VCP, SKD, SHS) — no coordinate-bearing
  dhātupāṭha citations; they gloss roots, they do not number them.
- **`kosha` datasets manifest** — no dhātupāṭha dataset registered.

## What this adds up to

The honest ceiling changes. **Coverage** is not stuck at 70%: Monier-Williams alone
carries ~250 immediately usable unambiguous claimants among the 525 dropped, taking
coordinate coverage to roughly **84%** with no acquisition and no new resolver — and
it simultaneously puts a 93.4% cross-validation under the 1,226 already shipped.
**Accuracy** is the harder half: every remaining Sanskrit-artha source (vidyut,
Mādhavīya) is on Pāṇinian numbering and must be joined through the root, and both are
currently **absent from this machine**, so they are acquisition work before they are
data work.

Recommended order: MW first (free, largest, both jobs at once) — minted as [H4339](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4339-Opus_SanskritLexicography_pwg-dhatup-mw-second-coordinate-witness_07.09.26.md) — then decide whether a
second artha witness is worth the acquisition — the 232-coordinate denominator PWG
gives us for free may simply be the honest sample size.

_Dr. Mārcis Gasūns_
