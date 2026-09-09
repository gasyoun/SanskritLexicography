# H4438 — independent adversarial verifier report

_Created: 09-09-2026 · Last updated: 09-09-2026_

Verifier: Opus 5 (`claude-opus-5`), no access to the implementer's session. Every figure below was
re-derived from the corpora with regexes and rules I wrote before reading the builder, then compared
against the builder's own. Every coverage figure was BUILT to a scratch `--out` and diffed key by key
— rows added, rows DELETED, roots changed, source changed as four separate numbers, never summed.
Nothing in the repository was modified; six builds were written to a scratch directory only.

Corpora: `/Users/mac/Documents/GitHub/csl-orig/v02/pwg/pwg.txt`,
`/Users/mac/Documents/GitHub/csl-orig/v02/mw/mw.txt`,
`/Users/mac/Documents/GitHub/csl-orig/v02/pw/pw.txt`.
Artifact under test:
[src/data/dhatup_palsule.json](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/data/dhatup_palsule.json),
built by
[src/build_dhatup_palsule.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_dhatup_palsule.py).

## C0 — reproducibility precondition

A fresh build of the shipped builder against the committed artifact:

```
=== committed src/data/dhatup_palsule.json -> fresh H4438 build ===
  rows 1573 -> 1573
  ADDED   : 0
  DELETED : 0
  ROOTS   : 0
  SOURCE-ONLY: 0
```

**CONFIRMED.** The committed JSON is exactly what the committed builder produces. Everything below is
therefore a statement about the shipped artifact, not about a stale file.

## C1 — the head-line population and the v. l. clause rule (claim A)

**As published.** 1999 head-line (coordinate, root) claimant pairs; 331 carry an `<ab>v. l.</ab>`
note later on the same line; 165 of those govern the citation under the clause rule; 166 do not; 148
under a strict reading that admits no `.` at parenthesis depth 0.

**What I derived.** I wrote my own entry splitter and my own three citation regexes. My first pass
gave **1998**, not 1999. The whole gap is one entry: `<L>20076 k1=kzaj`, whose head line carries no
`¦` separator (a corpus defect) and carries both a form-B citation `DHĀTUP. 19,7` and a form-C
citation `<ls n="DHĀTUP.">32,78</ls>`. Under "head line = the first content line of the entry" — which
is what `_scan_coords` and `read_pwg_coords` actually implement (`at_head = True` after `<L>`,
`at_head = False` after one line) — I get exactly 1999, and 281 form-C occurrences on head lines.
Applying the builder's `_boehtlingk_vl_governs` over my own extraction:

```
head-line (coord,root) pairs      : 1999
with a later v.l. on same line    : 331
GOVERN (builder rule)             : 165
DO NOT govern                     : 166
GOVERN (strict, no depth-0 dot)   : 148
```

**CONFIRMED** — all five numbers reproduce exactly. My own independently written loose/strict rules
landed at 161/151, i.e. the same order of magnitude and the same structure; the residual is knob
detail, adjudicated in C2.

## C2 — the "punctuation only" widening from 148 to 165 (REFUTED as reasoning)

**As published**, in `_boehtlingk_vl_governs`: "either no `.` at parenthesis depth zero, or — and this
is the one shape the strict reading gets wrong — nothing but punctuation between the two.
`</ls>. <ab>v. l.</ab> für {#X#}` is Böhtlingk's ordinary trailing disowning and it is genuine:
`24,20 parj`, `21,22 pas`, `26,106 bus`, `20,13 śal`, `15,36 śel` all have that shape."

**What I derived.** I extracted all 17 pairs the loose rule admits and the strict rule refuses and
read every one of their head lines in `pwg.txt`. The claim that the intervening text is "nothing but
punctuation" is only true because `_blank_markup` blanks `{#…#}` and `{%…%}` spans to spaces before
`_WORDLIKE` is applied. In 12 of the 17 the intervening text is a whole new lemma and gloss, in three
of them introduced by an em-dash, which the rule does not treat as a clause break at all:

| pair | text between citation and note | my reading |
|---|---|---|
| 15,44 `Kow` | `</ls>. — {#Kowa/yati#} {%werfen%} ` | note is about `khoṭayati` at the NEXT citation `35,23` |
| 9,21 `taw` | `</ls>. — {#taw, tAwa/yati#} ` | note is about `tāṭayati` at `32,43` |
| 8,29 `paRq` | `</ls>. {#paRqa/yati#} {%zusammenthun%}, ` | note is about `paṇḍayati` at `32,130` |
| 20,17 `paT` | `</ls>. {#pATa/yati#} {%hinwerfen%}, ` | note is about `pāṭhayati` at `32,20` |
| 17,55 `parz` | `</ls>. {#parz, pa/rzate#} ` | note is about `parṣate` at `16,12` |
| 28,43 `puR` | `</ls>. {#poRa/yati#} {%aufhäufen%}, ` | note is about `poṇayati` at `32,93` |
| 4,15 `maNk` | `</ls>. {%gehen, sich bewegen%} ` | note is about `mamaṅkire` at `BHAṬṬ. 14,10` |
| 20,13 `Sal` | `</ls>. ` | note is about `śval` at the NEXT citation `15,42` |

`20,13 śal` is one of the five examples the docstring names as proof that the shape is genuine. The
line reads
`{#Sa/lati (gatO)#} <ls>DHĀTUP. 20,13</ls>. <ab>v. l.</ab> für {#Sval (ASugamane)#} <ls n="DHĀTUP.">15,42</ls>.`
— "śal is a variant reading for śval **at 15,42**". `20,13` is śal's own coordinate. This is the same
semantics as the `17,80 cah` case the docstring's clause (a) was written to catch; the only difference
is that the note stands before the second citation instead of after it, so the `_LS_OPEN` guard never
fires. Two more of the five named examples, `24,20 parj` and `21,22 pas`, reach the right verdict for
the wrong reason: in both, the note that actually disowns the headword stands BEFORE the citation, and
the note the rule matched belongs to the following coordinate (`pij 18`, `33,45`).

**REFUTED.** The counts in C1 are right; the published justification for the 148→165 widening is not.
Of the 17 pairs it adds I judge 8 to be outright false positives, 3 right-for-the-wrong-reason, 5 a
different shape entirely (`{#yunT#} <ab>v. l.</ab>` names the OTHER form as the variant, not the
headword), and 1 (`26,106 bus`) a clean trailing disowning. The docstring's own claim that the knob
"changes no downstream verdict" is separately true — see C3 — so nothing shipped is wrong because of
this; what is wrong is the evidence offered for the knob.

## C3 — the clause test alone is a zero diff (claim B)

**As published.** Applying the clause test alone to the shipped builder is a zero diff.

**What I derived.** I copied the builder, reverted the one call site to the pre-H4438 behaviour
(`_BOEHTLINGK_VL.search(line, mm.end())` — "a note anywhere later on this line"), and built:

```
=== H4438 shipped -> CF: clause test reverted to whole-line ===
  rows 1573 -> 1573
  ADDED   : 0
  DELETED : 0
  ROOTS   : 0
  SOURCE-ONLY: 0
  stat coords_cited            1890 -> 1890
  stat match_rate              83.2 -> 83.2
  stat cross_agreement_rate    80.1 -> 80.1
```

**CONFIRMED.** Zero diff on all four numbers and on every published statistic.

**But the reason is not the one a reader will infer.** `_boehtlingk_vl_governs` is called from exactly
one place, `_scan_coords` (line 1032), which serves only the SIBLING sources — `read_pw_coords` and
`read_pwg_dotted_coords`. PWG's own head-line pass is `read_pwg_coords` (line 380), whose per-coord
slot list is `[head, body, head_nominal]` with no variant-reading slot and no call to the test at all.
So the entire measurement in C1 — 1999 pairs, 331 notes, 165/166/148 — characterises a population on
which the test never runs. That is a real gap between where the evidence was gathered and where the
code acts, and it is not stated anywhere in the file. It has a concrete consequence: see C9.

## C4 — the nominal head-line test scope (claim C)

**As published.** 128 head-line (coordinate, root) pairs are flagged nominal when `<lex>` is searched
over the whole line; 73 of them have no `<lex>` before the citation.

**What I derived**, over my own 1999-pair extraction:

```
[A+B] head-line pairs=1999  nominal WHOLE-LINE=128  nominal BEFORE-cite=55  whole-but-not-before=73
      radical WHOLE-LINE=1039  radical BEFORE-cite=1039  lost=0
      distance lex-after-cite: median=1238 max=8320
      vell (15,33) gap=1165   lal (9,76) gap=819
```

**CONFIRMED**, exactly. The sibling claim in `_head_radical` — "zero head-line claimant pairs lose the
marker" when `√` is scoped the same way — is also confirmed (1039 → 1039). The docstring's "1148
characters after" for `vell` is the distance from the end of the citation match; my 1165 is from its
start; the same 17-character citation prefix reconciles them.

The scoping is also justified on the outcome, not only on the reading. Reverting `_head_nominal` and
`_head_radical` to whole-line:

```
=== H4438 shipped -> CF: <lex>/√ scope reverted to whole-line ===
  rows 1573 -> 1575
  ADDED   : 3
  DELETED : 1
  ROOTS   : 4
  SOURCE-ONLY: 2
  stat match_rate              83.2 -> 83.3
  stat cross_agreement_rate    80.1 -> 79.9
```

Coverage is a hair higher unscoped and agreement with MW is lower — which is the trade the change was
supposed to make.

## C5 — the third citation form (claim D)

**As published.** 320 occurrences, 270 distinct coordinates, 141 cited by no other form, 281 of the
320 on the citing article's own head line, 93 of the 141 independently cited by MW.

**What I derived.** A blind census of every `<ls …>DHĀTUP …</ls>` shape in `pwg.txt` gives three
families: `<ls>DHĀTUP. N,N</ls>` (2230), `<ls n="DHĀTUP. N,">N</ls>` (84), `<ls n="DHĀTUP.">N,N</ls>`
(318, plus two with a letter suffix that the builder's regex also reads = 320).

```
form C total occurrences: 320 ; distinct coords: 270
form C distinct coords: 270 ; not cited by A or B: 141
form C occurrences on their own article's head line: 281 of 320
of the 141 form-C-only coords, MW independently cites 93
```

**CONFIRMED** — all five numbers. The 93 was derived from my own three MW roman-numeral regexes over
`mw.txt`, not from the builder's.

**One definitional caveat on `coords_cited` 1751 → 1890.** The raw union of the three forms is 1892,
not 1890; the shipped stat is post-screen, because the ceiling screen runs `del coords[coord]` on the
two refusals before `len(coords)` is taken. The source says so explicitly ("a refused coordinate is
not counted in the denominator either"), so this is documented, not hidden — but 1751 and 1890 are
counted under slightly different rules and the honest unscreened pair is 1751 → 1892.

## C6 — the ceiling screen (claim E)

**As published.** Exactly 3 of the 141 exceed the highest serial their gaṇa is attested to by the
other two citation forms: 6,113 (gaṇa 6 tops out at 25), 27,71 (gaṇa 27 tops out at 33), 32,133
(gaṇa 32 tops out at 132). MW names only 32,133, so 6,113 and 27,71 are refused and 32,133 ships.

**What I derived**, from my own ceilings over forms A+B and my own MW reader:

```
form-C-only coords: 141
above their gaṇa's spelled-out ceiling: 3
   6,113   ceiling(gaṇa 6) = 25
   27,71   ceiling(gaṇa 27) = 33
   32,133  ceiling(gaṇa 32) = 132
   MW cites 6,113 ? 0    27,71 ? 0    32,133 ? 1
```

The shipped `_refused_form_c_out_of_space` contains exactly `6,113` and `27,71`; `32,133` is in the
table as `stūp`. **CONFIRMED**, exactly.

**Reasoning objection.** `coordinate_ceilings` justifies excluding form C from the ceiling with "the
third citation form carries its source in an ATTRIBUTE, and an attribute is exactly what an encoder
can carry over", then immediately offers `27,71` as the example of a carried-over **gaṇa**. Those are
two different mechanisms: in `<ls n="DHĀTUP.">27,71</ls>` the attribute carries only the word
`DHĀTUP.`; the digits `27,71` are visible printed text and a carried gaṇa there is Böhtlingk's or the
typesetter's error, not attribute inheritance, and could occur in forms A and B just as easily. The
honest statement of the design is the circular-but-defensible one: a ceiling built from all three
forms lets each of the three suspect coordinates certify itself (gaṇa 6 → 113, gaṇa 27 → 71, gaṇa 32 →
133), so the screen would catch nothing; excluding the newly admitted form is what makes any screen
possible. That is a legitimate choice; the attribute-inheritance argument for it is not the reason it
works.

## C7 — the adjudication of 6,113 / 27,71 / 32,133 (claim F)

I read all six primary lines.

### 27,71 rādh — CONFIRMED, and on better evidence than the one published

PWG:
`√{#rAD#}¦ … {#rADno/ti#} ({#saMsidDO#}) <ls>DHĀTUP. 27,16</ls>. {#rA/Dyati#} ({#vfdDO#} …) <ls n="DHĀTUP.">27,71</ls>`

MW, `rādh`:
`<ab>cl.</ab> 5. 4. <ab>P.</ab> (<ls>Dhātup. xxvii, 16</ls>; <ls n="Dhātup.">xxvi, 71</ls>) <s>rADno/ti</s>, <s>rADyati</s>`

MW pairs class 5 with xxvii,16 (`rādhnoti`) and class 4 with **xxvi**,71 (`rādhyati`), in that order.
That alone settles it. There is a second, independent confirmation the implementer did not cite:
PWG's own `sādh` article, the parallel root, reads
`{#sA/Dyati (saMsidDO)#} <ls>DHĀTUP. 26,71</ls>. {#sAGno/ti#} … <ls n="DHĀTUP.">27,16</ls>`, and MW's
`sādh` says "accord. to Dhātup. **xxvi, 71** and xxvii, 16, cl. 4. sādhyati, cl. 5. sādhnoti". So
26,71 is the divādi (-yati) slot and 27,16 the svādi (-noti) slot for BOTH roots, in BOTH dictionaries.
PWG's `27,71` is `26,71` with the gaṇa of the previous clause. Refusing it rather than silently
correcting it to 26,71 (already held by `sādh`) is the right conservative call.

### 32,133 stūp — CONFIRMED, decisively

PWG: `{#stUp#}¦, {#stU/pyati#} <ls>DHĀTUP. 26,127</ls> und {#stUpa/yati#} <ls n="DHĀTUP.">32,133</ls>`.
MW, `stūp`: `<ls>Dhātup. xxvi, 127</ls>; <ls n="Dhātup.">xxxii, 133</ls>` — the identical pair — plus a
machine field `<info westergaard="ztUpa,26.127,04.xxxx;ztUpa,32.133,10.0119"/>` that maps 32.133 to
Westergaard class 10 explicitly. Gaṇa 32 is the curādi region and `stūpayati` is a class-10 stem, so
the coordinate is internally consistent as well. Shipping it is right.

### 6,113 kṣip — the reading is right, but 17,43 is a real inconsistency the implementer glossed over

PWG:
`{#kzi/pyati#} (nur im <ls>BHARTṚ.</ls> <ab>z. B.</ab> <ls n="DHĀTUP.">6,113</ls>. <ls n="DHĀTUP.">17,43</ls> nachzuweisen) <ls n="DHĀTUP.">26,14</ls>;`

I agree with the reading. The German is "kṣipyati is attestable only in Bhartṛhari, e.g. 6,113. 17,43";
`<ls>BHARTṚ.</ls>` and `<ab>z. B.</ab>` immediately precede the two numbers, and PWG's normal Bhartṛhari
citation form is exactly `BHARTṚ. N,N` (1186 occurrences). The class evidence corroborates `26,14`
independently: gaṇa 28 is the tudādi region and PWG gives `kṣipati` 28,5; gaṇa 26 is the divādi region
and `kṣipyati` is a divādi present, so 26,14 is where it belongs. And 113 exceeds not only PWG's
attested ceiling for gaṇa 6 (25) but MW's as well (77).

**The 17,43 inconsistency is real.** By the implementer's own reading, 17,43 in this line is equally a
Bhartṛhari locus, and it is not refused — gaṇa 17's ceiling is 89 in PWG and 85 in MW, so it is
comfortably inside the attested space and the ceiling screen cannot see it. The implementer's summary
does not name this asymmetry.

**But it is harmless here, and the ceiling screen is not what saved it.** The shipped row is

```
17,43 root=riṣ source=mw  pwg_claimants=["caz","kzip","riz"]
```

Admitting form C gave `17,43` a third PWG claimant, `kṣip`; PWG was already unable to resolve it
(`caṣ` and `riṣ` both claim it in both dictionaries — MW gives `Dhātup. xvii, 43` to `caṣ` and to
`1. riṣ`), so the multi-claimant filter refused PWG's answer and MW filled the row with `riṣ`. The
spurious kṣip claim changed nothing. The safety here comes from the multi-claimant filter and MW, not
from the ceiling screen, and a reader of the published adjudication would not know that.

## C8 — the shipped coverage figures (claim G)

**As published.** 1573 rows; 131 added, 23 DELETED, 17 roots changed, 26 source-changed-only, as four
separate numbers; coords_cited 1751→1890; match_rate 83.7→83.2; cross_agreement_rate 77.7→80.1;
mw_only_coords 124→33.

**What I derived**, building `git show origin/master:…/build_dhatup_palsule.py` and the shipped builder
to two scratch outputs and diffing key by key:

```
=== base(origin/master) -> H4438 shipped ===
  rows 1465 -> 1573
  ADDED   : 131
  DELETED : 23
  ROOTS   : 17
  SOURCE-ONLY: 26
  stat coords_cited            1751 -> 1890
  stat match_rate              83.7 -> 83.2
  stat cross_agreement_rate    77.7 -> 80.1
  stat mw_only_coords          124 -> 33
```

**CONFIRMED**, every number, and the four are genuinely four (131 + 23 + 17 + 26 is not any published
quantity). Dropping form C alone from the shipped builder gives 1464 rows and returns coords_cited to
1751 and mw_only_coords to 124, so form C is the dominant contributor and the nominal rescoping
accounts for the remainder.

I also checked the 17 root flips against MW independently, using my own MW prose regexes and MW's
`westergaard=` machine field. MW's own claimant for the coordinate matches the NEW root in 12 of them
— 15,32 kṣvel; 19,69 cam; 27,16 sādh; 32,104 juḍ; 32,114 tumb; 32,12 naṭ; 32,131 ruṭ; 32,27 luṇṭ;
32,45 kuṇḍ; 32,7 laḍ; 33,16 tūṇ; 33,28 kūṭ — which independently reproduces the builder's "MW confirms
the NEW root 12 times to 2". The two that do not go the new way are `32,105` (MW's `gaja` article
claims xxxii,105 for `gaj`; PWG's `garj` head line claims it in form C and wins on head-over-body) and
`35,80`, on which MW is silent. See C9.

## C9 — the 35,80 chid → chad regression (claim I)

**As published**, this is a known regression.

**REFUTED as harmless; CONFIRMED as a regression, and it is caused by the one change H4438 measured
and did not wire in.** The two PWG lines:

Head line of `1. chad` (form C, newly admitted):
`√{#Cad#}¦, {#CAda/yati#} … <ls>DHĀTUP. 34,27</ls>. <ls n="DHĀTUP.">32,41</ls>, <ab>v. l.</ab> ({#Ca/dati#} nicht zu belegen; ebenso wenig {#Canda/yati#} <ls n="DHĀTUP.">32,41</ls>. {#Cada/yati#} <ls n="DHĀTUP.">35,80</ls>, <ab>v. l.</ab> nur <ls>AIT. BR. 1,30</ls>);`

Body of `chid`:
`— <ab>caus.</ab> {#Cedayati#} 1〉 {%abschneiden, abhauen%} <ls>DHĀTUP. 35,80</ls> ({#Ced#}).`

`chad`'s citation of 35,80 stands inside a parenthesis whose entire content is Böhtlingk saying these
forms are not attestable, and it is followed immediately by `, <ab>v. l.</ab>` — Böhtlingk marking
`chadayati` at 35,80 as a variant reading. `chid`'s citation is an unhedged statement that 35,80 is
`ched`. So `chad` at 35,80 is wrong and the baseline's `chid` was right. MW has no `xxxv, 80` at all,
which is exactly why the MW cross-check did not catch it.

I then asked whether H4438's own new test would have caught it. Running
`_boehtlingk_vl_governs` on that head line:

```
form C 32,41 -> _boehtlingk_vl_governs = True
form C 35,80 -> _boehtlingk_vl_governs = True
form B 34,27 -> _boehtlingk_vl_governs = False
```

**Yes.** The clause test H4438 wrote, measured on PWG's head lines, and then wired only into the
sibling pass, refuses exactly this claim. Wiring it into `read_pwg_coords` as well and rebuilding:

```
=== H4438 shipped -> CF: clause test ALSO wired into PWG's own head-line pass ===
  rows 1573 -> 1596
  ADDED   : 37
  DELETED : 14
  ROOTS   : 16
  SOURCE-ONLY: 43
  stat coords_cited            1890 -> 1874
  stat match_rate              83.2 -> 85.2
  stat cross_agreement_rate    80.1 -> 79.4
  roots changed includes: ('35,80', 'chad', 'chid')
```

It does fix 35,80. It also does damage — `15,36 śel → sel`, `15,6 śucy → cucy`, and the deletion of
`20,13`, `8,29`, `9,21`, `17,55`, `20,17`, `28,43`, `4,15`, `16,18`, precisely the false positives I
catalogued in C2 — and it drops agreement with MW from 80.1 to 79.4. So **declining to wire it in is
defensible on the measured number**, and I would have made the same call. What is missing is that this
was evidently never measured or recorded: nothing in the builder says the test was considered for
PWG's own pass and declined, and the C2 false-positive class is the reason it would have to be.

## C10 — the six sole-nominal drops (claim H)

**As published.** 7,3 taucchya→kuc; 19,54 glepana→mad; 20,27 saṃparcana→kuc; 23,39 spardhā→hvā;
32,109 niśāna→tij; 33,73 avakalkana→bhū.

**What I derived.** `_dropped_sole_nominal_head` in the fresh build contains exactly those six pairs
and no others, and `coords_sole_nominal_head_dropped` is 6. On the one I was asked to read:

`{#sparDA#}¦ (wie eben) <lex>f.</lex> {%Wettlauf%} … = {#sAmya#} und {#kramasamunnati#} <ls>MED.</ls> als <ab>Bed.</ab> von {#hvA#} und {#A — hvA#} <ls>DHĀTUP. 23,39</ls>.`

`spardhā` is a `<lex>f.</lex>` noun article, and the clause containing the citation says in so many
words "as a **meaning of hvā** and ā-hvā". It is quoting the coordinate to define itself. The `hvā`
article confirms from the other side:
`{#hva/yati#} … <ls>DHĀTUP. 23,39</ls> ({#sparDAyAM Sabde ca#})` — with the artha spelled out inline.
The shipped row is `23,39 → hve` with Palsule arthas including `spardhāyām` and `sparāhāyāṁ śabde ca`.
**CONFIRMED**; this is the cleanest case in the whole pass.

## C11 — is admitting form C justified at all? (claim J)

I sampled 20 of the 141 new coordinates with a fixed seed and read every PWG line that cites them.
The dominant shape is exactly what the builder claims: a root article enumerating its class-forms, the
first coordinate spelled out and the rest in form C, standing on the same head line beside it. The
internal consistency is strong enough to be an independent check, because Westergaard's gaṇa bands map
onto the Sanskrit present classes and the form-C coordinates land in the right band every time:

- `si` — `sinoti` at 27,2 (class 5 band) and `sināti` at 31,5 (class 9 band).
- `kū/ku` — `kauti` 24,33 (class 2), `kavate` 22,54 (class 1), `kuvate` 28,108 (class 6), `kūnāti`
  31,10 (class 9). Four forms, four bands, three of them form C.
- `jar/jṝ` — 34,9, `jīryati` 26,22 (class 4), `jṛṇāti` 31,24 (class 9).
- `śraṇ` — `śraṇāti` 19,36, `śrāṇayati` 32,42 (curādi -ayati band).
- `lūṣ`, `pakṣ`, `pac/pañc`, `naṭ`, `tubh`, `ḍip`, `guj`, `dal`, `cīv`, `lūṣ` — same pattern.

Two of the twenty are not shipped, and correctly so: `22,4` stands in a parenthesis inside `1. kar`'s
head line enumerating `kṛ` 30,10 / 22,4 / `kṛv` 15,89, and `26,22` has no resolvable single claimant.
One (`35,37 dhvan`) is a body citation in the root's own article, which is right on the merits.

I found no systematic bad class that the ceiling screen misses. The nearest thing to one is the
variant-reading class: **22 of the 141** carry an `<ab>v. l.</ab>` note somewhere after the form-C
citation on the citing head line, and `35,80` is the member of that class that actually corrupted a
row. That is the residual risk of admitting form C, and it is the same gap as C3/C9, not a new one.

**Admitting form C is justified.** It moves agreement with MW from 77.7 to 80.1 on a nearly 8%
larger coordinate set, cuts `mw_only_coords` from 124 to 33, and the 12-to-2 MW verdict on the
attribution flips is independently reproducible.

## What I refuted

1. **The published justification for the 148 → 165 widening of the clause rule (C2).** The docstring
   says the extra 17 pairs have "nothing but punctuation" between citation and note; in 12 of the 17
   a whole lemma and gloss stand there, blanked to spaces before the test looks. Eight of the 17 are
   demonstrable false positives where the note belongs to a later coordinate on the same line, and
   `20,13 śal`, one of the five examples named as proof the shape is genuine, is one of them. The
   counts 165/166/148 are right; the argument for choosing 165 is not.
2. **The framing of claim B as a property of the clause test (C3).** The zero diff is real, but it is
   guaranteed rather than discovered: `_boehtlingk_vl_governs` is never called on PWG's head lines,
   which is the entire population the 1999/331/165/166/148 measurement describes. The file does not
   say so.
3. **The "attribute is inheritable" argument for excluding form C from the ceiling (C6).** In the
   flagship example `27,71` the gaṇa is visible printed text, not an attribute. The exclusion is
   right; the stated mechanism is not the one at work.
4. **The completeness of the 6,113 adjudication (C7).** The implementer's reading of the kṣip line is
   correct, but `17,43` is the same class of mis-tagged Bhartṛhari locus and is not refused, and the
   published note does not say so. It happens to be harmless only because three PWG claimants collide
   there and MW arbitrates — a fact the adjudication does not mention.
5. **`coords_cited` 1751 → 1890 as a like-for-like pair (C5).** The unscreened union is 1892; 1890 is
   post-refusal. The source documents the choice, the headline number does not carry it.
6. **The 35,80 regression as unavoidable (C9).** H4438's own new clause test refuses the offending
   claim. I built the counterfactual: wiring it into PWG's own pass fixes 35,80 and costs 0.7 points
   of MW agreement plus eight bad deletions. Declining is the right call; not recording that the
   decision was even available is the defect.

Nothing in the shipped artifact was refuted. Every published count reproduced exactly: 1999, 331,
165, 166, 148, 128, 73, 320, 270, 141, 281, 93, 3, the three coordinates and their ceilings, the six
sole-nominal drops, 1465 → 1573, 131 / 23 / 17 / 26, 1751 → 1890, 83.7 → 83.2, 77.7 → 80.1, 124 → 33.

## My own stated limits

1. **I did not consult Westergaard's *Radices Linguae Sanscritae* itself.** Every adjudication of
   "what actually stands at gaṇa g, serial s" is triangulated from PWG, pw and MW plus the class-band
   regularity I observed in the sample. Where all three are Böhtlingk-family or silent — `35,80` is
   exactly that case, MW has no `xxxv, 80` — my verdict rests on reading Böhtlingk's German, not on
   the primary text. A reader with the 1841 edition could overturn C9's direction, though not the
   observation that PWG's two statements conflict.
2. **I did not verify the Palsule XLS ingestion at all** — the artha/pada/page columns, the typo folds,
   `xls_artha_rows`, `xls_distinct_roots`, or whether the arthas attached to a row are the arthas
   Palsule prints for that coordinate rather than for that root name. The 35,80 row's arthas
   (`saṁvaraṇe` etc.) are keyed by root, so they cannot arbitrate a root dispute, and I did not try to
   make them.
3. **I read 20 of the 141 new coordinates, not all 141**, and 17 of 17 loose-only v. l. pairs but not
   all 331. My "8 of 17 are false positives" is a reading of eight German sentences by one verifier;
   two of the five `{#X#} <ab>v. l.</ab>` cases (`punth`/`preṣ`/`śucy`/`śūṣ`/`śel`) I labelled
   "different shape" are genuinely arguable in either direction and I did not resolve them.
4. **I did not adjudicate the 23 deletions or the 26 source-only changes individually.** I confirmed
   the counts and pulled MW's claimants for each of the 23, but I did not read the PWG lines. Some of
   the deletions look right on the MW evidence (`31,10` is `knū`'s coordinate by MW's own
   `westergaard="knUY"` field, and PWG marks it `v. l. für knū`); I did not check the rest.
5. **I did not run the repository's own selftests** (`src/pilot/dhatup_h4349_verify.py`,
   `ls_enrichment_selftest.py`), both of which the working tree modifies. I was scoped away from
   touching them and chose not to run them rather than risk a write; a separate pass should.
6. **I did not verify the pw.txt sibling pass**, which is the one place `_boehtlingk_vl_governs`
   actually acts. My C3 finding says the test does nothing on PWG; I did not measure what it does on
   pw, and the zero diff means it currently changes no shipped row from either source.
7. **My "12 of 17 flips agree with MW" is my own matcher's answer**, built from three MW regexes and
   the `westergaard=` field; I did not reproduce the builder's `_same_root` / `_disagreement_shape`
   normalisation, so my 12 and its 12 could agree by coincidence on a different partition. The two
   dissenters I name (`32,105`, `35,80`) I read by hand.
8. **Elapsed: 24 minutes.** Six full builds (~2 min each, run in parallel), one corpus census pass and
   nine analysis scripts. No token-rate figure is offered: this was an interactive run with no output
   log to measure.

## Overall verdict

**The arithmetic of H4438 is sound and the artifact is safe to ship. The published reasoning is not
uniformly sound, and one documented regression was avoidable with the pass's own new test.**

Every one of the 24 published figures I was asked to break reproduced exactly from independent
extraction, and the artifact rebuilds byte-for-byte from the committed builder. Change 4 (admitting
the third citation form) is well judged and independently corroborated by MW at 93 of 141
coordinates, by a 12-to-2 MW verdict on the attribution flips, and by a class-band regularity I
checked by hand on 20 samples. Changes 2 and 5 are correct and measurably improve agreement with MW.
The adjudications of `27,71` and `32,133` are right, and `27,71` is right on stronger grounds than
the ones published.

Three things should be corrected in the record rather than in the code: the "nothing but punctuation"
claim in `_boehtlingk_vl_governs` is false of 12 of the 17 pairs it admits and its own named example
`20,13 śal` is a false positive (C2); the zero-diff result for the clause test is a consequence of
the test never running on the population it was measured over, which the file does not disclose (C3);
and the ceiling exclusion's stated mechanism is not the one operating in its own flagship example
(C6). One thing should be added: a recorded measurement of wiring the clause test into
`read_pwg_coords`, which fixes `35,80` and costs 0.7 points of MW agreement — a real fork that a
human should decide, not a defect to be silently left open.

_Dr. Mārcis Gasūns_
