# H4432 — independent adversarial verifier report

_Created: 09-09-2026 · Last updated: 09-09-2026_

**Verifier model:** Claude Code, Opus 5 (`claude-opus-5`). Independent context; not the implementer.
**Scope:** every load-bearing number re-derived from `csl-orig/v02/pwg/pwg.txt`, `mw.txt` and
`Palsule_Artha_24_01_2014.xlsx` with code written for this report. My scanner
(`scan.py` / `resolve.py`) does **not** import `build_dhatup_palsule.py`; the four
end-to-end counterfactual builds use a **copy** of the builder patched in scratch and
written with `--out` to scratch. No file in any git repository was created, modified or deleted;
`git status --porcelain` in SanskritLexicography is empty at the end of this run.

Working directory for everything below:
`/private/tmp/claude-502/-Users-mac-Documents-GitHub/b0345078-e3e3-429b-b956-2062d8efdbb5/scratchpad/verifier/`

## Verdict table

| Claim | Verdict | One-line reason |
|---|---|---|
| C1 baseline 1465/1751, 1226/140/99, 1751 cited, 271 dropped | **CONFIRMED** | Reproduced exactly, including the 1226 coordinate set and every attribution |
| C2 blunt guard moves 241 = 93 + 130 + 18 | **CONFIRMED** | Exact, under "a claimant is dropped if ANY head-line citation carries the note" |
| C3 narrow = 0 lost / 93 gained / 18 reattributed, 32,56 → cakk | **CONFIRMED** | Exact, and the real build ships `32,56 cakk` |
| C4 funnel 74 → 43 → 31; **new baseline 1496/1751 = 85.4%** | **funnel CONFIRMED · baseline REFUTED** | The real build gives **1493/1751 = 85.3%**: +31 gains **−3 deleted rows** |
| C5 17 of 18 already in the shipped table, 33,5 is the 18th | **CONFIRMED** | Exact; nuance: 23,39's shipped row is `mw-respell`, not `pwg` |
| C6 331 claimants; 8 `<lex>`-nominal + 10 no-head-line, disjoint, exhaustive, zero verbal | **mechanically CONFIRMED · the published gloss REFUTED** | 331/8/10 exact — but **8 of the 18 targets are genuine root articles**, 6 of them carrying Böhtlingk's own `√` |
| C7 clause scoping: 331 → **148**, reattributions → exactly those **8** | **CONFIRMED** | My independently written clause rule gives 148 and the identical 8; robust to a rule variant |
| C7b "the detector is wrong 183 of 331" | **PLAUSIBLE, overstated** | ~17 of the 183 are genuine notes my v1 rule misses; the defensible figure is **166 of 331** |
| C7c "the MW-side defect left uncorrected on the Böhtlingk side" | **CONFIRMED** | Commits `cc1c75c6` + `4d6f285c` clause-scoped `_MW_VL`; `_BOEHTLINGK_VL` never got it |
| C8 all 10 eliminated notes belong elsewhere | **CONFIRMED, 10 of 10** | Corpus quoted below; none is a genuine disowning |
| C9 4 clearly justified, 32,30 with reservation, 17,13 + 32,119 not justified | **CONFIRMED with amendments** | 32,30 is better than "with reservation"; 17,13 / 32,119 never actually ship the noun |
| C10 `<lex>` test has the same line-scope defect | **CONFIRMED, magnitude wrong** | `vell`'s `<lex>` is **1148 chars** after the citation, not ~2 kB; globally **73 of 128** nominal flags are line-scope artifacts |
| C11 DECLINE CONFIRMED, artifact byte-identical | **CONFIRMED as to the decision · the stated reason set needs correcting** | Right call, partly wrong reasons; and two *unrelated* defects I found are worth applying |

---

## What I ran

```sh
cd .../scratchpad/verifier
python3 scan.py            # my own PWG scanner: citation forms, head/body, <lex>, v.l. line- and clause-scoped
python3 resolve.py         # H1333's resolution rule re-implemented + Palsule join
python3 c1.py              # C1 against the shipped artifact
python3 c2c3.py            # blunt / narrow counterfactuals, both drop-rule readings
python3 c4c7.py            # the 74→43→31 funnel, C5, clause-scoped reattributions
python3 c6.py              # nominal / no-head-line split + the hidden re-attributions among the 43
python3 c10.py             # <lex> position relative to the citation
python3 quote.py <coord>…  # raw corpus lines with offsets of citation, v.l. and <lex>
python3 sample183.py       # random sample + gap statistics over the 183 divergent firings
python3 edge.py            # clause-rule true positives and its closest refusals
python3 c7b.py / c7c.py    # robustness of the "exactly 8" result under two variant clause rules
python3 targets.py         # is each reattribution TARGET's own article a root or a noun article?

# end-to-end counterfactual BUILDS (patched copies of the builder, --out to scratch)
python3 cf_builder.py        --out base_rebuild.json   # sanity: reproduces the shipped table exactly
python3 cf_builder_line.py   --out cf_line.json        # narrow guard, LINE-scoped
python3 cf_builder_clause.py --out cf_clause.json      # narrow guard, CLAUSE-scoped
python3 cf_lex.py            --out cf_lex.json         # <lex> scoped to BEFORE the citation
python3 cf_formc.py          --out cf_formc.json       # + the citation form the builder cannot see

# the repo's own harnesses, read-only, from the main checkout
python3 src/pilot/dhatup_h4349_verify.py    # exit 0, "coverage 1465/1751 = 83.7%"
python3 src/pilot/ls_enrichment_selftest.py # exit 0, 21 checks passed
```

`base_rebuild.json`'s `table` is **byte-identical** to the shipped
`src/data/dhatup_palsule.json` `table` (only `built` and `builder_sha256` differ, because
I edited two path lines in my copy). Every counterfactual below is measured against that.

---

## C1 — CONFIRMED

My scanner, written from a survey of pwg.txt's markup:

```
entries seen: 122730
coords cited: 1751   resolved: 1480   dropped as multi-claimant: 271   linked to Palsule: 1226 (70.0%)
```

Against the shipped artifact: 1465 rows, `{'pwg': 1226, 'mw': 140, 'mw-respell': 99}`,
1465/1751 = 83.67% → 83.7%. My 1226 PWG coordinates are the **same set** as the shipped
`source=pwg` rows (symmetric difference 0) and **zero** attribution mismatches. `_stats`
`coords_cited` 1751, `coords_conflicted` 271, `coords_linked_pwg` 1226 all match my
independent derivation. `set(table) ⊆ cited` holds.

**One caveat that C1 does not state and nobody should read past** (see § "Two defects I found
that nobody claimed", defect 2): 1751 is the number of coordinates *the builder's citation
regexes can see*, not the number PWG cites.

## C2 — CONFIRMED

The drop rule has two natural readings. Only one reproduces the published split:

| reading of "the claimant carries the note" | gained | lost | reattributed | moved |
|---|--:|--:|--:|--:|
| **ANY head-line citation of that coordinate carries it** | **93** | **130** | **18** | **241** |
| ALL head-line citations of that coordinate carry it | 94 | 125 | 18 | 237 |

The published 93 / 130 / 18 = 241 is exact under the first reading. I use that reading
throughout. The 18 reattributions are identical under both.

## C3 — CONFIRMED

Narrow reading (guard applied only where the coordinate has >1 claimant, never emptying the
claimant set): **0 lost, 93 gained, 18 reattributed**, and `32,56` resolves to `cakk`
— confirmed not just in the scanner but in the real build, where the shipped row becomes
`{'root_iast': 'cakk', 'source': 'pwg', 'palsule_root': 'cakk', 'artha_count': 5}`.

## C4 — funnel CONFIRMED, published baseline REFUTED

The funnel reproduces exactly:

```
93 gains  →  74 have a Palsule row  →  43 of those are already in the shipped table
             (all 43 with source='mw')  →  31 net new
```

But **1465 + 31 = 1496 is not what the pipeline produces.** I built it. The narrow,
line-scoped guard end to end gives:

| | shipped | narrow / line-scoped | narrow / clause-scoped |
|---|--:|--:|--:|
| rows | 1465 (83.7%) | **1493 (85.3%)** | 1490 (85.1%) |
| rows added | — | 31 | 25 |
| **rows deleted** | — | **3** | **0** |
| rows whose root changes | — | **21** | 13 |
| rows whose `source` token changes but root does not | — | 46 | 33 |
| `coords_linked_pwg` | 1226 | 1290 | 1280 |
| `coords_conflicted` | 271 | 178 | 202 |

The three deleted rows are `28,1 tud`, `31,1 krī`, `31,41 grath` — all currently `source=pwg`.
They vanish because the guard hands the coordinate to `vyathana` / `vinimaya` / `saṃdarbha`,
none of which Palsule has, and MW does not refill them. **`28,1` is tud, the first root of the
tudādi gaṇa.** Deleting it is not a rounding error in a coverage figure.

The arithmetic `1465 + 31` counts the gains and silently assumes the reattributions are free.
They are not: 12 of the 18 reattribution targets have no Palsule row, so each either deletes a
shipped row or pushes it onto a different witness. **1496/1751 = 85.4% is REFUTED; the measured
figure is 1493/1751 = 85.3%.**

**And "17 already-published rows flip" undercounts the disturbance.** 21 shipped rows change
root, not 17 — because 13 of the "43 the MW pass already fills" are coordinates where the PWG
counterfactual, running *before* MW, wins with a *different* root:

```
5,53 gaggh→ghaggh · 15,6 śucy→cucy · 15,36 śel→sel · 17,43 riṣ→caṣ · 17,69 pis→pes
21,15 cīv→cīy · 26,23 jhṝ→su · 28,84 cuṇ→chuṭ · 28,90 puḍ→buḍ · 31,35 kṣī→kṣi
32,21 śamb→samb · 32,63 mul→mūl · 33,63 lag→rak
```

Those 13 are invisible in the published funnel, which counts them only as "already filled".
`26,23 jhṝ → su` and `33,63 lag → rak` are not spelling variants; they are different roots.

## C5 — CONFIRMED

17 of the 18 reattributed coordinates are in the shipped table; the missing one is exactly
`33,5 kuṭumbay → tantray`. Nuance worth recording: 16 of the 17 are `source=pwg`;
`23,39` is `source=mw-respell` (shipped root `hve`), so it is a published row but not a
published *PWG* attribution.

## C6 — mechanically CONFIRMED, the published gloss REFUTED

Mechanical part, exact: **331** head-line (coordinate, root) pairs carry a line-scoped note
(out of 1999 head-line claimant pairs). The 18 reattribution targets split
**8 `<lex>`-flagged nominal head-line claimants + 10 with no head-line citation of the
coordinate at all**, disjoint and exhaustive, and none goes to a claimant that is a
head-line, non-`<lex>` claimant of that coordinate. All reproduced.

**The gloss built on top of that split does not survive.** ABBREVIATIONS_RU says "all 18
reattributions hand the coordinate to a claimant that is not a verbal head line" and the
handoff repeats it as "all 18 … hand the coordinate to a NOMINAL claimant". I checked each
target's **own article head line**:

| target | coordinate | `√` on its head line | `<lex>` on its head line | what the article is |
|---|---|---|---|---|
| lal | 9,76 | **yes** | no | root article |
| vell | 15,33 | no | no | root article (`{#vell#}¦, {#ve/llati#}`) |
| tvacana | 17,13 | no | yes | noun |
| parikalkana | 17,80 | no | yes | noun |
| saṃcalana | 19,2 | no | yes | noun |
| śoṣaṇa | 23,10 | no | yes | adj./noun |
| hvā | 23,39 | no | no | root article (`{#hvA#}¦, {#hU#}`) |
| vyakta | 23,40 | no | yes | adj. |
| vyathana | 28,1 | no | no | deverbal action noun |
| jñīpsā | 28,120 | no | yes | noun |
| vinimaya | 31,1 | no | yes | noun |
| saṃdarbha | 31,41 | no | yes | noun |
| tuj | 32,30 | **yes** | no | root article |
| bal | 32,68 | **yes** | no | root article |
| mlecchana | 32,119 | no | yes | noun |
| tantray | 33,5 | **yes** | no | root article (denom.) |
| las | 33,55 | **yes** | no | root article |
| svar | 35,11 | **yes** | no | root article |

**8 of the 18 targets are verbal root articles, 6 of them carrying Böhtlingk's own `√`.**
"No head-line citation of this coordinate" is not "nominal": Böhtlingk routinely puts a
causative or secondary sense of the *same root* on a later `<div n="p">` continuation line —

```
las  33,55 : <div n="p">— <ab>caus.</ab> {#lAsa/yati#} ({#Silpayoge#}, <ab>v. l.</ab> {#Silpopayoge#}) <ls>DHĀTUP. 33,55</ls>.
svar 35,11 : <div n="p">— <ab>caus.</ab> {#svarayati#} <ls>DHĀTUP. 35,11</ls> ({#Akzepe#}).
bal  32,68 : {#bAla/yati#} {%ernähren%} ({#BftO#}) <ls n="DHĀTUP. 32,">68</ls>.
tuj  32,30 : <div n="1">— 3〉 {#tuYja/yati#} und {#toja/yati#} = {#hiMsA, bala, AdAna#} oder {#dAna, niketana#} <ls>DHĀTUP. 32,30</ls>.
```

Those are verbal claimants by any reading. The head/body discriminator cannot see them, which
is a **third** line-scope-class defect in the same builder (the `at_head` flag is true for
exactly one physical line after `<L>`, so every later sense of a multi-sense root article is
"body"). The correlation is sharp and it favours the clause rule: of the 8 reattributions the
clause test keeps, **6 go to root articles**; of the 10 it eliminates, **9 go to nouns**.

## C7 — CONFIRMED (the central claim), with one number corrected

I wrote my own clause test before reading the builder's `_vl_governs`, from the articles: the
note governs the citation only when, between them, there is (a) no other `<ls …>` citation,
(b) no `.` or `;` at parenthesis depth 0 once `<…>` tags and `{#…#}` / `{%…%}` braces are
stripped, and (c) no unclosed `(` — the note must not sit inside a parenthesis opened after the
citation.

```
head-line claimants carrying a note, LINE-scoped   : 331
head-line claimants carrying a GOVERNING note      : 148     <-- C7's number, reproduced
narrow-reading reattributions under clause scoping :   8     <-- C7's set, reproduced exactly
```

and the set is the same eight, in the same direction:

```
15,33 vehl→vell · 17,13 tvakṣ→tvacana · 32,30 lañj→tuj · 32,68 cal→bal
32,119 mlakṣ→mlecchana · 33,5 kuṭumbay→tantray · 33,55 laś→las · 35,11 sur→svar
```

**Robustness (this is what makes it more than a coincidence of two rules).** I built two
variants of my own rule and re-ran:

- **v2**, also admitting any note separated from the citation by punctuation only: 183 governing
  claimants, **10** reattributions — it wrongly re-admits `9,76 laḍ` and `19,2 vyath`, whose
  notes sit inside an artha parenthesis. v2 is a worse rule and I reject it.
- **v3**, admitting only a note separated by a bare `.` (no parenthesis): **165** governing
  claimants, **exactly the same 8 reattributions**.

So the "exactly 8" result is stable across a 148→165 swing in the detector's own sensitivity.

**The one number I will not sign as written is "wrong 183 times out of 331".** 183 is the count
of pairs where line-scope fires and my v1 clause rule does not; it is not a count of errors.
Sampling and shape analysis over those 183:

```
gap between the citation and the note: median 87 chars, mean 577, max 5802
firings with >= 1 intervening <ls> citation: 135 of 184 firing sites
firings with gap < 25 chars and no intervening citation (the closest calls): 22
```

Of those 22 closest calls, about 8 look like genuine notes my v1 rule refuses — 5 of the
shape `</ls>. <ab>v. l.</ab> für {#X#}` (`24,20 parj`, `21,22 pas`, `26,106 bus`,
`20,13 śal`, `15,36 śel`) and 3 parenthesised-immediately-after
(`21,21 as (v. l. aṣ)`, `27,25 ah (v. l. aḍ)`, `26,50 pat`) — the same parenthesis ambiguity
`_vl_governs`'s own docstring declares residual on the MW side. Under v3, which fixes the first
group, the count of line-scoped firings without a governing note is **166 of 331 (50.2%)**.
The honest sentence is: *the line-scoped detector attaches the note to the wrong citation in at
least half of its firings*, which supports the argument as forcefully as 183 did without
overclaiming.

**Is this the MW defect left uncorrected? Yes, and the git history says so.** Two commits fixed
exactly this on the MW side — `cc1c75c6 fix(dhatup): clause-scope the v.l. guard — the note's
side of the citation is the rule` and `4d6f285c fix(dhatup): count parenthesis depth in the
v.l. clause test — 32,130 shipped a root both dictionaries disown`. `_vl_governs` carries the
result. `_BOEHTLINGK_VL.search(line, mm.end())` never received it; its comment
("A note earlier in the line governs something else") shows the author reasoning about the
*direction* of the note and not about its *distance*. The Böhtlingk side is the same defect,
one direction rotated, uncorrected. **It refuses nothing today** —
`pw_refused_variant_reading: 0`, `pwg-dotted_refused_variant_reading: 0` — so it is latent, not
shipped; the moment a sibling pass is not order-shadowed it becomes live.

## C8 — CONFIRMED, 10 of 10; none is a genuine disowning

Each quotation is the head line as it stands in `pwg.txt`; offsets are characters into the line.

1. **9,76 laḍ** (note at 90; citation ends 51)
   `{#laq#}¦, {#la/qati#} ({#vilAse#}) <ls>DHĀTUP. 9,76</ls>. {#laqayati#} ({#jihvonmaTane#}, <ab>v. l.</ab> {#jihvonmaTanayoH, jihvonmATanayoH#}) <ls n="DHĀTUP.">19,53</ls>`
   The note is a variant of the **artha** of the *19,53* citation. Agree: misattributed.

2. **17,80 cah** (note at 105; citation ends 70)
   `{#cah#}¦, {#ca/hati#} und {#caha/yati#} {%betrügen%} <ls>DHĀTUP. 17,80</ls>. <ls n="DHĀTUP.">32,82</ls> (<ab>v. l.</ab> für {#cap#}).`
   The note says cah is a variant **for cap at 32,82**. It has nothing to do with 17,80.
   Agree; and note the intervening citation is in the form the builder cannot even read.

3. **19,2 vyath** (note at 69, inside the parenthesis opened at 63; citation ends 41)
   `√{#vyaT#}¦, {#vya/Tate#} <ls>DHĀTUP. 19,2</ls> ({#BayasaMcalanayoH#} <ab>v. l.</ab> {#duHKacalanayoH, duHKaBayacalanayoH#}…)`
   A variant of the **artha** (bhayasaṃcalanayoḥ vs duḥkhacalanayoḥ) inside the artha
   parenthesis, in an article Böhtlingk marks `√`. Agree.

4. **23,10 skand** (note at 434; citation ends 44)
   `√{#skand#}¦, {#ska/ndati#} <ls>DHĀTUP. 23,10</ls> ({#gatiSozaRayoH#}).`
   390 characters and several citations away. The winner, `śoṣaṇa`, is literally half of
   skand's own artha printed beside the citation. Agree.

5. **23,39 spardhā** (note at 1431; citation ends 329)
   the note is `<ls>Spr. (II) 2391</ls>, <ab>v. l.</ab> {#sparDAM vi-DA#}` — a variant reading in
   a *Subhāṣita* quotation. Agree: misattributed. **Separate observation, worth recording:** the
   shipped PWG verdict `23,39 → spardhā` is wrong on Böhtlingk's own words —
   `= {#sAmya#} und {#kramasamunnati#} <ls>MED.</ls> als <ab>Bed.</ab> von {#hvA#} und {#A — hvA#} <ls>DHĀTUP. 23,39</ls>`
   says spardhā is a *meaning of* hvā at 23,39. So the clause rule "wrongly rescues" an
   attribution that is independently bad — for nominal-vs-verbal reasons, not v.l. reasons.
   No harm reaches the artifact: spardhā has no Palsule row, so 23,39 ships as `hve` from MW.

6. **23,40 vad** (note at 127; citation ends 52)
   `√{#vad#}¦, {#va/dati#} und {#˚te#} <ls>DHĀTUP. 23,40</ls> ({#vyaktAyAM vAci#}). <ls n="DHĀTUP.">34,34</ls> ({#saMdeSavacane#}, <ab>v. l.</ab> {#saMdeSane, BAzaRe#})`
   The note is the artha variant of **34,34**. The winner `vyakta` is taken from vad's own
   artha `vyaktāyāṃ vāci`. Agree.

7. **28,1 tud** (note at **1973**; citation ends 64; the line is 2009 characters)
   `<hom>1.</hom> {#tud#}¦, {#tuda/ti#} und {#˚te#} <ls>DHĀTUP. 28,1</ls>; {#tudatI/#} …`
   The note is at the far end of a 2 kB article. The winner `vyathana` is a body-line action
   noun, "das Bereiten eines Schmerzes". Agree — and this is the reattribution that deletes a
   shipped row for the first root of the tudādi gaṇa.

8. **28,120 prach** (note at 2242; citation ends 43; line 5691 characters)
   `√{#praC#}¦, {#pfcCa/ti#} <ls>DHĀTUP. 28,120</ls>. <ls>P. 6,1,16</ls>; …`
   Winner `jñīpsā` `<lex>f.</lex>` "Erkundigung, das Fragen". Agree.

9. **31,1 krī** (note at 1958; citation ends 91; line 2361 characters)
   `<hom>1.</hom> {#krI#}¦, {#krIRA/ti#} und {#krIRI/te#} {%kaufen, erkaufen%} <ls>DHĀTUP. 31,1</ls>.`
   Winner `vinimaya` `<lex>m.</lex>` from a body line, cited there as `{#dravya˚#}`. Agree.

10. **31,41 grath** (notes at 268 and 310; citation ends 64)
    `<hom>1.</hom> √{#graT#}¦, {#granT, graTnA/ti#} <ls>DHĀTUP. 31,41</ls>. … {#gra/Tati, ˚te#} <ls n="DHĀTUP. 34,">19</ls>, <ab>v. l.</ab> <ls n="DHĀTUP.">2,35</ls>, <ab>v. l.</ab>`
    Both notes belong to the 34,19 and 2,35 citations. Winner `saṃdarbha` `<lex>m.</lex>`
    "das Winden". Agree.

**None of the 10 is a genuine disowning that the clause rule wrongly rescues.** The only case
where the *target* is arguably right is 23,39, and it is right for a reason unrelated to `v. l.`

## C9 — CONFIRMED with amendments

- **32,68 cal → bal — justified, unambiguously.**
  `<hom>3.</hom> √{#cal#}¦, {#cAla/yati#} {%ernähren%} <ls>DHĀTUP. 32,68</ls>, <ab>v. l.</ab> für {#bal#}.`
  and bal's own article: `{#bAla/yati#} {%ernähren%} ({#BftO#}) <ls n="DHĀTUP. 32,">68</ls>.`
  Böhtlingk disowns the headword and names the winner in the same clause.
- **33,55 laś → las — justified, unambiguously.**
  `{#laS#}¦, {#lASa/yati#} ({#Silpayoge#}) <ls>DHĀTUP. 33,55</ls>, <ab>v. l.</ab> für {#las#}.`
  and las: `<ab>caus.</ab> {#lAsa/yati#} ({#Silpayoge#}, <ab>v. l.</ab> {#Silpopayoge#}) <ls>DHĀTUP. 33,55</ls>.` Same artha, same coordinate.
- **35,11 sur → svar — justified.**
  `{#surayati (Akzepe)#} <ls>DHĀTUP. 35,11</ls>, <ab>v. l.</ab>` against
  `<ab>caus.</ab> {#svarayati#} <ls>DHĀTUP. 35,11</ls> ({#Akzepe#})` — same artha `ākṣepe`.
- **15,33 vehl → vell — justified.**
  `{#vehl#}¦, {#vehlati#} ({#calane#}) <ls>DHĀTUP. 15,33</ls>, <ab>v. l.</ab>` (bare trailing
  disowning) against a plain `{#vell#}¦, {#ve/llati#} ({#calane#}) <ls>DHĀTUP. 15,33</ls>.`
- **33,5 kuṭumbay → tantray — justified** (C9 does not rate it; I do).
  `!√{#kuwumbay#}¦ (von {#kuwumba#}), {#kuwumba/yate#} {%eine Familie unterhalten%} <ls>DHĀTUP. 33,5</ls>, <ab>v. l.</ab>`
  against tantray's `<ab>med.</ab> {%die Familie unterhalten%} <ls>DHĀTUP. 33,5</ls>` — identical
  gloss, and tantray's head line carries `√`. No shipped row either way.
- **32,30 lañj → tuj — I rate this stronger than "justified with reservation".** The reservation
  is real on the note's side: `<ls>DHĀTUP. 32,30</ls>, <ab>v. l.</ab> ({#BAzArTa#}, <ab>v. l.</ab> {#BAsArTa#}) <ls n="DHĀTUP.">33,111</ls>`
  could be read as opening the 33,111 group. But the *target* is independently strong: tuj's
  article gives `{#tuYja/yati#} und {#toja/yati#} = {#hiMsA, bala, AdAna#} oder {#dAna, niketana#} <ls>DHĀTUP. 32,30</ls>`,
  i.e. the same five-member artha set that lañj's own citation carries
  (`hiMsAbalAdAnaniketanezu`), in a `√`-marked root article. Verbal claimant, same artha,
  same coordinate.
- **17,13 tvakṣ → tvacana — agreed NOT justified.**
  `{#tvacana#}¦ (von {#tvacay#}) <lex>n.</lex> {%das Umlegen eines Felles%} <ls>DHĀTUP. 17,13</ls>.`
  is an action noun; tvakṣ's own line even points at it: `(nicht {%die Haut abziehen%}; <ab>vgl.</ab> {#tvacana, tvacay#})`.
  The root there is `tvacay`, not `tvacana`. **Amendment:** the artifact never ships the noun —
  tvacana has no Palsule row, so the real build hands 17,13 to `takṣ` via `mw-respell`. The row
  still changes (`tvakṣ` → `takṣ`), so the flip is real; the *noun* is not what ships.
- **32,119 mlakṣ → mlecchana — agreed NOT justified, and the reason is sharper than stated.**
  `{#mlakz#}¦, {#mlakza/yati (Cedane)#} <ls>DHĀTUP. 32,119</ls>, <ab>v. l.</ab>` is a genuine
  bare disowning. But the article that actually claims 32,119 verbally is `mrakṣ`:
  `<div n="p">— <ab>caus.</ab> {#mrakza/yati#} und {#mfkza/yati#} <ls>DHĀTUP. 32,119</ls> ({#mrakzaRe#} <ab>d. i.</ab> {#snehane#}; auch {#mlecCane#} und {#maMGAte#})`
  — Böhtlingk names `mlecchane` there as one of the *arthas*. The pipeline picks the noun over
  two verbal body claimants purely because the noun's citation happens to be on a head line.
  That is the pad/3,1 shape exactly. **Amendment:** the real build ships `mrakṣ` via
  `mw-respell`, i.e. the right root, by accident of Palsule membership.

**Net:** 6 of the 8 clause survivors are justified from the source, 2 are not — and both
failures are failures of the *head-line/`<lex>` ordering*, not of the variant-reading note.

## C10 — CONFIRMED, one magnitude wrong, and worse than claimed

`vell` (15,33): citation at offset 37–54, `<lex` at offset **1202** on a 1290-character line,
i.e. **1148 characters after** the citation — not "~2 kB". What sits there is a later sense of
the vell article:
`… <ls>RĀJA-TAR. 8,2373</ls>. <lex>n.</lex> = {#gamana#} <ls>MED.</ls> {%das Wälzen eines Pferdes%}`.
`vell`'s head line is a root article (`{#vell#}¦, {#ve/llati#} ({#calane#})`); the builder flags
it nominal on the strength of a tag 1.1 kB downstream. Meanwhile `tvacana` (`<lex` at 30, cit at
73), `mlecchana` (29 vs 92), `parikalkana` (17 vs 48), `saṃcalana` (26 vs 62), `jñīpsā`
(79 vs 121), `saṃdarbha` (55 vs 213) all carry the tag **before** the citation, where a real
part-of-speech tag stands. Confirmed as claimed.

**Generalised, this is bigger than the two examples.** Over the whole corpus, of the
**128** head-line (coordinate, root) pairs the builder flags nominal, **73 (57%) have no `<lex>`
anywhere before the citation** — the flag is a line-scope artifact in the majority of its
firings. `lal` (9,76) is a second instance: `√{#lal#}¦` with `<lex>adj.</lex>` 819 characters
later, on `{#lalita#}`.

I measured the fix end to end (`cf_lex.json`, `<lex>` required to precede the citation):
rows 1465 → **1463**, `coords_conflicted` 271 → 277, two attributions corrected
(`15,32 kvel → kṣvel`, `32,12 naḍ → naṭ`), two rows dropped (`15,33 vehl`, `19,13 klav`).
It costs 0.1 coverage points and it removes a class of wrong reason from the resolution.

## C11 — the decision is CONFIRMED; the reason set needs correcting

**Does the evidence support DECLINE CONFIRMED? Yes**, and more strongly than the published
argument does — but not for all of the published reasons.

What genuinely supports the decline:

1. **The detector is wrong at least half the times it fires** (166 of 331 by my best clause
   rule; 183 by the implementer's). A gain measured through it is not a measurement of
   Böhtlingk's note. This is the strongest argument and it is C7's, confirmed.
2. **The published yield is arithmetic, not a build.** The real narrow build is
   **1493/1751 (85.3%)**, not 1496/1751 (85.4%), because the reattributions delete three
   shipped rows including `28,1 tud`.
3. **The disturbance is 21 root changes, not 17 flips**, plus 46 provenance changes — the
   funnel hides 13 attributions inside its "already filled" bucket.
4. **Two of the eight clause-surviving flips are still wrong** (17,13, 32,119), and both fail
   for the `<lex>`/head-line ordering reason, which is unfixed. Applying the v.l. tie-break
   before fixing that ordering ships the pad/3,1 shape again.

What does **not** support it, and should be struck from the record:

- **"All 18 reattributions hand the coordinate to a nominal claimant" is false.** 8 of the 18
  targets are root articles, 6 with Böhtlingk's own `√`. The 8+10 split is mechanically correct
  and its *interpretation* is not. This matters: the decline is currently argued on a premise
  that a future reader will re-derive and find wrong — the same failure mode as the
  "12 of the 18" correction that H4386 already had to publish.
- **The parenthetical examples in ABBREVIATIONS_RU** (`19,2 vyath → saṃcalana`,
  `28,1 tud → vyathana`, `31,1 krī → vinimaya`, `32,119 mlakṣ → mlecchana`) are picked from the
  *ten the clause test eliminates*. They are evidence that the **detector** is broken, not that
  the **guard** is wrong. Quoting them as the reason to decline the guard is quoting the wrong
  defect.

**Would I instead APPLY something? Yes — three things, none of them the re-baseline.**

1. **Clause-scope `_BOEHTLINGK_VL`** (a ~15-line change, mirroring `_vl_governs`). It changes
   **no shipped row** today (both sibling variant counters are 0) and it closes the defect
   before a future sibling pass makes it live. This is a pure correctness fix with a
   zero-diff artifact — the easiest thing in this whole handoff to land.
2. **Scope the `<lex>` nominal test to markup preceding the citation.** 57% of its current
   firings are artifacts; the fix costs 2 rows (1465 → 1463) and fixes 2 attributions. It must
   be published as its own number, and it is a prerequisite to *any* future verbal-beats-nominal
   ordering — which is the question H4432 was asked to answer, and the honest answer is
   "the ordering cannot be evaluated while the nominal flag is 57% noise".
3. **Decide the citation-form gap** (below) before any coverage figure is quoted again.

**Evidence I think is missing from the implementer's case:** the end-to-end build. Every
number in H4386's residue paragraph is a scanner number; not one of them was produced by
running the builder. Three of the four corrections in this report (1493 not 1496, 21 not 17,
the three deleted rows) fall straight out of building it once. A counterfactual that is
argued instead of built is the exact defect FINDINGS §637 was written about.

---

## Two defects I found that nobody claimed

**Defect 1 — the head/body discriminator sees one physical line.** `at_head` is true for exactly
the line after `<L>`, so every later sense of a multi-sense root article is "body". That is why
`bal`, `las`, `svar`, `tuj` count as "no head-line citation" while being verbal claimants of
their own coordinate in their own root article. It is the same line-scope confusion as C7 and
C10, in a third place.

**Defect 2 — the PWG reader cannot see one of the three citation forms, and it moves the
denominator.** PWG writes `DHĀTUP.` citations three ways. The builder reads two:

```python
_DHATUP   = r'<ls\b[^>]*>\s*DH[ĀA]TUP\.\s*(\d+)\s*,\s*(\d+)'          # <ls>DHĀTUP. 4,13</ls>
_DHATUP_N = r'<ls\b[^>]*\bn\s*=\s*"DH[ĀA]TUP\.\s*(\d+)\s*,\s*"[^>]*>\s*(\d+)'   # <ls n="DHĀTUP. 26,">91</ls>
```

The third, `<ls n="DHĀTUP.">4,13</ls>`, occurs **318 times** and matches neither. Examples:

```
… {%ehren%} <ls>DHĀTUP. 33,58</ls>. <ls n="DHĀTUP.">34,24</ls>
… nach <ls>DHĀTUP. 32,118</ls> bedeutet {#il, ela/yati#} {%werfen%}; nach <ls n="DHĀTUP.">28,65</ls>
```

The MW reader in the same file handles the exact analogue — `_MW_DHATUP_N_FULL` for
`<ls n="Dhātup.">xxxiv, 40</ls>` — so this is an asymmetry between the two readers, not a
policy. Nothing in the builder, the verifier, ABBREVIATIONS_RU or FINDINGS records it as
deliberate; FINDINGS itself quotes `<ls n="DHĀTUP.">15,89</ls>` in its own prose.

Measured end to end (`cf_formc.json`): `coords_cited` **1751 → 1892 (+141, +8.1%)**,
rows 1465 → 1576, 131 added, 20 removed, 16 attributions changed
(`19,69 am→cam`, `27,16 rādh→sādh`, `32,7 lal→laḍ`, `32,105 gaj→garj`, `35,80 chid→chad`, …),
`coords_conflicted` 271 → 339, and the published rate **83.7% → 83.3%**.

That is a far larger effect on the number this handoff is arguing about than the ±31 the
handoff is arguing over, and it moves it in the opposite direction. **I am not asserting the
form should be admitted** — some of those 141 may be renumbering across editions, exactly the
`33,67`/`33,88` shape H4349 found — but the denominator 1751, and therefore 83.7%, is currently
a property of a regex set and not a property of PWG, and that should be said out loud wherever
83.7% is published.

## What I could not verify

- **The MW pass.** I did not re-implement `read_mw_coords` / `_mw_pass` from mw.txt
  independently; for MW-derived rows I used the shipped artifact and my patched **copy** of the
  builder. So "43 of the 74 the MW pass already fills" is confirmed against the artifact and
  the build, not against an independent reading of mw.txt. If MW's reader has its own defect,
  it is inside all my counterfactual builds too.
- **Palsule against the printed book.** I read the XLS (8170 artha rows, 2571 distinct
  normalised roots) but have no way to check the spreadsheet against Palsule's printed text, so
  every "has a Palsule row / has none" statement inherits the XLS's own accuracy.
- **Whether each attribution is right against the dhātupāṭha itself.** I adjudicated against
  Böhtlingk's and Monier-Williams's prose only. I did not consult Westergaard or a dhātupāṭha
  edition, so "32,68 belongs to bal" means "Böhtlingk says so", not "the dhātupāṭha says so".
- **Whether the 141 form-C coordinates are real.** I measured their effect; I did not
  adjudicate a single one of them. They may include renumbering artifacts.
- **The 183 (or 166) divergent firings one by one.** I read 10 of them in full (C8), sampled 12
  more at random, and shape-classified the 22 closest calls. The remaining ~140 are supported by
  the gap statistics, not by individual reading.
- **The handoff's own deliverable.** As of this run,
  `git status --porcelain` in SanskritLexicography is empty and `ABBREVIATIONS_RU.md` does not
  yet contain the 17-row adjudication table the acceptance line requires. The artifact being
  byte-identical is confirmed; the written adjudication is not yet on disk.

_Dr. Mārcis Gasūns_
