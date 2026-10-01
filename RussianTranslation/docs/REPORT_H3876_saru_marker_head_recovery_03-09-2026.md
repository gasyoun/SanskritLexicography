# Sa→Ru gloss layer — H3876: recovering the marker-residual forms (tier `marker-head`)

_Created: 03-09-2026 · Last updated: 03-09-2026_

**Verdict: GO.** The 1,389 unresolved forms carrying `+`/`-` morpheme marks are recovered
**1,018 forms / 1,783 tokens (73.3 % / 77.1 %)** by lemmatizing the rightmost element
through the *existing* DCS form→lemma map — no segmentation, no new morphology, no new
lexicon. Measured lemmatization precision **25/25** on the canonical wave-2 stratified
sample, against the wave-2 `marker`-tier baseline of 93.3 %. The layer's dominant
renderings are 99.93 % unchanged (27 top-1 flips in 40,387 lemma entries, 23 of them
ties between two one-occurrence glosses).

Run by **Opus 5 (`claude-opus-5`)**. elapsed: 47м 20с (interactive, no worker log — no
tok/s figure is reported).

## 1 · The gap, and why it is not the cheda problem

[`README.md` in gasyoun/SanskritRussian](https://github.com/gasyoun/SanskritRussian/blob/main/README.md)
records the residual as a failure-typology row:

| Type | forms | tokens | Example | Why it misses |
|---|--:|--:|---|---|
| morpheme-marker residual | 1,389 | 2,312 | `A-brahma-BuvanAt` | has `+`/`-` marks but rightmost element is itself inflected, not a bare root |

Tier 3 (`marker`) already recovers 2,480 forms with three probes in
[`marker_recover`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/build_rollup_glossaries.py):
the joined string as a whole form, then the rightmost element against the **bare-root**
inventory, then against the **bare-lemma** inventory. All three miss `A-brahma-BuvanAt`
for one reason: `BuvanAt` is an *ablative of* `Buvana`, so it is in neither inventory —
but it **is** a key in `dcs_form2lemma.tsv`, the very map that resolves whole corpus
forms. The residual was never a morphology gap. It was a probe the code did not make.

**This is deliberately not the wave-3 compound route.**
[`gold/saru_gloss_wave3_cheda_coverage.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/gold/saru_gloss_wave3_cheda_coverage.md)
returned NO-GO on `vidyut.cheda` over isolated forms: 36.4 % coverage at 28 % segmentation
precision, because a running-text segmenter with no context shatters an inflected word into
a stem plus a spurious glossable particle. Nothing here segments anything. The corpus's own
`+`/`-` marks already give the decomposition; the only new step is lemmatizing the element
they delimit. The cheda NO-GO and its recommended successor (a context-aware neural
segmenter over the aligned verse text, "wave 3.5") stand untouched.

## 2 · What changed

One probe, appended after the three existing ones, plus a distinct tier tag:

```python
if len(right) >= MIN_HEAD_LEN:              # rightmost is itself inflected (H3876)
    hcands = f2l.get(right)
    if hcands and hcands[0][3] == 'dcs':
        lemma, upos, _, _ = hcands[0]
        return lemma, upos, l2r.get(lemma), 'marker-head'
```

`marker_recover` now returns a 4-tuple whose last member is the tier, so
`marker`-tier forms keep their existing `source='marker'` and the new, weaker evidence is
separable everywhere provenance is carried — `surface_resolution.tsv`, the per-entry
`source` breakdown, and the provenance line the site renders since H3877. `marker-head`
is registered in the `TIERS` tuple of both
[`saru_gloss_sample.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/saru_gloss_sample.py)
and
[`saru_gloss_aggregate.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/saru_gloss_aggregate.py)
so the next precision panel measures it as its own stratum.

### The two guards, each bought with a measurement

**DCS form keys only.** The vidyut supplement exists to lemmatize whole corpus forms DCS
missed; used on a compound-*internal* element out of context it is markedly worse. All 42
vidyut-sourced heads in the residual were adjudicated exhaustively (not sampled): **35/42**
carry a defensible lemma, and 7 are outright bogus — `vart`→`varDi`, `sarp`→`sarb`,
`Bar`→`Barv`, `ar`→`arv`, `saNketa`→`saNketi`, `avaca`→`avaci`, `upAyatA`→`upaAi`. Five
more are garbled stems (`saMkalpi`, `saMBAvi`) or over-reductions (`cittas`→`cit`). This
agrees independently with the wave-2 panel, which put the **vidyut tier at 71.8 % lemma
precision** against dcs 94.9 % / marker 93.3 %. Cost of the guard: 42 forms / 59 tokens,
3.2 % of the available recovery.

A sharper alternative was tested and rejected — "accept a vidyut head whose lemma is a
DCS-attested lemma" keeps `Barv` and `avaci` while dropping five correct ones
(`yuktAtman`, `vimUQAtman`, `tfptAtman`, `nityatva`, `aBisaMtapta`). It does not separate
the classes, so it is not wired.

**Head length ≥ 3 (`MIN_HEAD_LEN`).** A 1–2 character SLP1 string is one syllable and is
overwhelmingly a homograph of a pronoun or particle. Every such head in the residual was
wrong: `aSva-zA` / `nf-zA` / `vAja-zA` → `zA` → **`tad`** (the demonstrative pronoun; the
real head is the root-noun `-ṣā` "winning", from √san), and `prA-ar` → `ar` → `arv`. Cost
of the guard: 4 forms / 4 tokens, all four of them errors. No correct recovery is lost.

## 3 · Baseline reproduced first

The unpatched script was run from `origin/master` over the real 190,838-form corpus before
anything was changed, and reproduces the published figures exactly:

```
[D] surface forms: hit=111996 (marker-recovered=2480) miss=78842 (hit%=58.7); homograph-flagged=9733
[D] 40370 lemmas, 1853 roots
```

`hit=111,996` · `marker=2,480` · `miss=78,842` · `58.7 %` · `1,853` roots all match the
README / `.ai_state.md` numbers of record. (The published `.tsv`/`.jsonl` still carry the
pre-H1349 root count 2,021 — that is the known **D8** republish fence, not a discrepancy
introduced here.)

## 4 · Coverage delta

```
[D] surface forms: hit=113014 (marker-recovered=3498, of which inflected-head=1018) miss=77824 (hit%=59.2)
[D] 40387 lemmas, 1856 roots
```

| | before | after | delta |
|---|--:|--:|--:|
| resolved forms | 111,996 (58.7 %) | 113,014 (**59.2 %**) | +1,018 |
| unresolved forms | 78,842 | 77,824 | −1,018 |
| unresolved tokens | 140,667 | 138,884 | −1,783 |
| token coverage | 87.11 % | **87.28 %** | +0.17 pp |
| marker-residual typology row | 1,389 / 2,312 | **371 / 529** | −73.3 % / −77.1 % |
| lemma entries | 40,370 | 40,387 | +17 |
| root entries | 1,853 | 1,856 | +3 |

Tier census from `surface_resolution.tsv` — **the pre-existing tiers are bit-for-bit
unchanged and every newly resolved form carries a marker**:

| tier | before (forms/tokens) | after (forms/tokens) |
|---|--:|--:|
| dcs | 80,949 / 863,763 | 80,949 / 863,763 |
| vidyut | 28,567 / 81,119 | 28,567 / 81,119 |
| marker | 2,480 / 5,979 | 2,480 / 5,979 |
| `marker-head` | — | **1,018 / 1,783** |

Zero forms became *newly* unresolved; zero lemma or root entries were lost.

## 5 · Precision — the wave-2 rubric, one judge

Drawn through the canonical sampler
([`saru_gloss_sample.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/saru_gloss_sample.py),
D5 tier × frequency, seed 42, k=10/cell) off the patched resolution trace: **25**
`marker-head` items (hapax 10 · low 10 · mid 4 · high 1 — the tier has only 4 mid and 1
high form in total). Judged on the two independent D6 axes.

| axis | n | correct | partial | wrong | precision | wave-2 `marker` baseline |
|---|--:|--:|--:|--:|--:|--:|
| lemmatization | 25 | 25 | — | 0 | **100 %** | 93.3 % |
| gloss | 25 | 15 | 8 | 2 | **60 %** (good+partial 92 %) | 90.0 % |

**This is a single-model adjudication (Opus 5), not the 3-judge panel** wave 2 used
(haiku + opus + sonnet with adversarial verify, D4/D12). It is weaker evidence by design
and the panel run stays owed — see §7.

A wider ad-hoc sample stratified on *linguistic* shape rather than frequency (98 items:
10 preverb+verb, 13 verbal head, 75 nominal head) put lemmatization at 90/91 on the DCS
half — the one error being `prakfti-sTas`, where DCS's dominant lemma for the isolated
form `sTas` is the finite verb √as rather than the adjectival stem `sTa`.

### The gloss axis is the honest weak point

Lemmatization is near-perfect because the probe does exactly one well-defined thing.
The gloss axis is not, and the reason is structural: these forms **are** compounds, so
the aggregated Russian belongs to the whole compound, not to the head lemma the tier
attributes it to. `mahA-raTAH` "великие воины" lands on `raTa` ("колесница");
`vigata-BIr` "бесстрашный" lands on `BI` ("страх") — a bahuvrīhi whose sense is the
*negation* of its head. Roughly 12 % of the nominal-head recoveries are bahuvrīhi of this
shape.

This is **not a new defect class**. The wave-2 panel already named it as systematic lemma
defect #3 — *"compound tokens lemmatized to their final member only … the marker/rightmost
rule keeps only the last member, dropping the prior stem"* — in the existing `marker` tier,
which still scored 93.3 %. H3876 extends an accepted approximation to 1,018 more forms; it
does not solve it, and does not claim to.

## 6 · Layer-level impact — the acceptance question

Wave 3's bar is *"a form recovered but wrong is a regression, not a win."* The item-level
gloss number above is the pessimistic reading. The question that decides the layer's
trustworthiness is narrower: **does any lemma's dominant rendering change?** The glossary
ranks each entry's Russian by occurrence count, and 1,018 mostly-hapax forms can only hurt
by displacing a top-1 gloss.

| | lemma layer | root layer |
|---|--:|--:|
| entries | 40,387 | 1,856 |
| entries whose top-1 gloss flipped | **27 (0.067 %)** | **2 (0.11 %)** |
| … of those, a tie between two 1-occurrence glosses | 23 | 1 |
| … of those, a genuinely larger new top gloss | 4 | 1 |
| entries lost | 0 | 0 |

The four real displacements, adjudicated:

- `diva` (n 15→57) — "небу" → **"день за днем"**, on 26 occurrences of `dive-dive`. A clear
  improvement: the reduplicated locative is a real and frequent rendering of `div`.
- `yAjin` (n 5→20) — "приноси жертву мнѣ" → **"Мне жертвующим"** (`mad-yAjI`, n=11). Correct.
- `guhyatama` (n 9→10) — "таинственнейшему" → "таинственнѣйшимъ". Orthographic variant of
  the same gloss; a wash.
- `saMsiD` (n 15→28) — "увенчалось успехом" → "многими рождениями достигший совершенства".
  A compound-scoped gloss displacing a clean one: **one mild degradation in 40,387 entries.**

The remaining 23 are entries where every attested rendering occurs exactly once, so there
was no meaningful "top" to disturb.

A third option was considered — resolve these forms for *lemma linkage only*, without
pushing their Russian into the lemma's translation list. At 0.067 % top-1 churn it does not
pay for the accounting complexity it would add to `emit()`, so it is not built.

## 7 · What stays open

1. **A 3-judge panel on the `marker-head` stratum.** The tier is registered in both `TIERS`
   tuples, so the next wave-2 panel run picks it up with no further code. The number in §5
   is single-judge and should be replaced, not cited as panel-grade.
2. **The 371 forms / 529 tokens still unresolved.** Two clean sub-classes: heads that are
   themselves unsplit compounds (`AjAneyaKurakzuRRa-pakvailAkzetrasaMBavam`) — that is the
   long-compound stratum and belongs to the wave-3.5 neural-segmenter route, not here; and
   dual/plural nominals absent from both lexica (`sargau`, `apyayau`, `vaSyaiH`).
3. **Compound-scoped Russian.** The real fix for the gloss axis is a compound layer, or
   attributing a bahuvrīhi's gloss somewhere other than its head. Both are design questions
   for the segmenter wave.
4. **Republish (D8, human-gated).** The published `.tsv`/`.jsonl` in
   [gasyoun/SanskritRussian](https://github.com/gasyoun/SanskritRussian) are untouched by
   this pass, as D8 requires. The numbers in §4 land in the data only at the next gated
   republish, which will also carry the pending root-count drop 2,021 → 1,853.

## 8 · Reproducing

```sh
# from RussianTranslation/
python -m pytest tests/test_h3876_marker_head_recovery.py -q          # 10 passed
python -m pytest tests/test_saru_gloss_pipeline.py tests/test_saru_gloss_wave2.py \
                tests/test_saru_gloss_wave3.py tests/test_saru_gloss_tm.py -q   # 23 passed

# full rebuild of layers 2 and 3 (needs glossary/surface_glossary.jsonl + the three maps)
python src/build_rollup_glossaries.py
```

The before/after run in §3–§6 used the live `glossary/surface_glossary.jsonl` (147 MB,
gitignored) and the three published maps from
[gasyoun/SanskritRussian](https://github.com/gasyoun/SanskritRussian)
(`dcs_form2lemma.tsv`, `dcs_lemma2root.tsv`, `vidyut_form2lemma.tsv`), with `origin/master`'s
copy of the script as the baseline arm. Both arms ran in ~13 s.

_Dr. Mārcis Gasūns_
